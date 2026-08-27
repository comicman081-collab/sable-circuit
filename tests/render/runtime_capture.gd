extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://artifacts/runtime_capture"

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

    await _capture_movement()
    await _capture_combat()
    await _capture_boss_phase3()
    await _capture_all_rooms()

    print("RUNTIME_CAPTURE: PASS")
    quit(0)

func _capture_movement() -> void:
    _clear_enemies()
    stage.current_step = 0
    stage.call("_activate_step")
    _place_squad(Vector2(360, 430), Vector2.RIGHT)
    camera.global_position = Vector2(410, 420)
    var active := stage.squad.get_active_operator()
    if active:
        active.debug_drive(Vector2.RIGHT, Vector2(0.93, -0.36))
    await _settle(20)
    if active:
        active.debug_stop_drive()
    await _save("01_map_movement.png")

func _capture_combat() -> void:
    _clear_enemies()
    stage.debug_spawn_encounter_for_step(1)
    _place_squad(Vector2(510, 470), Vector2.RIGHT)
    camera.global_position = Vector2(650, 420)
    await _settle(30)
    var active := stage.squad.get_active_operator()
    if active:
        active.aim_world = Vector2.RIGHT
        active.debug_fire_once()
    await _settle(4)
    await _save("02_combat_decon.png")

func _capture_boss_phase3() -> void:
    _clear_enemies()
    stage.debug_spawn_encounter_for_step(4)
    _place_squad(Vector2(1660, 500), Vector2.RIGHT)
    camera.global_position = Vector2(1820, 420)
    await _settle(12)
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            node.health = node.max_health * 0.24
    await _settle(45)
    await _save("03_boss_phase3.png")

func _capture_all_rooms() -> void:
    _clear_enemies()
    var rooms := [
        ["04_room_outer_gate.png", Vector2(260,420)],
        ["05_room_decon_corridor.png", Vector2(650,420)],
        ["06_room_archive_annex.png", Vector2(1040,420)],
        ["07_room_containment_junction.png", Vector2(1430,420)],
        ["08_room_core_c.png", Vector2(1820,420)],
        ["09_room_emergency_lift.png", Vector2(2210,420)],
        ["10_room_emergency_stores.png", Vector2(1040,720)],
        ["11_room_signal_lab.png", Vector2(1430,720)]
    ]
    for row in rooms:
        var filename: String = row[0]
        var pos: Vector2 = row[1]
        camera.global_position = pos
        _place_squad(pos + Vector2(-110, 60), Vector2.RIGHT)
        await _settle(12)
        await _save(filename)

func _place_squad(center: Vector2, aim: Vector2) -> void:
    var positions := [center, center + Vector2(-62, 64), center + Vector2(-112, 104)]
    for i in range(stage.squad.operators.size()):
        var actor := stage.squad.operators[i]
        actor.global_position = positions[i]
        actor.aim_world = aim
        actor.facing_sector = actor.call("_sector_from_vector", aim)
        actor.velocity = Vector2.ZERO

func _clear_enemies() -> void:
    for node in get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node):
            node.queue_free()
    for node in get_nodes_in_group("enemy_death_sequences"):
        if is_instance_valid(node):
            node.queue_free()
    await process_frame

func _settle(frames: int) -> void:
    for _i in range(frames):
        await process_frame

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
