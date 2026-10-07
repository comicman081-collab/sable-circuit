extends SceneTree
## Normal registry intake and state-machine emissions, no QA texture injection.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const NAMES := ["E","SE","S","SW","W","NW","N","NE"]
const TestOutput := preload("res://tests/support/test_output.gd")
var checks := 0
var failures: Array[String] = []
var emissions: Array[Dictionary] = []

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks+=1
    if not ok: failures.append(label);push_error(label)

func run() -> void:
    check(bool(ProjectSettings.get_setting("sable_visuals/site7_authored_machines",true)),"Default app intake enabled")
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_DRONE_01",62.0)
    root.add_child(actor);actor.set_physics_process(false)
    check(is_instance_valid(actor.machine_sprite),"Normal spawn binds registry without preview injection")
    if not is_instance_valid(actor.machine_sprite):quit(1);return
    actor.machine_sprite.set_process(false)
    check(actor.machine_sprite.views.size()==8 and actor.machine_sprite.facing=="W","All views and initial left facing")
    check(not actor._visual_root.visible and actor.machine_sprite.visible,"Mock hidden, authored machine visible")
    check(actor.max_health==62.0 and actor.enemy_id=="ENM_SITE7_DRONE_01","No gameplay health/identity override")
    var binding: Dictionary=actor.art_profile.machine_asset
    var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(binding.spec))
    check(FileAccess.get_sha256(binding.spec)==binding.sha256,"Registry binds exact versioned spec")
    for name in NAMES:
        var view: Dictionary=spec.views[name]
        check(str(view.texture).begins_with("res://assets/enemies/recon_drone/") and not "/qa/" in str(view.texture),"Runtime texture is not a QA path "+name)
        check(FileAccess.get_sha256(view.texture)==view.texture_sha256,"Exact reviewed texture "+name)
    var victim := OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    actor.projectile_emitted.connect(func(event: Dictionary) -> void:emissions.append(event))
    for hz in [30,60,120]:
        for i in range(8):
            emissions.clear()
            var direction := Vector2.from_angle(i*PI/4.0)
            victim.global_position=Vector2(0,-60)+direction*500.0
            actor.velocity=-direction*118.0
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.step(victim,1.0/hz)
            var locked: Vector2=actor.tactics.locked_aim
            check(actor.tactics.state=="WINDUP","Normal warning entered")
            check(actor.machine_sprite.visible_heading_world().dot(locked)>cos(PI/8.0+0.02),"Front agrees with announced shot")
            # Adversarial target reversal after the warning has been advertised.
            victim.global_position=Vector2(0,-60)-direction*500.0
            for tick in range(hz):
                actor.tactics.step(victim,1.0/hz)
                if not emissions.is_empty():break
            check(emissions.size()==1,"Actual timed state transition emits exactly one shot")
            if emissions.size()==1:
                var shot:=instance_from_id(emissions[0].projectile_id) as PrototypeProjectile
                check(shot.global_position.distance_to(actor.machine_sprite.muzzle_world())<0.001,"Actual shot starts at illustrated emitter")
                check(actor.machine_sprite.visible_heading_world().dot(locked)>cos(PI/8.0+0.02),"No reversed body at emission")
                shot.free()
            actor.tactics.state="RECOVER";actor.tactics.state_left=1.0
            actor.tactics.step(victim,1.0/hz)
            check(actor.machine_sprite.visible_heading_world().dot(locked)<-0.8,"Recovery follows the new opposite target")
    var prior:=actor.machine_sprite
    check(not prior.configure(actor,spec),"Repeated configure rejected atomically")
    check(prior.configured and prior.views.size()==8,"Rejected reconfigure preserves visible source")
    check(not actor.configure("ENM_SITE7_RIFLE_01",100.0),"Retired rifle role change is rejected")
    check(actor.is_queued_for_deletion() and not actor.is_visible_in_tree(),"Rejected role hides actor without restoring a humanoid placeholder")
    check(not actor.preview_machine_source(spec),"Drone spec cannot attach to humanoid")
    actor.free();victim.free()
    await process_frame
    var hashes: Dictionary={}
    for path in ["scripts/animation/site7_machine_sprite.gd","scripts/actors/enemy_actor.gd","scripts/combat/site7_enemy_tactics.gd","data/art_profiles/enemy_profiles.json","assets/enemies/recon_drone/authored_yaw8_v1/spec.json","tests/smoke/site7_drone_app_smoke.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    var out := TestOutput.path("res://qa/stage1_implementation_20260913/drone_app_"+str(Time.get_unix_time_from_system()).replace(".","_")+".json")
    var file:=FileAccess.open(out,FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"sha256":hashes,"candidate_injection":false,"visual_approval":false},"  "));file.close()
    print("SITE7_DRONE_APP_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks) ",out)
    quit(0 if failures.is_empty() else 1)
