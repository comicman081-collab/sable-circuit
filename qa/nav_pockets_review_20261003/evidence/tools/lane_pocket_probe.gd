extends SceneTree
## Claude review instrument (N-03): is Site7EnemyTactics.LaneRoutes still CoverNavigation._plan from inside a pocket?
##
## tests/smoke/firing_lane_search_smoke.gd compares every firing-lane candidate's route length from LaneRoutes with _plan's,
## but only from the enemy spawn slots. The navigation fix adds floor-clipped escape nodes to _fixed_nodes; LaneRoutes
## has to take them from the same function, or a robot standing in a pocket is told "no route" by one and "a route" by the
## other. This repeats the smoke's comparison from the listed pocket cells (a lane robot placed on each cell).
##
## Godot --headless --path <project> -s res://.cache/lane_pocket_probe.gd -- --cells=res://.cache/cells_dead.csv [--out=res://.cache/out/lane_probe.json]
## CSV rows: mission,step,x,y
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TACTICS := preload("res://scripts/combat/site7_enemy_tactics.gd")
const LANE_ROLES := ["drone", "skimmer", "shield"]
var cells_path := ""
var out := ""
var report: Array[Dictionary] = []

func _init() -> void:
    call_deferred("_run")

func _frames(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func _run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--cells="): cells_path = arg.get_slice("=", 1)
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
    var file := FileAccess.open(cells_path, FileAccess.READ)
    var order: Array[String] = []
    var groups := {}
    while not file.eof_reached():
        var line := file.get_line().strip_edges()
        if line == "" or line.begins_with("#"): continue
        var parts := line.split(",")
        var mission := parts[0] if parts[0].begins_with("MIS_") else "MIS_CH01_%02d" % int(parts[0])
        var key := "%s|%d" % [mission, int(parts[1])]
        if not groups.has(key):
            groups[key] = []
            order.append(key)
        (groups[key] as Array).append(Vector2(float(parts[2]), float(parts[3])))
    for key in order: await _room(key.get_slice("|", 0), int(key.get_slice("|", 1)), groups[key])
    var candidates := 0
    var mismatches := 0
    var origins := 0
    for row in report:
        candidates += int(row.candidates)
        mismatches += int(row.mismatched)
        origins += int(row.origins)
    if out != "":
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
        var handle := FileAccess.open(out, FileAccess.WRITE)
        if handle != null:
            handle.store_string(JSON.stringify({"rooms": report}, "  "))
            handle.close()
    print("LANE_POCKET_PROBE: %s (%d origins, %d candidate lanes, %d route lengths differ from _plan)" % ["PASS" if mismatches == 0 else "FAIL", origins, candidates, mismatches])
    quit(0 if mismatches == 0 else 1)

func _room(mission_id: String, step: int, points: Array) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await _frames(8)
    stage.start_battle_preview(step)
    await _frames(4)
    for node in get_nodes_in_group("m3_enemies"): node.process_mode = Node.PROCESS_MODE_DISABLED
    for operator in stage.squad.operators: operator.process_mode = Node.PROCESS_MODE_DISABLED
    var room_id := str(stage.main_route[stage.current_step].id)
    var target := stage.squad.get_active_operator()
    var enemy: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        var candidate := node as EnemyActor
        if candidate != null and is_instance_valid(candidate.machine_sprite) and str(TACTICS.ROLES.get(candidate.enemy_id, "")) in LANE_ROLES:
            enemy = candidate
            break
    var candidates := 0
    var mismatched := 0
    var origins := 0
    var finite_planned := 0
    if enemy != null:
        for point: Vector2 in points:
            enemy.global_position = point
            origins += 1
            var obstacles := NAV.ground_obstacles(enemy)
            var planner := NAV.new()
            var routes = TACTICS.LaneRoutes.new(enemy, enemy.global_position, obstacles)
            for radius in [180.0, 260.0, 340.0]:
                for index in range(16):
                    var spot: Vector2 = target.global_position + Vector2.from_angle(float(index) * TAU / 16.0) * float(radius)
                    if not NAV._clear_ground(enemy, spot, spot, obstacles): continue
                    candidates += 1
                    var path := planner._plan(enemy, enemy.global_position, spot, obstacles)
                    var planned := INF
                    if not path.is_empty():
                        planned = 0.0
                        var previous := enemy.global_position
                        for waypoint in path:
                            planned += previous.distance_to(waypoint)
                            previous = waypoint
                        finite_planned += 1
                    if planned != float(routes.cost_to(spot, INF)): mismatched += 1
    report.append({"mission": mission_id, "room": room_id, "step": step, "robot": str(enemy.enemy_id) if enemy != null else "none",
        "origins": origins, "candidates": candidates, "planned_routes": finite_planned, "mismatched": mismatched})
    print("LANE_PROBE_ROOM %s %s robot=%s origins=%d candidates=%d routed=%d mismatched=%d" % [mission_id, room_id, str(enemy.enemy_id) if enemy != null else "none", origins, candidates, finite_planned, mismatched])
    stage.free()
    await _frames(3)
