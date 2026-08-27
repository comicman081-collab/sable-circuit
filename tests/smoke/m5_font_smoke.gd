extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const FONT_PATH := "res://assets/fonts/Rajdhani-Medium.ttf"

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _check(ResourceLoader.exists(FONT_PATH), "pinned Rajdhani font imports as a Godot resource")
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    await process_frame
    await process_frame

    var hud := stage.get_node_or_null("StoryStageHUD") as StoryStageHUD
    _check(hud != null, "story HUD exists")
    _check(hud != null and hud.debug_font_source() == "bundled-rajdhani-v1.201", "story HUD selects bundled Rajdhani v1.201")

    var depth := stage.get_node_or_null("DepthPass") as Site7DepthPass
    _check(depth != null, "Site-7 2.5D depth pass loads as its authored script")
    _check(depth != null and depth.debug_room_depth_count() == 8, "Site-7 depth pass covers all eight authored environments")

    var overlay := stage.get_node_or_null("FieldOverlay/Vignette") as CinematicFieldOverlay
    _check(overlay != null, "cinematic field overlay loads")

    _check(stage.squad.operators.size() == 3, "three operators remain in M5 presentation")
    if stage.squad.operators.size() == 3:
        for actor in stage.squad.operators:
            _check(actor.get_node_or_null("GroundShadow") is OperatorGroundShadow, actor.display_name + " has contact shadow")

    stage.debug_spawn_encounter_for_step(1)
    await process_frame
    await process_frame
    var enemies := get_nodes_in_group("m3_enemies")
    _check(enemies.size() == 3, "Decon encounter still spawns three unique enemies")
    for node in enemies:
        if node is EnemyActor:
            _check(node.get_node_or_null("GroundShadow") is EnemyGroundShadow, node.enemy_id + " has contact shadow")
            _check(node.get_node_or_null("OverheadUI") is EnemyOverheadUI, node.enemy_id + " has overhead combat UI")

    stage.queue_free()
    await process_frame

    if failures.is_empty():
        print("M5_FONT_SMOKE: PASS")
        quit(0)
        return
    print("M5_FONT_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
