# Narrow SITE-7 NPC facing / reusable skill review

Round5's two named residual counterexamples are closed in the tested scope. Do not
restart that closure audit. The actual reply is retained separately. Continue with
the user-requested concrete NPC-facing correction below while local art work runs.

The user supplied a real game capture: a drone on the right faced down-right while
shooting left toward the squad. Root cause: one front-three-quarter image was used
for all AI aim directions. A spherical omni emitter did NOT solve body facing.
The current candidate now contains eight individually generated1536x1024 yaw
masters and per-view muzzle/root points. A first rear image with four thrusters
and a southwest image with reversed sensor order were rejected/repaired, retained.
The actual game recapture now shows the drone facing left and its left-side magenta
orb toward the squad. This does not prove every angle is artistically perfect.

Code changes: complete8-view intake before publication; no mirrored or2D-rotated
single-image fallback; select visual yaw and its own actual emitter ray together;
initial frame follows actor aim; no new visual target resolution during announced
WINDUP/BURST/LUNGE; recovery can retarget. Candidate yaw evaluation commits only the
selected texture, not8texture changes per tick. The anchored boss remains stationary.
Legacy mock weapons were rotating to world aim THEN being horizontally flipped;
weapon/arm pixels now remain unflipped. Humanoid mock bodies are still temporary.

Actual local Godot4.7.1 tests: enemy_facing_smoke240checks PASS, machine_source_smoke
388checks PASS. They exercise30/60/120Hz,8directions, real emitted object ids, locked
warning/body state, opposite movement/target changes, rejected missing/duplicate
views, actual mock gun transforms and transformed hit bounds. Native real-game
captures are1920x1080. Tests are not visual approval and images are not attached here.
No player source, gait, size, weapon interval or remote deployment changed. New art
is currently QA-candidate only, not an automatically approved app registry update.

Review the actual attached changed code/skill for concrete bugs in target-facing,
one-shot/telegraph ownership and false eight-view acceptance. Provide minimal
reproduction + narrowly scoped fix for confirmed defects; distinguish unverifiable
painted direction/art issues. Do not claim to run Godot or inspect unseen images.
This is not permission to author new art, run Luna, or approve the whole MVP.

## FILE: scripts/animation/site7_machine_sprite.gd
SHA256: e0bf313b9e2d5eb81b75b5cbf805ec7904924bbe0308e3802121b4f4af7570b8

```text
extends Node2D
## Source-preserving preview/runtime for non-walking machines only.
## A drone banks as one rigid object; an anchor stays anchored. Neither is a
## humanoid gait and neither may use a six-frame foot-cycle approval as proof.

var actor: EnemyActor
var sprite: Sprite2D
var kind := ""
var emitter_px := Vector2.ZERO
var image_size := Vector2.ZERO
var age := 0.0
var flash := 0.0
var render_scale := 1.0
var body_origin := Vector2.ZERO
var configured := false
const DIRECTIONS := ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
var views: Dictionary = {}
var facing := ""
var emitter_visible := true

func _read_view(spec: Dictionary) -> Dictionary:
    var path := str(spec.get("texture", ""))
    if FileAccess.get_sha256(path) != str(spec.get("texture_sha256", "")): return {}
    var image := Image.load_from_file(path)
    if image == null or image.is_empty(): return {}
    var root_xy: Array = spec.get("root_px", [])
    var emitter_xy: Array = spec.get("emitter_px", [])
    if root_xy.size() != 2 or emitter_xy.size() != 2: return {}
    var size := Vector2(image.get_size())
    var origin := Vector2(float(root_xy[0]),float(root_xy[1]))
    var emitter := Vector2(float(emitter_xy[0]),float(emitter_xy[1]))
    var ratio := float(spec.get("display_height",110.0)) / size.y
    if not origin.is_finite() or not emitter.is_finite() or not is_finite(ratio): return {}
    if ratio <= 0.0 or ratio > 1.0 or not Rect2(Vector2.ZERO,size).has_point(emitter): return {}
    return {"texture":ImageTexture.create_from_image(image),"size":size,"root":origin,
        "emitter":emitter,"scale":ratio,"emitter_visible":bool(spec.get("emitter_visible",true)),
        "texture_sha256":str(spec.texture_sha256)}

func configure(owner_actor: EnemyActor, spec: Dictionary) -> bool:
    actor = owner_actor
    kind = str(spec.get("kind", ""))
    if kind not in ["hover_machine", "anchored_machine"]:
        push_error("Machine sprite cannot substitute for a walking enemy")
        return false
    # Load the complete set before publishing any node/state. A single front
    # illustration is NOT an omnidirectional drone, even with an omni emitter.
    var staged: Dictionary = {}
    if kind == "hover_machine":
        if str(spec.get("facing_mode","")) != "authored_yaw8": return false
        var authored: Dictionary = spec.get("views",{})
        if authored.size() != 8: return false
        var hashes: Array[String] = []
        for direction in DIRECTIONS:
            if not authored.has(direction): return false
            var view := _read_view(authored[direction])
            if view.is_empty() or hashes.has(view.texture_sha256): return false
            hashes.append(view.texture_sha256)
            staged[direction] = view
    else:
        var fixed := _read_view(spec)
        if fixed.is_empty(): return false
        staged["ANCHORED"] = fixed
    sprite = Sprite2D.new()
    sprite.name = "AuthoredMachinePixels"
    sprite.set_meta("preserve_authored_material", true)
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.centered = false
    add_child(sprite)
    views = staged
    _apply_view("E" if kind == "hover_machine" else "ANCHORED")
    configured = true
    face_direction(actor._aim_dir)
    return true

func _apply_view(direction: String) -> void:
    if facing == direction: return
    var view: Dictionary = views[direction]
    facing = direction
    image_size = view.size
    emitter_px = view.emitter
    emitter_visible = view.emitter_visible
    render_scale = float(view.scale)
    sprite.texture = view.texture
    sprite.scale = Vector2.ONE * render_scale
    body_origin = -view.root * render_scale
    sprite.position = body_origin

func face_direction(direction: Vector2) -> void:
    if not configured or kind != "hover_machine" or direction.length_squared() < 0.000001: return
    var local_dir := actor.global_transform.affine_inverse().basis_xform(direction)
    var sector := int(floor(fposmod(local_dir.angle()+PI/8.0,TAU)/(PI/4.0)))%8
    _apply_view(DIRECTIONS[sector])

func visible_heading_world() -> Vector2:
    if kind != "hover_machine": return Vector2.ZERO
    var index := DIRECTIONS.find(facing)
    return global_transform.basis_xform(Vector2.from_angle(index*PI/4.0)).normalized()

func resolve_target(target: Vector2) -> Vector2:
    if not configured: return Vector2.LEFT
    if kind != "hover_machine": return (target-muzzle_world()).normalized()
    # Each authored yaw has a different physical emitter offset. Evaluate its
    # own ray, then keep the pose whose front actually agrees with that ray.
    # No interpolation, horizontal mirroring, or whole-bitmap screen rotation.
    var best := facing
    var error := INF
    sync_pose()
    for i in range(DIRECTIONS.size()):
        var direction: String = DIRECTIONS[i]
        var view: Dictionary = views[direction]
        var local_emitter: Vector2 = (view.emitter-view.root)*float(view.scale)
        var ray := (target-to_global(local_emitter)).normalized()
        var heading := global_transform.basis_xform(Vector2.from_angle(i*PI/4.0)).normalized()
        var candidate_error := absf(heading.angle_to(ray))
        if candidate_error < error:
            best = direction
            error = candidate_error
    _apply_view(best)
    return (target-muzzle_world()).normalized()

func _process(delta: float) -> void:
    if not configured: return
    age += delta
    flash = move_toward(flash, 0.0, delta * 7.0)
    sync_pose()
    queue_redraw()

func sync_pose() -> void:
    if not configured: return
    # Use bounded rigid-body motion only. No image stretching or cut-up limbs.
    if kind == "hover_machine":
        rotation = clampf(actor.velocity.x / 118.0, -1.0, 1.0) * 0.045
        position.y = sin(age * 2.8) * 3.0
        if actor.health <= 0.0:
            rotation += (0.55 - actor._death_left) * 1.2
            position.y += (0.55 - actor._death_left) * 65.0
    else:
        rotation = 0.0
        position = Vector2.ZERO
    sprite.modulate = Color.WHITE.lerp(Color(1.3,1.15,1.25),actor._hit_flash * 0.4)

func muzzle_world() -> Vector2:
    sync_pose()
    return sprite.to_global(emitter_px)

func fired() -> void:
    flash = 1.0
    queue_redraw()

func hit_rect_world() -> Rect2:
    var shape := Rect2(image_size * Vector2(0.12,0.15), image_size * Vector2(0.76,0.70))
    var bounds := Rect2(sprite.to_global(shape.position),Vector2.ZERO)
    for corner in [shape.position + Vector2(shape.size.x,0), shape.end, shape.position + Vector2(0,shape.size.y)]:
        bounds = bounds.expand(sprite.to_global(corner))
    return bounds

func _draw() -> void:
    if not configured or actor.health <= 0.0: return
    var center := to_local(sprite.to_global(emitter_px))
    var charge := 0.0
    if actor.tactics and actor.tactics.state == "WINDUP":
        charge = clampf(1.0 - actor.tactics.state_left / actor.tactics.state_duration, 0.0, 1.0)
    var radius := 8.0 if kind == "hover_machine" else 26.0
    var power := maxf(flash, charge * 0.5)
    if power > 0.0 and emitter_visible:
        draw_circle(center, radius * (1.0 + power), Color(0.94,0.25,0.75,power * 0.22))
        draw_arc(center, radius * 1.4, -age, TAU-age, 32, Color(0.8,0.45,1.0,power * 0.75),1.5)

func debug_contract() -> Dictionary:
    return {"kind":kind,"configured":configured,"art_warp":false,
        "gait_claim":false,"emitter_px":emitter_px,"emitter_world":muzzle_world(),
        "native_size":image_size,"display_height":image_size.y * render_scale,
        "facing":facing,"view_count":views.size(),"heading_world":visible_heading_world(),
        "emitter_visible":emitter_visible,"texture_sha256":views[facing].texture_sha256,
        "mirrored":false}

```

## FILE: scripts/actors/enemy_actor.gd
SHA256: 48995193548f418fcd2ee5693ecd92f04a844265354f308eac7e3ef1fa189f6a

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

func _ready() -> void:
    add_to_group("prototype_targets")
    add_to_group("m3_enemies")
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    health = max_health
    home_position = global_position
    _orbit_sign = -1.0 if abs(enemy_id.hash()) % 2 == 0 else 1.0
    _build_high_res_visual()
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
    move_and_slide()
    var stage := get_parent()
    if stage and stage.has_method("constrain_battle_position"):
        global_position = stage.call("constrain_battle_position", global_position)
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
    if is_instance_valid(machine_sprite): return machine_sprite.muzzle_world()
    return get_combat_aim_point() + dir * _muzzle_distance()

func aim_from_emitter(target_point: Vector2) -> Vector2:
    if is_instance_valid(machine_sprite): return machine_sprite.resolve_target(target_point)
    # Legacy muzzle offsets are collinear with aim and need no iterative solve.
    var origin: Vector2 = get_combat_aim_point()
    return (target_point-origin).normalized()

func preview_machine_source(spec: Dictionary) -> bool:
    # Explicit candidate intake for the owned native QA scene. No registry or
    # production pointer is written. Promotion is a separate reviewed change.
    if is_instance_valid(machine_sprite): return false
    var candidate := preload("res://scripts/animation/site7_machine_sprite.gd").new()
    candidate.name = "AuthoredMachine"
    add_child(candidate)
    if not candidate.configure(self,spec):
        candidate.queue_free()
        return false
    machine_sprite = candidate
    _visual_root.visible = false
    return true

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
    if is_instance_valid(_visual_root):
        _visual_root.queue_free()
    _bones.clear(); _parts.clear(); _base_positions.clear(); _rig_texture = null
    _build_high_res_visual()

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

## FILE: scripts/combat/site7_enemy_tactics.gd
SHA256: b658ce84f30ebe9784d5cc1f3a7f2896f9151d54be232441aa8950f12021045b

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
            actor.velocity = Vector2.ZERO
            # Stop/bank first, then freeze the actual emitter ray. Never home
            # a telegraphed shot onto the player's later position.
            locked_aim = actor.aim_from_emitter(target.get_combat_aim_point())
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

func _fire(direction: Vector2) -> void:
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

## FILE: scripts/animation/premium_enemy_presentation.gd
SHA256: 6e857ca973cedfdadfbb7d3d375fe25f7afe37232df9c0251a5bfe2fdfd51528

```text
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
        # The mock's gun/arms are already rotated to the world aim by their
        # bones. Mirroring those local +X pixels reverses the visible barrel
        # AGAIN while the emitted projectile keeps the original direction.
        if name in ["Rifle", "RamPistol", "ArmL", "ArmR", "HydraulicArm"]:
            sprite.flip_h = false
        elif "DRONE" not in actor.enemy_id and "BOSS" not in actor.enemy_id:
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
        # This torso has no animated base rotation. Accumulating the kick
        # every rendered frame turned a living enemy upside down after hits.
        torso.rotation = -k * 0.24
        torso.scale = Vector2(1.0 - k * 0.09, 1.0 + k * 0.14)
        if bones.has("skull"): (bones["skull"] as Bone2D).rotation += k * 0.31
        if bones.has("tail"): (bones["tail"] as Bone2D).rotation -= k * 0.48
    elif ("BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id) and bones.has("iris"):
        (bones["iris"] as Bone2D).scale = Vector2.ONE * (1.0 + k * 0.18)
        for i in range(1,5):
            var key := "arm_%d" % i
            if bones.has(key): (bones[key] as Bone2D).rotation += k * (0.065 + i * 0.014) * (-1.0 if i % 2 == 0 else 1.0)

func _update_boss_phase(delta: float) -> void:
    var ratio := actor.health / maxf(1.0, actor.max_health)
    var new_phase := 1 if ratio > 0.66 else (2 if ratio > 0.33 else 3)
    if new_phase != _phase_index:
        _phase_index = new_phase
        _boss_pattern_cd = 0.78 if _phase_index == 2 else (0.52 if _phase_index == 3 else 2.8)
    var bones: Dictionary = actor.get("_bones")
    if not bones.has("ring"):
        return
    var ring := bones["ring"] as Bone2D
    var iris := bones["iris"] as Bone2D if bones.has("iris") else null
    if _phase_index == 1:
        ring.scale = Vector2.ONE
    elif _phase_index == 2:
        ring.scale = Vector2.ONE * (1.025 + sin(Time.get_ticks_msec() * 0.004) * 0.014)
        if iris: iris.rotation -= 0.014
        for i in range(1,5):
            var p := bones.get("pylon_%d"%i) as Bone2D
            if p: p.rotation += (0.040 if i % 2 == 0 else -0.040)
    elif _phase_index == 3:
        # M7: phase-3 motion remains unstable but does not scale-pump the whole boss.
        ring.scale = Vector2.ONE * (1.045 + sin(Time.get_ticks_msec() * 0.006) * 0.018)
        if iris:
            iris.scale = Vector2.ONE * (1.065 + sin(Time.get_ticks_msec() * 0.009) * 0.055)
            iris.rotation -= 0.026
        for i in range(1,5):
            var arm := bones.get("arm_%d"%i) as Bone2D
            if arm: arm.rotation += sin(Time.get_ticks_msec() * 0.005 + i) * 0.072

    _boss_pattern_cd -= delta
    if _boss_pattern_cd <= 0.0:
        _fire_phase_pattern()
        _boss_pattern_cd = 2.60 if _phase_index == 2 else (1.72 if _phase_index == 3 else 3.0)

func _fire_phase_pattern() -> void:
    # The live tactics controller owns warning, timing and damage. Keeping the
    # former presentation timer alive would add a second, untelegraphed volley.
    if actor.tactics != null:
        return
    if _phase_index <= 1:
        return
    var aim: Vector2 = actor.get("_aim_dir")
    CombatFeedback.play_fire(actor.get_tree(), actor.art_profile)
    if _phase_index == 2:
        for a in [-0.34, 0.0, 0.34]:
            actor.call("_spawn_projectile", aim.rotated(a))
    else:
        # Five clear lanes aligned with the arena wedges. Wider spacing replaces
        # the old dense fan so each projectile remains readable at 1280x720.
        for a in [-0.72, -0.36, 0.0, 0.36, 0.72]:
            actor.call("_spawn_projectile", aim.rotated(a))

func _on_defeated(_enemy: EnemyActor) -> void:
    if actor == null:
        return
    # Never resurrect old SVG body fragments over the newly authored raster.
    if is_instance_valid(actor.machine_sprite): return
    var seq := EnemyDeathSequence.new()
    actor.get_tree().root.add_child(seq)
    seq.setup(actor.global_position, actor.enemy_id, actor.art_profile)

func _draw() -> void:
    if actor != null and is_instance_valid(actor.machine_sprite): return
    if actor != null and actor.health <= 0.0:
        return
    if actor == null or not ("BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id):
        return
    if _phase_index >= 2:
        var pulse := fposmod(Time.get_ticks_msec() * 0.00055, 1.0)
        var col := Color(0.55,0.38,1.0,(1.0-pulse)*0.12)
        if _phase_index == 3:
            col = Color(0.96,0.25,0.62,(1.0-pulse)*0.15)
        draw_arc(Vector2(0,-110), 58.0 + pulse * 34.0, 0.0, TAU, 48, col, 1.6 + float(_phase_index)*0.35)

func debug_phase() -> int:
    return _phase_index

func debug_sector() -> int:
    return _last_sector

func debug_phase_ring_clarity() -> bool:
    return true

func debug_m7_phase_contract() -> Dictionary:
    return {"phase2_burst":3,"phase3_burst":5,"phase3_spacing":0.36,"body_clear":true,"arena_separate":true}

```

## FILE: tests/smoke/site7_enemy_facing_smoke.gd
SHA256: f47f5613f0f3544b60afaf89cb0f89487128edef8c2c9b98d254be123fbf3166

```text
extends SceneTree
## Real node transforms and emitted shots, not an approval of painted yaw angles.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const PRESENTATION := preload("res://scripts/animation/premium_enemy_presentation.gd")
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
    var specs: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://motion_lab_v1/qa/stage1_enemies_20260913/machine_preview_specs.json"))
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_DRONE_01",620.0)
    root.add_child(actor); actor.set_physics_process(false)
    check(actor.preview_machine_source(specs[actor.enemy_id]),"Eight native views bind")
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
            actor.tactics.state="REPOSITION";actor.tactics.state_left=1.0
            actor.tactics.step(victim,1.0/hz)
            check(actor.machine_sprite.visible_heading_world().dot(ray)<-0.80,"Opposite target immediately selects opposite view")
    # Fail closed: a seven-view or duplicate-pixel set is not yaw8.
    for mutation in ["missing", "duplicate", "single"]:
        var bad: Dictionary = specs[actor.enemy_id].duplicate(true)
        if mutation=="missing": bad.views.erase("NW")
        elif mutation=="duplicate": bad.views["NW"]=bad.views["E"].duplicate(true)
        else: bad.erase("views")
        var stub := ENEMY.instantiate() as EnemyActor
        stub.configure("ENM_SITE7_DRONE_01",620.0);root.add_child(stub);stub.set_physics_process(false)
        check(not stub.preview_machine_source(bad),"Reject "+mutation+" facing set")
        check(stub.machine_sprite==null and stub._visual_root.visible,"Rejected intake leaves prior visual intact")
        stub.free()
    actor.free();victim.free()
    # Actual legacy mock barrels already rotate to aim; flipping again reverses them.
    for id in ["ENM_SITE7_RIFLE_01","ENM_SITE7_SHIELD_01"]:
        var mock := ENEMY.instantiate() as EnemyActor
        mock.configure(id,620.0);root.add_child(mock);mock.set_physics_process(false)
        var presentation := PRESENTATION.new();mock.add_child(presentation);presentation.set_process(false)
        var name := "Rifle" if "RIFLE" in id else "RamPistol"
        var gun: Sprite2D = mock._parts[name]
        for i in range(8):
            var dir := Vector2.from_angle(i*PI/4.0)
            mock._aim_dir=dir;mock._animate_identity();presentation._apply_directional_depth()
            var actual_front := gun.to_global(Vector2(100,0))-gun.to_global(Vector2.ZERO)
            if gun.flip_h: actual_front=-actual_front
            check(actual_front.normalized().dot(dir)>0.98,id+" visible barrel is not double-flipped")
        mock.free()
    # Let normal feedback nodes expire; do not leave pending sound/effect instances.
    for i in range(80): await process_frame
    print("SITE7_ENEMY_FACING_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)

```

## FILE: tests/smoke/site7_machine_source_smoke.gd
SHA256: 4e49eb4ad7e0defcdd7edc7606cb1805f9c7463d018ac5d65b952c4f571372d6

```text
extends SceneTree
## Source pixel/candidate binding and real projectile-origin tests, not visual PASS.
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
    var specs: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://motion_lab_v1/qa/stage1_enemies_20260913/machine_preview_specs.json"))
    for id in ["ENM_SITE7_DRONE_01","BOSS_SITE7_ANCHOR_01"]:
        var actor := ENEMY.instantiate() as EnemyActor
        actor.configure(id,620.0)
        root.add_child(actor)
        actor.set_physics_process(false)
        check(actor.preview_machine_source(specs[id]),id+" exact candidate binds")
        await process_frame
        await process_frame
        var sprite: Node2D = actor.machine_sprite
        check(is_instance_valid(sprite),id+" raster selected")
        if not is_instance_valid(sprite):continue
        check(not actor._visual_root.visible,id+" previous body hidden")
        check(sprite.sprite.material == null,id+" ImageGen authored materials unchanged")
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
                for point in [Vector2(0.13,0.16),Vector2(0.87,0.16),Vector2(0.87,0.84),Vector2(0.13,0.84)]:
                    check(bounds.has_point(sprite.sprite.to_global(sprite.image_size*point)),"Machine AABB covers transformed native region")
                check(sprite.muzzle_world().distance_to(expected)<0.001,id+" emitter follows visible source transform")
                if id.begins_with("BOSS"):
                    check(sprite.position == Vector2.ZERO and sprite.rotation == 0.0,"Anchor stays anchored")
                var previous := root.get_child_count()
                actor._spawn_projectile(dir)
                check(root.get_child_count() == previous + 1,"One emitter, one projectile")
                var projectile := root.get_child(root.get_child_count()-1) as PrototypeProjectile
                check(projectile.global_position.distance_to(expected)<0.001,"Projectile starts at actual authored iris/orb")
                projectile.free()
        actor.apply_damage(10000.0)
        check(get_nodes_in_group("enemy_death_sequences").is_empty(),"No old SVG death fragments")
        actor.free()
    print("SITE7_MACHINE_SOURCE_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)

```

## FILE: .agents/skills/sable-character-studio/references/enemy-facing.md
SHA256: 19905b39a20d825a7e4f467d0986da2c9cde3ec2849c7d7e9f86487dccdcc3a2

```text
# SITE-7 enemy facing: visible front, emitter and warning

Use for the current `site7_machine_sprite.gd` and enemy combat integration.
The 2026-09-13 user screenshot exposed a front-facing drone illustration being
reused while firing toward the opposite side. An omni **emitter** does not make
the whole vehicle's visible front omnidirectional. Do not repeat that shortcut.

- Flying drones use eight separately authored yaw views (`authored_yaw8`),
  exact texture hashes and per-view root/emitter coordinates. The runtime
  rejects missing views and repeated file hashes before publishing the node.
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
- At WINDUP entry, stop/bank first and freeze pose plus aim. WINDUP/BURST/LUNGE
  must not resolve a fresh target or home the advertised attack. Recovery may
  respond to the new target immediately. This is intentionally different from
  the player's latest-pointer-input behavior.
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

Run native 1920x1080 captures in the real game scene and inspect all affected
view transitions. A test PASS or source contact sheet is not runtime visual
approval. `prepare_drone_directions.py` only produces isolated candidates/specs;
the app registry must not point at an unreviewed QA candidate automatically.
Keep player art, gait, 1.8x display scale and weapon timing unchanged.

```

## FILE: motion_lab_v1/qa/stage1_enemies_20260913/machine_preview_specs.json
SHA256: 49ef9bd2b71887529b7007da31e1316954db553492f27a1d005e1077ffb4eb3a

```text
{
  "status": "CANDIDATE_RUNTIME_PREVIEW_NOT_PROMOTED",
  "ENM_SITE7_DRONE_01": {
    "kind": "hover_machine",
    "facing_mode": "authored_yaw8",
    "views": {
      "E": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_e/471d2e46c926_3203b573/candidate_rgba.png",
        "texture_sha256": "1b578c4ceab99cc27487f6e5c3fa91c85dbf393a9eef64cf740a6fb9c86fc93f",
        "display_height": 110,
        "root_px": [
          738.5,
          1084.0500000000002
        ],
        "emitter_px": [
          1210,
          635
        ],
        "emitter_visible": true
      },
      "SE": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_se/2eeab4a14906_3203b573/candidate_rgba.png",
        "texture_sha256": "3eafb4bf8536f048f5e51b1c89ef498b5d8f9cbd9396e1f948316d5abc4be0a7",
        "display_height": 110,
        "root_px": [
          745,
          1198.8000000000002
        ],
        "emitter_px": [
          870,
          790
        ],
        "emitter_visible": true
      },
      "S": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_s/92d3afd78ca8_3203b573/candidate_rgba.png",
        "texture_sha256": "1bd591cb950dfdf1a20b72c0af2e7ac68d78966cd01e535cf60bc6d31f567b27",
        "display_height": 110,
        "root_px": [
          677,
          1188
        ],
        "emitter_px": [
          679,
          789
        ],
        "emitter_visible": true
      },
      "SW": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_sw/f1f8959f94a7_3203b573/candidate_rgba.png",
        "texture_sha256": "cff84ee24f5a7c03ed6d56360c0a4d997da8a16da5860ecf3bf927a541b702b7",
        "display_height": 110,
        "root_px": [
          705.5,
          1237.95
        ],
        "emitter_px": [
          601,
          818
        ],
        "emitter_visible": true
      },
      "W": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_w/70faf301f14c_3203b573/candidate_rgba.png",
        "texture_sha256": "5d2a75ea9d2051bd29d0fe20d86d92ab0729cefee61371135a6f23097f62bfc0",
        "display_height": 110,
        "root_px": [
          728,
          1223.1000000000001
        ],
        "emitter_px": [
          108,
          644
        ],
        "emitter_visible": true
      },
      "NW": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_nw/8674418666cf_3203b573/candidate_rgba.png",
        "texture_sha256": "81a941bb695ab9a037dfdd16a5ff0f80fe3998fc51bd5e0776e644b7089125d9",
        "display_height": 110,
        "root_px": [
          713,
          1289.25
        ],
        "emitter_px": [
          170,
          337
        ],
        "emitter_visible": true
      },
      "N": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_n/6620d66f3cea_3203b573/candidate_rgba.png",
        "texture_sha256": "99760feeeded647bacb643dba1c04ecc9ded35616fcec535701b78e926cc97c6",
        "display_height": 110,
        "root_px": [
          741,
          1143.45
        ],
        "emitter_px": [
          740,
          598
        ],
        "emitter_visible": true
      },
      "NE": {
        "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw_ne/9c4c610537cb_3203b573/candidate_rgba.png",
        "texture_sha256": "9cef709e38e1e514f937f7b81ef902b7dc7400bd0662e5ea979f07ff4213def2",
        "display_height": 110,
        "root_px": [
          683.5,
          1294.65
        ],
        "emitter_px": [
          1176,
          527
        ],
        "emitter_visible": true
      }
    }
  },
  "BOSS_SITE7_ANCHOR_01": {
    "kind": "anchored_machine",
    "texture": "res://motion_lab_v1/qa/stage1_enemies_20260913/anchor/375bc85a7513_7c4594d6/candidate_rgba.png",
    "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
    "display_height": 270,
    "root_px": [613, 1235],
    "emitter_px": [638, 616]
  }
}

```
