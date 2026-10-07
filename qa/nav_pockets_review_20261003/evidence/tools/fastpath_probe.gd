extends SceneTree
## The combat-query fast paths added for the web build (2026-09-25) must answer exactly
## as the code they replaced. On real mission floors, cover props and actors this checks
## bit for bit, against verbatim copies of the replaced code below:
## Site7Battlefield.is_walkable / segment_walkable (bounding-box rejection),
## CombatHitGeometry.hit_point (early miss), Site7EnvironmentProp.projectile_hit (point
## and alpha sample count), CoverNavigation.ground_obstacles (cached ground rects) and
## CoverNavigation._plan (cached battle-floor graph). The planner's pair-visibility cache
## depends on the order of earlier plans, so one plan sequence is replayed against a
## reference planner that keeps its own cache.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const HIT := preload("res://scripts/combat/combat_hit_geometry.gd")
const MISSIONS := ["MIS_CH01_01", "MIS_CH01_03", "MIS_CH01_05"]
const POINTS := 3000
const SEGMENTS := 2000
const RAYS_PER_PROP := 60
const PLANS_PER_ACTOR := 36

var failures: Array[String] = []
var checks := 0
var totals := {}

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _check_hit_point_cases()
    for mission in MISSIONS:
        await _check_mission(mission)
    print("COMBAT_QUERY_FASTPATH totals ", JSON.stringify(totals))
    if failures.is_empty():
        print("COMBAT_QUERY_FASTPATH_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures.slice(0, 40): printerr("FAIL: ", failure)
        printerr("COMBAT_QUERY_FASTPATH_SMOKE: FAIL (%d of %d checks)" % [failures.size(), checks])
        quit(1)

func _count(key: String, amount: int = 1) -> void:
    totals[key] = int(totals.get(key, 0)) + amount

func _same(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)

# --- hit_point ------------------------------------------------------------------

func _check_hit_point_cases() -> void:
    var rng := RandomNumberGenerator.new()
    rng.seed = 20260925
    var rects: Array[Rect2] = [Rect2(10, 20, 40, 30), Rect2(0, 0, 0, 0), Rect2(5, 5, 0.3, 0.3),
        Rect2(-50, -50, 100, 1), Rect2(100, 100, 1, 100)]
    for i in range(60):
        rects.append(Rect2(rng.randf_range(-300, 300), rng.randf_range(-300, 300), rng.randf_range(0, 160), rng.randf_range(0, 160)))
    for rect in rects:
        var probes: Array[Vector2] = [rect.position, rect.end, Vector2(rect.end.x, rect.position.y), rect.get_center(),
            rect.position - Vector2(1.0, 0.0), rect.end + Vector2(0.5, 0.5), rect.end + Vector2(1.0, 1.0), rect.position - Vector2(1.5, 1.5)]
        for i in range(40):
            probes.append(rect.get_center() + Vector2(rng.randf_range(-260, 260), rng.randf_range(-260, 260)))
        for a in probes:
            for b in [a, a + Vector2(rng.randf_range(-200, 200), 0), a + Vector2(0, rng.randf_range(-200, 200)),
                    probes[rng.randi_range(0, probes.size() - 1)], a + Vector2.from_angle(rng.randf() * TAU) * rng.randf_range(0.1, 500)]:
                var fast := HIT.hit_point(a, b, rect)
                var ref := ref_hit_point(a, b, rect)
                _count("hit_point")
                if fast != ref and not (is_nan(fast.x) and is_nan(ref.x)):
                    _same(false, "hit_point %s -> %s in %s: %s, was %s" % [a, b, rect, fast, ref])
    _same(true, "hit_point cases")

# --- one mission --------------------------------------------------------------------

func _check_mission(mission: String) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.configure_campaign({}, "COMBAT-QUERY-FASTPATH", {})
    await _frames(10)
    var field: Node = stage.battlefield
    _same(bool(field.world_ready), "%s: world floor is built" % mission)
    # Freeze the fight: this checks queries, not combat.
    for enemy in get_nodes_in_group("m3_enemies"): enemy.process_mode = Node.PROCESS_MODE_DISABLED
    for operator in stage.squad.operators: operator.process_mode = Node.PROCESS_MODE_DISABLED
    var covers: Array = get_nodes_in_group("sable_environment_cover")
    for cover in covers: cover.set_active(true)
    await _frames(2)
    var bounds := Rect2(Vector2(float(stage.main_route[0].x), float(stage.main_route[0].y)), Vector2.ZERO)
    for row in stage.main_route + stage.optional_rooms: bounds = bounds.expand(Vector2(float(row.x), float(row.y)))
    bounds = bounds.grow(600.0)
    var rng := RandomNumberGenerator.new()
    rng.seed = hash(mission)
    _check_floor(mission, field, bounds, rng)
    _check_props(mission, covers, rng)
    _check_obstacles_and_plans(mission, stage, field, bounds, rng)
    stage.queue_free()
    await _frames(3)

func _check_floor(mission: String, field: Node, bounds: Rect2, rng: RandomNumberGenerator) -> void:
    var points: Array[Vector2] = []
    for shape: PackedVector2Array in field._world_polygons:
        for vertex in shape:
            for offset in [Vector2.ZERO, Vector2(0.5, 0), Vector2(0, -0.5), Vector2(2.1, 2.1), Vector2(-2.1, -2.1), Vector2(3, 0)]:
                points.append(vertex + offset)
    for i in range(POINTS):
        points.append(Vector2(rng.randf_range(bounds.position.x, bounds.end.x), rng.randf_range(bounds.position.y, bounds.end.y)))
    var walkable: Array[Vector2] = []
    var bad := 0
    for point in points:
        var fast: bool = field.is_walkable(point)
        if fast != ref_is_walkable(field, point):
            bad += 1
            if bad <= 3: failures.append("%s is_walkable %s: %s" % [mission, point, fast])
        if fast: walkable.append(point)
    _count("is_walkable", points.size())
    _same(bad == 0, "%s: is_walkable agrees on %d points (%d differ)" % [mission, points.size(), bad])
    bad = 0
    var blocked := 0
    for i in range(SEGMENTS):
        var a: Vector2 = walkable[rng.randi_range(0, walkable.size() - 1)] if rng.randf() < 0.8 else points[rng.randi_range(0, points.size() - 1)]
        var length := rng.randf_range(0.0, 80.0) if i % 2 == 0 else rng.randf_range(80.0, 1400.0)
        var b := a + Vector2.from_angle(rng.randf() * TAU) * length
        if i % 7 == 0: b = walkable[rng.randi_range(0, walkable.size() - 1)]
        var fast: bool = field.segment_walkable(a, b)
        if not fast: blocked += 1
        if fast != ref_segment_walkable(field, a, b):
            bad += 1
            if bad <= 3: failures.append("%s segment_walkable %s -> %s: %s" % [mission, a, b, fast])
    _count("segment_walkable", SEGMENTS)
    _same(bad == 0, "%s: segment_walkable agrees on %d segments (%d differ)" % [mission, SEGMENTS, bad])
    _same(blocked > SEGMENTS / 20 and blocked < SEGMENTS - SEGMENTS / 20, "%s: segment sample mixes clear and blocked (%d blocked)" % [mission, blocked])

func _check_props(mission: String, covers: Array, rng: RandomNumberGenerator) -> void:
    var bad := 0
    var hits := 0
    var rays := 0
    for cover in covers:
        var centre: Vector2 = cover.global_position
        for i in range(RAYS_PER_PROP):
            var from := centre + Vector2.from_angle(rng.randf() * TAU) * rng.randf_range(20.0, 700.0)
            var to := centre + Vector2(rng.randf_range(-160, 160), rng.randf_range(-260, 60)) if i % 3 != 0 else from + Vector2.from_angle(rng.randf() * TAU) * rng.randf_range(1.0, 900.0)
            var ref := ref_projectile_hit(cover, from, to)
            var fast: Vector2 = cover.projectile_hit(from, to)
            rays += 1
            if fast.is_finite(): hits += 1
            if fast != ref[0] or cover.last_projectile_samples != int(ref[1]):
                bad += 1
                if bad <= 3: failures.append("%s projectile_hit %s -> %s: %s/%d, was %s/%d" % [mission, from, to, fast, cover.last_projectile_samples, ref[0], ref[1]])
    _count("projectile_hit", rays)
    _same(bad == 0, "%s: projectile_hit agrees on %d rays over %d props (%d differ)" % [mission, rays, covers.size(), bad])
    _same(hits > rays / 20, "%s: rays include real cover hits (%d)" % [mission, hits])

func _check_obstacles_and_plans(mission: String, stage: StoryStage01, field: Node, bounds: Rect2, rng: RandomNumberGenerator) -> void:
    # Actors whose planner stage is this battle floor (the reference covers that case only).
    var actors: Array[Node2D] = []
    for operator in stage.squad.operators.slice(0, 2):
        if NAV._stage(operator) == stage: actors.append(operator)
    for enemy in get_nodes_in_group("m3_enemies"):
        if NAV._stage(enemy) == stage:
            actors.append(enemy)
            break
    _same(actors.size() >= 2, "%s: planner actors on the battle floor (%d)" % [mission, actors.size()])
    NAV._edge_cache.clear()
    NAV._graph_cache.clear()
    var ref_cache := {}
    var ref2_cache := {}
    var differ := 0
    var shorter := 0
    var longer := 0
    var same_len := 0
    var no_route_before := 0
    var gain := 0.0
    var ref2_differ := 0
    var planner = NAV.new()
    var bad_obstacles := 0
    var bad_plans := 0
    var routes := 0
    var plans := 0
    var anchors: Array[Vector2] = []
    for row in stage.main_route + stage.optional_rooms: anchors.append(Vector2(float(row.x), float(row.y)))
    for actor in actors:
        var home := anchors[rng.randi_range(0, anchors.size() - 1)]
        for i in range(PLANS_PER_ACTOR):
            # Mostly one room (repeated obstacle sets reuse the cached graph), sometimes far.
            if i % 9 == 8: home = anchors[rng.randi_range(0, anchors.size() - 1)]
            var origin := _walkable_near(field, home, 380.0, rng)
            var goal := _walkable_near(field, anchors[rng.randi_range(0, anchors.size() - 1)] if i % 4 == 3 else home, 420.0, rng)
            if not origin.is_finite() or not goal.is_finite(): continue
            var obstacles: Array[Rect2] = NAV.ground_obstacles(actor, origin)
            var ref_obstacles := ref_ground_obstacles(actor, origin)
            if obstacles != ref_obstacles:
                bad_obstacles += 1
                if bad_obstacles <= 3: failures.append("%s ground_obstacles around %s: %s, was %s" % [mission, origin, obstacles, ref_obstacles])
            var fast: PackedVector2Array = planner._plan(actor, origin, goal, obstacles)
            var ref := ref_plan(stage, field, origin, goal, ref_obstacles, ref_cache)
            var ref2 := ref2_plan(actor, stage, field, origin, goal, ref_obstacles, ref2_cache)
            if fast != ref2:
                ref2_differ += 1
                if ref2_differ <= 3: print("PROBE ref2 differs ", mission, " ", origin, " -> ", goal, ": ", fast, " vs ", ref2)
            if fast != ref:
                differ += 1
                var length_fast := _poly(origin, fast)
                var length_ref := _poly(origin, ref)
                if ref.is_empty(): no_route_before += 1
                elif length_fast < length_ref - 0.01:
                    shorter += 1
                    gain += length_ref - length_fast
                elif length_fast > length_ref + 0.01:
                    longer += 1
                    print("PROBE longer ", mission, " ", origin, " -> ", goal, " fast ", length_fast, " ref ", length_ref)
                else: same_len += 1
            plans += 1
            if not fast.is_empty(): routes += 1
            if fast != ref:
                bad_plans += 1
                if bad_plans <= 3: failures.append("%s plan %s -> %s: %s, was %s" % [mission, origin, goal, fast, ref])
    _count("plans", plans)
    _count("probe_plans_differ", differ)
    _count("probe_shorter", shorter)
    _count("probe_longer", longer)
    _count("probe_same_length_other_path", same_len)
    _count("probe_reference_found_no_route", no_route_before)
    _count("probe_gain_px_x100", int(round(gain * 100.0)))
    _count("probe_new_rules_reference_differs", ref2_differ)
    print("PROBE_MISSION ", mission, " plans ", plans, " differ ", differ, " shorter ", shorter, " longer ", longer, " same_len ", same_len, " no_route_before ", no_route_before, " mean_gain_px ", (gain / maxf(1.0, float(shorter))), " new_rules_reference_differs ", ref2_differ)
    _count("plans_with_route", routes)
    _same(bad_obstacles == 0, "%s: ground_obstacles agree (%d differ)" % [mission, bad_obstacles])
    _same(bad_plans == 0, "%s: _plan agrees on %d plans (%d differ)" % [mission, plans, bad_plans])
    _same(routes > plans / 3, "%s: plans include real routes (%d of %d)" % [mission, routes, plans])

func _walkable_near(field: Node, centre: Vector2, radius: float, rng: RandomNumberGenerator) -> Vector2:
    for attempt in range(200):
        var point := centre + Vector2(rng.randf_range(-radius, radius), rng.randf_range(-radius, radius))
        if field.is_walkable(point): return point
    return Vector2.INF

func _frames(count: int) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

# --- reference copies of the replaced code (e76cfea00) ----------------------------------

static func ref_hit_point(from: Vector2, to: Vector2, rect: Rect2) -> Vector2:
    if rect.has_point(from): return from
    var corners := [rect.position, Vector2(rect.end.x,rect.position.y), rect.end, Vector2(rect.position.x,rect.end.y)]
    var nearest := Vector2.INF
    var distance := INF
    for index in range(4):
        var point: Variant = Geometry2D.segment_intersects_segment(from,to,corners[index],corners[(index+1)%4])
        if point is Vector2:
            var d := from.distance_squared_to(point)
            if d < distance:
                distance = d
                nearest = point
    if nearest == Vector2.INF and rect.has_point(to): return to
    return nearest

static func ref_is_walkable(field: Node, point: Vector2) -> bool:
    if not field.world_ready: return false
    for shape: PackedVector2Array in field._world_polygons:
        if Geometry2D.is_point_in_polygon(point, shape): return true
    var segments: Array = field._route_segments
    var widths: PackedFloat32Array = field._route_half_widths
    for segment_index in range(segments.size()):
        var segment: PackedVector2Array = segments[segment_index]
        var half_width := widths[segment_index]
        if half_width <= 0.0: continue
        if point.distance_squared_to(Geometry2D.get_closest_point_to_segment(point, segment[0], segment[1])) <= half_width * half_width:
            return true
    return false

static func ref_segment_walkable(field: Node, a: Vector2, b: Vector2) -> bool:
    if not field.world_ready: return false
    var d := b - a
    var length_sq := d.length_squared()
    if length_sq < 0.0001: return ref_is_walkable(field, a)
    var cuts: Array[float] = [0.0, 1.0]
    for shape: PackedVector2Array in field._world_polygons:
        var count := shape.size()
        for i in range(count):
            var hit = Geometry2D.segment_intersects_segment(a, b, shape[i], shape[(i + 1) % count])
            if hit != null: cuts.append((hit - a).dot(d) / length_sq)
    var segments: Array = field._route_segments
    var widths: PackedFloat32Array = field._route_half_widths
    for segment_index in range(segments.size()):
        var p: Vector2 = segments[segment_index][0]
        var q: Vector2 = segments[segment_index][1]
        var radius := widths[segment_index]
        if radius <= 0.0: continue
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
    var min_piece := 2.0 / sqrt(length_sq)
    for i in range(cuts.size() - 1):
        if cuts[i + 1] - cuts[i] < min_piece: continue
        if not ref_is_walkable(field, a + d * ((cuts[i] + cuts[i + 1]) * 0.5)): return false
    return ref_is_walkable(field, a) and ref_is_walkable(field, b)

## [point, alpha samples read].
static func ref_projectile_hit(prop: Node2D, from: Vector2, to: Vector2) -> Array:
    var samples := 0
    if not prop.active or not prop.is_visible_in_tree(): return [Vector2.INF, 0]
    var space: Node2D = prop._source_space
    var a := space.to_local(from)
    var b := space.to_local(to)
    var bounds := Rect2(Vector2.ZERO, Vector2(prop.source_size))
    var interval: Vector2 = prop._image_segment_interval(a,b,bounds)
    if not interval.is_finite(): return [Vector2.INF, 0]
    var region: Rect2i = prop.alpha_region
    var image: Image = prop.alpha_image
    var start := a.lerp(b,interval.x)
    var end := a.lerp(b,interval.y)
    var steps := maxi(1,int(ceil(start.distance_to(end))))
    for i in range(steps + 1):
        samples += 1
        var t := lerpf(interval.x,interval.y,float(i)/float(steps))
        var point := a.lerp(b,t)
        var pixel := Vector2i(int(point.x),int(point.y))
        if bounds.has_point(point) and region.has_point(pixel) and image.get_pixel(pixel.x-region.position.x,pixel.y-region.position.y).a >= 0.5:
            return [from.lerp(to,t), samples]
    return [Vector2.INF, samples]

func ref_ground_obstacles(actor: Node2D, around: Vector2) -> Array[Rect2]:
    var obstacles: Array[Rect2] = []
    var collider := actor.get_node_or_null("CollisionShape2D") as CollisionShape2D
    var offset := Vector2.ZERO
    var extent := Vector2(20,20)
    if collider and collider.shape:
        offset = actor.to_local(collider.global_position)
        extent = collider.shape.get_rect().size * collider.scale * actor.global_scale.abs() * 0.5 + Vector2(3,3)
    for cover in actor.get_tree().get_nodes_in_group("sable_environment_cover"):
        if not is_instance_valid(cover) or not cover.active or not cover.is_visible_in_tree(): continue
        var centre := around if around.is_finite() else actor.global_position
        if centre.distance_squared_to(cover.global_position) > NAV.LOCAL_OBSTACLE_RADIUS * NAV.LOCAL_OBSTACLE_RADIUS: continue
        var rect := Rect2(cover.to_global(cover.ground[0]),Vector2.ZERO)
        for point in cover.ground: rect = rect.expand(cover.to_global(point))
        obstacles.append(Rect2(rect.position-offset-extent,rect.size+extent*2.0))
    return obstacles

static func ref_clear_ground(field: Node, a: Vector2, b: Vector2, obstacles: Array[Rect2]) -> bool:
    for rect in obstacles:
        if ref_hit_point(a,b,rect.grow(-0.4)).is_finite(): return false
    return ref_segment_walkable(field, a, b)

## The planner before the graph cache, on a battle floor, with its own edge cache.
static func ref_plan(stage: Node, field: Node, origin: Vector2, goal: Vector2, obstacles: Array[Rect2], edge_cache: Dictionary) -> PackedVector2Array:
    var nodes := PackedVector2Array([origin,goal])
    var waypoints: PackedVector2Array = field.navigation_waypoints()
    var cache_key := hash([obstacles, waypoints, stage.get_instance_id()])
    if not edge_cache.has(cache_key):
        if edge_cache.size() > 48: edge_cache.clear()
        edge_cache[cache_key] = {}
    var visible: Dictionary = edge_cache[cache_key]
    for waypoint in waypoints:
        if ref_clear_ground(field,waypoint,waypoint,obstacles): nodes.append(waypoint)
    for rect in obstacles:
        var safe := rect.grow(NAV.CORNER_CLEARANCE)
        for corner in [safe.position,Vector2(safe.end.x,safe.position.y),safe.end,Vector2(safe.position.x,safe.end.y)]:
            if ref_clear_ground(field,corner,corner,obstacles): nodes.append(corner)
    var distance: Array[float] = []
    var previous: Array[int] = []
    var visited: Array[bool] = []
    for _index in range(nodes.size()):
        distance.append(INF); previous.append(-1); visited.append(false)
    distance[0]=0
    for _index in range(nodes.size()):
        var next := -1
        for index in range(nodes.size()):
            if not visited[index] and (next<0 or distance[index]<distance[next]): next=index
        if next<0 or distance[next]==INF: break
        if next==1: break
        visited[next]=true
        for index in range(nodes.size()):
            if visited[index] or index==next: continue
            if nodes[next].distance_squared_to(nodes[index]) > NAV.MAX_GRAPH_EDGE*NAV.MAX_GRAPH_EDGE: continue
            if next < 2 or index < 2:
                if not ref_clear_ground(field,nodes[next],nodes[index],obstacles): continue
            else:
                var pair := Vector4(nodes[next].x,nodes[next].y,nodes[index].x,nodes[index].y) if next < index else Vector4(nodes[index].x,nodes[index].y,nodes[next].x,nodes[next].y)
                if not visible.has(pair): visible[pair] = ref_clear_ground(field,nodes[next],nodes[index],obstacles)
                if not bool(visible[pair]): continue
            var cost := distance[next]+nodes[next].distance_to(nodes[index])
            if cost<distance[index]: distance[index]=cost; previous[index]=next
    var path := PackedVector2Array()
    if previous[1]<0: return path
    var cursor := 1
    while cursor>0:
        path.insert(0,nodes[cursor]); cursor=previous[cursor]
    return path


func _poly(origin: Vector2, path: PackedVector2Array) -> float:
    var total := 0.0
    var cursor := origin
    for node in path:
        total += cursor.distance_to(node)
        cursor = node
    return total

## Reference with the new visibility rules: the inflated box is the broad phase, a clipped edge is confirmed by the
## actor's real collider (NAV._physics_ground_clear), then the exact floor test.
static func ref2_clear_ground(actor: Node2D, field: Node, a: Vector2, b: Vector2, obstacles: Array[Rect2]) -> bool:
    var clips := false
    for rect in obstacles:
        if ref_hit_point(a, b, rect.grow(-0.4)).is_finite():
            clips = true
            break
    if clips and not NAV._physics_ground_clear(actor, a, b): return false
    return ref_segment_walkable(field, a, b)

static func ref2_nodes(actor: Node2D, field: Node, waypoints: PackedVector2Array, obstacles: Array[Rect2]) -> PackedVector2Array:
    var fixed := PackedVector2Array()
    for waypoint in waypoints:
        if ref2_clear_ground(actor, field, waypoint, waypoint, obstacles): fixed.append(waypoint)
    for rect in obstacles:
        var safe := rect.grow(NAV.CORNER_CLEARANCE)
        for corner in [safe.position, Vector2(safe.end.x, safe.position.y), safe.end, Vector2(safe.position.x, safe.end.y)]:
            if ref2_clear_ground(actor, field, corner, corner, obstacles):
                fixed.append(corner)
                continue
            if not field.has_method("constrain") or NAV._on_floor(actor, corner): continue
            var point: Vector2 = field.constrain(corner)
            point = NAV._free_goal(actor, point, obstacles)
            if not point.is_finite(): continue
            if ref2_clear_ground(actor, field, point, point, obstacles): fixed.append(point)
    return fixed

static func ref2_plan(actor: Node2D, stage: Node, field: Node, origin: Vector2, goal: Vector2, obstacles: Array[Rect2], edge_cache: Dictionary) -> PackedVector2Array:
    var nodes := PackedVector2Array([origin, goal])
    var waypoints: PackedVector2Array = field.navigation_waypoints()
    var cache_key := hash([obstacles, waypoints, stage.get_instance_id()])
    if not edge_cache.has(cache_key):
        if edge_cache.size() > 48: edge_cache.clear()
        edge_cache[cache_key] = {}
    var visible: Dictionary = edge_cache[cache_key]
    nodes.append_array(ref2_nodes(actor, field, waypoints, obstacles))
    var distance: Array[float] = []
    var previous: Array[int] = []
    var visited: Array[bool] = []
    for _index in range(nodes.size()):
        distance.append(INF); previous.append(-1); visited.append(false)
    distance[0] = 0
    for _index in range(nodes.size()):
        var next := -1
        for index in range(nodes.size()):
            if not visited[index] and (next < 0 or distance[index] < distance[next]): next = index
        if next < 0 or distance[next] == INF: break
        if next == 1: break
        visited[next] = true
        for index in range(nodes.size()):
            if visited[index] or index == next: continue
            if nodes[next].distance_squared_to(nodes[index]) > NAV.MAX_GRAPH_EDGE * NAV.MAX_GRAPH_EDGE: continue
            if next < 2 or index < 2:
                if not ref2_clear_ground(actor, field, nodes[next], nodes[index], obstacles): continue
            else:
                var pair := Vector4(nodes[next].x, nodes[next].y, nodes[index].x, nodes[index].y) if next < index else Vector4(nodes[index].x, nodes[index].y, nodes[next].x, nodes[next].y)
                if not visible.has(pair): visible[pair] = ref2_clear_ground(actor, field, nodes[next], nodes[index], obstacles)
                if not bool(visible[pair]): continue
            var cost := distance[next] + nodes[next].distance_to(nodes[index])
            if cost < distance[index]: distance[index] = cost; previous[index] = next
    var path := PackedVector2Array()
    if previous[1] < 0: return path
    var cursor := 1
    while cursor > 0:
        path.insert(0, nodes[cursor]); cursor = previous[cursor]
    return path
