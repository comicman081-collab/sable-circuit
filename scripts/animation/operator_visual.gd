extends Node2D
class_name OperatorVisual

var accent_color := Color("69d2ff")
var operator_label := "ALPHA"
var facing_sector := 0
var speed_norm := 0.0
var move_world := Vector2.ZERO
var aim_world := Vector2.RIGHT
var is_combat := true
var reload_progress := 0.0
var is_reloading := false

var _phase := 0.0
var _recoil := 0.0
var _evade_flash := 0.0
var _selected := false

var skeleton: Skeleton2D
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var muzzle_socket: Node2D

var _bones: Dictionary = {}
var _base_positions: Dictionary = {}
var _weapon_shape: Polygon2D

func _ready() -> void:
    _build_runtime_rig()
    queue_redraw()

func configure(label: String, color: Color) -> void:
    operator_label = label
    accent_color = color
    if is_node_ready():
        _apply_colors()
        queue_redraw()

func set_selected(value: bool) -> void:
    _selected = value
    queue_redraw()

func set_runtime_state(move_vec: Vector2, aim_vec: Vector2, normalized_speed: float, combat: bool, sector: int, reloading: bool, reload_t: float) -> void:
    move_world = move_vec
    if aim_vec.length_squared() > 0.0001:
        aim_world = aim_vec.normalized()
    speed_norm = clampf(normalized_speed, 0.0, 1.35)
    is_combat = combat
    facing_sector = sector
    is_reloading = reloading
    reload_progress = clampf(reload_t, 0.0, 1.0)

func trigger_fire() -> void:
    _recoil = 1.0

func trigger_evade() -> void:
    _evade_flash = 1.0

func get_muzzle_global_position() -> Vector2:
    if is_instance_valid(muzzle_socket):
        return muzzle_socket.global_position
    return global_position

func _process(delta: float) -> void:
    _phase += delta * lerpf(3.2, 10.0, clampf(speed_norm, 0.0, 1.0))
    _recoil = move_toward(_recoil, 0.0, delta * 8.0)
    _evade_flash = move_toward(_evade_flash, 0.0, delta * 5.0)
    _pose_rig()
    queue_redraw()

func _build_runtime_rig() -> void:
    skeleton = Skeleton2D.new()
    skeleton.name = "Skeleton2D"
    add_child(skeleton)

    var pelvis := _bone(skeleton, "pelvis", Vector2(0, -28))
    var torso := _bone(pelvis, "torso", Vector2(0, -20))
    var head := _bone(torso, "head", Vector2(0, -21))

    var upper_l := _bone(torso, "upper_arm_L", Vector2(-12, -3))
    var lower_l := _bone(upper_l, "lower_arm_L", Vector2(15, 0))
    var upper_r := _bone(torso, "upper_arm_R", Vector2(12, -3))
    var lower_r := _bone(upper_r, "lower_arm_R", Vector2(15, 0))
    var weapon := _bone(torso, "weapon_root", Vector2(1, 0))

    var thigh_l := _bone(pelvis, "thigh_L", Vector2(-7, 5))
    var shin_l := _bone(thigh_l, "shin_L", Vector2(0, 18))
    var foot_l := _bone(shin_l, "foot_L", Vector2(0, 16))
    var thigh_r := _bone(pelvis, "thigh_R", Vector2(7, 5))
    var shin_r := _bone(thigh_r, "shin_R", Vector2(0, 18))
    var foot_r := _bone(shin_r, "foot_R", Vector2(0, 16))

    _rect_part(pelvis, "PelvisPart", Vector2(23, 15), Vector2(0, 3), accent_color.darkened(0.32))
    _rect_part(torso, "TorsoPart", Vector2(29, 29), Vector2(0, 1), accent_color.darkened(0.10))
    _circle_part(head, "HeadPart", 17.0, Vector2.ZERO, Color("f1d7c7"))
    _rect_part(head, "HairPart", Vector2(36, 13), Vector2(0, -7), accent_color.darkened(0.55))

    _limb_part(upper_l, "UpperArmLPart", 17.0, 7.0, accent_color.darkened(0.12))
    _limb_part(lower_l, "LowerArmLPart", 15.0, 6.0, Color("e8cdbd"))
    _limb_part(upper_r, "UpperArmRPart", 17.0, 7.0, accent_color.darkened(0.12))
    _limb_part(lower_r, "LowerArmRPart", 15.0, 6.0, Color("e8cdbd"))

    _vertical_limb_part(thigh_l, "ThighLPart", 20.0, 8.0, accent_color.darkened(0.35))
    _vertical_limb_part(shin_l, "ShinLPart", 18.0, 7.0, Color("4e5a66"))
    _vertical_limb_part(foot_l, "FootLPart", 12.0, 9.0, Color("202936"))
    _vertical_limb_part(thigh_r, "ThighRPart", 20.0, 8.0, accent_color.darkened(0.35))
    _vertical_limb_part(shin_r, "ShinRPart", 18.0, 7.0, Color("4e5a66"))
    _vertical_limb_part(foot_r, "FootRPart", 12.0, 9.0, Color("202936"))

    _weapon_shape = _rect_part(weapon, "WeaponPart", Vector2(44, 8), Vector2(22, 0), Color("28333d"))
    var weapon_glow := _rect_part(weapon, "WeaponGlow", Vector2(15, 3), Vector2(24, -1), accent_color)
    weapon_glow.z_index = 2

    muzzle_socket = Node2D.new()
    muzzle_socket.name = "muzzle_socket"
    muzzle_socket.position = Vector2(46, 0)
    weapon.add_child(muzzle_socket)

    var support_socket := Node2D.new()
    support_socket.name = "support_hand_socket"
    support_socket.position = Vector2(15, 0)
    weapon.add_child(support_socket)

    var fx_root := Node2D.new()
    fx_root.name = "fx_root"
    weapon.add_child(fx_root)

    animation_player = AnimationPlayer.new()
    animation_player.name = "AnimationPlayer"
    add_child(animation_player)
    var library := AnimationLibrary.new()
    for clip_name in ["IdleExplore", "Move", "FireSingle", "Reload"]:
        var anim := Animation.new()
        anim.length = 1.0
        anim.loop_mode = Animation.LOOP_LINEAR if clip_name in ["IdleExplore", "Move"] else Animation.LOOP_NONE
        library.add_animation(clip_name, anim)
    animation_player.add_animation_library("", library)

    animation_tree = AnimationTree.new()
    animation_tree.name = "AnimationTree"
    add_child(animation_tree)
    animation_tree.anim_player = NodePath("../AnimationPlayer")
    var root_anim := AnimationNodeAnimation.new()
    root_anim.animation = &"IdleExplore"
    animation_tree.tree_root = root_anim
    animation_tree.active = true

    for bone_name in _bones.keys():
        var bone: Bone2D = _bones[bone_name]
        bone.rest = bone.transform
        _base_positions[bone_name] = bone.position

    _apply_colors()

func _bone(parent: Node, bone_name: String, pos: Vector2) -> Bone2D:
    var bone := Bone2D.new()
    bone.name = bone_name
    bone.position = pos
    bone.set_autocalculate_length_and_angle(false)
    parent.add_child(bone)
    _bones[bone_name] = bone
    return bone

func _rect_part(parent: Node2D, part_name: String, size: Vector2, center: Vector2, color: Color) -> Polygon2D:
    var p := Polygon2D.new()
    p.name = part_name
    p.polygon = PackedVector2Array([
        center + Vector2(-size.x * 0.5, -size.y * 0.5),
        center + Vector2(size.x * 0.5, -size.y * 0.5),
        center + Vector2(size.x * 0.5, size.y * 0.5),
        center + Vector2(-size.x * 0.5, size.y * 0.5),
    ])
    p.color = color
    parent.add_child(p)
    return p

func _circle_part(parent: Node2D, part_name: String, radius: float, center: Vector2, color: Color) -> Polygon2D:
    var points := PackedVector2Array()
    for i in range(16):
        var a := TAU * float(i) / 16.0
        points.append(center + Vector2(cos(a), sin(a)) * radius)
    var p := Polygon2D.new()
    p.name = part_name
    p.polygon = points
    p.color = color
    parent.add_child(p)
    return p

func _limb_part(parent: Node2D, part_name: String, length: float, width: float, color: Color) -> Polygon2D:
    return _rect_part(parent, part_name, Vector2(length, width), Vector2(length * 0.5, 0), color)

func _vertical_limb_part(parent: Node2D, part_name: String, length: float, width: float, color: Color) -> Polygon2D:
    return _rect_part(parent, part_name, Vector2(width, length), Vector2(0, length * 0.5), color)

func _apply_colors() -> void:
    if not is_instance_valid(skeleton):
        return
    var torso_part := skeleton.get_node_or_null("pelvis/torso/TorsoPart") as Polygon2D
    var pelvis_part := skeleton.get_node_or_null("pelvis/PelvisPart") as Polygon2D
    var hair_part := skeleton.get_node_or_null("pelvis/torso/head/HairPart") as Polygon2D
    if torso_part: torso_part.color = accent_color.darkened(0.10)
    if pelvis_part: pelvis_part.color = accent_color.darkened(0.32)
    if hair_part: hair_part.color = accent_color.darkened(0.55)

func _pose_rig() -> void:
    if _bones.is_empty():
        return

    var pelvis: Bone2D = _bones["pelvis"]
    var torso: Bone2D = _bones["torso"]
    var head: Bone2D = _bones["head"]
    var thigh_l: Bone2D = _bones["thigh_L"]
    var thigh_r: Bone2D = _bones["thigh_R"]
    var shin_l: Bone2D = _bones["shin_L"]
    var shin_r: Bone2D = _bones["shin_R"]
    var upper_l: Bone2D = _bones["upper_arm_L"]
    var upper_r: Bone2D = _bones["upper_arm_R"]
    var lower_l: Bone2D = _bones["lower_arm_L"]
    var lower_r: Bone2D = _bones["lower_arm_R"]
    var weapon: Bone2D = _bones["weapon_root"]

    var gait := sin(_phase) * 0.50 * minf(speed_norm, 1.0)
    var bob := absf(sin(_phase)) * 2.8 * minf(speed_norm, 1.0)
    pelvis.position = (_base_positions["pelvis"] as Vector2) + Vector2(0, bob)
    torso.rotation = sin(_phase * 0.5) * 0.035 * minf(speed_norm, 1.0)
    head.rotation = -torso.rotation * 0.6 + sin(_phase * 0.5) * 0.018

    thigh_l.rotation = gait
    thigh_r.rotation = -gait
    shin_l.rotation = -gait * 0.62
    shin_r.rotation = gait * 0.62

    var aim_angle := aim_world.angle()
    var reload_fold := sin(reload_progress * PI) if is_reloading else 0.0
    var recoil_angle := _recoil * 0.08

    upper_r.rotation = aim_angle - 0.10 - recoil_angle - reload_fold * 0.55
    lower_r.rotation = 0.08 + recoil_angle * 0.5 + reload_fold * 0.75
    upper_l.rotation = aim_angle + 0.13 - recoil_angle * 0.7 + reload_fold * 0.30
    lower_l.rotation = -0.18 + reload_fold * 0.55
    weapon.rotation = aim_angle - recoil_angle + reload_fold * 0.55
    weapon.position = (_base_positions["weapon_root"] as Vector2) - aim_world * (_recoil * 4.0) + Vector2(0, reload_fold * 5.0)

    if _evade_flash > 0.0:
        skeleton.scale = Vector2(1.0 + _evade_flash * 0.14, 1.0 - _evade_flash * 0.08)
    else:
        skeleton.scale = Vector2.ONE

func _draw() -> void:
    var ring_color := accent_color if _selected else Color(0.25, 0.30, 0.36, 0.55)
    draw_arc(Vector2(0, 4), 24.0, 0.0, TAU, 32, ring_color, 2.5 if _selected else 1.0)
    if _selected:
        draw_arc(Vector2(0, 4), 29.0, -PI * 0.85, -PI * 0.15, 18, Color(accent_color, 0.65), 2.0)
    if _recoil > 0.15 and is_instance_valid(muzzle_socket):
        var local_muzzle := to_local(muzzle_socket.global_position)
        draw_line(local_muzzle, local_muzzle + aim_world * (18.0 + _recoil * 12.0), Color("fff0a8"), 4.0)
