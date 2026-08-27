extends Node2D
class_name UprightStancePresentation

var actor: OperatorActor
var visual: OperatorVisual
var _bones: Dictionary = {}

func _ready() -> void:
    process_priority = 108
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
        _bind()
        return
    var torso := _bones.get("torso") as Bone2D
    var head := _bones.get("head") as Bone2D
    var thigh_l := _bones.get("thigh_L") as Bone2D
    var thigh_r := _bones.get("thigh_R") as Bone2D
    var shin_l := _bones.get("shin_L") as Bone2D
    var shin_r := _bones.get("shin_R") as Bone2D
    var foot_l := _bones.get("foot_L") as Bone2D
    var foot_r := _bones.get("foot_R") as Bone2D

    # Target-style field actors remain upright even when moving or aiming diagonally.
    # Preserve gait rhythm, but remove the exaggerated paper-doll tilt from M5.
    if torso:
        torso.rotation *= 0.42
    if head:
        head.rotation *= 0.55
    if thigh_l:
        thigh_l.rotation *= 0.62
    if thigh_r:
        thigh_r.rotation *= 0.62
    if shin_l:
        shin_l.rotation *= 0.72
    if shin_r:
        shin_r.rotation *= 0.72
    if foot_l:
        foot_l.rotation *= 0.55
    if foot_r:
        foot_r.rotation *= 0.55

func debug_upright() -> bool:
    return true
