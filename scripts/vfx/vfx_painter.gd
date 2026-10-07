extends RefCounted
class_name VfxPainter
## Collects one frame of code-drawn VFX as a single triangle list with per-vertex colour
## and hands it to the renderer in one call. Separate draw_circle / draw_colored_polygon
## calls were one GPU command each and halved native combat FPS (qa/vfx_perf_20260925/).
## Soft shapes fade to zero alpha at their rim through the vertex colours, so glows,
## rings and beams need no texture and batch with everything else.
##
## Every shape is built in GDScript each frame, so round soft shapes (glow, dot, puff)
## are one textured quad whose alpha comes from a small procedural profile atlas; lines,
## rings and fragments stay as coloured triangles (a streak 2-4, a ring 4 x `segments`,
## about 1 us and 25 us to build). A frame is still at most two draw commands: the
## textured quads first, the plain triangles over them.

var points := PackedVector2Array()
var colors := PackedColorArray()
var sprite_points := PackedVector2Array()
var sprite_colors := PackedColorArray()
var sprite_uvs := PackedVector2Array()
var _filtered := RID()

static var _unit_circles := {}
static var _additive: CanvasItemMaterial
static var _atlas: ImageTexture
static var _noise := PackedFloat32Array()

## Profile atlas cells (quarter-width each): alpha only, white colour.
const CELL_GLOW := 0
const CELL_PUFF := 1
const CELL_CONE := 2
const ATLAS_CELL := 128
const NOISE_SIZE := 4096

func clear() -> void:
    points.clear()
    colors.clear()
    sprite_points.clear()
    sprite_colors.clear()
    sprite_uvs.clear()

func is_empty() -> bool:
    return points.is_empty() and sprite_points.is_empty()

func triangle_count() -> int:
    return (points.size() + sprite_points.size()) / 3

## Adds this frame's shapes to a canvas item. Call inside _draw for the node's own
## item, or after canvas_item_clear for a layer made with make_layer.
func flush(item: RID) -> void:
    if not sprite_points.is_empty():
        if item != _filtered:
            # The profiles are magnified many times; nearest filtering would band them.
            RenderingServer.canvas_item_set_default_texture_filter(item, RenderingServer.CANVAS_ITEM_TEXTURE_FILTER_LINEAR)
            _filtered = item
        RenderingServer.canvas_item_add_triangle_array(item, PackedInt32Array(), sprite_points, sprite_colors, sprite_uvs,
            PackedInt32Array(), PackedFloat32Array(), profile_atlas().get_rid())
    if not points.is_empty():
        RenderingServer.canvas_item_add_triangle_array(item, PackedInt32Array(), points, colors)

## White texture whose alpha holds the radial profiles, one per cell:
## glow  1 at the centre, 0.45 at 30 % of the radius, 0 at the rim;
## puff  1 at the centre, 0.92 at 55 %, 0 at the rim (a body, not light);
## cone  1 at the centre falling straight to 0 at the rim (dots, embers).
## Every cell is clear on its border, so bilinear filtering never bleeds between cells.
static func profile_atlas() -> ImageTexture:
    if _atlas != null:
        return _atlas
    var image := Image.create_empty(ATLAS_CELL * 4, ATLAS_CELL, false, Image.FORMAT_RGBA8)
    var half := ATLAS_CELL * 0.5
    for cell in range(3):
        for y in range(ATLAS_CELL):
            for x in range(ATLAS_CELL):
                var r := Vector2(float(x) + 0.5 - half, float(y) + 0.5 - half).length() / (half - 1.0)
                var a := 0.0
                if r < 1.0:
                    match cell:
                        CELL_GLOW: a = 1.0 - 0.55 * r / 0.3 if r < 0.3 else 0.45 * (1.0 - (r - 0.3) / 0.7)
                        CELL_PUFF: a = 1.0 - 0.08 * r / 0.55 if r < 0.55 else 0.92 * (1.0 - (r - 0.55) / 0.45)
                        CELL_CONE: a = 1.0 - r
                image.set_pixel(cell * ATLAS_CELL + x, y, Color(1.0, 1.0, 1.0, clampf(a, 0.0, 1.0)))
    _atlas = ImageTexture.create_from_image(image)
    return _atlas

## One profile quad: `ax`/`ay` are the half-extent vectors of its two axes. With a
## distinct `heart` the quad becomes a four-triangle fan whose centre takes that colour.
func _sprite(center: Vector2, ax: Vector2, ay: Vector2, cell: int, color: Color, heart := Color(0, 0, 0, 0)) -> void:
    var u0 := float(cell) * 0.25
    var u1 := u0 + 0.25
    var a := center - ax - ay
    var b := center + ax - ay
    var c := center + ax + ay
    var d := center - ax + ay
    var ua := Vector2(u0, 0.0)
    var ub := Vector2(u1, 0.0)
    var uc := Vector2(u1, 1.0)
    var ud := Vector2(u0, 1.0)
    if heart.a <= 0.0:
        sprite_points.append(a); sprite_points.append(b); sprite_points.append(c)
        sprite_points.append(a); sprite_points.append(c); sprite_points.append(d)
        for i in range(6): sprite_colors.append(color)
        sprite_uvs.append(ua); sprite_uvs.append(ub); sprite_uvs.append(uc)
        sprite_uvs.append(ua); sprite_uvs.append(uc); sprite_uvs.append(ud)
        return
    var um := Vector2(u0 + 0.125, 0.5)
    _fan(center, a, b, um, ua, ub, heart, color)
    _fan(center, b, c, um, ub, uc, heart, color)
    _fan(center, c, d, um, uc, ud, heart, color)
    _fan(center, d, a, um, ud, ua, heart, color)

func _fan(center: Vector2, p: Vector2, q: Vector2, um: Vector2, up: Vector2, uq: Vector2, heart: Color, color: Color) -> void:
    sprite_points.append(center); sprite_points.append(p); sprite_points.append(q)
    sprite_colors.append(heart); sprite_colors.append(color); sprite_colors.append(color)
    sprite_uvs.append(um); sprite_uvs.append(up); sprite_uvs.append(uq)

## A child canvas item of `parent` for shapes that need the other blend mode (smoke and
## scorch darken, so they cannot sit in an additive node). Free it with free_layer.
static func make_layer(parent: CanvasItem, additive: bool, behind := false) -> RID:
    var item := RenderingServer.canvas_item_create()
    RenderingServer.canvas_item_set_parent(item, parent.get_canvas_item())
    RenderingServer.canvas_item_set_draw_behind_parent(item, behind)
    if additive:
        RenderingServer.canvas_item_set_material(item, additive_material().get_rid())
    return item

static func free_layer(item: RID) -> void:
    if item.is_valid():
        RenderingServer.free_rid(item)

static func additive_material() -> CanvasItemMaterial:
    if _additive == null:
        _additive = CanvasItemMaterial.new()
        _additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
    return _additive

## Deterministic 0..1 noise for a seed and an index, so an effect keeps its layout
## from frame to frame without storing per-particle state. Effects call this a few
## hundred times a frame, so it reads a table filled once instead of hashing each time.
static func rand(seed_value: int, index: int) -> float:
    if _noise.is_empty():
        _noise.resize(NOISE_SIZE)
        for i in range(NOISE_SIZE):
            _noise[i] = fposmod(sin(float(i) * 12.9898 + 0.731) * 43758.5453, 1.0)
    return _noise[(seed_value * 7919 + index) & (NOISE_SIZE - 1)]

## The noise table itself, for effects that read it directly in hot loops:
## `table[(seed * 7919 + index) & (NOISE_SIZE - 1)]` equals `rand(seed, index)`.
static func noise() -> PackedFloat32Array:
    rand(0, 0)
    return _noise

static func ease_out(value: float) -> float:
    var c := clampf(value, 0.0, 1.0)
    return 1.0 - (1.0 - c) * (1.0 - c) * (1.0 - c)

static func ease_in(value: float) -> float:
    var c := clampf(value, 0.0, 1.0)
    return c * c

## 1 until `start`, falling linearly to 0 at `finish`.
static func fade_window(t: float, start: float, finish: float) -> float:
    if t <= start: return 1.0
    if t >= finish: return 0.0
    return 1.0 - (t - start) / (finish - start)

static func unit_circle(segments: int) -> PackedVector2Array:
    var cached: Variant = _unit_circles.get(segments)
    if cached != null:
        return cached
    var ring_points := PackedVector2Array()
    for i in range(segments + 1):
        ring_points.append(Vector2.from_angle(TAU * float(i) / float(segments)))
    _unit_circles[segments] = ring_points
    return ring_points

func tri(a: Vector2, b: Vector2, c: Vector2, color: Color) -> void:
    points.append(a)
    points.append(b)
    points.append(c)
    colors.append(color)
    colors.append(color)
    colors.append(color)

func tri3(a: Vector2, b: Vector2, c: Vector2, ca: Color, cb: Color, cc: Color) -> void:
    points.append(a)
    points.append(b)
    points.append(c)
    colors.append(ca)
    colors.append(cb)
    colors.append(cc)

func quad(a: Vector2, b: Vector2, c: Vector2, d: Vector2, color: Color) -> void:
    tri(a, b, c, color)
    tri(a, c, d, color)

## Quad with its own colour per corner (a-b-c-d in order round the edge).
func quad4(a: Vector2, b: Vector2, c: Vector2, d: Vector2, ca: Color, cb: Color, cc: Color, cd: Color) -> void:
    tri3(a, b, c, ca, cb, cc)
    tri3(a, c, d, ca, cc, cd)

func disc(center: Vector2, radius: float, color: Color, segments := 10) -> void:
    if color.a <= 0.003 or radius <= 0.2:
        return
    var unit := unit_circle(segments)
    for i in range(segments):
        tri(center, center + unit[i] * radius, center + unit[i + 1] * radius, color)

## Small soft point (ember, mote): colour in the middle, clear at the rim.
## `segments` is kept for callers; the shape is one profile quad.
func dot(center: Vector2, radius: float, color: Color, _segments := 6) -> void:
    if color.a <= 0.003 or radius <= 0.2:
        return
    _sprite(center, Vector2(radius, 0.0), Vector2(0.0, radius), CELL_CONE, color)

## Soft round glow: full colour in the middle, 45 % at 30 % of the radius, clear at the rim.
func glow(center: Vector2, radius: float, color: Color, _segments := 10) -> void:
    if color.a <= 0.003 or radius <= 0.2:
        return
    _sprite(center, Vector2(radius, 0.0), Vector2(0.0, radius), CELL_GLOW, color)

## Glow stretched to `radii`, its x axis turned to `angle`.
func ellipse_glow(center: Vector2, radii: Vector2, color: Color, _segments := 10, angle := 0.0) -> void:
    if color.a <= 0.003 or radii.x <= 0.2 or radii.y <= 0.2:
        return
    var ax := Vector2.from_angle(angle)
    _sprite(center, ax * radii.x, Vector2(-ax.y, ax.x) * radii.y, CELL_GLOW, color)

## Volume puff for fire and smoke: nearly solid to 55 % of the radius, then a soft edge,
## so overlapping puffs read as a body rather than as light. `core` recolours the centre
## (the hot heart of a fireball, the fire-lit face of smoke), fading to `color` at the
## rim; its alpha is ignored. `squash` flattens y.
func puff(center: Vector2, radius: float, color: Color, core := Color(0, 0, 0, 0), _segments := 10, squash := 1.0) -> void:
    if color.a <= 0.003 or radius <= 0.3:
        return
    var heart := Color(core, color.a) if core.a > 0.0 else Color(0, 0, 0, 0)
    _sprite(center, Vector2(radius, 0.0), Vector2(0.0, radius * squash), CELL_PUFF, color, heart)

## Soft ring: clear at radius ± width, full colour on the radius. `from`/`to` limit it
## to an arc (radians, clockwise on screen like draw_arc). `squash` flattens y.
func ring(center: Vector2, radius: float, width: float, color: Color, segments := 20, from := 0.0, to := TAU, squash := 1.0) -> void:
    if color.a <= 0.003 or radius <= 0.2 or width <= 0.05:
        return
    var inner := maxf(0.0, radius - width)
    var outer := radius + width
    var clear := Color(color, 0.0)
    var full_circle := is_equal_approx(to - from, TAU) and from == 0.0
    var unit := unit_circle(segments) if full_circle else PackedVector2Array()
    # Written out rather than through tri3: rings are the costliest shape per call.
    var i0 := Vector2.ZERO
    var m0 := Vector2.ZERO
    var o0 := Vector2.ZERO
    for i in range(segments + 1):
        var direction: Vector2 = unit[i] if full_circle else Vector2.from_angle(lerpf(from, to, float(i) / float(segments)))
        direction.y *= squash
        var i1 := center + direction * inner
        var m1 := center + direction * radius
        var o1 := center + direction * outer
        if i > 0:
            points.append(i0); points.append(i1); points.append(m1)
            points.append(i0); points.append(m1); points.append(m0)
            points.append(m0); points.append(m1); points.append(o1)
            points.append(m0); points.append(o1); points.append(o0)
            colors.append(clear); colors.append(clear); colors.append(color)
            colors.append(clear); colors.append(color); colors.append(color)
            colors.append(color); colors.append(color); colors.append(clear)
            colors.append(color); colors.append(clear); colors.append(clear)
        i0 = i1
        m0 = m1
        o0 = o1

## Soft elliptical ring with radii along its own axes, the x axis turned to `angle`
## (a coil ring seen edge-on, a ground ring under a body).
func oval_ring(center: Vector2, radii: Vector2, angle: float, width: float, color: Color, segments := 16) -> void:
    if color.a <= 0.003 or radii.x <= 0.2 or width <= 0.05:
        return
    var unit := unit_circle(segments)
    var ax := Vector2.from_angle(angle)
    var ay := Vector2(-ax.y, ax.x)
    var clear := Color(color, 0.0)
    var previous := Vector2.ZERO
    var previous_normal := Vector2.ZERO
    for i in range(segments + 1):
        var point: Vector2 = center + ax * (unit[i].x * radii.x) + ay * (unit[i].y * radii.y)
        var normal: Vector2 = (ax * unit[i].x / maxf(0.01, radii.x) + ay * unit[i].y / maxf(0.01, radii.y)).normalized() * width
        if i > 0:
            tri3(previous - previous_normal, point - normal, point, clear, clear, color)
            tri3(previous - previous_normal, point, previous, clear, color, color)
            tri3(previous, point, point + normal, color, color, clear)
            tri3(previous, point + normal, previous + previous_normal, color, clear, clear)
        previous = point
        previous_normal = normal

## Tracer / spark: sharp bright head, body widest near the head, tail fading to nothing.
func streak(tail: Vector2, head: Vector2, width: float, color: Color, core := false) -> void:
    var span := head - tail
    var length := span.length()
    if length <= 0.3 or color.a <= 0.003:
        return
    var side := Vector2(-span.y, span.x) / length * width
    var shoulder := tail + span * 0.72
    points.append(tail); points.append(shoulder + side); points.append(shoulder - side)
    points.append(shoulder + side); points.append(head); points.append(shoulder - side)
    colors.append(Color(color, 0.0)); colors.append(color); colors.append(color)
    colors.append(color); colors.append(color); colors.append(color)
    if core:
        var white := Color(1.0, 1.0, 1.0, minf(1.0, color.a))
        var inner := side * 0.36
        points.append(tail + span * 0.35); points.append(shoulder + inner); points.append(shoulder - inner)
        points.append(shoulder + inner); points.append(head); points.append(shoulder - inner)
        colors.append(Color(white, 0.0)); colors.append(white); colors.append(white)
        colors.append(white); colors.append(white); colors.append(white)

## Soft ribbon through `points` (oldest first) with a half-width and alpha per point.
## Neighbouring segments share their joint vertices, so a bending trail shows no gaps.
func ribbon(points: PackedVector2Array, widths: PackedFloat32Array, color: Color, alphas: PackedFloat32Array) -> void:
    var count := points.size()
    if count < 2 or color.a <= 0.003:
        return
    var previous_left := Vector2.ZERO
    var previous_right := Vector2.ZERO
    var previous_center := Vector2.ZERO
    var previous_color := color
    for i in range(count):
        var tangent := points[mini(count - 1, i + 1)] - points[maxi(0, i - 1)]
        if tangent.length_squared() < 0.0001:
            tangent = Vector2.RIGHT
        var normal := tangent.normalized().orthogonal() * widths[i]
        var center := points[i]
        var shade := Color(color, color.a * alphas[i])
        if i > 0:
            quad4(previous_left, center + normal, center, previous_center, Color(previous_color, 0.0), Color(shade, 0.0), shade, previous_color)
            quad4(previous_center, center, center - normal, previous_right, previous_color, shade, Color(shade, 0.0), Color(previous_color, 0.0))
        previous_left = center + normal
        previous_right = center - normal
        previous_center = center
        previous_color = shade

## Straight beam with soft edges: glow falls off to both sides, optional white core.
func beam(a: Vector2, b: Vector2, width: float, color: Color, core_alpha := 0.0) -> void:
    var span := b - a
    var length := span.length()
    if length <= 0.3 or color.a <= 0.003:
        return
    var side := Vector2(-span.y, span.x) / length
    var edge := Color(color, 0.0)
    var o := side * width
    var m := side * width * 0.35
    quad4(a + o, b + o, b + m, a + m, edge, edge, color, color)
    quad(a + m, b + m, b - m, a - m, color)
    quad4(a - m, b - m, b - o, a - o, color, color, edge, edge)
    if core_alpha > 0.003:
        var c := side * maxf(0.5, width * 0.13)
        quad(a + c, b + c, b - c, a - c, Color(1.0, 1.0, 1.0, minf(1.0, core_alpha)))

## Soft-edged strip whose alpha runs from alpha_a at `a` to alpha_b at `b`.
func fading_beam(a: Vector2, b: Vector2, width: float, color: Color, alpha_a: float, alpha_b: float) -> void:
    var span := b - a
    var length := span.length()
    if length <= 0.3 or color.a <= 0.003:
        return
    var side := Vector2(-span.y, span.x) / length * width
    var ca := Color(color, color.a * alpha_a)
    var cb := Color(color, color.a * alpha_b)
    var ea := Color(ca, 0.0)
    var eb := Color(cb, 0.0)
    quad4(a + side, b + side, b, a, ea, eb, cb, ca)
    quad4(a, b, b - side, a - side, ca, cb, eb, ea)

## Four-point star flare; the long arms lie along `axis`, the short ones across it.
func flare(center: Vector2, axis: Vector2, length: float, width: float, color: Color, cross := 0.5) -> void:
    if color.a <= 0.003 or length <= 0.5:
        return
    var along := axis.normalized()
    var across := Vector2(-along.y, along.x)
    streak(center - along * length * 0.1, center + along * length, width, color)
    streak(center + along * length * 0.1, center - along * length, width, color)
    streak(center - across * length * cross * 0.1, center + across * length * cross, width * 0.75, color)
    streak(center + across * length * cross * 0.1, center - across * length * cross, width * 0.75, color)

## Flat angular fragment (glass, metal, rock).
func shard(center: Vector2, angle: float, size: float, color: Color) -> void:
    if color.a <= 0.003 or size <= 0.2:
        return
    var axis := Vector2.from_angle(angle)
    var side := Vector2(-axis.y, axis.x)
    var tip := center + axis * size
    var heel := center - axis * size * 0.7
    tri(tip, center + side * size * 0.5, heel, color)
    tri(tip, heel, center - side * size * 0.38, color)

## Regular polygon outline made of soft beams (hex plates, target brackets).
func polygon_outline(center: Vector2, radius: float, sides: int, angle: float, width: float, color: Color, squash := 1.0) -> void:
    if color.a <= 0.003 or radius <= 0.5:
        return
    var previous := Vector2.ZERO
    for i in range(sides + 1):
        var corner := Vector2.from_angle(angle + TAU * float(i) / float(sides)) * radius
        corner.y *= squash
        if i > 0:
            beam(center + previous, center + corner, width, color)
        previous = corner

## Jagged electric arc from a to b; `seed_value` fixes its shape.
func bolt(a: Vector2, b: Vector2, segments: int, jitter: float, width: float, color: Color, seed_value: int) -> void:
    var span := b - a
    var length := span.length()
    if length <= 0.5 or color.a <= 0.003:
        return
    var side := Vector2(-span.y, span.x) / length
    var previous := a
    for i in range(1, segments + 1):
        var f := float(i) / float(segments)
        var offset := 0.0 if i == segments else (rand(seed_value, i) - 0.5) * 2.0 * jitter * sin(f * PI)
        var next := a + span * f + side * offset
        beam(previous, next, width, color, color.a * 0.8)
        previous = next
