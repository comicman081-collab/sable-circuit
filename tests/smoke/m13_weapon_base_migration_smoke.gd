extends SceneTree

var failures:Array[String]=[]

func _init()->void: call_deferred("_run")

func _run()->void:
    var progression:=CampaignProgression.new(false)
    progression.commit_mission({"transaction_id":"M13-BASE-SEED","outcome":"EXTRACTED","secured_research":900,"secured_salvage":5,"secured_fragments":1})
    progression.purchase_upgrade("ARMORY_CALIBRATION")
    var base:=BaseLobby.new(); root.add_child(base); base.configure_campaign(progression.snapshot()); await _frames(3)
    var emitted:=""; base.weapon_cycle_requested.connect(func(operator_id:String)->void: emitted=operator_id)
    var button:=base.find_child("WeaponCycle_CHR_PROTO_01",true,false) as Button
    _check(button!=null,"ASTER weapon cycle button exists")
    if button!=null:
        _check(not button.disabled,"ASTER weapon cycle button enabled after Armory L1")
        button.emit_signal("pressed")
    _check(emitted=="CHR_PROTO_01","actual Base weapon button emits ASTER ID")
    var contract:=base.debug_m13_weapon_contract()
    _check((contract.get("weapon_catalog",[]) as Array).size()==6,"Base receives six weapon specs")
    base.queue_free(); await process_frame

    var persistent:=CampaignProgression.new(true); persistent.debug_reset()
    _write_save({"schema_version":2,"research_value":50,"armory_level":1,"lab_level":0,"analyzed_intel":[],"unlocked_modules":[],"unlocked_weaknesses":[],"equipped_modules":{},"committed_run_ids":[]})
    var migrated:=CampaignProgression.new(true); var snapshot:=migrated.snapshot(); var equipped:Dictionary=snapshot.get("equipped_weapons",{})
    _check(int(snapshot.get("schema_version",0))==3,"v2 save migrates to schema3")
    _check(str(equipped.get("CHR_PROTO_01",""))=="WPN_AR_COIL_01","v2 ASTER safe default")
    _check(str(equipped.get("CHR_PROTO_02",""))=="WPN_SHOTGUN_MAG_01","v2 ROOK safe default")
    _check(str(equipped.get("CHR_PROTO_03",""))=="WPN_SMG_SENSOR_01","v2 MICA safe default")
    _check((snapshot.get("unlocked_weapons",[]) as Array).has("WPN_AR_BURST_02"),"v2 Armory L1 derives burst unlock")
    migrated.debug_reset()
    _finish()

func _write_save(payload:Dictionary)->void:
    var file:=FileAccess.open(CampaignProgression.SAVE_PATH,FileAccess.WRITE)
    if file==null: _check(false,"migration test opens save"); return
    file.store_string(JSON.stringify(payload)); file=null
func _frames(count:int)->void:
    for _i in range(count): await process_frame
func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)
func _finish()->void:
    if failures.is_empty(): print("M13_WEAPON_BASE_MIGRATION_SMOKE: PASS"); quit(0); return
    print("M13_WEAPON_BASE_MIGRATION_SMOKE: FAIL (%d)"%failures.size()); quit(1)
