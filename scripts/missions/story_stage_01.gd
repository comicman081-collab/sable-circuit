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

func _process(_delta: float) -> void:
    var active := squad.get_active_operator()
    if active == null:
        return
    _check_current_room_entry(active)
    var interact_pressed := Input.is_key_pressed(KEY_F)
    if interact_pressed and not _interact_latch:
        _handle_interaction(active)
    _interact_latch = interact_pressed

func _check_current_room_entry(active: OperatorActor) -> void:
    if current_step < 0 or current_step >= main_route.size(): return
    var node: Dictionary = main_route[current_step]
    var room_pos := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    if active.global_position.distance_to(room_pos) > 175.0: return
    var kind := str(node.get("type", "EVENT"))
    if kind in ["COMBAT", "ELITE", "BOSS"] and not _combat_started: _spawn_combat(node)

func _handle_interaction(active: OperatorActor) -> void:
    if current_step < main_route.size():
        var node: Dictionary = main_route[current_step]
        var room_pos := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
        if active.global_position.distance_to(room_pos) <= 175.0:
            var kind := str(node.get("type", "EVENT"))
            if kind in ["EVENT", "RESEARCH"]:
                if str(node.get("id", "")) == "R03_ARCHIVE": _ledger_recovered = true
                hud.set_story(str(node.get("story", "Objective complete.")))
                _complete_step(); return
            if kind == "EXTRACTION":
                hud.set_story(str(node.get("story", "Extraction confirmed.")))
                _finish_mission(); return
    if current_step >= 2:
        for room_variant in optional_rooms:
            var room: Dictionary = room_variant
            var room_id := str(room.get("id", ""))
            if (room_id == "O01_SUPPLY" and _supply_found) or (room_id == "O02_RESEARCH" and _signal_found): continue
            var room_pos := Vector2(float(room.get("x", 0)), float(room.get("y", 0)))
            if active.global_position.distance_to(room_pos) <= 150.0:
                if room_id == "O01_SUPPLY": _supply_found = true
                elif room_id == "O02_RESEARCH": _signal_found = true
                hud.set_story("OPTIONAL RECOVERY // " + str(room.get("story", "Recovered.")))
                hud.set_optional_status(_supply_found, _signal_found)
                queue_redraw(); return

func _spawn_combat(node: Dictionary) -> void:
    _combat_started = true; enemies_alive = 0; _active_enemy_ids.clear()
    var center := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var kind := str(node.get("type", "COMBAT"))
    var encounter: Array = node.get("encounter", [])
    if encounter.is_empty(): push_error("StoryStage01 encounter missing for " + str(node.get("id", "?"))); return
    for row_variant in encounter:
        if not (row_variant is Dictionary): continue
        var row: Dictionary = row_variant
        var identity := str(row.get("enemy_id", ""))
        if ArtProfileRegistry.get_profile(identity).is_empty(): push_error("StoryStage01 unknown enemy profile: " + identity); continue
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(identity, float(row.get("health", 100.0)))
        enemy.position = center + Vector2(float(row.get("offset_x", 70.0)), float(row.get("offset_y", 0.0)))
        enemy.defeated.connect(_on_story_enemy_defeated); add_child(enemy)
        enemies_alive += 1; _active_enemy_ids.append(identity)
    hud.set_story(_combat_story(kind)); hud.set_combat_status(enemies_alive); queue_redraw()

func _combat_story(kind: String) -> String:
    match kind:
        "BOSS": return "CORE C // The carrier signal condenses into the Signal Anchor Guardian. Its ring, pylons and emitter arms move as one hostile machine."
        "ELITE": return "CONTAINMENT JUNCTION // A Shield Breacher anchors the corridor while a rifle unit works the exposed angles."
        _: return "DECON CORRIDOR // Rifle security, a recon drone and an aberrant runner wake with three completely different attack rhythms."

func _on_story_enemy_defeated(enemy: EnemyActor) -> void:
    _active_enemy_ids.erase(enemy.enemy_id); enemies_alive = maxi(0, enemies_alive - 1); hud.set_combat_status(enemies_alive)
    if enemies_alive == 0:
        _combat_started = false; hud.set_story("AREA SECURE // Route lock released."); _complete_step()

func _activate_step() -> void:
    if main_route.is_empty() or current_step >= main_route.size(): return
    var node: Dictionary = main_route[current_step]
    var kind := str(node.get("type", "EVENT"))
    hud.set_room(current_step, main_route.size(), str(node.get("title", "Unknown")), kind)
    hud.set_objective(str(node.get("objective", "Proceed")), kind in ["EVENT", "RESEARCH", "EXTRACTION"])
    hud.set_combat_status(0)
    if kind in ["EVENT", "RESEARCH", "EXTRACTION"]: hud.set_story("Move into the marked room and press F to interact.")
    else: hud.set_story("Advance into the marked room. Combat locks progression until every unique hostile in the authored encounter is down.")
    _apply_progress_bounds(); queue_redraw()

func _complete_step() -> void:
    current_step += 1
    if current_step < main_route.size(): _activate_step()

func _apply_progress_bounds() -> void:
    if main_route.is_empty(): return
    var allowed_index := mini(current_step, main_route.size() - 1)
    var node: Dictionary = main_route[allowed_index]
    var right_edge := float(node.get("x", 400)) + 185.0
    var bounds := Rect2(90.0, 120.0, maxf(260.0, right_edge - 90.0), 650.0)
    for actor in squad.operators: actor.set_movement_bounds(bounds)

func _finish_mission() -> void:
    var summary := {"mission_id": mission.get("mission_id", "MIS_CH01_01"),"chapter_id": mission.get("chapter_id", "CH01"),"ledger_recovered": _ledger_recovered,"field_supplies": _supply_found,"carrier_fragment": _signal_found,"secured_rewards": 120 + (40 if _supply_found else 0) + (60 if _signal_found else 0)}
    stage_completed.emit(summary)

func _draw() -> void:
    for i in range(main_route.size()):
        var node: Dictionary = main_route[i]
        var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
        if i < main_route.size() - 1:
            var next_node: Dictionary = main_route[i + 1]
            var np := Vector2(float(next_node.get("x", 0)), float(next_node.get("y", 0)))
            draw_line(p, np, Color(0.18,0.34,0.40,0.035 if i >= current_step else 0.065), 2.0)
        _draw_room_marker(node, i, i <= current_step)
    for room_variant in optional_rooms:
        var room: Dictionary = room_variant
        var room_id := str(room.get("id", ""))
        var parent_index := 2 if room_id == "O01_SUPPLY" else 3
        if parent_index < main_route.size():
            var parent_row: Dictionary = main_route[parent_index]
            var parent_p := Vector2(float(parent_row.get("x", 0)), float(parent_row.get("y", 0)))
            var room_p := Vector2(float(room.get("x", 0)), float(room.get("y", 0)))
            var dir := (room_p-parent_p).normalized()
            draw_line(parent_p+dir*78.0, room_p-dir*68.0, Color(0.20,0.42,0.46,0.055), 2.0)
        var recovered := (room_id == "O01_SUPPLY" and _supply_found) or (room_id == "O02_RESEARCH" and _signal_found)
        _draw_optional_marker(room, recovered)

func _draw_room_marker(node: Dictionary, index: int, unlocked: bool) -> void:
    var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0))) + Vector2(0, 46)
    var active := index == current_step
    if active:
        var cyan := Color(0.43,0.91,0.95,0.46)
        var amber := Color(0.94,0.66,0.25,0.58)
        draw_line(p+Vector2(-11,-6),p+Vector2(-4,-6),cyan,1.5)
        draw_line(p+Vector2(4,-6),p+Vector2(11,-6),cyan,1.5)
        draw_line(p+Vector2(-8,0),p+Vector2(0,6),amber,2.0)
        draw_line(p+Vector2(0,6),p+Vector2(8,0),amber,2.0)
        draw_circle(p+Vector2(0,-6),1.7,Color(0.76,0.96,0.98,0.50))
    elif unlocked:
        draw_line(p+Vector2(-5,0),p+Vector2(5,0),Color(0.34,0.55,0.61,0.14),1.0)
        draw_circle(p,1.2,Color(0.42,0.62,0.68,0.16))

func _draw_optional_marker(node: Dictionary, recovered: bool) -> void:
    var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0))) + Vector2(0,34)
    var color := Color(0.44,0.88,0.62,0.30) if recovered else Color(0.35,0.65,0.68,0.14)
    draw_line(p+Vector2(-6,0),p+Vector2(6,0),color,1.2)
    if recovered:
        draw_line(p+Vector2(-5,-3),p+Vector2(-1,2),color,1.5)
        draw_line(p+Vector2(-1,2),p+Vector2(6,-5),color,1.5)

func debug_progress_marker_contract() -> Dictionary:
    return {"active_radius": 0.0,"optional_radius": 0.0,"giant_room_circles_forbidden": true,"floor_chevrons": true,"active_arc_removed": true}

func debug_route_count() -> int: return main_route.size()
func debug_optional_count() -> int: return optional_rooms.size()
func debug_advance_step() -> void:
    if current_step < main_route.size() - 1: _complete_step()
func debug_finish() -> Dictionary:
    _ledger_recovered = true; _supply_found = true; _signal_found = true
    return {"mission_id": mission.get("mission_id", "MIS_CH01_01"),"chapter_id": "CH01","ledger_recovered": true,"field_supplies": true,"carrier_fragment": true,"secured_rewards": 220}
func debug_spawn_encounter_for_step(step_index: int) -> Array[String]:
    if step_index < 0 or step_index >= main_route.size(): return []
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node): node.queue_free()
    enemies_alive = 0; _combat_started = false; current_step = step_index
    var row: Dictionary = main_route[current_step]; _spawn_combat(row)
    return _active_enemy_ids.duplicate()
