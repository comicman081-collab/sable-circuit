extends SceneTree
## Native UI and held gameplay/VFX fixtures. No human play or balance approval.
## Headless emits only fixture metadata; native screenshots use no image resize.
const Output := preload("res://tests/support/test_output.gd")
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
var out:=Output.path("res://.cache/diag/expansion_item3_20261006/native")
var failures:Array[String]=[]
var checks:=0
var captures:Array=[]
var flow:GameFlow
func _init()->void:call_deferred("run")
func run()->void:
    root.size=Vector2i(1920,1080); root.content_scale_size=Vector2i(1280,720); root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name()!="headless":DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    flow=GameFlow.new(); flow.persist_campaign=false; root.add_child(flow)
    var p:=flow.campaign; p.research_value=10000
    for key in IntelSamples.KEYS:p.intel_samples[key]=3
    flow.enter_base(); await create_timer(0.8).timeout
    var lobby:=flow.current_view as BaseLobby
    await shot("lab_page1","Three original analyses in original order; new samples are controlled fixture stock.")
    lobby._analysis_next.pressed.emit(); lobby._analysis_next.pressed.emit()
    await shot("lab_page3","All eight analyses span 3+3+2 rows.")
    for row:Dictionary in p.snapshot().discoveries:p.analyze_intel(row.analysis_id)
    lobby.refresh_campaign(p.snapshot())
    for operator in CampaignProgression.OPERATOR_IDS:
        # Real connected EQUIP, then NEXT MOD, puts the second unlocked module on.
        for i in range(2):
            var button:=lobby.find_child("ModuleCycle_"+operator,true,false) as Button
            button.pressed.emit()
    await shot("lab_module_cycle","Actual GameFlow module cycle: FROST LENS / SPORE FILTER / ECHO RELAY; one slot each.")
    flow.deploy_mission("MIS_CH01_01"); await create_timer(0.5).timeout
    var stage:=flow.current_view as StoryStage01
    freeze(stage)
    stage.debug_seed_intel(2,1,1,{"AERATOR":1,"CRYO":1,"GANTRY":1,"ARCHIVE":1,"ORIGIN":1})
    await shot("field_intel8","Actual stage HUD, eight-key fixture cargo; gameplay paused, not a human play capture.")
    for pair in [["WPN_DMR_RAIL_01",0],["WPN_SHOTGUN_NULL_01",1]]:
        clear_effects(); await physics_frame
        var actor:=stage.squad.operators[pair[1]]
        stage.squad.request_control(pair[1]); actor.apply_campaign_modifiers({"weapon_id":pair[0],"module_id":""})
        # A controlled operator re-aims at the cursor every frame: hold the aim and pose it for two physics frames instead.
        actor.set_physics_process(true); actor.debug_drive(Vector2.ZERO,Vector2.RIGHT); await physics_frame; await physics_frame; actor.set_physics_process(false)
        actor.reset_for_battle_preview()
        check(actor.debug_fire_once(),pair[0]+" actual trigger")
        var origin:=actor._get_projectile_spawn_origin()
        # The shot is aimed at a real enemy, moved onto the staged impact point so the hit family lands on a robot.
        var target:EnemyActor
        for node in get_nodes_in_group("m3_enemies"):
            if node is EnemyActor:
                target=node
                break
        check(target!=null,pair[0]+" has an enemy to aim at")
        if target:target.global_position=origin+Vector2(230,0)-(target.get_combat_hit_rect().get_center()-target.global_position)
        for node in root.get_children():
            if node is PrototypeProjectile and node.owner_actor==actor:
                node.set_physics_process(false); node.global_position=origin+node.direction*100; node._travelled=100; node.queue_redraw()
            elif node is CombatMuzzleVFX:
                node.set_process(false); node.age=node.life*0.22; node.queue_redraw()
        # Impact is explicitly staged visual evidence, independently of a target hit.
        CombatFeedback.spawn_hit_visual(self,origin+Vector2(230,0),str(actor.weapon_spec.hit_vfx_profile),Color.WHITE,Vector2.RIGHT)
        for node in root.get_children():
            if node is CombatHitVFX:node.set_process(false); node.age=node.lifetime*0.2; node.queue_redraw()
        await shot("vfx_"+str(pair[0]).to_lower(),"HELD VFX FIXTURE: real weapon trigger aimed at an enemy; projectile flight and impact positions staged. Not live collision or human play.")
        actor.debug_stop_drive()
    clear_effects()
    flow.show_results(stage.debug_extraction_summary())
    # The payout tiles count up (0.5 s delay + 0.9 s) and the stamp fades in until 1.8 s: capture only after both end.
    await create_timer(2.0).timeout
    var results:=flow.current_view as MissionResults
    var secured:=results.debug_summary()
    var tile_value:=results._tiles.get_child(0).get_child(0).get_child(1) as Label
    check(tile_value.text=="+%d"%int(secured.get("secured_research",secured.get("secured_rewards",0))),"results count-up finished before the capture: "+tile_value.text)
    await shot("results_intel8","Actual GameFlow results commit includes all eight secured sample keys.")
    var f:=FileAccess.open(out.path_join("capture_report.json"),FileAccess.WRITE)
    f.store_string(JSON.stringify({"checks":checks,"failures":failures,"captures":captures,"native_resolution":[1920,1080],"native_capture":DisplayServer.get_name()!="headless","human_play":false,"visual_approval":false,"balance_approval":false,"resize":false},"  ")); f.close()
    flow.queue_free(); await process_frame
    print("EXPANSION_ITEM3_CAPTURE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)
func shot(id:String,note:String)->void:
    await process_frame
    var row:={"id":id,"note":note,"capture":"","sha256":""}
    if DisplayServer.get_name()!="headless":
        await RenderingServer.frame_post_draw
        var image:=root.get_texture().get_image()
        check(image.get_size()==Vector2i(1920,1080),id+" exact native resolution")
        var path:=out.path_join(id+".png")
        check(image.save_png(ProjectSettings.globalize_path(path))==OK,id+" saved PNG")
        row.capture=path
        row.sha256=FileAccess.get_sha256(path)
    captures.append(row)
func freeze(stage:StoryStage01)->void:
    stage.set_physics_process(false); stage.squad.set_process(false)
    for actor in stage.squad.operators:actor.set_physics_process(false); actor.get_node("SkillController").set_process(false)
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:node.set_physics_process(false)
func clear_effects()->void:
    for node in root.get_children():
        if node is PrototypeProjectile or node is CombatMuzzleVFX or node is CombatHitVFX:node.queue_free()
func check(ok:bool,label:String)->void:
    checks+=1
    if not ok:failures.append(label);push_error(label)
