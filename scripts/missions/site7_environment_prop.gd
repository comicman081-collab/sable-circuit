extends StaticBody2D
## Licensed GLB-derived static prop. Collision is ground-only; bullets test its
## actual visible alpha, so invisible image margins never become cover.

var sprite: Sprite2D
## Alpha for bullet tests: the source image, or only its visible box (alpha_region) of it.
var alpha_image: Image
var alpha_region := Rect2i()
var source_size := Vector2i()
## Source-pixel space of the full render, as the art sprite had it before the GPU copy
## was reduced; bullet tests read alpha through it so their results do not change.
var _source_space: Node2D
var ground: PackedVector2Array
var active := false
var blocked_player_shots := 0
var blocked_enemy_shots := 0
var last_projectile_samples := 0

func record_projectile_block(source: Node) -> void:
    if source is OperatorActor: blocked_player_shots += 1
    elif source is EnemyActor: blocked_enemy_shots += 1

## texture may be a reduced copy of the source's visible box `region`; alpha_image then
## holds that box at full source resolution. Hit tests always run in source pixels.
func configure(texture: Texture2D, source_image: Image, row: Dictionary, width: float, region := Rect2i(), full_size := Vector2i()) -> void:
    alpha_image = source_image
    alpha_region = region if region.has_area() else Rect2i(Vector2i.ZERO, source_image.get_size())
    source_size = full_size if full_size != Vector2i() else source_image.get_size()
    collision_layer = 0
    collision_mask = 0
    sprite = Sprite2D.new()
    sprite.name = "LicensedPropArt"
    sprite.texture = texture
    sprite.centered = false
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
    sprite.modulate = Color(0.76,0.84,0.86)
    var factor := width / float(row.projected_width_px)
    var anchor := Vector2(float(row.root_px[0]), float(row.root_px[1]))
    sprite.scale = factor * Vector2(alpha_region.size) / texture.get_size()
    sprite.position = (Vector2(alpha_region.position) - anchor) * factor
    add_child(sprite)
    _source_space = Node2D.new()
    _source_space.name = "SourcePixelSpace"
    _source_space.scale = Vector2.ONE * factor
    _source_space.position = -anchor * factor
    add_child(_source_space)
    for point: Array in row.ground_px:
        ground.append((Vector2(float(point[0]), float(point[1])) - anchor) * factor)
    var shadow := Polygon2D.new()
    shadow.name = "GroundContactShadow"
    shadow.polygon = ground
    shadow.position = Vector2(3,4)
    shadow.color = Color(0,0,0,0.28)
    shadow.z_as_relative = false
    shadow.z_index = -40
    add_child(shadow)
    var collider := CollisionPolygon2D.new()
    collider.polygon = ground
    add_child(collider)
    add_to_group("sable_environment_cover")
    _cache_valid = false
    hide()

func set_active(value: bool) -> void:
    active = value
    visible = value
    collision_layer = 1 if value else 0
    z_as_relative = false
    z_index = preload("res://scripts/missions/site7_depth.gd").z_for(global_position.y)

## World boxes of the source image and of the ground footprint, cached per global
## transform (props are placed once, but a moved prop still recomputes them).
var _cached_xform := Transform2D()
var _cached_image_box := Rect2()
var _cached_ground_rect := Rect2()
var _cache_valid := false

func _refresh_world_cache() -> void:
    var xform := global_transform
    if _cache_valid and xform == _cached_xform: return
    var image_xform := _source_space.global_transform
    var size := Vector2(source_size)
    var box := Rect2(image_xform * Vector2.ZERO, Vector2.ZERO)
    box = box.expand(image_xform * Vector2(size.x, 0.0)).expand(image_xform * size).expand(image_xform * Vector2(0.0, size.y))
    # 2 px of slack: only rays clearly off the image skip the exact clip below.
    _cached_image_box = box.grow(2.0)
    var rect := Rect2()
    if not ground.is_empty():
        rect = Rect2(to_global(ground[0]), Vector2.ZERO)
        for point in ground: rect = rect.expand(to_global(point))
    _cached_ground_rect = rect
    _cached_xform = xform
    _cache_valid = true

## World bounding rect of the ground footprint, as CoverNavigation builds its obstacles.
func ground_world_rect() -> Rect2:
    _refresh_world_cache()
    return _cached_ground_rect

func projectile_hit(from: Vector2, to: Vector2) -> Vector2:
    last_projectile_samples = 0
    if not active: return Vector2.INF
    _refresh_world_cache()
    if (minf(from.x, to.x) > _cached_image_box.end.x or maxf(from.x, to.x) < _cached_image_box.position.x
            or minf(from.y, to.y) > _cached_image_box.end.y or maxf(from.y, to.y) < _cached_image_box.position.y):
        return Vector2.INF
    if not is_visible_in_tree(): return Vector2.INF
    # Clip the ray to the image BEFORE reading alpha.  A distant muzzle used to
    # scan thousands of empty pixels before reaching one nearby cover image;
    # several allies/enemies repeated that work each physics tick in WebGL.
    # Retain <= one source pixel per step inside the image so thin silhouette
    # edges still block both player and enemy shots.
    var a := _source_space.to_local(from)
    var b := _source_space.to_local(to)
    var bounds := Rect2(Vector2.ZERO, Vector2(source_size))
    var interval := _image_segment_interval(a,b,bounds)
    if not interval.is_finite(): return Vector2.INF
    var start := a.lerp(b,interval.x)
    var end := a.lerp(b,interval.y)
    var steps := maxi(1,int(ceil(start.distance_to(end))))
    for i in range(steps + 1):
        last_projectile_samples += 1
        var t := lerpf(interval.x,interval.y,float(i)/float(steps))
        var point := a.lerp(b,t)
        var pixel := Vector2i(int(point.x),int(point.y))
        if bounds.has_point(point) and alpha_region.has_point(pixel) and alpha_image.get_pixel(pixel.x-alpha_region.position.x,pixel.y-alpha_region.position.y).a >= 0.5:
            return from.lerp(to,t)
    return Vector2.INF

func _image_segment_interval(a: Vector2, b: Vector2, bounds: Rect2) -> Vector2:
    # Liang-Barsky clipping in source-image coordinates. INF means no overlap.
    var delta := b-a
    var p := [-delta.x,delta.x,-delta.y,delta.y]
    var q := [a.x-bounds.position.x,bounds.end.x-a.x,
        a.y-bounds.position.y,bounds.end.y-a.y]
    var enter := 0.0
    var leave := 1.0
    for edge in range(4):
        if is_zero_approx(float(p[edge])):
            if float(q[edge]) < 0.0: return Vector2.INF
            continue
        var ratio := float(q[edge])/float(p[edge])
        if float(p[edge]) < 0.0: enter = maxf(enter,ratio)
        else: leave = minf(leave,ratio)
        if enter > leave: return Vector2.INF
    return Vector2(enter,leave)
