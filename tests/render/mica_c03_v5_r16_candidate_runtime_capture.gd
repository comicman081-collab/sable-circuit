extends SceneTree

## Native runtime temporal evidence for the MICA C03 R16 two-cycle unique-frame QA candidate.
##
## This capture deliberately drives the real StoryStage01 scene and records
## one complete 24-frame UAL move cycle for every authored direction.  The
## Godot movie writer is used by the launch command, while this script writes
## a frame-by-frame runtime ledger so a reviewer can verify that the visible
## movie samples are not repeated stills or an untracked physics wait.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const DEFAULT_OUT_DIR := "res://artifacts/mica_c03_v5_r16_candidate_runtime_capture"
const DEFAULT_FRAME_DIR := DEFAULT_OUT_DIR + "/frames_r16_two_cycle"
const DEFAULT_EVIDENCE_PATH := DEFAULT_OUT_DIR + "/MICA_C03_V5_RUNTIME_UNIQUE_EVIDENCE_R16.json"
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
const AUTHORED_MOVE_FRAMES := 24
const MOVE_FRAMES := 48
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
var capture_out_dir := DEFAULT_OUT_DIR
var capture_frame_dir := DEFAULT_FRAME_DIR
var capture_evidence_path := DEFAULT_EVIDENCE_PATH
var capture_label := "MICA C03 V5 R16"
var capture_is_custom := false
var capture_fps := CAPTURE_FPS
var capture_sample_frames := MOVE_FRAMES
var capture_review_zoom := REVIEW_ZOOM
var capture_use_camera := USE_CAMERA
var capture_camera_follow_actor := CAMERA_FOLLOW_ACTOR
var capture_sprite_scale := 1.0
var expected_root_factor := 1.0
var root_step_min := 4.0
var root_step_max := 9.0
var root_step_spread := 3.0
var capture_mode := "legacy_24fps"
var overlay_title: Label
var overlay_detail: Label
var sample_index := 0
var frame_capture_ok := true
var r21_root_tracks: Dictionary = {}


func _init() -> void:
    var requested_mode := OS.get_environment("SABLE_RUNTIME_CAPTURE_MODE").strip_edges().to_lower()
    var configured_out := OS.get_environment("SABLE_RUNTIME_CAPTURE_OUT_DIR").strip_edges()
    if requested_mode == "r20_60hz" or requested_mode == "r21_60hz":
        capture_mode = requested_mode
        capture_is_custom = true
        var r21 := requested_mode == "r21_60hz"
        capture_out_dir = configured_out.trim_suffix("/") if not configured_out.is_empty() else ("res://artifacts/mica_c03_r21_r8c_60hz_sole_lock_capture" if r21 else "res://artifacts/mica_c03_r20_r8c_60hz_runtime_capture")
        capture_frame_dir = capture_out_dir + ("/frames_r21_60hz_two_cycle" if r21 else "/frames_r20_60hz_two_cycle")
        capture_evidence_path = capture_out_dir + ("/MICA_C03_R21_RUNTIME_60HZ_SOLE_LOCK_EVIDENCE.json" if r21 else "/MICA_C03_R20_RUNTIME_60HZ_EVIDENCE.json")
        capture_label = "MICA C03 R21 R8C 60Hz frame-transition sole lock" if r21 else "MICA C03 R20 R8C 60Hz gait-speed calibration"
        capture_fps = 60
        capture_sample_frames = AUTHORED_MOVE_FRAMES * 5
        capture_review_zoom = REVIEW_ZOOM
        capture_use_camera = true
        capture_camera_follow_actor = false
        capture_sprite_scale = 1.0
        expected_root_factor = float(OS.get_environment("SABLE_EXPECTED_ROOT_FACTOR")) if not OS.get_environment("SABLE_EXPECTED_ROOT_FACTOR").strip_edges().is_empty() else (0.0 if r21 else 0.258947368)
        root_step_min = 0.0 if r21 else 0.25
        root_step_max = 1.50 if r21 else 1.20
        root_step_spread = 1.50 if r21 else 0.90
    elif not configured_out.is_empty():
        capture_is_custom = true
        capture_out_dir = configured_out.trim_suffix("/")
        capture_frame_dir = capture_out_dir + "/frames_r19_r8c_two_cycle"
        capture_evidence_path = capture_out_dir + "/MICA_C03_R19_RUNTIME_UNIQUE_EVIDENCE.json"
        capture_label = "MICA C03 R19 R8C runtime integration"
    call_deferred("_run")


func _run() -> void:
    var prior_fast := bool(ProjectSettings.get_setting("sable_visuals/fast_character_runtime", true))
    var prior_aster := bool(ProjectSettings.get_setting("sable_visuals/aster_v4_locomotion_preview", false))
    var descriptor_override := OS.get_environment("SABLE_MICA_DESCRIPTOR_OVERRIDE").strip_edges()
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime", true)
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview", false)
    if not descriptor_override.is_empty():
        ProjectSettings.set_setting("sable_visuals/fast_character_runtime_descriptor_override", descriptor_override)
    if capture_mode == "r21_60hz":
        _load_r21_root_tracks(descriptor_override)
    DisplayServer.window_set_size(VIEWPORT_SIZE)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(capture_out_dir))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(capture_frame_dir))

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

    if not is_equal_approx(capture_sprite_scale, 1.0):
        # Legacy R16/R19 captures used an evidence-only sprite scale.  R20
        # deliberately leaves the sprite at its shipped descriptor scale and
        # applies review zoom to the camera instead, preserving root/sole
        # geometry for a meaningful lock measurement.
        runtime.sprite.scale *= capture_sprite_scale

    var camera := stage.get_node_or_null("Camera2D") as Camera2D
    if camera:
        camera.position_smoothing_enabled = false
        # Use a native camera zoom for gait inspection.  This enlarges the
        # runtime actor optically (without upscaling the captured container)
        # so leg/sole contact is reviewable at 1920x1080.
        camera.zoom = Vector2.ONE * capture_review_zoom
        camera.global_position = CAPTURE_ORIGIN
        camera.enabled = capture_use_camera
    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as Node
    if camera_presentation:
        camera_presentation.set_process(false)
    mica.set_movement_bounds(Rect2(0.0, 0.0, 1920.0, 1080.0))

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
        var alignment_budget := AUTHORED_MOVE_FRAMES + 2
        if capture_mode == "r20_60hz":
            # A 24fps cursor advances by 0.4 pose per 60Hz physics tick, so a
            # direction may begin anywhere in the cycle after the previous
            # segment's settle window.  Give it a full cycle plus margin to
            # find authored frame 00; the capture itself still starts exactly
            # at that boundary.
            alignment_budget = 80
        elif capture_mode == "r21_60hz":
            # The frame-transition path owns the animation cursor in the
            # physics tick.  A six-tick settle can leave the cursor anywhere
            # in its 24-frame loop; allow one complete 24 fps cycle plus
            # margin so every direction's first captured sample is F00.
            alignment_budget = 140
        for _alignment in range(alignment_budget):
            var alignment_contract := runtime.debug_contract()
            if str(alignment_contract.get("active_state", "")) == "move" and int(alignment_contract.get("active_frame", -1)) == 0:
                aligned = true
                break
            await physics_frame
            if camera and capture_camera_follow_actor:
                camera.global_position = mica.global_position
            await process_frame
            await RenderingServer.frame_post_draw
        var settle_contract := runtime.debug_contract()
        _require(aligned, "%s aligns temporal capture to move frame 00" % DIRECTIONS[sector])
        _require(mica.facing_sector == sector, "%s resolves authored sector before temporal capture" % DIRECTIONS[sector])
        _require(bool(settle_contract.get("active", false)), "%s runtime remains active before temporal capture" % DIRECTIONS[sector])
        if camera and capture_use_camera and not capture_camera_follow_actor:
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
        var root_motion_modes: Array[String] = []
        var states: Array[String] = []
        var frame_paths: Array[String] = []
        var visible_cycle := 1
        var prior_active_frame := -1
        for frame in range(capture_sample_frames):
            mica.debug_drive(VECTORS[sector], VECTORS[sector])
            await physics_frame
            if camera and capture_camera_follow_actor:
                # Follow the real actor so the native 1080p crop keeps the
                # legs/soles at review scale while the ledger still records
                # the actor's world displacement independently.
                camera.global_position = mica.global_position
            await process_frame
            var contract := runtime.debug_contract()
            var active_state := str(contract.get("active_state", ""))
            var active_frame := int(contract.get("active_frame", -1))
            var active_sector := int(contract.get("active_sector", -1))
            if prior_active_frame == AUTHORED_MOVE_FRAMES - 1 and active_frame == 0:
                visible_cycle += 1
            _set_overlay(
                "%s | %s | UAL MOVE %02d/%02d | VISIBLE CYCLE %d/2" % [capture_label, DIRECTIONS[sector], active_frame + 1, AUTHORED_MOVE_FRAMES, visible_cycle],
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
            root_motion_modes.append(str(contract.get("move_root_mode", "scalar")))
            samples.append({
                "sample_index": sample_index,
                "direction": DIRECTIONS[sector],
                "direction_index": sector,
                "cycle_frame": active_frame,
                "cycle_index": int(frame / maxf(1.0, float(capture_sample_frames) / 2.0)),
                "expected_active_frame": active_frame,
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
            prior_active_frame = active_frame
            sample_index += 1

        if _is_high_rate_capture():
            _verify_high_rate_active_frames(DIRECTIONS[sector], active_frames)
        else:
            _require(active_frames == _expected_two_cycle_frames(), "%s visits both authored move cycles in order" % DIRECTIONS[sector])
        _require(states == _repeat_string("move", capture_sample_frames), "%s temporal ledger contains no idle/fire frame" % DIRECTIONS[sector])
        # R14 carries twenty-four unique Blender+UAL move cells.  R20 wrongly
        # required every high-rate sample to move the root, which slides a
        # sole whenever the same 24fps raster cell is repeated.  R21 instead
        # verifies the exact per-visible-frame sole-lock trajectory.
        var root_steps: Array[float] = []
        for step_index in range(1, capture_sample_frames):
            var previous := Vector2(float(root_positions[step_index - 1][0]), float(root_positions[step_index - 1][1]))
            var current := Vector2(float(root_positions[step_index][0]), float(root_positions[step_index][1]))
            var step_distance := previous.distance_to(current)
            root_steps.append(step_distance)
            if capture_mode != "r21_60hz":
                _require(step_distance > 0.10, "%s unique move transition F%02d->F%02d advances the runtime root" % [DIRECTIONS[sector], step_index - 1, step_index])
        if capture_mode == "r21_60hz":
            _verify_r21_sole_lock_root_track(DIRECTIONS[sector], active_frames, root_positions)
            _require(root_motion_modes == _repeat_string("frame_transition_sole_lock", capture_sample_frames), "%s uses the R21 frame-transition sole-lock runtime mode for every sample" % DIRECTIONS[sector])
        elif not root_steps.is_empty():
            var min_step: float = float(root_steps.min())
            var max_step: float = float(root_steps.max())
            # The legacy 24fps movie loop can alternate one 1/30 and one 1/20
            # physics interval.  R20 samples every physics tick and therefore
            # expects a small, stable step at the calibrated root factor.
            _require(min_step >= root_step_min and max_step <= root_step_max and max_step - min_step <= root_step_spread, "%s two-cycle cadence is bounded and uniform (min=%.3f max=%.3f)" % [DIRECTIONS[sector], min_step, max_step])
        _require(root_motion_scales.size() == capture_sample_frames, "%s records cadence root scales for every sample" % DIRECTIONS[sector])
        if capture_mode != "r21_60hz":
            for cadence_index in range(root_motion_scales.size()):
                _require(abs(root_motion_scales[cadence_index] - expected_root_factor) <= 0.002, "%s move sample F%03d uses calibrated root factor %.6f" % [DIRECTIONS[sector], cadence_index, expected_root_factor])
        segments.append({
            "direction": DIRECTIONS[sector],
            "direction_index": sector,
            "capture_origin": [segment_origin.x, segment_origin.y],
            "move_vector": [VECTORS[sector].x, VECTORS[sector].y],
            "capture_fps": capture_fps,
            "move_frame_count": capture_sample_frames,
            "authored_move_frame_count": AUTHORED_MOVE_FRAMES,
            "cycle_count": 2,
            "sample_index_start": segment_start,
            "sample_index_end": sample_index - 1,
            "active_frames": active_frames,
            "root_positions": root_positions,
            "root_step_distances": root_steps,
            "root_motion_scales": root_motion_scales,
            "root_motion_modes": root_motion_modes,
            "frame_paths": frame_paths,
            # R20 captures sample the 24 authored cells at native 60 Hz, so
            # each authored frame appears for two or three physics ticks.
            # Keep the ledger flag truthful instead of comparing the 120
            # samples to the legacy 48-entry 24-fps sequence.
            "active_frame_verified": _active_frame_sequence_verified(active_frames),
            "state_verified": states == _repeat_string("move", capture_sample_frames),
        })
        await _physics_frames(SETTLE_FRAMES)

    var evidence := {
        "schema": 1,
        "actor_id": "CHR_PROTO_03",
        "costume_id": "MICA_RECON_C03",
        "runtime_descriptor": descriptor_override if not descriptor_override.is_empty() else "data/character_pipeline/mica_runtime.json",
        "capture_type": "actual StoryStage01 runtime temporal move capture",
        "native_capture_resolution": [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y],
        "capture_fps": capture_fps,
        "review_camera_zoom": capture_review_zoom,
        "camera_mode": "fixed_world_camera_no_sprite_scale" if capture_use_camera and not capture_camera_follow_actor else ("fixed_world_no_camera_with_evidence_sprite_scale" if not capture_use_camera else "production_camera_follow"),
        "collision_isolation": "capture_only_hidden_squad_bodies_and_active_actor_disabled",
        "directions": DIRECTIONS,
        "move_frames_per_direction": capture_sample_frames,
        "authored_move_frames_per_direction": AUTHORED_MOVE_FRAMES,
        "cycles_per_direction": 2,
        "settle_frames_between_segments": SETTLE_FRAMES,
        "frame_directory": capture_frame_dir,
        "frame_count": samples.size(),
        "frame_capture_resolution_verified": frame_capture_ok,
        "segments": segments,
        "samples": samples,
        "movie_writer": {
            "expected_video_extension": ".avi",
            "launch_requires": ["--write-movie", "--fixed-fps %d" % capture_fps],
            "overlay_active_frame": true,
        },
        "result": "FAIL" if not failures.is_empty() else "PASS",
        "visual_gate": "PONYTAIL_FULL_REVIEW_REQUIRED",
        "promotion": "R20_R8C_60HZ_GAIT_SPEED_CANDIDATE_HOLD" if capture_mode == "r20_60hz" else ("R19_R8C_RUNTIME_INTEGRATION_CANDIDATE_HOLD" if capture_is_custom else "R16_TWO_CYCLE_UNIQUE_MOVE_QA_CANDIDATE_HOLD"),
        "failures": failures,
    }
    var evidence_file := FileAccess.open(ProjectSettings.globalize_path(capture_evidence_path), FileAccess.WRITE)
    evidence_file.store_string(JSON.stringify(evidence, "  ") + "\n")
    evidence_file.close()
    await _finish(stage, prior_fast, prior_aster)


func _make_overlay() -> void:
    var layer := CanvasLayer.new()
    layer.layer = 999
    root.add_child(layer)
    var background := ColorRect.new()
    # Keep the active-frame ledger off the actor so anatomy and sole contact
    # remain unobstructed in every direction.
    background.position = Vector2(620.0, 24.0)
    background.size = Vector2(680.0, 112.0)
    background.color = Color(0.015, 0.025, 0.04, 0.92)
    layer.add_child(background)
    overlay_title = Label.new()
    overlay_title.position = Vector2(638.0, 37.0)
    overlay_title.add_theme_font_size_override("font_size", 18)
    overlay_title.add_theme_color_override("font_color", Color("e3bc75"))
    layer.add_child(overlay_title)
    overlay_detail = Label.new()
    overlay_detail.position = Vector2(638.0, 69.0)
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
    var path := ProjectSettings.globalize_path("%s/%03d_%s_F%02d.png" % [capture_frame_dir, sample_index, direction, frame])
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
    # root vertically per direction so the natural settle + 48-sample two-cycle travel
    # remains inside the native frame even at the enlarged review scale.
    var origin := CAPTURE_ORIGIN
    if VECTORS[sector].y < -0.1:
        origin.y = 480.0
    elif VECTORS[sector].y > 0.1:
        origin.y = 240.0
    return origin


func _is_high_rate_capture() -> bool:
    return capture_mode == "r20_60hz" or capture_mode == "r21_60hz"


func _load_r21_root_tracks(descriptor_path: String) -> void:
    r21_root_tracks.clear()
    if descriptor_path.is_empty():
        _fail("R21 capture requires a project-local descriptor override")
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(descriptor_path))
    if not (parsed is Dictionary):
        _fail("R21 descriptor could not be parsed")
        return
    var sync = (parsed as Dictionary).get("move_root_sync", {})
    if not (sync is Dictionary) or str((sync as Dictionary).get("mode", "")) != "frame_transition_sole_lock":
        _fail("R21 descriptor is missing frame-transition sole-lock mode")
        return
    var raw_tracks = (sync as Dictionary).get("directional_tracks", {})
    if not (raw_tracks is Dictionary):
        _fail("R21 descriptor has no directional sole-lock tracks")
        return
    for direction in DIRECTIONS:
        var track = (raw_tracks as Dictionary).get(direction, {})
        if not (track is Dictionary):
            _fail("R21 descriptor is missing the %s sole-lock track" % direction)
            continue
        var positions = (track as Dictionary).get("frame_positions", [])
        if not (positions is Array) or (positions as Array).size() != AUTHORED_MOVE_FRAMES:
            _fail("R21 descriptor has an invalid %s frame-position track" % direction)
            continue
        r21_root_tracks[direction] = {
            "positions": positions,
            "cycle_advance": float((track as Dictionary).get("cycle_advance", 0.0)),
        }


func _verify_r21_sole_lock_root_track(direction: String, active_frames: Array[int], root_positions: Array[Array]) -> void:
    var track := r21_root_tracks.get(direction, {}) as Dictionary
    var positions := track.get("positions", []) as Array
    var cycle_advance := float(track.get("cycle_advance", 0.0))
    if positions.size() != AUTHORED_MOVE_FRAMES or root_positions.size() != active_frames.size() or active_frames.is_empty():
        _fail("%s R21 root-track evidence has incomplete samples" % direction)
        return
    var sector := DIRECTIONS.find(direction)
    if sector < 0:
        _fail("unknown R21 direction %s" % direction)
        return
    var unit := VECTORS[sector]
    var perpendicular := Vector2(-unit.y, unit.x)
    var base := Vector2(float(root_positions[0][0]), float(root_positions[0][1]))
    var previous_frame := int(active_frames[0])
    var cycle := 0
    var max_error := 0.0
    var max_lateral := 0.0
    var repeated_motion_max := 0.0
    for index in range(active_frames.size()):
        var frame := int(active_frames[index])
        if index > 0 and previous_frame == AUTHORED_MOVE_FRAMES - 1 and frame == 0:
            cycle += 1
        var actual := Vector2(float(root_positions[index][0]), float(root_positions[index][1]))
        var actual_relative := actual - base
        var expected_along := float(positions[frame]) + float(cycle) * cycle_advance
        var actual_along := actual_relative.dot(unit)
        var error: float = abs(actual_along - expected_along)
        max_error = maxf(max_error, error)
        max_lateral = maxf(max_lateral, abs(actual_relative.dot(perpendicular)))
        if index > 0:
            var previous := Vector2(float(root_positions[index - 1][0]), float(root_positions[index - 1][1]))
            var transition := actual.distance_to(previous)
            if frame == previous_frame:
                repeated_motion_max = maxf(repeated_motion_max, transition)
                _require(transition <= 0.02, "%s repeated raster cell F%02d holds the root" % [direction, frame])
            else:
                var expected_delta := expected_along - (float(positions[previous_frame]) + float(cycle) * cycle_advance)
                if previous_frame == AUTHORED_MOVE_FRAMES - 1 and frame == 0:
                    expected_delta = cycle_advance - float(positions[previous_frame]) + float(positions[frame])
                _require(expected_delta > 0.0 and abs(actual_along - (Vector2(float(root_positions[index - 1][0]), float(root_positions[index - 1][1])) - base).dot(unit) - expected_delta) <= 0.02, "%s frame transition F%02d->F%02d follows the authored sole-lock root" % [direction, previous_frame, frame])
        previous_frame = frame
    _require(max_error <= 0.02, "%s R21 root position matches the display-scaled authored sole-lock track (max error %.3fpx)" % [direction, max_error])
    _require(max_lateral <= 0.02, "%s R21 root has no lateral drift (max %.3fpx)" % [direction, max_lateral])
    _require(repeated_motion_max <= 0.02, "%s R21 repeated raster samples do not move the root (max %.3fpx)" % [direction, repeated_motion_max])



func _expected_two_cycle_frames() -> Array[int]:
    var values: Array[int] = []
    for _cycle in range(2):
        values.append_array(_range_int(0, AUTHORED_MOVE_FRAMES))
    return values


func _verify_high_rate_active_frames(direction: String, active_frames: Array[int]) -> void:
    # At native 60Hz a 24fps authored atlas legitimately holds a cell for two
    # or three physics ticks.  Verify the frame cursor advances monotonically
    # through exactly two cycles without accepting an old six-tick still hold,
    # a skipped cell, or a direction reset.
    _require(active_frames.size() == capture_sample_frames, "%s records the full 60Hz two-cycle sample count" % direction)
    if active_frames.is_empty():
        _fail("%s has no active move samples" % direction)
        return
    var counts: Dictionary = {}
    var previous := -1
    var run_length := 0
    var max_run := 0
    var wraps := 0
    for index in range(active_frames.size()):
        var value := int(active_frames[index])
        _require(value >= 0 and value < AUTHORED_MOVE_FRAMES, "%s 60Hz sample %03d stays in authored frame range" % [direction, index])
        counts[value] = int(counts.get(value, 0)) + 1
        if value == previous:
            run_length += 1
        else:
            run_length = 1
            if previous >= 0:
                var expected := (previous + 1) % AUTHORED_MOVE_FRAMES
                _require(value == expected, "%s 60Hz cursor advances without skipping/resetting at sample %03d" % [direction, index])
                if value == 0:
                    wraps += 1
        max_run = maxi(max_run, run_length)
        previous = value
    _require(active_frames[0] == 0, "%s 60Hz capture starts at authored move frame 00" % direction)
    # R20 sampled a legacy cursor before its first 24fps step, so 120 samples
    # contained one visible wrap and ended on F23.  R21 advances the authored
    # frame and matching root in the physics tick immediately before each
    # screenshot; the same 120 samples therefore include the terminal F23->F00
    # transition of the second cycle and end on F00.  Both are exactly two
    # complete 24-frame cycles; keep the distinction explicit in the ledger.
    var expected_wraps := 2 if capture_mode == "r21_60hz" else 1
    _require(wraps == expected_wraps, "%s 60Hz capture contains the expected two-cycle wrap count (%d)" % [direction, expected_wraps])
    for frame in range(AUTHORED_MOVE_FRAMES):
        _require(int(counts.get(frame, 0)) >= 4 and int(counts.get(frame, 0)) <= 6, "%s authored frame %02d has bounded 60Hz hold count" % [direction, frame])
    _require(max_run <= 3, "%s 60Hz capture has no long raster hold (max=%d ticks)" % [direction, max_run])


func _active_frame_sequence_verified(active_frames: Array[int]) -> bool:
    if not _is_high_rate_capture():
        return active_frames == _expected_two_cycle_frames()
    if active_frames.size() != capture_sample_frames or active_frames.is_empty():
        return false
    var expected_last := 0 if capture_mode == "r21_60hz" else AUTHORED_MOVE_FRAMES - 1
    if active_frames[0] != 0 or active_frames[-1] != expected_last:
        return false
    var wraps := 0
    var counts: Dictionary = {}
    var previous := -1
    for value_variant in active_frames:
        var value := int(value_variant)
        if value < 0 or value >= AUTHORED_MOVE_FRAMES:
            return false
        counts[value] = int(counts.get(value, 0)) + 1
        if previous >= 0:
            if value == 0 and previous == AUTHORED_MOVE_FRAMES - 1:
                wraps += 1
            elif value != previous and value != (previous + 1) % AUTHORED_MOVE_FRAMES:
                return false
        previous = value
    var expected_wraps := 2 if capture_mode == "r21_60hz" else 1
    if wraps != expected_wraps:
        return false
    for frame in range(AUTHORED_MOVE_FRAMES):
        var count := int(counts.get(frame, 0))
        if count < 4 or count > 6:
            return false
    return true

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
