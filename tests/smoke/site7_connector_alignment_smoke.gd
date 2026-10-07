extends SceneTree

# Every mission joins its rooms the way the art is drawn: the five main-route decks
# climb up and to the right (a reversed mission walks them back down to the left);
# each branch leaves its parent room down and to the right, authored branches
# unmirrored and legacy branches mirrored. No plate is rotated, each
# deck runs into both rooms' painted floors, its painted walls stop the actor, and
# real WASD input carries an operator from one room over the deck into the next.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const INPUT := preload("res://scripts/ui/demo_input.gd")
var failures: Array[String] = []
var checks := 0

func _initialize() -> void:
    call_deferred("run")

func _check(ok: bool, note: String) -> void:
    checks += 1
    if not ok:
        failures.append(note)
        push_error(note)

## A frozen hostile is not a door; remove only its test-fixture body so this probe
## isolates terrain and prop traversal. Encounters keep spawning waves while the
## operator walks the rooms (a later drone wave once downed it mid-run), so every
## hostile is frozen before each input tick.
func _freeze_hostiles() -> void:
    for enemy in get_nodes_in_group("m3_enemies"):
        if enemy is EnemyActor and enemy.is_physics_processing():
            enemy.set_physics_process(false)
            enemy.collision_layer = 0
            enemy.collision_mask = 0

func _drive_to(actor: OperatorActor, target: Vector2, max_ticks: int = 360) -> void:
    INPUT.held[KEY_SHIFT] = true
    for tick in range(max_ticks):
        _freeze_hostiles()
        var delta := target - actor.global_position
        if delta.length() <= 35.0: break
        for key_code in [KEY_A, KEY_D, KEY_W, KEY_S]: INPUT.held.erase(key_code)
        if delta.x > 24.0: INPUT.held[KEY_D] = true
        elif delta.x < -24.0: INPUT.held[KEY_A] = true
        if delta.y > 24.0: INPUT.held[KEY_S] = true
        elif delta.y < -24.0: INPUT.held[KEY_W] = true
        await physics_frame
    for key_code in [KEY_A, KEY_D, KEY_W, KEY_S, KEY_SHIFT]: INPUT.held.erase(key_code)

## Walks the deck from `from` to `to` the way a player steers down a corridor: WASD
## toward a point 140 px ahead on the deck's line. First correct lateral drift:
## lookahead can cancel the sideways key at a narrow painted doorway. Keep the
## same 24 px input deadzone, collision and arrival limits for both steering modes.
func _follow(actor: OperatorActor, from: Vector2, to: Vector2, max_ticks: int = 480) -> void:
    INPUT.held[KEY_SHIFT] = true
    for tick in range(max_ticks):
        _freeze_hostiles()
        if actor.global_position.distance_to(to) <= 35.0: break
        var along := Geometry2D.get_closest_point_to_segment(actor.global_position, from, to)
        var lateral := along - actor.global_position
        var delta := lateral if maxf(absf(lateral.x), absf(lateral.y)) > 24.0 else along.move_toward(to, 140.0) - actor.global_position
        for key_code in [KEY_A, KEY_D, KEY_W, KEY_S]: INPUT.held.erase(key_code)
        if delta.x > 24.0: INPUT.held[KEY_D] = true
        elif delta.x < -24.0: INPUT.held[KEY_A] = true
        if delta.y > 24.0: INPUT.held[KEY_S] = true
        elif delta.y < -24.0: INPUT.held[KEY_W] = true
        await physics_frame
    for key_code in [KEY_A, KEY_D, KEY_W, KEY_S, KEY_SHIFT]: INPUT.held.erase(key_code)

## A point `distance` px from `door` toward the room centre, kept on walkable floor.
func _inside(field: Node, door: Vector2, room: Dictionary, distance: float) -> Vector2:
    var centre := Vector2(float(room.x), float(room.y))
    var step := distance
    while step > 0.0:
        var point := door.move_toward(centre, step)
        if field.is_walkable(point) and field.segment_walkable(door, point): return point
        step -= 20.0
    return door

func run() -> void:
    var only_mission := 0
    var floor_registry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/visual/site7_plate_floors.json"))["plates"]
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): only_mission = int(arg.get_slice("=", 1))
    for mission_number in range(1, 11):
        if only_mission != 0 and mission_number != only_mission: continue
        var mission_id := "MIS_CH01_%02d" % mission_number
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = mission_id
        root.add_child(stage)
        for tick in range(14):
            await physics_frame
            await process_frame
        var field := stage.battlefield
        _check(field.world_ready, mission_id + " continuous floor is ready")
        _freeze_hostiles()
        var actor := stage.squad.get_active_operator()
        var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
        for index in range(7):
            var branch := index >= 5
            var a: Dictionary = stage.branch_parent(index - 5) if branch else stage.main_route[index]
            var b: Dictionary = stage.optional_rooms[index - 5] if branch else stage.main_route[index + 1]
            var label := "%s/%s_%d" % [mission_id, "branch" if branch else "link", index - 5 if branch else index]
            var plate := art.get_connector_plate(index)
            _check(plate != null and field.connector_doors.has(index), label + " has artwork and deck doors")
            if plate == null or not field.connector_doors.has(index): continue
            _check(is_zero_approx(plate.rotation), label + " plate is not rotated")
            var placed: Dictionary = Site7RoomArtLayer.WORLD_LAYOUT.mission_connectors(mission_id)[index]
            var authored := not str(placed.get("deck", "")).is_empty()
            _check((plate.scale.x < 0.0) == (branch and not authored), label + " mirror matches authored/legacy deck")
            if authored:
                _check(str(placed.deck) == ("descending" if branch else "ascending"), label + " authored deck matches route direction")
            var ends: Array[Vector2] = field._deck_end_points(plate)
            var reverse := bool(placed.get("reverse", false))
            _check(not (branch and reverse), label + " branch decks are never reversed")
            for anchor in placed.get("door_anchors", []):
                var end_index := (0 if str(anchor.end) == "start" else 1) if plate.scale.x > 0 else (1 if str(anchor.end) == "start" else 0)
                var target := Vector2(float(anchor.position[0]), float(anchor.position[1]))
                _check(ends[end_index].distance_to(target) <= 0.5, label + " deck end meets authored doorway within 0.5 px")
                var room_plate := art.get_room_plate(str(anchor.room))
                var door: Array = floor_registry[str(room_plate.get_meta("asset"))]["doors"][str(anchor.side)]
                var threshold := room_plate.to_global((Vector2(float(door[0]), float(door[1])) - Vector2.ONE * 0.5) * room_plate.texture.get_size())
                _check(ends[end_index].distance_to(threshold) <= 0.5, label + " independently transformed painted threshold matches deck")
            var door_a: Vector2 = field.connector_doors[index][0]
            var door_b: Vector2 = field.connector_doors[index][1]
            if branch: _check(door_b.x > door_a.x and door_b.y > door_a.y, label + " descends down-right to the optional room")
            elif reverse: _check(door_b.x < door_a.x and door_b.y > door_a.y, label + " descends down-left to the next room")
            else: _check(door_b.x > door_a.x and door_b.y < door_a.y, label + " climbs up-right to the next room")
            _check(float(field.join_gaps.get("%d_a" % index, INF)) < 0.5 and float(field.join_gaps.get("%d_b" % index, INF)) < 0.5, label + " deck overlaps both rooms' painted floors")
            _check(field.segment_walkable(door_a, door_b), label + " deck is one straight walkable run")
            # The deck's painted walls: no walkable line leads 300 px sideways off its
            # midline (a neighbouring deck may lie beyond the wall).
            var middle := door_a.lerp(door_b, 0.5)
            var across := (door_b - door_a).orthogonal().normalized()
            _check(not field.segment_walkable(middle, middle + across * 300.0) and not field.segment_walkable(middle, middle - across * 300.0), label + " painted deck walls stop the actor")
            for forward in [true, false]:
                var from := _inside(field, door_a, a, 100.0) if forward else _inside(field, door_b, b, 100.0)
                var to := _inside(field, door_b, b, 100.0) if forward else _inside(field, door_a, a, 100.0)
                actor.global_position = from
                actor.velocity = Vector2.ZERO
                await physics_frame
                await _drive_to(actor, door_a if forward else door_b)
                await _follow(actor, door_a if forward else door_b, door_b if forward else door_a)
                await _drive_to(actor, to)
                var reached := actor.global_position.distance_to(to) <= 45.0 and not actor.is_downed()
                if not reached:
                    print("CONNECTOR_BLOCK ", JSON.stringify({"mission": mission_id, "connector": index, "forward": forward, "from": from, "to": to, "actor": actor.global_position, "walkable": field.is_walkable(actor.global_position)}))
                _check(reached, label + (" crossed from its first room into the next with WASD" if forward else " crossed back with WASD"))
        print("CONNECTOR_STAGE ", JSON.stringify({"mission": mission_id, "connectors": field.connector_doors.size(), "failed": failures.size()}))
        stage.queue_free()
        await process_frame
    print("SITE7_CONNECTOR_ALIGNMENT %s (%d checks)" % ["PASS" if failures.is_empty() else JSON.stringify(failures), checks])
    quit(0 if failures.is_empty() else 1)
