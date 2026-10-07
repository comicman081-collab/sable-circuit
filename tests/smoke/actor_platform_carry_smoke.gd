extends SceneTree
## Operators and robots never ride each other. CharacterBody2D's default grounded mode
## treats a body touched from its north side as floor and adds that body's velocity to
## the next move like a moving platform: an operator pressed against a robot was dragged
## by it, and a robot's velocity after a reposition threw the operator ~200 px in one tick.
## Uses the real app operator and robot bodies in a live combat room. Writes no files.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")

var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.configure_campaign({}, "PLATFORM-CARRY-SMOKE", {})
    var step := 0
    while step < stage.main_route.size() and (stage.main_route[step].get("encounter", []) as Array).is_empty(): step += 1
    stage.current_step = step
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(step)
    await _frames(2)
    stage.set_physics_process(false)
    stage.squad.set_physics_process(false)
    var operator := stage.squad.get_active_operator()
    var robot: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        # Physics processing off only: a disabled CollisionObject2D leaves the physics space.
        node.set_physics_process(false)
        if robot == null and node is EnemyActor: robot = node
    for member in stage.squad.operators: member.set_physics_process(false)
    _check(robot != null, "a live robot in the first combat room")
    if robot == null:
        _finish()
        return
    for body: CharacterBody2D in [operator, robot]:
        _check(body.platform_floor_layers == 0 and body.platform_wall_layers == 0, "%s follows no platform layers" % body.name)
    var home := robot.global_position
    # Operator presses down onto the robot's north side: a "floor" contact in grounded mode.
    operator.global_position = home + Vector2(0, -90)
    for _tick in range(40):
        await physics_frame
        operator.velocity = Vector2(0, 150)
        operator.move_and_slide()
    _check(operator.get_slide_collision_count() > 0 and operator.get_slide_collision(0).get_collider() == robot, "operator ends pressed against the robot")
    # Reposition the robot; the next physics step gives its body that jump as velocity.
    # The operator then moves with no velocity of its own and must stay where it is.
    robot.global_position = home + Vector2(220, 0)
    await physics_frame
    var before := operator.global_position
    operator.velocity = Vector2.ZERO
    operator.move_and_slide()
    var moved := operator.global_position.distance_to(before)
    _check(moved < 0.5, "operator is not carried by a repositioned robot (moved %.1f px)" % moved)
    # Same the other way round: a robot pressed onto an operator's north side.
    robot.global_position = operator.global_position + Vector2(0, -90)
    for _tick in range(40):
        await physics_frame
        robot.velocity = Vector2(0, 150)
        robot.move_and_slide()
    operator.global_position += Vector2(-220, 0)
    await physics_frame
    before = robot.global_position
    robot.velocity = Vector2.ZERO
    robot.move_and_slide()
    moved = robot.global_position.distance_to(before)
    _check(moved < 0.5, "robot is not carried by a repositioned operator (moved %.1f px)" % moved)
    _finish()

func _finish() -> void:
    if failures.is_empty():
        print("ACTOR_PLATFORM_CARRY_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _frames(count: int) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func _check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label)
