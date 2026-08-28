extends Control
class_name MissionResults

signal return_requested

const STORY_PATH := "res://data/story/chapter_01.json"
var _summary: Dictionary = {}
var _title: Label
var _body: Label
var _epilogue: Label
var _campaign_line: Label

func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _build_ui()
    _render()

func configure(summary: Dictionary) -> void:
    _summary = summary.duplicate(true)
    if is_node_ready():
        _render()

func _build_ui() -> void:
    var bg := ColorRect.new()
    bg.color = Color("071016")
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg)

    var panel := Panel.new()
    panel.position = Vector2(220, 82)
    panel.size = Vector2(840, 556)
    add_child(panel)

    _title = Label.new()
    _title.position = Vector2(34, 26)
    _title.add_theme_font_size_override("font_size", 34)
    _title.add_theme_color_override("font_color", Color("dff4ff"))
    panel.add_child(_title)

    _body = Label.new()
    _body.position = Vector2(34, 92)
    _body.size = Vector2(772, 218)
    _body.add_theme_font_size_override("font_size", 17)
    _body.add_theme_color_override("font_color", Color("a9bfca"))
    panel.add_child(_body)

    _campaign_line = Label.new()
    _campaign_line.position = Vector2(34, 310)
    _campaign_line.size = Vector2(772, 52)
    _campaign_line.add_theme_font_size_override("font_size", 16)
    _campaign_line.add_theme_color_override("font_color", Color("73d4b5"))
    panel.add_child(_campaign_line)

    _epilogue = Label.new()
    _epilogue.position = Vector2(34, 372)
    _epilogue.size = Vector2(772, 94)
    _epilogue.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _epilogue.add_theme_color_override("font_color", Color("d0e1e8"))
    panel.add_child(_epilogue)

    var button := Button.new()
    button.text = "RETURN TO OPERATIONS BASE"
    button.position = Vector2(34, 482)
    button.size = Vector2(772, 46)
    button.pressed.connect(func() -> void: return_requested.emit())
    panel.add_child(button)

func _render() -> void:
    if _title == null:
        return
    var outcome := str(_summary.get("outcome", "EXTRACTED")).to_upper()
    var depth := int(_summary.get("extraction_depth", 0))
    if outcome == "WIPED":
        _title.text = "MISSION LOSS // EMERGENCY RECOVERY"
        _title.add_theme_color_override("font_color", Color("f0a078"))
    elif depth < 6:
        _title.text = "EARLY EXTRACTION // SITE-7"
        _title.add_theme_color_override("font_color", Color("8fe1c2"))
    else:
        _title.text = "MISSION COMPLETE // SITE-7"
        _title.add_theme_color_override("font_color", Color("dff4ff"))

    var secured_research := int(_summary.get("secured_research", _summary.get("secured_rewards", 0)))
    var secured_salvage := int(_summary.get("secured_salvage", 0))
    var secured_fragments := int(_summary.get("secured_fragments", 0))
    var lost_unsecured := int(_summary.get("lost_unsecured", 0))
    _body.text = "LEDGER RECOVERED         %s   [%s]\nSUPPLY CACHE RECOVERED    %s\nSIGNAL FRAGMENT FOUND     %s\nSIGNAL FRAGMENT SECURED   %s\nEXTRACTION DEPTH          %d / 6\n\nSECURED  RESEARCH %d   SALVAGE %d   SIGNAL %d\nLOST UNSECURED VALUE      %d" % [
        _flag(_summary.get("ledger_recovered", false)),
        "RETAINED ON WIPE" if bool(_summary.get("ledger_retained_on_wipe", false)) else "STANDARD",
        _flag(_summary.get("field_supplies", false)),
        _flag(_summary.get("carrier_fragment", false)),
        _flag(_summary.get("carrier_fragment_secured", secured_fragments > 0)),
        depth,
        secured_research,
        secured_salvage,
        secured_fragments,
        lost_unsecured
    ]

    var campaign: Dictionary = _summary.get("campaign", {})
    _campaign_line.text = "BASE STOCK // RESEARCH %04d   SALVAGE %02d   SIGNAL %02d   |   ARMORY L%d   LAB L%d" % [
        int(campaign.get("research_value",0)),
        int(campaign.get("salvage",0)),
        int(campaign.get("signal_fragments",0)),
        int(campaign.get("armory_level",0)),
        int(campaign.get("lab_level",0))
    ]

    if outcome == "WIPED":
        _epilogue.text = "COMMAND // Squad telemetry went dark. Story-critical ledger data survived the emergency beacon, but unsecured high-value cargo and signal fragments were lost."
        return
    var story = JSON.parse_string(FileAccess.get_file_as_string(STORY_PATH))
    if story is Dictionary and depth >= 6:
        var lines: Array = story.get("post_mission", [])
        var parts: PackedStringArray = []
        for line_variant in lines:
            var line: Dictionary = line_variant
            parts.append("%s // %s" % [line.get("speaker", "COMMAND"), line.get("text", "")])
        _epilogue.text = "\n".join(parts)
    else:
        _epilogue.text = "COMMAND // Cargo is secure. The deeper Site-7 route remains unresolved; redeploy when the squad is ready to risk another push."

func _flag(value: bool) -> String:
    return "YES" if value else "NO"

func debug_return() -> void:
    return_requested.emit()

func debug_summary() -> Dictionary:
    return _summary.duplicate(true)
