extends SceneTree
const MotionPlayer = preload("res://skeletal_motion_player.gd")
var failures: Array[String] = []
var cases: Array = []

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var pack: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://MOTION_PACK.json"))
    for hz in [30, 60, 120]:
        for direction in range(8):
            _direction(pack, hz, direction)
    _projected_routing(pack)
    if cases.size() != 24: failures.append("INCOMPLETE_TEST_EXECUTION")
    var report := {"scope":"actual_blender_bones_technical_only", "case_count":cases.size(),
        "cases":cases, "failures":failures, "production_ready":false,
        "mica_appearance_or_fire_coverage_tested":false}
    var file := FileAccess.open("res://RESULT.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(report,"  "))
    print("SKELETAL_MOTION_CASES ", cases.size(), " FAILURES ", failures.size())
    for failure in failures: print(failure)
    quit(0 if failures.is_empty() else 1)

func _projected_routing(original: Dictionary) -> void:
    # Routing fixture only: duplicated clips do not represent authored strafing.
    var pack := original.duplicate(true)
    pack["authored_projection"] = {"schema":1, "kind":"source_orthographic_elevation",
        "elevation_degrees":30.0,"camera_center_height_m":0.875,
        "orthographic_size_m":2.0*cos(PI/6.0)}
    pack["clips"]["run/forward_right"] = pack["clips"]["run/forward"].duplicate(true)
    var player = MotionPlayer.new()
    var skeleton := Skeleton3D.new()
    player.add_child(skeleton)
    root.add_child(player)
    for row: Dictionary in pack["bone_order"]:
        skeleton.add_bone(row["name"])
        var index := skeleton.get_bone_count()-1
        skeleton.set_bone_parent(index,int(row["parent"]))
        skeleton.set_bone_rest(index,MotionPlayer._transform(row["rest"]))
    if not player.configure(skeleton,pack,100.0):
        failures.append("PROJECTED_CONFIG:"+player.error)
        player.free()
        return
    var spine: String = pack["humanoid_roles"]["spine"]
    var mask: Array[String] = [spine]
    player.configure_upper_body(mask,[pack["bone_order"][skeleton.find_bone(spine)]["rest"]],Quaternion.IDENTITY)
    if not player.commit_displacement(Vector2(-1,1),Vector2(1,1),1.0/60.0,true):
        failures.append("PROJECTED_ROUTING:"+player.error)
    if player.active_clip != "run/forward_right":
        failures.append("PROJECTED_RELATIVE_SECTOR_WRONG")
    var distance := float(pack["clips"]["run/forward"]["distance_m"])
    if absf(player.phase-sqrt(5.0)/(100.0*distance)) > 0.000001:
        failures.append("PROJECTED_DIAGONAL_DISTANCE_WRONG")
    for move in [Vector2(100,0),Vector2(0,50)]:
        player.phase = 0.0
        if not player.commit_displacement(move,move,1.0,false):
            failures.append("PROJECTED_METRE:"+player.error)
        if absf(player.phase-fposmod(1.0/distance,1.0)) > 0.000001:
            failures.append("PROJECTED_METRE_PHASE_WRONG")
    player.free()

func _direction(pack: Dictionary, hz: int, direction: int) -> void:
    var player = MotionPlayer.new()
    var skeleton := Skeleton3D.new()
    player.add_child(skeleton)
    root.add_child(player)
    for row: Dictionary in pack["bone_order"]:
        skeleton.add_bone(row["name"])
        var index := skeleton.get_bone_count()-1
        skeleton.set_bone_parent(index,int(row["parent"]))
        skeleton.set_bone_rest(index,MotionPlayer._transform(row["rest"]))
    if not player.configure(skeleton,pack,100.0):
        failures.append(player.error)
        player.free()
        return
    var left := skeleton.find_bone(pack["humanoid_roles"]["left_foot"])
    var spine_name: String = pack["humanoid_roles"]["spine"]
    var spine := skeleton.find_bone(spine_name)
    var mask: Array[String] = [spine_name]
    var spine_row: Dictionary = pack["bone_order"][spine]["rest"]
    if not player.configure_upper_body(mask,[spine_row],Quaternion(Vector3.RIGHT,0.08)):
        failures.append(player.error)
    var vector := Vector2.RIGHT.rotated(float(direction)*PI/4.0)
    var observations: Array[Vector3] = []
    var before_fire_phase := 0.0
    for tick in range(hz*2):
        if not player.commit_displacement(vector*224.0/hz,vector,1.0/hz,false):
            failures.append(player.error)
            break
        skeleton.force_update_all_bone_transforms()
        observations.append(skeleton.get_bone_global_pose(left).origin)
        if tick == hz:
            before_fire_phase = player.phase
            var before := skeleton.get_bone_global_pose(left)
            player.trigger_recoil()
            skeleton.force_update_all_bone_transforms()
            if player.phase != before_fire_phase or not skeleton.get_bone_global_pose(left).is_equal_approx(before):
                failures.append("RECOIL_CHANGED_LOWER_GAIT")
    var excursion := 0.0
    for point in observations: excursion=maxf(excursion,point.distance_to(observations[0]))
    if excursion < 0.05: failures.append("FOOT_DID_NOT_ANIMATE")
    var expected_phase := fposmod(448.0/(100.0*float(pack["clips"]["run/forward"]["distance_m"])),1.0)
    if absf(player.phase-expected_phase)>0.00001: failures.append("RATE_DEPENDENT_GAIT")
    var phase_before_stop: float = player.phase
    var rendered_forward: Vector3 = player.basis*MotionPlayer._vector(pack["forward_axis"])
    if Vector2(rendered_forward.x,rendered_forward.z).distance_to(vector)>0.00001:
        failures.append("WORLD_DIRECTION_REVERSED")
    player.commit_displacement(Vector2.ZERO,-vector,1.0/hz,true)
    rendered_forward=player.basis*MotionPlayer._vector(pack["forward_axis"])
    if Vector2(rendered_forward.x,rendered_forward.z).distance_to(-vector)>0.00001:
        failures.append("STATIONARY_AIM_DID_NOT_TURN")
    if player.phase != phase_before_stop: failures.append("STOP_ADVANCED_GAIT")
    if not skeleton.get_bone_pose(left).is_equal_approx(skeleton.get_bone_rest(left)):
        failures.append("IDLE_HELD_FLIGHT_POSE")
    # A missing backward/strafe clip must never be silently substituted by
    # twisting forward-run legs around a stationary aiming torso.
    var accepted: bool = player.commit_displacement(vector*2.0,-vector,1.0/hz,true)
    if accepted or not player.error.begins_with("MISSING_AUTHORED_RELATIVE_MOTION"):
        failures.append("BACKWARD_COVERAGE_FABRICATED")
    cases.append({"hz":hz,"world_direction":direction,"foot_excursion_m":excursion,
        "phase_after_two_seconds":phase_before_stop,"recoil_kept_lower_pose":true,
        "missing_backward_rejected":not accepted})
    player.configure(skeleton,pack,100.0)
    if not player.upper_mask.is_empty() or player.recoil_left != 0.0:
        failures.append("TARGET_REBIND_LEAKED_UPPER_POSE")
    if player.commit_displacement(Vector2.ZERO,vector,1.0/hz,true):
        failures.append("STATIONARY_AIM_WITHOUT_POSE_ACCEPTED")
    player.commit_displacement(vector*3.0,vector,1.0/hz,false)
    var gait_spine: Transform3D = skeleton.get_bone_pose(spine)
    var local_kick := Vector3(-0.02,0,0)
    if not player.configure_upper_body(mask,[spine_row],Quaternion(Vector3.RIGHT,0.08),true,local_kick):
        failures.append("ADDITIVE_UPPER_BIND_FAILED")
    var lower_before: Transform3D = skeleton.get_bone_global_pose(left)
    var phase_before_recoil: float = player.phase
    player.trigger_recoil()
    var first_recoil: Transform3D = skeleton.get_bone_pose(spine)
    var expected_recoil := gait_spine
    expected_recoil.origin += gait_spine.basis * local_kick * 0.45
    expected_recoil.basis *= Basis(Quaternion(Vector3.RIGHT,0.08*0.45))
    if not first_recoil.is_equal_approx(expected_recoil):
        failures.append("SOFT_RECOIL_REPLACED_EVALUATED_TORSO_POSE")
    player.trigger_recoil()
    if not skeleton.get_bone_pose(spine).is_equal_approx(first_recoil):
        failures.append("REPEATED_SHOT_ACCUMULATED_RECOIL")
    if player.phase != phase_before_recoil or not skeleton.get_bone_global_pose(left).is_equal_approx(lower_before):
        failures.append("ADDITIVE_RECOIL_CHANGED_FEET_OR_GAIT_PHASE")
    player.free()
