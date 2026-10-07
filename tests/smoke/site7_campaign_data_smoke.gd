extends SceneTree
## Data gate for the campaign catalog and every mission file (operations 1-10).
## An operation is held back ("deployable": false) until its 15 map plates and its boss art
## exist; all ten are open now, so the held-back controls below run only while one is. This test
## proves the held-back state is consistent and that a mission cannot be made deployable early:
## the same gate runs on synthetic broken copies as a negative control. It checks data and
## wiring only; it is no approval of balance, art or play.
const Catalog := preload("res://scripts/core/site7_campaign.gd")
const BATTLE_ART := "res://data/visual/site7_battle_art.json"
const WORLD_LAYOUT := "res://data/visual/site7_world_layout.json"
const BATTLE_LAYOUTS := "res://data/visual/site7_battle_layouts.json"
const MOOD := "res://data/visual/site7_mood.json"
const PROPS := "res://data/visual/site7_environment_props.json"
const AFFIXES := "res://data/progression/elite_affixes.json"
const HAZARDS := "res://data/progression/zone_hazards.json"
const OPERATIONS := 10
const ROOM_TYPES := ["EVENT", "COMBAT", "RESEARCH", "ELITE", "BOSS", "EXTRACTION"]
const OPTIONAL_TYPES := ["SUPPLY", "RESEARCH"]
const LOOT_IDS := ["LOT_RESEARCH_COMMON", "LOT_RESEARCH_HIGH_VALUE", "LOT_SALVAGE_FIELD", "LOT_SIGNAL_FRAGMENT", "LOT_INTEL_MECHANICAL"]
const SPEAKERS := ["COMMAND", "MICA", "ROOK", "ASTER"]
## A boss id containing one of these is routed to another effect family (docs/production/SITE7_BOSS_ROBOTS_CODEX_PROMPT_KO.md).
const BANNED_FRAGMENTS := ["ASTER", "ROOK", "MICA", "DRONE", "SHIELD", "PRISM", "_RAM_", "GUARD", "PYLON", "MORTAR", "RIFLE", "ANCHOR", "FORGE", "CARRIER"]
## Phrases the campaign uses to announce that the next operation is open.
const PROMISES := ["now available", "unlocked", "opens"]
## Tests and tools that loop over every operation by a literal count (see stale_loop_gaps).
const PER_OPERATION_FILES := [
    "res://tests/smoke/combat_density_smoke.gd",
    "res://tests/smoke/site7_battle_geometry_smoke.gd",
    "res://tests/smoke/site7_branch_navigation_regression.gd",
    "res://tests/smoke/site7_connector_alignment_smoke.gd",
    "res://tests/smoke/site7_traversal_audit_smoke.gd",
    "res://tests/smoke/site7_world_route_navigation_smoke.gd",
    "res://tests/smoke/firing_lane_search_smoke.gd",
    "res://tests/smoke/floor_segment_smoke.gd",
    "res://tests/smoke/zone_hazard_smoke.gd",
    "res://tests/smoke/elite_affix_smoke.gd",
    "res://tests/smoke/site7_live_entry_autostart_smoke.gd",
    "res://tests/render/site7_battle_capture.gd",
    "res://tests/render/stage_battle_video_10s_capture.gd",
    "res://tools/environment/record_stage_battle_with_audio.py",
    "res://tools/maintenance/run_regression_suite.py",
]
var failures: Array[String] = []
var checks := 0

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func load_json(path: String) -> Dictionary:
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    return parsed if parsed is Dictionary else {}

func mission_path(id: String) -> String:
    return "res://data/missions/%s.json" % id

## Fields every mission file shares: room order and types, encounters, waves, affixes,
## hazards, loot, extraction windows and (from operation 4 on) the objective chain.
func schema_gaps(id: String, m: Dictionary) -> Array[String]:
    var gaps: Array[String] = []
    var strict := int(id.right(2)) >= 4
    if str(m.get("mission_id", "")) != id: gaps.append("%s: mission_id field says %s" % [id, m.get("mission_id", "")])
    if str(m.get("title", "")).is_empty() or str(m.get("zone", "")).is_empty(): gaps.append("%s: title and zone are required" % id)
    var route: Array = m.get("main_route", [])
    var optional: Array = m.get("optional_rooms", [])
    if route.size() != ROOM_TYPES.size():
        gaps.append("%s: main route needs %d rooms, has %d" % [id, ROOM_TYPES.size(), route.size()])
        return gaps
    if optional.size() != OPTIONAL_TYPES.size(): gaps.append("%s: needs %d optional rooms, has %d" % [id, OPTIONAL_TYPES.size(), optional.size()])
    var room_ids := {}
    for index in range(route.size()):
        var room: Dictionary = route[index]
        var room_id := str(room.get("id", ""))
        if room_ids.has(room_id): gaps.append("%s: duplicate room id %s" % [id, room_id])
        room_ids[room_id] = true
        if str(room.get("type", "")) != ROOM_TYPES[index]: gaps.append("%s: room %d is %s, expected %s" % [id, index + 1, room.get("type", ""), ROOM_TYPES[index]])
        if not room_id.begins_with("R%02d_" % (index + 1)): gaps.append("%s: room id %s must start R%02d_" % [id, room_id, index + 1])
        if str(room.get("title", "")).is_empty() or str(room.get("objective", "")).is_empty(): gaps.append("%s: %s needs a title and an objective" % [id, room_id])
    for index in range(optional.size()):
        var room: Dictionary = optional[index]
        var room_id := str(room.get("id", ""))
        if room_ids.has(room_id): gaps.append("%s: duplicate room id %s" % [id, room_id])
        room_ids[room_id] = true
        if not room_id.begins_with("O%02d_" % (index + 1)): gaps.append("%s: optional id %s must start O%02d_" % [id, room_id, index + 1])
        if index < OPTIONAL_TYPES.size() and str(room.get("type", "")) != OPTIONAL_TYPES[index]: gaps.append("%s: %s is %s, expected %s" % [id, room_id, room.get("type", ""), OPTIONAL_TYPES[index]])
        var parent := str(room.get("from", ""))
        if strict and parent.is_empty(): gaps.append("%s: %s needs an explicit from (branch parent)" % [id, room_id])
        if not parent.is_empty():
            var parent_is_main := false
            for main_room: Dictionary in route:
                if str(main_room.id) == parent: parent_is_main = true
            if not parent_is_main: gaps.append("%s: %s branches from %s, which is not a main room" % [id, room_id, parent])
    var affixes: Dictionary = load_json(AFFIXES).get("affixes", {})
    var hazards: Dictionary = load_json(HAZARDS).get("hazards", {})
    var total := 0
    for room: Dictionary in route:
        var type := str(room.get("type", ""))
        var first: Array = room.get("encounter", [])
        var fights := type in ["COMBAT", "ELITE", "BOSS"]
        if fights == first.is_empty(): gaps.append("%s: %s (%s) %s an encounter" % [id, room.id, type, "needs" if fights else "must not have"])
        if strict and fights and str(room.get("encounter_id", "")).is_empty(): gaps.append("%s: %s needs an encounter_id" % [id, room.id])
        if strict:
            if not room.has("loot"): gaps.append("%s: %s needs a loot list" % [id, room.id])
            for row: Dictionary in room.get("loot", []):
                if not str(row.get("loot_id", "")) in LOOT_IDS or int(row.get("quantity", 0)) <= 0: gaps.append("%s: %s has a bad loot row %s" % [id, room.id, row])
        if not fights:
            if room.has("hazards") or room.has("reinforcements"): gaps.append("%s: %s (%s) must not carry hazards or waves" % [id, room.id, type])
            continue
        var waves: Array = [first]
        waves.append_array(room.get("reinforcements", []))
        var reinforce_at := int(room.get("reinforce_at", 0))
        var peak := first.size()
        for wave_index in range(1, waves.size()): peak = maxi(peak, reinforce_at + (waves[wave_index] as Array).size())
        if type != "BOSS" and peak < 5: gaps.append("%s: %s fields only %d hostiles at once" % [id, room.id, peak])
        if waves.size() < 2 or reinforce_at < 1: gaps.append("%s: %s needs a reinforcement wave with reinforce_at >= 1" % [id, room.id])
        var bosses := 0
        for wave_index in range(waves.size()):
            var wave: Array = waves[wave_index]
            total += wave.size()
            for row_index in range(wave.size()):
                var row: Dictionary = wave[row_index]
                var enemy_id := str(row.get("enemy_id", ""))
                var is_boss := enemy_id.begins_with("BOSS_")
                if ArtProfileRegistry.get_profile(enemy_id).is_empty(): gaps.append("%s: %s spawns %s, which has no active robot profile" % [id, room.id, enemy_id])
                if is_boss:
                    bosses += 1
                    if type != "BOSS" or wave_index != 0 or row_index != 0: gaps.append("%s: %s holds a boss row out of place" % [id, room.id])
                if float(row.get("health", 0.0)) <= 0.0: gaps.append("%s: %s row %s has no health" % [id, room.id, enemy_id])
                var affix := str(row.get("affix", ""))
                if not affix.is_empty() and (is_boss or not affixes.has(affix)): gaps.append("%s: %s row %s has affix %s" % [id, room.id, enemy_id, affix])
        if type == "BOSS" and bosses != 1: gaps.append("%s: the boss room needs exactly one boss row, has %d" % [id, bosses])
        for hazard: Dictionary in room.get("hazards", []):
            if type == "BOSS" or not hazards.has(str(hazard.get("type", ""))) or int(hazard.get("count", 0)) < 1 or int(hazard.get("count", 0)) > 3:
                gaps.append("%s: %s has a bad hazard row %s" % [id, room.id, hazard])
    if total < 18: gaps.append("%s: fields %d hostiles, needs at least 18" % [id, total])
    var offers: Array = m.get("extraction_offer_room_ids", [])
    if offers.size() < 2: gaps.append("%s: needs at least two extraction windows" % id)
    for offer in offers:
        var offer_index := -1
        for index in range(route.size()):
            if str(route[index].id) == str(offer): offer_index = index
        if offer_index < 2 or offer_index > 4: gaps.append("%s: extraction window %s must be one of rooms 3-5" % [id, offer])
    var objectives: Array = m.get("objectives", [])
    if strict and objectives.size() != route.size(): gaps.append("%s: needs one objective per main room" % id)
    var objective_ids := {}
    for objective: Dictionary in objectives: objective_ids[str(objective.get("id", ""))] = true
    for index in range(objectives.size()):
        var objective: Dictionary = objectives[index]
        if not room_ids.has(str(objective.get("source_room", ""))): gaps.append("%s: objective %s names an unknown room" % [id, objective.get("id", "")])
        for prerequisite in objective.get("prerequisites", []):
            if not objective_ids.has(str(prerequisite)): gaps.append("%s: objective %s needs an unknown %s" % [id, objective.get("id", ""), prerequisite])
        if strict and index < route.size():
            var room: Dictionary = route[index]
            if str(objective.get("source_room", "")) != str(room.id) or str(room.get("objective_id", "")) != str(objective.get("id", "")): gaps.append("%s: objective %d is not bound to room %s" % [id, index + 1, room.id])
            var expected_kind := "BOSS" if index == 4 else ("DEEP" if index == 3 else "PRIMARY")
            if str(objective.get("kind", "")) != expected_kind: gaps.append("%s: objective %d kind %s, expected %s" % [id, index + 1, objective.get("kind", ""), expected_kind])
            if bool(objective.get("required_for_extraction", false)) != (index == 2): gaps.append("%s: only the third objective gates early extraction" % id)
            var chain: Array = [] if index == 0 else [str((objectives[index - 1] as Dictionary).get("id", ""))]
            if objective.get("prerequisites", []) != chain: gaps.append("%s: objective %d must follow objective %d" % [id, index + 1, index])
    return gaps

## The optional rooms' loot; the main route's is checked in schema_gaps.
func optional_loot_gaps(id: String, m: Dictionary) -> Array[String]:
    var gaps: Array[String] = []
    for room: Dictionary in m.get("optional_rooms", []):
        if int(id.right(2)) >= 4 and not room.has("loot"): gaps.append("%s: %s needs a loot list" % [id, room.id])
        for row: Dictionary in room.get("loot", []):
            if not str(row.get("loot_id", "")) in LOOT_IDS or int(row.get("quantity", 0)) <= 0: gaps.append("%s: %s has a bad loot row %s" % [id, room.id, row])
    return gaps

## A mission held back for art carries a staging block describing what is still owed.
func staging_gaps(id: String, m: Dictionary) -> Array[String]:
    var gaps: Array[String] = []
    var number := int(id.right(2))
    var staging: Dictionary = m.get("staging", {})
    if str(staging.get("status", "")) != "ART_PENDING": gaps.append("%s: a held-back mission needs staging.status ART_PENDING" % id)
    var boss: Dictionary = staging.get("boss", {})
    var pending_id := str(boss.get("id", ""))
    if not (pending_id.begins_with("BOSS_SITE7_") and pending_id.ends_with("_01")): gaps.append("%s: planned boss id %s must look like BOSS_SITE7_<NAME>_01" % [id, pending_id])
    for fragment in BANNED_FRAGMENTS:
        if pending_id.contains(fragment): gaps.append("%s: planned boss id %s contains %s" % [id, pending_id, fragment])
    if str(boss.get("pattern", "")).is_empty() or str(boss.get("name", "")).is_empty(): gaps.append("%s: planned boss needs a name and a pattern" % id)
    # Once the planned boss is registered its row stands in the boss room (no placeholder) and its profile
    # carries the pattern the staging block promises; the day the plates arrive only the plates are owed.
    var planned := ArtProfileRegistry.get_profile(pending_id)
    if not planned.is_empty():
        if boss_of(m) != pending_id: gaps.append("%s: %s is registered, so the boss row must hold it, not %s" % [id, pending_id, boss_of(m)])
        if str(planned.get("boss_pattern", "")) != str(boss.get("pattern", "")): gaps.append("%s: %s runs %s, staging promises %s" % [id, pending_id, planned.get("boss_pattern", ""), boss.get("pattern", "")])
        if not FileAccess.file_exists(str((planned.get("machine_asset", {}) as Dictionary).get("spec", ""))): gaps.append("%s: registered boss %s has no authored machine spec" % [id, pending_id])
    var route: Array = m.get("main_route", [])
    if route.size() == ROOM_TYPES.size():
        var boss_room: Dictionary = route[4]
        if str(boss.get("room", "")) != str(boss_room.id): gaps.append("%s: planned boss room %s is not %s" % [id, boss.get("room", ""), boss_room.id])
        var first: Array = boss_room.get("encounter", [])
        if first.is_empty() or int((first[0] as Dictionary).get("health", 0)) != int(boss.get("health", -1)): gaps.append("%s: the boss row must already carry the planned health %s" % [id, boss.get("health", "")])
    var plates: Dictionary = staging.get("plates", {})
    if str(plates.get("prefix", "")) != "S%d" % number or int(plates.get("rooms", 0)) != 8 or int(plates.get("connectors", 0)) != 7 \
            or str(plates.get("asset_dir", "")) != "assets/environments/site7_v2/stage%02d" % number:
        gaps.append("%s: staging.plates must name S%d, 8 rooms, 7 connectors and stage%02d" % [id, number, number])
    var structure: Dictionary = staging.get("structure", {})
    if not str(structure.get("main_route", "")) in ["ascending", "reverse"]: gaps.append("%s: staging.structure.main_route must be ascending or reverse" % id)
    var branches: Dictionary = structure.get("branches", {})
    for room: Dictionary in m.get("optional_rooms", []):
        if str(branches.get(str(room.id), "")) != str(room.get("from", "-")): gaps.append("%s: staging branch for %s disagrees with the room's from" % [id, room.id])
    if branches.size() != (m.get("optional_rooms", []) as Array).size(): gaps.append("%s: staging.structure.branches must list every optional room" % id)
    return gaps

## What a mission needs before the campaign may deploy it.
func integration_gaps(id: String, m: Dictionary) -> Array[String]:
    var gaps: Array[String] = []
    if m.has("staging"): gaps.append("%s: deployable but still carries a staging block" % id)
    var route: Array = m.get("main_route", [])
    var optional: Array = m.get("optional_rooms", [])
    var wanted: Array[String] = []
    for room: Dictionary in route + optional: wanted.append(str(room.id))
    var art: Dictionary = (load_json(BATTLE_ART).get("missions", {}) as Dictionary).get(id, {})
    var rooms: Array = art.get("rooms", [])
    var connectors: Array = art.get("connectors", [])
    if rooms.size() != 8 or connectors.size() != 7: gaps.append("%s: needs 8 room plates and 7 connectors in site7_battle_art.json (has %d and %d)" % [id, rooms.size(), connectors.size()])
    var unplated: Array[String] = wanted.duplicate()
    for row: Dictionary in rooms:
        unplated.erase(str(row.get("room_id", "")))
        if not FileAccess.file_exists("res://" + str(row.get("asset", ""))): gaps.append("%s: plate file missing for %s" % [id, row.get("room_id", "")])
    for room_id in unplated: gaps.append("%s: no plate row for room %s" % [id, room_id])
    for row: Dictionary in connectors:
        if not FileAccess.file_exists("res://" + str(row.get("asset", ""))): gaps.append("%s: connector file missing for %s" % [id, row.get("connector_id", "")])
    if not (load_json(WORLD_LAYOUT).get("missions", {}) as Dictionary).has(id): gaps.append("%s: no solved world layout (build_site7_world_layout.py)" % id)
    if not (load_json(MOOD).get("missions", {}) as Dictionary).has(id): gaps.append("%s: no mood row in site7_mood.json" % id)
    var props: Dictionary = (load_json(PROPS).get("missions", {}) as Dictionary).get(id, {})
    for room_id in wanted:
        if not props.has(room_id): gaps.append("%s: no cover props for %s" % [id, room_id])
    var layouts: Dictionary = (load_json(BATTLE_LAYOUTS).get("missions", {}) as Dictionary).get(id, {})
    for room: Dictionary in route:
        if str(room.type) in ["COMBAT", "ELITE", "BOSS"] and not layouts.has(str(room.id)): gaps.append("%s: no combat layout for %s" % [id, room.id])
    var boss_id := boss_of(m)
    var profile := ArtProfileRegistry.get_profile(boss_id)
    if profile.is_empty() or str(profile.get("boss_pattern", "")).is_empty(): gaps.append("%s: boss %s needs a registered profile with a boss_pattern" % [id, boss_id])
    else:
        var spec := str((profile.get("machine_asset", {}) as Dictionary).get("spec", ""))
        if not FileAccess.file_exists(spec): gaps.append("%s: boss %s has no authored machine spec" % [id, boss_id])
    return gaps

## An operation's debrief names its successor only once that successor can be deployed. While it is held
## back neither the debrief nor ASTER's closing briefing line may promise it, or the base would show
## "now available" above an IN PREPARATION row. Applies to the operations written for the expansion.
func story_gaps(id: String, story: Dictionary, successor_title: String, successor_deployable: bool) -> Array[String]:
    var gaps: Array[String] = []
    var debrief := ""
    for line: Dictionary in story.get("post_mission", []):
        if str(line.get("speaker", "")) == "COMMAND": debrief = str(line.get("text", ""))
    var closing := ""
    for line: Dictionary in story.get("briefing", []):
        if str(line.get("speaker", "")) == "ASTER": closing = str(line.get("text", ""))
    var announces := debrief.to_lower().contains(successor_title.to_lower())
    if successor_deployable:
        if not announces: gaps.append("%s: its successor %s is deployable, so the COMMAND debrief must name it" % [id, successor_title])
        return gaps
    if announces: gaps.append("%s: the debrief names %s, which is held back" % [id, successor_title])
    for text in [debrief, closing]:
        for promise in PROMISES:
            if text.to_lower().contains(promise): gaps.append("%s: \"%s\" promises an unlock while %s is held back" % [id, text, successor_title])
    return gaps

## Spellings of a loop or a list that covers operations 1..last and stops there: range(1, last + 1), the
## tuple (1,2,...,last) and a mission list that ends at MIS_CH01_<last>.
func stop_markers(last: int) -> Array[String]:
    var numbers: Array[String] = []
    for n in range(1, last + 1): numbers.append(str(n))
    return ["range(1, %d)" % (last + 1), "range(1,%d)" % (last + 1), "(%s)" % ",".join(numbers), "\"MIS_CH01_%02d\"]" % last]

## A per-mission table whose last row is operation `last`: {..., "MIS_CH01_06": 4}.
func table_ends_at(text: String, last: int) -> bool:
    var end := RegEx.new()
    end.compile("\"MIS_CH01_%02d\"\\s*:\\s*[0-9]+\\s*\\}" % last)
    return end.search(text) != null

## These tests loop over a literal range(1, N) or list the operations and stop at operation K. Once more than
## K operations are deployable they would silently skip the rest, so the gate names each one that stops short
## of a playable operation. (A file that needs range(1, 7) for another reason, such as six rooms, has to spell
## it differently: the gate cannot tell the two apart.)
func stale_loop_gaps(playable_count: int, sources: Dictionary) -> Array[String]:
    var gaps: Array[String] = []
    for last in range(5, playable_count):
        for path in sources:
            var text := str(sources[path])
            var hit := ""
            for marker in stop_markers(last):
                if text.contains(marker):
                    hit = marker
                    break
            if hit.is_empty() and table_ends_at(text, last): hit = "\"MIS_CH01_%02d\": <n>}" % last
            if not hit.is_empty():
                gaps.append("%s still stops at operation %d (%s); extend it to all %d playable operations" % [path, last, hit, playable_count])
    return gaps

func gate(id: String, deployable: bool, m: Dictionary) -> Array[String]:
    var gaps := schema_gaps(id, m)
    gaps.append_array(optional_loot_gaps(id, m))
    gaps.append_array(integration_gaps(id, m) if deployable else staging_gaps(id, m))
    return gaps

func boss_of(m: Dictionary) -> String:
    var route: Array = m.get("main_route", [])
    if route.size() < 5: return ""
    var first: Array = (route[4] as Dictionary).get("encounter", [])
    return str((first[0] as Dictionary).get("enemy_id", "")) if not first.is_empty() else ""

func boss_health(m: Dictionary) -> int:
    var route: Array = m.get("main_route", [])
    if route.size() < 5: return 0
    var first: Array = (route[4] as Dictionary).get("encounter", [])
    return int((first[0] as Dictionary).get("health", 0)) if not first.is_empty() else 0

## "ascending" or "reverse", then the main rooms the two branches leave from.
func route_signature(id: String, m: Dictionary, art: Dictionary) -> String:
    var direction := str(((m.get("staging", {}) as Dictionary).get("structure", {}) as Dictionary).get("main_route", ""))
    if direction.is_empty():
        direction = "ascending"
        for connector: Dictionary in (art.get("missions", {}) as Dictionary).get(id, {}).get("connectors", []):
            if bool(connector.get("reverse", false)): direction = "reverse"
    var route: Array = m.get("main_route", [])
    var parents: Array[String] = []
    var optional: Array = m.get("optional_rooms", [])
    for index in range(optional.size()):
        var parent := str((optional[index] as Dictionary).get("from", ""))
        if parent.is_empty(): parent = str((route[mini(index + 2, route.size() - 1)] as Dictionary).id)
        parents.append(parent.substr(0, 3))
    return direction + ":" + ",".join(parents)

func run() -> void:
    var rows := Catalog.rows()
    var ids: Array[String] = []
    for row: Dictionary in rows: ids.append(str(row.mission_id))
    check(rows.size() == OPERATIONS, "The campaign lists %d operations (%d)" % [OPERATIONS, rows.size()])
    var mission_files := 0
    var directory := DirAccess.open("res://data/missions")
    if directory != null:
        for file_name in directory.get_files():
            if file_name.begins_with("MIS_CH01_") and file_name.ends_with(".json"): mission_files += 1
    check(mission_files == rows.size(), "One mission file per catalog row (%d files, %d rows)" % [mission_files, rows.size()])
    # Catalog semantics.
    var playable := Catalog.playable_ids()
    check(not playable.is_empty() and ",".join(ids.slice(0, playable.size())) == ",".join(playable), "Playable operations are the leading rows in order")
    for index in range(ids.size()):
        var id := ids[index]
        check(id == "MIS_CH01_%02d" % (index + 1), "Row %d is %s" % [index + 1, id])
        check(str(rows[index].requires) == ("" if index == 0 else ids[index - 1]), "%s requires its predecessor" % id)
        check(not str(rows[index].title).is_empty() and not str(rows[index].synopsis).is_empty(), "%s has a title and synopsis" % id)
        var cleared := ids.slice(0, index)
        check(Catalog.available(id, cleared) == Catalog.deployable(id), "%s is available exactly when it is deployable and its predecessor is cleared" % id)
        if index > 0: check(not Catalog.available(id, cleared.slice(0, index - 1)), "%s stays locked until its predecessor is cleared" % id)
        var expected_next := ids[index + 1] if index + 1 < ids.size() and Catalog.deployable(ids[index + 1]) else ""
        check(Catalog.next_after(id) == expected_next, "%s offers %s as the next operation" % [id, expected_next if not expected_next.is_empty() else "nothing"])
        var story := Catalog.story(id)
        var briefing: Array = story.get("briefing", [])
        var post: Array = story.get("post_mission", [])
        check(briefing.size() >= 4 and post.size() >= 2, "%s has a briefing of four lines and a two-line debrief" % id)
        for line: Dictionary in briefing + post: check(str(line.get("speaker", "")) in SPEAKERS and not str(line.get("text", "")).is_empty(), "%s dialogue line is spoken by an operator or COMMAND" % id)
        check(not str(rows[index].get("evidence_label", "")).is_empty(), "%s names its evidence" % id)
        if index >= 4 and index + 1 < ids.size():
            var text_gaps := story_gaps(id, story, str(rows[index + 1].title), Catalog.deployable(ids[index + 1]))
            check(text_gaps.is_empty(), "%s story text follows its successor's state: %s" % [id, "; ".join(text_gaps)])
    check(Catalog.recommended([]) == ids[0], "A new save is sent to operation 1")
    check(Catalog.recommended(playable) == playable.back(), "With every playable operation cleared the base recommends the last one")
    for row: Dictionary in Catalog.ui_rows(playable):
        check(bool(row.deployable) == Catalog.deployable(str(row.mission_id)), "%s list row reports deployable" % row.mission_id)
        check(bool(row.unlocked) == (bool(row.deployable) and (str(row.requires).is_empty() or playable.has(str(row.requires)))), "%s list row unlocked flag" % row.mission_id)
    # Mission files.
    var art := load_json(BATTLE_ART)
    var signatures := {}
    var boss_ids := {}
    var boss_patterns := {}
    var previous_health := 0
    for index in range(ids.size()):
        var id := ids[index]
        var m := load_json(mission_path(id))
        var deployable := Catalog.deployable(id)
        var gaps := gate(id, deployable, m)
        check(gaps.is_empty(), "%s (%s) gate: %s" % [id, "deployable" if deployable else "held back", "; ".join(gaps)])
        check(str(rows[index].get("evidence_room", "")) == str((m.main_route as Array)[2].id), "%s evidence room is the third main room" % id)
        if deployable: check(not rows[index].has("pending"), "%s is deployable, so its catalog row drops the pending note" % id)
        else: check(not str(rows[index].get("pending", "")).is_empty(), "%s is held back and its row says why" % id)
        var health := boss_health(m)
        check(health > previous_health, "%s boss health %d rises above the previous operation's %d" % [id, health, previous_health])
        previous_health = health
        var boss_id := boss_of(m) if deployable else str(((m.get("staging", {}) as Dictionary).get("boss", {}) as Dictionary).get("id", ""))
        var pattern := str(ArtProfileRegistry.get_profile(boss_id).get("boss_pattern", "")) if deployable else str(((m.get("staging", {}) as Dictionary).get("boss", {}) as Dictionary).get("pattern", ""))
        check(not boss_ids.has(boss_id), "%s boss %s is not used by another operation" % [id, boss_id])
        boss_ids[boss_id] = id
        check(not pattern.is_empty() and not boss_patterns.has(pattern), "%s boss pattern %s is not used by another operation" % [id, pattern])
        boss_patterns[pattern] = id
        if index >= 2:
            var signature := route_signature(id, m, art)
            check(not signatures.has(signature), "%s route structure %s differs from %s" % [id, signature, signatures.get(signature, "")])
            signatures[signature] = id
    # Negative controls: the gate must fail on each of these.
    var m5 := load_json(mission_path("MIS_CH01_05"))
    var early := m5.duplicate(true)
    early["staging"] = {"status": "ART_PENDING"}
    check(not gate("MIS_CH01_05", true, early).is_empty(), "Negative control: a deployable mission with a staging block is refused")
    var unknown_boss := m5.duplicate(true)
    ((unknown_boss.main_route[4] as Dictionary).encounter[0] as Dictionary)["enemy_id"] = "BOSS_SITE7_NOPE_01"
    check(not gate("MIS_CH01_05", true, unknown_boss).is_empty(), "Negative control: an unregistered boss is refused")
    var thin := m5.duplicate(true)
    ((thin.main_route[1] as Dictionary))["reinforcements"] = []
    check(not gate("MIS_CH01_05", true, thin).is_empty(), "Negative control: a combat room without reinforcements is refused")
    var doubled := m5.duplicate(true)
    (doubled.main_route[2] as Dictionary)["id"] = str((doubled.main_route[1] as Dictionary).id)
    check(not gate("MIS_CH01_05", true, doubled).is_empty(), "Negative control: a duplicate room id is refused")
    var affixed_boss := m5.duplicate(true)
    ((affixed_boss.main_route[4] as Dictionary).encounter[0] as Dictionary)["affix"] = "SHIELDED"
    check(not gate("MIS_CH01_05", true, affixed_boss).is_empty(), "Negative control: an affixed boss is refused")
    var promise_story := {"briefing": [{"speaker": "ASTER", "text": "Lift out. Full clearance opens the next wing."}], "post_mission": [{"speaker": "COMMAND", "text": "Done. Cold Storage is now available."}]}
    var quiet_story := {"briefing": [{"speaker": "ASTER", "text": "Lift out."}], "post_mission": [{"speaker": "COMMAND", "text": "Done. Refit at base."}]}
    check(not story_gaps("X", promise_story, "COLD STORAGE", false).is_empty(), "Negative control: a debrief that promises a held-back operation is refused")
    check(story_gaps("X", quiet_story, "COLD STORAGE", false).is_empty(), "A neutral debrief is accepted while the successor is held back")
    check(not story_gaps("X", quiet_story, "COLD STORAGE", true).is_empty(), "Negative control: a deployable successor that the debrief never names is refused")
    check(story_gaps("X", promise_story, "COLD STORAGE", true).is_empty(), "A debrief that names a deployable successor is accepted")
    # Files whose operation count stops short: none may survive once a later operation is deployable.
    var loop_sources := {}
    for path in PER_OPERATION_FILES:
        loop_sources[path] = FileAccess.get_file_as_string(path)
        check(not str(loop_sources[path]).is_empty(), "%s can be read" % path)
    var loop_gaps := stale_loop_gaps(playable.size(), loop_sources)
    check(loop_gaps.is_empty(), "Every per-operation test covers the playable operations: %s" % "; ".join(loop_gaps))
    check(not stale_loop_gaps(6, {"res://x.gd": "for n in range(1, 6):"}).is_empty(), "Negative control: a five-operation loop is refused once six operations are playable")
    check(not stale_loop_gaps(7, {"res://x.gd": "for n in range(1,6):"}).is_empty(), "Negative control: the compact spelling is refused too")
    check(not stale_loop_gaps(6, {"res://x.gd": "const MISSIONS := [\"MIS_CH01_04\", \"MIS_CH01_05\"]"}).is_empty(), "Negative control: a mission list that ends at operation 5 is refused")
    check(not stale_loop_gaps(6, {"res://x.gd": "const ROWS := {\"MIS_CH01_05\": 3}"}).is_empty(), "Negative control: a per-mission table that ends at operation 5 is refused")
    check(stale_loop_gaps(5, {"res://x.gd": "for n in range(1, 6):"}).is_empty(), "Five playable operations still allow the five-operation loops")
    check(stale_loop_gaps(6, {"res://x.gd": "for n in range(1, 7):"}).is_empty(), "A loop extended to six operations passes")
    check(not stale_loop_gaps(7, {"res://x.gd": "for n in range(1, 7):"}).is_empty(), "Negative control: a six-operation loop is refused once seven operations are playable")
    check(not stale_loop_gaps(7, {"res://x.gd": "for n in range(1,7):"}).is_empty(), "Negative control: the compact six-operation spelling is refused too")
    check(not stale_loop_gaps(7, {"res://x.gd": "const OPERATIONS := (1,2,3,4,5,6)"}).is_empty(), "Negative control: a tuple of operations 1-6 is refused")
    check(not stale_loop_gaps(7, {"res://x.gd": "const MISSIONS := [\"MIS_CH01_05\", \"MIS_CH01_06\"]"}).is_empty(), "Negative control: a mission list that ends at operation 6 is refused")
    check(not stale_loop_gaps(7, {"res://x.gd": "const ROWS := {\"MIS_CH01_05\": 3, \"MIS_CH01_06\": 4}"}).is_empty(), "Negative control: a per-mission table that ends at operation 6 is refused")
    check(stale_loop_gaps(7, {"res://x.gd": "for n in range(1, 8):\n    var pair := [\"MIS_CH01_06\", \"MIS_CH01_07\"]\n    var rows := {\"MIS_CH01_06\": 4, \"MIS_CH01_07\": 4}"}).is_empty(), "A loop, list and table extended to seven operations pass")
    check(stale_loop_gaps(7, {"res://x.gd": "for n in range(1, 8):"}).size() == 0 and stale_loop_gaps(8, {"res://x.gd": "for n in range(1, 8):"}).size() == 1, "The gate names exactly the loop that stops one short of the playable count")
    check(not stale_loop_gaps(8, {"res://x.gd": "for n in range(1,8):"}).is_empty(), "Negative control: the compact seven-operation spelling is refused once eight operations are playable")
    check(not stale_loop_gaps(8, {"res://x.gd": "const OPERATIONS := (1,2,3,4,5,6,7)"}).is_empty(), "Negative control: a tuple of operations 1-7 is refused")
    check(not stale_loop_gaps(8, {"res://x.gd": "const MISSIONS := [\"MIS_CH01_06\", \"MIS_CH01_07\"]"}).is_empty(), "Negative control: a mission list that ends at operation 7 is refused")
    check(not stale_loop_gaps(8, {"res://x.gd": "const ROWS := {\"MIS_CH01_06\": 3, \"MIS_CH01_07\": 4}"}).is_empty(), "Negative control: a per-mission table that ends at operation 7 is refused")
    check(stale_loop_gaps(8, {"res://x.gd": "for n in range(1, 9):\n    var pair := [\"MIS_CH01_07\", \"MIS_CH01_08\"]\n    var rows := {\"MIS_CH01_07\": 4, \"MIS_CH01_08\": 4}"}).is_empty(), "A loop, list and table extended to eight operations pass")
    check(stale_loop_gaps(8, {"res://x.gd": "for n in range(1, 9):"}).size() == 0 and stale_loop_gaps(9, {"res://x.gd": "for n in range(1, 9):"}).size() == 1, "The gate names the eight-operation loop once nine operations are playable")
    check(not stale_loop_gaps(9, {"res://x.gd": "for n in range(1,9):"}).is_empty(), "Negative control: the compact eight-operation spelling is refused once nine operations are playable")
    check(not stale_loop_gaps(9, {"res://x.gd": "const OPERATIONS := (1,2,3,4,5,6,7,8)"}).is_empty(), "Negative control: a tuple of operations 1-8 is refused")
    check(not stale_loop_gaps(9, {"res://x.gd": "const MISSIONS := [\"MIS_CH01_07\", \"MIS_CH01_08\"]"}).is_empty(), "Negative control: a mission list that ends at operation 8 is refused")
    check(not stale_loop_gaps(9, {"res://x.gd": "const ROWS := {\"MIS_CH01_07\": 3, \"MIS_CH01_08\": 4}"}).is_empty(), "Negative control: a per-mission table that ends at operation 8 is refused")
    check(stale_loop_gaps(9, {"res://x.gd": "for n in range(1, 10):\n    var pair := [\"MIS_CH01_08\", \"MIS_CH01_09\"]\n    var rows := {\"MIS_CH01_08\": 4, \"MIS_CH01_09\": 4}"}).is_empty(), "A loop, list and table extended to nine operations pass")
    check(stale_loop_gaps(9, {"res://x.gd": "for n in range(1, 10):"}).size() == 0 and stale_loop_gaps(10, {"res://x.gd": "for n in range(1, 10):"}).size() == 1, "The gate names the nine-operation loop once ten operations are playable")
    check(not stale_loop_gaps(10, {"res://x.gd": "for n in range(1,10):"}).is_empty(), "Negative control: the compact nine-operation spelling is refused once ten operations are playable")
    check(not stale_loop_gaps(10, {"res://x.gd": "const OPERATIONS := (1,2,3,4,5,6,7,8,9)"}).is_empty(), "Negative control: a tuple of operations 1-9 is refused")
    check(not stale_loop_gaps(10, {"res://x.gd": "const MISSIONS := [\"MIS_CH01_08\", \"MIS_CH01_09\"]"}).is_empty(), "Negative control: a mission list that ends at operation 9 is refused")
    check(not stale_loop_gaps(10, {"res://x.gd": "const ROWS := {\"MIS_CH01_08\": 3, \"MIS_CH01_09\": 4}"}).is_empty(), "Negative control: a per-mission table that ends at operation 9 is refused")
    check(stale_loop_gaps(10, {"res://x.gd": "for n in range(1, 11):\n    var pair := [\"MIS_CH01_09\", \"MIS_CH01_10\"]\n    var rows := {\"MIS_CH01_09\": 4, \"MIS_CH01_10\": 4}"}).is_empty(), "A loop, list and table extended to ten operations pass")
    var pending_id := ""
    for id in ids:
        if not Catalog.deployable(id): pending_id = id; break
    if not pending_id.is_empty():
        var pending := load_json(mission_path(pending_id))
        check(not gate(pending_id, true, pending).is_empty(), "Negative control: a held-back mission cannot be deployed early")
        var no_status := pending.duplicate(true)
        (no_status.staging as Dictionary).erase("status")
        check(not gate(pending_id, false, no_status).is_empty(), "Negative control: a held-back mission without its staging status is refused")
        var bad_boss := pending.duplicate(true)
        ((bad_boss.staging as Dictionary).boss as Dictionary)["id"] = "BOSS_SITE7_FORGEMASTER_01"
        check(not gate(pending_id, false, bad_boss).is_empty(), "Negative control: a planned boss id with a banned fragment is refused")
        var placeholder := pending.duplicate(true)
        ((placeholder.main_route[4] as Dictionary).encounter[0] as Dictionary)["enemy_id"] = "BOSS_SITE7_CARRIER_01"
        check(not gate(pending_id, false, placeholder).is_empty(), "Negative control: a registered boss replaced by another boss's row is refused")
        var wrong_pattern := pending.duplicate(true)
        ((wrong_pattern.staging as Dictionary).boss as Dictionary)["pattern"] = "carrier_null"
        check(not gate(pending_id, false, wrong_pattern).is_empty(), "Negative control: a staging pattern that differs from the registered boss is refused")
    print("SITE7_CAMPAIGN_DATA: %s (%d checks)" % ["PASS" if failures.is_empty() else "FAIL", checks])
    for failure in failures: print("  FAIL ", failure)
    quit(0 if failures.is_empty() else 1)
