extends SceneTree
## Same-session rotated A/B/C/D/E of the abyss styles: each mission's abyss row drawn
## behind mission 1's void-heavy views (connector 4, R06), vsync off, native 1080p.
## The style order rotates per round and view. Writes JSON to --out.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const MOOD := preload("res://scripts/missions/site7_mood.gd")
var out := "res://.cache/structure/abyss_style_perf.json"
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

func measure(viewport_rid: RID) -> Dictionary:
    await settle(30)
    var frames := 0
    var gpu := 0.0
    var start := Time.get_ticks_usec()
    while Time.get_ticks_usec() - start < int(seconds * 1000000.0):
        await process_frame
        frames += 1
        gpu += RenderingServer.viewport_get_measured_render_time_gpu(viewport_rid)
    var elapsed := float(Time.get_ticks_usec() - start) / 1000000.0
    return {"fps": snappedf(frames / elapsed, 0.1), "gpu_ms": snappedf(gpu / frames, 0.001)}

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
    for node in stage.find_children("*", "CharacterBody2D", true, false):
        node.set_physics_process(false)
        node.set_process(false)
    var backdrop := art.get_node("AbyssBackdrop")
    var mat := backdrop.material as ShaderMaterial
    var keep := [mat.get_shader_parameter("glow"), mat.get_shader_parameter("glow_color"), mat.get_shader_parameter("glow_count")]
    var rows := {}
    for number in range(1, 6):
        var row: Dictionary = MOOD.abyss("MIS_CH01_%02d" % number).duplicate(true)
        rows[str(row.get("style", "shaft"))] = row
    var styles: Array = rows.keys()
    var views := [{"name": "C4", "at": art.get_connector_plate(4).global_position},
            {"name": "R06", "at": art.get_room_plate("R06_EXTRACTION").global_position + Vector2(300, 150)}]
    var runs: Array = []
    for round_index in range(rounds):
        for view_index in range(views.size()):
            stage.camera.global_position = views[view_index].at
            stage.camera.reset_smoothing()
            for k in range(styles.size()):
                var style: String = styles[(k + round_index + view_index) % styles.size()]
                backdrop.call("setup", backdrop.get("_rect"), rows[style], [] as Array[Dictionary])
                mat = backdrop.material as ShaderMaterial
                mat.set_shader_parameter("glow", keep[0])
                mat.set_shader_parameter("glow_color", keep[1])
                mat.set_shader_parameter("glow_count", keep[2])
                var result := await measure(viewport_rid)
                result.merge({"round": round_index + 1, "view": views[view_index].name, "style": style})
                runs.append(result)
                print("ABYSS_AB ", JSON.stringify(result))
    var summary := {}
    for style in styles:
        var picked := runs.filter(func(row: Dictionary) -> bool: return row.style == style)
        var fps := 0.0
        var gpu := 0.0
        for row in picked:
            fps += float(row.fps)
            gpu += float(row.gpu_ms)
        summary[style] = {"mean_fps": snappedf(fps / picked.size(), 0.1), "mean_gpu_ms": snappedf(gpu / picked.size(), 0.001), "samples": picked.size()}
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"views_mission": "MIS_CH01_01", "native_resolution": [1920, 1080], "vsync": false, "rounds": rounds, "seconds_per_sample": seconds,
            "adapter": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(), "summary": summary, "runs": runs}, "  "))
    file.close()
    print("ABYSS_AB_SUMMARY ", JSON.stringify(summary))
    quit(0)
