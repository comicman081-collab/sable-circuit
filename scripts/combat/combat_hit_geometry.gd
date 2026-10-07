extends RefCounted

## Swept point versus visible body bounds, rather than a circle at the feet.
static func hit_point(from: Vector2, to: Vector2, rect: Rect2) -> Vector2:
    # Most calls are misses (every obstacle and target is tested per physics tick). A
    # segment whose bounding box is clear of the rect by more than the intersection
    # test's tolerance can neither start inside it nor cross one of its edges.
    if rect.size.x >= 0.0 and rect.size.y >= 0.0 and (
            minf(from.x, to.x) > rect.end.x + 1.0 or maxf(from.x, to.x) < rect.position.x - 1.0
            or minf(from.y, to.y) > rect.end.y + 1.0 or maxf(from.y, to.y) < rect.position.y - 1.0):
        return Vector2.INF
    if rect.has_point(from): return from
    var top_right := Vector2(rect.end.x, rect.position.y)
    var bottom_left := Vector2(rect.position.x, rect.end.y)
    var nearest := Vector2.INF
    var distance := INF
    # Top, right, bottom, left edge; on a tie the earlier edge wins.
    var point: Variant = Geometry2D.segment_intersects_segment(from, to, rect.position, top_right)
    if point is Vector2 and from.distance_squared_to(point) < distance:
        distance = from.distance_squared_to(point); nearest = point
    point = Geometry2D.segment_intersects_segment(from, to, top_right, rect.end)
    if point is Vector2 and from.distance_squared_to(point) < distance:
        distance = from.distance_squared_to(point); nearest = point
    point = Geometry2D.segment_intersects_segment(from, to, rect.end, bottom_left)
    if point is Vector2 and from.distance_squared_to(point) < distance:
        distance = from.distance_squared_to(point); nearest = point
    point = Geometry2D.segment_intersects_segment(from, to, bottom_left, rect.position)
    if point is Vector2 and from.distance_squared_to(point) < distance:
        distance = from.distance_squared_to(point); nearest = point
    if nearest == Vector2.INF and rect.has_point(to): return to
    return nearest
