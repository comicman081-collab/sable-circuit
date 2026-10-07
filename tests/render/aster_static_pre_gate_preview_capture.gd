extends SceneTree

const PREVIEW_SCENE := preload("res://scenes/qa/AsterStaticPreGatePreview.tscn")
const OUT_PATH := "res://artifacts/runtime_capture/ASTER_STATIC_PRE_GATE_QA.png"

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    DisplayServer.window_set_size(Vector2i(1280, 720))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_PATH.get_base_dir()))
    var preview := PREVIEW_SCENE.instantiate() as AsterStaticPreGatePreview
    root.add_child(preview)
    current_scene = preview
    await process_frame
    await process_frame
    var contract := preview.debug_contract()
    if not bool(contract.get("pre_gate", false)) or not bool(contract.get("nonpromoted", false)) or not bool(contract.get("uses_mask_derived_rgba", false)):
        push_error("ASTER pre-gate preview contract is invalid: " + str(contract))
        quit(1)
        return
    # `frame_post_draw` is not emitted by Godot's headless backend on every
    # machine. Force the completed frame instead; this keeps capture bounded.
    RenderingServer.force_draw()
    var image := root.get_texture().get_image()
    var err := image.save_png(ProjectSettings.globalize_path(OUT_PATH))
    if err != OK:
        push_error("ASTER pre-gate runtime capture failed: " + str(err))
        quit(1)
        return
    print("ASTER_STATIC_PRE_GATE_CAPTURE: PASS " + ProjectSettings.globalize_path(OUT_PATH))
    quit(0)
