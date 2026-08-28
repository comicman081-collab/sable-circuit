extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const CORE_CENTER := Vector2(1920.0, 490.0)
var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(8)

    var room_art := stage.get_node_or_null("RoomArtLayer") as Site7RoomArtLayer
    _check(room_art != null and room_art.debug_asset_count() == 8 and room_art.debug_all_assets_loaded(), "M7 loads eight expanded room art plates")

    var formation := stage.squad.debug_formation_contract()
    _check(bool(formation.get("m7_echelon", false)), "M7 widened triangular echelon is authoritative")
    _check(bool(formation.get("open_aim_lane", false)), "M7 echelon reserves the firing lane")
    _check(float(formation.get("rear_b", 0.0)) >= 110.0, "M7 rear operator separation is expanded")

    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    _check(camera_presentation != null, "M7 target-aware camera exists")
    if camera_presentation:
        var camera_contract := camera_presentation.debug_camera_contract()
        _check(bool(camera_contract.get("m7_camera", false)), "M7 camera contract is active")
        _check(bool(camera_contract.get("target_aware_combat_frame", false)), "camera frames actual hostile group")
        _check(float(camera_contract.get("combat_target_weight", 0.0)) >= 0.35, "camera reserves enemy-side screen space")

    var boss_arena := stage.get_node_or_null("BossArenaPresentation") as BossArenaPresentation
    _check(boss_arena != null, "Core C has dedicated boss arena presentation")
    if boss_arena:
        var arena_contract := boss_arena.debug_contract()
        _check(int(arena_contract.get("pylon_count",0)) == 4, "Core C owns four authored pylon anchors")
        _check(int(arena_contract.get("phase1_active_pylons",-1)) == 0, "Phase 1 pylons stay dormant")
        _check(int(arena_contract.get("phase2_active_pylons",0)) == 2, "Phase 2 activates two opposing pylons")
        _check(int(arena_contract.get("phase3_active_pylons",0)) == 4, "Phase 3 activates all four pylons")
        _check(int(arena_contract.get("phase3_wedges",0)) == 4, "Phase 3 uses four readable arena wedges")
        _check(bool(arena_contract.get("weakpoint_exposed_phase3",false)), "Phase 3 exposes the authored weakpoint core")
        _check(bool(arena_contract.get("phase3_body_clear",false)), "Phase 3 keeps the boss body readable")
        _check(bool(arena_contract.get("clear_movement_gaps",false)), "Phase 3 preserves movement gaps")

    stage.current_step = 4
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(4)
    await _frames(6)
    var boss: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            boss = node
            break
    _check(boss != null, "M7 boss spawns in Core C")
    if boss:
        _check(boss.global_position.distance_to(CORE_CENTER) < 2.0, "boss body is centered on the authored Core C dais")
        boss.health = boss.max_health * 0.24
        await _frames(6)
        var premium := boss.get_node_or_null("PremiumPresentation") as PremiumEnemyPresentation
        _check(premium != null and premium.debug_phase() == 3, "M7 boss reaches Phase 3")
        if premium:
            var phase_contract := premium.debug_m7_phase_contract()
            _check(int(phase_contract.get("phase3_burst",0)) == 5, "Phase 3 keeps five separated lanes")
            _check(bool(phase_contract.get("body_clear",false)), "Phase 3 body remains visually readable")
        _check(boss_arena != null and boss_arena.debug_phase() == 3, "boss arena follows boss into Phase 3")
        _check(boss_arena != null and boss_arena.debug_active_pylon_count() == 4, "Phase 3 runtime has four active pylons")
        _check(boss_arena != null and boss_arena.debug_weakpoint_exposed(), "Phase 3 runtime exposes the weakpoint")

    var active := stage.squad.get_active_operator()
    if active:
        active.set_movement_bounds(Rect2(100,100,2500,1000))
        active.global_position = Vector2(540,520)
        var start := active.global_position
        active.debug_drive(Vector2(1,-1).normalized(), Vector2.RIGHT)
        await _physics_frames(10)
        var travel := active.global_position-start
        _check(travel.x > 5.0 and travel.y < -5.0, "M7 preserves true diagonal movement")
        _check(active.aim_world.dot(Vector2.RIGHT) > 0.98, "M7 preserves independent aim")
        active.debug_stop_drive()

    stage.queue_free()
    await process_frame
    if failures.is_empty():
        print("M7_AUTHORED_VISUAL_SMOKE: PASS")
        quit(0)
        return
    print("M7_AUTHORED_VISUAL_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _frames(count:int) -> void:
    for _i in range(count): await process_frame

func _physics_frames(count:int) -> void:
    for _i in range(count): await physics_frame

func _check(condition:bool,label:String) -> void:
    if condition:
        print("PASS: "+label)
    else:
        failures.append(label)
        push_error("FAIL: "+label)
