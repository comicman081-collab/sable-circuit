extends Control
class_name BaseLobby

signal mission_requested
signal title_requested

var _facility_title: Label
var _facility_body: Label

func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _build_background()
    _build_header()
    _build_facilities()
    _build_squad_panel()
    _build_mission_panel()
    _show_facility("COMMAND")

func _build_background() -> void:
    var bg := ColorRect.new()
    bg.color = Color("0b141b")
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg)
    var floor := ColorRect.new()
    floor.color = Color("111f29")
    floor.position = Vector2(0, 510)
    floor.size = Vector2(1280, 210)
    add_child(floor)

func _build_header() -> void:
    var title := Label.new()
    title.text = "SABLE CIRCUIT // OPERATIONS BASE"
    title.position = Vector2(32, 22)
    title.add_theme_font_size_override("font_size", 25)
    title.add_theme_color_override("font_color", Color("d9ecf7"))
    add_child(title)

    var status := Label.new()
    status.text = "SITE NETWORK  ▸  DEGRADED     SIGNAL WATCH  ▸  ACTIVE"
    status.position = Vector2(742, 30)
    status.add_theme_font_size_override("font_size", 14)
    status.add_theme_color_override("font_color", Color("79a5bb"))
    add_child(status)

    var back := Button.new()
    back.text = "TITLE"
    back.position = Vector2(1160, 70)
    back.size = Vector2(88, 34)
    back.pressed.connect(func() -> void: title_requested.emit())
    add_child(back)

func _build_facilities() -> void:
    var panel := Panel.new()
    panel.position = Vector2(28, 92)
    panel.size = Vector2(278, 390)
    add_child(panel)

    var label := Label.new()
    label.text = "BASE FACILITIES"
    label.position = Vector2(18, 18)
    label.add_theme_font_size_override("font_size", 18)
    panel.add_child(label)

    var names := ["COMMAND", "ARMORY", "LAB"]
    for i in range(names.size()):
        var button := Button.new()
        button.text = names[i]
        button.position = Vector2(18, 58 + i * 54)
        button.size = Vector2(242, 42)
        var facility_name: String = names[i]
        button.pressed.connect(func() -> void: _show_facility(facility_name))
        panel.add_child(button)

    _facility_title = Label.new()
    _facility_title.position = Vector2(18, 235)
    _facility_title.add_theme_font_size_override("font_size", 17)
    panel.add_child(_facility_title)

    _facility_body = Label.new()
    _facility_body.position = Vector2(18, 270)
    _facility_body.size = Vector2(240, 98)
    _facility_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _facility_body.add_theme_color_override("font_color", Color("9fb4c0"))
    panel.add_child(_facility_body)

func _show_facility(name: String) -> void:
    _facility_title.text = name
    match name:
        "COMMAND":
            _facility_body.text = "Mission routing, story briefings and zone access. Site-7 is the only authorized operation in this slice."
        "ARMORY":
            _facility_body.text = "ASTER / ROOK / MICA loadouts are checked here. Weapon crafting unlocks after recovered field materials exist."
        "LAB":
            _facility_body.text = "Recovered samples and signal fragments are analyzed here. Chapter 01 can return a carrier-signal fragment."

func _build_squad_panel() -> void:
    var panel := Panel.new()
    panel.position = Vector2(330, 92)
    panel.size = Vector2(430, 390)
    add_child(panel)

    var title := Label.new()
    title.text = "ACTIVE SQUAD // 3 OPERATORS"
    title.position = Vector2(20, 18)
    title.add_theme_font_size_override("font_size", 18)
    panel.add_child(title)

    var roster := [
        ["ASTER", "ASSAULT", "AR / EXPOSED exploit"],
        ["ROOK", "BREACH", "Close disruption / armor break"],
        ["MICA", "SUPPORT-RECON", "Scan / shield / signal analysis"]
    ]
    for i in range(roster.size()):
        var card := Panel.new()
        card.position = Vector2(20, 62 + i * 94)
        card.size = Vector2(390, 78)
        panel.add_child(card)
        var n := Label.new()
        n.text = "%d  %s    [%s]" % [i + 1, roster[i][0], roster[i][1]]
        n.position = Vector2(14, 11)
        n.add_theme_font_size_override("font_size", 17)
        card.add_child(n)
        var d := Label.new()
        d.text = roster[i][2]
        d.position = Vector2(14, 42)
        d.add_theme_color_override("font_color", Color("8fa6b4"))
        card.add_child(d)

func _build_mission_panel() -> void:
    var panel := Panel.new()
    panel.position = Vector2(784, 92)
    panel.size = Vector2(468, 390)
    add_child(panel)

    var title := Label.new()
    title.text = "COMMAND // AVAILABLE OPERATION"
    title.position = Vector2(20, 18)
    title.add_theme_font_size_override("font_size", 18)
    panel.add_child(title)

    var chapter := Label.new()
    chapter.text = "CHAPTER 01\nBLACKOUT AT SITE-7"
    chapter.position = Vector2(20, 72)
    chapter.add_theme_font_size_override("font_size", 28)
    chapter.add_theme_color_override("font_color", Color("e7f2f7"))
    panel.add_child(chapter)

    var desc := Label.new()
    desc.text = "A sealed research site stopped transmitting after a containment alarm. Recover the missing team ledger, identify the signal source, and extract before auxiliary power fails."
    desc.position = Vector2(20, 158)
    desc.size = Vector2(426, 100)
    desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    desc.add_theme_color_override("font_color", Color("9bb1bd"))
    panel.add_child(desc)

    var route := Label.new()
    route.text = "ROUTE: 6 STORY ROOMS + 2 OPTIONAL ROOMS"
    route.position = Vector2(20, 270)
    route.add_theme_color_override("font_color", Color("70b6ce"))
    panel.add_child(route)

    var start := Button.new()
    start.text = "OPEN MISSION BRIEFING"
    start.position = Vector2(20, 312)
    start.size = Vector2(426, 52)
    start.pressed.connect(func() -> void: mission_requested.emit())
    panel.add_child(start)

func debug_select_mission() -> void:
    mission_requested.emit()
