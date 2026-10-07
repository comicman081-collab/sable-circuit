extends SceneTree
const Binding = preload("res://source_skin_weapon_binding.gd")

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var skeleton := Skeleton3D.new()
    root.add_child(skeleton)
    skeleton.add_bone("weapon")
    skeleton.set_bone_rest(0, Transform3D(Basis.IDENTITY, Vector3(0, 1, 0)))
    skeleton.set_bone_pose(0, skeleton.get_bone_rest(0))
    var binding = Binding.new()
    var failures: Array[String] = []
    var data := {"coordinate_system": "godot_y_up_mesh_rest", "bone": "weapon",
        "muzzle": [2.0, 1.0, 0.0], "barrel_rear": [1.0, 1.0, 0.0]}
    if not binding.configure(skeleton, data):
        failures.append("configure")
    var first: Dictionary = binding.current_launch()
    if first.get("origin", Vector3.ZERO).distance_to(Vector3(2, 1, 0)) > 0.00001:
        failures.append("rest muzzle")
    skeleton.set_bone_pose(0, Transform3D(Basis(Vector3.UP, PI / 2), Vector3(0, 1, 0)))
    var turned: Dictionary = binding.current_launch()
    if turned.get("origin", Vector3.ZERO).distance_to(Vector3(0, 1, -2)) > 0.00001:
        failures.append("muzzle follows actual bone")
    if turned.get("direction", Vector3.ZERO).distance_to(Vector3.FORWARD) > 0.00001:
        failures.append("axis follows actual bone")
    if first.get("direction", Vector3.ZERO) != Vector3.RIGHT:
        failures.append("prior shot changed with later aim")
    var invalid := data.duplicate(true)
    invalid["muzzle"][0] = NAN
    if binding.configure(skeleton, invalid) or not binding.current_launch().is_empty():
        failures.append("invalid socket did not clear previous binding")
    var result := {"synthetic_fixture": true, "production_ready": false,
        "scope": "actual Godot bone API and shot snapshot only", "failures": failures}
    var file := FileAccess.open("res://RESULT.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(result, "  "))
    file.close()
    skeleton.free()
    quit(0 if failures.is_empty() else 1)
