extends SceneTree
const Flow := preload("res://scenes/bootstrap/GameFlow.tscn")
const Output := preload("res://tests/support/test_output.gd")
var checks := 0
var failures: Array[String] = []
var captures := []
var out := Output.path("res://.cache/tests/run_contract/ui")
var native := false
func _init() -> void: call_deferred("run")
func run() -> void:
    root.size = Vector2i(1920,1080)
    root.content_scale_size = Vector2i(1280,720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    native = DisplayServer.get_name() != "headless"
    if native: DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var flow := Flow.instantiate() as GameFlow
    flow.persist_campaign = false
    root.add_child(flow)
    await frames(3)
    flow.open_mission_briefing("MIS_CH01_01")
    await frames(3)
    var screen := flow.current_view as BriefingScreen
    check(not screen._deploy_button.visible and screen._contracts.size() == 3, "before dialogue: three choices, no deploy")
    check(screen.selected_contract() == RunContract.build(flow.campaign.next_run_id()), "preselected default uses next deploy run ID without consuming it")
    var open := screen.find_child("ChooseContract",true,false) as Button
    await click(open)
    check(screen._contract_panel.visible and not screen._comms_panel.visible, "contracts reachable before completing dialogue")
    await click(open)
    check(screen._comms_panel.visible and not screen._deploy_button.visible, "contract panel cannot skip dialogue")
    await finish_dialogue(screen)
    check(screen._contract_panel.visible and screen._deploy_button.visible, "contracts visible before deploy after real dialogue completion")
    check(screen.selected_contract_index() == 0, "no choice input leaves default selected")
    geometry(screen)
    await shot("briefing_default", screen)
    await click(screen._deploy_button)
    check(flow.current_view is StoryStage01, "real deploy button reaches stage")
    if flow.current_view is StoryStage01:
        var stage := flow.current_view as StoryStage01
        var expected_default := RunContract.build(stage._run_id)
        expected_default["mission_id"] = "MIS_CH01_01"
        check(stage.debug_run_contract() == expected_default, "untouched/default briefing deploy exactly equals HEAD contract plus mission_id (no other added keys)")
    flow.enter_base(); await frames(3)
    flow.open_mission_briefing("MIS_CH01_01"); await frames(3)
    screen = flow.current_view as BriefingScreen
    await finish_dialogue(screen)
    screen._contract_choices[1].grab_focus()
    await accept_key()
    check(screen.selected_contract_index() == 1, "keyboard selects alternative radio button")
    await click(screen._contract_choices[2])
    check(screen.selected_contract_index() == 2, "mouse selects alternative")
    var chosen := screen.selected_contract()
    chosen["mission_id"] = "MIS_CH01_01"
    await click(screen._deploy_button)
    check((flow.current_view as StoryStage01).debug_run_contract() == chosen, "alternative survives actual GameFlow deploy")
    flow.enter_base(); await frames(3)
    flow.campaign.commit_mission({"transaction_id":"UI-FIRST-CLEAR", "mission_id":"MIS_CH01_01", "outcome":"EXTRACTED", "full_route_cleared":true})
    flow.open_mission_briefing("MIS_CH01_01"); await frames(3)
    screen = flow.current_view as BriefingScreen
    check(screen._contracts.size() == 4, "cleared operation displays REDLINE fourth choice")
    await finish_dialogue(screen)
    screen._contract_choices[3].grab_focus()
    await accept_key()
    check(screen.selected_contract_index() == 3, "keyboard selects REDLINE")
    geometry(screen)
    await shot("briefing_redline",screen)
    chosen = screen.selected_contract()
    chosen["mission_id"] = "MIS_CH01_01"
    await click(screen._deploy_button)
    var stage := flow.current_view as StoryStage01
    check(stage.debug_run_contract() == chosen and RunContract.is_redline(chosen), "REDLINE flows to actual stage")
    stage.debug_seed_cargo(100,40,10,10,true,6)
    var summary := stage.debug_extraction_summary("R06_EXTRACT")
    flow.show_results(summary); await frames(4)
    var results := flow.current_view as MissionResults
    print("CONTRACT_RESULT_LAYOUT: body=", results._body.get_rect(), " minimum=",results._body.get_minimum_size(), " contract=",results._contract_line.get_rect(), " minimum=",results._contract_line.get_minimum_size())
    check(results._contract_line.text.contains(str(chosen.hazard_title)) and results._contract_line.text.contains(str(chosen.opportunity_title)) and results._contract_line.text.contains("2.40"), "results show issued contract and actual reward factors")
    check(results._contract_line.get_rect().end.y <= results._campaign_line.position.y, "result contract occupies its own rectangle")
    check(results._body.get_rect().end.y <= results._contract_line.position.y, "result contract does not overlap field report")
    fit(results._contract_line)
    fit(results._body)
    check(results._body.get_minimum_size().x <= 540 and results._body.get_minimum_size().y <= 184, "field report fits fixed allocation")
    check(results._contract_line.get_minimum_size().x <= 540 and results._contract_line.get_minimum_size().y <= 40, "contract text fits fixed allocation")
    await shot("results_redline", results)
    flow.enter_base(); await frames(4)
    var lobby := flow.current_view as BaseLobby
    lobby.selected_mission_id = "MIS_CH01_01"
    lobby._refresh_missions()
    check(lobby._mission_status.text.contains("REDLINE CLEARED"), "lobby status shows REDLINE clear")
    check(lobby._mission_selector.get_item_text(0).contains("REDLINE CLEARED"), "operation selector displays REDLINE record")
    await shot("lobby_redline_cleared", lobby)
    # New campaign rows may have long titles; all ten use the same choice bounds.
    for n in range(1,11):
        var view := BriefingScreen.new()
        view.mission_id = "MIS_CH01_%02d" % n
        view.allow_redline = true
        root.add_child(view)
        await frames(2)
        view._show_contracts(true)
        geometry(view)
        view.free()
    flow.queue_free(); await frames(3)
    var f := FileAccess.open(out.path_join("ui_report.json"),FileAccess.WRITE)
    f.store_string(JSON.stringify({"checks":checks,"failures":failures,"native_capture":native,"captures":captures,"human_play":false,"visual_approval":false,"balance_approval":false},"  ")); f.close()
    print("RUN_CONTRACT_UI_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)
func geometry(screen: BriefingScreen) -> void:
    for button in screen._contract_choices:
        fit(button)
        check(button.get_minimum_size().x <= 714 and button.get_minimum_size().y <= 72, "choice text fits its fixed 714×72 slot")
        check(Rect2(Vector2.ZERO,screen._contract_panel.size).encloses(button.get_rect()), "choice within panel")
    check(not screen._comms_panel.visible, "choice panel replaces comms; both never visible together")
    var controls: Array[Control] = [screen._contract_panel,screen.get_node("RoutePanel"),screen._contract_button,screen.get_node("BackToBase")]
    if screen._deploy_button.visible: controls.append(screen._deploy_button)
    for a in controls:
        check(Rect2(0,0,1280,720).encloses(a.get_rect()), a.name + " inside 1280×720")
        if a is Button: fit(a)
        for b in controls:
            if a != b: check(not a.get_rect().intersects(b.get_rect()), a.name + " does not overlap " + b.name)
    for i in range(screen._contract_choices.size()):
        for j in range(i+1,screen._contract_choices.size()): check(not screen._contract_choices[i].get_rect().intersects(screen._contract_choices[j].get_rect()), "radio button rectangles separated")
func fit(control: Control) -> void:
    var minimum := control.get_minimum_size()
    check(control.size.x >= minimum.x and control.size.y >= minimum.y, control.name + " text minimum fits allocated rectangle")
func finish_dialogue(screen: BriefingScreen) -> void:
    # No debug_complete_briefing shortcut: the same button finishes typing and
    # advances every authored transmission, including the final one.
    for _i in range(screen._briefing.size()*2+2):
        if screen._deploy_button.visible: break
        screen._next_button.pressed.emit()
        await process_frame
    check(screen._deploy_button.visible, "all authored dialogue lines completed")
func click(button: Button) -> void:
    var event := InputEventMouseButton.new()
    event.button_index = MOUSE_BUTTON_LEFT
    event.position = button.get_global_rect().get_center()
    event.pressed = true
    root.push_input(event, true)
    await process_frame
    event = event.duplicate()
    event.pressed = false
    root.push_input(event, true)
    await frames(2)
func accept_key() -> void:
    var event := InputEventKey.new()
    event.keycode = KEY_ENTER
    event.pressed = true
    root.push_input(event, true)
    await process_frame
    event = event.duplicate(); event.pressed = false
    root.push_input(event, true)
    await frames(2)
func shot(label: String, view: Control) -> void:
    if not native: return
    await create_timer(1.7).timeout
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    var path := out.path_join(label+".png")
    check(image.get_size() == Vector2i(1920,1080), label + " native viewport 1080p")
    check(image.save_png(ProjectSettings.globalize_path(path)) == OK, label + " native capture saved")
    captures.append({"capture":path,"sha256":FileAccess.get_sha256(path),"size":[1920,1080],"runtime_view":view.get_class()})
func frames(n: int) -> void:
    for _i in range(n): await process_frame
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
