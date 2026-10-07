extends SceneTree
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TestOutput := preload("res://tests/support/test_output.gd")
var checks := 0
var failures: Array[String] = []
var observations: Array[Dictionary] = []
var captures: Array[String] = []
var run_dir := TestOutput.path("res://qa/cover_ai_20260919/run_"+str(Time.get_unix_time_from_system()).replace(".","_"))
var stage: StoryStage01
var barrier: StaticBody2D
var player: OperatorActor
var enemy: EnemyActor

func _init() -> void: call_deferred("run")
func check(ok: bool, note: String) -> void:
    checks+=1
    if not ok: failures.append(note); push_error(note)
func settle(count: int = 4) -> void:
    for _i in range(count): await physics_frame; await process_frame
func capture(name: String) -> void:
    if DisplayServer.get_name()=="headless": return
    # Fixture framing only: include the flanking drone and its emitter rather
    # than accepting an on-screen target with an off-screen shooter.
    stage.get_node("SquadCameraPresentation").set_process(false)
    stage.camera.global_position=barrier.global_position+Vector2(20,-60)
    stage.camera.zoom=Vector2.ONE
    stage.camera.reset_smoothing()
    stage.camera.force_update_scroll()
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    check(image.get_size()==Vector2i(1920,1080),"Native 1080p cover AI capture")
    var path := run_dir+"/"+name+".png"
    check(image.save_png(ProjectSettings.globalize_path(path))==OK,"Capture saved")
    captures.append(path)
func reset_positions() -> void:
    player.global_position=barrier.global_position+Vector2(-170,0)
    enemy.global_position=barrier.global_position+Vector2(170,0)
    player.velocity=Vector2.ZERO
    enemy.velocity=Vector2.ZERO
    player._debug_drive=false
    player.controlled=false
    player.set_ai_goal(player.global_position)
    player._ai_tactical_goal=Vector2.INF
    player._fire_cooldown=0
    enemy.tactics.state="REPOSITION"
    enemy.tactics.state_left=0
    enemy.tactics._flank_goal=Vector2.INF
    # A teleport is not motion. The physics server reports a teleported body's
    # jump as its velocity for one step, and an actor whose last contact was
    # that body rides it as a moving floor (a 200px follower jump at 60Hz).
    # Let one step take the jump and the next report rest before anyone moves;
    # a wait resumes before its step, hence three waits for two whole steps.
    for _i in range(3): await physics_frame

func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(run_dir))
    root.size=Vector2i(1920,1080)
    root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name()!="headless": DisplayServer.window_set_size(Vector2i(1920,1080))
    stage=STAGE.instantiate()
    stage.battle_preview=true
    root.add_child(stage)
    await settle(10)
    stage.start_battle_preview(1)
    await settle(4)
    stage.set_process(false)
    stage.set_physics_process(false)
    stage.squad.set_process(false)
    stage.squad.set_physics_process(false)
    stage.get_node("EnvironmentProps").set_process(false)
    player=stage.squad.get_active_operator()
    for actor in stage.squad.operators:
        actor.set_physics_process(false); actor.set_process(false)
        if actor!=player: actor.remove_from_group("operators"); actor.collision_layer=0
    for actor in get_nodes_in_group("m3_enemies"):
        actor.set_physics_process(false)
        if enemy==null: enemy=actor
        else: actor.remove_from_group("prototype_targets")
    for entry: Dictionary in stage.get_node("EnvironmentProps").entries:
        if entry.prop.active and entry.asset=="barrier" and entry.room_id == str(stage.main_route[stage.current_step].id): barrier=entry.prop
    check(barrier!=null and enemy!=null,"Actual app barrier and drone exist")
    if barrier==null or enemy==null: quit(1); return
    for node in root.get_children():
        if node is PrototypeProjectile: node.free()
    var old_hz := Engine.physics_ticks_per_second
    var enemy_shots: Array[PrototypeProjectile] = []
    enemy.projectile_emitted.connect(func(event: Dictionary) -> void:
        var shot := instance_from_id(event.projectile_id) as PrototypeProjectile
        shot.set_physics_process(false); enemy_shots.append(shot))
    for hz in [30,60,120]:
        Engine.physics_ticks_per_second=hz
        await settle(2)
        await reset_positions()
        var ammo := player.ammo
        check(not player._update_ai_aim_and_fire(),"Follower refuses covered target at %dHz"%hz)
        check(not player._try_fire(false) and player.ammo==ammo,"Covered follower does not spend ammo at %dHz"%hz)
        var before := enemy_shots.size()
        for tick in range(hz): enemy.tactics.step(player,1.0/hz)
        check(enemy.tactics.state=="REPOSITION" and enemy_shots.size()==before,"Covered drone waits to flank at %dHz"%hz)
        check(enemy.velocity.length()>0,"Covered drone requests actual movement at %dHz"%hz)
        if hz==60: await capture("01_cover_holds")
        # Introduce cover AFTER a real warning: AI suppression cannot replace
        # collision, and the announced ray must not home around the obstacle.
        barrier.set_active(false)
        enemy.tactics.state_left=0
        enemy.tactics.step(player,1.0/hz)
        check(enemy.tactics.state=="WINDUP","Uncovered drone enters fresh warning at %dHz"%hz)
        var aim: Vector2=enemy.tactics.locked_aim
        barrier.set_active(true)
        for tick in range(hz):
            enemy.tactics.step(player,1.0/hz)
            if enemy_shots.size()>before: break
        check(enemy_shots.size()==before+1 and enemy.tactics.locked_aim.is_equal_approx(aim),"Announced shot remains locked at %dHz"%hz)
        var blocks: int=barrier.blocked_enemy_shots
        var health := player.health
        if enemy_shots.size()>before:
            var shot: PrototypeProjectile=enemy_shots.back()
            for tick in range(hz*2):
                if shot.is_queued_for_deletion(): break
                shot._physics_process(1.0/hz)
        check(barrier.blocked_enemy_shots==blocks+1 and player.health==health,"Post-warning cover absorbs actual shot at %dHz"%hz)
        await settle(1)
        # Actual follower physics/gait/collision, with no targets shooting back.
        enemy.remove_from_group("prototype_targets")
        await reset_positions()
        var goal := barrier.global_position+Vector2(170,0)
        player.set_ai_goal(goal)
        var initial := player.global_position
        var max_side := 0.0
        for tick in range(hz*9):
            await physics_frame
            player._physics_process(1.0/hz)
            max_side=maxf(max_side,absf(player.global_position.y-initial.y))
            if player.global_position.distance_to(goal)<=20: break
        var reachable_goal := NAV._free_goal(player,goal,NAV.ground_obstacles(player))
        # The goal is occupied by a live enemy. Since operators now collide
        # with hostiles, the correct stop is one combined body radius away.
        var body_gap := player.global_position.distance_to(reachable_goal)
        check(body_gap>=24.0 and body_gap<=38.0 and player.global_position.x>barrier.global_position.x+100,"Follower bypasses cover and stops at hostile body at %dHz (gap=%.2f)"%[hz,body_gap])
        check(max_side>35,"Follower travels around ground footprint at %dHz"%hz)
        observations.append({"hz":hz,"kind":"follower_path","end_distance":player.global_position.distance_to(goal),"side_travel":max_side})
        if hz==60: await capture("02_follower_bypass")
        enemy.add_to_group("prototype_targets")
        await reset_positions()
        var start := enemy.global_position
        var warning_seen := false
        for tick in range(hz*10):
            await physics_frame
            enemy._physics_process(1.0/hz)
            if enemy.tactics.state=="WINDUP":
                warning_seen=true
                check(NAV.clear_shot(self,enemy.projectile_origin(enemy.tactics.locked_aim),player),"New warning has clear authored firing lane at %dHz"%hz)
                if hz==60: await capture("03_drone_new_warning")
                break
        check(warning_seen and enemy.global_position.distance_to(start)>35,"Drone physically flanks before new warning at %dHz"%hz)
        observations.append({"hz":hz,"kind":"drone_flank","displacement":enemy.global_position.distance_to(start),"new_warning":warning_seen})
        var projected := NAV._free_goal(player,barrier.global_position+Vector2(0,18),NAV.ground_obstacles(player))
        check(projected.is_finite(),"Blocked formation slot has reachable alternative at %dHz"%hz)
        for rect in NAV.ground_obstacles(player): check(not rect.has_point(projected),"Formation alternative outside active prop at %dHz"%hz)
    Engine.physics_ticks_per_second=old_hz
    stage.queue_free()
    await settle(3)
    var hashes: Dictionary={}
    for path in ["scripts/combat/prototype_projectile.gd","scripts/animation/boss_phase_transition_guard.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    for path in ["scripts/combat/cover_navigation.gd","scripts/combat/site7_enemy_tactics.gd","scripts/actors/operator_actor.gd","scripts/actors/enemy_actor.gd","scripts/missions/site7_environment_prop.gd","scripts/ui/battle_reticle.gd","scripts/ui/story_stage_hud.gd","data/visual/site7_environment_props.json","tests/render/site7_cover_ai_check.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    var result := {"status":"PASS_TECHNICAL_ONLY" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,
        "observations":observations,"captures":captures,"native_resolution":[1920,1080],"visual_approval":false,"dependency_sha256":hashes}
    FileAccess.open(run_dir+"/check.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
    print("SITE7_COVER_AI: %s / %d checks"%[result.status,checks])
    quit(0 if failures.is_empty() else 1)
