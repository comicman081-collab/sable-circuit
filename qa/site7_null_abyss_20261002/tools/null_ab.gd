extends SceneTree
## Scratch (Claude, 2026-10-02): same-session rotated A/B of operation 10's abyss: the shipped HEAD shader and row
## (abyss_old.gd, near-black) against the working-tree shader and row. Native 1080p window, vsync off, two void-heavy
## views, the variant order rotating per round and view. Only the abyss quad differs; plates, haze glows and camera
## are shared. Writes JSON to --out. The old shader is the committed script before the lift:
##   git show e97fb6ac:scripts/missions/site7_abyss_backdrop.gd > .cache/null_ab/abyss_old.gd   (--old=res://... to move it)
## Run it windowed (not --headless), one Godot at a time: godot --path . -s <this file> -- --out=res://.cache/null_ab/null_ab.json
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const MOOD := preload("res://scripts/missions/site7_mood.gd")
const OLD_ROW := {"style": "null", "style_color": [0.9, 0.94, 1.0], "style_strength": 0.9, "base": [0.012, 0.014, 0.02], "fog": [0.022, 0.028, 0.038], "fog_strength": 0.1, "haze_strength": 0.045, "far_light_density": 0.08, "dust_strength": 0.12, "dust": [1.0, 0.3, 0.26], "work_lights": [1.0, 0.12, 0.09]}
var out := "res://.cache/null_ab/null_ab.json"
var old_path := "res://.cache/null_ab/abyss_old.gd"
var rounds := 5
var seconds := 3.0

func _init() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.substr(6)
        if arg.begins_with("--old="): old_path = arg.substr(6)
        if arg.begins_with("--rounds="): rounds = int(arg.substr(9))
        if arg.begins_with("--seconds="): seconds = float(arg.substr(10))
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
    return {"fps": snappedf(frames / elapsed, 0.1), "gpu_ms": snappedf(gpu / frames, 0.001), "frame_ms": snappedf(1000.0 * elapsed / frames, 0.001)}

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
    stage.mission_id = "MIS_CH01_10"
    stage.battle_preview = true
    root.add_child(stage)
    await settle(10)
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    for node in stage.find_children("*", "CharacterBody2D", true, false):
        node.set_physics_process(false)
        node.set_process(false)
    var new_backdrop := art.get_node("AbyssBackdrop") as Node2D
    var new_material := new_backdrop.material as ShaderMaterial
    var old_script := load(old_path) as GDScript
    if old_script == null:
        push_error("--old=<the HEAD copy of site7_abyss_backdrop.gd> is missing: " + old_path)
        quit(2)
        return
    var old_backdrop := old_script.new() as Node2D
    old_backdrop.name = "AbyssBackdropOld"
    art.add_child(old_backdrop)
    art.move_child(old_backdrop, 0)
    old_backdrop.call("setup", new_backdrop.get("_rect"), OLD_ROW, [] as Array[Dictionary])
    var old_material := old_backdrop.material as ShaderMaterial
    for key in ["glow", "glow_color", "glow_count"]:
        old_material.set_shader_parameter(key, new_material.get_shader_parameter(key))
    var variants := {"old_head": old_backdrop, "new": new_backdrop}
    var views := [{"name": "C05", "at": art.get_connector_plate(4).global_position},
            {"name": "R05", "at": art.get_room_plate(str(stage.main_route[4].id)).global_position + Vector2(330, 120)}]
    var runs: Array = []
    var names: Array = variants.keys()
    for round_index in range(rounds):
        for view_index in range(views.size()):
            stage.camera.global_position = views[view_index].at
            stage.camera.reset_smoothing()
            for k in range(names.size()):
                var name: String = names[(k + round_index + view_index) % names.size()]
                for other in names:
                    (variants[other] as Node2D).visible = (other == name)
                var result := await measure(viewport_rid)
                result.merge({"round": round_index + 1, "view": views[view_index].name, "variant": name})
                runs.append(result)
                print("NULL_AB ", JSON.stringify(result))
    var summary := {}
    for name in names:
        var picked := runs.filter(func(row: Dictionary) -> bool: return row.variant == name)
        var fps := 0.0
        var gpu := 0.0
        var frame := 0.0
        for row in picked:
            fps += float(row.fps)
            gpu += float(row.gpu_ms)
            frame += float(row.frame_ms)
        summary[name] = {"mean_fps": snappedf(fps / picked.size(), 0.1), "mean_gpu_ms": snappedf(gpu / picked.size(), 0.001), "mean_frame_ms": snappedf(frame / picked.size(), 0.001), "samples": picked.size()}
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"mission": "MIS_CH01_10", "native_resolution": [1920, 1080], "vsync": false, "rounds": rounds, "seconds_per_sample": seconds,
            "adapter": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(), "summary": summary, "runs": runs}, "  "))
    file.close()
    print("NULL_AB_SUMMARY ", JSON.stringify(summary))
    quit(0)
