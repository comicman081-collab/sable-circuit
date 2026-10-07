extends SceneTree
## Diversity-pack hazard mechanics and every declared room's painted-floor escape.
## Uses real actors and navigation; no player save, settings, art or dated QA writes.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TestOutput := preload("res://tests/support/test_output.gd")
const DemoInput := preload("res://scripts/ui/demo_input.gd")
const GRID := 25.0
const SLOWEST_WALK := 138.0
const ESCAPE_MARGIN := 0.25
const IDS := ["ARC_VENT", "SPORE_CLOUD", "FROST_PLATE", "RAIL_LANE"]
var checks := 0
var failures: Array[String] = []
var report: Array[Dictionary] = []
var cycles: Array[Dictionary] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _table_contract()
    await _damage_contract()
    await _frost_contract()
    await _frost_dash_and_enemy_movement()
    await _spore_flinch_budget()
    await _fixture_followers()
    for number in range(1, 11):
        await _mission("MIS_CH01_%02d" % number)
    var out := TestOutput.path("res://.cache/hazard_expansion_smoke.json")
    var file := FileAccess.open(out, FileAccess.WRITE)
    _check(file != null, "test report opens at its --out path")
    if file != null:
        file.store_string(JSON.stringify({"status": "PASS" if failures.is_empty() else "FAIL", "checks": checks,
            "failures": failures, "grid_px": GRID, "slowest_walk_px_per_s": SLOWEST_WALK,
            "escape_margin_s": ESCAPE_MARGIN, "cycles": cycles, "rooms": report, "visual_approval": false}, "  "))
        file.close()
    for failure in failures: printerr("FAIL: ", failure)
    print("HAZARD_EXPANSION_SMOKE: %s (%d checks, %d rooms) %s" % ["PASS" if failures.is_empty() else "FAIL", checks, report.size(), out])
    quit(0 if failures.is_empty() else 1)

func _table_contract() -> void:
    var table := ZoneHazard.table()
    _check(table.size() == 4, "legacy vent and three new hazards are defined")
    _check(ZoneHazard.create("UNKNOWN", Vector2.ZERO, 0) == null, "unknown hazard creates no node")
    var colors: Array[String] = []
    var hex := RegEx.new()
    hex.compile("^[0-9a-fA-F]{6}$")
    var legacy := {"title": "ARC VENT", "color": "66e6ff",
        "tip": "ARC VENT: a grate crackles for a second before it discharges; step off it. Robots standing on it take the hit too.",
        "radius": 70.0, "first_delay": 2.4, "idle": 3.0, "telegraph": 1.1, "discharge": 0.3,
        "phase_step": 1.35, "operator_damage": 14.0, "enemy_damage": 24.0}
    _check(table.get("ARC_VENT", {}) == legacy, "ARC_VENT data is unchanged")
    for id: String in IDS:
        _check(table.has(id), id + " exists")
        if not table.has(id): continue
        var spec: Dictionary = table[id]
        var color := str(spec.get("color", "")).to_lower()
        _check(hex.search(color) != null and not colors.has(color), id + " has a distinct six-digit colour")
        colors.append(color)
        _check(ZoneHazard.tip(" " + id.to_lower() + " ").begins_with(str(spec.get("title", "")) + ":"), id + " has a title-prefixed normalized tip")
        _check(float(spec.get("first_delay", 0.0)) >= 2.0, id + " first placement is quiet for at least two seconds")
        _check(_damage_limits(spec), id + " damage/slow stays inside the declared limits")
        if str(spec.get("mode", "burst")) != "slow":
            _check(_escape_budget(spec), id + " innermost escape fits its warning at 138 px/s plus 0.25s")
        var hazard := ZoneHazard.create(id, Vector2.ZERO, 0)
        _check(hazard != null and hazard.phase == ZoneHazard.Phase.IDLE and hazard.phase_left >= 2.0, id + " is created quiet")
        if hazard != null: hazard.free()
    var unsafe: Dictionary = table.SPORE_CLOUD.duplicate(true)
    unsafe.operator_dps = 4.01
    _check(not _damage_limits(unsafe), "negative control rejects continuous damage over 4 HP/s")
    unsafe = table.RAIL_LANE.duplicate(true)
    unsafe.telegraph = 0.99
    _check(not _escape_budget(unsafe), "negative control rejects a sub-second warning")
    unsafe = table.SPORE_CLOUD.duplicate(true)
    unsafe.radius = 200.0
    _check(not _escape_budget(unsafe), "negative control rejects an oversized cloud for its warning")
    var rail := ZoneHazard.create("RAIL_LANE", Vector2.ZERO, 0)
    var angle := deg_to_rad(float(rail.spec.angle_degrees))
    _check(rail.contains(Vector2(80, 0).rotated(angle)) and not rail.contains(Vector2(0, 30).rotated(angle)), "rail contains its long axis and excludes points beyond its narrow half-width")
    _check(not rail.contains(Vector2(100, 0).rotated(angle)), "rail excludes points past the actual end instead of using its bounding circle")
    _check(is_equal_approx(rail.radius, Vector2(float(rail.spec.half_length), float(rail.spec.half_width)).length()), "rail placement radius is the band's bounding radius")
    rail.free()

func _damage_limits(spec: Dictionary) -> bool:
    if str(spec.get("mode", "burst")) == "slow":
        return float(spec.get("operator_damage", 0.0)) == 0.0 and float(spec.get("enemy_damage", 0.0)) == 0.0 and float(spec.get("slow_multiplier", 0.0)) >= 0.5 and float(spec.get("slow_multiplier", 0.0)) <= 0.8
    return float(spec.get("operator_damage", 0.0)) <= 14.0 and float(spec.get("enemy_damage", 0.0)) <= 24.0 and float(spec.get("operator_dps", 0.0)) <= 4.0 and float(spec.get("enemy_dps", 0.0)) <= 8.0

func _escape_budget(spec: Dictionary) -> bool:
    var distance := float(spec.get("half_width", 0.0)) if str(spec.get("shape", "")) == "band" else float(spec.get("radius", 0.0))
    return float(spec.get("telegraph", 0.0)) >= 1.0 and distance / SLOWEST_WALK + ESCAPE_MARGIN <= float(spec.get("telegraph", 0.0))

func _operator(parent: Node, point: Vector2) -> OperatorActor:
    var actor := OPERATOR.instantiate() as OperatorActor
    actor.configure("CHR_PROTO_03", "MICA", Color.WHITE)
    actor.position = point
    parent.add_child(actor)
    actor.set_process(false)
    actor.set_physics_process(false)
    actor.set_movement_bounds(Rect2(-2000, -2000, 4000, 4000))
    actor.health = actor.max_health
    return actor

func _enemy(parent: Node, point: Vector2) -> EnemyActor:
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_DRONE_01", 1000.0)
    actor.position = point
    parent.add_child(actor)
    actor.set_process(false)
    actor.set_physics_process(false)
    return actor

func _hazard(parent: Node, id: String, point: Vector2, index := 0) -> ZoneHazard:
    var hazard := ZoneHazard.create(id, point, index)
    parent.add_child(hazard)
    hazard.set_physics_process(false)
    return hazard

func _damage_contract() -> void:
    for id: String in ["ARC_VENT", "SPORE_CLOUD", "RAIL_LANE"]:
        var holder := Node2D.new()
        root.add_child(holder)
        var op := _operator(holder, Vector2.ZERO)
        var robot := _enemy(holder, Vector2.ZERO)
        var outside := _operator(holder, Vector2(200, 200))
        var hazard := _hazard(holder, id, Vector2.ZERO)
        var op_events: Array[Dictionary] = []
        var robot_events: Array[Dictionary] = []
        op.damage_taken.connect(func(_actor, amount, source): op_events.append({"amount": amount, "source": source}))
        robot.damage_taken.connect(func(_actor, amount, source): robot_events.append({"amount": amount, "source": source}))
        var op_before := op.health
        var robot_before := robot.health
        var outside_before := outside.health
        var initial_delay := hazard.phase_left
        hazard._physics_process(initial_delay - 0.01)
        _check(hazard.phase == ZoneHazard.Phase.IDLE and op.health == op_before and robot.health == robot_before, id + " stays quiet before its first delay")
        hazard._physics_process(hazard.phase_left + 0.000001)
        _check(hazard.phase == ZoneHazard.Phase.TELEGRAPH and op.health == op_before and robot.health == robot_before, id + " starts its warning without damage")
        var warning := float(hazard.spec.telegraph)
        hazard._physics_process(warning - 0.01)
        _check(hazard.phase == ZoneHazard.Phase.TELEGRAPH and hazard.discharges == 0 and op.health == op_before and robot.health == robot_before, id + " does no damage through the warning")
        hazard._physics_process(hazard.phase_left + 0.000001)
        _check(hazard.phase == ZoneHazard.Phase.DISCHARGE and hazard.discharges == 1, id + " discharges only after the full warning")
        var continuous := str(hazard.spec.get("mode", "burst")) == "continuous"
        var expected_op := float(hazard.spec.get("operator_damage", 0.0))
        var expected_robot := float(hazard.spec.get("enemy_damage", 0.0))
        if continuous:
            _check(op.health == op_before and robot.health == robot_before, id + " has no burst at cloud onset")
            for frame in range(60): hazard._physics_process(1.0 / 60.0)
            _check(absf(op_before - op.health - 4.0) < 0.001 and absf(robot_before - robot.health - 8.0) < 0.001, id + " deals exactly 4/8 HP over one second")
            hazard._physics_process(2.0)
            expected_op = float(hazard.spec.operator_dps) * float(hazard.spec.discharge)
            expected_robot = float(hazard.spec.enemy_dps) * float(hazard.spec.discharge)
        else:
            hazard._physics_process(float(hazard.spec.discharge))
        _check(absf(op_before - op.health - expected_op) < 0.001 and absf(robot_before - robot.health - expected_robot) < 0.001, id + " hits real operator and robot with exactly its complete discharge")
        _check(outside.health == outside_before, id + " does not hit actors outside its actual shape")
        _check(not op_events.is_empty() and op_events.all(func(row: Dictionary) -> bool: return row.source == "HAZARD_" + id), id + " attributes all operator damage")
        _check(not robot_events.is_empty() and robot_events.all(func(row: Dictionary) -> bool: return row.source == "HAZARD_" + id), id + " attributes all robot damage")
        _check(absf(_total(op_events) - expected_op) < 0.001 and absf(_total(robot_events) - expected_robot) < 0.001, id + " source events report actual health lost")
        var after := op.health
        hazard._physics_process(0.1)
        _check(hazard.phase == ZoneHazard.Phase.IDLE and hazard.discharges == 1 and op.health == after, id + " returns to idle without a second hit")
        cycles.append({"hazard": id, "operator_damage": op_before - op.health, "enemy_damage": robot_before - robot.health,
            "warning_s": warning, "first_delay_s": initial_delay, "operator_events": op_events.size(), "enemy_events": robot_events.size()})
        holder.free()
        await _frames(1)

func _total(events: Array[Dictionary]) -> float:
    var result := 0.0
    for row in events: result += float(row.amount)
    return result

func _frost_contract() -> void:
    var holder := Node2D.new()
    root.add_child(holder)
    var op := _operator(holder, Vector2.ZERO)
    var robot := _enemy(holder, Vector2.ZERO)
    op.apply_run_boosts({"operator_speed_multiplier": 1.1})
    robot.apply_run_modifiers({"enemy_speed_multiplier": 1.2})
    var op_base := op.run_speed_multiplier
    var robot_base := robot.run_speed_multiplier
    var op_health := op.health
    var robot_health := robot.health
    var frost := _hazard(holder, "FROST_PLATE", Vector2.ZERO)
    frost._physics_process(frost.phase_left - 0.01)
    _check(op.hazard_speed_factor() == 1.0 and robot.hazard_speed_factor() == 1.0, "frost's first delay does not slow actors")
    frost._physics_process(0.01)
    _check(is_equal_approx(op.hazard_speed_factor(), 0.7) and is_equal_approx(robot.hazard_speed_factor(), 0.7), "live frost slows both actor kinds on entry")
    _check(op.run_speed_multiplier == op_base and robot.run_speed_multiplier == robot_base, "frost leaves FIELD STIM and robot contract multipliers byte-exact")
    _check(is_equal_approx(op.run_speed_multiplier * op.hazard_speed_factor(), 0.77) and is_equal_approx(robot.run_speed_multiplier * robot.hazard_speed_factor(), 0.84), "frost multiplies independent existing speed effects once")
    op.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    op._physics_process(1.0 / 60.0)
    _check(is_equal_approx(op.velocity.length(), op.walk_speed * op_base * 0.7), "real operator movement consumes frost and FIELD STIM factors together")
    op.debug_stop_drive()
    op.global_position = Vector2.ZERO
    var overlap := _hazard(holder, "FROST_PLATE", Vector2.ZERO, 1)
    overlap.spec = overlap.spec.duplicate(true)
    overlap.spec.slow_multiplier = 0.6
    overlap._physics_process(overlap.phase_left)
    _check(is_equal_approx(op.hazard_speed_factor(), 0.6) and is_equal_approx(robot.hazard_speed_factor(), 0.6), "overlapping frost uses the strongest factor instead of multiplying")
    overlap.release_effects()
    _check(is_equal_approx(op.hazard_speed_factor(), 0.7) and is_equal_approx(robot.hazard_speed_factor(), 0.7), "removing one frost leaves the other contribution intact")
    overlap.free()
    op.global_position = Vector2(300, 300)
    robot.global_position = Vector2(300, 300)
    frost._physics_process(0.1)
    _check(op.hazard_speed_factor() == 1.0 and robot.hazard_speed_factor() == 1.0 and op.run_speed_multiplier == op_base and robot.run_speed_multiplier == robot_base, "leaving frost exactly restores independent speed factors")
    op.global_position = Vector2.ZERO
    robot.global_position = Vector2.ZERO
    frost._physics_process(0.1)
    _check(is_equal_approx(op.hazard_speed_factor(), 0.7), "re-entering frost slows again")
    _check(op.health == op_health and robot.health == robot_health, "frost never deals damage")
    op.apply_damage(99999.0, "FROST_TEST_DOWN")
    _check(op.is_downed() and op.hazard_speed_factor() == 1.0, "downing clears slow tokens immediately")
    op.revive()
    _check(not op.is_downed() and op.hazard_speed_factor() == 1.0 and op.run_speed_multiplier == op_base, "reviving leaves no inherited frost factor and preserves FIELD STIM")
    op.global_position = Vector2(300, 300)
    frost._physics_process(0.1)
    _check(op.hazard_speed_factor() == 1.0, "reviving and walking off before the next tick leaves no stale factor")
    op.global_position = Vector2.ZERO
    frost._physics_process(0.1)
    frost.release_effects()
    _check(op.hazard_speed_factor() == 1.0 and robot.hazard_speed_factor() == 1.0, "hazard cleanup releases both actor factors immediately while occupied")
    _check(op.run_speed_multiplier == op_base and robot.run_speed_multiplier == robot_base, "hazard cleanup leaves other speed sources exactly unchanged")
    holder.free()
    await _frames(1)

func _fixture_followers() -> void:
    var stage := await _stage("MIS_CH01_06")
    stage.start_battle_preview(1)
    _freeze(stage)
    stage.call("_clear_hazards")
    await _frames(1)
    var points: Array[Vector2] = stage.battlefield.call("hazard_points", 1, 94.0)
    _check(not points.is_empty(), "live follower fixture has a hazard-safe open floor")
    if not points.is_empty():
        for id: String in IDS:
            var hazard := _hazard(stage, id, points[0])
            var follower: OperatorActor = stage.squad.operators[1]
            var goal := ZoneHazard.steer(self, follower.global_position, hazard.global_position, stage)
            _check(not hazard.contains(goal, ZoneHazard.SAFE_MARGIN) and stage.battlefield.is_walkable(goal), id + " pushes an AI goal to painted floor outside its hazard")
            if id != "FROST_PLATE":
                await _follower(stage, hazard, id)
            stage.call("_clear_hazards")
            await _frames(1)
        var frost := _hazard(stage, "FROST_PLATE", points[0])
        var op: OperatorActor = stage.squad.operators[1]
        op.global_position = points[0]
        frost._physics_process(frost.phase_left)
        _check(op.hazard_speed_factor() < 1.0, "room cleanup fixture applies frost")
        stage.call("_clear_hazards")
        _check(op.hazard_speed_factor() == 1.0 and _hazards(stage).is_empty(), "room cleanup removes frost and its factor in the same stack")
    stage.free()
    await _frames(2)

## Movement checks execute the real controllers, including the SPACE action.
## Reset the drive acceleration/state between A/B so only frost differs.
func _frost_dash_and_enemy_movement() -> void:
    var holder := Node2D.new()
    root.add_child(holder)
    var op := _operator(holder, Vector2(400, 0))
    var robot := _enemy(holder, Vector2.ZERO)
    robot.apply_run_modifiers({"enemy_speed_multiplier": 1.2})
    robot.tactics.state = "REPOSITION"
    robot.tactics.state_left = 10.0
    robot._drive_speed = 10000.0
    robot._physics_process(1.0 / 60.0)
    var plain_speed := robot.velocity.length()
    _check(plain_speed > 10.0, "enemy movement fixture commands a real reposition")
    robot.global_position = Vector2.ZERO
    robot.tactics.state = "REPOSITION"
    robot.tactics.state_left = 10.0
    robot._drive_speed = 10000.0
    var frost := _hazard(holder, "FROST_PLATE", Vector2.ZERO)
    frost._physics_process(frost.phase_left)
    robot._physics_process(1.0 / 60.0)
    _check(absf(robot.velocity.length() / maxf(0.01, plain_speed) - 0.7) < 0.001, "actual enemy movement falls to exactly 0.7 while its contract remains 1.2")
    _check(is_equal_approx(robot.run_speed_multiplier, 1.2), "actual enemy frost movement does not mutate its contract")
    frost.release_effects()
    robot.global_position = Vector2.ZERO
    robot.tactics.state = "REPOSITION"
    robot.tactics.state_left = 10.0
    robot._drive_speed = 10000.0
    robot._physics_process(1.0 / 60.0)
    _check(absf(robot.velocity.length() - plain_speed) < 0.001, "actual enemy movement is fully restored when frost is cleared")
    frost.free()
    robot.global_position = Vector2(1000, 1000)
    op.global_position = Vector2(-300, -300)
    op.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    DemoInput.reset()
    DemoInput.held[KEY_SPACE] = true
    op.call("_handle_player_actions", Vector2.RIGHT)
    DemoInput.held.erase(KEY_SPACE)
    op._physics_process(0.01)
    _check(is_equal_approx(op.velocity.length(), 520.0), "SPACE dash keeps the shipped 520 px/s outside frost")
    op.set_hazard_speed_factor("DASH_FROST", 0.7)
    op._physics_process(0.01)
    var first_slow := op.velocity.length()
    op._physics_process(0.01)
    _check(is_equal_approx(first_slow, 364.0) and is_equal_approx(op.velocity.length(), 364.0), "SPACE dash uses 0.7 once and never compounds it on later frames")
    op.remove_hazard_speed_factor("DASH_FROST")
    op._physics_process(0.01)
    _check(is_equal_approx(op.velocity.length(), 520.0), "leaving frost during the same SPACE dash restores its original request")
    op._dash_left = 0.0
    op.velocity = Vector2.ZERO
    op.global_position = Vector2(-300, -300)
    var start := op.global_position
    op.skill_dash(Vector2.RIGHT, 100.0)
    var plain_distance := op.global_position.distance_to(start)
    _check(absf(plain_distance - 100.0) < 0.01, "skill dash keeps its requested distance outside frost")
    op._dash_left = 0.0
    op.velocity = Vector2.ZERO
    op.global_position = start
    op.set_hazard_speed_factor("SKILL_FROST", 0.7)
    op.skill_dash(Vector2.RIGHT, 100.0)
    _check(absf(op.global_position.distance_to(start) - plain_distance * 0.7) < 0.01, "skill dash swept distance is exactly 0.7 on frost")
    op.remove_hazard_speed_factor("SKILL_FROST")
    op._dash_left = 0.0
    op.velocity = Vector2.ZERO
    op.global_position = start
    op.skill_dash(Vector2.RIGHT, 100.0)
    _check(absf(op.global_position.distance_to(start) - plain_distance) < 0.01, "skill dash requested distance returns exactly after frost")
    op.debug_stop_drive()
    DemoInput.reset()
    holder.free()
    await _frames(2)

func _hurt_nodes(actor: OperatorActor) -> Dictionary:
    var result: Dictionary = {}
    for node in root.get_children():
        var fx := node as CombatHitVFX
        if fx != null and fx.effect_kind == CombatHitVFX.EFFECT_HURT and fx.target_kind == "OPERATOR" and fx.target_id == actor.operator_id:
            result[fx.get_instance_id()] = true
    return result

func _added_hurts(before: Dictionary, after: Dictionary) -> int:
    var added := 0
    for id in after:
        if not before.has(id): added += 1
    return added

## Rapid DOT still records every health/source tick. Only its tiny visual
## flinches are bounded by 90ms; ordinary hits, heavy hits and downs are intact.
func _spore_flinch_budget() -> void:
    var holder := Node2D.new()
    root.add_child(holder)
    var op := _operator(holder, Vector2.ZERO)
    var events: Array[Dictionary] = []
    var health_events: Array[float] = []
    op.damage_taken.connect(func(_actor, amount, source): events.append({"amount": amount, "source": source}))
    op.health_changed.connect(func(_actor, health, _max): health_events.append(float(health)))
    var health := op.health
    var before := _hurt_nodes(op)
    var began := Time.get_ticks_msec()
    for frame in range(120): op.apply_damage(4.0 / 60.0, "HAZARD_SPORE_CLOUD")
    var elapsed := Time.get_ticks_msec() - began
    var added := _added_hurts(before, _hurt_nodes(op))
    _check(events.size() == 120 and health_events.size() == 120 and absf(health - op.health - 8.0) < 0.001, "spore visual throttling preserves every health/source tick and exactly 8 damage")
    _check(events.all(func(row: Dictionary) -> bool: return row.source == "HAZARD_SPORE_CLOUD") and absf(_total(events) - 8.0) < 0.001, "throttled spore still attributes every actual damage increment")
    _check(added >= 1 and added <= 1 + int(elapsed / 90), "spore FLINCH effects obey the 90ms budget (%d effects/%dms)" % [added, elapsed])
    before = _hurt_nodes(op)
    op.apply_damage(0.01, "GENERAL_TEST")
    op.apply_damage(0.01, "GENERAL_TEST")
    _check(_added_hurts(before, _hurt_nodes(op)) == 2, "ordinary small hits retain both unthrottled visual reactions")
    before = _hurt_nodes(op)
    op.apply_damage(op.max_health * 0.2, "HAZARD_SPORE_CLOUD")
    _check(_added_hurts(before, _hurt_nodes(op)) == 1, "heavy spore damage is never suppressed by the tiny-FLINCH budget")
    before = _hurt_nodes(op)
    op.apply_damage(99999.0, "HAZARD_SPORE_CLOUD")
    _check(op.is_downed() and _added_hurts(before, _hurt_nodes(op)) == 1, "spore down keeps its full visible reaction")
    cycles.append({"hazard": "SPORE_CLOUD", "rapid_ticks": 120, "actual_damage": 8.0,
        "spore_flinch_effects": added, "elapsed_ms": elapsed, "min_flinch_interval_ms": 90})
    holder.free()
    await _frames(2)

func _follower(stage: StoryStage01, hazard: ZoneHazard, label: String) -> void:
    var squad := stage.squad
    var follower: OperatorActor = squad.operators[1]
    follower.reset_for_battle_preview()
    for actor in squad.operators: actor.global_position = hazard.global_position + Vector2(300, 180)
    squad.get_active_operator().global_position = hazard.global_position + Vector2(8, 2)
    follower.global_position = hazard.global_position + Vector2(-6, 3)
    follower.set_controlled(false)
    follower.set_ai_goal(hazard.global_position)
    follower.set_physics_process(true)
    hazard.phase = ZoneHazard.Phase.TELEGRAPH
    hazard.phase_left = float(hazard.spec.telegraph)
    hazard.set_physics_process(true)
    var before := follower.health
    var serial := hazard.discharges
    var left_at := -1
    for frame in range(120):
        await physics_frame
        if left_at < 0 and not hazard.contains(follower.global_position): left_at = frame
        if hazard.discharges > serial: break
    _check(hazard.discharges > serial, label + " live warning finishes")
    _check(left_at >= 0 and not hazard.contains(follower.global_position), "%s follower walks off before damage (frame %d)" % [label, left_at])
    _check(follower.health == before, label + " follower escapes without hazard damage")
    follower.set_physics_process(false)
    hazard.set_physics_process(false)

func _stage(mission: String) -> StoryStage01:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    stage.battle_preview = true
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.configure_campaign({}, "HAZARD-EXPANSION-SMOKE", {})
    _freeze(stage)
    return stage

func _freeze(stage: StoryStage01) -> void:
    stage.set_process(false)
    stage.set_physics_process(false)
    stage.squad.set_process(false)
    stage.squad.set_physics_process(false)
    for actor in stage.squad.operators:
        actor.set_process(false)
        actor.set_physics_process(false)
    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.set_physics_process(false)
    for hazard in _hazards(stage): hazard.set_physics_process(false)

func _mission(mission: String) -> void:
    var stage := await _stage(mission)
    for step in range(stage.main_route.size()):
        var room: Dictionary = stage.main_route[step]
        var declared := 0
        for row: Dictionary in room.get("hazards", []): declared += int(row.get("count", 1))
        if str(room.get("type", "")) == "BOSS": _check(declared == 0, mission + " boss room declares no hazards")
        if declared == 0: continue
        stage.start_battle_preview(step)
        _freeze(stage)
        var hazards := _hazards(stage)
        var label := "%s %s" % [mission, room.id]
        _check(hazards.size() == declared, "%s places exactly %d declared hazards (%d)" % [label, declared, hazards.size()])
        var tips := str(stage.call("_combat_story", str(room.type)))
        for hazard in hazards: _check(tips.contains(ZoneHazard.tip(hazard.hazard_id)), label + " explains " + hazard.hazard_id)
        _placement(stage, hazards, label)
        await _escape_grid(stage, hazards, label)
        stage.call("_clear_hazards")
        _check(_hazards(stage).is_empty(), label + " clears all hazards immediately")
        await _frames(1)
    stage.free()
    await _frames(2)

func _placement(stage: StoryStage01, hazards: Array[ZoneHazard], label: String) -> void:
    var footprints: Array[PackedVector2Array] = []
    for cover in get_nodes_in_group("sable_environment_cover"):
        var polygon := PackedVector2Array()
        for corner: Vector2 in cover.ground: polygon.append(cover.to_global(corner))
        footprints.append(polygon)
    var spawns: Array = stage.battlefield.call("debug_spawn_points")
    for hazard in hazards:
        var floor_ok := true
        var cover_ok := true
        var boundary := hazard.boundary_points(32)
        var samples := PackedVector2Array(boundary)
        if str(hazard.spec.get("shape", "")) == "band":
            for edge in range(boundary.size()):
                for fraction in range(1, 9):
                    samples.append(boundary[edge].lerp(boundary[(edge + 1) % boundary.size()], float(fraction) / 9.0))
        for point in samples:
            floor_ok = floor_ok and stage.battlefield.is_walkable(point)
            for footprint in footprints:
                if Geometry2D.is_point_in_polygon(point, footprint): cover_ok = false
        for footprint in footprints:
            if not Geometry2D.intersect_polygons(boundary, footprint).is_empty(): cover_ok = false
            for corner in footprint:
                if hazard.contains(corner): cover_ok = false
        _check(floor_ok, label + " whole " + hazard.hazard_id + " lies on painted floor")
        _check(cover_ok, label + " whole " + hazard.hazard_id + " avoids cover")
        var squad_gap := INF
        for index in range(3): squad_gap = minf(squad_gap, hazard.global_position.distance_to(stage.battlefield.call("squad_spawn", index)))
        _check(squad_gap >= hazard.radius + 90.0, "%s %s squad clearance %.1f >= %.1f" % [label, hazard.hazard_id, squad_gap, hazard.radius + 90.0])
        var spawn_gap := INF
        for point: Vector2 in spawns.slice(0, 4): spawn_gap = minf(spawn_gap, hazard.global_position.distance_to(point))
        _check(spawn_gap >= hazard.radius + 30.0, "%s %s spawn clearance %.1f >= %.1f" % [label, hazard.hazard_id, spawn_gap, hazard.radius + 30.0])
        for other in hazards:
            if other == hazard: continue
            var required := maxf(hazard.radius, other.radius) * 2.6
            _check(hazard.global_position.distance_to(other.global_position) >= required, label + " spreads mixed hazard bounding radii apart")

func _escape_grid(stage: StoryStage01, hazards: Array[ZoneHazard], label: String) -> void:
    var victim: OperatorActor = stage.squad.operators[0]
    var spots := 0
    var failing := 0
    var worst := 0.0
    var tightest := INF
    var examples: Array[String] = []
    var timed := {"standable_spots": 0, "failed_spots": 0, "worst_walk_px": 0.0,
        "tightest_margin_s": INF, "blocked_negative_checks": 0, "blocked_negative_rejected": 0}
    var untimed := {"kind": "untimed slow-escape", "standable_spots": 0, "failed_spots": 0,
        "worst_walk_px": 0.0, "blocked_negative_checks": 0, "blocked_negative_rejected": 0}
    var hazard_reports: Array[Dictionary] = []
    # A harmless slow has no warning deadline. Its search span is the current
    # room's actual floor bounding-box diagonal, not a new gameplay time limit.
    var room_span := _room_search_span(stage)
    for hazard in hazards:
        var slowing := str(hazard.spec.get("mode", "burst")) == "slow"
        var counts: Dictionary = untimed if slowing else timed
        var obstacles: Array[Rect2] = NAV.ground_obstacles(victim, hazard.global_position)
        var limit := room_span if slowing else (float(hazard.spec.telegraph) - ESCAPE_MARGIN) * SLOWEST_WALK
        var hazard_spots := 0
        var hazard_failing := 0
        var hazard_worst := 0.0
        var steps := int(ceil(hazard.radius / GRID))
        for ix in range(-steps, steps + 1):
            for iy in range(-steps, steps + 1):
                var spot := hazard.global_position + Vector2(ix, iy) * GRID
                if not hazard.contains(spot) or not _standable(stage, obstacles, spot): continue
                spots += 1
                hazard_spots += 1
                counts.standable_spots += 1
                var distance := _nearest_escape(stage, victim, hazards, obstacles, spot, limit, slowing)
                if distance < 0.0:
                    failing += 1
                    hazard_failing += 1
                    counts.failed_spots += 1
                    if examples.size() < 12: examples.append("%s (%d,%d)" % [hazard.hazard_id, spot.x, spot.y])
                else:
                    worst = maxf(worst, distance)
                    hazard_worst = maxf(hazard_worst, distance)
                    counts.worst_walk_px = maxf(float(counts.worst_walk_px), distance)
                    if not slowing:
                        tightest = minf(tightest, float(hazard.spec.telegraph) - distance / SLOWEST_WALK)
                        timed.tightest_margin_s = tightest
        _check(hazard_spots > 0, "%s %s checks a real standable hazard interior (%d spots)" % [label, hazard.hazard_id, hazard_spots])
        # A blocked route cannot pass merely because its destination is clear.
        var blocked: Array[Rect2] = [Rect2(hazard.global_position - Vector2(500, 500), Vector2(1000, 1000))]
        # Rectangles are now a broad phase only. Give this control a real layer-1
        # body, and wait for physics to register it before querying an escape.
        var blocker := _negative_cover_blocker(stage, hazard.global_position)
        await _frames(2)
        var blocked_rejected := _nearest_escape(stage, victim, hazards, blocked, hazard.global_position, limit, slowing) < 0.0
        blocker.free()
        await _frames(2)
        _check(blocked_rejected, label + " negative control rejects a cover-blocked escape")
        counts.blocked_negative_checks += 1
        if blocked_rejected: counts.blocked_negative_rejected += 1
        hazard_reports.append({"hazard": hazard.hazard_id, "escape_kind": "untimed slow-escape" if slowing else "timed damage-escape",
            "standable_spots": hazard_spots, "failed_spots": hazard_failing, "worst_walk_px": hazard_worst,
            "search_span_px": limit, "blocked_negative_rejected": blocked_rejected})
    _check(spots > 0, label + " tests actual standable hazard interiors on a 25px grid")
    _check(failing == 0, "%s all painted-floor hazard escapes exist at %d spots (%d fail)" % [label, spots, failing])
    _check(int(timed.failed_spots) == 0, "%s timed painted-floor escapes meet 138px/s + 0.25s at all %d damaging spots (%d fail)" % [label, int(timed.standable_spots), int(timed.failed_spots)])
    _check(int(untimed.failed_spots) == 0, "%s untimed slow-escape paths exist at all %d frost spots (%d fail)" % [label, int(untimed.standable_spots), int(untimed.failed_spots)])
    report.append({"room": label, "hazards": hazards.map(func(hazard: ZoneHazard) -> String: return hazard.hazard_id),
        "standable_spots": spots, "failed_spots": failing, "worst_walk_px": worst,
        "tightest_margin_s": tightest, "failing_examples": examples, "timed": timed, "untimed": untimed,
        "room_search_span_px": room_span, "hazard_escapes": hazard_reports})

func _negative_cover_blocker(stage: StoryStage01, point: Vector2) -> StaticBody2D:
    var blocker := StaticBody2D.new()
    blocker.collision_layer = 1
    blocker.collision_mask = 0
    var collider := CollisionShape2D.new()
    var shape := RectangleShape2D.new()
    shape.size = Vector2(1000, 1000)
    collider.shape = shape
    blocker.add_child(collider)
    stage.add_child(blocker)
    blocker.global_position = point
    return blocker

func _room_search_span(stage: StoryStage01) -> float:
    var floor_points: PackedVector2Array = stage.battlefield.polygon
    if floor_points.is_empty(): return 0.0
    var bounds := Rect2(floor_points[0], Vector2.ZERO)
    for point in floor_points: bounds = bounds.expand(point)
    return bounds.size.length()

func _standable(stage: StoryStage01, obstacles: Array[Rect2], point: Vector2) -> bool:
    return stage.battlefield.is_walkable(point) and obstacles.all(func(rect: Rect2) -> bool: return not rect.has_point(point))

func _nearest_escape(stage: StoryStage01, victim: OperatorActor, hazards: Array[ZoneHazard], obstacles: Array[Rect2], origin: Vector2, limit: float, avoid_slow := false) -> float:
    for ring in range(1, int(floor(limit / 5.0)) + 1):
        var distance := float(ring) * 5.0
        for index in range(48):
            var point := origin + Vector2.from_angle(TAU * float(index) / 48.0) * distance
            if not _standable(stage, obstacles, point): continue
            if hazards.any(func(hazard: ZoneHazard) -> bool: return (avoid_slow or str(hazard.spec.get("mode", "burst")) != "slow") and hazard.contains(point, 1.0)): continue
            if NAV._clear_ground(victim, origin, point, obstacles): return distance
    return -1.0

func _hazards(stage: Node) -> Array[ZoneHazard]:
    var result: Array[ZoneHazard] = []
    for node in get_nodes_in_group("zone_hazards"):
        if stage.is_ancestor_of(node) and not node.is_queued_for_deletion(): result.append(node as ZoneHazard)
    return result

func _frames(count: int) -> void:
    for _index in range(count):
        await physics_frame
        await process_frame

func _check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label)
