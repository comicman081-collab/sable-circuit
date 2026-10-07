extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://artifacts/aster_projectile_v6_runtime_capture"
const FEATURE_SETTING := "sable_visuals/aster_v4_locomotion_preview"
const CAPTURE_SIZE := Vector2i(1920, 1080)
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

var failed := false


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    ProjectSettings.set_setting(FEATURE_SETTING, true)
    DisplayServer.window_set_size(CAPTURE_SIZE)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(12)
    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.queue_free()
    await _frames(2)

    var actor := stage.squad.get_active_operator() as OperatorActor
    if actor == null or actor.operator_id != "CHR_PROTO_01":
        push_error("ASTER projectile capture cannot resolve active ASTER")
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
        actor.debug_drive(Vector2.ZERO, VECTORS[sector])
        await _physics_frames(3)
        if not actor.debug_fire_once():
            push_error("ASTER projectile capture could not trigger sector %s" % DIRECTIONS[sector])
            failed = true
            continue

        var captured := false
        for _index in range(30):
            await physics_frame
            for child in root.get_children():
                if not (child is PrototypeProjectile):
                    continue
                var projectile := child as PrototypeProjectile
                var contract := projectile.debug_visual_contract()
                if not bool(contract.get("aster_v6_sprite_active", false)):
                    continue
                if projectile.direction.dot(VECTORS[sector]) < 0.999:
                    continue
                var distance := projectile.global_position.distance_to(actor.global_position)
                if distance < 125.0 or distance > 440.0:
                    continue
                camera.global_position = actor.global_position
                await _save("ASTER_PROJECTILE_V6_%s_NATIVE_RUNTIME.png" % DIRECTIONS[sector])
                captured = true
                break
            if captured:
                break
        if not captured:
            push_error("ASTER projectile V6 never reached capture window in sector %s" % DIRECTIONS[sector])
            failed = true
        for child in root.get_children():
            if child is PrototypeProjectile:
                child.queue_free()
        await process_frame

    actor.debug_stop_drive()
    if failed:
        print("ASTER_PROJECTILE_V6_RUNTIME_CAPTURE: FAIL")
        quit(1)
        return
    print("ASTER_PROJECTILE_V6_8_DIRECTION_RUNTIME_CAPTURE: PASS %dx%d %s" % [CAPTURE_SIZE.x, CAPTURE_SIZE.y, ProjectSettings.globalize_path(OUT_DIR)])
    quit(0)


func _save(filename: String) -> void:
    RenderingServer.force_draw()
    var viewport_texture := root.get_texture()
    if viewport_texture == null:
        push_error("runtime capture backend exposed no viewport texture")
        failed = true
        return
    var image := viewport_texture.get_image()
    if image == null or image.is_empty() or image.get_size() != CAPTURE_SIZE:
        push_error("invalid runtime capture image: expected %s, got %s" % [CAPTURE_SIZE, image.get_size() if image != null else Vector2i.ZERO])
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
