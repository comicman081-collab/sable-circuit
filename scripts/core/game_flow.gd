extends Node
class_name GameFlow

const TITLE_SCENE := preload("res://scenes/ui/TitleScreen.tscn")
const LOBBY_SCENE := preload("res://scenes/base/BaseLobby.tscn")
const BRIEFING_SCENE := preload("res://scenes/story/BriefingScreen.tscn")
const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const RESULTS_SCENE := preload("res://scenes/ui/MissionResults.tscn")
const ASTER_STATIC_PRE_GATE_PREVIEW_SCENE := preload("res://scenes/qa/AsterStaticPreGatePreview.tscn")

var current_state := "BOOT"
var current_view: Node = null
var last_mission_summary: Dictionary = {}
var last_run_contract: Dictionary = {}
var campaign: CampaignProgression
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
const DeployWarmer := preload("res://scripts/core/deploy_warmer.gd")
var selected_mission_id := ""
var persist_campaign := true
var music: Node

func _ready() -> void:
    add_to_group("game_flow")
    music = preload("res://scripts/audio/demo_music.gd").new()
    music.name = "DemoMusic"
    add_child(music)
    campaign = CampaignProgression.new(persist_campaign and DisplayServer.get_name() != "headless")
    show_title()
    for argument in OS.get_cmdline_user_args():
        if argument.begins_with("--battle-stage="):
            call_deferred("open_battle_preview", int(argument.get_slice("=", 1)))
        elif argument == "--stage1":
            call_deferred("deploy_stage_01")

# What the next deploy loads is decoded behind the menus (see DeployWarmer), so DEPLOY
# does not wait on it. Web builds decode on the main thread: not during the intro video
# or on the title screen.
func _process(_delta: float) -> void:
    if OS.has_feature("web") and current_state in ["TITLE", "INTRO"]: return
    DeployWarmer.pump()

func _exit_tree() -> void:
    DeployWarmer.finish()

func show_title() -> void:
    var view := _replace_view(TITLE_SCENE,"TITLE") as TitleScreen
    view.start_requested.connect(enter_base)
    view.battle_requested.connect(open_battle_preview)
    view.mission_requested.connect(open_briefing)
    view.intro_requested.connect(show_intro)
    DeployWarmer.release()
    DeployWarmer.request_robots(MissionCatalog.recommended(campaign.cleared_missions))

func show_intro(continue_to_base: bool = true) -> void:
    if is_instance_valid(current_view):
        remove_child(current_view)
        current_view.queue_free()
    var view := Control.new()
    view.set_script(preload("res://scripts/ui/demo_intro.gd"))
    current_view = view
    current_state = "INTRO"
    music.select_state("INTRO")
    view.completed.connect(enter_base if continue_to_base else show_title)
    add_child(view)

func open_battle_preview(stage_number: int) -> void:
    if current_view != null and is_instance_valid(current_view):
        remove_child(current_view)
        current_view.queue_free()
    var view := STAGE_SCENE.instantiate() as StoryStage01
    # Only integrated operations can be previewed; a pending one has no plates.
    view.mission_id = "MIS_CH01_%02d" % clampi(stage_number, 1, maxi(1, MissionCatalog.playable_ids().size()))
    view.battle_preview = true
    current_view = view
    current_state = "BATTLE_PREVIEW"
    music.select_state(current_state, view.mission_id)
    add_child(view)
    # Same actors, AI, input, damage and stage scene. Preview earns no save data.
    view.return_requested.connect(show_title)
    view.stage_completed.connect(func(_summary: Dictionary) -> void: show_title())
    view.call_deferred("start_battle_preview")

func enter_base() -> void:
    var view := _replace_view(LOBBY_SCENE,"BASE") as BaseLobby
    view.configure_campaign(campaign.snapshot())
    view.mission_selected_requested.connect(open_mission_briefing)
    view.mission_requested.connect(open_briefing)
    view.title_requested.connect(show_title)
    view.upgrade_requested.connect(_on_upgrade_requested)
    view.analysis_requested.connect(_on_analysis_requested)
    view.module_equip_requested.connect(_on_module_equip_requested)
    view.weapon_cycle_requested.connect(_on_weapon_cycle_requested)
    DeployWarmer.release()
    DeployWarmer.request_robots(MissionCatalog.recommended(campaign.cleared_missions))

func open_briefing() -> void:
    open_mission_briefing(MissionCatalog.recommended(campaign.cleared_missions))

func open_mission_briefing(id: String) -> void:
    if not MissionCatalog.available(id, campaign.cleared_missions): return
    selected_mission_id = id
    var view := _replace_view(BRIEFING_SCENE,"BRIEFING", {"mission_id":id, "contract_run_id":campaign.next_run_id(), "allow_redline":RunContract.redline_available(id, campaign.cleared_missions)}) as BriefingScreen
    view.deploy_requested.connect(func() -> void: deploy_mission(id, view.selected_contract_index()))
    view.back_requested.connect(enter_base)
    DeployWarmer.request_deploy(id)

func deploy_stage_01() -> void:
    deploy_mission("MIS_CH01_01")

func deploy_mission(id: String, contract_index: int = 0) -> void:
    if not MissionCatalog.available(id, campaign.cleared_missions): return
    selected_mission_id = id
    # Room art, collision, encounters and briefing must agree before _ready.
    var view := _replace_view(STAGE_SCENE,"STAGE_" + id.right(2), {"mission_id":id}) as StoryStage01
    var run_id := campaign.issue_run_id("CH01")
    var snapshot := campaign.snapshot()
    last_run_contract = RunContract.build(run_id)
    var choices := RunContract.offers(run_id, id)
    if contract_index >= 0 and contract_index < choices.size(): last_run_contract = choices[contract_index]
    elif contract_index == 3 and RunContract.redline_available(id, campaign.cleared_missions): last_run_contract = RunContract.redline(run_id)
    last_run_contract["mission_id"] = id
    view.configure_campaign(snapshot,run_id,last_run_contract)
    _inject_weapon_loadouts(view,snapshot)
    view.stage_completed.connect(show_results)

func _inject_weapon_loadouts(view: StoryStage01, snapshot: Dictionary) -> void:
    if view==null or view.squad==null: return
    var damage_multiplier:=clampf(float(snapshot.get("damage_multiplier",1.0)),1.0,2.0)
    var modules:Dictionary=snapshot.get("equipped_modules",{})
    var weapons:Dictionary=snapshot.get("equipped_weapons",{})
    for actor in view.squad.operators:
        actor.apply_campaign_modifiers({
            "damage_multiplier":damage_multiplier,
            "module_id":str(modules.get(actor.operator_id,"")),
            "weapon_id":str(weapons.get(actor.operator_id,""))
        })

func show_results(summary: Dictionary) -> void:
    last_mission_summary=summary.duplicate(true)
    var transaction:=campaign.commit_mission(last_mission_summary)
    last_mission_summary["campaign_transaction"]=transaction
    last_mission_summary["campaign"]=campaign.snapshot()
    var view:=_replace_view(RESULTS_SCENE,"RESULTS") as MissionResults
    view.configure(last_mission_summary)
    view.return_requested.connect(enter_base)
    view.next_mission_requested.connect(open_mission_briefing)

func _on_upgrade_requested(upgrade_id:String)->void: _refresh_base_after_action(campaign.purchase_upgrade(upgrade_id))
func _on_analysis_requested(analysis_id:String)->void: _refresh_base_after_action(campaign.analyze_intel(analysis_id))
func _on_module_equip_requested(operator_id:String,module_id:String)->void: _refresh_base_after_action(campaign.equip_module(operator_id,module_id))
func _on_weapon_cycle_requested(operator_id:String)->void: _refresh_base_after_action(campaign.cycle_weapon(operator_id))
func _refresh_base_after_action(result:Dictionary)->void:
    if current_view is BaseLobby: (current_view as BaseLobby).refresh_campaign(campaign.snapshot(),result)

func _replace_view(scene:PackedScene,next_state:String, properties:Dictionary = {})->Node:
    if current_view!=null and is_instance_valid(current_view): remove_child(current_view); current_view.queue_free()
    current_view=scene.instantiate()
    for key: String in properties: current_view.set(key, properties[key])
    current_state=next_state
    music.select_state(next_state, str(properties.get("mission_id", "")))
    add_child(current_view)
    return current_view

func debug_state()->String: return current_state
func debug_enter_base()->void: enter_base()
func debug_open_briefing()->void: open_briefing()
func debug_deploy_stage()->void: deploy_stage_01()
func debug_open_aster_static_pre_gate_preview()->void:
    _replace_view(ASTER_STATIC_PRE_GATE_PREVIEW_SCENE,"QA_ASTER_STATIC_PRE_GATE")
func debug_return_base()->void: enter_base()
func debug_campaign_snapshot()->Dictionary: return campaign.snapshot() if campaign!=null else {}
func debug_last_run_contract()->Dictionary: return last_run_contract.duplicate(true)
func debug_show_results()->void:
    show_results({"mission_id":"MIS_CH01_01","chapter_id":"CH01","transaction_id":"DEBUG-M2-RESULT","outcome":"EXTRACTED","ledger_recovered":true,"field_supplies":true,"carrier_fragment":true,"secured_research":220,"secured_salvage":2,"secured_fragments":1,"secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1},"secured_rewards":220,"lost_unsecured":0,"lost_intel_samples":0,"extraction_depth":6})
func debug_purchase(upgrade_id:String)->Dictionary:
    if campaign==null: return {"success":false,"reason":"NO_CAMPAIGN"}
    var result:=campaign.purchase_upgrade(upgrade_id); _refresh_base_after_action(result); return result
func debug_analyze(analysis_id:String)->Dictionary:
    if campaign==null: return {"success":false,"reason":"NO_CAMPAIGN"}
    var result:=campaign.analyze_intel(analysis_id); _refresh_base_after_action(result); return result
func debug_equip(operator_id:String,module_id:String)->Dictionary:
    if campaign==null: return {"success":false,"reason":"NO_CAMPAIGN"}
    var result:=campaign.equip_module(operator_id,module_id); _refresh_base_after_action(result); return result
func debug_cycle_weapon(operator_id:String)->Dictionary:
    if campaign==null: return {"success":false,"reason":"NO_CAMPAIGN"}
    var result:=campaign.cycle_weapon(operator_id); _refresh_base_after_action(result); return result
