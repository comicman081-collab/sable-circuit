extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")

var failures: Array[String] = []
var checks := 0
var out_dir := TestOutput.path("res://.cache/tests/play_session_log")

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _check(PlaySessionLog.default_output_dir() == "", "headless runs keep no play log by default")
    var existing := DirAccess.get_files_at(out_dir)
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    var chosen := RunContract.offers("PLAY-LOG-SMOKE", stage.mission_id)[1]
    stage.configure_campaign({}, "PLAY-LOG-SMOKE", chosen)
    _check(stage.get_node_or_null("PlaySessionLog") == null, "stage attaches no log when the default folder is off")
    var overlay := stage.get_node_or_null("DebugOverlay")
    _check(overlay != null, "stage carries the F9 debug overlay")
    if overlay != null:
        var text := str(overlay.call("readout"))
        _check(text.contains("ATTACKING") and text.contains("/ 3"), "overlay reports attackers against the cap of 3")
        _check(text.contains("PLAY LOG off"), "overlay shows the log is off")

    var session_log := PlaySessionLog.attach(stage, out_dir)
    _check(session_log != null and session_log.get_parent() == stage, "log attaches with an explicit folder")
    # Open the first combat room, then spawn its encounter in the same frame.
    var combat_step := -1
    for index in range(stage.main_route.size()):
        if str(stage.main_route[index].get("type", "")) == "COMBAT":
            combat_step = index
            break
    stage.current_step = combat_step
    stage.call("_activate_step")
    var enemy_ids := stage.debug_spawn_encounter_for_step(combat_step)
    await _frames(2)
    _check(not enemy_ids.is_empty(), "combat room spawns hostiles")

    var squad := stage.squad
    var aster := squad.operators[0]
    var rook := squad.operators[1]
    squad.request_control(0)
    rook.apply_damage(30.0, "ENM_SITE7_DRONE_01")
    aster.apply_damage(5.0)
    var enemies := root.get_tree().get_nodes_in_group("m3_enemies")
    var target: EnemyActor = enemies[0] as EnemyActor if not enemies.is_empty() else null
    if target != null:
        aster.on_projectile_hit(target, 12.0)
        target.apply_damage(99999.0)
    var skills := aster.get_node("SkillController") as OperatorSkillController
    var cast := skills.debug_force_cast("E")
    rook.apply_damage(99999.0, "ENM_SITE7_RAM_01")
    stage.call("_finish_mission", "EXTRACTED")
    await _frames(2)

    _check(not session_log.written_path.is_empty() and FileAccess.file_exists(session_log.written_path), "mission end writes a JSON record")
    var record = JSON.parse_string(FileAccess.get_file_as_string(session_log.written_path)) if not session_log.written_path.is_empty() else null
    _check(record is Dictionary, "record parses")
    if record is Dictionary:
        var totals: Dictionary = record.totals
        var by_source: Dictionary = totals.damage_taken_by_source
        _check(record.outcome == "EXTRACTED" and record.mission_id == stage.mission_id, "record names outcome and mission")
        _check(str(record.get("contract_id", "")) == RunContract.identity(chosen) and not bool(record.get("redline", true)), "record names selected alternative and ordinary deployment")
        _check(is_equal_approx(float(by_source.get("ENM_SITE7_DRONE_01", 0.0)), 30.0), "damage is attributed to the enemy type")
        _check(by_source.has("UNKNOWN") and by_source.has("ENM_SITE7_RAM_01"), "unattributed and lethal damage are kept")
        _check(int(totals.downs) == 1, "down counted once")
        _check(float(totals.damage_taken) <= 35.01 + rook.max_health, "a lethal hit counts only the health it removed")
        _check(FileAccess.get_file_as_string(session_log.written_path).contains("\"downs\": 1,"), "counters are written as whole numbers")
        _check(target == null or int((totals.kills as Dictionary).get(target.enemy_id, 0)) == 1, "kill counted by enemy type")
        _check(target == null or (int(totals.hits) >= 1 and int(totals.player_hits) == 1), "controlled operator hit counted")
        _check(cast == ((totals.skills as Dictionary).size() == 1), "a successful skill cast is counted")
        var rooms: Array = record.rooms
        _check(rooms.size() >= 1 and rooms[0].id == stage.main_route[combat_step].id and (rooms[0].waves as Array).size() >= 1, "room and wave recorded")
        _check(float(rooms[0].seconds) >= 0.0 and is_equal_approx(float((rooms[0].damage_taken_by_source as Dictionary).get("ENM_SITE7_DRONE_01", 0.0)), 30.0), "room keeps its own damage and time")
        var kinds := []
        for row in record.events: kinds.append(row.event)
        _check("wave" in kinds and "damage" in kinds and "down" in kinds and kinds[-1] == "end", "event timeline recorded in order")

    # Leaving mid-mission still leaves an ABANDONED record.
    var second := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(second)
    await _frames(4)
    second.configure_campaign({}, "PLAY-LOG-REDLINE", RunContract.redline("PLAY-LOG-REDLINE"))
    var second_log := PlaySessionLog.attach(second, out_dir)
    second.queue_free()
    await _frames(2)
    _check(second_log == null or (not is_instance_valid(second_log)), "log leaves with its stage")
    var abandoned := 0
    for file in DirAccess.get_files_at(out_dir):
        if file.ends_with("_ABANDONED.json") and not file in existing:
            abandoned += 1
            var row: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(out_dir.path_join(file)))
            _check(str(row.get("contract_id", "")) == "REDLINE/REDLINE_RECOVERY" and bool(row.get("redline", false)), "abandoned REDLINE log retains its contract")
    _check(abandoned == 1, "leaving mid-mission writes one ABANDONED record")

    if failures.is_empty():
        print("PLAY_SESSION_LOG_SMOKE: PASS (%d checks) %s" % [checks, out_dir])
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _frames(count: int) -> void:
    for i in range(count): await process_frame

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)
