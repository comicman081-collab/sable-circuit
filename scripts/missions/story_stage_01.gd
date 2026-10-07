extends Node2D
class_name StoryStage01
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
const DemoInput := preload("res://scripts/ui/demo_input.gd")

signal stage_completed(summary: Dictionary)
# Play-session log hooks (scripts/core/play_session_log.gd).
signal room_activated(room: Dictionary, step: int)
signal room_completed(room: Dictionary, step: int)
signal wave_spawned(room: Dictionary, wave_index: int, enemy_ids: Array)
signal hostile_defeated(enemy_id: String)
signal extraction_offered(room_id: String)
signal extraction_declined(room_id: String)

const MISSION_PATH := "res://data/missions/MIS_CH01_01.json"
@export var mission_id := "MIS_CH01_01"
var battle_preview := false
var _preview_cleared := false
signal return_requested
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const EXTRACTION_OFFER_IDS := ["R03_ARCHIVE", "R04_CONTAINMENT", "R05_CORE"]
const INTEL_KEYS := IntelSamples.KEYS
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
const DeployWarmer := preload("res://scripts/core/deploy_warmer.gd")
const WORLD_LAYOUT := preload("res://scripts/missions/site7_world_layout.gd")
const WORLD_X_SPACING := 6.0
const OPTIONAL_BRANCH_DROP := 1600.0

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
# Elite affixes seen in the current encounter, for the combat tips.
var _active_affix_ids: Array[String] = []
# Room hazards placed for the current encounter, for the combat tips.
var _active_hazard_ids: Array[String] = []
# The room rule of the current encounter (RoomRule.for_room; {} for almost every room), the seconds
# the room has been fought, and the HUD line last shown for it.
var _room_rule: Dictionary = {}
var _room_rule_clock := 0.0
var _room_rule_line := ""
var _encounter_waves: Array = []
var _wave_index := 0
var _wave_wait := 0.0
# Running spawn slot across all waves of the current encounter, so each new
# hostile takes a fresh point instead of stacking on the first three.
var _spawn_serial := 0
# Next wave arrives once this many hostiles (or fewer) remain; authored per
# room as "reinforce_at", 0 = only after the room is cleared (legacy).
var _reinforce_at := 0
var _elapsed_seconds := 0.0
var _defeated_count := 0

# Persistent campaign authority is separate from deployment-only run authority.
var _run_id := "UNCONFIGURED-RUN"
var _campaign_snapshot: Dictionary = {}
var _research_multiplier := 1.0
var _cargo_common_research := 0
var _cargo_unsecured_research := 0
var _cargo_salvage := 0
var _cargo_fragments := 0
var _cargo_intel: Dictionary = IntelSamples.empty()
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
@onready var battlefield: Node = $Battlefield

func _ready() -> void:
    add_to_group("sable_combat_audio_host")
    add_to_group("story_stage_01")
    _load_mission()
    _place_squad_at_entry()
    _apply_progress_bounds()
    hud.set_optional_status(_supply_found, _signal_found)
    _refresh_cargo_hud()
    queue_redraw()
    call_deferred("_activate_step")
    var guide := Site7FloorGuide.new()
    guide.name = "FloorGuide"
    add_child(guide)
    var controls := CanvasLayer.new()
    controls.name = "DemoControls"
    controls.set_script(preload("res://scripts/ui/demo_controls.gd"))
    add_child(controls)
    var debug_overlay := CanvasLayer.new()
    debug_overlay.name = "DebugOverlay"
    debug_overlay.set_script(preload("res://scripts/ui/debug_overlay.gd"))
    add_child(debug_overlay)
    PlaySessionLog.attach(self)

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

func _unhandled_key_input(event: InputEvent) -> void:
    if not battle_preview and event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE:
        hud.set_story("OPERATION ACTIVE // Extract at a recovery window, or reach the emergency lift. [F] INTERACT / [C] CONTINUE")
    if battle_preview and event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_ESCAPE:
            return_requested.emit()
        elif event.keycode == KEY_F6:
            start_battle_preview(current_step)
        elif event.keycode == KEY_F7:
            start_battle_preview(_next_preview_step())

func start_battle_preview(step_index: int = 1) -> void:
    if not battle_preview or main_route.size() < 2:
        return
    for node in get_tree().root.get_children():
        if node is PrototypeProjectile:
            var projectile := node as PrototypeProjectile
            if is_instance_valid(projectile.owner_actor) and is_ancestor_of(projectile.owner_actor):
                projectile.queue_free()
    _mission_ended = false
    _wave_wait = 0.0
    _extraction_offer_active = false
    _preview_cleared = false
    current_step = step_index if step_index in [1,3,4] else 1
    var room: Dictionary = main_route[current_step]
    var center := Vector2(float(room.x), float(room.y))
    battlefield.call("begin_encounter", room)
    for i in range(squad.operators.size()):
        var actor := squad.operators[i]
        actor.reset_for_battle_preview()
        actor.global_position = battlefield.call("squad_spawn", i)
        actor.aim_world = Vector2.RIGHT
    squad.request_control(0)
    _activate_step()
    debug_spawn_encounter_for_step(current_step)
    camera.position = center + Vector2(70, -10)
    hud.set_story("WASD MOVE / SHIFT RUN / LMB FIRE / R RELOAD / F6 RESET / F7 ENCOUNTER / ESC HELP")

func _next_preview_step() -> int:
    return 3 if current_step == 1 else (4 if current_step == 3 else 1)

func constrain_battle_position(point: Vector2) -> Vector2:
    return battlefield.call("constrain", point) if battlefield else point

func has_battle_floor() -> bool:
    return battlefield != null and bool(battlefield.get("world_ready"))

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
    # Configure before entering the tree. Campaign deployment defaults to S01.
    var path := "res://data/missions/%s.json" % mission_id
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if parsed is Dictionary:
        mission = parsed
        main_route = mission.get("main_route", [])
        optional_rooms = mission.get("optional_rooms", [])
        # Source mission coordinates describe the route graph, not the size of
        # its 1.3k-pixel environment plates. The world layout places every plate
        # so each connector deck runs into both rooms' painted floors.
        # Missions without a solved layout keep the old spaced-out placement.
        for room: Dictionary in main_route:
            room.x = float(room.x) * WORLD_X_SPACING
        for index in range(optional_rooms.size()):
            var room: Dictionary = optional_rooms[index]
            if not room.has("from"): room["from"] = str(main_route[mini(index + 2, main_route.size() - 1)].id)
            var parent := branch_parent(index)
            room.x = float(room.x) * WORLD_X_SPACING
            room.y = float(parent.y) + OPTIONAL_BRANCH_DROP
        var placed: Dictionary = WORLD_LAYOUT.mission_rooms(mission_id)
        for room: Dictionary in main_route + optional_rooms:
            if placed.has(str(room.id)):
                var at: Array = placed[str(room.id)]
                room.x = float(at[0])
                room.y = float(at[1])
        _warm_enemy_art()

## The main-route room optional room `index` branches from: its mission row's "from"
## (by default the room two ahead of it, as the first missions are built).
func branch_parent(index: int) -> Dictionary:
    var from := str((optional_rooms[index] as Dictionary).get("from", ""))
    for room: Dictionary in main_route:
        if str(room.id) == from: return room
    return main_route[mini(index + 2, main_route.size() - 1)]

## Every mission carries two optional recoveries: the supply cache (squad health and ammo) and the signal
## fragment. Operations 1-5 name their rooms O01_SUPPLY and O02_RESEARCH; later operations name them for the
## place (O01_STORES), so the kind is the room's own "type" ("SUPPLY" / "RESEARCH", which the campaign data
## gate requires in that order), else its legacy id, else its position. The result is always a legacy id,
## which is also the "source_room" the run-only boosts name.
const OPTIONAL_SUPPLY := "O01_SUPPLY"
const OPTIONAL_RESEARCH := "O02_RESEARCH"

static func optional_kind_of(room: Dictionary, index: int) -> String:
    match str(room.get("type", "")).to_upper():
        "SUPPLY": return OPTIONAL_SUPPLY
        "RESEARCH": return OPTIONAL_RESEARCH
    var room_id := str(room.get("id", ""))
    if room_id == OPTIONAL_SUPPLY or room_id == OPTIONAL_RESEARCH: return room_id
    return OPTIONAL_SUPPLY if index == 0 else OPTIONAL_RESEARCH

func optional_kind(index: int) -> String:
    return optional_kind_of(optional_rooms[index] as Dictionary, index)

func optional_recovered(index: int) -> bool:
    return _supply_found if optional_kind(index) == OPTIONAL_SUPPLY else _signal_found

## "EAST" or "WEST": the way the route leaves the entry room (a descending mission
## heads down and to the left).
func _route_heading() -> String:
    if main_route.size() < 2: return "EAST"
    return "WEST" if float(main_route[1].x) < float(main_route[0].x) else "EAST"

## Decode and verify every robot type this mission can spawn while it loads; done at the
## first spawn instead, it froze combat about a second per new type. GameFlow usually has
## DeployWarmer load it on the menus, which leaves only cache hits here.
func _warm_enemy_art() -> void:
    DeployWarmer.finish()
    for identity in DeployWarmer.room_enemy_ids(main_route + optional_rooms):
        EnemyActor.warm_art(identity)

func _place_squad_at_entry() -> void:
    if main_route.is_empty() or squad == null: return
    var entry: Dictionary = main_route[0]
    var center := Vector2(float(entry.x), float(entry.y))
    for index in range(squad.operators.size()):
        squad.operators[index].global_position = center + SquadController.FORMATION_OFFSETS[index]

func _process(_delta: float) -> void:
    if _mission_ended:
        return
    _elapsed_seconds += _delta
    if _wave_wait > 0.0:
        queue_redraw()
        _wave_wait = maxf(0.0, _wave_wait - _delta)
        if _wave_wait <= 0.0:
            _spawn_wave(main_route[current_step])
    _tick_room_rule(_delta)
    if _all_squad_downed():
        _finish_mission("WIPED")
        return

    if battle_preview:
        var next_pressed := DemoInput.key(KEY_F)
        if _preview_cleared and next_pressed and not _interact_latch:
            start_battle_preview(_next_preview_step())
        _interact_latch = next_pressed
        return

    # M12: F is shared by field interaction and manual revive. A nearby downed
    # squadmate always reserves F first. Latches still follow the held key so a
    # completed revive cannot accidentally extract/interact without release+press.
    var revive_reserved := squad != null and squad.has_revivable_target_in_range()
    if _extraction_offer_active:
        var extract_pressed := DemoInput.key(KEY_F)
        var continue_pressed := DemoInput.key(KEY_C)
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
    # The opening access beat is not a combat gate. Requiring a separate F tap
    # left normal web deployments in an empty "AREA SECURE" room indefinitely,
    # while the training shortcut skipped this path entirely. Arm the first
    # authored encounter as soon as the continuous floor is ready on every
    # campaign mission; later research/extraction interactions still use F.
    if current_step == 0 and battlefield.world_ready and str(main_route[0].get("type", "")) == "EVENT":
        _handle_interaction(active, true)
    _check_current_room_entry(active)
    var interact_pressed := DemoInput.key(KEY_F)
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

func objective_action_state() -> Dictionary:
    if battle_preview or _mission_ended or _combat_started or _extraction_offer_active or current_step >= main_route.size():
        return {"visible":false}
    var actor := squad.get_active_operator()
    if actor == null: return {"visible":false}
    var row: Dictionary = main_route[current_step]
    var distance := actor.global_position.distance_to(Vector2(float(row.x),float(row.y)))
    var interaction := str(row.type) in ["EVENT","RESEARCH","EXTRACTION"]
    var ready := distance <= 175.0 and interaction
    # The first normal deployment must visibly lead into playable combat. The
    # old generic confirmation then required an unmarked walk before any
    # hostile could appear.
    var opening_gate := current_step == 0 and str(row.get("id", "")) == "R01_ENTRY"
    var text := "F / CONFIRM OBJECTIVE" if ready else "MOVE TO MARKER / %dm" % maxi(1, int(distance/10.0))
    if opening_gate:
        text = "F / ACTIVATE ACCESS" if ready else "ACCESS TERMINAL / %dm" % maxi(1, int(distance/10.0))
    if not interaction: text = "ENTER COMBAT ZONE / %dm" % maxi(1,int(distance/10.0))
    return {"visible":true,"enabled":ready,"text":text}

func use_objective_action() -> void:
    if bool(objective_action_state().get("enabled",false)) and not squad.has_revivable_target_in_range():
        _handle_interaction(squad.get_active_operator())

func _check_current_room_entry(active: OperatorActor) -> void:
    if current_step < 0 or current_step >= main_route.size(): return
    var node: Dictionary = main_route[current_step]
    var room_pos := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    if active.global_position.distance_to(room_pos) > 175.0: return
    var kind := str(node.get("type", "EVENT"))
    if kind in ["COMBAT", "ELITE", "BOSS"] and not _combat_started: _spawn_combat(node)

func _handle_interaction(active: OperatorActor, auto_opening: bool = false) -> void:
    if current_step < main_route.size():
        var node: Dictionary = main_route[current_step]
        var room_pos := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
        if active.global_position.distance_to(room_pos) <= 175.0 or (auto_opening and current_step == 0):
            var kind := str(node.get("type", "EVENT"))
            if kind in ["EVENT", "RESEARCH"]:
                var opening_gate := current_step == 0 and kind == "EVENT"
                if str(node.get("id", "")) == str(MissionCatalog.get_mission(mission_id).get("evidence_room", "R03_ARCHIVE")): _ledger_recovered = true
                hud.set_story(str(node.get("story", "Objective complete.")))
                hud.show_transmission(str(node.get("title", "FIELD LOG")).to_upper() + " // " + str(node.get("story", "Objective complete.")))
                _complete_step()
                # Start the first encounter at its authored world coordinates as
                # soon as access is activated. The enemies travel through the
                # same map; the squad does not teleport or switch backgrounds.
                if opening_gate:
                    if current_step < main_route.size() and str(main_route[current_step].get("type", "")) == "COMBAT":
                        _spawn_combat(main_route[current_step])
                    hud.set_story("ACCESS ROUTE ACTIVE // HOSTILES AHEAD. FOLLOW THE %s DECK." % _route_heading())
                return
            if kind == "EXTRACTION":
                _completed_depth = maxi(_completed_depth, current_step + 1)
                hud.set_story(str(node.get("story", "Extraction confirmed.")))
                _finish_mission("EXTRACTED"); return
    if current_step >= 2:
        for index in range(optional_rooms.size()):
            var room: Dictionary = optional_rooms[index]
            var kind := optional_kind(index)
            if optional_recovered(index): continue
            var room_pos := Vector2(float(room.get("x", 0)), float(room.get("y", 0)))
            if active.global_position.distance_to(room_pos) <= 150.0:
                if kind == OPTIONAL_SUPPLY:
                    _supply_found = true
                    if room.has("loot"): _award_authored_loot(room.loot)
                    else:
                        _cargo_common_research += 20
                        _cargo_salvage += 2
                    for member in squad.operators:
                        if not member.is_downed():
                            member.heal(member.max_health * 0.35)
                            member.ammo = member.magazine_size
                elif kind == OPTIONAL_RESEARCH:
                    _signal_found = true
                    if room.has("loot"): _award_authored_loot(room.loot)
                    else:
                        _cargo_unsecured_research += 40
                        _cargo_fragments += 1
                var boost_id := _activate_run_boost_for_room(kind)
                var boost_suffix := ""
                if not boost_id.is_empty(): boost_suffix = " // RUN BOOST " + boost_id
                hud.set_story("OPTIONAL RECOVERY // " + str(room.get("story", "Recovered.")) + boost_suffix)
                hud.show_transmission("RECOVERY // " + str(room.get("story", "Recovered.")) + (" Squad health +35%, magazines replenished." if kind == OPTIONAL_SUPPLY else " Signal fragment secured in field cargo."))
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
    _combat_started = true; enemies_alive = 0; _active_enemy_ids.clear(); _active_affix_ids.clear()
    battlefield.call("begin_encounter", node)
    _place_hazards(node)
    _begin_room_rule(node)
    # Normal campaign never teleports the squad at an encounter boundary.
    _encounter_waves = [node.get("encounter", [])]
    if not battle_preview:
        _encounter_waves.append_array(node.get("reinforcements", []))
    _wave_index = 0
    _wave_wait = 0.0
    _spawn_serial = 0
    _reinforce_at = int(node.get("reinforce_at", 0)) if not battle_preview else 0
    _apply_progress_bounds()
    _spawn_wave(node)

func _spawn_wave(node: Dictionary) -> void:
    var center := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
    var kind := str(node.get("type", "COMBAT"))
    preload("res://scripts/audio/demo_music.gd").encounter(get_tree(), mission_id, kind == "BOSS")
    var encounter: Array = _encounter_waves[_wave_index]
    if encounter.is_empty(): push_error("StoryStage01 encounter missing for " + str(node.get("id", "?"))); return
    var spawned_ids: Array = []
    for row_variant in encounter:
        if not (row_variant is Dictionary): continue
        var row: Dictionary = row_variant
        var identity := str(row.get("enemy_id", ""))
        if ArtProfileRegistry.get_profile(identity).is_empty(): push_error("StoryStage01 unknown enemy profile: " + identity); continue
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        if not enemy.configure(identity, float(row.get("health", 100.0))):
            enemy.free()
            continue
        enemy.apply_run_modifiers(RunContract.enemy_modifiers(_enemy_run_modifiers_with_mode(), identity))
        var affix := EliteAffix.apply(enemy, str(row.get("affix", "")))
        if affix != null and not affix.affix_id in _active_affix_ids: _active_affix_ids.append(affix.affix_id)
        enemy.position = center + Vector2(float(row.get("offset_x", 70.0)), float(row.get("offset_y", 0.0)))
        if has_battle_floor():
            if not battle_preview and mission_id == "MIS_CH01_01" and current_step == 1 and _wave_index == 0 and enemies_alive < 2:
                enemy.position = battlefield.call("opening_patrol_spawn", enemies_alive)
            else:
                enemy.position = battlefield.call("enemy_spawn", _spawn_serial)
        enemy.defeated.connect(_on_story_enemy_defeated); add_child(enemy)
        # Alternate orbit direction per spawn so same-type robots fan out
        # around the squad instead of circling as one stacked silhouette.
        enemy._orbit_sign = -1.0 if _spawn_serial % 2 == 0 else 1.0
        _spawn_serial += 1
        enemies_alive += 1; _active_enemy_ids.append(identity); spawned_ids.append(identity)
    wave_spawned.emit(node, _wave_index, spawned_ids)
    hud.set_story(_combat_story(kind)); hud.set_combat_status(enemies_alive)
    if _wave_index == 0 and not battle_preview: hud.show_transmission(_combat_story(kind), 7.0)
    if _encounter_waves.size() > 1:
        hud.set_objective("%s / WAVE %d-%d" % [str(node.get("objective", "Clear hostiles")), _wave_index + 1, _encounter_waves.size()], false)
    queue_redraw()

func _combat_story(kind: String) -> String:
    var room: Dictionary = main_route[current_step]
    var heading := str(room.get("title", "SITE-7")).to_upper() + " // "
    if kind == "BOSS":
        for node in get_tree().get_nodes_in_group("m3_enemies"):
            if node is EnemyActor and "BOSS" in node.enemy_id:
                return heading + str(node.art_profile.get("boss_brief", "Central iris active. Evade the announced fan and floor blast; reposition while CORE SHIELDED is active."))
        return heading + "Central iris active. Evade the announced fan and floor blast; reposition while CORE SHIELDED is active."
    var tips: PackedStringArray = []
    if "ENM_SITE7_MORTAR_01" in _active_enemy_ids: tips.append("VESPER: leave the violet landing circle; blasts bypass cover.")
    if "ENM_SITE7_NULL_PYLON_01" in _active_enemy_ids: tips.append("NULL PYLON: leave the cyan lens circle; the jammer shot ignores cover.")
    if "ENM_SITE7_PRISM_01" in _active_enemy_ids: tips.append("PRISM: its pulse emitter follows the authored facing; flank the ion ring.")
    if "ENM_SITE7_RAM_01" in _active_enemy_ids: tips.append("CINDER: sidestep the orange charge lane; cover stops its rush.")
    if "ENM_SITE7_BULWARK_01" in _active_enemy_ids: tips.append("BULWARK: flank its front armor or stagger it.")
    if tips.is_empty(): tips.append("Recon drones active. Use cover against their announced shots.")
    for hazard_id in _active_hazard_ids: tips.append(ZoneHazard.tip(hazard_id))
    for affix_id in _active_affix_ids: tips.append(EliteAffix.tip(affix_id))
    if not _room_rule.is_empty(): tips.append(RoomRule.tip(str(_room_rule.type)))
    return heading + " ".join(tips)

## The room's declared rule (data/progression/room_rules.json), if it declares a usable one. Rooms
## without a "rule" key, boss rooms and the training simulator run exactly as before.
func _begin_room_rule(node: Dictionary) -> void:
    _room_rule = {}
    _room_rule_clock = 0.0
    _set_room_rule_line("")
    if battle_preview or not node.has("rule"): return
    for line in RoomRule.problems(node): push_error("StoryStage01 " + line)
    _room_rule = RoomRule.for_room(node)

func _tick_room_rule(delta: float) -> void:
    if _room_rule.is_empty() or not _combat_started: return
    _room_rule_clock += delta
    if RoomRule.overrun_due(_room_rule, _room_rule_clock, _wave_pending(), _wave_wait): _call_reinforcements()
    _refresh_room_rule_line()

## The HUD line follows the clock and the wave state; no rule (or a hidden line) means an empty line.
func _refresh_room_rule_line() -> void:
    _set_room_rule_line(RoomRule.hud_line(_room_rule, _room_rule_clock, _wave_pending(), _wave_wait))

func _set_room_rule_line(line: String) -> void:
    if line == _room_rule_line: return
    _room_rule_line = line
    hud.set_room_rule(line)

func _wave_pending() -> bool:
    return _wave_index + 1 < _encounter_waves.size()

## Calls the next wave in: the marked-entry wait comes first, then _process spawns it. Called when the
## room is thinned out to reinforce_at (_on_story_enemy_defeated) and by a room rule's timer, which
## counts its seconds from the wave called last.
func _call_reinforcements() -> void:
    _wave_index += 1
    _room_rule_clock = 0.0
    _wave_wait = 1.4 if enemies_alive > 0 else 2.2
    hud.set_objective("REINFORCEMENTS / WAVE %d-%d" % [_wave_index + 1, _encounter_waves.size()], false)
    hud.set_story("HOSTILE SIGNALS INBOUND // Reposition and reload. Entry points marked on the floor.")
    _refresh_room_rule_line()
    queue_redraw()

## Room hazards declared on the encounter row ("hazards": [{"type", "count"}]), placed by
## the battlefield on open floor. A room without a battle floor gets none.
func _place_hazards(node: Dictionary) -> void:
    _clear_hazards()
    var index := 0
    var reserved: Array[Dictionary] = []
    var requests: Array[Dictionary] = []
    for row_variant in node.get("hazards", []):
        if not (row_variant is Dictionary): continue
        var row: Dictionary = row_variant
        var id := str(row.get("type", "")).strip_edges().to_upper()
        if not ZoneHazard.table().has(id):
            push_error("StoryStage01 unknown hazard: " + id)
            continue
        if not has_battle_floor(): continue
        var radius := float((ZoneHazard.table()[id] as Dictionary).get("radius", 70.0))
        requests.append({"id": id, "radius": radius, "count": int(row.get("count", 1)), "order": requests.size(), "band": str((ZoneHazard.table()[id] as Dictionary).get("shape", "ellipse")) == "band"})
    # Place the broadest reservation first. Equal radii retain declaration order
    # (and a single ARC row retains its original positions and phase indices).
    requests.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
        return int(a.order) < int(b.order) if is_equal_approx(float(a.radius), float(b.radius)) else float(a.radius) > float(b.radius))
    for request in requests:
        var id := str(request.id)
        var radius := float(request.radius)
        var declared := int(request.count)
        var points: Array[Vector2] = battlefield.call("hazard_points", declared, radius, reserved, bool(request.band))
        if points.size() != declared:
            push_error("StoryStage01 hazard placement %s: %d of %d" % [id, points.size(), declared])
        for point in points:
            add_child(ZoneHazard.create(id, point, index))
            reserved.append({"point": point, "radius": radius})
            index += 1
        if not points.is_empty() and not id in _active_hazard_ids: _active_hazard_ids.append(id)

func _clear_hazards() -> void:
    for node in get_tree().get_nodes_in_group("zone_hazards"):
        if is_ancestor_of(node):
            if node.has_method("release_effects"): node.release_effects()
            node.remove_from_group("zone_hazards")
            node.queue_free()
    _active_hazard_ids.clear()

## Reserve both plain hatchlings before the parent's defeated signal decrements
## enemies_alive. Even the last BROODING robot therefore cannot open the room early.
func spawn_elite_brood(parent_enemy: EnemyActor, spec: Dictionary) -> Array[EnemyActor]:
    var children: Array[EnemyActor] = []
    if _mission_ended or not _combat_started or parent_enemy.brood_generation > 0: return children
    var points := brood_spawn_points(parent_enemy, 2)
    if points.size() != 2:
        push_error("BROODING could not place two hatchlings on nearby open floor")
        return children
    # Parent max health already has the contract. Restore authored HP first,
    # then pass each child's authored share through the normal modifier path once.
    var authored_parent_hp := parent_enemy.max_health / parent_enemy.run_health_multiplier
    var authored_hp := authored_parent_hp * float(spec.get("brood_health_ratio", 0.25))
    for index in range(2):
        var child := ENEMY_SCENE.instantiate() as EnemyActor
        if not child.configure("ENM_SITE7_DRONE_01", authored_hp):
            child.free()
            for pending in children: pending.free()
            children.clear()
            push_error("BROODING drone profile is not available")
            return children
        child.apply_run_modifiers(_enemy_run_modifiers)
        child.brood_generation = 1
        child.brood_hatch_duration = maxf(0.6, float(spec.get("brood_hatch_windup", 0.6)))
        child.brood_hatch_left = child.brood_hatch_duration
        child.set_meta("brood_parent_id", parent_enemy.get_instance_id())
        child.position = to_local(points[index])
        child.defeated.connect(_on_story_enemy_defeated)
        children.append(child)
    enemies_alive += children.size()
    for index in range(children.size()):
        var child := children[index]
        add_child(child)
        child._orbit_sign = -1.0 if index == 0 else 1.0
        _active_enemy_ids.append(child.enemy_id)
    hud.set_combat_status(enemies_alive)
    return children

## Search deterministically around the parent's painted-floor position. The
## collider footprint, rather than just its centre, must clear floor and cover.
func brood_spawn_points(parent_enemy: EnemyActor, count: int) -> Array[Vector2]:
    var result: Array[Vector2] = []
    var nav := preload("res://scripts/combat/cover_navigation.gd")
    var obstacles: Array[Rect2] = nav.ground_obstacles(parent_enemy)
    for radius: float in [32.0, 48.0, 72.0, 104.0, 144.0, 192.0, 256.0, 320.0]:
        for index in range(24):
            var point := parent_enemy.global_position + Vector2.RIGHT.rotated(TAU * float(index) / 24.0) * radius
            if not _brood_spawn_fits(parent_enemy, point, obstacles): continue
            var separated := true
            for prior in result:
                if prior.distance_to(point) < 44.0: separated = false; break
            if not separated: continue
            result.append(point)
            if result.size() == count: return result
    return result

func _brood_spawn_fits(parent_enemy: EnemyActor, point: Vector2, obstacles: Array[Rect2]) -> bool:
    var nav := preload("res://scripts/combat/cover_navigation.gd")
    if not nav._on_floor(parent_enemy, point): return false
    for obstacle in obstacles:
        if obstacle.has_point(point): return false
    var collider := parent_enemy.get_node_or_null("CollisionShape2D") as CollisionShape2D
    var center := point + (collider.position if collider != null else Vector2.ZERO)
    var extent := Vector2(21, 21)
    if collider != null and collider.shape != null:
        extent = collider.shape.get_rect().size * collider.scale.abs() * 0.5 + Vector2(3, 3)
    for index in range(16):
        var rim := center + Vector2.RIGHT.rotated(TAU * float(index) / 16.0) * extent
        if not nav._on_floor(parent_enemy, rim): return false
        if has_battle_floor() and not Geometry2D.is_point_in_polygon(rim, battlefield._walk_polygon): return false
    return true

func _on_story_enemy_defeated(enemy: EnemyActor) -> void:
    if _mission_ended: return
    _defeated_count += 1
    hostile_defeated.emit(enemy.enemy_id)
    _award_enemy_intel(enemy.enemy_id)
    _active_enemy_ids.erase(enemy.enemy_id)
    enemies_alive = maxi(0, enemies_alive - 1)
    hud.set_combat_status(enemies_alive)
    # Reinforcements keep pressure on: they are called in while the last few
    # hostiles of the previous wave are still fighting (reinforce_at), or once
    # the room is clear in rooms without that setting.
    if _wave_wait <= 0.0 and _wave_pending() and enemies_alive <= _reinforce_at:
        _call_reinforcements()
        return
    if enemies_alive == 0:
        if _wave_wait > 0.0:
            return
        _combat_started = false
        _clear_hazards()
        _room_rule = {}
        _set_room_rule_line("")
        preload("res://scripts/audio/demo_music.gd").encounter(get_tree(), mission_id, false)
        hud.set_story("AREA SECURE // Intel samples tagged. Route lock released.")
        if battle_preview:
            _preview_cleared = true
            hud.set_objective("Sector secured. [F] Next encounter", false)
            hud.set_story("AREA SECURE / F NEXT ENCOUNTER / F6 REPLAY / ESC RETURN")
            return
        battlefield.call("release")
        _complete_step()

func _award_enemy_intel(enemy_id: String) -> void:
    var id := enemy_id.to_upper()
    if _intel_seen_enemy_ids.has(id): return
    _intel_seen_enemy_ids.append(id)
    var key := IntelSamples.enemy_key(id)
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
    if current_step == 0 and str(node.get("id", "")) == "R01_ENTRY":
        hud.set_story("SEALED BULKHEAD // [F] ACTIVATE THE %s DECK ACCESS ROUTE." % _route_heading())
    elif kind in ["EVENT", "RESEARCH", "EXTRACTION"]: hud.set_story("Move into the marked room and press F to interact.")
    else: hud.set_story("Advance into the marked room. Combat locks progression until every unique hostile in the authored encounter is down.")
    _apply_progress_bounds(); queue_redraw()
    room_activated.emit(node, current_step)

func _complete_step() -> void:
    if current_step < 0 or current_step >= main_route.size(): return
    var completed_node: Dictionary = main_route[current_step]
    room_completed.emit(completed_node, current_step)
    _award_main_route_reward(completed_node)
    _completed_depth = maxi(_completed_depth, current_step + 1)
    if str(completed_node.get("id", "")) in mission.get("extraction_offer_room_ids", EXTRACTION_OFFER_IDS):
        _offer_extraction(completed_node)
        return
    current_step += 1
    if current_step < main_route.size(): _activate_step()

func _award_main_route_reward(node: Dictionary) -> void:
    if node.has("loot"):
        _award_authored_loot(node.loot)
        _refresh_cargo_hud()
        return
    var kind := str(node.get("type", "EVENT"))
    match kind:
        "EVENT": _cargo_common_research += 10
        "COMBAT": _cargo_common_research += 25
        "RESEARCH": _cargo_common_research += 45
        "ELITE": _cargo_common_research += 35
        "BOSS": _cargo_unsecured_research += 45
    _refresh_cargo_hud()

func _award_authored_loot(loot: Array) -> void:
    for row: Dictionary in loot:
        var amount := maxi(0, int(row.get("quantity", 0)))
        match str(row.get("loot_id", "")):
            "LOT_RESEARCH_COMMON": _cargo_common_research += amount
            "LOT_RESEARCH_HIGH_VALUE": _cargo_unsecured_research += amount
            "LOT_SALVAGE_FIELD": _cargo_salvage += amount
            "LOT_SIGNAL_FRAGMENT": _cargo_fragments += amount
            # Legacy save key retained; sample now comes from robot research,
            # not the retired humanoid/organic enemy roster.
            "LOT_INTEL_MECHANICAL": _cargo_intel["ABERRANT"] += amount

func _offer_extraction(node: Dictionary) -> void:
    _extraction_offer_active = true
    _extraction_offer_room = str(node.get("id", ""))
    _extract_latch = DemoInput.key(KEY_F)
    _continue_latch = DemoInput.key(KEY_C)
    hud.set_extraction_offer(true, _completed_depth, _cargo_common_research + _cargo_unsecured_research)
    hud.set_story("EXTRACTION WINDOW // [F] secure cargo + intel now   [C] continue deeper and keep samples at risk.")
    hud.set_objective("Choose extraction or continue deeper", false)
    _apply_progress_bounds()
    extraction_offered.emit(_extraction_offer_room)

func _continue_after_extraction_offer() -> void:
    if not _extraction_offer_active: return
    _extraction_offer_active = false
    extraction_declined.emit(_extraction_offer_room)
    _extraction_offer_room = ""
    _extract_latch = false
    _continue_latch = true
    current_step += 1
    if current_step < main_route.size(): _activate_step()

func _apply_progress_bounds() -> void:
    if main_route.is_empty(): return
    # Progression gates objectives, never an invisible rectangle in open space.
    # The painted floor keeps actors on the map; this only has to contain it.
    var art := get_node_or_null("RoomArtLayer")
    var bounds: Rect2 = art.get("_world_bounds") if art else Rect2()
    if bounds.size == Vector2.ZERO:
        var first: Dictionary = main_route[0]
        var last: Dictionary = main_route[-1]
        bounds = Rect2(Vector2(float(first.x) - 750.0, -350.0), Vector2(float(last.x - first.x) + 1500.0, OPTIONAL_BRANCH_DROP + 1500.0))
    else:
        bounds = bounds.grow(200.0)
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
    var secured_intel := IntelSamples.empty()
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
        "battle_preview": battle_preview,
        "evidence_label": MissionCatalog.get_mission(mission_id).get("evidence_label", "MISSION EVIDENCE"),
        "chapter_id": mission.get("chapter_id", "CH01"),
        "transaction_id": _run_id,
        "run_id": _run_id,
        "outcome": outcome.to_upper(),
        "elapsed_seconds": _elapsed_seconds,
        "hostiles_defeated": _defeated_count,
        "full_route_cleared": not wiped and _completed_depth == main_route.size(),
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
        "lost_intel_samples": 0 if not wiped else IntelSamples.total(_cargo_intel),
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
    _clear_hazards()
    _extraction_offer_active = false
    hud.set_extraction_offer(false, 0, 0)
    stage_completed.emit(_build_summary(outcome))

func _draw() -> void:
    if _wave_wait > 0.0 and battlefield:
        for index in range((_encounter_waves[_wave_index] as Array).size()):
            var entry: Vector2 = battlefield.call("enemy_spawn", _spawn_serial + index)
            draw_arc(entry, 28.0, 0.0, TAU, 32, Color("ee9979",0.75), 2.0)
            draw_line(entry + Vector2(-9,-9), entry + Vector2(9,9), Color("ee9979",0.65), 1.5)
            draw_line(entry + Vector2(9,-9), entry + Vector2(-9,9), Color("ee9979",0.65), 1.5)
    for i in range(main_route.size()):
        var node: Dictionary = main_route[i]
        var p := Vector2(float(node.get("x", 0)), float(node.get("y", 0)))
        if i < main_route.size() - 1:
            var next_node: Dictionary = main_route[i + 1]
            var np := Vector2(float(next_node.get("x", 0)), float(next_node.get("y", 0)))
            draw_line(p, np, Color(0.18,0.34,0.40,0.035 if i >= current_step else 0.065), 2.0)
        _draw_room_marker(node, i, i <= current_step)
    for index in range(optional_rooms.size()):
        var room: Dictionary = optional_rooms[index]
        var parent_row := branch_parent(index)
        var parent_p := Vector2(float(parent_row.get("x", 0)), float(parent_row.get("y", 0)))
        var room_p := Vector2(float(room.get("x", 0)), float(room.get("y", 0)))
        var dir := (room_p-parent_p).normalized()
        draw_line(parent_p+dir*78.0, room_p-dir*68.0, Color(0.20,0.42,0.46,0.055), 2.0)
        _draw_optional_marker(room, optional_recovered(index))

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
func debug_seed_intel(security:int,aberrant:int,anchor:int,extra:Dictionary={})->void:
    _cargo_intel=IntelSamples.sanitize(extra)
    _cargo_intel["SECURITY"]=maxi(0,security); _cargo_intel["ABERRANT"]=maxi(0,aberrant); _cargo_intel["ANCHOR"]=maxi(0,anchor); _refresh_cargo_hud()
func debug_extraction_summary(room_id:String="DEBUG_EXTRACTION")->Dictionary:
    _extraction_offer_room=room_id; return _build_summary("EXTRACTED")
func debug_wipe_summary()->Dictionary: return _build_summary("WIPED")
func debug_offer_extraction(room_id:String="R03_ARCHIVE")->void:
    _extraction_offer_active=true; _extraction_offer_room=room_id; hud.set_extraction_offer(true,_completed_depth,_cargo_common_research+_cargo_unsecured_research)
func debug_continue_extraction()->void: _continue_after_extraction_offer()
func debug_extraction_active()->bool: return _extraction_offer_active
func debug_intel_cargo()->Dictionary: return _cargo_intel.duplicate(true)
func debug_run_contract()->Dictionary: return _run_contract.duplicate(true)

func _enemy_run_modifiers_with_mode() -> Dictionary:
    var modifiers := _enemy_run_modifiers.duplicate()
    modifiers["hazard_id"] = _run_contract.get("hazard_id", "")
    modifiers["opportunity_id"] = _run_contract.get("opportunity_id", "")
    return modifiers
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
        "extraction_offer_ids":mission.get("extraction_offer_room_ids", EXTRACTION_OFFER_IDS).duplicate()
    }
