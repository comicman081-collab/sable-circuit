extends SceneTree
## Traversal audit across all five operations: painted-floor walk graph, every
## room reachable around live cover, every cover prop standing on floor, every
## authored hostile actually spawning on reachable ground, and physical WASD
## movement from each room into the next. Technical checks only; not a human
## playtest or art approval.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const MAX_JOIN_GAP := 420.0
var failures: Array[String] = []
var checks := 0
var report: Array[Dictionary] = []

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func center(room: Dictionary) -> Vector2:
    return Vector2(float(room.x), float(room.y))

## Same goal handling as live AI (CoverNavigation.direction): points inside a
## cover footprint are first moved to its nearest free floor edge.
func reachable(stage: StoryStage01, actor: OperatorActor, from: Vector2, to: Vector2) -> bool:
    actor.global_position = stage.constrain_battle_position(from)
    var nav := NAV.new()
    var obstacles := NAV.ground_obstacles(actor)
    var start := NAV._free_goal(actor, actor.global_position, obstacles)
    var goal := NAV._free_goal(actor, stage.constrain_battle_position(to), obstacles)
    if not start.is_finite() or not goal.is_finite(): return false
    actor.global_position = start
    if actor.global_position.distance_to(goal) < 8.0: return true
    if NAV._clear_ground(actor, actor.global_position, goal, obstacles): return true
    return not nav._plan(actor, actor.global_position, goal, obstacles).is_empty()

## Drive the real actor (physics, collision, floor clamp) along the live
## navigation direction, as a steering player would. Held-key door crossings
## are covered separately by site7_connector_alignment_smoke.
func walk(stage: StoryStage01, actor: OperatorActor, goal: Vector2, max_ticks: int) -> float:
    var nav := NAV.new()
    for tick in range(max_ticks):
        var offset := goal - actor.global_position
        if offset.length() <= 60.0: break
        actor.debug_drive(nav.direction(actor, goal, 1.0 / 60.0), Vector2.RIGHT)
        actor._debug_run = true
        await physics_frame
    actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    return actor.global_position.distance_to(goal)

func run() -> void:
    for number in range(1, 11):
        var mission_id := "MIS_CH01_%02d" % number
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = mission_id
        stage.battle_preview = true
        root.add_child(stage)
        for tick in range(12): await process_frame; await physics_frame
        var bf: Node = stage.battlefield
        var row := {"mission": mission_id}
        check(bf.world_ready, mission_id + " walk graph ready")
        # 15 plates plus the door funnels that join connector ends to rooms.
        check((bf.get("_world_polygons") as Array).size() >= 15, mission_id + " all 15 plates contribute floor")
        var worst_gap := 0.0
        var gaps: Variant = bf.get("join_gaps")
        if gaps is Dictionary:
            for key in gaps: worst_gap = maxf(worst_gap, float(gaps[key]))
        row["worst_join_gap"] = worst_gap
        check(worst_gap <= MAX_JOIN_GAP, mission_id + " every room/deck join bridged within %d px" % int(MAX_JOIN_GAP))
        var actor := stage.squad.get_active_operator()
        for other in stage.squad.operators:
            other.set_physics_process(false)
        var rooms: Array = stage.main_route + stage.optional_rooms
        # 1. Every objective marker can be stood on (interaction radius 175).
        for room: Dictionary in rooms:
            var c := center(room)
            var snapped: Vector2 = stage.constrain_battle_position(c)
            check(snapped.distance_to(c) < 150.0, "%s %s marker is on painted floor" % [mission_id, room.id])
        # 2. Every cover prop stands on floor and is not stranded in a wall.
        var props: Array = stage.get_node("EnvironmentProps").entries
        var off_floor: Array[String] = []
        for entry: Dictionary in props:
            var prop: Node2D = entry.prop
            var footprint := Vector2.ZERO
            for p in prop.ground: footprint += prop.to_global(p)
            footprint /= float(maxi(1, prop.ground.size()))
            if not bf.is_walkable(footprint): off_floor.append("%s@%s" % [entry.asset, entry.room_id])
        row["cover_off_floor"] = off_floor
        check(off_floor.is_empty(), "%s every cover prop stands on painted floor %s" % [mission_id, str(off_floor)])
        # Make every prop active so routing is tested around real cover.
        for entry: Dictionary in props: entry.prop.set_active(true)
        actor.set_physics_process(false)
        # 3. Route connectivity around live cover, room to room and branches.
        for index in range(stage.main_route.size() - 1):
            check(reachable(stage, actor, center(stage.main_route[index]), center(stage.main_route[index + 1])),
                "%s route %s -> %s navigable around cover" % [mission_id, stage.main_route[index].id, stage.main_route[index + 1].id])
        for index in range(stage.optional_rooms.size()):
            var parent: Dictionary = stage.branch_parent(index)
            check(reachable(stage, actor, center(parent), center(stage.optional_rooms[index])),
                "%s branch %s -> %s navigable" % [mission_id, parent.id, stage.optional_rooms[index].id])
            check(reachable(stage, actor, center(stage.optional_rooms[index]), center(parent)),
                "%s branch %s return navigable" % [mission_id, stage.optional_rooms[index].id])
        # 4. Every authored hostile spawns on reachable floor, every wave.
        var spawned_total := 0
        var authored_total := 0
        for room: Dictionary in stage.main_route:
            var waves: Array = [room.get("encounter", [])]
            waves.append_array(room.get("reinforcements", []))
            if (waves[0] as Array).is_empty(): continue
            bf.call("begin_encounter", room)
            var squad_point: Vector2 = bf.call("squad_spawn", 0)
            # Training preview places the squad here; it must not overlap cover.
            for i in range(3):
                var spawn: Vector2 = bf.call("squad_spawn", i)
                for entry: Dictionary in props:
                    var footprint := PackedVector2Array()
                    for g in entry.prop.ground: footprint.append(entry.prop.to_global(g))
                    var clear := not Geometry2D.is_point_in_polygon(spawn, footprint)
                    for edge in range(footprint.size()):
                        clear = clear and spawn.distance_to(Geometry2D.get_closest_point_to_segment(spawn, footprint[edge], footprint[(edge + 1) % footprint.size()])) > 24.0
                    check(clear, "%s %s squad spawn %d clear of %s cover" % [mission_id, room.id, i, entry.asset])
            var slot := 0
            var slots: Array[Vector2] = []
            for wave: Array in waves:
                authored_total += wave.size()
                for i in range(wave.size()):
                    var p: Vector2 = bf.call("enemy_spawn", slot)
                    check(bf.is_walkable(p), "%s %s hostile slot %d spawns on floor" % [mission_id, room.id, slot])
                    check(reachable(stage, actor, p, squad_point), "%s %s hostile slot %d can reach the squad" % [mission_id, room.id, slot])
                    slot += 1
            # A wave never stacks two hostiles on one point.
            for point in bf.call("debug_spawn_points"): slots.append(point)
            var stacked := false
            for a in range(slots.size()):
                for b in range(a + 1, slots.size()):
                    stacked = stacked or slots[a].distance_to(slots[b]) < 60.0
            check(not stacked, "%s %s spawn slots are spread apart" % [mission_id, room.id])
            check(slots.size() >= mini(slot, 6), "%s %s has distinct slots for the wave sizes (%d)" % [mission_id, room.id, slots.size()])
            bf.call("release")
            # Live spawn through the game's own encounter entry point.
            stage._encounter_waves = waves
            stage._wave_index = 0
            stage._spawn_serial = 0
            stage.enemies_alive = 0
            stage.current_step = stage.main_route.find(room)
            bf.call("begin_encounter", room)
            for wave_index in range(waves.size()):
                stage._wave_index = wave_index
                var before: int = stage.enemies_alive
                stage._spawn_wave(room)
                spawned_total += stage.enemies_alive - before
            await physics_frame
            for enemy in get_nodes_in_group("m3_enemies"):
                if enemy is EnemyActor:
                    check(enemy.is_inside_tree() and enemy.visible, "%s %s %s visible after spawn" % [mission_id, room.id, enemy.enemy_id])
                    check(bf.is_walkable(enemy.global_position), "%s %s %s stays on floor" % [mission_id, room.id, enemy.enemy_id])
                    enemy.queue_free()
            await process_frame
            bf.call("release")
        row["hostiles"] = [spawned_total, authored_total]
        check(spawned_total == authored_total, "%s all %d authored hostiles spawned (%d)" % [mission_id, authored_total, spawned_total])
        # 5. Physical steered traversal of the whole route and both branches.
        actor.set_physics_process(true)
        stage.battle_preview = true
        stage._mission_ended = true
        actor.global_position = stage.constrain_battle_position(center(stage.main_route[0]))
        await physics_frame
        var legs: Array[Dictionary] = []
        # Room by room, out to each branch from its parent room and back.
        var sequence: Array = []
        for step in range(1, stage.main_route.size()):
            sequence.append(stage.main_route[step])
            for branch in range(stage.optional_rooms.size()):
                if str(stage.branch_parent(branch).id) == str(stage.main_route[step].id):
                    sequence.append_array([stage.optional_rooms[branch], stage.main_route[step]])
        for target: Dictionary in sequence:
            var miss := await walk(stage, actor, stage.constrain_battle_position(center(target)), 1500)
            legs.append({"to": target.id, "miss": snappedf(miss, 0.1), "at": [snappedf(actor.global_position.x, 1), snappedf(actor.global_position.y, 1)]})
            check(miss <= 120.0, "%s steered movement reaches %s (%.0f px short)" % [mission_id, target.id, miss])
            check(bf.is_walkable(actor.global_position), "%s actor never leaves floor near %s" % [mission_id, target.id])
            if miss > 120.0: break
        row["wasd_legs"] = legs
        report.append(row)
        print("TRAVERSAL_AUDIT ", JSON.stringify(row))
        stage.queue_free()
        for tick in range(4): await process_frame
    var out := "res://qa/traversal_audit_20260924"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var file := FileAccess.open(out + "/audit.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"checks": checks, "failures": failures, "missions": report, "human_playtest": false}, "  "))
    file.close()
    print("SITE7_TRAVERSAL_AUDIT: %s (%d checks, %d failures)" % ["PASS" if failures.is_empty() else "FAIL", checks, failures.size()])
    quit(0 if failures.is_empty() else 1)
