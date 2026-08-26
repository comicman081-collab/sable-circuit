extends Node2D
class_name StoryStage01

signal stage_completed(summary: Dictionary)

const MISSION_PATH := "res://data/missions/MIS_CH01_01.json"
const TARGET_SCENE := preload("res://scenes/actors/enemy/TargetDummy.tscn")

var mission: Dictionary = {}
var main_route: Array = []
var optional_rooms: Array = []
var current_step := 0
var enemies_alive := 0
var _combat_started := false
var _interact_latch := false
var _supply_found := false
var _signal_found := false
var _ledger_recovered := false

@onready var squad: SquadController = $SquadController
@onready var camera: Camera2D = $Camera2D
@onready var hud: StoryStageHUD = $StoryStageHUD

func _ready() -> void:
    add_to_group("story_stage_01")
    _load_mission()
    _apply_progress_bounds()
    hud.set_optional_status(_supply_found, _signal_found)
    queue_redraw()
    call_deferred("_activate_step")

func _load_mission() -> void:
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(MISSION_PATH))
    if parsed is Dictionary:
        mission = parsed
        main_route = mission.get("main_route", [])
        optional_rooms = mission.get("optional_rooms", [])

func _process(delta: float) -> void:
    var active := squad.get_active_operator()
    if active == null:
        return
    camera.global_position = camera.global_position.lerp(active.global_position, 1.0 - pow(0.0004, delta))
    _check_current_room_entry(active)

    var interact_pressed := Input.is_key_pressed(KEY_F)
    if interact_pressed and not _interact_latch:
        _handle_interaction(active)
    _interact_latch = interact_pressed

func _check_current_room_entry(active: OperatorActor) -> void:
    if current_step < 0 or current_step >= main_route.size():
        return
    var node: Dictionary = main_route[current_step]
    var room_pos := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    if active.global_position.distance_to(room_pos) > 175.0:
        return
    var kind := str(node.get("type", "EVENT"))
    if kind in ["COMBAT", "ELITE", "BOSS"] and not _combat_started:
        _spawn_combat(node)

func _handle_interaction(active: OperatorActor) -> void:
    if current_step < main_route.size():
        var node: Dictionary = main_route[current_step]
        var room_pos := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
        if active.global_position.distance_to(room_pos) <= 175.0:
            var kind := str(node.get("type", "EVENT"))
            if kind in ["EVENT", "RESEARCH"]:
                if str(node.get("id", "")) == "R03_ARCHIVE":
                    _ledger_recovered = true
                hud.set_story(str(node.get("story", "Objective complete.")))
                _complete_step()
                return
            if kind == "EXTRACTION":
                hud.set_story(str(node.get("story", "Extraction confirmed.")))
                _finish_mission()
                return

    if current_step >= 2:
        for room_variant in optional_rooms:
            var room: Dictionary = room_variant
            var room_id := str(room.get("id", ""))
            if (room_id == "O01_SUPPLY" and _supply_found) or (room_id == "O02_RESEARCH" and _signal_found):
                continue
            var room_pos := Vector2(float(room.get("x", 0)), float(room.get("y", 0)))
            if active.global_position.distance_to(room_pos) <= 150.0:
                if room_id == "O01_SUPPLY":
                    _supply_found = true
                elif room_id == "O02_RESEARCH":
                    _signal_found = true
                hud.set_story("OPTIONAL RECOVERY // " + str(room.get("story", "Recovered.")))
                hud.set_optional_status(_supply_found, _signal_found)
                queue_redraw()
                return

func _spawn_combat(node: Dictionary) -> void:
    _combat_started = true
    enemies_alive = 0
    var count := int(node.get("enemy_count", 1))
    var hp := float(node.get("enemy_health", 100.0))
    var center := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var kind := str(node.get("type", "COMBAT"))
    for i in range(count):
        var enemy := TARGET_SCENE.instantiate() as PrototypeTargetDummy
        enemy.reset_on_zero = false
        enemy.max_health = hp
        enemy.body_color = _enemy_color(kind)
        enemy.position = center + Vector2(70.0 + i * 58.0, -50.0 + (i % 2) * 90.0)
        enemy.scale = Vector2.ONE * (1.45 if kind == "BOSS" else (1.15 if kind == "ELITE" else 1.0))
        enemy.defeated.connect(_on_story_enemy_defeated)
        add_child(enemy)
        enemies_alive += 1
    hud.set_story(_combat_story(kind))
    hud.set_combat_status(enemies_alive)

func _enemy_color(kind: String) -> Color:
    match kind:
        "BOSS": return Color("b477ff")
        "ELITE": return Color("ff9d62")
        _: return Color("c8d0d9")

func _combat_story(kind: String) -> String:
    match kind:
        "BOSS": return "CORE C // The carrier signal condenses around a physical anchor. Destroy it before the reactor warning reaches critical."
        "ELITE": return "CONTAINMENT JUNCTION // Security frames are still following a corrupted quarantine order."
        _: return "DECON CORRIDOR // Automated security wakes as the squad crosses the inner seal."

func _on_story_enemy_defeated(_enemy: PrototypeTargetDummy) -> void:
    enemies_alive = maxi(0, enemies_alive - 1)
    hud.set_combat_status(enemies_alive)
    if enemies_alive == 0:
        _combat_started = false
        hud.set_story("AREA SECURE // Route lock released.")
        _complete_step()

func _activate_step() -> void:
    if main_route.is_empty() or current_step >= main_route.size():
        return
    var node: Dictionary = main_route[current_step]
    var kind := str(node.get("type", "EVENT"))
    hud.set_room(current_step, main_route.size(), str(node.get("title", "Unknown")), kind)
    hud.set_objective(str(node.get("objective", "Proceed")), kind in ["EVENT", "RESEARCH", "EXTRACTION"])
    hud.set_combat_status(0)
    if kind in ["EVENT", "RESEARCH", "EXTRACTION"]:
        hud.set_story("Move into the marked room and press F to interact.")
    else:
        hud.set_story("Advance into the marked room. Combat locks progression until the room is secure.")
    _apply_progress_bounds()
    queue_redraw()

func _complete_step() -> void:
    current_step += 1
    if current_step < main_route.size():
        _activate_step()

func _apply_progress_bounds() -> void:
    if main_route.is_empty():
        return
    var allowed_index := mini(current_step, main_route.size() - 1)
    var node: Dictionary = main_route[allowed_index]
    var right_edge := float(node.get("x", 400)) + 185.0
    var bounds := Rect2(90.0, 120.0, maxf(260.0, right_edge - 90.0), 650.0)
    for actor in squad.operators:
        actor.set_movement_bounds(bounds)

func _finish_mission() -> void:
    var summary := {
        "mission_id": mission.get("mission_id", "MIS_CH01_01"),
        "chapter_id": mission.get("chapter_id", "CH01"),
        "ledger_recovered": _ledger_recovered,
        "field_supplies": _supply_found,
        "carrier_fragment": _signal_found,
        "secured_rewards": 120 + (40 if _supply_found else 0) + (60 if _signal_found else 0)
    }
    stage_completed.emit(summary)

func _draw() -> void:
    draw_rect(Rect2(40, 70, 2380, 790), Color("0d171e"), true)
    for i in range(main_route.size()):
        var node: Dictionary = main_route[i]
        var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
        if i < main_route.size() - 1:
            var next_node: Dictionary = main_route[i + 1]
            var np := Vector2(float(next_node.get("x", 0)), float(next_node.get("y", 0)))
            draw_line(p, np, Color("344d5a"), 18.0)
        _draw_room(node, i <= current_step)
    for room_variant in optional_rooms:
        var room: Dictionary = room_variant
        var main_x := float(room.get("x", 0))
        draw_line(Vector2(main_x, 520), Vector2(main_x, float(room.get("y", 720)) - 120), Color("2a444f"), 12.0)
        var recovered := (str(room.get("id", "")) == "O01_SUPPLY" and _supply_found) or (str(room.get("id", "")) == "O02_RESEARCH" and _signal_found)
        _draw_optional_room(room, recovered)

func _draw_room(node: Dictionary, unlocked: bool) -> void:
    var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var rect := Rect2(p - Vector2(155, 120), Vector2(310, 240))
    var fill := Color("19303b") if unlocked else Color("11191e")
    draw_rect(rect, fill, true)
    draw_rect(rect, Color("588396") if unlocked else Color("28353b"), false, 4.0)
    draw_circle(p, 12.0, Color("63c7df") if unlocked else Color("34434a"))

func _draw_optional_room(node: Dictionary, recovered: bool) -> void:
    var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var rect := Rect2(p - Vector2(130, 92), Vector2(260, 184))
    draw_rect(rect, Color("18272d"), true)
    draw_rect(rect, Color("69a07f") if recovered else Color("496472"), false, 3.0)

func debug_route_count() -> int:
    return main_route.size()

func debug_optional_count() -> int:
    return optional_rooms.size()

func debug_advance_step() -> void:
    if current_step < main_route.size() - 1:
        _complete_step()

func debug_finish() -> Dictionary:
    _ledger_recovered = true
    _supply_found = true
    _signal_found = true
    return {
        "mission_id": mission.get("mission_id", "MIS_CH01_01"),
        "chapter_id": "CH01",
        "ledger_recovered": true,
        "field_supplies": true,
        "carrier_fragment": true,
        "secured_rewards": 220
    }
