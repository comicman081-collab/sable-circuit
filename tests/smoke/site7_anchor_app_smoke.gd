extends SceneTree
## Normal app registry intake, not an injected QA candidate or visual approval.
const ENEMY:=preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR:=preload("res://scenes/actors/player/OperatorActor.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")
var failures: Array[String]=[]
var checks:=0
var emissions: Array[Dictionary]=[]
func _init() -> void:call_deferred("run")
func check(ok: bool,label: String) -> void:
    checks+=1
    if not ok:failures.append(label);push_error(label)
func run() -> void:
    var actor:=ENEMY.instantiate() as EnemyActor
    actor.configure("BOSS_SITE7_ANCHOR_01",620.0)
    root.add_child(actor);actor.set_physics_process(false)
    check(is_instance_valid(actor.machine_sprite),"Normal registry activates anchored art")
    if not is_instance_valid(actor.machine_sprite):quit(1);return
    actor.machine_sprite.set_process(false)
    var spec: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(actor.art_profile.machine_asset.spec))
    check(FileAccess.get_sha256(actor.art_profile.machine_asset.spec)==actor.art_profile.machine_asset.sha256,"Exact spec hash")
    check(str(spec.texture).begins_with("res://assets/enemies/signal_anchor_guardian/") and not "/qa/" in str(spec.texture),"Runtime-owned texture")
    check(FileAccess.get_sha256(spec.texture)==spec.texture_sha256,"Exact authored image bytes")
    check(actor.health==620.0 and actor.max_health==620.0,"No gameplay HP substitution")
    check(actor.machine_sprite.kind=="anchored_machine" and actor.machine_sprite.views.size()==1,"Fixed structure, not manufactured yaw8")
    check(not actor._visual_root.visible,"Old mock hidden after valid intake")
    var victim:=OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    actor.projectile_emitted.connect(func(row: Dictionary) -> void:emissions.append(row))
    var iris: Vector2=actor.machine_sprite.muzzle_world()
    for hz in [30,60,120]:
        for sector in range(8):
            emissions.clear()
            victim.global_position=actor.global_position+Vector2.from_angle(sector*PI/4.0)*500.0
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0;actor.tactics.attack_serial=0
            actor.tactics.step(victim,1.0/hz)
            var locked: Vector2=actor.tactics.locked_aim
            check(actor.tactics.state=="WINDUP","Actual warning entered")
            check(locked.dot(victim.get_combat_aim_point()-iris)>0.0,"Warning aims from actual iris to initial target")
            victim.global_position=-victim.global_position
            for tick in range(hz+2):
                actor.tactics.step(victim,1.0/hz)
                if actor.tactics.state=="RECOVER":break
            check(emissions.size()==3,"Actual phase-1 transition emits three and only three")
            check(actor.machine_sprite.rotation==0.0 and actor.machine_sprite.position==Vector2.ZERO,"Chassis remains fixed")
            check(actor.machine_sprite.muzzle_world().distance_to(iris)<0.001,"Iris does not chase new target")
            for i in range(emissions.size()):
                var shot:=instance_from_id(emissions[i].projectile_id) as PrototypeProjectile
                check(shot.global_position.distance_to(iris)<0.001,"Created projectile originates at iris")
                var direction:=Vector2(emissions[i].direction[0],emissions[i].direction[1])
                check(direction.distance_to(locked.rotated((i-1)*0.22))<0.0001,"Fan keeps locked warning orientation")
                shot.free()
    actor.free();victim.free()
    await process_frame
    var hashes: Dictionary={}
    for path in ["scripts/actors/enemy_actor.gd","scripts/animation/site7_machine_sprite.gd","scripts/combat/site7_enemy_tactics.gd","scripts/ui/enemy_overhead_ui.gd","data/art_profiles/enemy_profiles.json","assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json","tests/smoke/site7_anchor_app_smoke.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    var out:=TestOutput.path("res://qa/stage1_implementation_20260913/anchor_app_"+str(Time.get_unix_time_from_system()).replace(".","_")+".json")
    var file:=FileAccess.open(out,FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"hashes":hashes,"candidate_injection":false,"visual_approval":false},"  "));file.close()
    print("SITE7_ANCHOR_APP_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks) ",out)
    quit(0 if failures.is_empty() else 1)
