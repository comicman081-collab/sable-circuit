extends SceneTree
const FLOW := preload("res://scenes/bootstrap/GameFlow.tscn")
const State := preload("res://scripts/ui/demo_input.gd")
var failures: Array[String] = []
var checks := 0
var capture := false
var out := "res://qa/demo_20260920"

func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks+=1
    if not ok: failures.append(label); push_error(label)
# Actors read input in _physics_process; on a fast display two rendered frames can pass
# before the next 60 Hz physics tick, so each step waits for both.
func frames(n: int) -> void:
    for i in range(n):
        await physics_frame
        await process_frame
func shot(name: String) -> void:
    if not capture: return
    await RenderingServer.frame_post_draw
    var img := root.get_texture().get_image()
    check(img.get_size()==Vector2i(1920,1080),"Native capture size")
    img.save_png(out+"/"+name+".png")
func touch(index: int, pos: Vector2, pressed: bool) -> void:
    var ev := InputEventScreenTouch.new(); ev.index=index; ev.position=pos; ev.pressed=pressed
    root.push_input(ev,true)
func run() -> void:
    capture = DisplayServer.get_name() != "headless"
    root.size = Vector2i(1920,1080)
    root.content_scale_size = Vector2i(1280,720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var flow := FLOW.instantiate() as GameFlow
    flow.persist_campaign=false
    root.add_child(flow)
    await frames(5)
    check(flow.current_state=="TITLE","Boot title")
    check(flow.current_view.find_child("StartDemo",true,false)!=null,"Visible demo start")
    await shot("title")
    flow.show_intro(true)
    await frames(70)
    var intro: Control=flow.current_view
    check(flow.current_state=="INTRO","Intro route")
    check(intro.player.stream is VideoStreamTheora,"Theora runtime video connected")
    check(intro.player.is_playing(),"Intro playback active")
    if capture: check(intro.player.stream_position>0.1,"Intro frames advance")
    await shot("intro")
    intro.finish()
    await frames(5)
    check(flow.current_state=="BASE","Intro skip to base")
    await shot("operations")
    flow.campaign.research_value=1000; flow.campaign.salvage=10; flow.campaign.signal_fragments=10
    check(bool(flow.debug_purchase("ARMORY_CALIBRATION").get("success",false)),"Actual growth transaction")
    check(flow.campaign.armory_level==1,"Upgrade retained in campaign")
    flow.open_battle_preview(4)
    await frames(8)
    var stage: StoryStage01=flow.current_view
    var controls: CanvasLayer=stage.get_node("DemoControls")
    check(controls.tip.visible,"Persistent keyboard guide")
    controls._toggle_touch()
    await frames(2)
    touch(0,Vector2(166,491),true)
    touch(1,Vector2(1210,450),true)
    await physics_frame
    check(State.movement.length()>0.5 and State.movement.length()<=1.001,"Diagonal stick normalized")
    check(State.firing and State.aim.x>0.9,"Independent aim/fire stick")
    var actor: OperatorActor=stage.squad.get_active_operator()
    var before := actor.global_position
    var ammo := actor.ammo
    await create_timer(0.6).timeout
    check(actor.global_position.distance_to(before)>5,"Touch drives real actor movement")
    check(actor.ammo<ammo,"Touch uses real firing cadence/ammo")
    await shot("touch_combat")
    touch(0,Vector2(166,491),false)
    await frames(2)
    check(State.movement==Vector2.ZERO and State.firing,"Release movement independently")
    touch(1,Vector2(1210,450),false)
    await frames(2)
    check(not State.firing,"Release stops fire")
    var reload_point: Vector2=controls.zones[KEY_R].rect.get_center()
    touch(7,reload_point,true); await frames(2)
    check(actor.is_reloading(),"Touch reload enters actual reload state")
    touch(7,reload_point,false)
    var switch_point: Vector2=controls.zones[KEY_2].rect.get_center()
    touch(2,switch_point,true)
    await frames(2)
    check(stage.squad.active_index==1,"Touch switches to ROOK")
    touch(2,switch_point,false)
    var skill_point: Vector2=controls.zones[KEY_E].rect.get_center()
    touch(8,skill_point,true); await frames(2)
    check(stage.squad.get_active_operator().get_node("SkillController").e_left>0,"Touch casts actual E skill")
    touch(8,skill_point,false)
    var run_point: Vector2=controls.zones[KEY_SHIFT].rect.get_center()
    touch(9,run_point,true); await frames(2)
    check(State.key(KEY_SHIFT),"Touch run held")
    touch(9,run_point,false)
    var continue_point: Vector2=controls.zones[KEY_C].rect.get_center()
    touch(3,continue_point,true)
    await frames(2)
    check(State.key(KEY_C),"Continue-route touch action")
    touch(3,continue_point,false)
    controls._toggle_help()
    await frames(2)
    check(paused and controls.help_panel.visible,"Help pauses gameplay")
    await shot("manual")
    controls._toggle_help()
    check(not paused,"Resume unpauses")
    for code in [KEY_W,KEY_D]:
        var ev := InputEventKey.new(); ev.keycode=code; ev.physical_keycode=code; ev.pressed=true; Input.parse_input_event(ev)
    await frames(2)
    check(State.move_vector().is_equal_approx(Vector2(1,-1).normalized()),"Physical diagonal keys combine without speed boost")
    for code in [KEY_W,KEY_D]:
        var ev := InputEventKey.new(); ev.keycode=code; ev.physical_keycode=code; ev.pressed=false; Input.parse_input_event(ev)
    touch(4,Vector2(168,451),true)
    controls._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
    check(State.movement==Vector2.ZERO and State.held.is_empty(),"Focus loss clears touch state")
    flow.show_title()
    await frames(3)
    check(not paused and State.held.is_empty(),"Scene transition releases input")
    check(flow.campaign.armory_level==1,"Training retains prior growth without replacing save")
    if "--intro-complete" in OS.get_cmdline_user_args():
        flow.show_intro(false)
        await create_timer(64.0).timeout
        check(flow.current_state=="TITLE","Full 60-second intro returns automatically")
    var report := {"checks":checks,"failures":failures,"native_capture":capture,"resolution":[1920,1080],"human_playtest":false}
    var file := FileAccess.open(out+"/integration_"+("native" if capture else "headless")+".json",FileAccess.WRITE)
    file.store_string(JSON.stringify(report,"  ")); file.close()
    flow.queue_free(); await frames(3)
    print("DEMO_INTEGRATION %s / %d checks" % ["PASS" if failures.is_empty() else "FAIL",checks])
    quit(0 if failures.is_empty() else 1)
