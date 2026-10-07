extends SceneTree
## Negative check for the geometry smoke's shared-plate rule: with the mission
## "plates" rows dropped in memory, the same comparison must flag every shared plate.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const MOOD := preload("res://scripts/missions/site7_mood.gd")

func _init() -> void: call_deferred("run")

func run() -> void:
    MOOD.abyss("MIS_CH01_03")
    for id in ["MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05"]:
        (MOOD._mood.missions[id] as Dictionary).erase("plates")
    var shared := {}
    for id in ["MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05"]:
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = id
        stage.battle_preview = true
        root.add_child(stage)
        for i in 5: await process_frame
        var art := stage.get_node("RoomArtLayer")
        for room: Dictionary in stage.main_route + stage.optional_rooms:
            var asset := str(art.get_room_plate(str(room.id)).get_meta("asset", ""))
            var rows: Array = shared.get(asset, [])
            rows.append({"grade": art.call("_room_grade", str(room.id)), "lights": JSON.stringify([MOOD.plate_lights(asset, id), MOOD.plate_fill(asset, id)])})
            shared[asset] = rows
        stage.queue_free()
        for i in 3: await process_frame
    var flagged := 0
    var pairs := 0
    for asset: String in shared:
        var rows: Array = shared[asset]
        for i in range(rows.size()):
            for j in range(i + 1, rows.size()):
                pairs += 1
                var ga: Vector4 = rows[i].grade
                var gb: Vector4 = rows[j].grade
                if not (Vector3(ga.x - gb.x, ga.y - gb.y, ga.z - gb.z).length() >= 0.05 and rows[i].lights != rows[j].lights): flagged += 1
    print("NEGATIVE_SHARED_LIGHT flagged %d of %d pairs" % [flagged, pairs])
    quit(0 if flagged == pairs else 1)
