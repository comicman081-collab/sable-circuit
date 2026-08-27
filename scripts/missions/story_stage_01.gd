extends Node2D
class_name StoryStage01

signal stage_completed(summary: Dictionary)

const MISSION_PATH := "res://data/missions/MIS_CH01_01.json"
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")

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
var _active_enemy_ids: Array[String] = []

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
    _active_enemy_ids.clear()
    var center := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var kind := str(node.get("type", "COMBAT"))
    var encounter: Array = node.get("encounter", [])
    if encounter.is_empty():
        push_error("StoryStage01 encounter missing for " + str(node.get("id", "?")))
        return

    for row_variant in encounter:
        if not (row_variant is Dictionary):
            continue
        var row: Dictionary = row_variant
        var identity := str(row.get("enemy_id", ""))
        if ArtProfileRegistry.get_profile(identity).is_empty():
            push_error("StoryStage01 unknown enemy profile: " + identity)
            continue
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(identity, float(row.get("health", 100.0)))
        enemy.position = center + Vector2(float(row.get("offset_x", 70.0)), float(row.get("offset_y", 0.0)))
        enemy.defeated.connect(_on_story_enemy_defeated)
        add_child(enemy)
        enemies_alive += 1
        _active_enemy_ids.append(identity)

    hud.set_story(_combat_story(kind))
    hud.set_combat_status(enemies_alive)
    queue_redraw()

func _combat_story(kind: String) -> String:
    match kind:
        "BOSS": return "CORE C // The carrier signal condenses into the Signal Anchor Guardian. Its ring, pylons and emitter arms move as one hostile machine."
        "ELITE": return "CONTAINMENT JUNCTION // A Shield Breacher anchors the corridor while a rifle unit works the exposed angles."
        _: return "DECON CORRIDOR // Rifle security, a recon drone and an aberrant runner wake with three completely different attack rhythms."

func _on_story_enemy_defeated(enemy: EnemyActor) -> void:
    _active_enemy_ids.erase(enemy.enemy_id)
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
        hud.set_story("Advance into the marked room. Combat locks progression until every unique hostile in the authored encounter is down.")
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
    # M6: StoryStage01 no longer paints opaque prototype rooms. Gameplay authority
    # remains here, while FacilityArchitecture/SurfaceDetail/EnvironmentDirector own
    # the visible Site-7 world. Only lightweight progression markers are drawn.
    for i in range(main_route.size()):
        var node: Dictionary = main_route[i]
        var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
        if i < main_route.size() - 1:
            var next_node: Dictionary = main_route[i + 1]
            var np := Vector2(float(next_node.get("x", 0)), float(next_node.get("y", 0)))
            draw_line(p, np, Color(0.18,0.34,0.40,0.10 if i >= current_step else 0.18), 5.0)
        _draw_room_marker(node, i, i <= current_step)
    for room_variant in optional_rooms:
        var room: Dictionary = room_variant
        var main_x := float(room.get("x", 0))
        var room_y := float(room.get("y", 720))
        draw_line(Vector2(main_x, 530), Vector2(main_x, room_y - 105), Color(0.20,0.42,0.46,0.10), 4.0)
        var recovered := (str(room.get("id", "")) == "O01_SUPPLY" and _supply_found) or (str(room.get("id", "")) == "O02_RESEARCH" and _signal_found)
        _draw_optional_marker(room, recovered)

func _draw_room_marker(node: Dictionary, index: int, unlocked: bool) -> void:
    var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var active := index == current_step
    var color := Color("6ee7f1") if active else (Color(0.34,0.55,0.61,0.24) if unlocked else Color(0.20,0.27,0.31,0.18))
    var radius := 80.0 if active else 66.0
    draw_arc(p,radius,-0.28,PI*0.68,24,Color(color.r,color.g,color.b,color.a*0.55),2.0)
    if active:
        draw_arc(p,radius+8.0,PI*0.78,PI*1.28,12,Color(0.95,0.68,0.24,0.50),3.0)
        for i in range(4):
            var angle := -0.18+float(i)*PI*0.44
            var d := Vector2.RIGHT.rotated(angle)
            draw_line(p+d*(radius-4.0),p+d*(radius+8.0),Color(0.54,0.95,0.98,0.50),2.0)

func _draw_optional_marker(node: Dictionary, recovered: bool) -> void:
    var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var color := Color("71e0a0") if recovered else Color(0.35,0.65,0.68,0.28)
    draw_arc(p,58.0,0.0,TAU,32,color,2.0)
    draw_circle(p,4.0,Color(color.r,color.g,color.b,0.62))

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

func debug_spawn_encounter_for_step(step_index: int) -> Array[String]:
    if step_index < 0 or step_index >= main_route.size():
        return []
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node):
            node.queue_free()
    enemies_alive = 0
    _combat_started = false
    current_step = step_index
    var row: Dictionary = main_route[current_step]
    _spawn_combat(row)
    return _active_enemy_ids.duplicate()
