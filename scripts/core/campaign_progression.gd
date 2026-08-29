extends RefCounted
class_name CampaignProgression

const SAVE_PATH := "user://campaign_progression_v1.json"
const INTEL_PATH := "res://data/progression/intel_discoveries.json"
const SAVE_SCHEMA_VERSION := 3
const MAX_UPGRADE_LEVEL := 3
const INTEL_KEYS := ["SECURITY", "ABERRANT", "ANCHOR"]
const OPERATOR_IDS := ["CHR_PROTO_01", "CHR_PROTO_02", "CHR_PROTO_03"]
const DEFAULT_WEAPONS := {
    "CHR_PROTO_01":"WPN_AR_COIL_01",
    "CHR_PROTO_02":"WPN_SHOTGUN_MAG_01",
    "CHR_PROTO_03":"WPN_SMG_SENSOR_01"
}

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
var intel_samples: Dictionary = {"SECURITY": 0, "ABERRANT": 0, "ANCHOR": 0}
var equipped_modules: Dictionary = {"CHR_PROTO_01": "", "CHR_PROTO_02": "", "CHR_PROTO_03": ""}
var equipped_weapons: Dictionary = DEFAULT_WEAPONS.duplicate(true)

var _analyzed_intel: Array[String] = []
var _unlocked_modules: Array[String] = []
var _unlocked_weaknesses: Array[String] = []
var _unlocked_weapons: Array[String] = []
var _committed_run_ids: Array[String] = []
var _persistence_enabled := true
var _discovery_cache: Array[Dictionary] = []

func _init(enable_persistence: bool = true) -> void:
    _persistence_enabled = enable_persistence
    _load_discoveries()
    _sync_weapon_unlocks()
    if _persistence_enabled:
        _load()
    else:
        _sanitize_weapon_loadouts({})

func issue_run_id(chapter_id: String = "CH01") -> String:
    run_serial += 1
    _save()
    return "%s-RUN-%06d" % [chapter_id, run_serial]

func commit_mission(summary: Dictionary) -> Dictionary:
    var run_id := str(summary.get("transaction_id", summary.get("run_id", "")))
    if run_id.is_empty():
        run_id = "LEGACY-%06d" % (completed_runs + 1)
    if _committed_run_ids.has(run_id):
        return {"committed":false,"duplicate":true,"run_id":run_id,"campaign":snapshot()}
    var secured_research:=maxi(0,int(summary.get("secured_research",summary.get("secured_rewards",0))))
    var secured_salvage:=maxi(0,int(summary.get("secured_salvage",0)))
    var secured_fragments:=maxi(0,int(summary.get("secured_fragments",0)))
    var secured_intel:Dictionary=_sanitize_intel(summary.get("secured_intel",{}))
    var outcome:=str(summary.get("outcome","EXTRACTED")).to_upper()
    research_value+=secured_research; salvage+=secured_salvage; signal_fragments+=secured_fragments
    for key in INTEL_KEYS: intel_samples[key]=int(intel_samples.get(key,0))+int(secured_intel.get(key,0))
    completed_runs+=1
    if outcome=="WIPED": wiped_runs+=1
    else: extracted_runs+=1
    _append_unique(_committed_run_ids,run_id)
    while _committed_run_ids.size()>64: _committed_run_ids.pop_front()
    last_transaction={"committed":true,"duplicate":false,"run_id":run_id,"outcome":outcome,"research_delta":secured_research,"salvage_delta":secured_salvage,"fragment_delta":secured_fragments,"intel_delta":secured_intel.duplicate(true)}
    _save(); var result:=last_transaction.duplicate(true); result["campaign"]=snapshot(); return result

func purchase_upgrade(upgrade_id:String)->Dictionary:
    var id:=upgrade_id.to_upper(); var current_level:=_upgrade_level(id)
    if current_level<0: return {"success":false,"reason":"UNKNOWN_UPGRADE","upgrade_id":id,"campaign":snapshot()}
    if current_level>=MAX_UPGRADE_LEVEL: return {"success":false,"reason":"MAX_LEVEL","upgrade_id":id,"campaign":snapshot()}
    var cost:=get_upgrade_cost(id); var research_cost:=int(cost.get("research",0)); var salvage_cost:=int(cost.get("salvage",0)); var fragment_cost:=int(cost.get("fragments",0))
    if research_value<research_cost or salvage<salvage_cost or signal_fragments<fragment_cost:
        return {"success":false,"reason":"INSUFFICIENT_RESOURCES","upgrade_id":id,"cost":cost,"campaign":snapshot()}
    research_value-=research_cost; salvage-=salvage_cost; signal_fragments-=fragment_cost
    if id=="ARMORY_CALIBRATION": armory_level+=1
    elif id=="LAB_SIGNAL_ANALYSIS": lab_level+=1
    _sync_weapon_unlocks(); _save()
    return {"success":true,"reason":"PURCHASED","upgrade_id":id,"new_level":_upgrade_level(id),"cost":cost,"campaign":snapshot()}

func analyze_intel(analysis_id:String)->Dictionary:
    var id:=analysis_id.to_upper(); var definition:=get_discovery(id)
    if definition.is_empty(): return {"success":false,"reason":"UNKNOWN_ANALYSIS","analysis_id":id,"campaign":snapshot()}
    if _analyzed_intel.has(id): return {"success":false,"reason":"ALREADY_ANALYZED","analysis_id":id,"campaign":snapshot()}
    var sample_key:=str(definition.get("sample_key","")).to_upper(); var sample_cost:=maxi(0,int(definition.get("sample_cost",0))); var research_cost:=maxi(0,int(definition.get("research_cost",0)))
    if research_value<research_cost or int(intel_samples.get(sample_key,0))<sample_cost:
        return {"success":false,"reason":"INSUFFICIENT_INTEL","analysis_id":id,"research_cost":research_cost,"sample_key":sample_key,"sample_cost":sample_cost,"campaign":snapshot()}
    research_value-=research_cost; intel_samples[sample_key]=int(intel_samples.get(sample_key,0))-sample_cost; _append_unique(_analyzed_intel,id)
    var module_id:=str(definition.get("module_id","")).to_upper(); var weakness_id:=str(definition.get("weakness_id","")).to_upper()
    if not module_id.is_empty(): _append_unique(_unlocked_modules,module_id)
    if not weakness_id.is_empty(): _append_unique(_unlocked_weaknesses,weakness_id)
    _sync_weapon_unlocks(); _save()
    return {"success":true,"reason":"ANALYZED","analysis_id":id,"module_id":module_id,"weakness_id":weakness_id,"campaign":snapshot()}

func equip_module(operator_id:String,module_id:String)->Dictionary:
    var operator:=operator_id.to_upper(); var module:=module_id.to_upper()
    if not OPERATOR_IDS.has(operator): return {"success":false,"reason":"UNKNOWN_OPERATOR","operator_id":operator,"campaign":snapshot()}
    if module in ["","NONE"]:
        equipped_modules[operator]=""; _save(); return {"success":true,"reason":"UNEQUIPPED","operator_id":operator,"module_id":"","campaign":snapshot()}
    if not _unlocked_modules.has(module): return {"success":false,"reason":"MODULE_LOCKED","operator_id":operator,"module_id":module,"campaign":snapshot()}
    var definition:=get_discovery_by_module(module)
    if definition.is_empty() or str(definition.get("operator_id","")).to_upper()!=operator:
        return {"success":false,"reason":"MODULE_INCOMPATIBLE","operator_id":operator,"module_id":module,"campaign":snapshot()}
    equipped_modules[operator]=module; _save(); return {"success":true,"reason":"EQUIPPED","operator_id":operator,"module_id":module,"campaign":snapshot()}

func equip_weapon(operator_id:String,weapon_id:String)->Dictionary:
    var operator:=operator_id.to_upper(); var weapon:=weapon_id.to_upper()
    if not OPERATOR_IDS.has(operator): return {"success":false,"reason":"UNKNOWN_OPERATOR","operator_id":operator,"campaign":snapshot()}
    if WeaponRegistry.get_weapon(weapon).is_empty(): return {"success":false,"reason":"UNKNOWN_WEAPON","weapon_id":weapon,"campaign":snapshot()}
    if not _unlocked_weapons.has(weapon): return {"success":false,"reason":"WEAPON_LOCKED","operator_id":operator,"weapon_id":weapon,"campaign":snapshot()}
    if not WeaponRegistry.is_compatible(operator,weapon): return {"success":false,"reason":"WEAPON_INCOMPATIBLE","operator_id":operator,"weapon_id":weapon,"campaign":snapshot()}
    equipped_weapons[operator]=weapon; _save(); return {"success":true,"reason":"WEAPON_EQUIPPED","operator_id":operator,"weapon_id":weapon,"campaign":snapshot()}

func cycle_weapon(operator_id:String)->Dictionary:
    var operator:=operator_id.to_upper()
    if not OPERATOR_IDS.has(operator): return {"success":false,"reason":"UNKNOWN_OPERATOR","operator_id":operator,"campaign":snapshot()}
    var choices:=WeaponRegistry.compatible_weapons(operator,_unlocked_weapons)
    if choices.is_empty(): return {"success":false,"reason":"NO_COMPATIBLE_WEAPON","operator_id":operator,"campaign":snapshot()}
    var current:=str(equipped_weapons.get(operator,"")); var index:=choices.find(current); var next_index:=0 if index<0 else (index+1)%choices.size()
    return equip_weapon(operator,choices[next_index])

func get_upgrade_cost(upgrade_id:String)->Dictionary:
    var id:=upgrade_id.to_upper(); var level:=maxi(0,_upgrade_level(id))
    if id=="ARMORY_CALIBRATION": return {"research":140+level*100,"salvage":1+level,"fragments":0}
    if id=="LAB_SIGNAL_ANALYSIS": return {"research":100+level*120,"salvage":0,"fragments":1}
    return {"research":0,"salvage":0,"fragments":0}
func get_discovery(analysis_id:String)->Dictionary:
    var id:=analysis_id.to_upper()
    for row in _discovery_cache:
        if str(row.get("analysis_id","")).to_upper()==id: return row.duplicate(true)
    return {}
func get_discovery_by_module(module_id:String)->Dictionary:
    var id:=module_id.to_upper()
    for row in _discovery_cache:
        if str(row.get("module_id","")).to_upper()==id: return row.duplicate(true)
    return {}

func snapshot()->Dictionary:
    _sync_weapon_unlocks()
    return {"schema_version":SAVE_SCHEMA_VERSION,"research_value":research_value,"salvage":salvage,"signal_fragments":signal_fragments,"armory_level":armory_level,"lab_level":lab_level,"completed_runs":completed_runs,"extracted_runs":extracted_runs,"wiped_runs":wiped_runs,"damage_multiplier":1.0+float(armory_level)*0.08,"research_multiplier":1.0+float(lab_level)*0.12,"armory_cost":get_upgrade_cost("ARMORY_CALIBRATION"),"lab_cost":get_upgrade_cost("LAB_SIGNAL_ANALYSIS"),"max_upgrade_level":MAX_UPGRADE_LEVEL,"intel_samples":intel_samples.duplicate(true),"analyzed_intel":_analyzed_intel.duplicate(),"unlocked_modules":_unlocked_modules.duplicate(),"unlocked_weaknesses":_unlocked_weaknesses.duplicate(),"equipped_modules":equipped_modules.duplicate(true),"unlocked_weapons":_unlocked_weapons.duplicate(),"equipped_weapons":equipped_weapons.duplicate(true),"weapon_catalog":_weapon_ui_rows(),"discoveries":_discovery_ui_rows()}

func _weapon_ui_rows()->Array[Dictionary]:
    var out:Array[Dictionary]=[]
    for row in WeaponRegistry.get_all_weapons():
        var copy:=row.duplicate(true); var id:=str(copy.get("weapon_id","")).to_upper(); copy["unlocked"]=_unlocked_weapons.has(id); out.append(copy)
    return out
func _discovery_ui_rows()->Array[Dictionary]:
    var out:Array[Dictionary]=[]
    for row in _discovery_cache:
        var copy:=row.duplicate(true); var id:=str(copy.get("analysis_id","")).to_upper(); var sample_key:=str(copy.get("sample_key","")).to_upper(); copy["analyzed"]=_analyzed_intel.has(id); copy["module_unlocked"]=_unlocked_modules.has(str(copy.get("module_id","")).to_upper()); copy["can_analyze"]=not bool(copy["analyzed"]) and research_value>=int(copy.get("research_cost",0)) and int(intel_samples.get(sample_key,0))>=int(copy.get("sample_cost",0)); out.append(copy)
    return out
func _sync_weapon_unlocks()->void:
    for operator in OPERATOR_IDS: _append_unique(_unlocked_weapons,str(DEFAULT_WEAPONS[operator]))
    if armory_level>=1: _append_unique(_unlocked_weapons,"WPN_AR_BURST_02")
    if armory_level>=2: _append_unique(_unlocked_weapons,"WPN_LMG_HELIX_01")
    if _analyzed_intel.has("ANL_ANCHOR_SIGNAL_MODEL"): _append_unique(_unlocked_weapons,"WPN_SPECIAL_ARC_01")
func _sanitize_weapon_loadouts(saved:Dictionary)->void:
    _sync_weapon_unlocks(); equipped_weapons=DEFAULT_WEAPONS.duplicate(true)
    for operator in OPERATOR_IDS:
        var requested:=str(saved.get(operator,DEFAULT_WEAPONS[operator])).to_upper()
        if _unlocked_weapons.has(requested) and WeaponRegistry.is_compatible(operator,requested): equipped_weapons[operator]=requested
func _upgrade_level(upgrade_id:String)->int:
    if upgrade_id=="ARMORY_CALIBRATION": return armory_level
    if upgrade_id=="LAB_SIGNAL_ANALYSIS": return lab_level
    return -1
func _sanitize_intel(value:Variant)->Dictionary:
    var out:={"SECURITY":0,"ABERRANT":0,"ANCHOR":0}
    if value is Dictionary:
        for key in INTEL_KEYS: out[key]=maxi(0,int((value as Dictionary).get(key,0)))
    return out
func _load_discoveries()->void:
    _discovery_cache.clear()
    if not FileAccess.file_exists(INTEL_PATH): push_warning("CampaignProgression missing M10 intel registry"); return
    var parsed=JSON.parse_string(FileAccess.get_file_as_string(INTEL_PATH))
    if not (parsed is Dictionary): push_warning("CampaignProgression ignored malformed M10 intel registry"); return
    for row_variant in (parsed as Dictionary).get("discoveries",[]):
        if row_variant is Dictionary: _discovery_cache.append((row_variant as Dictionary).duplicate(true))
func _save()->void:
    if not _persistence_enabled: return
    var file:=FileAccess.open(SAVE_PATH,FileAccess.WRITE)
    if file==null: push_warning("CampaignProgression could not open save path"); return
    var payload:=snapshot(); payload["run_serial"]=run_serial; payload["committed_run_ids"]=_committed_run_ids.duplicate(); file.store_string(JSON.stringify(payload))
func _load()->void:
    if not FileAccess.file_exists(SAVE_PATH): _sanitize_weapon_loadouts({}); return
    var parsed=JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
    if not (parsed is Dictionary): push_warning("CampaignProgression ignored malformed save"); _sanitize_weapon_loadouts({}); return
    var data:Dictionary=parsed
    research_value=maxi(0,int(data.get("research_value",0))); salvage=maxi(0,int(data.get("salvage",0))); signal_fragments=maxi(0,int(data.get("signal_fragments",0))); armory_level=clampi(int(data.get("armory_level",0)),0,MAX_UPGRADE_LEVEL); lab_level=clampi(int(data.get("lab_level",0)),0,MAX_UPGRADE_LEVEL); completed_runs=maxi(0,int(data.get("completed_runs",0))); extracted_runs=maxi(0,int(data.get("extracted_runs",0))); wiped_runs=maxi(0,int(data.get("wiped_runs",0))); run_serial=maxi(0,int(data.get("run_serial",0))); intel_samples=_sanitize_intel(data.get("intel_samples",{}))
    _analyzed_intel.clear(); _unlocked_modules.clear(); _unlocked_weaknesses.clear(); _unlocked_weapons.clear(); _committed_run_ids.clear()
    for value in data.get("analyzed_intel",[]):
        var id:=str(value).to_upper()
        if not id.is_empty() and not get_discovery(id).is_empty(): _append_unique(_analyzed_intel,id)
    for value in data.get("unlocked_modules",[]):
        var id:=str(value).to_upper()
        if not id.is_empty() and not get_discovery_by_module(id).is_empty(): _append_unique(_unlocked_modules,id)
    for value in data.get("unlocked_weaknesses",[]):
        var id:=str(value).to_upper()
        if not id.is_empty(): _append_unique(_unlocked_weaknesses,id)
    for value in data.get("committed_run_ids",[]):
        var id:=str(value)
        if not id.is_empty(): _append_unique(_committed_run_ids,id)
    while _committed_run_ids.size()>64: _committed_run_ids.pop_front()
    equipped_modules={"CHR_PROTO_01":"","CHR_PROTO_02":"","CHR_PROTO_03":""}; var saved_modules:Dictionary=data.get("equipped_modules",{})
    for operator in OPERATOR_IDS:
        var module:=str(saved_modules.get(operator,"")).to_upper()
        if module.is_empty() or not _unlocked_modules.has(module): continue
        var definition:=get_discovery_by_module(module)
        if not definition.is_empty() and str(definition.get("operator_id","")).to_upper()==operator: equipped_modules[operator]=module
    _sync_weapon_unlocks()
    for value in data.get("unlocked_weapons",[]):
        var weapon:=str(value).to_upper()
        if not WeaponRegistry.get_weapon(weapon).is_empty(): _append_unique(_unlocked_weapons,weapon)
    _sanitize_weapon_loadouts(data.get("equipped_weapons",{}))
func _append_unique(target:Array[String],value:String)->void:
    if not target.has(value): target.append(value)
func debug_reset()->void:
    research_value=0; salvage=0; signal_fragments=0; armory_level=0; lab_level=0; completed_runs=0; extracted_runs=0; wiped_runs=0; run_serial=0; last_transaction.clear(); _analyzed_intel.clear(); _unlocked_modules.clear(); _unlocked_weaknesses.clear(); _unlocked_weapons.clear(); _committed_run_ids.clear(); intel_samples={"SECURITY":0,"ABERRANT":0,"ANCHOR":0}; equipped_modules={"CHR_PROTO_01":"","CHR_PROTO_02":"","CHR_PROTO_03":""}; equipped_weapons=DEFAULT_WEAPONS.duplicate(true); _sync_weapon_unlocks()
    if _persistence_enabled and FileAccess.file_exists(SAVE_PATH): DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
