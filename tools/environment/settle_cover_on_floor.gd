extends SceneTree
## Move kArchive cover props that are off the walk graph, cover an objective
## marker, or overlap a squad spawn to the nearest spot that (a) keeps the whole
## footprint on the live walk graph, (b) stays clear of objectives/spawns and
## other cover, and (c) still leaves every route through the room plannable
## around the cover with the real CoverNavigation planner. Prop size and asset
## are unchanged. Reviewed placements that already pass keep their point.
##
## Godot --headless --path . -s res://tools/environment/settle_cover_on_floor.gd [-- --write]
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const PROPS := "res://data/visual/site7_environment_props.json"
const OBJECTIVE_CLEARANCE := 60.0
const SPAWN_CLEARANCE := 24.0
## A cover this close to a deck door stands in the doorway; squads entering the room
## bump into it even when the planner can squeeze round it.
const DOOR_CLEARANCE := 110.0
## Routes are checked with the operator's collider plus this margin on every side:
## robots are up to 4 px wider (an 18 px circle against the operator's 14 px capsule),
## and in corridor rooms a lane one robot wide was plugged by the robot that stopped
## there to attack.
const LANE_MARGIN := 20.0
## Robots stand on the first spawn slots of a combat room (a mortar never leaves its
## slot), so routes must also pass around a robot body of this radius on each slot.
const ROBOT_RADIUS := 18.0
const BODY_SLOTS := 4
var report: Array[Dictionary] = []

func _init() -> void: call_deferred("run")

func footprint(prop: Node2D) -> PackedVector2Array:
    var out := PackedVector2Array()
    for g in prop.ground: out.append(prop.to_global(g))
    return out

func distance_to_shape(point: Vector2, shape: PackedVector2Array) -> float:
    if Geometry2D.is_point_in_polygon(point, shape): return 0.0
    var best := INF
    for i in range(shape.size()):
        best = minf(best, point.distance_to(Geometry2D.get_closest_point_to_segment(point, shape[i], shape[(i + 1) % shape.size()])))
    return best

func on_floor(bf: Node, shape: PackedVector2Array) -> bool:
    var centre := Vector2.ZERO
    for p in shape: centre += p
    centre /= float(shape.size())
    if not bf.is_walkable(centre): return false
    for p in shape:
        if not bf.is_walkable(p.move_toward(centre, 6.0)): return false
    return true

func keep_clear_points(stage: StoryStage01, bf: Node, room: Dictionary, layout: bool) -> Array:
    var points: Array = []
    if layout:
        bf.call("begin_encounter", room)
        for i in range(3): points.append([bf.call("squad_spawn", i), SPAWN_CLEARANCE])
        for i in range(3): points.append([bf.call("enemy_spawn", i), SPAWN_CLEARANCE])
        bf.call("release")
    else:
        points.append([Vector2(float(room.x), float(room.y)), OBJECTIVE_CLEARANCE])
    # StoryStage01._place_squad_at_entry drops the squad around the entry marker.
    if str(room.id) == str(stage.main_route[0].id):
        for offset in SquadController.FORMATION_OFFSETS:
            points.append([Vector2(float(room.x), float(room.y)) + offset, SPAWN_CLEARANCE + 16.0])
    for pair: Array in (bf.get("connector_doors") as Dictionary).values():
        for door: Vector2 in pair: points.append([door, DOOR_CLEARANCE])
    return points

## Room centre plus every route node inside this room's reach: all must stay
## mutually reachable around the live cover.
func route_points(stage: StoryStage01, bf: Node, room: Dictionary, layout: bool) -> Array[Vector2]:
    var centre: Vector2 = stage.constrain_battle_position(Vector2(float(room.x), float(room.y)))
    var points: Array[Vector2] = [centre]
    # A combat room's robots must reach the squad around the cover.
    if layout:
        points.append_array(robot_slots(bf, room))
        bf.call("begin_encounter", room)
        points.append(bf.call("squad_spawn", 0))
        bf.call("release")
    for segment: PackedVector2Array in bf.get("_route_segments"):
        for end in [segment[0], segment[1]]:
            if end.distance_to(centre) < 900.0 and end.distance_to(centre) > 60.0 and bf.is_walkable(end):
                var duplicate := false
                for p in points: duplicate = duplicate or p.distance_to(end) < 40.0
                if not duplicate: points.append(end)
    # A door node can sit just beside a crate that still closes the deck's mouth
    # behind it, so the route must also reach the deck itself past each door.
    var doors: Dictionary = bf.get("connector_doors")
    for pair: Array in doors.values():
        for side in range(2):
            var door: Vector2 = pair[side]
            var deck: Vector2 = door.move_toward(pair[1 - side], 160.0)
            if door.distance_to(centre) < 900.0 and bf.is_walkable(deck): points.append(deck)
    return points

## The first spawn slots of a combat room, where its robots stand.
func robot_slots(bf: Node, room: Dictionary) -> Array[Vector2]:
    var slots: Array[Vector2] = []
    bf.call("begin_encounter", room)
    for i in range(BODY_SLOTS): slots.append(bf.call("enemy_spawn", i))
    bf.call("release")
    return slots

## A robot standing at `body`, as a planner obstacle for `actor` (as ground_obstacles
## inflates cover by the actor's collider).
func body_obstacle(actor: Node2D, body: Vector2) -> Rect2:
    var collider := actor.get_node("CollisionShape2D") as CollisionShape2D
    var offset := actor.to_local(collider.global_position)
    var extent := collider.shape.get_rect().size * collider.scale * actor.global_scale.abs() * 0.5 + Vector2(3, 3)
    return Rect2(body - Vector2.ONE * ROBOT_RADIUS - offset - extent, Vector2.ONE * ROBOT_RADIUS * 2.0 + extent * 2.0)

## Every point reachable from the first around the live cover and the robots standing
## on the other spawn slots. Without cover it checks the robots alone: a point they
## already shut off is not a cover's fault and is dropped from the room's route.
func passable(stage: StoryStage01, actor: OperatorActor, points: Array[Vector2], bodies: Array[Vector2], with_covers := true) -> bool:
    actor.global_position = points[0]
    var covers: Array[Rect2] = []
    if with_covers:
        for rect in NAV.ground_obstacles(actor): covers.append(rect.grow(LANE_MARGIN))
    for index in range(1, points.size()):
        var obstacles := covers.duplicate()
        for body in bodies:
            if body.distance_to(points[index]) > 1.0: obstacles.append(body_obstacle(actor, body).grow(LANE_MARGIN))
        var start := NAV._free_goal(actor, points[0], obstacles)
        var goal := NAV._free_goal(actor, points[index], obstacles)
        if not start.is_finite() or not goal.is_finite(): return false
        actor.global_position = start
        if NAV._clear_ground(actor, start, goal, obstacles): continue
        if NAV.new()._plan(actor, start, goal, obstacles).is_empty(): return false
    return true

## JSON parsing turns every number into a float; restore the whole numbers.
static func _whole_numbers(value: Variant) -> Variant:
    if value is Dictionary:
        var out := {}
        for key in value: out[key] = _whole_numbers(value[key])
        return out
    if value is Array:
        return (value as Array).map(func(item: Variant) -> Variant: return _whole_numbers(item))
    if value is float and is_equal_approx(value, roundf(value)) and absf(value) < 1e9: return int(value)
    return value

func run() -> void:
    var write := "--write" in OS.get_cmdline_user_args()
    var only_mission := ""
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): only_mission = arg.trim_prefix("--mission=")
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PROPS))
    var layouts: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/visual/site7_battle_layouts.json")).missions
    for mission_id: String in config.missions:
        if not only_mission.is_empty() and mission_id != only_mission: continue
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = mission_id
        stage.battle_preview = true
        root.add_child(stage)
        for i in range(12): await process_frame; await physics_frame
        var bf: Node = stage.battlefield
        var actor := stage.squad.get_active_operator()
        for other in stage.squad.operators: other.set_physics_process(false)
        var entries: Array = stage.get_node("EnvironmentProps").entries
        for entry: Dictionary in entries: entry.prop.set_active(true)
        var rows_by_room: Dictionary = config.missions[mission_id]
        var rooms: Dictionary = {}
        for room: Dictionary in stage.main_route + stage.optional_rooms: rooms[str(room.id)] = room
        var contexts: Dictionary = {}
        for entry: Dictionary in entries:
            var room: Dictionary = rooms[entry.room_id]
            var layout: bool = (layouts.get(mission_id, {}) as Dictionary).has(entry.room_id)
            if not contexts.has(entry.room_id):
                var bodies: Array[Vector2] = []
                if layout: bodies = robot_slots(bf, room)
                var route := route_points(stage, bf, room, layout)
                var reachable: Array[Vector2] = [route[0]]
                for index in range(1, route.size()):
                    if passable(stage, actor, [route[0], route[index]] as Array[Vector2], bodies, false): reachable.append(route[index])
                    else: print("SETTLE_SKIP %s %s route point %s is shut off by robots alone" % [mission_id, entry.room_id, route[index]])
                contexts[entry.room_id] = {"layout": layout, "clear": keep_clear_points(stage, bf, room, layout), "route": reachable, "bodies": bodies}
        var valid := func(entry: Dictionary) -> bool:
            var prop: Node2D = entry.prop
            var context: Dictionary = contexts[entry.room_id]
            var clear_points: Array = context.clear
            var shape := footprint(prop)
            if not on_floor(bf, shape): return false
            for pair in clear_points:
                if distance_to_shape(pair[0], shape) < float(pair[1]): return false
            # A spawn inside a cover's planner rectangle (footprint box grown
            # by the body; CINDER is ~4 px wider than an operator) leaves no
            # clear ground lane to it: charges stall. Keep spawns outside.
            if context.layout:
                actor.global_position = prop.global_position
                var box := Rect2(shape[0], Vector2.ZERO)
                for p in shape: box = box.expand(p)
                for obstacle in NAV.ground_obstacles(actor):
                    if not obstacle.grow(-1.0).intersects(box): continue
                    for pair in clear_points:
                        if obstacle.grow(12.0).has_point(pair[0]): return false
            for other: Dictionary in entries:
                if other == entry or other.room_id != entry.room_id or not other.prop.active: continue
                var other_shape := footprint(other.prop)
                for p in shape:
                    if Geometry2D.is_point_in_polygon(p, other_shape): return false
                for p in other_shape:
                    if Geometry2D.is_point_in_polygon(p, shape): return false
            return passable(stage, actor, context.route, context.bodies)
        # Covers that fail can block each other (a barrier across a corridor leaves
        # no valid spot for the crate behind it), so every failing cover is lifted
        # first and then placed back one at a time against the covers already settled.
        var failing: Array[Dictionary] = []
        for entry: Dictionary in entries:
            if not valid.call(entry): failing.append(entry)
        for entry in failing: entry.prop.set_active(false)
        for entry in failing:
            var prop: Node2D = entry.prop
            var plate: Sprite2D = entry.plate
            prop.set_active(true)
            var original := prop.global_position
            var span := plate.texture.get_size() * plate.scale
            var chosen := original if valid.call(entry) else Vector2.INF
            if not chosen.is_finite():
                var candidates: Array[Vector2] = []
                for ix in range(4, 97, 2):
                    for iy in range(4, 97, 2):
                        candidates.append(plate.global_position + (Vector2(ix, iy) / 100.0 - Vector2.ONE * 0.5) * span)
                candidates.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.distance_squared_to(original) < b.distance_squared_to(original))
                for candidate in candidates:
                    if candidate.distance_to(original) > 700.0: break
                    prop.global_position = candidate
                    if valid.call(entry): chosen = candidate; break
            if chosen == original: continue
            var row := {"mission": mission_id, "room": entry.room_id, "asset": entry.asset}
            for data_row: Dictionary in rows_by_room[entry.room_id]:
                if data_row.asset != entry.asset: continue
                var old_point: Array = data_row.point
                var expected := plate.global_position + (Vector2(float(old_point[0]), float(old_point[1])) - Vector2.ONE * 0.5) * span
                if expected.distance_to(original) > 2.0: continue
                row["from"] = old_point
                if chosen.is_finite():
                    var normalized := (chosen - plate.global_position) / span + Vector2.ONE * 0.5
                    data_row.point = [snappedf(normalized.x, 0.001), snappedf(normalized.y, 0.001)]
                    row["to"] = data_row.point
                    row["moved_px"] = snappedf(chosen.distance_to(original), 0.1)
                else:
                    row["error"] = "NO_VALID_SPOT"
                break
            if not chosen.is_finite(): prop.global_position = original
            report.append(row)
            print("SETTLE ", JSON.stringify(row))
        stage.queue_free()
        for i in range(4): await process_frame
    if write:
        var file := FileAccess.open(PROPS, FileAccess.WRITE)
        # Keep the file's key order and whole numbers, so a write only changes points.
        file.store_string(JSON.stringify(_whole_numbers(config), "  ", false) + "\n")
        file.close()
    print("SETTLE_DONE moved=%d %s" % [report.size(), "WRITTEN" if write else "DRY"])
    quit(0)
