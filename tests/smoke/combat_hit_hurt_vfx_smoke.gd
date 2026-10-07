extends SceneTree
## Volumetric impact and hurt-reaction VFX: every live profile routes by the round's
## direction, target reactions escalate with the share of health a hit took, and the
## actors raise them from their normal damage path. Heavy hits and blasts shake the squad
## camera unless the player turned screen shake off (checked in memory, never saved).

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const IMPACT_PROFILES := ["HIT_ASTER_PRISM_01", "HIT_ROOK_CRUSH_01", "HIT_MICA_SCANBURST_01",
    "HIT_ENM_DRONE_ARC_01", "HIT_BOSS_ANCHOR_RIFT_01", "HIT_GENERIC"]

var failures: Array[String] = []
var checks := 0
var shake: SquadCameraPresentation

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    GameSettings.load_once()
    GameSettings.screen_shake = true
    shake = SquadCameraPresentation.new()
    root.add_child(shake)
    shake.camera = Camera2D.new()
    root.add_child(shake.camera)
    _verify_impacts()
    _verify_reactions()
    await _verify_operator()
    await _verify_robot()
    await _verify_boss()
    _verify_shake()
    for node in _vfx():
        node.call("_process", 5.0)
    await _frames(2)
    _check(_vfx().is_empty(), "every impact and hurt effect frees itself after its lifetime")
    if failures.is_empty():
        print("COMBAT_HIT_HURT_VFX_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _verify_impacts() -> void:
    var travel := Vector2(0.94, -0.34).normalized()
    for profile_id in IMPACT_PROFILES:
        CombatFeedback.spawn_hit(self, Vector2(400, 300), {"hit_vfx_profile": profile_id}, Color("6fe7ff"), null, travel)
        var vfx: CombatHitVFX = _vfx()[-1]
        var contract := vfx.debug_vfx_contract()
        var axis := Vector2(contract.directional_axis)
        _check(contract.effect_kind == CombatHitVFX.EFFECT_IMPACT and contract.profile_id == profile_id and float(contract.lifetime) >= 0.38, profile_id + " impact contract")
        _check(bool(contract.volumetric_layer) and bool(contract.practical_light), profile_id + " has the volume layer and desktop flash light")
        _check(axis.dot(-travel) > 0.999, profile_id + " sparks spray back against the round's travel")
        _check(vfx.z_index == 3100 and vfx.scale.x < 1.0, profile_id + " keeps the actor-over depth and runtime draw scale")
        vfx.free()

func _verify_reactions() -> void:
    _check(CombatFeedback.hurt_reaction(3.0, 97.0, 100.0) == "FLINCH", "under 4% of health flinches")
    _check(CombatFeedback.hurt_reaction(5.0, 95.0, 100.0) == "LIGHT", "4% of health is a light reaction")
    _check(CombatFeedback.hurt_reaction(14.0, 86.0, 100.0) == "HEAVY", "14% of health is a heavy reaction")
    _check(CombatFeedback.hurt_reaction(5.0, 0.0, 100.0) == "DOWNED", "reaching zero is downed")
    var previous := 0.0
    for reaction in ["FLINCH", "LIGHT", "HEAVY", "DOWNED"]:
        var vfx := CombatHitVFX.new()
        root.add_child(vfx)
        vfx.setup_hurt("ENEMY", "ENM_SITE7_BULWARK_01", reaction, Color("d84d59"))
        var lifetime := float(vfx.debug_vfx_contract().lifetime)
        _check(lifetime > previous, reaction + " lasts longer than the lighter reaction")
        previous = lifetime
        vfx.free()

func _verify_operator() -> void:
    var actor := OPERATOR_SCENE.instantiate() as OperatorActor
    actor.configure("CHR_PROTO_02", "ROOK", Color("ffb45c"))
    actor.global_position = Vector2(320, 360)
    root.add_child(actor)
    await process_frame
    actor.set_physics_process(false)
    shake.trauma = 0.0
    actor.apply_damage(actor.max_health * 0.2)
    _check(shake.trauma > 0.0, "a heavy hit on an operator shakes the camera")
    var hurt := _latest_hurt("CHR_PROTO_02")
    _check(hurt != null and hurt.debug_vfx_contract().target_kind == "OPERATOR" and hurt.debug_vfx_contract().reaction == "HEAVY", "operator damage raises a heavy hurt reaction")
    _check(hurt != null and actor.get_combat_hit_rect().has_point(hurt.global_position), "operator hurt sits on the operator's body")
    actor.apply_damage(99999.0)
    hurt = _latest_hurt("CHR_PROTO_02")
    _check(hurt != null and hurt.debug_vfx_contract().reaction == "DOWNED", "the downing hit shows a downed reaction")
    actor.queue_free()
    await process_frame

func _verify_robot() -> void:
    var enemy := ENEMY_SCENE.instantiate() as EnemyActor
    enemy.configure("ENM_SITE7_BULWARK_01", 200.0)
    enemy.global_position = Vector2(640, 360)
    root.add_child(enemy)
    await process_frame
    enemy.set_physics_process(false)
    var before := _hurt_count()
    shake.trauma = 0.0
    enemy.apply_damage(2.0)
    _check(shake.trauma == 0.0, "small hits on robots do not shake the camera")
    _check(_hurt_count() == before + 1 and _latest_hurt(enemy.enemy_id).debug_vfx_contract().reaction == "FLINCH", "a small hit on a robot flinches")
    enemy.apply_damage(2.0)
    _check(_hurt_count() == before + 1, "a second small hit within 90 ms adds no extra reaction")
    enemy.apply_damage(40.0)
    _check(_hurt_count() == before + 2 and _latest_hurt(enemy.enemy_id).debug_vfx_contract().reaction == "HEAVY", "a heavy hit always reacts")
    enemy.apply_damage(99999.0)
    _check(_hurt_count() == before + 2, "the killing hit leaves the reaction to the death sequence")
    enemy.queue_free()
    await process_frame

func _verify_boss() -> void:
    var boss := ENEMY_SCENE.instantiate() as EnemyActor
    boss.configure("BOSS_SITE7_ANCHOR_01", 900.0)
    boss.global_position = Vector2(960, 360)
    root.add_child(boss)
    await process_frame
    boss.set_physics_process(false)
    boss.apply_damage(60.0)
    var hurt := _latest_hurt(boss.enemy_id)
    _check(hurt != null and hurt.debug_vfx_contract().target_kind == "BOSS" and float(hurt.debug_vfx_contract().lifetime) > 0.3, "boss damage raises the larger boss reaction")
    boss.queue_free()
    await process_frame

func _verify_shake() -> void:
    shake.trauma = 0.0
    SquadCameraPresentation.kick(self, 0.5)
    _check(is_equal_approx(shake.trauma, 0.5), "a kick adds trauma to the squad camera")
    shake._apply_shake(0.1)
    _check(shake.camera.offset.length() <= SquadCameraPresentation.SHAKE_MAX_OFFSET * 1.5 and shake.trauma < 0.5, "shake stays light and decays")
    for i in range(30): shake._apply_shake(0.1)
    _check(shake.trauma == 0.0 and shake.camera.offset == Vector2.ZERO, "the camera settles back to no offset")
    GameSettings.screen_shake = false
    SquadCameraPresentation.kick(self, 0.8)
    shake._apply_shake(0.016)
    _check(shake.trauma == 0.0 and shake.camera.offset == Vector2.ZERO, "screen shake off means no shake")
    GameSettings.screen_shake = true

func _vfx() -> Array:
    return root.get_children().filter(func(node: Node) -> bool: return node is CombatHitVFX and not node.is_queued_for_deletion())

func _hurt_count() -> int:
    return _vfx().filter(func(node: Node) -> bool: return (node as CombatHitVFX).effect_kind == CombatHitVFX.EFFECT_HURT).size()

func _latest_hurt(target_id: String) -> CombatHitVFX:
    var found: CombatHitVFX = null
    for node in _vfx():
        var vfx := node as CombatHitVFX
        if vfx.effect_kind == CombatHitVFX.EFFECT_HURT and vfx.target_id == target_id:
            found = vfx
    return found

func _frames(count: int) -> void:
    for i in range(count): await process_frame

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)
