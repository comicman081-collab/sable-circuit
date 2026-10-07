"""Claude review helper (N-1, B-3 diagnosis): build a scratch copy of tests/smoke/combat_query_fastpath_smoke.gd that
  (a) classifies every plan where the real _plan differs from the test's frozen reference (shorter / same length / longer /
      the reference found no route), and
  (b) replays the same plan sequence against a SECOND reference that has the new rules (narrow-phase ground test + the
      floor-projected escape node) but is still an uncached, plain Dijkstra, to show that the cached graph itself still
      agrees bit for bit once the reference speaks the new visibility rules.
usage: make_fastpath_probe.py <source smoke .gd> <target .gd>"""
import sys
from pathlib import Path

src = Path(sys.argv[1]).read_bytes().decode("utf-8").replace("\r\n", "\n")

# 1) the second reference cache next to the first
old = "    var ref_cache := {}\n"
assert src.count(old) == 1
src = src.replace(old, old + "    var ref2_cache := {}\n    var differ := 0\n    var shorter := 0\n    var longer := 0\n    var same_len := 0\n    var no_route_before := 0\n    var gain := 0.0\n    var ref2_differ := 0\n")

# 2) classify after the first reference plan
old = "            var ref := ref_plan(stage, field, origin, goal, ref_obstacles, ref_cache)\n"
assert src.count(old) == 1
new = old + """            var ref2 := ref2_plan(actor, stage, field, origin, goal, ref_obstacles, ref2_cache)
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
"""
src = src.replace(old, new)

# 3) totals after the loop
old = '    _count("plans", plans)\n'
assert src.count(old) == 1
src = src.replace(old, old + '    _count("probe_plans_differ", differ)\n    _count("probe_shorter", shorter)\n    _count("probe_longer", longer)\n    _count("probe_same_length_other_path", same_len)\n    _count("probe_reference_found_no_route", no_route_before)\n    _count("probe_gain_px_x100", int(round(gain * 100.0)))\n    _count("probe_new_rules_reference_differs", ref2_differ)\n    print("PROBE_MISSION ", mission, " plans ", plans, " differ ", differ, " shorter ", shorter, " longer ", longer, " same_len ", same_len, " no_route_before ", no_route_before, " mean_gain_px ", (gain / maxf(1.0, float(shorter))), " new_rules_reference_differs ", ref2_differ)\n')

# 4) helpers: polyline length, second reference
src += '''

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
'''
Path(sys.argv[2]).write_bytes(src.encode("utf-8"))
print("wrote", sys.argv[2], len(src))
