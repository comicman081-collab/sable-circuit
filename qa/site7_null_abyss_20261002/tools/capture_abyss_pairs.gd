extends SceneTree
## Scratch (Claude, 2026-10-02): the plate-edge views of a mission twice, once as shipped and once with every
## plate hidden, so the abyss alone can be measured. Same cameras and frozen shader TIME as
## tools/environment/capture_site7_plate_edges.gd. --out=res://... --mission=MIS_CH01_NN
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
    var mission := "MIS_CH01_10"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
        if arg.begins_with("--mission="): mission = arg.trim_prefix("--mission=")
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
    var plates: Array[Node] = []
    for child in art.get_children():
        if child is Sprite2D: plates.append(child)
    # The backdrop follows the stage camera in _process, which is disabled here: pin its parallax centre to this
    # capture camera so every run draws the same pixels (the game's own camera centre drives it the same way).
    var backdrop_material := art.get_node("AbyssBackdrop").material as ShaderMaterial
    for target in targets:
        var plate := target.plate as Sprite2D
        camera.global_position = plate.global_position + target.offset
        backdrop_material.set_shader_parameter("camera_center", camera.global_position)
        for tick in 4: await process_frame
        await RenderingServer.frame_post_draw
        root.get_texture().get_image().save_png("%s/%s_native_1080p.png" % [out, target.id])
        for node in plates: node.visible = false
        for tick in 2: await process_frame
        await RenderingServer.frame_post_draw
        root.get_texture().get_image().save_png("%s/%s_abyss_only.png" % [out, target.id])
        for node in plates: node.visible = true
        print("ABYSS_PAIR ", target.id)
    print("ABYSS_PAIR_COMPLETE")
    quit()
