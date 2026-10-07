extends SceneTree
## Diagnostic: mission 1 combat rooms with squad and robots, mood on vs off.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var out := "res://.cache/mood/actors"

func _init() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.substr(6)
    call_deferred("run")

func settle(frames: int) -> void:
    for i in range(frames):
        await physics_frame
        await process_frame

func set_mood(art: Node, on: bool) -> void:
    for sprite in art.find_children("*", "Sprite2D", true, false):
        var mat := (sprite as Sprite2D).material as ShaderMaterial
        if mat == null: continue
        if not sprite.has_meta("mood_saved"):
            sprite.set_meta("mood_saved", [mat.get_shader_parameter("mood"), mat.get_shader_parameter("use_void_mask")])
        var saved: Array = sprite.get_meta("mood_saved")
        mat.set_shader_parameter("mood", saved[0] if on else false)
        mat.set_shader_parameter("use_void_mask", saved[1] if on else false)
    var abyss := art.get_node_or_null("AbyssBackdrop")
    if abyss: abyss.visible = on

func run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    stage.battle_preview = true
    root.add_child(stage)
    await settle(6)
    var art := stage.get_node("RoomArtLayer")
    for step in [1, 3, 4]:
        stage.start_battle_preview(step)
        await settle(40)
        for on in [false, true]:
            set_mood(art, on)
            await settle(2)
            await RenderingServer.frame_post_draw
            var image := root.get_texture().get_image()
            image.save_png(ProjectSettings.globalize_path(out + "/step%d_%s.png" % [step, "mood" if on else "flat"]))
    print("MOOD_ACTOR_CAPTURE done")
    quit(0)
