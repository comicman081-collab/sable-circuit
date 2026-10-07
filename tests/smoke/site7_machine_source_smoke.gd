extends SceneTree
## Reviewed-spec binding and real projectile-origin tests, not visual PASS.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("run")

func check(value: bool, label: String) -> void:
    checks += 1
    if not value:
        failures.append(label)
        push_error(label)

func run() -> void:
    # Bind the registry's reviewed spec explicitly (the 2026-09-13 QA candidates were retired).
    ProjectSettings.set_setting("sable_visuals/site7_authored_machines",false)
    for id in ["ENM_SITE7_DRONE_01","BOSS_SITE7_ANCHOR_01"]:
        var actor := ENEMY.instantiate() as EnemyActor
        actor.configure(id,620.0)
        root.add_child(actor)
        actor.set_physics_process(false)
        check(actor.preview_machine_source(EnemyActor.reviewed_machine_spec(id)),id+" reviewed spec binds")
        await process_frame
        await process_frame
        var sprite: Node2D = actor.machine_sprite
        check(is_instance_valid(sprite),id+" raster selected")
        if not is_instance_valid(sprite):continue
        check(not actor._visual_root.visible,id+" previous body hidden")
        # The runtime adds only the object-space weathering shader, which keeps source alpha.
        var weathering := sprite.sprite.material as ShaderMaterial
        check(weathering != null and weathering.shader.resource_path == "res://assets/shaders/machine_weathering.gdshader",id+" only the weathering shader over ImageGen authored pixels")
        var victim := OPERATOR.instantiate() as OperatorActor
        victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
        root.add_child(victim);victim.set_physics_process(false)
        victim.global_position = Vector2(450,120)
        for hz in [30,60,120]:
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.step(victim,1.0/hz)
            var locked: Vector2 = actor.tactics.locked_aim
            var target_point := victim.get_combat_aim_point()
            var actual_origin: Vector2 = sprite.sprite.to_global(sprite.emitter_px)
            check(absf(locked.cross((target_point-actual_origin).normalized()))<0.00001,"Telegraph ray originates at visible emitter")
            check(locked.dot(target_point-actual_origin)>0,"Telegraph points toward initial target")
            victim.global_position += Vector2(70,-45)
            actor.tactics.step(victim,1.0/hz)
            check(actor.tactics.locked_aim.is_equal_approx(locked),"Later target motion cannot home a telegraphed ray")
        victim.free()
        actor.rotation=0.13
        actor.scale=Vector2(0.8,1.2)
        for hz in [30,60,120]:
            for i in range(8):
                var dir := Vector2.from_angle(i * PI / 4.0)
                actor.velocity = dir * 118.0
                sprite._process(1.0 / hz)
                var expected: Vector2 = sprite.sprite.to_global(sprite.emitter_px)
                var bounds: Rect2 = sprite.hit_rect_world()
                var overhead: EnemyOverheadUI=actor.get_node("OverheadUI")
                var clears_all:=true
                for corner in [Vector2.ZERO,Vector2(sprite.image_size.x,0),sprite.image_size,Vector2(0,sprite.image_size.y)]:
                    clears_all=clears_all and overhead.bar_y_local()<=overhead.to_local(sprite.sprite.to_global(corner)).y-11.99
                check(clears_all,"Health bar clears full authored machine, including pylons and bank")
                for point in [Vector2(0.13,0.16),Vector2(0.87,0.16),Vector2(0.87,0.84),Vector2(0.13,0.84)]:
                    check(bounds.has_point(sprite.sprite.to_global(sprite.image_size*point)),"Machine AABB covers transformed native region")
                check(sprite.muzzle_world().distance_to(expected)<0.001,id+" emitter follows visible source transform")
                if id.begins_with("BOSS"):
                    check(sprite.position == Vector2.ZERO and sprite.rotation == 0.0,"Anchor stays anchored")
                var previous := root.get_child_count()
                actor._spawn_projectile(dir)
                # The shot also leaves a muzzle flash beside it; count projectiles only.
                var fresh := root.get_children().slice(previous)
                var shots := fresh.filter(func(n): return n is PrototypeProjectile)
                check(shots.size() == 1,"One emitter, one projectile")
                var projectile := shots[0] as PrototypeProjectile
                check(projectile.global_position.distance_to(expected)<0.001,"Projectile starts at actual authored iris/orb")
                for n in fresh:
                    n.free()
        actor.apply_damage(10000.0)
        check(get_nodes_in_group("enemy_death_sequences").is_empty(),"No old SVG death fragments")
        actor.free()
    print("SITE7_MACHINE_SOURCE_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)
