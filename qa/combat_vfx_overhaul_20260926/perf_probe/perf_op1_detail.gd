extends SceneTree
## Native frame-cost probe: op 1 R02 battle preview, 30 s of live combat with the squad on AI.
## Counts every live effect node whose script sits under scripts/vfx/ (works on either tree).
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
func _init(): call_deferred("_run")
func _run():
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    Engine.max_fps = 0
    root.size = Vector2i(1920, 1080)
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    stage.mission_id = "MIS_CH01_01"
    root.add_child(stage)
    for i in 6: await process_frame
    stage.start_battle_preview(1)
    var start := Time.get_ticks_msec()
    var frames := 0
    var proc := 0.0
    var window_start := start
    var vfx_sum := 0
    var vfx_max := 0
    var draws := 0.0
    var prims := 0.0
    var objs := 0.0
    var kinds := {}
    while Time.get_ticks_msec() - start < 30000:
        await process_frame
        frames += 1
        var live := 0
        for c in root.get_children():
            var script: Script = c.get_script()
            if script != null and (script.resource_path.begins_with("res://scripts/vfx/") or c is PrototypeProjectile):
                if not (c is PrototypeProjectile): live += 1
                var k := script.resource_path.get_file()
                kinds[k] = int(kinds.get(k, 0)) + 1
        vfx_sum += live
        vfx_max = maxi(vfx_max, live)
        if get_nodes_in_group("m3_enemies").is_empty() and Time.get_ticks_msec() - start > 1500:
            stage.debug_spawn_encounter_for_step(1)
        for o in stage.squad.operators:
            if not o.is_downed() and o.health < o.max_health * 0.5: o.heal(o.max_health)
        proc += Performance.get_monitor(Performance.TIME_PROCESS)
        draws += Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
        prims += Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
        objs += Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
        var now := Time.get_ticks_msec()
        if now - window_start >= 5000:
            print("PERF t=%2ds fps=%5.1f process_ms=%5.2f hostiles=%d vfx_avg=%.1f vfx_max=%d" % [
                (now - start) / 1000, frames * 1000.0 / (now - window_start), proc * 1000.0 / frames,
                get_nodes_in_group("m3_enemies").size(), float(vfx_sum) / frames, vfx_max])
            var avg := {}
            for k in kinds: avg[k] = snappedf(float(kinds[k]) / frames, 0.1)
            print("DETAIL draws=%.0f prims=%.0f objs=%.0f kinds=%s" % [draws / frames, prims / frames, objs / frames, JSON.stringify(avg)])
            draws = 0.0; prims = 0.0; objs = 0.0; kinds = {}
            frames = 0; proc = 0.0; window_start = now; vfx_sum = 0; vfx_max = 0
    quit()
