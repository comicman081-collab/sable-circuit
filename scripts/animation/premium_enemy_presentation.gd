extends Node2D
class_name PremiumEnemyPresentation

var actor: EnemyActor
var _last_hit := 0.0
var _hit_kick := 0.0
var _phase_index := 1
var _boss_pattern_cd := 1.4
var _last_sector := -1

func _ready() -> void:
    process_priority = 90
    actor = get_parent() as EnemyActor
    if actor:
        actor.defeated.connect(_on_defeated)

func _process(delta: float) -> void:
    if actor == null or not is_instance_valid(actor):
        return
    var hit := float(actor.get("_hit_flash"))
    if hit > 0.78 and _last_hit <= 0.78:
        _hit_kick = 1.0
    _last_hit = hit
    _hit_kick = move_toward(_hit_kick, 0.0, delta * _hit_recover_rate())
    _apply_directional_depth()
    _apply_unique_hit_reaction()
    if "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id:
        _update_boss_phase(delta)
    queue_redraw()

func _hit_recover_rate() -> float:
    if "SHIELD" in actor.enemy_id: return 2.7
    if "DRONE" in actor.enemy_id: return 6.5
    if "ABERRANT" in actor.enemy_id: return 4.2
    if "BOSS" in actor.enemy_id: return 1.9
    return 5.0

func _sector_from_dir(dir: Vector2) -> int:
    if dir.length_squared() < 0.001:
        return 4
    return int(floor(fposmod(dir.angle() + PI / 8.0, TAU) / (PI / 4.0))) % 8

func _apply_directional_depth() -> void:
    var aim: Vector2 = actor.get("_aim_dir")
    var sector := _sector_from_dir(aim)
    var left := sector in [3,4,5]
    var rear := sector in [5,6,7]
    var parts: Dictionary = actor.get("_parts")
    for name in parts.keys():
        var sprite := parts[name] as Sprite2D
        if sprite == null:
            continue
        if "DRONE" not in actor.enemy_id and "BOSS" not in actor.enemy_id:
            sprite.flip_h = left
        sprite.modulate = Color(0.78,0.84,0.90,1.0) if rear else Color.WHITE
    if parts.has("Rifle"):
        (parts["Rifle"] as Sprite2D).z_index = -1 if rear else 6
    if parts.has("RamPistol"):
        (parts["RamPistol"] as Sprite2D).z_index = -1 if rear else 6
    if parts.has("SlabShield"):
        (parts["SlabShield"] as Sprite2D).z_index = 7 if sector in [2,3,4] else 3
    _last_sector = sector

func _apply_unique_hit_reaction() -> void:
    var bones: Dictionary = actor.get("_bones")
    var bases: Dictionary = actor.get("_base_positions")
    if bones.is_empty():
        return
    var k := _hit_kick
    if "RIFLE" in actor.enemy_id and bones.has("body"):
        var body := bones["body"] as Bone2D
        body.rotation += k * 0.16
        body.position = (bases.get("body", body.position) as Vector2) + Vector2(-k * 8.0, 0)
        if bones.has("weapon"): (bones["weapon"] as Bone2D).rotation -= k * 0.18
    elif "SHIELD" in actor.enemy_id and bones.has("body"):
        var body := bones["body"] as Bone2D
        body.position = (bases.get("body", body.position) as Vector2) + Vector2(-k * 4.0, k * 3.0)
        if bones.has("shield"): (bones["shield"] as Bone2D).rotation -= k * 0.23
        if bones.has("hydraulic_arm"): (bones["hydraulic_arm"] as Bone2D).rotation += k * 0.12
    elif "DRONE" in actor.enemy_id and bones.has("chassis"):
        var chassis := bones["chassis"] as Bone2D
        chassis.rotation += sin(k * PI) * 0.28
        chassis.position = (bases.get("chassis", chassis.position) as Vector2) + Vector2(k * 7.0, -k * 4.0)
        if bones.has("sensor_cluster"): (bones["sensor_cluster"] as Bone2D).scale = Vector2.ONE * (1.0 + k * 0.18)
    elif "ABERRANT" in actor.enemy_id and bones.has("torso"):
        var torso := bones["torso"] as Bone2D
        torso.rotation -= k * 0.24
        torso.scale = Vector2(1.0 - k * 0.09, 1.0 + k * 0.14)
        if bones.has("skull"): (bones["skull"] as Bone2D).rotation += k * 0.31
        if bones.has("tail"): (bones["tail"] as Bone2D).rotation -= k * 0.48
    elif ("BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id) and bones.has("iris"):
        (bones["iris"] as Bone2D).scale = Vector2.ONE * (1.0 + k * 0.22)
        for i in range(1,5):
            var key := "arm_%d" % i
            if bones.has(key): (bones[key] as Bone2D).rotation += k * (0.08 + i * 0.018) * (-1.0 if i % 2 == 0 else 1.0)

func _update_boss_phase(delta: float) -> void:
    var ratio := actor.health / maxf(1.0, actor.max_health)
    var new_phase := 1 if ratio > 0.66 else (2 if ratio > 0.33 else 3)
    if new_phase != _phase_index:
        _phase_index = new_phase
        _boss_pattern_cd = 0.35
        ImpactFeel.boss_phase_changed(actor.get_tree(), new_phase)
    var bones: Dictionary = actor.get("_bones")
    if not bones.has("ring"):
        return
    var ring := bones["ring"] as Bone2D
    var iris := bones["iris"] as Bone2D if bones.has("iris") else null
    if _phase_index == 2:
        ring.scale = Vector2.ONE * (1.04 + sin(Time.get_ticks_msec() * 0.004) * 0.025)
        if iris: iris.rotation -= 0.018
        for i in range(1,5):
            var p := bones.get("pylon_%d"%i) as Bone2D
            if p: p.rotation += (0.07 if i % 2 == 0 else -0.07)
    elif _phase_index == 3:
        ring.scale = Vector2.ONE * (1.09 + sin(Time.get_ticks_msec() * 0.006) * 0.04)
        if iris:
            iris.scale = Vector2.ONE * (1.10 + sin(Time.get_ticks_msec() * 0.009) * 0.12)
            iris.rotation -= 0.035
        for i in range(1,5):
            var arm := bones.get("arm_%d"%i) as Bone2D
            if arm: arm.rotation += sin(Time.get_ticks_msec() * 0.005 + i) * 0.13
        actor.set("_attack_cd", minf(float(actor.get("_attack_cd")), 0.58))

    _boss_pattern_cd -= delta
    if _boss_pattern_cd <= 0.0:
        _fire_phase_pattern()
        _boss_pattern_cd = 2.35 if _phase_index == 2 else (1.35 if _phase_index == 3 else 3.0)

func _fire_phase_pattern() -> void:
    if _phase_index <= 1:
        return
    var aim: Vector2 = actor.get("_aim_dir")
    CombatFeedback.play_fire(actor.get_tree(), actor.art_profile)
    if _phase_index == 2:
        for a in [-0.42, -0.21, 0.21, 0.42]:
            actor.call("_spawn_projectile", aim.rotated(a))
    else:
        for a in [-0.62, -0.31, 0.0, 0.31, 0.62]:
            actor.call("_spawn_projectile", aim.rotated(a))

func _on_defeated(_enemy: EnemyActor) -> void:
    if actor == null:
        return
    ImpactFeel.enemy_defeated(actor.get_tree(), actor.enemy_id)
    var seq := EnemyDeathSequence.new()
    actor.get_tree().root.add_child(seq)
    seq.setup(actor.global_position, actor.enemy_id, actor.art_profile)

func _draw() -> void:
    if actor == null or not ("BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id):
        return
    if _phase_index >= 2:
        var pulse := fposmod(Time.get_ticks_msec() * 0.0006, 1.0)
        var col := Color(0.55,0.38,1.0,(1.0-pulse)*0.35)
        if _phase_index == 3:
            col = Color(0.96,0.25,0.62,(1.0-pulse)*0.46)
        draw_arc(Vector2(0,-110), 92.0 + pulse * 90.0, 0.0, TAU, 64, col, 3.0 + _phase_index)

func debug_phase() -> int:
    return _phase_index

func debug_sector() -> int:
    return _last_sector
