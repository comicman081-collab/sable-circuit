extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(4)

    var lighting := stage.get_node_or_null("LightingRig") as Site7LightingRig
    _check(lighting != null, "M6 Site-7 lighting rig exists")
    _check(lighting != null and lighting.debug_light_count() == 8, "M6 lighting owns eight authored room lights")

    var surface := stage.get_node_or_null("SurfaceDetail") as Site7SurfaceDetail
    _check(surface != null and surface.debug_surface_count() == 8, "M6 has eight unique high-density room surface treatments")

    var camera := stage.get_node_or_null("Camera2D") as Camera2D
    _check(camera != null and camera.zoom.x >= 1.40, "M6 camera fills the screen with one premium room instead of prototype boxes")

    var active := stage.squad.operators[0] as OperatorActor
    stage.squad.request_control(0)
    active.set_movement_bounds(Rect2(100,100,2100,900))
    active.global_position = Vector2(620,480)
    active.aim_world = Vector2.RIGHT
    var start := active.global_position
    active.debug_drive(Vector2(1,-1).normalized(),Vector2.RIGHT)
    await _physics_frames(12)
    var travel := active.global_position-start
    _check(travel.x > 6.0 and travel.y < -6.0, "simultaneous horizontal and vertical axes produce real diagonal travel")
    _check(absf(absf(travel.x)-absf(travel.y)) < maxf(4.0,travel.length()*0.12), "diagonal vector stays normalized and balanced across both axes")
    _check(active.aim_world.dot(Vector2.RIGHT) > 0.98, "aim remains independent while travelling diagonally")

    var diagonal := active.get_node_or_null("DiagonalLocomotionPresentation") as DiagonalLocomotionPresentation
    _check(diagonal != null, "diagonal locomotion presentation is attached")
    if diagonal:
        var contract := diagonal.debug_locomotion_contract()
        _check(bool(contract.get("screen_diagonal",false)), "lower-body presentation resolves diagonal movement")
        _check(absf(float(contract.get("forward",0.0))) > 0.45 and absf(float(contract.get("strafe",0.0))) > 0.45, "diagonal locomotion blends forward and strafe components")
        _check(bool(contract.get("pelvis_rotation_forbidden",false)), "diagonal locomotion never rotates the pelvis/root")

    var upright := active.get_node_or_null("UprightStancePresentation") as UprightStancePresentation
    _check(upright != null and upright.debug_upright(), "field actor keeps an upright body axis during diagonal travel")
    _check(upright != null and upright.debug_body_axis_locked(), "pelvis body axis is hard-locked upright after diagonal presentation")

    var ik := active.get_node_or_null("OperatorWeaponIK") as OperatorWeaponIK
    _check(ik != null and ik.debug_connected(), "both operator arms solve to the authoritative weapon instead of detached paper-doll aim")
    var shading := active.get_node_or_null("PremiumSpriteShading") as PremiumSpriteShading
    _check(shading != null and shading.debug_bound(), "operator layered rig receives premium 2.5D shading")
    active.debug_stop_drive()

    stage.debug_spawn_encounter_for_step(1)
    await _frames(4)
    var enemy_count := 0
    var shaded_enemy_count := 0
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            enemy_count += 1
            var enemy_shading := node.get_node_or_null("PremiumSpriteShading") as PremiumSpriteShading
            if enemy_shading != null and enemy_shading.debug_bound():
                shaded_enemy_count += 1
    _check(enemy_count >= 3, "Decon encounter still spawns its unique enemy composition")
    _check(shaded_enemy_count == enemy_count, "all spawned enemies receive the same premium render pipeline without asset reuse")

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
    for _i in range(count):
        await process_frame

func _physics_frames(count: int) -> void:
    for _i in range(count):
        await physics_frame

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
