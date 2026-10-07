extends SceneTree
## Claude review scratch probe: ASCII map of walkable floor / NAV-dead points around the baseline operation 9 stall.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
func _init() -> void:
    call_deferred("_run")
func _frames(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame
func _run() -> void:
    var x0 := -6260.0
    var x1 := -5840.0
    var y0 := 3690.0
    var y1 := 3900.0
    var stepx := 6.0
    var stepy := 4.0
    var mission := "MIS_CH01_09"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): mission = arg.get_slice("=", 1)
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    stage.configure_campaign({}, "NAV-POCKET-MAP", {})
    await _frames(5)
    stage.current_step = 3
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(3)
    await _frames(10)
    var active := stage.squad.get_active_operator()
    var goal := Vector2(float(stage.optional_rooms[0].x), float(stage.optional_rooms[0].y))
    var nav := NAV.new()
    var rows: Array[String] = []
    var y := y0
    while y <= y1:
        var line := ""
        var x := x0
        while x <= x1:
            var p := Vector2(x, y)
            active.global_position = p
            var obstacles := NAV.ground_obstacles(active)
            var inside := false
            for rect in obstacles:
                if rect.has_point(p): inside = true
            if inside: line += "#"
            elif not NAV._on_floor(active, p): line += " "
            else:
                var d := NAV.new().direction(active, goal, 1.0 / 60.0)
                line += "Z" if d.length_squared() < 0.0001 else "."
            x += stepx
        rows.append("%7.0f " % y + line)
        y += stepy
    print("MAP x from ", x0, " step ", stepx, "; y from ", y0, " step ", stepy, "; '#'=inside inflated cover rect, ' '=off floor, 'Z'=floor but planner returns ZERO, '.'=floor and planner works")
    for r in rows: print(r)
    quit(0)
