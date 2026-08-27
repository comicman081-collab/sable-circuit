extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(6)

    var lighting := stage.get_node_or_null("LightingRig") as Site7LightingRig
    _check(lighting != null and lighting.debug_light_count() == 8, "M6 owns eight authored semantic light sockets")
    _check(lighting != null and lighting.debug_additive_wash_disabled(), "M6 disables Compatibility additive wash")

    var architecture := stage.get_node_or_null("FacilityArchitecture") as Site7FacilityArchitecture
    _check(architecture != null and architecture.debug_connected_deck(), "M6 uses a connected Site-7 deck")
    _check(architecture != null and architecture.debug_diagonal_route(), "M6 main route alternates through diagonal deck segments")

    var room_art := stage.get_node_or_null("RoomArtLayer") as Site7RoomArtLayer
    _check(room_art != null and room_art.debug_asset_count() == 8 and room_art.debug_all_assets_loaded(), "eight unique room SVGs load")
    var prop_art := stage.get_node_or_null("PropArtLayer") as Site7PropArtLayer
    _check(prop_art != null and prop_art.debug_asset_count() == 8 and prop_art.debug_all_assets_loaded(), "eight unique room prop SVGs load")

    _check(stage.hud != null and stage.hud.debug_uses_unique_portraits(), "HUD keeps three dedicated portraits")
    _check(stage.hud != null and stage.hud.debug_uses_unique_hud_art(), "HUD keeps unique weapon/action SVGs")
    _check(stage.hud != null and stage.hud.debug_hud_art_loaded(), "active HUD art loads")

    var detail_paths: Dictionary = {}
    for actor in stage.squad.operators:
        var detail := actor.get_node_or_null("DetailOverlayPresentation") as OperatorDetailOverlayPresentation
        _check(detail != null and detail.debug_loaded(), actor.display_name + " detail overlay loads on 15+ articulated parts")
        if detail:
            _check(detail.debug_overlay_count() >= 15, actor.display_name + " has 15+ detail overlay layers")
            var path := detail.debug_source_path()
            _check(not path.is_empty(), actor.display_name + " detail overlay path exists")
            _check(not detail_paths.has(path), actor.display_name + " detail overlay path is unique")
            detail_paths[path] = true
    _check(detail_paths.size() == 3, "three playable detail overlay assets are unique")

    var formation: Dictionary = stage.squad.debug_formation_contract()
    _check(bool(formation.get("compact", false)), "M6 uses compact three-person echelon")

    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    _check(camera_presentation != null, "aim-aware gameplay camera is attached")
    if camera_presentation:
        var camera_contract := camera_presentation.debug_camera_contract()
        _check(float(camera_contract.get("aim_look_ahead_x",0.0)) >= 80.0, "camera reserves forward combat space")
        _check(bool(camera_contract.get("player_lower_screen_bias",false)), "camera targets lower-screen squad composition")

    var marker_contract := stage.debug_progress_marker_contract()
    _check(bool(marker_contract.get("giant_room_circles_forbidden",false)), "giant prototype room circles are forbidden")
    _check(bool(marker_contract.get("active_arc_removed",false)), "active room circular arc is removed")

    var active := stage.squad.operators[0] as OperatorActor
    stage.squad.request_control(0)
    active.set_movement_bounds(Rect2(100,100,2400,900))
    active.global_position = Vector2(620,480)
    active.aim_world = Vector2.RIGHT
    var start := active.global_position
    active.debug_drive(Vector2(1,-1).normalized(), Vector2.RIGHT)
    await _physics_frames(12)
    var travel := active.global_position - start
    _check(travel.x > 6.0 and travel.y < -6.0, "simultaneous axes produce real diagonal travel")
    _check(absf(absf(travel.x)-absf(travel.y)) < maxf(4.0,travel.length()*0.12), "diagonal travel stays normalized")
    _check(active.aim_world.dot(Vector2.RIGHT) > 0.98, "aim remains independent while moving diagonally")

    var diagonal := active.get_node_or_null("DiagonalLocomotionPresentation") as DiagonalLocomotionPresentation
    if diagonal:
        var contract := diagonal.debug_locomotion_contract()
        _check(bool(contract.get("screen_diagonal",false)), "lower body resolves diagonal movement")
        _check(bool(contract.get("pelvis_rotation_forbidden",false)), "diagonal locomotion never rotates pelvis/root")
    else:
        _check(false, "diagonal locomotion presentation exists")

    var upright := active.get_node_or_null("UprightStancePresentation") as UprightStancePresentation
    _check(upright != null and upright.debug_body_axis_locked(), "pelvis/body axis stays upright")
    var ik := active.get_node_or_null("OperatorWeaponIK") as OperatorWeaponIK
    _check(ik != null and ik.debug_connected(), "both arms solve to authoritative weapon")
    var shading := active.get_node_or_null("PremiumSpriteShading") as PremiumSpriteShading
    _check(shading != null and shading.debug_premium_volume_contract(), "operator uses premium volume/soft-ink shading")
    active.debug_stop_drive()

    var boss_projectile := PrototypeProjectile.new()
    _check(boss_projectile.debug_anchor_visual_width() <= 10.0, "Phase 3 anchor lance stays visually restrained")
    boss_projectile.free()

    stage.debug_spawn_encounter_for_step(1)
    await _frames(5)
    var enemy_count := 0
    var scaled_count := 0
    var shaded_count := 0
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            enemy_count += 1
            var scale_layer := node.get_node_or_null("FieldScalePresentation") as EnemyFieldScalePresentation
            if scale_layer != null and scale_layer.debug_scaled_for_field(): scaled_count += 1
            var enemy_shading := node.get_node_or_null("PremiumSpriteShading") as PremiumSpriteShading
            if enemy_shading != null and enemy_shading.debug_premium_volume_contract(): shaded_count += 1
    _check(enemy_count >= 3, "Decon keeps unique enemy composition")
    _check(scaled_count == enemy_count, "all spawned enemies use corrected field scale")
    _check(shaded_count == enemy_count, "all spawned enemies use premium volume shading")

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
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
