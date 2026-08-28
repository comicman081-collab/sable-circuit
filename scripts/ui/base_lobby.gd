extends Control
class_name BaseLobby

signal mission_requested
signal title_requested
signal upgrade_requested(upgrade_id: String)
signal analysis_requested(analysis_id: String)
signal module_equip_requested(operator_id: String, module_id: String)

var _facility_title: Label
var _facility_body: Label
var _upgrade_button: Button
var _purchase_status: Label
var _wallet_label: Label
var _intel_summary_label: Label
var _analysis_box: Control
var _loadout_box: Control
var _m10_status_label: Label
var _campaign: Dictionary = {}
var _current_facility := "COMMAND"

func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _build_background()
    _build_header()
    _build_facilities()
    _build_squad_panel()
    _build_mission_panel()
    _build_m10_progression_panel()
    _show_facility("COMMAND")
    _refresh_wallet()
    _refresh_m10_panel()

func configure_campaign(snapshot: Dictionary) -> void:
    _campaign = snapshot.duplicate(true)
    if is_node_ready():
        _refresh_wallet()
        _show_facility(_current_facility)
        _refresh_m10_panel()

func refresh_campaign(snapshot: Dictionary, action_result: Dictionary = {}) -> void:
    _campaign = snapshot.duplicate(true)
    _refresh_wallet()
    _refresh_action_status(action_result)
    _show_facility(_current_facility)
    _refresh_m10_panel()

func _build_background() -> void:
    var bg:=ColorRect.new(); bg.color=Color("0b141b"); bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); add_child(bg)
    var floor:=ColorRect.new(); floor.color=Color("111f29"); floor.position=Vector2(0,492); floor.size=Vector2(1280,228); add_child(floor)

func _build_header() -> void:
    var title:=Label.new(); title.text="SABLE CIRCUIT // OPERATIONS BASE"; title.position=Vector2(32,22); title.add_theme_font_size_override("font_size",25); title.add_theme_color_override("font_color",Color("d9ecf7")); add_child(title)
    var status:=Label.new(); status.text="SITE NETWORK  ▸  DEGRADED     SIGNAL WATCH  ▸  ACTIVE"; status.position=Vector2(742,24); status.add_theme_font_size_override("font_size",14); status.add_theme_color_override("font_color",Color("79a5bb")); add_child(status)
    _wallet_label=Label.new(); _wallet_label.position=Vector2(690,50); _wallet_label.size=Vector2(470,26); _wallet_label.horizontal_alignment=HORIZONTAL_ALIGNMENT_RIGHT; _wallet_label.add_theme_font_size_override("font_size",15); _wallet_label.add_theme_color_override("font_color",Color("d3e6ec")); add_child(_wallet_label)
    var back:=Button.new(); back.text="TITLE"; back.position=Vector2(1160,70); back.size=Vector2(88,34); back.pressed.connect(func()->void:title_requested.emit()); add_child(back)

func _refresh_wallet() -> void:
    if _wallet_label == null: return
    _wallet_label.text = "RESEARCH  %04d     SALVAGE  %02d     SIGNAL  %02d" % [
        int(_campaign.get("research_value",0)),int(_campaign.get("salvage",0)),int(_campaign.get("signal_fragments",0))
    ]

func _build_facilities() -> void:
    var panel:=Panel.new(); panel.position=Vector2(28,92); panel.size=Vector2(278,390); add_child(panel)
    var label:=Label.new(); label.text="BASE FACILITIES"; label.position=Vector2(18,18); label.add_theme_font_size_override("font_size",18); panel.add_child(label)
    var names:Array[String]=["COMMAND","ARMORY","LAB"]
    for i in range(names.size()):
        var button:=Button.new(); button.text=names[i]; button.position=Vector2(18,58+i*54); button.size=Vector2(242,42); var facility_name:String=names[i]; button.pressed.connect(func()->void:_show_facility(facility_name)); panel.add_child(button)
    _facility_title=Label.new(); _facility_title.position=Vector2(18,225); _facility_title.add_theme_font_size_override("font_size",17); panel.add_child(_facility_title)
    _facility_body=Label.new(); _facility_body.position=Vector2(18,255); _facility_body.size=Vector2(240,58); _facility_body.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART; _facility_body.add_theme_font_size_override("font_size",15); _facility_body.add_theme_color_override("font_color",Color("9fb4c0")); panel.add_child(_facility_body)
    _upgrade_button=Button.new(); _upgrade_button.position=Vector2(18,318); _upgrade_button.size=Vector2(242,36); _upgrade_button.pressed.connect(_request_current_upgrade); panel.add_child(_upgrade_button)
    _purchase_status=Label.new(); _purchase_status.position=Vector2(18,360); _purchase_status.size=Vector2(242,22); _purchase_status.add_theme_font_size_override("font_size",12); panel.add_child(_purchase_status)

func _show_facility(name:String)->void:
    _current_facility=name
    if _facility_title == null: return
    _facility_title.text=name
    _upgrade_button.visible = name in ["ARMORY","LAB"]
    match name:
        "COMMAND":
            _facility_body.text="Mission routing, extraction windows\nand zone access for Site-7."
        "ARMORY":
            var level:=int(_campaign.get("armory_level",0)); var max_level:=int(_campaign.get("max_upgrade_level",3)); var cost:Dictionary=_campaign.get("armory_cost",{})
            _facility_body.text="CALIBRATION LEVEL %d/%d\n+8%% projectile damage per level."%[level,max_level]
            _upgrade_button.text="CALIBRATE // %dR + %dS"%[int(cost.get("research",0)),int(cost.get("salvage",0))]
            _upgrade_button.disabled = level>=max_level or not _can_afford(cost)
        "LAB":
            var level:=int(_campaign.get("lab_level",0)); var max_level:=int(_campaign.get("max_upgrade_level",3)); var cost:Dictionary=_campaign.get("lab_cost",{})
            _facility_body.text="SIGNAL ANALYSIS LEVEL %d/%d\n+12%% secured research per level."%[level,max_level]
            _upgrade_button.text="ANALYZE CORE // %dR + %dF"%[int(cost.get("research",0)),int(cost.get("fragments",0))]
            _upgrade_button.disabled = level>=max_level or not _can_afford(cost)

func _can_afford(cost: Dictionary) -> bool:
    return int(_campaign.get("research_value",0))>=int(cost.get("research",0)) and int(_campaign.get("salvage",0))>=int(cost.get("salvage",0)) and int(_campaign.get("signal_fragments",0))>=int(cost.get("fragments",0))

func _request_current_upgrade() -> void:
    if _current_facility == "ARMORY": upgrade_requested.emit("ARMORY_CALIBRATION")
    elif _current_facility == "LAB": upgrade_requested.emit("LAB_SIGNAL_ANALYSIS")

func _build_squad_panel() -> void:
    var panel:=Panel.new(); panel.position=Vector2(330,92); panel.size=Vector2(430,390); add_child(panel)
    var title:=Label.new(); title.text="ACTIVE SQUAD // 3 UNIQUE OPERATORS"; title.position=Vector2(20,18); title.add_theme_font_size_override("font_size",18); panel.add_child(title)
    var ids:Array[String]=["CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"]
    var roles:Array[String]=["ASSAULT","BREACH","SUPPORT-RECON"]
    var details:Array[String]=["Precision coil AR / fast recovery","Magnetic scattergun / heavy breach","Sensor carbine / scan & support"]
    for i in range(ids.size()):
        var profile:Dictionary=ArtProfileRegistry.get_profile(ids[i])
        var card:=Panel.new(); card.position=Vector2(20,62+i*94); card.size=Vector2(390,78); panel.add_child(card)
        var portrait:=TextureRect.new(); portrait.name="Portrait_"+str(profile.get("name","OP")); portrait.position=Vector2(4,3); portrait.size=Vector2(76,72); portrait.expand_mode=TextureRect.EXPAND_IGNORE_SIZE; portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        var master_path:=str(profile.get("master_asset","")); if not master_path.is_empty() and ResourceLoader.exists("res://"+master_path): portrait.texture=load("res://"+master_path) as Texture2D
        card.add_child(portrait)
        var n:=Label.new(); n.text="%d  %s    [%s]"%[i+1,str(profile.get("name","OP")),roles[i]]; n.position=Vector2(88,10); n.add_theme_font_size_override("font_size",17); card.add_child(n)
        var d:=Label.new(); d.text=details[i]; d.position=Vector2(88,42); d.add_theme_color_override("font_color",Color("8fa6b4")); card.add_child(d)

func _build_mission_panel() -> void:
    var panel:=Panel.new(); panel.position=Vector2(784,92); panel.size=Vector2(468,390); add_child(panel)
    var title:=Label.new(); title.text="COMMAND // AVAILABLE OPERATION"; title.position=Vector2(20,18); title.add_theme_font_size_override("font_size",18); panel.add_child(title)
    var chapter:=Label.new(); chapter.text="CHAPTER 01\nBLACKOUT AT SITE-7"; chapter.position=Vector2(20,72); chapter.add_theme_font_size_override("font_size",28); chapter.add_theme_color_override("font_color",Color("e7f2f7")); panel.add_child(chapter)
    var desc:=Label.new(); desc.text="Recover the missing team ledger.\nPush deeper for signal value and intel samples,\nor extract early before the risk cargo is lost."; desc.position=Vector2(20,158); desc.size=Vector2(426,82); desc.add_theme_font_size_override("font_size",15); desc.add_theme_color_override("font_color",Color("9bb1bd")); panel.add_child(desc)
    var route:=Label.new(); route.text="6 STORY ROOMS + 2 OPTIONAL // 3 EXTRACTION WINDOWS"; route.position=Vector2(20,266); route.add_theme_color_override("font_color",Color("70b6ce")); panel.add_child(route)
    var risk:=Label.new(); risk.text="WIPE: 50% COMMON RETAINED · HIGH-VALUE / INTEL LOST"; risk.position=Vector2(20,290); risk.add_theme_font_size_override("font_size",12); risk.add_theme_color_override("font_color",Color("d59a6b")); panel.add_child(risk)
    var start:=Button.new(); start.text="OPEN MISSION BRIEFING"; start.position=Vector2(20,322); start.size=Vector2(426,46); start.pressed.connect(func()->void:mission_requested.emit()); panel.add_child(start)

func _build_m10_progression_panel() -> void:
    var panel:=Panel.new(); panel.position=Vector2(28,500); panel.size=Vector2(1224,202); add_child(panel)
    var title:=Label.new(); title.text="DISCOVERY PIPELINE // FIELD INTEL → LAB ANALYSIS → ARMORY LOADOUT"; title.position=Vector2(16,8); title.add_theme_font_size_override("font_size",17); title.add_theme_color_override("font_color",Color("b8e5e1")); panel.add_child(title)
    _intel_summary_label=Label.new(); _intel_summary_label.position=Vector2(16,34); _intel_summary_label.size=Vector2(520,22); _intel_summary_label.add_theme_font_size_override("font_size",13); _intel_summary_label.add_theme_color_override("font_color",Color("76bbb5")); panel.add_child(_intel_summary_label)
    _m10_status_label=Label.new(); _m10_status_label.position=Vector2(824,34); _m10_status_label.size=Vector2(382,22); _m10_status_label.horizontal_alignment=HORIZONTAL_ALIGNMENT_RIGHT; _m10_status_label.add_theme_font_size_override("font_size",12); panel.add_child(_m10_status_label)
    _analysis_box=Control.new(); _analysis_box.position=Vector2(16,60); _analysis_box.size=Vector2(760,126); panel.add_child(_analysis_box)
    _loadout_box=Control.new(); _loadout_box.position=Vector2(796,60); _loadout_box.size=Vector2(410,126); panel.add_child(_loadout_box)

func _refresh_m10_panel() -> void:
    if _analysis_box==null or _loadout_box==null or _intel_summary_label==null: return
    var intel:Dictionary=_campaign.get("intel_samples",{})
    _intel_summary_label.text="SAMPLES // SECURITY %02d   ABERRANT %02d   ANCHOR %02d"%[int(intel.get("SECURITY",0)),int(intel.get("ABERRANT",0)),int(intel.get("ANCHOR",0))]
    _clear_control(_analysis_box); _clear_control(_loadout_box)
    var discoveries:Array=_campaign.get("discoveries",[])
    for i in range(mini(3,discoveries.size())):
        var row:Dictionary=discoveries[i]
        var y:=i*40.0
        var label:=Label.new(); label.position=Vector2(0,y); label.size=Vector2(470,38); label.add_theme_font_size_override("font_size",12); label.add_theme_color_override("font_color",Color("c4d7dc")); label.text="%s\n%s x%d + %dR"%[str(row.get("title","UNKNOWN")),str(row.get("sample_key","?")),int(row.get("sample_cost",0)),int(row.get("research_cost",0))]; _analysis_box.add_child(label)
        var effect:=Label.new(); effect.position=Vector2(300,y+2); effect.size=Vector2(300,34); effect.add_theme_font_size_override("font_size",10); effect.add_theme_color_override("font_color",Color("799aa3")); effect.text=str(row.get("module_name","MODULE"))+" // "+str(row.get("effect_text","")); effect.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS; _analysis_box.add_child(effect)
        var button:=Button.new(); button.position=Vector2(612,y+3); button.size=Vector2(140,32); var analysis_id:=str(row.get("analysis_id","")); var analyzed:=bool(row.get("analyzed",false)); button.text="ANALYZED" if analyzed else "ANALYZE"; button.disabled=analyzed or not bool(row.get("can_analyze",false)); button.pressed.connect(func()->void:analysis_requested.emit(analysis_id)); _analysis_box.add_child(button)
    var loadout_title:=Label.new(); loadout_title.text="OPERATOR LOADOUT"; loadout_title.position=Vector2(0,-24); loadout_title.add_theme_font_size_override("font_size",13); loadout_title.add_theme_color_override("font_color",Color("b9d7e2")); _loadout_box.add_child(loadout_title)
    var unlocked:Array=_campaign.get("unlocked_modules",[]); var equipped:Dictionary=_campaign.get("equipped_modules",{})
    var loadouts:Array=[
        ["ASTER","CHR_PROTO_01","MOD_PRISM_FOCUS","PRISM FOCUS"],
        ["ROOK","CHR_PROTO_02","MOD_BREACH_LINER","BREACH LINER"],
        ["MICA","CHR_PROTO_03","MOD_SENSOR_ARRAY","SENSOR ARRAY"]
    ]
    for i in range(loadouts.size()):
        var row:Array=loadouts[i]; var y:=i*40.0; var operator_id:String=row[1]; var module_id:String=row[2]; var equipped_id:=str(equipped.get(operator_id,"")); var is_unlocked:=unlocked.has(module_id); var is_equipped:=equipped_id==module_id
        var label:=Label.new(); label.position=Vector2(0,y+7); label.size=Vector2(240,24); label.text="%s  //  %s"%[row[0],row[3] if is_unlocked else "LOCKED"]; label.add_theme_font_size_override("font_size",12); label.add_theme_color_override("font_color",Color("d6e3e7") if is_unlocked else Color("596b72")); _loadout_box.add_child(label)
        var button:=Button.new(); button.position=Vector2(248,y+3); button.size=Vector2(154,32); button.text="UNEQUIP" if is_equipped else ("EQUIP" if is_unlocked else "LOCKED"); button.disabled=not is_unlocked; var requested_module: String="" if is_equipped else module_id; button.pressed.connect(func()->void:module_equip_requested.emit(operator_id,requested_module)); _loadout_box.add_child(button)

func _clear_control(control: Control) -> void:
    for child in control.get_children():
        control.remove_child(child)
        child.queue_free()

func _refresh_action_status(result: Dictionary) -> void:
    if result.is_empty(): return
    var success:=bool(result.get("success",false)); var reason:=str(result.get("reason",""))
    if _m10_status_label:
        match reason:
            "ANALYZED": _m10_status_label.text="LAB COMPLETE // %s UNLOCKED"%str(result.get("module_id","MODULE"))
            "EQUIPPED": _m10_status_label.text="ARMORY LOADOUT // %s EQUIPPED"%str(result.get("module_id","MODULE"))
            "UNEQUIPPED": _m10_status_label.text="ARMORY LOADOUT // MODULE REMOVED"
            _: _m10_status_label.text=("ACTION COMPLETE" if success else "ACTION BLOCKED")+" // "+reason
        _m10_status_label.add_theme_color_override("font_color",Color("75e0b0") if success else Color("ef9a65"))
    if _purchase_status and reason=="PURCHASED":
        _purchase_status.text="UPGRADE INSTALLED // LEVEL %d"%int(result.get("new_level",0)); _purchase_status.add_theme_color_override("font_color",Color("70e0a0"))

func debug_select_mission()->void: mission_requested.emit()
func debug_request_upgrade(upgrade_id:String)->void: upgrade_requested.emit(upgrade_id)
func debug_request_analysis(analysis_id:String)->void: analysis_requested.emit(analysis_id)
func debug_request_module(operator_id:String,module_id:String)->void: module_equip_requested.emit(operator_id,module_id)
func debug_campaign_snapshot()->Dictionary: return _campaign.duplicate(true)
func debug_m10_contract()->Dictionary:
    return {"intel_samples":(_campaign.get("intel_samples",{}) as Dictionary).duplicate(true),"analyzed_intel":(_campaign.get("analyzed_intel",[]) as Array).duplicate(),"unlocked_modules":(_campaign.get("unlocked_modules",[]) as Array).duplicate(),"equipped_modules":(_campaign.get("equipped_modules",{}) as Dictionary).duplicate(true)}
