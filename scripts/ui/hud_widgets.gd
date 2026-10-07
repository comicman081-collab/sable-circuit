extends RefCounted
class_name HudWidgets
## Small procedural HUD pieces for the mockup-style field HUD: panel styles,
## vector resource icons, segmented bars and key badges. UI iconography only.

const INK := Color("e8eef0")
const MUTED := Color("9aa9ad")
const LINE := Color(0.62, 0.72, 0.76, 0.42)
const CYAN := Color("3fd8e6")
const AMBER := Color("f2b042")
const RED := Color("f0596a")

static func panel_style(alpha: float = 0.8, border: Color = LINE, radius: int = 4) -> StyleBoxFlat:
    var box := StyleBoxFlat.new()
    box.bg_color = Color(0.03, 0.05, 0.065, alpha)
    box.border_color = border
    box.set_border_width_all(1)
    box.set_corner_radius_all(radius)
    box.shadow_color = Color(0, 0, 0, 0.45)
    box.shadow_size = 6
    return box

## Vector icons for the resource strip. `kind`: research, salvage, signal, intel.
class ResourceIcon extends Control:
    var kind := "research"
    var tint := Color.WHITE
    func _init(icon_kind: String = "research", icon_tint: Color = Color.WHITE) -> void:
        kind = icon_kind
        tint = icon_tint
        custom_minimum_size = Vector2(18, 18)
        mouse_filter = Control.MOUSE_FILTER_IGNORE
    func _draw() -> void:
        var c := size * 0.5
        var r := minf(size.x, size.y) * 0.46
        match kind:
            "salvage":
                # Gear: toothed ring with a hub.
                var points := PackedVector2Array()
                for i in range(32):
                    var a := TAU * float(i) / 32.0
                    var rr := r if (i / 2) % 2 == 0 else r * 0.74
                    points.append(c + Vector2.from_angle(a) * rr)
                draw_colored_polygon(points, Color(tint, 0.95))
                draw_circle(c, r * 0.38, Color(0.03, 0.05, 0.065))
            "signal":
                var hexagon := PackedVector2Array()
                for i in range(6): hexagon.append(c + Vector2.from_angle(TAU * i / 6.0 + PI / 6.0) * r)
                draw_colored_polygon(hexagon, Color(tint, 0.3))
                hexagon.append(hexagon[0])
                draw_polyline(hexagon, tint, 1.6, true)
                draw_circle(c, r * 0.32, tint)
            "intel":
                var diamond := PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0), c + Vector2(0, -r)])
                draw_polyline(diamond, tint, 1.6, true)
                draw_circle(c, r * 0.36, tint)
            _:
                draw_circle(c, r, Color(tint, 0.95))
                draw_circle(c, r * 0.68, Color(tint.darkened(0.45), 1.0))
                var inner := PackedVector2Array([c + Vector2(0, -r * 0.42), c + Vector2(r * 0.42, 0), c + Vector2(0, r * 0.42), c + Vector2(-r * 0.42, 0)])
                draw_colored_polygon(inner, tint)

## Key cap badge such as [TAB], [M], [Q].
class KeyBadge extends Control:
    var text := ""
    var font: Font
    var font_size := 13
    func _init(key_text: String = "", key_font: Font = null, key_size: int = 13) -> void:
        text = key_text
        font = key_font
        font_size = key_size
        mouse_filter = Control.MOUSE_FILTER_IGNORE
    func _draw() -> void:
        draw_rect(Rect2(Vector2.ZERO, size), Color(0.02, 0.04, 0.05, 0.85))
        draw_rect(Rect2(Vector2(0.5, 0.5), size - Vector2.ONE), Color(0.8, 0.86, 0.88, 0.75), false, 1.0)
        var face := font if font else ThemeDB.fallback_font
        var width := face.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
        draw_string(face, Vector2((size.x - width) * 0.5, size.y * 0.5 + font_size * 0.36), text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, INK)

## Segmented health bar (mockup: ten blocks).
class SegmentBar extends Control:
    var ratio := 1.0
    var segments := 10
    var tint := CYAN
    func _init() -> void:
        mouse_filter = Control.MOUSE_FILTER_IGNORE
    func set_ratio(value: float) -> void:
        if not is_equal_approx(value, ratio):
            ratio = value
            queue_redraw()
    func _draw() -> void:
        var gap := 2.0
        var w := (size.x - gap * float(segments - 1)) / float(segments)
        var lit := ratio * float(segments)
        for i in range(segments):
            var rect := Rect2(i * (w + gap), 0, w, size.y)
            draw_rect(rect, Color(0.16, 0.2, 0.22, 0.9))
            var fill := clampf(lit - float(i), 0.0, 1.0)
            if fill > 0.0:
                var colour := tint if ratio > 0.3 else RED
                draw_rect(Rect2(rect.position, Vector2(w * fill, size.y)), colour)

## Magazine glyph for the reload button.
class MagazineIcon extends Control:
    var tint := INK
    var progress := 0.0
    func _init() -> void:
        mouse_filter = Control.MOUSE_FILTER_IGNORE
    func _draw() -> void:
        var body := Rect2(size.x * 0.34, size.y * 0.16, size.x * 0.32, size.y * 0.68)
        var points := PackedVector2Array([body.position, body.position + Vector2(body.size.x, 0),
            body.end + Vector2(3, 0), Vector2(body.position.x + 3, body.end.y), body.position])
        draw_polyline(points, tint, 1.6, true)
        for i in range(3):
            var y := body.position.y + body.size.y * (0.25 + 0.22 * i)
            draw_line(Vector2(body.position.x + 3, y), Vector2(body.end.x - 1, y), Color(tint, 0.6), 1.0)
        if progress > 0.0:
            draw_arc(size * 0.5, minf(size.x, size.y) * 0.46, -PI * 0.5, -PI * 0.5 + TAU * progress, 32, CYAN, 2.0, true)
