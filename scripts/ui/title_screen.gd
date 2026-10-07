extends Control
class_name TitleScreen

signal start_requested
signal battle_requested(stage_number: int)
signal mission_requested
signal intro_requested(continue_to_base: bool)

const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
# The signal-anchor chamber: the campaign's recurring threat, graded for type.
const TITLE_PLATE := "res://assets/environments/site7_v2/stage03/S3_R05/S3_R05_GAME.png"
const TRAINING := ["BLACKOUT", "RECOVERY SWEEP", "INNER BREACH", "FORGE DESCENT", "OFFSHORE NULL"]

var backdrop: MenuBackdrop
var lineup: OperatorLineup
var training_panel: PanelContainer
var _title_block: Control
var _menu: VBoxContainer
var _glitch: Array[Label] = []
var _glitch_timer := 5.0
var _glitch_left := 0.0
var _status_dot: ColorRect

class HudFrame extends Control:
    var _time := 0.0
    func _process(delta: float) -> void:
        _time += delta
        queue_redraw()
    func _draw() -> void:
        var line := Color(MenuFx.ACCENT, 0.32)
        var inset := 22.0
        var arm := 34.0
        for corner in [Vector2(inset, inset), Vector2(size.x - inset, inset), Vector2(inset, size.y - inset), Vector2(size.x - inset, size.y - inset)]:
            var sx := 1.0 if corner.x < size.x * 0.5 else -1.0
            var sy := 1.0 if corner.y < size.y * 0.5 else -1.0
            draw_line(corner, corner + Vector2(arm * sx, 0), line, 1.5)
            draw_line(corner, corner + Vector2(0, arm * sy), line, 1.5)
        # Top telemetry rule with a travelling tick.
        var y := 26.0
        draw_line(Vector2(76, y), Vector2(size.x - 76, y), Color(MenuFx.ACCENT, 0.08), 1.0)
        var travel := fmod(_time * 90.0, size.x - 152.0)
        draw_rect(Rect2(76 + travel, y - 1.5, 26, 3), Color(MenuFx.ACCENT, 0.4))
        for i in range(25):
            var x := 76.0 + (size.x - 152.0) * float(i) / 24.0
            draw_line(Vector2(x, y - (4.0 if i % 6 == 0 else 2.0)), Vector2(x, y), Color(MenuFx.ACCENT, 0.2), 1.0)

func _ready() -> void:
    theme = preload("res://scripts/ui/demo_theme.gd").build()
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    var cleared := _cleared_missions()

    backdrop = MenuBackdrop.new().setup(TITLE_PLATE, {
        "exposure": 0.8, "focus": Vector2(0.7, 0.36), "left_shade": 0.7,
        "shadow_tint": Color(0.1, 0.24, 0.38), "saturation": 0.95, "vignette": 0.85, "flip_h": true})
    add_child(backdrop)
    var atmosphere := MenuAtmosphere.new()
    add_child(atmosphere)

    lineup = OperatorLineup.new()
    lineup.position = Vector2(600, 118)
    lineup.size = Vector2(660, 572)
    add_child(lineup)

    add_child(MenuFx.band(true, 120, 0.82))
    add_child(MenuFx.band(false, 210, 0.96))
    var frame := HudFrame.new()
    frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(frame)

    _build_title_block()
    _build_menu(cleared)
    _build_campaign_widget(cleared)
    _build_training_panel()
    _build_utility_row()
    add_child(MenuFx.grain_overlay())
    _play_entrance()

func _cleared_missions() -> Array:
    var flow := get_tree().get_first_node_in_group("game_flow")
    if flow != null and flow.get("campaign") != null:
        return (flow.campaign.cleared_missions as Array).duplicate()
    return []

func _build_title_block() -> void:
    _title_block = Control.new()
    _title_block.name = "TitleBlock"
    _title_block.position = Vector2(70, 0)
    _title_block.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(_title_block)
    _status_dot = ColorRect.new()
    _status_dot.color = MenuFx.ACCENT
    _status_dot.position = Vector2(4, 66)
    _status_dot.size = Vector2(7, 7)
    _title_block.add_child(_status_dot)
    var kicker := MenuFx.label("SITE-7 CONTAINMENT  //  CHAPTER 01  //  BLACKOUT PROTOCOL", 14, Color(MenuFx.ACCENT, 0.9), 4)
    kicker.position = Vector2(22, 58)
    _title_block.add_child(kicker)
    var sable := MenuFx.glow_title("SABLE", 108, MenuFx.INK, MenuFx.ACCENT, 18)
    sable.position = Vector2(-4, 68)
    _title_block.add_child(sable)
    var circuit := MenuFx.glow_title("CIRCUIT", 108, Color("a6f6ee"), MenuFx.ACCENT, 18)
    circuit.position = Vector2(-4, 160)
    _title_block.add_child(circuit)
    # Chromatic split copies, only visible during a brief signal glitch.
    for tint in [Color(1.0, 0.25, 0.3, 0.55), Color(0.2, 0.95, 1.0, 0.55)]:
        var copy := MenuFx.label("CIRCUIT", 108, tint, 18)
        copy.position = circuit.position
        copy.visible = false
        _title_block.add_child(copy)
        _glitch.append(copy)
    var rule := ColorRect.new()
    rule.color = MenuFx.ACCENT
    rule.position = Vector2(2, 300)
    rule.size = Vector2(56, 3)
    _title_block.add_child(rule)
    var hair := ColorRect.new()
    hair.color = Color(MenuFx.ACCENT, 0.3)
    hair.position = Vector2(66, 301)
    hair.size = Vector2(330, 1)
    _title_block.add_child(hair)
    var tagline := MenuFx.label("Recover what the blackout left behind.", 20, MenuFx.MUTED, 1)
    tagline.position = Vector2(0, 310)
    _title_block.add_child(tagline)

func _build_menu(cleared: Array) -> void:
    _menu = VBoxContainer.new()
    _menu.name = "MainMenu"
    _menu.position = Vector2(64, 362)
    _menu.size = Vector2(440, 0)
    _menu.add_theme_constant_override("separation", 8)
    add_child(_menu)
    var next_id := MissionCatalog.recommended(cleared)
    var next_title := str(MissionCatalog.get_mission(next_id).get("title", "SITE-7"))
    var entries := [
        ["StartDemo", "START CAMPAIGN", "Intro cinematic  ·  Operations base", func() -> void: intro_requested.emit(true)],
        ["QuickDeploy", "QUICK DEPLOY", "Next operation  ·  %s  %s" % [next_id.right(2), next_title], func() -> void: mission_requested.emit()],
        ["OperationsBase", "OPERATIONS BASE", "Squad  ·  Armory  ·  Lab  ·  Loadouts", func() -> void: start_requested.emit()],
        ["TrainingSimulator", "TRAINING SIMULATOR", "Isolated encounters  ·  no save rewards", _toggle_training],
    ]
    for i in range(entries.size()):
        var row: Array = entries[i]
        var button := CinematicMenuButton.new(str(row[1]), str(row[2]), "%02d" % (i + 1))
        button.name = str(row[0])
        button.custom_minimum_size = Vector2(440, 58)
        button.pressed.connect(row[3])
        _menu.add_child(button)
    (_menu.get_child(0) as Control).grab_focus()

## One bar segment per operation, laid inside `width` px. Segments keep their 60 px step
## while they fit (five operations or fewer) and tighten beyond that: the fixed 60 px step
## pushed operations 7-10 past the right edge of the 1280 px canvas.
static func campaign_segments(count: int, width: float = 300.0) -> Array[Rect2]:
    var rects: Array[Rect2] = []
    var step := minf(60.0, (width + 6.0) / maxf(1.0, float(count)))
    for i in range(count):
        rects.append(Rect2(i * step, 24.0, step - 6.0, 4.0))
    return rects

func _build_campaign_widget(cleared: Array) -> void:
    var box := Control.new()
    box.name = "CampaignProgress"
    box.position = Vector2(916, 44)
    box.size = Vector2(300, 70)
    box.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(box)
    var rows := MissionCatalog.rows()
    var done := 0
    for row: Dictionary in rows:
        if cleared.has(row.mission_id): done += 1
    var heading := MenuFx.label("CAMPAIGN  //  CHAPTER 01", 13, Color(MenuFx.MUTED, 0.9), 3)
    heading.position = Vector2(0, 0)
    box.add_child(heading)
    var count := MenuFx.label("%d / %d" % [done, rows.size()], 22, MenuFx.INK, 2)
    count.position = Vector2(236, -6)
    box.add_child(count)
    var layout := campaign_segments(rows.size(), box.size.x)
    for i in range(rows.size()):
        var segment := ColorRect.new()
        var is_done := cleared.has(rows[i].mission_id)
        var is_next := not is_done and MissionCatalog.available(str(rows[i].mission_id), cleared)
        segment.color = MenuFx.ACCENT if is_done else (Color(MenuFx.AMBER, 0.85) if is_next else Color(MenuFx.DIM, 0.45))
        segment.position = layout[i].position
        segment.size = layout[i].size
        box.add_child(segment)
        if is_next:
            var pulse := segment.create_tween().set_loops()
            pulse.tween_property(segment, "modulate:a", 0.35, 0.8).set_trans(Tween.TRANS_SINE)
            pulse.tween_property(segment, "modulate:a", 1.0, 0.8).set_trans(Tween.TRANS_SINE)
    var next_id := MissionCatalog.recommended(cleared)
    var note := MenuFx.label(("NEXT  ▸  %s  %s" % [next_id.right(2), str(MissionCatalog.get_mission(next_id).get("title", ""))]) if done < rows.size() else "CHAPTER COMPLETE  ▸  REPLAY ANY OPERATION", 13, Color(MenuFx.AMBER, 0.9) if done < rows.size() else MenuFx.ACCENT, 2)
    note.position = Vector2(0, 34)
    box.add_child(note)

func _build_training_panel() -> void:
    training_panel = PanelContainer.new()
    training_panel.name = "TrainingPanel"
    training_panel.add_theme_stylebox_override("panel", MenuFx.panel_style(MenuFx.AMBER, 0.9))
    training_panel.position = Vector2(522, 362)
    training_panel.custom_minimum_size = Vector2(318, 0)
    training_panel.visible = false
    add_child(training_panel)
    var stack := VBoxContainer.new()
    stack.add_theme_constant_override("separation", 6)
    training_panel.add_child(stack)
    stack.add_child(MenuFx.section_header("TRAINING SIMULATOR", MenuFx.AMBER))
    var note := MenuFx.label("Same squad, AI and damage. No rewards or saves.", 13, MenuFx.MUTED)
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    note.custom_minimum_size = Vector2(282, 0)
    stack.add_child(note)
    for i in range(TRAINING.size()):
        var button := CinematicMenuButton.new(str(TRAINING[i]), "", "%02d" % (i + 1))
        button.name = "Training%02d" % (i + 1)
        button.accent = MenuFx.AMBER
        button.title_size = 18
        button.custom_minimum_size = Vector2(282, 40)
        button.pressed.connect(func() -> void: battle_requested.emit(i + 1))
        stack.add_child(button)

func _toggle_training() -> void:
    var opening := not training_panel.visible
    training_panel.visible = true
    var tween := create_tween().set_parallel()
    if opening:
        training_panel.modulate.a = 0.0
        training_panel.position.x = 500
        tween.tween_property(training_panel, "modulate:a", 1.0, 0.22)
        tween.tween_property(training_panel, "position:x", 522.0, 0.26).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
        (training_panel.find_child("Training01", true, false) as Control).grab_focus()
    else:
        tween.tween_property(training_panel, "modulate:a", 0.0, 0.15)
        tween.chain().tween_callback(func() -> void: training_panel.visible = false)
        (_menu.find_child("TrainingSimulator", false, false) as Control).grab_focus()

func _build_utility_row() -> void:
    var row := HBoxContainer.new()
    row.name = "UtilityRow"
    row.position = Vector2(64, 650)
    row.add_theme_constant_override("separation", 6)
    add_child(row)
    var credits := AcceptDialog.new()
    credits.title = "SABLE CIRCUIT / ASSET CREDITS"
    credits.dialog_text = preload("res://assets/audio/combat_r04/bank.gd").CREDITS + "\n\nENVIRONMENT MODELS\n자료: kArchive\n출처: 쓰레드 dogfooter\nhttps://karchive.vibeline.co.kr/models\nUsed and modified under the bundled commercial-project license. No AI training."
    add_child(credits)
    var manual := AcceptDialog.new()
    manual.title = "FIELD MANUAL / KEYBOARD + TOUCH"
    manual.dialog_text = preload("res://scripts/ui/demo_controls.gd").HELP
    add_child(manual)
    _utility_button(row, "HowToPlay", "HOW TO PLAY", func() -> void: manual.popup_centered(Vector2i(880, 360)))
    _utility_button(row, "WatchIntro", "WATCH INTRO", func() -> void: intro_requested.emit(false))
    _utility_button(row, "AssetCredits", "CREDITS", func() -> void: credits.popup_centered())
    var music_button := _utility_button(row, "MusicToggle", "MUSIC ON / M", func() -> void: pass)
    var refresh_music := func() -> void:
        var manager := get_tree().get_first_node_in_group("sable_music")
        music_button.text = "MUSIC OFF / M" if manager != null and manager.muted else "MUSIC ON / M"
    music_button.pressed.connect(func() -> void:
        var manager := get_tree().get_first_node_in_group("sable_music")
        if manager != null: manager.toggle_mute()
        refresh_music.call())
    refresh_music.call()
    var music_manager := get_tree().get_first_node_in_group("sable_music")
    if music_manager != null: music_manager.mute_changed.connect(refresh_music)
    var footer := MenuFx.label("DEMO BUILD  ·  PROGRESS SAVES ON THIS DEVICE", 12, Color(MenuFx.DIM, 0.9), 3)
    footer.position = Vector2(76, 690)
    add_child(footer)

func _utility_button(row: HBoxContainer, node_name: String, label_text: String, action: Callable) -> Button:
    var button := Button.new()
    button.name = node_name
    button.text = label_text
    button.flat = true
    button.theme_type_variation = &"UtilityButton"
    button.custom_minimum_size = Vector2(0, 32)
    button.pressed.connect(action)
    row.add_child(button)
    return button

func _play_entrance() -> void:
    var curtain := ColorRect.new()
    curtain.name = "Curtain"
    curtain.color = Color.BLACK
    curtain.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    curtain.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(curtain)
    var fade := create_tween()
    fade.tween_property(curtain, "modulate:a", 0.0, 1.1).set_trans(Tween.TRANS_SINE)
    fade.tween_callback(curtain.queue_free)
    _title_block.modulate.a = 0.0
    _title_block.position.x = 46
    var title_in := create_tween().set_parallel()
    title_in.tween_property(_title_block, "modulate:a", 1.0, 1.0).set_delay(0.35)
    title_in.tween_property(_title_block, "position:x", 70.0, 1.2).set_delay(0.35).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
    for i in range(_menu.get_child_count()):
        var button := _menu.get_child(i) as CinematicMenuButton
        button.modulate.a = 0.0
        create_tween().tween_property(button, "modulate:a", 1.0, 0.45).set_delay(0.8 + 0.09 * i)
    var blink := _status_dot.create_tween().set_loops()
    blink.tween_property(_status_dot, "modulate:a", 0.2, 0.6)
    blink.tween_property(_status_dot, "modulate:a", 1.0, 0.6)

func _process(delta: float) -> void:
    if backdrop and lineup:
        lineup.parallax = backdrop.mouse_offset() * 22.0
    _glitch_timer -= delta
    if _glitch_timer <= 0.0:
        _glitch_timer = randf_range(6.0, 10.0)
        _glitch_left = 0.14
    if _glitch_left > 0.0:
        _glitch_left -= delta
        var jitter := randf_range(2.0, 5.0)
        _glitch[0].visible = _glitch_left > 0.0
        _glitch[1].visible = _glitch_left > 0.0
        _glitch[0].position = Vector2(-4 - jitter, 160)
        _glitch[1].position = Vector2(-4 + jitter, 160)

func _unhandled_key_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE and training_panel.visible:
        get_viewport().set_input_as_handled()
        _toggle_training()

func debug_start() -> void:
    start_requested.emit()
