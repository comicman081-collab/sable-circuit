extends Control
class_name TacticalMinimap
## Tilted "diorama" minimap after the mockup: the live walk graph (traced room
## and corridor floors) projected at an angle with plate thickness, the current
## objective room lit, the squad marker and hostiles. +/- zoom around the squad.
##
## Two layers: this Control draws the deck grid and floors, redrawn only when their
## projection (zoom, squad focus, lit room) changes; the child Markers layer draws
## the pulsing objective, hostiles and squad every frame. Redrawing the floors every
## frame rebuilt ~80 polygons (a vertex array and buffers each on the web renderer)
## just for the objective pulse. Children draw after their parent, in the same order
## as the single layer did.

const TILT := -0.42
const SQUASH := 0.62
const ZOOM_LEVELS: Array[float] = [1.0, 3.0, 4.6]

var stage: StoryStage01
var _route: Array[Vector2] = [
    Vector2(280,470), Vector2(690,350), Vector2(1100,490),
    Vector2(1510,350), Vector2(1920,490), Vector2(2330,350)
]
var _optional: Array[Vector2] = [Vector2(1100,705),Vector2(1510,705)]
# Local view around the squad by default (mockup); M toggles the overview.
var _zoom_index := 1
var _zoom := 3.0
var _time := 0.0
var _fit_cache := Transform2D.IDENTITY
var _bounds_cache := Rect2()
var _markers: Control
## Projection the floor layer was last drawn with.
var _floor_key: Array = []
## Per floor shape, cached once the world is built: tilted points, world centroid,
## and whether it belongs to an optional room.
var _tilted: Array[PackedVector2Array] = []
var _centroids: Array[Vector2] = []
var _optional_shape: Array[bool] = []
var _shapes_source := -1
var _bounds_source := -1
var _bounds_value := Rect2()

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    clip_contents = true
    _markers = Control.new()
    _markers.name = "Markers"
    _markers.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _markers.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _markers.draw.connect(_draw_markers)
    add_child(_markers)
    queue_redraw()

func bind_stage(value: StoryStage01) -> void:
    stage = value
    if stage:
        _route.clear()
        _optional.clear()
        for row: Dictionary in stage.main_route:
            _route.append(Vector2(float(row.x), float(row.y)))
        for row: Dictionary in stage.optional_rooms:
            _optional.append(Vector2(float(row.x), float(row.y)))
    _bounds_source = -1
    _shapes_source = -1
    queue_redraw()

func zoom_by(step: int) -> void:
    _zoom_index = clampi(_zoom_index + step, 0, ZOOM_LEVELS.size() - 1)

func toggle_zoom() -> void:
    _zoom_index = 0 if _zoom_index > 0 else 1

func debug_zoom() -> float:
    return ZOOM_LEVELS[_zoom_index]

func _process(delta: float) -> void:
    _time += delta
    _zoom = lerpf(_zoom, ZOOM_LEVELS[_zoom_index], 1.0 - exp(-delta * 8.0))
    if _markers:
        _markers.queue_redraw()

func _polygons() -> Array:
    if stage and stage.battlefield and bool(stage.battlefield.get("world_ready")):
        return stage.battlefield.get("_world_polygons")
    return []

func _bounds() -> Rect2:
    var box := Rect2(_route[0], Vector2.ZERO) if not _route.is_empty() else Rect2(0, 0, 1, 1)
    for p in _route: box = box.expand(p)
    for p in _optional: box = box.expand(p)
    for shape: PackedVector2Array in _polygons():
        for p in shape: box = box.expand(p)
    return box.grow(160.0)

## _bounds(), recomputed only when the route or the floor set changes.
func _current_bounds() -> Rect2:
    var count := _polygons().size()
    if count != _bounds_source:
        _bounds_value = _bounds()
        _bounds_source = count
    return _bounds_value

## World -> tilted minimap space (before fitting).
func _tilt(world: Vector2) -> Vector2:
    var rotated := world.rotated(TILT)
    return Vector2(rotated.x, rotated.y * SQUASH)

func _fit() -> Transform2D:
    var box := _bounds_cache if _bounds_cache.has_area() else _bounds()
    var corners := [box.position, Vector2(box.end.x, box.position.y), box.end, Vector2(box.position.x, box.end.y)]
    var t_box := Rect2(_tilt(corners[0]), Vector2.ZERO)
    for c in corners: t_box = t_box.expand(_tilt(c))
    var usable := size - Vector2(12, 16)
    var scale_value := minf(usable.x / t_box.size.x, usable.y / t_box.size.y) * _zoom
    var focus := t_box.get_center()
    if _zoom > 1.01 and stage and stage.squad and stage.squad.get_active_operator():
        var zoom_mix := clampf((_zoom - 1.0) / 1.2, 0.0, 1.0)
        focus = focus.lerp(_tilt(stage.squad.get_active_operator().global_position), zoom_mix)
    return Transform2D(0.0, Vector2.ONE * scale_value, 0.0, size * 0.5 - focus * scale_value)

func _map(world: Vector2) -> Vector2:
    return _fit_cache * _tilt(world)

func _floor_projection_key(fit: Transform2D, current: int) -> Array:
    return [fit, current, _zoom, size, _polygons().size()]

func _ensure_shapes(polygons: Array) -> void:
    if _shapes_source == polygons.size(): return
    _tilted.clear()
    _centroids.clear()
    _optional_shape.clear()
    for shape: PackedVector2Array in polygons:
        var tilted := PackedVector2Array()
        var centroid := Vector2.ZERO
        for p in shape:
            tilted.append(_tilt(p))
            centroid += p
        centroid /= float(shape.size())
        var optional := false
        for o in _optional: optional = optional or centroid.distance_to(o) < 600.0
        _tilted.append(tilted)
        _centroids.append(centroid)
        _optional_shape.append(optional)
    _shapes_source = polygons.size()

func _draw() -> void:
    _bounds_cache = _current_bounds()
    _fit_cache = _fit()
    var fit := _fit_cache
    var current := stage.current_step if stage else 0
    _floor_key = _floor_projection_key(fit, current)
    # Faint deck grid for depth.
    for i in range(-8, 9):
        var a := fit * _tilt(_bounds_cache.get_center() + Vector2(i * 700.0, -3000.0))
        var b := fit * _tilt(_bounds_cache.get_center() + Vector2(i * 700.0, 3000.0))
        draw_line(a, b, Color(0.4, 0.6, 0.65, 0.05), 1.0)
    var polygons := _polygons()
    if polygons.is_empty():
        for i in range(_route.size() - 1):
            draw_line(_map(_route[i]), _map(_route[i + 1]), Color("607983"), 3.0)
    var current_centre := _route[current] if current < _route.size() else Vector2.INF
    var thickness := Vector2(0, 3.0 * clampf(_zoom, 1.0, 2.0))
    # Point + thickness for every projected point (identity basis, exact).
    var raise := Transform2D(Vector2.RIGHT, Vector2.DOWN, thickness)
    _ensure_shapes(polygons)
    for index in range(_tilted.size()):
        var projected: PackedVector2Array = fit * _tilted[index]
        var centroid := _centroids[index]
        var lit := current_centre.is_finite() and centroid.distance_to(current_centre) < 700.0
        var optional := _optional_shape[index]
        var side: PackedVector2Array = raise * projected
        draw_colored_polygon(side, Color(0.02, 0.05, 0.06, 0.95))
        var face := Color(0.12, 0.26, 0.3, 0.95) if lit else (Color(0.2, 0.16, 0.09, 0.9) if optional else Color(0.08, 0.14, 0.17, 0.92))
        draw_colored_polygon(projected, face)
        var outline := projected.duplicate()
        outline.append(projected[0])
        draw_polyline(outline, Color(0.36, 0.9, 0.95, 0.85) if lit else (Color(0.85, 0.62, 0.3, 0.7) if optional else Color(0.45, 0.6, 0.65, 0.45)), 1.0, true)

## Markers layer (child), redrawn every frame.
func _draw_markers() -> void:
    _bounds_cache = _current_bounds()
    _fit_cache = _fit()
    var current := stage.current_step if stage else 0
    # The floors follow the same projection; redraw them in this frame when it moved.
    if _floor_projection_key(_fit_cache, current) != _floor_key:
        queue_redraw()
    var current_centre := _route[current] if current < _route.size() else Vector2.INF
    var layer := _markers
    # Objective marker: pulsing cyan diamond over the current room.
    if current_centre.is_finite():
        var m := _map(current_centre)
        var pulse := 0.6 + 0.4 * sin(_time * 3.0)
        var r := 5.0
        layer.draw_colored_polygon(PackedVector2Array([m + Vector2(0, -r), m + Vector2(r, 0), m + Vector2(0, r), m + Vector2(-r, 0)]), Color(0.35, 0.95, 1.0, 0.9))
        layer.draw_arc(m, 9.0 + pulse * 2.0, 0.0, TAU, 24, Color(0.35, 0.95, 1.0, 0.35 * pulse), 1.5, true)
    for o in _optional:
        var m := _map(o)
        layer.draw_colored_polygon(PackedVector2Array([m + Vector2(0, -4), m + Vector2(4, 0), m + Vector2(0, 4), m + Vector2(-4, 0)]), Color(0.95, 0.68, 0.3, 0.9))
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and node.health > 0.0:
            var ep := _map(node.global_position)
            layer.draw_circle(ep, 2.6, Color("f0596a"))
    if stage and stage.squad:
        for member in stage.squad.operators:
            if member != stage.squad.get_active_operator() and not member.is_downed():
                layer.draw_circle(_map(member.global_position), 2.0, Color(0.75, 0.85, 0.88, 0.8))
        var active := stage.squad.get_active_operator()
        if active:
            var p := _map(active.global_position)
            var d := _tilt(active.aim_world).normalized()
            if d.length_squared() < 0.01: d = Vector2.RIGHT
            var side := Vector2(-d.y, d.x)
            layer.draw_circle(p, 8.0, Color(0.25, 0.86, 0.92, 0.16))
            layer.draw_arc(p, 8.0, 0.0, TAU, 24, Color(0.35, 0.95, 1.0, 0.8), 1.4, true)
            layer.draw_colored_polygon(PackedVector2Array([p + d * 6.5, p - d * 4.0 + side * 3.8, p - d * 4.0 - side * 3.8]), Color("69e5ef"))

func debug_diagonal_route() -> bool:
    for i in range(_route.size()-1):
        var delta := _route[i+1]-_route[i]
        if absf(delta.y)<80.0:
            return false
    return true
