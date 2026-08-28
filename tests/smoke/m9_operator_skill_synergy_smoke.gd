extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(6)
    stage.configure_campaign({"damage_multiplier":1.08,"research_multiplier":1.12},"M9-SMOKE")
    var squad := stage.squad
    _check(squad.operators.size()==3,"M9 retains three-operator squad")
    var aster:=squad.operators[0]; var rook:=squad.operators[1]; var mica:=squad.operators[2]
    var aster_skills:=aster.get_node_or_null("SkillController") as OperatorSkillController
    var rook_skills:=rook.get_node_or_null("SkillController") as OperatorSkillController
    var mica_skills:=mica.get_node_or_null("SkillController") as OperatorSkillController
    _check(aster_skills!=null and rook_skills!=null and mica_skills!=null,"all three operators own skill authority")
    if aster_skills==null or rook_skills==null or mica_skills==null:
        _finish(); return

    var aster_contract:=aster_skills.debug_contract(); var rook_contract:=rook_skills.debug_contract(); var mica_contract:=mica_skills.debug_contract()
    _check(str(aster_contract.get("ultimate_key",""))=="X" and str(aster_contract.get("reload_key",""))=="R","M9 preserves R reload and assigns X ultimate")
    _check((aster_contract.get("skill_icons",[]) as Array).size()==3 and (rook_contract.get("skill_icons",[]) as Array).size()==3 and (mica_contract.get("skill_icons",[]) as Array).size()==3,"three authored skill icons remain bound per operator")

    stage.current_step=1
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(1)
    await _frames(4)
    var enemies:Array[EnemyActor]=[]
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor: enemies.append(node as EnemyActor)
    _check(enemies.size()>=1,"M9 synergy smoke has a live hostile")
    if enemies.is_empty(): _finish(); return
    var target:=enemies[0]
    # Keep the authority target alive for the full setup→exploit→consume→ultimate
    # audit. The previous test used production encounter HP and MICA Sensor Bloom
    # killed the already-damaged target before the final status-source assertion.
    target.max_health=400.0
    target.health=400.0
    target.global_position=Vector2(700,420)
    for i in range(1,enemies.size()): enemies[i].global_position=Vector2(1450+float(i)*120.0,650)
    squad.debug_set_energy(0.0)

    mica.global_position=Vector2(510,420); mica.aim_world=Vector2.RIGHT; squad.request_control(2)
    var scan_ok:=mica_skills.debug_force_cast("Q")
    _check(scan_ok,"MICA Pulse Scan casts on live hostile")
    _check(target.is_exposed(),"MICA Pulse Scan applies EXPOSED")
    _check(str(mica_skills.debug_contract().get("last_synergy",""))=="EXPOSED_SETUP","MICA records EXPOSED setup role")
    var energy_after_scan:=float(squad.debug_energy_contract().get("current",0.0))
    _check(energy_after_scan>0.0,"MICA setup contributes squad energy")

    aster.global_position=Vector2(505,420); aster.aim_world=Vector2.RIGHT; squad.request_control(0)
    var hp_before_prism:=target.health
    var prism_ok:=aster_skills.debug_force_cast("Q")
    _check(prism_ok,"ASTER Prism casts into MICA setup")
    _check(target.health<hp_before_prism-40.0,"ASTER Prism receives EXPOSED exploit multiplier")
    _check(target.is_exposed(),"ASTER exploit does not consume EXPOSED before Breach")
    _check(str(aster_skills.debug_contract().get("last_synergy",""))=="EXPOSED_EXPLOIT","ASTER records EXPOSED exploit")

    rook.global_position=Vector2(555,420); rook.aim_world=Vector2.RIGHT; squad.request_control(1)
    var energy_before_breach:=float(squad.debug_energy_contract().get("current",0.0))
    var breach_ok:=rook_skills.debug_force_cast("Q")
    _check(breach_ok,"ROOK Breach Slam casts after setup/exploit")
    _check(not target.is_exposed() and target.is_staggered(),"ROOK consumes EXPOSED into STAGGER")
    _check(float(squad.debug_energy_contract().get("current",0.0))>=energy_before_breach+27.9,"stagger grants large squad-energy reward")
    _check(str(rook_skills.debug_contract().get("last_synergy",""))=="EXPOSED_CONSUMED_STAGGER","ROOK records setup-consume synergy")

    aster.global_position=Vector2(450,520); aster.aim_world=Vector2.RIGHT; squad.request_control(0)
    var dash_start:=aster.global_position
    _check(aster_skills.debug_force_cast("E"),"ASTER Vector Dash casts")
    _check(aster.global_position.x>=dash_start.x+140.0,"ASTER Vector Dash repositions authoritatively")

    rook.health=rook.max_health; squad.request_control(1); _check(rook_skills.debug_force_cast("E"),"ROOK Bulwark casts")
    var rook_hp:=rook.health; rook.apply_damage(20.0)
    _check(rook.health>=rook_hp-10.1,"ROOK Bulwark halves incoming damage")

    aster.health=aster.max_health*0.45; mica.global_position=Vector2(500,520); mica.aim_world=Vector2.RIGHT; squad.request_control(2)
    var aster_hp_before_relay:=aster.health
    _check(mica_skills.debug_force_cast("E"),"MICA Relay Step casts")
    _check(aster.health>aster_hp_before_relay,"MICA Relay Step heals squad")
    _check(float(aster.debug_runtime_skill_buffs().get("guard_left",0.0))>0.0,"MICA Relay Step grants squad guard")

    squad.debug_set_energy(100.0); squad.request_control(0)
    _check(aster_skills.debug_force_cast("X"),"ASTER Overclock spends full energy")
    _check(float(squad.debug_energy_contract().get("current",99.0))<=0.01,"ultimate transaction consumes shared energy")
    _check(float(aster.debug_runtime_skill_buffs().get("overclock_left",0.0))>4.5,"ASTER Overclock activates timed fire buff")

    squad.debug_set_energy(100.0); squad.request_control(1)
    _check(rook_skills.debug_force_cast("X"),"ROOK Scatter Cycle casts")
    _check(float(rook.debug_runtime_skill_buffs().get("scatter_cycle_left",0.0))>4.5,"ROOK Scatter Cycle activates timed shotgun cycle")

    squad.debug_set_energy(100.0); squad.request_control(2); mica.global_position=Vector2(520,420)
    _check(mica_skills.debug_force_cast("X"),"MICA Sensor Bloom casts")
    _check(target.is_exposed(),"MICA Sensor Bloom applies area EXPOSED")
    _check(str(mica_skills.debug_contract().get("last_skill",""))=="MICA_SENSOR_BLOOM","MICA ultimate identity is preserved")

    await _frames(2)
    var hud_contract:=stage.hud.debug_skill_hud_contract()
    _check((hud_contract.get("keys",[]) as Array)==["Q","E","X"],"HUD exposes Q/E/X skill keys")
    _check(str(hud_contract.get("reload_key",""))=="R","HUD keeps R reserved for reload")

    _check(is_instance_valid(target),"M9 status audit target remains alive through the full combo")
    if is_instance_valid(target):
        var status_contract:=target.debug_status_contract()
        _check(str(status_contract.get("status_source","")) in ["MICA_SENSOR_BLOOM","ROOK_BREACH_SLAM"],"enemy status authority records skill source")

    stage.queue_free(); await process_frame
    _finish()

func _frames(count:int)->void:
    for _i in range(count): await process_frame

func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)

func _finish()->void:
    if failures.is_empty(): print("M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS"); quit(0); return
    print("M9_OPERATOR_SKILL_SYNERGY_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
