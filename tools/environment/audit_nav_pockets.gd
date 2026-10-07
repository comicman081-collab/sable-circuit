extends SceneTree
## Audit: where does CoverNavigation give an AI operator no way out of open floor?
##
## For every combat room (steps 1, 3 and 4: R02, R04 and the boss room) of every mission it samples the
## walkable floor outside the inflated cover boxes and asks a fresh planner for a direction to the squad
## start, a point that is always reachable. A cell that gets a zero vector is a dead end: an AI follower, or
## the full-operation bot, standing there waits forever, although a player on WASD walks out. Cells are
## grouped into clusters with their bounding boxes.
##
## First measured 2026-10-03 (cell 12 px): 70 zero cells in 4 of 30 rooms, all older than the expansion
## work: MIS_CH01_01 R02_CORRIDOR (23), MIS_CH01_05 R05_CARRIER (9), MIS_CH01_09 R04_GALLERY (23, the
## wedge under a barrier prop where the baseline full_op_09 froze for 600 s) and MIS_CH01_10 R04_GALLERY (15).
## The planner drops the inflated cover boxes' corner nodes that fall off the floor (CORNER_CLEARANCE), so a
## floor wedge thinner than the actor between a box and a wall keeps no node to route from.
##
## Godot --headless --path . -s res://tools/environment/audit_nav_pockets.gd -- [--cell=12] [--missions=1,2]
##       [--out=res://.cache/nav_pockets.json]
## Exit 0 when no room has a dead end, 1 otherwise. Technical audit: no art, balance or play approval.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const STEPS: Array[int] = [1, 3, 4]
## Cells this close to the goal always see it directly.
const GOAL_SKIP := 30.0
var cell := 12.0
var out := ""
var missions: Array[String] = []
var report: Array[Dictionary] = []

func _init() -> void:
    call_deferred("_run")

func _frames(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func _run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
        if arg.begins_with("--cell="): cell = maxf(4.0, float(arg.get_slice("=", 1)))
        if arg.begins_with("--missions="):
            for number in arg.get_slice("=", 1).split(","): missions.append("MIS_CH01_%02d" % int(number))
    if missions.is_empty():
        for number in range(1, 11): missions.append("MIS_CH01_%02d" % number)
    for mission_id in missions:
        for step in STEPS: await _room(mission_id, step)
    var cells := 0
    var rooms := 0
    for row in report:
        cells += int(row.zero_cells)
        if int(row.zero_cells) > 0: rooms += 1
    if out != "":
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
        var file := FileAccess.open(out, FileAccess.WRITE)
        if file != null:
            file.store_string(JSON.stringify({"cell_px": cell, "rooms": report}, "  "))
            file.close()
    print("NAV_POCKET_AUDIT: %s (%d dead-end cells in %d of %d rooms, cell %.0f px)" % ["PASS" if cells == 0 else "FAIL", cells, rooms, report.size(), cell])
    quit(0 if cells == 0 else 1)

func _room(mission_id: String, step: int) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await _frames(8)
    stage.start_battle_preview(step)
    await _frames(4)
    var operator := stage.squad.get_active_operator()
    var room_id := str(stage.main_route[stage.current_step].id)
    var field: Node = stage.battlefield
    var goal: Vector2 = field.squad_spawn(0)
    var floor_polygon: PackedVector2Array = field.polygon
    var box := Rect2(floor_polygon[0], Vector2.ZERO)
    for vertex in floor_polygon: box = box.expand(vertex)
    var obstacles: Array[Rect2] = NAV.ground_obstacles(operator, goal)
    var walkable := 0
    var dead: Array[Vector2] = []
    var x := box.position.x
    while x <= box.end.x:
        var y := box.position.y
        while y <= box.end.y:
            var point := Vector2(x, y)
            y += cell
            if not bool(field.call("is_walkable", point)) or point.distance_to(goal) <= GOAL_SKIP: continue
            var covered := false
            for rect in obstacles:
                if rect.has_point(point):
                    covered = true
                    break
            if covered: continue
            walkable += 1
            operator.global_position = point
            if NAV.new().direction(operator, goal, 1.0 / 60.0).length_squared() < 0.0001: dead.append(point)
        x += cell
    var clusters := _clusters(dead)
    report.append({"mission": mission_id, "room": room_id, "step": step, "walkable_cells": walkable, "zero_cells": dead.size(),
        "cover_boxes": obstacles.size(), "clusters": clusters.slice(0, 8)})
    print("NAV_POCKET_ROOM %s %s walkable=%d dead=%d clusters=%s" % [mission_id, room_id, walkable, dead.size(), JSON.stringify(clusters.slice(0, 3))])
    stage.free()
    await _frames(3)

## Cells within 1.5 cell widths of each other form one cluster; largest first.
func _clusters(dead: Array[Vector2]) -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    var seen := {}
    for first in range(dead.size()):
        if seen.has(first): continue
        var stack: Array[int] = [first]
        seen[first] = true
        var low := dead[first]
        var high := dead[first]
        var count := 0
        while not stack.is_empty():
            var index: int = stack.pop_back()
            count += 1
            low = Vector2(minf(low.x, dead[index].x), minf(low.y, dead[index].y))
            high = Vector2(maxf(high.x, dead[index].x), maxf(high.y, dead[index].y))
            for other in range(dead.size()):
                if seen.has(other) or dead[other].distance_to(dead[index]) > cell * 1.5: continue
                seen[other] = true
                stack.append(other)
        result.append({"cells": count, "bbox": [int(low.x), int(low.y), int(high.x), int(high.y)]})
    result.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return int(a.cells) > int(b.cells))
    return result
