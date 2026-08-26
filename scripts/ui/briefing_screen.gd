extends Control
class_name BriefingScreen

signal deploy_requested
signal back_requested

const STORY_PATH := "res://data/story/chapter_01.json"

var _story: Dictionary = {}
var _briefing: Array = []
var _line_index := 0
var _speaker: Label
var _dialogue: Label
var _next_button: Button
var _deploy_button: Button

func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _load_story()
    _build_ui()
    _render_line()

func _load_story() -> void:
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(STORY_PATH))
    if parsed is Dictionary:
        _story = parsed
        _briefing = _story.get("briefing", [])

func _build_ui() -> void:
    var bg := ColorRect.new()
    bg.color = Color("081118")
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg)

    var header := Label.new()
    header.text = "%s // %s" % [_story.get("chapter_id", "CH01"), _story.get("title", "BLACKOUT AT SITE-7")]
    header.position = Vector2(46, 34)
    header.add_theme_font_size_override("font_size", 30)
    header.add_theme_color_override("font_color", Color("e5f2f8"))
    add_child(header)

    var synopsis := Label.new()
    synopsis.text = _story.get("synopsis", "")
    synopsis.position = Vector2(46, 92)
    synopsis.size = Vector2(1180, 88)
    synopsis.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    synopsis.add_theme_color_override("font_color", Color("8ea7b4"))
    add_child(synopsis)

    var map_panel := Panel.new()
    map_panel.position = Vector2(46, 205)
    map_panel.size = Vector2(440, 340)
    add_child(map_panel)

    var route := Label.new()
    route.text = "MISSION ROUTE\n\n01  OUTER GATE\n      ↓\n02  DECON CORRIDOR\n      ↓\n03  ARCHIVE ANNEX  ── OPTIONAL STORES\n      ↓\n04  CONTAINMENT JUNCTION ── SIGNAL LAB\n      ↓\n05  CONTAINMENT CORE C\n      ↓\n06  EMERGENCY LIFT / EXTRACTION"
    route.position = Vector2(24, 20)
    route.size = Vector2(390, 300)
    route.add_theme_font_size_override("font_size", 17)
    route.add_theme_color_override("font_color", Color("a9c6d5"))
    map_panel.add_child(route)

    var comms := Panel.new()
    comms.position = Vector2(520, 205)
    comms.size = Vector2(706, 340)
    add_child(comms)

    var comms_label := Label.new()
    comms_label.text = "PRE-DEPLOYMENT COMMS"
    comms_label.position = Vector2(24, 22)
    comms_label.add_theme_font_size_override("font_size", 17)
    comms.add_child(comms_label)

    _speaker = Label.new()
    _speaker.position = Vector2(24, 76)
    _speaker.add_theme_font_size_override("font_size", 22)
    _speaker.add_theme_color_override("font_color", Color("6ec3df"))
    comms.add_child(_speaker)

    _dialogue = Label.new()
    _dialogue.position = Vector2(24, 118)
    _dialogue.size = Vector2(656, 116)
    _dialogue.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _dialogue.add_theme_font_size_override("font_size", 19)
    _dialogue.add_theme_color_override("font_color", Color("d3e1e8"))
    comms.add_child(_dialogue)

    _next_button = Button.new()
    _next_button.text = "NEXT COMMS"
    _next_button.position = Vector2(452, 266)
    _next_button.size = Vector2(228, 48)
    _next_button.pressed.connect(_advance_line)
    comms.add_child(_next_button)

    _deploy_button = Button.new()
    _deploy_button.text = "DEPLOY ASTER / ROOK / MICA"
    _deploy_button.position = Vector2(810, 584)
    _deploy_button.size = Vector2(416, 58)
    _deploy_button.visible = false
    _deploy_button.pressed.connect(func() -> void: deploy_requested.emit())
    add_child(_deploy_button)

    var back := Button.new()
    back.text = "BACK TO BASE"
    back.position = Vector2(46, 584)
    back.size = Vector2(190, 48)
    back.pressed.connect(func() -> void: back_requested.emit())
    add_child(back)

func _render_line() -> void:
    if _briefing.is_empty():
        _speaker.text = "COMMAND"
        _dialogue.text = "Briefing data unavailable."
        _next_button.visible = false
        _deploy_button.visible = true
        return
    var line: Dictionary = _briefing[_line_index]
    _speaker.text = str(line.get("speaker", "COMMAND"))
    _dialogue.text = str(line.get("text", ""))
    _next_button.text = "NEXT COMMS" if _line_index < _briefing.size() - 1 else "BRIEFING COMPLETE"

func _advance_line() -> void:
    if _line_index < _briefing.size() - 1:
        _line_index += 1
        _render_line()
    else:
        _next_button.visible = false
        _deploy_button.visible = true

func debug_complete_briefing() -> void:
    _line_index = maxi(0, _briefing.size() - 1)
    _render_line()
    _next_button.visible = false
    _deploy_button.visible = true

func debug_deploy() -> void:
    deploy_requested.emit()
