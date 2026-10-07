extends SceneTree
## Controlled facing cases in the real Stage 1 scene. Not a playthrough.
## Each case starts a fresh, normal-health battle preview and advances the
## actual tactics state machine; it never calls the emission function directly.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAMES := ["E","SE","S","SW","W","NW","N","NE"]
var out := "res://qa/stage1_implementation_20260913/facing_native_" + str(Time.get_unix_time_from_system()).replace(".","_")
var rows: Array[Dictionary] = []
var failures: Array[String] = []
var emissions: Array[Dictionary] = []
var use_app_registry := "--app-registry" in OS.get_cmdline_user_args()

func _init() -> void: call_deferred("run")

func settle(count: int) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func capture(actor: EnemyActor, victim: OperatorActor, label: String) -> void:
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    var path := out + "/" + label + ".webp"
    if image.get_size() != Vector2i(1920,1080) or image.save_webp(path,true,0.94) != OK:
        failures.append("Native capture failed: "+label)
    rows.append({"image":path,"sha256":FileAccess.get_sha256(path),"native":[1920,1080],
        "label":label,"physics_tick":Engine.get_physics_frames(),"wall_ms":Time.get_ticks_msec(),
        "actor_position":actor.global_position,"target_aim_point":victim.get_combat_aim_point(),
        "machine":actor.machine_sprite.debug_contract(),"tactics":actor.tactics.contract(),
        "actual_emissions":emissions.duplicate(true)})

func run() -> void:
    ProjectSettings.set_setting("sable_visuals/site7_authored_machines",use_app_registry)
    root.size = Vector2i(1920,1080)
    root.content_scale_size = Vector2i(1280,720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    for i in range(8):
        var stage := STAGE.instantiate() as StoryStage01
        stage.battle_preview=true
        root.add_child(stage)
        await settle(5)
        stage.start_battle_preview(1)
        await settle(2)
        stage.set_process(false)
        stage.squad.set_process(false)
        stage.squad.set_physics_process(false)
        var actor: EnemyActor
        for enemy in get_nodes_in_group("m3_enemies"):
            enemy.set_physics_process(false)
            if enemy.enemy_id=="ENM_SITE7_DRONE_01": actor=enemy
            else: enemy.hide()
        if actor==null or (not is_instance_valid(actor.machine_sprite) if use_app_registry else not actor.preview_machine_source(EnemyActor.reviewed_machine_spec(actor.enemy_id))):
            failures.append("Missing drone intake"); stage.queue_free(); await settle(2); continue
        actor.global_position=Vector2(690,350)
        stage.camera.global_position=actor.global_position+Vector2(0,-85)
        stage.camera.position_smoothing_enabled=false
        var victim: OperatorActor
        for operator in get_nodes_in_group("operators"):
            operator.debug_drive(Vector2.ZERO,Vector2.LEFT)
            if operator.operator_id=="CHR_PROTO_01": victim=operator
            else: operator.hide(); operator.set_physics_process(false)
        var direction := Vector2.from_angle(i*PI/4.0)
        # Place the target by its actual aim point after the initial view is
        # selected. Avoid confusing floor positions with elevated emitters.
        actor.machine_sprite.face_direction(direction)
        var target_offset := victim.get_combat_aim_point()-victim.global_position
        victim.global_position=actor.machine_sprite.muzzle_world()+direction*160.0-target_offset
        victim.debug_drive(Vector2.ZERO,-direction)
        victim.set_physics_process(false)
        actor.tactics.state="REPOSITION"; actor.tactics.state_left=0.0
        emissions.clear()
        actor.projectile_emitted.connect(func(row: Dictionary) -> void: emissions.append(row))
        actor.tactics.step(victim,1.0/60.0)
        await settle(2)
        await capture(actor,victim,NAMES[i]+"_windup_start")
        for tick in range(38):
            actor.tactics.step(victim,1.0/60.0)
            await settle(1)
            if tick==15: await capture(actor,victim,NAMES[i]+"_windup_mid")
            if emissions.size()>0:
                await capture(actor,victim,NAMES[i]+"_actual_emission")
                break
        if emissions.size()!=1: failures.append(NAMES[i]+" expected one actual state-machine emission")
        stage.queue_free()
        for child in root.get_children():
            if child is PrototypeProjectile: child.queue_free()
        await settle(3)
    var hashes := {}
    for path in ["res://scripts/animation/site7_machine_sprite.gd","res://scripts/actors/enemy_actor.gd","res://scripts/combat/site7_enemy_tactics.gd","res://tests/render/site7_enemy_facing_capture.gd","res://data/art_profiles/enemy_profiles.json","res://assets/enemies/recon_drone/authored_yaw8_v1/spec.json"]:
        hashes[path]=FileAccess.get_sha256(path)
    var file := FileAccess.open(out+"/capture_report.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"CAPTURED_CONTROLLED_CASES_NOT_VISUAL_APPROVAL","app_registry":use_app_registry,"failures":failures,"rows":rows,"sha256":hashes},"  "))
    file.close()
    print("SITE7_FACING_CAPTURE: ","PASS_CAPTURE_ONLY" if failures.is_empty() else "FAIL"," ",out)
    quit(0 if failures.is_empty() else 1)
