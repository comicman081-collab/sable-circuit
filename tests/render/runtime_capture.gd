extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OUT_DIR := "res://artifacts/runtime_capture"
const REQUIRED_EVIDENCE: Array[String] = [
    "01_map_movement.png","02_combat_decon.png","03_boss_phase3.png",
    "19_direction_sector_7.png","24_death_boss.png"
]

var stage: StoryStage01
var camera: Camera2D
var camera_presentation: SquadCameraPresentation
var capture_failed := false

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    DisplayServer.window_set_size(Vector2i(1280, 720))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    stage = STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _settle(10)
    camera = stage.get_node("Camera2D") as Camera2D
    camera_presentation = stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    camera.enabled = true
    camera.position_smoothing_enabled = false
    stage.set_process(false)
    await _capture_movement()
    await _capture_combat()
    await _capture_boss_phase3()
    await _capture_all_rooms()
    await _capture_eight_directions()
    await _capture_unique_deaths()
    if capture_failed or not _verify_required_evidence():
        quit(1)
        return
    print("RUNTIME_CAPTURE: PASS")
    quit(0)

func _capture_movement() -> void:
    await _clear_enemies()
    stage.current_step = 0
    stage.call("_activate_step")
    _place_squad(Vector2(320,515), Vector2(0.98,-0.18))
    var active := stage.squad.get_active_operator()
    if active:
        active.debug_drive(Vector2(1.0,-1.0).normalized(), Vector2(0.98,-0.18))
    await _settle(11)
    _focus_live_camera()
    await _settle(1)
    await _save("01_map_movement.png")
    if active:
        active.debug_stop_drive()
    await _settle(2)

func _capture_combat() -> void:
    await _clear_enemies()
    stage.current_step = 1
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(1)
    _place_squad(Vector2(548,432), Vector2(0.98,-0.14))
    await _settle(22)
    var active := stage.squad.get_active_operator()
    if active:
        active.aim_world = Vector2(0.98,-0.14).normalized()
        active.debug_fire_once()
    _focus_live_camera()
    await _settle(1)
    await _save("02_combat_decon.png")

func _capture_boss_phase3() -> void:
    await _clear_enemies()
    stage.current_step = 4
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(4)
    _place_squad(Vector2(1710,610), Vector2(0.96,-0.28))
    await _settle(8)
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            node.health = node.max_health * 0.24
    await _settle(18)
    _focus_live_camera()
    await _settle(2)
    await _save("03_boss_phase3.png")

func _capture_all_rooms() -> void:
    await _clear_enemies()
    var rooms: Array = [
        ["04_room_outer_gate.png", Vector2(280,470),0],
        ["05_room_decon_corridor.png", Vector2(690,350),1],
        ["06_room_archive_annex.png", Vector2(1100,490),2],
        ["07_room_containment_junction.png", Vector2(1510,350),3],
        ["08_room_core_c.png", Vector2(1920,490),4],
        ["09_room_emergency_lift.png", Vector2(2330,350),5],
        ["10_room_emergency_stores.png", Vector2(1100,705),2],
        ["11_room_signal_lab.png", Vector2(1510,705),3]
    ]
    for row in rooms:
        var filename: String = str(row[0])
        var pos: Vector2 = row[1]
        stage.current_step = int(row[2])
        stage.call("_activate_step")
        _place_squad(pos + Vector2(-118,82), Vector2(0.98,-0.10))
        camera.global_position = pos
        await _settle(8)
        camera.global_position = pos
        await _settle(1)
        await _save(filename)

func _capture_eight_directions() -> void:
    await _clear_enemies()
    stage.current_step = 2
    stage.call("_activate_step")
    camera.global_position = Vector2(1100,490)
    var active := stage.squad.operators[0]
    stage.squad.request_control(0)
    stage.squad.operators[1].visible = false
    stage.squad.operators[2].visible = false
    active.global_position = Vector2(1100,515)
    var vectors: Array[Vector2] = [
        Vector2.RIGHT,Vector2(1,1).normalized(),Vector2.DOWN,Vector2(-1,1).normalized(),
        Vector2.LEFT,Vector2(-1,-1).normalized(),Vector2.UP,Vector2(1,-1).normalized()
    ]
    for sector in range(8):
        active.aim_world = vectors[sector]
        active.facing_sector = sector
        active.velocity = Vector2.ZERO
        await _settle(3)
        camera.global_position = Vector2(1100,490)
        await _save("%02d_direction_sector_%d.png" % [12+sector,sector])
    stage.squad.operators[1].visible = true
    stage.squad.operators[2].visible = true

func _capture_unique_deaths() -> void:
    await _clear_enemies()
    stage.current_step = 3
    stage.call("_activate_step")
    var ids: Array[String] = ["ENM_SITE7_RIFLE_01","ENM_SITE7_SHIELD_01","ENM_SITE7_DRONE_01","ENM_SITE7_ABERRANT_01","BOSS_SITE7_ANCHOR_01"]
    var names: Array[String] = ["rifle","shield","drone","aberrant","boss"]
    var camera_was_processing := false
    if camera_presentation != null:
        camera_was_processing = camera_presentation.is_processing()
        camera_presentation.set_process(false)
    for i in range(ids.size()):
        await _clear_enemies()
        var center := Vector2(1510,350)
        var death_origin := center + Vector2(72,0)
        camera.global_position = death_origin
        _place_squad(center+Vector2(-190,118),Vector2.RIGHT)
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(ids[i],300.0 if i==4 else 90.0)
        enemy.global_position = death_origin
        stage.add_child(enemy)
        await _settle(4)
        enemy.apply_damage(9999.0)
        var sequence := await _await_death_sequence(ids[i])
        if sequence == null:
            push_error("death evidence missing sequence for " + ids[i])
            capture_failed = true
            break
        if sequence.debug_piece_count() <= 0:
            push_error("death evidence has zero authored fragments for " + ids[i])
            capture_failed = true
            break
        var target_progress := 0.30 if i < 4 else 0.24
        var guard := 0
        while is_instance_valid(sequence) and sequence.debug_progress() < target_progress and guard < 60:
            camera.global_position = death_origin
            await process_frame
            guard += 1
        if not is_instance_valid(sequence) or sequence.debug_piece_count() <= 0:
            push_error("death evidence expired before capture for " + ids[i])
            capture_failed = true
            break
        camera.global_position = death_origin
        await _settle(1)
        camera.global_position = death_origin
        print("DEATH_EVIDENCE: %s mode=%s pieces=%d progress=%.3f" % [ids[i], sequence.debug_mode(), sequence.debug_piece_count(), sequence.debug_progress()])
        await _save("%02d_death_%s.png" % [20+i,names[i]])
    if camera_presentation != null:
        camera_presentation.set_process(camera_was_processing)

func _await_death_sequence(expected_id: String) -> EnemyDeathSequence:
    for _frame in range(18):
        for node in get_nodes_in_group("enemy_death_sequences"):
            if node is EnemyDeathSequence and node.enemy_id == expected_id:
                return node as EnemyDeathSequence
        await process_frame
    return null

func _place_squad(center: Vector2, aim: Vector2) -> void:
    var aim_dir := aim.normalized() if aim.length_squared() > 0.001 else Vector2.RIGHT
    var side := Vector2(-aim_dir.y,aim_dir.x)
    var rear := -aim_dir
    # Match the real M7 live echelon exactly.
    var positions: Array[Vector2] = [
        center,
        center+rear*82.0+side*72.0,
        center+rear*118.0-side*48.0
    ]
    for i in range(stage.squad.operators.size()):
        var actor := stage.squad.operators[i]
        actor.global_position = positions[i]
        actor.aim_world = aim_dir
        actor.facing_sector = actor.call("_sector_from_vector", aim_dir)
        actor.velocity = Vector2.ZERO

func _focus_live_camera() -> void:
    if camera_presentation != null:
        camera.global_position = camera_presentation.debug_target_for_active()
    elif stage.squad.get_active_operator() != null:
        camera.global_position = stage.squad.get_active_operator().global_position

func _clear_enemies() -> void:
    for node in get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node): node.queue_free()
    for node in get_nodes_in_group("enemy_death_sequences"):
        if is_instance_valid(node): node.queue_free()
    await process_frame
    await process_frame

func _settle(frames: int) -> void:
    for _i in range(frames): await process_frame

func _save(filename: String) -> void:
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    var path := ProjectSettings.globalize_path(OUT_DIR + "/" + filename)
    var err := image.save_png(path)
    if err != OK:
        push_error("capture failed: " + path + " err=" + str(err))
        capture_failed = true
        return
    print("CAPTURED: " + path)

func _verify_required_evidence() -> bool:
    for filename in REQUIRED_EVIDENCE:
        var path := ProjectSettings.globalize_path(OUT_DIR + "/" + filename)
        if not FileAccess.file_exists(path):
            push_error("missing required runtime evidence: " + filename)
            return false
    return true
