extends Node
class_name PlaySessionLog
## Play-session record for balance tuning: one JSON file per deployment with per-room time,
## damage taken by enemy type, downs and revives, skills, shots and hits, kills and the
## extraction choice. A run from the project folder writes <project>/playtest_logs/, an
## exported native build user://playtest_logs/. Web, headless and test-script (-s) runs
## record nothing unless a test passes an explicit folder.

const SCHEMA := 1
const EVENT_LIMIT := 20000

var output_dir := ""
var written_path := ""
var _stage: StoryStage01
var _start_msec := 0
var _started_utc := ""
var _events: Array = []
var _dropped_events := 0
var _rooms: Array = []
var _room: Dictionary = {}
var _totals: Dictionary = {}

static func default_output_dir() -> String:
    if OS.has_feature("web") or DisplayServer.get_name() == "headless": return ""
    # A -s test script replaces the plain SceneTree main loop; only real play is recorded.
    if Engine.get_main_loop().get_script() != null: return ""
    if OS.has_feature("template"): return "user://playtest_logs"
    return ProjectSettings.globalize_path("res://playtest_logs")

static func attach(stage: StoryStage01, forced_dir: String = "") -> PlaySessionLog:
    var folder := forced_dir if not forced_dir.is_empty() else default_output_dir()
    if folder.is_empty(): return null
    var session_log := PlaySessionLog.new()
    session_log.name = "PlaySessionLog"
    session_log.output_dir = folder
    stage.add_child(session_log)
    return session_log

static func _bucket() -> Dictionary:
    return {"damage_taken": 0.0, "damage_taken_by_source": {}, "downs": 0, "revives": 0,
        "skills": {}, "shots": 0, "player_shots": 0, "hits": 0, "player_hits": 0,
        "damage_dealt": 0.0, "kills": {}}

func _ready() -> void:
    _stage = get_parent() as StoryStage01
    _start_msec = Time.get_ticks_msec()
    _started_utc = Time.get_datetime_string_from_system(true)
    _totals = _bucket()
    if _stage == null: return
    _stage.room_activated.connect(_on_room_activated)
    _stage.room_completed.connect(_on_room_completed)
    _stage.wave_spawned.connect(_on_wave_spawned)
    _stage.hostile_defeated.connect(_on_hostile_defeated)
    _stage.extraction_offered.connect(func(room_id: String) -> void: _event("extraction_offered", {"room": room_id}))
    _stage.extraction_declined.connect(func(room_id: String) -> void: _event("extraction_declined", {"room": room_id}))
    _stage.stage_completed.connect(_on_stage_completed)
    if _stage.squad != null:
        _stage.squad.revive_completed.connect(_on_revived)
        for actor in _stage.squad.operators:
            actor.damage_taken.connect(_on_damage_taken)
            actor.downed.connect(_on_downed)
            actor.primary_fired.connect(_on_primary_fired)
            actor.hit_landed.connect(_on_hit_landed)
            var skills := actor.get_node_or_null("SkillController") as OperatorSkillController
            if skills != null: skills.skill_cast.connect(_on_skill_cast)
    _event("deploy", {"mission": _stage.mission_id, "preview": _stage.battle_preview})

func _exit_tree() -> void:
    # Quitting or returning mid-mission still leaves a record of what was played.
    if written_path.is_empty() and _stage != null and not _events.is_empty():
        write("ABANDONED", {})

func _now() -> float:
    return snappedf((Time.get_ticks_msec() - _start_msec) / 1000.0, 0.01)

func _event(kind: String, data: Dictionary = {}) -> void:
    if _events.size() >= EVENT_LIMIT:
        _dropped_events += 1
        return
    var row := {"t": _now(), "event": kind}
    if not _room.is_empty(): row["room"] = _room.id
    row.merge(data)
    _events.append(row)

func _add(key: String, amount: Variant = 1, sub_key: String = "") -> void:
    for bucket in ([_totals, _room] if not _room.is_empty() else [_totals]):
        if sub_key.is_empty():
            bucket[key] = bucket[key] + amount
        else:
            var table: Dictionary = bucket[key]
            table[sub_key] = table.get(sub_key, 0) + amount

func _on_room_activated(room: Dictionary, step: int) -> void:
    _close_room(false)
    _room = _bucket()
    _room.merge({"id": str(room.get("id", "")), "type": str(room.get("type", "")), "step": step,
        "entered_at": _now(), "cleared_at": -1.0, "seconds": 0.0, "waves": []})
    _rooms.append(_room)
    _event("room_enter", {"type": _room.type, "step": step})

func _on_room_completed(room: Dictionary, _step: int) -> void:
    if _room.is_empty() or _room.id != str(room.get("id", "")): return
    _room.cleared_at = _now()
    _event("room_clear", {"seconds": snappedf(_room.cleared_at - _room.entered_at, 0.01)})

func _close_room(_ended: bool) -> void:
    if _room.is_empty(): return
    var end: float = _room.cleared_at if _room.cleared_at >= 0.0 else _now()
    _room.seconds = snappedf(end - _room.entered_at, 0.01)

func _on_wave_spawned(_room_data: Dictionary, wave_index: int, enemy_ids: Array) -> void:
    if not _room.is_empty(): _room.waves.append({"wave": wave_index, "at": _now(), "enemies": enemy_ids.duplicate()})
    _event("wave", {"wave": wave_index, "enemies": enemy_ids.duplicate()})

func _on_hostile_defeated(enemy_id: String) -> void:
    _add("kills", 1, enemy_id)
    _event("kill", {"enemy": enemy_id})

func _on_damage_taken(actor: OperatorActor, applied: float, source_id: String) -> void:
    var source := source_id if not source_id.is_empty() else "UNKNOWN"
    _add("damage_taken", applied)
    _add("damage_taken_by_source", applied, source)
    _event("damage", {"operator": actor.operator_id, "amount": snappedf(applied, 0.01), "source": source,
        "health": snappedf(actor.health, 0.1)})

func _on_downed(actor: OperatorActor) -> void:
    _add("downs")
    _event("down", {"operator": actor.operator_id})

func _on_revived(target: OperatorActor) -> void:
    _add("revives")
    _event("revive", {"operator": target.operator_id})

func _on_skill_cast(actor: OperatorActor, slot: String, skill_id: String, hits: int) -> void:
    _add("skills", 1, skill_id)
    _event("skill", {"operator": actor.operator_id, "slot": slot, "skill": skill_id, "hits": hits})

func _on_primary_fired(actor: OperatorActor) -> void:
    _add("shots")
    if actor.controlled: _add("player_shots")

func _on_hit_landed(actor: OperatorActor, target_id: String, applied_damage: float) -> void:
    _add("hits")
    _add("damage_dealt", applied_damage)
    if actor.controlled: _add("player_hits")

func _on_stage_completed(summary: Dictionary) -> void:
    write(str(summary.get("outcome", "UNKNOWN")), summary)

func write(outcome: String, summary: Dictionary) -> String:
    _close_room(true)
    _event("end", {"outcome": outcome})
    var record := {
        "schema": SCHEMA,
        "mission_id": _stage.mission_id if _stage != null else "",
        "run_id": _stage._run_id if _stage != null else "",
        "contract_id": RunContract.identity(_stage.debug_run_contract()) if _stage != null else "NEUTRAL",
        "redline": RunContract.is_redline(_stage.debug_run_contract()) if _stage != null else false,
        "outcome": outcome,
        "battle_preview": _stage.battle_preview if _stage != null else false,
        "started_utc": _started_utc,
        "duration_seconds": _now(),
        "early_extraction": bool(summary.get("early_extraction", false)),
        "extraction_room": str(summary.get("extraction_room", "")),
        "hostiles_defeated": int(summary.get("hostiles_defeated", 0)),
        "totals": _totals,
        "rooms": _rooms,
        "events": _events,
        "dropped_events": _dropped_events,
        "human_playtest": true,
    }
    var folder := output_dir
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder))
    var stamp := Time.get_datetime_string_from_system(false, true).replace("-", "").replace(":", "").replace(" ", "_")
    var path := "%s/%s_%s_%s.json" % [folder, stamp, record.mission_id, outcome]
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        push_warning("PlaySessionLog could not write " + path)
        return ""
    file.store_string(JSON.stringify(record, "  "))
    file.close()
    written_path = path
    print("PLAY_LOG: ", ProjectSettings.globalize_path(path))
    return path
