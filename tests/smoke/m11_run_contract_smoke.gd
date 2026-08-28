extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var run_id := "CH01-RUN-M11-0042"
    var contract_a := RunContract.build(run_id)
    var contract_b := RunContract.build(run_id)
    _check(contract_a == contract_b,"same run ID produces identical M11 contract")
    _check(str(contract_a.get("run_id",""))==run_id,"M11 contract preserves authoritative run ID")
    _check(not str(contract_a.get("hazard_id","")).is_empty() and not str(contract_a.get("opportunity_id","")).is_empty(),"M11 contract always selects one hazard and one opportunity")

    var hazard_ids: Dictionary = {}
    var opportunity_ids: Dictionary = {}
    for i in range(32):
        var sampled := RunContract.build("CH01-RUN-VARIANCE-%02d"%i)
        hazard_ids[str(sampled.get("hazard_id",""))]=true
        opportunity_ids[str(sampled.get("opportunity_id",""))]=true
    _check(hazard_ids.size()>1,"different run IDs produce more than one hazard")
    _check(opportunity_ids.size()>1,"different run IDs produce more than one opportunity")

    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene=stage
    await _frames(4)
    stage.configure_campaign({},run_id,contract_a)

    _check(stage.debug_run_contract()==contract_a,"StoryStage owns the issued run contract")
    stage.debug_spawn_encounter_for_step(1)
    await _frames(3)
    var rifle:EnemyActor=null
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and "RIFLE" in (node as EnemyActor).enemy_id:
            rifle=node as EnemyActor
            break
    _check(rifle!=null,"M11 smoke resolves authored rifle hostile")
    if rifle!=null:
        var enemy_contract:=rifle.debug_run_modifier_contract()
        _check(is_equal_approx(float(enemy_contract.get("enemy_health_multiplier",0.0)),float(contract_a.get("enemy_health_multiplier",0.0))),"enemy receives run health multiplier")
        _check(is_equal_approx(float(enemy_contract.get("enemy_damage_multiplier",0.0)),float(contract_a.get("enemy_damage_multiplier",0.0))),"enemy receives run damage multiplier")
        _check(is_equal_approx(float(enemy_contract.get("enemy_speed_multiplier",0.0)),float(contract_a.get("enemy_speed_multiplier",0.0))),"enemy receives run speed multiplier")
        _check(is_equal_approx(float(enemy_contract.get("enemy_attack_interval_multiplier",0.0)),float(contract_a.get("enemy_attack_interval_multiplier",0.0))),"enemy receives run attack interval multiplier")
        var expected_hp:=92.0*float(contract_a.get("enemy_health_multiplier",1.0))
        _check(is_equal_approx(rifle.max_health,expected_hp),"authored rifle HP is multiplied exactly once by run contract")

    # Freeze the encounter after enemy-modifier assertions. Run-boost checks below
    # must measure only explicit test damage/energy, never incidental enemy AI.
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            (node as EnemyActor).set_physics_process(false)
    for node in root.get_children():
        if node is PrototypeProjectile and (node as PrototypeProjectile).target_group=="operators":
            node.queue_free()
    await process_frame

    stage.debug_seed_cargo(100,40,2,1,true,5)
    var summary:=stage.debug_extraction_summary("R05_CORE")
    var expected_research:=int(round(140.0*float(contract_a.get("research_reward_multiplier",1.0))))
    var expected_salvage:=int(round(2.0*float(contract_a.get("salvage_reward_multiplier",1.0))))
    var expected_fragments:=int(round(1.0*float(contract_a.get("fragment_reward_multiplier",1.0))))
    _check(int(summary.get("secured_research",-1))==expected_research,"run contract multiplies secured research reward")
    _check(int(summary.get("secured_salvage",-1))==expected_salvage,"run contract multiplies secured salvage reward")
    _check(int(summary.get("secured_fragments",-1))==expected_fragments,"run contract multiplies secured signal reward")

    # Optional-room boosts are deployment-only and idempotent.
    var aster:=stage.squad.operators[0]
    aster.health=aster.max_health
    var field_stim:=stage.debug_activate_run_boost_for_room("O01_SUPPLY")
    _check(field_stim=="FIELD_STIM","O01 activates FIELD STIM run-only boost")
    var stim_contract:=aster.debug_run_boost_contract()
    _check(is_equal_approx(float(stim_contract.get("operator_speed_multiplier",0.0)),1.10),"FIELD STIM grants +10 percent operator speed")
    _check(is_equal_approx(float(stim_contract.get("incoming_damage_multiplier",0.0)),0.90),"FIELD STIM grants 10 percent incoming damage reduction")
    var hp_before:=aster.health
    aster.apply_damage(20.0)
    _check(is_equal_approx(hp_before-aster.health,18.0),"FIELD STIM changes actual incoming damage authority")
    var repeated:=stage.debug_activate_run_boost_for_room("O01_SUPPLY")
    _check(repeated.is_empty(),"same optional-room boost cannot stack twice")
    var repeated_contract:=aster.debug_run_boost_contract()
    _check(is_equal_approx(float(repeated_contract.get("operator_speed_multiplier",0.0)),1.10),"repeated boost attempt leaves speed multiplier unchanged")

    var overcharge:=stage.debug_activate_run_boost_for_room("O02_RESEARCH")
    _check(overcharge=="OVERCHARGE_CELL","O02 activates OVERCHARGE CELL run-only boost")
    var combined_contract:=aster.debug_run_boost_contract()
    _check(is_equal_approx(float(combined_contract.get("primary_damage_multiplier",0.0)),1.08),"OVERCHARGE CELL grants primary damage multiplier")
    stage.squad.debug_set_energy(0.0)
    stage.squad.add_energy(10.0,"M11-ENERGY-TEST")
    _check(is_equal_approx(float(stage.squad.debug_energy_contract().get("current",0.0)),12.0),"OVERCHARGE CELL grants +20 percent actual squad energy gain")

    var boost_ids:=stage.debug_active_run_boosts()
    _check(boost_ids==["FIELD_STIM","OVERCHARGE_CELL"],"stage records active run-only boosts in activation order")
    summary=stage.debug_extraction_summary("R05_CORE")
    _check(bool(summary.get("run_only_boosts_expire_on_return",false)),"mission summary explicitly marks run-only boost expiration")
    _check((summary.get("active_run_boosts",[]) as Array)==["FIELD_STIM","OVERCHARGE_CELL"],"mission summary audits active run-only boosts")

    # Campaign commits permanent rewards only; run contract/boost state must not leak.
    var campaign:=CampaignProgression.new(false)
    var transaction:=campaign.commit_mission(summary)
    _check(bool(transaction.get("committed",false)),"M11 summary still commits through normal campaign transaction")
    var campaign_snapshot:=campaign.snapshot()
    _check(not campaign_snapshot.has("run_contract") and not campaign_snapshot.has("active_run_boosts"),"CampaignProgression never persists run contract or run-only boost list")
    _check(not campaign_snapshot.has("run_energy_gain_multiplier") and not campaign_snapshot.has("run_primary_damage_multiplier"),"CampaignProgression never persists tactical run multipliers")

    stage.queue_free()
    await process_frame

    # A new stage configured without a new run contract starts neutral, proving
    # the previous deployment's tactical boosts did not become permanent growth.
    var next_stage:=STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(next_stage)
    current_scene=next_stage
    await _frames(3)
    next_stage.configure_campaign(campaign.snapshot(),"CH01-NEXT-NEUTRAL")
    var next_aster:=next_stage.squad.operators[0]
    var next_boost:=next_aster.debug_run_boost_contract()
    _check(is_equal_approx(float(next_boost.get("operator_speed_multiplier",0.0)),1.0),"new deployment does not inherit prior FIELD STIM")
    _check(is_equal_approx(float(next_boost.get("primary_damage_multiplier",0.0)),1.0),"new deployment does not inherit prior OVERCHARGE CELL")
    _check(is_equal_approx(float(next_stage.squad.debug_energy_contract().get("run_energy_gain_multiplier",0.0)),1.0),"new deployment resets run energy multiplier")

    next_stage.debug_spawn_encounter_for_step(1)
    await _frames(2)
    var neutral_rifle:EnemyActor=null
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and "RIFLE" in (node as EnemyActor).enemy_id:
            neutral_rifle=node as EnemyActor
            break
    _check(neutral_rifle!=null and is_equal_approx(neutral_rifle.max_health,92.0),"legacy/neutral configure path preserves authored enemy HP")

    next_stage.queue_free()
    await process_frame
    _finish()

func _frames(count:int)->void:
    for _i in range(count): await process_frame

func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)

func _finish()->void:
    if failures.is_empty():
        print("M11_RUN_CONTRACT_SMOKE: PASS")
        quit(0)
        return
    print("M11_RUN_CONTRACT_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
