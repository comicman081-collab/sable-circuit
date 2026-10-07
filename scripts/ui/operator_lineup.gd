extends Control
class_name OperatorLineup
## Title-screen squad lineup built from the approved Motion Studio idle frames.
## Only presentation is added (rim light, scan band, breathing, floor shadow);
## the character pixels themselves are drawn unmodified underneath.

const RIM_SHADER := """
shader_type canvas_item;
uniform vec4 rim_color : source_color = vec4(0.42, 0.95, 0.9, 1.0);
uniform float rim_strength = 0.85;
uniform vec2 light_dir = vec2(0.85, -0.4);
uniform float shade = 1.0;
uniform float reveal = 1.0;
uniform float scan_offset = 0.0;
void fragment() {
    vec4 c = texture(TEXTURE, UV);
    vec2 step_uv = normalize(light_dir) * TEXTURE_PIXEL_SIZE * 6.0;
    float rim = clamp(c.a - texture(TEXTURE, UV + step_uv).a, 0.0, 1.0);
    vec3 col = c.rgb * shade + rim_color.rgb * rim * rim_strength;
    float band = fract(TIME * 0.09 + scan_offset);
    col += rim_color.rgb * smoothstep(0.008, 0.0, abs(UV.y - band)) * 0.14 * step(0.5, c.a);
    float lit = smoothstep(0.0, 1.0, reveal * 1.25 - (1.0 - UV.y) * 0.25);
    COLOR = vec4(mix(rim_color.rgb * rim * 0.6, col, lit), c.a * clamp(reveal * 2.0, 0.0, 1.0));
}
"""

# Order is back to front. x is a fraction of this control's width; feet are
# fractions of its height. ASTER leads at the front, matching the squad order.
const MEMBERS := [
    {"id": "rook", "dir": "SE", "x": 0.2, "feet": 0.93, "scale": 0.6, "shade": 0.78, "rim": Color(0.98, 0.72, 0.36), "phase": 0.0, "delay": 0.35},
    {"id": "mica", "dir": "SW", "x": 0.82, "feet": 0.945, "scale": 0.6, "shade": 0.8, "rim": Color(0.42, 0.95, 0.9), "phase": 2.1, "delay": 0.55},
    {"id": "aster", "dir": "S", "x": 0.5, "feet": 1.0, "scale": 0.7, "shade": 1.0, "rim": Color(0.55, 0.85, 1.0), "phase": 1.0, "delay": 0.15},
]
const ROOT := Vector2(384.0, 716.0)

var _sprites: Array[Sprite2D] = []
var _materials: Array[ShaderMaterial] = []
var _time := 0.0
var parallax := Vector2.ZERO

func _init() -> void:
    name = "OperatorLineup"
    mouse_filter = Control.MOUSE_FILTER_IGNORE

func _ready() -> void:
    var shader := Shader.new()
    shader.code = RIM_SHADER
    for member: Dictionary in MEMBERS:
        var frame := MenuFx.operator_idle(str(member.id), str(member.dir))
        if frame.is_empty():
            continue
        var sprite := Sprite2D.new()
        sprite.name = "Lineup_" + str(member.id).to_upper()
        sprite.texture = frame.texture
        sprite.centered = false
        sprite.offset = -ROOT / float(frame.scale)
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
        sprite.set_meta("base_scale", float(member.scale) * float(frame.scale))
        sprite.set_meta("member", member)
        var material := ShaderMaterial.new()
        material.shader = shader
        material.set_shader_parameter("rim_color", member.rim)
        material.set_shader_parameter("shade", member.shade)
        material.set_shader_parameter("reveal", 0.0)
        material.set_shader_parameter("scan_offset", float(member.phase) * 0.31)
        sprite.material = material
        add_child(sprite)
        _sprites.append(sprite)
        _materials.append(material)
        var reveal := create_tween()
        reveal.tween_interval(float(member.delay))
        reveal.tween_method(func(value: float) -> void: material.set_shader_parameter("reveal", value), 0.0, 1.0, 1.6).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)

func _process(delta: float) -> void:
    _time += delta
    for sprite in _sprites:
        var member: Dictionary = sprite.get_meta("member")
        var base_scale := float(sprite.get_meta("base_scale"))
        # Breathing is anchored at the feet (the atlas root sits at the origin).
        var breath := 1.0 + 0.0045 * sin(_time * 1.35 + float(member.phase))
        sprite.scale = Vector2(base_scale, base_scale * breath)
        var depth := 0.4 + 0.6 * float(member.scale) / 0.7
        sprite.position = Vector2(size.x * float(member.x), size.y * float(member.feet)) - parallax * depth
    queue_redraw()

func _draw() -> void:
    # Backlight separates the squad from the dark chamber behind it.
    var pulse := 0.85 + 0.15 * sin(_time * 0.6)
    var glow_center := Vector2(size.x * 0.52, size.y * 0.52) - parallax * 0.3
    _ellipse(glow_center, Vector2(400, 300), Color(0.36, 0.3, 0.75, 0.16 * pulse), Color(0.36, 0.3, 0.75, 0.0))
    _ellipse(glow_center + Vector2(0, 40), Vector2(240, 220), Color(0.35, 0.9, 0.88, 0.1 * pulse), Color(0.35, 0.9, 0.88, 0.0))
    for sprite in _sprites:
        var member: Dictionary = sprite.get_meta("member")
        var radius := Vector2(150.0, 26.0) * float(member.scale) / 0.7
        _ellipse(sprite.position + Vector2(0, 2), radius, Color(0, 0, 0, 0.62), Color(0, 0, 0, 0.0))
        _ellipse(sprite.position + Vector2(0, 4), radius * Vector2(1.5, 1.3), Color(member.rim, 0.09), Color(member.rim, 0.0))

func _ellipse(center: Vector2, radius: Vector2, inner: Color, outer: Color) -> void:
    var points := PackedVector2Array([center])
    var colors := PackedColorArray([inner])
    for i in range(33):
        var angle := TAU * float(i) / 32.0
        points.append(center + Vector2(cos(angle) * radius.x, sin(angle) * radius.y))
        colors.append(outer)
    for i in range(1, 33):
        draw_polygon(PackedVector2Array([points[0], points[i], points[i + 1 if i < 32 else 1]]),
            PackedColorArray([colors[0], colors[i], colors[i + 1 if i < 32 else 1]]))

func debug_member_count() -> int:
    return _sprites.size()
