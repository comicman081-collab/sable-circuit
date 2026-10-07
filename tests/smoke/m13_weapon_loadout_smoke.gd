extends SceneTree

const TestOutput := preload("res://tests/support/test_output.gd")
var test_save_path := TestOutput.path("res://qa/campaign_20260919/m13_weapon_loadout_smoke_" + str(Time.get_unix_time_from_system()).replace(".","_") + ".json")

var failures:Array[String]=[]

func _init()->void: call_deferred("_run")

func _run()->void:
    var envelope := preload("res://tests/support/weapon_envelope.gd")
    for id: String in envelope.NEW_IDS:
        var row := WeaponRegistry.get_weapon(id)
        var damage_rate: Dictionary = envelope.dps(row)
        _check(damage_rate.burst<=100.0 and damage_rate.sustained<=78.0,id+" item3 absolute DPS envelope")
        for operator: String in row.compatible_operators:
            _check(damage_rate.sustained<=envelope.legacy_best(operator),id+" sustained DPS below operator's best legacy weapon")
        _check(not str(row.get("role","")).is_empty(),id+" states its range/burst tradeoff")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(test_save_path.get_base_dir()))
    var progression:=CampaignProgression.new(false)
    var initial:=progression.snapshot(); var initial_unlocked:Array=initial.get("unlocked_weapons",[]); var initial_equipped:Dictionary=initial.get("equipped_weapons",{})
    _check(int(initial.get("schema_version",0))==CampaignProgression.SAVE_SCHEMA_VERSION,"Current campaign schema")
    _check(initial_unlocked.size()==3 and initial_unlocked.has("WPN_AR_COIL_01") and initial_unlocked.has("WPN_SHOTGUN_MAG_01") and initial_unlocked.has("WPN_SMG_SENSOR_01"),"M13 starts with exactly three authored default weapons")
    _check(str(initial_equipped.get("CHR_PROTO_01",""))=="WPN_AR_COIL_01" and str(initial_equipped.get("CHR_PROTO_02",""))=="WPN_SHOTGUN_MAG_01" and str(initial_equipped.get("CHR_PROTO_03",""))=="WPN_SMG_SENSOR_01","each operator starts with its authored default weapon")
    var locked:=progression.equip_weapon("CHR_PROTO_03","WPN_SPECIAL_ARC_01")
    _check(not bool(locked.get("success",true)) and str(locked.get("reason",""))=="WEAPON_LOCKED","locked special weapon cannot be equipped early")

    progression.commit_mission({"transaction_id":"M13-SEED","outcome":"EXTRACTED","secured_research":1200,"secured_salvage":10,"secured_fragments":3,"secured_intel":{"ANCHOR":1}})
    _check(bool(progression.purchase_upgrade("ARMORY_CALIBRATION").get("success",false)),"Armory level 1 purchases")
    var l1:=progression.snapshot(); _check((l1.get("unlocked_weapons",[]) as Array).has("WPN_AR_BURST_02"),"Armory level 1 unlocks burst AR")
    var incompatible:=progression.equip_weapon("CHR_PROTO_02","WPN_AR_BURST_02")
    _check(not bool(incompatible.get("success",true)) and str(incompatible.get("reason",""))=="WEAPON_INCOMPATIBLE","Rook cannot equip incompatible burst AR")
    _check(bool(progression.equip_weapon("CHR_PROTO_01","WPN_AR_BURST_02").get("success",false)),"Aster equips burst AR")

    _check(bool(progression.purchase_upgrade("ARMORY_CALIBRATION").get("success",false)),"Armory level 2 purchases")
    _check((progression.snapshot().get("unlocked_weapons",[]) as Array).has("WPN_LMG_HELIX_01"),"Armory level 2 unlocks LMG")
    var choices:=WeaponRegistry.compatible_weapons("CHR_PROTO_01",progression.snapshot().get("unlocked_weapons",[]))
    var cycle:=progression.cycle_weapon("CHR_PROTO_01")
    _check(bool(cycle.get("success",false)) and choices.has(str(cycle.get("weapon_id",""))) and str(cycle.get("weapon_id",""))!="WPN_AR_BURST_02","Aster weapon cycle advances to the next unlocked compatible weapon")
    _check(bool(progression.equip_weapon("CHR_PROTO_01","WPN_LMG_HELIX_01").get("success",false)),"Aster can directly equip unlocked LMG")
    _check(bool(progression.equip_weapon("CHR_PROTO_01","WPN_AR_BURST_02").get("success",false)),"Aster returns to burst AR for firing audit")

    _check(bool(progression.analyze_intel("ANL_ANCHOR_SIGNAL_MODEL").get("success",false)),"Anchor analysis completes")
    var after_analysis:=progression.snapshot(); _check((after_analysis.get("unlocked_weapons",[]) as Array).has("WPN_SPECIAL_ARC_01"),"Anchor analysis unlocks Arc Lance special weapon")
    _check(bool(progression.equip_weapon("CHR_PROTO_03","WPN_SPECIAL_ARC_01").get("success",false)),"Mica equips Arc Lance special weapon")

    var flow:=GameFlow.new(); root.add_child(flow); await _frames(3); flow.campaign=progression; flow.deploy_stage_01(); await _frames(5)
    var stage:=flow.current_view as StoryStage01
    _check(stage!=null,"M13 GameFlow deploys StoryStage01")
    if stage==null: _finish(); return
    var aster:=stage.squad.operators[0]; var rook:=stage.squad.operators[1]; var mica:=stage.squad.operators[2]
    _check(aster.debug_equipped_weapon()=="WPN_AR_BURST_02","next deployment injects Aster burst AR")
    _check(rook.debug_equipped_weapon()=="WPN_SHOTGUN_MAG_01","next deployment keeps Rook scattergun")
    _check(mica.debug_equipped_weapon()=="WPN_SPECIAL_ARC_01","next deployment injects Mica Arc Lance")
    var ac:=aster.debug_weapon_contract(); var rc:=rook.debug_weapon_contract(); var mc:=mica.debug_weapon_contract()
    _check(int(ac.get("magazine_size",0))==30 and int(ac.get("pellet_count",0))==3 and int(ac.get("ammo_per_trigger",0))==3,"burst AR runtime spec owns 30-mag / 3-shot / 3-ammo transaction")
    _check(int(rc.get("magazine_size",0))==10 and int(rc.get("pellet_count",0))==5 and int(rc.get("ammo_per_trigger",0))==1,"scattergun runtime spec owns five pellets for one shell")
    _check(int(mc.get("magazine_size",0))==6 and is_equal_approx(float(mc.get("damage",0.0)),28.0),"Arc Lance runtime spec owns 6-mag / 28 base damage")

    for actor in stage.squad.operators: actor.set_physics_process(false)
    var campaign_damage:=float(progression.snapshot().get("damage_multiplier",1.0))

    var aster_before:=aster.ammo; _clear_operator_projectiles()
    _check(aster.debug_fire_once(),"Aster burst trigger fires")
    var aster_shots:=_operator_projectiles(aster)
    _check(aster.ammo==aster_before-3,"burst trigger consumes exactly three rounds")
    _check(aster_shots.size()==3,"burst trigger spawns exactly three projectiles")
    for p in aster_shots:
        _check(is_equal_approx(p.damage,7.2*campaign_damage),"burst projectile damage uses weapon spec times campaign multiplier")
        _check(is_equal_approx(p.speed,1100.0) and is_equal_approx(p.lifetime,0.88),"burst projectile speed/lifetime use weapon spec")
    _clear_operator_projectiles()

    var rook_before:=rook.ammo; _check(rook.debug_fire_once(),"Rook scattergun trigger fires"); var rook_shots:=_operator_projectiles(rook)
    _check(rook.ammo==rook_before-1,"scattergun trigger consumes exactly one shell")
    _check(rook_shots.size()==5,"scattergun trigger spawns exactly five pellets")
    _clear_operator_projectiles()

    var mica_before:=mica.ammo; _check(mica.debug_fire_once(),"Mica Arc Lance trigger fires"); var mica_shots:=_operator_projectiles(mica)
    _check(mica.ammo==mica_before-1 and mica_shots.size()==1,"Arc Lance consumes one cell and spawns one projectile")
    if mica_shots.size()==1:
        var p:PrototypeProjectile=mica_shots[0]; _check(is_equal_approx(p.damage,28.0*campaign_damage) and is_equal_approx(p.speed,520.0),"Arc Lance projectile uses special weapon damage/speed authority")
    _clear_operator_projectiles()

    aster.ammo=2; _check(not aster.debug_fire_once(),"burst AR refuses trigger when fewer than three rounds remain")
    _check(aster.is_reloading(),"insufficient burst ammo begins reload transaction")

    var base:=BaseLobby.new(); root.add_child(base); base.configure_campaign(progression.snapshot()); await _frames(3)
    var emitted: Array[String]=[]; base.weapon_cycle_requested.connect(func(operator_id:String)->void: emitted.append(operator_id))
    var weapon_button:=base.find_child("WeaponCycle_CHR_PROTO_01",true,false) as Button
    _check(weapon_button!=null and not weapon_button.disabled,"Aster Base weapon cycle button is enabled when multiple compatible weapons are unlocked")
    if weapon_button!=null: weapon_button.emit_signal("pressed")
    _check(emitted==["CHR_PROTO_01"],"actual Base weapon button emits Aster operator ID exactly once")
    var base_contract:=base.debug_m13_weapon_contract(); _check((base_contract.get("weapon_catalog",[]) as Array).size()==8,"Base receives all eight weapon specs without new image assets")
    base.queue_free(); await process_frame

    var persistent:=CampaignProgression.new(true,test_save_path); persistent.debug_reset(); _write_save({"schema_version":2,"research_value":50,"armory_level":1,"lab_level":0,"analyzed_intel":[],"unlocked_modules":[],"unlocked_weaknesses":[],"equipped_modules":{},"committed_run_ids":[]})
    var migrated:=CampaignProgression.new(true,test_save_path); var migrated_snapshot:=migrated.snapshot(); var migrated_weapons:Dictionary=migrated_snapshot.get("equipped_weapons",{})
    _check(int(migrated_snapshot.get("schema_version",0))==CampaignProgression.SAVE_SCHEMA_VERSION,"v2 campaign migrates to current schema")
    _check(str(migrated_weapons.get("CHR_PROTO_01",""))=="WPN_AR_COIL_01" and str(migrated_weapons.get("CHR_PROTO_02",""))=="WPN_SHOTGUN_MAG_01" and str(migrated_weapons.get("CHR_PROTO_03",""))=="WPN_SMG_SENSOR_01","v2 save receives all three safe default weapons")
    _check((migrated_snapshot.get("unlocked_weapons",[]) as Array).has("WPN_AR_BURST_02"),"v2 Armory level 1 derives burst AR unlock during migration")
    migrated.debug_reset()

    flow.queue_free(); await process_frame
    _finish()

# Live projectiles of this operator. Nodes already queued for deletion are not
# live: followers legitimately fire at the auto-started opening encounter during
# deployment, and a cleared volley stays a root child until the frame ends.
func _operator_projectiles(actor:OperatorActor)->Array[PrototypeProjectile]:
    var out:Array[PrototypeProjectile]=[]
    for node in root.get_children():
        if node is PrototypeProjectile and not node.is_queued_for_deletion() and (node as PrototypeProjectile).owner_actor==actor: out.append(node as PrototypeProjectile)
    return out
func _clear_operator_projectiles()->void:
    for node in root.get_children():
        if node is PrototypeProjectile: node.queue_free()
func _write_save(payload:Dictionary)->void:
    var file:=FileAccess.open(test_save_path,FileAccess.WRITE)
    if file==null: _check(false,"M13 migration test opens save path"); return
    file.store_string(JSON.stringify(payload)); file=null
func _frames(count:int)->void:
    for _i in range(count): await process_frame
func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)
func _finish()->void:
    if failures.is_empty(): print("M13_WEAPON_LOADOUT_SMOKE: PASS"); quit(0); return
    print("M13_WEAPON_LOADOUT_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
