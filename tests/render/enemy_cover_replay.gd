extends "res://tests/render/stage_battle_video_10s_capture.gd"
## Replays the user's delivered input pattern and records actual enemy motion.
func run() -> void:
    var label := "before"
    for argument in OS.get_cmdline_user_args():
        if argument.begins_with("--label="): label=argument.trim_prefix("--label=")
    var out := "res://qa/enemy_cover_repair_20260919/"+label
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size=SIZE; root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    var rows: Array[Dictionary]=[]
    for number in [1,2,3]:
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id="MIS_CH01_%02d"%number; stage.battle_preview=true
        root.add_child(stage); current_scene=stage
        for _i in range(8): await process_frame
        stage.start_battle_preview(1)
        var previous: Dictionary={}
        for frame in range(600):
            var keys: Array[int]=[]
            if frame<90: keys=[KEY_D]
            elif frame<150: keys=[KEY_S]
            elif frame<210: keys=[KEY_A]
            elif frame==210: keys=[KEY_R]
            elif frame>=300 and frame<390: keys=[KEY_D]
            elif frame>=390 and frame<450: keys=[KEY_W,KEY_SHIFT]
            _set_keys(keys); _aim_at_enemy(stage); _set_fire(frame<210 or frame>=300)
            await process_frame
            if frame%30!=0: continue
            for enemy in get_nodes_in_group("m3_enemies"):
                if not enemy is EnemyActor or enemy.is_queued_for_deletion(): continue
                var eid := enemy.get_instance_id()
                var position_before: Vector2=previous.get(eid,enemy.global_position)
                var collisions: Array=[]
                for index in range(enemy.get_slide_collision_count()):
                    var c: KinematicCollision2D=enemy.get_slide_collision(index)
                    collisions.append({"normal":str(c.get_normal()),"collider":str(c.get_collider())})
                rows.append({"mission":number,"frame":frame,"id":eid,"enemy":enemy.enemy_id,
                    "position":str(enemy.global_position),"travel_30f":enemy.global_position.distance_to(position_before),
                    "velocity":str(enemy.velocity),"health":enemy.health,"state":enemy.tactics.state,
                    "flank":str(enemy.tactics._flank_goal),"nav_goal":str(enemy.tactics._cover_navigation._goal),
                    "path":str(enemy.tactics._cover_navigation._path),"collisions":collisions,
                    "player":str(stage.squad.get_active_operator().global_position)})
                previous[eid]=enemy.global_position
        _set_keys([]); _set_fire(false)
        stage.queue_free()
        for _i in range(5): await process_frame
    FileAccess.open(out+"/replay.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "))
    print("ENEMY_COVER_REPLAY ",out," rows=",rows.size()); quit()
