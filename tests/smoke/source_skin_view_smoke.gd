extends SceneTree
const View = preload("res://scripts/animation/source_skin_view.gd")
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("run")

func check(value: bool, message: String) -> void:
    if not value: failures.append(message)

func run() -> void:
    var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://SOURCE_SKIN.json"))
    var motion: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://MOTION_PACK.json"))
    var picture := Image.load_from_file("res://SOURCE_RGBA.png")
    var texture := ImageTexture.create_from_image(picture)
    var view := View.new()
    root.add_child(view)
    check(view.configure(source, motion, texture, 100.0), "actual source skin must bind: " + view.error)
    if not failures.is_empty(): finish(); return
    check(view.skeleton.get_bone_count() == 22, "actual 22-bone binding")
    check(view.mesh_instance.skin.get_bind_count() == 22, "all inverse bind matrices present")
    var arrays: Array = view.mesh_instance.mesh.surface_get_arrays(0)
    var points: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
    var indices: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
    var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
    var largest_neutral_error := 0.0
    var largest_quantization_bound := 0.0
    var largest_movement := 0.0
    var neutral_positions: Array[Vector3] = []
    var skin: Skin = view.mesh_instance.skin
    for i in range(0, points.size(), 31):
        var position := Vector3.ZERO
        for j in range(4):
            var b := indices[i * 4 + j]
            position += (view.skeleton.get_bone_global_pose(b) * skin.get_bind_pose(b) * points[i]) * weights[i * 4 + j]
        largest_neutral_error = maxf(largest_neutral_error, position.distance_to(points[i]))
        # ArrayMesh stores skin weights as UNORM16. Four independently rounded
        # weights can change their sum by at most 4/65535; allow that explicit
        # vertex-scale error plus floating-point matrix composition precision.
        var quantization_bound := points[i].length() * 4.0 / 65535.0 + 0.000002
        largest_quantization_bound = maxf(largest_quantization_bound, quantization_bound)
        check(position.distance_to(points[i]) <= quantization_bound, "neutral skin exceeds weight quantization bound")
        neutral_positions.append(position)
    var player = view.motion_player
    player.running = true
    player._sample(motion["clips"]["run/forward"], 0.48)
    for i in range(0, points.size(), 31):
        var position := Vector3.ZERO
        for j in range(4):
            var b := indices[i * 4 + j]
            position += (view.skeleton.get_bone_global_pose(b) * skin.get_bind_pose(b) * points[i]) * weights[i * 4 + j]
        largest_movement = maxf(largest_movement, position.distance_to(neutral_positions[i / 31]))
    check(largest_movement > 0.10, "source vertices must actually deform with Blender motion")
    var material: StandardMaterial3D = view.mesh_instance.mesh.surface_get_material(0)
    var retained_base: Image = material.albedo_texture.get_image().get_region(Rect2i(Vector2i.ZERO, picture.get_size()))
    retained_base.clear_mipmaps()
    var original_base: Image = picture.duplicate()
    original_base.clear_mipmaps()
    check(retained_base.get_data() == original_base.get_data(), "original base source pixels retained before mip filtering")
    check(material.albedo_texture.get_image().has_mipmaps(), "battle-scale source minification uses mipmaps")
    check(material.transparency == BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR, "real alpha required")
    var broken := source.duplicate(true)
    broken["weights"][0] = -1.0
    check(not view.configure(broken, motion, texture, 100.0), "invalid weights rejected")
    check(view.get_child_count() == 0, "failed binding must not leave a partial visible character")
    check(view.configure(source, motion, texture, 100.0), "valid rebind after rejection")
    var invalid_motion := motion.duplicate(true)
    invalid_motion["clips"]["run/forward"]["duration_s"] = 0.0
    check(not view.configure(source, invalid_motion, texture, 100.0), "invalid clip rejected")
    check(view.get_child_count() == 0, "failed clip binding clears renderer")
    view.free()
    finish({"sampled_vertices": neutral_positions.size(), "neutral_max_error_m": largest_neutral_error,
            "neutral_weight_quantization_bound_m": largest_quantization_bound,
            "actual_deformation_max_m": largest_movement, "render_capture_performed": false})

func finish(metrics: Dictionary = {}) -> void:
    var file := FileAccess.open("res://RESULT.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"scope":"actual Blender skin and Godot bone binding; no GPU visual claim", "failures":failures,"metrics":metrics}, "  "))
    file.close()
    quit(0 if failures.is_empty() else 1)
