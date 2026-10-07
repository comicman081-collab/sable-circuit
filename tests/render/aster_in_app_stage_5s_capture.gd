extends SceneTree

## Five-second in-app stage capture.  This drives the real production scene,
## CharacterBody2D, 16-way ASTER aim/fire layer, camera, HUD, and projectile
## renderer; it does not replace gameplay authority or author new art.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const FEATURE_SETTING := "sable_visuals/aster_v4_locomotion_preview"
const OUT_DIR := "res://artifacts/in_app_stage_video/frames"
const VIEWPORT_SIZE := Vector2i(1920, 1080)
const CAPTURE_FPS := 30
const CAPTURE_FRAMES := 150
const MOVE_VECTOR := Vector2.RIGHT
const FIRE_EVERY_FRAMES := 7

var overlay: Label


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    var previous_setting := bool(ProjectSettings.get_setting(FEATURE_SETTING, false))
    ProjectSettings.set_setting(FEATURE_SETTING, true)
    DisplayServer.window_set_size(VIEWPORT_SIZE)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))

    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(20)

    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.queue_free()
    await _frames(2)

    var actor := stage.squad.get_active_operator() as OperatorActor
    if actor == null or actor.operator_id != "CHR_PROTO_01":
        push_error("ASTER in-app capture could not resolve the active operator")
        ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
        quit(1)
        return

    for operator in stage.squad.operators:
        if operator != actor:
            operator.downed_state = true
            operator.velocity = Vector2.ZERO
            operator.visible = false
    actor.visible = true
    actor.set_movement_bounds(Rect2(260.0, 120.0, 1740.0, 820.0))
    actor.global_position = Vector2(960.0, 540.0)
    actor.ammo = actor.magazine_size
    actor.debug_drive(MOVE_VECTOR, MOVE_VECTOR)
    _make_overlay()
    await _frames(4)

    for frame in range(CAPTURE_FRAMES):
        var angle := TAU * float(frame) / float(CAPTURE_FRAMES)
        var aim := Vector2.from_angle(angle)
        actor.debug_drive(MOVE_VECTOR, aim)
        if frame % FIRE_EVERY_FRAMES == 0:
            actor.debug_fire_once()
        _set_overlay(actor, frame)
        await _physics_and_render_frame()
        var image := get_root().get_viewport().get_texture().get_image()
        if image == null or image.get_size() != VIEWPORT_SIZE:
            push_error("in-app capture produced an unexpected viewport size")
            ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
            quit(1)
            return
        var output := ProjectSettings.globalize_path("%s/frame_%04d.png" % [OUT_DIR, frame])
        var error := image.save_png(output)
        if error != OK:
            push_error("failed to save in-app capture frame %d: %s" % [frame, error])
            ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
            quit(1)
            return

    actor.debug_drive(Vector2.ZERO, actor.aim_world)
    await _frames(2)
    ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
    print("ASTER_IN_APP_STAGE_5S_CAPTURE: PASS frames=%d resolution=%dx%d" % [CAPTURE_FRAMES, VIEWPORT_SIZE.x, VIEWPORT_SIZE.y])
    quit(0)


func _make_overlay() -> void:
    overlay = Label.new()
    overlay.position = Vector2(34.0, 24.0)
    overlay.add_theme_font_size_override("font_size", 24)
    overlay.modulate = Color("8ff4ff")
    overlay.z_index = 100
    root.add_child(overlay)


func _set_overlay(actor: OperatorActor, frame: int) -> void:
    if overlay == null:
        return
    overlay.text = "IN-APP STAGE  |  ASTER MOVE + FIRE  |  %0.2fs / 5.00s  |  AIM %03d°" % [float(frame) / float(CAPTURE_FPS), int(round(rad_to_deg(actor.aim_world.angle()))) % 360]


func _frames(count: int) -> void:
    for _index in range(count):
        await process_frame


func _physics_and_render_frame() -> void:
    await physics_frame
    await process_frame
    await RenderingServer.frame_post_draw
