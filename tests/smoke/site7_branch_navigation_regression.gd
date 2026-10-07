extends SceneTree

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var failed := false
    var only_mission := 0
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): only_mission = int(arg.get_slice("=", 1))
    for mission_number in range(1, 11):
        if only_mission != 0 and mission_number != only_mission: continue
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % mission_number
        root.add_child(stage)
        for tick in range(15):
            await physics_frame
            await process_frame
        for enemy in get_nodes_in_group("m3_enemies"):
            if enemy is EnemyActor and stage.is_ancestor_of(enemy):
                enemy.set_physics_process(false)
                enemy.collision_layer = 0
                enemy.collision_mask = 0
        var actor := stage.squad.get_active_operator()
        var nav := NAV.new()
        for branch in range(2):
            var parent: Dictionary = stage.branch_parent(branch)
            var target: Dictionary = stage.optional_rooms[branch]
            actor.global_position = Vector2(float(parent.x), float(parent.y))
            await physics_frame
            var goal := Vector2(float(target.x), float(target.y))
            var initial := actor.global_position
            var no_progress := 0
            var last_distance := initial.distance_to(goal)
            var min_distance := last_distance
            for tick in range(700):
                if actor.global_position.distance_to(goal) < 130.0: break
                var direction: Vector2 = nav.direction(actor, goal, 1.0 / 60.0)
                actor.debug_drive(direction, Vector2.RIGHT)
                actor._debug_run = true
                await physics_frame
                var distance := actor.global_position.distance_to(goal)
                if distance < min_distance - 5.0:
                    min_distance = distance
                    no_progress = 0
                else:
                    no_progress += 1
                last_distance = distance
                if no_progress > 120: break
            actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
            var ok := actor.global_position.distance_to(goal) < 130.0
            print("BRANCH_NAV ", JSON.stringify({"mission":stage.mission_id,"branch":branch,"ok":ok,"start":initial,"end":actor.global_position,"goal":goal,"path":Array(nav._path),"min_distance":min_distance,"replans":nav.replans,"obstacles":NAV.ground_obstacles(actor)}))
            if not ok: failed = true
        stage.queue_free()
        await process_frame
    print("SITE7_BRANCH_NAVIGATION ", "FAIL" if failed else "PASS")
    quit(1 if failed else 0)
