extends Control
class_name TitleScreen

signal start_requested

func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    var bg := ColorRect.new()
    bg.color = Color("081018")
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg)

    var center := VBoxContainer.new()
    center.position = Vector2(320, 180)
    center.size = Vector2(640, 360)
    center.alignment = BoxContainer.ALIGNMENT_CENTER
    center.add_theme_constant_override("separation", 18)
    add_child(center)

    var kicker := Label.new()
    kicker.text = "TACTICAL RECOVERY UNIT // 07"
    kicker.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    kicker.add_theme_color_override("font_color", Color("6f8494"))
    kicker.add_theme_font_size_override("font_size", 18)
    center.add_child(kicker)

    var title := Label.new()
    title.text = "SABLE CIRCUIT"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.add_theme_color_override("font_color", Color("e8f4ff"))
    title.add_theme_font_size_override("font_size", 54)
    center.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "Recover what the blackout left behind."
    subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    subtitle.add_theme_color_override("font_color", Color("8fa8b9"))
    subtitle.add_theme_font_size_override("font_size", 19)
    center.add_child(subtitle)

    var start := Button.new()
    start.text = "ENTER OPERATIONS"
    start.custom_minimum_size = Vector2(0, 56)
    start.pressed.connect(func() -> void: start_requested.emit())
    center.add_child(start)

    var build := Label.new()
    build.text = "M2 INTERNAL STORY VERTICAL SLICE"
    build.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    build.add_theme_color_override("font_color", Color("50616d"))
    build.add_theme_font_size_override("font_size", 13)
    center.add_child(build)

func debug_start() -> void:
    start_requested.emit()
