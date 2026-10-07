extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var progression := CampaignProgression.new(false)
    var commit := progression.commit_mission({
        "transaction_id":"M10-INTEL-RUN-1",
        "outcome":"EXTRACTED",
        "secured_research":900,
        "secured_salvage":4,
        "secured_fragments":2,
        "secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1}
    })
    _check(bool(commit.get("committed",false)),"M10 extraction commits intel exactly once")
    var initial:=progression.snapshot(); var samples:Dictionary=initial.get("intel_samples",{})
    _check(int(samples.get("SECURITY",0))==2 and int(samples.get("ABERRANT",0))==1 and int(samples.get("ANCHOR",0))==1,"M10 deposits all three secured intel families")
    progression.commit_mission({"transaction_id":"M10-INTEL-RUN-1","outcome":"EXTRACTED","secured_research":900,"secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1}})
    var duplicate_snapshot:=progression.snapshot(); var duplicate_samples:Dictionary=duplicate_snapshot.get("intel_samples",{})
    _check(int(duplicate_samples.get("SECURITY",0))==2,"duplicate run cannot duplicate intel samples")

    var security:=progression.analyze_intel("ANL_SECURITY_ARC_GAP")
    _check(bool(security.get("success",false)),"Lab analyzes SECURITY arc-gap sample")
    var after_security:=progression.snapshot(); var after_security_samples:Dictionary=after_security.get("intel_samples",{})
    _check(int(after_security.get("research_value",0))==780 and int(after_security_samples.get("SECURITY",-1))==0,"SECURITY analysis deducts 120 research and two samples")
    _check((after_security.get("unlocked_modules",[]) as Array).has("MOD_PRISM_FOCUS"),"SECURITY analysis unlocks PRISM FOCUS")
    _check((after_security.get("unlocked_weaknesses",[]) as Array).has("SECURITY_ARC_GAP"),"SECURITY analysis unlocks security weakness knowledge")
    var wrong_operator:=progression.equip_module("CHR_PROTO_02","MOD_PRISM_FOCUS")
    _check(not bool(wrong_operator.get("success",true)) and str(wrong_operator.get("reason",""))=="MODULE_INCOMPATIBLE","module cannot be equipped by the wrong operator")
    _check(bool(progression.equip_module("CHR_PROTO_01","MOD_PRISM_FOCUS").get("success",false)),"ASTER equips PRISM FOCUS")

    _check(bool(progression.analyze_intel("ANL_ABERRANT_JOINT_MAP").get("success",false)),"Lab analyzes ABERRANT joint map")
    _check(bool(progression.equip_module("CHR_PROTO_02","MOD_BREACH_LINER").get("success",false)),"ROOK equips BREACH LINER")
    _check(bool(progression.analyze_intel("ANL_ANCHOR_SIGNAL_MODEL").get("success",false)),"Lab analyzes ANCHOR signal model")
    _check(bool(progression.equip_module("CHR_PROTO_03","MOD_SENSOR_ARRAY").get("success",false)),"MICA equips SENSOR ARRAY")
    var loadout:=progression.snapshot(); var equipped:Dictionary=loadout.get("equipped_modules",{})
    _check(str(equipped.get("CHR_PROTO_01",""))=="MOD_PRISM_FOCUS" and str(equipped.get("CHR_PROTO_02",""))=="MOD_BREACH_LINER" and str(equipped.get("CHR_PROTO_03",""))=="MOD_SENSOR_ARRAY","M10 persists all three operator loadouts")
    _check(int(loadout.get("research_value",0))==460,"all three analyses deduct their exact research costs")

    var stage:=STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage); current_scene=stage; await _frames(4)
    stage.configure_campaign(loadout,"M10-STAGE-RUN")
    var aster:=stage.squad.operators[0]; var rook:=stage.squad.operators[1]; var mica:=stage.squad.operators[2]
    _check(aster.debug_equipped_module()=="MOD_PRISM_FOCUS","next deployment injects ASTER module")
    _check(rook.debug_equipped_module()=="MOD_BREACH_LINER","next deployment injects ROOK module")
    _check(mica.debug_equipped_module()=="MOD_SENSOR_ARRAY","next deployment injects MICA module")
    var ac:Dictionary=(aster.get_node("SkillController") as OperatorSkillController).debug_contract(); var rc:Dictionary=(rook.get_node("SkillController") as OperatorSkillController).debug_contract(); var mc:Dictionary=(mica.get_node("SkillController") as OperatorSkillController).debug_contract()
    _check(is_equal_approx(float(ac.get("aster_prism_focus_multiplier",0.0)),1.15),"PRISM FOCUS changes ASTER skill authority")
    _check(is_equal_approx(float(rc.get("rook_breach_damage",0.0)),52.0) and is_equal_approx(float(rc.get("rook_breach_stagger",0.0)),3.0),"BREACH LINER changes ROOK damage and stagger authority")
    _check(is_equal_approx(float(mc.get("mica_scan_radius",0.0)),500.0) and is_equal_approx(float(mc.get("mica_scan_exposed",0.0)),8.0),"SENSOR ARRAY changes MICA scan range and duration authority")

    stage.call("_award_enemy_intel","ENM_SITE7_RIFLE_01")
    stage.call("_award_enemy_intel","ENM_SITE7_RIFLE_01")
    stage.call("_award_enemy_intel","ENM_SITE7_DRONE_01")
    stage.call("_award_enemy_intel","ENM_SITE7_ABERRANT_01")
    stage.call("_award_enemy_intel","BOSS_SITE7_ANCHOR_01")
    var field_intel:=stage.debug_intel_cargo()
    _check(int(field_intel.get("SECURITY",0))==2 and int(field_intel.get("ABERRANT",0))==1 and int(field_intel.get("ANCHOR",0))==1,"field intel awards one sample per unique enemy identity")
    _check("SEC 02" in stage.hud.debug_intel_text() and "ABR 01" in stage.hud.debug_intel_text() and "ANC 01" in stage.hud.debug_intel_text(),"field HUD exposes unsecured intel cargo")

    stage.debug_seed_cargo(100,40,2,1,true,5)
    var extracted:=stage.debug_extraction_summary("R05_CORE")
    var secured_intel:Dictionary=extracted.get("secured_intel",{})
    _check(int(secured_intel.get("SECURITY",0))==2 and int(secured_intel.get("ABERRANT",0))==1 and int(secured_intel.get("ANCHOR",0))==1,"deliberate extraction secures all intel samples")
    _check(int(extracted.get("lost_intel_samples",-1))==0,"extraction loses no intel samples")
    var wiped:=stage.debug_wipe_summary(); var wiped_intel:Dictionary=wiped.get("secured_intel",{})
    _check(int(wiped_intel.get("SECURITY",-1))==0 and int(wiped_intel.get("ABERRANT",-1))==0 and int(wiped_intel.get("ANCHOR",-1))==0,"wipe secures zero intel samples")
    _check(int(wiped.get("lost_intel_samples",0))==4,"wipe loses all four unsecured intel samples")

    # Retained M8 regression: test actual mission node IDs rather than a detached
    # constant list so authored extraction windows cannot silently drift from data.
    stage.current_step=2; stage.call("_complete_step")
    _check(stage.debug_extraction_active(),"Archive Annex actual node opens extraction window")
    stage.debug_continue_extraction()
    _check(stage.current_step==3,"Archive continue advances to Containment Junction")
    stage.call("_complete_step")
    _check(stage.debug_extraction_active(),"Containment Junction actual node opens extraction window")
    stage.debug_continue_extraction()
    _check(stage.current_step==4,"Containment continue advances to Core C")
    stage.call("_complete_step")
    _check(not stage.debug_extraction_active() and stage.current_step==5,"Current Stage 1 Core C proceeds to the final lift (two early windows)")

    # M10 module behavior with one deterministic live SECURITY target. All other
    # encounter actors are moved outside every tested skill radius so nearest-in-aim
    # gameplay targeting cannot make this regression nondeterministic.
    for node in get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node): node.queue_free()
    await _frames(2)
    stage.debug_spawn_encounter_for_step(1); await _frames(3)
    var target:EnemyActor=null
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and "DRONE" in (node as EnemyActor).enemy_id:
            target=node as EnemyActor
            break
    _check(target!=null,"M10 module smoke resolves live SECURITY target")
    if target!=null:
        var parked_index:=0
        for node in get_nodes_in_group("m3_enemies"):
            if not (node is EnemyActor):
                continue
            var enemy:=node as EnemyActor
            enemy.set_physics_process(false)
            if enemy==target:
                continue
            enemy.global_position=Vector2(1700.0+float(parked_index)*160.0,650.0)
            parked_index+=1

        target.max_health=500.0
        target.health=500.0
        target.global_position=Vector2(990,450)
        target.set_physics_process(false)

        mica.global_position=Vector2(520,450); mica.aim_world=Vector2.RIGHT; stage.squad.request_control(2)
        var mica_skills:=mica.get_node("SkillController") as OperatorSkillController
        _check(mica_skills.debug_force_cast("Q"),"SENSOR ARRAY reaches target beyond vanilla 420 range")
        var status:=target.debug_status_contract()
        _check(float(status.get("exposed_left",0.0))>7.5,"SENSOR ARRAY applies extended EXPOSED duration")

        aster.global_position=Vector2(520,450); aster.aim_world=Vector2.RIGHT; stage.squad.request_control(0)
        var before:=target.health
        _check((aster.get_node("SkillController") as OperatorSkillController).debug_force_cast("Q"),"PRISM FOCUS casts against analyzed SECURITY target")
        _check(before-target.health>49.0,"PRISM FOCUS adds 15 percent to EXPOSED security Prism damage")

        target.apply_exposed(6.0,"M10-RESET")
        rook.global_position=Vector2(800,450); rook.aim_world=Vector2.RIGHT; stage.squad.request_control(1)
        var rook_before:=target.health
        _check((rook.get_node("SkillController") as OperatorSkillController).debug_force_cast("Q"),"BREACH LINER consumes EXPOSED")
        var post_breach:=target.debug_status_contract()
        _check(rook_before-target.health>=51.9 and float(post_breach.get("stagger_left",0.0))>2.8,"BREACH LINER applies boosted damage and 3 second stagger")

    stage.queue_free(); await process_frame
    _finish()

func _frames(count:int)->void:
    for _i in range(count): await process_frame
func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)
func _finish()->void:
    if failures.is_empty(): print("M10_INTEL_LOADOUT_SMOKE: PASS"); quit(0); return
    print("M10_INTEL_LOADOUT_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
