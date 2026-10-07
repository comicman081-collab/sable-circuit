extends SceneTree
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const PROJECTILE := preload("res://scripts/combat/prototype_projectile.gd")
const OUT := "res://qa/continuous_map_20260923/environment_props"
var failures: Array[String] = []
var checks := 0
var captures: Array[String] = []
var capture_dir := OUT+"/run_"+str(Time.get_unix_time_from_system()).replace(".","_")

class Target extends Node2D:
    var damage_received := 0.0
    func apply_damage(value: float) -> void: damage_received += value
    func get_combat_hit_rect() -> Rect2:
        return Rect2(global_position-Vector2(10,10),Vector2(20,20))

func _init() -> void: call_deferred("run")
func check(ok: bool, note: String) -> void:
    checks += 1
    if not ok:
        failures.append(note)
        push_error(note)
func settle(frames: int = 5) -> void:
    for i in range(frames):
        await physics_frame
        await process_frame

func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(capture_dir))
    root.size=Vector2i(1920,1080)
    root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name() != "headless": DisplayServer.window_set_size(Vector2i(1920,1080))
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    root.add_child(stage)
    await settle()
    var props := stage.get_node("EnvironmentProps")
    check(props.entries.size()==15, "15 scoped Stage 1 prop placements")
    check(props.textures.size()==4, "Only four cached prop textures")
    for step in [1,3,4]:
        stage.start_battle_preview(step)
        await settle(20)
        var active := 0
        for entry: Dictionary in props.entries:
            var prop: StaticBody2D=entry.prop
            if prop.active:
                active+=1
                check(entry.plate.visible, "Prop remains bound to its world plate")
                check(prop.collision_layer==1, "Visible prop blocks actor ground movement")
                check(prop.ground.size()==4, "Model-derived footprint has four corners")
                check(prop.z_index==preload("res://scripts/missions/site7_depth.gd").z_for(prop.global_position.y), "Prop shares actor depth order")
                for actor in stage.squad.operators:
                    check(not Geometry2D.is_point_in_polygon(prop.to_local(actor.global_position), prop.ground), "Prop footprint does not contain squad spawn")
            else:
                check(prop.collision_layer==0, "Hidden room props cannot block movement")
        check(active==15, "All mission props stay collidable across one continuous map")
        for actor in stage.squad.operators:
            check(not actor.is_downed(), "Squad still live")
        if DisplayServer.get_name() != "headless":
            await RenderingServer.frame_post_draw
            var image := root.get_texture().get_image()
            check(image.get_size()==Vector2i(1920,1080), "Native 1080p app capture")
            var path := capture_dir+"/stage1_step_%d_1920x1080.png" % step
            check(image.save_png(ProjectSettings.globalize_path(path))==OK,"Capture saved")
            captures.append(path)
    stage.start_battle_preview(1)
    await settle()
    var barrier: StaticBody2D
    for entry: Dictionary in props.entries:
        if entry.prop.active and entry.asset=="barrier" and entry.room_id==str(stage.main_route[stage.current_step].id): barrier=entry.prop
    check(is_instance_valid(barrier), "Active barrier found")
    if is_instance_valid(barrier):
        var center := barrier.global_position
        var probe := CharacterBody2D.new()
        probe.collision_layer=0
        probe.collision_mask=1
        var shape := CollisionShape2D.new()
        var circle := CircleShape2D.new()
        circle.radius=4
        shape.shape=circle
        probe.add_child(shape)
        root.add_child(probe)
        probe.global_position=center+Vector2(-140,0)
        await settle(2)
        var hit := probe.move_and_collide(Vector2(280,0))
        check(hit!=null and hit.get_collider()==barrier,"Actual CharacterBody movement collides with barrier")
        probe.queue_free()
        var a := center+Vector2(-160,-28)
        var b := center+Vector2(160,-28)
        check(barrier.projectile_hit(a,b)!=Vector2.INF,"Visible barrier face stops swept ray")
        check(barrier.projectile_hit(center+Vector2(-160,-180),center+Vector2(160,-180))==Vector2.INF,"Transparent margin does not block")
        for side in [-1,1]:
            var victim := Target.new()
            root.add_child(victim)
            victim.add_to_group("environment_smoke_victim")
            victim.global_position=center+Vector2(160*side,-28)
            var projectile := PROJECTILE.new()
            root.add_child(projectile)
            projectile.set_physics_process(false)
            projectile.setup(center+Vector2(-160*side,-28),Vector2(side,0),null,Color.WHITE,{},"environment_smoke_victim")
            projectile.speed=1000
            projectile._physics_process(.4)
            check(projectile.is_queued_for_deletion(),"Real projectile consumed by cover in both directions")
            check(victim.damage_received==0,"Cover prevents damage to target behind it")
            victim.queue_free()
            await settle(1)
        await real_weapon_cover(stage,barrier)
    stage.queue_free()
    await settle()
    check(get_nodes_in_group("sable_environment_cover").is_empty(), "Stage exit releases all prop colliders")
    var hashes: Dictionary = {}
    for path in ["scripts/missions/site7_environment_prop.gd","scripts/missions/site7_environment_props.gd","scripts/combat/prototype_projectile.gd","scripts/combat/cover_navigation.gd","scripts/combat/site7_enemy_tactics.gd","scripts/actors/operator_actor.gd","data/visual/site7_environment_props.json","assets/environments/site7/karchive_props_v1/spec.json","tests/render/site7_environment_props_check.gd"]:
        hashes[path] = FileAccess.get_sha256("res://"+path)
    var result := {"status":"PASS_TECHNICAL_ONLY" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"dependency_sha256":hashes,
        "native_resolution":[1920,1080],"captures":captures,"visual_approval":false}
    var output := FileAccess.open(capture_dir+"/check.json",FileAccess.WRITE)
    output.store_string(JSON.stringify(result,"  "))
    print("SITE7_ENVIRONMENT_PROPS: %s / %d checks" % [result.status,checks])
    quit(0 if failures.is_empty() else 1)

func advance_shot(shot: PrototypeProjectile, hz: int) -> void:
    shot.set_physics_process(false)
    for i in range(hz*2):
        if shot.is_queued_for_deletion(): break
        shot._physics_process(1.0/hz)

func real_weapon_cover(stage: StoryStage01, barrier: StaticBody2D) -> void:
    # Controlled combat fixture using real weapon/emitter/telegraph paths,
    # separate from the unmodified full-operation playthrough.
    stage.set_process(false)
    for node in root.get_children():
        if node is PrototypeProjectile: node.free()
    var player := stage.squad.get_active_operator()
    var enemy: EnemyActor
    for node in get_nodes_in_group("m3_enemies"):
        node.set_physics_process(false)
        if stage.is_ancestor_of(node) and enemy==null: enemy=node
        else: node.remove_from_group("prototype_targets")
    for actor in stage.squad.operators:
        actor.set_physics_process(false)
        actor.set_process(false)
        if actor!=player: actor.remove_from_group("operators")
    check(enemy!=null,"Actual drone available for weapon-cover fixture")
    if enemy==null:return
    player.global_position=barrier.global_position+Vector2(-200,0)
    enemy.global_position=barrier.global_position+Vector2(200,0)
    enemy.machine_sprite.set_process(false)
    player.debug_drive(Vector2.ZERO,Vector2.RIGHT)
    var player_shots: Array[PrototypeProjectile] = []
    var enemy_shots: Array[PrototypeProjectile] = []
    player.projectile_spawned.connect(func(shot: PrototypeProjectile) -> void:player_shots.append(shot))
    enemy.projectile_emitted.connect(func(event: Dictionary) -> void:enemy_shots.append(instance_from_id(event.projectile_id)))
    for hz in [30,60,120]:
        var enemy_hp := enemy.health
        var player_hp := player.health
        var blocked_player: int = barrier.blocked_player_shots
        var blocked_enemy: int = barrier.blocked_enemy_shots
        player._pointer_target=enemy.get_combat_aim_point()
        check(player.debug_fire_once(),"Actual player weapon fires at %dHz" % hz)
        advance_shot(player_shots.back(),hz)
        check(barrier.blocked_player_shots==blocked_player+1 and enemy.health==enemy_hp,"Real player shot blocked, enemy protected at %dHz" % hz)
        enemy.tactics.state="REPOSITION"
        enemy.tactics.state_left=0
        var before := enemy_shots.size()
        # Existing cover now prevents AI windup. Introduce it after a normal
        # warning instead, so this still proves actual projectile blocking.
        barrier.set_active(false)
        enemy.tactics.step(player,1.0/hz)
        barrier.set_active(true)
        for tick in range(hz*2):
            enemy.tactics.step(player,1.0/hz)
            if enemy_shots.size()>before:break
        check(enemy_shots.size()==before+1,"Drone telegraph emits one actual shot at %dHz" % hz)
        if enemy_shots.size()>before:
            advance_shot(enemy_shots.back(),hz)
            check(barrier.blocked_enemy_shots==blocked_enemy+1 and player.health==player_hp,"Real drone shot blocked, player protected at %dHz" % hz)
    # Control: clearing this one barrier must allow the same real player shot
    # to damage the same drone. A missing shot cannot masquerade as cover.
    var hp_without_cover := enemy.health
    barrier.set_active(false)
    player._pointer_target=enemy.get_combat_aim_point()
    check(player.debug_fire_once(),"Uncovered control shot fires")
    advance_shot(player_shots.back(),60)
    check(enemy.health<hp_without_cover,"Removing barrier exposes target to the same shot")
    barrier.set_active(true)
    await settle(1)
