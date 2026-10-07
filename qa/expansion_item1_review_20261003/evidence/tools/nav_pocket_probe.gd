extends SceneTree
## Claude review scratch probe (not part of the repo): is the position where the baseline
## operation 9 bot froze (-6100.857, 3838.127) a CoverNavigation dead end, and how big is it?
## Run: godot --headless --path <project> -s res://.cache/probe/nav_pocket_probe.gd -- --out=res://.cache/probe/nav_pocket.json
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
var out := "res://.cache/probe/nav_pocket.json"
var mission := "MIS_CH01_09"
var stall := Vector2(-6100.857421875, 3838.12670898438)

func _init() -> void:
    call_deferred("_run")

func _frames(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func _run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
        if arg.begins_with("--mission="): mission = arg.get_slice("=", 1)
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    stage.configure_campaign({}, "NAV-POCKET-PROBE", {})
    await _frames(5)
    stage.current_step = 3
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(3)
    for guard in range(40):
        if stage.current_step >= 4: break
        for node in get_nodes_in_group("m3_enemies"):
            if node is EnemyActor and node.get_parent() == stage and node.health > 0.0: node.apply_damage(99999.0)
        await _frames(30)
    print("PROBE step=", stage.current_step, " hazards=", get_nodes_in_group("zone_hazards").size())
    var active := stage.squad.get_active_operator()
    var goal := Vector2(float(stage.optional_rooms[0].x), float(stage.optional_rooms[0].y))
    var result := {"mission": mission, "step_reached": stage.current_step, "goal": [goal.x, goal.y]}
    active.global_position = stall
    await _frames(2)
    var nav := NAV.new()
    var obstacles := NAV.ground_obstacles(active)
    var rects: Array = []
    for rect in obstacles:
        if rect.grow(60.0).has_point(stall): rects.append([rect.position.x, rect.position.y, rect.end.x, rect.end.y])
    var d := nav.direction(active, goal, 1.0 / 60.0)
    result["stall_direction"] = [d.x, d.y]
    result["stall_on_floor"] = NAV._on_floor(active, stall)
    result["obstacles_near_stall"] = rects
    result["obstacle_count"] = obstacles.size()
    print("PROBE stall direction=", d, " on_floor=", result.stall_on_floor, " near_rects=", rects)
    # Scan a window around the stall: where does a fresh planner return ZERO although the goal is far away?
    var zero: Array = []
    var live := 0
    var inside_rect := 0
    var x := stall.x - 140.0
    while x <= stall.x + 140.0:
        var y := stall.y - 70.0
        while y <= stall.y + 30.0:
            var p := Vector2(x, y)
            if NAV._on_floor(active, p):
                active.global_position = p
                var local_nav := NAV.new()
                var local_obstacles := NAV.ground_obstacles(active)
                var inside := false
                for rect in local_obstacles:
                    if rect.has_point(p): inside = true
                var dir := local_nav.direction(active, goal, 1.0 / 60.0)
                if inside: inside_rect += 1
                if dir.length_squared() < 0.0001 and not inside:
                    zero.append([snappedf(x, 0.1), snappedf(y, 0.1)])
                else:
                    live += 1
            y += 2.0
        x += 4.0
    result["scan_live_count"] = live
    result["scan_inside_rect_count"] = inside_rect
    result["scan_zero_count"] = zero.size()
    result["scan_zero_points_first40"] = zero.slice(0, 40)
    if not zero.is_empty():
        var lo := Vector2(INF, INF)
        var hi := Vector2(-INF, -INF)
        for q in zero:
            lo = Vector2(minf(lo.x, q[0]), minf(lo.y, q[1]))
            hi = Vector2(maxf(hi.x, q[0]), maxf(hi.y, q[1]))
        result["scan_zero_bbox"] = [lo.x, lo.y, hi.x, hi.y]
    print("PROBE scan live=", live, " inside_rect=", inside_rect, " zero=", zero.size(), " bbox=", result.get("scan_zero_bbox", []))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
    var file := FileAccess.open(out, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(result, "  "))
        file.close()
    quit(0)
