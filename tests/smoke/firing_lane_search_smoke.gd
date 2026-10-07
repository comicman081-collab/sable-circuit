extends SceneTree
## Site7EnemyTactics.LaneRoutes answers what CoverNavigation._plan would, one candidate at
## a time: in every combat room of the five operations, from several robot positions,
## each firing-lane candidate's route length equals _plan's path length exactly, and
## _choose_firing_lane picks the same lane as planning every candidate separately.
## Robots and operators are frozen so positions do not change between the two answers.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TACTICS := preload("res://scripts/combat/site7_enemy_tactics.gd")
const MISSIONS := ["MIS_CH01_01", "MIS_CH01_02", "MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05", "MIS_CH01_06", "MIS_CH01_07", "MIS_CH01_08", "MIS_CH01_09", "MIS_CH01_10"]
const LANE_ROLES := ["drone", "skimmer", "shield"]

var failures: Array[String] = []
var checks := 0
var candidates := 0
var lanes := 0
var reference_ms := 0.0
var search_ms := 0.0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    for mission in MISSIONS:
        await _check_mission(mission)
    _check(lanes >= 40, "enough lane searches compared (%d)" % lanes)
    print("lane searches %d, candidates %d; per-candidate planning %.0f ms, one search %.0f ms" % [lanes, candidates, reference_ms, search_ms])
    if failures.is_empty():
        print("FIRING_LANE_SEARCH_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures.slice(0, 20): printerr("FAIL: ", failure)
        quit(1)

func _check_mission(mission: String) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.configure_campaign({}, "FIRING-LANE-SMOKE", {})
    for step in range(stage.main_route.size()):
        var room: Dictionary = stage.main_route[step]
        if (room.get("encounter", []) as Array).is_empty(): continue
        stage.current_step = step
        stage.call("_activate_step")
        stage.debug_spawn_encounter_for_step(step)
        await _frames(2)
        for node in get_nodes_in_group("m3_enemies"): node.process_mode = Node.PROCESS_MODE_DISABLED
        for operator in stage.squad.operators: operator.process_mode = Node.PROCESS_MODE_DISABLED
        var target := stage.squad.get_active_operator()
        var tested := 0
        for node in get_nodes_in_group("m3_enemies"):
            var enemy := node as EnemyActor
            if tested >= 2 or enemy == null or not is_instance_valid(enemy.machine_sprite): continue
            if not str(TACTICS.ROLES.get(enemy.enemy_id, "")) in LANE_ROLES: continue
            tested += 1
            for spot in range(3):
                enemy.global_position = stage.battlefield.call("enemy_spawn", spot * 2 + tested)
                _compare(enemy, target, "%s %s %s #%d" % [mission, room.id, enemy.enemy_id, spot])
        for node in get_nodes_in_group("m3_enemies"): node.queue_free()
        for operator in stage.squad.operators: operator.process_mode = Node.PROCESS_MODE_INHERIT
        await _frames(2)
    stage.queue_free()
    await _frames(3)

func _compare(enemy: EnemyActor, target: OperatorActor, label: String) -> void:
    var tactics = enemy.tactics
    var obstacles := NAV.ground_obstacles(enemy)
    var planner := NAV.new()
    var routes = TACTICS.LaneRoutes.new(enemy, enemy.global_position, obstacles)
    var mismatched := 0
    for radius in [180.0, 260.0, 340.0]:
        for index in range(16):
            var point: Vector2 = target.global_position + Vector2.from_angle(float(index) * TAU / 16.0) * float(radius)
            if not NAV._clear_ground(enemy, point, point, obstacles): continue
            candidates += 1
            var path := planner._plan(enemy, enemy.global_position, point, obstacles)
            var planned := INF
            if not path.is_empty():
                planned = 0.0
                var previous := enemy.global_position
                for waypoint in path: planned += previous.distance_to(waypoint); previous = waypoint
            var searched: float = routes.cost_to(point, INF)
            if planned != searched: mismatched += 1
    _check(mismatched == 0, "%s: %d candidate route lengths differ from _plan" % [label, mismatched])
    var t0 := Time.get_ticks_usec()
    var expected := _reference_lane(enemy, target)
    var t1 := Time.get_ticks_usec()
    var chosen: Vector2 = tactics._choose_firing_lane(target)
    var t2 := Time.get_ticks_usec()
    reference_ms += (t1 - t0) / 1000.0
    search_ms += (t2 - t1) / 1000.0
    lanes += 1
    _check(chosen == expected or (not chosen.is_finite() and not expected.is_finite()), "%s: lane %s, per-candidate planning %s" % [label, chosen, expected])

## The lane search as it was: one _plan per candidate.
func _reference_lane(enemy: EnemyActor, target: OperatorActor) -> Vector2:
    var obstacles := NAV.ground_obstacles(enemy)
    var best := Vector2.INF
    var best_cost := INF
    var target_point := target.get_combat_aim_point()
    var planner := NAV.new()
    for radius in [180.0, 260.0, 340.0]:
        for index in range(16):
            var point: Vector2 = target.global_position + Vector2.from_angle(float(index) * TAU / 16.0) * float(radius)
            if not NAV._clear_ground(enemy, point, point, obstacles): continue
            var path := planner._plan(enemy, enemy.global_position, point, obstacles)
            if path.is_empty(): continue
            var cost := 0.0
            var previous := enemy.global_position
            for waypoint in path: cost += previous.distance_to(waypoint); previous = waypoint
            if cost >= best_cost: continue
            var solution: Dictionary = enemy.machine_sprite.target_solution_from(point, target_point)
            if solution.is_empty() or not NAV.clear_shot(self, solution.origin, target): continue
            best = point
            best_cost = cost
    return best

func _frames(count: int) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func _check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label)
