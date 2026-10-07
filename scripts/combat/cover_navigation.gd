extends RefCounted
## Small visibility graph over streamed prop footprints. Movement uses ground
## geometry + the actor's real collider; shooting uses the visible alpha instead.
const HIT := preload("res://scripts/combat/combat_hit_geometry.gd")
const GROUND_MARGIN := 3.0
const CORNER_CLEARANCE := 12.0
const LOCAL_OBSTACLE_RADIUS := 1000.0
const MAX_GRAPH_EDGE := 900.0
# Waypoints and cover are static during a mission, so floor/cover visibility
# between two fixed nodes is reused across plans (keyed by the obstacle set and
# the waypoint set). Origin/goal edges are always tested fresh.
static var _edge_cache: Dictionary = {}
# On a battle floor the fixed part of the graph is cached under the same key and
# cleared with it: the on-floor waypoints and cover corners, each one's fixed
# neighbours within MAX_GRAPH_EDGE, and their floor visibility. Plans visit, test
# and cache edges in the same order as the full scan, so routes are unchanged.
static var _graph_cache: Dictionary = {}
var _path := PackedVector2Array()
var _goal := Vector2.INF
var _signature := 0
var _refresh := 0.0
var _direct := false
var replans := 0

static func first_cover(tree: SceneTree, from: Vector2, to: Vector2) -> Node2D:
    var nearest: Node2D = null
    var distance := INF
    for cover in tree.get_nodes_in_group("sable_environment_cover"):
        if not is_instance_valid(cover) or cover.is_queued_for_deletion(): continue
        var hit: Vector2 = cover.projectile_hit(from,to)
        if hit.is_finite() and from.distance_squared_to(hit) < distance:
            distance = from.distance_squared_to(hit)
            nearest = cover
    return nearest

static func clear_shot(tree: SceneTree, from: Vector2, target: Node2D) -> bool:
    if not is_instance_valid(target): return false
    var to: Vector2 = target.get_combat_aim_point() if target.has_method("get_combat_aim_point") else target.global_position
    if target.has_method("get_combat_hit_rect"):
        var hit := HIT.hit_point(from,to,target.get_combat_hit_rect().grow(2.0))
        if hit.is_finite(): to = hit
    return first_cover(tree,from,to) == null

static func reticle_blocked(tree: SceneTree, from: Vector2, cursor: Vector2) -> bool:
    var end := cursor
    for target in tree.get_nodes_in_group("prototype_targets"):
        if not is_instance_valid(target) or not target.has_method("get_combat_hit_rect"): continue
        var hit := HIT.hit_point(from,end,target.get_combat_hit_rect().grow(2.0))
        if hit.is_finite(): end=hit
    # Cover BEHIND the first damageable target cannot block that target.
    return first_cover(tree,from,end)!=null

static func _stage(actor: Node2D) -> Node:
    var parent := actor.get_parent()
    if parent and parent.has_method("has_battle_floor"): return parent
    return parent.get_parent() if parent else null

static func _on_floor(actor: Node2D, point: Vector2) -> bool:
    var stage := _stage(actor)
    if stage and stage.has_method("has_battle_floor") and stage.has_battle_floor():
        if stage.battlefield and stage.battlefield.has_method("is_walkable"):
            return bool(stage.battlefield.is_walkable(point))
        return stage.battlefield.contains(point)
    if actor is OperatorActor: return actor.movement_bounds.has_point(point)
    return true

static func ground_obstacles(actor: Node2D, around: Vector2 = Vector2.INF) -> Array[Rect2]:
    var obstacles: Array[Rect2] = []
    var collider := actor.get_node_or_null("CollisionShape2D") as CollisionShape2D
    var offset := Vector2.ZERO
    var extent := Vector2(20,20)
    if collider and collider.shape:
        offset = actor.to_local(collider.global_position)
        extent = collider.shape.get_rect().size * collider.scale * actor.global_scale.abs() * 0.5 + Vector2.ONE * GROUND_MARGIN
    for cover in actor.get_tree().get_nodes_in_group("sable_environment_cover"):
        if not is_instance_valid(cover) or not cover.active or not cover.is_visible_in_tree(): continue
        var centre := around if around.is_finite() else actor.global_position
        if centre.distance_squared_to(cover.global_position) > LOCAL_OBSTACLE_RADIUS * LOCAL_OBSTACLE_RADIUS: continue
        var rect: Rect2 = cover.ground_world_rect()
        # Transform the shape-center obstacle into actor-root coordinates.
        obstacles.append(Rect2(rect.position-offset-extent,rect.size+extent*2.0))
    return obstacles

static func _clear_ground(actor: Node2D, a: Vector2, b: Vector2, obstacles: Array[Rect2]) -> bool:
    var clips_box := false
    for rect in obstacles:
        if HIT.hit_point(a,b,rect.grow(-0.4)).is_finite():
            clips_box = true
            break
    # The boxes are a broad phase: an angled cover footprint and the actor's
    # capsule leave real space at their corners. Two overlapping boxes can
    # falsely close a wedge against the floor. When they clip an edge, confirm
    # it against the actual collider and ground collision polygons, keeping
    # the same 3 px margin. No actor/art/floor geometry is changed.
    if clips_box and not _physics_ground_clear(actor,a,b): return false
    var stage := _stage(actor)
    if stage and stage.has_method("has_battle_floor") and stage.has_battle_floor()             and stage.battlefield and stage.battlefield.has_method("segment_walkable"):
        return bool(stage.battlefield.segment_walkable(a, b))
    var span := a.distance_to(b)
    # A 32px probe skipped the narrow gap between the route capsule and a
    # connector polygon. A valid endpoint across it made actors press forever
    # against an invisible boundary even though the path node was walkable.
    var steps := maxi(1,int(ceil(span/(4.0 if span <= 64.0 else 16.0))))
    for i in range(steps+1):
        if not _on_floor(actor,a.lerp(b,float(i)/steps)): return false
    return true

static func _physics_ground_clear(actor: Node2D, a: Vector2, b: Vector2) -> bool:
    var stage := _stage(actor)
    # Off a battle floor, callers may be building geometry fixtures before the
    # physics server has received their bodies. Preserve that original scan.
    if not (stage and stage.has_method("has_battle_floor") and stage.has_battle_floor()): return false
    var collider := actor.get_node_or_null("CollisionShape2D") as CollisionShape2D
    # Geometry-only probes without a real body retain the conservative boxes.
    if collider == null or collider.shape == null or not actor.is_inside_tree(): return false
    # A cached fixed pair must answer identically from either end.
    if b.x < a.x or (b.x == a.x and b.y < a.y):
        var held := a
        a = b
        b = held
    var query := PhysicsShapeQueryParameters2D.new()
    query.shape = collider.shape
    query.margin = GROUND_MARGIN
    query.collision_mask = 1 # ground cover and walls, never other actors
    if actor is CollisionObject2D: query.exclude = [(actor as CollisionObject2D).get_rid()]
    var space := actor.get_world_2d().direct_space_state
    var transform := collider.global_transform
    transform.origin += a - actor.global_position
    query.transform = transform
    if not space.intersect_shape(query,1).is_empty(): return false
    transform.origin += b - a
    query.transform = transform
    if not space.intersect_shape(query,1).is_empty(): return false
    if a == b: return true
    transform.origin -= b - a
    query.transform = transform
    query.motion = b - a
    var fractions := space.cast_motion(query)
    return fractions.size() == 2 and fractions[0] >= 1.0

static func _free_goal(actor: Node2D, goal: Vector2, obstacles: Array[Rect2]) -> Vector2:
    var point := goal
    for _pass in range(obstacles.size()+1):
        var moved := false
        for rect in obstacles:
            if not rect.has_point(point): continue
            if _physics_ground_clear(actor,point,point): continue
            var candidates := [Vector2(rect.position.x-2,point.y),Vector2(rect.end.x+2,point.y),
                Vector2(point.x,rect.position.y-2),Vector2(point.x,rect.end.y+2)]
            var best := Vector2.INF
            var distance := INF
            for candidate: Vector2 in candidates:
                if not _on_floor(actor,candidate): continue
                var d := candidate.distance_squared_to(point)
                if d < distance: best=candidate; distance=d
            if not best.is_finite(): return Vector2.INF
            point=best; moved=true
        if not moved: return point
    return Vector2.INF

static func _steer(origin: Vector2, goal: Vector2, step_distance: float) -> Vector2:
    var offset := goal-origin
    return offset.normalized()*minf(1.0,offset.length()/maxf(step_distance,0.001))

func direction(actor: Node2D, goal: Vector2, delta: float, step_distance: float = 0.0) -> Vector2:
    if not goal.is_finite(): return Vector2.ZERO
    var obstacles := ground_obstacles(actor)
    var origin := actor.global_position
    var free_goal := _free_goal(actor,goal,obstacles)
    if not free_goal.is_finite(): return Vector2.ZERO
    for rect in obstacles:
        if rect.has_point(origin) and not _physics_ground_clear(actor,origin,origin):
            var escape := _free_goal(actor,origin,obstacles)
            return _steer(origin,escape,step_distance) if escape.is_finite() else Vector2.ZERO
    _refresh -= delta
    var signature := hash(obstacles)
    var same_plan := _refresh > 0.0 and signature == _signature and _goal.distance_to(free_goal) <= 28.0
    if same_plan:
        var local_target := free_goal if _direct else (_path[0] if not _path.is_empty() else Vector2.INF)
        if local_target.is_finite() and _clear_ground(actor,origin,origin.move_toward(local_target,64.0),obstacles):
            if _direct: return _steer(origin,free_goal,step_distance) if origin.distance_to(free_goal)>2 else Vector2.ZERO
            # Reuse the committed path during its short validity window.  The
            # old direct test sampled the entire multi-room line every 60 Hz.
            while not _path.is_empty() and origin.distance_to(_path[0]) < 3.0:
                if _path.size() > 1 and not _clear_ground(actor,origin,_path[1],obstacles): break
                _path.remove_at(0)
            if not _path.is_empty(): return _steer(origin,_path[0],step_distance)
    _signature=signature
    _goal=free_goal
    _refresh=0.3
    if origin.distance_to(free_goal) <= MAX_GRAPH_EDGE and _clear_ground(actor,origin,free_goal,obstacles):
        _direct=true
        _path.clear()
        return _steer(origin,free_goal,step_distance) if origin.distance_to(free_goal)>2 else Vector2.ZERO
    _direct=false
    _path = _plan(actor,origin,free_goal,obstacles)
    replans += 1
    # A close corner is not passed until the NEXT edge is clear from the actual
    # body position. Dropping it early cuts into the inflated prop, making the
    # escape steering alternate with the route every physics tick.
    while not _path.is_empty() and origin.distance_to(_path[0])<3:
        if _path.size()>1 and not _clear_ground(actor,origin,_path[1],obstacles): break
        _path.remove_at(0)
    if _path.is_empty(): return Vector2.ZERO
    return _steer(origin,_path[0],step_distance)

func _plan(actor: Node2D, origin: Vector2, goal: Vector2, obstacles: Array[Rect2]) -> PackedVector2Array:
    var stage := _stage(actor)
    var waypoints := PackedVector2Array()
    if stage and stage.get("battlefield") != null and stage.battlefield.has_method("navigation_waypoints"):
        waypoints = stage.battlefield.navigation_waypoints()
    var cache_key := hash([obstacles, waypoints, stage.get_instance_id() if stage else 0])
    if not _edge_cache.has(cache_key):
        if _edge_cache.size() > 48:
            _edge_cache.clear()
            _graph_cache.clear()
        _edge_cache[cache_key] = {}
    # Off a battle floor a node's ground test can depend on the actor's movement
    # bounds, so that case keeps the uncached scan.
    if not (stage and stage.has_method("has_battle_floor") and stage.has_battle_floor()
            and stage.battlefield and stage.battlefield.has_method("segment_walkable")):
        return _plan_scan(actor, origin, goal, obstacles, waypoints, _edge_cache[cache_key])
    if not _graph_cache.has(cache_key):
        _graph_cache[cache_key] = _fixed_graph(actor, waypoints, obstacles)
    var graph: Array = _graph_cache[cache_key]
    var fixed: PackedVector2Array = graph[0]
    var neighbours: Array = graph[1]
    var canonical: PackedInt32Array = graph[2]
    var seen: PackedByteArray = graph[3]
    var fixed_count := fixed.size()
    var nodes := PackedVector2Array([origin,goal])
    nodes.append_array(fixed)
    var count := nodes.size()
    var distance := PackedFloat64Array()
    distance.resize(count)
    distance.fill(INF)
    var previous := PackedInt32Array()
    previous.resize(count)
    previous.fill(-1)
    var visited := PackedByteArray()
    visited.resize(count)
    distance[0]=0.0
    # Reached, unvisited nodes. The full scan took the lowest distance and, on a tie,
    # the lowest index, and stopped before any unreached (INF) node.
    var open := PackedInt32Array([0])
    while not open.is_empty():
        var slot := 0
        for k in range(1, open.size()):
            var candidate := open[k]
            var held := open[slot]
            if distance[candidate] < distance[held] or (distance[candidate] == distance[held] and candidate < held): slot = k
        var next := open[slot]
        open.remove_at(slot)
        if next==1: break
        visited[next]=1
        var from := nodes[next]
        if next < 2:
            for index in range(count):
                if visited[index] or index==next: continue
                if from.distance_squared_to(nodes[index]) > MAX_GRAPH_EDGE*MAX_GRAPH_EDGE: continue
                if not _clear_ground(actor,from,nodes[index],obstacles): continue
                var cost := distance[next]+from.distance_to(nodes[index])
                if cost<distance[index]:
                    if distance[index]==INF: open.append(index)
                    distance[index]=cost; previous[index]=next
            continue
        # Origin and goal edges are always tested fresh.
        for index in range(2):
            if visited[index]: continue
            if from.distance_squared_to(nodes[index]) > MAX_GRAPH_EDGE*MAX_GRAPH_EDGE: continue
            if not _clear_ground(actor,from,nodes[index],obstacles): continue
            var cost := distance[next]+from.distance_to(nodes[index])
            if cost<distance[index]:
                if distance[index]==INF: open.append(index)
                distance[index]=cost; previous[index]=next
        # A fixed pair's visibility is kept per (lower-index node, higher-index node)
        # position, as tested from whichever end was visited first.
        var row: PackedInt32Array = neighbours[next-2]
        for index in row:
            if visited[index]: continue
            var cell := canonical[next-2]*fixed_count+canonical[index-2] if next < index else canonical[index-2]*fixed_count+canonical[next-2]
            var state := seen[cell]
            if state == 0:
                state = 1 if _clear_ground(actor,from,nodes[index],obstacles) else 2
                seen[cell] = state
            if state != 1: continue
            var cost := distance[next]+from.distance_to(nodes[index])
            if cost<distance[index]:
                if distance[index]==INF: open.append(index)
                distance[index]=cost; previous[index]=next
    graph[3] = seen
    var path := PackedVector2Array()
    if previous[1]<0: return path
    var cursor := 1
    while cursor>0:
        path.insert(0,nodes[cursor]); cursor=previous[cursor]
    return path

## [fixed nodes; per fixed node, its fixed neighbours within MAX_GRAPH_EDGE as graph
## indices in ascending order; per fixed node, the first fixed node at the same
## position; pair visibility (0 untested, 1 clear, 2 blocked)].
static func _fixed_graph(actor: Node2D, waypoints: PackedVector2Array, obstacles: Array[Rect2]) -> Array:
    var fixed := _fixed_nodes(actor, waypoints, obstacles)
    var neighbours: Array[PackedInt32Array] = []
    var canonical := PackedInt32Array()
    var first_at := {}
    for i in range(fixed.size()):
        var row := PackedInt32Array()
        for j in range(fixed.size()):
            if j != i and fixed[i].distance_squared_to(fixed[j]) <= MAX_GRAPH_EDGE*MAX_GRAPH_EDGE: row.append(j+2)
        neighbours.append(row)
        if not first_at.has(fixed[i]): first_at[fixed[i]] = i
        canonical.append(int(first_at[fixed[i]]))
    var seen := PackedByteArray()
    seen.resize(fixed.size()*fixed.size())
    return [fixed, neighbours, canonical, seen]

static func _fixed_nodes(actor: Node2D, waypoints: PackedVector2Array, obstacles: Array[Rect2]) -> PackedVector2Array:
    var fixed := PackedVector2Array()
    for waypoint in waypoints:
        if _clear_ground(actor,waypoint,waypoint,obstacles): fixed.append(waypoint)
    var stage := _stage(actor)
    var floor_field: Node = stage.battlefield if stage and stage.get("battlefield") != null else null
    for rect in obstacles:
        var safe := rect.grow(CORNER_CLEARANCE)
        for corner in [safe.position,Vector2(safe.end.x,safe.position.y),safe.end,Vector2(safe.position.x,safe.end.y)]:
            if _clear_ground(actor,corner,corner,obstacles):
                fixed.append(corner)
                continue
            # A floor edge can clip the padded corner while leaving a walkable
            # wedge beside the actual inflated box. Keep a nearby node in that
            # wedge instead of dropping its only connection to the graph. The
            # floor's exact clamp moves inward; _free_goal keeps the actor's
            # full collider clearance from every box. Every edge is still
            # checked against the same painted floor and obstacles.
            if floor_field == null or not floor_field.has_method("constrain") or _on_floor(actor,corner): continue
            var point: Vector2 = floor_field.constrain(corner)
            point = _free_goal(actor, point, obstacles)
            if not point.is_finite(): continue
            if _clear_ground(actor,point,point,obstacles): fixed.append(point)
    return fixed

## Full O(n^2) scan with pair visibility cached by position: the planner as it was
## before the battle-floor graph cache. Used off a battle floor.
func _plan_scan(actor: Node2D, origin: Vector2, goal: Vector2, obstacles: Array[Rect2], waypoints: PackedVector2Array, visible: Dictionary) -> PackedVector2Array:
    var nodes := PackedVector2Array([origin,goal])
    nodes.append_array(_fixed_nodes(actor, waypoints, obstacles))
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
            # The authored world route may bend farther than a direct-line
            # heuristic allows. Keep every waypoint, but only test nearby
            # graph edges; distant all-pairs floor sampling froze WebGL and
            # pruned valid routes in later missions.
            if nodes[next].distance_squared_to(nodes[index]) > MAX_GRAPH_EDGE*MAX_GRAPH_EDGE: continue
            if next < 2 or index < 2:
                if not _clear_ground(actor,nodes[next],nodes[index],obstacles): continue
            else:
                var pair := Vector4(nodes[next].x,nodes[next].y,nodes[index].x,nodes[index].y) if next < index else Vector4(nodes[index].x,nodes[index].y,nodes[next].x,nodes[next].y)
                if not visible.has(pair): visible[pair] = _clear_ground(actor,nodes[next],nodes[index],obstacles)
                if not bool(visible[pair]): continue
            var cost := distance[next]+nodes[next].distance_to(nodes[index])
            if cost<distance[index]: distance[index]=cost; previous[index]=next
    var path := PackedVector2Array()
    if previous[1]<0: return path
    var cursor := 1
    while cursor>0:
        path.insert(0,nodes[cursor]); cursor=previous[cursor]
    return path
