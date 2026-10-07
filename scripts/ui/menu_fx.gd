extends RefCounted
class_name MenuFx
## Shared cinematic menu layers. Everything is presentation built from art the
## project already ships (Site-7 room plates, Motion Studio idle atlases and
## portraits): grading, light, dust and type. No new source illustration.

const ACCENT := Color("5ee6da")
const AMBER := Color("f2b45a")
const DANGER := Color("ff6b5e")
const INK := Color("eaf6fb")
const MUTED := Color("8aa3b1")
const DIM := Color("5d7481")
const DEEP := Color("03070b")

const RAJDHANI := preload("res://assets/fonts/Rajdhani-Medium.ttf")
const NOTO_KR := preload("res://assets/fonts/NotoSansKR-Regular.otf")
const BATTLE_ART := "res://data/visual/site7_battle_art.json"
const ATLAS_ROOT := "res://motion_lab_v1/public/assets/atlas/"

const GRADE_SHADER := """
shader_type canvas_item;
uniform float exposure = 0.62;
uniform vec4 shadow_tint : source_color = vec4(0.10, 0.30, 0.40, 1.0);
uniform vec4 highlight_tint : source_color = vec4(1.0, 0.94, 0.88, 1.0);
uniform float saturation = 0.9;
uniform float vignette = 0.8;
uniform vec2 focus = vec2(0.62, 0.46);
uniform float left_shade = 0.5;
uniform float bottom_shade = 0.35;
void fragment() {
    vec4 c = texture(TEXTURE, UV);
    float l = dot(c.rgb, vec3(0.299, 0.587, 0.114));
    vec3 g = mix(vec3(l), c.rgb, saturation);
    g = mix(g * shadow_tint.rgb * 1.8, g * highlight_tint.rgb, smoothstep(0.05, 0.65, l));
    g *= exposure;
    g *= mix(1.0 - left_shade, 1.0, smoothstep(0.0, 0.62, SCREEN_UV.x));
    g *= mix(1.0 - bottom_shade, 1.0, smoothstep(1.0, 0.62, SCREEN_UV.y));
    g *= 1.0 - vignette * smoothstep(0.28, 1.0, distance(SCREEN_UV, focus));
    COLOR = vec4(g, c.a);
}
"""

const GRAIN_SHADER := """
shader_type canvas_item;
uniform float line_alpha = 0.05;
uniform float grain = 0.045;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void fragment() {
    float line = step(0.5, fract(FRAGCOORD.y * 0.5));
    float n = hash(floor(FRAGCOORD.xy) + fract(TIME * 7.0) * vec2(113.0, 71.0));
    COLOR = vec4(vec3(n * 0.6), line * line_alpha + n * grain);
}
"""

static func font(spacing: int = 0) -> Font:
    var variation := FontVariation.new()
    variation.base_font = RAJDHANI
    variation.fallbacks = [NOTO_KR]
    variation.spacing_glyph = spacing
    return variation

## Label with explicit LabelSettings so large display type keeps its spacing.
static func label(text: String, size: int, color: Color = INK, spacing: int = 0) -> Label:
    var result := Label.new()
    result.text = text
    var settings := LabelSettings.new()
    settings.font = font(spacing)
    settings.font_size = size
    settings.font_color = color
    result.label_settings = settings
    result.mouse_filter = Control.MOUSE_FILTER_IGNORE
    return result

## Display word with a layered soft glow (stacked translucent outlines behind
## the crisp face). Returns the container; the face label is its last child.
static func glow_title(text: String, size: int, color: Color, glow: Color, spacing: int) -> Control:
    var holder := Control.new()
    holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
    for layer in [[26, 0.05], [14, 0.09], [6, 0.16]]:
        var halo := label(text, size, Color(0, 0, 0, 0), spacing)
        halo.label_settings.outline_size = int(layer[0])
        halo.label_settings.outline_color = Color(glow, float(layer[1]))
        holder.add_child(halo)
    var face := label(text, size, color, spacing)
    face.label_settings.outline_size = 2
    face.label_settings.outline_color = Color(0, 0, 0, 0.55)
    holder.add_child(face)
    holder.size = face.get_minimum_size()
    return holder

static func load_texture(path: String) -> Texture2D:
    return BattleTextureLibrary.texture(path) if BattleTextureLibrary.has_texture(path) else null

## Full-body Motion Studio idle frame. Web builds may only ship the
## half-resolution derivative; `scale` compensates so layout stays identical.
static func operator_idle(character: String, direction: String) -> Dictionary:
    var path := ATLAS_ROOT + "%s/%s_idle.webp" % [character, direction]
    var scale := 1.0
    if not FileAccess.file_exists(path):
        path = path.get_basename() + ".web.webp"
        scale = 2.0
    if not FileAccess.file_exists(path):
        return {}
    var image := Image.new()
    if image.load_webp_from_buffer(FileAccess.get_file_as_bytes(path)) != OK or image.is_empty():
        return {}
    image.generate_mipmaps()
    return {"texture": ImageTexture.create_from_image(image), "scale": scale}

static func mission_plate(mission_id: String, room_index: int = 0) -> String:
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(BATTLE_ART))
    if not (parsed is Dictionary):
        return ""
    var rooms: Array = (parsed as Dictionary).get("missions", {}).get(mission_id, {}).get("rooms", [])
    if rooms.is_empty():
        return ""
    return "res://" + str(rooms[clampi(room_index, 0, rooms.size() - 1)].get("asset", ""))

static func grain_overlay() -> ColorRect:
    var overlay := ColorRect.new()
    overlay.name = "FilmGrain"
    overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var shader := Shader.new()
    shader.code = GRAIN_SHADER
    var material := ShaderMaterial.new()
    material.shader = shader
    overlay.material = material
    return overlay

## Top/bottom cinema bands: a vertical gradient that fades into the scene.
static func band(top: bool, height: float, alpha: float = 0.92) -> TextureRect:
    var gradient := Gradient.new()
    gradient.set_color(0, Color(DEEP, alpha))
    gradient.set_color(1, Color(DEEP, 0.0))
    var texture := GradientTexture2D.new()
    texture.gradient = gradient
    texture.width = 4
    texture.height = 64
    texture.fill_from = Vector2(0, 0) if top else Vector2(0, 1)
    texture.fill_to = Vector2(0, 1) if top else Vector2(0, 0)
    var rect := TextureRect.new()
    rect.texture = texture
    rect.stretch_mode = TextureRect.STRETCH_SCALE
    rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    rect.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE if top else Control.PRESET_BOTTOM_WIDE)
    if top:
        rect.offset_bottom = height
    else:
        rect.offset_top = -height
    return rect

## Glass panel style with a chamfered corner and a lit top edge.
static func panel_style(accent: Color = ACCENT, alpha: float = 0.8) -> StyleBoxFlat:
    var box := StyleBoxFlat.new()
    box.bg_color = Color(0.015, 0.045, 0.06, alpha)
    box.border_color = Color(accent, 0.32)
    box.set_border_width_all(1)
    box.border_width_top = 2
    box.corner_radius_top_left = 14
    box.corner_radius_bottom_right = 14
    box.corner_detail = 1
    box.shadow_color = Color(0, 0, 0, 0.45)
    box.shadow_size = 14
    box.content_margin_left = 18
    box.content_margin_right = 18
    box.content_margin_top = 14
    box.content_margin_bottom = 14
    return box

static func section_header(text: String, accent: Color = ACCENT) -> Control:
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 10)
    row.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var tick := ColorRect.new()
    tick.color = accent
    tick.custom_minimum_size = Vector2(4, 16)
    tick.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    tick.mouse_filter = Control.MOUSE_FILTER_IGNORE
    row.add_child(tick)
    row.add_child(label(text, 15, Color(accent, 0.95), 3))
    return row
