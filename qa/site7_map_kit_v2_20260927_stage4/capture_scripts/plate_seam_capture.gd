extends SceneTree
## Frames each connector plate of a mission whole (native 1920x1080) so the seams at its
## top and bottom borders can be compared before/after. Actors and HUD are hidden.
## -- --mission=MIS_CH01_01 --out=res://.cache/diag/vfx/seams/after
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")

func _init(): call_deferred("_run")

func _run():
    var mission := "MIS_CH01_01"
    var out := "res://.cache/diag/vfx/seams"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): mission = arg.trim_prefix("--mission=")
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    for i in 30: await process_frame
    var art := stage.get_node_or_null("RoomArt")
    if art == null:
        for n in stage.get_children():
            if n is Site7RoomArtLayer: art = n
    for n in stage.get_children():
        if n is CanvasLayer: n.visible = false
    for group in ["operators", "m3_enemies", "sable_environment_cover"]:
        for n in get_nodes_in_group(group):
            if n is CanvasItem: (n as CanvasItem).visible = false
    stage.process_mode = Node.PROCESS_MODE_DISABLED
    var cam := Camera2D.new()
    cam.zoom = Vector2(0.84, 0.84)
    cam.process_mode = Node.PROCESS_MODE_ALWAYS
    root.add_child(cam)
    cam.make_current()
    for index in range(7):
        var plate := art.call("get_connector_plate", index) as Sprite2D
        if plate == null: continue
        # New native v2 plates are larger; keep both complete cut ends in frame.
        var bounds := plate.texture.get_size() * plate.scale.abs()
        cam.zoom = Vector2.ONE * minf(0.84, minf(1200.0 / bounds.x, 672.0 / bounds.y))
        cam.global_position = plate.global_position
        for i in 4: await process_frame
        await RenderingServer.frame_post_draw
        var image := root.get_texture().get_image()
        var path := "%s/%s_C%d.png" % [out, mission, index]
        image.save_png(path)
        print("SEAM_CAPTURE ", path, " ", image.get_size(), " masks=", plate.get_meta("floor_masks", -1), " cap=", plate.get_meta("cap_fade", 0.0))
    cam.zoom = Vector2(1.22, 1.22)
    for room: Dictionary in stage.main_route + stage.optional_rooms:
        for offset in [Vector2(-330, -120), Vector2(330, 120)]:
            cam.global_position = Vector2(float(room.x), float(room.y)) + offset
            for i in 4: await process_frame
            await RenderingServer.frame_post_draw
            var shot := root.get_texture().get_image()
            var room_path := "%s/%s_%s_%s.png" % [out, mission, str(room.id), "a" if offset.x < 0 else "b"]
            shot.save_png(room_path)
            print("SEAM_CAPTURE ", room_path)
    quit()
