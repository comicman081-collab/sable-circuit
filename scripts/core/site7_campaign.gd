extends RefCounted
## Authored mission order; preview and campaign use identical mission files.
const PATH := "res://data/story/site7_campaign.json"

static func rows() -> Array:
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
    return parsed.get("missions", []) if parsed is Dictionary else []

static func get_mission(id: String) -> Dictionary:
    for row: Dictionary in rows():
        if row.mission_id == id: return row.duplicate(true)
    return {}

static func story(id: String) -> Dictionary:
    var row := get_mission(id)
    if row.has("story_path"):
        var original: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(row.story_path))
        row["briefing"] = original.get("briefing", [])
        row["post_mission"] = original.get("post_mission", [])
    return row

## An authored row with `"deployable": false` is listed in the base but cannot be
## played: its map plates or boss are not integrated yet (docs/production/
## SITE7_OPERATIONS_6_10_DESIGN_KO.md). Deleting the flag is the last step of
## integrating a mission; the site7_campaign_data_smoke gate refuses it earlier.
static func deployable(id: String) -> bool:
    var row := get_mission(id)
    return not row.is_empty() and bool(row.get("deployable", true))

## Playable now: its predecessor is cleared and it is integrated.
static func available(id: String, cleared: Array) -> bool:
    var row := get_mission(id)
    return not row.is_empty() and bool(row.get("deployable", true)) and (str(row.requires).is_empty() or cleared.has(str(row.requires)))

## The authored row that requires `id`, playable or not; {} after the last one.
static func successor(id: String) -> Dictionary:
    for row: Dictionary in rows():
        if row.requires == id: return row
    return {}

## The mission that follows `id`, or "" when none is playable yet, so the results
## screen never offers a next-operation button that would go nowhere.
static func next_after(id: String) -> String:
    var row := successor(id)
    return str(row.mission_id) if not row.is_empty() and bool(row.get("deployable", true)) else ""

static func recommended(cleared: Array) -> String:
    var last_playable := "MIS_CH01_01"
    for row: Dictionary in rows():
        if not bool(row.get("deployable", true)): continue
        last_playable = str(row.mission_id)
        if available(row.mission_id, cleared) and not cleared.has(row.mission_id): return row.mission_id
    return last_playable

static func ui_rows(cleared: Array) -> Array:
    var output := rows()
    for row: Dictionary in output:
        row["deployable"] = bool(row.get("deployable", true))
        row["unlocked"] = available(row.mission_id, cleared)
        row["cleared"] = cleared.has(row.mission_id)
    return output

## Rows a player can ever clear right now; the chapter is complete only when every
## authored row is cleared, "all playable cleared" is a separate, weaker state.
static func playable_ids() -> Array[String]:
    var ids: Array[String] = []
    for row: Dictionary in rows():
        if bool(row.get("deployable", true)): ids.append(str(row.mission_id))
    return ids
