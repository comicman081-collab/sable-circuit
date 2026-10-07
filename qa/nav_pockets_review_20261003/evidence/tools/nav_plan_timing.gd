extends SceneTree
## Claude review instrument (N-07): time only the planner. Same rooms and sampling as tools/environment/audit_nav_pockets.gd
## (steps 1, 3 and 4 of every mission, walkable floor cells outside the inflated cover boxes, a fresh CoverNavigation per cell,
## goal = squad start), but the clock runs around NAV.new().direction() alone, so stage loading, scene setup and Godot
## start-up are not in the number. Prints one line per room and a total.
##
## Godot --headless --path <project> -s res://.cache/nav_plan_timing.gd -- --out=res://.cache/timing.json [--cell=12] [--missions=1,2]
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const STEPS: Array[int] = [1, 3, 4]
const GOAL_SKIP := 30.0
var cell := 12.0
var out := ""
var missions: Array[String] = []
var rooms: Array[Dictionary] = []

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
    var wall := Time.get_ticks_msec()
    for mission_id in missions:
        for step in STEPS: await _room(mission_id, step)
    var total_us := 0
    var calls := 0
    var dead := 0
    for row in rooms:
        total_us += int(row.plan_us)
        calls += int(row.calls)
        dead += int(row.dead)
    if out != "":
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
        var file := FileAccess.open(out, FileAccess.WRITE)
        if file != null:
            file.store_string(JSON.stringify({"cell_px": cell, "plan_us": total_us, "calls": calls, "dead": dead, "rooms": rooms}, "  "))
            file.close()
    print("NAV_PLAN_TIMING: plan %.3f s over %d calls (%.1f us per call), dead %d, wall %.1f s" % [float(total_us) / 1.0e6, calls, float(total_us) / maxf(1.0, float(calls)), dead, float(Time.get_ticks_msec() - wall) / 1000.0])
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
    var calls := 0
    var dead := 0
    var plan_us := 0
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
            operator.global_position = point
            var planner := NAV.new()
            var t0 := Time.get_ticks_usec()
            var d: Vector2 = planner.direction(operator, goal, 1.0 / 60.0)
            plan_us += Time.get_ticks_usec() - t0
            calls += 1
            if d.length_squared() < 0.0001: dead += 1
        x += cell
    rooms.append({"mission": mission_id, "room": room_id, "step": step, "calls": calls, "dead": dead, "plan_us": plan_us})
    print("NAV_TIMING_ROOM %s %s calls=%d dead=%d plan=%.3f s" % [mission_id, room_id, calls, dead, float(plan_us) / 1.0e6])
    stage.free()
    await _frames(3)
