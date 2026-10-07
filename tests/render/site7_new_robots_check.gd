extends SceneTree
## Same scene/runtime with explicit isolated target placements; not a playthrough.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const DIRS := ["E","SE","S","SW","W","NW","N","NE"]
const IDS := ["ENM_SITE7_BULWARK_01","ENM_SITE7_RAM_01","ENM_SITE7_MORTAR_01"]
# The candidate intake mode was retired with its QA candidates on 2026-09-28; --app is kept as a no-op.
const app := true
var out := "res://qa/stage_enemies_20260919/native_"+str(Time.get_unix_time_from_system()).replace(".","_")
var failures: Array[String] = []
var captures: Array[Dictionary] = []
var checks := 0
var emissions: Array[Dictionary] = []
var stage: StoryStage01
var victim: OperatorActor

func _init() -> void: call_deferred("run")
func check(ok: bool, note: String) -> void:
    checks += 1
    if not ok: failures.append(note); push_error(note)
func settle(n: int=2) -> void:
    for _i in range(n): await physics_frame; await process_frame
func capture(actor: EnemyActor, label: String) -> void:
    if DisplayServer.get_name()=="headless": return
    await RenderingServer.frame_post_draw
    var im := root.get_texture().get_image()
    var path := out+"/"+label+".png"
    check(im.get_size()==Vector2i(1920,1080),"Native 1080p "+label)
    check(im.save_png(ProjectSettings.globalize_path(path))==OK,"Save "+label)
    captures.append({"label":label,"image":path,"sha256":FileAccess.get_sha256(path),"native":[1920,1080],
        "machine":actor.machine_sprite.debug_contract(),"tactics":actor.tactics.contract(),"emissions":emissions.duplicate(true)})

func spawn(id: String) -> EnemyActor:
    var actor := ENEMY.instantiate() as EnemyActor
    check(actor.configure(id,300.0),"Robot-only profile "+id)
    actor.position=Vector2(690,350)
    stage.add_child(actor)
    actor.set_physics_process(false)
    check(is_instance_valid(actor.machine_sprite),"Machine intake "+id)
    check(actor._bones.is_empty(),"No procedural/human fallback skeleton "+id)
    actor.projectile_emitted.connect(func(row: Dictionary) -> void: emissions.append(row))
    return actor

func target_for(actor: EnemyActor, direction: Vector2) -> void:
    actor.machine_sprite.face_direction(direction)
    var lift := victim.get_combat_aim_point()-victim.global_position
    victim.global_position=actor.machine_sprite.muzzle_world()+direction*180.0-lift
    if actor.enemy_id=="ENM_SITE7_RAM_01": victim.global_position=actor.global_position+direction*160.0
    victim.debug_drive(Vector2.ZERO,-direction)
    actor.tactics.state="REPOSITION"; actor.tactics.state_left=0.0
    actor.velocity=Vector2.ZERO

func run() -> void:
    root.size=Vector2i(1920,1080); root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name()!="headless": DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    ProjectSettings.set_setting("sable_visuals/site7_authored_machines",app)
    stage=STAGE.instantiate(); stage.battle_preview=true; root.add_child(stage); await settle(4)
    stage.start_battle_preview(1); await settle()
    stage.set_process(false); stage.squad.set_process(false); stage.squad.set_physics_process(false)
    for old in get_nodes_in_group("m3_enemies"): old.queue_free()
    await settle()
    for operator in stage.squad.operators:
        operator.set_physics_process(false)
        operator.debug_drive(Vector2.ZERO,Vector2.RIGHT)
        if operator.operator_id=="CHR_PROTO_01": victim=operator
        else: operator.hide()
    stage.camera.position_smoothing_enabled=false
    stage.camera.global_position=Vector2(690,290)
    stage.camera.zoom=Vector2.ONE*1.0
    # Sources are real; positions/state clock inputs are controlled fixtures.
    for id in IDS:
        var actor := spawn(id); await settle()
        if not is_instance_valid(actor.machine_sprite): continue
        for hz in [30,60,120]:
            var dt := 1.0/float(hz)
            for i in range(8 if id!="ENM_SITE7_MORTAR_01" else 1):
                var direction := Vector2.from_angle(i*PI/4.0)
                target_for(actor,direction); emissions.clear()
                # Disable cover only in this aiming fixture by choosing a point
                # local to actor; coverage/collision tests are separate below.
                for prop in get_nodes_in_group("sable_environment_cover"): prop.remove_from_group("sable_environment_cover")
                actor.tactics.step(victim,dt)
                check(actor.tactics.state=="WINDUP",id+" begins warning @"+str(hz)+" "+DIRS[i])
                var frozen_facing: String=actor.machine_sprite.facing
                var frozen_aim: Vector2=actor.tactics.locked_aim
                var frozen_root: Vector2=actor.machine_sprite.position
                if hz==60: await capture(actor,id+"_"+DIRS[i]+"_warning")
                victim.global_position=actor.global_position-direction*200.0
                for tick in range(int(hz*1.05)):
                    actor.tactics.step(victim,dt)
                    if actor.tactics.state in ["WINDUP","BURST","LUNGE"]:
                        check(actor.machine_sprite.facing==frozen_facing,"Warning does not home body")
                        check(actor.tactics.locked_aim.is_equal_approx(frozen_aim),"Warning does not home aim")
                    if not emissions.is_empty() or actor.tactics.state in ["LUNGE","RECOVER"]: break
                if id=="ENM_SITE7_BULWARK_01":
                    check(emissions.size()==1,"One actual shield cannon shot")
                    if not emissions.is_empty():
                        var row: Dictionary=emissions[0]
                        check(Vector2(row.direction[0],row.direction[1]).is_equal_approx(frozen_aim),"Bullet follows frozen muzzle ray")
                    check(actor.machine_sprite.position.is_equal_approx(Vector2.ZERO),"Tank stays grounded")
                    check(actor.projectile_damage_multiplier(-direction)<1.0,"Front armour blocks direct shot")
                    check(actor.projectile_damage_multiplier(direction)==1.0,"Rear takes full damage")
                    check(actor.projectile_damage_multiplier(direction.orthogonal())==1.0,"Side takes full damage")
                elif id=="ENM_SITE7_RAM_01":
                    check(actor.tactics.state=="LUNGE","Ram enters advertised charge")
                    check(emissions.is_empty(),"Impact nose does not fire gun bullets")
                else:
                    check(actor.tactics.mortar_launches>0,"Mortar actually launches a shell")
                    check(actor.machine_sprite.position==Vector2.ZERO,"Mortar root fixed")
                for node in get_nodes_in_group("site7_mortar_shells"): node.queue_free()
                for child in root.get_children():
                    if child is PrototypeProjectile: child.queue_free()
                await settle()
        actor.apply_stagger(0.5)
        check(actor.tactics.state=="RECOVER","Stagger cancels warning")
        if id=="ENM_SITE7_BULWARK_01": check(actor.projectile_damage_multiplier(Vector2.LEFT)==1.0,"Stagger defeats armour")
        actor.apply_damage(1000.0)
        await capture(actor,id+"_death")
        actor.queue_free(); await settle()
    await check_actual_armour_hits()
    await check_ram_collision()
    await check_mortar_impact()
    var file := FileAccess.open(out+"/check.json",FileAccess.WRITE)
    var hashes: Dictionary={}
    for path in ["scripts/actors/enemy_actor.gd","scripts/animation/site7_machine_sprite.gd","scripts/combat/site7_enemy_tactics.gd","scripts/combat/site7_mortar_shell.gd","scripts/combat/prototype_projectile.gd","scripts/animation/enemy_detail_overlay_presentation.gd","scripts/animation/enemy_ground_shadow.gd","scripts/ui/enemy_overhead_ui.gd","tests/render/site7_new_robots_check.gd","data/art_profiles/enemy_profiles.json"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    for id in IDS:
        var path: String=ArtProfileRegistry.get_profile(id).machine_asset.spec
        hashes[path]=FileAccess.get_sha256(path)
    file.store_string(JSON.stringify({"status":"PASS_TECHNICAL" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,
        "app_registry":app,"captures":captures,"sha256":hashes,"visual_approval":false,"fixture_not_playthrough":true},"  ")); file.close()
    stage.queue_free(); await settle(3)
    print("SITE7_NEW_ROBOTS %s %d %s"%["PASS" if failures.is_empty() else "FAIL",checks,out])
    quit(0 if failures.is_empty() else 1)

func check_actual_armour_hits() -> void:
    var actor := spawn("ENM_SITE7_BULWARK_01"); await settle()
    actor.machine_sprite.face_direction(Vector2.RIGHT)
    for direction in [Vector2.LEFT,Vector2.RIGHT,Vector2.UP]:
        var target := actor.get_combat_aim_point()
        var bullet := PrototypeProjectile.new()
        root.add_child(bullet)
        bullet.setup(target-direction*180.0,direction,victim,Color.WHITE,{"projectile_profile":"PRJ_ASTER_TEST"})
        var before := actor.health
        await settle(18)
        var expected := 3.5 if direction==Vector2.LEFT else 10.0
        check(is_equal_approx(before-actor.health,expected),"Real bullet front/side/rear armour damage")
        if is_instance_valid(bullet): bullet.queue_free()
    actor.queue_free(); await settle()

func check_ram_collision() -> void:
    var actor := spawn("ENM_SITE7_RAM_01"); await settle()
    # A real StaticBody wall, not an aim-only occlusion flag.
    var wall := StaticBody2D.new(); wall.collision_layer=1
    var collider := CollisionShape2D.new(); var shape := RectangleShape2D.new()
    shape.size=Vector2(12,200); collider.shape=shape; wall.add_child(collider)
    stage.add_child(wall); wall.position=actor.position+Vector2(70,-18)
    victim.global_position=actor.global_position+Vector2(105,0)
    var hp := victim.health
    actor.tactics.locked_ground=Vector2.RIGHT; actor.tactics.locked_aim=Vector2.RIGHT
    actor.tactics._lunge_origin=actor.position; actor.tactics._lunge_reach=151.2
    actor.tactics._enter("LUNGE",0.42)
    actor.machine_sprite.face_direction(Vector2.RIGHT)
    actor.set_physics_process(true); await settle(14); actor.set_physics_process(false)
    check(actor.position.x < wall.position.x,"Ram stopped by actual wall")
    check(victim.health==hp,"Ram cannot damage through wall")
    check(actor.tactics.state=="RECOVER","Wall collision cancels lunge")
    await capture(actor,"ram_wall_collision")
    wall.queue_free(); actor.queue_free(); await settle()

func check_mortar_impact() -> void:
    var actor := spawn("ENM_SITE7_MORTAR_01"); await settle()
    victim.global_position=actor.position+Vector2(-120,80)
    actor.tactics.locked_landing=victim.global_position
    actor.tactics._launch_mortar()
    var shell: Node2D=get_nodes_in_group("site7_mortar_shells")[-1]
    var fixed: Vector2=shell.landing
    var hp := victim.health
    check(shell.arc_point(0.01).y<shell.origin.y,"Shell ascends from vertical barrel")
    await settle(18); await capture(actor,"mortar_in_flight")
    check(shell.landing==fixed,"Mortar landing remains locked")
    await settle(50)
    check(victim.health<hp,"Actual mortar impact damages victim inside marked circle")
    await capture(actor,"mortar_impact")
    await settle(20)
    actor.tactics._launch_mortar()
    victim.global_position=fixed+Vector2(150,0)
    hp=victim.health
    await settle(70)
    check(victim.health==hp,"Moving outside mortar mark avoids damage")
    actor.apply_damage(1000.0)
    await capture(actor,"mortar_death")
    actor.queue_free(); await settle()
