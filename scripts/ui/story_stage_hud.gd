extends CanvasLayer
class_name StoryStageHUD

var _room_label: Label
var _objective_label: Label
var _story_label: Label
var _status_label: Label
var _optional_label: Label

func _ready() -> void:
    var top := Panel.new()
    top.position = Vector2(22, 18)
    top.size = Vector2(560, 126)
    add_child(top)

    var chapter := Label.new()
    chapter.text = "CH01 // BLACKOUT AT SITE-7"
    chapter.position = Vector2(18, 12)
    chapter.add_theme_font_size_override("font_size", 19)
    chapter.add_theme_color_override("font_color", Color("77c5df"))
    top.add_child(chapter)

    _room_label = Label.new()
    _room_label.position = Vector2(18, 42)
    _room_label.add_theme_font_size_override("font_size", 18)
    top.add_child(_room_label)

    _objective_label = Label.new()
    _objective_label.position = Vector2(18, 72)
    _objective_label.size = Vector2(520, 44)
    _objective_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _objective_label.add_theme_color_override("font_color", Color("d9e8ef"))
    top.add_child(_objective_label)

    var story_panel := Panel.new()
    story_panel.position = Vector2(274, 590)
    story_panel.size = Vector2(732, 108)
    add_child(story_panel)

    _story_label = Label.new()
    _story_label.position = Vector2(18, 14)
    _story_label.size = Vector2(696, 78)
    _story_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _story_label.add_theme_font_size_override("font_size", 17)
    _story_label.add_theme_color_override("font_color", Color("c7d8e0"))
    story_panel.add_child(_story_label)

    _status_label = Label.new()
    _status_label.position = Vector2(1008, 26)
    _status_label.size = Vector2(246, 58)
    _status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _status_label.add_theme_color_override("font_color", Color("ffc977"))
    add_child(_status_label)

    _optional_label = Label.new()
    _optional_label.position = Vector2(1000, 90)
    _optional_label.size = Vector2(254, 88)
    _optional_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _optional_label.add_theme_color_override("font_color", Color("7f9eae"))
    add_child(_optional_label)

func set_room(index: int, total: int, room_title: String, room_type: String) -> void:
    _room_label.text = "%02d/%02d  %s  [%s]" % [index + 1, total, room_title, room_type]

func set_objective(text: String, interaction_required: bool = false) -> void:
    _objective_label.text = ("F  //  " if interaction_required else "") + text

func set_story(text: String) -> void:
    _story_label.text = text

func set_combat_status(alive: int) -> void:
    _status_label.text = "HOSTILES REMAINING  %d" % alive if alive > 0 else "AREA SECURE"

func set_optional_status(supply_found: bool, signal_found: bool) -> void:
    _optional_label.text = "OPTIONAL\nSTORES  %s\nSIGNAL LAB  %s" % ["RECOVERED" if supply_found else "UNRESOLVED", "RECOVERED" if signal_found else "UNRESOLVED"]
