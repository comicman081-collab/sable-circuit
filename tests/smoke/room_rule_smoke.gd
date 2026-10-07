extends SceneTree
## Room rules (data/progression/room_rules.json, scripts/combat/room_rule.gd): the OVERRUN timer.
## The table and the pure helpers, every mission file's rooms, and a live StoryStage01: the timer calls the
## next wave in when it runs out and counts its seconds from the wave called last, a room thinned out first
## still calls it the old way, a room without a rule runs exactly as before, a rule on a boss room or on
## the training simulator is refused, and the rule and its HUD line are gone when the room is cleared.
## A technical check of the mechanism: it places no rule in any room and approves no balance or play.
## The "ERROR: StoryStage01 ..." lines in its log are the stage refusing rules this test hands it on purpose.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const Output := preload("res://tests/support/test_output.gd")
const DRONE := {"enemy_id": "ENM_SITE7_DRONE_01", "health": 100.0}
var checks := 0
var failures: Array[String] = []
var measurements: Dictionary = {}

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _table_contract()
    _problem_contract()
    _timer_contract()
    _mission_scan()
    await _live_timer()
    await _live_thinned_first()
    await _live_no_rule()
    await _live_two_waves()
    await _live_refusals()
    await _live_room_change()
    _write()
    if failures.is_empty():
        print("ROOM_RULE_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        print("ROOM_RULE_SMOKE: FAIL (%d checks, %d failures)" % [checks, failures.size()])
        quit(1)

# --- pure ------------------------------------------------------------------------------------------

## A whole standalone room row for the pure checks.
func _room(rule: Variant = null, extra: Dictionary = {}) -> Dictionary:
    var room := {"id": "R_TEST", "type": "COMBAT", "encounter": [DRONE.duplicate()],
        "reinforcements": [[DRONE.duplicate()]], "reinforce_at": 0}
    if rule != null: room["rule"] = rule
    for key in extra: room[key] = extra[key]
    return room

func _table_contract() -> void:
    var table := RoomRule.table()
    _check(table.keys() == ["OVERRUN"], "the table holds one room rule, OVERRUN")
    var spec: Dictionary = table.get("OVERRUN", {})
    _check(bool(spec.get("needs_reinforcements", false)), "OVERRUN calls a reinforcement wave, so it needs one")
    var low := float(spec.get("min_seconds", -1.0))
    var base := float(spec.get("seconds", -1.0))
    var high := float(spec.get("max_seconds", -1.0))
    _check(is_equal_approx(low, 20.0) and is_equal_approx(high, 120.0) and low <= base and base <= high,
        "OVERRUN seconds run 20-120 and the default sits inside (%s in %s-%s)" % [base, low, high])
    var tip := RoomRule.tip("OVERRUN")
    _check(tip.begins_with("OVERRUN:") and tip.length() <= 140, "the briefing tip names the rule and stays short enough for the transmission panel (%d chars)" % tip.length())
    _check(RoomRule.tip("overrun") == tip and RoomRule.tip("NOPE") == "", "tips are looked up case-insensitively and an unknown id has none")
    _check(RoomRule.rule_id({"type": " overrun "}) == "OVERRUN" and RoomRule.rule_id("OVERRUN") == "" and RoomRule.rule_id(null) == "", "rule_id reads only an object's type")

func _problem_contract() -> void:
    _check(RoomRule.problems(_room()).is_empty() and RoomRule.for_room(_room()).is_empty(), "a room without a rule has no problems and runs no rule")
    var plain := _room({"type": "OVERRUN", "seconds": 45})
    _check(RoomRule.problems(plain).is_empty(), "a plain OVERRUN row is accepted")
    var rule := RoomRule.for_room(plain)
    _check(rule.get("type") == "OVERRUN" and is_equal_approx(float(rule.get("seconds", -1.0)), 45.0), "for_room returns the type and its seconds")
    var defaulted := RoomRule.for_room(_room({"type": "overrun"}))
    _check(defaulted.get("type") == "OVERRUN" and is_equal_approx(float(defaulted.get("seconds", -1.0)), 45.0), "the type is case-insensitive and seconds default to the table's 45")
    for value in [20, 20.0, 120, 75.5]:
        _check(RoomRule.problems(_room({"type": "OVERRUN", "seconds": value})).is_empty(), "seconds %s is inside the limits" % str(value))
    var refused := {
        "a rule that is not an object": _room("OVERRUN"),
        "an unknown type": _room({"type": "FLOOD"}),
        "no type": _room({"seconds": 30}),
        "a boss room": _room({"type": "OVERRUN"}, {"type": "BOSS"}),
        "a room with no wave to call": _room({"type": "OVERRUN"}, {"reinforcements": []}),
        "seconds under the floor": _room({"type": "OVERRUN", "seconds": 19.9}),
        "seconds over the ceiling": _room({"type": "OVERRUN", "seconds": 120.1}),
        "seconds as text": _room({"type": "OVERRUN", "seconds": "45"}),
        "negative seconds": _room({"type": "OVERRUN", "seconds": -5}),
    }
    for label in refused:
        var row: Dictionary = refused[label]
        _check(not RoomRule.problems(row).is_empty(), "refused: " + str(label))
        _check(RoomRule.for_room(row).is_empty(), "no rule runs for: " + str(label))

func _timer_contract() -> void:
    var rule := {"type": "OVERRUN", "seconds": 45.0}
    _check(not RoomRule.overrun_due(rule, 44.99, true, 0.0), "the timer is not due before its seconds")
    _check(RoomRule.overrun_due(rule, 45.0, true, 0.0), "the timer is due when its seconds are up")
    _check(not RoomRule.overrun_due(rule, 90.0, false, 0.0), "never due with no wave left to call")
    _check(not RoomRule.overrun_due(rule, 90.0, true, 0.4), "never due while a wave is already on its way in")
    _check(not RoomRule.overrun_due({}, 90.0, true, 0.0), "an empty rule is never due")
    _check(not RoomRule.overrun_due({"type": "FLOOD", "seconds": 1.0}, 90.0, true, 0.0), "another type is not OVERRUN's timer")
    var line := "OVERRUN // NEXT WAVE IN %d"
    _check(RoomRule.hud_line(rule, 0.0, true, 0.0) == line % 45, "the line starts at the rule's seconds")
    _check(RoomRule.hud_line(rule, 0.2, true, 0.0) == line % 45, "a started second still counts as a whole one")
    _check(RoomRule.hud_line(rule, 44.2, true, 0.0) == line % 1, "the last second reads 1")
    _check(RoomRule.hud_line(rule, 45.0, true, 0.0) == line % 0 and RoomRule.hud_line(rule, 50.0, true, 0.0) == line % 0, "the line never goes negative")
    _check(RoomRule.hud_line(rule, 10.0, false, 0.0) == "", "no line with no wave left")
    _check(RoomRule.hud_line(rule, 10.0, true, 1.4) == "", "no line while a wave is on its way in")
    _check(RoomRule.hud_line({}, 10.0, true, 0.0) == "", "no line without a rule")

func _mission_scan() -> void:
    var rooms := 0
    var with_rule: Array[String] = []
    var problems: Array[String] = []
    var files := 0
    for file in DirAccess.get_files_at("res://data/missions"):
        if not (file.begins_with("MIS_CH01_") and file.ends_with(".json")): continue
        var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/" + file))
        if not (parsed is Dictionary):
            problems.append(file + ": unreadable")
            continue
        files += 1
        for key in ["main_route", "optional_rooms"]:
            for room_variant in (parsed as Dictionary).get(key, []):
                if not (room_variant is Dictionary): continue
                var room: Dictionary = room_variant
                rooms += 1
                if room.has("rule"): with_rule.append("%s/%s" % [file.get_basename(), str(room.get("id", "?"))])
                for line in RoomRule.problems(room): problems.append(file.get_basename() + " " + line)
    _check(files >= 10 and rooms >= 80, "the scan reads every mission's rooms (%d files, %d rooms)" % [files, rooms])
    _check(problems.is_empty(), "every room row that declares a rule declares a valid one: " + "; ".join(problems))
    measurements["mission_files"] = files
    measurements["mission_rooms"] = rooms
    measurements["rooms_with_rule"] = with_rule

# --- live stage ------------------------------------------------------------------------------------

## A stage in mission 6's fourth room, process off so the test sets the clock, with the first wave standing
## (one drone) and `extra` merged over the room's row: encounter, a one-wave reinforcement row, no hazards.
func _fixture(extra: Dictionary = {}) -> StoryStage01:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_06"
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.set_process(false)
    stage.configure_campaign({}, "ROOM-RULE-FIXTURE")
    stage.current_step = 3
    var room: Dictionary = stage.main_route[3].duplicate(true)
    room.encounter = [DRONE.duplicate()]
    room.reinforcements = [[DRONE.duplicate()]]
    room.reinforce_at = 0
    room.hazards = []
    for key in extra: room[key] = extra[key]
    stage.main_route[3] = room
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(3)
    _freeze(stage)
    return stage

func _freeze(stage: StoryStage01) -> void:
    for node in get_nodes_in_group("m3_enemies"):
        if node.get_parent() == stage: node.set_physics_process(false)

func _live_enemies(stage: StoryStage01) -> Array[EnemyActor]:
    var found: Array[EnemyActor] = []
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and node.get_parent() == stage and not node.is_queued_for_deletion(): found.append(node)
    return found

func _drop(stage: StoryStage01) -> void:
    stage.free()
    current_scene = null
    await _frames(2)

func _live_timer() -> void:
    var stage: StoryStage01 = await _fixture({"rule": {"type": "OVERRUN", "seconds": 30}})
    var waves: Array[int] = []
    var completed: Array[int] = []
    stage.wave_spawned.connect(func(_row: Dictionary, index: int, _ids: Array) -> void: waves.append(index))
    stage.room_completed.connect(func(_row: Dictionary, step: int) -> void: completed.append(step))
    _check(stage._room_rule == {"type": "OVERRUN", "seconds": 30.0}, "the room's rule is read from its row")
    _check(stage.enemies_alive == 1 and stage._wave_index == 0 and is_zero_approx(stage._room_rule_clock), "the first wave stands and the clock starts at zero")
    stage._process(0.0)
    _check(stage.hud.debug_rule_text() == "OVERRUN // NEXT WAVE IN 30", "the HUD counts down from the rule's seconds")
    _check(str(stage.call("_combat_story", "COMBAT")).contains("OVERRUN:"), "the briefing line explains the rule")
    var rule_rect := (stage.hud.get("_rule_label") as Control).get_global_rect()
    # The hidden legacy _optional_label (858, 98) is the one HUD label this line may overlap.
    for label_name in ["_intel_label", "_cargo_label", "_status_label", "_transmission_panel"]:
        var other := (stage.hud.get(label_name) as Control).get_global_rect()
        _check(not rule_rect.intersects(other), "the rule line does not touch " + label_name)
    _check(Rect2(Vector2.ZERO, Vector2(1280, 720)).encloses(rule_rect), "the rule line sits inside the 1280 x 720 HUD")
    for step in range(29): stage._process(1.0)
    _check(stage._wave_index == 0 and stage.enemies_alive == 1 and stage.hud.debug_rule_text() == "OVERRUN // NEXT WAVE IN 1",
        "one second short of the timer nothing is called")
    stage._process(1.0)
    _check(stage._wave_index == 1 and is_equal_approx(stage._wave_wait, 1.4) and stage.enemies_alive == 1,
        "the timer calls the next wave in with the stage's own 1.4 s entry wait while a robot still lives")
    _check(str(stage.hud.get("_objective_label").text) == "REINFORCEMENTS / WAVE 2-2", "the objective names the called wave")
    _check(stage.hud.debug_rule_text() == "" and is_zero_approx(stage._room_rule_clock), "the countdown hides and the clock restarts at the call")
    stage._process(1.0)
    _check(stage.enemies_alive == 1 and waves.is_empty() and is_equal_approx(stage._wave_wait, 0.4), "the wave is still on its way in: nobody has spawned")
    stage._process(0.5)
    _freeze(stage)
    _check(stage.enemies_alive == 2 and is_zero_approx(stage._wave_wait) and waves == [1], "the called wave appears once the entry wait is over")
    measurements["timer_called_wave_at_seconds"] = 30.0
    for enemy in _live_enemies(stage): enemy.apply_damage(99999.0)
    _check(stage.enemies_alive == 0 and completed == [3] and not stage._combat_started, "clearing both waves completes the room")
    _check(stage._room_rule.is_empty() and stage.hud.debug_rule_text() == "", "the rule and its HUD line end with the room")
    await _drop(stage)

func _live_thinned_first() -> void:
    var stage: StoryStage01 = await _fixture({"rule": {"type": "OVERRUN", "seconds": 30}})
    stage._process(10.0)
    _check(stage._wave_index == 0 and is_equal_approx(stage._room_rule_clock, 10.0), "ten seconds in, nothing is called yet")
    for enemy in _live_enemies(stage): enemy.apply_damage(99999.0)
    _check(stage._wave_index == 1 and is_equal_approx(stage._wave_wait, 2.2) and stage._combat_started,
        "a room thinned out first still calls its wave the old way (2.2 s with no robot left)")
    _check(is_zero_approx(stage._room_rule_clock) and stage.hud.debug_rule_text() == "", "the timer restarts with that call")
    stage._process(100.0)
    _freeze(stage)
    _check(stage._wave_index == 1 and stage.enemies_alive == 1, "the timer never calls a wave that is not there: the last one only arrives")
    await _drop(stage)

func _live_no_rule() -> void:
    var stage: StoryStage01 = await _fixture()
    _check(stage._room_rule.is_empty() and stage.hud.debug_rule_text() == "", "a room with no rule row runs none")
    for step in range(120): stage._process(1.0)
    _check(stage._wave_index == 0 and stage.enemies_alive == 1 and stage.hud.debug_rule_text() == "",
        "two minutes in, a room with no rule has called nothing on a timer")
    _check(not str(stage.call("_combat_story", "COMBAT")).contains("OVERRUN"), "its briefing line has no rule text")
    for enemy in _live_enemies(stage): enemy.apply_damage(99999.0)
    _check(stage._wave_index == 1 and is_equal_approx(stage._wave_wait, 2.2) and stage._combat_started, "the thinned-out call is the one the stage always had")
    await _drop(stage)

func _live_two_waves() -> void:
    var stage: StoryStage01 = await _fixture({"rule": {"type": "OVERRUN", "seconds": 20},
        "reinforcements": [[DRONE.duplicate()], [DRONE.duplicate()]]})
    stage._process(20.0)
    _check(stage._wave_index == 1 and is_equal_approx(stage._wave_wait, 1.4), "the timer calls the second wave at 20 s")
    stage._process(1.0)
    stage._process(0.5)
    _freeze(stage)
    _check(stage.enemies_alive == 2 and stage._wave_index == 1, "the second wave stands")
    _check(stage.hud.debug_rule_text() == "OVERRUN // NEXT WAVE IN 19", "the countdown returns for the third wave, counted from the wave called last")
    stage._process(18.0)
    _check(stage._wave_index == 1, "the third wave is not called 18 s after the second")
    stage._process(0.5)
    _check(stage._wave_index == 2 and is_equal_approx(stage._wave_wait, 1.4), "the third wave is called 20 s after the second")
    _check(stage.hud.debug_rule_text() == "", "no countdown once no wave is left")
    await _drop(stage)

func _live_refusals() -> void:
    var stage: StoryStage01 = await _fixture()
    var wave := [[DRONE.duplicate()]]
    var cases := {
        "a boss room": {"id": "R_BOSS", "type": "BOSS", "rule": {"type": "OVERRUN"}, "reinforcements": wave},
        "a room with no wave to call": {"id": "R_ONE", "type": "COMBAT", "rule": {"type": "OVERRUN"}, "reinforcements": []},
        "an unknown type": {"id": "R_FLOOD", "type": "COMBAT", "rule": {"type": "FLOOD"}, "reinforcements": wave},
        "a rule that is not an object": {"id": "R_TEXT", "type": "COMBAT", "rule": "OVERRUN", "reinforcements": wave},
        "seconds out of range": {"id": "R_FAST", "type": "COMBAT", "rule": {"type": "OVERRUN", "seconds": 5}, "reinforcements": wave},
    }
    for label in cases:
        stage.call("_begin_room_rule", cases[label])
        _check(stage._room_rule.is_empty() and stage.hud.debug_rule_text() == "", "the stage refuses and runs no rule for " + str(label))
    var valid := {"id": "R_OK", "type": "COMBAT", "rule": {"type": "OVERRUN"}, "reinforcements": wave}
    stage.battle_preview = true
    stage.call("_begin_room_rule", valid)
    _check(stage._room_rule.is_empty(), "the training simulator runs no room rule")
    stage.battle_preview = false
    stage.call("_begin_room_rule", valid)
    _check(stage._room_rule == {"type": "OVERRUN", "seconds": 45.0}, "the same row outside the simulator does run, at the default 45 s")
    await _drop(stage)

func _live_room_change() -> void:
    var stage: StoryStage01 = await _fixture({"rule": {"type": "OVERRUN", "seconds": 30}})
    stage._process(12.0)
    _check(stage.hud.debug_rule_text() == "OVERRUN // NEXT WAVE IN 18", "the rule is counting")
    var plain: Dictionary = stage.main_route[3].duplicate(true)
    plain.erase("rule")
    stage.main_route[3] = plain
    stage.debug_spawn_encounter_for_step(3)
    _freeze(stage)
    _check(stage._room_rule.is_empty() and is_zero_approx(stage._room_rule_clock) and stage.hud.debug_rule_text() == "",
        "the next room does not inherit the rule, its clock or its HUD line")
    await _drop(stage)

# --- plumbing --------------------------------------------------------------------------------------

func _write() -> void:
    var out := Output.path("res://.cache/tests/room_rule.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var file := FileAccess.open(out, FileAccess.WRITE)
    if file == null:
        failures.append("cannot write " + out)
        return
    file.store_string(JSON.stringify({"checks": checks, "measurements": measurements, "failures": failures}, "  "))
    file.close()

func _frames(count: int) -> void:
    for index in range(count):
        await physics_frame
        await process_frame

func _check(condition: bool, message: String) -> void:
    checks += 1
    if not condition: failures.append(message)
