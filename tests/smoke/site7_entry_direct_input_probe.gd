extends SceneTree

# Diagnose what a player actually gets from holding D after the opening fight.
# Uses the normal controlled actor and input state, not navigation/teleportation.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const INPUT := preload("res://scripts/ui/demo_input.gd")
const OUT := "res://qa/direct_entry_traversal_20260923"

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var capture := "--capture" in OS.get_cmdline_user_args()
    if capture:
        root.size = Vector2i(1920, 1080)
        root.content_scale_size = Vector2i(1280, 720)
        root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    root.add_child(stage)
    for tick in range(12):
        await physics_frame
        await process_frame
    # "After the opening fight": hostiles are frozen AND non-colliding, as in
    # site7_connector_alignment_smoke. A frozen BULWARK body standing on the
    # route is a test-fixture obstacle, not a wall/floor defect.
    for enemy in get_nodes_in_group("m3_enemies"):
        if enemy is EnemyActor and stage.is_ancestor_of(enemy):
            enemy.set_physics_process(false)
            enemy.collision_layer = 0
            enemy.collision_mask = 0
    var actor := stage.squad.get_active_operator()
    var samples: Array[Dictionary] = []
    INPUT.held[KEY_D] = true
    INPUT.held[KEY_SHIFT] = true
    for tick in range(900):
        await physics_frame
        if capture and tick in [300, 660, 840]:
            await RenderingServer.frame_post_draw
            var frame := root.get_texture().get_image()
            var path := ProjectSettings.globalize_path(OUT + "/hold_d_%d_native.png" % tick)
            if frame.get_size() == Vector2i(1920, 1080): frame.save_png(path)
        if tick % 60 == 0 or tick == 899:
            var contacts: Array[String] = []
            for index in range(actor.get_slide_collision_count()):
                var collider := actor.get_slide_collision(index).get_collider()
                if collider is Node:
                    contacts.append((collider as Node).name)
            samples.append({"tick":tick,"position":actor.global_position,
                "walkable":stage.battlefield.is_walkable(actor.global_position),"contacts":contacts})
    INPUT.held.erase(KEY_D)
    INPUT.held.erase(KEY_SHIFT)
    for row in samples:
        print("DIRECT_ENTRY_D ", JSON.stringify(row))
    var goal: Dictionary = stage.main_route[1]
    var distance := actor.global_position.distance_to(Vector2(float(goal.x),float(goal.y)))
    print("DIRECT_ENTRY_D_FINAL ", JSON.stringify({"distance_to_r02":distance,"position":actor.global_position}))
    var passed := actor.global_position.x > 5200.0
    print("DIRECT_ENTRY_D_SMOKE: ", "PASS" if passed else "FAIL")
    stage.queue_free()
    await process_frame
    quit(0 if passed else 1)
