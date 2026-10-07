extends RefCounted
class_name WeaponRegistry

const DATA_PATH := "res://data/progression/weapons.json"

static var _weapons: Dictionary = {}
static var _order: Array[String] = []
static var _loaded := false

static func get_weapon(weapon_id: String) -> Dictionary:
    _ensure_loaded()
    return (_weapons.get(weapon_id.to_upper(), {}) as Dictionary).duplicate(true)

static func get_all_weapons() -> Array[Dictionary]:
    _ensure_loaded()
    var out: Array[Dictionary] = []
    for weapon_id in _order:
        out.append((_weapons[weapon_id] as Dictionary).duplicate(true))
    return out

static func get_default_weapon(operator_id: String) -> String:
    _ensure_loaded()
    var operator := operator_id.to_upper()
    for weapon_id in _order:
        var row: Dictionary = _weapons[weapon_id]
        if str(row.get("default_for", "")).to_upper() == operator:
            return weapon_id
    return ""

static func compatible_weapons(operator_id: String, unlocked: Array = []) -> Array[String]:
    _ensure_loaded()
    var operator := operator_id.to_upper()
    var out: Array[String] = []
    for weapon_id in _order:
        var row: Dictionary = _weapons[weapon_id]
        var compatible: Array = row.get("compatible_operators", [])
        if not compatible.has(operator):
            continue
        if not unlocked.is_empty() and not unlocked.has(weapon_id):
            continue
        out.append(weapon_id)
    return out

static func is_compatible(operator_id: String, weapon_id: String) -> bool:
    var row := get_weapon(weapon_id)
    if row.is_empty():
        return false
    return (row.get("compatible_operators", []) as Array).has(operator_id.to_upper())

static func _ensure_loaded() -> void:
    if _loaded:
        return
    _loaded = true
    if not FileAccess.file_exists(DATA_PATH):
        push_error("WeaponRegistry missing file: " + DATA_PATH)
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
    if not (parsed is Dictionary):
        push_error("WeaponRegistry parse failed: " + DATA_PATH)
        return
    for row_variant in parsed.get("weapons", []):
        if not (row_variant is Dictionary):
            continue
        var row: Dictionary = row_variant
        var weapon_id := str(row.get("weapon_id", "")).to_upper()
        if weapon_id.is_empty() or _weapons.has(weapon_id):
            push_error("WeaponRegistry invalid/duplicate weapon: " + weapon_id)
            continue
        _weapons[weapon_id] = row.duplicate(true)
        _order.append(weapon_id)
