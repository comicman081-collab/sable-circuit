extends Node2D
class_name DiagonalLocomotionPresentation

var actor: OperatorActor
var visual: OperatorVisual
var _bones: Dictionary = {}
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

func _process(_delta: float) -> void:
    if actor == null or visual == null:
        return
    if _bones.is_empty():
        _bones = visual.get("_bones")
    if _bones.is_empty():
        return

    var speed := actor.velocity.length()
    if speed <= 1.0:
        _last_screen_diagonal = false
        _last_forward = 0.0
        _last_strafe = 0.0
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

    # Lateral travel shifts the lower body under the independently aimed torso.
    # This is intentionally additive after OperatorVisual's base gait.
    if pelvis:
        pelvis.rotation += strafe*0.075*speed_norm
        pelvis.position.x += strafe*3.6*speed_norm
        pelvis.position.y += maxf(0.0,-forward)*1.8*speed_norm
    if torso:
        torso.rotation -= strafe*0.028*speed_norm
        torso.position.x -= strafe*1.6*speed_norm

    # Diagonal steps widen the stance instead of looking like a straight walk
    # sliding across the floor. Backpedal shortens the stride and adds knee bend.
    var diagonal_gain := minf(absf(forward),absf(strafe))*1.35 if screen_diagonal else 0.0
    var backpedal := maxf(0.0,-forward)
    if thigh_l and thigh_r:
        thigh_l.rotation += strafe*0.12*speed_norm + diagonal_gain*0.08
        thigh_r.rotation += strafe*0.12*speed_norm - diagonal_gain*0.08
        thigh_l.position.x -= absf(strafe)*2.1*speed_norm
        thigh_r.position.x += absf(strafe)*2.1*speed_norm
    if shin_l and shin_r:
        shin_l.rotation += backpedal*0.12*speed_norm - strafe*0.045*speed_norm
        shin_r.rotation += backpedal*0.12*speed_norm + strafe*0.045*speed_norm
    if foot_l and foot_r:
        var foot_turn := clampf(strafe*0.19 + move_dir.x*0.06,-0.24,0.24)
        foot_l.rotation += foot_turn
        foot_r.rotation += foot_turn

    # Screen-space travel depth: moving down comes slightly forward in the 3/4 view;
    # moving up recedes. This is subtle so hitboxes never depend on presentation.
    if visual.skeleton:
        var depth_scale := 1.0 + clampf(move_dir.y,-1.0,1.0)*0.018*speed_norm
        visual.skeleton.scale *= Vector2(depth_scale,depth_scale)

func debug_locomotion_contract() -> Dictionary:
    return {
        "screen_diagonal": _last_screen_diagonal,
        "forward": _last_forward,
        "strafe": _last_strafe
    }
