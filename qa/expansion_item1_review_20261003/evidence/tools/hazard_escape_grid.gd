extends SceneTree
## Claude review scratch probe (not part of the repo), item 1: V-14 / V-15 and a position dump.
## For every mission room that declares hazards it loads the REAL room (battle preview, hazards placed by the stage),
## then for each hazard
##   - dumps its position and type (compare base against after to see which rooms moved),
##   - checks placement facts (squad start, first-wave slots, floor and cover under its rim, spacing),
##   - for damaging kinds, walks every standable grid point inside the hazard: nearest straight walk (10 px rings, 64 bearings)
##     to a spot outside the hazard (+24 px) on painted floor, clear of cover; time = distance / 138 + 0.25 against the warning.
## Run: godot --headless --path <project> -s res://.cache/probe/hazard_escape_grid.gd -- --grid=25 --missions=6,7 --out=res://.cache/probe/x.json
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const WALK := 138.0
const REACT := 0.25
const EXIT_MARGIN := 24.0
var grid := 25.0
var out := "res://.cache/probe/hazard_escape.json"
var missions: Array[String] = []
var report: Array = []

func _init() -> void:
    call_deferred("_run")

func _frames(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func _run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
        if arg.begins_with("--grid="): grid = float(arg.get_slice("=", 1))
        if arg.begins_with("--missions="):
            for n in arg.get_slice("=", 1).split(","): missions.append("MIS_CH01_%02d" % int(n))
    if missions.is_empty():
        for n in range(1, 11): missions.append("MIS_CH01_%02d" % n)
    for mission_id in missions:
        for step in [1, 3]:
            await _room(mission_id, step)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
    var file := FileAccess.open(out, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify({"grid": grid, "rooms": report}, "  "))
        file.close()
    var failing := 0
    var unreachable := 0
    var hazards := 0
    for row: Dictionary in report:
        for h: Dictionary in row.hazards:
            hazards += 1
            failing += int(h.get("escape_failing", 0))
            unreachable += int(h.get("escape_unreachable", 0))
    print("HAZARD_ESCAPE_GRID rooms=", report.size(), " hazards=", hazards, " failing_points=", failing, " unreachable_points=", unreachable, " grid=", grid)
    quit(0)

func _standable(stage: StoryStage01, obstacles: Array[Rect2], point: Vector2) -> bool:
    if not stage.battlefield.is_walkable(point): return false
    for rect in obstacles:
        if rect.has_point(point): return false
    return true

func _room(mission_id: String, step: int) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await _frames(8)
    stage.start_battle_preview(step)
    await _frames(4)
    var room_id := str(stage.main_route[stage.current_step].id)
    var declared := 0
    for row_variant in stage.main_route[stage.current_step].get("hazards", []):
        declared += int((row_variant as Dictionary).get("count", 1))
    var victim := stage.squad.get_active_operator()
    var live: Array = []
    for node in get_nodes_in_group("zone_hazards"):
        if node is ZoneHazard and stage.is_ancestor_of(node) and not node.is_queued_for_deletion(): live.append(node)
    var entry := {"mission": mission_id, "room": room_id, "step": stage.current_step, "declared": declared, "placed": live.size(), "hazards": []}
    var width := victim.get_combat_hit_rect().size.x
    for i in range(live.size()):
        var h: ZoneHazard = live[i]
        var obstacles: Array[Rect2] = NAV.ground_obstacles(victim, h.global_position)
        var info := {"type": h.hazard_id, "x": snappedf(h.global_position.x, 0.01), "y": snappedf(h.global_position.y, 0.01), "radius": h.radius, "band": h.has_method("is_band") and h.is_band()}
        var squad_d := INF
        for s in range(3): squad_d = minf(squad_d, h.global_position.distance_to(stage.battlefield.squad_spawn(s)))
        var slot_d := INF
        for s in range(4): slot_d = minf(slot_d, h.global_position.distance_to(stage.battlefield.enemy_spawn(s)))
        info["min_squad_start_distance"] = snappedf(squad_d, 0.1)
        info["min_first_wave_slot_distance"] = snappedf(slot_d, 0.1)
        var bad_rim := 0
        var rim := PackedVector2Array()
        if h.has_method("boundary_points"):
            rim = h.boundary_points(32, 0.0)
        else:
            for k in range(32): rim.append(h.global_position + Vector2.from_angle(TAU * float(k) / 32.0) * Vector2(h.radius, h.radius * 0.55))
        for point in rim:
            if not _standable(stage, obstacles, point): bad_rim += 1
        info["rim_points"] = rim.size()
        info["rim_off_floor_or_in_cover"] = bad_rim
        var min_gap := INF
        for j in range(live.size()):
            if j == i: continue
            min_gap = minf(min_gap, h.global_position.distance_to((live[j] as ZoneHazard).global_position))
        info["nearest_other_hazard_distance"] = snappedf(min_gap, 0.1) if is_finite(min_gap) else -1.0
        var damaging := float(h.spec.get("operator_damage", 0.0)) > 0.0 or float(h.spec.get("operator_dps", 0.0)) > 0.0
        info["damaging"] = damaging
        if damaging:
            var warning := float(h.spec.get("telegraph", 0.0))
            info["telegraph"] = warning
            var inside := 0
            var failing := 0
            var unreachable := 0
            var worst := 0.0
            var tight := 99.0
            var tight_at := ""
            var extent := h.radius + 40.0
            var steps := int(extent / grid) + 1
            for ix in range(-steps, steps + 1):
                for iy in range(-steps, steps + 1):
                    var p := h.global_position + Vector2(float(ix), float(iy)) * grid
                    if not h.contains(p): continue
                    if not _standable(stage, obstacles, p): continue
                    inside += 1
                    var found := -1.0
                    for r in range(10, 411, 10):
                        for b in range(64):
                            var dir := Vector2.from_angle(float(b) * TAU / 64.0)
                            var q := p + dir * float(r)
                            if h.contains(q, EXIT_MARGIN): continue
                            var tangent := dir.orthogonal() * width * 0.5
                            if not _standable(stage, obstacles, q) or not _standable(stage, obstacles, q - tangent) or not _standable(stage, obstacles, q + tangent): continue
                            if not NAV._clear_ground(victim, p, q, obstacles): continue
                            found = float(r)
                            break
                        if found > 0.0: break
                    if found < 0.0:
                        unreachable += 1
                        if tight_at == "": tight_at = "unreachable at (%d, %d)" % [int(p.x), int(p.y)]
                        continue
                    worst = maxf(worst, found)
                    var margin := warning - (found / WALK + REACT)
                    if margin < tight: tight = margin; tight_at = "(%d, %d) leave %d px in %.2f s of %.2f s" % [int(p.x), int(p.y), int(found), found / WALK, warning]
                    if margin < 0.0: failing += 1
            info["escape_points_inside"] = inside
            info["escape_failing"] = failing
            info["escape_unreachable"] = unreachable
            info["escape_worst_walk_px"] = worst
            info["escape_tightest_margin_s"] = snappedf(tight, 0.01) if tight < 99.0 else null
            info["escape_tightest_at"] = tight_at
        entry.hazards.append(info)
    report.append(entry)
    print("ROOM ", mission_id, " ", room_id, " declared=", declared, " placed=", live.size(), " ", JSON.stringify(entry.hazards.map(func(x: Dictionary) -> String: return "%s@(%d,%d)" % [x.type, int(x.x), int(x.y)])))
    stage.free()
    await _frames(3)
