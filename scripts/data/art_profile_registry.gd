extends RefCounted
class_name ArtProfileRegistry

const PLAYABLE_PATH := "res://data/art_profiles/playable_profiles.json"
const ENEMY_PATH := "res://data/art_profiles/enemy_profiles.json"

static var _profiles: Dictionary = {}
static var _loaded := false

static func get_profile(identity_id: String) -> Dictionary:
    _ensure_loaded()
    return (_profiles.get(identity_id, {}) as Dictionary).duplicate(true)

static func get_all_profiles() -> Dictionary:
    _ensure_loaded()
    return _profiles.duplicate(true)

static func _ensure_loaded() -> void:
    if _loaded:
        return
    _loaded = true
    _load_file(PLAYABLE_PATH)
    _load_file(ENEMY_PATH)

static func _load_file(path: String) -> void:
    if not FileAccess.file_exists(path):
        push_error("ArtProfileRegistry missing file: " + path)
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if not (parsed is Dictionary):
        push_error("ArtProfileRegistry parse failed: " + path)
        return
    for row_variant in parsed.get("profiles", []):
        if not (row_variant is Dictionary):
            continue
        var row: Dictionary = row_variant
        var identity := str(row.get("actor_id", row.get("enemy_id", "")))
        if identity.is_empty():
            continue
        if _profiles.has(identity):
            push_error("ArtProfileRegistry duplicate identity: " + identity)
            continue
        _profiles[identity] = row.duplicate(true)
