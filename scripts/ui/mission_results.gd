extends Control
class_name MissionResults
const IntelSamples := preload("res://scripts/core/intel_samples.gd")

signal return_requested
signal next_mission_requested(mission_id: String)
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")

const STORY_PATH := "res://data/story/chapter_01.json"
var _summary: Dictionary = {}
var _title: Label
var _kicker: Label
var _stamp: Label
var _body: Label
var _epilogue: Label
var _campaign_line: Label
var _next_button: Button
var _backdrop: MenuBackdrop
var _panel: Panel
var _next_id := ""
var _tiles: VBoxContainer
var _contract_line: Label

func _ready() -> void:
    theme = preload("res://scripts/ui/demo_theme.gd").build()
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _build_ui()
    add_child(MenuFx.grain_overlay())
    _render()
    _play_entrance()

func configure(summary: Dictionary) -> void:
    _summary = summary.duplicate(true)
    if is_node_ready(): _render()

func _build_ui() -> void:
    _backdrop = MenuBackdrop.new()
    add_child(_backdrop)
    var atmosphere := MenuAtmosphere.new()
    atmosphere.beam_alpha = 0.035
    atmosphere.mote_count = 36
    add_child(atmosphere)
    add_child(MenuFx.band(true, 120, 0.85))
    add_child(MenuFx.band(false, 120, 0.85))
    # Vertical outcome stamp along the right margin, HUD-style.
    _stamp = MenuFx.label("", 104, Color(1, 1, 1, 0.08), 22)
    _stamp.position = Vector2(1116, 690)
    _stamp.rotation = -PI * 0.5
    add_child(_stamp)
    _panel=Panel.new(); _panel.position=Vector2(200,64); _panel.size=Vector2(880,590); add_child(_panel)
    _kicker = MenuFx.label("", 13, Color(MenuFx.AMBER, 0.95), 4); _kicker.position = Vector2(34, 22); _panel.add_child(_kicker)
    _title=Label.new(); _title.position=Vector2(32,38); _title.add_theme_font_size_override("font_size",40); _title.add_theme_color_override("font_color",Color("dff4ff")); _title.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.6)); _title.add_theme_constant_override("outline_size", 4); _panel.add_child(_title)
    var rule := ColorRect.new(); rule.color = Color(MenuFx.ACCENT, 0.25); rule.position = Vector2(34, 96); rule.size = Vector2(812, 1); _panel.add_child(rule)
    var report := MenuFx.section_header("FIELD REPORT"); report.position = Vector2(34, 110); _panel.add_child(report)
    _body=Label.new(); _body.position=Vector2(34,136); _body.size=Vector2(540,184); _body.add_theme_font_size_override("font_size",14); _body.add_theme_color_override("font_color",Color("b9ccd5")); _body.add_theme_constant_override("line_spacing", -2); _panel.add_child(_body)
    _contract_line=Label.new(); _contract_line.name="AppliedContract"; _contract_line.position=Vector2(34,326); _contract_line.size=Vector2(540,40); _contract_line.add_theme_font_size_override("font_size",12); _contract_line.add_theme_color_override("font_color",MenuFx.AMBER); _panel.add_child(_contract_line)
    _campaign_line=Label.new(); _campaign_line.position=Vector2(34,368); _campaign_line.size=Vector2(812,45); _campaign_line.add_theme_font_size_override("font_size",14); _campaign_line.add_theme_color_override("font_color",Color("73d4b5")); _panel.add_child(_campaign_line)
    # The rail starts below the two-line BASE STOCK / INTEL text (it ends at y 415) and spans the debrief box (416-498).
    var comms_bar := ColorRect.new(); comms_bar.name = "CommandBar"; comms_bar.color = Color(MenuFx.ACCENT, 0.6); comms_bar.position = Vector2(34, 416); comms_bar.size = Vector2(3, 82); _panel.add_child(comms_bar)
    _epilogue=Label.new(); _epilogue.position=Vector2(50,416); _epilogue.size=Vector2(796,82); _epilogue.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART; _epilogue.add_theme_color_override("font_color",Color("d0e1e8")); _epilogue.add_theme_font_size_override("font_size", 16); _panel.add_child(_epilogue)
    var button:=Button.new(); button.name = "ReturnToBase"; button.text="◂  BASE / REFIT"; button.position=Vector2(34,516); button.size=Vector2(360,52); button.pressed.connect(func()->void:return_requested.emit()); _panel.add_child(button)
    _next_button = Button.new(); _next_button.name = "NextOperation"; _next_button.position = Vector2(414,516); _next_button.size = Vector2(432,52); _next_button.pressed.connect(func()->void:next_mission_requested.emit(_next_id)); _panel.add_child(_next_button)
    _style_primary(_next_button)
    _tiles = VBoxContainer.new(); _tiles.position = Vector2(600, 130); _tiles.add_theme_constant_override("separation", 10); _panel.add_child(_tiles)

func _stat_tile(caption: String, value: int, tint: Color) -> void:
    var tile := PanelContainer.new()
    var style := MenuFx.panel_style(tint, 0.6)
    style.shadow_size = 0; style.content_margin_top = 8; style.content_margin_bottom = 8
    tile.add_theme_stylebox_override("panel", style)
    tile.custom_minimum_size = Vector2(272, 0)
    var row := HBoxContainer.new()
    tile.add_child(row)
    var name_label := MenuFx.label(caption, 13, Color(tint, 0.95), 2)
    name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    name_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    row.add_child(name_label)
    var value_label := MenuFx.label("+0", 30, MenuFx.INK, 1)
    row.add_child(value_label)
    _tiles.add_child(tile)
    # Count the secured cargo up so the payout reads as an event.
    var tween := value_label.create_tween()
    tween.tween_method(func(v: float) -> void: value_label.text = "+%d" % int(round(v)), 0.0, float(value), 0.9).set_delay(0.5).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

func _style_primary(button: Button) -> void:
    for state in ["normal", "hover", "pressed", "focus"]:
        var box := (theme.get_stylebox(state, "Button") as StyleBoxFlat).duplicate() as StyleBoxFlat
        if state != "focus":
            box.bg_color = Color(0.18, 0.11, 0.03, 0.94) if state == "normal" else Color(0.34, 0.21, 0.05, 0.97)
        box.border_color = Color(MenuFx.AMBER, 0.95 if state != "normal" else 0.75)
        box.shadow_color = Color(MenuFx.AMBER, 0.28)
        box.shadow_size = 14
        button.add_theme_stylebox_override(state, box)
    button.add_theme_color_override("font_color", Color("ffe2b0"))
    button.add_theme_font_size_override("font_size", 19)

func _render() -> void:
    if _title==null:return
    var outcome:=str(_summary.get("outcome","EXTRACTED")).to_upper(); var depth:=int(_summary.get("extraction_depth",0))
    var mission_id := str(_summary.get("mission_id", "MIS_CH01_01"))
    var mission_story := MissionCatalog.story(mission_id)
    var transaction: Dictionary = _summary.get("campaign_transaction", {})
    _next_id = str(transaction.get("next_mission_id", ""))
    _next_button.visible = not _next_id.is_empty()
    _next_button.text = "NEXT  /  " + str(MissionCatalog.get_mission(_next_id).get("title", "")) + "  ▸"
    var tone := MenuFx.ACCENT
    if outcome=="WIPED": _title.text="MISSION LOSS // EMERGENCY RECOVERY"; _title.add_theme_color_override("font_color",Color("f0a078")); tone = MenuFx.DANGER
    elif depth<6: _title.text="EARLY EXTRACTION // SITE-7"; _title.add_theme_color_override("font_color",Color("8fe1c2")); tone = Color("8fe1c2")
    else: _title.text="OPERATION %s COMPLETE // SITE-7" % mission_id.right(2); _title.add_theme_color_override("font_color",Color("dff4ff"))
    _kicker.text = "CHAPTER 01  //  OPERATION %s  //  DEBRIEF" % mission_id.right(2)
    _stamp.text = "LOST" if outcome == "WIPED" else ("SECURED" if depth >= 6 else "EXTRACTED")
    _stamp.label_settings.font_color = Color(tone, 0.09)
    _panel.add_theme_stylebox_override("panel", MenuFx.panel_style(tone, 0.84))
    _backdrop_for(mission_id, outcome, depth)

    var secured_research:=int(_summary.get("secured_research",_summary.get("secured_rewards",0))); var secured_salvage:=int(_summary.get("secured_salvage",0)); var secured_fragments:=int(_summary.get("secured_fragments",0)); var lost_unsecured:=int(_summary.get("lost_unsecured",0)); var lost_intel:=int(_summary.get("lost_intel_samples",0)); var secured_intel:Dictionary=_summary.get("secured_intel",{})
    _body.text="LEDGER RECOVERED         %s   [%s]\nSUPPLY CACHE RECOVERED    %s\nSIGNAL FRAGMENT FOUND     %s\nSIGNAL FRAGMENT SECURED   %s\nEXTRACTION DEPTH          %d / 6\n\nSECURED  RESEARCH %d   SALVAGE %d   SIGNAL %d\nSECURED  INTEL    %s\nLOST UNSECURED VALUE      %d\nLOST INTEL SAMPLES        %d"%[
        _flag(_summary.get("ledger_recovered",false)),"RETAINED ON WIPE" if bool(_summary.get("ledger_retained_on_wipe",false)) else "STANDARD",_flag(_summary.get("field_supplies",false)),_flag(_summary.get("carrier_fragment",false)),_flag(_summary.get("carrier_fragment_secured",secured_fragments>0)),depth,secured_research,secured_salvage,secured_fragments,_secured_intel_lines(secured_intel),lost_unsecured,lost_intel
    ]
    _body.text = _body.text.replace("LEDGER RECOVERED", str(mission_story.get("evidence_label", "MISSION EVIDENCE")) + " RECOVERED")
    _body.text = _body.text.replace("\n\nSECURED", "\nSECURED").replace("\nLOST INTEL SAMPLES", "  /  INTEL SAMPLES")
    var contract: Dictionary = _summary.get("run_contract", {})
    var contract_title := "%s // %s" % [contract.get("hazard_title", "NEUTRAL"), contract.get("opportunity_title", "STANDARD RECOVERY")]
    _contract_line.text = "CONTRACT  %s\nREWARDS  RESEARCH ×%.2f  /  SALVAGE ×%.2f  /  SIGNAL ×%.2f" % [contract_title,
        float(_summary.get("run_research_reward_multiplier",1.0)), float(_summary.get("run_salvage_reward_multiplier",1.0)), float(_summary.get("run_fragment_reward_multiplier",1.0))]
    for child in _tiles.get_children():
        _tiles.remove_child(child); child.queue_free()
    _stat_tile("RESEARCH SECURED", secured_research, MenuFx.ACCENT)
    _stat_tile("SALVAGE SECURED", secured_salvage, MenuFx.AMBER)
    _stat_tile("SIGNAL FRAGMENTS", secured_fragments, Color("b59cff"))
    if lost_unsecured > 0 or lost_intel > 0:
        _stat_tile("VALUE LOST", lost_unsecured, MenuFx.DANGER)

    var campaign:Dictionary=_summary.get("campaign",{}); var samples:Dictionary=campaign.get("intel_samples",{})
    _campaign_line.text="BASE STOCK // R %04d   S %02d   F %02d   |   ARMORY L%d LAB L%d\nINTEL %s"%[
        int(campaign.get("research_value",0)),int(campaign.get("salvage",0)),int(campaign.get("signal_fragments",0)),int(campaign.get("armory_level",0)),int(campaign.get("lab_level",0)),IntelSamples.counts(samples, " ", true)
    ]

    if outcome=="WIPED":
        _epilogue.text="COMMAND // Emergency recovery. High-value cargo, signal fragments and field intel were lost. Refit and retry this operation; the next route remains unchanged."
        return
    var story := mission_story
    if story is Dictionary and depth>=6:
        var lines:Array=story.get("post_mission",[]); var parts:PackedStringArray=[]
        for line_variant in lines:
            var line:Dictionary=line_variant; parts.append("%s // %s"%[line.get("speaker","COMMAND"),line.get("text","")])
        _epilogue.text="\n".join(parts)
    else:
        _epilogue.text="COMMAND // Cargo and intel are secure. Lab analysis can convert samples into weaknesses and operator modules before the next deployment."

func _backdrop_for(mission_id: String, outcome: String, depth: int) -> void:
    for child in _backdrop.get_children():
        child.queue_free()
    var settings := {"exposure": 0.55, "focus": Vector2(0.5, 0.45), "left_shade": 0.2, "bottom_shade": 0.3, "vignette": 0.85, "shadow_tint": Color(0.08, 0.22, 0.3)}
    if outcome == "WIPED":
        settings["shadow_tint"] = Color(0.42, 0.1, 0.08)
        settings["exposure"] = 0.45
        settings["saturation"] = 0.55
    _backdrop.setup(MenuFx.mission_plate(mission_id, 5 if depth >= 6 else 0), settings)
    move_child(_backdrop, 0)

func _play_entrance() -> void:
    _panel.modulate.a = 0.0
    _panel.position.y = 84
    var tween := create_tween().set_parallel()
    tween.tween_property(_panel, "modulate:a", 1.0, 0.45).set_delay(0.1)
    tween.tween_property(_panel, "position:y", 64.0, 0.55).set_delay(0.1).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
    _stamp.modulate.a = 0.0
    tween.tween_property(_stamp, "modulate:a", 1.0, 1.4).set_delay(0.4)

func _flag(value:bool)->String:return "YES" if value else "NO"
func debug_return()->void:return_requested.emit()
func debug_next()->void:
    if not _next_id.is_empty(): next_mission_requested.emit(_next_id)
func debug_summary()->Dictionary:return _summary.duplicate(true)

func _secured_intel_lines(samples: Dictionary) -> String:
    var legacy := IntelSamples.counts(samples,"   ",false,0,3)
    var added := IntelSamples.counts(samples,"   ",true,3)
    return legacy + ("\n                 " + added if not added.is_empty() else "")
