extends SceneTree
## A live duel for all ten bosses. Each boss runs the shipped controller and its own attack
## warnings against three operators who stand still and cannot fall, at 1/60 s per physics
## tick. Six attacks (two per damage phase) show that every attack lays the shape frozen in
## site7_boss_pattern_smoke.gd, that its wind-up lasts 1.1 s (ANCHOR 0.95 s), that the cycle
## keeps its timing, and that damage lands only when a warning goes off, at least 1.0 s after
## it appeared, on exactly the operators standing inside it. A second run per boss goes through
## real damage: the phase changes, the 8 s core shield, the kill and the clean-up. Negative
## controls run GANTRY's duel with a fault built in (wrong pattern, a warning that goes off
## early, a warning that hits too hard); each must be rejected by the checks above.
## Operations 6-10 have no plates, so there is no full_op_06-10 playthrough yet; this is their
## live boss check. Technical only: no art, balance or play approval.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const Pattern := preload("res://tests/smoke/site7_boss_pattern_smoke.gd")
const TestOutput := preload("res://tests/support/test_output.gd")
## Attack A / attack B of ANCHOR in phases 1-3; the pattern smoke computes them inline.
const ANCHOR_SHAPES := ["S3C0L0/S3C0L0", "S5C0L0/S0C1L0", "S5C0L0/S0C1L4"]
const TICK := 1.0 / 60.0
## Simulated seconds per real second. The tick rate rises with it, so every physics tick
## still advances exactly 1/60 s (Godot hands _physics_process step * time_scale).
const SPEEDUP := 10
const BOSS_HEALTH := 1000.0
const OPERATOR_HEALTH := 100000.0
## Share of maximum health while the two attacks of phase 1, 2 and 3 run.
const PHASE_HEALTH := [1.0, 0.5, 0.2]
const RUN_TICK_LIMIT := 3000
const BOSS_AT := Vector2(100.0, 100.0)
## The pattern smoke's layout: the boss faces ASTER, ROOK and MICA stand 150 px away from her.
const ROSTER := [["CHR_PROTO_01", "ASTER", Vector2(300.0, 100.0)], ["CHR_PROTO_02", "ROOK", Vector2(300.0, 250.0)],
    ["CHR_PROTO_03", "MICA", Vector2(300.0, -50.0)]]
## Seconds a cycle may stray from wind-up + recover + reposition (ticks are 1/60 s).
const CYCLE_TOLERANCE := 0.07
var failures: Array[String] = []
var checks := 0
var operators: Array[OperatorActor] = []
var attacks: Array[Dictionary] = []
var emissions: Array[Dictionary] = []
var hits: Array[Dictionary] = []
var seen_warnings := {}
var emission_cursor := 0
var last_state := ""
var windup_from := 0
var run_from := 0
var defeated_count := 0
var report := {}
var redline_mode := false
## Negative control: which fault the duel carries, and the failures its checks report meanwhile.
var fault := ""
var capturing := false
var captured: Array[String] = []

func _init() -> void:
    call_deferred("run")

func check(ok: bool, label: String) -> void:
    if capturing:
        if not ok: captured.append(label)
        return
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func run() -> void:
    Engine.physics_ticks_per_second = 60 * SPEEDUP
    Engine.time_scale = float(SPEEDUP)
    Engine.max_physics_steps_per_frame = 32
    check(absf(Engine.time_scale / float(Engine.physics_ticks_per_second) - TICK) < 0.000001, "every physics tick advances 1/60 s")
    for entry in ROSTER:
        var operator := OPERATOR.instantiate() as OperatorActor
        operator.configure(str(entry[0]), str(entry[1]), Color.WHITE)
        root.add_child(operator)
        operator.set_physics_process(false)
        operator.global_position = entry[2]
        operator.max_health = OPERATOR_HEALTH
        operator.health = OPERATOR_HEALTH
        operator.damage_taken.connect(_on_damage)
        operators.append(operator)
    var ids: Array[String] = ["BOSS_SITE7_ANCHOR_01"]
    for id in Pattern.OTHER_BOSSES: ids.append(str(id))
    for id in ids:
        await _duel(id)
        await _damage_flow(id)
    redline_mode = true
    for id in ids: await _duel(id)
    redline_mode = false
    var controls := {}
    for control in [["shape", "live shape"], ["early", "first hit"], ["damage", "takes exactly the damage"]]:
        await _duel("BOSS_SITE7_GANTRY_01", str(control[0]))
        controls[str(control[0])] = captured.size()
        check(captured.any(func(label: String) -> bool: return label.contains(str(control[1]))), "negative control '%s' is rejected (%d failures reported)" % [control[0], captured.size()])
    for operator in operators: operator.free()
    var out := TestOutput.path("res://.cache/site7_boss_duel.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": "PASS" if failures.is_empty() else "FAIL", "checks": checks, "failures": failures,
        "bosses": ids.size(), "redline_bosses": ids.size(), "physics_ticks_per_second": Engine.physics_ticks_per_second, "simulated_seconds_per_second": SPEEDUP,
        "negative_controls_failures_reported": controls, "duels": report, "visual_approval": false, "balance_approval": false,
        "note": "Live controller and warning loop against stationary operators in a bare scene; no plates, no play session."}, "  "))
    file.close()
    print("SITE7_BOSS_DUEL_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks) ", out)
    quit(0 if failures.is_empty() else 1)

# --- the duel: six attacks through the real loop ------------------------------------------

func _duel(id: String, injected := "") -> void:
    var boss := _spawn(id)
    if boss == null: return
    var arena := boss.get_parent()
    var home := boss.global_position
    var original_pattern := str(boss.art_profile.get("boss_pattern", ""))
    capturing = injected != ""
    captured.clear()
    fault = injected
    if injected == "shape": boss.art_profile["boss_pattern"] = "bloom_field"
    for phase in range(1, 4):
        boss.health = boss.max_health * float(PHASE_HEALTH[phase - 1])
        while attacks.size() < phase * 2 and Engine.get_physics_frames() - run_from < RUN_TICK_LIMIT:
            await _advance(boss)
    # The last warning goes off at most 1.7 s after its attack; 2.3 s cover it and stop before the next attack.
    for i in range(138): await _advance(boss)
    check(attacks.size() == 6, "%s completes six attacks in its duel (got %d)" % [id, attacks.size()])
    check(boss.global_position.distance_to(home) < 0.5, id + " stays on its post")
    check(is_equal_approx(boss.health, boss.max_health * float(PHASE_HEALTH[2])), id + " is not hurt by its own attacks")
    _verify_duel(id)
    if injected == "shape": boss.art_profile["boss_pattern"] = original_pattern
    arena.free()
    for i in range(3): await physics_frame
    check(get_nodes_in_group("site7_attack_warnings").is_empty(), id + " leaves no warning behind")
    check(emissions.all(func(row: Dictionary) -> bool: return not is_instance_valid(instance_from_id(int(row.projectile_id)))), id + " leaves no projectile behind")
    capturing = false
    fault = ""

func _verify_duel(id: String) -> void:
    var shapes: Array = ANCHOR_SHAPES if id == "BOSS_SITE7_ANCHOR_01" else Pattern.SIGNATURES[id]
    var wind_expected := 0.95 if id == "BOSS_SITE7_ANCHOR_01" else 1.1
    var rows: Array[Dictionary] = []
    var victim_total := 0.0
    for index in range(attacks.size()):
        var attack: Dictionary = attacks[index]
        var phase := 1 + int(floor(float(index) / 2.0))
        var context := "%s attack %d (phase %d)" % [id, index + 1, phase]
        var warnings: Array = attack.warnings
        var shots: Array = attack.shots
        var circles := 0
        var lanes := 0
        var windups: Array[float] = []
        for w in warnings:
            if str(w.kind) == "circle": circles += 1
            elif str(w.kind) == "lane": lanes += 1
            windups.append(float(w.windup))
            check(float(w.windup) >= 1.0 and float(w.damage) <= 20.0, "warning wind-up and damage: " + context)
        var shape := "S%dC%dL%d" % [shots.size(), circles, lanes]
        var frozen := str(str(shapes[phase - 1]).split("/")[0 if int(attack.serial) % 2 == 1 else 1])
        check(int(attack.serial) == index + 1 and int(attack.phase) == phase, "serial and phase in the live loop: " + context)
        check(shape == frozen, "live shape %s, frozen %s: %s" % [shape, frozen, context])
        check(absf(float(attack.windup_ticks) * TICK - wind_expected) <= 0.05, "wind-up lasts %.2f s (got %.3f): %s" % [wind_expected, float(attack.windup_ticks) * TICK, context])
        var since := 0.0
        var expected_since := 0.0
        if index == 0:
            since = float(int(attack.tick) - run_from) * TICK
            expected_since = 0.7 + wind_expected
        else:
            since = float(int(attack.tick) - int(attacks[index - 1].tick)) * TICK
            expected_since = (1.8 - float(attacks[index - 1].phase) * 0.2) + 0.45 + wind_expected
        check(absf(since - expected_since) <= (0.1 if index == 0 else CYCLE_TOLERANCE), "attack comes %.2f s after the last (expected %.2f): %s" % [since, expected_since, context])
        var end_tick := int(attacks[index + 1].tick) if index + 1 < attacks.size() else int(attack.tick) + 150
        var earliest := 99.0
        for value in windups: earliest = minf(earliest, value)
        var shot_total := 0.0
        for value in shots: shot_total += float(value)
        var damage := {}
        for operator in operators:
            var covering := 0.0
            var first_cover := 99.0
            for w in warnings:
                if _covers(w, operator.global_position):
                    # Warnings store authored damage; the shipped warning loop
                    # applies the source's run factor when it damages an operator.
                    covering += float(w.damage) * (RunContract.REDLINE_DAMAGE if redline_mode else 1.0)
                    first_cover = minf(first_cover, float(w.windup))
            var early := 0.0
            var late := 0.0
            var first_late := -1
            for hit in hits:
                if str(hit.op) != operator.operator_id or int(hit.tick) < int(attack.tick) or int(hit.tick) >= end_tick: continue
                var after := int(hit.tick) - int(attack.tick)
                if float(after) * TICK < earliest - 3.0 * TICK:
                    early += float(hit.amount)
                else:
                    late += float(hit.amount)
                    if first_late < 0: first_late = after
            check(early <= shot_total + 0.01, "%s loses only shot damage before a warning goes off (%.1f of %.1f): %s" % [operator.display_name, early, shot_total, context])
            check(absf(late - covering) < 0.01, "%s takes exactly the damage of the warnings over it (%.1f, expected %.1f): %s" % [operator.display_name, late, covering, context])
            if covering > 0.0:
                check(absf(float(first_late) * TICK - first_cover) <= 0.06, "%s is first hit when its warning goes off (%.2f s, expected %.2f): %s" % [operator.display_name, float(first_late) * TICK, first_cover, context])
                check(float(first_late) * TICK >= 0.95, "%s has at least 0.95 s between the warning and the hit: %s" % [operator.display_name, context])
            damage[operator.display_name] = {"shots": snappedf(early, 0.01), "warnings": snappedf(late, 0.01)}
            if operator.operator_id == "CHR_PROTO_01": victim_total += late
        rows.append({"serial": int(attack.serial), "phase": int(attack.phase), "shape": shape, "tick": int(attack.tick) - run_from,
            "windup_s": snappedf(float(attack.windup_ticks) * TICK, 0.001), "since_last_s": snappedf(since, 0.001),
            "warning_windups_s": windups, "damage": damage})
    check(victim_total > 0.0, id + " hurts a target that never moves")
    if not capturing:
        if redline_mode:
            var standard: Array = report[id].attacks
            check(rows.size() == standard.size(), id + " REDLINE preserves attack count")
            for i in range(mini(rows.size(), standard.size())):
                check(rows[i].shape == standard[i].shape and rows[i].warning_windups_s == standard[i].warning_windups_s and absf(float(rows[i].windup_s)-float(standard[i].windup_s)) <= TICK, id + " REDLINE warning shapes and wind-up equal standard")
        report[("REDLINE/" if redline_mode else "") + id] = {"attacks": rows, "warning_damage_to_the_target": snappedf(victim_total, 0.01)}

# --- the damage flow: phases, core shield, kill --------------------------------------------

func _damage_flow(id: String) -> void:
    var boss := _spawn(id)
    if boss == null: return
    var arena := boss.get_parent()
    var guard := boss.get_node_or_null("BossPhaseTransitionGuard") as BossPhaseTransitionGuard
    check(guard != null, id + " carries its phase guard")
    if guard == null:
        arena.free()
        return
    for i in range(6): await _advance(boss)
    check(int(boss.tactics.phase) == 1 and not guard.debug_guard_active(), id + " opens in phase 1 without a shield")
    boss.apply_damage(BOSS_HEALTH * 0.4)
    for i in range(2): await _advance(boss)
    check(is_equal_approx(boss.health, BOSS_HEALTH * 0.6) and int(boss.tactics.phase) == 2 and not guard.debug_guard_active(), id + " is in phase 2 at 60 % health")
    boss.apply_damage(BOSS_HEALTH * 0.3)
    for i in range(2): await _advance(boss)
    check(int(boss.tactics.phase) == 3 and guard.debug_guard_active(), id + " raises its core shield in phase 3")
    check(not boss.is_in_group("prototype_targets") and boss.is_in_group("site7_guarded_targets"), id + " leaves auto-targeting while shielded")
    var kept := boss.health
    boss.apply_damage(50.0)
    check(is_equal_approx(boss.health, kept), id + " takes no damage while shielded")
    var attacks_at_shield := attacks.size()
    for i in range(int(round(guard.debug_guard_seconds() / TICK)) - 40): await _advance(boss)
    check(guard.debug_guard_active(), id + " is still shielded just before the shield ends")
    for i in range(60): await _advance(boss)
    check(not guard.debug_guard_active() and boss.is_in_group("prototype_targets"), id + " loses its shield after 8 s")
    check(attacks.size() - attacks_at_shield >= 2, id + " keeps attacking under its shield (%d attacks)" % (attacks.size() - attacks_at_shield))
    boss.apply_damage(50.0)
    check(is_equal_approx(boss.health, kept - 50.0), id + " takes damage again once the shield ends")
    boss.apply_damage(boss.health)
    check(boss.health <= 0.0 and defeated_count == 1, id + " is defeated exactly once (%d)" % defeated_count)
    check(not boss.tactics.visible, id + " hides its warning layer when defeated")
    for i in range(3): await physics_frame
    check(not get_nodes_in_group("site7_attack_warnings").any(func(warning: Node) -> bool: return warning.source == boss), id + " leaves no warning of its own after the kill")
    for i in range(45): await physics_frame
    check(not is_instance_valid(boss), id + " is removed after its death fade")
    check(emissions.all(func(row: Dictionary) -> bool: return not is_instance_valid(instance_from_id(int(row.projectile_id)))), id + " leaves no projectile after the kill")
    arena.free()
    if report.has(id): (report[id] as Dictionary)["shield"] = {"attacks_under_shield": attacks.size() - attacks_at_shield}

# --- helpers ------------------------------------------------------------------------------------

func _spawn(id: String) -> EnemyActor:
    var arena := Node2D.new()
    root.add_child(arena)
    var boss := ENEMY.instantiate() as EnemyActor
    if not boss.configure(id, BOSS_HEALTH):
        check(false, id + " is refused by the runtime gate")
        boss.free()
        arena.free()
        return null
    # The boss pins itself to where it stood when it entered the tree.
    if redline_mode:
        boss.apply_run_modifiers(RunContract.enemy_modifiers(RunContract.redline("REDLINE-DUEL"), id))
        check(is_equal_approx(boss.max_health, BOSS_HEALTH * RunContract.REDLINE_HEALTH) and is_equal_approx(boss.run_damage_multiplier, RunContract.REDLINE_DAMAGE), id + " REDLINE HP/damage apply once")
        check(is_equal_approx(boss.run_speed_multiplier, 1.0) and is_equal_approx(boss.run_attack_interval_multiplier, 1.0), id + " REDLINE preserves boss speed/interval")
    boss.position = BOSS_AT
    arena.add_child(boss)
    boss.projectile_emitted.connect(_on_emitted)
    boss.tactics.attack_started.connect(_on_attack)
    boss.defeated.connect(_on_defeated)
    attacks.clear()
    emissions.clear()
    hits.clear()
    seen_warnings.clear()
    emission_cursor = 0
    last_state = ""
    windup_from = 0
    defeated_count = 0
    run_from = Engine.get_physics_frames()
    return boss

## One physics tick, then what the tick left behind: the wind-up start, the new shots and warnings.
func _advance(boss: EnemyActor) -> void:
    await physics_frame
    if not is_instance_valid(boss) or boss.tactics == null: return
    var state := str(boss.tactics.state)
    if state == "WINDUP" and last_state != "WINDUP": windup_from = Engine.get_physics_frames()
    last_state = state
    _collect(boss)

func _collect(boss: EnemyActor) -> void:
    while emission_cursor < emissions.size():
        var row: Dictionary = emissions[emission_cursor]
        emission_cursor += 1
        var shot := instance_from_id(int(row.projectile_id)) as PrototypeProjectile
        for attack in attacks:
            if int(attack.serial) == int(row.attack_serial):
                (attack.shots as Array).append(shot.damage if is_instance_valid(shot) else 24.0)
    for node in get_nodes_in_group("site7_attack_warnings"):
        if node.source != boss or seen_warnings.has(node.get_instance_id()): continue
        seen_warnings[node.get_instance_id()] = true
        if attacks.is_empty(): continue
        (attacks[attacks.size() - 1].warnings as Array).append({"kind": node.kind, "at": node.global_position, "ray": node.ray,
            "radius": node.radius, "reach": node.reach, "half": node.half_width, "windup": node.windup, "damage": node.damage})
        # Faults for the negative controls, applied after the warning was read: it goes off 0.5 s early, or hits harder.
        if fault == "early": node.elapsed = 0.5
        elif fault == "damage": node.damage = 35.0

## Whether a warning marks the point, computed here rather than by the warning's own contains().
func _covers(w: Dictionary, point: Vector2) -> bool:
    var offset: Vector2 = point - (w.at as Vector2)
    if str(w.kind) == "circle": return offset.length() <= float(w.radius)
    var ray: Vector2 = w.ray
    var forward := offset.dot(ray)
    return forward >= 0.0 and forward <= float(w.reach) and absf(offset.dot(ray.orthogonal())) <= float(w.half)

func _on_attack(event: Dictionary) -> void:
    var now := Engine.get_physics_frames()
    attacks.append({"serial": int(event.attack_serial), "phase": int(event.phase), "tick": now,
        "windup_ticks": now - windup_from + 1, "warnings": [], "shots": []})

func _on_emitted(row: Dictionary) -> void:
    emissions.append(row)

func _on_damage(operator: OperatorActor, amount: float, source_id: String) -> void:
    hits.append({"op": operator.operator_id, "tick": Engine.get_physics_frames(), "amount": amount, "source": source_id})

func _on_defeated(_enemy: EnemyActor) -> void:
    defeated_count += 1
