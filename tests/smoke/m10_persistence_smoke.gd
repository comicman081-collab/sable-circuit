extends SceneTree

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var first := CampaignProgression.new(true)
    first.debug_reset()
    first = CampaignProgression.new(true)

    var commit := first.commit_mission({
        "transaction_id":"M10-PERSIST-RUN",
        "outcome":"EXTRACTED",
        "secured_research":700,
        "secured_salvage":3,
        "secured_fragments":2,
        "secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1}
    })
    _check(bool(commit.get("committed",false)),"M10 persistence seed run commits")
    _check(bool(first.analyze_intel("ANL_SECURITY_ARC_GAP").get("success",false)),"M10 persistence analyzes SECURITY")
    _check(bool(first.analyze_intel("ANL_ABERRANT_JOINT_MAP").get("success",false)),"M10 persistence analyzes ABERRANT")
    _check(bool(first.analyze_intel("ANL_ANCHOR_SIGNAL_MODEL").get("success",false)),"M10 persistence analyzes ANCHOR")
    _check(bool(first.equip_module("CHR_PROTO_01","MOD_PRISM_FOCUS").get("success",false)),"M10 persistence equips ASTER")
    _check(bool(first.equip_module("CHR_PROTO_02","MOD_BREACH_LINER").get("success",false)),"M10 persistence equips ROOK")
    _check(bool(first.equip_module("CHR_PROTO_03","MOD_SENSOR_ARRAY").get("success",false)),"M10 persistence equips MICA")

    var before := first.snapshot()
    var restored := CampaignProgression.new(true)
    var after := restored.snapshot()

    _check(int(after.get("research_value",-1))==int(before.get("research_value",-2)),"research inventory survives CampaignProgression recreation")
    _check(int(after.get("salvage",-1))==int(before.get("salvage",-2)),"salvage inventory survives CampaignProgression recreation")
    _check(int(after.get("signal_fragments",-1))==int(before.get("signal_fragments",-2)),"signal inventory survives CampaignProgression recreation")
    _check((after.get("intel_samples",{}) as Dictionary)==(before.get("intel_samples",{}) as Dictionary),"intel sample inventory survives CampaignProgression recreation")
    _check((after.get("analyzed_intel",[]) as Array)==(before.get("analyzed_intel",[]) as Array),"analysis completion survives CampaignProgression recreation")
    _check((after.get("unlocked_modules",[]) as Array)==(before.get("unlocked_modules",[]) as Array),"module unlocks survive CampaignProgression recreation")
    _check((after.get("unlocked_weaknesses",[]) as Array)==(before.get("unlocked_weaknesses",[]) as Array),"weakness knowledge survives CampaignProgression recreation")
    _check((after.get("equipped_modules",{}) as Dictionary)==(before.get("equipped_modules",{}) as Dictionary),"three-operator loadout survives CampaignProgression recreation")

    var duplicate := restored.commit_mission({
        "transaction_id":"M10-PERSIST-RUN",
        "outcome":"EXTRACTED",
        "secured_research":700,
        "secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1}
    })
    _check(bool(duplicate.get("duplicate",false)) and not bool(duplicate.get("committed",true)),"persisted run-ID ledger still blocks duplicate rewards after recreation")

    restored.debug_reset()
    _finish()

func _check(condition:bool,label:String)->void:
    if condition: print("PASS: "+label)
    else: failures.append(label); push_error("FAIL: "+label)

func _finish()->void:
    if failures.is_empty():
        print("M10_PERSISTENCE_SMOKE: PASS")
        quit(0)
        return
    print("M10_PERSISTENCE_SMOKE: FAIL (%d)"%failures.size())
    for failure in failures: print(" - "+failure)
    quit(1)
