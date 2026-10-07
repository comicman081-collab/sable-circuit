extends "res://tests/smoke/site7_full_operation_smoke.gd"
## Contact census over the technical playthrough: every physics tick, before any actor
## moves, each operator or robot whose last move_and_slide ended on another actor's north
## side (a grounded-mode floor) is recorded with the velocity that floor body has in the
## physics server this tick. That is the platform velocity grounded move_and_slide applies
## this tick while platform_floor_layers includes the floor's layer: applied_px counts
## only those ticks, carried_px every tick. The playthrough bot itself is unchanged.
## Writes <out>/contact_census.json next to full_operation.json.
## qa/ is .gdignore'd: copy this file to .cache/probe/ and run
## godot --headless --path . -s res://.cache/probe/contact_census.gd -- --mission=MIS_CH01_04 --out=res://.cache/census/op04

var census_ticks := 0
var totals: Dictionary = {}
var open_rides: Dictionary = {}
var rides: Array[Dictionary] = []
var attack_exposure := 0
var config := {}

func run() -> void:
    physics_frame.connect(_census)
    await super.run()
    for id in open_rides.keys(): _close_ride(id)
    rides.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.px > b.px)
    var report := {"mission": mission_id, "physics_ticks": census_ticks, "physics_hz": Engine.physics_ticks_per_second,
        "outcome": result.get("outcome", ""), "by_rider": totals, "rides": rides.size(),
        "longest_rides": rides.slice(0, 12), "robot_attack_ticks_carried": attack_exposure,
        "config": config}
    var file := FileAccess.open(OUT + "/contact_census.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("CONTACT_CENSUS " + JSON.stringify({"mission": mission_id, "by_rider": totals, "rides": rides.size(), "attack_ticks": attack_exposure}))

func _census() -> void:
    if stage == null or not is_instance_valid(stage) or not stage.is_inside_tree(): return
    census_ticks += 1
    if config.is_empty() and not stage.squad.operators.is_empty():
        var sample: OperatorActor = stage.squad.operators[0]
        config = {"motion_mode": sample.motion_mode, "platform_floor_layers": sample.platform_floor_layers, "platform_on_leave": sample.platform_on_leave}
    var dt := 1.0 / Engine.physics_ticks_per_second
    var bodies: Array = get_nodes_in_group("operators") + get_nodes_in_group("m3_enemies")
    var seen := {}
    for body in bodies:
        if not is_instance_valid(body) or not body is CharacterBody2D or not body.is_physics_processing(): continue
        if body is OperatorActor and body.is_downed(): continue
        if body is EnemyActor and body.health <= 0.0: continue
        var floor_body: Object = null
        if body.is_on_floor():
            for i in range(body.get_slide_collision_count()):
                var hit: KinematicCollision2D = body.get_slide_collision(i)
                if hit.get_normal().dot(body.up_direction) >= cos(body.floor_max_angle + 0.01): floor_body = hit.get_collider()
        if not (floor_body is CharacterBody2D and is_instance_valid(floor_body)): continue
        var state := PhysicsServer2D.body_get_direct_state(floor_body.get_rid())
        var velocity: Vector2 = state.linear_velocity if state else Vector2.ZERO
        var step := velocity.length() * dt
        var rider := _label(body)
        var row: Dictionary = totals.get(rider, {"floor_ticks": 0, "carried_ticks": 0, "carried_px": 0.0, "applied_px": 0.0, "max_step_px": 0.0, "floors": {}})
        row.floor_ticks += 1
        row.floors[_label(floor_body)] = int(row.floors.get(_label(floor_body), 0)) + 1
        if step > 0.05:
            row.carried_ticks += 1
            row.carried_px = snappedf(row.carried_px + step, 0.01)
            if (body.platform_floor_layers & floor_body.collision_layer) != 0: row.applied_px = snappedf(row.applied_px + step, 0.01)
            row.max_step_px = maxf(row.max_step_px, snappedf(step, 0.01))
            if body is EnemyActor and body.tactics and body.tactics.state in ["WINDUP", "BURST"]: attack_exposure += 1
            var id: int = body.get_instance_id()
            var ride: Dictionary = open_rides.get(id, {"rider": rider, "floor": _label(floor_body), "step": stage.current_step,
                "tick": tick, "ticks": 0, "px": 0.0, "max_speed": 0.0})
            ride.ticks += 1
            ride.px = snappedf(ride.px + step, 0.01)
            ride.max_speed = maxf(ride.max_speed, snappedf(velocity.length(), 0.1))
            open_rides[id] = ride
            seen[id] = true
        totals[rider] = row
    for id in open_rides.keys():
        if not seen.has(id): _close_ride(id)

func _close_ride(id: int) -> void:
    rides.append(open_rides[id])
    open_rides.erase(id)

func _label(body: Object) -> String:
    if body is OperatorActor: return "operator (%s)" % ("controlled" if body.controlled else "follower")
    if body is EnemyActor: return "robot %s" % body.enemy_id
    return str(body)
