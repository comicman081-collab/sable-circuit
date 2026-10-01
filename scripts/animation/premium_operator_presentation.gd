extends Node2D
class_name PremiumOperatorPresentation

var actor: OperatorActor
var visual: OperatorVisual
var face: FaceMicroRig
var _last_velocity := Vector2.ZERO
var _last_aim := Vector2.RIGHT
var _hair_angle := 0.0
var _hair_velocity := 0.0
var _accessory_angle := 0.0
var _accessory_velocity := 0.0
var _last_sector := -1

func _ready() -> void:
    process_priority = 80
    actor = get_parent() as OperatorActor
    if actor:
        actor.downed.connect(_on_actor_downed)
        visual = actor.get_node_or_null("VisualRoot") as OperatorVisual
    call_deferred("_bind_face")

func _on_actor_downed(_actor: OperatorActor) -> void:
    ImpactFeel.operator_downed(actor.get_tree())

func _bind_face() -> void:
    if visual == null:
        return
    var bones: Dictionary = visual.get("_bones")
    if not bones.has("head"):
        return
    var head := bones["head"] as Bone2D
    face = FaceMicroRig.new()
    face.name = "FaceMicroRig"
    face.position = Vector2(0, -1.5)
    face.z_index = 12
    head.add_child(face)
    face.configure(str(actor.art_profile.get("visual_profile", actor.display_name)))

func _process(delta: float) -> void:
    if actor == null or visual == null or not is_instance_valid(visual.skeleton):
        return
    var bones: Dictionary = visual.get("_bones")
    if bones.is_empty():
        return
    _apply_directional_depth(bones)
    _apply_secondary_springs(delta)
    if face:
        face.set_state(actor.facing_sector, actor.aim_world, minf(1.0, actor.velocity.length() / maxf(1.0, actor.run_speed)), float(visual.get("_hit_flash")), delta)
    _last_velocity = actor.velocity
    _last_aim = actor.aim_world
    _last_sector = actor.facing_sector

func _apply_directional_depth(bones: Dictionary) -> void:
    var sector := actor.facing_sector
    var is_left := sector in [3, 4, 5]
    var is_rear := sector in [5, 6, 7]
    var is_front := sector in [1, 2, 3]
    var side_strength := 1.0 if sector in [0, 4] else 0.55
    var back_tint := Color(0.78, 0.84, 0.90, 1.0) if is_rear else Color.WHITE

    var parts: Array[Node] = []
    _collect_sprites(visual.skeleton, parts)
    for node in parts:
        var sprite := node as Sprite2D
        if sprite == null:
            continue
        if sprite.name in ["HeadHR", "HairHR", "TorsoHR", "PelvisHR", "AccessoryHR"]:
            sprite.flip_h = is_left
        sprite.modulate = back_tint

    var torso := bones.get("torso") as Bone2D
    var head := bones.get("head") as Bone2D
    var weapon := bones.get("weapon_root") as Bone2D
    var ul := bones.get("upper_arm_L") as Bone2D
    var ur := bones.get("upper_arm_R") as Bone2D
    if torso and head:
        var base_positions: Dictionary = visual.get("_base_positions")
        var torso_base: Vector2 = base_positions.get("torso", torso.position)
        var head_base: Vector2 = base_positions.get("head", head.position)
        var identity := str(actor.art_profile.get("visual_profile", ""))
        var shoulder_depth := -1.8 if is_rear else (1.4 if is_front else 0.0)
        var head_shift := 1.8 * signf(actor.aim_world.x) * side_strength
        if "ROOK" in identity:
            shoulder_depth *= 1.35
            head_shift *= 0.65
        elif "MICA" in identity:
            shoulder_depth *= 0.72
            head_shift *= 1.15
        torso.position = torso_base + Vector2(0, shoulder_depth)
        head.position = head_base + Vector2(head_shift, shoulder_depth * 0.55)

    if weapon:
        weapon.z_index = -1 if is_rear else (7 if is_front else 4)
    if ul:
        ul.z_index = -2 if is_rear else 3
    if ur:
        ur.z_index = -1 if is_rear else 4

    var lateral_scale := 0.94 if sector in [0, 4] else (0.975 if sector in [1, 3, 5, 7] else 1.0)
    if visual.skeleton:
        var base_evade: Vector2 = visual.skeleton.scale
        visual.skeleton.scale = Vector2(absf(base_evade.x) * lateral_scale, base_evade.y)

func _apply_secondary_springs(delta: float) -> void:
    var hair := visual.find_child("HairHR", true, false) as Node2D
    var accessory := visual.find_child("AccessoryHR", true, false) as Node2D
    var accel := (actor.velocity - _last_velocity) / maxf(delta, 0.0001)
    var aim_turn := _last_aim.angle_to(actor.aim_world) / maxf(delta, 0.0001)
    var identity := str(actor.art_profile.get("visual_profile", ""))
    var hair_stiff := 28.0
    var hair_damp := 8.5
    var accessory_stiff := 18.0
    var accessory_damp := 6.5
    var accel_gain := 0.00034
    var turn_gain := 0.010
    if "ASTER" in identity:
        hair_stiff = 24.0; hair_damp = 7.0; accessory_stiff = 30.0; accessory_damp = 9.5; accel_gain = 0.00042; turn_gain = 0.014
    elif "ROOK" in identity:
        hair_stiff = 34.0; hair_damp = 10.5; accessory_stiff = 12.0; accessory_damp = 5.0; accel_gain = 0.00018; turn_gain = 0.006
    elif "MICA" in identity:
        hair_stiff = 17.0; hair_damp = 5.5; accessory_stiff = 10.5; accessory_damp = 4.3; accel_gain = 0.00030; turn_gain = 0.018

    var target_hair := clampf(-accel.x * accel_gain - aim_turn * turn_gain, -0.22, 0.22)
    var target_accessory := clampf(-accel.x * accel_gain * 1.45 - aim_turn * turn_gain * 1.7, -0.31, 0.31)
    _hair_velocity += (target_hair - _hair_angle) * hair_stiff * delta
    _hair_velocity *= exp(-hair_damp * delta)
    _hair_angle += _hair_velocity * delta
    _accessory_velocity += (target_accessory - _accessory_angle) * accessory_stiff * delta
    _accessory_velocity *= exp(-accessory_damp * delta)
    _accessory_angle += _accessory_velocity * delta
    if hair:
        hair.rotation += _hair_angle
    if accessory:
        accessory.rotation += _accessory_angle

func _collect_sprites(node: Node, out: Array[Node]) -> void:
    for child in node.get_children():
        if child is Sprite2D:
            out.append(child)
        _collect_sprites(child, out)

func debug_sector_contract(sector: int) -> Dictionary:
    return {
        "sector": sector,
        "rear": sector in [5, 6, 7],
        "front": sector in [1, 2, 3],
        "left": sector in [3, 4, 5]
    }

func debug_has_face_rig() -> bool:
    return face != null
