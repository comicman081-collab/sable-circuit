extends Node3D
class_name SkeletalMotionPlayer
## Evaluated Blender bone motion. Rendering, appearance approval and gameplay
## remain with the character binding and the real OperatorActor.

const RELATIVE := ["forward", "forward_right", "right", "backward_right", "backward", "backward_left", "left", "forward_left"]
const RECOIL_KEYS := [0.45, 1.0, 0.45, -0.28, -0.10, 0.0]
const RECOIL_DURATION := 5.0 / 30.0
const SourceProjection = preload("res://scripts/animation/source_projection.gd")
var skeleton: Skeleton3D
var pack: Dictionary = {}
var clips: Dictionary = {}
var bone_indices: Array[int] = []
var phase := 0.0
var active_clip := ""
var error := ""
var moving := false
var running := true
var recoil_left := 0.0
var upper_mask: Array[int] = []
var upper_pose: Array = []
var upper_additive := false
var _upper_base: Array[Transform3D] = []
var recoil_rotation := Quaternion.IDENTITY
var recoil_translation := Vector3.ZERO
var pixels_per_metre := 100.0
var forward_axis := Vector3.FORWARD
var ground_vertical_scale := 1.0
var _intent := Vector2.ZERO

func configure(target: Skeleton3D, motion: Dictionary, pixels_in_metre: float) -> bool:
    error = ""
    skeleton = null
    pack = {}
    clips = {}
    bone_indices.clear()
    upper_mask.clear()
    upper_pose.clear()
    _upper_base.clear()
    upper_additive = false
    recoil_left = 0.0
    recoil_rotation = Quaternion.IDENTITY
    recoil_translation = Vector3.ZERO
    phase = 0.0
    active_clip = ""
    ground_vertical_scale = 1.0
    var projection: Dictionary = SourceProjection.resolve(motion.get("authored_projection"))
    if projection.is_empty():
        return _fail("INVALID_AUTHORED_SOURCE_PROJECTION")
    if motion.get("representation") != "evaluated_skeleton_motion" or motion.get("coordinate_system") != "godot_y_up":
        return _fail("INVALID_BONE_MOTION_PACK")
    if target == null or not is_finite(pixels_in_metre) or pixels_in_metre <= 0:
        return _fail("INVALID_TARGET_OR_WORLD_UNITS")
    var axis: Variant = motion.get("forward_axis")
    if not axis is Array or axis.size() != 3:
        return _fail("EXPLICIT_FORWARD_AXIS_REQUIRED")
    for component: Variant in axis:
        if not (component is float or component is int) or not is_finite(float(component)):
            return _fail("INVALID_FORWARD_AXIS")
    var source_forward := _vector(axis)
    if absf(source_forward.length()-1.0)>0.0001 or absf(source_forward.y)>0.0001:
        return _fail("PLANAR_UNIT_FORWARD_AXIS_REQUIRED")
    var names: Dictionary = {}
    var rows: Array = motion.get("bone_order", [])
    if rows.is_empty(): return _fail("MISSING_REST_BONES")
    var mapped: Array[int] = []
    for i in range(rows.size()):
        var row: Dictionary = rows[i]
        var bone_name := str(row.get("name", ""))
        var parent_index := int(row.get("parent", -2))
        if bone_name.is_empty() or names.has(bone_name) or parent_index < -1 or parent_index >= i:
            return _fail("INVALID_PARENT_ORDER_OR_DUPLICATE_BONE")
        names[bone_name] = true
        var index := target.find_bone(bone_name)
        if index < 0: return _fail("TARGET_BONE_MISSING:" + bone_name)
        var expected_parent := -1 if parent_index == -1 else mapped[parent_index]
        if target.get_bone_parent(index) != expected_parent:
            return _fail("TARGET_HIERARCHY_MISMATCH:" + bone_name)
        if not _valid_pose(row.get("rest", {})):
            return _fail("INVALID_REST_TRANSFORM")
        var rest := _transform(row["rest"])
        if not target.get_bone_rest(index).is_equal_approx(rest):
            return _fail("RETARGET_REQUIRED_FOR_DIFFERENT_REST:" + bone_name)
        mapped.append(index)
    var candidate: Dictionary = motion.get("clips", {})
    if candidate.is_empty(): return _fail("NO_ANIMATION_CLIPS")
    for key: String in candidate:
        var clip: Dictionary = candidate[key]
        var duration := float(clip.get("duration_s", 0.0))
        var frames: Array = clip.get("frames", [])
        if not is_finite(duration) or duration <= 0 or frames.size() < 3:
            return _fail("INVALID_CLIP_TIMING:" + key)
        if not is_finite(float(clip.get("distance_m", 0.0))) or float(clip.get("distance_m", 0.0)) <= 0:
            return _fail("ACTUAL_CYCLE_DISTANCE_REQUIRED:" + key)
        var last := -1.0
        for frame: Dictionary in frames:
            var time := float(frame.get("time_s", -1.0))
            var poses: Array = frame.get("poses", [])
            if not is_finite(time) or time <= last or poses.size() != mapped.size():
                return _fail("INVALID_EVALUATED_SAMPLE:" + key)
            for pose: Dictionary in poses:
                if not _valid_pose(pose): return _fail("INVALID_BONE_TRANSFORM:" + key)
            last = time
        if absf(float(frames[0]["time_s"])) > 0.000001 or absf(last - duration) > 0.000001:
            return _fail("EXACT_CYCLE_ENDPOINTS_REQUIRED:" + key)
    skeleton = target
    pack = motion
    clips = candidate
    bone_indices = mapped
    pixels_per_metre = pixels_in_metre
    forward_axis = source_forward
    ground_vertical_scale = float(projection["ground_vertical_scale"])
    phase = 0.0
    active_clip = ""
    return true

func configure_upper_body(bone_names: Array[String], pose_rows: Array, recoil: Quaternion, additive: bool = false, local_translation: Vector3 = Vector3.ZERO) -> bool:
    if skeleton == null or bone_names.is_empty() or bone_names.size() != pose_rows.size():
        return _fail("EXPLICIT_UPPER_BODY_POSE_REQUIRED")
    var roles: Dictionary = pack.get("humanoid_roles", {})
    var hips := skeleton.find_bone(str(roles.get("hips", "")))
    var selected: Array[int] = []
    var root_spine := skeleton.find_bone(str(roles.get("spine", "")))
    if bone_names[0] != str(roles.get("spine", "")) or not recoil.is_finite() or recoil.length_squared() < 0.0001 or not local_translation.is_finite():
        return _fail("EXPLICIT_SPINE_RECOIL_ROOT_REQUIRED")
    for i in range(bone_names.size()):
        var index := skeleton.find_bone(bone_names[i])
        if index < 0 or index == hips or selected.has(index) or not _valid_pose(pose_rows[i]):
            return _fail("INVALID_UPPER_BODY_MASK")
        # A lower-body joint in an aim/recoil mask would silently replace gait.
        var ancestor := index
        while ancestor >= 0 and ancestor != root_spine:
            ancestor = skeleton.get_bone_parent(ancestor)
        if root_spine < 0 or ancestor != root_spine:
            return _fail("AIM_MASK_MUST_STAY_ABOVE_PELVIS")
        selected.append(index)
    upper_mask = selected
    upper_pose = pose_rows.duplicate(true)
    recoil_rotation = recoil.normalized()
    recoil_translation = local_translation
    upper_additive = additive
    _capture_upper_base()
    return true

func set_motion_intent(direction: Vector2, is_running: bool) -> void:
    _intent = direction
    running = is_running

func commit_displacement(displacement: Vector2, aim: Vector2, delta: float, aiming: bool) -> bool:
    if skeleton == null or delta <= 0: return false
    recoil_left = maxf(0.0, recoil_left - delta)
    moving = displacement.length() / delta > 0.1
    if aiming and (upper_mask.is_empty() or not aim.is_finite() or aim.length_squared() < 0.00001):
        return _fail("AIM_POSE_NOT_BOUND")
    var heading := aim.angle() if aiming else displacement.angle()
    var screen_heading := Vector2.from_angle(heading)
    var physical_heading := Vector2(screen_heading.x, screen_heading.y / ground_vertical_scale).angle()
    var yaw := atan2(forward_axis.z,forward_axis.x)-physical_heading
    if not moving:
        if aiming: rotation.y = yaw
        # Stand in the neutral bind pose; never freeze a flight frame as idle.
        for i in range(bone_indices.size()):
            skeleton.set_bone_pose(bone_indices[i], _transform(pack["bone_order"][i]["rest"]))
        active_clip = ""
        _capture_upper_base()
        _apply_upper()
        return true
    var physical_displacement := Vector2(displacement.x, displacement.y / ground_vertical_scale)
    var move_angle := physical_displacement.angle()
    var relative_sector := posmod(roundi(wrapf(move_angle - physical_heading, -PI, PI) / (PI / 4.0)), 8)
    var key: String = ("run/" if running else "walk/") + str(RELATIVE[relative_sector])
    if not clips.has(key):
        return _fail("MISSING_AUTHORED_RELATIVE_MOTION:" + key)
    var clip: Dictionary = clips[key]
    phase = fposmod(phase + physical_displacement.length() / (float(clip["distance_m"]) * pixels_per_metre), 1.0)
    # Body yaw and the relative locomotion clip change together. No 180-degree
    # detached lower-body rotation under a forward-only upper body.
    rotation.y = yaw
    active_clip = key
    error = ""
    _sample(clip, phase)
    _capture_upper_base()
    _apply_upper()
    return true

func trigger_recoil() -> void:
    # Commit the soft first pose before OperatorActor asks for the muzzle.
    recoil_left = RECOIL_DURATION
    _apply_upper()

func _sample(clip: Dictionary, sample_phase: float) -> void:
    var time := sample_phase * float(clip["duration_s"])
    var frames: Array = clip["frames"]
    var index := 0
    while index + 1 < frames.size() - 1 and float(frames[index + 1]["time_s"]) <= time:
        index += 1
    var first: Dictionary = frames[index]
    var second: Dictionary = frames[index + 1]
    var amount := (time - float(first["time_s"])) / (float(second["time_s"]) - float(first["time_s"]))
    for i in range(bone_indices.size()):
        var a: Dictionary = first["poses"][i]
        var b: Dictionary = second["poses"][i]
        skeleton.set_bone_pose_position(bone_indices[i], _vector(a["p"]).lerp(_vector(b["p"]), amount))
        skeleton.set_bone_pose_rotation(bone_indices[i], _quaternion(a["q"]).slerp(_quaternion(b["q"]), amount))
        skeleton.set_bone_pose_scale(bone_indices[i], _vector(a["s"]).lerp(_vector(b["s"]), amount))

func _capture_upper_base() -> void:
    _upper_base.clear()
    for index in upper_mask:
        _upper_base.append(skeleton.get_bone_pose(index))

func _recoil_amount() -> float:
    if recoil_left <= 0.0:
        return 0.0
    var sample := clampf((RECOIL_DURATION - recoil_left) * 30.0, 0.0, 5.0)
    var index := mini(floori(sample), 4)
    return lerpf(RECOIL_KEYS[index], RECOIL_KEYS[index + 1], sample - index)

func _apply_upper() -> void:
    for i in range(upper_mask.size()):
        var value := _transform(upper_pose[i])
        if upper_additive:
            # Preserve evaluated gait's torso compensation. A rest aim pose
            # contributes identity; repeated fire never accumulates offsets.
            value = _upper_base[i] * skeleton.get_bone_rest(upper_mask[i]).affine_inverse() * value
        if i == 0 and recoil_left > 0:
            var amount := _recoil_amount()
            value.origin += value.basis * recoil_translation * amount
            var angle := recoil_rotation.get_angle()
            if absf(angle) > 0.00000001:
                value.basis *= Basis(Quaternion(recoil_rotation.get_axis(), angle * amount))
        skeleton.set_bone_pose(upper_mask[i], value)

func _fail(message: String) -> bool:
    error = message
    return false

static func _vector(value: Array) -> Vector3:
    return Vector3(value[0], value[1], value[2])

static func _quaternion(value: Array) -> Quaternion:
    return Quaternion(value[0], value[1], value[2], value[3]).normalized()

static func _transform(value: Dictionary) -> Transform3D:
    return Transform3D(Basis(_quaternion(value["q"])).scaled(_vector(value["s"])), _vector(value["p"]))

static func _valid_pose(value: Dictionary) -> bool:
    for key in ["p", "q", "s"]:
        if not value.get(key) is Array or value[key].size() != (4 if key == "q" else 3): return false
        for component: Variant in value[key]:
            if not (component is float or component is int) or not is_finite(float(component)): return false
    var q: Array = value["q"]
    var norm := float(q[0])*float(q[0]) + float(q[1])*float(q[1]) + float(q[2])*float(q[2]) + float(q[3])*float(q[3])
    return absf(norm - 1.0) < 0.001 and float(value["s"][0]) > 0 and float(value["s"][1]) > 0 and float(value["s"][2]) > 0
