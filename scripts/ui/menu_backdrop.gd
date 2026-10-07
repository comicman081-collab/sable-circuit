extends Control
class_name MenuBackdrop
## Slow Ken Burns drift over an existing Site-7 room plate, graded for menus,
## with a gentle mouse parallax. Presentation only; the plate bytes are unchanged.

var plate: TextureRect
var grade: ShaderMaterial
var drift_seconds := 42.0
var zoom_range := Vector2(1.07, 1.15)
var pan := Vector2(18.0, 8.0)
var parallax := 12.0
var _time := 0.0
var _mouse := Vector2.ZERO

func _init() -> void:
    name = "MenuBackdrop"
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    clip_contents = true

func setup(texture_path: String, settings: Dictionary = {}) -> MenuBackdrop:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    var base := ColorRect.new()
    base.color = MenuFx.DEEP
    base.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    base.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(base)
    plate = TextureRect.new()
    plate.name = "Plate"
    plate.texture = MenuFx.load_texture(texture_path)
    plate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    plate.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    plate.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
    plate.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
    plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
    plate.flip_h = bool(settings.get("flip_h", false))
    var shader := Shader.new()
    shader.code = MenuFx.GRADE_SHADER
    grade = ShaderMaterial.new()
    grade.shader = shader
    for key: String in settings:
        if key != "flip_h":
            grade.set_shader_parameter(key, settings[key])
    plate.material = grade
    add_child(plate)
    return self

func _process(delta: float) -> void:
    if plate == null:
        return
    _time += delta
    var k := 0.5 - 0.5 * cos(TAU * _time / drift_seconds)
    var target := Vector2.ZERO
    if size.x > 0.0 and size.y > 0.0:
        target = (get_local_mouse_position() - size * 0.5) / (size * 0.5)
        target = target.clamp(Vector2(-1, -1), Vector2(1, 1))
    _mouse = _mouse.lerp(target, 1.0 - exp(-delta * 2.2))
    plate.pivot_offset = size * 0.5
    plate.scale = Vector2.ONE * lerpf(zoom_range.x, zoom_range.y, k)
    plate.position = Vector2(lerpf(-pan.x, pan.x, k), lerpf(pan.y, -pan.y, k)) - _mouse * parallax

func mouse_offset() -> Vector2:
    return _mouse
