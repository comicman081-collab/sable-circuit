extends CanvasLayer
const State := preload("res://scripts/ui/demo_input.gd")
const HELP := "MOVE   WASD / ARROWS     •     RUN   SHIFT     •     AIM   MOUSE     •     FIRE   LEFT CLICK\nRELOAD   R     •     EVADE   SPACE     •     SKILLS   Q / E / X     •     SWITCH   1 / 2 / 3\nINTERACT / REVIVE / EXTRACT   HOLD F     •     CONTINUE ROUTE   C\nTOUCH: LEFT PAD MOVE • RIGHT PAD AIM + FIRE • RUN / EVADE + ACTION BUTTONS\nClear rooms → collect research / salvage / intel → extract → upgrade in OPERATIONS.\nTraining does not award resources. Cover blocks bullets, not blast zones."
var canvas: Control
var tip: Label
var help_panel: PanelContainer
var touch_button: Button
var shake_button: Button
var resume_button: Button
var abort_button: Button
var abort_armed := false
var fingers: Dictionary = {}
var zones: Dictionary = {}
var move_center := Vector2(126,451)
var aim_center := Vector2(1154,451)
var _prior_touch_emulation := true

func _ready() -> void:
    layer = 40
    process_mode = Node.PROCESS_MODE_ALWAYS
    State.reset()
    _prior_touch_emulation = Input.emulate_mouse_from_touch
    Input.emulate_mouse_from_touch = false
    canvas = Control.new()
    canvas.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
    canvas.theme = preload("res://scripts/ui/demo_theme.gd").build()
    add_child(canvas)
    canvas.draw.connect(_draw_controls)
    # Persistent but quiet keyboard guide; the field HUD owns the screen edges.
    tip = Label.new()
    tip.text = "WASD MOVE   •   SHIFT RUN   •   MOUSE AIM / FIRE   •   R RELOAD   •   SPACE EVADE   •   TAB MANUAL"
    tip.position = Vector2(290,16)
    tip.size = Vector2(560,18)
    tip.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    tip.add_theme_font_size_override("font_size",12)
    tip.add_theme_color_override("font_color",Color(0.82,0.88,0.9,0.62))
    canvas.add_child(tip)
    touch_button = _button("TOUCH OFF",Vector2(575,36),_toggle_touch)
    _button("MANUAL / H",Vector2(488,36),_toggle_help)
    help_panel = PanelContainer.new()
    help_panel.position = Vector2(300,178)
    help_panel.size = Vector2(680,330)
    help_panel.visible = false
    var stack := VBoxContainer.new()
    var margin := MarginContainer.new()
    for edge in ["left","right","top","bottom"]: margin.add_theme_constant_override("margin_"+edge,20)
    help_panel.add_child(margin); margin.add_child(stack)
    var title := Label.new(); title.text = "FIELD MANUAL  /  PAUSED"; title.add_theme_font_size_override("font_size",28); stack.add_child(title)
    var body := Label.new(); body.text = HELP; body.add_theme_font_size_override("font_size",17); stack.add_child(body)
    shake_button = Button.new(); shake_button.custom_minimum_size.y=40; shake_button.focus_mode = Control.FOCUS_NONE; shake_button.pressed.connect(_toggle_shake); stack.add_child(shake_button)
    resume_button = Button.new(); resume_button.text = "RESUME"; resume_button.custom_minimum_size.y=48; resume_button.pressed.connect(_toggle_help); stack.add_child(resume_button)
    abort_button = Button.new(); abort_button.text = "LEAVE RUN / FORFEIT UNSECURED CARGO"; abort_button.custom_minimum_size.y=48; abort_button.pressed.connect(_abort); stack.add_child(abort_button)
    canvas.add_child(help_panel)
    var keys := [KEY_1,KEY_2,KEY_3,KEY_Q,KEY_E,KEY_X,KEY_R,KEY_SPACE,KEY_SHIFT,KEY_F,KEY_C]
    var labels := ["1","2","3","Q","E","X","R","EVADE","RUN","F / USE","C / GO"]
    for i in range(keys.size()): zones[keys[i]] = {"rect":Rect2(337+(i%6)*101,582+(i/6)*59,96,54),"label":labels[i]}
    if DisplayServer.is_touchscreen_available(): State.touch_mode = true
    _refresh()

func _button(text: String, pos: Vector2, callback: Callable) -> Button:
    var button := Button.new(); button.text=text; button.position=pos; button.size=Vector2(82,22)
    button.add_theme_font_size_override("font_size",11)
    button.modulate = Color(1,1,1,0.72)
    button.focus_mode = Control.FOCUS_NONE
    button.pressed.connect(callback); canvas.add_child(button); return button

func _toggle_touch() -> void:
    State.reset(); fingers.clear(); State.touch_mode = not State.touch_mode; _refresh()

func _toggle_shake() -> void:
    GameSettings.set_screen_shake(not GameSettings.screen_shake); _refresh()

func _refresh() -> void:
    touch_button.text = "TOUCH ON" if State.touch_mode else "TOUCH OFF"
    GameSettings.load_once()
    shake_button.text = "SCREEN SHAKE: ON" if GameSettings.screen_shake else "SCREEN SHAKE: OFF"
    var hud := get_parent().get_node_or_null("StoryStageHUD")
    if hud: hud.set_touch_layout(State.touch_mode)
    canvas.queue_redraw()

func _toggle_help() -> void:
    State.reset(); fingers.clear()
    abort_armed = false
    abort_button.text = "LEAVE TRAINING" if get_parent().battle_preview else "LEAVE RUN / FORFEIT UNSECURED CARGO"
    help_panel.visible = not help_panel.visible
    get_tree().paused = help_panel.visible

func _abort() -> void:
    if not get_parent().battle_preview and not abort_armed:
        abort_armed = true
        abort_button.text = "CONFIRM ABORT / COUNTS AS A WIPE"
        return
    get_tree().paused = false
    State.reset(); fingers.clear()
    if get_parent().battle_preview: get_parent().return_requested.emit()
    else: get_parent()._finish_mission("WIPED")

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo and not help_panel.visible:
        State.remember_press(event.physical_keycode if event.physical_keycode != 0 else event.keycode)
    var hud := get_parent().get_node_or_null("StoryStageHUD")
    if not help_panel.visible and ((event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT) or (event is InputEventScreenTouch and event.pressed)):
        if hud != null and hud.activate_field_control_at(event.position):
            State.mouse_blocked = true
            get_viewport().set_input_as_handled()
            return
    if event is InputEventKey and event.pressed and not event.echo and event.keycode in [KEY_H,KEY_ESCAPE,KEY_TAB]:
        _toggle_help(); get_viewport().set_input_as_handled(); return
    if event is InputEventScreenTouch:
        # Screen touches also operate these controls without mouse emulation.
        if event.pressed and Rect2(488,36,82,22).grow(6).has_point(event.position): _toggle_help(); return
        if event.pressed and Rect2(575,36,82,22).grow(6).has_point(event.position): _toggle_touch(); return
        if help_panel.visible:
            if event.pressed and resume_button.get_global_rect().has_point(event.position): _toggle_help()
            elif event.pressed and abort_button.get_global_rect().has_point(event.position): _abort()
            return
        if event.pressed:
            if not State.touch_mode: State.touch_mode=true; _refresh()
            if event.position.distance_to(move_center)<82 and not fingers.values().has("move"): fingers[event.index]="move"
            elif event.position.distance_to(aim_center)<82 and not fingers.values().has("aim"): fingers[event.index]="aim"
            else:
                for key in zones:
                    if zones[key].rect.has_point(event.position): fingers[event.index]=key; break
            _finger_move(event.index,event.position)
        else:
            fingers.erase(event.index); _recompute_buttons()
            if not fingers.values().has("move"): State.movement=Vector2.ZERO
            if not fingers.values().has("aim"): State.firing=false
        get_viewport().set_input_as_handled()
    elif event is InputEventScreenDrag:
        _finger_move(event.index,event.position)
        if fingers.has(event.index): get_viewport().set_input_as_handled()

func _finger_move(index: int, point: Vector2) -> void:
    var role: Variant = fingers.get(index, "")
    if role is String:
        if role == "move": State.movement = ((point-move_center)/62.0).limit_length(1.0)
        elif role == "aim":
            var offset := point-aim_center
            State.firing=offset.length()>12
            if State.firing: State.aim=offset.normalized()
    _recompute_buttons()

func _recompute_buttons() -> void:
    State.held.clear()
    for role in fingers.values():
        if role is int: State.held[role]=true

func _process(_delta: float) -> void:
    State.mouse_blocked = get_viewport().gui_get_hovered_control() is BaseButton or help_panel.visible
    var hud := get_parent().get_node_or_null("StoryStageHUD")
    if hud != null and hud.blocks_pointer_at(canvas.get_global_mouse_position()): State.mouse_blocked = true
    canvas.queue_redraw()

func _draw_controls() -> void:
    if not State.touch_mode or help_panel.visible: return
    var font := ThemeDB.fallback_font
    for center in [move_center,aim_center]:
        canvas.draw_circle(center,72,Color(0.025,0.07,0.09,0.7))
        canvas.draw_arc(center,72,0,TAU,64,Color("70b7b3"),2,true)
    canvas.draw_circle(move_center+State.movement*42,23,Color("81c4bd"))
    canvas.draw_circle(aim_center+(State.aim*42 if State.firing else Vector2.ZERO),23,Color("ddb976"))
    canvas.draw_string(font,move_center+Vector2(-25,100),"MOVE",HORIZONTAL_ALIGNMENT_LEFT,-1,16)
    canvas.draw_string(font,aim_center+Vector2(-45,100),"AIM / FIRE",HORIZONTAL_ALIGNMENT_LEFT,-1,16)
    for key in zones:
        var rect: Rect2=zones[key].rect
        canvas.draw_rect(rect,Color("355b60") if State.held.has(key) else Color(0.025,0.07,0.09,0.9))
        canvas.draw_rect(rect,Color("638781"),false,1)
        canvas.draw_string(font,rect.position+Vector2(4,33),zones[key].label,HORIZONTAL_ALIGNMENT_CENTER,88,16)

func _notification(what: int) -> void:
    if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
        State.reset(); fingers.clear()

func _exit_tree() -> void:
    State.reset()
    Input.emulate_mouse_from_touch = _prior_touch_emulation
    get_tree().paused = false
