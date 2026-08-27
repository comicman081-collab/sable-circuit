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
