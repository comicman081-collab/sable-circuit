extends Control
class_name BriefingScreen

signal deploy_requested
signal back_requested

const STORY_PATH := "res://data/story/chapter_01.json"
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
const SPEAKERS := {
    "ASTER": {"id": "CHR_PROTO_01", "role": "SQUAD LEAD  //  ASSAULT", "color": Color("6cc8ff")},
    "ROOK": {"id": "CHR_PROTO_02", "role": "BREACHER  //  HEAVY", "color": Color("f2b45a")},
    "MICA": {"id": "CHR_PROTO_03", "role": "SUPPORT  //  RECON", "color": Color("5ee6da")},
}
const TYPE_TAGS := {"EVENT": Color("8aa3b1"), "COMBAT": Color("ff8a6b"), "RESEARCH": Color("6cc8ff"), "ELITE": Color("f2b45a"), "BOSS": Color("ff5d73"), "EXTRACTION": Color("5ee6da")}
var mission_id := "MIS_CH01_01"
var _mission: Dictionary = {}
var contract_run_id := "CH01-RUN-000001"
var allow_redline := false
var _contracts: Array[Dictionary] = []
var _selected_contract := 0
var _contract_panel: Panel
var _contract_button: Button
var _contract_choices: Array[Button] = []
var _comms_panel: Panel

var _story: Dictionary = {}
var _briefing: Array = []
var _line_index := 0
var _speaker: Label
var _role: Label
var _dialogue: Label
var _counter: Label
var _portrait: TextureRect
var _emblem: Control
var _pips: HBoxContainer
var _next_button: Button
var _deploy_button: Button
var _type_tween: Tween

class RouteGraph extends Control:
    var rooms: Array = []
    var optional: Array = []
    func _draw() -> void:
        var face := get_theme_font("font")
        var x := 14.0
        var step := 36.0
        var top := 12.0
        draw_line(Vector2(x, top), Vector2(x, top + step * (rooms.size() - 1)), Color(MenuFx.ACCENT, 0.35), 2.0)
        for i in range(rooms.size()):
            var room: Dictionary = rooms[i]
            var y := top + step * i
            var kind := str(room.get("type", "EVENT"))
            var tag_color: Color = BriefingScreen.TYPE_TAGS.get(kind, MenuFx.MUTED)
            draw_circle(Vector2(x, y), 6.0 if kind in ["BOSS", "EXTRACTION"] else 4.5, tag_color)
            draw_circle(Vector2(x, y), 9.5, Color(tag_color, 0.18))
            draw_string(face, Vector2(x + 22, y + 6), "%02d" % (i + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(MenuFx.MUTED, 0.9))
            draw_string(face, Vector2(x + 50, y + 6), str(room.get("title", "")).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, size.x - 150, 16, MenuFx.INK)
            draw_string(face, Vector2(0, y + 5), kind, HORIZONTAL_ALIGNMENT_RIGHT, size.x - 4, 11, Color(tag_color, 0.95))
        var branch_top := top + step * rooms.size() + 12.0
        draw_string(face, Vector2(x - 4, branch_top), "OPTIONAL RECOVERY", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(MenuFx.AMBER, 0.9))
        for i in range(optional.size()):
            var y := branch_top + 24.0 + 26.0 * i
            draw_line(Vector2(x, y - 14), Vector2(x, y), Color(MenuFx.AMBER, 0.35), 1.0)
            draw_line(Vector2(x, y), Vector2(x + 14, y), Color(MenuFx.AMBER, 0.35), 1.0)
            draw_string(face, Vector2(x + 22, y + 5), "+  " + str((optional[i] as Dictionary).get("title", "")).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, 300, 14, Color("d9c7a6"))
            # The main room the branch leaves from (by default the one two ahead of it).
            var hub := mini(i + 2, rooms.size() - 1)
            for r in range(rooms.size()):
                if str((rooms[r] as Dictionary).get("id", "")) == str((optional[i] as Dictionary).get("from", "")): hub = r
            draw_string(face, Vector2(0, y + 5), "OFF %02d" % (hub + 1), HORIZONTAL_ALIGNMENT_RIGHT, size.x - 4, 11, Color(MenuFx.AMBER, 0.9))

class CommandEmblem extends Control:
    var _time := 0.0
    func _process(delta: float) -> void:
        _time += delta
        queue_redraw()
    func _draw() -> void:
        var center := size * 0.5
        draw_rect(Rect2(Vector2.ZERO, size), Color(0.02, 0.06, 0.08, 0.9))
        for ring in range(3):
            var radius := 26.0 + ring * 16.0
            draw_arc(center, radius, _time * (0.6 + ring * 0.3), _time * (0.6 + ring * 0.3) + TAU * 0.72, 48, Color(MenuFx.ACCENT, 0.5 - ring * 0.12), 2.0)
        var face := get_theme_font("font")
        draw_string(face, center + Vector2(-40, 8), "CMD", HORIZONTAL_ALIGNMENT_CENTER, 80, 26, MenuFx.INK)

func _ready() -> void:
    theme = preload("res://scripts/ui/demo_theme.gd").build()
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _load_story()
    _build_ui()
    add_child(MenuFx.grain_overlay())
    _render_line()
    _play_entrance()

func _load_story() -> void:
    _story = MissionCatalog.story(mission_id)
    _briefing = _story.get("briefing", [])
    _mission = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission_id))

func _build_ui() -> void:
    add_child(MenuBackdrop.new().setup(MenuFx.mission_plate(mission_id, 0), {
        "exposure": 0.6, "focus": Vector2(0.62, 0.5), "left_shade": 0.35, "bottom_shade": 0.3,
        "vignette": 0.8, "shadow_tint": Color(0.08, 0.22, 0.34)}))
    var atmosphere := MenuAtmosphere.new()
    atmosphere.beam_alpha = 0.04
    atmosphere.mote_count = 44
    add_child(atmosphere)
    add_child(MenuFx.band(true, 150, 0.9))
    add_child(MenuFx.band(false, 130, 0.85))

    var kicker := MenuFx.label("CHAPTER 01  //  OPERATION %s  //  MISSION BRIEFING" % mission_id.right(2), 13, Color(MenuFx.AMBER, 0.95), 4)
    kicker.position = Vector2(48, 30)
    add_child(kicker)
    var header := MenuFx.glow_title(str(_story.get("title", "SITE-7")).to_upper(), 46, MenuFx.INK, MenuFx.ACCENT, 6)
    header.name = "MissionTitle"
    header.position = Vector2(44, 46)
    add_child(header)
    var synopsis := Label.new()
    synopsis.text = _story.get("synopsis", "")
    synopsis.position = Vector2(48, 112)
    synopsis.size = Vector2(820, 60)
    synopsis.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    synopsis.add_theme_font_size_override("font_size", 17)
    synopsis.add_theme_color_override("font_color", Color("a9c0cc"))
    add_child(synopsis)

    var map_panel := Panel.new()
    map_panel.name = "RoutePanel"
    map_panel.position = Vector2(46, 196)
    map_panel.size = Vector2(404, 400)
    map_panel.add_theme_stylebox_override("panel", MenuFx.panel_style(MenuFx.ACCENT, 0.82))
    add_child(map_panel)
    var route_header := MenuFx.section_header("MISSION ROUTE")
    route_header.position = Vector2(18, 16)
    map_panel.add_child(route_header)
    var graph := RouteGraph.new()
    graph.rooms = _mission.get("main_route", [])
    graph.optional = _mission.get("optional_rooms", [])
    graph.position = Vector2(20, 54)
    graph.size = Vector2(366, 336)
    graph.mouse_filter = Control.MOUSE_FILTER_IGNORE
    map_panel.add_child(graph)

    var comms := Panel.new()
    comms.name = "CommsPanel"
    comms.position = Vector2(476, 196)
    comms.size = Vector2(758, 400)
    _comms_panel = comms
    comms.add_theme_stylebox_override("panel", MenuFx.panel_style(MenuFx.ACCENT, 0.82))
    add_child(comms)
    var comms_header := MenuFx.section_header("PRE-DEPLOYMENT COMMS")
    comms_header.position = Vector2(20, 16)
    comms.add_child(comms_header)
    _counter = MenuFx.label("", 13, Color(MenuFx.MUTED, 0.9), 3)
    _counter.position = Vector2(640, 18)
    comms.add_child(_counter)

    var frame := Panel.new()
    frame.position = Vector2(20, 56)
    frame.size = Vector2(164, 196)
    var frame_style := StyleBoxFlat.new()
    frame_style.bg_color = Color(0.01, 0.03, 0.04, 0.95)
    frame_style.border_color = Color(MenuFx.ACCENT, 0.5)
    frame_style.set_border_width_all(1)
    frame_style.corner_radius_top_left = 12
    frame_style.corner_detail = 1
    frame.add_theme_stylebox_override("panel", frame_style)
    comms.add_child(frame)
    _portrait = TextureRect.new()
    _portrait.position = Vector2(4, 4)
    _portrait.size = Vector2(156, 188)
    _portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    _portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
    frame.add_child(_portrait)
    _emblem = CommandEmblem.new()
    _emblem.position = Vector2(4, 4)
    _emblem.size = Vector2(156, 188)
    frame.add_child(_emblem)

    _speaker = Label.new()
    _speaker.position = Vector2(206, 58)
    _speaker.add_theme_font_size_override("font_size", 28)
    _speaker.add_theme_color_override("font_color", Color("6ec3df"))
    comms.add_child(_speaker)
    _role = MenuFx.label("", 12, Color(MenuFx.MUTED, 0.95), 3)
    _role.position = Vector2(208, 96)
    comms.add_child(_role)

    _dialogue = Label.new()
    _dialogue.position = Vector2(206, 126)
    _dialogue.size = Vector2(528, 150)
    _dialogue.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _dialogue.add_theme_font_size_override("font_size", 20)
    _dialogue.add_theme_color_override("font_color", Color("dde9ee"))
    comms.add_child(_dialogue)

    _pips = HBoxContainer.new()
    _pips.position = Vector2(22, 272)
    _pips.add_theme_constant_override("separation", 6)
    comms.add_child(_pips)
    for i in range(_briefing.size()):
        var pip := ColorRect.new()
        pip.custom_minimum_size = Vector2(26, 4)
        pip.mouse_filter = Control.MOUSE_FILTER_IGNORE
        _pips.add_child(pip)

    _next_button = Button.new()
    _next_button.name = "NextComms"
    _next_button.text = "NEXT COMMS  ▸"
    _next_button.position = Vector2(496, 326)
    _next_button.size = Vector2(242, 52)
    _next_button.pressed.connect(_advance_line)
    comms.add_child(_next_button)

    _deploy_button = Button.new()
    _deploy_button.name = "DeployButton"
    _deploy_button.text = "DEPLOY  ASTER / ROOK / MICA  ▸"
    _deploy_button.position = Vector2(790, 616)
    _deploy_button.size = Vector2(444, 62)
    _deploy_button.visible = false
    _deploy_button.pressed.connect(func() -> void: deploy_requested.emit())
    _style_primary(_deploy_button)
    add_child(_deploy_button)

    var back := Button.new()
    back.name = "BackToBase"
    back.text = "◂  BACK TO BASE"
    back.position = Vector2(46, 622)
    back.size = Vector2(210, 50)
    back.pressed.connect(func() -> void: back_requested.emit())
    add_child(back)
    _build_contracts()
    _next_button.grab_focus()

func _build_contracts() -> void:
    _contracts = RunContract.offers(contract_run_id, mission_id)
    if allow_redline: _contracts.append(RunContract.redline(contract_run_id))
    _contract_button = Button.new()
    _contract_button.name = "ChooseContract"
    _contract_button.text = "CONTRACT 1  /  CHANGE"
    _contract_button.position = Vector2(280, 622)
    _contract_button.size = Vector2(480, 50)
    _contract_button.pressed.connect(func() -> void: _show_contracts(not _contract_panel.visible))
    add_child(_contract_button)
    _contract_panel = Panel.new()
    _contract_panel.name = "ContractPanel"
    _contract_panel.position = Vector2(476, 196)
    _contract_panel.size = Vector2(758, 400)
    _contract_panel.add_theme_stylebox_override("panel", MenuFx.panel_style(MenuFx.AMBER, 0.90))
    _contract_panel.visible = false
    add_child(_contract_panel)
    var header := MenuFx.section_header("DEPLOYMENT CONTRACT  //  SELECT ONE")
    header.position = Vector2(22, 16)
    _contract_panel.add_child(header)
    var group := ButtonGroup.new()
    for i in range(_contracts.size()):
        var choice := Button.new()
        choice.name = "ContractChoice%d" % i
        choice.position = Vector2(22, 52 + i * 77)
        choice.size = Vector2(714, 72)
        choice.add_theme_font_size_override("font_size", 14)
        choice.alignment = HORIZONTAL_ALIGNMENT_LEFT
        choice.toggle_mode = true
        choice.button_group = group
        var c := _contracts[i]
        choice.text = "%s  //  %s%s\n%s" % [c.hazard_title, c.opportunity_title, "  [DEFAULT]" if i == 0 else "", RunContract.effect_text(c)]
        choice.pressed.connect(func() -> void: _select_contract(i))
        _contract_panel.add_child(choice)
        _contract_choices.append(choice)
    _contract_choices[0].set_pressed_no_signal(true)
    var note := MenuFx.label("Contracts expire on return. REDLINE keeps boss movement and warning timing.", 12, MenuFx.MUTED)
    note.position = Vector2(22, 372)
    _contract_panel.add_child(note)

func _select_contract(index: int) -> void:
    if index < 0 or index >= _contracts.size(): return
    _selected_contract = index
    _contract_button.text = "%s  /  %s" % ["REDLINE" if index == 3 else "CONTRACT %d" % (index + 1), "COMMS" if _contract_panel.visible else "CHANGE"]

func _show_contracts(show_choices: bool) -> void:
    _contract_panel.visible = show_choices
    _comms_panel.visible = not show_choices
    _select_contract(_selected_contract)
    if show_choices: _contract_choices[_selected_contract].grab_focus()
    elif _next_button.visible: _next_button.grab_focus()
    else: _deploy_button.grab_focus()

func selected_contract_index() -> int:
    return _selected_contract

func selected_contract() -> Dictionary:
    return _contracts[_selected_contract].duplicate(true)

func _style_primary(button: Button) -> void:
    for state in ["normal", "hover", "pressed", "focus"]:
        var box := (theme.get_stylebox(state, "Button") as StyleBoxFlat).duplicate() as StyleBoxFlat
        if state != "focus":
            box.bg_color = Color(0.18, 0.11, 0.03, 0.94) if state == "normal" else Color(0.34, 0.21, 0.05, 0.97)
        box.border_color = Color(MenuFx.AMBER, 0.95 if state != "normal" else 0.75)
        box.shadow_color = Color(MenuFx.AMBER, 0.3)
        box.shadow_size = 16
        button.add_theme_stylebox_override(state, box)
    button.add_theme_color_override("font_color", Color("ffe2b0"))
    button.add_theme_color_override("font_hover_color", Color.WHITE)
    button.add_theme_font_size_override("font_size", 22)

func _render_line() -> void:
    if _briefing.is_empty():
        _speaker.text = "COMMAND"
        _dialogue.text = "Briefing data unavailable."
        _next_button.visible = false
        _deploy_button.visible = true
        return
    var line: Dictionary = _briefing[_line_index]
    var speaker := str(line.get("speaker", "COMMAND"))
    _speaker.text = speaker
    _dialogue.text = str(line.get("text", ""))
    _next_button.text = "NEXT COMMS  ▸" if _line_index < _briefing.size() - 1 else "BRIEFING COMPLETE  ▸"
    _counter.text = "%02d / %02d" % [_line_index + 1, _briefing.size()]
    var info: Dictionary = SPEAKERS.get(speaker.to_upper(), {})
    var tint: Color = info.get("color", MenuFx.ACCENT)
    _speaker.add_theme_color_override("font_color", tint)
    _role.text = str(info.get("role", "SABLE COMMAND  //  REMOTE UPLINK"))
    _portrait.texture = null
    if info.has("id"):
        _portrait.texture = BattleTextureLibrary.portrait(ArtProfileRegistry.get_profile(str(info.id)))
    _emblem.visible = _portrait.texture == null
    for i in range(_pips.get_child_count()):
        (_pips.get_child(i) as ColorRect).color = tint if i <= _line_index else Color(MenuFx.DIM, 0.4)
    if _type_tween and _type_tween.is_valid():
        _type_tween.kill()
    _dialogue.visible_ratio = 0.0
    _type_tween = create_tween()
    _type_tween.tween_property(_dialogue, "visible_ratio", 1.0, clampf(_dialogue.text.length() / 70.0, 0.35, 1.6))

func _advance_line() -> void:
    if _dialogue.visible_ratio < 1.0:
        # First press finishes the transmission; the next one advances.
        if _type_tween and _type_tween.is_valid(): _type_tween.kill()
        _dialogue.visible_ratio = 1.0
        return
    if _line_index < _briefing.size() - 1:
        _line_index += 1
        _render_line()
    else:
        _reveal_deploy()

func _reveal_deploy() -> void:
    _next_button.visible = false
    _deploy_button.visible = true
    _show_contracts(true)
    _deploy_button.modulate.a = 0.0
    var tween := create_tween()
    tween.tween_property(_deploy_button, "modulate:a", 1.0, 0.3)
    var pulse := _deploy_button.create_tween().set_loops()
    pulse.tween_property(_deploy_button, "self_modulate", Color(1.15, 1.08, 0.95), 0.9).set_trans(Tween.TRANS_SINE)
    pulse.tween_property(_deploy_button, "self_modulate", Color.WHITE, 0.9).set_trans(Tween.TRANS_SINE)
    _deploy_button.grab_focus()

func _play_entrance() -> void:
    var index := 0
    for child in get_children():
        if child is Panel:
            var panel := child as Panel
            var final_y := panel.position.y
            panel.modulate.a = 0.0
            panel.position.y = final_y + 16.0
            var tween := create_tween().set_parallel()
            tween.tween_property(panel, "modulate:a", 1.0, 0.4).set_delay(0.12 + 0.1 * index)
            tween.tween_property(panel, "position:y", final_y, 0.5).set_delay(0.12 + 0.1 * index).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
            index += 1

func debug_complete_briefing() -> void:
    _line_index = maxi(0, _briefing.size() - 1)
    _render_line()
    _dialogue.visible_ratio = 1.0
    _reveal_deploy()

func debug_deploy() -> void:
    deploy_requested.emit()
