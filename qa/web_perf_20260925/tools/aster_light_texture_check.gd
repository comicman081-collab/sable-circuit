extends SceneTree
## The shared ASTER projectile light texture has the same pixels as the per-shot texture
## the committed code built (same gradient and fill settings, built here the old way),
## and two projectiles' lights use one texture.
const PROJECTILE := preload("res://scripts/combat/prototype_projectile.gd")

func _init(): call_deferred("_run")

func _old_texture() -> GradientTexture2D:
    var gradient := Gradient.new()
    gradient.offsets = PackedFloat32Array([0.0, 0.28, 1.0])
    gradient.colors = PackedColorArray([
        Color(1.0, 0.92, 0.70, 1.0),
        Color(1.0, 0.46, 0.12, 0.46),
        Color(0.12, 0.72, 0.86, 0.0),
    ])
    var texture := GradientTexture2D.new()
    texture.width = 128
    texture.height = 64
    texture.fill = GradientTexture2D.FILL_RADIAL
    texture.fill_from = Vector2(0.5, 0.5)
    texture.fill_to = Vector2(1.0, 0.5)
    texture.gradient = gradient
    return texture

func _run():
    var a = PROJECTILE.new()
    var b = PROJECTILE.new()
    var la: PointLight2D = a._make_aster_projectile_light()
    var lb: PointLight2D = b._make_aster_projectile_light()
    var old := _old_texture()
    await process_frame
    await process_frame
    var shared := la.texture == lb.texture
    var same_pixels: bool = la.texture.get_image().get_data() == old.get_image().get_data()
    print("ASTER_LIGHT_TEXTURE shared=%s same_pixels=%s size=%s" % [shared, same_pixels, la.texture.get_size()])
    print("ASTER_LIGHT_TEXTURE: %s" % ("PASS" if shared and same_pixels else "FAIL"))
    la.free(); lb.free(); a.free(); b.free()
    quit()
