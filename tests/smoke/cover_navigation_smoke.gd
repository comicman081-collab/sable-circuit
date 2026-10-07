extends SceneTree
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const PROP := preload("res://scripts/missions/site7_environment_prop.gd")
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var checks := 0
var failures: Array[String] = []

class Target extends Node2D:
    func get_combat_hit_rect() -> Rect2: return Rect2(global_position-Vector2(8,8),Vector2(16,16))
    func get_combat_aim_point() -> Vector2: return global_position

func _init() -> void: call_deferred("run")
func check(ok: bool, note: String) -> void:
    checks+=1
    if not ok: failures.append(note); push_error(note)
func run() -> void:
    # Synthetic pixels are geometry fixtures only; never registered as art.
    var image := Image.create(80,80,false,Image.FORMAT_RGBA8)
    image.fill(Color.TRANSPARENT)
    image.fill_rect(Rect2i(20,20,40,40),Color.WHITE)
    var prop := PROP.new()
    root.add_child(prop)
    prop.configure(ImageTexture.create_from_image(image),image,
        {"projected_width_px":80,"root_px":[40,40],"ground_px":[[20,20],[60,20],[60,60],[20,60]]},80)
    prop.global_position=Vector2(300,300)
    prop.set_active(true)
    var target := Target.new()
    root.add_child(target)
    target.add_to_group("prototype_targets")
    target.global_position=Vector2(400,300)
    check(not NAV.clear_shot(self,Vector2(200,300),target),"Opaque cover blocks target")
    check(NAV.reticle_blocked(self,Vector2(200,300),Vector2(400,300)),"Reticle displays blocked ray")
    target.global_position=Vector2(250,300)
    check(NAV.clear_shot(self,Vector2(200,300),target),"Cover behind damage entry does not block target")
    check(not NAV.reticle_blocked(self,Vector2(200,300),Vector2(400,300)),"Reticle ignores cover behind first target")
    target.global_position=Vector2(400,260)
    check(NAV.clear_shot(self,Vector2(200,260),target),"Transparent image margin stays open")
    prop.set_active(false)
    check(NAV.first_cover(self,Vector2(200,300),Vector2(400,300))==null,"Streamed-out prop is not a shot obstruction")
    prop.set_active(true)
    var actor := CharacterBody2D.new()
    root.add_child(actor)
    actor.global_position=Vector2(200,300)
    var collider := CollisionShape2D.new()
    collider.name="CollisionShape2D"
    var shape := CircleShape2D.new()
    shape.radius=12
    collider.shape=shape
    collider.position=Vector2(0,-18)
    actor.add_child(collider)
    var obstacles := NAV.ground_obstacles(actor)
    check(obstacles.size()==1 and obstacles[0].get_center().is_equal_approx(Vector2(300,318)),"Collider offset included in root-space obstacle")
    var nav := NAV.new()
    var path := nav._plan(actor,actor.global_position,Vector2(400,300),obstacles)
    check(path.size()>=3,"Visibility graph routes around box, not through it")
    var prev := actor.global_position
    for point in path:
        check(NAV._clear_ground(actor,prev,point,obstacles),"Every planned edge avoids inflated collision")
        prev=point
    var goal := NAV._free_goal(actor,Vector2(300,318),obstacles)
    check(goal.is_finite() and not obstacles[0].has_point(goal),"Goal inside prop projects outside")
    var forward := nav.direction(actor,Vector2(400,300),1.0/60)
    check(absf(forward.y)>0.05,"Navigation steers laterally before collision")
    var plans := nav.replans
    for tick in range(5): nav.direction(actor,Vector2(400,300),1.0/60)
    check(nav.replans==plans,"Static route is cached across nearby physics ticks")
    prop.set_active(false)
    check(nav.direction(actor,Vector2(400,300),1.0/60).is_equal_approx(Vector2.RIGHT),"Stream change drops obsolete path immediately")
    target.free(); prop.free(); actor.free()
    await _pocket_walk_contract()
    print("COVER_NAVIGATION_SMOKE: %s / %d checks"%["PASS" if failures.is_empty() else "FAIL",checks])
    quit(0 if failures.is_empty() else 1)

func _pocket_walk_contract() -> void:
    # Pinned inside the four clusters found by the unchanged 12 px audit.
    # This checks real CharacterBody2D movement, not just a nonzero direction.
    var cases := [
        {"mission": 1, "step": 1, "point": Vector2(3766, -289)},
        {"mission": 5, "step": 4, "point": Vector2(12246, -3639)},
        {"mission": 9, "step": 3, "point": Vector2(-6013, 3856)},
        {"mission": 10, "step": 3, "point": Vector2(9472, -2149)},
    ]
    for row: Dictionary in cases:
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % int(row.mission)
        stage.battle_preview = true
        root.add_child(stage)
        for _tick in range(8): await physics_frame; await process_frame
        stage.start_battle_preview(int(row.step))
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
        for _tick in range(4): await physics_frame; await process_frame
        var operator := stage.squad.get_active_operator()
        var goal: Vector2 = stage.battlefield.squad_spawn(0)
        operator.global_position = row.point
        var origin := operator.global_position
        var obstacles := NAV.ground_obstacles(operator, goal)
        var label := "%s %s" % [stage.mission_id, stage.main_route[int(row.step)].id]
        check(NAV._clear_ground(operator, origin, origin, obstacles), label + " pocket fixture is on open painted floor")
        var nav := NAV.new()
        var path := nav._plan(operator, origin, goal, obstacles)
        check(not path.is_empty(), label + " pocket connects to the squad start")
        var previous := origin
        var all_edges_clear := not path.is_empty()
        for point in path:
            all_edges_clear = all_edges_clear and NAV._clear_ground(operator, previous, point, obstacles)
            previous = point
        check(all_edges_clear, label + " every planned escape edge stays on floor outside inflated cover")
        var still := 0.0
        var longest_still := 0.0
        var left_floor := false
        var tick_count := 0
        if not path.is_empty():
            operator._debug_run = true
            for tick in range(60 * 20):
                if operator.global_position.distance_to(goal) <= 12.0: break
                await physics_frame
                var before := operator.global_position
                operator.debug_drive(nav.direction(operator, goal, 1.0 / 60.0, operator.run_speed / 60.0), Vector2.RIGHT)
                operator._physics_process(1.0 / 60.0)
                tick_count = tick + 1
                left_floor = left_floor or not stage.battlefield.is_walkable(operator.global_position)
                still = still + 1.0 / 60.0 if before.distance_to(operator.global_position) < 0.08 else 0.0
                longest_still = maxf(longest_still, still)
        check(operator.global_position.distance_to(origin) > 30.0, label + " actual actor physically leaves the pocket")
        check(operator.global_position.distance_to(goal) <= 12.0, label + " actor reaches the squad start within 20 s")
        check(not left_floor, label + " physical escape never leaves painted floor")
        check(longest_still <= 0.8, label + " physical escape has no stationary interval over 0.8 s")
        print("POCKET_WALK %s ticks=%d remaining=%.2f longest_still=%.3f" % [label, tick_count, operator.global_position.distance_to(goal), longest_still])
        stage.free()
        for _tick in range(3): await physics_frame; await process_frame
