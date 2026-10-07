extends "res://tests/render/battle_video_10s_capture.gd"
## MovieWriter captures the engine's real mixed audio alongside native frames.
## Scripted input only: no damage/HP/AI/animation overrides or post-added SFX.
func run() -> void:
    var output := "res://qa/sfx_integration_20260919/"
    root.size = SIZE
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(SIZE)
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    Engine.physics_ticks_per_second = FPS
    Input.use_accumulated_input = false
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    stage.battle_preview = true
    root.add_child(stage)
    current_scene = stage
    for i in range(8): await process_frame
    stage.start_battle_preview(4)
    var sfx: Node = preload("res://scripts/audio/combat_sfx_bank.gd").manager(self)
    sfx.debug_trace = true
    for actor in stage.squad.operators:
        actor.projectile_spawned.connect(record_shot)
    var start_frame := Engine.get_frames_drawn()
    for frame in range(FRAME_COUNT):
        var keys: Array[int] = []
        if frame < 90: keys = [KEY_D]
        elif frame < 150: keys = [KEY_S]
        elif frame < 210: keys = [KEY_A]
        elif frame == 210: keys = [KEY_R]
        elif frame >= 300 and frame < 360: keys = [KEY_D]
        elif frame >= 360 and frame < 420: keys = [KEY_W, KEY_SHIFT]
        set_keys(keys)
        aim_at_enemy(stage)
        set_fire(frame < 210 or (frame >= 300 and frame < 460))
        await process_frame
        await RenderingServer.frame_post_draw
        if frame in [30, 240, 540]:
            var picture := root.get_texture().get_image()
            assert(picture.get_size() == SIZE)
            picture.save_png(output.path_join("battle_sfx_%04d.png" % frame))
        if frame % 120 == 0: print("SFX_CAPTURE_FRAME ", frame)
    set_keys([])
    set_fire(false)
    var report := {"native_resolution":[1920,1080], "frames":600, "fps":60,
        "capture_start_render_frame":start_frame, "capture_end_render_frame":Engine.get_frames_drawn(),
        "scene":"res://scenes/mission/StoryStage01.tscn", "encounter":4, "normal_ai_and_damage":true,
        "clock":"Godot MovieWriter fixed 60 Hz; not wall-clock performance footage",
        "audio":"Actual Godot AudioServer mix, not post-added soundtrack", "shots":shots,
        "audio_events":sfx.debug_snapshot(), "auditory_approval":false}
    var file := FileAccess.open(output.path_join("battle_capture.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report,"  ")); file.close()
    print("SFX_CAPTURE_COMPLETE shots=", shots)
    quit()
