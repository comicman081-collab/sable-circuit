extends Node3D
class_name SourceSkinView
## Original source pixels on an actual Blender-exported skinned mesh.
## This renderer does not substitute a generic character or animate a flat sprite.
const MotionPlayer = preload("res://scripts/animation/skeletal_motion_player.gd")

var motion_player: Node3D
var skeleton: Skeleton3D
var mesh_instance: MeshInstance3D
var error := ""

func configure(surface: Dictionary, motion: Dictionary, texture: Texture2D, pixels_per_metre: float) -> bool:
    for child in get_children():
        remove_child(child)
        child.free()
    skeleton = null
    mesh_instance = null
    motion_player = null
    error = ""
    if surface.get("representation") != "source_surface_skin" or surface.get("coordinate_system") != "godot_y_up":
        return _fail("INVALID_SOURCE_SKIN")
    if texture == null or surface.get("bone_order") != motion.get("bone_order"):
        return _fail("EXACT_TEXTURE_AND_TARGET_REST_REQUIRED")
    for key in ["positions", "uv", "bones", "weights", "indices", "bone_order"]:
        if not surface.get(key) is Array:
            return _fail("MISSING_SKIN_ARRAY:" + key)
    var points: Array = surface["positions"]
    var vertex_count: int = points.size() / 3
    if vertex_count < 3 or vertex_count > 250000 or points.size() != vertex_count * 3:
        return _fail("INVALID_VERTEX_COUNT")
    if surface["uv"].size() != vertex_count * 2 or surface["bones"].size() != vertex_count * 4 or surface["weights"].size() != vertex_count * 4:
        return _fail("INVALID_SKIN_ARRAY_LENGTH")
    if surface["indices"].is_empty() or surface["indices"].size() % 3 != 0:
        return _fail("TRIANGLE_INDICES_REQUIRED")
    for key in ["positions", "uv", "weights"]:
        for value: Variant in surface[key]:
            if not (value is float or value is int) or not is_finite(float(value)):
                return _fail("NONFINITE_SKIN_VALUE")
    var rows: Array = surface["bone_order"]
    for i in range(vertex_count):
        var total := 0.0
        for j in range(4):
            var bone: float = float(surface["bones"][i * 4 + j])
            var weight: float = float(surface["weights"][i * 4 + j])
            if not is_finite(bone) or bone != floor(bone) or bone < 0 or bone >= rows.size() or weight < 0 or weight > 1:
                return _fail("INVALID_VERTEX_BONE_BINDING")
            total += weight
        if absf(total - 1.0) > 0.00001:
            return _fail("UNNORMALIZED_VERTEX_WEIGHTS")
    for value: Variant in surface["indices"]:
        if not (value is float or value is int) or not is_finite(float(value)) or float(value) != floor(float(value)) or value < 0 or value >= vertex_count:
            return _fail("INVALID_TRIANGLE_INDEX")

    motion_player = MotionPlayer.new()
    motion_player.name = "BoneMotion"
    add_child(motion_player)
    skeleton = Skeleton3D.new()
    skeleton.name = "SourceSkeleton"
    motion_player.add_child(skeleton)
    var rest_world: Array[Transform3D] = []
    var bind := Skin.new()
    for i in range(rows.size()):
        var row: Dictionary = rows[i]
        var parent_index := int(row["parent"])
        if parent_index < -1 or parent_index >= i or str(row["name"]).is_empty():
            return _fail("INVALID_SOURCE_BONE_HIERARCHY")
        var rest: Transform3D = MotionPlayer._transform(row["rest"])
        skeleton.add_bone(str(row["name"]))
        skeleton.set_bone_parent(i, parent_index)
        skeleton.set_bone_rest(i, rest)
        skeleton.set_bone_pose(i, rest)
        var global_rest: Transform3D = rest_world[parent_index] * rest if parent_index >= 0 else rest
        rest_world.append(global_rest)
        bind.add_bind(i, global_rest.affine_inverse())
    if not motion_player.configure(skeleton, motion, pixels_per_metre):
        return _fail(str(motion_player.error))

    var positions := PackedVector3Array()
    var normals := PackedVector3Array()
    var coordinates := PackedVector2Array()
    positions.resize(vertex_count)
    normals.resize(vertex_count)
    coordinates.resize(vertex_count)
    for i in range(vertex_count):
        positions[i] = Vector3(points[i * 3], points[i * 3 + 1], points[i * 3 + 2])
        normals[i] = Vector3.BACK
        coordinates[i] = Vector2(surface["uv"][i * 2], surface["uv"][i * 2 + 1])
    var arrays: Array = []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX] = positions
    arrays[Mesh.ARRAY_NORMAL] = normals
    arrays[Mesh.ARRAY_TEX_UV] = coordinates
    arrays[Mesh.ARRAY_BONES] = PackedInt32Array(surface["bones"])
    arrays[Mesh.ARRAY_WEIGHTS] = PackedFloat32Array(surface["weights"])
    arrays[Mesh.ARRAY_INDEX] = PackedInt32Array(surface["indices"])
    var model := ArrayMesh.new()
    model.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
    var material := StandardMaterial3D.new()
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
    material.alpha_scissor_threshold = 0.5
    material.cull_mode = BaseMaterial3D.CULL_DISABLED
    material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
    material.alpha_antialiasing_mode = BaseMaterial3D.ALPHA_ANTIALIASING_ALPHA_TO_COVERAGE
    var filtered_source: Image = texture.get_image()
    if not filtered_source.has_mipmaps():
        filtered_source.generate_mipmaps()
    material.albedo_texture = ImageTexture.create_from_image(filtered_source)
    model.surface_set_material(0, material)
    mesh_instance = MeshInstance3D.new()
    mesh_instance.name = "OriginalSourceSkin"
    mesh_instance.mesh = model
    mesh_instance.skin = bind
    skeleton.add_child(mesh_instance)
    mesh_instance.skeleton = NodePath("..")
    return true

func _fail(message: String) -> bool:
    error = message
    for child in get_children():
        remove_child(child)
        child.free()
    skeleton = null
    mesh_instance = null
    motion_player = null
    return false
