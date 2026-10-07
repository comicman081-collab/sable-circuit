extends SceneTree

const FLOW_SCENE := preload("res://scenes/bootstrap/GameFlow.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _check(FileAccess.file_exists("res://data/story/chapter_01.json"), "chapter 1 scenario data exists")
    _check(FileAccess.file_exists("res://data/missions/MIS_CH01_01.json"), "chapter 1 mission graph exists")

    var mission = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/MIS_CH01_01.json"))
    _check(mission is Dictionary, "mission graph parses")
    if mission is Dictionary:
        var route: Array = mission.get("main_route", [])
        var optional: Array = mission.get("optional_rooms", [])
        _check(route.size() == 6, "main story route has exactly 6 ordered rooms")
        _check(optional.size() == 2, "mission has exactly 2 optional rooms")
        var expected := ["EVENT", "COMBAT", "RESEARCH", "ELITE", "BOSS", "EXTRACTION"]
        var actual: Array[String] = []
        for room_variant in route:
            var room: Dictionary = room_variant
            actual.append(str(room.get("type", "")))
        _check(actual == expected, "story room types follow authored scenario order")

    var flow := FLOW_SCENE.instantiate() as GameFlow
    root.add_child(flow)
    await process_frame
    _check(flow.debug_state() == "TITLE", "game boots to title, not combat arena")
    _check(flow.current_view is TitleScreen, "title screen is active view")

    var title := flow.current_view as TitleScreen
    title.debug_start()
    await process_frame
    _check(flow.debug_state() == "BASE", "title enters operations base lobby")
    _check(flow.current_view is BaseLobby, "base lobby scene is active")

    var lobby := flow.current_view as BaseLobby
    lobby.debug_select_mission()
    await process_frame
    _check(flow.debug_state() == "BRIEFING", "mission selection opens story briefing")
    _check(flow.current_view is BriefingScreen, "briefing scene is active")

    var briefing := flow.current_view as BriefingScreen
    briefing.debug_complete_briefing()
    briefing.debug_deploy()
    await process_frame
    _check(flow.debug_state() == "STAGE_01", "briefing deploys chapter 1 stage")
    _check(flow.current_view is StoryStage01, "authored StoryStage01 scene is active")

    var stage := flow.current_view as StoryStage01
    _check(stage.debug_route_count() == 6, "runtime stage loaded six main story rooms")
    _check(stage.debug_optional_count() == 2, "runtime stage loaded two optional rooms")
    _check(stage.squad.operators.size() == 3, "story stage deploys all three animated operators")
    # The continuous map is walkable end to end; progression is gated by the
    # ordered objectives. Standing on later objectives must not complete them.
    var runner := stage.squad.get_active_operator()
    var step_before := stage.current_step
    var bounds := runner.movement_bounds
    var last_room: Dictionary = stage.main_route[-1]
    _check(bounds.has_point(Vector2(float(last_room.x), float(last_room.y))), "continuous map lets the squad walk to every authored room")
    for later_index in [2, 5]:
        var later: Dictionary = stage.main_route[later_index]
        runner.global_position = stage.constrain_battle_position(Vector2(float(later.x), float(later.y)))
        stage.call("_handle_interaction", runner)
        await process_frame
    _check(stage.current_step == step_before, "interacting at later objectives cannot skip the current room")
    _check(not bool(stage.get("_ledger_recovered")), "later research room cannot be claimed early")
    _check(not bool(stage.get("_mission_ended")), "early extraction marker cannot end the operation")
    stage.debug_advance_step()
    await process_frame
    _check(stage.current_step == step_before + 1, "story completion advances exactly one ordered room")

    var summary := stage.debug_finish()
    _check(summary.get("ledger_recovered", false), "stage result secures story-critical ledger")
    _check(summary.get("carrier_fragment", false), "optional research reward can be secured")
    flow.show_results(summary)
    await process_frame
    _check(flow.debug_state() == "RESULTS", "stage completion opens result debrief")
    _check(flow.current_view is MissionResults, "mission result scene is active")

    var results := flow.current_view as MissionResults
    results.debug_return()
    await process_frame
    _check(flow.debug_state() == "BASE", "result debrief returns to operations base")

    flow.queue_free()
    await process_frame

    if failures.is_empty():
        print("M2_STORY_FLOW_SMOKE: PASS")
        quit(0)
        return
    print("M2_STORY_FLOW_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
