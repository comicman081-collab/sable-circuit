extends SceneTree
## Redraw census (diagnostic): op 1 R02 battle preview, like perf_op1.gd. After 8 s of
## combat, counts for 10 s how often each CanvasItem redraws (its `draw` signal), by
## script file (or engine class). Each redraw of a node that draws polygons, polylines,
## arcs or circles rebuilds a vertex array and buffers per shape on the web renderer.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var watched := {}
var redraws := {}
var nodes := {}
var node_redraws := {}
var counting := false

func _init(): call_deferred("_run")

func _watch(node: Node) -> void:
    if not (node is CanvasItem): return
    var id := node.get_instance_id()
    if watched.has(id): return
    watched[id] = true
    var script: Script = node.get_script()
    var key: String = script.resource_path.get_file() if script and not script.resource_path.is_empty() else node.get_class()
    node.draw.connect(_on_draw.bind(key, id))

func _watch_tree(node: Node) -> void:
    _watch(node)
    for child in node.get_children(): _watch_tree(child)

func _on_draw(key: String, id: int) -> void:
    if not counting: return
    redraws[key] = int(redraws.get(key, 0)) + 1
    node_redraws[id] = int(node_redraws.get(id, 0)) + 1
    var seen: Dictionary = nodes.get(key, {})
    seen[id] = true
    nodes[key] = seen

func _run():
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    Engine.max_fps = 0
    root.size = Vector2i(1920, 1080)
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    node_added.connect(_watch)
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    stage.mission_id = "MIS_CH01_01"
    root.add_child(stage)
    _watch_tree(root)
    for i in 6: await process_frame
    stage.start_battle_preview(1)
    var start := Time.get_ticks_msec()
    var frames := 0
    while Time.get_ticks_msec() - start < 18000:
        await process_frame
        if get_nodes_in_group("m3_enemies").is_empty() and Time.get_ticks_msec() - start > 1500:
            stage.debug_spawn_encounter_for_step(1)
        for o in stage.squad.operators:
            if not o.is_downed() and o.health < o.max_health * 0.5: o.heal(o.max_health)
        if not counting and Time.get_ticks_msec() - start >= 8000:
            counting = true
        if counting: frames += 1
    counting = false
    var rows := []
    for key in redraws:
        rows.append([key, float(redraws[key]) / frames, (nodes[key] as Dictionary).size()])
    rows.sort_custom(func(a, b): return a[1] > b[1])
    var total := 0.0
    for row in rows: total += row[1]
    print("CENSUS frames=%d redraws_per_frame=%.1f hostiles=%d" % [frames, total, get_nodes_in_group("m3_enemies").size()])
    for row in rows:
        print("CENSUS_ROW %-42s %7.2f per frame  nodes=%d" % [row[0], row[1], row[2]])
    var per_node := []
    for id in node_redraws:
        var node := instance_from_id(id) as Node
        if node and node.is_inside_tree() and float(node_redraws[id]) / frames >= 0.9:
            per_node.append([str(node.get_path()).trim_prefix("/root/"), float(node_redraws[id]) / frames])
    per_node.sort_custom(func(a, b): return a[0] < b[0])
    for row in per_node:
        print("CENSUS_NODE %6.2f %s" % [row[1], row[0]])
    quit()
