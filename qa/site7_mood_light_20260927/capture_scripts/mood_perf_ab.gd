extends SceneTree
## Same-session rotated A/B of the SITE-7 mood light: mood on (lit plates, void
## masks, abyss backdrop) vs off (the plates as before, black clear colour), in
## mission 1 views, vsync off. Writes JSON to --out.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var out := "res://.cache/mood/perf_ab.json"
var rounds := 3
var seconds := 3.0

func _init() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.substr(6)
        if arg.begins_with("--rounds="): rounds = int(arg.substr(9))
    call_deferred("run")

func settle(frames: int) -> void:
    for i in range(frames):
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
    var abyss := art.get_node_or_null("AbyssBackdrop") as Node2D
    if abyss:
        abyss.visible = on
        abyss.set_process(on)

func measure(viewport_rid: RID) -> Dictionary:
    await settle(30)
    var frames := 0
    var gpu := 0.0
    var cpu := 0.0
    var start := Time.get_ticks_usec()
    while Time.get_ticks_usec() - start < int(seconds * 1000000.0):
        await process_frame
        frames += 1
        gpu += RenderingServer.viewport_get_measured_render_time_gpu(viewport_rid)
        cpu += RenderingServer.viewport_get_measured_render_time_cpu(viewport_rid)
    var elapsed := float(Time.get_ticks_usec() - start) / 1000000.0
    return {"fps": snappedf(frames / elapsed, 0.1), "gpu_ms": snappedf(gpu / frames, 0.001), "render_cpu_ms": snappedf(cpu / frames, 0.001)}

func run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    Engine.max_fps = 0
    var viewport_rid := root.get_viewport_rid()
    RenderingServer.viewport_set_measure_render_time(viewport_rid, true)
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    stage.battle_preview = true
    root.add_child(stage)
    await settle(10)
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    stage.start_battle_preview(1)
    await settle(5)
    # Freeze every actor so each view draws the same scene in both arms.
    for node in stage.find_children("*", "CharacterBody2D", true, false):
        node.set_physics_process(false)
        node.set_process(false)
    var views: Array[Dictionary] = []
    for room_id in ["R02_CORRIDOR", "R04_CONTAINMENT", "R05_CORE"]:
        views.append({"name": room_id, "at": art.get_room_plate(room_id).global_position})
    for index in [2, 4]:
        views.append({"name": "C%d" % index, "at": art.get_connector_plate(index).global_position})
    var camera := stage.camera
    var runs: Array = []
    for round_index in range(rounds):
        for view_index in range(views.size()):
            var view: Dictionary = views[view_index]
            camera.global_position = view.at
            camera.reset_smoothing()
            var order := [true, false] if (round_index + view_index) % 2 == 0 else [false, true]
            for on in order:
                set_mood(art, on)
                var result := await measure(viewport_rid)
                result.merge({"round": round_index + 1, "view": view.name, "mood": on})
                runs.append(result)
                print("MOOD_AB ", JSON.stringify(result))
    var summary := {}
    for on in [true, false]:
        var picked := runs.filter(func(row: Dictionary) -> bool: return row.mood == on)
        var fps := 0.0
        var gpu := 0.0
        for row in picked:
            fps += float(row.fps)
            gpu += float(row.gpu_ms)
        summary["mood_on" if on else "mood_off"] = {"mean_fps": snappedf(fps / picked.size(), 0.1), "mean_gpu_ms": snappedf(gpu / picked.size(), 0.001), "samples": picked.size()}
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"mission": "MIS_CH01_01", "native_resolution": [1920, 1080], "vsync": false, "rounds": rounds, "seconds_per_sample": seconds,
            "adapter": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(), "summary": summary, "runs": runs}, "  "))
    file.close()
    print("MOOD_AB_SUMMARY ", JSON.stringify(summary))
    quit(0)
