extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(5)

    var lighting := stage.get_node_or_null("LightingRig") as Site7LightingRig
    _check(lighting != null and lighting.debug_light_count() == 8, "M6 owns eight authored semantic light sockets")
    _check(lighting != null and lighting.debug_additive_wash_disabled(), "M6 disables Compatibility additive wash")

    var architecture := stage.get_node_or_null("FacilityArchitecture") as Site7FacilityArchitecture
    _check(architecture != null and architecture.debug_connected_deck(), "M6 uses a connected Site-7 deck")
    _check(architecture != null and architecture.debug_diagonal_route(), "M6 main route alternates through real diagonal deck segments")

    var room_art := stage.get_node_or_null("RoomArtLayer") as Site7RoomArtLayer
    _check(room_art != null and room_art.debug_asset_count() == 8, "M6 loads eight authored room-specific SVG art assets")
    _check(room_art != null and room_art.debug_unique_asset_count() == 8, "M6 room art paths are all unique")
    _check(room_art != null and room_art.debug_all_assets_loaded(), "all eight room SVGs import and render")

    var prop_art := stage.get_node_or_null("PropArtLayer") as Site7PropArtLayer
    _check(prop_art != null and prop_art.debug_asset_count() == 8, "M6 loads eight room-specific environment prop SVGs")
    _check(prop_art != null and prop_art.debug_unique_asset_count() == 8, "M6 prop art paths are all unique")
    _check(prop_art != null and prop_art.debug_all_assets_loaded(), "all eight environment prop SVGs import and render")

    var surface := stage.get_node_or_null("SurfaceDetail") as Site7SurfaceDetail
    _check(surface != null and surface.debug_surface_count() == 8, "M6 retains eight unique high-density room surfaces")
    var depth := stage.get_node_or_null("DepthPass") as Site7DepthPass
    _check(depth != null and depth.debug_diagonal_depth(), "M6 depth pass follows the diagonal facility route")

    var minimap: TacticalMinimap = null
    if stage.hud != null:
        minimap = stage.hud.get("_minimap") as TacticalMinimap
    _check(minimap != null and minimap.debug_diagonal_route(), "HUD minimap renders the spatial diagonal route")
    _check(stage.hud != null and stage.hud.debug_uses_unique_portraits(), "HUD keeps three dedicated operator portraits")
    _check(stage.hud != null and stage.hud.debug_uses_unique_hud_art(), "HUD has twelve unique weapon/action SVG assets")
    _check(stage.hud != null and stage.hud.debug_hud_art_loaded(), "active weapon and three action icons load")

    var formation: Dictionary = stage.squad.debug_formation_contract()
    _check(bool(formation.get("compact", false)), "M6 live squad uses compact three-person echelon")
    _check(float(formation.get("side", 999.0)) <= 60.0, "M6 followers stay readable without drifting off-frame")

    var camera := stage.get_node_or_null("Camera2D") as Camera2D
    _check(camera != null and camera.zoom.x >= 1.40, "M6 camera keeps premium room-focused framing")
    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    _check(camera_presentation != null, "M6 gameplay camera presentation is attached")
    if camera_presentation:
        var camera_contract := camera_presentation.debug_camera_contract()
        _check(float(camera_contract.get("aim_look_ahead_x",0.0)) >= 80.0, "camera reserves forward combat space along aim")
        _check(float(camera_contract.get("vertical_safe_bias",0.0)) >= 16.0, "camera keeps squad above the lower HUD safe area")
        _check(bool(camera_contract.get("compact_squad_safe",false)), "camera contract preserves all three compact squad members")

    var marker_contract := stage.debug_progress_marker_contract()
    _check(bool(marker_contract.get("giant_room_circles_forbidden",false)), "prototype giant room progress circles are forbidden")
    _check(float(marker_contract.get("active_radius",999.0)) <= 30.0, "active room marker is a small floor cue")
    _check(float(marker_contract.get("optional_radius",999.0)) <= 16.0, "optional room marker stays unobtrusive")

    var active := stage.squad.operators[0] as OperatorActor
    var visual_root := active.get_node_or_null("VisualRoot") as Node2D
    _check(visual_root != null and visual_root.scale.x <= 0.74, "operator field scale leaves room for environment readability")
    stage.squad.request_control(0)
    active.set_movement_bounds(Rect2(100,100,2400,900))
    active.global_position = Vector2(620,480)
    active.aim_world = Vector2.RIGHT
    var start := active.global_position
    active.debug_drive(Vector2(1,-1).normalized(),Vector2.RIGHT)
    await _physics_frames(12)
    var travel := active.global_position-start
    _check(travel.x > 6.0 and travel.y < -6.0, "simultaneous axes produce real diagonal travel")
    _check(absf(absf(travel.x)-absf(travel.y)) < maxf(4.0,travel.length()*0.12), "diagonal vector stays normalized")
    _check(active.aim_world.dot(Vector2.RIGHT) > 0.98, "aim remains independent during diagonal travel")

    var diagonal := active.get_node_or_null("DiagonalLocomotionPresentation") as DiagonalLocomotionPresentation
    _check(diagonal != null, "diagonal locomotion presentation is attached")
    if diagonal:
        var contract := diagonal.debug_locomotion_contract()
        _check(bool(contract.get("screen_diagonal",false)), "lower body resolves diagonal movement")
        _check(absf(float(contract.get("forward",0.0))) > 0.45 and absf(float(contract.get("strafe",0.0))) > 0.45, "diagonal locomotion blends forward and strafe")
        _check(bool(contract.get("pelvis_rotation_forbidden",false)), "diagonal locomotion never rotates pelvis/root")

    var upright := active.get_node_or_null("UprightStancePresentation") as UprightStancePresentation
    _check(upright != null and upright.debug_body_axis_locked(), "pelvis body axis stays upright")
    var ik := active.get_node_or_null("OperatorWeaponIK") as OperatorWeaponIK
    _check(ik != null and ik.debug_connected(), "both arms solve to authoritative weapon")
    var shading := active.get_node_or_null("PremiumSpriteShading") as PremiumSpriteShading
    _check(shading != null and shading.debug_bound(), "operator high-resolution rig keeps premium shading")
    _check(shading != null and shading.debug_premium_volume_contract(), "operator material uses key light, AO, bounce, sheen and softened ink")
    active.debug_stop_drive()

    stage.debug_spawn_encounter_for_step(1)
    await _frames(5)
    var enemy_count := 0
    var scaled_enemy_count := 0
    var shaded_enemy_count := 0
    var volume_enemy_count := 0
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            enemy_count += 1
            var scale_layer := node.get_node_or_null("FieldScalePresentation") as EnemyFieldScalePresentation
            if scale_layer != null and scale_layer.debug_scaled_for_field(): scaled_enemy_count += 1
            var enemy_shading := node.get_node_or_null("PremiumSpriteShading") as PremiumSpriteShading
            if enemy_shading != null and enemy_shading.debug_bound(): shaded_enemy_count += 1
            if enemy_shading != null and enemy_shading.debug_premium_volume_contract(): volume_enemy_count += 1
    _check(enemy_count >= 3, "Decon still spawns its unique enemy composition")
    _check(scaled_enemy_count == enemy_count, "all normal enemies use corrected field scale")
    _check(shaded_enemy_count == enemy_count, "all enemies keep premium render pipeline")
    _check(volume_enemy_count == enemy_count, "all enemies receive volumetric shader system without sharing final art")

    stage.queue_free()
    await process_frame
    if failures.is_empty():
        print("M6_TARGET_STYLE_SMOKE: PASS")
        quit(0)
        return
    print("M6_TARGET_STYLE_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _frames(count: int) -> void:
    for _i in range(count): await process_frame

func _physics_frames(count: int) -> void:
    for _i in range(count): await physics_frame

func _check(condition: bool, label: String) -> void:
    if condition: print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
