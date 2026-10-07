extends SceneTree

var failed := false

func _init() -> void:
    call_deferred("run")

func check(value: bool, message: String) -> void:
    if not value:
        failed = true
        push_error(message)

func settle() -> void:
    for i in range(6):
        await process_frame

func run() -> void:
    var flow := GameFlow.new()
    root.add_child(flow)
    await settle()
    check(flow.current_view is TitleScreen, "Title screen did not load")
    var before := JSON.stringify(flow.campaign.snapshot())
    for number in range(1,4):
        (flow.current_view as TitleScreen).battle_requested.emit(number)
        await settle()
        check(flow.current_state == "BATTLE_PREVIEW", "Stage button not connected")
        var stage := flow.current_view as StoryStage01
        check(stage.mission_id == "MIS_CH01_%02d" % number, "Wrong mission selected")
        # Preview opens each room's authored first wave (reinforcements are
        # campaign-only), so expected sizes come from the mission data.
        var first_wave := (stage.main_route[1].get("encounter", []) as Array).size()
        var boss_wave := (stage.main_route[4].get("encounter", []) as Array).size()
        check(first_wave >= 4 and boss_wave >= 3, "Dense authored first waves")
        check(stage.current_step == 1 and stage.enemies_alive == first_wave, "Direct combat not playable")
        stage.squad.operators[0].ammo = 0
        var event := InputEventKey.new()
        event.pressed = true
        event.keycode = KEY_F6
        stage._unhandled_key_input(event)
        check(stage.squad.operators[0].ammo == stage.squad.operators[0].magazine_size, "F6 did not reset ammunition")
        event.keycode = KEY_F7
        stage._unhandled_key_input(event)
        await settle()
        check(stage.current_step == 3 and stage.enemies_alive > 0, "F7 did not open elite encounter")
        stage._unhandled_key_input(event)
        await settle()
        check(stage.current_step == 4 and stage.enemies_alive == boss_wave, "F7 did not open boss encounter")
        stage._unhandled_key_input(event)
        await settle()
        check(stage.current_step == 1 and stage.enemies_alive == first_wave, "F7 encounter loop failed")
        event.keycode = KEY_ESCAPE
        stage._unhandled_key_input(event)
        await settle()
        check(flow.current_view is TitleScreen, "Escape did not return to title")
        check(JSON.stringify(flow.campaign.snapshot()) == before, "Preview modified persistent rewards")
    flow.queue_free()
    await settle()
    print("SITE7_BATTLE_FLOW: " + ("FAIL" if failed else "PASS"))
    quit(1 if failed else 0)
