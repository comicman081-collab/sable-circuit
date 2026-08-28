extends Node2D
class_name StoryStage01

signal stage_completed(summary: Dictionary)

const MISSION_PATH := "res://data/missions/MIS_CH01_01.json"
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const EXTRACTION_OFFER_IDS := ["R03_ARCHIVE", "R04_CONTAINMENT", "R05_CORE"]
const INTEL_KEYS := ["SECURITY","ABERRANT","ANCHOR"]

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

# Persistent campaign authority is separate from deployment-only run authority.
var _run_id := "UNCONFIGURED-RUN"
var _campaign_snapshot: Dictionary = {}
var _research_multiplier := 1.0
var _cargo_common_research := 0
var _cargo_unsecured_research := 0
var _cargo_salvage := 0
var _cargo_fragments := 0
var _cargo_intel: Dictionary = {"SECURITY":0,"ABERRANT":0,"ANCHOR":0}
var _intel_seen_enemy_ids: Array[String] = []
var _completed_depth := 0
var _extraction_offer_active := false
var _extraction_offer_room := ""
var _extract_latch := false
var _continue_latch := false
var _mission_ended := false

# M11 run contract. These values are never committed to CampaignProgression.
var _run_contract: Dictionary = {}
var _enemy_run_modifiers: Dictionary = {
    "enemy_health_multiplier":1.0,
    "enemy_damage_multiplier":1.0,
    "enemy_speed_multiplier":1.0,
    "enemy_attack_interval_multiplier":1.0
}
var _run_research_reward_multiplier := 1.0
var _run_salvage_reward_multiplier := 1.0
var _run_fragment_reward_multiplier := 1.0
var _run_boost_definitions: Array = []
var _active_run_boost_ids: Array[String] = []

@onready var squad: SquadController = $SquadController
@onready var camera: Camera2D = $Camera2D
@onready var hud: StoryStageHUD = $StoryStageHUD

func _ready() -> void:
    add_to_group("story_stage_01")
    _load_mission()
    _apply_progress_bounds()
    hud.set_optional_status(_supply_found, _signal_found)
    _refresh_cargo_hud()
    queue_redraw()
    call_deferred("_activate_step")

func configure_campaign(snapshot: Dictionary, run_id: String, run_contract: Dictionary = {}) -> void:
    _campaign_snapshot = snapshot.duplicate(true)
    _run_id = run_id if not run_id.is_empty() else "UNCONFIGURED-RUN"
    _research_multiplier = clampf(float(snapshot.get("research_multiplier", 1.0)), 1.0, 2.0)
    var damage_multiplier := clampf(float(snapshot.get("damage_multiplier", 1.0)), 1.0, 2.0)
    var equipped: Dictionary = snapshot.get("equipped_modules",{})

    _configure_run_contract(run_contract)
    if squad != null:
        for actor in squad.operators:
            actor.apply_campaign_modifiers({
                "damage_multiplier": damage_multiplier,
                "module_id": str(equipped.get(actor.operator_id,""))
            })
        _apply_active_run_boosts()
    _refresh_cargo_hud()

func _configure_run_contract(run_contract: Dictionary) -> void:
    _run_contract = run_contract.duplicate(true)
    _enemy_run_modifiers = {
        "enemy_health_multiplier":clampf(float(_run_contract.get("enemy_health_multiplier",1.0)),0.5,3.0),
        "enemy_damage_multiplier":clampf(float(_run_contract.get("enemy_damage_multiplier",1.0)),0.5,3.0),
        "enemy_speed_multiplier":clampf(float(_run_contract.get("enemy_speed_multiplier",1.0)),0.5,2.0),
        "enemy_attack_interval_multiplier":clampf(float(_run_contract.get("enemy_attack_interval_multiplier",1.0)),0.5,2.0)
    }
    _run_research_reward_multiplier = clampf(float(_run_contract.get("research_reward_multiplier",1.0)),0.5,4.0)
    _run_salvage_reward_multiplier = clampf(float(_run_contract.get("salvage_reward_multiplier",1.0)),0.5,4.0)
    _run_fragment_reward_multiplier = clampf(float(_run_contract.get("fragment_reward_multiplier",1.0)),0.5,4.0)
    _run_boost_definitions = (_run_contract.get("run_only_boosts",[]) as Array).duplicate(true)
    _active_run_boost_ids.clear()

func _load_mission() -> void:
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(MISSION_PATH))
    if parsed is Dictionary:
        mission = parsed
        main_route = mission.get("main_route", [])
        optional_rooms = mission.get("optional_rooms", [])

func _process(_delta: float) -> void:
    if _mission_ended:
        return
    if _all_squad_downed():
        _finish_mission("WIPED")
        return

    # M12: F is shared by field interaction and manual revive. A nearby downed
    # squadmate always reserves F first. Latches still follow the held key so a
    # completed revive cannot accidentally extract/interact without release+press.
    var revive_reserved := squad != null and squad.has_revivable_target_in_range()
    if _extraction_offer_active:
        var extract_pressed := Input.is_key_pressed(KEY_F)
        var continue_pressed := Input.is_key_pressed(KEY_C)
        if revive_reserved:
            _extract_latch = extract_pressed
            _continue_latch = continue_pressed
            return
        if extract_pressed and not _extract_latch:
            _finish_mission("EXTRACTED")
        elif continue_pressed and not _continue_latch:
            _continue_after_extraction_offer()
        _extract_latch = extract_pressed
        _continue_latch = continue_pressed
        return

    var active := squad.get_active_operator()
    if active == null:
        return
    _check_current_room_entry(active)
    var interact_pressed := Input.is_key_pressed(KEY_F)
    if interact_pressed and not _interact_latch and not revive_reserved:
        _handle_interaction(active)
    _interact_latch = interact_pressed

func _all_squad_downed() -> bool:
    if squad == null or squad.operators.is_empty():
        return false
    for actor in squad.operators:
        if actor != null and not actor.is_downed():
            return false
    return true

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
                _completed_depth = maxi(_completed_depth, current_step + 1)
                hud.set_story(str(node.get("story", "Extraction confirmed.")))
                _finish_mission("EXTRACTED"); return
    if current_step >= 2:
        for room_variant in optional_rooms:
            var room: Dictionary = room_variant
            var room_id := str(room.get("id", ""))
            if (room_id == "O01_SUPPLY" and _supply_found) or (room_id == "O02_RESEARCH" and _signal_found): continue
            var room_pos := Vector2(float(room.get("x", 0)), float(room.get("y", 0)))
            if active.global_position.distance_to(room_pos) <= 150.0:
                if room_id == "O01_SUPPLY":
                    _supply_found = true
                    _cargo_common_research += 20
                    _cargo_salvage += 2
                elif room_id == "O02_RESEARCH":
                    _signal_found = true
                    _cargo_unsecured_research += 40
                    _cargo_fragments += 1
                var boost_id := _activate_run_boost_for_room(room_id)
                var boost_suffix := ""
                if not boost_id.is_empty(): boost_suffix = " // RUN BOOST " + boost_id
                hud.set_story("OPTIONAL RECOVERY // " + str(room.get("story", "Recovered.")) + boost_suffix)
                hud.set_optional_status(_supply_found, _signal_found)
                _refresh_cargo_hud()
                queue_redraw(); return

func _activate_run_boost_for_room(room_id: String) -> String:
    for row_variant in _run_boost_definitions:
        if not (row_variant is Dictionary): continue
        var row: Dictionary = row_variant
        if str(row.get("source_room", "")) != room_id: continue
        var boost_id := str(row.get("id", "")).to_upper()
        if boost_id.is_empty() or _active_run_boost_ids.has(boost_id): return ""
        _active_run_boost_ids.append(boost_id)
        _apply_active_run_boosts()
        return boost_id
    return ""

func _apply_active_run_boosts() -> void:
    if squad == null: return
    var aggregate := {
        "operator_speed_multiplier":1.0,
        "incoming_damage_multiplier":1.0,
        "primary_damage_multiplier":1.0,
        "energy_gain_multiplier":1.0
    }
    for row_variant in _run_boost_definitions:
        if not (row_variant is Dictionary): continue
        var row: Dictionary = row_variant
        var boost_id := str(row.get("id", "")).to_upper()
        if not _active_run_boost_ids.has(boost_id): continue
        aggregate["operator_speed_multiplier"] = float(aggregate["operator_speed_multiplier"]) * clampf(float(row.get("operator_speed_multiplier",1.0)),0.75,1.50)
        aggregate["incoming_damage_multiplier"] = float(aggregate["incoming_damage_multiplier"]) * clampf(float(row.get("incoming_damage_multiplier",1.0)),0.50,1.50)
        aggregate["primary_damage_multiplier"] = float(aggregate["primary_damage_multiplier"]) * clampf(float(row.get("primary_damage_multiplier",1.0)),0.75,1.75)
        aggregate["energy_gain_multiplier"] = float(aggregate["energy_gain_multiplier"]) * clampf(float(row.get("energy_gain_multiplier",1.0)),0.50,2.00)
    for actor in squad.operators:
        actor.apply_run_boosts(aggregate)
    squad.configure_run_energy_multiplier(float(aggregate["energy_gain_multiplier"]))

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
        enemy.apply_run_modifiers(_enemy_run_modifiers)
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
    _award_enemy_intel(enemy.enemy_id)
    _active_enemy_ids.erase(enemy.enemy_id)
    enemies_alive = maxi(0, enemies_alive - 1)
    hud.set_combat_status(enemies_alive)
    if enemies_alive == 0:
        _combat_started = false
        hud.set_story("AREA SECURE // Intel samples tagged. Route lock released.")
        _complete_step()

func _award_enemy_intel(enemy_id: String) -> void:
    var id := enemy_id.to_upper()
    if _intel_seen_enemy_ids.has(id): return
    _intel_seen_enemy_ids.append(id)
    var key := ""
    if "BOSS" in id or "ANCHOR" in id: key = "ANCHOR"
    elif "ABERRANT" in id: key = "ABERRANT"
    elif "RIFLE" in id or "SHIELD" in id or "DRONE" in id: key = "SECURITY"
    if key.is_empty(): return
    _cargo_intel[key] = int(_cargo_intel.get(key,0)) + 1
    hud.set_intel_status(_cargo_intel)

func _activate_step() -> void:
    if main_route.is_empty() or current_step >= main_route.size(): return
    var node: Dictionary = main_route[current_step]
    var kind := str(node.get("type", "EVENT"))
    hud.set_extraction_offer(false, 0, 0)
    hud.set_room(current_step, main_route.size(), str(node.get("title", "Unknown")), kind)
    hud.set_objective(str(node.get("objective", "Proceed")), kind in ["EVENT", "RESEARCH", "EXTRACTION"])
    hud.set_combat_status(0)
    if kind in ["EVENT", "RESEARCH", "EXTRACTION"]: hud.set_story("Move into the marked room and press F to interact.")
    else: hud.set_story("Advance into the marked room. Combat locks progression until every unique hostile in the authored encounter is down.")
    _apply_progress_bounds(); queue_redraw()

func _complete_step() -> void:
    if current_step < 0 or current_step >= main_route.size(): return
    var completed_node: Dictionary = main_route[current_step]
    _award_main_route_reward(completed_node)
    _completed_depth = maxi(_completed_depth, current_step + 1)
    if str(completed_node.get("id", "")) in EXTRACTION_OFFER_IDS:
        _offer_extraction(completed_node)
        return
    current_step += 1
    if current_step < main_route.size(): _activate_step()

func _award_main_route_reward(node: Dictionary) -> void:
    var kind := str(node.get("type", "EVENT"))
    match kind:
        "EVENT": _cargo_common_research += 10
        "COMBAT": _cargo_common_research += 25
        "RESEARCH": _cargo_common_research += 45
        "ELITE": _cargo_common_research += 35
        "BOSS": _cargo_unsecured_research += 45
    _refresh_cargo_hud()

func _offer_extraction(node: Dictionary) -> void:
    _extraction_offer_active = true
    _extraction_offer_room = str(node.get("id", ""))
    _extract_latch = Input.is_key_pressed(KEY_F)
    _continue_latch = Input.is_key_pressed(KEY_C)
    hud.set_extraction_offer(true, _completed_depth, _cargo_common_research + _cargo_unsecured_research)
    hud.set_story("EXTRACTION WINDOW // [F] secure cargo + intel now   [C] continue deeper and keep samples at risk.")
    hud.set_objective("Choose extraction or continue deeper", false)
    _apply_progress_bounds()

func _continue_after_extraction_offer() -> void:
    if not _extraction_offer_active: return
    _extraction_offer_active = false
    _extraction_offer_room = ""
    _extract_latch = false
    _continue_latch = true
    current_step += 1
    if current_step < main_route.size(): _activate_step()

func _apply_progress_bounds() -> void:
    if main_route.is_empty(): return
    var allowed_index := mini(current_step, main_route.size() - 1)
    var node: Dictionary = main_route[allowed_index]
    var right_edge := float(node.get("x", 400)) + 185.0
    var bounds := Rect2(90.0, 120.0, maxf(260.0, right_edge - 90.0), 650.0)
    for actor in squad.operators: actor.set_movement_bounds(bounds)

func _refresh_cargo_hud() -> void:
    if hud == null: return
    hud.set_cargo_status(_cargo_common_research, _cargo_unsecured_research, _cargo_salvage, _cargo_fragments)
    hud.set_intel_status(_cargo_intel)

func _build_summary(outcome: String) -> Dictionary:
    var wiped := outcome.to_upper() == "WIPED"
    var raw_research := 0
    var base_salvage := 0
    var base_fragments := 0
    var lost_research := 0
    var secured_intel := {"SECURITY":0,"ABERRANT":0,"ANCHOR":0}
    if wiped:
        raw_research = int(floor(float(_cargo_common_research) * 0.5))
        base_salvage = int(floor(float(_cargo_salvage) * 0.5))
        base_fragments = 0
        lost_research = (_cargo_common_research - raw_research) + _cargo_unsecured_research
    else:
        raw_research = _cargo_common_research + _cargo_unsecured_research
        base_salvage = _cargo_salvage
        base_fragments = _cargo_fragments
        for key in INTEL_KEYS: secured_intel[key] = int(_cargo_intel.get(key,0))

    var secured_research := maxi(0,int(round(float(raw_research) * _research_multiplier * _run_research_reward_multiplier)))
    var secured_salvage := maxi(0,int(round(float(base_salvage) * _run_salvage_reward_multiplier)))
    var secured_fragments := maxi(0,int(round(float(base_fragments) * _run_fragment_reward_multiplier)))
    return {
        "mission_id": mission.get("mission_id", "MIS_CH01_01"),
        "chapter_id": mission.get("chapter_id", "CH01"),
        "transaction_id": _run_id,
        "run_id": _run_id,
        "outcome": outcome.to_upper(),
        "early_extraction": not wiped and _completed_depth < main_route.size(),
        "extraction_room": _extraction_offer_room,
        "extraction_depth": _completed_depth,
        "ledger_recovered": _ledger_recovered,
        "ledger_retained_on_wipe": wiped and _ledger_recovered,
        "field_supplies": _supply_found,
        "carrier_fragment": _signal_found,
        "carrier_fragment_secured": secured_fragments > 0,
        "secured_research": secured_research,
        "secured_salvage": secured_salvage,
        "secured_fragments": secured_fragments,
        "secured_intel": secured_intel,
        "secured_rewards": secured_research,
        "lost_unsecured": lost_research,
        "lost_intel_samples": 0 if not wiped else int(_cargo_intel.get("SECURITY",0))+int(_cargo_intel.get("ABERRANT",0))+int(_cargo_intel.get("ANCHOR",0)),
        "research_multiplier": _research_multiplier,
        "run_research_reward_multiplier": _run_research_reward_multiplier,
        "run_salvage_reward_multiplier": _run_salvage_reward_multiplier,
        "run_fragment_reward_multiplier": _run_fragment_reward_multiplier,
        "run_contract": _run_contract.duplicate(true),
        "active_run_boosts": _active_run_boost_ids.duplicate(),
        "run_only_boosts_expire_on_return": true,
        "cargo_before_resolution": {
            "common_research": _cargo_common_research,
            "unsecured_research": _cargo_unsecured_research,
            "salvage": _cargo_salvage,
            "fragments": _cargo_fragments,
            "intel": _cargo_intel.duplicate(true)
        },
        "wipe_policy": "50% COMMON RESEARCH/SALVAGE RETAINED; HIGH-VALUE RESEARCH + SIGNAL FRAGMENTS + INTEL SAMPLES LOST; RUN-ONLY BOOSTS EXPIRE; STORY LEDGER RETAINED"
    }

func _finish_mission(outcome: String = "EXTRACTED") -> void:
    if _mission_ended: return
    _mission_ended = true
    _extraction_offer_active = false
    hud.set_extraction_offer(false, 0, 0)
    stage_completed.emit(_build_summary(outcome))

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
    return {"active_radius":0.0,"optional_radius":0.0,"giant_room_circles_forbidden":true,"floor_chevrons":true,"active_arc_removed":true}
func debug_route_count() -> int: return main_route.size()
func debug_optional_count() -> int: return optional_rooms.size()
func debug_advance_step() -> void:
    if current_step < main_route.size() - 1:
        _complete_step()
        if _extraction_offer_active: _continue_after_extraction_offer()
func debug_finish() -> Dictionary:
    _ledger_recovered=true; _supply_found=true; _signal_found=true; _cargo_common_research=135; _cargo_unsecured_research=85; _cargo_salvage=2; _cargo_fragments=1; _completed_depth=6
    return _build_summary("EXTRACTED")
func debug_spawn_encounter_for_step(step_index: int) -> Array[String]:
    if step_index < 0 or step_index >= main_route.size(): return []
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node): node.queue_free()
    enemies_alive=0; _combat_started=false; current_step=step_index
    var row:Dictionary=main_route[current_step]; _spawn_combat(row)
    return _active_enemy_ids.duplicate()
func debug_seed_cargo(common_research:int,unsecured_research:int,salvage_value:int,fragments:int,ledger:bool,depth:int)->void:
    _cargo_common_research=maxi(0,common_research); _cargo_unsecured_research=maxi(0,unsecured_research); _cargo_salvage=maxi(0,salvage_value); _cargo_fragments=maxi(0,fragments); _ledger_recovered=ledger; _supply_found=_cargo_salvage>0; _signal_found=_cargo_fragments>0; _completed_depth=clampi(depth,0,main_route.size()); _refresh_cargo_hud()
func debug_seed_intel(security:int,aberrant:int,anchor:int)->void:
    _cargo_intel={"SECURITY":maxi(0,security),"ABERRANT":maxi(0,aberrant),"ANCHOR":maxi(0,anchor)}; _refresh_cargo_hud()
func debug_extraction_summary(room_id:String="DEBUG_EXTRACTION")->Dictionary:
    _extraction_offer_room=room_id; return _build_summary("EXTRACTED")
func debug_wipe_summary()->Dictionary: return _build_summary("WIPED")
func debug_offer_extraction(room_id:String="R03_ARCHIVE")->void:
    _extraction_offer_active=true; _extraction_offer_room=room_id; hud.set_extraction_offer(true,_completed_depth,_cargo_common_research+_cargo_unsecured_research)
func debug_continue_extraction()->void: _continue_after_extraction_offer()
func debug_extraction_active()->bool: return _extraction_offer_active
func debug_intel_cargo()->Dictionary: return _cargo_intel.duplicate(true)
func debug_run_contract()->Dictionary: return _run_contract.duplicate(true)
func debug_active_run_boosts()->Array[String]: return _active_run_boost_ids.duplicate()
func debug_activate_run_boost_for_room(room_id:String)->String: return _activate_run_boost_for_room(room_id)
func debug_interaction_reserved_for_revive()->bool: return squad!=null and squad.has_revivable_target_in_range()
func debug_campaign_contract()->Dictionary:
    return {
        "run_id":_run_id,
        "research_multiplier":_research_multiplier,
        "damage_multiplier":squad.operators[0].debug_campaign_damage_multiplier() if squad!=null and not squad.operators.is_empty() else 1.0,
        "wipe_common_retain_ratio":0.5,
        "high_value_lost_on_wipe":true,
        "signal_fragments_lost_on_wipe":true,
        "intel_samples_lost_on_wipe":true,
        "run_only_boosts_expire_on_return":true,
        "ledger_retained_on_wipe":true,
        "extraction_offer_ids":EXTRACTION_OFFER_IDS.duplicate()
    }
