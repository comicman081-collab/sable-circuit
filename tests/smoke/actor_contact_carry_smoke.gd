extends SceneTree
## Operators and robots in contact must not carry each other. Both are CharacterBody2Ds in
## Godot's default grounded motion mode although the game is top-down, so a body touched
## from its north side counts as floor, and grounded move_and_slide moves a body with the
## velocity of the floor it stands on. Uses the app's operator and robot bodies on a real
## battle floor. Each robot moves by its own move_and_slide at a gameplay speed (BULWARK
## crawl, CINDER approach and charge) while a controlled operator, then an AI follower
## holding its post, stands against its north side. Then an operator walks out from under
## a robot touching it from the north. Bodies are placed apart and the physics server
## settles before any contact, so no teleport is ridden. The operator AI, formation and
## mission flow are otherwise frozen. Report: --out (default under the git-ignored .cache).

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const TestOutput := preload("res://tests/support/test_output.gd")
const RAM := "ENM_SITE7_RAM_01"
const BULWARK := "ENM_SITE7_BULWARK_01"
## Displacement a carried body may show along the other body's motion (px).
const CARRY_TOLERANCE := 1.0

var out_path := TestOutput.path("res://.cache/tests/actor_contact_carry.json")
var checks := 0
var failures: Array[String] = []
var scenarios: Array[Dictionary] = []
var stage: StoryStage01
var lead: OperatorActor
var follower: OperatorActor
var robots: Dictionary = {}
var site := Vector2.INF

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)

func settle(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func run() -> void:
    stage = STAGE.instantiate() as StoryStage01
    # M1's first combat room is an open diamond; the M2 rooms are diagonal corridors
    # too narrow for the 370 x 120 px fixture.
    stage.mission_id = "MIS_CH01_01"
    stage.battle_preview = true
    root.add_child(stage)
    await settle(10)
    stage.start_battle_preview(1)
    await settle(4)
    # Only the measured bodies move: no mission flow, formation, hazards or other robots.
    stage.set_process(false)
    stage.set_physics_process(false)
    stage.squad.set_process(false)
    stage.squad.set_physics_process(false)
    stage._clear_hazards()
    for node in get_nodes_in_group("m3_enemies"): node.queue_free()
    for node in root.get_children():
        if node is PrototypeProjectile: node.queue_free()
    lead = stage.squad.get_active_operator()
    for member in stage.squad.operators:
        if member != lead and follower == null: follower = member
        use(member, false)
    for id in [BULWARK, RAM]:
        var robot := StoryStage01.ENEMY_SCENE.instantiate() as EnemyActor
        check(robot.configure(id, 5000.0), "%s is a runtime robot" % id)
        stage.add_child(robot)
        # Driven below through its own move_and_slide; its tactics would pick other moves.
        robot.set_physics_process(false)
        robot.remove_from_group("prototype_targets")
        robots[id] = robot
    await settle(2)
    site = _open_site()
    check(site.is_finite(), "open battle floor for the contact fixture")
    if not site.is_finite() or follower == null:
        _finish()
        return
    var hz := Engine.physics_ticks_per_second
    for row: Array in [[BULWARK, "BULWARK crawl", 62.0, 90], [RAM, "CINDER approach", 112.0, 60], [RAM, "CINDER charge", 360.0, 25]]:
        for rider: OperatorActor in [lead, follower]:
            await _robot_moves(robots[row[0]], rider, row[1], Vector2.RIGHT * float(row[2]), int(row[3]), hz)
    await _operator_walks_out(robots[BULWARK], hz)
    await _operator_walks_out(robots[RAM], hz)
    _finish()

## One robot moves east at a gameplay speed with an operator standing against its north side.
func _robot_moves(robot: EnemyActor, rider: OperatorActor, label: String, velocity: Vector2, ticks: int, hz: int) -> void:
    var role := "controlled operator" if rider == lead else "AI follower"
    await _place(robot, rider, Vector2(0, -50))
    if rider == lead: lead.debug_drive(Vector2.DOWN, Vector2.RIGHT)
    else: follower.set_ai_goal(site)
    var touched := await _press(robot, rider)
    if rider == lead: lead.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    else: follower.set_ai_goal(follower.global_position)
    await _drive(robot, Vector2.ZERO, 3)
    var on_robot := rider.is_on_floor()
    var rider_start := rider.global_position
    var robot_start := robot.global_position
    var farthest := 0.0
    for _tick in range(ticks):
        await _drive(robot, velocity, 1)
        farthest = maxf(farthest, (rider.global_position - rider_start).dot(velocity.normalized()))
    # The rider's own tick after the robot's last step.
    await _drive(robot, Vector2.ZERO, 1)
    var moved := rider.global_position - rider_start
    var along := moved.dot(velocity.normalized())
    farthest = maxf(farthest, along)
    var robot_moved := (robot.global_position - robot_start).dot(velocity.normalized())
    var name := "%s / %s north of it" % [label, role]
    check(touched and on_robot, "%s: rider pressed onto the robot's north side counts it as floor" % name)
    check(robot_moved >= velocity.length() * ticks / hz * 0.9, "%s: robot moves %.1f px" % [name, robot_moved])
    check(absf(farthest) < CARRY_TOLERANCE, "%s: rider is not carried (up to %.1f px along the robot's motion)" % [name, farthest])
    scenarios.append({"name": name, "robot": robot.enemy_id, "rider": rider.operator_id, "rider_role": role,
        "robot_speed_px_s": velocity.length(), "ticks": ticks, "physics_hz": hz, "rider_counts_robot_as_floor": touched and on_robot,
        "robot_moved_px": snappedf(robot_moved, 0.01), "rider_moved_along_px": snappedf(along, 0.01),
        "rider_farthest_along_px": snappedf(farthest, 0.01), "rider_moved_across_px": snappedf(moved.dot(velocity.normalized().orthogonal()), 0.01)})

## An operator walks east out from under a robot that touches it from the north.
func _operator_walks_out(robot: EnemyActor, hz: int) -> void:
    await _place(robot, lead, Vector2(0, 50))
    lead.debug_drive(Vector2.UP, Vector2.RIGHT)
    var touched := await _press(robot, lead)
    lead.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    await _drive(robot, Vector2.ZERO, 3)
    var on_operator := robot.is_on_floor()
    var robot_start := robot.global_position
    var lead_start := lead.global_position
    var ticks := hz
    var farthest := 0.0
    lead.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    for _tick in range(ticks):
        # A robot holding still still runs move_and_slide every tick, as in combat.
        await _drive(robot, Vector2.ZERO, 1)
        farthest = maxf(farthest, robot.global_position.x - robot_start.x)
    lead.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    await _drive(robot, Vector2.ZERO, 1)
    var moved := robot.global_position - robot_start
    farthest = maxf(farthest, moved.x)
    var walked := lead.global_position.x - lead_start.x
    var name := "operator walks out from under %s" % robot.enemy_id
    check(touched and on_operator, "%s: robot pressed onto the operator's north side counts it as floor" % name)
    check(walked >= lead.walk_speed * lead.run_speed_multiplier * 0.6, "%s: operator walks %.1f px" % [name, walked])
    check(absf(farthest) < CARRY_TOLERANCE, "%s: robot is not carried (up to %.1f px along the operator's walk)" % [name, farthest])
    scenarios.append({"name": name, "robot": robot.enemy_id, "rider": robot.enemy_id, "rider_role": "robot holding still",
        "operator_walk_px": snappedf(walked, 0.01), "ticks": ticks, "physics_hz": hz, "rider_counts_operator_as_floor": touched and on_operator,
        "rider_moved_along_px": snappedf(moved.x, 0.01), "rider_farthest_along_px": snappedf(farthest, 0.01),
        "rider_moved_across_px": snappedf(moved.y, 0.01)})

## Puts the robot on the site and one operator apart from it, and lets the physics server
## absorb the jump: a body's teleport reaches the server as one step of velocity.
func _place(robot: EnemyActor, operator: OperatorActor, offset: Vector2) -> void:
    for member in stage.squad.operators: use(member, member == operator)
    for other: EnemyActor in robots.values():
        other.collision_layer = 2 if other == robot else 0
        if other != robot: other.global_position = site + Vector2(0, 600)
    robot.global_position = site
    robot.velocity = Vector2.ZERO
    operator.global_position = site + offset
    operator.velocity = Vector2.ZERO
    await _drive(robot, Vector2.ZERO, 3)

## The operator walks into the robot; true once they touch.
func _press(robot: EnemyActor, operator: OperatorActor) -> bool:
    for _tick in range(60):
        await _drive(robot, Vector2.ZERO, 1)
        for i in range(operator.get_slide_collision_count()):
            if operator.get_slide_collision(i).get_collider() == robot: return true
    return false

## One physics tick per count; the robot moves as EnemyActor._physics_process moves it,
## before the operators' own physics processing in the same tick.
func _drive(robot: EnemyActor, velocity: Vector2, count: int) -> void:
    for _i in range(count):
        await physics_frame
        robot.velocity = velocity
        robot.move_and_slide()
        robot.global_position = stage.constrain_battle_position(robot.global_position)

func use(member: OperatorActor, active: bool) -> void:
    member.set_physics_process(active)
    member.collision_layer = 4 if active else 0
    if not active: member.global_position = site + Vector2(0, -600) if site.is_finite() else member.global_position

## Walkable floor with no cover in the region the fixture moves through.
func _open_site() -> Vector2:
    var room: Dictionary = stage.main_route[stage.current_step]
    var center := Vector2(float(room.x), float(room.y))
    var best := Vector2.INF
    for gx in range(-25, 26):
        for gy in range(-25, 26):
            var point := center + Vector2(gx, gy) * 40.0
            if best.is_finite() and point.distance_squared_to(center) >= best.distance_squared_to(center): continue
            # Root positions the bodies pass through: 50 px either side, east to a carried
            # charge's end. Obstacle rects already include each body's collision extent.
            var region := Rect2(point + Vector2(-30, -60), Vector2(370, 120))
            if _region_clear(region): best = point
    return best

func _region_clear(region: Rect2) -> bool:
    for obstacle in NAV.ground_obstacles(lead, region.get_center()):
        if obstacle.intersects(region): return false
    for robot: EnemyActor in robots.values():
        for obstacle in NAV.ground_obstacles(robot, region.get_center()):
            if obstacle.intersects(region): return false
    var x := region.position.x
    while x <= region.end.x:
        if not stage.battlefield.segment_walkable(Vector2(x, region.position.y), Vector2(x, region.end.y)): return false
        x += 16.0
    return true

func _finish() -> void:
    var report := {"recorded_utc": Time.get_datetime_string_from_system(true), "mission": stage.mission_id if stage else "",
        "site": [site.x, site.y] if site.is_finite() else [], "scenarios": scenarios, "checks": checks, "failures": failures,
        "status": "PASS" if failures.is_empty() else "FAIL"}
    if lead != null and not robots.is_empty():
        var robot: EnemyActor = robots.values()[0]
        report["bodies"] = {}
        for body: CharacterBody2D in [lead, robot]:
            report.bodies[body.get_script().resource_path.get_file()] = {"motion_mode": body.motion_mode,
                "platform_floor_layers": body.platform_floor_layers, "platform_wall_layers": body.platform_wall_layers,
                "platform_on_leave": body.platform_on_leave, "floor_snap_length": body.floor_snap_length}
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_path.get_base_dir()))
    var file := FileAccess.open(out_path, FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    for row in scenarios:
        print("CONTACT_CARRY %-58s along %7.2f px  farthest %7.2f px  across %6.2f px" % [row.name, row.rider_moved_along_px, row.rider_farthest_along_px, row.rider_moved_across_px])
    for failure in failures: printerr("FAIL: ", failure)
    print("ACTOR_CONTACT_CARRY_SMOKE: %s (%d checks)" % [report.status, checks])
    quit(0 if failures.is_empty() else 1)
