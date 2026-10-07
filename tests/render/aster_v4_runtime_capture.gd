extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://artifacts/aster_v4_runtime_capture"
const FEATURE_SETTING := "sable_visuals/aster_v4_locomotion_preview"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const VECTORS: Array[Vector2] = [
    Vector2.RIGHT, Vector2(0.70710678, 0.70710678), Vector2.DOWN, Vector2(-0.70710678, 0.70710678),
    Vector2.LEFT, Vector2(-0.70710678, -0.70710678), Vector2.UP, Vector2(0.70710678, -0.70710678),
]

var failed := false


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    ProjectSettings.set_setting(FEATURE_SETTING, true)
    DisplayServer.window_set_size(Vector2i(1280, 720))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(12)

    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.queue_free()
    await _frames(2)
    var actor := stage.squad.get_active_operator() as OperatorActor
    var preview := actor.get_node_or_null("AsterV4LocomotionPreview") as AsterV4LocomotionPreview if actor else null
    if actor == null or preview == null or not bool(preview.debug_contract().get("active", false)):
        push_error("ASTER V4 capture cannot resolve active preview")
        quit(1)
        return

    for operator in stage.squad.operators:
        operator.visible = operator == actor
    actor.set_movement_bounds(Rect2(720.0, 280.0, 760.0, 440.0))
    actor.global_position = Vector2(1100.0, 500.0)
    var camera := stage.get_node("Camera2D") as Camera2D
    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as Node
    if camera_presentation:
        camera_presentation.set_process(false)
    camera.position_smoothing_enabled = false
    camera.global_position = actor.global_position
    camera.zoom = Vector2.ONE * 1.8

    for sector in range(DIRECTIONS.size()):
        actor.global_position = Vector2(1100.0, 500.0)
        actor.debug_drive(Vector2.RIGHT, VECTORS[sector])
        await _physics_frames(24)
        camera.global_position = actor.global_position
        var contract := preview.debug_contract()
        if int(contract.get("sector", -1)) != sector:
            push_error("ASTER V4 capture sector mismatch expected=%d actual=%s" % [sector, str(contract.get("sector", -1))])
            failed = true
            continue
        await _save("MOVE_%s_RUNTIME.png" % DIRECTIONS[sector])

    actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    await _physics_frames(3)
    var fired := actor.debug_fire_once()
    var captured_flash := false
    if fired:
        for _index in range(60):
            await process_frame
            var contract := preview.debug_contract()
            if bool(contract.get("muzzle_vfx_visible", false)):
                if int(contract.get("last_frame", -1)) != 2:
                    push_error("runtime muzzle VFX escaped the shot frame")
                    failed = true
                camera.global_position = actor.global_position
                await _save("FIRE_E_RUNTIME_SEPARATE_VFX.png")
                captured_flash = true
                break
    else:
        push_error("runtime fire capture could not trigger the authoritative actor shot")
        failed = true
    if not captured_flash:
        push_error("runtime fire capture missed separate muzzle VFX")
        failed = true

    actor.debug_stop_drive()
    if failed:
        print("ASTER_V4_RUNTIME_CAPTURE: FAIL")
        quit(1)
        return
    print("ASTER_V4_RUNTIME_CAPTURE: PASS " + ProjectSettings.globalize_path(OUT_DIR))
    quit(0)


func _save(filename: String) -> void:
    RenderingServer.force_draw()
    var viewport_texture := root.get_texture()
    if viewport_texture == null:
        push_error("runtime capture backend exposed no viewport texture: " + filename)
        failed = true
        return
    var image := viewport_texture.get_image()
    if image == null or image.is_empty() or image.get_width() != 1280 or image.get_height() != 720:
        push_error("invalid runtime capture image: " + filename)
        failed = true
        return
    var path := ProjectSettings.globalize_path(OUT_DIR + "/" + filename)
    var error := image.save_png(path)
    if error != OK:
        push_error("capture write failed: %s error=%d" % [path, error])
        failed = true
        return
    print("CAPTURED: " + path)


func _frames(count: int) -> void:
    for _index in range(count):
        await process_frame


func _physics_frames(count: int) -> void:
    for _index in range(count):
        await physics_frame
