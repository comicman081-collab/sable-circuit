extends SceneTree
const Controls := preload("res://scripts/ui/demo_input.gd")
var checks := 0
var failed: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok:bool,label:String)->void:
    checks += 1
    if not ok: failed.append(label); push_error(label)
func tap(code:int)->void:
    var event := InputEventKey.new()
    event.keycode = code
    event.physical_keycode = code
    event.pressed = true
    root.push_input(event,true)
    event = event.duplicate()
    event.pressed = false
    root.push_input(event,true)
func settle()->void:
    for i in range(5): await physics_frame
func run()->void:
    var flow := preload("res://scripts/core/game_flow.gd").new()
    flow.persist_campaign = false
    root.add_child(flow)
    flow.deploy_mission("MIS_CH01_01")
    await settle()
    var stage: StoryStage01 = flow.current_view
    for actor in stage.squad.operators:
        check(not actor.equipped_weapon_id.is_empty(),actor.display_name+" equipped default")
        check(not actor.weapon_spec.is_empty(),actor.display_name+" valid weapon stats")
    for index in [1,2,0]:
        tap(KEY_1 + index)
        await settle()
        check(stage.squad.active_index == index,"Sub-frame key switches operator %d"%index)
        var actor: OperatorActor = stage.squad.get_active_operator()
        var initial: int = actor.ammo
        Controls.firing = true
        # A former follower may still be inside its real weapon cadence from
        # shots at the opening patrol; hold the trigger for one interval.
        for frame in range(int(ceil(actor.fire_interval * 60.0)) + 2):
            await physics_frame
            if actor.ammo < initial: break
        Controls.firing = false
        await physics_frame
        check(actor.ammo < initial,"Real controlled firing spends ammo %d"%index)
    var click := InputEventMouseButton.new()
    click.button_index = MOUSE_BUTTON_LEFT
    click.pressed = true
    click.position = Vector2(170,610)
    root.push_input(click,true)
    check(stage.squad.active_index == 1,"Portrait mouse selects ROOK")
    click = click.duplicate(); click.pressed = false; root.push_input(click,true)
    var touch := InputEventScreenTouch.new()
    touch.pressed = true; touch.index = 9; touch.position = Vector2(272,610)
    root.push_input(touch,true)
    check(stage.squad.active_index == 2,"Portrait touch selects MICA")
    touch = touch.duplicate(); touch.pressed = false; root.push_input(touch,true)
    tap(KEY_1)
    await settle()
    check(stage.current_step == 1,"Normal route arms first combat without an unmarked F gate")
    var follower_shots := {}
    for actor in stage.squad.operators:
        actor.primary_fired.connect(func(shooter:OperatorActor)->void: follower_shots[shooter.operator_id]=true)
    var combat_audio: Node = preload("res://scripts/audio/combat_sfx_bank.gd").manager(self)
    combat_audio.debug_trace = true
    var opening_wave := (stage.main_route[1].get("encounter", []) as Array).size()
    check(opening_wave >= 4 and stage.enemies_alive == opening_wave,"Opening route immediately registers every authored first-wave robot")
    check(stage._combat_started,"Opening route begins real combat without debug encounter shortcut")
    var leader := stage.squad.get_active_operator()
    for tick in range(120): await physics_frame
    for follower in stage.squad.operators:
        if follower != leader:
            check(follower.global_position.distance_to(leader.global_position) < 520.0,
                follower.display_name+" abandoned the controlled operator for distant hostiles")
    check(stage.current_step == 1,"Remote hostiles cannot clear an encounter before player arrival")
    var encounter: Dictionary = stage.main_route[1]
    var center := Vector2(float(encounter.x),float(encounter.y))
    # Place the fixture at the authored combat space. The normal access action,
    # not debug_spawn_encounter_for_step(), started the remote encounter.
    for index in range(stage.squad.operators.size()):
        stage.squad.operators[index].global_position = stage.battlefield.constrain(center + Vector2(-120.0, 35.0) + SquadController.FORMATION_OFFSETS[index] * 0.35)
    var arrival := stage.squad.get_active_operator().global_position
    await settle()
    check(stage.enemies_alive > 0,"Entering the connected combat zone spawns robot encounter")
    check(stage._combat_started,"Encounter activated in normal campaign")
    check(stage.battlefield.active,"Normal encounter owns an active combat floor")
    check(stage.squad.get_active_operator().global_position.distance_to(arrival) < 60.0,"Normal encounter teleported the squad")
    for actor in stage.squad.operators:
        check(stage.battlefield.contains(actor.global_position),actor.display_name+" placed on active combat floor")
    for tick in range(600):
        await physics_frame
        if follower_shots.has("CHR_PROTO_02") and follower_shots.has("CHR_PROTO_03") and combat_audio.played_count >= 3:
            break
    check(follower_shots.has("CHR_PROTO_02"),"ROOK follower fires in actual encounter")
    check(follower_shots.has("CHR_PROTO_03"),"MICA follower fires in actual encounter")
    var cues: Array[String] = []
    for event in combat_audio.debug_snapshot().get("events",[]): cues.append(str(event.get("cue","")))
    check(cues.has("rook_fire"),"ROOK live firing emits mapped SFX")
    check(cues.has("mica_fire"),"MICA live firing emits mapped SFX")
    check(combat_audio.played_count >= 3,"Live encounter advances the combat SFX voice bank")
    var report := {"checks":checks,"failed":failed,"pass":failed.is_empty(),"normal_opening_route":true,"native_input_events":true,"no_debug_fire":true,"sfx_events":cues}
    var report_path := "res://qa/music_integration_20260920/combat_regression.json"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="):
            report_path = arg.trim_prefix("--out=")
    var f := FileAccess.open(report_path,FileAccess.WRITE)
    f.store_string(JSON.stringify(report,"  "))
    print("COMBAT_ENTRY_REGRESSION ",JSON.stringify(report))
    flow.queue_free()
    await process_frame
    quit(0 if failed.is_empty() else 1)
