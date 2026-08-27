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
    camera.enabled = true
    camera.position_smoothing_enabled = false
    stage.set_process(false)
    await _capture_movement()
    await _capture_combat()
    await _capture_boss_phase3()
    await _capture_all_rooms()
    await _capture_eight_directions()
    await _capture_unique_deaths()
    if not _verify_required_evidence():
        quit(1)
        return
    print("RUNTIME_CAPTURE: PASS")
    quit(0)

func _capture_movement() -> void:
    await _clear_enemies()
    stage.current_step = 0
    stage.call("_activate_step")
    _place_squad(Vector2(320,515), Vector2(0.98,-0.18))
    camera.global_position = Vector2(300,470)
    var active := stage.squad.get_active_operator()
    if active:
        # M6 evidence is captured while the actor is actually travelling diagonally
        active.debug_drive(Vector2(1.0,-1.0).normalized(), Vector2(0.98,-0.18))
    await _settle(11)
    camera.global_position = Vector2(300,470)
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
    camera.global_position = Vector2(690,350)
    await _settle(22)
    var active := stage.squad.get_active_operator()
    if active:
        active.aim_world = Vector2(0.98,-0.14).normalized()
        active.debug_fire_once()
    camera.global_position = Vector2(690,350)
    await _settle(1)
    await _save("02_combat_decon.png")

func _capture_boss_phase3() -> void:
    await _clear_enemies()
    stage.current_step = 4
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(4)
    _place_squad(Vector2(1740,575), Vector2(0.96,-0.28))
    camera.global_position = Vector2(1920,490)
    await _settle(8)
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            node.health = node.max_health * 0.24
    await _settle(18)
    camera.global_position = Vector2(1920,490)
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
        _place_squad(pos + Vector2(-96,68), Vector2(0.98,-0.10))
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
    for i in range(ids.size()):
        await _clear_enemies()
        var center := Vector2(1510,350)
        camera.global_position = center
        _place_squad(center+Vector2(-158,96),Vector2.RIGHT)
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(ids[i],300.0 if i==4 else 90.0)
        enemy.global_position = center+Vector2(72,0)
        stage.add_child(enemy)
        await _settle(4)
        enemy.apply_damage(9999.0)
        await _settle(7 if i<4 else 11)
        camera.global_position = center
        await _save("%02d_death_%s.png" % [20+i,names[i]])

func _place_squad(center: Vector2, aim: Vector2) -> void:
    var positions: Array[Vector2] = [center,center+Vector2(-72,64),center+Vector2(-132,108)]
    for i in range(stage.squad.operators.size()):
        var actor := stage.squad.operators[i]
        actor.global_position = positions[i]
        actor.aim_world = aim
        actor.facing_sector = actor.call("_sector_from_vector", aim)
        actor.velocity = Vector2.ZERO

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
        quit(1)
        return
    print("CAPTURED: " + path)

func _verify_required_evidence() -> bool:
    for filename in REQUIRED_EVIDENCE:
        var path := ProjectSettings.globalize_path(OUT_DIR + "/" + filename)
        if not FileAccess.file_exists(path):
            push_error("missing required runtime evidence: " + filename)
            return false
    return true
