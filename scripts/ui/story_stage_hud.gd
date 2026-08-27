extends CanvasLayer
class_name StoryStageHUD

const TECH_FONT_PATH := "res://assets/fonts/Rajdhani-Medium.ttf"

var _tech_font: Font
var _font_source := "system-fallback"
var _stage: StoryStage01
var _room_label: Label
var _objective_label: Label
var _story_label: Label
var _status_label: Label
var _optional_label: Label
var _weapon_label: Label
var _ammo_label: Label
var _energy_fill: ColorRect
var _minimap: TacticalMinimap
var _cards: Array[Dictionary] = []
var _skill_labels: Array[Label] = []
var _skill_icons: Array[TextureRect] = []
var _weapon_icon: TextureRect
var _active_hud_operator_id := ""

func _ready() -> void:
    layer = 20
    _tech_font = _load_tech_font()
    _build_minimap_panel()
    _build_objective_panel()
    _build_top_status()
    _build_squad_cards()
    _build_energy_bar()
    _build_weapon_panel()
    _build_story_strip()
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
    _update_runtime_values()

func _process(_delta: float) -> void:
    _update_runtime_values()

func _panel(pos: Vector2, panel_size: Vector2, border: Color = Color("45616d"), alpha: float = 0.88) -> Panel:
    var p := Panel.new()
    p.position = pos
    p.size = panel_size
    var box := StyleBoxFlat.new()
    box.bg_color = Color(0.025,0.042,0.054,alpha)
    box.border_color = border
    box.set_border_width_all(1)
    box.corner_radius_top_left = 3
    box.corner_radius_top_right = 3
    box.corner_radius_bottom_left = 3
    box.corner_radius_bottom_right = 3
    box.shadow_color = Color(0,0,0,0.5)
    box.shadow_size = 5
    p.add_theme_stylebox_override("panel",box)
    add_child(p)
    return p

func _label(parent: Node, text_value: String, pos: Vector2, font_size: int, color: Color = Color("dce9ee")) -> Label:
    var l := Label.new()
    l.text = text_value
    l.position = pos
    l.add_theme_font_override("font",_tech_font)
    l.add_theme_font_size_override("font_size",font_size)
    l.add_theme_color_override("font_color",color)
    l.add_theme_color_override("font_shadow_color",Color(0,0,0,0.72))
    l.add_theme_constant_override("shadow_offset_x",1)
    l.add_theme_constant_override("shadow_offset_y",1)
    parent.add_child(l)
    return l

func _build_minimap_panel() -> void:
    var p := _panel(Vector2(16,14),Vector2(266,174),Color("66808a"),0.92)
    _label(p,"CH01  BLACKOUT AT SITE-7",Vector2(14,8),18,Color("d9e4e8"))
    var rule := ColorRect.new()
    rule.position = Vector2(14,34)
    rule.size = Vector2(238,1)
    rule.color = Color("4b6670")
    p.add_child(rule)
    _minimap = TacticalMinimap.new()
    _minimap.position = Vector2(14,42)
    _minimap.size = Vector2(238,102)
    p.add_child(_minimap)
    _room_label = _label(p,"SITE-7 // OUTER GATE",Vector2(14,148),13,Color("8299a4"))

func _build_objective_panel() -> void:
    var p := _panel(Vector2(16,198),Vector2(310,104),Color("506b75"),0.90)
    _label(p,"OBJECTIVES",Vector2(14,8),16,Color("e3edf0"))
    var diamond := Label.new()
    diamond.text = "◇"
    diamond.position = Vector2(12,34)
    diamond.add_theme_font_override("font",_tech_font)
    diamond.add_theme_font_size_override("font_size",20)
    diamond.add_theme_color_override("font_color",Color("f2b544"))
    p.add_child(diamond)
    _objective_label = _label(p,"Inspect the silent access terminal",Vector2(38,36),16,Color("f2c765"))
    _objective_label.size = Vector2(252,56)
    _objective_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

func _build_top_status() -> void:
    _status_label = _label(self,"AREA SECURE",Vector2(955,18),16,Color("f0b850"))
    _status_label.size = Vector2(305,26)
    _status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _optional_label = _label(self,"STORES --   SIGNAL --",Vector2(922,48),13,Color("7894a0"))
    _optional_label.size = Vector2(338,42)
    _optional_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

func _build_squad_cards() -> void:
    var ids: Array[String] = ["CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"]
    var names: Array[String] = ["ASTER","ROOK","MICA"]
    var accents: Array[Color] = [Color("69d2ff"),Color("d39a58"),Color("62d8c8")]
    for i in range(3):
        var p := _panel(Vector2(18+i*112,548),Vector2(104,154),accents[i],0.94)
        var top_glow := ColorRect.new()
        top_glow.position = Vector2(1,1)
        top_glow.size = Vector2(102,2)
        top_glow.color = Color(accents[i].r,accents[i].g,accents[i].b,0.62)
        p.add_child(top_glow)
        var num := _label(p,str(i+1),Vector2(7,4),15,Color.WHITE)
        num.size = Vector2(18,18)
        var portrait := TextureRect.new()
        portrait.position = Vector2(8,20)
        portrait.size = Vector2(88,74)
        portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        portrait.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
        p.add_child(portrait)
        _label(p,names[i],Vector2(8,94),15,Color("eef8fa"))
        var hp := _label(p,"--/--",Vector2(8,114),13,Color("cddce2"))
        var bar_bg := ColorRect.new()
        bar_bg.position = Vector2(8,135)
        bar_bg.size = Vector2(88,7)
        bar_bg.color = Color("1a252c")
        p.add_child(bar_bg)
        var bar := ColorRect.new()
        bar.position = Vector2(8,135)
        bar.size = Vector2(88,7)
        bar.color = accents[i]
        p.add_child(bar)
        _cards.append({"id":ids[i],"portrait":portrait,"hp":hp,"bar":bar,"panel":p,"accent":accents[i],"top_glow":top_glow})

func _bind_card_portraits() -> void:
    for card: Dictionary in _cards:
        var profile: Dictionary = ArtProfileRegistry.get_profile(str(card["id"]))
        var portrait_path := str(profile.get("portrait_asset",""))
        var portrait_texture := _load_visual_texture(portrait_path)
        if portrait_texture != null:
            (card["portrait"] as TextureRect).texture = portrait_texture
            continue
        var master_path := str(profile.get("master_asset",""))
        var texture := _load_visual_texture(master_path)
        if texture == null:
            continue
        var atlas := AtlasTexture.new()
        atlas.atlas = texture
        var w := float(texture.get_width())
        var h := float(texture.get_height())
        atlas.region = Rect2(w*0.20,h*0.08,w*0.60,h*0.46)
        (card["portrait"] as TextureRect).texture = atlas

func _build_energy_bar() -> void:
    _label(self,"ENERGY",Vector2(500,674),13,Color("61dce8"))
    var bg := ColorRect.new()
    bg.position = Vector2(560,681)
    bg.size = Vector2(250,7)
    bg.color = Color("15272d")
    add_child(bg)
    _energy_fill = ColorRect.new()
    _energy_fill.position = Vector2(560,681)
    _energy_fill.size = Vector2(220,7)
    _energy_fill.color = Color("71e8eb")
    add_child(_energy_fill)
    _label(self,"100/100",Vector2(818,672),13,Color("dbe8ec"))

func _build_weapon_panel() -> void:
    var p := _panel(Vector2(1012,548),Vector2(252,154),Color("345d66"),0.94)
    _label(p,"AMMO",Vector2(14,10),13,Color("829ba5"))
    _ammo_label = _label(p,"24",Vector2(162,8),36,Color("f0f5f6"))
    _ammo_label.size = Vector2(70,42)
    _ammo_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _weapon_icon = TextureRect.new()
    _weapon_icon.position = Vector2(14,29)
    _weapon_icon.size = Vector2(132,31)
    _weapon_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    _weapon_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    _weapon_icon.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
    p.add_child(_weapon_icon)
    _weapon_label = _label(p,"COIL ASSAULT RIFLE",Vector2(14,62),15,Color("62d8e3"))
    var keys: Array[String] = ["Q","E","R"]
    for i in range(3):
        var skill := _panel(Vector2(1022+i*76,630),Vector2(66,56),Color("3a515b"),0.92)
        var icon := TextureRect.new()
        icon.position = Vector2(13,4)
        icon.size = Vector2(40,34)
        icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        icon.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
        skill.add_child(icon)
        _skill_icons.append(icon)
        var key := keys[i]
        var kl := _label(skill,key,Vector2(27,35),13,Color("b5c7ce"))
        _skill_labels.append(kl)

func _build_story_strip() -> void:
    var p := _panel(Vector2(388,621),Vector2(510,38),Color("24414b"),0.62)
    _story_label = _label(p,"Move into the marked room and press F to interact.",Vector2(12,7),13,Color("b9cbd1"))
    _story_label.size = Vector2(486,26)
    _story_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS

func _update_runtime_values() -> void:
    if _stage == null or _stage.squad == null:
        return
    for i in range(mini(_cards.size(),_stage.squad.operators.size())):
        var actor := _stage.squad.operators[i]
        var card: Dictionary = _cards[i]
        (card["hp"] as Label).text = "%d/%d" % [int(actor.health),int(actor.max_health)]
        var ratio := clampf(actor.health/maxf(1.0,actor.max_health),0.0,1.0)
        (card["bar"] as ColorRect).size.x = 88.0*ratio
        var panel := card["panel"] as Panel
        panel.modulate = Color(1,1,1,1) if not actor.is_downed() else Color(0.48,0.52,0.55,0.72)
        var glow := card["top_glow"] as ColorRect
        glow.modulate.a = 1.0 if i == _stage.squad.active_index else 0.28
    var active := _stage.squad.get_active_operator()
    if active:
        _ammo_label.text = "%02d" % active.ammo
        match active.display_name:
            "ROOK": _weapon_label.text = "MAG SCATTERGUN"
            "MICA": _weapon_label.text = "SENSOR CARBINE"
            _: _weapon_label.text = "COIL ASSAULT RIFLE"
        if _active_hud_operator_id != active.operator_id:
            _active_hud_operator_id = active.operator_id
            _bind_active_hud_art(active)

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
    if not ResourceLoader.exists(resource_path):
        return null
    return load(resource_path) as Texture2D

func set_room(index: int, total: int, room_title: String, room_type: String) -> void:
    if _room_label:
        _room_label.text = "SITE-7 / %s  %02d-%02d" % [room_title.to_upper(),index+1,total]

func set_objective(text: String, interaction_required: bool = false) -> void:
    if _objective_label:
        _objective_label.text = (("[F]  " if interaction_required else "") + text)

func set_story(text: String) -> void:
    if _story_label:
        _story_label.text = text

func set_combat_status(alive: int) -> void:
    if _status_label:
        _status_label.text = "HOSTILES  %02d" % alive if alive>0 else "AREA SECURE"
        _status_label.add_theme_color_override("font_color",Color("f05b68") if alive>0 else Color("f0b850"))

func set_optional_status(supply_found: bool, signal_found: bool) -> void:
    if _optional_label:
        _optional_label.text = "STORES  %s     SIGNAL  %s" % ["OK" if supply_found else "--","OK" if signal_found else "--"]

func debug_font_source() -> String:
    return _font_source

func debug_uses_unique_portraits() -> bool:
    for card: Dictionary in _cards:
        var profile := ArtProfileRegistry.get_profile(str(card["id"]))
        if str(profile.get("portrait_asset","")).is_empty():
            return false
    return true

func debug_uses_unique_hud_art() -> bool:
    var paths: Dictionary = {}
    for identity in ["CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"]:
        var profile := ArtProfileRegistry.get_profile(identity)
        var weapon_path := str(profile.get("weapon_hud_asset",""))
        if weapon_path.is_empty() or paths.has(weapon_path):
            return false
        paths[weapon_path] = true
        var actions: Array = profile.get("hud_action_icon_assets", [])
        if actions.size() != 3:
            return false
        for value in actions:
            var path := str(value)
            if path.is_empty() or paths.has(path):
                return false
            paths[path] = true
    return paths.size() == 12

func debug_hud_art_loaded() -> bool:
    if _weapon_icon == null or _weapon_icon.texture == null or _skill_icons.size() != 3:
        return false
    for icon in _skill_icons:
        if icon.texture == null:
            return false
    return true
