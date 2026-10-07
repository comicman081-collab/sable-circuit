extends SceneTree
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
var failures: Array[String] = []
var checks := 0
func _init() -> void: call_deferred("run")
func check(value: bool, label: String) -> void:
    checks += 1
    if not value: failures.append(label); push_error(label)
func run() -> void:
    for number in range(1,11):
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        root.add_child(stage)
        for tick in range(10): await process_frame; await physics_frame
        var actor := stage.squad.get_active_operator()
        actor.set_physics_process(false)
        var route := stage.main_route
        check(stage.battlefield.world_ready,"S%d world floor ready" % number)
        for index in range(route.size()-1):
            var start := Vector2(float(route[index].x),float(route[index].y))
            var goal := Vector2(float(route[index+1].x),float(route[index+1].y))
            actor.global_position = start
            var nav := NAV.new()
            check(nav.direction(actor,goal,1.0/60.0).length() > 0.5,"S%d main link %d has first navigation step" % [number,index])
        var before_boss := Vector2(float(route[3].x),float(route[3].y)).lerp(Vector2(float(route[4].x),float(route[4].y)),0.5)
        actor.global_position = stage.battlefield.constrain(before_boss)
        var extraction := Vector2(float(route[5].x),float(route[5].y))
        var nav := NAV.new()
        var path := nav._plan(actor,actor.global_position,extraction,NAV.ground_obstacles(actor))
        check(not path.is_empty(),"S%d long route bends through authored world nodes" % number)
        check(nav.direction(actor,extraction,1.0/60.0).length() > 0.5,"S%d long route produces movement, not a zero-vector stall" % number)
        var post_boss_return: Vector2 = stage.battlefield.constrain(Vector2(float(route[2].x) + 180.0, float(route[2].y) + 150.0))
        actor.global_position = post_boss_return
        nav = NAV.new()
        check(not nav._plan(actor,post_boss_return,extraction,NAV.ground_obstacles(actor)).is_empty(),"S%d long return route survives diagonal-connector detour" % number)
        if number == 5:
            # Recorded archive-corner stall. Live actors are clamped onto the
            # walk graph every tick (OperatorActor._clamp_to_arena), so apply
            # the same clamp; the raw point sits ~4px outside the floor after
            # the 2026-09-23 connector overlap change and is unreachable in play.
            var archive_corner: Vector2 = stage.constrain_battle_position(Vector2(6404.0596,680.0560))
            check(stage.battlefield.is_walkable(archive_corner),"S5 archive-corner fixture is on the live walk graph")
            actor.global_position = archive_corner
            nav = NAV.new()
            var escape_step := nav.direction(actor,extraction,1.0/60.0)
            check(escape_step.length() > 0.5,"S5 surviving squadmate can leave the archive after boss")
            var rook := stage.squad.operators[1]
            rook.global_position = archive_corner
            actor.apply_damage(1000.0)
            stage.squad.request_control(1)
            nav = NAV.new()
            var rook_step := nav.direction(rook,extraction,1.0/60.0)
            check(rook_step.length() > 0.5,"S5 ROOK fallback has a route after ASTER is down")
            rook.debug_drive(rook_step,Vector2.RIGHT)
            rook._debug_run = true
            var before_move := rook.global_position
            rook.set_physics_process(true)
            for tick in range(30): await physics_frame
            check(rook.global_position.distance_to(before_move) > 10.0,"S5 ROOK fallback physically leaves archive corner")
        stage.queue_free()
        for tick in range(3): await process_frame; await physics_frame
    print("SITE7_WORLD_ROUTE_NAVIGATION: %s (%d checks)" % ["PASS" if failures.is_empty() else "FAIL",checks])
    quit(0 if failures.is_empty() else 1)
