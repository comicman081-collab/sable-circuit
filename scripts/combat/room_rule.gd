extends RefCounted
class_name RoomRule
## A room rule (data/progression/room_rules.json): a pacing change a combat room declares on its row,
## "rule": {"type": "OVERRUN", "seconds": 45}. A room without the key, a boss room and the training
## simulator behave exactly as before. A rule moves WHEN things happen; it never adds damage and
## never touches robot art.
## OVERRUN calls the room's next reinforcement wave in `seconds` after the previous wave was called
## (the room's first wave appears when the room starts), whether or not the wave on the floor is thinned
## out to `reinforce_at`. The wave keeps its marked entry points and the stage's usual wait before
## anything appears, and a room thinned out early still calls it the old way, at once.

const DATA_PATH := "res://data/progression/room_rules.json"

static var _table: Dictionary = {}

static func table() -> Dictionary:
    if _table.is_empty():
        var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
        _table = (parsed.get("rules", {}) as Dictionary) if parsed is Dictionary else {}
    return _table

static func rule_id(raw: Variant) -> String:
    return str((raw as Dictionary).get("type", "")).strip_edges().to_upper() if raw is Dictionary else ""

## What is wrong with the rule a room declares, one readable line each. Empty when it declares none
## or a usable one. The stage logs these and then runs the room without a rule; the quick test
## `room_rule` reads every mission file through here.
static func problems(room: Dictionary) -> Array[String]:
    var found: Array[String] = []
    if not room.has("rule"): return found
    var where := str(room.get("id", "?"))
    var raw: Variant = room.get("rule")
    if not (raw is Dictionary):
        found.append("%s: a room rule is an object like {\"type\": \"OVERRUN\"}" % where)
        return found
    var id := rule_id(raw)
    if not table().has(id):
        found.append("%s: unknown room rule '%s'" % [where, id])
        return found
    var spec: Dictionary = table()[id]
    if str(room.get("type", "")) == "BOSS":
        found.append("%s: a boss room takes no room rule" % where)
    if bool(spec.get("needs_reinforcements", false)) and (room.get("reinforcements", []) as Array).is_empty():
        found.append("%s: %s calls in a reinforcement wave and this room has none" % [where, id])
    if (raw as Dictionary).has("seconds"):
        var value: Variant = (raw as Dictionary).get("seconds")
        if not (value is float or value is int):
            found.append("%s: %s seconds must be a number" % [where, id])
        elif float(value) < float(spec.get("min_seconds", 0.0)) or float(value) > float(spec.get("max_seconds", INF)):
            found.append("%s: %s seconds %s is outside %s-%s" % [where, id, str(value), str(spec.get("min_seconds", 0.0)), str(spec.get("max_seconds", INF))])
    return found

## The rule the stage runs for a room: {} unless the room declares a usable one.
static func for_room(room: Dictionary) -> Dictionary:
    if not room.has("rule") or not problems(room).is_empty(): return {}
    var id := rule_id(room.get("rule"))
    var spec: Dictionary = table()[id]
    return {"type": id, "seconds": float((room.get("rule") as Dictionary).get("seconds", spec.get("seconds", 45.0)))}

static func tip(id_value: String) -> String:
    return str((table().get(id_value.strip_edges().to_upper(), {}) as Dictionary).get("tip", ""))

## OVERRUN: is the next wave to be called in now? Never while a wave is already waiting to appear.
static func overrun_due(rule: Dictionary, elapsed: float, wave_pending: bool, wave_wait: float) -> bool:
    return str(rule.get("type", "")) == "OVERRUN" and wave_pending and wave_wait <= 0.0 and elapsed >= float(rule.get("seconds", INF))

## The HUD line for the running rule; empty when there is nothing to count down to (no wave left to call,
## or one is already on its way in: the stage's own "HOSTILE SIGNALS INBOUND" line says so).
static func hud_line(rule: Dictionary, elapsed: float, wave_pending: bool, wave_wait: float) -> String:
    if str(rule.get("type", "")) != "OVERRUN" or not wave_pending or wave_wait > 0.0: return ""
    return "OVERRUN // NEXT WAVE IN %d" % maxi(0, int(ceil(float(rule.get("seconds", 0.0)) - elapsed)))
