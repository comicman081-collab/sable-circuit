extends RefCounted
class_name CampaignProgression

const SAVE_PATH := "user://campaign_progression_v1.json"
const MAX_UPGRADE_LEVEL := 3

var research_value := 0
var salvage := 0
var signal_fragments := 0
var armory_level := 0
var lab_level := 0
var completed_runs := 0
var extracted_runs := 0
var wiped_runs := 0
var run_serial := 0
var last_transaction: Dictionary = {}

var _committed_run_ids: Array[String] = []
var _persistence_enabled := true

func _init(enable_persistence: bool = true) -> void:
    _persistence_enabled = enable_persistence
    if _persistence_enabled:
        _load()

func issue_run_id(chapter_id: String = "CH01") -> String:
    run_serial += 1
    _save()
    return "%s-RUN-%06d" % [chapter_id, run_serial]

func commit_mission(summary: Dictionary) -> Dictionary:
    var run_id := str(summary.get("transaction_id", summary.get("run_id", "")))
    if run_id.is_empty():
        run_id = "LEGACY-%06d" % (completed_runs + 1)
    if _committed_run_ids.has(run_id):
        return {
            "committed": false,
            "duplicate": true,
            "run_id": run_id,
            "campaign": snapshot()
        }

    var secured_research := maxi(0, int(summary.get("secured_research", summary.get("secured_rewards", 0))))
    var secured_salvage := maxi(0, int(summary.get("secured_salvage", 0)))
    var secured_fragments := maxi(0, int(summary.get("secured_fragments", 0)))
    var outcome := str(summary.get("outcome", "EXTRACTED")).to_upper()

    research_value += secured_research
    salvage += secured_salvage
    signal_fragments += secured_fragments
    completed_runs += 1
    if outcome == "WIPED":
        wiped_runs += 1
    else:
        extracted_runs += 1

    _committed_run_ids.append(run_id)
    while _committed_run_ids.size() > 64:
        _committed_run_ids.pop_front()

    last_transaction = {
        "committed": true,
        "duplicate": false,
        "run_id": run_id,
        "outcome": outcome,
        "research_delta": secured_research,
        "salvage_delta": secured_salvage,
        "fragment_delta": secured_fragments
    }
    _save()
    var result := last_transaction.duplicate(true)
    result["campaign"] = snapshot()
    return result

func purchase_upgrade(upgrade_id: String) -> Dictionary:
    var id := upgrade_id.to_upper()
    var current_level := _upgrade_level(id)
    if current_level < 0:
        return {"success": false, "reason": "UNKNOWN_UPGRADE", "upgrade_id": id, "campaign": snapshot()}
    if current_level >= MAX_UPGRADE_LEVEL:
        return {"success": false, "reason": "MAX_LEVEL", "upgrade_id": id, "campaign": snapshot()}

    var cost := get_upgrade_cost(id)
    var research_cost := int(cost.get("research", 0))
    var salvage_cost := int(cost.get("salvage", 0))
    var fragment_cost := int(cost.get("fragments", 0))
    if research_value < research_cost or salvage < salvage_cost or signal_fragments < fragment_cost:
        return {
            "success": false,
            "reason": "INSUFFICIENT_RESOURCES",
            "upgrade_id": id,
            "cost": cost,
            "campaign": snapshot()
        }

    research_value -= research_cost
    salvage -= salvage_cost
    signal_fragments -= fragment_cost
    if id == "ARMORY_CALIBRATION":
        armory_level += 1
    elif id == "LAB_SIGNAL_ANALYSIS":
        lab_level += 1
    _save()
    return {
        "success": true,
        "reason": "PURCHASED",
        "upgrade_id": id,
        "new_level": _upgrade_level(id),
        "cost": cost,
        "campaign": snapshot()
    }

func get_upgrade_cost(upgrade_id: String) -> Dictionary:
    var id := upgrade_id.to_upper()
    var level := maxi(0, _upgrade_level(id))
    if id == "ARMORY_CALIBRATION":
        return {"research": 140 + level * 100, "salvage": 1 + level, "fragments": 0}
    if id == "LAB_SIGNAL_ANALYSIS":
        return {"research": 100 + level * 120, "salvage": 0, "fragments": 1}
    return {"research": 0, "salvage": 0, "fragments": 0}

func snapshot() -> Dictionary:
    return {
        "research_value": research_value,
        "salvage": salvage,
        "signal_fragments": signal_fragments,
        "armory_level": armory_level,
        "lab_level": lab_level,
        "completed_runs": completed_runs,
        "extracted_runs": extracted_runs,
        "wiped_runs": wiped_runs,
        "damage_multiplier": 1.0 + float(armory_level) * 0.08,
        "research_multiplier": 1.0 + float(lab_level) * 0.12,
        "armory_cost": get_upgrade_cost("ARMORY_CALIBRATION"),
        "lab_cost": get_upgrade_cost("LAB_SIGNAL_ANALYSIS"),
        "max_upgrade_level": MAX_UPGRADE_LEVEL
    }

func _upgrade_level(upgrade_id: String) -> int:
    if upgrade_id == "ARMORY_CALIBRATION":
        return armory_level
    if upgrade_id == "LAB_SIGNAL_ANALYSIS":
        return lab_level
    return -1

func _save() -> void:
    if not _persistence_enabled:
        return
    var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    if file == null:
        push_warning("CampaignProgression could not open save path")
        return
    var payload := snapshot()
    payload["run_serial"] = run_serial
    payload["committed_run_ids"] = _committed_run_ids
    file.store_string(JSON.stringify(payload))

func _load() -> void:
    if not FileAccess.file_exists(SAVE_PATH):
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
    if not (parsed is Dictionary):
        push_warning("CampaignProgression ignored malformed save")
        return
    var data: Dictionary = parsed
    research_value = maxi(0, int(data.get("research_value", 0)))
    salvage = maxi(0, int(data.get("salvage", 0)))
    signal_fragments = maxi(0, int(data.get("signal_fragments", 0)))
    armory_level = clampi(int(data.get("armory_level", 0)), 0, MAX_UPGRADE_LEVEL)
    lab_level = clampi(int(data.get("lab_level", 0)), 0, MAX_UPGRADE_LEVEL)
    completed_runs = maxi(0, int(data.get("completed_runs", 0)))
    extracted_runs = maxi(0, int(data.get("extracted_runs", 0)))
    wiped_runs = maxi(0, int(data.get("wiped_runs", 0)))
    run_serial = maxi(0, int(data.get("run_serial", 0)))
    _committed_run_ids.clear()
    var ids: Array = data.get("committed_run_ids", [])
    for id_variant in ids:
        var id := str(id_variant)
        if not id.is_empty():
            _committed_run_ids.append(id)

func debug_reset() -> void:
    research_value = 0
    salvage = 0
    signal_fragments = 0
    armory_level = 0
    lab_level = 0
    completed_runs = 0
    extracted_runs = 0
    wiped_runs = 0
    run_serial = 0
    last_transaction.clear()
    _committed_run_ids.clear()
    if _persistence_enabled and FileAccess.file_exists(SAVE_PATH):
        DirAccess.remove_absolute(SAVE_PATH)
