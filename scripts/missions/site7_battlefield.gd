extends Node

## One ground graph spans the entire mission. An encounter selects local spawn
## geometry only; it never replaces the traversable map with one room polygon.
const LAYOUTS := "res://data/visual/site7_battle_layouts.json"
# Floor traced from each painted plate. Replaces the generic room/connector
# quads, which let actors walk over machinery and blocked painted deck.
const PLATE_FLOORS := "res://data/visual/site7_plate_floors.json"
# Operator collision is a 14px-radius capsule offset above the root.  Keep the
# root a little farther from the painted room edge so the torso cannot look as
# though it has crossed a wall before the physics boundary stops it.
const ACTOR_EDGE_CLEARANCE := 20.0
const DEPTH := preload("res://scripts/missions/site7_depth.gd")
var stage: Node2D
var art: Node2D
var active := false
var room_id := ""
var polygon := PackedVector2Array()
var _walk_polygon := PackedVector2Array()
var _layout: Dictionary = {}
var _catalog: Dictionary = {}
var _plate: Sprite2D
var _center := Vector2.ZERO
var world_ready := false
var _world_polygons: Array[PackedVector2Array] = []
var _world_centers: Array[Vector2] = []
var _route_segments: Array[PackedVector2Array] = []
var _plate_floors: Dictionary = {}
var _connector_shapes: Dictionary = {}
var _room_shapes: Dictionary = {}
var join_gaps: Dictionary = {}
## Connector index -> [deck door at the route's first room, deck door at its second].
var connector_doors: Dictionary = {}
var _route_half_widths := PackedFloat32Array()
# Painted floor of each plate (before the actor clearance inset), for the art
# layer's floor masks.
var _raw_floors: Dictionary = {}
# The world layout (site7_world_layout.gd) runs every connector deck into both
# rooms' painted floors, so routes between rooms are navigation-only (width 0)
# and add no walkable ground; a 100 px capsule from each combat room's centre
# used to let actors cross painted walls. A deck that missed its room would get
# a narrow bridge instead; the layout tool rejects such a layout.
const ROUTE_HALF_WIDTH := 0.0
const BRIDGE_HALF_WIDTH := 48.0
const MAIN_CONNECTOR_FLOOR := [[0.02,0.62],[0.98,0.04],[0.98,0.32],[0.02,0.94]]
const BRANCH_CONNECTOR_FLOOR := [[0.08,0.72],[0.67,0.18],[0.93,0.38],[0.35,0.90]]

func _ready() -> void:
    stage = get_parent()
    art = stage.get_node("RoomArtLayer")
    _catalog = JSON.parse_string(FileAccess.get_file_as_string(LAYOUTS))
    var floors: Variant = JSON.parse_string(FileAccess.get_file_as_string(PLATE_FLOORS)) if FileAccess.file_exists(PLATE_FLOORS) else {}
    _plate_floors = (floors as Dictionary).get("plates", {}) if floors is Dictionary else {}
    process_priority = 160
    call_deferred("_build_world_geometry")

func _build_world_geometry() -> void:
    if world_ready or stage == null or art == null: return
    if stage.main_route.is_empty(): return
    if art.call("get_room_plate", str(stage.main_route[0].id)) == null:
        art.call("_load_manifest")
    var mission_layouts: Dictionary = _catalog.get("missions", {}).get(stage.mission_id, {})
    for room: Dictionary in stage.main_route + stage.optional_rooms:
        var plate := art.call("get_room_plate", str(room.id)) as Sprite2D
        if plate == null: continue
        var authored: Dictionary = mission_layouts.get(str(room.id), {})
        var points: Array = authored.get("floor", _plate_floor(plate, [[0.17,0.65],[0.65,0.25],[0.88,0.43],[0.42,0.84]]))
        # A room plate's border band is drawn over by the plates after it (the art
        # layer's floor masks fade out there), so its floor stops where they take
        # over: a floor running to the plate edge let actors walk onto a deck's
        # painted railing. Connector decks, drawn last, own their ends.
        _room_shapes[str(room.id)] = _append_walk_polygon(plate, points, Site7RoomArtLayer.MASK_EDGE_FADE * 0.5)
    # Connector art has a wide diagonal deck, not a 200px horizontal strip.
    # Its painted floor participates in the same collision graph as rooms.
    for index in range(7):
        var connector := art.call("get_connector_plate", index) as Sprite2D
        if connector:
            _connector_shapes[index] = _append_walk_polygon(connector, _plate_floor(connector, MAIN_CONNECTOR_FLOOR if index < 5 else BRANCH_CONNECTOR_FLOOR))
    for index in range(stage.main_route.size() - 1):
        _add_connector_route(stage.main_route[index], stage.main_route[index + 1], index)
    for index in range(stage.optional_rooms.size()):
        _add_connector_route(stage.call("branch_parent", index), stage.optional_rooms[index], index + 5)
    world_ready = not _world_polygons.is_empty() and not _route_segments.is_empty()
    if world_ready:
        _collect_corner_nodes()
        if art.has_method("apply_floor_masks"): art.call("apply_floor_masks", _raw_floors, connector_doors)
        stage.call("_apply_progress_bounds")

## Adds a plate's floor, kept `edge_band` (fraction of the plate size) inside its
## border, as walk polygons; returns the largest.
func _append_walk_polygon(plate: Sprite2D, points: Array, edge_band: float = 0.0) -> PackedVector2Array:
    var shape := PackedVector2Array()
    for point: Array in points:
        shape.append(_plate_point(plate, Vector2(float(point[0]), float(point[1]))))
    _raw_floors[plate] = shape
    var pieces: Array[PackedVector2Array] = [shape]
    if edge_band > 0.0:
        var low := _plate_point(plate, Vector2.ONE * edge_band)
        var high := _plate_point(plate, Vector2.ONE * (1.0 - edge_band))
        var inner := Rect2(low, Vector2.ZERO).expand(high)
        var clipped := Geometry2D.intersect_polygons(shape, PackedVector2Array([inner.position, Vector2(inner.end.x, inner.position.y), inner.end, Vector2(inner.position.x, inner.end.y)]))
        pieces.clear()
        for piece in clipped:
            if Geometry2D.is_polygon_clockwise(piece) != Geometry2D.is_polygon_clockwise(shape): continue
            pieces.append(piece)
        if pieces.is_empty(): pieces = [shape]
    var largest := PackedVector2Array()
    var largest_area := -1.0
    for piece in pieces:
        var inset := Geometry2D.offset_polygon(piece, -ACTOR_EDGE_CLEARANCE, Geometry2D.JOIN_MITER)
        for walk_shape in (inset if not inset.is_empty() else [piece]):
            if Geometry2D.is_polygon_clockwise(walk_shape) != Geometry2D.is_polygon_clockwise(piece): continue
            _world_polygons.append(walk_shape)
            var centroid := Vector2.ZERO
            for vertex in walk_shape: centroid += vertex
            _world_centers.append(centroid / float(walk_shape.size()))
            var box := Rect2(walk_shape[0], Vector2.ZERO)
            for vertex in walk_shape: box = box.expand(vertex)
            if box.get_area() > largest_area: largest_area = box.get_area(); largest = walk_shape
    return largest

func _add_connector_route(a: Dictionary, b: Dictionary, index: int) -> void:
    var start := Vector2(float(a.x), float(a.y))
    var finish := Vector2(float(b.x), float(b.y))
    var plate := art.call("get_connector_plate", index) as Sprite2D
    if plate == null:
        _add_route_segment(start, finish)
        return
    # A main deck leaves `a` at its image-left end; a mirrored branch deck at
    # its image-right end, which the mirror puts on the world's upper left. A
    # reversed deck (a descending route) meets `a` at the other end.
    var ends := _deck_end_points(plate)
    var from_left := (plate.scale.x > 0.0) != bool(plate.get_meta("reverse", false))
    var near_a: Vector2 = ends[0] if from_left else ends[1]
    var near_b: Vector2 = ends[1] if from_left else ends[0]
    var deck: PackedVector2Array = _connector_shapes.get(index, PackedVector2Array())
    var door_a := _door(_room_shapes.get(str(a.id), PackedVector2Array()), deck, _onto_deck(near_a, index), start)
    var door_b := _door(_room_shapes.get(str(b.id), PackedVector2Array()), deck, _onto_deck(near_b, index), finish)
    join_gaps["%d_a" % index] = door_a[0].distance_to(door_a[1])
    join_gaps["%d_b" % index] = door_b[0].distance_to(door_b[1])
    connector_doors[index] = [door_a[1], door_b[1]]
    # Room centre -> door, along the deck, door -> next room centre. Where the
    # floors overlap each door is one node and the route only guides navigation.
    _add_route_segment(start, door_a[0])
    if door_a[0] != door_a[1]: _add_route_segment(door_a[0], door_a[1], BRIDGE_HALF_WIDTH)
    _add_route_segment(door_a[1], door_b[1])
    if door_b[0] != door_b[1]: _add_route_segment(door_b[1], door_b[0], BRIDGE_HALF_WIDTH)
    _add_route_segment(door_b[0], finish)

## World midpoints of a connector deck's image-left and image-right ends.
func _deck_end_points(plate: Sprite2D) -> Array[Vector2]:
    var points: Array = _plate_floor(plate, MAIN_CONNECTOR_FLOOR)
    var low := INF
    var high := -INF
    for point: Array in points:
        low = minf(low, float(point[0]))
        high = maxf(high, float(point[0]))
    var sums: Array[Vector2] = [Vector2.ZERO, Vector2.ZERO]
    var counts := [0, 0]
    for point: Array in points:
        var world := _plate_point(plate, Vector2(float(point[0]), float(point[1])))
        if float(point[0]) <= low + 0.05: sums[0] += world; counts[0] += 1
        if float(point[0]) >= high - 0.05: sums[1] += world; counts[1] += 1
    return [sums[0] / float(maxi(1, counts[0])), sums[1] / float(maxi(1, counts[1]))]

## Shortest crossing between a room floor and its connector deck near the
## deck's painted opening: [room-side node, deck-side node]. Overlapping floors
## share one node; a gap is spanned by a single narrow route bridge.
func _door(room: PackedVector2Array, deck: PackedVector2Array, deck_hint: Vector2, room_center: Vector2) -> Array[Vector2]:
    if room.size() < 3 or deck.size() < 3: return [room_center, deck_hint]
    var overlap := Geometry2D.intersect_polygons(room, deck)
    if not overlap.is_empty():
        var best := Vector2.INF
        for piece in overlap:
            var centroid := _centroid(piece)
            if not best.is_finite() or centroid.distance_squared_to(deck_hint) < best.distance_squared_to(deck_hint): best = centroid
        return [best, best]
    var deck_point := deck_hint
    var room_point := _closest_on(room, deck_point)
    for _pass in range(3):
        deck_point = _closest_on(deck, room_point)
        room_point = _closest_on(room, deck_point)
    return [room_point.move_toward(_centroid(room), 24.0), deck_point.move_toward(_centroid(deck), 24.0)]

static func _closest_on(shape: PackedVector2Array, point: Vector2) -> Vector2:
    if Geometry2D.is_point_in_polygon(point, shape): return point
    var best := point
    var best_d2 := INF
    for edge in range(shape.size()):
        var candidate := Geometry2D.get_closest_point_to_segment(point, shape[edge], shape[(edge + 1) % shape.size()])
        var d2 := point.distance_squared_to(candidate)
        if d2 < best_d2: best_d2 = d2; best = candidate
    return best

static func _centroid(shape: PackedVector2Array) -> Vector2:
    var sum := Vector2.ZERO
    for vertex in shape: sum += vertex
    return sum / float(maxi(1, shape.size()))

func _plate_floor(plate: Sprite2D, fallback: Array) -> Array:
    var row: Variant = _plate_floors.get(str(plate.get_meta("asset", "")), {})
    return (row as Dictionary).get("floor", fallback) if row is Dictionary else fallback

## Keep a connector's door node on its traced deck so the route bridge does
## not start inside the machinery that frames the painted corridor.
func _onto_deck(point: Vector2, index: int) -> Vector2:
    var shape: PackedVector2Array = _connector_shapes.get(index, PackedVector2Array())
    if shape.size() < 3 or Geometry2D.is_point_in_polygon(point, shape): return point
    var best := point
    var best_d2 := INF
    for edge in range(shape.size()):
        var candidate := Geometry2D.get_closest_point_to_segment(point, shape[edge], shape[(edge + 1) % shape.size()])
        var d2 := point.distance_squared_to(candidate)
        if d2 < best_d2: best_d2 = d2; best = candidate
    var centroid := Vector2.ZERO
    for vertex in shape: centroid += vertex
    return best.move_toward(centroid / float(shape.size()), 24.0)

func _add_route_segment(a: Vector2, b: Vector2, half_width: float = ROUTE_HALF_WIDTH) -> void:
    _route_segments.append(PackedVector2Array([a,b]))
    _route_half_widths.append(half_width)

func navigation_waypoints() -> PackedVector2Array:
    var result := PackedVector2Array()
    for segment in _route_segments:
        # A full-length authored deck is about 1925 px between thresholds.
        # Its old single midpoint left two >900 px edges, beyond the cover
        # planner's MAX_GRAPH_EDGE, when no nearby floor corner bridged them.
        var pieces := maxi(2, ceili(segment[0].distance_to(segment[1]) / 760.0))
        for step in range(pieces + 1):
            var point := segment[0].lerp(segment[1], float(step) / float(pieces))
            if not result.has(point): result.append(point)
    # Traced floors bend around painted machinery. A straight line between two
    # route nodes can leave such a floor, so the planner also needs the floor's
    # inner (reflex) corners: the classic visibility-graph node set.
    result.append_array(_corner_nodes)
    return result

var _corner_nodes := PackedVector2Array()

func _collect_corner_nodes() -> void:
    _corner_nodes.clear()
    for shape in _world_polygons:
        var clockwise := Geometry2D.is_polygon_clockwise(shape)
        var count := shape.size()
        for index in range(count):
            var previous := shape[(index + count - 1) % count]
            var vertex := shape[index]
            var following := shape[(index + 1) % count]
            var turn := (vertex - previous).cross(following - vertex)
            var reflex := turn > 0.0 if clockwise else turn < 0.0
            if not reflex: continue
            var bisector := ((previous - vertex).normalized() + (following - vertex).normalized())
            if bisector.length_squared() < 0.0001: bisector = (following - previous).orthogonal()
            bisector = bisector.normalized()
            # Keep the node 10 px inside the corner. Corners that another floor
            # also covers are kept: they still bend routes around the union's
            # joins, and CoverNavigation caches their visibility.
            var inner := vertex - bisector * 10.0
            if not Geometry2D.is_point_in_polygon(inner, shape): inner = vertex + bisector * 10.0
            if not is_walkable(inner): continue
            _corner_nodes.append(inner)

func _plate_point(plate: Sprite2D, point: Vector2) -> Vector2:
    return plate.to_global((point - Vector2.ONE * 0.5) * plate.texture.get_size())

func begin_encounter(room: Dictionary) -> void:
    release()
    room_id = str(room.id)
    _layout = _catalog.get("missions", {}).get(stage.mission_id, {}).get(room_id, {})
    if _layout.is_empty(): return
    _plate = art.call("get_room_plate", room_id)
    if _plate == null: return
    _center = Vector2.ZERO
    for point: Array in _layout.floor:
        var world := normalized_to_world(Vector2(float(point[0]), float(point[1])))
        polygon.append(world)
        _center += world
    _center /= float(polygon.size())
    # A true edge offset, not radial vertex movement (which gives inconsistent
    # clearance on diagonal walls). All authored floors are simple polygons.
    var inset := Geometry2D.offset_polygon(polygon, -ACTOR_EDGE_CLEARANCE, Geometry2D.JOIN_MITER)
    if not inset.is_empty(): _walk_polygon = inset[0]
    else: _walk_polygon = polygon
    active = polygon.size() >= 3

func release() -> void:
    active = false
    polygon.clear()
    _walk_polygon.clear()
    _spawn_points.clear()

func normalized_to_world(point: Vector2) -> Vector2:
    return _plate_point(_plate, point)

func constrain(point: Vector2) -> Vector2:
    if not world_ready or is_walkable(point): return point
    var best := point
    var best_d2 := INF
    for index in range(_world_polygons.size()):
        var shape := _world_polygons[index]
        for edge in range(shape.size()):
            var a := shape[edge]
            var b := shape[(edge + 1) % shape.size()]
            var on_edge := Geometry2D.get_closest_point_to_segment(point, a, b)
            # Step off the edge along its inward normal. Traced floors are
            # concave, where "toward the centroid" can leave the polygon.
            var normal := (b - a).orthogonal().normalized() * 2.0
            var candidate := on_edge + normal
            if not Geometry2D.is_point_in_polygon(candidate, shape):
                candidate = on_edge - normal
                if not Geometry2D.is_point_in_polygon(candidate, shape):
                    candidate = on_edge.move_toward(_world_centers[index], 2.0)
            var d2 := point.distance_squared_to(candidate)
            if d2 < best_d2: best_d2 = d2; best = candidate
    for segment_index in range(_route_segments.size()):
        if _route_half_widths[segment_index] <= 0.0: continue
        var segment := _route_segments[segment_index]
        var axis := Geometry2D.get_closest_point_to_segment(point, segment[0], segment[1])
        var delta := point - axis
        var candidate := axis + delta.normalized() * (_route_half_widths[segment_index] - 0.5) if delta.length_squared() > 0.001 else axis
        var d2 := point.distance_squared_to(candidate)
        if d2 < best_d2: best_d2 = d2; best = candidate
    return best

func contains(point: Vector2) -> bool:
    return is_walkable(point)

## Bounding boxes of the floor polygons and route capsules, 2 px wider than the shapes.
## A point or segment outside a box cannot touch that shape, so the exact tests below
## skip it; they are the answers' whole cost on the web build (thousands per tick).
var _world_boxes: Array[Rect2] = []
var _route_boxes: Array[Rect2] = []

func _ensure_boxes() -> void:
    if _world_boxes.size() == _world_polygons.size() and _route_boxes.size() == _route_segments.size(): return
    _world_boxes.clear()
    for shape in _world_polygons:
        var box := Rect2(shape[0], Vector2.ZERO) if not shape.is_empty() else Rect2()
        for vertex in shape: box = box.expand(vertex)
        _world_boxes.append(box.grow(2.0))
    _route_boxes.clear()
    for segment_index in range(_route_segments.size()):
        var segment := _route_segments[segment_index]
        _route_boxes.append(Rect2(segment[0], Vector2.ZERO).expand(segment[1]).grow(_route_half_widths[segment_index] + 2.0))

func is_walkable(point: Vector2) -> bool:
    if not world_ready: return false
    _ensure_boxes()
    for index in range(_world_polygons.size()):
        if _world_boxes[index].has_point(point) and Geometry2D.is_point_in_polygon(point, _world_polygons[index]): return true
    for segment_index in range(_route_segments.size()):
        if _route_half_widths[segment_index] <= 0.0 or not _route_boxes[segment_index].has_point(point): continue
        var segment := _route_segments[segment_index]
        var half_width := _route_half_widths[segment_index]
        if point.distance_squared_to(Geometry2D.get_closest_point_to_segment(point, segment[0], segment[1])) <= half_width * half_width:
            return true
    return false

## True when the whole segment a-b lies on walkable floor. Exact rather than sampled: the
## segment is cut wherever it crosses a floor-polygon edge or a route capsule's rim, and each
## piece is tested at its midpoint. A 16px sampler let route edges clip the corner of a floor
## hole, and actors then flipped between two plans at that corner forever. Pieces shorter
## than SEAM_TOLERANCE are seams between abutting shapes, not holes, and pass.
const SEAM_TOLERANCE := 2.0
func segment_walkable(a: Vector2, b: Vector2) -> bool:
    if not world_ready: return false
    var d := b - a
    var length_sq := d.length_squared()
    if length_sq < 0.0001: return is_walkable(a)
    var cuts: Array[float] = [0.0, 1.0]
    _ensure_boxes()
    var box := Rect2(a, Vector2.ZERO).expand(b)
    for index in range(_world_polygons.size()):
        if not box.intersects(_world_boxes[index], true): continue
        var shape := _world_polygons[index]
        var count := shape.size()
        for i in range(count):
            var hit = Geometry2D.segment_intersects_segment(a, b, shape[i], shape[(i + 1) % count])
            if hit != null: cuts.append((hit - a).dot(d) / length_sq)
    for segment_index in range(_route_segments.size()):
        if _route_half_widths[segment_index] <= 0.0 or not box.intersects(_route_boxes[segment_index], true): continue
        var p := _route_segments[segment_index][0]
        var q := _route_segments[segment_index][1]
        var radius := _route_half_widths[segment_index]
        for end: Vector2 in [p, q]:
            var t := Geometry2D.segment_intersects_circle(a, b, end, radius)
            if t >= 0.0: cuts.append(t)
            var back := Geometry2D.segment_intersects_circle(b, a, end, radius)
            if back >= 0.0: cuts.append(1.0 - back)
        if p.distance_squared_to(q) > 0.0001:
            var side := (q - p).orthogonal().normalized() * radius
            for offset: Vector2 in [side, -side]:
                var hit = Geometry2D.segment_intersects_segment(a, b, p + offset, q + offset)
                if hit != null: cuts.append((hit - a).dot(d) / length_sq)
    cuts.sort()
    var min_piece := SEAM_TOLERANCE / sqrt(length_sq)
    for i in range(cuts.size() - 1):
        if cuts[i + 1] - cuts[i] < min_piece: continue
        if not is_walkable(a + d * ((cuts[i] + cuts[i + 1]) * 0.5)): return false
    return is_walkable(a) and is_walkable(b)

func squad_spawn(index: int) -> Vector2:
    var spawn: Array = _layout.get("spawn", [0.43,0.63] if str(_layout.get("kind", "")) == "boss" else [0.47,0.60])
    var anchor := Vector2(float(spawn[0]),float(spawn[1]))
    return constrain(normalized_to_world(anchor) + SquadController.FORMATION_OFFSETS[index])

func objective_point() -> Vector2:
    var point: Array = _layout.get("objective", [0.60,0.56])
    return constrain(normalized_to_world(Vector2(float(point[0]),float(point[1]))))

const AUTHORED_ENEMY_SPAWNS: Array[Vector2] = [Vector2(0.69,0.53), Vector2(0.77,0.56), Vector2(0.61,0.58)]
const BOSS_ANCHOR := Vector2(0.64,0.48)
const SPAWN_SEPARATION := 96.0
const SPAWN_SQUAD_CLEARANCE := 250.0
const SPAWN_COVER_CLEARANCE := 44.0
var _spawn_points: Array[Vector2] = []

## Encounter spawn slot `index` (a running count across all waves of the
## encounter). Slots 0-2 keep the authored points (boss rooms: the boss anchor
## first; a room entered from the far side lists its own "enemy_spawns" and
## "boss_anchor"); further slots are spread over this room's floor away from the squad,
## other slots and cover, so larger waves never stack on one point.
func enemy_spawn(index: int) -> Vector2:
    if _spawn_points.is_empty(): _build_spawn_points()
    if _spawn_points.is_empty(): return constrain(normalized_to_world(AUTHORED_ENEMY_SPAWNS[0]))
    return _spawn_points[index % _spawn_points.size()]

func _build_spawn_points() -> void:
    _spawn_points.clear()
    if _plate == null or polygon.size() < 3: return
    var boss := str(_layout.get("kind", "")) == "boss"
    var seeds: Array[Vector2] = []
    if boss:
        var anchor: Array = _layout.get("boss_anchor", [BOSS_ANCHOR.x, BOSS_ANCHOR.y])
        seeds.append(Vector2(float(anchor[0]), float(anchor[1])))
        # A long corridor boss can place its support robots on the approach
        # side. Otherwise farthest-point sampling may choose the exit apron
        # and make that narrow mouth impassable while the boss is alive.
        for point: Array in _layout.get("enemy_spawns", []):
            seeds.append(Vector2(float(point[0]), float(point[1])))
    elif _layout.has("enemy_spawns"):
        for point: Array in _layout.enemy_spawns: seeds.append(Vector2(float(point[0]), float(point[1])))
    else: seeds.append_array(AUTHORED_ENEMY_SPAWNS)
    for seed in seeds: _spawn_points.append(constrain(normalized_to_world(seed)))
    var squad := squad_spawn(0)
    var covers: Array[PackedVector2Array] = []
    for cover in stage.get_tree().get_nodes_in_group("sable_environment_cover"):
        var footprint := PackedVector2Array()
        for g in cover.ground: footprint.append(cover.to_global(g))
        covers.append(footprint)
    var candidates: Array[Vector2] = []
    for ix in range(6, 95, 3):
        for iy in range(6, 95, 3):
            var point := normalized_to_world(Vector2(ix, iy) / 100.0)
            if not Geometry2D.is_point_in_polygon(point, _walk_polygon) or not is_walkable(point): continue
            if point.distance_to(squad) < SPAWN_SQUAD_CLEARANCE: continue
            var clear := true
            for footprint in covers:
                if Geometry2D.is_point_in_polygon(point, footprint): clear = false; break
                for edge in range(footprint.size()):
                    if point.distance_to(Geometry2D.get_closest_point_to_segment(point, footprint[edge], footprint[(edge + 1) % footprint.size()])) < SPAWN_COVER_CLEARANCE:
                        clear = false; break
                if not clear: break
            if clear: candidates.append(point)
    # Farthest-point sampling, biased away from the squad: an even spread over
    # the enemy side of the room, deterministic for a given layout.
    while _spawn_points.size() < 10 and not candidates.is_empty():
        var best := -1
        var best_score := -INF
        for i in range(candidates.size()):
            var nearest := INF
            for placed in _spawn_points: nearest = minf(nearest, candidates[i].distance_to(placed))
            if nearest < SPAWN_SEPARATION: continue
            var score := minf(nearest, 320.0) + 0.35 * candidates[i].distance_to(squad)
            if score > best_score: best_score = score; best = i
        if best < 0: break
        var chosen := candidates[best]
        candidates.remove_at(best)
        # Only keep slots with a real ground route to the squad around cover.
        if _reaches(chosen, squad): _spawn_points.append(chosen)

func _reaches(from: Vector2, to: Vector2) -> bool:
    if stage == null or stage.squad == null or stage.squad.operators.is_empty(): return true
    var probe: Node2D = stage.squad.operators[0]
    var NAV := preload("res://scripts/combat/cover_navigation.gd")
    var obstacles := NAV.ground_obstacles(probe, from)
    for rect in obstacles:
        if rect.has_point(from): return false
    if NAV._clear_ground(probe, from, to, obstacles): return true
    return not NAV.new()._plan(probe, from, to, obstacles).is_empty()

const HAZARD_SQUAD_CLEARANCE := 90.0
const HAZARD_SPAWN_CLEARANCE := 30.0
## First-wave spawn slots kept off hazards (later slots may land beside one; robots take its hit too).
const HAZARD_PROTECTED_SPAWNS := 4

## `count` floor points for room hazards of `radius` (a floor ellipse, see ZoneHazard):
## the whole ellipse on this room's walkable floor and off cover, clear of the squad start
## and the first-wave enemy spawn slots, spread apart and nearest the contested middle of the room.
## Deterministic for a given layout.
func hazard_points(count: int, radius: float, reserved: Array = [], circular_bounds := false) -> Array[Vector2]:
    var result: Array[Vector2] = []
    if _plate == null or polygon.size() < 3 or count <= 0: return result
    if _spawn_points.is_empty(): _build_spawn_points()
    var squad: Array[Vector2] = [squad_spawn(0), squad_spawn(1), squad_spawn(2)]
    var enemy_mid := Vector2.ZERO
    for point in _spawn_points: enemy_mid += point
    enemy_mid = enemy_mid / float(_spawn_points.size()) if not _spawn_points.is_empty() else squad[0]
    var middle := squad[0].lerp(enemy_mid, 0.5)
    var covers: Array[PackedVector2Array] = []
    for cover in stage.get_tree().get_nodes_in_group("sable_environment_cover"):
        var footprint := PackedVector2Array()
        for g in cover.ground: footprint.append(cover.to_global(g))
        covers.append(footprint)
    # A rail reserves its real rectangle's bounding circle. Mixed declarations
    # share reservations, so a second row cannot reuse the first row's points.
    var shape := Vector2(radius, radius if circular_bounds else radius * ZoneHazard.FLOOR_RATIO)
    var candidates: Array[Vector2] = []
    for ix in range(6, 95, 2):
        for iy in range(6, 95, 2):
            var point := normalized_to_world(Vector2(ix, iy) / 100.0)
            if _hazard_fits(point, shape, squad, radius, covers): candidates.append(point)
    candidates.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.distance_squared_to(middle) < b.distance_squared_to(middle))
    for point in candidates:
        if result.size() >= count: break
        var spread := true
        for placed in result:
            if point.distance_to(placed) < radius * 2.6: spread = false; break
        for other: Dictionary in reserved:
            if point.distance_to(other.point as Vector2) < maxf(radius, float(other.radius)) * 2.6: spread = false; break
        if spread: result.append(point)
    return result

func _hazard_fits(point: Vector2, shape: Vector2, squad: Array[Vector2], radius: float, covers: Array[PackedVector2Array]) -> bool:
    for start in squad:
        if point.distance_to(start) < radius + HAZARD_SQUAD_CLEARANCE: return false
    for spawn in _spawn_points.slice(0, HAZARD_PROTECTED_SPAWNS):
        if point.distance_to(spawn) < radius + HAZARD_SPAWN_CLEARANCE: return false
    var rim := PackedVector2Array([point])
    for i in range(16): rim.append(point + Vector2.RIGHT.rotated(TAU * i / 16.0) * shape)
    for sample in rim:
        if not Geometry2D.is_point_in_polygon(sample, _walk_polygon) or not is_walkable(sample): return false
        for footprint in covers:
            if Geometry2D.is_point_in_polygon(sample, footprint): return false
    for footprint in covers:
        for corner in footprint:
            if ((corner - point) / shape).length_squared() <= 1.0: return false
    return true

func debug_spawn_points() -> Array[Vector2]:
    if _spawn_points.is_empty(): _build_spawn_points()
    return _spawn_points.duplicate()

func opening_patrol_spawn(index: int) -> Vector2:
    # First-encounter scouts must be visible on the entry deck, not 2.7k px
    # away behind two screens of connector art. The heavy still guards R02.
    var entry := art.call("get_room_plate", str(stage.main_route[0].id)) as Sprite2D
    if entry == null:
        return enemy_spawn(index)
    var positions := [Vector2(0.62, 0.45), Vector2(0.77, 0.51)]
    return constrain(_plate_point(entry, positions[index % positions.size()]))

func _process(_delta: float) -> void:
    # Ground contact, not sibling creation order, determines body occlusion.
    var camera := stage.get_node_or_null("Camera2D") as Camera2D
    if camera: DEPTH.follow(camera.global_position.y)
    for actor in stage.squad.operators:
        _depth_actor(actor)
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node) and stage.is_ancestor_of(node):
            _depth_actor(node)
    for cover in get_tree().get_nodes_in_group("sable_environment_cover"):
        if cover.visible and stage.is_ancestor_of(cover): cover.z_index = DEPTH.z_for(cover.global_position.y)

func _depth_actor(actor: Node2D) -> void:
    actor.z_index = DEPTH.z_for(actor.global_position.y)
    var shadow := actor.get_node_or_null("GroundShadow") as Node2D
    if shadow:
        shadow.z_as_relative = false
        shadow.z_index = -50
    for name in ["MotionLabCharacterRuntime", "FastCharacterRuntime"]:
        var runtime := actor.get_node_or_null(name)
        if runtime and runtime.get("sprite"):
            (runtime.get("sprite") as Sprite2D).z_index = 0

func debug_contract() -> Dictionary:
    return {"active":active,"room_id":room_id,"vertices":polygon.size(),"world_polygon":Array(polygon),"actor_edge_clearance":ACTOR_EDGE_CLEARANCE,"body_depth_sort":true,"ground_before_gait_commit":true,"single_world":world_ready,"world_regions":_world_polygons.size(),"route_segments":_route_segments.size()}
