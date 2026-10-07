extends SceneTree

# Art-only native-size inspection at representative up/down seams. Movement
# proof is the separate normal-input smoke, not these placed camera views.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT := "res://qa/direct_entry_traversal_20260923"

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
    for case in [{"mission":"MIS_CH01_02","link":1}, {"mission":"MIS_CH01_05","link":0}, {"mission":"MIS_CH01_01","link":5}, {"mission":"MIS_CH01_05","link":6}]:
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = str(case.mission)
        root.add_child(stage)
        for tick in range(20):
            await physics_frame
            await process_frame
        for enemy in get_nodes_in_group("m3_enemies"):
            if enemy is EnemyActor and stage.is_ancestor_of(enemy): enemy.set_physics_process(false)
        var link := int(case.link)
        var p1: Vector2 = stage.battlefield._route_segments[link * 3][1]
        var actor := stage.squad.get_active_operator()
        actor.global_position = p1 + Vector2(-105.0, 10.0)
        for tick in range(100):
            await physics_frame
            await process_frame
        await RenderingServer.frame_post_draw
        var image := root.get_texture().get_image()
        var name := "open_connector_%s_link%d_native.png" % [case.mission, link]
        var path := ProjectSettings.globalize_path(OUT + "/" + name)
        if image.get_size() != Vector2i(1920, 1080) or image.save_png(path) != OK:
            push_error("Failed native capture: " + name)
            quit(1)
            return
        print("OPEN_CONNECTOR_CAPTURE ", JSON.stringify({"mission":case.mission,"link":link,"path":path}))
        stage.queue_free()
        await process_frame
    quit()
