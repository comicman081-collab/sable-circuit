extends SceneTree
## Claude review instrument (N-1 differential): dump CoverNavigation.direction for every sampled walkable cell of every combat
## room, so the same dump from the tree before and after Codex's navigation fix can be compared cell by cell
## (nav_dump_diff.py). Same sampling as tools/environment/audit_nav_pockets.gd (floor cells outside inflated cover boxes,
## fresh planner per cell, goal = squad start), but it records the vector instead of only counting zeros.
##
## Godot --headless --path <project> -s res://<this file> -- --out=res://.cache/nav_dump.csv [--cell=24] [--missions=1,2]
## CSV rows: mission,room,step,x,y,dx,dy   (dx,dy to 5 decimals; 0.00000,0.00000 = dead cell)
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const STEPS: Array[int] = [1, 3, 4]
const GOAL_SKIP := 30.0
var cell := 24.0
var out := ""
var missions: Array[String] = []
var lines := PackedStringArray()

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
    var started := Time.get_ticks_msec()
    for mission_id in missions:
        for step in STEPS: await _room(mission_id, step)
    if out != "":
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
        var file := FileAccess.open(out, FileAccess.WRITE)
        if file != null:
            file.store_string("\n".join(lines) + "\n")
            file.close()
    print("NAV_DIRECTION_DUMP: %d rows, cell %.0f px, %.1f s" % [lines.size(), cell, float(Time.get_ticks_msec() - started) / 1000.0])
    quit(0)

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
    var x := box.position.x
    var rows := 0
    var dead := 0
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
            operator.global_position = point
            var d: Vector2 = NAV.new().direction(operator, goal, 1.0 / 60.0)
            if d.length_squared() < 0.0001: dead += 1
            lines.append("%s,%s,%d,%.1f,%.1f,%.5f,%.5f" % [mission_id, room_id, step, point.x, point.y, d.x, d.y])
            rows += 1
        x += cell
    print("NAV_DUMP_ROOM %s %s rows=%d dead=%d" % [mission_id, room_id, rows, dead])
    stage.free()
    await _frames(3)
