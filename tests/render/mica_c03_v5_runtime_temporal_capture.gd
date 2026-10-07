extends SceneTree

## Native runtime temporal evidence for MICA C03 V5.
##
## This capture deliberately drives the real StoryStage01 scene and records
## one complete 24-frame UAL move cycle for every authored direction.  The
## Godot movie writer is used by the launch command, while this script writes
## a frame-by-frame runtime ledger so a reviewer can verify that the visible
## movie samples are not repeated stills or an untracked physics wait.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://artifacts/mica_c03_v5_runtime_temporal_capture"
const FRAME_DIR := OUT_DIR + "/frames_r13"
const EVIDENCE_PATH := OUT_DIR + "/MICA_C03_V5_RUNTIME_TEMPORAL_EVIDENCE_R13.json"
const VIEWPORT_SIZE := Vector2i(1920, 1080)
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const VECTORS: Array[Vector2] = [
    Vector2.RIGHT,
    Vector2(0.70710678, 0.70710678),
    Vector2.DOWN,
    Vector2(-0.70710678, 0.70710678),
    Vector2.LEFT,
    Vector2(-0.70710678, -0.70710678),
    Vector2.UP,
    Vector2(0.70710678, -0.70710678),
]
const MOVE_FRAMES := 24
const SETTLE_FRAMES := 6
const CAPTURE_FPS := 24
const REVIEW_ZOOM := 2.6
# Keep the evidence camera fixed at the actor's start point.  Following a
# CharacterBody2D immediately after physics can leave Camera2D one render tick
# behind, which makes an otherwise planted duplicate cell appear to jump on
# screen.  The fixed camera also exposes the real world travel instead of
# cancelling it out, while the ledger continues to record root positions.
const CAMERA_FOLLOW_ACTOR := false
const USE_CAMERA := false
const CAPTURE_ORIGIN := Vector2(640.0, 360.0)

var failures: Array[String] = []
var segments: Array[Dictionary] = []
var samples: Array[Dictionary] = []
var overlay_title: Label
var overlay_detail: Label
var sample_index := 0
var frame_capture_ok := true


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    var prior_fast := bool(ProjectSettings.get_setting("sable_visuals/fast_character_runtime", true))
    var prior_aster := bool(ProjectSettings.get_setting("sable_visuals/aster_v4_locomotion_preview", false))
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime", true)
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview", false)
    DisplayServer.window_set_size(VIEWPORT_SIZE)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(FRAME_DIR))

    _make_overlay()
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(20)
    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.queue_free()
    await _frames(2)

    var mica: OperatorActor = null
    for actor in stage.squad.operators:
        if actor is OperatorActor and (actor as OperatorActor).operator_id == "CHR_PROTO_03":
            mica = actor as OperatorActor
        elif actor is CanvasItem:
            (actor as CanvasItem).visible = false
    if mica == null:
        _fail("MICA actor not found in StoryStage01 squad")
        await _finish(stage, prior_fast, prior_aster)
        return

    stage.squad.request_control(2)
    await _frames(2)
    _require(stage.squad.get_active_operator() == mica, "MICA is the active Stage operator")
    mica.visible = true
    var runtime := mica.get_node_or_null("FastCharacterRuntime") as FastCharacterRuntime
    if runtime == null or not runtime.is_runtime_active():
        _fail("MICA C03 V5 FastCharacterRuntime did not activate in stage")
        await _finish(stage, prior_fast, prior_aster)
        return

    # The capture is a temporal presentation audit, not a collision test.
    # Remove the hidden squad bodies from the contact solver so an inactive
    # follower cannot inject a sideways correction into a planted duplicate
    # sample (this was only visible on the W segment).  The shipped runtime
    # collision contract is exercised separately by the smoke suite.
    mica.collision_layer = 0
    mica.collision_mask = 0
    for squad_actor in stage.squad.operators:
        if squad_actor != mica:
            squad_actor.collision_layer = 0
            squad_actor.collision_mask = 0

    if not USE_CAMERA:
        # With the production camera disabled, enlarge only the evidence
        # sprite so the legs/soles remain reviewable at native 1080p without
        # changing any shipped descriptor or source atlas.
        runtime.sprite.scale *= REVIEW_ZOOM

    var camera := stage.get_node_or_null("Camera2D") as Camera2D
    if camera:
        camera.position_smoothing_enabled = false
        # Use a native camera zoom for gait inspection.  This enlarges the
        # runtime actor optically (without upscaling the captured container)
        # so leg/sole contact is reviewable at 1920x1080.
        camera.zoom = Vector2.ONE * REVIEW_ZOOM
        camera.global_position = CAPTURE_ORIGIN
        camera.enabled = USE_CAMERA
    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as Node
    if camera_presentation:
        camera_presentation.set_process(false)
    mica.set_movement_bounds(Rect2(160.0, 115.0, 960.0, 500.0))

    for sector in range(DIRECTIONS.size()):
        _clear_projectiles()
        var segment_origin := _capture_origin_for_sector(sector)
        mica.global_position = segment_origin
        mica.debug_drive(VECTORS[sector], VECTORS[sector])
        await _physics_frames(SETTLE_FRAMES)
        # Align the first recorded sample to authored move cell 00.  The
        # runtime cursor is intentionally private, so wait for its natural
        # modulo boundary instead of mutating animation state from the test.
        var aligned := false
        for _alignment in range(MOVE_FRAMES + 2):
            var alignment_contract := runtime.debug_contract()
            if str(alignment_contract.get("active_state", "")) == "move" and int(alignment_contract.get("active_frame", -1)) == 0:
                aligned = true
                break
            await physics_frame
            if camera and CAMERA_FOLLOW_ACTOR:
                camera.global_position = mica.global_position
            await process_frame
            await RenderingServer.frame_post_draw
        var settle_contract := runtime.debug_contract()
        _require(aligned, "%s aligns temporal capture to move frame 00" % DIRECTIONS[sector])
        _require(mica.facing_sector == sector, "%s resolves authored sector before temporal capture" % DIRECTIONS[sector])
        _require(bool(settle_contract.get("active", false)), "%s runtime remains active before temporal capture" % DIRECTIONS[sector])
        if camera and USE_CAMERA and not CAMERA_FOLLOW_ACTOR:
            # Re-anchor once after the natural frame-00 alignment.  Camera2D
            # normally commits its scroll at the next render tick; forcing the
            # update here prevents the first sample from inheriting the prior
            # direction's camera transform without advancing the actor.
            camera.global_position = mica.global_position
            if camera.has_method("force_update_scroll"):
                camera.call("force_update_scroll")

        var segment_start := sample_index
        var active_frames: Array[int] = []
        var root_positions: Array[Array] = []
        var root_motion_scales: Array[float] = []
        var states: Array[String] = []
        var frame_paths: Array[String] = []
        for frame in range(MOVE_FRAMES):
            mica.debug_drive(VECTORS[sector], VECTORS[sector])
            await physics_frame
            if camera and CAMERA_FOLLOW_ACTOR:
                # Follow the real actor so the native 1080p crop keeps the
                # legs/soles at review scale while the ledger still records
                # the actor's world displacement independently.
                camera.global_position = mica.global_position
            await process_frame
            var contract := runtime.debug_contract()
            var active_state := str(contract.get("active_state", ""))
            var active_frame := int(contract.get("active_frame", -1))
            var active_sector := int(contract.get("active_sector", -1))
            _set_overlay(
                "MICA C03 V5 | %s | UAL MOVE %02d/%02d" % [DIRECTIONS[sector], frame + 1, MOVE_FRAMES],
                "runtime active_frame=%02d  active_sector=%d  root=(%.1f, %.1f)  sample=%03d" % [active_frame, active_sector, mica.global_position.x, mica.global_position.y, sample_index],
            )
            await RenderingServer.frame_post_draw
            var frame_path := await _capture_temporal_frame(DIRECTIONS[sector], frame)
            frame_paths.append(frame_path)
            if frame_path.is_empty():
                frame_capture_ok = false
            active_frames.append(active_frame)
            root_positions.append([snappedf(mica.global_position.x, 0.001), snappedf(mica.global_position.y, 0.001)])
            states.append(active_state)
            samples.append({
                "sample_index": sample_index,
                "direction": DIRECTIONS[sector],
                "direction_index": sector,
                "cycle_frame": frame,
                "expected_active_frame": frame,
                "active_state": active_state,
                "active_frame": active_frame,
                "active_sector": active_sector,
                "root_position": root_positions.back(),
                "camera_position": [snappedf(camera.global_position.x, 0.001), snappedf(camera.global_position.y, 0.001)] if camera else [],
                "runtime_position": [snappedf(runtime.global_position.x, 0.001), snappedf(runtime.global_position.y, 0.001)],
                "sprite_position": [snappedf(runtime.sprite.position.x, 0.001), snappedf(runtime.sprite.position.y, 0.001)] if runtime.sprite else [],
                "sprite_region_y": snappedf(runtime.sprite.region_rect.position.y, 0.001) if runtime.sprite else -1.0,
                "velocity": [snappedf(mica.velocity.x, 0.001), snappedf(mica.velocity.y, 0.001)],
                "root_motion_scale": snappedf(float(contract.get("root_motion_scale", 1.0)), 0.001),
                "capture_path": frame_path,
            })
            root_motion_scales.append(snappedf(float(contract.get("root_motion_scale", 1.0)), 0.001))
            _require(active_state == "move", "%s sample %02d is in move state" % [DIRECTIONS[sector], frame])
            _require(active_sector == sector, "%s sample %02d keeps authored sector" % [DIRECTIONS[sector], frame])
            sample_index += 1

        _require(active_frames == _range_int(0, MOVE_FRAMES), "%s visits every active move frame exactly once" % DIRECTIONS[sector])
        _require(states == _repeat_string("move", MOVE_FRAMES), "%s temporal ledger contains no idle/fire frame" % DIRECTIONS[sector])
        # MICA's twelve authored poses occupy two UAL samples each.  The
        # second sample must hold the gameplay root so a duplicate raster cell
        # cannot drag its planted sole across the floor.  Keep this as an
        # explicit runtime gate so a future atlas/cadence regression is caught
        # before another video is sent for visual review.
        for pair_start in range(0, MOVE_FRAMES, 2):
            var first := Vector2(float(root_positions[pair_start][0]), float(root_positions[pair_start][1]))
            var second := Vector2(float(root_positions[pair_start + 1][0]), float(root_positions[pair_start + 1][1]))
            _require(first.distance_to(second) <= 0.05, "%s duplicate pose F%02d->F%02d holds the runtime root" % [DIRECTIONS[sector], pair_start, pair_start + 1])
        _require(root_motion_scales.size() == MOVE_FRAMES, "%s records cadence root scales for every sample" % DIRECTIONS[sector])
        segments.append({
            "direction": DIRECTIONS[sector],
            "direction_index": sector,
            "capture_origin": [segment_origin.x, segment_origin.y],
            "move_vector": [VECTORS[sector].x, VECTORS[sector].y],
            "capture_fps": CAPTURE_FPS,
            "move_frame_count": MOVE_FRAMES,
            "sample_index_start": segment_start,
            "sample_index_end": sample_index - 1,
            "active_frames": active_frames,
            "root_positions": root_positions,
            "root_motion_scales": root_motion_scales,
            "frame_paths": frame_paths,
            "active_frame_verified": active_frames == _range_int(0, MOVE_FRAMES),
            "state_verified": states == _repeat_string("move", MOVE_FRAMES),
        })
        await _physics_frames(SETTLE_FRAMES)

    var evidence := {
        "schema": 1,
        "actor_id": "CHR_PROTO_03",
        "costume_id": "MICA_RECON_C03",
        "runtime_descriptor": "data/character_pipeline/mica_runtime.json",
        "capture_type": "actual StoryStage01 runtime temporal move capture",
        "native_capture_resolution": [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y],
        "capture_fps": CAPTURE_FPS,
        "review_camera_zoom": REVIEW_ZOOM,
        "camera_mode": "fixed_world_no_camera_with_evidence_sprite_scale" if not USE_CAMERA else "production_camera",
        "collision_isolation": "capture_only_hidden_squad_bodies_and_active_actor_disabled",
        "directions": DIRECTIONS,
        "move_frames_per_direction": MOVE_FRAMES,
        "settle_frames_between_segments": SETTLE_FRAMES,
        "frame_directory": FRAME_DIR,
        "frame_count": samples.size(),
        "frame_capture_resolution_verified": frame_capture_ok,
        "segments": segments,
        "samples": samples,
        "movie_writer": {
            "expected_video_extension": ".avi",
            "launch_requires": ["--write-movie", "--fixed-fps 24"],
            "overlay_active_frame": true,
        },
        "result": "FAIL" if not failures.is_empty() else "PASS",
        "visual_gate": "PONYTAIL_FULL_REVIEW_REQUIRED",
        "promotion": "R8C_CAPTURE_ONLY_HOLD",
        "failures": failures,
    }
    var evidence_file := FileAccess.open(ProjectSettings.globalize_path(EVIDENCE_PATH), FileAccess.WRITE)
    evidence_file.store_string(JSON.stringify(evidence, "  ") + "\n")
    evidence_file.close()
    await _finish(stage, prior_fast, prior_aster)


func _make_overlay() -> void:
    var layer := CanvasLayer.new()
    layer.layer = 120
    root.add_child(layer)
    var background := ColorRect.new()
    # Keep the active-frame ledger off the actor so anatomy and sole contact
    # remain unobstructed in every direction.
    background.position = Vector2(1430.0, 28.0)
    background.size = Vector2(455.0, 112.0)
    background.color = Color(0.015, 0.025, 0.04, 0.92)
    layer.add_child(background)
    overlay_title = Label.new()
    overlay_title.position = Vector2(1446.0, 39.0)
    overlay_title.add_theme_font_size_override("font_size", 18)
    overlay_title.add_theme_color_override("font_color", Color("e3bc75"))
    layer.add_child(overlay_title)
    overlay_detail = Label.new()
    overlay_detail.position = Vector2(1446.0, 70.0)
    overlay_detail.add_theme_font_size_override("font_size", 12)
    overlay_detail.add_theme_color_override("font_color", Color("e8edf3"))
    layer.add_child(overlay_detail)


func _set_overlay(title: String, detail: String) -> void:
    overlay_title.text = title
    overlay_detail.text = detail


func _capture_temporal_frame(direction: String, frame: int) -> String:
    var viewport := get_root().get_viewport()
    var texture := viewport.get_texture() if viewport else null
    var image := texture.get_image() if texture else null
    if image == null or image.is_empty() or image.get_size() != VIEWPORT_SIZE:
        _fail("invalid native temporal frame %s F%02d" % [direction, frame])
        return ""
    var path := ProjectSettings.globalize_path("%s/%03d_%s_F%02d.png" % [FRAME_DIR, sample_index, direction, frame])
    var error := image.save_png(path)
    if error != OK:
        _fail("temporal frame save failure: %s F%02d" % [direction, frame])
        return ""
    return path


func _range_int(start: int, count: int) -> Array[int]:
    var values: Array[int] = []
    for value in range(start, start + count):
        values.append(value)
    return values


func _capture_origin_for_sector(sector: int) -> Vector2:
    # The fixed evidence camera leaves real travel visible.  Bias the starting
    # root vertically per direction so the natural settle + 24-sample travel
    # remains inside the native frame even at the enlarged review scale.
    var origin := CAPTURE_ORIGIN
    if VECTORS[sector].y < -0.1:
        origin.y = 480.0
    elif VECTORS[sector].y > 0.1:
        origin.y = 240.0
    return origin


func _repeat_string(value: String, count: int) -> Array[String]:
    var values: Array[String] = []
    for _index in range(count):
        values.append(value)
    return values


func _frames(count: int) -> void:
    for _index in range(count):
        await process_frame


func _physics_frames(count: int) -> void:
    for _index in range(count):
        await physics_frame


func _clear_projectiles() -> void:
    for child in root.get_children():
        if child is PrototypeProjectile:
            child.queue_free()


func _require(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        _fail(label)


func _fail(label: String) -> void:
    failures.append(label)
    push_error(label)


func _finish(stage: Node, prior_fast: bool, prior_aster: bool) -> void:
    _clear_projectiles()
    if stage:
        stage.queue_free()
    await _frames(2)
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime", prior_fast)
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview", prior_aster)
    print("MICA_C03_V5_RUNTIME_TEMPORAL_CAPTURE: " + ("PASS" if failures.is_empty() else "FAIL"))
    quit(0 if failures.is_empty() else 1)
