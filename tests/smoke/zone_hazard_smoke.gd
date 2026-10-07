extends SceneTree
## Room hazards (data/progression/zone_hazards.json): every room that declares them gets
## that many vents on open floor, clear of the squad start, first-wave spawns and cover; a vent
## hits nobody until its telegraph ends, then hits operators and robots on it once (with
## the source for the play log); AI followers keep off vents and walk off one that is
## warning; clearing the room removes the vents.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const MISSIONS := ["MIS_CH01_01", "MIS_CH01_02", "MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05", "MIS_CH01_06", "MIS_CH01_07", "MIS_CH01_08", "MIS_CH01_09", "MIS_CH01_10"]

var failures: Array[String] = []
var checks := 0
var hazard_rooms := 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var table := ZoneHazard.table()
    _check(table.has("ARC_VENT") and ZoneHazard.tip("arc_vent").begins_with("ARC VENT:"), "ARC_VENT is defined with a tip")
    _check(ZoneHazard.create("UNKNOWN", Vector2.ZERO, 0) == null, "unknown hazard ids create nothing")
    for mission in MISSIONS:
        await _check_mission(mission)
    _check(hazard_rooms >= 5, "at least five rooms carry hazards (%d)" % hazard_rooms)
    if failures.is_empty():
        print("ZONE_HAZARD_SMOKE: PASS (%d checks, %d rooms)" % [checks, hazard_rooms])
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _check_mission(mission: String) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.configure_campaign({}, "ZONE-HAZARD-SMOKE", {})
    var cycled := false
    for step in range(stage.main_route.size()):
        var room: Dictionary = stage.main_route[step]
        var declared := 0
        for row in room.get("hazards", []): declared += int((row as Dictionary).get("count", 1))
        if declared == 0: continue
        hazard_rooms += 1
        _check(str(room.get("type", "")) != "BOSS", "%s %s: boss rooms keep their own area attacks" % [mission, room.id])
        stage.current_step = step
        stage.call("_activate_step")
        stage.debug_spawn_encounter_for_step(step)
        await _frames(1)
        var vents := _vents()
        var label := "%s %s" % [mission, room.id]
        _check(vents.size() == declared, "%s: %d of %d vents placed" % [label, vents.size(), declared])
        _check_placement(stage, vents, label)
        _check(str(stage.call("_combat_story", str(room.type))).contains("ARC VENT:"), label + ": combat tip explains the vent")
        for row: Dictionary in room.get("hazards", []):
            _check(str(stage.call("_combat_story", str(room.type))).contains(ZoneHazard.tip(str(row.type))), label + ": combat tip explains " + str(row.type))
        var arc: ZoneHazard = null
        for vent in vents:
            if vent.hazard_id == "ARC_VENT" and arc == null: arc = vent
        if not cycled and arc != null:
            cycled = true
            _check_cycle(stage, arc, label)
            await _check_followers(stage, arc, label)
        await _clear_room(stage)
        _check(_vents().is_empty(), label + ": clearing the room removes its vents")
    stage.queue_free()
    await _frames(3)

func _check_placement(stage: StoryStage01, vents: Array[ZoneHazard], label: String) -> void:
    var field: Node = stage.battlefield
    var covers: Array[PackedVector2Array] = []
    for cover in get_nodes_in_group("sable_environment_cover"):
        var footprint := PackedVector2Array()
        for g in cover.ground: footprint.append(cover.to_global(g))
        covers.append(footprint)
    var spawns: Array = field.call("debug_spawn_points")
    for vent in vents:
        var on_floor := true
        var clear_of_cover := true
        for rim in vent.boundary_points():
            if not bool(field.call("is_walkable", rim)): on_floor = false
            for footprint in covers:
                if Geometry2D.is_point_in_polygon(rim, footprint): clear_of_cover = false
        for footprint in covers:
            for corner in footprint:
                if vent.contains(corner): clear_of_cover = false
        _check(on_floor, label + ": the whole vent lies on walkable floor")
        _check(clear_of_cover, label + ": the vent does not overlap cover")
        var squad_gap := INF
        for i in range(3): squad_gap = minf(squad_gap, vent.global_position.distance_to(field.call("squad_spawn", i)))
        _check(squad_gap >= vent.radius + 90.0, "%s: vent clear of the squad start (%.0f)" % [label, squad_gap])
        var spawn_gap := INF
        for point: Vector2 in spawns.slice(0, 4): spawn_gap = minf(spawn_gap, vent.global_position.distance_to(point))
        _check(spawn_gap >= vent.radius + 30.0, "%s: vent clear of the first-wave spawn slots (%.0f)" % [label, spawn_gap])
        for other in vents:
            if other != vent: _check(vent.global_position.distance_to(other.global_position) >= maxf(vent.radius, other.radius) * 2.6, label + ": vents are spread apart")

func _check_cycle(stage: StoryStage01, vent: ZoneHazard, label: String) -> void:
    var ops := stage.squad.operators
    var sources: Array[String] = []
    ops[0].damage_taken.connect(func(_actor, _amount, source): sources.append(str(source)))
    var robot: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        var enemy := node as EnemyActor
        if robot == null and enemy.get_node_or_null("EliteAffix") == null and not enemy.enemy_id.begins_with("BOSS_"): robot = enemy
    _check(robot != null, label + ": a plain robot is available for the vent test")
    var place := func() -> void:
        ops[0].global_position = vent.global_position + Vector2(10, 4)
        ops[1].global_position = vent.global_position + Vector2(vent.radius + 60.0, 0)
        ops[2].global_position = vent.global_position + Vector2(0, -vent.radius - 80.0)
        if robot != null: robot.global_position = vent.global_position + Vector2(-14, -6)
    for enemy in get_nodes_in_group("m3_enemies"):
        if enemy != robot: (enemy as Node2D).global_position = vent.global_position + Vector2(900, 0)
    place.call()
    var before: Array[float] = [ops[0].health, ops[1].health, ops[2].health]
    var robot_before := robot.health if robot != null else 0.0
    _check(vent.phase == ZoneHazard.Phase.IDLE and vent.phase_left >= 2.0, label + ": a fresh vent idles before its first discharge")
    vent._physics_process(vent.phase_left + 0.01)
    _check(vent.phase == ZoneHazard.Phase.TELEGRAPH and ops[0].health == before[0], label + ": the telegraph starts without damage")
    place.call()
    vent._physics_process(float(vent.spec.telegraph) * 0.5)
    _check(vent.phase == ZoneHazard.Phase.TELEGRAPH and vent.discharges == 0, label + ": still warning halfway through the telegraph")
    place.call()
    vent._physics_process(float(vent.spec.telegraph) * 0.5 + 0.01)
    _check(vent.phase == ZoneHazard.Phase.DISCHARGE and vent.discharges == 1, label + ": the vent discharges once after the telegraph")
    _check(is_equal_approx(before[0] - ops[0].health, float(vent.spec.operator_damage)), "%s: operator on the vent takes %.0f (%.1f)" % [label, float(vent.spec.operator_damage), before[0] - ops[0].health])
    _check(ops[1].health == before[1] and ops[2].health == before[2], label + ": operators off the vent are untouched")
    _check(robot == null or is_equal_approx(robot_before - robot.health, float(vent.spec.enemy_damage)), label + ": the robot on the vent takes the discharge too")
    _check(sources == ["HAZARD_ARC_VENT"], label + ": the damage is attributed to the vent for the play log")
    vent._physics_process(float(vent.spec.discharge) + 0.01)
    _check(vent.phase == ZoneHazard.Phase.IDLE and vent.discharges == 1, label + ": the vent returns to idle without a second hit")

func _check_followers(stage: StoryStage01, vent: ZoneHazard, label: String) -> void:
    var squad := stage.squad
    var follower: OperatorActor = null
    for i in range(squad.operators.size()):
        if i != squad.active_index and not squad.operators[i].is_downed() and follower == null: follower = squad.operators[i]
    _check(follower != null, label + ": a follower is available for the vent test")
    if follower == null: return
    vent.phase = ZoneHazard.Phase.IDLE
    vent.phase_left = 3.0
    var rim := ZoneHazard.steer(self, follower.global_position, vent.global_position, stage)
    _check(not vent.contains(rim, ZoneHazard.SAFE_MARGIN) and bool(stage.battlefield.call("is_walkable", rim)), label + ": a follower goal on a vent moves to walkable floor off it")
    _check(ZoneHazard.steer(self, vent.global_position, rim, stage) == rim, label + ": an idle vent does not divert a follower heading off it")
    _check(not ZoneHazard.steer(self, vent.global_position + Vector2(vent.radius + 80.0, 0), Vector2.INF, stage).is_finite(), label + ": nothing to dodge away from the vent")
    vent.phase_left = ZoneHazard.REACT_LEAD * 0.5
    _check(ZoneHazard.steer(self, vent.global_position, Vector2.INF, stage).is_finite(), label + ": standing on a vent about to warn asks to step off")
    # Live: hold the robots still, put the follower on the vent at the start of its warning.
    for enemy in get_nodes_in_group("m3_enemies"): (enemy as Node).process_mode = Node.PROCESS_MODE_DISABLED
    squad.get_active_operator().global_position = vent.global_position + Vector2(8, 2)
    follower.global_position = vent.global_position + Vector2(-6, 3)
    vent.phase = ZoneHazard.Phase.TELEGRAPH
    vent.phase_left = float(vent.spec.telegraph)
    var before := follower.health
    var discharges := vent.discharges
    var left_at := -1
    for frame in range(90):
        await physics_frame
        if left_at < 0 and not vent.contains(follower.global_position): left_at = frame
        if vent.discharges > discharges: break
    _check(vent.discharges > discharges, label + ": the warning ran into a discharge")
    _check(left_at >= 0 and not vent.contains(follower.global_position), "%s: the follower walked off during the warning (frame %d)" % [label, left_at])
    _check(follower.health == before, label + ": the follower took no vent damage")
    for enemy in get_nodes_in_group("m3_enemies"): (enemy as Node).process_mode = Node.PROCESS_MODE_INHERIT

func _clear_room(stage: StoryStage01) -> void:
    for i in range(900):
        for node in get_nodes_in_group("m3_enemies"):
            var enemy := node as EnemyActor
            if enemy.health > 0.0: enemy.apply_damage(99999.0)
        await _frames(1)
        if not stage._combat_started: return
    _check(false, "room never cleared")

func _vents() -> Array[ZoneHazard]:
    var result: Array[ZoneHazard] = []
    for node in get_nodes_in_group("zone_hazards"):
        if not (node as Node).is_queued_for_deletion(): result.append(node as ZoneHazard)
    return result

func _frames(count: int) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)
