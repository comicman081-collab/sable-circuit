extends Control
class_name MissionResults

signal return_requested

const STORY_PATH := "res://data/story/chapter_01.json"
var _summary: Dictionary = {}
var _title: Label
var _body: Label
var _epilogue: Label

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
    panel.position = Vector2(220, 105)
    panel.size = Vector2(840, 510)
    add_child(panel)

    _title = Label.new()
    _title.position = Vector2(34, 30)
    _title.add_theme_font_size_override("font_size", 34)
    _title.add_theme_color_override("font_color", Color("dff4ff"))
    panel.add_child(_title)

    _body = Label.new()
    _body.position = Vector2(34, 100)
    _body.size = Vector2(772, 170)
    _body.add_theme_font_size_override("font_size", 18)
    _body.add_theme_color_override("font_color", Color("a9bfca"))
    panel.add_child(_body)

    _epilogue = Label.new()
    _epilogue.position = Vector2(34, 280)
    _epilogue.size = Vector2(772, 120)
    _epilogue.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _epilogue.add_theme_color_override("font_color", Color("d0e1e8"))
    panel.add_child(_epilogue)

    var button := Button.new()
    button.text = "RETURN TO OPERATIONS BASE"
    button.position = Vector2(34, 430)
    button.size = Vector2(772, 52)
    button.pressed.connect(func() -> void: return_requested.emit())
    panel.add_child(button)

func _render() -> void:
    if _title == null:
        return
    _title.text = "MISSION COMPLETE // SITE-7"
    var rewards := int(_summary.get("secured_rewards", 0))
    _body.text = "LEDGER RECOVERED      %s\nEMERGENCY STORES      %s\nCARRIER FRAGMENT      %s\n\nSECURED RESEARCH VALUE      %d" % [
        _flag(_summary.get("ledger_recovered", false)),
        _flag(_summary.get("field_supplies", false)),
        _flag(_summary.get("carrier_fragment", false)),
        rewards
    ]
    var story = JSON.parse_string(FileAccess.get_file_as_string(STORY_PATH))
    if story is Dictionary:
        var lines: Array = story.get("post_mission", [])
        var parts: PackedStringArray = []
        for line_variant in lines:
            var line: Dictionary = line_variant
            parts.append("%s // %s" % [line.get("speaker", "COMMAND"), line.get("text", "")])
        _epilogue.text = "\n".join(parts)

func _flag(value: bool) -> String:
    return "YES" if value else "NO"

func debug_return() -> void:
    return_requested.emit()
