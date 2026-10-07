extends SceneTree
## Elite affixes (data/progression/elite_affixes.json): mission rows attach them to the
## named robots, SHIELDED soaks damage and recharges, OVERCHARGED stacks on the run
## modifiers, VOLATILE bursts only after its warning and only hits operators inside the
## circle, and the combat tips name each variant in the room.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const BLAST := preload("res://scripts/combat/elite_volatile_blast.gd")
const EXPECTED_ROWS := {"MIS_CH01_01": 1, "MIS_CH01_02": 1, "MIS_CH01_03": 2, "MIS_CH01_04": 3, "MIS_CH01_05": 3, "MIS_CH01_06": 4, "MIS_CH01_07": 4, "MIS_CH01_08": 4, "MIS_CH01_09": 4, "MIS_CH01_10": 5}

var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var table := EliteAffix.table()
    _check(table.size() == 5 and table.has("SHIELDED") and table.has("OVERCHARGED") and table.has("VOLATILE") and table.has("BROODING") and table.has("BEACON"), "five affixes are defined")
    for id: String in table:
        _check(EliteAffix.tip(id).begins_with(id + ":") and str(table[id].get("color", "")).length() == 6, id + " has a tip and a colour")
    for mission: String in EXPECTED_ROWS:
        var rows := _affix_rows(mission)
        _check(rows.size() == EXPECTED_ROWS[mission], "%s carries %d elite rows (found %d)" % [mission, EXPECTED_ROWS[mission], rows.size()])
        for row: Dictionary in rows:
            _check(table.has(str(row.affix)) and not str(row.enemy_id).begins_with("BOSS_"), "%s %s is a known affix on a normal robot" % [mission, row.enemy_id])

    _check_overcharged()

    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_03"
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.configure_campaign({}, "ELITE-AFFIX-SMOKE", {})
    var elite_step := -1
    for index in range(stage.main_route.size()):
        if str(stage.main_route[index].get("type", "")) == "ELITE":
            elite_step = index
            break
    stage.current_step = elite_step
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(elite_step)
    await _frames(2)

    var shielded: EnemyActor = null
    var volatile: EnemyActor = null
    var plain: Array[EnemyActor] = []
    for node in get_nodes_in_group("m3_enemies"):
        var enemy := node as EnemyActor
        var affix := enemy.get_node_or_null("EliteAffix") as EliteAffix
        if affix == null: plain.append(enemy)
        elif affix.affix_id == "SHIELDED": shielded = enemy
        elif affix.affix_id == "VOLATILE": volatile = enemy
    _check(shielded != null and shielded.enemy_id == "ENM_SITE7_BULWARK_01", "M3 elite room: the BULWARK is SHIELDED")
    _check(volatile != null and volatile.enemy_id == "ENM_SITE7_DRONE_01", "M3 elite room: the drone is VOLATILE")
    _check(plain.size() == 2, "the other two robots stay plain (%d)" % plain.size())
    var story := str(stage.call("_combat_story", "ELITE"))
    _check(story.contains("SHIELDED:") and story.contains("VOLATILE:") and not story.contains("OVERCHARGED:"), "combat tips explain exactly the variants present")

    if shielded != null:
        var affix := shielded.get_node("EliteAffix") as EliteAffix
        _check(is_equal_approx(affix.barrier_max, shielded.max_health * float(affix.spec.barrier_ratio)), "barrier is the table's share of the robot's health")
        affix.barrier = affix.barrier_max
        var full := shielded.health
        shielded.apply_damage(affix.barrier_max * 0.5)
        _check(is_equal_approx(shielded.health, full) and is_equal_approx(affix.barrier, affix.barrier_max * 0.5), "a hit smaller than the barrier leaves health untouched")
        shielded.apply_damage(affix.barrier_max)
        _check(affix.barrier == 0.0 and is_equal_approx(shielded.health, full - affix.barrier_max * 0.5), "the overflow of a breaking hit reaches health")
        shielded.apply_damage(4.0)
        _check(is_equal_approx(shielded.health, full - affix.barrier_max * 0.5 - 4.0), "a broken barrier no longer soaks")
        var delay := float(affix.spec.barrier_regen_delay)
        affix._process(delay - 1.0)
        _check(affix.barrier == 0.0, "no recharge before the delay without damage")
        affix._process(1.5)
        _check(affix.barrier > 0.0 and affix.barrier < affix.barrier_max, "the barrier recharges after the delay without damage")
        affix._process(10.0)
        _check(is_equal_approx(affix.barrier, affix.barrier_max) and is_equal_approx(affix.barrier_share(), 1.0), "recharge stops at the full barrier")

    if volatile != null:
        for enemy in plain: enemy.free()
        if shielded != null: shielded.free()
        var at := volatile.global_position
        var ops := stage.squad.operators
        var hits: Array[String] = []
        ops[0].damage_taken.connect(func(_actor, _amount, source): hits.append(str(source)))
        ops[0].global_position = at + Vector2(60, 20)
        ops[1].global_position = at + Vector2(420, 0)
        ops[2].global_position = at + Vector2(-420, 60)
        var before: Array[float] = [ops[0].health, ops[1].health, ops[2].health]
        volatile.apply_damage(99999.0)
        var blast = null
        for child in stage.get_children():
            if child.get_script() == BLAST: blast = child
        _check(blast != null and not blast.detonated and blast.global_position.distance_to(at) < 0.01, "destroying it opens a warning circle on its position")
        _check(ops[0].health == before[0], "nothing is hit during the warning")
        if blast != null:
            var spec: Dictionary = EliteAffix.table().VOLATILE
            blast._physics_process(float(spec.death_blast_windup) * 0.55)
            _check(not blast.detonated, "still warning halfway through the windup")
            ops[0].global_position = at + Vector2(60, 20)
            ops[1].global_position = at + Vector2(420, 0)
            ops[2].global_position = at + Vector2(-420, 60)
            blast._physics_process(float(spec.death_blast_windup) * 0.5)
            _check(blast.detonated and blast.hits == 1, "the burst lands after the windup and hits one operator (%d)" % blast.hits)
            _check(is_equal_approx(before[0] - ops[0].health, float(spec.death_blast_damage)), "operator inside the circle takes the burst damage (%.1f)" % (before[0] - ops[0].health))
            _check(ops[1].health == before[1] and ops[2].health == before[2], "operators outside the circle are untouched")
            _check(hits == ["ENM_SITE7_DRONE_01"], "the burst is attributed to the drone for the play log")
            blast._physics_process(0.5)
            await _frames(1)
            _check(not is_instance_valid(blast), "the burst clears itself")

    if failures.is_empty():
        print("ELITE_AFFIX_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _check_overcharged() -> void:
    var ram := StoryStage01.ENEMY_SCENE.instantiate() as EnemyActor
    ram.configure("ENM_SITE7_RAM_01", 100.0)
    ram.apply_run_modifiers({"enemy_damage_multiplier": 1.2})
    _check(EliteAffix.apply(ram, "") == null and EliteAffix.apply(ram, "UNKNOWN") == null, "empty and unknown ids add nothing")
    var affix := EliteAffix.apply(ram, " overcharged ")
    _check(affix != null and affix.affix_id == "OVERCHARGED", "ids are trimmed and case-insensitive")
    var spec: Dictionary = EliteAffix.table().OVERCHARGED
    _check(is_equal_approx(ram.run_damage_multiplier, 1.2 * float(spec.damage_multiplier)) and is_equal_approx(ram.run_attack_interval_multiplier, float(spec.attack_interval_multiplier)) and is_equal_approx(ram.run_speed_multiplier, float(spec.speed_multiplier)), "OVERCHARGED stacks on the run modifiers")
    _check(affix != null and affix.barrier_max == 0.0, "OVERCHARGED has no barrier")
    _check(EliteAffix.apply(ram, "SHIELDED") == null, "a robot takes one affix")
    ram.free()

func _affix_rows(mission: String) -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    var data = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission))
    _collect(data, rows)
    return rows

func _collect(value: Variant, rows: Array[Dictionary]) -> void:
    if value is Dictionary:
        if value.has("enemy_id") and value.has("affix"): rows.append(value)
        for child in value.values(): _collect(child, rows)
    elif value is Array:
        for child in value: _collect(child, rows)

func _frames(count: int) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)
