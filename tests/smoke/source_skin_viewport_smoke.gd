extends SceneTree
const SourceViewport = preload("res://scripts/animation/source_skin_viewport.gd")

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var surface: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://SOURCE_SKIN.json"))
    var motion: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://MOTION_PACK.json"))
    var texture := ImageTexture.create_from_image(Image.load_from_file("res://SOURCE_RGBA.png"))
    var node = SourceViewport.new()
    root.add_child(node)
    var failures: Array[String] = []
    if not node.configure(surface, motion, texture, 128.0):
        failures.append(str(node.error))
    else:
        if node.viewport.size != Vector2i(1024, 1024) or node.viewport.msaa_3d != Viewport.MSAA_4X:
            failures.append("supersampling or multisampling missing")
        if node.camera.get_parent() != node.view.motion_player:
            failures.append("camera not bound to authored direction view")
        if surface.has("weapon_binding"):
            if not node.configure_coherent_recoil(0.018, 0.012):
                failures.append("actual weapon recoil failed: " + str(node.error))
            node.view.motion_player.set_motion_intent(Vector2.RIGHT, true)
            if not node.view.motion_player.commit_displacement(Vector2(3.0, 0), Vector2.RIGHT, 1.0 / 60.0, true):
                failures.append("actual forward gait and upper binding failed")
            var gait_phase: float = node.view.motion_player.phase
            var foot_index: int = node.view.skeleton.find_bone("foot_l")
            var foot_before: Transform3D = node.view.skeleton.get_bone_global_pose(foot_index)
            var before: Dictionary = node.current_launch_2d()
            if before.is_empty():
                failures.append("armed source missing projected barrel")
            else:
                var immutable_origin: Vector2 = before["origin"]
                node.view.motion_player.trigger_recoil()
                var after: Dictionary = node.current_launch_2d()
                if node.view.motion_player.phase != gait_phase or not node.view.skeleton.get_bone_global_pose(foot_index).is_equal_approx(foot_before):
                    failures.append("fire changed committed lower gait or foot")
                if after.is_empty() or after["origin"].distance_to(immutable_origin) < 0.01:
                    failures.append("same-phase recoil did not move visible barrel")
                if before["origin"] != immutable_origin:
                    failures.append("previous launch snapshot mutated")
                if not after.is_empty() and absf(after["direction"].length() - 1.0) > 0.0001:
                    failures.append("projected barrel direction not normalized")
        elif node.current_muzzle_position() != null:
            failures.append("unarmed source invented a muzzle")
        node.set_render_active(false)
        if node.visible or node.viewport.render_target_update_mode != SubViewport.UPDATE_DISABLED:
            failures.append("inactive view continues rendering")
    node.clear()
    if node.get_child_count() != 0:
        failures.append("partial renderer not released")
    node.free()
    _projection_checks(surface,motion,texture,failures)
    var file := FileAccess.open("res://RESULT.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"failures": failures, "production_ready": false,
        "scope": "actual source skin and viewport wiring only; no GPU visual or combat claim"}, "  "))
    file.close()
    quit(0 if failures.is_empty() else 1)

func _projection_checks(source: Dictionary, original: Dictionary, texture: Texture2D, failures: Array[String]) -> void:
    # Explicit consumer fixture; old geometry is not a new approved MICA binding.
    var surface := source.duplicate(true)
    var motion := original.duplicate(true)
    var projection := {"schema":1,"kind":"source_orthographic_elevation",
        "elevation_degrees":30.0,"camera_center_height_m":0.875,
        "orthographic_size_m":2.0*cos(PI/6.0)}
    surface["authored_projection"] = projection
    motion["authored_projection"] = projection.duplicate(true)
    var node = SourceViewport.new()
    root.add_child(node)
    if not node.configure(surface,motion,texture,128.0):
        failures.append("projected configure: "+str(node.error))
        node.free()
        return
    var expected_forward := Vector3(0,-0.5,-sqrt(3.0)/2.0)
    if (-node.camera.basis.z).distance_to(expected_forward) > 0.000001:
        failures.append("projected camera basis wrong")
    var ground_pixel: Vector2 = node.camera.unproject_position(Vector3.ZERO)
    var ground_display: Vector2 = node.display.to_global(ground_pixel-Vector2(512,512))
    if ground_display.length() > 0.001:
        failures.append("projected neutral origin not at actor ground")
    for pair in [[Vector3.RIGHT,Vector2(128,0)],[Vector3.BACK,Vector2(0,64)]]:
        var pixel: Vector2 = node.camera.unproject_position(pair[0])
        var delta: Vector2 = node.display.to_global(pixel-Vector2(512,512))-ground_display
        if delta.distance_to(pair[1]) > 0.001:
            failures.append("projected one metre display mismatch")
    if surface.has("weapon_binding"):
        if not node.configure_coherent_recoil(0.018,0.012):
            failures.append("projected recoil binding failed")
        var player = node.view.motion_player
        if not player.commit_displacement(Vector2(3,0),Vector2.RIGHT,1.0/60.0,true):
            failures.append("projected gait commit failed")
        var phase: float = player.phase
        var foot: int = node.view.skeleton.find_bone("foot_l")
        var foot_before: Transform3D = node.view.skeleton.get_bone_global_pose(foot)
        var before: Dictionary = node.current_launch_2d()
        player.trigger_recoil()
        var after: Dictionary = node.current_launch_2d()
        if before.is_empty() or after.is_empty():
            failures.append("projected weapon launch missing")
        elif before["origin"].distance_to(after["origin"]) < 0.01:
            failures.append("projected same phase recoil did not move barrel")
        if phase != player.phase or not foot_before.is_equal_approx(node.view.skeleton.get_bone_global_pose(foot)):
            failures.append("projected recoil changed lower gait")
    motion["authored_projection"]["elevation_degrees"] = 40.0
    if node.configure(surface,motion,texture,128.0) or node.error != "EXACT_SKIN_AND_MOTION_PROJECTION_REQUIRED":
        failures.append("mismatched projection accepted")
    node.free()
