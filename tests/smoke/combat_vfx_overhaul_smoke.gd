extends SceneTree
## Code-drawn combat VFX beyond the hit/hurt contract: every robot and boss has its own
## impact family, projectiles draw their family and raise one muzzle flash per shooter per
## tick, robot deaths and area attacks blast at the caller's radius and leave scorch,
## damaged robots smoulder, skills and buff auras draw on both layers and ride their
## caster, and every effect stays inside its triangle budget and frees itself.

const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const Projectile := preload("res://scripts/combat/prototype_projectile.gd")
const SkillVFX := preload("res://scripts/vfx/operator_skill_vfx.gd")
const Explosion := preload("res://scripts/vfx/combat_explosion_vfx.gd")
## Families each robot's hit profile must reach (mortar shells land as explosions).
const ENEMY_FAMILIES := {"ENM_SITE7_DRONE_01": "DRONE", "BOSS_SITE7_ANCHOR_01": "ANCHOR",
    "ENM_SITE7_BULWARK_01": "BULWARK", "ENM_SITE7_RAM_01": "RAM", "ENM_SITE7_MORTAR_01": "GENERIC",
    "ENM_SITE7_PRISM_01": "PRISM", "ENM_SITE7_NULL_PYLON_01": "GENERIC",
    "BOSS_SITE7_FORGE_01": "FORGE", "BOSS_SITE7_CARRIER_01": "CARRIER",
    "BOSS_SITE7_RELAY_01": "RELAY", "BOSS_SITE7_REMNANT_01": "REMNANT",
    "BOSS_SITE7_AERATOR_01": "AERATOR", "BOSS_SITE7_CRYO_01": "CRYO", "BOSS_SITE7_GANTRY_01": "GANTRY",
    "BOSS_SITE7_ARCHIVE_01": "ARCHIVE", "BOSS_SITE7_ORIGIN_01": "ORIGIN"}
const PROJECTILE_FAMILIES := {"PRJ_ASTER_NEEDLE_01": "ASTER", "PRJ_ROOK_SCATTER_01": "ROOK",
    "PRJ_MICA_PULSE_01": "MICA", "PRJ_ENM_DRONE_BEAMLET_01": "DRONE", "PRJ_ENM_SHIELD_01": "BULWARK",
    "PRJ_ENM_PRISM_BEAM_01": "PRISM", "PRJ_BOSS_ANCHOR_LANCE_01": "ANCHOR",
    "PRJ_BOSS_FORGE_LANCE_01": "FORGE", "PRJ_BOSS_CARRIER_LANCE_01": "CARRIER",
    "PRJ_BOSS_RELAY_BOLT_01": "RELAY", "PRJ_BOSS_REMNANT_ARC_01": "REMNANT",
    "PRJ_BOSS_AERATOR_SPORE_01": "AERATOR", "PRJ_BOSS_CRYO_SHARD_01": "CRYO",
    "PRJ_BOSS_GANTRY_RAIL_01": "GANTRY", "PRJ_BOSS_ARCHIVE_ECHO_01": "ARCHIVE",
    "PRJ_BOSS_ORIGIN_NULL_01": "ORIGIN",
    "PRJ_WEAPON_RAIL_01": "WEAPON_RAIL", "PRJ_WEAPON_NULL_01": "WEAPON_NULL",
    "PRJ_ENM_MORTAR_01": "MORTAR", "PRJ_ENM_ABERRANT_01": "GENERIC"}
## Most triangles any one effect may draw in a frame (per kind), a guard on frame cost.
const EXPLOSION_BUDGET := {"BOSS": 6500, "VOLATILE": 3200}
const DEFAULT_BUDGET := 2400
const SKILLS := ["ASTER_PRISM", "VECTOR_DASH", "OVERCLOCK", "OVERCLOCK_AURA", "ROOK_BREACH_SLAM",
    "BULWARK", "GUARD_AURA", "SCATTER_CYCLE", "SCATTER_AURA", "MICA_PULSE_SCAN", "RELAY_STEP", "SENSOR_BLOOM"]

var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _verify_impact_families()
    await _verify_projectiles_and_muzzle()
    await _verify_explosions()
    await _verify_ground_marks()
    await _verify_destruction_and_smoulder()
    await _verify_skills()
    for node in root.get_children():
        if node is CombatHitVFX or node is CombatExplosionVFX or node is CombatMuzzleVFX or node is OperatorSkillVFX:
            node.queue_free()
    if failures.is_empty():
        print("COMBAT_VFX_OVERHAUL_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _verify_impact_families() -> void:
    for enemy_id in ENEMY_FAMILIES:
        var profile := ArtProfileRegistry.get_profile(enemy_id)
        var hit_id := str(profile.get("hit_vfx_profile", ""))
        _check(not hit_id.is_empty(), enemy_id + " names a hit profile")
        _check(CombatHitVFX.family_for(hit_id) == ENEMY_FAMILIES[enemy_id], "%s hits draw the %s family (got %s)" % [enemy_id, ENEMY_FAMILIES[enemy_id], CombatHitVFX.family_for(hit_id)])
        CombatFeedback.spawn_hit_visual(self, Vector2(300, 300), hit_id, Color("ffffff"), Vector2.RIGHT)
        var vfx := _last(CombatHitVFX) as CombatHitVFX
        vfx.age = vfx.lifetime * 0.2
        vfx.call("_draw")
        _check(vfx.debug_triangle_count() > 0 and vfx.debug_triangle_count() < 1500, "%s impact draws a bounded shape (%d triangles)" % [enemy_id, vfx.debug_triangle_count()])
        vfx.free()
    for extra in ["HIT_ARMOR_DEFLECT_01", "HIT_BARRIER_GUARD_01", "HIT_WEAPON_RAIL_01", "HIT_WEAPON_NULL_01"]:
        _check(CombatHitVFX.family_for(extra) != "GENERIC", extra + " has its own family")
    CombatFeedback.spawn_cover_hit(self, Vector2(300, 300), {"hit_vfx_profile": "HIT_ROOK_CRUSH_01"}, Color("ffb45c"), null, Vector2.RIGHT)
    var cover := _last(CombatHitVFX) as CombatHitVFX
    _check(cover.debug_vfx_contract().surface == "COVER", "a round stopped by cover marks the concrete surface")
    cover.free()
    # An armour deflect replaces the weapon's impact look: one effect per hit, not two.
    var before := _count(CombatHitVFX)
    CombatFeedback.spawn_hit(self, Vector2(300, 300), {"hit_vfx_profile": "HIT_ROOK_CRUSH_01"}, Color("ffe09a"), null, Vector2.RIGHT, "HIT_ARMOR_DEFLECT_01")
    var deflect := _last(CombatHitVFX) as CombatHitVFX
    _check(_count(CombatHitVFX) == before + 1 and deflect.family == "DEFLECT", "a deflected round draws one DEFLECT impact")
    deflect.free()
    # A volley into a crowd thins the particles of the later impacts, never the first ones.
    var volley: Array[CombatHitVFX] = []
    for i in range(14):
        CombatFeedback.spawn_hit_visual(self, Vector2(300 + i * 4, 300), "HIT_ROOK_CRUSH_01", Color("ffb45c"), Vector2.RIGHT)
        volley.append(_last(CombatHitVFX) as CombatHitVFX)
    for fx in volley:
        fx.age = fx.lifetime * 0.2
        fx.call("_draw")
    var first := volley[0].debug_triangle_count()
    var last := volley[volley.size() - 1].debug_triangle_count()
    _check(last < first and last * 3 > first, "a crowded impact draws fewer, not no, particles (%d -> %d triangles)" % [first, last])
    for fx in volley: fx.free()
    CombatFeedback.spawn_hit_visual(self, Vector2(300, 300), "HIT_ROOK_CRUSH_01", Color("ffb45c"), Vector2.RIGHT)
    var alone := _last(CombatHitVFX) as CombatHitVFX
    alone.age = alone.lifetime * 0.2
    alone.call("_draw")
    _check(alone.debug_triangle_count() == first, "freed impacts leave the crowd count, so the next hit is whole again")
    alone.free()

func _verify_projectiles_and_muzzle() -> void:
    var shooter := Node2D.new()
    root.add_child(shooter)
    shooter.global_position = Vector2(100, 100)
    await physics_frame
    for profile_id in PROJECTILE_FAMILIES:
        var shot := Projectile.new() as PrototypeProjectile
        root.add_child(shot)
        shot.setup(Vector2(120, 100), Vector2.RIGHT, null, Color("ffffff"), {"projectile_profile": profile_id}, "none")
        shot.set_physics_process(false)
        _check(str(shot.get("_family")) == PROJECTILE_FAMILIES[profile_id], "%s flies as %s" % [profile_id, PROJECTILE_FAMILIES[profile_id]])
        shot.set("_travelled", 400.0)
        shot.call("_draw")
        var drawn: int = shot.get("_paint").triangle_count()
        _check(drawn > 0 and drawn < 400, "%s draws a bounded body and trail (%d triangles)" % [profile_id, drawn])
        shot.free()
    for node in root.get_children():
        if node is CombatMuzzleVFX: node.free()
    # A volley from one shooter in one physics tick shares one flash, which rides with it.
    var first := CombatMuzzleVFX.spawn(self, Vector2(130, 100), Vector2.RIGHT, "PRJ_ROOK_SCATTER_01", Color("ffb45c"), shooter)
    var second := CombatMuzzleVFX.spawn(self, Vector2(130, 100), Vector2.RIGHT, "PRJ_ROOK_SCATTER_01", Color("ffb45c"), shooter)
    _check(first != null and second == null, "five pellets in one tick raise a single muzzle flash")
    _check(first != null and first.debug_contract().family == "ROOK", "the flash takes the weapon's family")
    shooter.global_position += Vector2(40, 10)
    first.call("_process", 0.001)
    _check(first.global_position.is_equal_approx(Vector2(170, 110)), "the flash rides with its shooter")
    await physics_frame
    _check(CombatMuzzleVFX.spawn(self, Vector2(130, 100), Vector2.RIGHT, "PRJ_ROOK_SCATTER_01", Color("ffb45c"), shooter) != null, "the next tick flashes again")
    for node in root.get_children():
        if node is CombatMuzzleVFX:
            node.call("_process", 1.0)
    await process_frame
    _check(_count(CombatMuzzleVFX) == 0, "muzzle flashes free themselves after their life")
    # A wind-up charge on a robot that is not winding up lets go at once.
    var enemy := ENEMY_SCENE.instantiate() as EnemyActor
    enemy.configure("ENM_SITE7_DRONE_01", 60.0)
    enemy.global_position = Vector2(500, 300)
    root.add_child(enemy)
    await process_frame
    enemy.set_physics_process(false)
    var charge := CombatMuzzleVFX.spawn_charge(self, enemy, "PRJ_ENM_DRONE_BEAMLET_01", Color("d9577d"), 0.9)
    _check(charge != null and charge.debug_contract().mode == "CHARGE", "a wind-up raises a charge on the emitter")
    charge.call("_process", 0.02)
    _check(bool(charge.debug_contract().released), "the charge releases when the robot is no longer winding up")
    charge.call("_process", 0.1)
    await process_frame
    _check(not is_instance_valid(charge), "a released charge frees itself")
    enemy.queue_free()
    shooter.queue_free()
    await process_frame

func _verify_explosions() -> void:
    for kind in Explosion.KINDS:
        var fx := CombatFeedback.spawn_explosion(self, Vector2(400, 300), kind, Color("c097fa"), 80.0 if kind != "LANE" else 16.0, Vector2.RIGHT, 300.0)
        _check(fx != null and fx.debug_contract().kind == kind, kind + " explosion spawns")
        if kind == "TRAIL":
            fx.set("_trail", PackedVector2Array([Vector2(300, 300), Vector2(340, 310), Vector2(380, 300), Vector2(400, 300)]))
        var budget := int(EXPLOSION_BUDGET.get(kind, DEFAULT_BUDGET))
        var peak := 0
        var steps := 24
        for i in range(steps):
            fx.age = fx.duration * float(i) / float(steps)
            fx.call("_draw")
            peak = maxi(peak, int(fx.debug_contract().triangles))
        _check(peak > 0, kind + " draws")
        _check(peak <= budget, "%s stays inside its triangle budget (%d of %d)" % [kind, peak, budget])
        fx.age = 0.0
        fx.call("_process", fx.duration + 0.05)
        await process_frame
        _check(not is_instance_valid(fx), kind + " frees itself after its duration")

func _verify_ground_marks() -> void:
    for mark in get_nodes_in_group("vfx_ground_marks"):
        mark.free()
    for i in range(15):
        CombatFeedback.spawn_explosion(self, Vector2(100 + i * 20, 400), "MORTAR", Color("c097fa"), 64.0)
    _check(get_nodes_in_group("vfx_ground_marks").size() == 15, "each floor-level blast leaves a scorch")
    var hurried := 0
    for mark in get_nodes_in_group("vfx_ground_marks"):
        if float(mark.get("age")) > 0.0:
            hurried += 1
    _check(hurried >= 3, "only the newest dozen scorches keep their full life")
    CombatFeedback.spawn_explosion(self, Vector2(400, 400), "ROBOT_SMALL", Color("d9577d"), 62.0)
    _check(get_nodes_in_group("vfx_ground_marks").size() == 15, "an airborne drone's burst leaves no scorch")
    for mark in get_nodes_in_group("vfx_ground_marks"):
        _check(mark.z_index < -2, "scorch stays under warnings and hazards")
        mark.call("_process", 10.0)
    for node in root.get_children():
        if node is CombatExplosionVFX: node.free()
    await process_frame
    _check(get_nodes_in_group("vfx_ground_marks").is_empty(), "scorch fades and frees itself")

func _verify_destruction_and_smoulder() -> void:
    var cases := {"ENM_SITE7_DRONE_01": "ROBOT_SMALL", "ENM_SITE7_BULWARK_01": "ROBOT_HEAVY", "BOSS_SITE7_ANCHOR_01": "BOSS"}
    for enemy_id in cases:
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(enemy_id, 300.0)
        enemy.global_position = Vector2(640, 360)
        root.add_child(enemy)
        await process_frame
        enemy.set_physics_process(false)
        # Below 40 % health a robot leaks smoke from its body.
        enemy.apply_damage(enemy.max_health * 0.7)
        var before := _count(CombatExplosionVFX)
        enemy.call("_smolder", 1.0)
        var smoke := _last(CombatExplosionVFX) as CombatExplosionVFX
        _check(_count(CombatExplosionVFX) == before + 1 and smoke.debug_contract().kind == "SMOLDER", enemy_id + " smoulders when badly damaged")
        _check(smoke != null and enemy.get_combat_hit_rect().grow(4.0).has_point(smoke.global_position), enemy_id + " smoke leaves its own body")
        enemy.apply_damage(99999.0)
        var blast := _last(CombatExplosionVFX) as CombatExplosionVFX
        _check(blast != null and blast.debug_contract().kind == cases[enemy_id], "%s is destroyed in a %s blast" % [enemy_id, cases[enemy_id]])
        enemy.queue_free()
        await process_frame
    for node in root.get_children():
        if node is CombatExplosionVFX: node.free()
    for mark in get_nodes_in_group("vfx_ground_marks"):
        mark.free()

func _verify_skills() -> void:
    var caster := Node2D.new()
    root.add_child(caster)
    caster.global_position = Vector2(400, 400)
    var target := Node2D.new()
    root.add_child(target)
    target.global_position = Vector2(600, 360)
    for skill_id in SKILLS:
        var fx := SkillVFX.new() as OperatorSkillVFX
        root.add_child(fx)
        fx.global_position = caster.global_position + Vector2(0, -18)
        fx.setup(skill_id, Color("69d2ff"), 150.0, Vector2.RIGHT, 5.0 if "AURA" in skill_id else 0.7)
        fx.mark_targets([target])
        var peak := 0
        for i in range(10):
            fx.life = fx.max_life * (1.0 - float(i) / 10.0)
            fx.set("_age", fx.max_life * float(i) / 10.0)
            fx.call("_draw")
            peak = maxi(peak, fx.get("_ground").triangle_count() + fx.get("_air").triangle_count() + fx.get("_dust").triangle_count())
        _check(peak > 0 and peak < 3000, "%s draws a bounded skill effect (%d triangles)" % [skill_id, peak])
        _check(fx.debug_contract().air_layer, skill_id + " has its air layer over the bodies")
        fx.queue_free()
    await process_frame
    # An aura rides with its caster and ends early when the caster leaves.
    var aura := SkillVFX.new() as OperatorSkillVFX
    root.add_child(aura)
    aura.setup("GUARD_AURA", Color("ffb45c"), 40.0, Vector2.RIGHT, 5.0)
    aura.follow_actor(caster)
    caster.global_position = Vector2(500, 420)
    aura.call("_process", 0.016)
    _check(aura.global_position.is_equal_approx(Vector2(500, 402)), "a buff aura rides with its caster")
    caster.free()
    aura.call("_process", 0.016)
    _check(aura.life <= 0.25, "an aura ends early once its caster is gone")
    aura.call("_process", 0.3)
    await process_frame
    _check(not is_instance_valid(aura), "the aura frees itself")
    target.queue_free()

func _last(type: Variant) -> Node:
    var found: Node = null
    for node in root.get_children():
        if is_instance_of(node, type) and not node.is_queued_for_deletion():
            found = node
    return found

func _count(type: Variant) -> int:
    var total := 0
    for node in root.get_children():
        if is_instance_of(node, type) and not node.is_queued_for_deletion():
            total += 1
    return total

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)
