extends Node2D
## Interactive shell around the actual game actor and FastCharacterRuntime.
## No JavaScript movement, independent gait clock or alternative muzzle code.
const ACTOR_SCENE = preload("res://scenes/actors/player/OperatorActor.tscn")
var actor: OperatorActor
var status_label: Label
var rounds_label: Label
var shot_count := 0
var elapsed := 0.0
var pad_direction := Vector2.ZERO
var pad_run := false
var pad_fire := false
var pad_buttons: Array[Button] = []
var walls := [Rect2(480,400,220,60),Rect2(1160,660,260,60)]

func _ready() -> void:
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime",true)
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview",false)
    var descriptor_path := str(ProjectSettings.get_setting("sable_web/descriptor", ""))
    if descriptor_path.is_empty():
        push_error("An exact candidate descriptor is required")
        return
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime_descriptor_override",descriptor_path)
    actor=ACTOR_SCENE.instantiate() as OperatorActor
    # The authored runtime is the only character renderer in this review shell.
    # Unrelated legacy presentation nodes need their own retired asset packs.
    for child in actor.get_children():
        if child.name not in ["CollisionShape2D","VisualRoot","FastCharacterRuntime"]:
            child.free()
    actor.configure("CHR_PROTO_03","MICA",Color("61e5d8"))
    actor.position=Vector2(960,580)
    actor.set_movement_bounds(Rect2(100,230,1720,750))
    add_child(actor)
    actor.set_controlled(true)
    actor.projectile_spawned.connect(_on_projectile)
    for rect in walls:
        var wall=StaticBody2D.new()
        var shape=CollisionShape2D.new()
        var box=RectangleShape2D.new()
        box.size=rect.size;shape.shape=box;wall.position=rect.get_center()
        wall.add_child(shape);add_child(wall)
    var hud=CanvasLayer.new();add_child(hud)
    _label(hud,Vector2(72,45),"SABLE CIRCUIT  /  FIELD TEST",22,Color("62c7bb"))
    _label(hud,Vector2(70,78),"MICA",64,Color("edf5f3"))
    var scope := str(ProjectSettings.get_setting("sable_web/asset_scope","UNREVIEWED CANDIDATE"))
    _label(hud,Vector2(72,160),scope,20,Color("efbd72"))
    _label(hud,Vector2(72,1015),"W A S D   MOVE     |     SHIFT   RUN     |     MOUSE   AIM     |     LEFT CLICK   FIRE     |     R   RELOAD",20,Color("a9bbb9"))
    status_label=_label(hud,Vector2(1170,70),"",22,Color("d1e4e0"))
    rounds_label=_label(hud,Vector2(1510,117),"",24,Color("61e5d8"))
    var reset=Button.new();reset.text="RESET POSITION";reset.position=Vector2(1655,65);reset.size=Vector2(190,48)
    reset.pressed.connect(func():actor.position=Vector2(960,580));hud.add_child(reset)
    _make_input_pad(hud)
    get_viewport().gui_disable_input=false
    queue_redraw()

func _make_input_pad(hud:CanvasLayer)->void:
    _label(hud,Vector2(90,764),"CLICK TO MOVE  /  CLICK STOP TO RELEASE",15,Color("a9bbb9"))
    var labels=["NW","N","NE","W","STOP","E","SW","S","SE"]
    var vectors=[Vector2(-1,-1),Vector2(0,-1),Vector2(1,-1),Vector2(-1,0),Vector2.ZERO,Vector2(1,0),Vector2(-1,1),Vector2(0,1),Vector2(1,1)]
    for i in range(9):
        var button=Button.new();button.text=labels[i]
        button.position=Vector2(90+(i%3)*70,794+(i/3)*52);button.size=Vector2(64,46)
        button.pressed.connect(_set_pad_direction.bind(vectors[i]))
        hud.add_child(button)
    for i in range(2):
        var button=Button.new();button.text=["RUN","AUTO FIRE"][i]
        button.toggle_mode=true;button.position=Vector2(316,794+i*52);button.size=Vector2(144,46)
        button.toggled.connect(_set_pad_toggle.bind(i));pad_buttons.append(button);hud.add_child(button)
    var reload_button=Button.new();reload_button.text="RELOAD"
    reload_button.position=Vector2(316,898);reload_button.size=Vector2(144,46)
    reload_button.pressed.connect(_pad_reload);hud.add_child(reload_button)

func _key_event(code:Key,pressed:bool)->void:
    var event=InputEventKey.new();event.keycode=code;event.physical_keycode=code;event.pressed=pressed
    Input.parse_input_event(event)

func _set_pad_direction(direction:Vector2)->void:
    pad_direction=direction
    _key_event(KEY_W,direction.y<0);_key_event(KEY_S,direction.y>0)
    _key_event(KEY_A,direction.x<0);_key_event(KEY_D,direction.x>0)

func _set_pad_toggle(enabled:bool,which:int)->void:
    if which==0:
        pad_run=enabled;_key_event(KEY_SHIFT,enabled)
    else:
        pad_fire=enabled
        var event=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_LEFT;event.pressed=enabled
        event.position=get_viewport().get_mouse_position();Input.parse_input_event(event)

func _pad_reload()->void:
    _key_event(KEY_R,true)
    await get_tree().physics_frame
    await get_tree().physics_frame
    _key_event(KEY_R,false)

func _notification(what:int)->void:
    if what==NOTIFICATION_APPLICATION_FOCUS_OUT:
        _set_pad_direction(Vector2.ZERO)
        for button in pad_buttons:button.set_pressed(false)

func _physics_process(_delta:float)->void:
    # A real click on the canvas releases the mouse button. Reassert the
    # explicitly selected accessibility toggle through the public input API.
    if pad_fire and not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
        _set_pad_toggle(true,1)

func _label(parent:Node,pos:Vector2,text:String,size:int,color:Color)->Label:
    var label=Label.new();label.position=pos;label.text=text
    label.add_theme_font_size_override("font_size",size);label.add_theme_color_override("font_color",color)
    label.mouse_filter=Control.MOUSE_FILTER_IGNORE;parent.add_child(label);return label

func _on_projectile(_projectile:Node2D)->void:
    shot_count+=1

func _process(delta:float)->void:
    elapsed+=delta
    if actor==null:return
    var runtime=actor.get_node("FastCharacterRuntime")
    var state:Dictionary=runtime.call("debug_contract")
    var directions=["E","SE","S","SW","W","NW","N","NE"]
    status_label.text="MOVE  %s     AIM  %s\n%s    /    FRAME %02d" % [directions[int(state.get("movement_sector",0))],directions[actor.facing_sector],str(state.get("active_state","idle")).to_upper(),int(state.get("active_frame",0))]
    rounds_label.text=("RELOADING" if actor.is_reloading() else "%02d / %02d" % [actor.ammo,actor.magazine_size])+"   |   SHOTS %d" % shot_count
    if OS.has_feature("web"):
        var telemetry={"position":[actor.position.x,actor.position.y],"shots":shot_count,"ammo":actor.ammo,"runtime":state,"elapsed":elapsed}
        JavaScriptBridge.eval("window.sableTelemetry="+JSON.stringify(telemetry),true)
    queue_redraw()

func _draw()->void:
    draw_rect(Rect2(0,0,1920,1080),Color("0b1219"))
    draw_rect(Rect2(48,206,1824,784),Color("101d26"))
    for x in range(48,1873,64):draw_line(Vector2(x,206),Vector2(x,990),Color("1a2b35"))
    for y in range(206,991,64):draw_line(Vector2(48,y),Vector2(1872,y),Color("1a2b35"))
    draw_rect(Rect2(100,230,1720,750),Color("35545b"),false,2)
    for rect in walls:
        draw_rect(rect,Color("20323f"));draw_rect(rect,Color("53757c"),false,2)
        draw_line(rect.position+Vector2(8,6),rect.position+Vector2(rect.size.x-8,6),Color("62c7bb"),3)
    if actor!=null:
        var mouse=get_global_mouse_position()
        draw_arc(mouse,12,0,TAU,32,Color("9ce7dc"),1.5)
        draw_line(mouse-Vector2(18,0),mouse-Vector2(7,0),Color("9ce7dc"))
        draw_line(mouse+Vector2(7,0),mouse+Vector2(18,0),Color("9ce7dc"))
        draw_line(mouse-Vector2(0,18),mouse-Vector2(0,7),Color("9ce7dc"))
        draw_line(mouse+Vector2(0,7),mouse+Vector2(0,18),Color("9ce7dc"))
