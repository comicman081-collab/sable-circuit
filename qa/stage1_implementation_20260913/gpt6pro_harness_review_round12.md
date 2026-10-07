# Round12 — actual R11 reproduction and narrow corrections

Please verify only closure of R11-01/02/03/04 in the attached current code and tests. Prior H01/H02 and R8 remain closed. No new framework, old harness, or art approval is requested.

Your Round11 final reply was actually read. Locally I added its concrete cases BEFORE changing the bridge/Actor. Real Godot4.7.1 run: 871 assertions, 19 failures, including empty idle/walk acceptance, same frames repacked to2 columns, padding-only changed duplicate sequence, derived overflow, and moved WINDUP/BURST continuing. The before report and actual log are attached. The underflow negative was already rejected by the previous input path; I do not claim that case was newly reproduced as a failure. Before-code hashes match the Round11 bridge/Actor. The before test had only the initial counterexamples; five later assertions add derived-scale and valid alternate-layout positive controls, not relaxed assertions.

Fixes:
- R11-01: check every USED cell for complete invisibility before publishing a visual. No artificial opaque pixels or fallback source.
- R11-02: hash ordered used RGBA cells with invisible RGB canonicalized; no page dimensions/columns/unused pixels in the semantic identity. Cache key includes actual file hash, cell, columns and frame count. Valid distinct SE4-column and NW2-column layouts still pass; distinct visible padding is ignored, not forbidden.
- R11-03: derive the cycle distance in a temporary and reject nonfinite/nonpositive results. Check derived scale and actual Vector2-scaled geometry before publishing. Cell dimensions are integral. Normal1.33*129.6/1.72 stays100.2139534883721; no gameplay speed change.
- R11-04: after real move_and_slide plus stage constraint, if an active candidate biped had nonzero measured displacement and Tactics is WINDUP/BURST, call existing interrupt(). Keep the actual position and commit that displacement; no origin snapshot masquerading as current, no silent target reacquisition during old warning. Tactics code itself is unchanged. The added test exercises actual Actor->Tactics ordering under stage correction at30/60/120Hz in WINDUP and the WINDUP-to-BURST transition, verifying cancellation, no continued emission and honest distance clock. Existing zero-displacement three-round cases remain positive controls.

Actual current Godot smoke: 876 assertions, no failures, empty stderr. Current report binds all five runtime/test hashes. Other reruns after shared Actor change: drone170, anchor271, machine436, MotionLab player PASS, ROOK1895/0. Old shutdown warnings remain in drone48, anchor78, player2 and ROOK68; warning counts vary with transient sound lifetime. They are not clean-exit or visual approval claims. The new bridge smoke cleans only its test process's own transient audio nodes.

The skill now documents the four safeguards and precise test scope: real physical wall is atdefault60Hz; explicit stage correction while locked is tested at30/60/120Hz. All synthetic64px images are technical fixtures, not character art or1080p visual evidence. The rifle art is still under a separate SE whole-cycle review. No production biped_asset pointer, no completed Stage1 MVP/deployment, no Luna end-to-end claim. Preserve the accepted three playable characters and1.8xscale.

Please distinguish your executed checks from our actual local Godot reports and static reasoning. If the four original counterexamples are closed, state that limited closure; identify any concrete remaining counterexample in this modified scope with exact code location.

## FILE: scripts/actors/enemy_actor.gd
SHA256: 807cf7b7f27cd4cec22fa63cfbdbcdaae2c49e815aaa6dda5409910975085b1a
```text
extends CharacterBody2D
class_name EnemyActor

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")
const TILE := 512.0

signal defeated(enemy: EnemyActor)
signal projectile_emitted(event: Dictionary)

@export var enemy_id := "ENM_SITE7_RIFLE_01"
@export var max_health := 100.0

var health := 100.0
var art_profile: Dictionary = {}
var home_position := Vector2.ZERO
var _phase := 0.0
var _attack_cd := 0.8
var _hit_flash := 0.0
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
var run_attack_interval_multiplier := 1.0

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

func _ready() -> void:
    add_to_group("prototype_targets")
    add_to_group("m3_enemies")
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    health = max_health
    home_position = global_position
    _orbit_sign = -1.0 if abs(enemy_id.hash()) % 2 == 0 else 1.0
    _build_high_res_visual()
    _load_reviewed_machine_source()
    _load_reviewed_biped_source()
    tactics = preload("res://scripts/combat/site7_enemy_tactics.gd").new()
    tactics.name = "Tactics"
    add_child(tactics)
    queue_redraw()

func configure(id_value: String, hp: float = -1.0) -> void:
    enemy_id = id_value
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    if hp > 0.0:
        max_health = hp
    health = max_health
    _exposed_left=0.0; _stagger_left=0.0; _status_source=""; _last_consumed_source=""
    if is_node_ready():
        _rebuild_visual()

func apply_run_modifiers(modifiers: Dictionary) -> void:
    run_health_multiplier = clampf(float(modifiers.get("enemy_health_multiplier",1.0)),0.5,3.0)
    run_damage_multiplier = clampf(float(modifiers.get("enemy_damage_multiplier",1.0)),0.5,3.0)
    run_speed_multiplier = clampf(float(modifiers.get("enemy_speed_multiplier",1.0)),0.5,2.0)
    run_attack_interval_multiplier = clampf(float(modifiers.get("enemy_attack_interval_multiplier",1.0)),0.5,2.0)
    max_health *= run_health_multiplier
    health = max_health

func apply_damage(amount: float) -> void:
    if amount<=0.0 or health<=0.0: return
    var guard := get_node_or_null("BossPhaseTransitionGuard")
    if guard and guard.has_method("debug_guard_active") and guard.debug_guard_active():
        return
    health = maxf(0.0, health - amount)
    _hit_flash = 1.0
    if health <= 0.0:
        remove_from_group("prototype_targets")
        remove_from_group("m3_enemies")
        velocity = Vector2.ZERO
        _death_left = 0.55
        if tactics: tactics.visible = false
        if get_node_or_null("OverheadUI"): get_node("OverheadUI").visible = false
        defeated.emit(self)
        return
    queue_redraw()

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
    _phase += delta
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
            velocity *= run_speed_multiplier
        else:
            velocity = velocity.move_toward(Vector2.ZERO, 260.0 * delta)
    var position_before_motion := global_position
    move_and_slide()
    var stage := get_parent()
    if stage and stage.has_method("constrain_battle_position"):
        global_position = stage.call("constrain_battle_position", global_position)
    if is_instance_valid(biped_sprite):
        var actual_displacement := global_position-position_before_motion
        # A physical correction changes the origin of an already announced
        # shot. Cancel it; do not continue the old warning from a new muzzle.
        if actual_displacement.length()>0.000001 and tactics and tactics.state in ["WINDUP","BURST"]:
            tactics.interrupt()
        biped_sprite.commit_displacement(actual_displacement)
    _animate_identity()
    if is_instance_valid(_rig):
        var tint:=Color.WHITE
        if _exposed_left>0.0: tint=tint.lerp(Color("8ff5e8"),0.26)
        if _stagger_left>0.0: tint=tint.lerp(Color("ffd17d"),0.32)
        _rig.modulate = tint.lerp(Color("ff8a8a"), _hit_flash * 0.68)
    queue_redraw()

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
    if _attack_cd > 0.0 or _stagger_left>0.0:
        return
    _attack_cd = interval * run_attack_interval_multiplier
    CombatFeedback.play_fire(get_tree(), art_profile)
    _spawn_projectile(dir)
    if "BOSS" in str(art_profile.get("projectile_profile", "")):
        _spawn_projectile(dir.rotated(-0.16))
        _spawn_projectile(dir.rotated(0.16))

func _spawn_projectile(dir: Vector2, emission_owner: Node = null, attack_serial: int = -1, ordinal: int = -1) -> void:
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
    if is_instance_valid(machine_sprite) or is_instance_valid(biped_sprite): return false
    var candidate := preload("res://scripts/animation/site7_machine_sprite.gd").new()
    candidate.name = "AuthoredMachine"
    add_child(candidate)
    if not candidate.configure(self,spec):
        candidate.queue_free()
        return false
    machine_sprite = candidate
    _visual_root.visible = false
    return true

func preview_biped_source(spec: Dictionary) -> bool:
    # Candidate-only explicit intake; no partial eight-view sets, no registry
    # mutation. A reviewed package pointer is a separate promotion operation.
    if is_instance_valid(machine_sprite) or is_instance_valid(biped_sprite): return false
    var candidate := preload("res://scripts/animation/site7_biped_sprite.gd").new()
    candidate.name="AuthoredBiped"
    add_child(candidate)
    if not candidate.configure(self,spec):
        candidate.queue_free()
        return false
    biped_sprite=candidate
    _visual_root.visible=false
    return true

func _load_reviewed_biped_source() -> void:
    var binding: Variant=art_profile.get("biped_asset",{})
    if not binding is Dictionary or binding.is_empty(): return
    var path := str(binding.get("spec",""))
    if not path.begins_with("res://assets/enemies/") or ".." in path or not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != str(binding.get("sha256","")):
        push_error("Reviewed biped spec is missing or changed: "+enemy_id);return
    var spec: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
    if not spec is Dictionary or str(spec.get("enemy_id","")) != enemy_id:
        push_error("Reviewed biped identity mismatch: "+enemy_id);return
    if not preview_biped_source(spec): push_error("Reviewed biped intake failed: "+enemy_id)

func _load_reviewed_machine_source() -> void:
    if not bool(ProjectSettings.get_setting("sable_visuals/site7_authored_machines",true)): return
    var binding: Dictionary = art_profile.get("machine_asset",{})
    if binding.is_empty(): return
    var path := str(binding.get("spec",""))
    if not path.begins_with("res://assets/enemies/") or FileAccess.get_sha256(path) != str(binding.get("sha256","")):
        push_error("Reviewed machine spec is missing or changed: "+enemy_id);return
    var spec: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
    if not spec is Dictionary or str(spec.get("enemy_id","")) != enemy_id:
        push_error("Reviewed machine identity mismatch: "+enemy_id);return
    if not preview_machine_source(spec): push_error("Reviewed machine intake failed: "+enemy_id)

func _muzzle_distance() -> float:
    if "BOSS" in enemy_id: return 92.0
    if "SHIELD" in enemy_id: return 44.0
    if "DRONE" in enemy_id: return 38.0
    return 34.0

func _projectile_color() -> Color:
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
    _load_reviewed_biped_source()

func _build_high_res_visual() -> void:
    _visual_root = Node2D.new()
    _visual_root.name = "HighResVisualRoot"
    add_child(_visual_root)
    _hidden_master = Sprite2D.new(); _hidden_master.name="UniqueMasterSprite"; _hidden_master.visible=false
    var master_path := str(art_profile.get("master_asset", ""))
    if not master_path.is_empty() and ResourceLoader.exists("res://" + master_path): _hidden_master.texture=load("res://"+master_path) as Texture2D
    _visual_root.add_child(_hidden_master)
    var rig_path := str(art_profile.get("rig_sheet", ""))
    if not rig_path.is_empty() and ResourceLoader.exists("res://" + rig_path): _rig_texture=load("res://"+rig_path) as Texture2D
    _rig=Skeleton2D.new(); _rig.name="UniqueLayerRig"; _visual_root.add_child(_rig)
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
    if not is_instance_valid(_rig): return
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

```

## FILE: scripts/animation/site7_biped_sprite.gd
SHA256: f654151fe478c7c6b90a0b0d3b31329e98017ef0665a360d1a22e63a313729e2
```text
extends Node2D
## Whole authored Motion Studio frames for enemy bipeds. Candidate intake does
## not publish a registry entry or authorize art. AI owns speeds and attacks;
## this node owns only source pixels, distance phase and the visible muzzle.
const DIRECTIONS := ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const MAX_TARGET_ERROR := PI / 8.0 + 0.02
const IDENTITIES := {"ENM_SITE7_RIFLE_01":"site7_rifle", "ENM_SITE7_SHIELD_01":"site7_shield"}
var actor: EnemyActor
var sprite: Sprite2D
var configured := false
var clips: Dictionary = {}
var textures: Dictionary = {}
var facing := 4
var phase := 0.0
var moving := false
var move_direction := Vector2.RIGHT
var action := "idle"
var frame := 0
var cell := Vector2.ZERO
var root_px := Vector2.ZERO
var display_height := 129.6
var render_scale := 1.0
var cycle_distance := 1.0
var emitter_px := Vector2.ZERO
static var _pixel_hash_cache: Dictionary = {}

static func _used_sequence_hash(image: Image, file_hash: String, size: Vector2i, columns: int, count: int) -> String:
    # Hash the displayed cells in order, not atlas packaging/padding. The same
    # page can be interpreted differently, so geometry belongs in the cache key.
    var cache_key := file_hash+":"+str(size)+":"+str(columns)+":"+str(count)
    if _pixel_hash_cache.has(cache_key): return _pixel_hash_cache[cache_key]
    var canonical := image.duplicate() as Image
    canonical.convert(Image.FORMAT_RGBA8)
    var digest := HashingContext.new()
    digest.start(HashingContext.HASH_SHA256)
    digest.update((str(size)+":"+str(count)+":ordered-used-RGBA8:").to_utf8_buffer())
    for index in range(count):
        var used := canonical.get_region(Rect2i(Vector2i(index%columns,int(index/columns))*size,size))
        if used.is_invisible(): return ""
        var bytes := used.get_data()
        for alpha in range(3,bytes.size(),4):
            if bytes[alpha]==0:
                bytes[alpha-3]=0;bytes[alpha-2]=0;bytes[alpha-1]=0
        digest.update(bytes)
    var value := digest.finish().hex_encode()
    _pixel_hash_cache[cache_key]=value
    return value

static func _number(value: Variant) -> bool:
    return (value is int or value is float) and is_finite(float(value))

static func _point(value: Variant) -> Vector2:
    if not value is Array or value.size() != 2 or not _number(value[0]) or not _number(value[1]): return Vector2.INF
    return Vector2(float(value[0]),float(value[1]))

static func _path(value: Variant) -> bool:
    return value is String and value.begins_with("res://") and not ".." in value and not "\\" in value

func configure(owner_actor: EnemyActor, spec: Dictionary) -> bool:
    if configured or not is_instance_valid(owner_actor): return false
    var identity := str(IDENTITIES.get(owner_actor.enemy_id,""))
    if identity.is_empty() or str(spec.get("character_id","")) != identity or str(spec.get("enemy_id","")) != owner_actor.enemy_id or spec.get("kind","") != "authored_biped8": return false
    var path: Variant = spec.get("profile","")
    if not _path(path) or not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != str(spec.get("profile_sha256","")): return false
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if not parsed is Dictionary or parsed.get("id","") != identity: return false
    var animation: Variant = parsed.get("animation",{})
    var locomotion: Variant = parsed.get("locomotion",{})
    var views: Variant = parsed.get("views",{})
    var atlas_files: Variant = spec.get("atlas_files",{})
    if not animation is Dictionary or animation.get("presentation","") != "authored_frames" or not locomotion is Dictionary or not views is Dictionary or not atlas_files is Dictionary: return false
    var height: Variant = spec.get("display_height",129.6)
    var metres: Variant = parsed.get("heightMetres",0)
    var stride: Variant = locomotion.get("walkStride",0)
    if not _number(height) or not _number(metres) or not _number(stride): return false
    if height < 56 or height > 240 or metres <= 0 or stride <= 0: return false
    var staged_distance := float(stride)*float(height)/float(metres)
    if not is_finite(staged_distance) or staged_distance <= 0.0: return false
    if views.size() != 8: return false
    var staged_clips: Dictionary = {}
    var staged_textures: Dictionary = {}
    var geometry: Dictionary = {}
    # No state/visible node is published until the complete set validates.
    for clip_action in ["idle","walk"]:
        var hashes: Array[String] = []
        var pixel_hashes: Array[String] = []
        for direction in DIRECTIONS:
            var view: Variant = views.get(direction,{})
            if not view is Dictionary: return false
            var clip: Variant = view.get(clip_action,{})
            if not clip is Dictionary: return false
            var size := _point(clip.get("cell",[]))
            var origin := _point(clip.get("root",[]))
            var source_height: Variant = clip.get("height",0)
            var count: Variant = clip.get("frames",0)
            var columns: Variant = clip.get("columns",0)
            if not size.is_finite() or not origin.is_finite() or size.x <= 0 or size.y <= 0: return false
            if size.x != floor(size.x) or size.y != floor(size.y): return false
            if not _number(source_height) or source_height <= 0 or source_height > size.y: return false
            var staged_scale := float(height)/float(source_height)
            if not is_finite(staged_scale) or staged_scale <= 0.0 or not (size*staged_scale).is_finite() or not (origin*staged_scale).is_finite(): return false
            if not Rect2(Vector2.ZERO,size).has_point(origin): return false
            if not _number(count) or count != (1 if clip_action == "idle" else 6) or not _number(columns) or columns < 1 or floor(float(columns)) != float(columns) or columns > count: return false
            var muzzles: Variant = clip.get("muzzles",[])
            if not muzzles is Array or muzzles.size() != count: return false
            for value in muzzles:
                if not Rect2(Vector2.ZERO,size).has_point(_point(value)): return false
            var starts: Variant = clip.get("phaseStarts",[])
            if clip_action == "walk":
                if not starts is Array or starts.size() != count: return false
                var previous := -1.0
                for value in starts:
                    if not _number(value) or value < 0 or value >= 1 or value <= previous: return false
                    previous = float(value)
                if float(starts[0]) != 0.0: return false
            if geometry.is_empty(): geometry={"cell":size,"root":origin,"height":float(source_height)}
            elif size != geometry.cell or origin != geometry.root or float(source_height) != geometry.height: return false
            var asset: Variant = clip.get("image","")
            if not asset is String or asset.is_empty() or asset.begins_with("/") or ":" in asset or ".." in asset or "\\" in asset: return false
            var asset_root: Variant = spec.get("asset_root","")
            if not _path(asset_root) or not asset_root.ends_with("/"): return false
            var texture_path: String = asset_root+asset
            var expected := str(atlas_files.get(texture_path,""))
            if expected.length() != 64 or not FileAccess.file_exists(texture_path) or FileAccess.get_sha256(texture_path) != expected or hashes.has(expected): return false
            var image := Image.load_from_file(texture_path)
            if image == null or image.is_empty() or image.detect_alpha() == Image.ALPHA_NONE: return false
            if Vector2(image.get_size()) != Vector2(size.x*columns,size.y*ceil(float(count)/columns)): return false
            var pixel_hash := _used_sequence_hash(image,expected,Vector2i(size),int(columns),int(count))
            if pixel_hash.is_empty() or pixel_hashes.has(pixel_hash): return false
            pixel_hashes.append(pixel_hash)
            hashes.append(expected)
            var key: String = direction+"/"+clip_action
            staged_clips[key] = clip.duplicate(true)
            staged_textures[key] = ImageTexture.create_from_image(image)
    actor=owner_actor
    var initial_aim := global_transform.affine_inverse().basis_xform(actor._aim_dir)
    if initial_aim.is_finite() and initial_aim.length_squared()>0.000001:
        facing=int(floor(fposmod(initial_aim.angle()+PI/8.0,TAU)/(PI/4.0)))%8
    clips=staged_clips
    textures=staged_textures
    cell=geometry.cell
    root_px=geometry.root
    display_height=float(height)
    render_scale=display_height/float(geometry.height)
    # Metres are converted using THIS source height, not player speed or a
    # hard-coded 100px/m. Actual world displacement is the sole phase clock.
    cycle_distance=staged_distance
    sprite=Sprite2D.new()
    sprite.name="AuthoredBipedPixels"
    sprite.centered=false
    sprite.region_enabled=true
    sprite.region_filter_clip_enabled=true
    sprite.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.set_meta("preserve_authored_material",true)
    sprite.position=-root_px*render_scale
    sprite.scale=Vector2.ONE*render_scale
    add_child(sprite)
    configured=true
    sync_pose()
    return true

func _render_phase(sector: int) -> float:
    var heading := global_transform.basis_xform(Vector2.from_angle(sector*PI/4.0)).normalized()
    return fposmod(1.0-phase,1.0) if move_direction.dot(heading) < -0.35 else phase

func _frame_for(clip: Dictionary, at_phase: float) -> int:
    var starts: Array=clip.get("phaseStarts",[0.0])
    for index in range(starts.size()-1,-1,-1):
        if at_phase >= float(starts[index]): return index
    return 0

func commit_displacement(displacement: Vector2) -> void:
    if not configured or not displacement.is_finite(): return
    moving=displacement.length() > 0.000001 and actor.health > 0.0
    if moving:
        move_direction=displacement.normalized()
        phase=fposmod(phase+displacement.length()/cycle_distance,1.0)
    sync_pose()

func sync_pose() -> void:
    if not configured: return
    action="walk" if moving and actor.health > 0.0 else "idle"
    var key: String=DIRECTIONS[facing]+"/"+action
    var clip: Dictionary=clips[key]
    frame=_frame_for(clip,_render_phase(facing)) if action == "walk" else 0
    var columns: int=clip.columns
    sprite.texture=textures[key]
    sprite.region_rect=Rect2(Vector2(frame%columns,floor(float(frame)/columns))*cell,cell)
    emitter_px=_point(clip.muzzles[frame])
    sprite.modulate=Color.WHITE.lerp(Color(1.3,1.15,1.25),actor._hit_flash*0.4)

func resolve_target(target: Vector2, stationary: bool = false) -> Vector2:
    if not configured or not target.is_finite(): return Vector2.INF
    if stationary: moving=false
    var selected_action := "walk" if moving else "idle"
    var best := facing
    var error := INF
    for sector in range(8):
        var clip: Dictionary=clips[DIRECTIONS[sector]+"/"+selected_action]
        var index := _frame_for(clip,_render_phase(sector)) if selected_action == "walk" else 0
        var muzzle := to_global((_point(clip.muzzles[index])-root_px)*render_scale)
        var offset := target-muzzle
        if offset.length_squared() < 0.000001: continue
        var heading := global_transform.basis_xform(Vector2.from_angle(sector*PI/4.0)).normalized()
        var candidate_error := absf(heading.angle_to(offset.normalized()))
        if candidate_error < error:
            error=candidate_error
            best=sector
    sync_pose()
    if error > MAX_TARGET_ERROR: return Vector2.INF
    facing=best
    sync_pose()
    return (target-muzzle_world()).normalized()

func muzzle_world() -> Vector2:
    sync_pose()
    return to_global((emitter_px-root_px)*render_scale)

func visible_heading_world() -> Vector2:
    return global_transform.basis_xform(Vector2.from_angle(facing*PI/4.0)).normalized()

func hit_rect_world() -> Rect2:
    return _world_rect(Rect2(Vector2(-display_height*0.17,-display_height*0.81),Vector2(display_height*0.34,display_height*0.79)))

func visual_rect_world() -> Rect2:
    return _world_rect(Rect2(-root_px*render_scale,cell*render_scale))

func _world_rect(local_rect: Rect2) -> Rect2:
    var result := Rect2(to_global(local_rect.position),Vector2.ZERO)
    for corner in [local_rect.position+Vector2(local_rect.size.x,0),local_rect.end,local_rect.position+Vector2(0,local_rect.size.y)]:
        result=result.expand(to_global(corner))
    return result

```

## FILE: scripts/combat/site7_enemy_tactics.gd
SHA256: efacd6facda231852c947cb26572cc873ed022d62bb5ddf1ef55b2c8b260bd02
```text
extends Node2D
## Enemy attack controller. Authored art reads these states; it never supplies AI.
const Warning := preload("res://scripts/combat/site7_attack_warning.gd")
const ROLES := {"ENM_SITE7_RIFLE_01":"rifle", "ENM_SITE7_SHIELD_01":"shield",
    "ENM_SITE7_DRONE_01":"drone", "ENM_SITE7_ABERRANT_01":"melee", "BOSS_SITE7_ANCHOR_01":"boss"}
const LUNGE_SPEED := 360.0
const LUNGE_DURATION := 0.42
const LUNGE_RADIUS := 58.0
signal attack_started(event: Dictionary)

var actor: EnemyActor
var state := "REPOSITION"
var state_left := 0.7
var state_duration := 0.7
var locked_aim := Vector2.LEFT
var locked_ground := Vector2.LEFT
var burst_left := 0
var burst_clock := 0.0
var phase := 1
var attack_serial := 0
var shots_fired := 0
var lunges := 0
var _struck: Array[int] = []
var _age := 0.0
var _lunge_origin := Vector2.ZERO
var _lunge_reach := 0.0
var _shot_ordinal := 0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    top_level = true
    z_index = 1

func _enter(next_state: String, duration: float) -> void:
    state = next_state
    state_left = duration
    state_duration = maxf(duration, 0.001)
    # Stagger skips step(). Invalidate THIS CanvasItem's cached warning now.
    queue_redraw()

func interrupt() -> void:
    burst_left = 0
    _struck.clear()
    _enter("RECOVER", 0.55)

func step(target: OperatorActor, delta: float) -> void:
    global_transform = Transform2D(0.0, actor.global_position)
    var role := str(ROLES.get(actor.enemy_id,""))
    if role.is_empty():
        actor.velocity = Vector2.ZERO
        _enter("UNSUPPORTED_ROLE",1.0)
        return
    _age += delta
    state_left -= delta
    var offset := target.global_position - actor.global_position
    var dist := offset.length()
    var toward := offset.normalized() if dist > 0.01 else Vector2.LEFT
    # Do not even resolve a new visual yaw while an announced attack is locked.
    # Its body, muzzle and shot must retain the same warning direction.
    var aim := locked_aim
    if state not in ["WINDUP", "BURST", "LUNGE"]:
        aim = actor.aim_from_emitter(target.get_combat_aim_point())
        if not _valid_aim(aim): aim = actor._aim_dir
    var boss := role == "boss"
    var rifle := role == "rifle"
    var shield := role == "shield"
    var drone := role == "drone"
    var melee := role == "melee"
    phase = 1 if actor.health > actor.max_health * 0.66 else (2 if actor.health > actor.max_health * 0.33 else 3)
    actor.velocity = Vector2.ZERO
    actor._aim_dir = locked_aim if state in ["WINDUP", "BURST", "LUNGE"] else aim
    if state == "REPOSITION":
        if drone:
            var tangent := toward.orthogonal() * actor._orbit_sign
            actor.velocity = (tangent * 0.72 + toward * clampf((dist - 280.0) / 160.0, -0.7, 0.7)).limit_length(1.0) * 118.0
        elif melee:
            actor.velocity = toward * 112.0 if dist > 85.0 else Vector2.ZERO
        elif shield:
            actor.velocity = toward * 62.0 if dist > 190.0 else Vector2.ZERO
        elif rifle:
            var radial := 1.0 if dist > 360.0 else (-0.7 if dist < 220.0 else 0.0)
            actor.velocity = (toward * radial + toward.orthogonal() * actor._orbit_sign * 0.38).limit_length(1.0) * 86.0
        if state_left <= 0.0 and (not melee or dist < 250.0):
            var reposition_velocity := actor.velocity
            actor.velocity = Vector2.ZERO
            # Stop/bank first, then freeze the actual emitter ray. Never home
            # a telegraphed shot onto the player's later position.
            var candidate_aim := actor.aim_from_emitter(target.get_combat_aim_point())
            if not _valid_aim(candidate_aim):
                # The target may be inside every authored emitter offset.
                # Keep moving normally; do not advertise or emit a reverse ray.
                actor.velocity = reposition_velocity
                queue_redraw()
                return
            locked_aim = candidate_aim
            locked_ground = toward
            _lunge_origin = actor.global_position
            _lunge_reach = LUNGE_SPEED * LUNGE_DURATION * actor.run_speed_multiplier
            actor._aim_dir = locked_aim
            actor.velocity = Vector2.ZERO
            _enter("WINDUP", 0.95 if boss else (0.7 if shield else (0.6 if melee else 0.48)))
    elif state == "WINDUP":
        if state_left <= 0.0:
            attack_serial += 1
            _shot_ordinal = 0
            attack_started.emit({"actor_id":actor.get_instance_id(),"enemy_id":actor.enemy_id,
                "attack_serial":attack_serial,"phase":phase,"owner_id":get_instance_id()})
            if melee:
                lunges += 1
                _struck.clear()
                _enter("LUNGE", LUNGE_DURATION)
            elif boss:
                _boss_attack(target)
                _enter("RECOVER", (1.8 - float(phase) * 0.20) * actor.run_attack_interval_multiplier)
            else:
                burst_left = 3 if rifle else 1
                burst_clock = 0.0
                _enter("BURST", 0.5)
    elif state == "BURST":
        burst_clock -= delta
        if burst_left > 0 and burst_clock <= 0.0:
            _fire(locked_aim)
            burst_left -= 1
            burst_clock += 0.14
        if burst_left <= 0:
            _enter("RECOVER", (1.4 if shield else 0.85) * actor.run_attack_interval_multiplier)
    elif state == "LUNGE":
        actor.velocity = locked_ground * LUNGE_SPEED
        for victim in get_tree().get_nodes_in_group("operators"):
            if not victim is OperatorActor or victim.is_downed() or _struck.has(victim.get_instance_id()):
                continue
            if lunge_contains(victim.global_position) and actor.global_position.distance_to(victim.global_position) < LUNGE_RADIUS:
                victim.apply_damage(18.0 * actor.run_damage_multiplier)
                _struck.append(victim.get_instance_id())
        if state_left <= 0.0:
            actor.velocity = Vector2.ZERO
            _enter("RECOVER", 1.1 * actor.run_attack_interval_multiplier)
    elif state == "RECOVER":
        if drone:
            actor.velocity = toward.orthogonal() * actor._orbit_sign * 62.0
        if state_left <= 0.0:
            _enter("REPOSITION", 0.9 if not boss else 0.45)
    queue_redraw()

func _valid_aim(direction: Vector2) -> bool:
    return direction.is_finite() and direction.length_squared() > 0.000001

func _fire(direction: Vector2) -> void:
    if not _valid_aim(direction): return
    shots_fired += 1
    CombatFeedback.play_fire(get_tree(), actor.art_profile)
    actor._spawn_projectile(direction, self, attack_serial, _shot_ordinal)
    _shot_ordinal += 1

func _boss_attack(target: OperatorActor) -> void:
    # Slow readable fan in phase one; frozen impact zones in two; cross lanes
    # in three. Large gaps are intentional. These are damaging, not fake decals.
    if phase >= 2 and attack_serial % 2 == 0:
        _warning("circle", target.global_position, Vector2.RIGHT)
        if phase == 3:
            var origin := actor.global_position
            for i in range(4):
                var ray := locked_ground.rotated(float(i) * PI * 0.5)
                _warning("lane", origin + ray * 100.0, ray)
    else:
        var count := 3 if phase == 1 else 5
        for i in range(count):
            _fire(locked_aim.rotated((float(i) - float(count - 1) * 0.5) * 0.22))

func _warning(kind: String, location: Vector2, direction: Vector2) -> void:
    var warning := Warning.new()
    warning.source = actor
    warning.kind = kind
    warning.top_level = true
    warning.ray = direction
    warning.windup = 1.15 if kind == "circle" else 1.35
    warning.damage = 20.0
    actor.get_parent().add_child(warning)
    warning.global_transform = Transform2D(0.0,location)

func lunge_contains(point: Vector2) -> bool:
    var offset := point - _lunge_origin
    var nearest := _lunge_origin + locked_ground * clampf(offset.dot(locked_ground),0.0,_lunge_reach)
    return point.distance_to(nearest) <= LUNGE_RADIUS

func _draw() -> void:
    if not is_instance_valid(actor) or actor.health <= 0.0 or state != "WINDUP":
        return
    var progress := 1.0 - clampf(state_left / state_duration, 0.0, 1.0)
    var color := Color("ef907e", 0.30 + progress * 0.42)
    if "ABERRANT" in actor.enemy_id:
        var base := to_local(_lunge_origin)
        var side := locked_ground.orthogonal() * LUNGE_RADIUS
        var tip := base + locked_ground * _lunge_reach
        draw_colored_polygon(PackedVector2Array([base-side,base+side,tip+side,tip-side]),Color(color,0.12))
        draw_circle(base,LUNGE_RADIUS,Color(color,0.12))
        draw_circle(tip,LUNGE_RADIUS,Color(color,0.12))
        draw_line(base-side,tip-side,color,1.8)
        draw_line(base+side,tip+side,color,1.8)
        var angle := locked_ground.angle()
        draw_arc(base,LUNGE_RADIUS,angle+PI/2,angle+3*PI/2,32,color,1.8)
        draw_arc(tip,LUNGE_RADIUS,angle-PI/2,angle+PI/2,32,color,1.8)
    else:
        var origin := to_local(actor.projectile_origin(locked_aim))
        draw_line(origin, origin + locked_aim * 300.0, color, 1.1)
    draw_arc(Vector2(0,6), 23.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 32, color, 2.0)

func contract() -> Dictionary:
    return {"state": state, "state_left": state_left, "locked_aim": locked_aim,
        "phase": phase, "attacks": attack_serial, "shots": shots_fired, "lunges": lunges,
        "contract_is_intent_not_validation":true,
        "role":ROLES.get(actor.enemy_id,"unsupported"),"lunge_radius":LUNGE_RADIUS,"lunge_reach":_lunge_reach}

```

## FILE: scripts/ui/enemy_overhead_ui.gd
SHA256: b46c788c0b07945790653bbafe0656fe1fa99361f5806de4438cff1f06367b22
```text
extends Node2D
class_name EnemyOverheadUI

var actor: EnemyActor
var _phase := 0.0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    z_as_relative = false
    z_index = 3200
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func bar_y_local() -> float:
    if actor == null: return -12.0
    if is_instance_valid(actor.biped_sprite):
        var bounds: Rect2=actor.biped_sprite.visual_rect_world()
        var top:=INF
        for corner in [bounds.position,bounds.position+Vector2(bounds.size.x,0),bounds.end,bounds.position+Vector2(0,bounds.size.y)]:
            top=minf(top,to_local(corner).y)
        return top-12.0
    if is_instance_valid(actor.machine_sprite):
        # Damage bounds deliberately omit antennas/pylons. A health bar must
        # clear the whole visible machine, not sit inside that inset hit box.
        var machine: Node2D=actor.machine_sprite
        var size: Vector2=machine.image_size
        var top:=INF
        for corner in [Vector2.ZERO,Vector2(size.x,0),size,Vector2(0,size.y)]:
            top=minf(top,to_local(machine.sprite.to_global(corner)).y)
        return top-12.0
    return actor.get_combat_hit_rect().position.y-actor.global_position.y-12.0

func _draw() -> void:
    if actor == null:
        return
    var ratio := clampf(actor.health/maxf(1.0,actor.max_health),0.0,1.0)
    var boss := "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id
    var width := 118.0 if boss else 48.0
    var y := bar_y_local()
    var accent := _accent()

    # Backplate + thin luminous outline.
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(0.015,0.022,0.028,0.88),true)
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(accent.r,accent.g,accent.b,0.24),false,1.0)
    draw_rect(Rect2(-width*0.5,y,width,4.0),Color("182329"),true)

    # Segmented health fill.
    var segments := 12 if boss else 6
    var segment_w := (width-float(segments-1)*2.0)/float(segments)
    for i in range(segments):
        var threshold := float(i)/float(segments)
        var filled := ratio > threshold
        var x := -width*0.5 + float(i)*(segment_w+2.0)
        draw_rect(Rect2(x,y,segment_w,4.0),Color(accent,0.95 if filled else 0.12),true)

    # Small threat chevron. Boss gets a phase-reactive double marker.
    var pulse := 0.72 + sin(_phase*4.0)*0.16
    var marker_y := y-10.0
    var pts := PackedVector2Array([Vector2(-6,marker_y),Vector2(6,marker_y),Vector2(0,marker_y+6)])
    draw_colored_polygon(pts,Color(accent.r,accent.g,accent.b,pulse))
    if boss:
        var phase := 1 if ratio>0.66 else (2 if ratio>0.33 else 3)
        if phase>=2:
            draw_arc(Vector2.ZERO,94.0+phase*5.0,-PI*0.82,-PI*0.18,28,Color(accent.r,accent.g,accent.b,0.18+phase*0.06),2.0+phase)

func _accent() -> Color:
    if actor == null: return Color("f05b68")
    if "RIFLE" in actor.enemy_id: return Color("ef6470")
    if "SHIELD" in actor.enemy_id: return Color("e5a94d")
    if "DRONE" in actor.enemy_id: return Color("e45a91")
    if "ABERRANT" in actor.enemy_id: return Color("bd61da")
    if "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id:
        var ratio := actor.health/maxf(1.0,actor.max_health)
        return Color("f0529d") if ratio<=0.33 else Color("9179ff")
    return Color("f05b68")

```

## FILE: tests/smoke/site7_biped_bridge_smoke.gd
SHA256: 94c8db7af701911bb6f8fa5a16ac5526858e9946e1714b3679239595931b8c6b
```text
extends SceneTree
## Test-only coloured cells, NEVER character artwork or visual approval.
## No production registry is changed; incomplete rifle art stays quarantined.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const BRIDGE := preload("res://scripts/animation/site7_biped_sprite.gd")
const NAMES := ["E","SE","S","SW","W","NW","N","NE"]
var checks := 0
var failures: Array[String] = []
var emissions: Array[Dictionary] = []
var output := ""
var fixture_profile: Dictionary = {}
var fixture_spec: Dictionary = {}
var fixture_number := 0

class BoundsFixture extends Node2D:
    var locked_position := Vector2.ZERO
    func constrain_battle_position(_value: Vector2) -> Vector2: return locked_position

func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks+=1
    if not ok: failures.append(label);push_error(label)

func write_json(path: String, value: Variant) -> void:
    var file := FileAccess.open(path,FileAccess.WRITE)
    file.store_string(JSON.stringify(value,"  "));file.close()

func save_spec(profile: Dictionary) -> Dictionary:
    fixture_number+=1
    var path := output+"/profile_"+str(fixture_number)+".json"
    write_json(path,profile)
    var spec := fixture_spec.duplicate(true)
    spec.profile=path
    spec.profile_sha256=FileAccess.get_sha256(path)
    return spec

func make_fixture() -> void:
    fixture_profile={"id":"site7_rifle","heightMetres":1.72,"animation":{"presentation":"authored_frames"},"locomotion":{"walkStride":1.33},"views":{}}
    fixture_spec={"kind":"authored_biped8","enemy_id":"ENM_SITE7_RIFLE_01","character_id":"site7_rifle","asset_root":output+"/","display_height":129.6,"atlas_files":{}}
    for sector in range(8):
        var view: Dictionary={}
        for act in ["idle","walk"]:
            var count := 1 if act == "idle" else 6
            var columns := 1 if act == "idle" else 3
            var image := Image.create(64*columns,64*(1 if act == "idle" else 2),false,Image.FORMAT_RGBA8)
            image.fill(Color.TRANSPARENT)
            var muzzles: Array=[]
            for index in range(count):
                var base := Vector2i((index%columns)*64,int(index/columns)*64)
                image.fill_rect(Rect2i(base+Vector2i(16,8),Vector2i(32,48)),Color.from_hsv(float(sector)/8,0.5+index*0.04,0.7))
                var tip := Vector2(32,32)+Vector2.from_angle(sector*PI/4.0)*(8.0+index)
                muzzles.append([tip.x,tip.y])
            var filename: String=NAMES[sector]+"_"+act+".png"
            var path:=output+"/"+filename
            check(image.save_png(path)==OK,"Write test-only synthetic cell "+filename)
            fixture_spec.atlas_files[path]=FileAccess.get_sha256(path)
            view[act]={"cell":[64,64],"root":[32,56],"height":48,"columns":columns,"frames":count,"image":filename,"muzzles":muzzles}
            if act == "walk":view[act].phaseStarts=[0.0,0.2,0.33,0.5,0.7,0.83]
        fixture_profile.views[NAMES[sector]]=view

func refuses(actor: EnemyActor, spec: Dictionary, label: String) -> void:
    var candidate := BRIDGE.new()
    actor.add_child(candidate)
    check(not candidate.configure(actor,spec),label)
    check(not candidate.configured and candidate.sprite==null,"Atomic rejection: "+label)
    candidate.free()

func test_atlas(profile: Dictionary, direction: String, act: String, filename: String, image: Image, columns: int) -> void:
    var path := output+"/"+filename
    check(image.save_png(path)==OK,"Write counterexample atlas "+filename)
    fixture_spec.atlas_files[path]=FileAccess.get_sha256(path)
    profile.views[direction][act].image=filename
    profile.views[direction][act].columns=columns

func repack_walk(columns: int, direction: String = "E") -> Image:
    var source := Image.load_from_file(output+"/"+direction+"_walk.png")
    var result := Image.create(columns*64,int(ceil(6.0/columns))*64,false,Image.FORMAT_RGBA8)
    result.fill(Color.TRANSPARENT)
    for index in range(6):
        result.blit_rect(source,Rect2i((index%3)*64,int(index/3)*64,64,64),Vector2i((index%columns)*64,int(index/columns)*64))
    return result

func review_input_counterexamples(actor: EnemyActor) -> void:
    var bad := fixture_profile.duplicate(true)
    var empty := Image.create(64,64,false,Image.FORMAT_RGBA8);empty.fill(Color.TRANSPARENT)
    test_atlas(bad,"NW","idle","empty_idle.png",empty,1)
    refuses(actor,save_spec(bad),"R11-01 empty idle cell rejected")
    bad=fixture_profile.duplicate(true)
    var partial := Image.load_from_file(output+"/SE_walk.png")
    partial.fill_rect(Rect2i(0,64,64,64),Color.TRANSPARENT)
    test_atlas(bad,"SE","walk","empty_walk_cell.png",partial,3)
    refuses(actor,save_spec(bad),"R11-01 empty used walk cell rejected")
    bad=fixture_profile.duplicate(true)
    test_atlas(bad,"SE","walk","repacked_columns2.png",repack_walk(2),2)
    refuses(actor,save_spec(bad),"R11-02 identical used cells repacked to two columns rejected")
    bad=fixture_profile.duplicate(true)
    var padded := repack_walk(4)
    test_atlas(bad,"E","walk","padded_e.png",padded,4)
    padded.set_pixel(140,90,Color.RED)
    test_atlas(bad,"SE","walk","padded_se.png",padded,4)
    refuses(actor,save_spec(bad),"R11-02 unused padding cannot disguise duplicate used sequence")
    bad=fixture_profile.duplicate(true);bad.locomotion.walkStride=1.0e308
    refuses(actor,save_spec(bad),"R11-03 derived cycle distance overflow rejected")
    bad=fixture_profile.duplicate(true);bad.locomotion.walkStride=1.0e-308;bad.heightMetres=1.0e308
    refuses(actor,save_spec(bad),"R11-03 derived cycle distance underflow rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.height=1.0e-308
    refuses(actor,save_spec(bad),"R11-03 invalid derived render scale rejected")
    # Real distinct sequences remain accepted with a different valid layout;
    # unused padding is ignored for identity, not forbidden unconditionally.
    var good := fixture_profile.duplicate(true)
    var unique := repack_walk(4,"SE");unique.set_pixel(140,90,Color.RED)
    test_atlas(good,"SE","walk","valid_unique_padded.png",unique,4)
    test_atlas(good,"NW","walk","valid_unique_columns2.png",repack_walk(2,"NW"),2)
    var candidate := BRIDGE.new();actor.add_child(candidate)
    check(candidate.configure(actor,save_spec(good)),"R11-02 distinct used sequences survive alternate layouts and padding")
    candidate.free()

func run() -> void:
    output="res://qa/stage1_implementation_20260913/biped_bridge_"+str(Time.get_unix_time_from_system()).replace(".","_")
    DirAccess.make_dir_recursive_absolute(output)
    var registry_hash := FileAccess.get_sha256("res://data/art_profiles/enemy_profiles.json")
    make_fixture()
    var spec:=save_spec(fixture_profile)
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_RIFLE_01",100.0)
    root.add_child(actor);actor.set_physics_process(false)
    check(not is_instance_valid(actor.biped_sprite),"Unfinished rifle has no production binding")
    review_input_counterexamples(actor)
    var bad := fixture_profile.duplicate(true)
    bad.views.erase("NE");refuses(actor,save_spec(bad),"Partial direction set rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.phaseStarts=[0,0.2,0.2,0.5,0.7,0.83]
    refuses(actor,save_spec(bad),"Duplicate phase start rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.muzzles[3]=[90,20]
    refuses(actor,save_spec(bad),"Out-of-cell muzzle rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.muzzles[3]=["NaN",20]
    refuses(actor,save_spec(bad),"Nonnumeric muzzle rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.image="../outside.png"
    refuses(actor,save_spec(bad),"Traversal path rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.image=bad.views.E.walk.image
    refuses(actor,save_spec(bad),"One file reused for two directions rejected")
    var duplicate := Image.load_from_file(output+"/E_walk.png")
    duplicate.set_pixel(0,0,Color(1,0,0,0))
    duplicate.save_png(output+"/hidden_rgb_duplicate.png")
    fixture_spec.atlas_files[output+"/hidden_rgb_duplicate.png"]=FileAccess.get_sha256(output+"/hidden_rgb_duplicate.png")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.image="hidden_rgb_duplicate.png"
    check(fixture_spec.atlas_files[output+"/hidden_rgb_duplicate.png"]!=fixture_spec.atlas_files[output+"/E_walk.png"],"Hidden-RGB fixture changes file bytes")
    refuses(actor,save_spec(bad),"Different file hash cannot disguise duplicate visible direction")
    var broken := spec.duplicate(true);broken.profile_sha256="invalid"
    refuses(actor,broken,"Changed profile rejected")
    broken=spec.duplicate(true);broken.atlas_files[output+"/SE_walk.png"]="invalid"
    refuses(actor,broken,"Changed atlas rejected")
    broken=spec.duplicate(true);broken.enemy_id="ENM_SITE7_SHIELD_01"
    refuses(actor,broken,"Wrong enemy role rejected")
    actor._aim_dir=Vector2.UP
    check(actor.preview_biped_source(spec),"Complete candidate intake")
    if not is_instance_valid(actor.biped_sprite):actor.free();quit(1);return
    var bridge: Node2D=actor.biped_sprite
    check(bridge.facing==6,"Initial view respects actor aim before first tactics step")
    check(not actor._visual_root.visible and bridge.sprite.visible,"Candidate replaces only its own mock")
    check(is_equal_approx(bridge.cycle_distance,1.33*129.6/1.72),"NPC metre conversion uses own source height")
    check(actor.max_health==100.0 and actor.run_speed_multiplier==1.0,"No AI health/speed overwritten from Studio")
    for hz in [30,60,120]:
        for move_sector in range(8):
            for aim_sector in range(8):
                bridge.phase=0.0
                bridge.facing=aim_sector
                var movement: Vector2=Vector2.from_angle(move_sector*PI/4.0)*86.0/float(hz)
                for tick in range(hz):bridge.commit_displacement(movement)
                check(absf(bridge.phase-fposmod(86.0/bridge.cycle_distance,1.0))<0.00001,"Distance phase independent of Hz/movement/aim")
                check(bridge.action=="walk" and bridge.facing==aim_sector,"Whole-body movement retains aim sector")
                var saved: float=bridge.phase
                bridge.commit_displacement(Vector2.ZERO)
                for tick in range(5):bridge.sync_pose()
                check(bridge.action=="idle" and bridge.frame==0 and bridge.phase==saved,"Zero measured displacement has no time-driven legs")
    bridge.phase=0.23;bridge.move_direction=Vector2.LEFT;bridge.moving=true;bridge.facing=0;bridge.sync_pose()
    check(bridge.frame==4,"Reverse travel selects reversed authored phase, not warped limbs")
    bridge.move_direction=Vector2.RIGHT;bridge.sync_pose()
    check(bridge.frame==1,"Forward travel retains ordinary phase")
    var victim:=OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    actor.projectile_emitted.connect(func(event: Dictionary) -> void:emissions.append(event))
    for hz in [30,60,120]:
        for sector in range(8):
            emissions.clear()
            var direction:=Vector2.from_angle(sector*PI/4.0)
            victim.global_position=direction*500.0
            actor.velocity=-direction*86.0
            bridge.commit_displacement(-direction*3.0)
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.step(victim,1.0/hz)
            var frozen_muzzle: Vector2=bridge.muzzle_world()
            var frozen_facing: int=bridge.facing
            var frozen_phase: float=bridge.phase
            var locked: Vector2=actor.tactics.locked_aim
            check(actor.tactics.state=="WINDUP" and bridge.action=="idle","Stop before acquiring announced idle emitter")
            check(bridge.visible_heading_world().dot(locked)>cos(PI/8.0+0.02),"Visible front agrees with warning ray")
            victim.global_position=-direction*500.0
            for tick in range(hz*2):
                actor.tactics.step(victim,1.0/hz)
                bridge.commit_displacement(Vector2.ZERO)
                if emissions.size()==3:break
            check(emissions.size()==3,"Real tactics emits exactly three rifle rounds")
            check(bridge.facing==frozen_facing and bridge.phase==frozen_phase and bridge.action=="idle","Target reversal during attack cannot turn body or cycle feet")
            for event in emissions:
                var origin:=Vector2(event.origin[0],event.origin[1])
                var shot_direction:=Vector2(event.direction[0],event.direction[1])
                check(origin.distance_to(frozen_muzzle)<0.001 and shot_direction.distance_to(locked)<0.001,"Actual creation boundary matches frozen visible muzzle/ray")
                var shot:=instance_from_id(event.projectile_id)
                if is_instance_valid(shot):shot.free()
            actor.tactics.state="REPOSITION";actor.tactics.state_left=1.0
            actor.tactics.step(victim,1.0/hz)
            check(bridge.visible_heading_world().dot(locked)<-0.8,"Next movement follows opposite target without smoothing lag")
    actor.velocity=Vector2.ZERO
    bridge.commit_displacement(Vector2.ZERO)
    check(not actor.aim_from_emitter(actor.global_position+Vector2(0,-64.8)).is_finite(),"Inside all emitter offsets rejects reverse shot")
    var previous_facing: int=bridge.facing
    check(not bridge.resolve_target(Vector2.INF).is_finite() and bridge.facing==previous_facing,"Invalid target preserves view")
    var old_texture: Texture2D=bridge.sprite.texture
    check(not bridge.configure(actor,spec) and bridge.sprite.texture==old_texture,"Repeated configure cannot replace active pixels")
    check(actor.get_node("OverheadUI").bar_y_local()<bridge.visual_rect_world().position.y-actor.global_position.y,"HUD stays above entire cell")
    var arena := BoundsFixture.new()
    root.add_child(arena)
    root.remove_child(actor);arena.add_child(actor)
    victim.global_position=Vector2(5000,0)
    actor.tactics.state="REPOSITION";actor.tactics.state_left=10.0
    var phase_before_bounds: float=bridge.phase
    actor._physics_process(1.0/60.0)
    check(actor.velocity.length()>0.0 and actor.global_position==Vector2.ZERO,"Actual enemy movement is clamped by stage boundary")
    check(bridge.phase==phase_before_bounds and bridge.action=="idle","Post-boundary actual displacement, not intended velocity, drives phase")
    for hz in [30,60,120]:
        for lock_state in ["WINDUP","BURST"]:
            arena.locked_position=Vector2.ZERO;actor.global_position=Vector2.ZERO
            victim.global_position=Vector2(500,0)
            bridge.phase=0.23;bridge.facing=0
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor._physics_process(1.0/float(hz))
            check(actor.tactics.state=="WINDUP" and bridge.action=="idle","R11-04 acquire normal announced idle")
            if lock_state=="BURST":actor.tactics.state_left=0.000001
            arena.locked_position=Vector2(1,0)
            emissions.clear()
            actor._physics_process(1.0/float(hz))
            check(actor.global_position==Vector2(1,0),"R11-04 retain actual physical correction")
            check(actor.tactics.state=="RECOVER","R11-04 moved warning/burst is interrupted")
            check(absf(bridge.phase-fposmod(0.23+1.0/bridge.cycle_distance,1.0))<0.00001,"R11-04 do not falsify corrected displacement phase")
            for tick in range(4):actor._physics_process(1.0/float(hz))
            check(emissions.is_empty(),"R11-04 no continuation fire from unannounced corrected origin")
            for event in emissions:
                var shot:=instance_from_id(event.projectile_id)
                if is_instance_valid(shot):shot.free()
    arena.locked_position=Vector2.ZERO;actor.global_position=Vector2.ZERO
    arena.remove_child(actor);root.add_child(actor);arena.free()
    var wall := StaticBody2D.new()
    wall.collision_layer=1;wall.collision_mask=2
    var wall_shape := CollisionShape2D.new()
    var rectangle := RectangleShape2D.new();rectangle.size=Vector2(20,200)
    wall_shape.shape=rectangle;wall.add_child(wall_shape)
    wall.position=Vector2(45,-18);root.add_child(wall)
    actor.global_position=Vector2.ZERO
    actor._orbit_sign=0.0
    bridge.phase=0.0
    actor.tactics.state="REPOSITION";actor.tactics.state_left=10.0
    actor.set_physics_process(true)
    var travel := 0.0
    var before := actor.global_position
    for tick in range(60):
        await physics_frame
        travel+=actor.global_position.distance_to(before)
        before=actor.global_position
    actor.set_physics_process(false)
    check(travel>5.0 and travel<18.0 and actor.get_slide_collision_count()>0,"Real move_and_slide stops on collision wall")
    check(absf(bridge.phase-fposmod(travel/bridge.cycle_distance,1.0))<0.001 and bridge.action=="idle","Actual collision distance agrees with phase and stops walking")
    wall.free()
    actor.configure("ENM_SITE7_SHIELD_01",155.0)
    check(not is_instance_valid(actor.biped_sprite) and not bridge.visible and actor._visual_root.visible,"Role replacement retires old candidate safely")
    check(not actor.preview_biped_source(spec),"Rifle cannot attach to shield")
    actor.free();victim.free()
    # Dispose only this isolated process's transient sound nodes and release
    # their streams before shutdown; production sound generation is unchanged.
    for node in root.get_children():
        if node is AudioStreamPlayer:
            node.stop();node.stream=null;node.queue_free()
    await process_frame
    check(FileAccess.get_sha256("res://data/art_profiles/enemy_profiles.json")==registry_hash,"Production registry is byte-unchanged")
    var hashes: Dictionary={}
    for path in ["scripts/animation/site7_biped_sprite.gd","scripts/actors/enemy_actor.gd","scripts/ui/enemy_overhead_ui.gd","scripts/combat/site7_enemy_tactics.gd","tests/smoke/site7_biped_bridge_smoke.gd"]: hashes[path]=FileAccess.get_sha256("res://"+path)
    write_json(output+"/report.json",{"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"sha256":hashes,"synthetic_fixtures_only":true,"visual_approval":false,"production_registry_changed":false})
    print("SITE7_BIPED_BRIDGE: ","PASS" if failures.is_empty() else "FAIL"," (",checks,") ",output)
    quit(0 if failures.is_empty() else 1)

```

## FILE: .agents/skills/sable-character-studio/references/enemy-facing.md
SHA256: 8ed8dfe4222f5205c58a55b9cebbddf5ad826e26d0e8780538037e5a6fe9c6c6
```text
# SITE-7 enemy facing: visible front, emitter and warning

Use for the current `site7_machine_sprite.gd` and enemy combat integration.
The 2026-09-13 user screenshot exposed a front-facing drone illustration being
reused while firing toward the opposite side. An omni **emitter** does not make
the whole vehicle's visible front omnidirectional. Do not repeat that shortcut.

- Flying drones use eight separately authored yaw views (`authored_yaw8`),
  exact texture hashes and per-view root/emitter coordinates. The runtime
  rejects missing views and repeated file OR visible-RGBA hashes before publishing
  the node. Metadata and RGB hidden under alpha=0 do not create new views.
  Hash uniqueness cannot judge whether the paintings show the correct angles.
- Use the ImageGen appearance authority; do not roll a 2D three-quarter picture
  around the screen or mirror asymmetric sensors to manufacture all views.
  Inspect front versus rear surfaces, appendage count, native alpha and the
  original-scale visible emitter. The separate three-sensor cluster is not the
  lower magenta firing orb. Preserve rejected four-thruster/mirrored-lens art.
- `resolve_target` selects an authored pose and solves that pose's actual
  emitter ray together. It evaluates candidates without committing eight
  texture changes per tick. The initial frame uses the actor's current aim.
  Movement velocity may oppose aim; orbiting does not turn the gun away.
- A nearest-angle result is not automatically valid: targets inside all gun
  offsets can leave every candidate pointing backward. `Vector2.INF` is an
  explicit invalid aim, not a shot direction. Keep the prior pose and reposition;
  do not enter WINDUP, fire a zero/non-finite ray, or invent a forward target.
- At WINDUP entry, stop/bank first and freeze pose plus aim. WINDUP/BURST/LUNGE
  must not resolve a fresh target or home the advertised attack. Recovery may
  respond to the new target immediately. This is intentionally different from
  the player's latest-pointer-input behavior.
- `_enter` invalidates the Tactics CanvasItem's own cached draw commands.
  Stagger skips `step`, so redrawing only EnemyActor leaves the old warning line.
  Check the native before/after warning pixels while stagger is still active.
- Legacy mock rifle/pistol/arm pixels already rotate around their bones to
  world aim. Applying `flip_h` to them again reverses the barrel. Keep those
  pixels unflipped while that mock remains; it is not an eight-view humanoid
  appearance solution and must not replace the pending authored biped cycle.
- Anchored machines retain their own stationary emitter/root contract. Do not
  force humanoid footsteps or a yawing chassis onto the stationary boss.

Current executable checks: `tests/smoke/site7_enemy_facing_smoke.gd` exercises
8 target directions at 30/60/120Hz, opposite movement, first-frame facing,
locked warnings, real projectile creation and opposite-target recovery. It also
rejects incomplete/duplicate views and checks actual mock barrel transforms.
`site7_machine_source_smoke.gd` checks actual image binding, transformed muzzle,
hit bounds, anchor stability and death presentation. Count actual projectile
objects/emission events, not all root children (audio is a separate child).

`tests/render/site7_machine_edge_case_smoke.gd` checks the R6 close-target,
metadata-only/hidden-RGB duplicate and interrupted-warning regressions. Run it
with actual rendering, not headless: the warning check reads native viewport
pixels as well as the Tactics draw signal. Synthetic PNGs are test-only.

Run native 1920x1080 captures in the real game scene and inspect all affected
view transitions. A test PASS or source contact sheet is not runtime visual
approval. `prepare_drone_directions.py` only produces isolated candidates/specs;
the app registry must not point at an unreviewed QA candidate automatically.
Keep player art, gait, 1.8x display scale and weapon timing unchanged.

## Current local app connection

The reviewed drone is now bound by `data/art_profiles/enemy_profiles.json`
to `assets/enemies/recon_drone/authored_yaw8_v1/spec.json`, with byte-identical
copies of the selected images. The app loader validates identity/spec hash and
each texture before hiding the existing visual. A failed candidate does not
erase the current visible node. Repeated configure and wrong-role intake fail.

Run `tests/smoke/site7_drone_app_smoke.gd` without disabling app intake. Unlike
the candidate smokes, it starts the normal registry path and advances actual
WINDUP-to-emission transitions at 30/60/120Hz. Capture the app path using
`tests/render/site7_enemy_facing_capture.gd -- --app-registry`. Retain the
candidate-only tests too; they still cover deliberately invalid input.

GPT 6 Pro round 7 closed the three R6 counterexamples by code/test comparison
and its own synthetic pixel/math checks. It did not run Godot, inspect the
drone art or certify this registry connection. Keep those scopes separate.

The fixed boss is also connected through the registry, at
`assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json`. Its central
iris emits; the four arm housings do not acquire independent yaw. Keep the
body/root stationary. `site7_anchor_app_smoke.gd` exercises normal app loading
and actual locked emissions. `site7_anchor_candidate_capture.gd -- --app-registry`
captures all three phases through real Tactics time advancement, with explicitly
controlled HP/attack serial fixtures; this is not a whole-operation playthrough.

For anchored-boss captures, frame the real `home_position`: the boss anchor
component restores it after an attempted fixture relocation. Require the
visible iris on-screen, not merely a decoded 1080p screenshot. The first
offscreen capture is retained as VISUAL_HOLD. Machine overhead bars use the
full transformed artwork corners, not inset damage bounds; the pylon otherwise
overlaps its health bar. `site7_machine_source_smoke.gd` covers these corners
under scaled/rotated transforms. Do not change damage bounds to fix a UI overlap.

Round8 capture regressions use `tests/render/site7_anchor_capture_smoke.gd`:
reject hidden artwork even with an on-screen iris; collect only this actor's
actual warning objects (phase2: one circle; phase3: one circle and four lanes).
Capture elapsed/windup/fired during the visible warning and impact window and
record real in-zone damage. Zero projectiles plus RECOVER does not prove a
ground attack happened. Do not label fixed-delay after-effects as a visible hit.
App-mode capture must not read a QA candidate spec; bind the normal registry's
actual spec hash. Candidate mode still explicitly rejects missing/malformed
JSON. The test-only no-warning subclass must never enter a runtime registry.
Visibility/geometry/clock checks do not replace observing the native pictures.

## Authored biped app bridge — candidate implementation, not art promotion

`scripts/animation/site7_biped_sprite.gd` accepts complete eight-view Motion
Studio walk/idle profiles for the rifle/shield roles only. It validates profile
and atlas hashes (including duplicate used-frame RGBA sequence rejection), geometry,
finite muzzle coordinates and six phase starts
before publishing the visual. A spec or test fixture is not an approval receipt.
Every used idle/walk cell must contain visible alpha. Hash the ordered used
cells independent of atlas columns and unused padding, canonicalizing invisible
RGB; include cell/columns/frame count in any interpretation cache key. A valid
file hash or a nonempty whole page does not prove each displayed cell exists.
Reject nonfinite/zero derived render scales and cycle distances before creating
the visible node; finite scalar inputs can still overflow during conversion.
The unfinished rifle still has **no** `biped_asset` production registry pointer.
Do not activate its E/SE-only sources, reuse one view eight times, borrow player
pixels, or use these technical checks as the missing cycle/runtime visual gate.

The NPC metre conversion is `walkStride * displayHeightPx / heightMetres`.
For this rifle that is 100.213953px per cycle, not the player's 160px cycle or
Studio weapon timing. `EnemyActor` commits actual global displacement AFTER
`move_and_slide` and stage constraints; zero displacement selects planted idle
without advancing phase. Reverse travel changes authored phase selection, not
body parts. At warning entry, select the stopped idle pose and its muzzle
together. Preserve both through WINDUP and the actual three-round burst; the
player's immediate retargeting policy must not home an enemy's announced shot.
If a real collision/stage position correction moves the emitter during
WINDUP/BURST, cancel that announced attack through Tactics and require a fresh
normal warning later. Keep the actual correction and distance accounting;
do not keep shooting from an old position or silently retarget the old warning.

`tests/smoke/site7_biped_bridge_smoke.gd` uses explicitly synthetic coloured
cells, not production art. It exercises the 8x8 movement/aim matrix at
30/60/120Hz, real Tactics/projectile emissions at those rates, malformed/partial
intake, reverse phase, a real collision wall and the actual stage-boundary
clamp. The real collision-wall case runs at default60Hz; explicit stage
corrections during WINDUP and transition to BURST run at30/60/120Hz. Preserve
that distinction from the all-rate movement/emission tests. It checks that the
production registry stays byte-unchanged. Also rerun the normal drone, boss,
machine and player Motion Studio smokes after changing shared EnemyActor code.

```

## FILE: data/art_profiles/enemy_profiles.json
SHA256: 549ca45d47ec39ea740776c9eccfd52323a00775da0a29b38e969baf4ec951a3
```text
{
  "schema_version": 1,
  "profiles": [
    {
      "enemy_id":"ENM_SITE7_RIFLE_01","name":"SITE-7 RIFLE TROOPER","tier":"NORMAL","visual_profile":"VIS_ENM_RIFLE_01",
      "master_asset":"assets/enemies/rifle_trooper/rifle_trooper_master.svg","rig_sheet":"assets/enemies/rifle_trooper/rifle_trooper_rig_sheet.svg",
      "silhouette":"narrow hazard hood, offset radio mast, split knee armor, long bullpup rifle","palette":["#D9E1E7","#43525C","#B83B45","#78A9B7"],
      "motion_profile":"MOT_ENM_RIFLE_01","motion_signature":"cautious shoulder-led patrol, quick alert snap, short lateral burst steps, disciplined three-round recoil",
      "projectile_profile":"PRJ_ENM_RIFLE_TRACER_01","projectile_signature":"red-white narrow tracer with intermittent dash gaps","hit_vfx_profile":"HIT_ENM_RIFLE_METAL_01","hit_vfx_signature":"small pale spark fork with red paint flecks","fire_sfx_profile":"SFX_FIRE_ENM_RIFLE_01","fire_sfx_signature":"dry suppressed mechanical crack with radio-like tail","impact_sfx_profile":"SFX_HIT_ENM_RIFLE_01","impact_sfx_signature":"thin plate ping and fabric thud"
    },
    {
      "enemy_id":"ENM_SITE7_SHIELD_01","name":"SITE-7 SHIELD BREACHER","tier":"ELITE","visual_profile":"VIS_ENM_SHIELD_01",
      "master_asset":"assets/enemies/shield_breacher/shield_breacher_master.svg","rig_sheet":"assets/enemies/shield_breacher/shield_breacher_rig_sheet.svg",
      "silhouette":"tall slab shield, forward helmet wedge, one exposed hydraulic arm, compact ram pistol","palette":["#C7D0D5","#2D3942","#E2A94E","#7D342E"],
      "motion_profile":"MOT_ENM_SHIELD_01","motion_signature":"slow shield-first advance, heavy stomp cadence, brace before fire, violent shoulder ram with long recover","projectile_profile":"PRJ_ENM_SHIELD_RAMSHOT_01","projectile_signature":"short fat brass plasma slug with rectangular shock wake","hit_vfx_profile":"HIT_ENM_SHIELD_PLATE_01","hit_vfx_signature":"broad angled spark sheet with shield-edge scrape streak","fire_sfx_profile":"SFX_FIRE_ENM_SHIELD_01","fire_sfx_signature":"compressed piston bark with shield resonance","impact_sfx_profile":"SFX_HIT_ENM_SHIELD_01","impact_sfx_signature":"thick steel gong with hydraulic rattle"
    },
    {
      "enemy_id":"ENM_SITE7_DRONE_01","name":"SITE-7 RECON DRONE","tier":"NORMAL","visual_profile":"VIS_ENM_DRONE_01",
      "machine_asset":{"spec":"res://assets/enemies/recon_drone/authored_yaw8_v1/spec.json","sha256":"0c716b309edfa5ecaa29cffef01642e23c855a3527a979a922002a9e8ad6b5ba"},
      "master_asset":"assets/enemies/recon_drone/recon_drone_master.svg","rig_sheet":"assets/enemies/recon_drone/recon_drone_rig_sheet.svg",
      "silhouette":"flat crescent chassis, three uneven sensor eyes, dangling micro-thruster, no humanoid limbs","palette":["#9DBAC7","#1D2A31","#D9577D","#65E1E8"],
      "motion_profile":"MOT_ENM_DRONE_01","motion_signature":"constant hover micro-orbit, asymmetric banking, scan pause, sudden lateral dart, rotational death tumble","projectile_profile":"PRJ_ENM_DRONE_BEAMLET_01","projectile_signature":"magenta dotted beamlet packets with cyan sensor ghost","hit_vfx_profile":"HIT_ENM_DRONE_ARC_01","hit_vfx_signature":"thin electric crescent arcs and falling pixel sparks","fire_sfx_profile":"SFX_FIRE_ENM_DRONE_01","fire_sfx_signature":"high servo chirp followed by clipped laser zip","impact_sfx_profile":"SFX_HIT_ENM_DRONE_01","impact_sfx_signature":"glass-electronic tick with unstable electrical sputter"
    },
    {
      "enemy_id":"ENM_SITE7_ABERRANT_01","name":"SITE-7 ABERRANT RUNNER","tier":"NORMAL","visual_profile":"VIS_ENM_ABERRANT_01",
      "master_asset":"assets/enemies/aberrant_melee/aberrant_melee_master.svg","rig_sheet":"assets/enemies/aberrant_melee/aberrant_melee_rig_sheet.svg",
      "silhouette":"long forelimbs, collapsed shoulder line, split mask-like skull plate, trailing biofilament tail","palette":["#C9C5BA","#302D32","#7F3FA4","#DA6B83"],
      "motion_profile":"MOT_ENM_ABERRANT_01","motion_signature":"uneven four-beat crouch gait, head lag, explosive lunge, elastic recoil and twitching recovery","projectile_profile":"PRJ_ENM_ABERRANT_SPIT_01","projectile_signature":"slow violet organic glob with whipping filament tail","hit_vfx_profile":"HIT_ENM_ABERRANT_BIO_01","hit_vfx_signature":"wet magenta membrane tear with dark filament snapback","fire_sfx_profile":"SFX_FIRE_ENM_ABERRANT_01","fire_sfx_signature":"throat click into viscous whip release","impact_sfx_profile":"SFX_HIT_ENM_ABERRANT_01","impact_sfx_signature":"damped flesh strike with fibrous tear"
    },
    {
      "enemy_id":"BOSS_SITE7_ANCHOR_01","name":"SIGNAL ANCHOR GUARDIAN","tier":"BOSS","visual_profile":"VIS_BOSS_ANCHOR_01",
      "machine_asset":{"spec":"res://assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json","sha256":"c3f98d11fc537fd5e7d542e7114296cdc0c12b7f2f4877e71c1bd6fed194b763"},
      "master_asset":"assets/enemies/signal_anchor_guardian/signal_anchor_guardian_master.svg","rig_sheet":"assets/enemies/signal_anchor_guardian/signal_anchor_guardian_rig_sheet.svg",
      "silhouette":"massive suspended ring body, offset armored pylons, four articulated emitter arms, exposed inner signal iris","palette":["#2A313B","#8572FF","#F0529D","#E7E0FF"],
      "motion_profile":"MOT_BOSS_ANCHOR_01","motion_signature":"slow orbital idle, pylon breathing, arm-by-arm charge choreography, phase-transition ring inversion, heavy camera-readable attacks","projectile_profile":"PRJ_BOSS_ANCHOR_LANCE_01","projectile_signature":"wide violet-magenta lance segment with rotating black notches and lingering distortion ribs","hit_vfx_profile":"HIT_BOSS_ANCHOR_RIFT_01","hit_vfx_signature":"large iris-shaped rupture, violet radial shards and inward-pulling black streaks","fire_sfx_profile":"SFX_FIRE_BOSS_ANCHOR_01","fire_sfx_signature":"layered resonant charge chord collapsing into a hard spatial crack","impact_sfx_profile":"SFX_HIT_BOSS_ANCHOR_01","impact_sfx_signature":"low structural boom plus reversed crystalline suction"
    }
  ]
}

```

## FILE: qa/stage1_implementation_20260913/biped_bridge_1789298056_896/report.json
SHA256: 355043578bc6fa9cd70e8c33f21ce482ebd3a6fcd8e64d7c5b0380023690ceeb
```text
{
  "checks": 871,
  "failures": [
    "R11-01 empty idle cell rejected",
    "Atomic rejection: R11-01 empty idle cell rejected",
    "R11-01 empty used walk cell rejected",
    "Atomic rejection: R11-01 empty used walk cell rejected",
    "R11-02 identical used cells repacked to two columns rejected",
    "Atomic rejection: R11-02 identical used cells repacked to two columns rejected",
    "R11-02 unused padding cannot disguise duplicate used sequence",
    "Atomic rejection: R11-02 unused padding cannot disguise duplicate used sequence",
    "R11-03 derived cycle distance overflow rejected",
    "Atomic rejection: R11-03 derived cycle distance overflow rejected",
    "R11-04 moved warning/burst is interrupted",
    "R11-04 moved warning/burst is interrupted",
    "R11-04 no continuation fire from unannounced corrected origin",
    "R11-04 moved warning/burst is interrupted",
    "R11-04 moved warning/burst is interrupted",
    "R11-04 no continuation fire from unannounced corrected origin",
    "R11-04 moved warning/burst is interrupted",
    "R11-04 moved warning/burst is interrupted",
    "R11-04 no continuation fire from unannounced corrected origin"
  ],
  "production_registry_changed": false,
  "sha256": {
    "scripts/actors/enemy_actor.gd": "f9c8000073867c15d7c8337249ca2c98ba29d80c950aa60ce5a2910b4b2ccaa0",
    "scripts/animation/site7_biped_sprite.gd": "6e0ed61e1eaa97d99bf3d4155002deb5d6252f64e8fb9c43222fcd94a13ad929",
    "scripts/combat/site7_enemy_tactics.gd": "efacd6facda231852c947cb26572cc873ed022d62bb5ddf1ef55b2c8b260bd02",
    "scripts/ui/enemy_overhead_ui.gd": "b46c788c0b07945790653bbafe0656fe1fa99361f5806de4438cff1f06367b22",
    "tests/smoke/site7_biped_bridge_smoke.gd": "329e49f371bb97387eabd8ff59b398c67222e48403050a58ac2f6b590c5545b9"
  },
  "status": "FAIL",
  "synthetic_fixtures_only": true,
  "visual_approval": false
}
```

## FILE: qa/stage1_implementation_20260913/biped_bridge_1789298299_626/report.json
SHA256: 1eaba7b7b23e482ad963d6f779d11dc65159522984423fca408e48a270a7ffca
```text
{
  "checks": 876,
  "failures": [],
  "production_registry_changed": false,
  "sha256": {
    "scripts/actors/enemy_actor.gd": "807cf7b7f27cd4cec22fa63cfbdbcdaae2c49e815aaa6dda5409910975085b1a",
    "scripts/animation/site7_biped_sprite.gd": "f654151fe478c7c6b90a0b0d3b31329e98017ef0665a360d1a22e63a313729e2",
    "scripts/combat/site7_enemy_tactics.gd": "efacd6facda231852c947cb26572cc873ed022d62bb5ddf1ef55b2c8b260bd02",
    "scripts/ui/enemy_overhead_ui.gd": "b46c788c0b07945790653bbafe0656fe1fa99361f5806de4438cff1f06367b22",
    "tests/smoke/site7_biped_bridge_smoke.gd": "94c8db7af701911bb6f8fa5a16ac5526858e9946e1714b3679239595931b8c6b"
  },
  "status": "PASS",
  "synthetic_fixtures_only": true,
  "visual_approval": false
}
```

## FILE: qa/stage1_implementation_20260913/r11_counterexamples_before_fix.log
SHA256: e1ceeb64af71c66cc48084b8448dc9487e9bb01ed908fc1bbeeb1ad59bbcb3e1
```text
Godot Engine v4.7.1.stable.official.a13da4feb - https://godotengine.org

ERROR: R11-01 empty idle cell rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:65)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:88)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: Atomic rejection: R11-01 empty idle cell rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:66)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:88)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: R11-01 empty used walk cell rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:65)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:93)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: Atomic rejection: R11-01 empty used walk cell rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:66)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:93)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: R11-02 identical used cells repacked to two columns rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:65)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:96)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: Atomic rejection: R11-02 identical used cells repacked to two columns rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:66)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:96)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: R11-02 unused padding cannot disguise duplicate used sequence
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:65)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:102)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: Atomic rejection: R11-02 unused padding cannot disguise duplicate used sequence
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:66)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:102)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: R11-03 derived cycle distance overflow rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:65)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:104)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: Atomic rejection: R11-03 derived cycle distance overflow rejected
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] refuses (res://tests/smoke/site7_biped_bridge_smoke.gd:66)
       [2] review_input_counterexamples (res://tests/smoke/site7_biped_bridge_smoke.gd:104)
       [3] run (res://tests/smoke/site7_biped_bridge_smoke.gd:118)
ERROR: R11-04 moved warning/burst is interrupted
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:234)
ERROR: R11-04 moved warning/burst is interrupted
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:234)
ERROR: R11-04 no continuation fire from unannounced corrected origin
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:237)
ERROR: R11-04 moved warning/burst is interrupted
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:234)
ERROR: R11-04 moved warning/burst is interrupted
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:234)
ERROR: R11-04 no continuation fire from unannounced corrected origin
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:237)
ERROR: R11-04 moved warning/burst is interrupted
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:234)
ERROR: R11-04 moved warning/burst is interrupted
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:234)
ERROR: R11-04 no continuation fire from unannounced corrected origin
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] check (res://tests/smoke/site7_biped_bridge_smoke.gd:23)
       [1] run (res://tests/smoke/site7_biped_bridge_smoke.gd:237)
M7_RASTER_QUARANTINED identity=aster status=partial chunks=2 encoded=20000 present=15000 declared=94718
SITE7_BIPED_BRIDGE: FAIL (871) res://qa/stage1_implementation_20260913/biped_bridge_1789298056_896

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_biped_bridge_smoke.stdout.log
SHA256: 4c04efde137623af1d92e80b0ab8dae83a20485da23e538833336cc394861917
```text
Godot Engine v4.7.1.stable.official.a13da4feb - https://godotengine.org

M7_RASTER_QUARANTINED identity=aster status=partial chunks=2 encoded=20000 present=15000 declared=94718
SITE7_BIPED_BRIDGE: PASS (876) res://qa/stage1_implementation_20260913/biped_bridge_1789298299_626

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_biped_bridge_smoke.stderr.log
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```text

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_drone_app_smoke.stdout.log
SHA256: 273116a4776b7721e02d20bd4527ad22b92f7d8f082c40fb5e073f289da1fa23
```text
Godot Engine v4.7.1.stable.official.a13da4feb - https://godotengine.org

SITE7_DRONE_APP_SMOKE: PASS (170 checks) res://qa/stage1_implementation_20260913/drone_app_1789298300_972.json

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_drone_app_smoke.stderr.log
SHA256: db1254922e97cb0aede88f91133328831fcfa3cd4d69a6a246a6559ecfe195c6
```text
WARNING: 48 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_anchor_app_smoke.stdout.log
SHA256: 6ef6fcc641a08d5c93519f8ff1a5d08f753e24f97d5933172af1ed9f9a80cff0
```text
Godot Engine v4.7.1.stable.official.a13da4feb - https://godotengine.org

SITE7_ANCHOR_APP_SMOKE: PASS (271 checks) res://qa/stage1_implementation_20260913/anchor_app_1789298300_938.json

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_anchor_app_smoke.stderr.log
SHA256: 70f560f7b8c72f5f865ba4980bfd2ae315017ece1c6e37f2c2e28d73b6983a3d
```text
WARNING: 78 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_machine_source_smoke.stdout.log
SHA256: 8a0a74ea4da07909b8a2506030befe88dee41da14a1d2d00c4275ea9ac6c8d50
```text
Godot Engine v4.7.1.stable.official.a13da4feb - https://godotengine.org

SITE7_MACHINE_SOURCE_SMOKE: PASS (436 checks)

```

## FILE: qa/stage1_implementation_20260913/r11_final_site7_machine_source_smoke.stderr.log
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```text

```

## FILE: qa/stage1_implementation_20260913/r11_final_motion_lab_character_runtime_smoke.stdout.log
SHA256: f88b138244daeadc348bd214e109f15ce2c00f93ac1d7b30fadbd60bf2497806
```text
Godot Engine v4.7.1.stable.official.a13da4feb - https://godotengine.org

M7_RASTER_QUARANTINED identity=aster status=partial chunks=2 encoded=20000 present=15000 declared=94718
PASS: ASTER exists in the real StoryStage squad
PASS: ASTER owns the shared Motion Studio runtime bridge
MOTION_LAB_RUNTIME_CONTRACT ASTER: { "active": true, "status": "active", "character_id": "aster", "profile_path": "res://motion_lab_v1/public/assets/atlas/aster/profile.json", "directions": 8, "display_height_px": 129.6, "display_scale": 0.19756097560976, "ground_anchor_local": (0.0, 0.0), "action": "idle", "sector": 5, "direction": "NW", "frame": 0, "phase": 0.0, "walk_cycle_distance": 160.0, "run_cycle_distance": 195.0, "muzzle_global": (354.8386, 263.3866), "whole_body_fire_policy": "shared_walk_or_idle_frame", "map_scale_policy": "129_6px_authored_subject_height_user_enlarged_20260911" }
PASS: ASTER current Motion Studio package activates
PASS: ASTER reads its exact current package profile
PASS: ASTER profile resolves inside the project Motion Studio package
PASS: ASTER loads every authored direction
PASS: ASTER uses the user-requested 129.6px map-operator height
PASS: ASTER source root is grounded on the actor map position
PASS: ASTER displays authored Motion Studio raster pixels
PASS: ASTER suppresses the old vector body without changing gameplay sockets
PASS: ASTER has no competing legacy fast-raster body
PASS: ASTER Motion Studio body suppresses the retired V4 preview
PASS: ASTER direction E selects its matching authored atlas
PASS: ASTER direction E keeps a drawable atlas
PASS: ASTER direction SE selects its matching authored atlas
PASS: ASTER direction SE keeps a drawable atlas
PASS: ASTER direction S selects its matching authored atlas
PASS: ASTER direction S keeps a drawable atlas
PASS: ASTER direction SW selects its matching authored atlas
PASS: ASTER direction SW keeps a drawable atlas
PASS: ASTER direction W selects its matching authored atlas
PASS: ASTER direction W keeps a drawable atlas
PASS: ASTER direction NW selects its matching authored atlas
PASS: ASTER direction NW keeps a drawable atlas
PASS: ASTER direction N selects its matching authored atlas
PASS: ASTER direction N keeps a drawable atlas
PASS: ASTER direction NE selects its matching authored atlas
PASS: ASTER direction NE keeps a drawable atlas
PASS: ASTER advances across the actual map while walking
PASS: ASTER distance-driven walk visits all six approved gait frames
PASS: ASTER projectile source follows the visible authored muzzle
PASS: ASTER accepts a gameplay fire request
PASS: ASTER spawned projectile uses the same current whole-body frame muzzle
PASS: ROOK exists in the real StoryStage squad
PASS: ROOK owns the shared Motion Studio runtime bridge
MOTION_LAB_RUNTIME_CONTRACT ROOK: { "active": true, "status": "active", "character_id": "rook", "profile_path": "res://motion_lab_v1/public/assets/atlas/rook/profile.json", "directions": 8, "display_height_px": 129.6, "display_scale": 0.19756097560976, "ground_anchor_local": (0.0, 0.0), "action": "walk", "sector": 0, "direction": "E", "frame": 0, "phase": 0.11456640167162, "walk_cycle_distance": 160.0, "run_cycle_distance": 195.0, "muzzle_global": (522.2426, 353.1837), "whole_body_fire_policy": "shared_walk_or_idle_frame", "map_scale_policy": "129_6px_authored_subject_height_user_enlarged_20260911" }
PASS: ROOK current Motion Studio package activates
PASS: ROOK reads its exact current package profile
PASS: ROOK profile resolves inside the project Motion Studio package
PASS: ROOK loads every authored direction
PASS: ROOK uses the user-requested 129.6px map-operator height
PASS: ROOK source root is grounded on the actor map position
PASS: ROOK displays authored Motion Studio raster pixels
PASS: ROOK suppresses the old vector body without changing gameplay sockets
PASS: ROOK has no competing legacy fast-raster body
PASS: ROOK direction E selects its matching authored atlas
PASS: ROOK direction E keeps a drawable atlas
PASS: ROOK direction SE selects its matching authored atlas
PASS: ROOK direction SE keeps a drawable atlas
PASS: ROOK direction S selects its matching authored atlas
PASS: ROOK direction S keeps a drawable atlas
PASS: ROOK direction SW selects its matching authored atlas
PASS: ROOK direction SW keeps a drawable atlas
PASS: ROOK direction W selects its matching authored atlas
PASS: ROOK direction W keeps a drawable atlas
PASS: ROOK direction NW selects its matching authored atlas
PASS: ROOK direction NW keeps a drawable atlas
PASS: ROOK direction N selects its matching authored atlas
PASS: ROOK direction N keeps a drawable atlas
PASS: ROOK direction NE selects its matching authored atlas
PASS: ROOK direction NE keeps a drawable atlas
PASS: ROOK advances across the actual map while walking
PASS: ROOK distance-driven walk visits all six approved gait frames
PASS: ROOK projectile source follows the visible authored muzzle
PASS: ROOK accepts a gameplay fire request
PASS: ROOK spawned projectile uses the same current whole-body frame muzzle
PASS: MICA exists in the real StoryStage squad
PASS: MICA owns the shared Motion Studio runtime bridge
MOTION_LAB_RUNTIME_CONTRACT MICA: { "active": true, "status": "active", "character_id": "mica", "profile_path": "res://motion_lab_v1/public/assets/atlas/mica/profile.json", "directions": 8, "display_height_px": 129.6, "display_scale": 0.19756097560976, "ground_anchor_local": (0.0, 0.0), "action": "walk", "sector": 0, "direction": "E", "frame": 2, "phase": 0.43998165726662, "walk_cycle_distance": 160.0, "run_cycle_distance": 195.0, "muzzle_global": (528.5323, 347.2043), "whole_body_fire_policy": "shared_walk_or_idle_frame", "map_scale_policy": "129_6px_authored_subject_height_user_enlarged_20260911" }
PASS: MICA current Motion Studio package activates
PASS: MICA reads its exact current package profile
PASS: MICA profile resolves inside the project Motion Studio package
PASS: MICA loads every authored direction
PASS: MICA uses the user-requested 129.6px map-operator height
PASS: MICA source root is grounded on the actor map position
PASS: MICA displays authored Motion Studio raster pixels
PASS: MICA suppresses the old vector body without changing gameplay sockets
PASS: MICA has no competing legacy fast-raster body
PASS: MICA direction E selects its matching authored atlas
PASS: MICA direction E keeps a drawable atlas
PASS: MICA direction SE selects its matching authored atlas
PASS: MICA direction SE keeps a drawable atlas
PASS: MICA direction S selects its matching authored atlas
PASS: MICA direction S keeps a drawable atlas
PASS: MICA direction SW selects its matching authored atlas
PASS: MICA direction SW keeps a drawable atlas
PASS: MICA direction W selects its matching authored atlas
PASS: MICA direction W keeps a drawable atlas
PASS: MICA direction NW selects its matching authored atlas
PASS: MICA direction NW keeps a drawable atlas
PASS: MICA direction N selects its matching authored atlas
PASS: MICA direction N keeps a drawable atlas
PASS: MICA direction NE selects its matching authored atlas
PASS: MICA direction NE keeps a drawable atlas
PASS: MICA advances across the actual map while walking
PASS: MICA distance-driven walk visits all six approved gait frames
PASS: MICA projectile source follows the visible authored muzzle
PASS: MICA accepts a gameplay fire request
PASS: MICA spawned projectile uses the same current whole-body frame muzzle
MOTION_LAB_CHARACTER_RUNTIME_SMOKE: PASS

```

## FILE: qa/stage1_implementation_20260913/r11_final_motion_lab_character_runtime_smoke.stderr.log
SHA256: 23f60e542ff9a09a2b8f942ac0d8006dec22bbf92f6fdcfa1562f5d46b28f1fe
```text
WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)

```

## FILE: qa/stage1_implementation_20260913/r11_final_rook_motion_lab_app_smoke.stdout.log
SHA256: a3959a8b2a40c5682cc39ec03afed12eb9d41f328a56decb417dc9ee91f3ef85
```text
Godot Engine v4.7.1.stable.official.a13da4feb - https://godotengine.org

ROOK_MOTION_LAB_APP_SMOKE: PASS (1895 checks, 0 failures)

```

## FILE: qa/stage1_implementation_20260913/r11_final_rook_motion_lab_app_smoke.stderr.log
SHA256: a31bcd1ff28fe698684c06cfd9ee71deebe3a89e8555463587f46274a66f24d5
```text
WARNING: 68 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)

```
