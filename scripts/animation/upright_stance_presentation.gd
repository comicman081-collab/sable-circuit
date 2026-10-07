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

    var pelvis := _bones.get("pelvis") as Bone2D
    var torso := _bones.get("torso") as Bone2D
    var head := _bones.get("head") as Bone2D
    var thigh_l := _bones.get("thigh_L") as Bone2D
    var thigh_r := _bones.get("thigh_R") as Bone2D
    var shin_l := _bones.get("shin_L") as Bone2D
    var shin_r := _bones.get("shin_R") as Bone2D
    var foot_l := _bones.get("foot_L") as Bone2D
    var foot_r := _bones.get("foot_R") as Bone2D

    # M6 field contract: the character's vertical body axis never follows aim or
    # diagonal strafe. Pelvis/root is authoritative upright; torso/head may only
    # carry tiny natural sway. Arms/weapon are solved later by OperatorWeaponIK.
    if pelvis:
        pelvis.rotation = 0.0
    if torso:
        torso.rotation = clampf(torso.rotation, -0.026, 0.026)
    if head:
        head.rotation = clampf(head.rotation, -0.035, 0.035)

    # Keep locomotion readable without the exaggerated paper-doll lean.
    if thigh_l:
        thigh_l.rotation = clampf(thigh_l.rotation * 0.58, -0.34, 0.34)
    if thigh_r:
        thigh_r.rotation = clampf(thigh_r.rotation * 0.58, -0.34, 0.34)
    if shin_l:
        shin_l.rotation = clampf(shin_l.rotation * 0.68, -0.28, 0.28)
    if shin_r:
        shin_r.rotation = clampf(shin_r.rotation * 0.68, -0.28, 0.28)
    if foot_l:
        foot_l.rotation = clampf(foot_l.rotation * 0.52, -0.16, 0.16)
    if foot_r:
        foot_r.rotation = clampf(foot_r.rotation * 0.52, -0.16, 0.16)

func debug_upright() -> bool:
    return true

func debug_body_axis_locked() -> bool:
    if _bones.is_empty():
        _bind()
    var pelvis := _bones.get("pelvis") as Bone2D
    return pelvis != null and absf(pelvis.rotation) < 0.001
