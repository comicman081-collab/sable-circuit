extends SceneTree
## Claude review instrument (N-1 differential, version 2): like nav_direction_dump.gd, plus
##   * blocked8: does the operator's real body bump into something within 8 px along the returned direction
##     (CharacterBody2D.test_move against the project's own collision layers - independent of the planner's own query),
##   * plen: length of the route the planner committed to (straight line when it sees the goal, else origin -> nodes -> goal),
##   * --actor=robot: use the room's first lane robot (drone / skimmer / shield, as firing_lane_search_smoke does) as the
##     probe instead of the controlled operator, to see the 4 px wider robot colliders on the same grid.
##
##   (robot mode: a disabled-process robot has no physics space, so blocked8 is not measured and stays 0; direction and plen are unaffected,
##    the planner queries the world space, not the body's own)
## Godot --headless --path <project> -s res://.cache/nav_direction_dump2.gd -- --out=res://.cache/x.csv [--cell=12]
##       [--missions=1,2] [--actor=operator|robot]
## CSV rows: mission,room,step,x,y,dx,dy,blocked8,plen
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TACTICS := preload("res://scripts/combat/site7_enemy_tactics.gd")
const STEPS: Array[int] = [1, 3, 4]
const GOAL_SKIP := 30.0
const LANE_ROLES := ["drone", "skimmer", "shield"]
var cell := 12.0
var out := ""
var actor_kind := "operator"
var missions: Array[String] = []
var lines := PackedStringArray()
var skipped_rooms: Array[String] = []

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
        if arg.begins_with("--actor="): actor_kind = arg.get_slice("=", 1)
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
    print("NAV_DIRECTION_DUMP2: %d rows, actor %s, cell %.0f px, %.1f s, rooms without a robot: %s" % [lines.size(), actor_kind, cell, float(Time.get_ticks_msec() - started) / 1000.0, str(skipped_rooms)])
    quit(0)

func _room(mission_id: String, step: int) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await _frames(8)
    stage.start_battle_preview(step)
    await _frames(4)
    var room_id := str(stage.main_route[stage.current_step].id)
    var field: Node = stage.battlefield
    var goal: Vector2 = field.squad_spawn(0)
    var probe: Node2D = stage.squad.get_active_operator()
    var body: CharacterBody2D = probe
    if actor_kind == "robot":
        stage.debug_spawn_encounter_for_step(step)
        await _frames(2)
        for node in get_nodes_in_group("m3_enemies"): node.process_mode = Node.PROCESS_MODE_DISABLED
        for operator in stage.squad.operators: operator.process_mode = Node.PROCESS_MODE_DISABLED
        var chosen: EnemyActor = null
        for node in get_nodes_in_group("m3_enemies"):
            var enemy := node as EnemyActor
            if enemy == null or not is_instance_valid(enemy.machine_sprite): continue
            if str(TACTICS.ROLES.get(enemy.enemy_id, "")) in LANE_ROLES:
                chosen = enemy
                break
        if chosen == null:
            skipped_rooms.append("%s %s" % [mission_id, room_id])
            print("NAV_DUMP_ROOM %s %s SKIPPED (no lane robot)" % [mission_id, room_id])
            stage.free()
            await _frames(3)
            return
        probe = chosen
        body = chosen
    var floor_polygon: PackedVector2Array = field.polygon
    var box := Rect2(floor_polygon[0], Vector2.ZERO)
    for vertex in floor_polygon: box = box.expand(vertex)
    var obstacles: Array[Rect2] = NAV.ground_obstacles(probe, goal)
    var x := box.position.x
    var rows := 0
    var dead := 0
    var blocked := 0
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
            probe.global_position = point
            var planner := NAV.new()
            var d: Vector2 = planner.direction(probe, goal, 1.0 / 60.0)
            var plen := 0.0
            if planner._direct:
                plen = point.distance_to(goal)
            elif not planner._path.is_empty():
                var cursor := point
                for node in planner._path:
                    plen += cursor.distance_to(node)
                    cursor = node
            var is_blocked := 0
            if d.length_squared() < 0.0001:
                dead += 1
            elif actor_kind != "robot" and body.test_move(body.global_transform, d.normalized() * 8.0):
                is_blocked = 1
                blocked += 1
            lines.append("%s,%s,%d,%.1f,%.1f,%.5f,%.5f,%d,%.1f" % [mission_id, room_id, step, point.x, point.y, d.x, d.y, is_blocked, plen])
            rows += 1
        x += cell
    print("NAV_DUMP_ROOM %s %s rows=%d dead=%d blocked8=%d" % [mission_id, room_id, rows, dead, blocked])
    stage.free()
    await _frames(3)
