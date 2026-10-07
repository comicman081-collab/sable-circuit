extends SceneTree
## Cached drawings equal fresh ones. During op 1 R02 live combat (squad on AI, as in
## perf_op1.gd) the tree is paused at each sample. Every CanvasItem that did NOT redraw in
## the last unpaused frame is showing a cached drawing; those nodes are told to redraw from
## their current state, one script at a time, and a 1920x1080 frame is captured after each
## script's nodes. An unchanged frame means that script's cached drawings equal what a
## redraw every frame (the removed behaviour) would have shown.
## Nodes that redrew in the last frame are already fresh and are left alone; several of them
## (hit effects, reticle) do not draw the same thing twice (random sparks, live mouse).
## A1 == A2 checks that nothing changes while paused without a redraw.
## usage: godot --path . -s res://.cache/diag/redraw_equiv.gd [-- --control]
##   --control changes each squadmate's velocity behind its ground shadow's back (no redraw),
##   as a missed cache dependency would, and restores it before resuming; the run must then
##   report differences for operator_ground_shadow.gd. (OperatorVisual cannot serve: the
##   Motion Lab runtime sets its modulate alpha to 0, so its rings are never visible.)
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT := "res://.cache/diag/redraw_equiv"
const SAMPLES := 40
const EVERY := 40

var CONTROL := "--control" in OS.get_cmdline_user_args()
var _last_draw := {}
## Counts process_frame emissions, which come before node processing and the redraw flush.
var _process_count := 0

func _init(): call_deferred("_run")

func _watch(node: Node) -> void:
    if node is CanvasItem:
        var id := node.get_instance_id()
        node.draw.connect(func(): _last_draw[id] = _process_count)

func _watch_tree(node: Node) -> void:
    _watch(node)
    for child in node.get_children():
        _watch_tree(child)

func _key(node: CanvasItem) -> String:
    var script := node.get_script() as Script
    return script.resource_path.get_file() if script else node.get_class()

func _canvas_items(node: Node, out: Array) -> void:
    if node is CanvasItem:
        out.append(node)
    for child in node.get_children():
        _canvas_items(child, out)

func _capture() -> Image:
    await RenderingServer.frame_post_draw
    return root.get_texture().get_image()

func _run():
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    root.size = Vector2i(1920, 1080)
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
    process_frame.connect(func(): _process_count += 1)
    node_added.connect(_watch)
    _watch_tree(root)
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    stage.mission_id = "MIS_CH01_01"
    root.add_child(stage)
    for i in 6: await process_frame
    stage.start_battle_preview(1)
    var sampled := 0
    var stable := 0
    var clean := 0
    var checked_nodes := 0
    var checked_by_script := {}
    var differing_by_script := {}
    var saved := 0
    var start := Time.get_ticks_msec()
    var frame := 0
    while sampled < SAMPLES:
        await process_frame
        frame += 1
        if get_nodes_in_group("m3_enemies").is_empty() and Time.get_ticks_msec() - start > 1500:
            stage.debug_spawn_encounter_for_step(1)
        for o in stage.squad.operators:
            if not o.is_downed() and o.health < o.max_health * 0.5: o.heal(o.max_health)
        if frame < 90 or frame % EVERY != 0:
            continue
        # Pause at the start of the next physics step, before any node runs, so no state
        # changes after the last unpaused frame's processing and drawing. That frame's
        # process_frame has been counted and the next one has not.
        await physics_frame
        paused = true
        var last_unpaused := _process_count
        var saved_velocity := {}
        if CONTROL:
            for o in stage.squad.operators:
                if not o.controlled and not o.is_downed():
                    saved_velocity[o] = o.velocity
                    o.velocity = Vector2.ZERO if o.velocity.length() > o.run_speed * 0.5 else Vector2(o.run_speed, 0.0)
        var a1: Image = await _capture()
        var previous: Image = await _capture()
        var is_stable := a1.get_data() == previous.get_data()
        stable += int(is_stable)
        var groups := {}
        var items := []
        _canvas_items(root, items)
        for item in items:
            var ci := item as CanvasItem
            if not ci.is_visible_in_tree():
                continue
            if _last_draw.get(ci.get_instance_id(), -1) >= last_unpaused:
                continue
            var key := _key(ci)
            if not groups.has(key): groups[key] = []
            groups[key].append(ci)
        var keys := groups.keys()
        keys.sort()
        var sample_diffs := []
        for key in keys:
            for ci in groups[key]:
                ci.queue_redraw()
            checked_nodes += groups[key].size()
            checked_by_script[key] = checked_by_script.get(key, 0) + groups[key].size()
            await _capture()
            var after: Image = await _capture()
            if after.get_data() != previous.get_data():
                sample_diffs.append(key)
                differing_by_script[key] = differing_by_script.get(key, 0) + 1
                if saved < 6:
                    saved += 1
                    previous.save_png("%s/diff_%02d_%s_before.png" % [OUT, sampled + 1, key.get_basename()])
                    after.save_png("%s/diff_%02d_%s_after.png" % [OUT, sampled + 1, key.get_basename()])
            previous = after
        for o in saved_velocity:
            o.velocity = saved_velocity[o]
        paused = false
        sampled += 1
        clean += int(sample_diffs.is_empty())
        print("SAMPLE %d frame=%d stable=%s cached_groups=%d cached_nodes=%d hostiles=%d differing=%s" % [
            sampled, frame, is_stable, keys.size(), groups.values().reduce(func(a, g): return a + g.size(), 0),
            get_nodes_in_group("m3_enemies").size(), sample_diffs])
    print("REDRAW_EQUIV checked_by_script=%s" % JSON.stringify(checked_by_script))
    print("REDRAW_EQUIV samples=%d stable=%d clean=%d checked_redraws=%d differing_by_script=%s control=%s" % [
        sampled, stable, clean, checked_nodes, JSON.stringify(differing_by_script), CONTROL])
    print("REDRAW_EQUIV: %s" % ("PASS" if clean == sampled and stable == sampled else "FAIL"))
    quit()
