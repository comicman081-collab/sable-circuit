extends Node
class_name GameFlow

const TITLE_SCENE := preload("res://scenes/ui/TitleScreen.tscn")
const LOBBY_SCENE := preload("res://scenes/base/BaseLobby.tscn")
const BRIEFING_SCENE := preload("res://scenes/story/BriefingScreen.tscn")
const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const RESULTS_SCENE := preload("res://scenes/ui/MissionResults.tscn")

var current_state := "BOOT"
var current_view: Node = null
var last_mission_summary: Dictionary = {}
var last_run_contract: Dictionary = {}
var campaign: CampaignProgression

func _ready() -> void:
    add_to_group("game_flow")
    campaign = CampaignProgression.new(DisplayServer.get_name() != "headless")
    show_title()

func show_title() -> void:
    var view := _replace_view(TITLE_SCENE, "TITLE") as TitleScreen
    view.start_requested.connect(enter_base)

func enter_base() -> void:
    var view := _replace_view(LOBBY_SCENE, "BASE") as BaseLobby
    view.configure_campaign(campaign.snapshot())
    view.mission_requested.connect(open_briefing)
    view.title_requested.connect(show_title)
    view.upgrade_requested.connect(_on_upgrade_requested)
    view.analysis_requested.connect(_on_analysis_requested)
    view.module_equip_requested.connect(_on_module_equip_requested)

func open_briefing() -> void:
    var view := _replace_view(BRIEFING_SCENE, "BRIEFING") as BriefingScreen
    view.deploy_requested.connect(deploy_stage_01)
    view.back_requested.connect(enter_base)

func deploy_stage_01() -> void:
    var view := _replace_view(STAGE_SCENE, "STAGE_01") as StoryStage01
    var run_id := campaign.issue_run_id("CH01")
    last_run_contract = RunContract.build(run_id)
    view.configure_campaign(campaign.snapshot(), run_id, last_run_contract)
    view.stage_completed.connect(show_results)

func show_results(summary: Dictionary) -> void:
    last_mission_summary = summary.duplicate(true)
    var transaction := campaign.commit_mission(last_mission_summary)
    last_mission_summary["campaign_transaction"] = transaction
    last_mission_summary["campaign"] = campaign.snapshot()
    var view := _replace_view(RESULTS_SCENE, "RESULTS") as MissionResults
    view.configure(last_mission_summary)
    view.return_requested.connect(enter_base)

func _on_upgrade_requested(upgrade_id: String) -> void:
    _refresh_base_after_action(campaign.purchase_upgrade(upgrade_id))

func _on_analysis_requested(analysis_id: String) -> void:
    _refresh_base_after_action(campaign.analyze_intel(analysis_id))

func _on_module_equip_requested(operator_id: String, module_id: String) -> void:
    _refresh_base_after_action(campaign.equip_module(operator_id,module_id))

func _refresh_base_after_action(result: Dictionary) -> void:
    if current_view is BaseLobby:
        (current_view as BaseLobby).refresh_campaign(campaign.snapshot(), result)

func _replace_view(scene: PackedScene, next_state: String) -> Node:
    if current_view != null and is_instance_valid(current_view):
        remove_child(current_view)
        current_view.queue_free()
    current_view = scene.instantiate()
    add_child(current_view)
    current_state = next_state
    return current_view

func debug_state() -> String:
    return current_state
func debug_enter_base() -> void: enter_base()
func debug_open_briefing() -> void: open_briefing()
func debug_deploy_stage() -> void: deploy_stage_01()
func debug_return_base() -> void: enter_base()
func debug_campaign_snapshot() -> Dictionary: return campaign.snapshot() if campaign != null else {}
func debug_last_run_contract() -> Dictionary: return last_run_contract.duplicate(true)

func debug_show_results() -> void:
    show_results({
        "mission_id":"MIS_CH01_01","chapter_id":"CH01","transaction_id":"DEBUG-M2-RESULT","outcome":"EXTRACTED",
        "ledger_recovered":true,"field_supplies":true,"carrier_fragment":true,
        "secured_research":220,"secured_salvage":2,"secured_fragments":1,
        "secured_intel":{"SECURITY":2,"ABERRANT":1,"ANCHOR":1},
        "secured_rewards":220,"lost_unsecured":0,"lost_intel_samples":0,"extraction_depth":6
    })

func debug_purchase(upgrade_id: String) -> Dictionary:
    if campaign == null: return {"success":false,"reason":"NO_CAMPAIGN"}
    var result:=campaign.purchase_upgrade(upgrade_id); _refresh_base_after_action(result); return result
func debug_analyze(analysis_id: String) -> Dictionary:
    if campaign == null: return {"success":false,"reason":"NO_CAMPAIGN"}
    var result:=campaign.analyze_intel(analysis_id); _refresh_base_after_action(result); return result
func debug_equip(operator_id: String,module_id: String) -> Dictionary:
    if campaign == null: return {"success":false,"reason":"NO_CAMPAIGN"}
    var result:=campaign.equip_module(operator_id,module_id); _refresh_base_after_action(result); return result
