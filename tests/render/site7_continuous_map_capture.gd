extends SceneTree

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT := "res://qa/continuous_map_20260923"

func _init() -> void:
    call_deferred("run")

func _frames(count: int = 8) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func _capture(label: String) -> bool:
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    if image.get_size() != Vector2i(1920, 1080):
        push_error("Capture size is not native 1080p: " + str(image.get_size()))
        return false
    var path := ProjectSettings.globalize_path(OUT + "/" + label + ".png")
    return image.save_png(path) == OK

func run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name() != "headless": DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    root.add_child(stage)
    await _frames(20)
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    var success: bool = bool(stage.battlefield.world_ready) and art.debug_streaming_state().visible_ids.size() == 15
    success = await _capture("entry_native_1920x1080") and success
    var aster := stage.squad.get_active_operator()
    aster.debug_drive(Vector2.LEFT, Vector2.LEFT)
    await _frames(9)
    success = await _capture("aster_lateral_early_native_1920x1080") and success
    await _frames(20)
    success = await _capture("aster_lateral_late_native_1920x1080") and success
    aster.debug_drive(Vector2.ZERO, Vector2.LEFT)
    await _frames(3)
    var first: Dictionary = stage.main_route[0]
    var second: Dictionary = stage.main_route[1]
    var halfway := Vector2(float(first.x),float(first.y)).lerp(Vector2(float(second.x),float(second.y)),0.5)
    stage.squad.get_active_operator().global_position = halfway
    await _frames(120)
    success = await _capture("connector_native_1920x1080") and success
    stage.battle_preview = true
    stage.start_battle_preview(1)
    await _frames(30)
    success = await _capture("combat_native_1920x1080") and success
    print("SITE7_CONTINUOUS_MAP_CAPTURE: ", "PASS" if success else "FAIL")
    stage.queue_free()
    await _frames(2)
    quit(0 if success else 1)
