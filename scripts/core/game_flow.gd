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

func _ready() -> void:
    add_to_group("game_flow")
    show_title()

func show_title() -> void:
    var view := _replace_view(TITLE_SCENE, "TITLE") as TitleScreen
    view.start_requested.connect(enter_base)

func enter_base() -> void:
    var view := _replace_view(LOBBY_SCENE, "BASE") as BaseLobby
    view.mission_requested.connect(open_briefing)
    view.title_requested.connect(show_title)

func open_briefing() -> void:
    var view := _replace_view(BRIEFING_SCENE, "BRIEFING") as BriefingScreen
    view.deploy_requested.connect(deploy_stage_01)
    view.back_requested.connect(enter_base)

func deploy_stage_01() -> void:
    var view := _replace_view(STAGE_SCENE, "STAGE_01") as StoryStage01
    view.stage_completed.connect(show_results)

func show_results(summary: Dictionary) -> void:
    last_mission_summary = summary.duplicate(true)
    var view := _replace_view(RESULTS_SCENE, "RESULTS") as MissionResults
    view.configure(last_mission_summary)
    view.return_requested.connect(enter_base)

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

func debug_enter_base() -> void:
    enter_base()

func debug_open_briefing() -> void:
    open_briefing()

func debug_deploy_stage() -> void:
    deploy_stage_01()

func debug_show_results() -> void:
    show_results({
        "mission_id": "MIS_CH01_01",
        "chapter_id": "CH01",
        "ledger_recovered": true,
        "field_supplies": true,
        "carrier_fragment": true,
        "secured_rewards": 220
    })

func debug_return_base() -> void:
    enter_base()
