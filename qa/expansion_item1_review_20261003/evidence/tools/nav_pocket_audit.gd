extends SceneTree
## Claude review scratch probe: where does CoverNavigation return ZERO although the point is open floor?
## For every mission and combat room (steps 1, 3, 4) it samples the walkable floor outside the inflated cover boxes and asks a fresh
## planner for a direction to the squad start. A cell that gets ZERO has no way out for an AI that stands there.
## Run: godot --headless --path <project> -s res://.cache/probe/nav_pocket_audit.gd -- --cell=12 --missions=1,2 --out=res://.cache/probe/nav_audit.json
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
var cell := 12.0
var out := "res://.cache/probe/nav_audit.json"
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
        if arg.begins_with("--cell="): cell = float(arg.get_slice("=", 1))
        if arg.begins_with("--missions="):
            for n in arg.get_slice("=", 1).split(","): missions.append("MIS_CH01_%02d" % int(n))
    if missions.is_empty():
        for n in range(1, 11): missions.append("MIS_CH01_%02d" % n)
    for mission_id in missions:
        for step in [1, 3, 4]:
            await _room(mission_id, step)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
    var file := FileAccess.open(out, FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify({"cell": cell, "rooms": report}, "  "))
        file.close()
    var total_zero := 0
    for row: Dictionary in report: total_zero += int(row.zero_cells)
    print("NAV_POCKET_AUDIT rooms=", report.size(), " zero_cells=", total_zero, " cell=", cell)
    quit(0)

func _room(mission_id: String, step: int) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await _frames(8)
    stage.start_battle_preview(step)
    await _frames(4)
    var active := stage.squad.get_active_operator()
    var room_id := str(stage.main_route[stage.current_step].id)
    var goal: Vector2 = stage.battlefield.squad_spawn(0)
    var field = stage.battlefield
    var polys: Array = field.get("_world_polygons")
    var box := Rect2()
    var first := true
    var centre: Vector2 = field.get("_center")
    # Room floor bounds: the begin_encounter polygon (field.polygon) is the room's own floor.
    var poly: PackedVector2Array = field.polygon
    for v in poly:
        if first: box = Rect2(v, Vector2.ZERO); first = false
        else: box = box.expand(v)
    var obstacles: Array[Rect2] = NAV.ground_obstacles(active, centre)
    var walkable := 0
    var zero: Array = []
    var x := box.position.x
    while x <= box.end.x:
        var y := box.position.y
        while y <= box.end.y:
            var p := Vector2(x, y)
            var skip: bool = not field.is_walkable(p)
            if not skip:
                for rect in obstacles:
                    if rect.has_point(p): skip = true; break
            if not skip and p.distance_to(goal) > 30.0:
                walkable += 1
                active.global_position = p
                var d := NAV.new().direction(active, goal, 1.0 / 60.0)
                if d.length_squared() < 0.0001: zero.append(p)
            y += cell
        x += cell
    var clusters: Array = []
    # Greedy clustering of zero cells (adjacent within 1.5 cells).
    var used := {}
    for i in range(zero.size()):
        if used.has(i): continue
        var queue := [i]
        used[i] = true
        var lo: Vector2 = zero[i]
        var hi: Vector2 = zero[i]
        var count := 0
        while not queue.is_empty():
            var k: int = queue.pop_back()
            count += 1
            lo = Vector2(minf(lo.x, zero[k].x), minf(lo.y, zero[k].y))
            hi = Vector2(maxf(hi.x, zero[k].x), maxf(hi.y, zero[k].y))
            for j in range(zero.size()):
                if used.has(j): continue
                if (zero[j] as Vector2).distance_to(zero[k]) <= cell * 1.5:
                    used[j] = true
                    queue.append(j)
        clusters.append({"cells": count, "bbox": [int(lo.x), int(lo.y), int(hi.x), int(hi.y)]})
    clusters.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return int(a.cells) > int(b.cells))
    var entry := {"mission": mission_id, "room": room_id, "step": step, "walkable_cells": walkable, "zero_cells": zero.size(), "clusters": clusters.slice(0, 8), "cover_boxes": obstacles.size()}
    report.append(entry)
    print("AUDIT ", mission_id, " ", room_id, " walkable=", walkable, " zero=", zero.size(), " clusters=", clusters.size(), " top=", JSON.stringify(clusters.slice(0, 2)))
    stage.free()
    await _frames(3)
