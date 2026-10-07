extends SceneTree
## Native frame-cost probe: op 1 R02 battle preview, 30 s of live combat with the squad on AI.
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
    var phys := 0.0
    var window_start := start
    var vfx_sum := 0
    var vfx_max := 0
    while Time.get_ticks_msec() - start < 30000:
        await process_frame
        frames += 1
        var live := 0
        for c in root.get_children():
            if c is CombatHitVFX: live += 1
        vfx_sum += live
        vfx_max = maxi(vfx_max, live)
        if get_nodes_in_group("m3_enemies").is_empty() and Time.get_ticks_msec() - start > 1500:
            stage.debug_spawn_encounter_for_step(1)
        for o in stage.squad.operators:
            if not o.is_downed() and o.health < o.max_health * 0.5: o.heal(o.max_health)
        proc += Performance.get_monitor(Performance.TIME_PROCESS)
        phys += Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)
        var now := Time.get_ticks_msec()
        if now - window_start >= 5000:
            var hostiles := get_nodes_in_group("m3_enemies").size()
            print("PERF t=%2ds fps=%5.1f process_ms=%5.2f physics_ms=%5.2f nodes=%d objects=%d hostiles=%d vfx_avg=%.1f vfx_max=%d" % [
                (now - start) / 1000, frames * 1000.0 / (now - window_start), proc * 1000.0 / frames, phys * 1000.0 / frames,
                int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)), int(Performance.get_monitor(Performance.OBJECT_COUNT)),
                hostiles, float(vfx_sum) / frames, vfx_max])
            frames = 0; proc = 0.0; phys = 0.0; window_start = now; vfx_sum = 0; vfx_max = 0
    quit()
