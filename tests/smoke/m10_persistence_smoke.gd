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

    _check(int(after.get("schema_version",0))==2,"M10 snapshot writes schema version 2")
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

    # Legacy M8/M9 save migration: those saves predate intel/module fields and
    # schema_version. M10 must preserve their campaign currencies/upgrades while
    # initializing every new discovery/loadout field to a safe empty value.
    restored.debug_reset()
    _write_save({
        "research_value":321,
        "salvage":4,
        "signal_fragments":2,
        "armory_level":2,
        "lab_level":1,
        "completed_runs":7,
        "extracted_runs":5,
        "wiped_runs":2,
        "run_serial":9,
        "committed_run_ids":["LEGACY-RUN-001"]
    })
    var migrated := CampaignProgression.new(true)
    var migrated_snapshot := migrated.snapshot()
    _check(int(migrated_snapshot.get("research_value",0))==321 and int(migrated_snapshot.get("salvage",0))==4,"legacy campaign inventory migrates without reset")
    _check(int(migrated_snapshot.get("armory_level",0))==2 and int(migrated_snapshot.get("lab_level",0))==1,"legacy facility levels migrate without reset")
    _check((migrated_snapshot.get("intel_samples",{}) as Dictionary)=={"SECURITY":0,"ABERRANT":0,"ANCHOR":0},"legacy save initializes M10 intel inventory safely")
    _check((migrated_snapshot.get("analyzed_intel",[]) as Array).is_empty(),"legacy save initializes analysis ledger empty")
    _check((migrated_snapshot.get("unlocked_modules",[]) as Array).is_empty(),"legacy save initializes module unlocks empty")
    var migrated_equipped:Dictionary=migrated_snapshot.get("equipped_modules",{})
    _check(str(migrated_equipped.get("CHR_PROTO_01",""))=="" and str(migrated_equipped.get("CHR_PROTO_02",""))=="" and str(migrated_equipped.get("CHR_PROTO_03",""))=="","legacy save initializes all operator loadouts empty")

    var legacy_duplicate:=migrated.commit_mission({"transaction_id":"LEGACY-RUN-001","outcome":"EXTRACTED","secured_research":999})
    _check(bool(legacy_duplicate.get("duplicate",false)),"legacy committed-run ledger still blocks duplicate rewards after migration")

    # Tampered/inconsistent M10 data must not grant locked modules or allow a
    # module to jump to another operator simply because it appears in JSON.
    migrated.debug_reset()
    _write_save({
        "schema_version":2,
        "research_value":50,
        "intel_samples":{"SECURITY":0,"ABERRANT":0,"ANCHOR":0},
        "analyzed_intel":["ANL_SECURITY_ARC_GAP"],
        "unlocked_modules":["MOD_PRISM_FOCUS"],
        "unlocked_weaknesses":["SECURITY_ARC_GAP"],
        "equipped_modules":{
            "CHR_PROTO_01":"MOD_PRISM_FOCUS",
            "CHR_PROTO_02":"MOD_PRISM_FOCUS",
            "CHR_PROTO_03":"MOD_SENSOR_ARRAY"
        },
        "committed_run_ids":[]
    })
    var sanitized := CampaignProgression.new(true)
    var sanitized_snapshot:=sanitized.snapshot()
    var sanitized_equipped:Dictionary=sanitized_snapshot.get("equipped_modules",{})
    _check(str(sanitized_equipped.get("CHR_PROTO_01",""))=="MOD_PRISM_FOCUS","valid unlocked module survives save sanitation")
    _check(str(sanitized_equipped.get("CHR_PROTO_02",""))=="","cross-operator module assignment is removed on load")
    _check(str(sanitized_equipped.get("CHR_PROTO_03",""))=="","locked module assignment is removed on load")

    sanitized.debug_reset()
    _finish()

func _write_save(payload:Dictionary)->void:
    var file:=FileAccess.open(CampaignProgression.SAVE_PATH,FileAccess.WRITE)
    if file==null:
        _check(false,"test can open CampaignProgression save path")
        return
    file.store_string(JSON.stringify(payload))
    file=null

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
