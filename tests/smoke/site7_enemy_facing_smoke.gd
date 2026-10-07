extends SceneTree
## Real node transforms and emitted shots, not an approval of painted yaw angles.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
var checks := 0
var failures: Array[String] = []
var emissions: Array[Dictionary] = []

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func run() -> void:
    ProjectSettings.set_setting("sable_visuals/site7_authored_machines",false)
    # The registry's reviewed spec (the 2026-09-13 QA candidates were retired).
    var spec := EnemyActor.reviewed_machine_spec("ENM_SITE7_DRONE_01")
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_DRONE_01",620.0)
    root.add_child(actor); actor.set_physics_process(false)
    check(actor.preview_machine_source(spec),"Eight native views bind")
    if not is_instance_valid(actor.machine_sprite): quit(1); return
    actor.machine_sprite.set_process(false)
    check(actor.machine_sprite.facing=="W","Initial frame respects actor's current left aim")
    actor.projectile_emitted.connect(func(row: Dictionary) -> void: emissions.append(row))
    var victim := OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim); victim.set_physics_process(false)
    for hz in [30,60,120]:
        for i in range(8):
            var dir := Vector2.from_angle(i*PI/4.0)
            # Target point, not movement velocity, owns the visual front.
            victim.global_position = actor.global_position + Vector2(0,-75) + dir*520.0
            actor.velocity = -dir*118.0
            actor.tactics.state="REPOSITION"; actor.tactics.state_left=0.0
            actor.tactics.step(victim,1.0/hz)
            var view := str(actor.machine_sprite.facing)
            var ray: Vector2 = actor.tactics.locked_aim
            var front: Vector2 = actor.machine_sprite.visible_heading_world()
            check(front.dot(ray)>cos(PI/8.0+0.02),"Visual yaw agrees with actual target ray")
            check(not actor.machine_sprite.sprite.flip_h,"No mirrored directional art")
            var muzzle: Vector2 = actor.machine_sprite.muzzle_world()
            check(absf(ray.cross((victim.get_combat_aim_point()-muzzle).normalized()))<0.0001,"Visible emitter ray targets initial player")
            # Move the victim BEHIND the drone during the announced shot.
            victim.global_position=actor.global_position+Vector2(0,-75)-dir*520.0
            actor.tactics.step(victim,1.0/hz)
            check(actor.machine_sprite.facing==view,"Windup does not turn body toward later target")
            check(actor.tactics.locked_aim.is_equal_approx(ray),"Windup does not home")
            emissions.clear()
            actor.tactics._fire(ray)
            # Audio feedback is also a root child, but it is not a projectile.
            check(emissions.size()==1,"One actual projectile")
            var shot := instance_from_id(emissions[0].projectile_id) as PrototypeProjectile
            check(shot.global_position.distance_to(muzzle)<0.001,"Shot starts at selected illustrated emitter")
            check(actor.machine_sprite.facing==view,"Emission keeps announced pose")
            shot.free()
            # Recovery must respond on the next step, with no gait/cooldown gate.
            actor.tactics.state="RECOVER";actor.tactics.state_left=1.0
            actor.tactics.step(victim,1.0/hz)
            check(actor.machine_sprite.visible_heading_world().dot(ray)<-0.80,"Opposite target immediately selects opposite view")
    # Fail closed: a seven-view or duplicate-pixel set is not yaw8.
    for mutation in ["missing", "duplicate", "single"]:
        var bad: Dictionary = spec.duplicate(true)
        if mutation=="missing": bad.views.erase("NW")
        elif mutation=="duplicate": bad.views["NW"]=bad.views["E"].duplicate(true)
        else: bad.erase("views")
        var stub := ENEMY.instantiate() as EnemyActor
        stub.configure("ENM_SITE7_DRONE_01",620.0);root.add_child(stub);stub.set_physics_process(false)
        check(not stub.preview_machine_source(bad),"Reject "+mutation+" facing set")
        check(stub.machine_sprite==null and stub._visual_root.visible,"Rejected intake leaves prior visual intact")
        stub.free()
    actor.free();victim.free()
    # The humanoid RIFLE/SHIELD barrel checks were removed with the zero-humanoid-enemy rule.
    # Let normal feedback nodes expire; do not leave pending sound/effect instances.
    for i in range(80): await process_frame
    print("SITE7_ENEMY_FACING_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)
