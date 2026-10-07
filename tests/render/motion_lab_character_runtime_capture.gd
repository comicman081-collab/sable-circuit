extends SceneTree

## Native 1080p map-scale evidence for the two current Motion Studio packages.
## This is an app integration capture, not a replacement source-art review.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://qa/motion_lab_runtime_integration_20260911"
const OUT_FILE := "story_stage_aster_mica_1920x1080.png"

var stage: StoryStage01
var failed := false


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    root.size = Vector2i(1920, 1080)
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))

    stage = STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _settle(12)

    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    if camera_presentation:
        camera_presentation.set_process(false)
    stage.set_process(false)
    stage.squad.set_process(false)

    var aster := _find_operator("CHR_PROTO_01")
    var mica := _find_operator("CHR_PROTO_03")
    var rook := _find_operator("CHR_PROTO_02")
    if aster == null or mica == null:
        _fail("StoryStage is missing ASTER or MICA")
        await _finish()
        return
    if rook:
        rook.visible = false

    var featured: Array[OperatorActor] = [aster, mica]
    for actor in featured:
        actor.set_movement_bounds(Rect2(-10000.0, -10000.0, 20000.0, 20000.0))
        actor.visible = true
    aster.global_position = Vector2(1010.0, 520.0)
    mica.global_position = Vector2(1145.0, 570.0)
    aster.debug_drive(Vector2.RIGHT, Vector2(1.0, -0.24).normalized())
    mica.debug_drive(Vector2.ZERO, Vector2(-0.72, -0.42).normalized())

    stage.camera.enabled = true
    stage.camera.position_smoothing_enabled = false
    stage.camera.global_position = Vector2(1085.0, 520.0)
    stage.camera.zoom = Vector2.ONE * 1.36
    await _settle(10)

    var aster_runtime := aster.get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
    var mica_runtime := mica.get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
    if aster_runtime == null or mica_runtime == null or not aster_runtime.is_runtime_active() or not mica_runtime.is_runtime_active():
        _fail("Motion Studio runtime did not remain active for both map actors")
    else:
        var aster_contract := aster_runtime.debug_contract()
        var mica_contract := mica_runtime.debug_contract()
        if not is_equal_approx(float(aster_contract.get("display_height_px", 0.0)), 72.0) or not is_equal_approx(float(mica_contract.get("display_height_px", 0.0)), 72.0):
            _fail("Motion Studio display scale diverged from 72px map contract")
        print("MOTION_LAB_MAP_CAPTURE ASTER=%s MICA=%s" % [aster_contract, mica_contract])

    # The capture runner uses Godot's regular renderer (hidden window) rather
    # than the headless dummy driver, which has no viewport texture to read.
    var viewport_texture := root.get_texture()
    if viewport_texture == null:
        _fail("capture renderer exposed no viewport texture")
        await _finish()
        return
    var image := viewport_texture.get_image()
    if image == null:
        _fail("capture renderer returned no viewport image")
        await _finish()
        return
    if image.get_width() != 1920 or image.get_height() != 1080:
        _fail("capture is not native 1920x1080: %dx%d" % [image.get_width(), image.get_height()])
    else:
        var path := ProjectSettings.globalize_path(OUT_DIR + "/" + OUT_FILE)
        var err := image.save_png(path)
        if err != OK:
            _fail("could not save capture: %s (%d)" % [path, err])
        else:
            print("MOTION_LAB_MAP_CAPTURED: " + path)
    await _finish()


func _find_operator(actor_id: String) -> OperatorActor:
    for actor in stage.squad.operators:
        if actor.operator_id == actor_id:
            return actor
    return null


func _settle(frames: int) -> void:
    for _frame in range(frames):
        await process_frame


func _fail(message: String) -> void:
    failed = true
    push_error(message)


func _finish() -> void:
    if stage != null:
        stage.queue_free()
    await process_frame
    print("MOTION_LAB_MAP_CAPTURE: " + ("FAIL" if failed else "PASS"))
    quit(1 if failed else 0)
