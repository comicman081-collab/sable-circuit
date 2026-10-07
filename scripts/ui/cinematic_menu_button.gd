extends Button
class_name CinematicMenuButton
## Large cinematic menu entry: index, title, subtitle and an animated accent
## sweep on hover/focus. `text` keeps the plain label for semantics/tests; the
## visible type is drawn here so it can animate.

var index_text := ""
var subtitle := ""
var accent := MenuFx.ACCENT
var title_size := 25
var _hover := 0.0
var _flash := 0.0
var _reveal := 1.0

func _init(label_text: String = "", sub: String = "", index_label: String = "") -> void:
    text = label_text
    subtitle = sub
    index_text = index_label
    flat = true
    focus_mode = Control.FOCUS_ALL
    mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
    for color_name in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color", "font_hover_pressed_color", "font_disabled_color"]:
        add_theme_color_override(color_name, Color(0, 0, 0, 0))
    var empty := StyleBoxEmpty.new()
    for style in ["normal", "hover", "pressed", "focus", "disabled", "hover_pressed"]:
        add_theme_stylebox_override(style, empty)
    pressed.connect(func() -> void: _flash = 1.0)

func set_reveal(value: float) -> void:
    _reveal = value
    modulate.a = value
    queue_redraw()

func _process(delta: float) -> void:
    var target := 1.0 if (is_hovered() or has_focus()) and not disabled else 0.0
    var previous := _hover
    _hover = move_toward(_hover, target, delta * 5.5)
    _flash = move_toward(_flash, 0.0, delta * 3.0)
    if not is_equal_approx(previous, _hover) or _flash > 0.0 or target > 0.0:
        queue_redraw()

func _draw() -> void:
    var h := _hover
    var w := size.x
    var mid := size.y * 0.5
    var tint := accent if not disabled else MenuFx.DIM
    draw_rect(Rect2(Vector2.ZERO, size), Color(0.01, 0.04, 0.055, 0.42 + 0.3 * h))
    var sweep := w * (0.18 + 0.82 * h)
    var lit := Color(tint, 0.05 + 0.22 * h + 0.25 * _flash)
    draw_polygon(PackedVector2Array([Vector2.ZERO, Vector2(sweep, 0), Vector2(sweep - 18.0, size.y), Vector2(0, size.y)]),
        PackedColorArray([lit, Color(tint, 0.0), Color(tint, 0.0), lit]))
    draw_rect(Rect2(0, 0, 3.0 + 3.0 * h, size.y), Color(tint, 0.5 + 0.5 * h))
    draw_line(Vector2(0, 0.5), Vector2(w * (0.35 + 0.65 * h), 0.5), Color(tint, 0.12 + 0.3 * h), 1.0)
    draw_line(Vector2(0, size.y - 0.5), Vector2(w, size.y - 0.5), Color(tint, 0.08 + 0.12 * h), 1.0)
    var face := get_theme_font("font")
    var x := 26.0
    if not index_text.is_empty():
        draw_string(face, Vector2(x, mid + 7.0), index_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color(tint, 0.55 + 0.45 * h))
        x = 66.0
    x += 6.0 * h
    var title_color := MenuFx.INK if not disabled else MenuFx.DIM
    var title_y := mid + (9.0 if subtitle.is_empty() else 2.0)
    draw_string(face, Vector2(x, title_y), text, HORIZONTAL_ALIGNMENT_LEFT, w - x - 40.0, title_size, title_color)
    if not subtitle.is_empty():
        draw_string(face, Vector2(x + 1.0, mid + 21.0), subtitle, HORIZONTAL_ALIGNMENT_LEFT, w - x - 40.0, 14, Color(MenuFx.MUTED, 0.75 + 0.25 * h))
    var chevron_x := w - 30.0 + 6.0 * h
    var chevron := Color(tint, 0.25 + 0.75 * h)
    draw_polyline(PackedVector2Array([Vector2(chevron_x, mid - 7.0), Vector2(chevron_x + 7.0, mid), Vector2(chevron_x, mid + 7.0)]), chevron, 2.0)
