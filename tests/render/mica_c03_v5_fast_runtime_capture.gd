extends SceneTree

## Native 1080p in-stage evidence for the MICA C03 V5 fast authored runtime.
## It deliberately captures the actual squad stage and shared projectile path;
## no custom visual scene or gameplay-timing override is introduced.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://artifacts/mica_c03_v5_native_runtime_capture"
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

var failures: Array[String] = []
var overlay_title: Label
var overlay_detail: Label


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    var prior_fast := bool(ProjectSettings.get_setting("sable_visuals/fast_character_runtime", true))
    var prior_aster := bool(ProjectSettings.get_setting("sable_visuals/aster_v4_locomotion_preview", false))
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime", true)
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview", false)
    DisplayServer.window_set_size(VIEWPORT_SIZE)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    _make_overlay()
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(14)
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
    # The Stage HUD follows SquadController's active operator.  This capture
    # must therefore select MICA before drawing evidence, rather than merely
    # hiding the other squad members.
    stage.squad.request_control(2)
    await _frames(2)
    _require(stage.squad.get_active_operator() == mica, "MICA is the active Stage operator for HUD evidence")
    mica.visible = true
    var runtime := mica.get_node_or_null("FastCharacterRuntime") as FastCharacterRuntime
    if runtime == null or not runtime.is_runtime_active():
        _fail("MICA C03 V5 FastCharacterRuntime did not activate in stage")
        await _finish(stage, prior_fast, prior_aster)
        return
    var camera := stage.get_node_or_null("Camera2D") as Camera2D
    if camera:
        camera.position_smoothing_enabled = false
        camera.zoom = Vector2.ONE * 1.36
    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as Node
    if camera_presentation:
        camera_presentation.set_process(false)
    mica.set_movement_bounds(Rect2(340.0, 145.0, 1500.0, 710.0))
    var stride_captures: Array[String] = []
    var cases: Array[Dictionary] = []
    for sector in range(DIRECTIONS.size()):
        _clear_projectiles()
        mica.global_position = Vector2(1100.0, 510.0)
        mica.debug_drive(Vector2.RIGHT, VECTORS[sector])
        # Frame 12 is safely inside UAL's alternating-leg stride rather than
        # the reference/plant frame.  Capture it before Fire switches to the
        # static firing pose, so the evidence proves independent leg motion.
        await _physics_frames(12)
        await process_frame
        if camera:
            camera.global_position = mica.global_position
        var sector_ok := mica.facing_sector == sector
        _require(sector_ok, "%s aim resolves the matching authored sector" % DIRECTIONS[sector])
        _set_overlay(
            "MICA C03 V5  |  %s  |  UAL LEG STRIDE" % DIRECTIONS[sector],
            "ImageGen authority → Blender+UAL · independent screen-left/right lower-leg transforms, move frame 12/24",
        )
        var stride_capture := await _capture("MICA_C03_V5_%s_MOVE_STRIDE_1920X1080.png" % DIRECTIONS[sector])
        stride_captures.append(stride_capture)
        var fired := mica.debug_fire_once()
        _require(fired, "%s shot begins during movement" % DIRECTIONS[sector])
        var projectile := _find_projectile(mica)
        # Schema 2 switches to the visible fire cell synchronously with the
        # shot.  Compare birth to that fire-frame socket, not to the preceding
        # move-frame socket, or every legitimate moving shot becomes a false
        # mismatch.
        var muzzle := runtime.get_authored_muzzle_global_position()
        var birth_error := projectile.global_position.distance_to(muzzle) if projectile else INF
        _require(projectile != null and birth_error < 0.05, "%s projectile birth matches the authored muzzle" % DIRECTIONS[sector])
        _set_overlay(
            "MICA C03 V5  |  %s  |  MOVE + PULSE CARBINE FIRE" % DIRECTIONS[sector],
            "ImageGen authority → Blender+UAL motion → Fast runtime · muzzle/projectile error %.4f px" % birth_error,
        )
        var fire_capture := await _capture("MICA_C03_V5_%s_MOVE_FIRE_1920X1080.png" % DIRECTIONS[sector])
        cases.append({
            "direction": DIRECTIONS[sector],
            "authored_sector": mica.facing_sector,
            "fired": fired,
            "projectile_birth_error_px": birth_error,
            "stride_capture": stride_capture,
            "fire_capture": fire_capture,
        })
        _clear_projectiles()
        await _physics_frames(28)
    var contact := _make_contact(stride_captures)
    var evidence := {
        "schema": 1,
        "actor_id": "CHR_PROTO_03",
        "costume_id": "MICA_RECON_C03",
        "runtime_descriptor": "data/character_pipeline/mica_runtime.json",
        "native_capture_resolution": [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y],
        "capture_type": "actual StoryStage01 runtime, UAL lower-leg stride then firing in all eight aim sectors",
        "projectile_visual_revision": "MICA single mint pulse uses the active frame-tracked muzzle; origin and collision behavior remain coupled",
        "cases": cases,
        "contact_sheet": contact,
        "contact_sheet_resolution": [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y],
        "result": "FAIL" if not failures.is_empty() else "PASS",
        "visual_gate": "USER_REVIEW_REQUIRED",
        "failures": failures,
    }
    var evidence_file := FileAccess.open(ProjectSettings.globalize_path(OUT_DIR + "/MICA_C03_V5_FAST_RUNTIME_EVIDENCE.json"), FileAccess.WRITE)
    evidence_file.store_string(JSON.stringify(evidence, "  ") + "\n")
    evidence_file.close()
    await _finish(stage, prior_fast, prior_aster)


func _make_overlay() -> void:
    var layer := CanvasLayer.new()
    layer.layer = 120
    root.add_child(layer)
    var background := ColorRect.new()
    background.position = Vector2(120.0, 42.0)
    background.size = Vector2(1230.0, 78.0)
    background.color = Color(0.015, 0.025, 0.04, 0.92)
    layer.add_child(background)
    overlay_title = Label.new()
    overlay_title.position = Vector2(142.0, 50.0)
    overlay_title.add_theme_font_size_override("font_size", 25)
    overlay_title.add_theme_color_override("font_color", Color("e3bc75"))
    layer.add_child(overlay_title)
    overlay_detail = Label.new()
    overlay_detail.position = Vector2(142.0, 84.0)
    overlay_detail.add_theme_font_size_override("font_size", 16)
    overlay_detail.add_theme_color_override("font_color", Color("e8edf3"))
    layer.add_child(overlay_detail)


func _set_overlay(title: String, detail: String) -> void:
    overlay_title.text = title
    overlay_detail.text = detail


func _capture(filename: String) -> String:
    var was_paused := paused
    paused = true
    await process_frame
    RenderingServer.force_draw()
    var image := root.get_texture().get_image()
    paused = was_paused
    if image == null or image.is_empty() or image.get_size() != VIEWPORT_SIZE:
        _fail("invalid native 1080p capture: " + filename)
        return ""
    var path := ProjectSettings.globalize_path(OUT_DIR + "/" + filename)
    var error := image.save_png(path)
    if error != OK:
        _fail("capture save failure: " + filename)
        return ""
    print("CAPTURED: " + path)
    return path


func _make_contact(paths: Array[String]) -> String:
    var contact := Image.create(VIEWPORT_SIZE.x, VIEWPORT_SIZE.y, false, Image.FORMAT_RGBA8)
    contact.fill(Color("08111b"))
    var cell_size := Vector2i(480, 360)
    for index in range(paths.size()):
        var source := Image.new()
        if source.load(paths[index]) != OK or source.get_size() != VIEWPORT_SIZE:
            _fail("invalid contact source %d" % index)
            continue
        var crop := source.get_region(Rect2i(430, 160, 1060, 810))
        crop.resize(cell_size.x, cell_size.y, Image.INTERPOLATE_LANCZOS)
        contact.blit_rect(crop, Rect2i(Vector2i.ZERO, cell_size), Vector2i(index % 4, index / 4) * cell_size)
    var path := ProjectSettings.globalize_path(OUT_DIR + "/MICA_C03_V5_8_DIRECTION_STAGE_CONTACT_1920X1080.png")
    if contact.save_png(path) != OK:
        _fail("contact save failure")
        return ""
    return path


func _find_projectile(actor: OperatorActor) -> PrototypeProjectile:
    for child in root.get_children():
        if child is PrototypeProjectile and (child as PrototypeProjectile).owner_actor == actor:
            return child as PrototypeProjectile
    return null


func _clear_projectiles() -> void:
    for child in root.get_children():
        if child is PrototypeProjectile:
            child.queue_free()


func _frames(count: int) -> void:
    for _index in range(count):
        await process_frame


func _physics_frames(count: int) -> void:
    for _index in range(count):
        await physics_frame


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
    print("MICA_C03_V5_FAST_RUNTIME_CAPTURE: " + ("PASS" if failures.is_empty() else "FAIL"))
    quit(0 if failures.is_empty() else 1)
