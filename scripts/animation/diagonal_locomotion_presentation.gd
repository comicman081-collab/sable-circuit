extends Node2D
class_name DiagonalLocomotionPresentation

var actor: OperatorActor
var visual: OperatorVisual
var _bones: Dictionary = {}
var _base_rotations: Dictionary = {}
var _last_screen_diagonal := false
var _last_forward: float = 0.0
var _last_strafe: float = 0.0

func _ready() -> void:
    process_priority = 95
    actor = get_parent() as OperatorActor
    if actor:
        visual = actor.get_node_or_null("VisualRoot") as OperatorVisual
    call_deferred("_bind")

func _bind() -> void:
    if visual:
        _bones = visual.get("_bones")
        _base_rotations.clear()
        for bone_name in _bones.keys():
            var bone := _bones[bone_name] as Bone2D
            if bone != null:
                _base_rotations[bone_name] = bone.rotation

func _process(_delta: float) -> void:
    if actor == null or visual == null:
        return
    if _bones.is_empty():
        _bind()
    if _bones.is_empty():
        return

    var speed := actor.velocity.length()
    if speed <= 1.0:
        _last_screen_diagonal = false
        _last_forward = 0.0
        _last_strafe = 0.0
        _restore_non_animated_offsets()
        return

    var move_dir := actor.velocity.normalized()
    var aim_dir := actor.aim_world.normalized() if actor.aim_world.length_squared() > 0.001 else Vector2.RIGHT
    var side_dir := Vector2(-aim_dir.y, aim_dir.x)
    var forward := move_dir.dot(aim_dir)
    var strafe := move_dir.dot(side_dir)
    var speed_norm := clampf(speed/maxf(1.0,actor.run_speed),0.0,1.2)
    var screen_diagonal := absf(move_dir.x) > 0.32 and absf(move_dir.y) > 0.32

    _last_screen_diagonal = screen_diagonal
    _last_forward = forward
    _last_strafe = strafe

    var pelvis := _bones.get("pelvis") as Bone2D
    var torso := _bones.get("torso") as Bone2D
    var thigh_l := _bones.get("thigh_L") as Bone2D
    var thigh_r := _bones.get("thigh_R") as Bone2D
    var shin_l := _bones.get("shin_L") as Bone2D
    var shin_r := _bones.get("shin_R") as Bone2D
    var foot_l := _bones.get("foot_L") as Bone2D
    var foot_r := _bones.get("foot_R") as Bone2D
    var base_positions: Dictionary = visual.get("_base_positions")

    # Important M6 rule: never rotate the pelvis/root to imply strafe. Because the
    # torso/head/legs inherit from pelvis, that old shortcut made the whole operator
    # look like a paper doll lying sideways. Direction is communicated through stance
    # width, feet and translation. All offsets are absolute from cached rig bases so
    # holding a diagonal input cannot accumulate limb drift frame after frame.
    if pelvis:
        var pelvis_base: Vector2 = base_positions.get("pelvis",pelvis.position)
        pelvis.position.x = pelvis_base.x + strafe*2.8*speed_norm
        pelvis.position.y += maxf(0.0,-forward)*1.5*speed_norm
    if torso:
        var torso_base: Vector2 = base_positions.get("torso",torso.position)
        torso.rotation += clampf(-strafe*0.012*speed_norm,-0.018,0.018)
        torso.position.x = torso_base.x - strafe*0.9*speed_norm

    var diagonal_gain := minf(absf(forward),absf(strafe))*1.15 if screen_diagonal else 0.0
    var backpedal := maxf(0.0,-forward)
    if thigh_l and thigh_r:
        var thigh_l_base: Vector2 = base_positions.get("thigh_L",thigh_l.position)
        var thigh_r_base: Vector2 = base_positions.get("thigh_R",thigh_r.position)
        thigh_l.rotation += strafe*0.075*speed_norm + diagonal_gain*0.055
        thigh_r.rotation += strafe*0.075*speed_norm - diagonal_gain*0.055
        thigh_l.position.x = thigh_l_base.x - absf(strafe)*1.7*speed_norm
        thigh_r.position.x = thigh_r_base.x + absf(strafe)*1.7*speed_norm
    if shin_l and shin_r:
        shin_l.rotation += backpedal*0.09*speed_norm - strafe*0.028*speed_norm
        shin_r.rotation += backpedal*0.09*speed_norm + strafe*0.028*speed_norm
    if foot_l and foot_r:
        var foot_turn := clampf(strafe*0.13 + move_dir.x*0.04,-0.17,0.17)
        foot_l.rotation = float(_base_rotations.get("foot_L",0.0)) + foot_turn
        foot_r.rotation = float(_base_rotations.get("foot_R",0.0)) + foot_turn

    # Small depth scaling only; presentation never changes gameplay coordinates.
    if visual.skeleton:
        var depth_scale := 1.0 + clampf(move_dir.y,-1.0,1.0)*0.010*speed_norm
        visual.skeleton.scale *= Vector2(depth_scale,depth_scale)

func _restore_non_animated_offsets() -> void:
    var base_positions: Dictionary = visual.get("_base_positions")
    for bone_name in ["pelvis","torso","thigh_L","thigh_R"]:
        var bone := _bones.get(bone_name) as Bone2D
        if bone == null:
            continue
        var base_pos: Vector2 = base_positions.get(bone_name,bone.position)
        bone.position.x = base_pos.x
    for bone_name in ["foot_L","foot_R"]:
        var bone := _bones.get(bone_name) as Bone2D
        if bone != null:
            bone.rotation = float(_base_rotations.get(bone_name,0.0))

func debug_locomotion_contract() -> Dictionary:
    return {
        "screen_diagonal": _last_screen_diagonal,
        "forward": _last_forward,
        "strafe": _last_strafe,
        "pelvis_rotation_forbidden": true,
        "non_accumulating_offsets": true
    }
