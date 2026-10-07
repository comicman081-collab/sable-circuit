extends Node2D
class_name SourceSkinViewport
## One reviewed view rendered from its real skeleton at supersampled resolution.
## Direction selection and the complete movement/aim matrix belong to the actor.
const SkinView = preload("res://scripts/animation/source_skin_view.gd")
const WeaponBinding = preload("res://scripts/animation/source_skin_weapon_binding.gd")
const SourceProjection = preload("res://scripts/animation/source_projection.gd")

var view: Node3D
var camera: Camera3D
var viewport: SubViewport
var display: Sprite2D
var weapon = WeaponBinding.new()
var error := ""
var _display_pixels_per_metre := 128.0

func configure(surface: Dictionary, motion: Dictionary, texture: Texture2D,
        world_pixels_per_metre: float) -> bool:
    clear()
    error = ""
    if not is_finite(world_pixels_per_metre) or world_pixels_per_metre <= 0:
        error = "POSITIVE_DISPLAY_SCALE_REQUIRED"
        return false
    # The same scale controls visible feet and displacement-driven gait phase.
    # Separate presentation/motion units would introduce systematic foot sliding.
    var display_pixels_per_metre := world_pixels_per_metre
    if surface.get("authored_projection") != motion.get("authored_projection"):
        error = "EXACT_SKIN_AND_MOTION_PROJECTION_REQUIRED"
        return false
    var projection: Dictionary = SourceProjection.resolve(surface.get("authored_projection"))
    if projection.is_empty():
        error = "INVALID_AUTHORED_SOURCE_PROJECTION"
        return false
    _display_pixels_per_metre = world_pixels_per_metre
    viewport = SubViewport.new()
    viewport.name = "SourceSkinRender"
    viewport.size = Vector2i(1024, 1024)
    viewport.transparent_bg = true
    viewport.own_world_3d = true
    viewport.msaa_3d = Viewport.MSAA_4X
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    add_child(viewport)
    view = SkinView.new()
    viewport.add_child(view)
    if not view.configure(surface, motion, texture, world_pixels_per_metre):
        error = str(view.error)
        clear()
        return false
    camera = Camera3D.new()
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    camera.size = float(projection["size"])
    camera.near = 0.1
    camera.far = 12.0
    # Source view already determines visible facing. Moving this camera with
    # the skeleton's world heading preserves that view instead of rotating art
    # edge-on. Actual pose/deformation remains visible relative to the camera.
    view.motion_player.add_child(camera)
    var camera_center := Vector3(0, float(projection["center_height"]), 0)
    camera.transform = Transform3D(Basis.looking_at(projection["forward"], projection["up"]),
        camera_center - projection["forward"] * 6.0)
    camera.current = true
    display = Sprite2D.new()
    display.name = "OriginalArtDisplay"
    display.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    display.texture = viewport.get_texture()
    var render_scale := camera.size * display_pixels_per_metre / 1024.0
    display.scale = Vector2.ONE * render_scale
    display.position.y = -float(projection["screen_center_height"]) * display_pixels_per_metre
    add_child(display)
    if surface.has("weapon_binding"):
        if not weapon.configure(view.skeleton, surface["weapon_binding"]):
            error = str(weapon.error)
            clear()
            return false
    return true

func current_muzzle_position() -> Variant:
    var launch := current_launch_2d()
    return null if launch.is_empty() else launch["origin"]

func configure_coherent_recoil(angle_radians: float, distance_metres: float) -> bool:
    if view == null or not is_finite(angle_radians) or not is_finite(distance_metres) or distance_metres < 0:
        error = "VALID_CHARACTER_RECOIL_CALIBRATION_REQUIRED"
        return false
    var launch: Dictionary = weapon.current_launch()
    if launch.is_empty():
        error = "ACTUAL_WEAPON_BINDING_REQUIRED_FOR_RECOIL"
        return false
    var direction: Vector3 = launch["direction"]
    var camera_right := camera.global_basis.x
    var camera_up := camera.global_basis.y
    var image_direction := camera_right * direction.dot(camera_right) + camera_up * direction.dot(camera_up)
    if image_direction.length_squared() < 0.000001:
        error = "VISIBLE_BARREL_PROJECTION_REQUIRED"
        return false
    image_direction = image_direction.normalized()
    var motion: Dictionary = view.motion_player.pack
    var spine_name: String = motion["humanoid_roles"]["spine"]
    var index: int = view.skeleton.find_bone(spine_name)
    var inverse_basis: Basis = (view.skeleton.global_basis * view.skeleton.get_bone_global_rest(index).basis).inverse()
    var local_axis := (inverse_basis * camera.global_basis.z).normalized()
    var horizontal := image_direction.dot(camera_right)
    var direction_sign := signf(horizontal) if absf(horizontal) > 0.1 else 0.0
    var rotation_offset := Quaternion(local_axis, angle_radians * direction_sign)
    var translation_offset: Vector3 = inverse_basis * (-image_direction * distance_metres)
    var names: Array[String] = [spine_name]
    return view.motion_player.configure_upper_body(names, [motion["bone_order"][index]["rest"]],
        rotation_offset, true, translation_offset)

func current_launch_2d() -> Dictionary:
    var launch: Dictionary = weapon.current_launch()
    if launch.is_empty() or camera == null or display == null:
        return {}
    var pixel: Vector2 = camera.unproject_position(launch["origin"])
    var rear_pixel: Vector2 = camera.unproject_position(launch["origin"] - launch["direction"] * 0.1)
    var origin := display.to_global(pixel - Vector2(viewport.size) * 0.5)
    var rear := display.to_global(rear_pixel - Vector2(viewport.size) * 0.5)
    if origin.distance_squared_to(rear) < 0.000001:
        return {}
    return {"origin": origin, "direction": (origin-rear).normalized()}

func set_render_active(active: bool) -> void:
    visible = active
    if viewport != null:
        viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS if active else SubViewport.UPDATE_DISABLED

func clear() -> void:
    weapon = WeaponBinding.new()
    for child in get_children():
        remove_child(child)
        child.free()
    view = null
    camera = null
    viewport = null
    display = null
