extends SceneTree
## Claude review instrument (N-1): physical walk-out of listed floor cells.
##
## Codex's cover_navigation_smoke walks four pinned points. This walks as many cells as a CSV lists, with the same
## real CharacterBody2D loop (debug_drive + _physics_process at 1/60 s), so the tree before and after the fix can be
## compared on the very same cells: does an operator standing there reach the squad start, how long does it stand
## still, does it leave the painted floor?
##
## Godot --headless --fixed-fps 60 --path <project> -s res://.cache/nav_walkout.gd -- --cells=res://.cache/cells.csv
##       --out=res://.cache/walk.json [--max_s=20] [--stuck_s=3]
## CSV rows: mission,step,x,y   (mission as 1..10 or MIS_CH01_NN; further columns are ignored; # lines are comments)
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
var cells_path := ""
var out := ""
var max_s := 20.0
var stuck_s := 3.0
var results: Array[Dictionary] = []

func _init() -> void:
    call_deferred("_run")

func _frames(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func _run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--cells="): cells_path = arg.get_slice("=", 1)
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
        if arg.begins_with("--max_s="): max_s = float(arg.get_slice("=", 1))
        if arg.begins_with("--stuck_s="): stuck_s = float(arg.get_slice("=", 1))
    var file := FileAccess.open(cells_path, FileAccess.READ)
    if file == null:
        printerr("NAV_WALKOUT: cannot read %s" % cells_path)
        quit(2)
        return
    var order: Array[String] = []
    var groups := {}
    while not file.eof_reached():
        var line := file.get_line().strip_edges()
        if line == "" or line.begins_with("#"): continue
        var parts := line.split(",")
        if parts.size() < 4: continue
        var mission := parts[0] if parts[0].begins_with("MIS_") else "MIS_CH01_%02d" % int(parts[0])
        var key := "%s|%d" % [mission, int(parts[1])]
        if not groups.has(key):
            groups[key] = []
            order.append(key)
        (groups[key] as Array).append(Vector2(float(parts[2]), float(parts[3])))
    var started := Time.get_ticks_msec()
    for key in order:
        await _room(key.get_slice("|", 0), int(key.get_slice("|", 1)), groups[key])
    var reached := 0
    var stuck := 0
    var left := 0
    for row in results:
        if bool(row.reached): reached += 1
        if bool(row.stuck): stuck += 1
        if bool(row.left_floor): left += 1
    if out != "":
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out).get_base_dir())
        var handle := FileAccess.open(out, FileAccess.WRITE)
        if handle != null:
            handle.store_string(JSON.stringify({"max_s": max_s, "stuck_s": stuck_s, "rows": results}, "  "))
            handle.close()
    print("NAV_WALKOUT: %d cells, %d reached the squad start, %d stuck, %d left the floor, %.1f s" % [results.size(), reached, stuck, left, float(Time.get_ticks_msec() - started) / 1000.0])
    quit(0)

func _room(mission_id: String, step: int, points: Array) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await _frames(8)
    stage.start_battle_preview(step)
    stage.set_process(false)
    stage.set_physics_process(false)
    stage.squad.set_process(false)
    stage.squad.set_physics_process(false)
    for operator in stage.squad.operators:
        operator.set_process(false)
        operator.set_physics_process(false)
    for enemy in get_nodes_in_group("m3_enemies"): enemy.process_mode = Node.PROCESS_MODE_DISABLED
    for node in stage.find_children("*", "", true, false):
        if node is ZoneHazard: node.process_mode = Node.PROCESS_MODE_DISABLED
    await _frames(4)
    var operator := stage.squad.get_active_operator()
    var room_id := str(stage.main_route[stage.current_step].id)
    var goal: Vector2 = stage.battlefield.squad_spawn(0)
    operator._debug_run = true
    var done := 0
    for point: Vector2 in points:
        operator.global_position = point
        operator.velocity = Vector2.ZERO
        await physics_frame
        var first: Vector2 = NAV.new().direction(operator, goal, 1.0 / 60.0, operator.run_speed / 60.0)
        var nav := NAV.new()
        var still := 0.0
        var longest_still := 0.0
        var left_floor := false
        var travelled := 0.0
        var ticks := 0
        var max_ticks := int(max_s * 60.0)
        for tick in range(max_ticks):
            if operator.global_position.distance_to(goal) <= 12.0: break
            await physics_frame
            var before := operator.global_position
            operator.debug_drive(nav.direction(operator, goal, 1.0 / 60.0, operator.run_speed / 60.0), Vector2.RIGHT)
            operator._physics_process(1.0 / 60.0)
            ticks = tick + 1
            var moved := before.distance_to(operator.global_position)
            travelled += moved
            left_floor = left_floor or not stage.battlefield.is_walkable(operator.global_position)
            still = still + 1.0 / 60.0 if moved < 0.08 else 0.0
            longest_still = maxf(longest_still, still)
            if still >= stuck_s: break
        results.append({"mission": mission_id, "room": room_id, "step": step, "x": point.x, "y": point.y,
            "first_zero": first.length_squared() < 0.0001, "reached": operator.global_position.distance_to(goal) <= 12.0,
            "stuck": longest_still >= stuck_s, "ticks": ticks, "remaining": snappedf(operator.global_position.distance_to(goal), 0.01),
            "travelled": snappedf(travelled, 0.1), "longest_still": snappedf(longest_still, 0.001), "left_floor": left_floor,
            "end_x": snappedf(operator.global_position.x, 0.1), "end_y": snappedf(operator.global_position.y, 0.1)})
        done += 1
    print("NAV_WALKOUT_ROOM %s %s step=%d cells=%d" % [mission_id, room_id, step, done])
    stage.free()
    await _frames(3)
