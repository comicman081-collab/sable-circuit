extends SceneTree

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")

func _init() -> void:
    call_deferred("run")

func run() -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    stage.battle_preview = true
    root.add_child(stage)
    for i in range(6): await process_frame
    var art := stage.get_node("RoomArtLayer")
    for sprite in art.find_children("*", "Sprite2D", true, false):
        if sprite.has_meta("mood_lights"):
            print("MOOD_COUNT ", str(sprite.get_meta("asset", "")).get_file(), " ", sprite.get_meta("mood_lights"), " dropped ", sprite.get_meta("mood_lights_dropped"))
    quit(0)
