extends SceneTree
## Same-session rotated A/B of the per-mission stage 3 plate rows: each mission
## (3, 4, 5) loaded with its "plates" rows and with them dropped in memory, at two
## room views, vsync off, native 1080p. Writes JSON to --out.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const MOOD := preload("res://scripts/missions/site7_mood.gd")
var out := "res://.cache/s3mood/mission_rows_perf.json"
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
    MOOD.abyss("MIS_CH01_03")
    var saved := {}
    for id in ["MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05"]:
        saved[id] = (MOOD._mood.missions[id] as Dictionary).get("plates", {})
    var runs: Array = []
    var variants := ["mission_rows", "shared_rows"]
    for round_index in range(rounds):
        for id in ["MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05"]:
            for k in range(2):
                var variant: String = variants[(k + round_index) % 2]
                var row: Dictionary = MOOD._mood.missions[id]
                if variant == "mission_rows": row["plates"] = saved[id]
                else: row.erase("plates")
                var stage := STAGE.instantiate() as StoryStage01
                stage.mission_id = id
                stage.battle_preview = true
                root.add_child(stage)
                await settle(10)
                for node in stage.find_children("*", "CharacterBody2D", true, false):
                    node.set_physics_process(false)
                    node.set_process(false)
                for view_index in range(2):
                    var room: Dictionary = stage.main_route[1 + view_index * 3]
                    stage.camera.global_position = Vector2(float(room.x), float(room.y))
                    stage.camera.reset_smoothing()
                    var result := await measure(viewport_rid)
                    result.merge({"round": round_index + 1, "mission": id, "view": str(room.id), "variant": variant})
                    runs.append(result)
                    print("ROWS_AB ", JSON.stringify(result))
                stage.queue_free()
                await settle(5)
    for id in saved: (MOOD._mood.missions[id] as Dictionary)["plates"] = saved[id]
    var summary := {}
    for variant in variants:
        var picked := runs.filter(func(r: Dictionary) -> bool: return r.variant == variant)
        var fps := 0.0
        var gpu := 0.0
        for r in picked:
            fps += float(r.fps)
            gpu += float(r.gpu_ms)
        summary[variant] = {"mean_fps": snappedf(fps / picked.size(), 0.1), "mean_gpu_ms": snappedf(gpu / picked.size(), 0.001), "samples": picked.size()}
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"native_resolution": [1920, 1080], "vsync": false, "rounds": rounds, "seconds_per_sample": seconds,
            "views": "each mission's main_route[1] and main_route[4] room centres, actors paused",
            "adapter": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(), "summary": summary, "runs": runs}, "  "))
    file.close()
    print("ROWS_AB_SUMMARY ", JSON.stringify(summary))
    quit(0)
