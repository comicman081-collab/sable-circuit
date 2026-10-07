extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var progression := CampaignProgression.new(false)
    var empty := progression.snapshot()
    _check(int(empty.get("research_value",-1))==0,"M8 campaign starts with zero research")
    _check(int(empty.get("salvage",-1))==0,"M8 campaign starts with zero salvage")
    _check(int(empty.get("signal_fragments",-1))==0,"M8 campaign starts with zero signal fragments")

    var first:=progression.commit_mission({"transaction_id":"TEST-EXTRACT-1","outcome":"EXTRACTED","secured_research":220,"secured_salvage":2,"secured_fragments":1})
    _check(bool(first.get("committed",false)),"extracted run commits exactly once")
    var after_first:=progression.snapshot()
    _check(int(after_first.get("research_value",0))==220,"extraction deposits secured research")
    _check(int(after_first.get("salvage",0))==2,"extraction deposits secured salvage")
    _check(int(after_first.get("signal_fragments",0))==1,"extraction deposits secured signal fragment")

    var duplicate:=progression.commit_mission({"transaction_id":"TEST-EXTRACT-1","outcome":"EXTRACTED","secured_research":220,"secured_salvage":2,"secured_fragments":1})
    _check(bool(duplicate.get("duplicate",false)) and not bool(duplicate.get("committed",true)),"mission transaction is idempotent")
    _check(int(progression.snapshot().get("research_value",0))==220,"duplicate result cannot double-credit research")

    var armory:=progression.purchase_upgrade("ARMORY_CALIBRATION")
    _check(bool(armory.get("success",false)),"ARMORY calibration purchases with secured resources")
    var after_armory:=progression.snapshot()
    _check(int(after_armory.get("armory_level",0))==1,"ARMORY reaches level 1")
    _check(int(after_armory.get("research_value",0))==80 and int(after_armory.get("salvage",0))==1,"ARMORY cost is deducted authoritatively")
    _check(is_equal_approx(float(after_armory.get("damage_multiplier",0.0)),1.08),"ARMORY level 1 grants +8 percent projectile damage")

    progression.commit_mission({"transaction_id":"TEST-EXTRACT-2","outcome":"EXTRACTED","secured_research":120})
    var lab:=progression.purchase_upgrade("LAB_SIGNAL_ANALYSIS")
    _check(bool(lab.get("success",false)),"LAB analysis purchases with research and signal fragment")
    var after_lab:=progression.snapshot()
    _check(int(after_lab.get("lab_level",0))==1,"LAB reaches level 1")
    _check(int(after_lab.get("research_value",0))==100 and int(after_lab.get("signal_fragments",-1))==0,"LAB cost is deducted authoritatively")
    _check(is_equal_approx(float(after_lab.get("research_multiplier",0.0)),1.12),"LAB level 1 grants +12 percent secured research")
    var blocked_lab:=progression.purchase_upgrade("LAB_SIGNAL_ANALYSIS")
    _check(not bool(blocked_lab.get("success",true)) and str(blocked_lab.get("reason",""))=="INSUFFICIENT_RESOURCES","upgrade purchase cannot drive campaign currency negative")

    var stage:=STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage); current_scene=stage; await _frames(2)
    stage.configure_campaign({"damage_multiplier":1.08,"research_multiplier":1.12},"TEST-STAGE-1")
    await process_frame
    _check(stage.squad.operators.size()==3,"M8 stage retains three-operator squad")
    for actor in stage.squad.operators:
        _check(is_equal_approx(actor.debug_campaign_damage_multiplier(),1.08),"%s receives ARMORY damage multiplier"%actor.display_name)

    stage.debug_seed_cargo(115,85,2,1,true,5)
    var cargo_text:=stage.hud.debug_cargo_text()
    _check("R 115" in cargo_text and "+HV 085" in cargo_text and "S 02" in cargo_text and "F 01" in cargo_text,"HUD exposes common/high-value/salvage/fragment cargo")
    var extracted:=stage.debug_extraction_summary("R05_CORE")
    _check(str(extracted.get("outcome",""))=="EXTRACTED","M8 can resolve deliberate extraction")
    _check(bool(extracted.get("early_extraction",false)),"depth 5 extraction is marked early")
    _check(int(extracted.get("secured_research",0))==224,"LAB multiplier applies to all research secured by extraction")
    _check(int(extracted.get("secured_salvage",0))==2,"extraction secures all salvage")
    _check(int(extracted.get("secured_fragments",0))==1,"extraction secures signal fragment")
    _check(int(extracted.get("lost_unsecured",-1))==0,"deliberate extraction loses no cargo")
    _check(bool(extracted.get("carrier_fragment_secured",false)),"results distinguish found signal fragment from secured fragment")

    var wiped:=stage.debug_wipe_summary()
    _check(str(wiped.get("outcome",""))=="WIPED","M8 can resolve squad wipe")
    _check(int(wiped.get("secured_research",0))==64,"wipe recovers half common research then applies LAB multiplier")
    _check(int(wiped.get("secured_salvage",0))==1,"wipe recovers half common salvage")
    _check(int(wiped.get("secured_fragments",-1))==0,"wipe loses unsecured signal fragment")
    _check(int(wiped.get("lost_unsecured",0))==143,"wipe loses high-value research plus unrecovered common half")
    _check(bool(wiped.get("ledger_recovered",false)) and bool(wiped.get("ledger_retained_on_wipe",false)),"story-critical ledger survives wipe")
    _check(not bool(wiped.get("carrier_fragment_secured",true)),"found signal fragment is not falsely reported as secured after wipe")

    # Data-authoritative extraction windows: complete the actual authored checkpoint
    # rows in order and require each one to stop the route until the player chooses.
    stage.current_step=2; stage.call("_complete_step")
    _check(stage.debug_extraction_active(),"Archive Annex actual node opens extraction decision gate")
    _check(stage.hud.debug_extraction_visible(),"HUD makes Archive extraction decision visible")
    stage.debug_continue_extraction(); _check(stage.current_step==3,"continue resumes route at Containment Junction")
    stage.call("_complete_step")
    _check(stage.debug_extraction_active(),"Containment Junction actual node opens extraction decision gate")
    stage.debug_continue_extraction(); _check(stage.current_step==4,"continue resumes route at Core C")
    stage.call("_complete_step")
    _check(stage.debug_extraction_active(),"Core C actual node opens extraction decision gate")

    var stage_contract:=stage.debug_campaign_contract(); var offers:Array=stage_contract.get("extraction_offer_ids",[])
    _check(offers==["R03_ARCHIVE","R04_CONTAINMENT","R05_CORE"],"M8 extraction IDs match authored mission data")
    _check(is_equal_approx(float(stage_contract.get("wipe_common_retain_ratio",0.0)),0.5),"wipe common-cargo retain ratio is frozen at 50 percent")
    _check(bool(stage_contract.get("high_value_lost_on_wipe",false)),"high-value research remains risk cargo until extraction")
    _check(bool(stage_contract.get("signal_fragments_lost_on_wipe",false)),"signal fragments remain risk cargo until extraction")
    _check(bool(stage_contract.get("ledger_retained_on_wipe",false)),"story progression is not erased by economic wipe")

    stage.queue_free(); await process_frame
    _finish()

func _frames(count:int)->void:
    for _i in range(count): await process_frame
func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)
func _finish()->void:
    if failures.is_empty(): print("M8_EXTRACTION_PROGRESSION_SMOKE: PASS"); quit(0); return
    print("M8_EXTRACTION_PROGRESSION_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
