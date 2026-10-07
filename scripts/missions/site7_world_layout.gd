extends RefCounted
## Where each room and connector plate of a mission sits in its world, as solved by
## tools/environment/build_site7_world_layout.py. Main-route connectors climb up and
## to the right; authored v2 branches descend unmirrored (legacy branches mirror).
## No plate is rotated. Missions without an entry keep the older placement.

const PATH := "res://data/visual/site7_world_layout.json"
static var _missions: Dictionary = {}
static var _loaded := false

static func _mission(mission_id: String) -> Dictionary:
    if not _loaded:
        _loaded = true
        if FileAccess.file_exists(PATH):
            var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
            if parsed is Dictionary: _missions = (parsed as Dictionary).get("missions", {})
    var row: Variant = _missions.get(mission_id.to_upper(), {})
    return row if row is Dictionary else {}

## Room id -> [x, y] plate centre.
static func mission_rooms(mission_id: String) -> Dictionary:
    return _mission(mission_id).get("rooms", {})

## Connector rows in manifest order: {position: [x, y], scale, mirror}.
static func mission_connectors(mission_id: String) -> Array:
    return _mission(mission_id).get("connectors", [])

const SEAM_LIGHT_PATH := "res://data/visual/site7_seam_light.json"
static var _seam_light: Dictionary = {}
static var _seam_light_loaded := false

## Light map of a mission's connector (manifest order), made by the same tool: an
## RG8 image over the connector's texture, R a log2 brightness gain and G a log2
## saturation factor in [-seam_light_range(), seam_light_range()]. Null when there
## is none.
static func seam_light(mission_id: String, index: int) -> Image:
    if not _seam_light_loaded:
        _seam_light_loaded = true
        if FileAccess.file_exists(SEAM_LIGHT_PATH):
            var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(SEAM_LIGHT_PATH))
            if parsed is Dictionary: _seam_light = parsed
    var grid: Array = _seam_light.get("grid", [])
    var missions: Dictionary = _seam_light.get("missions", {})
    var mission: Variant = missions.get(mission_id.to_upper(), {})
    var encoded := str((mission as Dictionary).get("C%d" % index, "")) if mission is Dictionary else ""
    if grid.size() != 2 or encoded.is_empty(): return null
    var bytes := Marshalls.base64_to_raw(encoded)
    if bytes.size() != int(grid[0]) * int(grid[1]) * 2: return null
    return Image.create_from_data(int(grid[0]), int(grid[1]), false, Image.FORMAT_RG8, bytes)

static func seam_light_range() -> float:
    return float(_seam_light.get("log2_range", 0.0))
