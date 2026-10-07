extends SceneTree
## The kArchive cover props now keep only their visible box at half size on the GPU and
## that box at full resolution for bullet tests. Every ray must hit exactly as it did with
## the full 1920x1080 texture and alpha, with the same sample count, and the art must
## land on the same screen rectangle.

const PROP := preload("res://scripts/missions/site7_environment_prop.gd")
const PROPS := preload("res://scripts/missions/site7_environment_props.gd")
const CONFIG := "res://data/visual/site7_environment_props.json"
const RAYS := 1500

var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
    var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(config.spec)))
    var before_bytes := 0
    var after_bytes := 0
    for id: String in spec.props:
        var asset: Dictionary = spec.props[id]
        var image := Image.new()
        image.load_png_from_buffer(FileAccess.get_file_as_bytes(str(asset.texture)))
        var reduced := PROPS.reduced_prop_texture(image)
        var width := 200.0
        var legacy := _prop(ImageTexture.create_from_image(image), image, asset, width, Rect2i(), Vector2i())
        var current := _prop(reduced.texture, reduced.alpha, asset, width, reduced.region, reduced.source_size)
        before_bytes += image.get_width() * image.get_height() * 4 * 2
        after_bytes += int(reduced.texture.get_width() * reduced.texture.get_height() * 4 * 4 / 3.0) + reduced.alpha.get_data().size()

        var region: Rect2i = reduced.region
        var legacy_corner: Vector2 = legacy.sprite.get_global_transform() * Vector2(region.position)
        var current_corner: Vector2 = current.sprite.get_global_transform() * Vector2.ZERO
        var legacy_far: Vector2 = legacy.sprite.get_global_transform() * Vector2(region.end)
        var current_far: Vector2 = current.sprite.get_global_transform() * Vector2(reduced.texture.get_size())
        _check(legacy_corner.distance_to(current_corner) < 0.01 and legacy_far.distance_to(current_far) < 0.01, id + " art covers the same screen rectangle")

        var rng := RandomNumberGenerator.new()
        rng.seed = hash(id)
        var span := width * 1.4
        var same := 0
        var blocked := 0
        for i in range(RAYS):
            var from := Vector2(rng.randf_range(-span, span), rng.randf_range(-span, span))
            var to := Vector2(rng.randf_range(-span, span), rng.randf_range(-span, span))
            var reference := _previous_hit(legacy, from, to)
            var a: Vector2 = reference.hit
            var b: Vector2 = current.projectile_hit(from, to)
            if a.is_finite(): blocked += 1
            if ((not a.is_finite() and not b.is_finite()) or (a.is_finite() and b.is_finite() and a.distance_to(b) < 0.001)) and int(reference.samples) == current.last_projectile_samples:
                same += 1
        _check(same == RAYS, "%s: %d/%d rays hit identically" % [id, same, RAYS])
        _check(blocked > RAYS / 20, "%s: the ray set actually crosses the silhouette (%d blocked)" % [id, blocked])
        _check(reduced.texture.get_width() * reduced.texture.get_height() * 5 < image.get_width() * image.get_height(), id + " GPU copy is under a fifth of the source pixels")
        legacy.free()
        current.free()
    _check(after_bytes * 4 < before_bytes, "cover memory drops to under a quarter (%.1f MB -> %.1f MB)" % [before_bytes / 1048576.0, after_bytes / 1048576.0])
    if failures.is_empty():
        print("COVER_TEXTURE_REDUCTION_SMOKE: PASS (%d checks) %.1f MB -> %.1f MB" % [checks, before_bytes / 1048576.0, after_bytes / 1048576.0])
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

## The bullet test as it was before the reduction: full source alpha read through the
## full-size sprite's own transform.
func _previous_hit(prop: StaticBody2D, from: Vector2, to: Vector2) -> Dictionary:
    var samples := 0
    var image: Image = prop.alpha_image
    var a: Vector2 = prop.sprite.to_local(from)
    var b: Vector2 = prop.sprite.to_local(to)
    var bounds := Rect2(Vector2.ZERO, Vector2(image.get_size()))
    var interval: Vector2 = prop._image_segment_interval(a, b, bounds)
    if not interval.is_finite(): return {"hit": Vector2.INF, "samples": 0}
    var start := a.lerp(b, interval.x)
    var end := a.lerp(b, interval.y)
    var steps := maxi(1, int(ceil(start.distance_to(end))))
    for i in range(steps + 1):
        samples += 1
        var t := lerpf(interval.x, interval.y, float(i) / float(steps))
        var point := a.lerp(b, t)
        if bounds.has_point(point) and image.get_pixel(int(point.x), int(point.y)).a >= 0.5:
            return {"hit": from.lerp(to, t), "samples": samples}
    return {"hit": Vector2.INF, "samples": samples}

func _prop(texture: Texture2D, alpha: Image, asset: Dictionary, width: float, region: Rect2i, source_size: Vector2i) -> StaticBody2D:
    var prop := PROP.new() as StaticBody2D
    root.add_child(prop)
    prop.global_position = Vector2(37.25, -11.5)
    prop.configure(texture, alpha, asset, width, region, source_size)
    prop.set_active(true)
    return prop

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)
