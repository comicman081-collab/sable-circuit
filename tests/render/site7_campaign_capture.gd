extends SceneTree
## Native UI/encounter fixtures. Synthetic clears unlock UI only; full combat
## outcomes are measured separately by site7_full_operation_smoke.gd.
const FLOW := preload("res://scripts/core/game_flow.gd")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
var out := "res://qa/campaign_20260919/native_"+str(Time.get_unix_time_from_system()).replace(".","_")
var captures: Array[String] = []
var failures: Array[String] = []
var checks := 0
var flow: GameFlow
func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks+=1
    if not ok: failures.append(label); push_error(label)
func settle(count: int = 8) -> void:
    for _i in range(count): await process_frame; await physics_frame
func capture(label: String) -> void:
    if DisplayServer.get_name()=="headless": return
    await RenderingServer.frame_post_draw
    var im := root.get_texture().get_image()
    check(im.get_size()==Vector2i(1920,1080), "Native frame "+label)
    var path := out+"/"+label+".png"
    check(im.save_png(ProjectSettings.globalize_path(path))==OK,"Saved "+label)
    captures.append(path)

func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size=Vector2i(1920,1080); root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name()!="headless": DisplayServer.window_set_size(Vector2i(1920,1080))
    flow=FLOW.new(); flow.persist_campaign=false; root.add_child(flow); await settle()
    flow.enter_base(); await settle(); await capture("base_initial")
    for number in range(1,4):
        flow.campaign.commit_mission({"transaction_id":"UI-FIXTURE-%d"%number,"mission_id":"MIS_CH01_%02d"%number,"outcome":"EXTRACTED","full_route_cleared":true})
    flow.enter_base(); await settle(); await capture("base_all_operations")
    for number in [2,3]:
        var id := "MIS_CH01_%02d" % number
        flow.open_mission_briefing(id); await settle(); await capture("stage%d_briefing"%number)
        flow.open_battle_preview(number); await settle()
        var stage := flow.current_view as StoryStage01
        for step in [1,3,4]:
            stage.start_battle_preview(step); await settle(2)
            var enemies: Array = get_nodes_in_group("m3_enemies")
            var player := stage.squad.get_active_operator()
            var obstacles := NAV.ground_obstacles(player)
            var planner := NAV.new()
            for i in range((stage.main_route[step].encounter as Array).size()):
                check(not planner._plan(player,stage.battlefield.squad_spawn(0),stage.battlefield.enemy_spawn(i),obstacles).is_empty(),"Stage%d step%d route around cover to hostile%d"%[number,step,i])
            for i in range(3):
                var spawn: Vector2 = stage.battlefield.squad_spawn(i)
                for obstacle in obstacles:
                    check(not obstacle.has_point(spawn),"Stage%d step%d squad spawn%d outside cover"%[number,step,i])
            for i in range(enemies.size()):
                var enemy := enemies[i] as EnemyActor
                if enemy == null or enemy.is_queued_for_deletion(): continue
                for obstacle in NAV.ground_obstacles(enemy):
                    check(not obstacle.has_point(enemy.global_position),"Stage%d step%d enemy outside cover"%[number,step])
            var props := stage.get_node("EnvironmentProps")
            for entry: Dictionary in props.entries:
                if not entry.prop.active: continue
                check(stage.battlefield.contains(entry.prop.global_position),"Stage%d step%d %s anchor on floor"%[number,step,entry.asset])
            for _frame in range(48):
                if not enemies.is_empty() and is_instance_valid(enemies[0]):
                    var cursor: Vector2 = root.get_final_transform() * (stage.get_canvas_transform() * enemies[0].get_combat_aim_point())
                    var motion := InputEventMouseMotion.new()
                    motion.position=cursor; motion.global_position=cursor
                    Input.parse_input_event(motion)
                await settle(1)
            await capture("stage%d_encounter%d"%[number,step])
        flow.show_results({"mission_id":id,"transaction_id":"RESULT-UI-%d"%number,"outcome":"EXTRACTED","full_route_cleared":true,"extraction_depth":6,"ledger_recovered":true,"secured_research":236,"secured_salvage":3,"secured_fragments":1})
        await settle(); await capture("stage%d_results"%number)
    var file := FileAccess.open(out+"/capture.json",FileAccess.WRITE)
    var hashes: Dictionary = {}
    for path in ["scripts/core/game_flow.gd","scripts/core/campaign_progression.gd","scripts/core/site7_campaign.gd","scripts/ui/base_lobby.gd","scripts/ui/briefing_screen.gd","scripts/ui/mission_results.gd","scripts/missions/story_stage_01.gd","data/story/site7_campaign.json","data/visual/site7_environment_props.json","data/art_profiles/playable_profiles.json","data/visual/site7_battle_layouts.json","tests/render/site7_campaign_capture.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    file.store_string(JSON.stringify({"status":"PASS_TECHNICAL" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"native_resolution":[1920,1080],"captures":captures,"synthetic_ui_unlocks":true,"visual_approval":false,"tested_sha256":hashes},"  ")); file.close()
    flow.queue_free(); await settle()
    print("SITE7_CAMPAIGN_CAPTURE %s %s"%["PASS" if failures.is_empty() else "FAIL",out]); quit(0 if failures.is_empty() else 1)
