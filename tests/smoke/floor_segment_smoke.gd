extends SceneTree
## Floor clearance for route planning (site7_battlefield.segment_walkable). On every
## operation's floor the exact test must agree with a 1px walk along random segments, and
## the operation 5 R02 spot where a 16px sampler let a route clip a floor-hole corner (the
## planner then flipped between two plans there forever) must now route through to R03.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
const MISSIONS := ["MIS_CH01_01", "MIS_CH01_02", "MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05", "MIS_CH01_06", "MIS_CH01_07", "MIS_CH01_08", "MIS_CH01_09", "MIS_CH01_10"]
const SEGMENTS := 240

var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    for mission in MISSIONS:
        await _check_mission(mission)
    await _check_hole_corner()
    if failures.is_empty():
        print("FLOOR_SEGMENT_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _load(mission: String) -> StoryStage01:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.configure_campaign({}, "FLOOR-SEGMENT-SMOKE", {})
    await _frames(10)
    return stage

func _check_mission(mission: String) -> void:
    var stage := await _load(mission)
    var field: Node = stage.battlefield
    var bounds := Rect2(Vector2(float(stage.main_route[0].x), float(stage.main_route[0].y)), Vector2.ZERO)
    for row in stage.main_route + stage.optional_rooms: bounds = bounds.expand(Vector2(float(row.x), float(row.y)))
    bounds = bounds.grow(500.0)
    var rng := RandomNumberGenerator.new()
    rng.seed = hash(mission)
    var disagreements: Array[String] = []
    var blocked := 0
    var sampler_misses := 0
    for i in range(SEGMENTS):
        var a := Vector2.INF
        for attempt in range(200):
            var candidate := Vector2(rng.randf_range(bounds.position.x, bounds.end.x), rng.randf_range(bounds.position.y, bounds.end.y))
            if field.is_walkable(candidate):
                a = candidate
                break
        if not a.is_finite(): continue
        var b := a + Vector2.RIGHT.rotated(rng.randf() * TAU) * rng.randf_range(40.0, 700.0)
        var exact: bool = field.segment_walkable(a, b)
        # Longest run of off-floor 1px samples along the same segment.
        var span := a.distance_to(b)
        var steps := int(ceil(span))
        var run := 0
        var longest := 0
        for s in range(steps + 1):
            if field.is_walkable(a.lerp(b, float(s) / steps)): run = 0
            else:
                run += 1
                longest = maxi(longest, run)
        var dense_clear := longest == 0
        # A clear verdict tolerates only seam-width gaps; a blocked one must have a real gap.
        if exact and longest > int(field.SEAM_TOLERANCE) + 1: disagreements.append("%s -> %s clear, but %dpx off floor" % [a.round(), b.round(), longest])
        if not exact and dense_clear: disagreements.append("%s -> %s blocked, but every 1px sample is on floor" % [a.round(), b.round()])
        if not exact:
            blocked += 1
            var coarse := true
            var coarse_steps := maxi(1, int(ceil(span / 16.0)))
            for s in range(coarse_steps + 1):
                if not field.is_walkable(a.lerp(b, float(s) / coarse_steps)): coarse = false
            if coarse: sampler_misses += 1
    _check(disagreements.is_empty(), "%s: exact floor test agrees with a 1px walk on %d segments %s" % [mission, SEGMENTS, str(disagreements.slice(0, 3))])
    _check(blocked > 0, "%s: some random segments leave the floor (%d)" % [mission, blocked])
    print("%s: %d of %d segments blocked, %d of them missed by 16px sampling" % [mission, blocked, SEGMENTS, sampler_misses])
    stage.queue_free()
    await _frames(3)

func _check_hole_corner() -> void:
    var stage := await _load("MIS_CH01_05")
    var field: Node = stage.battlefield
    var start := Vector2(3502, 414)
    var corner_edge := Vector2(3566.155, 283.4416)
    _check(not field.segment_walkable(start, corner_edge), "op 5 R02: the edge that clips the floor hole's corner is blocked")
    var active := stage.squad.get_active_operator()
    var goal := Vector2(float(stage.main_route[2].x), float(stage.main_route[2].y))
    var nav := NAV.new()
    # Floor routing only: the room's live robots would shoot the operator down, and a
    # follower fighting them could park in the corridor and wedge it (1 run in 4 failed).
    # A disabled body also leaves the physics space (CollisionObject2D.DISABLE_MODE_REMOVE).
    for enemy in get_nodes_in_group("m3_enemies"): enemy.process_mode = Node.PROCESS_MODE_DISABLED
    for follower in stage.squad.operators:
        if follower != active: follower.process_mode = Node.PROCESS_MODE_DISABLED
    await _frames(2)
    active.global_position = start
    var arrived := -1
    for frame in range(1200):
        active.debug_drive(nav.direction(active, goal, 1.0 / 60.0), Vector2.RIGHT)
        active._debug_run = true
        await physics_frame
        if active.global_position.distance_to(goal) < 60.0:
            arrived = frame
            break
    active.debug_stop_drive()
    _check(arrived >= 0, "op 5 R02: an operator routed from the hole corner reaches R03 (frame %d, %d replans)" % [arrived, nav.replans])
    _check(nav.replans < 80, "op 5 R02: the route does not flip between plans (%d replans)" % nav.replans)
    stage.queue_free()
    await _frames(3)

func _frames(count: int) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition: failures.append(label)
