extends SceneTree
## Freeze the shipped ANCHOR attack and every other boss's shape, then hold all ten bosses to
## the fairness rules: at most seven warnings, 1.0 s of wind-up, warning damage 20, projectile
## damage 24, a clear 1.5-actor-wide patch of floor within 300 px, and no two bosses sharing a
## shape in a phase. The five bosses of operations 6-10 also have their geometry checked.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")
const OTHER_BOSSES := ["BOSS_SITE7_RELAY_01", "BOSS_SITE7_REMNANT_01", "BOSS_SITE7_FORGE_01", "BOSS_SITE7_CARRIER_01",
    "BOSS_SITE7_AERATOR_01", "BOSS_SITE7_CRYO_01", "BOSS_SITE7_GANTRY_01", "BOSS_SITE7_ARCHIVE_01", "BOSS_SITE7_ORIGIN_01"]
## Shots / circles / lanes of attack A and attack B in phases 1-3, as this smoke's three
## operators see them. A later edit that changes a shape shows up here.
const SIGNATURES := {
    "BOSS_SITE7_RELAY_01": ["S0C3L0/S0C3L0", "S0C5L0/S2C0L0", "S0C7L0/S2C0L0"],
    "BOSS_SITE7_REMNANT_01": ["S0C0L3/S0C0L3", "S0C0L3/S0C1L2", "S0C0L5/S0C1L2"],
    "BOSS_SITE7_FORGE_01": ["S0C1L0/S2C0L0", "S0C2L0/S2C0L0", "S0C2L2/S2C0L2"],
    "BOSS_SITE7_CARRIER_01": ["S2C0L1/S2C0L1", "S0C0L3/S0C0L3", "S0C1L3/S0C1L3"],
    "BOSS_SITE7_AERATOR_01": ["S0C4L0/S0C4L0", "S0C6L0/S3C0L0", "S0C7L0/S0C7L0"],
    "BOSS_SITE7_CRYO_01": ["S0C0L2/S2C0L0", "S0C0L3/S0C0L4", "S0C0L5/S0C0L5"],
    "BOSS_SITE7_GANTRY_01": ["S0C0L2/S0C1L0", "S0C0L3/S0C2L0", "S0C0L4/S0C1L4"],
    "BOSS_SITE7_ARCHIVE_01": ["S0C1L0/S0C2L0", "S0C3L0/S0C3L0", "S0C4L0/S0C4L1"],
    "BOSS_SITE7_ORIGIN_01": ["S0C0L3/S2C1L0", "S0C0L4/S2C2L0", "S0C1L5/S0C2L3"],
}
## Operations 6-10 keep a patch of safe floor this close to the target (px): the slowest
## operator walks 138 px/s and a warning winds up for at least 1.1 s.
const NEW_BOSS_GAP_LIMIT := 180
const NEW_BOSSES := ["BOSS_SITE7_AERATOR_01", "BOSS_SITE7_CRYO_01", "BOSS_SITE7_GANTRY_01", "BOSS_SITE7_ARCHIVE_01", "BOSS_SITE7_ORIGIN_01"]
const FLOOR := Rect2(Vector2(-100.0, -300.0), Vector2(800.0, 800.0))
## The sweep puts the target at these distances and bearings from a new boss, on open floor.
const SWEEP_DISTANCES := [150.0, 250.0, 350.0, 450.0, 550.0]
const SWEEP_BEARINGS := [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]
## CRYO's last-phase axis lane reaches the second frost bar and stops. Its old 900 px ran on over the target
## and left no gap beside it where a boss room narrows (site7_boss_room_fairness_smoke.gd, operation 7's vault).
## That test found none at 340 px or less and 10 spots at 400 px, so a longer lane is a fairness regression.
const CRYO_AXIS_REACH := 300.0
const CRYO_AXIS_REACH_LIMIT := 340.0
## GANTRY's phase-two diagonal rails and its phase-three star wind up this long. Beside a wall the nearest gap in a
## star can be 180 px away, 1.30 s at the slowest walk; the old 1.4 s and 1.5 s failed 101 of 1,410 attacks on
## operation 8's terminal floor (site7_boss_room_fairness_smoke.gd). Anything under GANTRY_LATE_WINDUP_MIN
## (the walk out plus ESCAPE_MARGIN) is a fairness regression.
const GANTRY_LATE_WINDUP := 1.6
const GANTRY_LATE_WINDUP_MIN := 1.56
## INDEX SPIRE's newest echo circle winds up this long, each older echo 0.1 s later, then the target's own ground
## (+0.3 s) and the last phase's lane (+0.4 s). A target that stands still stacks every echo on its own spot, so the
## newest one is the time it has to leave: beside a wall the nearest gap is 120 px, 0.87 s at the slowest walk, and the
## old 1.0 s left 0.13 s where site7_boss_room_fairness_smoke.gd asks 0.25 s (2 of 4,524 attacks on operation 9's stacks
## room at a 25 px grid). Anything under ECHO_WINDUP_MIN (that walk plus ESCAPE_MARGIN) is a fairness regression.
const ECHO_WINDUP := 1.3
const ECHO_WINDUP_MIN := 1.12
## ORIGIN's last-phase lanes, core circle and target circle wind up this long. Beside a wall the nearest gap between the
## three lanes and the two circles is 150 px away, 1.09 s at the slowest walk; the old 1.2 s / 1.3 s left 0.11 s where
## site7_boss_room_fairness_smoke.gd asks 0.25 s (3 spots of 5,743 at a 10 px grid on operation 10's core room, all of the
## last phase's second attack). Anything under ORIGIN_LATE_WINDUP_MIN (a 180 px walk out plus ESCAPE_MARGIN, the most the
## room limit allows) is a fairness regression.
const ORIGIN_LATE_WINDUP := 1.6
const ORIGIN_LATE_WINDUP_MIN := 1.56
## Walk speed of the slowest operator (ROOK), px/s.
const SLOWEST_WALK := 138.0
## Seconds to spare, beyond walking out at that speed, before the warning on the target's own spot goes off.
const ESCAPE_MARGIN := 0.25
var failures: Array[String] = []
var checks := 0
var emissions: Array[Dictionary] = []
var gap_radius := {}
var sweep_worst := {}
var last_gap := -1

func _init() -> void:
    call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func run() -> void:
    var actor := ENEMY.instantiate() as EnemyActor
    check(actor.configure("BOSS_SITE7_ANCHOR_01", 620.0), "anchor configures")
    root.add_child(actor)
    actor.set_physics_process(false)
    actor.global_position = Vector2(100.0, 100.0)
    var victim := OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01", "ASTER", Color.WHITE)
    root.add_child(victim)
    victim.set_physics_process(false)
    victim.global_position = Vector2(300.0, 100.0)
    actor.projectile_emitted.connect(func(row: Dictionary) -> void: emissions.append(row))
    for phase in range(1, 4):
        for serial in range(1, 3):
            var context := "anchor phase=%d serial=%d" % [phase, serial]
            actor.tactics.phase = phase
            actor.tactics.attack_serial = serial
            actor.tactics.locked_aim = Vector2.RIGHT
            actor.tactics.locked_ground = Vector2.RIGHT
            actor.tactics._shot_ordinal = 0
            emissions.clear()
            actor.tactics._boss_attack(victim)
            var warnings := get_nodes_in_group("site7_attack_warnings")
            var warning_turn := phase >= 2 and serial == 2
            var expected_shots := 0 if warning_turn else (3 if phase == 1 else 5)
            var expected_warnings := (5 if phase == 3 else 1) if warning_turn else 0
            check(emissions.size() == expected_shots, "shipped shot count " + context)
            check(warnings.size() == expected_warnings, "shipped warning count " + context)
            for i in range(emissions.size()):
                var row: Dictionary = emissions[i]
                var span := (float(i) - float(expected_shots - 1) * 0.5) * 0.22
                var direction := Vector2(row.direction[0], row.direction[1])
                check(direction.distance_to(Vector2.RIGHT.rotated(span)) < 0.0001, "shipped fan angle " + context)
            if warning_turn and warnings.size() == expected_warnings:
                var circle := warnings[0]
                check(circle.kind == "circle" and circle.global_position == victim.global_position, "shipped circle target " + context)
                check(circle.radius == 58.0 and circle.windup == 1.15 and circle.damage == 20.0, "shipped circle parameters " + context)
                if phase == 3:
                    for i in range(4):
                        var lane := warnings[i + 1]
                        var ray := Vector2.RIGHT.rotated(float(i) * PI * 0.5)
                        check(lane.kind == "lane" and lane.global_position.distance_to(actor.global_position + ray * 100.0) < 0.001, "shipped lane origin " + context)
                        check(lane.ray.distance_to(ray) < 0.001 and lane.reach == 430.0 and lane.half_width == 16.0 and lane.windup == 1.35 and lane.damage == 20.0, "shipped lane parameters " + context)
            for row in emissions:
                var bullet := instance_from_id(row.projectile_id)
                if is_instance_valid(bullet): bullet.free()
            for warning in warnings: warning.free()
    actor.free()
    var ally_one := OPERATOR.instantiate() as OperatorActor
    ally_one.configure("CHR_PROTO_02", "ROOK", Color.WHITE)
    root.add_child(ally_one)
    ally_one.set_physics_process(false)
    ally_one.global_position = Vector2(300.0, 250.0)
    var ally_two := OPERATOR.instantiate() as OperatorActor
    ally_two.configure("CHR_PROTO_03", "MICA", Color.WHITE)
    root.add_child(ally_two)
    ally_two.set_physics_process(false)
    ally_two.global_position = Vector2(300.0, -50.0)
    var signatures := {}
    for phase in range(1, 4):
        signatures[phase] = {"BOSS_SITE7_ANCHOR_01": ("S3C0L0/S3C0L0" if phase == 1 else ("S5C0L0/S0C1L0" if phase == 2 else "S5C0L0/S0C1L4"))}
    var negative_control_signature := ""
    for enemy_id in OTHER_BOSSES:
        var boss := _spawn_boss(enemy_id, Vector2(100.0, 100.0))
        gap_radius[enemy_id] = []
        for phase in range(1, 4):
            var parts: Array[String] = []
            var gaps: Array[int] = []
            for serial in range(1, 3):
                parts.append(_run_pattern_attack(boss, victim, phase, serial))
                gaps.append(last_gap)
            signatures[phase][enemy_id] = "/".join(parts)
            (gap_radius[enemy_id] as Array).append(gaps)
            check(str(signatures[phase][enemy_id]) == str((SIGNATURES[enemy_id] as Array)[phase - 1]), "%s phase %d keeps its shape %s (got %s)" % [enemy_id, phase, (SIGNATURES[enemy_id] as Array)[phase - 1], signatures[phase][enemy_id]])
            if enemy_id in NEW_BOSSES:
                for index in range(gaps.size()):
                    check(gaps[index] > 0 and gaps[index] <= NEW_BOSS_GAP_LIMIT, "%s phase %d attack %d keeps clear floor within %d px (nearest %d)" % [enemy_id, phase, index + 1, NEW_BOSS_GAP_LIMIT, gaps[index]])
        if enemy_id == "BOSS_SITE7_RELAY_01":
            # Deliberately collide two profile patterns in memory; the uniqueness
            # gate must reject the exact shapes the real tactics then produces.
            boss.art_profile["boss_pattern"] = "resonance_lanes"
            negative_control_signature = _run_pattern_attack(boss, victim, 1, 1) + "/" + _run_pattern_attack(boss, victim, 1, 2)
            boss.art_profile["boss_pattern"] = "relay_chain"
        boss.free()
    for phase in range(1, 4):
        check(_distinct((signatures[phase] as Dictionary).values()), "ten boss shapes differ in phase %d" % phase)
    var collision: Dictionary = signatures[1].duplicate()
    collision["BOSS_SITE7_RELAY_01"] = negative_control_signature
    check(negative_control_signature == str(collision["BOSS_SITE7_REMNANT_01"]), "negative control creates the same actual pattern")
    check(not _distinct(collision.values()), "duplicate boss pattern is rejected")
    var arenas := {}
    for enemy_id in ["BOSS_SITE7_ANCHOR_01"] + OTHER_BOSSES:
        var profile := ArtProfileRegistry.get_profile(enemy_id)
        var palette: Array = profile.get("palette", [])
        var accent := str(profile.get("arena_accent", str(palette[1]) if palette.size() > 1 else ""))
        check(not accent.is_empty() and not arenas.has(accent.to_lower()), "%s has its own arena colour %s" % [enemy_id, accent])
        arenas[accent.to_lower()] = enemy_id
    _verify_new_geometry(victim)
    _verify_gap_sweep(victim)
    ally_one.free()
    ally_two.free()
    victim.free()
    var out := TestOutput.path("res://.cache/site7_boss_pattern_baseline.json")
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": "PASS" if failures.is_empty() else "FAIL", "checks": checks, "failures": failures, "anchor_baseline": true, "bosses": OTHER_BOSSES.size() + 1, "signatures": signatures, "nearest_clear_floor_px": gap_radius, "new_boss_gap_limit_px": NEW_BOSS_GAP_LIMIT, "escape_margin_s": ESCAPE_MARGIN, "slowest_walk_px_per_s": SLOWEST_WALK, "new_boss_sweep_worst": sweep_worst, "negative_control_rejected": not _distinct(collision.values())}, "  "))
    file.close()
    print("SITE7_BOSS_PATTERN_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks) ", out)
    quit(0 if failures.is_empty() else 1)

func _spawn_boss(enemy_id: String, at: Vector2) -> EnemyActor:
    var boss := ENEMY.instantiate() as EnemyActor
    check(boss.configure(enemy_id, 800.0), enemy_id + " configures")
    root.add_child(boss)
    boss.set_physics_process(false)
    boss.global_position = at
    boss.projectile_emitted.connect(func(row: Dictionary) -> void: emissions.append(row))
    return boss

func _run_pattern_attack(boss: EnemyActor, victim: OperatorActor, phase: int, serial: int) -> String:
    var context := "%s phase=%d serial=%d" % [boss.enemy_id, phase, serial]
    boss.tactics.phase = phase
    boss.tactics.attack_serial = serial
    boss.tactics.locked_aim = Vector2.RIGHT
    boss.tactics.locked_ground = Vector2.RIGHT
    boss.tactics._shot_ordinal = 0
    emissions.clear()
    boss.tactics._boss_attack(victim)
    var warnings := get_nodes_in_group("site7_attack_warnings")
    check(warnings.size() <= 7, "at most seven warnings " + context)
    var circles := 0
    var lanes := 0
    for warning in warnings:
        if warning.kind == "circle": circles += 1
        elif warning.kind == "lane": lanes += 1
        check(warning.windup >= 1.0 and warning.damage <= 20.0, "warning time and damage " + context)
        check(warning.source == boss, "warning has attack owner " + context)
    check(_safe_floor_gap(warnings, victim), "300 px safe floor gap at 1.5 actor widths " + context)
    last_gap = _nearest_clear_floor(warnings, victim)
    for row in emissions:
        check(row.attack_serial == serial and row.actor_id == boss.get_instance_id(), "shot belongs to attack " + context)
        var projectile := instance_from_id(row.projectile_id) as PrototypeProjectile
        check(is_instance_valid(projectile) and projectile.damage <= 24.0, "projectile damage at most 24 " + context)
        if is_instance_valid(projectile): projectile.free()
    for warning in warnings: warning.free()
    return "S%dC%dL%d" % [emissions.size(), circles, lanes]

func _safe_floor_gap(warnings: Array[Node], victim: OperatorActor) -> bool:
    var width := victim.get_combat_hit_rect().size.x * 1.5
    for radius in [120.0, 180.0, 240.0, 300.0]:
        for i in range(64):
            if _clear_patch(warnings, victim.global_position, Vector2.from_angle(float(i) * TAU / 64.0), float(radius), width):
                return true
    return false

## The nearest ring (30 px steps) on which some 1.5-actor-wide patch of floor is not warned,
## or -1: how far the target has to walk to stand somewhere safe.
func _nearest_clear_floor(warnings: Array[Node], victim: OperatorActor) -> int:
    var width := victim.get_combat_hit_rect().size.x * 1.5
    for radius in range(30, 301, 30):
        for i in range(64):
            if _clear_patch(warnings, victim.global_position, Vector2.from_angle(float(i) * TAU / 64.0), float(radius), width):
                return radius
    return -1

func _clear_patch(warnings: Array[Node], from: Vector2, direction: Vector2, radius: float, width: float) -> bool:
    var center: Vector2 = from + direction * radius
    var tangent: Vector2 = direction.orthogonal() * width * 0.5
    var points: Array[Vector2] = [center - tangent, center, center + tangent]
    if not points.all(func(point: Vector2) -> bool: return FLOOR.has_point(point)):
        return false
    return points.all(func(point: Vector2) -> bool: return warnings.all(func(warning: Node) -> bool: return not warning.contains(point)))

func _distinct(values: Array) -> bool:
    var seen := {}
    for value in values:
        if seen.has(value): return false
        seen[value] = true
    return true

# --- operations 6-10: what each new pattern actually lays on the floor --------------------

## One attack read back as plain rows (kind, start, direction, sizes, wind-up) and shot
## directions; the warnings and shots are freed.
func _attack_rows(boss: EnemyActor, victim: OperatorActor, phase: int, serial: int) -> Dictionary:
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
    var shots: Array[Vector2] = []
    for row in emissions:
        shots.append(Vector2(row.direction[0], row.direction[1]))
        var projectile := instance_from_id(row.projectile_id)
        if is_instance_valid(projectile): projectile.free()
    for warning in get_nodes_in_group("site7_attack_warnings"): warning.free()
    return {"rows": rows, "shots": shots}

func _lanes(rows: Array) -> Array:
    return rows.filter(func(row: Dictionary) -> bool: return row.kind == "lane")

func _circles(rows: Array) -> Array:
    return rows.filter(func(row: Dictionary) -> bool: return row.kind == "circle")

func _lane_covers(row: Dictionary, point: Vector2) -> bool:
    var offset: Vector2 = point - (row.at as Vector2)
    var ray: Vector2 = row.ray
    var forward := offset.dot(ray)
    return forward >= 0.0 and forward <= float(row.reach) and absf(offset.dot(ray.orthogonal())) <= float(row.half)

## Angle of a lane against the boss-to-target line, folded into 0-180 degrees.
func _lane_angle(row: Dictionary, ground: Vector2) -> float:
    return fposmod(rad_to_deg((row.ray as Vector2).angle() - ground.angle()), 180.0)

func _has_angle(angles: Array, wanted: float) -> bool:
    return angles.any(func(angle: float) -> bool: return absf(angle - wanted) < 0.2 or absf(angle - wanted - 180.0) < 0.2)

func _verify_new_geometry(victim: OperatorActor) -> void:
    var home := victim.global_position
    var boss_at := Vector2(100.0, 100.0)
    var ground := (home - boss_at).normalized()
    var across := ground.orthogonal()
    # AERATOR: spore circles on a ring round the target; the middle blooms too from phase two.
    var boss := _spawn_boss("BOSS_SITE7_AERATOR_01", boss_at)
    var turned_first: Array[float] = []
    for phase in range(1, 4):
        for serial in range(1, 3):
            var context := "AERATOR phase=%d serial=%d" % [phase, serial]
            var result := _attack_rows(boss, victim, phase, serial)
            var rows: Array = result.rows
            if phase == 2 and serial == 2:
                check(rows.is_empty() and (result.shots as Array).size() == 3, "spore volley of three in " + context)
                var spread: Array = (result.shots as Array).map(func(shot: Vector2) -> float: return snappedf(shot.angle_to(ground), 0.01))
                spread.sort()
                check(spread == [-0.3, 0.0, 0.3], "spore volley fans 0.3 rad either side of the aim in " + context)
                continue
            var ring := rows.filter(func(row: Dictionary) -> bool: return float(row.radius) == 64.0)
            var centre := rows.filter(func(row: Dictionary) -> bool: return float(row.radius) == 70.0)
            check(ring.size() == [4, 5, 6][phase - 1], "ring size in " + context)
            for i in range(ring.size()):
                var row: Dictionary = ring[i]
                check(absf((row.at as Vector2).distance_to(home) - (190.0 + 10.0 * float(phase - 1))) < 0.01, "ring circle %d sits on the ring in %s" % [i, context])
                check(is_equal_approx(float(row.windup), 1.2 + 0.1 * float(i)), "ring circle %d opens in turn in %s" % [i, context])
            check(centre.size() == (0 if phase == 1 else 1), "middle circle count in " + context)
            if centre.size() == 1:
                check((centre[0].at as Vector2).distance_to(home) < 0.01 and is_equal_approx(float(centre[0].windup), 1.7), "middle circle is on the target and opens last in " + context)
            if phase != 2:
                turned_first.append(((ring[0].at as Vector2) - home).angle())
    # Phase 1 ring turned 45 degrees for attack B, phase 3 by 30 degrees.
    check(is_equal_approx(wrapf(turned_first[1] - turned_first[0], -PI, PI), PI * 0.25), "AERATOR turns the phase 1 ring 45 degrees")
    check(is_equal_approx(wrapf(turned_first[3] - turned_first[2], -PI, PI), PI / 6.0), "AERATOR turns the phase 3 ring 30 degrees")
    boss.free()
    # CRYO: frost bars across the compressor-to-target line, 150 px apart, lighting in a wave.
    boss = _spawn_boss("BOSS_SITE7_CRYO_01", boss_at)
    for phase in range(1, 4):
        for serial in range(1, 3):
            var context := "CRYO phase=%d serial=%d" % [phase, serial]
            var result := _attack_rows(boss, victim, phase, serial)
            var bars := _lanes(result.rows).filter(func(row: Dictionary) -> bool: return float(row.half) == 30.0)
            var axis_lanes := _lanes(result.rows).filter(func(row: Dictionary) -> bool: return float(row.half) == 22.0)
            if phase == 1 and serial == 2:
                check(bars.is_empty() and (result.shots as Array).size() == 2, "two ice shards in " + context)
                continue
            var expected_bars := 2 if phase == 1 else (4 if serial == 2 or phase == 3 else 3)
            check(bars.size() == expected_bars, "bar count in " + context)
            check(axis_lanes.size() == (1 if phase == 3 else 0), "axis lane count in " + context)
            var inward := phase == 3 and serial == 2
            for i in range(bars.size()):
                var row: Dictionary = bars[i]
                check(absf((row.ray as Vector2).dot(ground)) < 0.001 and float(row.reach) == 700.0, "bar %d crosses the line in %s" % [i, context])
                var middle: Vector2 = (row.at as Vector2) + (row.ray as Vector2) * 350.0
                check(middle.distance_to(boss_at + ground * (130.0 + 150.0 * float(i))) < 0.01, "bar %d sits %d px out in %s" % [i, 130 + 150 * i, context])
                var wave := bars.size() - 1 - i if inward else i
                check(is_equal_approx(float(row.windup), 1.1 + 0.2 * float(wave)), "bar %d lights in the %s wave in %s" % [i, "inward" if inward else "outward", context])
            for row in axis_lanes:
                check((row.at as Vector2).distance_to(boss_at) < 0.01 and (row.ray as Vector2).distance_to(ground) < 0.001 and float(row.reach) == CRYO_AXIS_REACH and is_equal_approx(float(row.windup), 1.4), "axis lane runs from the compressor toward the target and stops at the second bar in " + context)
                check(float(row.reach) <= CRYO_AXIS_REACH_LIMIT, "axis lane stays short enough to leave room beside it on a narrow floor in " + context)
    boss.free()
    # GANTRY: rails cross where the target stands; circles either side of it; a star at the end.
    boss = _spawn_boss("BOSS_SITE7_GANTRY_01", boss_at)
    check(GANTRY_LATE_WINDUP_MIN >= ESCAPE_MARGIN + float(NEW_BOSS_GAP_LIMIT) / SLOWEST_WALK,
        "GANTRY's late wind-up floor covers a 180 px walk out plus the escape margin")
    for phase in range(1, 4):
        for serial in range(1, 3):
            var context := "GANTRY phase=%d serial=%d" % [phase, serial]
            var result := _attack_rows(boss, victim, phase, serial)
            var lanes := _lanes(result.rows)
            var circles := _circles(result.rows)
            check((result.shots as Array).is_empty(), "rails fire no shots in " + context)
            for lane in lanes:
                check(_lane_covers(lane, home), "rail crosses the target's spot in %s" % context)
                check(float(lane.reach) == 1100.0 and float(lane.windup) >= 1.4, "rail is 1100 px long and winds up 1.4 s in " + context)
            # The rails that can leave only a distant gap (the diagonal set and the star, and the star's circle) wind up longer.
            var late := phase == 3 or (phase == 2 and serial == 1)
            if late:
                for warning in lanes + circles:
                    check(is_equal_approx(float(warning.windup), GANTRY_LATE_WINDUP) and float(warning.windup) >= GANTRY_LATE_WINDUP_MIN,
                        "%s winds up %.1f s, never under %.2f s in %s" % [warning.kind, GANTRY_LATE_WINDUP, GANTRY_LATE_WINDUP_MIN, context])
            var angles: Array = lanes.map(func(row: Dictionary) -> float: return _lane_angle(row, ground))
            if phase == 1 and serial == 1:
                check(_has_angle(angles, 0.0) and _has_angle(angles, 90.0), "phase 1 rails cross at right angles")
            if phase == 2 and serial == 1:
                check(_has_angle(angles, 0.0) and _has_angle(angles, 90.0) and _has_angle(angles, 45.0), "phase 2 rails add a diagonal")
            if phase == 3:
                var offset := 22.5 if serial == 2 else 0.0
                check([0.0, 45.0, 90.0, 135.0].all(func(step: float) -> bool: return _has_angle(angles, step + offset)), "phase 3 rails form a star %s" % ("turned 22.5 degrees" if serial == 2 else "on the line"))
            if phase == 1 and serial == 2:
                check(circles.size() == 1 and (circles[0].at as Vector2).distance_to(home) < 0.01 and float(circles[0].radius) == 100.0, "phase 1 impact circle is on the target")
            if phase == 2 and serial == 2:
                var sides: Array = circles.map(func(row: Dictionary) -> float: return snappedf(((row.at as Vector2) - home).dot(across), 0.1))
                sides.sort()
                check(circles.size() == 2 and sides == [-160.0, 160.0], "phase 2 circles land 160 px either side of the target")
    boss.free()
    # ARCHIVE: the target's own ground and the ground it stood on at its last attacks.
    boss = _spawn_boss("BOSS_SITE7_ARCHIVE_01", boss_at)
    var stood: Array[Vector2] = []
    var steps := [[1, 1], [1, 2], [2, 1], [2, 2], [3, 1], [3, 2]]
    for index in range(steps.size()):
        var phase: int = steps[index][0]
        var serial: int = steps[index][1]
        var context := "ARCHIVE attack %d (phase %d, serial %d)" % [index + 1, phase, serial]
        victim.global_position = home + Vector2(37.0 * float(index), -53.0 * float(index))
        var result := _attack_rows(boss, victim, phase, serial)
        var circles := _circles(result.rows)
        var recalled := mini(mini(stood.size(), 3), phase)
        check(circles.size() == 1 + recalled, "%s lays %d circles" % [context, 1 + recalled])
        var positions: Array = circles.map(func(row: Dictionary) -> Vector2: return row.at)
        check(positions.has(victim.global_position), "%s blooms under the target" % context)
        for k in range(recalled):
            var remembered: Vector2 = stood[stood.size() - 1 - k]
            check(positions.has(remembered), "%s remembers where the target stood %d attack(s) ago" % [context, k + 1])
            # The echoes go off first, the newest at ECHO_WINDUP and each older one 0.1 s later, and never under ECHO_WINDUP_MIN.
            var echo := circles.filter(func(row: Dictionary) -> bool: return (row.at as Vector2).distance_to(remembered) < 0.01)
            check(echo.size() == 1 and is_equal_approx(float(echo[0].windup), ECHO_WINDUP + 0.1 * float(k)) and float(echo[0].windup) >= ECHO_WINDUP_MIN,
                "%s echo %d winds up %.1f s, never under %.2f s" % [context, k + 1, ECHO_WINDUP + 0.1 * float(k), ECHO_WINDUP_MIN])
        var own := circles.filter(func(row: Dictionary) -> bool: return (row.at as Vector2).distance_to(victim.global_position) < 0.01)
        check(own.size() == 1 and is_equal_approx(float(own[0].windup), ECHO_WINDUP + 0.3), "%s: the target's own ground winds up %.1f s, after the echoes" % [context, ECHO_WINDUP + 0.3])
        check(circles.all(func(row: Dictionary) -> bool: return float(row.radius) == 70.0), "%s circles are 70 px" % context)
        if index == 4:
            check(not positions.has(home), "%s has forgotten the oldest position" % context)
        var lanes := _lanes(result.rows)
        check(lanes.size() == (1 if phase == 3 and serial == 2 else 0), "%s lane count" % context)
        for row in lanes:
            check((row.at as Vector2).distance_to(boss_at) < 0.01 and float(row.reach) == 900.0 and float(row.half) == 22.0, "%s lane runs from the spire to the target" % context)
            check(is_equal_approx(float(row.windup), ECHO_WINDUP + 0.4), "%s lane winds up %.1f s, after the target's own ground" % [context, ECHO_WINDUP + 0.4])
        stood.append(victim.global_position)
    victim.global_position = home
    boss.free()
    # ORIGIN: lanes come in from every side and meet on the target; the core's own ground closes.
    boss = _spawn_boss("BOSS_SITE7_ORIGIN_01", boss_at)
    check(ORIGIN_LATE_WINDUP_MIN >= ESCAPE_MARGIN + float(NEW_BOSS_GAP_LIMIT) / SLOWEST_WALK,
        "ORIGIN's late wind-up floor covers a 180 px walk out plus the escape margin")
    var expected_lanes := {"1:1": 3, "1:2": 0, "2:1": 4, "2:2": 0, "3:1": 5, "3:2": 3}
    for phase in range(1, 4):
        for serial in range(1, 3):
            var context := "ORIGIN phase=%d serial=%d" % [phase, serial]
            var late := phase == 3
            var result := _attack_rows(boss, victim, phase, serial)
            var lanes := _lanes(result.rows)
            var circles := _circles(result.rows)
            check(lanes.size() == int(expected_lanes["%d:%d" % [phase, serial]]), "converging lane count in " + context)
            var starts: Array = []
            for lane in lanes:
                check(_lane_covers(lane, home), "lane covers the target's spot in " + context)
                check((lane.at as Vector2).distance_to(home) > 419.0 and (lane.at as Vector2).distance_to(home) < 421.0, "lane starts 420 px out in " + context)
                check(((home - (lane.at as Vector2)).normalized()).dot(lane.ray) > 0.999, "lane runs toward the target in " + context)
                check(float(lane.half) == (22.0 if late else 20.0) and is_equal_approx(float(lane.windup), ORIGIN_LATE_WINDUP if late else 1.3)
                    and (not late or float(lane.windup) >= ORIGIN_LATE_WINDUP_MIN), "lane width and wind-up (never under %.2f s in the last phase) in %s" % [ORIGIN_LATE_WINDUP_MIN, context])
                starts.append(((lane.at as Vector2) - home).angle())
            if lanes.size() >= 3:
                starts.sort()
                var widest := 0.0
                for k in range(starts.size()):
                    widest = maxf(widest, fposmod(float(starts[(k + 1) % starts.size()]) - float(starts[k]), TAU))
                check(widest <= TAU / float(lanes.size()) + 0.001, "lanes are spread evenly round the target in " + context)
            var core := circles.filter(func(row: Dictionary) -> bool: return float(row.radius) == 150.0)
            var target_circle := circles.filter(func(row: Dictionary) -> bool: return float(row.radius) == 90.0)
            check(core.size() == (1 if serial == 2 and phase >= 2 else 0), "core circle count in " + context)
            for row in core:
                check((row.at as Vector2).distance_to(boss_at) < 0.01 and is_equal_approx(float(row.windup), ORIGIN_LATE_WINDUP if late else 1.2)
                    and (not late or float(row.windup) >= ORIGIN_LATE_WINDUP_MIN), "core circle closes on the core (never under %.2f s in the last phase) in %s" % [ORIGIN_LATE_WINDUP_MIN, context])
            check(target_circle.size() == (1 if (phase == 1 and serial == 2) or (phase == 2 and serial == 2) or phase == 3 else 0), "target circle count in " + context)
            for row in target_circle:
                check((row.at as Vector2).distance_to(home) < 0.01 and is_equal_approx(float(row.windup), ORIGIN_LATE_WINDUP if late else 1.2)
                    and (not late or float(row.windup) >= ORIGIN_LATE_WINDUP_MIN), "target circle is on the target (never under %.2f s in the last phase) in %s" % [ORIGIN_LATE_WINDUP_MIN, context])
            var expected_shots := 2 if serial == 2 and phase <= 2 else 0
            check((result.shots as Array).size() == expected_shots, "bolt count in " + context)
    boss.free()

## Where does the target have to walk to be safe, wherever it stands? Every new boss attack is
## laid on the target at 5 distances x 6 bearings on open floor; the nearest patch of floor
## no warning covers must be within NEW_BOSS_GAP_LIMIT, and reachable at the slowest walk
## before the warning that covers the target's own spot goes off.
func _verify_gap_sweep(victim: OperatorActor) -> void:
    var home := victim.global_position
    var boss_at := Vector2(100.0, 100.0)
    var open := Rect2(Vector2(-1500.0, -1500.0), Vector2(3000.0, 3000.0))
    var width := victim.get_combat_hit_rect().size.x * 1.5
    for enemy_id in NEW_BOSSES:
        var boss := _spawn_boss(enemy_id, boss_at)
        var worst := {"radius": 0, "where": ""}
        var slowest := {"seconds": 0.0, "where": ""}
        for phase in range(1, 4):
            for serial in range(1, 3):
                for distance in SWEEP_DISTANCES:
                    for bearing in SWEEP_BEARINGS:
                        victim.global_position = boss_at + Vector2.from_angle(deg_to_rad(float(bearing))) * float(distance)
                        var rows: Array = _attack_rows(boss, victim, phase, serial).rows
                        var where := "phase %d attack %d, target %d px out at %d deg" % [phase, serial, int(distance), int(bearing)]
                        var radius := _nearest_clear_rows(rows, victim.global_position, width, open)
                        if radius < 0 or radius > int(worst.radius):
                            worst = {"radius": radius, "where": where}
                        # The earliest warning on the target's own spot sets the time to leave it.
                        var covering: Array = rows.filter(func(row: Dictionary) -> bool: return _row_covers(row, victim.global_position))
                        if not covering.is_empty():
                            var earliest := 99.0
                            for row in covering: earliest = minf(earliest, float(row.windup))
                            var need := float(maxi(radius, 0)) / SLOWEST_WALK
                            var margin := earliest - need
                            if slowest.where.is_empty() or margin < float(slowest.seconds):
                                slowest = {"seconds": margin, "where": where + " (leave %d px in %.2f s of %.2f s)" % [radius, need, earliest]}
        check(int(worst.radius) > 0 and int(worst.radius) <= NEW_BOSS_GAP_LIMIT, "%s: safe floor within %d px wherever the target stands (worst %d px: %s)" % [enemy_id, NEW_BOSS_GAP_LIMIT, int(worst.radius), worst.where])
        check(slowest.where.is_empty() or float(slowest.seconds) >= ESCAPE_MARGIN, "%s: the slowest walk leaves the warned spot with %.2f s to spare (tightest margin %.2f s: %s)" % [enemy_id, ESCAPE_MARGIN, float(slowest.seconds), slowest.where])
        sweep_worst[enemy_id] = {"nearest_clear_floor_px": int(worst.radius), "where": worst.where, "tightest_escape_margin_s": snappedf(float(slowest.seconds), 0.01), "tightest_escape": slowest.where}
        boss.free()
    victim.global_position = home

func _row_covers(row: Dictionary, point: Vector2) -> bool:
    if row.kind == "circle":
        return (row.at as Vector2).distance_to(point) <= float(row.radius)
    return _lane_covers(row, point)

## Nearest ring (30 px steps up to 300) with a clear 1.5-actor-wide patch inside `bounds`, or -1.
func _nearest_clear_rows(rows: Array, from: Vector2, width: float, bounds: Rect2) -> int:
    for radius in range(30, 301, 30):
        for i in range(64):
            var direction := Vector2.from_angle(float(i) * TAU / 64.0)
            var center := from + direction * float(radius)
            var tangent := direction.orthogonal() * width * 0.5
            var patch: Array[Vector2] = [center - tangent, center, center + tangent]
            if not patch.all(func(point: Vector2) -> bool: return bounds.has_point(point)):
                continue
            if patch.all(func(point: Vector2) -> bool: return rows.all(func(row: Dictionary) -> bool: return not _row_covers(row, point))):
                return radius
    return -1
