extends SceneTree
const SourceViewport = preload("res://scripts/animation/source_skin_viewport.gd")

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    root.size = Vector2i(1920, 1080)
    var background := ColorRect.new()
    background.color = Color("17252e")
    background.size = Vector2(1920, 1080)
    root.add_child(background)
    var surface: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://SOURCE_SKIN.json"))
    var motion: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://MOTION_PACK.json"))
    var texture := ImageTexture.create_from_image(Image.load_from_file("res://SOURCE_RGBA.png"))
    var actor = SourceViewport.new()
    root.add_child(actor)
    actor.position = Vector2(960, 710)
    if not actor.configure(surface, motion, texture, 224.0 / 1.72):
        push_error(actor.error)
        quit(1)
        return
    if not actor.configure_coherent_recoil(0.018, 0.012):
        push_error(actor.error)
        quit(1)
        return
    var phases := [0.0, 0.25, 0.5, 0.75]
    var records: Array = []
    for phase: float in phases:
        actor.view.motion_player.phase = phase
        actor.view.motion_player.set_motion_intent(Vector2.RIGHT, true)
        if not actor.view.motion_player.commit_displacement(Vector2(0.01, 0), Vector2.RIGHT, 1.0 / 60.0, true):
            push_error(actor.view.motion_player.error)
            quit(1)
            return
        for firing: bool in [false, true]:
            if firing:
                actor.view.motion_player.trigger_recoil()
            await process_frame
            await RenderingServer.frame_post_draw
            var image := root.get_texture().get_image()
            if image == null or image.get_size() != Vector2i(1920, 1080):
                push_error("NATIVE_GPU_CAPTURE_REQUIRED")
                quit(1)
                return
            var filename := "GPU_PHASE_%02d_%s.png" % [roundi(phase * 100), "FIRE" if firing else "RUN"]
            if image.save_png("res://" + filename) != OK:
                quit(1)
                return
            var launch: Dictionary = actor.current_launch_2d()
            records.append({"image": filename, "phase": actor.view.motion_player.phase,
                "firing": firing, "muzzle": [launch["origin"].x, launch["origin"].y],
                "direction": [launch["direction"].x, launch["direction"].y]})
        actor.view.motion_player.recoil_left = 0
    var file := FileAccess.open("res://RESULT.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"captures": records, "native_resolution": [1920,1080],
        "production_ready": false, "scope": "one E source-view GPU gait/recoil capture; not combat or eight directions"}, "  "))
    file.close()
    quit(0)
