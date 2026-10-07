extends SceneTree
## Native same-camera comparison of each dedicated stage-4/5 room against its S3 floor reference.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")

const BASE := {
    "MIS_CH01_04": ["S3_R06", "S3_R04", "S3_R01", "S3_R02", "S3_R05", "S3_R03", "S3_O01", "S3_O02"],
    "MIS_CH01_05": ["S3_R01", "S3_R05", "S3_R03", "S3_R04", "S3_R02", "S3_R06", "S3_O01", "S3_O02"],
}

func _initialize() -> void:
    call_deferred("run")

func _shot(path: String) -> void:
    for i in 4: await process_frame
    await RenderingServer.frame_post_draw
    var im := root.get_texture().get_image()
    assert(im.get_size() == Vector2i(1920, 1080))
    assert(im.save_png(path) == OK)
    print("STAGE4_COMPARE_CAPTURE ", path)

func run() -> void:
    var mission := ""
    var out := ""
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): mission = arg.trim_prefix("--mission=")
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
    if not BASE.has(mission) or not out.begins_with("res://.cache/"):
        quit(2)
        return
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = root.size
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(root.size)
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    stage.battle_preview = true
    root.add_child(stage)
    for i in 30: await process_frame
    stage.process_mode = Node.PROCESS_MODE_DISABLED
    for child in stage.get_children():
        if child is CanvasLayer: child.visible = false
    for group in ["m3_enemies", "sable_environment_cover"]:
        for n in get_nodes_in_group(group):
            if n is CanvasItem: (n as CanvasItem).visible = false
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    var all_sprites: Array = art.get("_sprites")
    var cam := Camera2D.new()
    cam.process_mode = Node.PROCESS_MODE_ALWAYS
    cam.zoom = Vector2.ONE
    root.add_child(cam)
    cam.make_current()
    var rooms: Array = stage.main_route + stage.optional_rooms
    var rows: Array = []
    for index in range(rooms.size()):
        var room: Dictionary = rooms[index]
        var room_id := str(room.id)
        var plate := art.get_room_plate(room_id)
        assert(plate != null)
        for sprite in all_sprites: sprite.visible = sprite == plate
        for seal in get_nodes_in_group("site7_sealed_bulkhead"): (seal as CanvasItem).visible = false
        for i in range(stage.squad.operators.size()):
            var actor: OperatorActor = stage.squad.operators[i]
            actor.global_position = plate.global_position + [Vector2(-190,110), Vector2(5,170), Vector2(200,110)][i]
            actor.velocity = Vector2.ZERO
            actor.z_as_relative = false
            actor.z_index = 3000
        cam.global_position = plate.global_position
        var new_asset := str(plate.get_meta("asset"))
        var base_id: String = BASE[mission][index]
        var base_asset := "res://assets/environments/site7_v2/stage03/%s/%s_GAME.png" % [base_id, base_id]
        var original_texture := plate.texture
        var original_material := plate.material
        var stem := "%s_%s" % [mission, room_id]
        await _shot(out + "/" + stem + "_dedicated.png")
        plate.texture = ImageTexture.create_from_image(Image.load_from_file(base_asset))
        plate.material = null
        await _shot(out + "/" + stem + "_S3_reference.png")
        plate.texture = original_texture
        plate.material = original_material
        rows.append({"room": room_id, "dedicated_asset": new_asset, "S3_reference_asset": base_asset, "camera_position": [cam.global_position.x, cam.global_position.y], "camera_zoom": 1.0})
    var manifest := FileAccess.open(out + "/capture_manifest.json", FileAccess.WRITE)
    manifest.store_string(JSON.stringify({"scene": "StoryStage01", "mission": mission, "native_capture": [1920,1080], "mode": "actual game fixture; identical camera and actor positions per pair", "rooms": rows}, "  "))
    manifest.close()
    quit(0)
