extends Node2D
class_name OperatorWeaponIK

var actor: OperatorActor
var visual: OperatorVisual
var _bones: Dictionary = {}
var _enabled := false

func _ready() -> void:
    process_priority = 115
    actor = get_parent() as OperatorActor
    if actor:
        visual = actor.get_node_or_null("VisualRoot") as OperatorVisual
    call_deferred("_bind")

func _bind() -> void:
    if visual == null:
        return
    _bones = visual.get("_bones")
    _enabled = _bones.has("weapon_root") and _bones.has("upper_arm_L") and _bones.has("lower_arm_L") and _bones.has("upper_arm_R") and _bones.has("lower_arm_R")

func _process(_delta: float) -> void:
    if not _enabled or visual == null:
        return
    if _bones.is_empty():
        _bind()
        return

    var weapon := _bones.get("weapon_root") as Bone2D
    var ul := _bones.get("upper_arm_L") as Bone2D
    var ll := _bones.get("lower_arm_L") as Bone2D
    var ur := _bones.get("upper_arm_R") as Bone2D
    var lr := _bones.get("lower_arm_R") as Bone2D
    if weapon == null or ul == null or ll == null or ur == null or lr == null:
        return

    var identity := str(actor.art_profile.get("visual_profile",actor.display_name)).to_upper()
    var reload_t := float(visual.reload_progress) if visual.is_reloading else 0.0
    var fold := sin(reload_t*PI)

    # Targets are expressed in torso-local space, matching the arm and weapon bones.
    # The weapon keeps the authoritative aim angle; the arms solve themselves to it.
    var primary_offset := Vector2(7.0,2.0)
    var support_offset := Vector2(21.0,-1.0)
    var upper_len := 16.0
    var lower_len := 16.0
    if "ROOK" in identity:
        primary_offset = Vector2(8.0,3.0)
        support_offset = Vector2(23.0,-1.0)
        upper_len = 17.5
        lower_len = 17.0
    elif "MICA" in identity:
        primary_offset = Vector2(6.0,1.0)
        support_offset = Vector2(18.5,-1.5)
        upper_len = 15.5
        lower_len = 15.5

    if fold > 0.0:
        # Tactical reload lowers the weapon while keeping shoulders connected.
        primary_offset += Vector2(-2.0,9.0*fold)
        support_offset += Vector2(-7.0,12.0*fold)

    var primary_target := weapon.position + primary_offset.rotated(weapon.rotation)
    var support_target := weapon.position + support_offset.rotated(weapon.rotation)

    _solve_two_bone(ur,lr,primary_target,upper_len,lower_len,-1.0)
    _solve_two_bone(ul,ll,support_target,upper_len,lower_len,1.0)

func _solve_two_bone(upper: Bone2D, lower: Bone2D, target: Vector2, upper_len: float, lower_len: float, bend_sign: float) -> void:
    var shoulder := upper.position
    var delta := target-shoulder
    var raw_distance := delta.length()
    if raw_distance < 0.001:
        return
    var distance := clampf(raw_distance,absf(upper_len-lower_len)+0.35,upper_len+lower_len-0.35)
    var base_angle := delta.angle()
    var cos_shoulder := clampf((upper_len*upper_len+distance*distance-lower_len*lower_len)/(2.0*upper_len*distance),-1.0,1.0)
    var shoulder_offset := acos(cos_shoulder)
    var cos_elbow := clampf((upper_len*upper_len+lower_len*lower_len-distance*distance)/(2.0*upper_len*lower_len),-1.0,1.0)
    var elbow_inner := acos(cos_elbow)

    upper.rotation = base_angle + bend_sign*shoulder_offset
    lower.rotation = -bend_sign*(PI-elbow_inner)

func debug_connected() -> bool:
    return _enabled
