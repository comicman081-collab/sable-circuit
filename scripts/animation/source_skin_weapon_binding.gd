extends RefCounted
class_name SourceSkinWeaponBinding
## A muzzle follows the same actual bone transform as its approved weapon pixels.
## Authored points still require an independent visible-barrel comparison.

var error := ""
var _skeleton: Skeleton3D
var _bone := -1
var _inverse_rest := Transform3D.IDENTITY
var _muzzle := Vector3.ZERO
var _rear := Vector3.ZERO

func configure(skeleton: Skeleton3D, binding: Dictionary) -> bool:
    _skeleton = null
    _bone = -1
    error = ""
    if skeleton == null or binding.get("coordinate_system") != "godot_y_up_mesh_rest":
        error = "EXACT_SKIN_REST_SPACE_REQUIRED"
        return false
    var index := skeleton.find_bone(str(binding.get("bone", "")))
    if index < 0:
        error = "WEAPON_BONE_MISSING"
        return false
    for key in ["muzzle", "barrel_rear"]:
        var point: Variant = binding.get(key)
        if not point is Array or point.size() != 3:
            error = "THREE_DIMENSIONAL_BARREL_POINT_REQUIRED"
            return false
        for value: Variant in point:
            if not (value is float or value is int) or not is_finite(float(value)):
                error = "FINITE_BARREL_POINT_REQUIRED"
                return false
    _muzzle = Vector3(binding["muzzle"][0], binding["muzzle"][1], binding["muzzle"][2])
    _rear = Vector3(binding["barrel_rear"][0], binding["barrel_rear"][1], binding["barrel_rear"][2])
    if _muzzle.distance_to(_rear) < 0.0001:
        error = "DISTINCT_VISIBLE_BARREL_AXIS_REQUIRED"
        return false
    _inverse_rest = skeleton.get_bone_global_rest(index).affine_inverse()
    _skeleton = skeleton
    _bone = index
    return true

func current_launch() -> Dictionary:
    if not is_instance_valid(_skeleton) or _bone < 0:
        return {}
    var deformation: Transform3D = _skeleton.global_transform * _skeleton.get_bone_global_pose(_bone) * _inverse_rest
    var origin: Vector3 = deformation * _muzzle
    var rear: Vector3 = deformation * _rear
    # Value types snapshot the launch. Subsequent aim/recoil cannot bend a shot.
    return {"origin": origin, "direction": (origin - rear).normalized()}
