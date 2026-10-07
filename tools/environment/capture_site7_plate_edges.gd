extends SceneTree
## Bounded production review capture. Six fixed cameras, native 1920x1080;
## --out is required. Shader TIME is frozen only on duplicated capture materials.
## This is an art preview, not a playthrough or a visual approval test.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")

func _initialize() -> void:
    call_deferred("capture")

func freeze_shader_time(node: Node) -> void:
    if node is CanvasItem and node.material is ShaderMaterial:
        var original := node.material as ShaderMaterial
        if original.shader and original.shader.code.contains("TIME"):
            var material := original.duplicate() as ShaderMaterial
            var shader := Shader.new()
            shader.code = original.shader.code.replace("TIME", "1.0")
            material.shader = shader
            node.material = material
    for child in node.get_children(): freeze_shader_time(child)

func capture() -> void:
    var out := ""
    var mission := "MIS_CH01_08"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
        if arg.begins_with("--mission="): mission = arg.trim_prefix("--mission=")
    if out.is_empty():
        push_error("capture_site7_plate_edges.gd requires --out=<project path>")
        quit(2)
        return
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    stage.battle_preview = true
    root.add_child(stage)
    for tick in 30: await process_frame
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    for child in stage.get_children():
        if child is CanvasLayer: child.visible = false
    for group in ["operators", "m3_enemies", "sable_environment_cover"]:
        for actor in get_nodes_in_group(group):
            if actor is CanvasItem: actor.visible = false
    stage.process_mode = Node.PROCESS_MODE_DISABLED
    freeze_shader_time(stage)
    var prefix := "S%d_" % int(mission.right(2))
    var targets: Array[Dictionary] = [
        {"id": prefix + "R01", "plate": art.get_room_plate(str(stage.main_route[0].id)), "offset": Vector2(-330, -120)},
        {"id": prefix + "R05", "plate": art.get_room_plate(str(stage.main_route[4].id)), "offset": Vector2(330, 120)},
        {"id": prefix + "O02", "plate": art.get_room_plate(str(stage.optional_rooms[1].id)), "offset": Vector2(-180, -100)},
        {"id": prefix + "C03", "plate": art.get_connector_plate(2), "offset": Vector2.ZERO},
        {"id": prefix + "C05", "plate": art.get_connector_plate(4), "offset": Vector2.ZERO},
        {"id": prefix + "C06", "plate": art.get_connector_plate(5), "offset": Vector2.ZERO},
    ]
    var camera := Camera2D.new()
    camera.zoom = Vector2(1.22, 1.22)
    root.add_child(camera)
    camera.make_current()
    var rows: Array[Dictionary] = []
    for target in targets:
        var plate := target.plate as Sprite2D
        camera.global_position = plate.global_position + target.offset
        for tick in 4: await process_frame
        await RenderingServer.frame_post_draw
        var image := root.get_texture().get_image()
        var path := "%s/%s_native_1080p.png" % [out, target.id]
        image.save_png(path)
        rows.append({"plate": target.id, "asset": plate.get_meta("asset"), "camera": [camera.global_position.x, camera.global_position.y], "zoom": 1.22, "resolution": [image.get_width(), image.get_height()], "path": path})
        print("PLATE_EDGE_CAPTURE ", target.id, " ", image.get_size())
    var file := FileAccess.open(out.path_join("capture.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify({"mission": mission, "native_resolution": [1920, 1080], "shader_time_seconds": 1.0, "actors_and_hud": "hidden", "capture_kind": "actual runtime art preview, no activation or play approval", "frames": rows}, "  "))
    print("PLATE_EDGE_CAPTURE_COMPLETE 6 native frames")
    quit()
