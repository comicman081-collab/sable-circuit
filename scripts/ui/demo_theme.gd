extends RefCounted

## Shared menu/pause theme. Sizes and content margins match the original demo
## theme so existing fixed layouts keep fitting; only the styling changed.
const ACCENT := Color("5ee6da")
const INK := Color("e6f3f7")

static func _box(bg: Color, border: Color, width: int = 1) -> StyleBoxFlat:
    var box := StyleBoxFlat.new()
    box.bg_color = bg
    box.border_color = border
    box.set_border_width_all(width)
    box.corner_radius_top_left = 8
    box.corner_radius_bottom_right = 8
    box.corner_detail = 1
    box.content_margin_left = 14; box.content_margin_right = 14
    box.content_margin_top = 4; box.content_margin_bottom = 4
    return box

static func build() -> Theme:
    var result := Theme.new()
    result.default_font = preload("res://assets/fonts/demo_font.tres")
    result.default_font_size = 18
    var normal := _box(Color(0.025, 0.07, 0.09, 0.9), Color(ACCENT, 0.3))
    normal.border_width_left = 3
    var hover := _box(Color(0.05, 0.14, 0.16, 0.95), Color(ACCENT, 0.85))
    hover.border_width_left = 4
    hover.shadow_color = Color(ACCENT, 0.18)
    hover.shadow_size = 10
    var pressed := _box(Color(0.1, 0.27, 0.28, 0.98), Color(ACCENT, 1.0))
    pressed.border_width_left = 4
    var focus := _box(Color(0, 0, 0, 0), Color(ACCENT, 0.95), 2)
    focus.shadow_color = Color(ACCENT, 0.22)
    focus.shadow_size = 12
    var disabled := _box(Color(0.02, 0.04, 0.05, 0.75), Color(0.2, 0.28, 0.3, 0.5))
    var styles := {"normal": normal, "hover": hover, "pressed": pressed, "hover_pressed": pressed, "focus": focus, "disabled": disabled}
    for state: String in styles:
        result.set_stylebox(state, "Button", styles[state])
        result.set_stylebox(state, "OptionButton", styles[state])
    result.set_color("font_color", "Button", Color("cfe3e6"))
    result.set_color("font_hover_color", "Button", Color.WHITE)
    result.set_color("font_focus_color", "Button", Color("c9fbf5"))
    result.set_color("font_pressed_color", "Button", Color.WHITE)
    result.set_color("font_hover_pressed_color", "Button", Color.WHITE)
    result.set_color("font_disabled_color", "Button", Color("5b6b72"))
    for key in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color", "font_disabled_color"]:
        result.set_color(key, "OptionButton", result.get_color(key, "Button"))

    # Low-key text links for secondary title actions.
    result.set_type_variation(&"UtilityButton", &"Button")
    var link := StyleBoxFlat.new()
    link.bg_color = Color(0, 0, 0, 0)
    link.content_margin_left = 12; link.content_margin_right = 12
    link.content_margin_top = 4; link.content_margin_bottom = 4
    var link_hover := link.duplicate() as StyleBoxFlat
    link_hover.bg_color = Color(ACCENT, 0.08)
    link_hover.border_color = Color(ACCENT, 0.8)
    link_hover.border_width_bottom = 2
    for state in ["normal", "disabled"]:
        result.set_stylebox(state, &"UtilityButton", link)
    for state in ["hover", "pressed", "hover_pressed", "focus"]:
        result.set_stylebox(state, &"UtilityButton", link_hover)
    result.set_font_size("font_size", &"UtilityButton", 14)
    result.set_color("font_color", &"UtilityButton", Color("8aa3b1"))
    result.set_color("font_hover_color", &"UtilityButton", INK)
    result.set_color("font_focus_color", &"UtilityButton", INK)

    var panel := StyleBoxFlat.new()
    panel.bg_color = Color(0.015, 0.045, 0.06, 0.84)
    panel.border_color = Color(ACCENT, 0.28)
    panel.set_border_width_all(1)
    panel.border_width_top = 2
    panel.corner_radius_top_left = 14
    panel.corner_radius_bottom_right = 14
    panel.corner_detail = 1
    panel.shadow_color = Color(0, 0, 0, 0.4)
    panel.shadow_size = 12
    result.set_stylebox("panel", "Panel", panel)
    result.set_stylebox("panel", "PanelContainer", panel)
    result.set_color("font_color", "Label", Color("d8e8ee"))

    var popup := panel.duplicate() as StyleBoxFlat
    popup.bg_color = Color(0.02, 0.06, 0.08, 0.98)
    popup.content_margin_left = 6; popup.content_margin_right = 6
    popup.content_margin_top = 6; popup.content_margin_bottom = 6
    result.set_stylebox("panel", "PopupMenu", popup)
    var popup_hover := StyleBoxFlat.new()
    popup_hover.bg_color = Color(ACCENT, 0.16)
    popup_hover.border_color = ACCENT
    popup_hover.border_width_left = 3
    result.set_stylebox("hover", "PopupMenu", popup_hover)
    result.set_color("font_color", "PopupMenu", Color("cfe3e6"))
    result.set_color("font_hover_color", "PopupMenu", Color.WHITE)
    result.set_color("font_disabled_color", "PopupMenu", Color("56666d"))

    var dialog := panel.duplicate() as StyleBoxFlat
    dialog.bg_color = Color(0.015, 0.04, 0.055, 0.98)
    dialog.content_margin_left = 20; dialog.content_margin_right = 20
    dialog.content_margin_top = 16; dialog.content_margin_bottom = 16
    result.set_stylebox("panel", "AcceptDialog", dialog)
    var border := StyleBoxFlat.new()
    border.bg_color = Color(0.03, 0.09, 0.11, 1.0)
    border.border_color = Color(ACCENT, 0.6)
    border.set_border_width_all(1)
    border.expand_margin_top = 30
    border.expand_margin_left = 2; border.expand_margin_right = 2; border.expand_margin_bottom = 2
    result.set_stylebox("embedded_border", "Window", border)
    result.set_stylebox("embedded_unfocused_border", "Window", border)
    result.set_color("title_color", "Window", Color("bff7f0"))

    var tooltip := popup.duplicate() as StyleBoxFlat
    tooltip.content_margin_left = 10; tooltip.content_margin_right = 10
    result.set_stylebox("panel", "TooltipPanel", tooltip)
    result.set_color("font_color", "TooltipLabel", Color("d8e8ee"))
    return result
