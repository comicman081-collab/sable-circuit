extends SceneTree
## Minimap render equivalence (diagnostic, windowed, Compatibility renderer): the committed
## single-layer TacticalMinimap (.cache/diag/tactical_minimap_old.gd, class_name removed)
## and the working-tree two-layer one, each alone in a 190x106 transparent SubViewport,
## bound to the same live op 1 combat stage. Both advance with the same frame deltas;
## every 4th frame both render targets are read back and compared byte for byte.
## Script: settled local zoom, zoom-in and its lerp, the active operator moving while
## zoomed (floors follow it), settled again, overview zoom and its lerp, moving in the
## overview (floors fixed), settled. `cached` counts compares where the new floor layer
## had not redrawn since the previous compare (only the markers had).
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const OLD := preload("res://.cache/diag/tactical_minimap_old.gd")
const NEW := preload("res://scripts/ui/tactical_minimap.gd")
const FRAMES := 2000

func _init(): call_deferred("_run")

func _make(script: Script) -> Array:
    var viewport := SubViewport.new()
    viewport.size = Vector2i(190, 106)
    viewport.transparent_bg = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    root.add_child(viewport)
    var map: Control = script.new()
    map.size = Vector2(190, 106)
    viewport.add_child(map)
    return [viewport, map]

func _moving(frame: int) -> bool:
    return (frame >= 700 and frame < 800) or (frame >= 1650 and frame < 1750)

func _run():
    root.size = Vector2i(1920, 1080)
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    stage.mission_id = "MIS_CH01_01"
    root.add_child(stage)
    for i in 6: await process_frame
    stage.start_battle_preview(1)
    var old_pair := _make(OLD)
    var new_pair := _make(NEW)
    old_pair[1].bind_stage(stage)
    new_pair[1].bind_stage(stage)
    var floor_draws := [0]
    new_pair[1].draw.connect(func(): floor_draws[0] += 1)
    var compared := 0
    var cached := 0
    var cached_moving := 0
    var different := 0
    var nonblank := 0
    var max_channel_diff := 0
    var last_floor_draws := 0
    for frame in FRAMES:
        await process_frame
        if get_nodes_in_group("m3_enemies").is_empty() and frame > 90:
            stage.debug_spawn_encounter_for_step(1)
        for o in stage.squad.operators:
            if not o.is_downed() and o.health < o.max_health * 0.5: o.heal(o.max_health)
        var active := stage.squad.get_active_operator()
        if active and _moving(frame):
            active.global_position += Vector2(cos(frame * 0.07), sin(frame * 0.07)) * 4.0
        if frame == 150:
            for pair in [old_pair, new_pair]: pair[1].zoom_by(1)
        if frame == 1100:
            for pair in [old_pair, new_pair]: pair[1].toggle_zoom()
        if frame < 20 or frame % 4 != 0: continue
        await RenderingServer.frame_post_draw
        var a: Image = old_pair[0].get_texture().get_image()
        var b: Image = new_pair[0].get_texture().get_image()
        compared += 1
        if floor_draws[0] == last_floor_draws:
            cached += 1
            if _moving(frame): cached_moving += 1
        last_floor_draws = floor_draws[0]
        if not a.is_invisible(): nonblank += 1
        if a.get_data() != b.get_data():
            different += 1
            var da := a.get_data()
            var db := b.get_data()
            for i in da.size(): max_channel_diff = maxi(max_channel_diff, absi(int(da[i]) - int(db[i])))
            if different <= 3:
                a.save_png("res://.cache/diag/minimap_old_%d.png" % frame)
                b.save_png("res://.cache/diag/minimap_new_%d.png" % frame)
    print("MINIMAP_EQUIV compared=%d nonblank=%d different=%d max_channel_diff=%d cached=%d cached_while_moving=%d new_floor_redraws=%d of %d frames zoom_old=%s zoom_new=%s" % [
        compared, nonblank, different, max_channel_diff, cached, cached_moving, floor_draws[0], FRAMES,
        old_pair[1].get("_zoom"), new_pair[1].get("_zoom")])
    print("MINIMAP_EQUIV: %s" % ("PASS" if different == 0 and nonblank == compared and compared > 400 and cached > 100 else "FAIL"))
    quit()
