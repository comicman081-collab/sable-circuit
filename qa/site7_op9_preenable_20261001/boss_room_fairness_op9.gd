extends SceneTree
## site7_boss_pattern_smoke.gd fits the newer bosses' attacks to open floor. This test lays the same attacks
## on the boss's own room in each playable operation: wherever the operator can stand on that room's painted
## floor (off the cover), some floor no warning covers must lie within NEW_BOSS_GAP_LIMIT, be reached by a
## straight walk that stays on floor and clear of cover, and the slowest operator must get there ESCAPE_MARGIN
## before the warning on the spot goes off. Nothing here approves art, balance or play.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const PATTERN := preload("res://tests/smoke/site7_boss_pattern_smoke.gd")
const Catalog := preload("res://scripts/core/site7_campaign.gd")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TestOutput := preload("res://tests/support/test_output.gd")
## Route step of the boss room in every mission file.
const BOSS_ROOM_STEP := 4
## Target spots: a grid this far apart (`--grid=<px>` overrides), at least MIN_BOSS_DISTANCE and at most REACH
## from the boss.
const DEFAULT_GRID := 50.0
const MIN_BOSS_DISTANCE := 150.0
const REACH := 800.0
var grid := DEFAULT_GRID
var failures: Array[String] = []
var checks := 0
var report: Array[Dictionary] = []
var emissions: Array[Dictionary] = []

func _init() -> void:
    call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func settle(frames: int = 3) -> void:
    for _i in range(frames):
        await physics_frame
        await process_frame

func run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--grid="): grid = maxf(20.0, float(arg.get_slice("=", 1)))
    var checked := 0
    for mission_id in ["MIS_CH01_09"]:
        var boss_id := _boss_id(mission_id)
        if not PATTERN.NEW_BOSSES.has(boss_id): continue
        checked += 1
        await _room(mission_id, boss_id)
    check(checked > 0, "at least one playable operation stands a newer boss")
    var out := TestOutput.path("res://.cache/site7_boss_room_fairness.json")
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": "PASS" if failures.is_empty() else "FAIL", "checks": checks, "failures": failures,
        "gap_limit_px": PATTERN.NEW_BOSS_GAP_LIMIT, "escape_margin_s": PATTERN.ESCAPE_MARGIN, "slowest_walk_px_per_s": PATTERN.SLOWEST_WALK,
        "grid_px": grid, "rooms": report, "visual_approval": false}, "  "))
    file.close()
    print("SITE7_BOSS_ROOM_FAIRNESS: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks) ", out)
    quit(0 if failures.is_empty() else 1)

func _boss_id(mission_id: String) -> String:
    var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission_id))
    var route: Array = mission.get("main_route", [])
    if route.size() <= BOSS_ROOM_STEP: return ""
    var encounter: Array = (route[BOSS_ROOM_STEP] as Dictionary).get("encounter", [])
    return str((encounter[0] as Dictionary).get("enemy_id", "")) if not encounter.is_empty() else ""

func _room(mission_id: String, boss_id: String) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await settle(8)
    stage.start_battle_preview(BOSS_ROOM_STEP)
    await settle(4)
    var boss: EnemyActor
    for enemy in get_nodes_in_group("m3_enemies"):
        if not stage.is_ancestor_of(enemy): continue
        enemy.set_physics_process(false)
        if enemy.enemy_id == boss_id: boss = enemy
    check(boss != null, "%s stands %s in its boss room" % [mission_id, boss_id])
    if boss == null:
        stage.free()
        return
    boss.projectile_emitted.connect(func(row: Dictionary) -> void: emissions.append(row))
    stage.set_process(false)
    stage.set_physics_process(false)
    stage.squad.set_process(false)
    stage.squad.set_physics_process(false)
    for operator in stage.squad.operators:
        operator.set_process(false)
        operator.set_physics_process(false)
    var victim := stage.squad.get_active_operator()
    var origin := boss.global_position
    var obstacles: Array[Rect2] = NAV.ground_obstacles(victim, origin)
    var width := victim.get_combat_hit_rect().size.x * 1.5
    var spots: Array[Vector2] = []
    var steps := int(REACH / grid)
    for ix in range(-steps, steps + 1):
        for iy in range(-steps, steps + 1):
            var point := origin + Vector2(float(ix), float(iy)) * grid
            var distance := point.distance_to(origin)
            if distance < MIN_BOSS_DISTANCE or distance > REACH: continue
            if _standable(stage, obstacles, point): spots.append(point)
    check(spots.size() >= 20, "%s: the boss room offers floor to stand on (%d spots)" % [mission_id, spots.size()])
    var worst := {"radius": 0, "where": ""}
    var tightest := {"margin": 99.0, "where": ""}
    var failing: Array[String] = []
    var evaluated := 0
    for spot in spots:
        for phase in range(1, 4):
            for serial in range(1, 3):
                victim.global_position = spot
                var rows := _attack_rows(boss, victim, phase, serial)
                evaluated += 1
                var radius := _nearest_clear(stage, victim, obstacles, rows, spot, width)
                var where := "phase %d attack %d, target at (%d, %d), %d px from the boss" % [phase, serial, int(spot.x), int(spot.y), int(spot.distance_to(origin))]
                if radius < 0 or radius > int(worst.radius): worst = {"radius": radius, "where": where}
                var ok := radius > 0 and radius <= PATTERN.NEW_BOSS_GAP_LIMIT
                var covering := rows.filter(func(row: Dictionary) -> bool: return _covers(row, spot))
                if not covering.is_empty():
                    var earliest := 99.0
                    for row in covering: earliest = minf(earliest, float(row.windup))
                    var margin := earliest - float(maxi(radius, 0)) / PATTERN.SLOWEST_WALK
                    if margin < float(tightest.margin): tightest = {"margin": margin, "where": where + " (leave %d px in %.2f s of %.2f s)" % [radius, float(maxi(radius, 0)) / PATTERN.SLOWEST_WALK, earliest]}
                    ok = ok and margin >= PATTERN.ESCAPE_MARGIN
                if not ok: failing.append(where + " (nearest clear floor %d px)" % radius)
    check(failing.is_empty(), "%s (%s): safe floor within %d px, reachable in time, wherever the target stands on the room floor: %d of %d attacks fail, e.g. %s" % [
        mission_id, boss_id, PATTERN.NEW_BOSS_GAP_LIMIT, failing.size(), evaluated, failing[0] if not failing.is_empty() else "none"])
    # Negative control: a warning that covers the whole room must leave no safe floor.
    if not spots.is_empty():
        victim.global_position = spots[0]
        var rows := _attack_rows(boss, victim, 1, 1)
        rows.append({"kind": "circle", "at": spots[0], "radius": 2000.0, "windup": 1.1})
        check(_nearest_clear(stage, victim, obstacles, rows, spots[0], width) == -1, "Negative control: a room-wide warning leaves no safe floor")
    report.append({"mission": mission_id, "boss": boss_id, "spots": spots.size(), "attacks_evaluated": evaluated, "failing": failing.size(),
        "nearest_clear_floor_worst_px": int(worst.radius), "nearest_clear_floor_worst_at": worst.where,
        "tightest_escape_margin_s": snappedf(float(tightest.margin), 0.01), "tightest_escape_at": tightest.where,
        "failing_examples": failing.slice(0, 12), "cover_obstacles": obstacles.size()})
    stage.free()
    await settle(3)

## A spot the operator can stand on: painted floor and outside every cover footprint.
func _standable(stage: StoryStage01, obstacles: Array[Rect2], point: Vector2) -> bool:
    if not stage.battlefield.is_walkable(point): return false
    return obstacles.all(func(rect: Rect2) -> bool: return not rect.has_point(point))

## One attack laid on the target as plain rows (kind, start, direction, sizes, wind-up); the warnings and
## shots are freed.
func _attack_rows(boss: EnemyActor, victim: OperatorActor, phase: int, serial: int) -> Array[Dictionary]:
    var toward := (victim.global_position - boss.global_position).normalized()
    boss.tactics.phase = phase
    boss.tactics.attack_serial = serial
    boss.tactics.locked_aim = toward
    boss.tactics.locked_ground = toward
    boss.tactics._shot_ordinal = 0
    emissions.clear()
    boss.tactics._boss_attack(victim)
    var rows: Array[Dictionary] = []
    for warning in get_nodes_in_group("site7_attack_warnings"):
        rows.append({"kind": warning.kind, "at": warning.global_position, "ray": warning.ray, "radius": warning.radius,
            "reach": warning.reach, "half": warning.half_width, "windup": warning.windup})
    for row in emissions:
        var projectile := instance_from_id(row.projectile_id)
        if is_instance_valid(projectile): projectile.free()
    for warning in get_nodes_in_group("site7_attack_warnings"): warning.free()
    for node in root.get_children():
        if node is PrototypeProjectile: node.free()
    return rows

func _covers(row: Dictionary, point: Vector2) -> bool:
    if row.kind == "circle":
        return (row.at as Vector2).distance_to(point) <= float(row.radius)
    var offset: Vector2 = point - (row.at as Vector2)
    var ray: Vector2 = row.ray
    var forward := offset.dot(ray)
    return forward >= 0.0 and forward <= float(row.reach) and absf(offset.dot(ray.orthogonal())) <= float(row.half)

## Nearest ring (30 px steps up to 300) holding a 1.5-actor-wide patch of standable floor that no warning
## covers and that a straight walk from `from` reaches, or -1.
func _nearest_clear(stage: StoryStage01, victim: OperatorActor, obstacles: Array[Rect2], rows: Array[Dictionary], from: Vector2, width: float) -> int:
    for radius in range(30, 301, 30):
        for i in range(64):
            var direction := Vector2.from_angle(float(i) * TAU / 64.0)
            var center := from + direction * float(radius)
            var tangent := direction.orthogonal() * width * 0.5
            var patch: Array[Vector2] = [center - tangent, center, center + tangent]
            if not patch.all(func(point: Vector2) -> bool: return _standable(stage, obstacles, point)): continue
            if not patch.all(func(point: Vector2) -> bool: return rows.all(func(row: Dictionary) -> bool: return not _covers(row, point))): continue
            if NAV._clear_ground(victim, from, center, obstacles): return radius
    return -1
