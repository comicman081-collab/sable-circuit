extends Control
class_name BaseLobby
const IntelSamples := preload("res://scripts/core/intel_samples.gd")

signal mission_requested
signal mission_selected_requested(mission_id: String)
signal title_requested
signal upgrade_requested(upgrade_id: String)
signal analysis_requested(analysis_id: String)
signal module_equip_requested(operator_id: String, module_id: String)
signal weapon_cycle_requested(operator_id: String)

const BASE_PLATE := "res://assets/environments/site7/stage02/reserve_field_cache/S02_07_RESERVE_FIELD_CACHE_CONTINUITY.png"
const OPERATOR_TINTS := {"CHR_PROTO_01": Color("6cc8ff"), "CHR_PROTO_02": Color("f2b45a"), "CHR_PROTO_03": Color("5ee6da")}
## Width of the facility upgrade button; a price too long for it shrinks the font instead of overflowing.
const UPGRADE_BUTTON_WIDTH := 242.0

var _facility_title: Label
var _facility_body: Label
var _upgrade_button: Button
var _purchase_status: Label
var _wallet_label: Label
var _intel_summary_label: Label
var _analysis_box: Control
var _loadout_box: Control
var _m10_status_label: Label
var _m10_panel: Panel
var _analysis_page := 0
var _analysis_page_label: Label
var _analysis_previous: Button
var _analysis_next: Button
var _weapon_labels: Dictionary = {}
var _weapon_buttons: Dictionary = {}
var _facility_buttons: Dictionary = {}
var _campaign: Dictionary = {}
var _current_facility := "COMMAND"
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
var _mission_selector: OptionButton
var _mission_title: Label
var _mission_desc: Label
var _mission_status: Label
var _mission_route: Label
var _mission_art: TextureRect
var _mission_index: Label
var selected_mission_id := "MIS_CH01_01"

func _ready() -> void:
    theme = preload("res://scripts/ui/demo_theme.gd").build()
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _build_background(); _build_header(); _build_facilities(); _build_squad_panel(); _build_mission_panel(); _build_m10_progression_panel()
    add_child(MenuFx.grain_overlay())
    _show_facility("COMMAND"); _refresh_wallet(); _refresh_m10_panel(); _refresh_weapon_buttons()
    _play_entrance()

func configure_campaign(snapshot: Dictionary) -> void:
    _campaign=snapshot.duplicate(true)
    selected_mission_id = str(_campaign.get("recommended_mission_id", "MIS_CH01_01"))
    _refresh_missions()
    if is_node_ready(): _refresh_wallet(); _show_facility(_current_facility); _refresh_m10_panel(); _refresh_weapon_buttons()

func refresh_campaign(snapshot: Dictionary, action_result: Dictionary = {}) -> void:
    _campaign=snapshot.duplicate(true); _refresh_wallet(); _refresh_action_status(action_result); _show_facility(_current_facility); _refresh_m10_panel(); _refresh_weapon_buttons()

func _build_background() -> void:
    add_child(MenuBackdrop.new().setup(BASE_PLATE, {"exposure": 0.56, "focus": Vector2(0.5, 0.45), "left_shade": 0.15, "bottom_shade": 0.2, "vignette": 0.75, "shadow_tint": Color(0.08, 0.2, 0.3)}))
    var atmosphere := MenuAtmosphere.new()
    atmosphere.beam_alpha = 0.035
    atmosphere.mote_count = 40
    add_child(atmosphere)
    add_child(MenuFx.band(true, 110, 0.9))

func _build_header() -> void:
    var kicker := MenuFx.label("SABLE CIRCUIT  //  FORWARD COMMAND", 13, Color(MenuFx.ACCENT, 0.9), 4)
    kicker.position = Vector2(32, 16)
    add_child(kicker)
    var title := MenuFx.label("OPERATIONS BASE", 34, MenuFx.INK, 6)
    title.position = Vector2(30, 32)
    add_child(title)
    var status := MenuFx.label("SITE NETWORK  ▸  DEGRADED     SIGNAL WATCH  ▸  ACTIVE", 12, Color(MenuFx.MUTED, 0.9), 2)
    status.position = Vector2(404, 52)
    add_child(status)
    var chip := PanelContainer.new()
    var chip_style := MenuFx.panel_style(MenuFx.AMBER, 0.78)
    chip_style.content_margin_top = 6; chip_style.content_margin_bottom = 6; chip_style.shadow_size = 6
    chip.add_theme_stylebox_override("panel", chip_style)
    chip.position = Vector2(690, 18)
    chip.custom_minimum_size = Vector2(454, 40)
    add_child(chip)
    _wallet_label=Label.new(); _wallet_label.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER; _wallet_label.add_theme_font_size_override("font_size",16); _wallet_label.add_theme_color_override("font_color",Color("f5dcae")); chip.add_child(_wallet_label)
    var back:=Button.new(); back.name="TitleButton"; back.text="TITLE"; back.position=Vector2(1160,18); back.size=Vector2(92,40); back.pressed.connect(func()->void:title_requested.emit()); add_child(back)
func _refresh_wallet() -> void:
    if _wallet_label==null:return
    _wallet_label.text="RESEARCH  %04d     SALVAGE  %02d     SIGNAL  %02d"%[int(_campaign.get("research_value",0)),int(_campaign.get("salvage",0)),int(_campaign.get("signal_fragments",0))]

func _panel(rect: Rect2, title: String, accent: Color = MenuFx.ACCENT) -> Panel:
    var panel := Panel.new()
    panel.position = rect.position
    panel.size = rect.size
    panel.add_theme_stylebox_override("panel", MenuFx.panel_style(accent, 0.8))
    add_child(panel)
    var header := MenuFx.section_header(title, accent)
    header.position = Vector2(18, 16)
    panel.add_child(header)
    return panel

func _build_facilities() -> void:
    var panel:=_panel(Rect2(28,92,278,390),"BASE FACILITIES")
    var names:Array[String]=["COMMAND","ARMORY","LAB"]
    var group := ButtonGroup.new()
    for i in range(names.size()):
        var button:=Button.new(); button.text=names[i]; button.toggle_mode=true; button.button_group=group; button.position=Vector2(18,52+i*52); button.size=Vector2(242,42); var facility_name:String=names[i]; button.pressed.connect(func()->void:_show_facility(facility_name)); panel.add_child(button)
        _facility_buttons[names[i]] = button
    var divider := ColorRect.new(); divider.color = Color(MenuFx.ACCENT, 0.18); divider.position = Vector2(18, 214); divider.size = Vector2(242, 1); panel.add_child(divider)
    _facility_title=Label.new(); _facility_title.position=Vector2(18,225); _facility_title.add_theme_font_size_override("font_size",19); _facility_title.add_theme_color_override("font_color",MenuFx.INK); panel.add_child(_facility_title)
    _facility_body=Label.new(); _facility_body.position=Vector2(18,255); _facility_body.size=Vector2(240,58); _facility_body.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART; _facility_body.add_theme_font_size_override("font_size",15); _facility_body.add_theme_color_override("font_color",Color("9fb4c0")); panel.add_child(_facility_body)
    _upgrade_button=Button.new(); _upgrade_button.position=Vector2(18,318); _upgrade_button.size=Vector2(UPGRADE_BUTTON_WIDTH,36); _upgrade_button.pressed.connect(_request_current_upgrade); panel.add_child(_upgrade_button)
    _purchase_status=Label.new(); _purchase_status.position=Vector2(18,360); _purchase_status.size=Vector2(242,22); _purchase_status.add_theme_font_size_override("font_size",12); panel.add_child(_purchase_status)
func _show_facility(name:String)->void:
    _current_facility=name
    if _facility_title==null:return
    if _facility_buttons.has(name): (_facility_buttons[name] as Button).set_pressed_no_signal(true)
    _facility_title.text=name; _upgrade_button.visible=name in ["ARMORY","LAB"]
    match name:
        "COMMAND": _facility_body.text="Mission routing, extraction windows\nand zone access for Site-7."
        "ARMORY":
            var level:=int(_campaign.get("armory_level",0)); var max_level:=int(_campaign.get("armory_max_level",_campaign.get("max_upgrade_level",3))); var cost:Dictionary=_campaign.get("armory_cost",{})
            _facility_body.text="CALIBRATION LEVEL %d/%d\n+8%% damage; weapon unlock tiers."%[level,max_level]; _upgrade_button.text=_upgrade_label("CALIBRATE",cost,level>=max_level); _upgrade_button.disabled=level>=max_level or not _can_afford(cost)
        "LAB":
            var level:=int(_campaign.get("lab_level",0)); var max_level:=int(_campaign.get("lab_max_level",_campaign.get("max_upgrade_level",3))); var cost:Dictionary=_campaign.get("lab_cost",{})
            _facility_body.text="SIGNAL ANALYSIS LEVEL %d/%d\n+12%% secured research per level."%[level,max_level]; _upgrade_button.text=_upgrade_label("ANALYZE CORE",cost,level>=max_level); _upgrade_button.disabled=level>=max_level or not _can_afford(cost)
    if name in ["ARMORY","LAB"]: _fit_upgrade_button()
func _fit_upgrade_button()->void:
    _upgrade_button.remove_theme_font_size_override("font_size")
    var font_size:=_upgrade_button.get_theme_font_size("font_size")
    _upgrade_button.size=Vector2(UPGRADE_BUTTON_WIDTH,_upgrade_button.size.y)
    while font_size>12 and _upgrade_button.get_minimum_size().x>UPGRADE_BUTTON_WIDTH:
        font_size-=1; _upgrade_button.add_theme_font_size_override("font_size",font_size)
    _upgrade_button.size=Vector2(UPGRADE_BUTTON_WIDTH,_upgrade_button.size.y)
func _can_afford(cost:Dictionary)->bool: return int(_campaign.get("research_value",0))>=int(cost.get("research",0)) and int(_campaign.get("salvage",0))>=int(cost.get("salvage",0)) and int(_campaign.get("signal_fragments",0))>=int(cost.get("fragments",0))
func _upgrade_label(verb:String,cost:Dictionary,maxed:bool)->String:
    if maxed: return "%s // MAX LEVEL"%verb
    var parts:Array[String]=["%dR"%int(cost.get("research",0))]
    if int(cost.get("salvage",0))>0: parts.append("%dS"%int(cost.get("salvage",0)))
    if int(cost.get("fragments",0))>0: parts.append("%dF"%int(cost.get("fragments",0)))
    return "%s // %s"%[verb," + ".join(parts)]
func _request_current_upgrade()->void:
    if _current_facility=="ARMORY":upgrade_requested.emit("ARMORY_CALIBRATION")
    elif _current_facility=="LAB":upgrade_requested.emit("LAB_SIGNAL_ANALYSIS")

func _build_squad_panel() -> void:
    var panel:=_panel(Rect2(330,92,430,390),"ACTIVE SQUAD  //  LOADOUT")
    var ids:Array[String]=["CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"]; var roles:Array[String]=["ASSAULT","BREACH","SUPPORT-RECON"]
    for i in range(ids.size()):
        var tint: Color = OPERATOR_TINTS.get(ids[i], MenuFx.ACCENT)
        var profile:Dictionary=ArtProfileRegistry.get_profile(ids[i]); var card:=Panel.new(); card.position=Vector2(18,52+i*108); card.size=Vector2(394,96); panel.add_child(card)
        var card_style := StyleBoxFlat.new(); card_style.bg_color = Color(0.01, 0.035, 0.05, 0.9); card_style.border_color = Color(tint, 0.9); card_style.border_width_left = 3; card_style.corner_radius_bottom_right = 10; card_style.corner_detail = 1
        card.add_theme_stylebox_override("panel", card_style)
        var glow := TextureRect.new(); glow.texture = _fade_texture(tint); glow.position = Vector2(3, 0); glow.size = Vector2(150, 96); glow.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; glow.stretch_mode = TextureRect.STRETCH_SCALE; glow.mouse_filter = Control.MOUSE_FILTER_IGNORE; card.add_child(glow)
        var portrait:=TextureRect.new(); portrait.name="Portrait_"+str(profile.get("name","OP")); portrait.position=Vector2(8,4); portrait.size=Vector2(92,88); portrait.expand_mode=TextureRect.EXPAND_IGNORE_SIZE; portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        var master_path:=str(profile.get("master_asset","")); if not master_path.is_empty() and ResourceLoader.exists("res://"+master_path):portrait.texture=load("res://"+master_path) as Texture2D
        if profile.has("portrait_region"):
            portrait.texture = preload("res://scripts/core/battle_texture_library.gd").portrait(profile)
        card.add_child(portrait)
        var slot := MenuFx.label("%02d" % (i + 1), 13, Color(tint, 0.9), 2); slot.position = Vector2(110, 8); card.add_child(slot)
        var n := MenuFx.label(str(profile.get("name","OP")), 24, MenuFx.INK, 4); n.position = Vector2(110, 18); card.add_child(n)
        var role := MenuFx.label(roles[i], 12, Color(tint, 0.95), 3); role.position = Vector2(112, 50); card.add_child(role)
        var weapon_label:=Label.new(); weapon_label.position=Vector2(112,66); weapon_label.size=Vector2(150,24); weapon_label.add_theme_font_size_override("font_size",12); weapon_label.add_theme_color_override("font_color",Color("9db4c1")); weapon_label.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS; card.add_child(weapon_label); _weapon_labels[ids[i]]=weapon_label
        var weapon_button:=Button.new(); weapon_button.name="WeaponCycle_"+ids[i]; weapon_button.text="NEXT WPN"; weapon_button.position=Vector2(268,48); weapon_button.size=Vector2(116,38); var operator_id:=ids[i]; weapon_button.pressed.connect(func()->void:weapon_cycle_requested.emit(operator_id)); card.add_child(weapon_button); _weapon_buttons[ids[i]]=weapon_button

func _fade_texture(tint: Color) -> GradientTexture2D:
    var gradient := Gradient.new()
    gradient.set_color(0, Color(tint, 0.26))
    gradient.set_color(1, Color(tint, 0.0))
    var texture := GradientTexture2D.new()
    texture.gradient = gradient
    texture.width = 64
    texture.height = 4
    return texture

func _refresh_weapon_buttons()->void:
    if _weapon_labels.is_empty():return
    var equipped:Dictionary=_campaign.get("equipped_weapons",{}); var unlocked:Array=_campaign.get("unlocked_weapons",[])
    for operator_id in _weapon_labels.keys():
        var weapon_id:=str(equipped.get(operator_id,"")); var spec:=WeaponRegistry.get_weapon(weapon_id); var label:=_weapon_labels[operator_id] as Label; var button:=_weapon_buttons[operator_id] as Button
        label.text=(str(spec.get("class","--"))+" // "+str(spec.get("display_name","NO WEAPON"))) if not spec.is_empty() else "NO WEAPON"
        var choices:=WeaponRegistry.compatible_weapons(str(operator_id),unlocked); button.disabled=choices.size()<=1; button.tooltip_text="Cycle unlocked compatible weapons (%d)"%choices.size()

func _build_mission_panel() -> void:
    var panel:=_panel(Rect2(784,92,468,390),"COMMAND  //  AVAILABLE OPERATION", MenuFx.AMBER)
    panel.clip_contents = true
    _mission_art = TextureRect.new(); _mission_art.name = "MissionArt"; _mission_art.position = Vector2(2, 98); _mission_art.size = Vector2(464, 190)
    _mission_art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; _mission_art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED; _mission_art.modulate = Color(0.85, 0.88, 0.92, 1.0); _mission_art.mouse_filter = Control.MOUSE_FILTER_IGNORE
    panel.add_child(_mission_art)
    var fade := TextureRect.new(); fade.texture = _vertical_fade(); fade.position = Vector2(2, 98); fade.size = Vector2(464, 190); fade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE; fade.stretch_mode = TextureRect.STRETCH_SCALE; fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    panel.add_child(fade)
    _mission_selector = OptionButton.new(); _mission_selector.name = "MissionSelector"
    _mission_selector.position = Vector2(18,48); _mission_selector.size = Vector2(430,40)
    _mission_selector.add_theme_font_size_override("font_size",16)
    _mission_selector.item_selected.connect(_select_mission); panel.add_child(_mission_selector)
    _mission_index = MenuFx.label("OP 01", 13, Color(MenuFx.AMBER, 0.95), 4); _mission_index.position = Vector2(20, 104); panel.add_child(_mission_index)
    _mission_title = Label.new(); _mission_title.position = Vector2(18,118); _mission_title.add_theme_font_size_override("font_size",30); _mission_title.add_theme_color_override("font_color", MenuFx.INK); _mission_title.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.7)); _mission_title.add_theme_constant_override("outline_size", 4); panel.add_child(_mission_title)
    _mission_desc = Label.new(); _mission_desc.position = Vector2(20,160); _mission_desc.size = Vector2(426,76); _mission_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; _mission_desc.add_theme_font_size_override("font_size",15); _mission_desc.add_theme_color_override("font_color", Color("cfdde3")); _mission_desc.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.6)); _mission_desc.add_theme_constant_override("outline_size", 3); panel.add_child(_mission_desc)
    _mission_status = Label.new(); _mission_status.position = Vector2(20,242); _mission_status.add_theme_font_size_override("font_size",14); _mission_status.add_theme_color_override("font_color",Color("70d6b8")); panel.add_child(_mission_status)
    var route:=Label.new(); route.text="6 STORY ROOMS + 2 OPTIONAL // 3 EXTRACTION WINDOWS"; route.position=Vector2(20,266); route.add_theme_font_size_override("font_size",13); route.add_theme_color_override("font_color",Color("70b6ce")); panel.add_child(route)
    _mission_route = route
    var risk:=Label.new(); risk.text="WIPE: 50% COMMON RETAINED · HIGH-VALUE / INTEL LOST"; risk.position=Vector2(20,290); risk.add_theme_font_size_override("font_size",12); risk.add_theme_color_override("font_color",Color("d59a6b")); panel.add_child(risk)
    var start:=Button.new(); start.name="OpenBriefing"; start.text="OPEN MISSION BRIEFING  ▸"; start.position=Vector2(18,322); start.size=Vector2(430,50); start.pressed.connect(func()->void:mission_selected_requested.emit(selected_mission_id)); panel.add_child(start)
    _style_primary(start)
    _refresh_missions()

func _vertical_fade() -> GradientTexture2D:
    var gradient := Gradient.new()
    gradient.offsets = PackedFloat32Array([0.0, 0.45, 1.0])
    gradient.colors = PackedColorArray([Color(0.015, 0.045, 0.06, 0.25), Color(0.015, 0.045, 0.06, 0.5), Color(0.015, 0.045, 0.06, 0.97)])
    var texture := GradientTexture2D.new()
    texture.gradient = gradient
    texture.width = 4
    texture.height = 64
    texture.fill_from = Vector2(0, 0)
    texture.fill_to = Vector2(0, 1)
    return texture

func _style_primary(button: Button) -> void:
    for state in ["normal", "hover", "pressed", "focus"]:
        var box := (theme.get_stylebox(state, "Button") as StyleBoxFlat).duplicate() as StyleBoxFlat
        if state != "focus":
            box.bg_color = Color(0.16, 0.1, 0.03, 0.92) if state == "normal" else Color(0.3, 0.19, 0.05, 0.96)
        box.border_color = Color(MenuFx.AMBER, 0.95 if state != "normal" else 0.7)
        if state == "hover" or state == "focus":
            box.shadow_color = Color(MenuFx.AMBER, 0.25)
        button.add_theme_stylebox_override(state, box)
    button.add_theme_color_override("font_color", Color("ffe2b0"))
    button.add_theme_font_size_override("font_size", 19)

func _refresh_missions() -> void:
    if _mission_selector == null: return
    var cleared: Array = _campaign.get("cleared_missions", [])
    _mission_selector.clear()
    for row: Dictionary in MissionCatalog.ui_rows(cleared):
        var index := _mission_selector.item_count
        var note := " / IN PREPARATION" if not row.deployable else (" / LOCKED" if not row.unlocked else (" / CLEARED" if row.cleared else ""))
        if (_campaign.get("redline_cleared", []) as Array).has(row.mission_id): note = " / REDLINE CLEARED"
        _mission_selector.add_item("%02d  %s%s" % [index + 1, row.title, note])
        _mission_selector.set_item_metadata(index, row.mission_id)
        _mission_selector.set_item_disabled(index, not row.unlocked)
        if row.mission_id == selected_mission_id: _mission_selector.select(index)
    _select_mission(_mission_selector.selected)

func _select_mission(index: int) -> void:
    if index < 0 or _mission_selector.is_item_disabled(index): return
    selected_mission_id = str(_mission_selector.get_item_metadata(index))
    var row := MissionCatalog.get_mission(selected_mission_id)
    _mission_title.text = row.title
    _mission_desc.text = row.synopsis
    _mission_index.text = "OPERATION %s  //  CHAPTER 01" % selected_mission_id.right(2)
    if _mission_art:
        _mission_art.texture = MenuFx.load_texture(MenuFx.mission_plate(selected_mission_id, 0))
    var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % selected_mission_id))
    var windows: Array = mission.get("extraction_offer_room_ids", [])
    _mission_route.text = "%d STORY ROOMS + %d OPTIONAL // %d EARLY WINDOWS" % [(mission.main_route as Array).size(),(mission.optional_rooms as Array).size(),windows.size()]
    _mission_selector.tooltip_text = "%d main rooms / %d optional / %d early extraction windows" % [(mission.main_route as Array).size(),(mission.optional_rooms as Array).size(),windows.size()]
    var cleared: Array = _campaign.get("cleared_missions", [])
    var following := MissionCatalog.successor(selected_mission_id)
    var next_pending := not following.is_empty() and not bool(following.get("deployable", true))
    if bool(_campaign.get("chapter_complete", false)): _mission_status.text = "CH01 COMPLETE // REPLAY AVAILABLE"
    elif cleared.has(selected_mission_id): _mission_status.text = "CLEARED // NEXT OPERATION IN PREPARATION" if next_pending else "CLEARED // REPLAY AVAILABLE"
    else: _mission_status.text = "NEXT OPERATION IN PREPARATION" if next_pending else "FULL EXTRACTION UNLOCKS THE NEXT OPERATION"
    if (_campaign.get("redline_cleared", []) as Array).has(selected_mission_id): _mission_status.text = "REDLINE CLEARED // REPLAY AVAILABLE"

func _build_m10_progression_panel()->void:
    var panel:=_panel(Rect2(28,500,1224,202),"DISCOVERY PIPELINE  //  FIELD INTEL  →  LAB ANALYSIS  →  ARMORY LOADOUT")
    _m10_panel=panel
    var heading:=panel.get_child(0).get_child(1) as Label
    heading.name="LabHeader"; heading.size=Vector2(788,22); _fit_lab_label(heading,13,Vector2(788,22))
    _intel_summary_label=Label.new(); _intel_summary_label.name="LabSamples"; _intel_summary_label.position=Vector2(18,40); _intel_summary_label.size=Vector2(570,22); _intel_summary_label.add_theme_color_override("font_color",Color("76bbb5")); panel.add_child(_intel_summary_label)
    _m10_status_label=Label.new(); _m10_status_label.name="LabStatus"; _m10_status_label.position=Vector2(824,14); _m10_status_label.size=Vector2(382,22); _m10_status_label.horizontal_alignment=HORIZONTAL_ALIGNMENT_RIGHT; _m10_status_label.add_theme_font_size_override("font_size",12); panel.add_child(_m10_status_label)
    _analysis_previous=_page_button(panel,"AnalysisPrevious","<",Vector2(600,38),-1)
    _analysis_page_label=Label.new(); _analysis_page_label.name="AnalysisPage"; _analysis_page_label.position=Vector2(648,38); _analysis_page_label.size=Vector2(40,24); _analysis_page_label.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER; _analysis_page_label.add_theme_font_size_override("font_size",12); panel.add_child(_analysis_page_label)
    _analysis_next=_page_button(panel,"AnalysisNext",">",Vector2(694,38),1)
    _analysis_box=Control.new(); _analysis_box.position=Vector2(18,70); _analysis_box.size=Vector2(760,122); panel.add_child(_analysis_box)
    _loadout_box=Control.new(); _loadout_box.position=Vector2(796,70); _loadout_box.size=Vector2(410,122); panel.add_child(_loadout_box)
    var divider := ColorRect.new(); divider.color = Color(MenuFx.ACCENT, 0.16); divider.position = Vector2(782,44); divider.size=Vector2(1,146); panel.add_child(divider)
func _page_button(panel:Panel,id:String,text:String,where:Vector2,step:int)->Button:
    var button:=Button.new(); button.name=id; button.text=text; button.position=where; button.size=Vector2(42,24); button.add_theme_font_size_override("font_size",14)
    for state in ["normal","hover","pressed","focus","disabled"]:
        var box:=theme.get_stylebox(state,"Button").duplicate() as StyleBoxFlat
        box.content_margin_left=6; box.content_margin_right=6; box.content_margin_top=2; box.content_margin_bottom=2; button.add_theme_stylebox_override(state,box)
    button.pressed.connect(func()->void:_change_analysis_page(step)); panel.add_child(button); return button
func _change_analysis_page(step:int)->void:
    _analysis_page+=step; _refresh_m10_panel()
func _refresh_m10_panel()->void:
    if _analysis_box==null or _loadout_box==null or _intel_summary_label==null:return
    var intel:Dictionary=_campaign.get("intel_samples",{}); _intel_summary_label.text="SAMPLES // "+IntelSamples.named_counts(intel); _fit_lab_label(_intel_summary_label,12,Vector2(570,22))
    _clear_control(_analysis_box); _clear_control(_loadout_box)
    var discoveries:Array=_campaign.get("discoveries",[])
    var pages:=maxi(1,ceili(float(discoveries.size())/3.0))
    _analysis_page=clampi(_analysis_page,0,pages-1)
    _analysis_page_label.text="%d/%d"%[_analysis_page+1,pages]
    _analysis_previous.disabled=_analysis_page==0; _analysis_next.disabled=_analysis_page==pages-1
    for i in range(mini(3,discoveries.size()-_analysis_page*3)):
        var row:Dictionary=discoveries[_analysis_page*3+i]; var y:=i*41.0
        var label:=Label.new(); label.name="AnalysisTitle_%s"%row.analysis_id; label.position=Vector2(0,y); label.size=Vector2(284,38); label.add_theme_color_override("font_color",Color("c4d7dc")); label.text="%s\n%s x%d + %dR"%[row.title,row.sample_key,int(row.sample_cost),int(row.research_cost)]; _analysis_box.add_child(label); _fit_lab_label(label,12,Vector2(284,38))
        var effect:=Label.new(); effect.name="AnalysisEffect_%s"%row.analysis_id; effect.position=Vector2(294,y); effect.size=Vector2(306,38); effect.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART; effect.add_theme_color_override("font_color",Color("799aa3")); effect.text=str(row.module_name)+" // "+str(row.effect_text); effect.tooltip_text=effect.text; _analysis_box.add_child(effect); _fit_lab_label(effect,10,Vector2(306,38))
        var button:=Button.new(); button.name="Analyze_%s"%row.analysis_id; button.set_meta("analysis_id",row.analysis_id); button.position=Vector2(612,y+3); button.size=Vector2(140,34); var analysis_id:=str(row.analysis_id); var analyzed:=bool(row.get("analyzed",false)); button.text="ANALYZED" if analyzed else "ANALYZE"; button.disabled=analyzed or not bool(row.get("can_analyze",false)); button.pressed.connect(func()->void:analysis_requested.emit(analysis_id)); _analysis_box.add_child(button)
    var loadout_title:=Label.new(); loadout_title.name="ModuleHeader"; loadout_title.text="OPERATOR MODULES"; loadout_title.position=Vector2(0,-24); loadout_title.size=Vector2(410,22); loadout_title.add_theme_font_size_override("font_size",13); loadout_title.add_theme_color_override("font_color",Color("b9d7e2")); _loadout_box.add_child(loadout_title)
    var unlocked:Array=_campaign.get("unlocked_modules",[]); var equipped:Dictionary=_campaign.get("equipped_modules",{})
    var operators:Array=[["ASTER","CHR_PROTO_01"],["ROOK","CHR_PROTO_02"],["MICA","CHR_PROTO_03"]]
    for i in range(operators.size()):
        var operator_id:String=operators[i][1]; var y:=i*41.0; var choices:Array[Dictionary]=[]
        for row:Dictionary in discoveries:
            if row.operator_id==operator_id and unlocked.has(row.module_id): choices.append(row)
        var equipped_id:=str(equipped.get(operator_id,"")); var selected:=-1; var names:PackedStringArray=[]
        for j in range(choices.size()):
            names.append(str(choices[j].module_name))
            if choices[j].module_id==equipped_id:selected=j
        var caption:=str(choices[selected].module_name) if selected>=0 else ("NO MODULE" if not choices.is_empty() else "LOCKED")
        # An operator with unlocked modules gets a second line naming all of them (the equipped one in brackets), so the player need not press EQUIP to learn what is unlocked.
        var two_lines:=not choices.is_empty()
        var line_box:=Vector2(240,18 if two_lines else 24)
        var label:=Label.new(); label.name="ModuleLabel_%s"%operator_id; label.position=Vector2(0,y+1 if two_lines else y+7); label.size=line_box; label.text="%s // %s"%[operators[i][0],caption]; label.add_theme_color_override("font_color",Color("d6e3e7") if two_lines else Color("596b72")); _loadout_box.add_child(label); _fit_lab_label(label,12,line_box)
        if two_lines:
            var listed:PackedStringArray=[]; var list_box:=Vector2(240,16)
            for j in range(names.size()):listed.append("[%s]"%names[j] if j==selected else names[j])
            var listing:=Label.new(); listing.name="ModuleChoices_%s"%operator_id; listing.position=Vector2(0,y+19); listing.size=list_box; listing.add_theme_color_override("font_color",Color("799aa3")); listing.text=" / ".join(listed); _loadout_box.add_child(listing); _fit_lab_label(listing,10,list_box)
        var button:=Button.new(); button.name="ModuleCycle_%s"%operator_id; button.position=Vector2(248,y+3); button.size=Vector2(154,34); button.disabled=choices.is_empty(); button.tooltip_text="Unlocked modules: "+", ".join(names)
        var requested:=""
        if choices.is_empty():button.text="LOCKED"
        elif selected<0:button.text="EQUIP"; requested=str(choices[0].module_id)
        elif selected+1<choices.size():button.text="NEXT MOD"; requested=str(choices[selected+1].module_id)
        else:button.text="UNEQUIP"
        button.set_meta("module_id",requested); button.pressed.connect(func()->void:module_equip_requested.emit(operator_id,requested)); _loadout_box.add_child(button)
func _fit_lab_label(label:Label,maximum:int,box:Vector2=Vector2.ZERO)->void:
    var target:=box if box!=Vector2.ZERO else label.size
    var font:=label.label_settings.font if label.label_settings else label.get_theme_font("font")
    for font_size in range(maximum,7,-1):
        var width:=target.x if label.autowrap_mode!=TextServer.AUTOWRAP_OFF else -1.0
        var extent:=font.get_multiline_string_size(label.text,HORIZONTAL_ALIGNMENT_LEFT,width,font_size)
        if extent.x<=target.x and extent.y<=target.y:
            if label.label_settings:label.label_settings.font_size=font_size
            else:label.add_theme_font_size_override("font_size",font_size)
            label.size=target; return
    if label.label_settings:label.label_settings.font_size=8
    else:label.add_theme_font_size_override("font_size",8)
    label.size=target

func _clear_control(control:Control)->void:
    for child in control.get_children():control.remove_child(child); child.queue_free()
func _refresh_action_status(result:Dictionary)->void:
    if result.is_empty():return
    var success:=bool(result.get("success",false)); var reason:=str(result.get("reason",""))
    if _m10_status_label:
        match reason:
            "ANALYZED":_m10_status_label.text="LAB COMPLETE // %s UNLOCKED"%str(result.get("module_id","MODULE"))
            "EQUIPPED":_m10_status_label.text="ARMORY MODULE // %s EQUIPPED"%str(result.get("module_id","MODULE"))
            "UNEQUIPPED":_m10_status_label.text="ARMORY MODULE // REMOVED"
            "WEAPON_EQUIPPED":_m10_status_label.text="ARMORY WEAPON // %s"%str(result.get("weapon_id","WEAPON"))
            _:_m10_status_label.text=("ACTION COMPLETE" if success else "ACTION BLOCKED")+" // "+reason
        _fit_lab_label(_m10_status_label,12,Vector2(382,22))
        _m10_status_label.add_theme_color_override("font_color",Color("75e0b0") if success else Color("ef9a65"))
    if _purchase_status and reason=="PURCHASED":_purchase_status.text="UPGRADE INSTALLED // LEVEL %d"%int(result.get("new_level",0)); _purchase_status.add_theme_color_override("font_color",Color("70e0a0"))

func _play_entrance() -> void:
    var index := 0
    for child in get_children():
        if child is Panel:
            var panel := child as Panel
            var final_y := panel.position.y
            panel.modulate.a = 0.0
            panel.position.y = final_y + 14.0
            var tween := create_tween().set_parallel()
            tween.tween_property(panel, "modulate:a", 1.0, 0.35).set_delay(0.06 * index)
            tween.tween_property(panel, "position:y", final_y, 0.45).set_delay(0.06 * index).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
            index += 1

func debug_select_mission()->void:mission_requested.emit()
func debug_request_upgrade(upgrade_id:String)->void:upgrade_requested.emit(upgrade_id)
func debug_request_analysis(analysis_id:String)->void:analysis_requested.emit(analysis_id)
func debug_request_module(operator_id:String,module_id:String)->void:module_equip_requested.emit(operator_id,module_id)
func debug_request_weapon_cycle(operator_id:String)->void:weapon_cycle_requested.emit(operator_id)
func debug_campaign_snapshot()->Dictionary:return _campaign.duplicate(true)
func debug_m10_contract()->Dictionary:return {"intel_samples":(_campaign.get("intel_samples",{}) as Dictionary).duplicate(true),"analyzed_intel":(_campaign.get("analyzed_intel",[]) as Array).duplicate(),"unlocked_modules":(_campaign.get("unlocked_modules",[]) as Array).duplicate(),"equipped_modules":(_campaign.get("equipped_modules",{}) as Dictionary).duplicate(true)}
func debug_m13_weapon_contract()->Dictionary:return {"unlocked_weapons":(_campaign.get("unlocked_weapons",[]) as Array).duplicate(),"equipped_weapons":(_campaign.get("equipped_weapons",{}) as Dictionary).duplicate(true),"weapon_catalog":(_campaign.get("weapon_catalog",[]) as Array).duplicate(true)}
