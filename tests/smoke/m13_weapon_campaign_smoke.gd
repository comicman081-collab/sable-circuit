extends SceneTree

var failures:Array[String]=[]

func _init()->void: call_deferred("_run")

func _run()->void:
    var progression:=CampaignProgression.new(false)
    var initial:=progression.snapshot(); var unlocked:Array=initial.get("unlocked_weapons",[]); var equipped:Dictionary=initial.get("equipped_weapons",{})
    _check(int(initial.get("schema_version",0))==CampaignProgression.SAVE_SCHEMA_VERSION,"current save schema")
    _check(unlocked.size()==3,"exactly three default weapons unlocked")
    _check(str(equipped.get("CHR_PROTO_01",""))=="WPN_AR_COIL_01","ASTER default weapon")
    _check(str(equipped.get("CHR_PROTO_02",""))=="WPN_SHOTGUN_MAG_01","ROOK default weapon")
    _check(str(equipped.get("CHR_PROTO_03",""))=="WPN_SMG_SENSOR_01","MICA default weapon")
    var locked:=progression.equip_weapon("CHR_PROTO_03","WPN_SPECIAL_ARC_01")
    _check(not bool(locked.get("success",true)) and str(locked.get("reason",""))=="WEAPON_LOCKED","special locked early")

    progression.commit_mission({"transaction_id":"M13-CAMPAIGN-SEED","outcome":"EXTRACTED","secured_research":1200,"secured_salvage":10,"secured_fragments":3,"secured_intel":{"ANCHOR":1}})
    _check(bool(progression.purchase_upgrade("ARMORY_CALIBRATION").get("success",false)),"Armory L1 purchase")
    _check((progression.snapshot().get("unlocked_weapons",[]) as Array).has("WPN_AR_BURST_02"),"burst unlock at L1")
    var incompatible:=progression.equip_weapon("CHR_PROTO_02","WPN_AR_BURST_02")
    _check(not bool(incompatible.get("success",true)) and str(incompatible.get("reason",""))=="WEAPON_INCOMPATIBLE","incompatible weapon rejected")
    _check(bool(progression.equip_weapon("CHR_PROTO_01","WPN_AR_BURST_02").get("success",false)),"ASTER equips burst")

    _check(bool(progression.purchase_upgrade("ARMORY_CALIBRATION").get("success",false)),"Armory L2 purchase")
    _check((progression.snapshot().get("unlocked_weapons",[]) as Array).has("WPN_LMG_HELIX_01"),"LMG unlock at L2")
    var choices:=WeaponRegistry.compatible_weapons("CHR_PROTO_01",progression.snapshot().get("unlocked_weapons",[]))
    var cycle:=progression.cycle_weapon("CHR_PROTO_01")
    _check(bool(cycle.get("success",false)) and choices.has(str(cycle.get("weapon_id",""))),"weapon cycle returns compatible unlocked choice")

    _check(bool(progression.analyze_intel("ANL_ANCHOR_SIGNAL_MODEL").get("success",false)),"Anchor analysis")
    _check((progression.snapshot().get("unlocked_weapons",[]) as Array).has("WPN_SPECIAL_ARC_01"),"special unlock from analysis")
    _check(bool(progression.equip_weapon("CHR_PROTO_03","WPN_SPECIAL_ARC_01").get("success",false)),"MICA equips special")

    _finish()

func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)
func _finish()->void:
    if failures.is_empty(): print("M13_WEAPON_CAMPAIGN_SMOKE: PASS"); quit(0); return
    print("M13_WEAPON_CAMPAIGN_SMOKE: FAIL (%d)"%failures.size()); quit(1)
