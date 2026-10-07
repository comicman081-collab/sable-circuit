extends CharacterBody2D
class_name EnemyActor
signal damage_taken(actor: EnemyActor, applied: float, source_id: String)

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")
const TILE := 512.0
# Dense encounters: mobile robots keep a readable gap instead of stacking into
# one silhouette. Fixed emplacements and locked attacks are never pushed.
const CROWD_RADIUS := 140.0
const CROWD_PUSH := 80.0
const CROWD_ROLES := ["drone", "skimmer", "shield", "melee"]

signal defeated(enemy: EnemyActor)
signal projectile_emitted(event: Dictionary)

@export var enemy_id := "ENM_SITE7_DRONE_01"
@export var max_health := 100.0

var health := 100.0
var art_profile: Dictionary = {}
var home_position := Vector2.ZERO
var _phase := 0.0
var _attack_cd := 0.8
var _hit_flash := 0.0
var _last_hurt_msec := -1000
var _lunge_left := 0.0
var _orbit_sign := 1.0
var _aim_dir := Vector2.LEFT

var _exposed_left := 0.0
var _stagger_left := 0.0
var _status_source := ""
var _last_consumed_source := ""

# M11 deployment-only modifiers. They are applied after authored encounter HP is
# configured and never written to CampaignProgression.
var run_health_multiplier := 1.0
var run_damage_multiplier := 1.0
var run_speed_multiplier := 1.0
var _hazard_speed_factors: Dictionary = {}
var run_attack_interval_multiplier := 1.0
# Plain first-generation BROODING hatchlings cannot attack during their marked hatch.
var brood_generation := 0
var brood_hatch_left := 0.0
var brood_hatch_duration := 0.0
var _brood_paint := VfxPainter.new()

var _visual_root: Node2D
var _hidden_master: Sprite2D
var _rig: Skeleton2D
var _rig_texture: Texture2D
var _bones: Dictionary = {}
var _parts: Dictionary = {}
var _base_positions: Dictionary = {}
var tactics: Node2D
var _death_left := -1.0
var machine_sprite: Node2D
var biped_sprite: Node2D
var _drive_speed := 0.0
# Below this share of health a robot leaks smoke and sparks (code-drawn, never on its art).
const SMOLDER_BELOW := 0.4
var _smolder_left := 0.0
var _smolder_count := 0

func set_hazard_speed_factor(token: String, factor: float) -> void:
    if health <= 0.0: return
    _hazard_speed_factors[token] = clampf(factor, 0.5, 1.0)

func remove_hazard_speed_factor(token: String) -> void:
    _hazard_speed_factors.erase(token)

func hazard_speed_factor() -> float:
    var factor := 1.0
    for value in _hazard_speed_factors.values(): factor = minf(factor, float(value))
    return factor

func _ready() -> void:
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    if not _runtime_enemy_allowed():
        hide()
        queue_free()
        return
    add_to_group("prototype_targets")
    add_to_group("m3_enemies")
    # Top-down bodies ride nothing (see OperatorActor._ready): an operator touched from
    # its north side must not carry the robot as a moving platform.
    platform_floor_layers = 0
    platform_wall_layers = 0
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    health = max_health
    home_position = global_position
    _orbit_sign = -1.0 if abs(enemy_id.hash()) % 2 == 0 else 1.0
    _build_high_res_visual()
    _load_reviewed_machine_source()
    tactics = preload("res://scripts/combat/site7_enemy_tactics.gd").new()
    tactics.name = "Tactics"
    add_child(tactics)
    queue_redraw()

func _runtime_enemy_allowed() -> bool:
    return str(art_profile.get("enemy_id", "")) == enemy_id and str(art_profile.get("body_plan", "")) == "robot" and bool(art_profile.get("runtime_enabled", false)) and not art_profile.has("biped_asset")

func configure(id_value: String, hp: float = -1.0) -> bool:
    enemy_id = id_value
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    if not _runtime_enemy_allowed():
        health = 0.0
        if is_inside_tree():
            remove_from_group("prototype_targets")
            remove_from_group("m3_enemies")
            hide()
            queue_free()
        return false
    if hp > 0.0:
        max_health = hp
    health = max_health
    _exposed_left=0.0; _stagger_left=0.0; _status_source=""; _last_consumed_source=""
    if is_node_ready():
        _rebuild_visual()
    return true

func apply_run_modifiers(modifiers: Dictionary) -> void:
    run_health_multiplier = clampf(float(modifiers.get("enemy_health_multiplier",1.0)),0.5,3.0)
    run_damage_multiplier = clampf(float(modifiers.get("enemy_damage_multiplier",1.0)),0.5,3.0)
    run_speed_multiplier = clampf(float(modifiers.get("enemy_speed_multiplier",1.0)),0.5,2.0)
    run_attack_interval_multiplier = clampf(float(modifiers.get("enemy_attack_interval_multiplier",1.0)),0.5,2.0)
    max_health *= run_health_multiplier
    health = max_health

func apply_damage(amount: float, source_id: String = "") -> void:
    if amount<=0.0 or health<=0.0: return
    var guard := get_node_or_null("BossPhaseTransitionGuard")
    if guard and guard.has_method("debug_guard_active") and guard.debug_guard_active():
        return
    # BEACON reduces incoming damage once, then SHIELDED absorbs that result.
    amount = EliteAffix.protected_damage(self, amount)
    # An elite SHIELDED barrier soaks damage before health; a fully soaked hit only flashes.
    var affix := get_node_or_null("EliteAffix") as EliteAffix
    if affix != null:
        amount = affix.absorb(amount)
        if amount <= 0.0:
            _hit_flash = 0.5
            queue_redraw()
            return
    var before := health
    health = maxf(0.0, health - amount)
    damage_taken.emit(self, before - health, source_id)
    _hit_flash = 1.0
    _spawn_hurt(before - health)
    if health <= 0.0:
        _hazard_speed_factors.clear()
        remove_from_group("prototype_targets")
        remove_from_group("m3_enemies")
        velocity = Vector2.ZERO
        _death_left = 0.55
        if tactics: tactics.visible = false
        if get_node_or_null("OverheadUI"): get_node("OverheadUI").visible = false
        # Every boss (ANCHOR, FORGE, CARRIER) collapses with the full tail;
        # ordinary robots burst apart with an armour-break crack.
        preload("res://scripts/audio/combat_sfx_bank.gd").play(get_tree(), "boss_destroy" if enemy_id.begins_with("BOSS_") else "armor_break", self)
        SquadCameraPresentation.kick(get_tree(), 0.75 if enemy_id.begins_with("BOSS_") else 0.22)
        # The art fades out under a code-drawn blast; the robot's pixels are never recoloured.
        if is_inside_tree(): CombatFeedback.spawn_destruction(get_tree(), self, get_combat_hit_rect(), enemy_id, _projectile_color())
        if affix != null: affix.on_defeated()
        defeated.emit(self)
        return
    queue_redraw()

## A robot's own hurt reaction. The death sequence already covers the killing hit, and a
## stream of small hits shows at most one reaction every 90 ms so rapid fire stays readable.
func _spawn_hurt(applied: float) -> void:
    if health <= 0.0 or not is_inside_tree(): return
    var reaction := CombatFeedback.hurt_reaction(applied, health, max_health)
    var now := Time.get_ticks_msec()
    if reaction == "FLINCH" and now - _last_hurt_msec < 90: return
    _last_hurt_msec = now
    var boss := enemy_id.begins_with("BOSS_")
    CombatFeedback.spawn_hurt(get_tree(), get_combat_hit_rect().get_center(), "BOSS" if boss else "ENEMY", enemy_id, reaction, _projectile_color())

func projectile_damage_multiplier(incoming_direction: Vector2) -> float:
    # Armour covers only the visible FRONT cone. Flanking and stagger defeat it.
    # A shot's travel direction points toward the victim, hence the negation.
    if enemy_id != "ENM_SITE7_BULWARK_01" or is_staggered() or not is_instance_valid(machine_sprite):
        return 1.0
    var front: Vector2 = machine_sprite.visible_heading_world()
    return 0.35 if front.dot(-incoming_direction.normalized()) >= 0.60 else 1.0

func apply_exposed(duration: float, source: String = "") -> void:
    if health<=0.0: return
    _exposed_left=maxf(_exposed_left,maxf(0.0,duration))
    _status_source=source
    queue_redraw()

func is_exposed() -> bool:
    return _exposed_left>0.0

func apply_stagger(duration: float, source: String = "") -> void:
    if health<=0.0: return
    var applied:=maxf(0.0,duration)
    if "BOSS" in enemy_id or "ANCHOR" in enemy_id: applied=minf(applied,1.2)
    _stagger_left=maxf(_stagger_left,applied)
    _status_source=source
    velocity=Vector2.ZERO
    if tactics: tactics.interrupt()
    queue_redraw()

func is_staggered() -> bool:
    return _stagger_left>0.0

func consume_exposed_for_stagger(duration: float, source: String = "") -> bool:
    if not is_exposed(): return false
    _last_consumed_source=_status_source
    _exposed_left=0.0
    apply_stagger(duration,source)
    return true

func _physics_process(delta: float) -> void:
    if health <= 0.0:
        _death_left -= delta
        modulate.a = clampf(_death_left / 0.55, 0.0, 1.0)
        if _death_left <= 0.0: queue_free()
        return
    if brood_hatch_left > 0.0:
        brood_hatch_left = maxf(0.0, brood_hatch_left - delta)
        velocity = Vector2.ZERO
        queue_redraw()
        return
    _phase += delta
    _smolder(delta)
    _attack_cd = maxf(0.0, _attack_cd - delta)
    _hit_flash = move_toward(_hit_flash, 0.0, delta * 4.5)
    _exposed_left=maxf(0.0,_exposed_left-delta)
    _stagger_left=maxf(0.0,_stagger_left-delta)
    if _stagger_left>0.0:
        velocity=Vector2.ZERO
    else:
        var target := _nearest_operator()
        if target:
            tactics.step(target, delta)
            velocity += _crowd_separation()
            velocity *= run_speed_multiplier * hazard_speed_factor()
        else:
            velocity = velocity.move_toward(Vector2.ZERO, 260.0 * delta)
    # Accelerate into a route, but never coast beyond the navigation step or
    # move during a locked warning. Direction and clearance remain nav-owned.
    var commanded_speed := velocity.length()
    var acceleration := 220.0 if enemy_id == "ENM_SITE7_BULWARK_01" else 420.0
    if tactics and tactics.state == "LUNGE":
        _drive_speed = commanded_speed
    else:
        _drive_speed = minf(commanded_speed,move_toward(_drive_speed,commanded_speed,acceleration*delta))
    if commanded_speed > 0.001:
        velocity *= _drive_speed/commanded_speed
    var position_before_motion := global_position
    move_and_slide()
    var stage := get_parent()
    if stage and stage.has_method("constrain_battle_position"):
        global_position = stage.call("constrain_battle_position", global_position)
    var actual_displacement := global_position-position_before_motion
    if enemy_id == "ENM_SITE7_RAM_01" and tactics and tactics.state == "LUNGE":
        # Contact with cover cancels the ram; it cannot damage through a wall.
        if get_slide_collision_count() > 0 or actual_displacement.length() < velocity.length()*delta*0.5:
            tactics.interrupt()
            velocity = Vector2.ZERO
        else:
            tactics.commit_lunge_motion(position_before_motion, global_position)
    # Applies to the active drone as well: collision/floor correction cannot
    # move the source of an already announced shot without a fresh warning.
    if actual_displacement.length()>0.000001 and tactics and tactics.state in ["WINDUP","BURST"]:
        tactics.interrupt()
    if is_instance_valid(biped_sprite):
        biped_sprite.commit_displacement(actual_displacement)
    _animate_identity()
    if is_instance_valid(_rig):
        var tint:=Color.WHITE
        if _exposed_left>0.0: tint=tint.lerp(Color("8ff5e8"),0.26)
        if _stagger_left>0.0: tint=tint.lerp(Color("ffd17d"),0.32)
        _rig.modulate = tint.lerp(Color("ff8a8a"), _hit_flash * 0.68)
    queue_redraw()

## A badly damaged robot puffs smoke and the odd spark from its body every few tenths
## of a second. Timing and placement come from its own counter, not the shared RNG.
func _smolder(delta: float) -> void:
    if health >= max_health * SMOLDER_BELOW or not is_inside_tree() or not visible:
        return
    _smolder_left -= delta
    if _smolder_left > 0.0:
        return
    _smolder_count += 1
    var boss := enemy_id.begins_with("BOSS_")
    var jitter := VfxPainter.rand(get_instance_id(), _smolder_count)
    _smolder_left = (0.18 if boss else 0.3) + 0.25 * jitter
    var rect := get_combat_hit_rect()
    var at := rect.position + rect.size * Vector2(0.25 + 0.5 * VfxPainter.rand(get_instance_id(), _smolder_count + 7), 0.2 + 0.3 * jitter)
    CombatFeedback.spawn_explosion(get_tree(), at, "SMOLDER", _projectile_color(), 30.0 if boss else 18.0)

func _nearest_operator() -> OperatorActor:
    var best: OperatorActor = null
    var best_d2: float = INF
    for node in get_tree().get_nodes_in_group("operators"):
        if node is OperatorActor and not node.is_downed():
            var d2: float = global_position.distance_squared_to(node.global_position)
            if d2 < best_d2:
                best_d2 = d2
                best = node
    return best

func _crowd_separation() -> Vector2:
    if tactics == null or tactics.state in ["WINDUP", "BURST", "LUNGE"]: return Vector2.ZERO
    if str(tactics.ROLES.get(enemy_id, "")) not in CROWD_ROLES: return Vector2.ZERO
    var push := Vector2.ZERO
    for other in get_tree().get_nodes_in_group("m3_enemies"):
        if other == self or not other is EnemyActor or other.health <= 0.0: continue
        var away: Vector2 = global_position - other.global_position
        var d := away.length()
        if d >= CROWD_RADIUS: continue
        # Exact overlap: split deterministically by spawn order.
        if d < 0.01: away = Vector2.UP if get_instance_id() < other.get_instance_id() else Vector2.DOWN
        push += away.normalized() * (1.0 - d / CROWD_RADIUS)
    return push.limit_length(1.0) * CROWD_PUSH

func get_combat_hit_rect() -> Rect2:
    if is_instance_valid(biped_sprite): return biped_sprite.hit_rect_world()
    if is_instance_valid(machine_sprite): return machine_sprite.hit_rect_world()
    var local := Rect2(-25,-108,50,112)
    if "SHIELD" in enemy_id: local = Rect2(-38,-128,76,132)
    elif "DRONE" in enemy_id: local = Rect2(-38,-105,76,62)
    elif "ABERRANT" in enemy_id: local = Rect2(-31,-104,62,108)
    elif "BOSS" in enemy_id or "ANCHOR" in enemy_id: local = Rect2(-98,-210,196,214)
    return Rect2(global_position + local.position, local.size)

func get_combat_aim_point() -> Vector2:
    return get_combat_hit_rect().get_center()

func _update_tactics(target: OperatorActor, delta: float) -> void:
    var to_target := target.global_position - global_position
    var dist: float = to_target.length()
    var dir := to_target.normalized() if dist > 0.001 else Vector2.RIGHT
    var aim_delta := target.get_combat_aim_point() - get_combat_aim_point()
    _aim_dir = aim_delta.normalized() if aim_delta.length_squared() > 1.0 else dir
    var motion := str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion:
        var radial: float = 0.0
        if dist > 350.0: radial = 1.0
        elif dist < 250.0: radial = -0.8
        var side := Vector2(-dir.y, dir.x) * sin(_phase * 2.2) * 0.72
        velocity = (dir * radial + side).limit_length(1.0) * 105.0
        _try_attack(_aim_dir, 1.05)
    elif "SHIELD" in motion:
        velocity = dir * (72.0 if dist > 190.0 else 18.0)
        _try_attack(_aim_dir, 1.65)
    elif "DRONE" in motion:
        var tangent := Vector2(-dir.y, dir.x) * _orbit_sign
        var radial: float = clampf((dist - 300.0) / 140.0, -0.7, 0.7)
        velocity = (tangent * 0.9 + dir * radial).normalized() * 138.0
        _try_attack(_aim_dir, 0.78)
    elif "ABERRANT" in motion:
        if _lunge_left > 0.0:
            _lunge_left = maxf(0.0, _lunge_left - delta)
            velocity = dir * 330.0
        elif dist > 130.0:
            velocity = dir * 126.0
            if dist < 270.0 and _attack_cd <= 0.0:
                _lunge_left = 0.22
                _attack_cd = 1.35 * run_attack_interval_multiplier
        else:
            velocity = Vector2.ZERO
            _try_attack(_aim_dir, 1.25)
    elif "BOSS" in motion or "ANCHOR" in motion:
        velocity = Vector2(sin(_phase * 0.7), cos(_phase * 0.53)) * 18.0
        _try_attack(_aim_dir.rotated(sin(_phase * 0.8) * 0.18), 1.18)
    else:
        velocity = dir * 80.0
        _try_attack(_aim_dir, 1.2)

func _try_attack(dir: Vector2, interval: float) -> void:
    if brood_hatch_left > 0.0 or _attack_cd > 0.0 or _stagger_left>0.0:
        return
    _attack_cd = interval * run_attack_interval_multiplier
    CombatFeedback.play_fire(get_tree(), art_profile, self)
    _spawn_projectile(dir)
    if "BOSS" in str(art_profile.get("projectile_profile", "")):
        _spawn_projectile(dir.rotated(-0.16))
        _spawn_projectile(dir.rotated(0.16))

func _spawn_projectile(dir: Vector2, emission_owner: Node = null, attack_serial: int = -1, ordinal: int = -1) -> void:
    if brood_hatch_left > 0.0: return
    if not dir.is_finite() or dir.length_squared() < 0.000001: return
    var projectile := Projectile.new()
    get_tree().root.add_child(projectile)
    var origin := projectile_origin(dir)
    if is_instance_valid(machine_sprite):
        machine_sprite.fired()
    projectile.setup(origin, dir, self, _projectile_color(), art_profile, "operators")
    projectile.damage *= run_damage_multiplier
    # Observe the actual creation boundary, including any legacy caller. A
    # controller's intended shot count alone cannot prove duplicate-free fire.
    var owner_node: Node = emission_owner if is_instance_valid(emission_owner) else self
    projectile_emitted.emit({"actor_id":get_instance_id(),"enemy_id":enemy_id,
        "attack_serial":attack_serial,"ordinal":ordinal,"owner_id":owner_node.get_instance_id(),
        "owner_path":str(owner_node.get_path()),"projectile_id":projectile.get_instance_id(),
        "origin":[origin.x,origin.y],"direction":[dir.x,dir.y],"physics_tick":Engine.get_physics_frames()})

func projectile_origin(dir: Vector2) -> Vector2:
    if is_instance_valid(biped_sprite): return biped_sprite.muzzle_world()
    if is_instance_valid(machine_sprite): return machine_sprite.muzzle_world()
    return get_combat_aim_point() + dir * _muzzle_distance()

func aim_from_emitter(target_point: Vector2) -> Vector2:
    if is_instance_valid(biped_sprite): return biped_sprite.resolve_target(target_point,velocity.length_squared()<0.000001)
    if is_instance_valid(machine_sprite): return machine_sprite.resolve_target(target_point)
    # Legacy muzzle offsets are collinear with aim and need no iterative solve.
    var origin: Vector2 = get_combat_aim_point()
    return (target_point-origin).normalized()

func preview_machine_source(spec: Dictionary) -> bool:
    # Explicit candidate intake for the owned native QA scene. No registry or
    # production pointer is written. Promotion is a separate reviewed change.
    if not _runtime_enemy_allowed() or is_instance_valid(machine_sprite) or is_instance_valid(biped_sprite): return false
    var candidate := preload("res://scripts/animation/site7_machine_sprite.gd").new()
    candidate.name = "AuthoredMachine"
    add_child(candidate)
    if not candidate.configure(self,spec):
        candidate.queue_free()
        return false
    machine_sprite = candidate
    _visual_root.visible = false
    return true

func preview_biped_source(_spec: Dictionary) -> bool:
    # 2026-09-19: humanoid enemies are retired, including diagnostic app intake.
    return false

func _load_reviewed_machine_source() -> void:
    if not bool(ProjectSettings.get_setting("sable_visuals/site7_authored_machines",true)): return
    var binding: Dictionary = art_profile.get("machine_asset",{})
    if binding.is_empty(): return
    var spec := reviewed_machine_spec(enemy_id)
    if spec.is_empty(): return
    if not preview_machine_source(spec): push_error("Reviewed machine intake failed: "+enemy_id)

## The registry's reviewed machine spec for a robot, checked against its bound hash.
## Parsed once per run; each caller gets its own copy.
static var _reviewed_specs: Dictionary = {}
static func reviewed_machine_spec(id_value: String) -> Dictionary:
    var binding: Dictionary = ArtProfileRegistry.get_profile(id_value).get("machine_asset",{})
    var path := str(binding.get("spec",""))
    var key := path + "|" + str(binding.get("sha256",""))
    if not _reviewed_specs.has(key):
        if not path.begins_with("res://assets/enemies/") or FileAccess.get_sha256(path) != str(binding.get("sha256","")):
            push_error("Reviewed machine spec is missing or changed: "+id_value);return {}
        var parsed: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
        if not parsed is Dictionary or str(parsed.get("enemy_id","")) != id_value:
            push_error("Reviewed machine identity mismatch: "+id_value);return {}
        _reviewed_specs[key] = parsed
    return (_reviewed_specs[key] as Dictionary).duplicate(true)

## Loads a robot type's art ahead of combat (mission load), so its first spawn in a fight
## does not stall on decoding and verifying eight full-size views.
static func warm_art(id_value: String) -> void:
    var profile := ArtProfileRegistry.get_profile(id_value)
    var paths: Array[String] = [str(profile.get("master_asset", "")), str(profile.get("rig_sheet", "")), EnemyDetailOverlayPresentation.detail_asset(id_value)]
    for path in paths:
        var resource_path := path if path.is_empty() or path.begins_with("res://") else "res://" + path
        if not resource_path.is_empty() and ResourceLoader.exists(resource_path): cached_texture(resource_path)
    if not bool(ProjectSettings.get_setting("sable_visuals/site7_authored_machines",true)): return
    if (profile.get("machine_asset",{}) as Dictionary).is_empty(): return
    var spec := reviewed_machine_spec(id_value)
    if not spec.is_empty(): preload("res://scripts/animation/site7_machine_sprite.gd").warm(spec)

## Robot textures stay loaded for the run. Freed with a room's last robot of a type, they
## were decoded again by the next room's first spawn (2048 px sheets, 11-18 ms each).
static var _textures: Dictionary = {}
static func cached_texture(path: String) -> Texture2D:
    if not _textures.has(path): _textures[path] = load(path) as Texture2D
    return _textures[path]

static func has_cached_texture(path: String) -> bool:
    return _textures.has(path)

## Keeps a texture DeployWarmer loaded on a thread.
static func keep_texture(path: String, texture: Texture2D) -> void:
    if texture != null and not _textures.has(path): _textures[path] = texture

func _muzzle_distance() -> float:
    if "BOSS" in enemy_id: return 92.0
    if enemy_id == "ENM_SITE7_PRISM_01": return 38.0
    if enemy_id == "ENM_SITE7_NULL_PYLON_01": return 44.0
    if "SHIELD" in enemy_id: return 44.0
    if "DRONE" in enemy_id: return 38.0
    return 34.0

func _projectile_color() -> Color:
    if enemy_id=="ENM_SITE7_BULWARK_01": return Color("e5b860")
    if enemy_id=="ENM_SITE7_RAM_01": return Color("ef9251")
    if enemy_id=="ENM_SITE7_MORTAR_01": return Color("c097fa")
    if enemy_id=="ENM_SITE7_PRISM_01": return Color("8a7bff")
    if enemy_id=="ENM_SITE7_NULL_PYLON_01": return Color("c097fa")
    if enemy_id=="BOSS_SITE7_FORGE_01": return Color("56e3e8")
    if enemy_id=="BOSS_SITE7_CARRIER_01": return Color("a27aff")
    if enemy_id=="BOSS_SITE7_RELAY_01": return Color("d8283c")
    if enemy_id=="BOSS_SITE7_REMNANT_01": return Color("bfe8ff")
    if enemy_id=="BOSS_SITE7_AERATOR_01": return Color("8fdc4a")
    if enemy_id=="BOSS_SITE7_CRYO_01": return Color("ff7fc8")
    if enemy_id=="BOSS_SITE7_GANTRY_01": return Color("ffd84a")
    if enemy_id=="BOSS_SITE7_ARCHIVE_01": return Color("2fe0b4")
    if enemy_id=="BOSS_SITE7_ORIGIN_01": return Color("f4efe8")
    var p := str(art_profile.get("projectile_profile", ""))
    if "RIFLE" in p: return Color("d95c65")
    if "SHIELD" in p: return Color("e2a94e")
    if "DRONE" in p: return Color("d9577d")
    if "ABERRANT" in p: return Color("a055c5")
    if "ANCHOR" in p: return Color("9b7cff")
    return Color.WHITE

func _rebuild_visual() -> void:
    if is_instance_valid(biped_sprite):
        biped_sprite.hide()
        biped_sprite.queue_free()
        biped_sprite=null
    if is_instance_valid(machine_sprite):
        machine_sprite.hide()
        machine_sprite.queue_free()
        machine_sprite=null
    if is_instance_valid(_visual_root):
        _visual_root.hide()
        _visual_root.queue_free()
    _bones.clear(); _parts.clear(); _base_positions.clear(); _rig_texture = null
    _build_high_res_visual()
    _load_reviewed_machine_source()

func _build_high_res_visual() -> void:
    _visual_root = Node2D.new()
    _visual_root.name = "HighResVisualRoot"
    add_child(_visual_root)
    _hidden_master = Sprite2D.new(); _hidden_master.name="UniqueMasterSprite"; _hidden_master.visible=false
    var master_path := str(art_profile.get("master_asset", ""))
    if not master_path.is_empty() and ResourceLoader.exists("res://" + master_path): _hidden_master.texture=cached_texture("res://"+master_path)
    _visual_root.add_child(_hidden_master)
    var rig_path := str(art_profile.get("rig_sheet", ""))
    if not rig_path.is_empty() and ResourceLoader.exists("res://" + rig_path): _rig_texture=cached_texture("res://"+rig_path)
    _rig=Skeleton2D.new(); _rig.name="UniqueLayerRig"; _visual_root.add_child(_rig)
    if enemy_id in ["ENM_SITE7_BULWARK_01", "ENM_SITE7_RAM_01", "ENM_SITE7_MORTAR_01",
        "ENM_SITE7_PRISM_01", "ENM_SITE7_NULL_PYLON_01", "BOSS_SITE7_FORGE_01", "BOSS_SITE7_CARRIER_01",
        "BOSS_SITE7_RELAY_01", "BOSS_SITE7_REMNANT_01", "BOSS_SITE7_AERATOR_01", "BOSS_SITE7_CRYO_01",
        "BOSS_SITE7_GANTRY_01", "BOSS_SITE7_ARCHIVE_01", "BOSS_SITE7_ORIGIN_01"]:
        return # New robots have no legacy human or procedural fallback pixels.
    if "RIFLE" in enemy_id: _build_rifle_rig()
    elif "SHIELD" in enemy_id: _build_shield_rig()
    elif "DRONE" in enemy_id: _build_drone_rig()
    elif "ABERRANT" in enemy_id: _build_aberrant_rig()
    elif "BOSS" in enemy_id: _build_boss_rig()
    for key in _bones.keys():
        var bone: Bone2D=_bones[key]; bone.rest=bone.transform; _base_positions[key]=bone.position

func _build_rifle_rig() -> void:
    var body:=_bone(_rig,"body",Vector2(0,-42)); var head:=_bone(body,"head",Vector2(0,-28)); var arm_l:=_bone(body,"arm_L",Vector2(-10,-2)); var arm_r:=_bone(body,"arm_R",Vector2(10,-2)); var leg_l:=_bone(body,"leg_L",Vector2(-7,23)); var shin_l:=_bone(leg_l,"shin_L",Vector2(0,18)); var leg_r:=_bone(body,"leg_R",Vector2(7,23)); var shin_r:=_bone(leg_r,"shin_R",Vector2(0,18)); var weapon:=_bone(body,"weapon",Vector2(3,0))
    _part(head,"Head",0,0,.115,3); _part(body,"RadioPack",1,0,.105,0); _part(body,"Torso",2,0,.108,1); _part(body,"Pelvis",3,0,.105,1); _part(arm_l,"ArmL",0,1,.105,2); _part(arm_r,"ArmR",2,1,.105,2); _part(leg_l,"ThighL",0,2,.105,0); _part(shin_l,"ShinL",1,2,.105,0); _part(leg_r,"ThighR",2,2,.105,0); _part(shin_r,"ShinR",3,2,.105,0); _part(weapon,"Rifle",2,3,.11,5)

func _build_shield_rig() -> void:
    var body:=_bone(_rig,"body",Vector2(0,-45)); var head:=_bone(body,"head",Vector2(5,-31)); var shield:=_bone(body,"shield",Vector2(-19,5)); var arm:=_bone(body,"hydraulic_arm",Vector2(14,-2)); var weapon:=_bone(arm,"weapon",Vector2(18,3)); var leg_l:=_bone(body,"leg_L",Vector2(-4,24)); var leg_r:=_bone(body,"leg_R",Vector2(9,24))
    _part(head,"WedgeHelmet",0,0,.12,4); _part(body,"Torso",1,0,.12,1); _part(body,"Pelvis",2,0,.11,1); _part(shield,"SlabShield",3,0,.13,6); _part(arm,"HydraulicArm",0,1,.12,3); _part(leg_l,"LegL",2,1,.115,0); _part(leg_r,"LegR",3,1,.115,0); _part(weapon,"RamPistol",2,2,.115,5); _part(body,"Cable",0,3,.11,2)

func _build_drone_rig() -> void:
    var chassis:=_bone(_rig,"chassis",Vector2(0,-56)); var eyes:=_bone(chassis,"sensor_cluster",Vector2(0,2)); var fins:=_bone(chassis,"fins",Vector2(0,-2)); var mast:=_bone(chassis,"mast",Vector2(0,-16)); var thruster:=_bone(chassis,"thruster",Vector2(0,20)); var emitter:=_bone(chassis,"emitter",Vector2(0,10))
    _part(chassis,"Crescent",0,0,.14,2); _part(eyes,"Eyes",1,0,.13,4); _part(fins,"Fins",2,0,.14,1); _part(mast,"Mast",3,0,.11,0); _part(thruster,"Thruster",0,1,.11,0); _part(emitter,"ScanArc",1,1,.12,3); _part(emitter,"Gun",0,2,.11,5); _part(chassis,"Glow",3,3,.12,0)

func _build_aberrant_rig() -> void:
    var torso:=_bone(_rig,"torso",Vector2(0,-42)); var skull:=_bone(torso,"skull",Vector2(0,-30)); var arm_l:=_bone(torso,"forelimb_L",Vector2(-13,-1)); var arm_r:=_bone(torso,"forelimb_R",Vector2(13,-1)); var leg_l:=_bone(torso,"leg_L",Vector2(-8,22)); var leg_r:=_bone(torso,"leg_R",Vector2(8,22)); var tail:=_bone(torso,"tail",Vector2(8,20)); var gland:=_bone(torso,"gland",Vector2(0,7))
    _part(skull,"SplitSkull",0,0,.12,4); _part(torso,"Torso",1,0,.112,1); _part(torso,"Pelvis",2,0,.105,1); _part(arm_r,"ForelimbR",3,0,.12,3); _part(arm_l,"ForelimbL",0,1,.12,3); _part(leg_l,"LegL",1,1,.115,0); _part(leg_r,"LegR",2,1,.115,0); _part(tail,"BioTail",1,2,.12,0); _part(gland,"Gland",3,1,.10,2)

func _build_boss_rig() -> void:
    var ring:=_bone(_rig,"ring",Vector2(0,-110)); var iris:=_bone(ring,"iris",Vector2.ZERO); var p1:=_bone(ring,"pylon_1",Vector2(-54,-54)); var p2:=_bone(ring,"pylon_2",Vector2(54,-54)); var p3:=_bone(ring,"pylon_3",Vector2(-54,54)); var p4:=_bone(ring,"pylon_4",Vector2(54,54)); var a1:=_bone(ring,"arm_1",Vector2(-58,-20)); var a2:=_bone(ring,"arm_2",Vector2(58,-20)); var a3:=_bone(ring,"arm_3",Vector2(-58,38)); var a4:=_bone(ring,"arm_4",Vector2(58,38)); var anchor:=_bone(ring,"anchor",Vector2(0,92)); var distortion:=_bone(ring,"distortion",Vector2.ZERO)
    _part(ring,"OuterRing",0,0,.27,1); _part(iris,"SignalIris",1,0,.24,5); _part(p1,"Pylon1",2,0,.18,2); _part(p2,"Pylon2",3,0,.18,2); _part(a1,"Arm1",0,1,.18,3); _part(a2,"Arm2",1,1,.18,3); _part(a3,"Arm3",2,1,.18,3); _part(a4,"Arm4",3,1,.18,3); _part(p3,"Pylon3",0,2,.18,2); _part(p4,"Pylon4",1,2,.18,2); _part(anchor,"Anchor",0,3,.18,0); _part(distortion,"Distortion",1,3,.24,0)

func _bone(parent: Node, bone_name: String, pos: Vector2) -> Bone2D:
    var bone:=Bone2D.new(); bone.name=bone_name; bone.position=pos; bone.set_autocalculate_length_and_angle(false); parent.add_child(bone); _bones[bone_name]=bone; return bone

func _part(parent:Node2D, part_name:String, col:int, row:int, scale_value:float, z:int) -> Sprite2D:
    var sprite:=Sprite2D.new(); sprite.name=part_name; sprite.texture=_rig_texture; sprite.region_enabled=true; sprite.region_rect=Rect2(col*TILE,row*TILE,TILE,TILE); sprite.centered=true; sprite.scale=Vector2.ONE*scale_value; sprite.z_index=z; sprite.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS; parent.add_child(sprite); _parts[part_name]=sprite; return sprite

func _animate_identity() -> void:
    if not is_instance_valid(_rig) or _bones.is_empty(): return
    var motion:=str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion: _animate_rifle()
    elif "SHIELD" in motion: _animate_shield()
    elif "DRONE" in motion: _animate_drone()
    elif "ABERRANT" in motion: _animate_aberrant()
    elif "BOSS" in motion or "ANCHOR" in motion: _animate_boss()

func _animate_rifle() -> void:
    var gait:float=sin(_phase*7.2)*0.28*minf(1.0,velocity.length()/maxf(1.0,105.0*run_speed_multiplier)); (_bones["leg_L"] as Bone2D).rotation=gait; (_bones["leg_R"] as Bone2D).rotation=-gait; (_bones["shin_L"] as Bone2D).rotation=-gait*.55; (_bones["shin_R"] as Bone2D).rotation=gait*.55; (_bones["body"] as Bone2D).rotation=sin(_phase*3.6)*.018; (_bones["weapon"] as Bone2D).rotation=_aim_dir.angle(); (_bones["arm_L"] as Bone2D).rotation=_aim_dir.angle()+.10; (_bones["arm_R"] as Bone2D).rotation=_aim_dir.angle()-.08
func _animate_shield() -> void:
    var stomp:float=absf(sin(_phase*4.1)); (_bones["body"] as Bone2D).position=(_base_positions["body"] as Vector2)+Vector2(0,stomp*3.2); (_bones["shield"] as Bone2D).rotation=-.06+sin(_phase*2.0)*.025; (_bones["hydraulic_arm"] as Bone2D).rotation=_aim_dir.angle()*.45; (_bones["weapon"] as Bone2D).rotation=_aim_dir.angle()*.55
func _animate_drone() -> void:
    (_bones["chassis"] as Bone2D).position=(_base_positions["chassis"] as Vector2)+Vector2(0,sin(_phase*3.8)*7.0); (_bones["chassis"] as Bone2D).rotation=sin(_phase*2.6)*.10; (_bones["fins"] as Bone2D).rotation=-sin(_phase*3.3)*.13; (_bones["thruster"] as Bone2D).scale=Vector2(1.0,1.0+sin(_phase*8.0)*.18); (_bones["sensor_cluster"] as Bone2D).rotation=sin(_phase*1.7)*.09
func _animate_aberrant() -> void:
    var gait:float=sin(_phase*6.6); (_bones["torso"] as Bone2D).position=(_base_positions["torso"] as Vector2)+Vector2(0,absf(gait)*4.5); (_bones["forelimb_L"] as Bone2D).rotation=.42+gait*.34; (_bones["forelimb_R"] as Bone2D).rotation=-.38-gait*.31; (_bones["leg_L"] as Bone2D).rotation=-gait*.38; (_bones["leg_R"] as Bone2D).rotation=gait*.38; (_bones["tail"] as Bone2D).rotation=sin(_phase*3.1-.8)*.32; (_bones["skull"] as Bone2D).rotation=-sin(_phase*3.3)*.07
func _animate_boss() -> void:
    var ring:=_bones["ring"] as Bone2D; ring.position=(_base_positions["ring"] as Vector2)+Vector2(0,sin(_phase*1.2)*9.0); ring.rotation=sin(_phase*.72)*.035; (_bones["iris"] as Bone2D).rotation=-_phase*.22; (_bones["distortion"] as Bone2D).rotation=_phase*.15
    for i in range(1,5):
        var arm:=_bones["arm_%d"%i] as Bone2D; arm.rotation=sin(_phase*1.35+float(i)*.8)*.18
        var pylon:=_bones["pylon_%d"%i] as Bone2D; pylon.scale=Vector2.ONE*(1.0+sin(_phase*1.1+float(i))*.035)

func _draw() -> void:
    var ratio:=clampf(health/maxf(1.0,max_health),0.0,1.0); var width:=58.0 if "BOSS" not in enemy_id else 130.0; var bar_y:=-82.0 if "BOSS" not in enemy_id else -242.0
    var radius:=30.0 if "BOSS" not in enemy_id else 82.0
    if brood_hatch_left > 0.0:
        var progress := 1.0 - brood_hatch_left / maxf(0.6, brood_hatch_duration)
        _brood_paint.clear()
        _brood_paint.ring(Vector2(0, 6), 34.0, 2.0, Color("9bda67", 0.45), 32, 0.0, TAU, 0.55)
        _brood_paint.ring(Vector2(0, 6), 34.0, 3.0, Color("9bda67", 0.9), 32, -PI * 0.5, -PI * 0.5 + TAU * progress, 0.55)
        _brood_paint.flush(get_canvas_item())
    # The scene already owns a foot ellipse and one overhead health UI.
    # Duplicating them here produced floating circles and double health bars.
    if get_node_or_null("OverheadUI") == null:
        draw_rect(Rect2(-width*.5,bar_y,width,5),Color("172028"),true)
        draw_rect(Rect2(-width*.5+1,bar_y+1,(width-2)*ratio,3),_projectile_color(),true)
    if _exposed_left>0.0:
        var sr:=radius+8.0; draw_arc(Vector2(0,5),sr,-2.7,-0.45,28,Color("70eadb",0.82),2.3); draw_arc(Vector2(0,5),sr,0.45,2.7,28,Color("70eadb",0.48),1.4)
    if _stagger_left>0.0:
        draw_arc(Vector2(0,5),radius+13.0,0.0,TAU,40,Color("ffc567",0.78),3.2)
        draw_line(Vector2(-12,bar_y-8),Vector2(12,bar_y-8),Color("ffdca0",0.85),2.0)

func debug_status_contract() -> Dictionary:
    return {"exposed":is_exposed(),"exposed_left":_exposed_left,"staggered":is_staggered(),"stagger_left":_stagger_left,"status_source":_status_source,"last_consumed_source":_last_consumed_source}

func debug_run_modifier_contract() -> Dictionary:
    return {
        "enemy_health_multiplier":run_health_multiplier,
        "enemy_damage_multiplier":run_damage_multiplier,
        "enemy_speed_multiplier":run_speed_multiplier,
        "enemy_attack_interval_multiplier":run_attack_interval_multiplier,
        "max_health":max_health,
        "health":health
    }
