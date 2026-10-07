extends SceneTree

const PROP := preload("res://scripts/missions/site7_environment_prop.gd")
var failures: Array[String] = []

func _init() -> void:
    call_deferred("run")

func check(condition: bool, label: String) -> void:
    if not condition:
        failures.append(label)
        push_error(label)

func run() -> void:
    var image := Image.create(64, 64, false, Image.FORMAT_RGBA8)
    image.fill(Color.TRANSPARENT)
    for x in range(30, 34):
        for y in range(30, 34):
            image.set_pixel(x, y, Color.WHITE)
    var prop := PROP.new() as StaticBody2D
    root.add_child(prop)
    prop.configure(ImageTexture.create_from_image(image), image, {
        "projected_width_px":64,
        "root_px":[0, 0],
        "ground_px":[[0, 0], [63, 0], [63, 63], [0, 63]]
    }, 64.0)
    prop.set_active(true)
    await process_frame

    var hit: Vector2 = prop.projectile_hit(Vector2(-1000, 31), Vector2(1000, 31))
    check(hit.is_finite() and absf(hit.x - 30.0) <= 1.0, "long ray hits exact alpha silhouette")
    check(prop.last_projectile_samples <= 67, "long ray scans only clipped image")
    hit = prop.projectile_hit(Vector2(1000, 31), Vector2(-1000, 31))
    check(hit.is_finite() and absf(hit.x - 33.0) <= 1.0, "reverse ray hits same silhouette")
    hit = prop.projectile_hit(Vector2(-1000, 10), Vector2(1000, 10))
    check(not hit.is_finite(), "transparent row does not block")
    hit = prop.projectile_hit(Vector2(-1000, -10), Vector2(1000, -10))
    check(not hit.is_finite() and prop.last_projectile_samples == 0, "off-image ray performs no alpha reads")

    print("SITE7_COVER_ALPHA_CLIP: %s / %d checks" % ["PASS" if failures.is_empty() else "FAIL", 5])
    prop.queue_free()
    quit(0 if failures.is_empty() else 1)
