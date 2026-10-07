extends CanvasLayer
class_name StoryStageHUD
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
## Field HUD laid out after the SABLE CIRCUIT mockup: chapter minimap and
## objectives top-left, resource strip top-right, squad cards bottom-left,
## energy bar bottom-centre, weapon/ammo and skill keys bottom-right.

const TECH_FONT_PATH := "res://assets/fonts/demo_font.tres"
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
const W := preload("res://scripts/ui/hud_widgets.gd")
const CARD_ACCENTS: Array[Color] = [Color("3fd8e6"), Color("e0a95a"), Color("7fe0c6")]

var _tech_font: Font
var _font_source := "system-fallback"
var _stage: StoryStage01
var _mission_label: Label
var _room_label: Label
var _objective_label: Label
var _sub_objective_labels: Array[Label] = []
var _story_label: Label
var _story_panel: Control
var _status_label: Label
var _optional_label: Label
var _cargo_label: Label
var _intel_label: Label
var _rule_label: Label
var _resource_values: Dictionary = {}
var _weapon_label: Label
var _ammo_label: Label
var _reserve_label: Label
var _reload_button: Panel
var _reload_icon: Control
var _energy_fill: ColorRect
var _energy_glow: ColorRect
var _energy_bg: ColorRect
var _energy_caption: Label
var _energy_value_label: Label
var _minimap: TacticalMinimap
var _minimap_buttons: Dictionary = {}
var _cards: Array[Dictionary] = []
var _skill_labels: Array[Label] = []
var _skill_icons: Array[TextureRect] = []
var _skill_boxes: Array[Panel] = []
var _skill_shades: Array[ColorRect] = []
var _weapon_icon: TextureRect
var _active_hud_operator_id := ""
var _extraction_panel: Panel
var _extraction_label: Label
var _transmission_panel: Panel
var _transmission_text: Label
var _transmission_left := 0.0
var _objective_action: Button
var _supply_found := false
var _signal_found := false
var _optional_titles: Array[String] = ["Field supplies", "Signal fragment"]

func _ready() -> void:
    layer = 20
    _tech_font = _load_tech_font()
    _build_minimap_panel()
    _build_objective_panel()
    _build_top_status()
    _objective_action = Button.new()
    _objective_action.position = Vector2(14, 290)
    _objective_action.size = Vector2(243, 36)
    _objective_action.add_theme_font_override("font", _tech_font)
    _objective_action.add_theme_font_size_override("font_size", 15)
    _style_action_button(_objective_action)
    _objective_action.pressed.connect(func() -> void:
        if _stage != null: _stage.use_objective_action())
    add_child(_objective_action)
    _build_squad_cards()
    _build_energy_bar()
    _build_weapon_panel()
    _build_extraction_panel()
    _build_story_strip()
    _transmission_panel = _panel(Vector2(360, 70), Vector2(560, 48), W.LINE, 0.86)
    var bar := ColorRect.new()
    bar.color = W.CYAN
    bar.position = Vector2(0, 0)
    bar.size = Vector2(3, 48)
    bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _transmission_panel.add_child(bar)
    _transmission_text = _label(_transmission_panel, "", Vector2(16, 6), 14, Color("dbe7ea"))
    _transmission_text.add_theme_constant_override("line_spacing", -3)
    _transmission_text.size = Vector2(536, 38)
    _transmission_text.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    _transmission_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _transmission_panel.visible = false
    var reticle := Control.new()
    reticle.set_script(preload("res://scripts/ui/battle_reticle.gd"))
    reticle.name = "BattleReticle"
    reticle.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(reticle)
    call_deferred("_bind_runtime")

func _load_tech_font() -> Font:
    if ResourceLoader.exists(TECH_FONT_PATH):
        var bundled := load(TECH_FONT_PATH) as Font
        if bundled != null:
            _font_source = "bundled-rajdhani-v1.201"
            return bundled
    var fallback := SystemFont.new()
    fallback.font_names = PackedStringArray(["Rajdhani","Bahnschrift SemiCondensed","Arial Narrow","DejaVu Sans Condensed","Liberation Sans"])
    _font_source = "system-fallback"
    return fallback

func _bind_runtime() -> void:
    _stage = get_parent() as StoryStage01
    if _minimap:
        _minimap.bind_stage(_stage)
    _bind_card_portraits()
    if _stage and _mission_label:
        var title := str(MissionCatalog.get_mission(_stage.mission_id).get("title", "SITE-7"))
        _mission_label.text = "CH01   %s" % title.to_upper()
    if _stage:
        for i in range(mini(2, _stage.optional_rooms.size())):
            _optional_titles[i] = str((_stage.optional_rooms[i] as Dictionary).get("title", _optional_titles[i]))
        _refresh_sub_objectives()
    _update_runtime_values()

func _process(_delta: float) -> void:
    _transmission_left = maxf(0.0, _transmission_left - _delta)
    if _transmission_panel:
        _transmission_panel.visible = _transmission_left > 0.0
        _transmission_panel.modulate.a = minf(1.0, _transmission_left)
    _update_runtime_values()

func _unhandled_key_input(event: InputEvent) -> void:
    if not (event is InputEventKey) or not event.pressed or event.echo or _minimap == null: return
    match event.keycode:
        KEY_M: _minimap.toggle_zoom()
        KEY_EQUAL, KEY_KP_ADD: _minimap.zoom_by(1)
        KEY_MINUS, KEY_KP_SUBTRACT: _minimap.zoom_by(-1)
        _: return
    get_viewport().set_input_as_handled()

func _panel(pos: Vector2, panel_size: Vector2, border: Color = W.LINE, alpha: float = 0.8) -> Panel:
    var p := Panel.new()
    p.position = pos
    p.size = panel_size
    p.mouse_filter = Control.MOUSE_FILTER_IGNORE
    p.add_theme_stylebox_override("panel", W.panel_style(alpha, border))
    add_child(p)
    return p

func _label(parent: Node, text_value: String, pos: Vector2, font_size: int, color: Color = W.INK) -> Label:
    var l := Label.new()
    l.text = text_value
    l.mouse_filter = Control.MOUSE_FILTER_IGNORE
    l.position = pos
    l.add_theme_font_override("font",_tech_font)
    l.add_theme_font_size_override("font_size",font_size)
    l.add_theme_color_override("font_color",color)
    l.add_theme_color_override("font_shadow_color",Color(0,0,0,0.72))
    l.add_theme_constant_override("shadow_offset_x",1)
    l.add_theme_constant_override("shadow_offset_y",1)
    parent.add_child(l)
    return l

func _rule(parent: Node, pos: Vector2, width: float) -> void:
    var line := ColorRect.new()
    line.color = Color(W.LINE, 0.5)
    line.position = pos
    line.size = Vector2(width, 1)
    line.mouse_filter = Control.MOUSE_FILTER_IGNORE
    parent.add_child(line)

func _style_action_button(button: Button) -> void:
    for state in ["normal", "hover", "pressed", "disabled", "focus"]:
        var box := W.panel_style(0.86, Color(W.AMBER, 0.85) if state != "disabled" else Color(W.LINE, 0.5))
        if state == "hover" or state == "pressed": box.bg_color = Color(0.18, 0.12, 0.03, 0.92)
        if state == "focus": box.bg_color = Color(0, 0, 0, 0)
        button.add_theme_stylebox_override(state, box)
    button.add_theme_color_override("font_color", Color("ffd89a"))
    button.add_theme_color_override("font_disabled_color", Color("a9b2b4"))
    button.focus_mode = Control.FOCUS_NONE

# --- top-left: chapter minimap --------------------------------------------

func _build_minimap_panel() -> void:
    var p := _panel(Vector2(14, 14), Vector2(243, 172), W.LINE, 0.84)
    _mission_label = _label(p, "CH01   BLACKOUT AT SITE-7", Vector2(12, 7), 15, W.INK)
    _mission_label.size = Vector2(220, 20)
    _mission_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
    _rule(p, Vector2(10, 31), 223)
    _minimap = TacticalMinimap.new()
    _minimap.position = Vector2(8, 36)
    _minimap.size = Vector2(190, 106)
    p.add_child(_minimap)
    for spec in [["+", Vector2(206, 64)], ["-", Vector2(206, 92)], ["M", Vector2(206, 140)]]:
        var badge := W.KeyBadge.new(str(spec[0]), _tech_font, 15)
        badge.position = spec[1]
        badge.size = Vector2(22, 22)
        p.add_child(badge)
        _minimap_buttons[str(spec[0])] = badge
    _room_label = _label(p, "SITE-7 / OUTER GATE", Vector2(12, 146), 12, W.MUTED)
    _room_label.size = Vector2(186, 18)
    _room_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS

# --- top-left: objectives -------------------------------------------------

func _build_objective_panel() -> void:
    var p := _panel(Vector2(14, 196), Vector2(243, 88), W.LINE, 0.78)
    _label(p, "OBJECTIVES", Vector2(12, 6), 14, W.INK)
    _rule(p, Vector2(10, 27), 223)
    _label(p, "◇", Vector2(10, 29), 17, W.AMBER)
    _objective_label = _label(p, "Secure the corridor", Vector2(30, 31), 14, W.AMBER)
    _objective_label.size = Vector2(205, 20)
    _objective_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
    for i in range(2):
        var line := _label(p, "", Vector2(30, 51 + i * 16), 12, Color("d6dee0"))
        line.size = Vector2(205, 16)
        line.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
        _sub_objective_labels.append(line)
    _refresh_sub_objectives()

func _refresh_sub_objectives() -> void:
    if _sub_objective_labels.is_empty(): return
    _sub_objective_labels[0].text = "•  %s  %s" % [_optional_titles[0], "RECOVERED" if _supply_found else "(optional)"]
    _sub_objective_labels[1].text = "•  %s  %s" % [_optional_titles[1], "RECOVERED" if _signal_found else "(optional)"]
    _sub_objective_labels[0].add_theme_color_override("font_color", Color("7fe0c6") if _supply_found else Color("d6dee0"))
    _sub_objective_labels[1].add_theme_color_override("font_color", Color("7fe0c6") if _signal_found else Color("d6dee0"))

# --- top-right: resources and status --------------------------------------

func _build_top_status() -> void:
    var strip := HBoxContainer.new()
    strip.name = "ResourceStrip"
    strip.add_theme_constant_override("separation", 14)
    strip.position = Vector2(880, 14)
    strip.size = Vector2(376, 24)
    strip.alignment = BoxContainer.ALIGNMENT_END
    strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(strip)
    for spec in [["salvage", Color("c9d3d6")], ["signal", Color("b28cff")], ["intel", Color("5fb4ff")], ["research", Color("f2c14e")]]:
        var item := HBoxContainer.new()
        item.add_theme_constant_override("separation", 5)
        item.mouse_filter = Control.MOUSE_FILTER_IGNORE
        var icon := W.ResourceIcon.new(str(spec[0]), spec[1])
        icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
        item.add_child(icon)
        var value := Label.new()
        value.text = "0"
        value.add_theme_font_override("font", _tech_font)
        value.add_theme_font_size_override("font_size", 17)
        value.add_theme_color_override("font_color", W.INK)
        value.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
        value.mouse_filter = Control.MOUSE_FILTER_IGNORE
        item.add_child(value)
        strip.add_child(item)
        _resource_values[str(spec[0])] = value
    var tab := W.KeyBadge.new("TAB", _tech_font, 13)
    tab.custom_minimum_size = Vector2(38, 22)
    tab.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    strip.add_child(tab)
    _status_label = _label(self, "AREA SECURE", Vector2(958, 44), 16, W.AMBER)
    _status_label.size = Vector2(298, 22)
    _status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    # Detailed ledger lines stay available (tests and debriefs read them) but
    # are secondary to the icon strip.
    _cargo_label = _label(self, "", Vector2(858, 66), 11, Color("8fb9c4"))
    _cargo_label.size = Vector2(398, 16)
    _cargo_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _cargo_label.modulate.a = 0.75
    # Right-aligned and at most ~324 px wide with all eight keys; the box starts
    # right of the transmission panel (x 360-920) so the two boxes never overlap.
    _intel_label = _label(self, "", Vector2(924, 82), 11, Color("5d827f"))
    _intel_label.size = Vector2(332, 16)
    _intel_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _intel_label.modulate.a = 0.75
    _optional_label = _label(self, "STORES --   SIGNAL --", Vector2(858, 98), 11, Color("a8b8b0"))
    _optional_label.size = Vector2(398, 16)
    _optional_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _optional_label.visible = false
    # A room rule's countdown (OVERRUN): right of the transmission panel like the intel line, under it.
    # Shown only while a rule is running in the room.
    _rule_label = _label(self, "", Vector2(924, 100), 13, W.RED)
    _rule_label.size = Vector2(332, 18)
    _rule_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _rule_label.visible = false

# --- bottom-left: squad cards ---------------------------------------------

func _build_squad_cards() -> void:
    var ids: Array[String] = ["CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"]
    var names: Array[String] = ["ASTER","ROOK","MICA"]
    for i in range(3):
        var p := _panel(Vector2(24 + i * 110, 544), Vector2(102, 160), W.LINE, 0.9)
        p.clip_contents = true
        var portrait := TextureRect.new()
        portrait.position = Vector2(1, 1)
        portrait.size = Vector2(100, 100)
        portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
        portrait.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
        portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
        p.add_child(portrait)
        var fade := TextureRect.new()
        var gradient := Gradient.new()
        gradient.set_color(0, Color(0.03, 0.05, 0.065, 0.0))
        gradient.set_color(1, Color(0.03, 0.05, 0.065, 0.95))
        var fade_texture := GradientTexture2D.new()
        fade_texture.gradient = gradient
        fade_texture.fill_from = Vector2(0, 0)
        fade_texture.fill_to = Vector2(0, 1)
        fade_texture.width = 4
        fade_texture.height = 32
        fade.texture = fade_texture
        fade.position = Vector2(1, 62)
        fade.size = Vector2(100, 40)
        fade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        fade.stretch_mode = TextureRect.STRETCH_SCALE
        fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
        p.add_child(fade)
        var top_glow := ColorRect.new()
        top_glow.position = Vector2(1, 1)
        top_glow.size = Vector2(100, 2)
        top_glow.color = CARD_ACCENTS[i]
        top_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
        p.add_child(top_glow)
        var badge := W.KeyBadge.new(str(i + 1), _tech_font, 13)
        badge.position = Vector2(6, 6)
        badge.size = Vector2(19, 19)
        p.add_child(badge)
        _label(p, names[i], Vector2(8, 100), 15, W.INK)
        var hp := _label(p, "--/--", Vector2(8, 118), 13, Color("c9d4d6"))
        var bar := W.SegmentBar.new()
        bar.position = Vector2(8, 138)
        bar.size = Vector2(86, 5)
        bar.tint = W.CYAN
        p.add_child(bar)
        var weapon := TextureRect.new()
        weapon.position = Vector2(8, 146)
        weapon.size = Vector2(40, 11)
        weapon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        weapon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        weapon.modulate = Color(0.78, 0.82, 0.84, 0.8)
        weapon.mouse_filter = Control.MOUSE_FILTER_IGNORE
        p.add_child(weapon)
        _cards.append({"id":ids[i],"portrait":portrait,"hp":hp,"bar":bar,"panel":p,"accent":CARD_ACCENTS[i],"top_glow":top_glow,"weapon":weapon})

func _bind_card_portraits() -> void:
    var paths := {
        "CHR_PROTO_01":"res://motion_lab_v1/public/assets/atlas/aster/portrait.png",
        "CHR_PROTO_03":"res://motion_lab_v1/public/assets/atlas/mica/portrait.png",
    }
    var crops := {
        "CHR_PROTO_01":Rect2(177,40,157,180),
        "CHR_PROTO_03":Rect2(47,7,167,182),
    }
    for card: Dictionary in _cards:
        var id := str(card.id)
        var profile := ArtProfileRegistry.get_profile(id)
        (card.weapon as TextureRect).texture = _load_visual_texture(str(profile.get("weapon_hud_asset", "")))
        if profile.has("portrait_region"):
            (card.portrait as TextureRect).texture = preload("res://scripts/core/battle_texture_library.gd").portrait(profile)
            (card.portrait as TextureRect).material = null
            continue
        var texture := _load_visual_texture(str(paths[id]))
        if texture == null:
            push_error("Missing current character HUD portrait: " + id)
            continue
        var atlas := AtlasTexture.new()
        atlas.atlas = texture
        atlas.region = crops[id]
        atlas.filter_clip = true
        (card.portrait as TextureRect).texture = atlas

# --- bottom-centre: energy --------------------------------------------------

func _build_energy_bar() -> void:
    _energy_caption = _label(self, "ENERGY", Vector2(450, 669), 15, Color("cfe9ee"))
    var bg := ColorRect.new()
    _energy_bg = bg
    bg.position = Vector2(520, 679)
    bg.size = Vector2(250, 5)
    bg.color = Color(0.16, 0.22, 0.25, 0.9)
    bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(bg)
    _energy_glow = ColorRect.new()
    _energy_glow.position = Vector2(520, 676)
    _energy_glow.size = Vector2(0, 11)
    _energy_glow.color = Color(W.CYAN, 0.18)
    _energy_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(_energy_glow)
    _energy_fill = ColorRect.new()
    _energy_fill.position = Vector2(520, 679)
    _energy_fill.size = Vector2(0, 5)
    _energy_fill.color = W.CYAN
    _energy_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(_energy_fill)
    _energy_value_label = _label(self, "000/100", Vector2(778, 669), 15, W.INK)
    _energy_value_label.size = Vector2(70, 20)

func set_touch_layout(enabled: bool) -> void:
    if _energy_bg == null: return
    var top := 104.0 if enabled else 669.0
    _energy_caption.position.y = top
    _energy_value_label.position.y = top
    _energy_bg.position.y = top + 10.0
    _energy_fill.position.y = top + 10.0
    _energy_glow.position.y = top + 7.0
    if _story_panel: _story_panel.position.y = 138.0 if enabled else 628.0
    if _extraction_panel: _extraction_panel.position.y = 173.0 if enabled else 572.0

# --- bottom-right: weapon and skills --------------------------------------

func _build_weapon_panel() -> void:
    var p := _panel(Vector2(1032, 563), Vector2(224, 70), W.LINE, 0.84)
    _weapon_icon = TextureRect.new()
    _weapon_icon.position = Vector2(10, 10)
    _weapon_icon.size = Vector2(100, 30)
    _weapon_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    _weapon_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    _weapon_icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
    p.add_child(_weapon_icon)
    _ammo_label = _label(p, "24", Vector2(114, -4), 32, W.INK)
    _ammo_label.size = Vector2(60, 40)
    _ammo_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _reserve_label = _label(p, "/24", Vector2(118, 30), 13, W.MUTED)
    _reserve_label.size = Vector2(56, 16)
    _reserve_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _weapon_label = _label(p, "COIL ASSAULT RIFLE", Vector2(10, 46), 13, W.CYAN)
    _weapon_label.size = Vector2(150, 18)
    _weapon_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
    _reload_button = Panel.new()
    _reload_button.name = "ReloadButton"
    _reload_button.position = Vector2(182, 16)
    _reload_button.size = Vector2(34, 38)
    _reload_button.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _reload_button.add_theme_stylebox_override("panel", W.panel_style(0.6, Color(W.CYAN, 0.7), 3))
    p.add_child(_reload_button)
    _reload_icon = W.MagazineIcon.new()
    _reload_icon.size = _reload_button.size
    _reload_button.add_child(_reload_icon)
    _label(p, "R", Vector2(206, 52), 10, W.MUTED)
    var keys: Array[String] = ["Q","E","X"]
    for i in range(3):
        var skill := _panel(Vector2(1044 + i * 72, 641), Vector2(62, 44), W.LINE, 0.86)
        var icon := TextureRect.new()
        icon.position = Vector2(14, 5)
        icon.size = Vector2(34, 34)
        icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
        skill.add_child(icon)
        var shade := ColorRect.new()
        shade.color = Color(0, 0, 0, 0.62)
        shade.position = Vector2(1, 1)
        shade.size = Vector2(60, 0)
        shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
        skill.add_child(shade)
        _skill_icons.append(icon)
        _skill_boxes.append(skill)
        _skill_shades.append(shade)
        var badge := W.KeyBadge.new(keys[i], _tech_font, 13)
        badge.position = Vector2(1044 + i * 72 + 21, 689)
        badge.size = Vector2(20, 20)
        add_child(badge)
        # Readiness text for tests/accessibility sits inside the box.
        var kl := _label(skill, keys[i], Vector2(1, 29), 10, Color("c7d3c9"))
        kl.size = Vector2(60, 14)
        kl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        _skill_labels.append(kl)

func _build_extraction_panel() -> void:
    _extraction_panel = _panel(Vector2(388, 572), Vector2(510, 46), Color(W.AMBER, 0.85), 0.94)
    _extraction_label = _label(_extraction_panel, "EXTRACTION WINDOW // [F] EXTRACT   [C] CONTINUE", Vector2(12, 9), 16, Color("ffd8a0"))
    _extraction_label.size = Vector2(486, 28)
    _extraction_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    _extraction_panel.visible = false

func _build_story_strip() -> void:
    # Field messages sit quietly above the energy bar, no heavy frame.
    var holder := Control.new()
    holder.position = Vector2(372, 628)
    holder.size = Vector2(536, 26)
    holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(holder)
    _story_panel = holder
    var shade := TextureRect.new()
    var gradient := Gradient.new()
    gradient.offsets = PackedFloat32Array([0.0, 0.2, 0.8, 1.0])
    gradient.colors = PackedColorArray([Color(0, 0, 0, 0), Color(0.02, 0.04, 0.05, 0.62), Color(0.02, 0.04, 0.05, 0.62), Color(0, 0, 0, 0)])
    var texture := GradientTexture2D.new()
    texture.gradient = gradient
    texture.width = 64
    texture.height = 4
    shade.texture = texture
    shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    shade.stretch_mode = TextureRect.STRETCH_SCALE
    shade.size = holder.size
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    holder.add_child(shade)
    _story_label = _label(holder, "WASD MOVE  /  SHIFT RUN  /  LMB FIRE  /  R RELOAD", Vector2(0, 4), 12, Color("c4d3d6"))
    _story_label.size = Vector2(536, 18)
    _story_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    _story_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS

# --- runtime ----------------------------------------------------------------

func _update_runtime_values() -> void:
    if _stage == null or _stage.squad == null:
        return
    var action := _stage.objective_action_state()
    _objective_action.visible = bool(action.get("visible",false))
    _objective_action.disabled = not bool(action.get("enabled",false))
    _objective_action.text = str(action.get("text",""))
    for i in range(mini(_cards.size(),_stage.squad.operators.size())):
        var actor := _stage.squad.operators[i]
        var card: Dictionary = _cards[i]
        (card["hp"] as Label).text = "%d/%d" % [int(actor.health),int(actor.max_health)]
        var ratio := clampf(actor.health/maxf(1.0,actor.max_health),0.0,1.0)
        (card["bar"] as W.SegmentBar).set_ratio(ratio)
        var panel := card["panel"] as Panel
        var active := i == _stage.squad.active_index
        panel.modulate = Color(1,1,1,1) if not actor.is_downed() else Color(0.48,0.52,0.55,0.72)
        var style := panel.get_theme_stylebox("panel") as StyleBoxFlat
        var border := Color(W.CYAN, 0.95) if active else W.LINE
        if style and style.border_color != border:
            style.border_color = border
            style.set_border_width_all(2 if active else 1)
            style.shadow_color = Color(W.CYAN, 0.35) if active else Color(0, 0, 0, 0.45)
            style.shadow_size = 10 if active else 6
        var glow := card["top_glow"] as ColorRect
        glow.modulate.a = 1.0 if active else 0.28
    var energy := _stage.squad.debug_energy_contract()
    var current := float(energy.get("current",0.0))
    var width := 250.0 * clampf(current / 100.0, 0.0, 1.0)
    _energy_fill.size.x = width
    _energy_glow.size.x = width
    _energy_value_label.text = "%03d/100" % int(round(current))
    _energy_fill.color = Color("ffe18a") if current>=99.9 else W.CYAN
    _energy_glow.color = Color(_energy_fill.color, 0.2)
    var active_operator := _stage.squad.get_active_operator()
    if active_operator:
        var reload_left := float(active_operator.get("_reload_left"))
        _ammo_label.text = ("..." if reload_left > 0.0 else "%02d" % active_operator.ammo)
        _reserve_label.text = "/%d" % int(active_operator.magazine_size)
        _set_font_color(_ammo_label, W.RED if active_operator.ammo <= maxi(2, active_operator.magazine_size / 5) and reload_left <= 0.0 else W.INK)
        var reload_icon := _reload_icon as W.MagazineIcon
        var progress := 0.0 if reload_left <= 0.0 else 1.0 - reload_left / maxf(0.01, float(active_operator.reload_duration))
        if reload_icon.progress != progress:
            reload_icon.progress = progress
            reload_icon.queue_redraw()
        _weapon_label.text = str(active_operator.weapon_spec.get("display_name", active_operator.display_name + " PRIMARY")).to_upper()
        if _active_hud_operator_id != active_operator.operator_id:
            _active_hud_operator_id = active_operator.operator_id
            _bind_active_hud_art(active_operator)
        _update_skill_state(active_operator,current)

func portrait_index_at(point: Vector2) -> int:
    for i in range(_cards.size()):
        if (_cards[i].panel as Panel).get_global_rect().has_point(point): return i
    return -1

func select_portrait_at(point: Vector2) -> bool:
    var index := portrait_index_at(point)
    if index < 0 or _stage == null or _stage.squad == null: return false
    _stage.squad.request_control(index)
    return true

func _minimap_control_at(point: Vector2) -> String:
    for key in _minimap_buttons:
        if (_minimap_buttons[key] as Control).get_global_rect().grow(3).has_point(point): return str(key)
    return ""

func blocks_pointer_at(point: Vector2) -> bool:
    if portrait_index_at(point) >= 0 or (_objective_action.visible and _objective_action.get_global_rect().has_point(point)): return true
    if not _minimap_control_at(point).is_empty(): return true
    if _reload_button and _reload_button.get_global_rect().has_point(point): return true
    for box in _skill_boxes:
        if box.get_global_rect().has_point(point): return true
    return false

func activate_field_control_at(point: Vector2) -> bool:
    if select_portrait_at(point): return true
    if _objective_action.visible and _objective_action.get_global_rect().has_point(point):
        if not _objective_action.disabled: _stage.use_objective_action()
        return true
    match _minimap_control_at(point):
        "+": _minimap.zoom_by(1); return true
        "-": _minimap.zoom_by(-1); return true
        "M": _minimap.toggle_zoom(); return true
    if _reload_button and _reload_button.get_global_rect().has_point(point):
        var active := _stage.squad.get_active_operator() if _stage and _stage.squad else null
        if active: active.call("_begin_reload")
        return true
    for box in _skill_boxes:
        if box.get_global_rect().has_point(point): return true
    return false

func _update_skill_state(active: OperatorActor, energy: float) -> void:
    var controller := active.get_node_or_null("SkillController") as OperatorSkillController
    if controller == null:
        return
    var c := controller.debug_contract()
    var q := float(c.get("q_cooldown",0.0))
    var e := float(c.get("e_cooldown",0.0))
    _skill_labels[0].text = "Q READY" if q<=0.0 else "Q %.1f"%q
    _skill_labels[1].text = "E READY" if e<=0.0 else "E %.1f"%e
    _skill_labels[2].text = "X READY" if energy>=99.9 else "X %02d%%"%int(round(energy))
    _set_font_color(_skill_labels[2], Color("ffe18a") if energy>=99.9 else Color("7f929a"))
    # Cooldown shading grows from the top; ready skills show the icon only.
    var fractions := [clampf(q / 8.0, 0.0, 1.0) if q > 0.0 else 0.0, clampf(e / 8.0, 0.0, 1.0) if e > 0.0 else 0.0, 1.0 - clampf(energy / 100.0, 0.0, 1.0)]
    for i in range(3):
        _skill_shades[i].size.y = 42.0 * float(fractions[i])
        _skill_labels[i].visible = float(fractions[i]) > 0.0
        var ready := float(fractions[i]) <= 0.0
        var style := _skill_boxes[i].get_theme_stylebox("panel") as StyleBoxFlat
        var border := (Color(W.CYAN, 0.8) if i < 2 else Color("ffe18a")) if ready else W.LINE
        # Setting a style's colour emits `changed` and redraws the panel even when equal.
        if style and style.border_color != border:
            style.border_color = border

## Re-adding an equal override still notifies a theme change, and the label then
## reshapes its text and redraws.
func _set_font_color(label: Label, color: Color) -> void:
    if label.has_theme_color_override("font_color") and label.get_theme_color("font_color") == color: return
    label.add_theme_color_override("font_color", color)

func _bind_active_hud_art(active: OperatorActor) -> void:
    var profile := active.art_profile
    if profile.is_empty():
        profile = ArtProfileRegistry.get_profile(active.operator_id)
    if _weapon_icon:
        _weapon_icon.texture = _load_visual_texture(str(profile.get("weapon_hud_asset","")))
    var action_assets: Array = profile.get("hud_action_icon_assets", [])
    for i in range(_skill_icons.size()):
        var rel_path := str(action_assets[i]) if i < action_assets.size() else ""
        _skill_icons[i].texture = _load_visual_texture(rel_path)

func _load_visual_texture(rel_path: String) -> Texture2D:
    if rel_path.is_empty():
        return null
    var resource_path := rel_path if rel_path.begins_with("res://") else "res://" + rel_path
    if resource_path.ends_with(".png"):
        return preload("res://scripts/core/battle_texture_library.gd").texture(resource_path)
    if not ResourceLoader.exists(resource_path):
        return null
    return load(resource_path) as Texture2D

func set_room(index: int, total: int, room_title: String, room_type: String) -> void:
    if _room_label:
        _room_label.text = "SITE-7 / %s   %02d-%02d" % [room_title.to_upper(),index+1,total]

func set_objective(text: String, interaction_required: bool = false) -> void:
    if _objective_label:
        _objective_label.text = (("[F]  " if interaction_required else "") + text)

func set_story(text: String) -> void:
    if _story_label:
        _story_label.text = text

func show_transmission(text: String, seconds: float = 8.0) -> void:
    if _transmission_text:
        _transmission_text.text = text
        _transmission_left = seconds
        # Multi-enemy briefings run two or three lines; grow the box to fit.
        var lines := maxi(1, _transmission_text.get_line_count())
        var height := 20.0 + 19.0 * float(lines)
        _transmission_panel.size.y = maxf(48.0, height)
        _transmission_text.size.y = _transmission_panel.size.y - 12.0
        (_transmission_panel.get_child(0) as ColorRect).size.y = _transmission_panel.size.y

func set_combat_status(alive: int) -> void:
    if _status_label:
        _status_label.text = "HOSTILES  %02d" % alive if alive>0 else "AREA SECURE"
        _status_label.add_theme_color_override("font_color",W.RED if alive>0 else W.AMBER)

func set_optional_status(supply_found: bool, signal_found: bool) -> void:
    _supply_found = supply_found
    _signal_found = signal_found
    _refresh_sub_objectives()
    if _optional_label:
        _optional_label.text = "STORES  %s     SIGNAL  %s" % ["OK" if supply_found else "--","OK" if signal_found else "--"]

func set_cargo_status(common_research: int, unsecured_research: int, salvage: int, fragments: int) -> void:
    if _resource_values.has("research"):
        (_resource_values["research"] as Label).text = _thousands(maxi(0, common_research) + maxi(0, unsecured_research))
        (_resource_values["salvage"] as Label).text = str(maxi(0, salvage))
        (_resource_values["signal"] as Label).text = str(maxi(0, fragments))
    if _cargo_label:
        _cargo_label.text = "CARGO  R %03d +HV %03d   S %02d   F %02d" % [maxi(0,common_research),maxi(0,unsecured_research),maxi(0,salvage),maxi(0,fragments)]
        _cargo_label.add_theme_color_override("font_color",Color("e2a76c") if unsecured_research>0 or fragments>0 else Color("8fb9c4"))

func set_intel_status(samples: Dictionary) -> void:
    var total := IntelSamples.total(samples)
    if _resource_values.has("intel"):
        (_resource_values["intel"] as Label).text = str(total)
    if _intel_label:
        _intel_label.text = "INTEL  " + IntelSamples.counts(samples, "   ", true)
        _intel_label.add_theme_color_override("font_color",Color("8ff0df") if total > 0 else Color("5d827f"))

## A room rule's countdown line (RoomRule.hud_line); an empty line hides the label.
func set_room_rule(text: String) -> void:
    if _rule_label == null: return
    _rule_label.text = text
    _rule_label.visible = not text.is_empty()

static func _thousands(value: int) -> String:
    var digits := str(value)
    var out := ""
    while digits.length() > 3:
        out = "," + digits.right(3) + out
        digits = digits.left(digits.length() - 3)
    return digits + out

func set_extraction_offer(active: bool, depth: int, cargo_value: int) -> void:
    if _extraction_panel == null:
        return
    _extraction_panel.visible = active
    if active and _extraction_label:
        _extraction_label.text = "WINDOW %d/6 // [F] SECURE %dR   [C] CONTINUE" % [clampi(depth,0,6),maxi(0,cargo_value)]

func debug_extraction_visible() -> bool:
    return _extraction_panel != null and _extraction_panel.visible
func debug_cargo_text() -> String:
    return _cargo_label.text if _cargo_label != null else ""
func debug_intel_text() -> String:
    return _intel_label.text if _intel_label != null else ""
func debug_rule_text() -> String:
    return _rule_label.text if _rule_label != null and _rule_label.visible else ""
func debug_font_source() -> String:
    return _font_source
func debug_skill_hud_contract() -> Dictionary:
    var labels: Array[String] = []
    for label in _skill_labels:
        labels.append(label.text)
    return {"keys":["Q","E","X"],"reload_key":"R","energy_text":_energy_value_label.text if _energy_value_label else "","skill_labels":labels}
func debug_uses_unique_portraits() -> bool:
    var seen: Dictionary = {}
    for card: Dictionary in _cards:
        var texture := (card.portrait as TextureRect).texture
        if texture == null or seen.has(texture): return false
        seen[texture] = true
    return seen.size() == 3

func debug_uses_unique_hud_art() -> bool:
    var paths: Dictionary = {}
    for identity in ["CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"]:
        var profile := ArtProfileRegistry.get_profile(identity)
        var weapon_path := str(profile.get("weapon_hud_asset",""))
        if weapon_path.is_empty() or paths.has(weapon_path): return false
        paths[weapon_path] = true
        var actions: Array = profile.get("hud_action_icon_assets", [])
        if actions.size() != 3: return false
        for value in actions:
            var path := str(value)
            if path.is_empty() or paths.has(path): return false
            paths[path] = true
    return paths.size() == 12
func debug_hud_art_loaded() -> bool:
    if _weapon_icon == null or _weapon_icon.texture == null or _skill_icons.size() != 3: return false
    for icon in _skill_icons:
        if icon.texture == null: return false
    return true
