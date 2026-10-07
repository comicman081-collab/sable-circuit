extends SceneTree

## App-path regression for the input path that used to let a player cross a
## visible KArchive prop: normal movement and the immediate skill dash both use
## the real OperatorActor body against the live room collider.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("_run")

func _check(ok: bool, note: String) -> void:
    checks += 1
    if not ok:
        failures.append(note)
        push_error(note)

func _settle(frames: int = 4) -> void:
    for _frame in range(frames):
        await physics_frame
        await process_frame

func _run() -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    root.add_child(stage)
    await _settle(12)
    stage.start_battle_preview(1)
    await _settle(8)

    var barrier: StaticBody2D
    for entry: Dictionary in stage.get_node("EnvironmentProps").entries:
        if entry.prop.active and entry.asset == "barrier" and entry.room_id == str(stage.main_route[stage.current_step].id):
            barrier = entry.prop
            break
    var mica := stage.squad.operators[2] as OperatorActor
    _check(is_instance_valid(barrier), "The live Stage 1 barrier is active")
    _check(is_instance_valid(mica), "MICA exists as a real OperatorActor")
    if is_instance_valid(barrier) and is_instance_valid(mica):
        var y := barrier.global_position.y - 18.0
        var left := barrier.global_position + Vector2(-180.0, -18.0)
        var right_edge := barrier.global_position.x + 20.0
        mica.global_position = left
        mica.velocity = Vector2.ZERO
        mica.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
        var touched_barrier := false
        for tick in range(150):
            await physics_frame
            await process_frame
            for slide in range(mica.get_slide_collision_count()):
                if mica.get_slide_collision(slide).get_collider() == barrier:
                    touched_barrier = true
        mica.debug_stop_drive()
        # The continuous map legitimately permits walking around either end.
        # Contact with the actual prop, not a permanent x-stop, is the gate.
        _check(touched_barrier, "MICA body never contacted the visible barrier before passing it")

        mica.global_position = left
        mica.velocity = Vector2.ZERO
        mica.skill_dash(Vector2.RIGHT, 360.0)
        await _settle(2)
        _check(mica.global_position.x < right_edge, "MICA skill dash cannot phase through a visible barrier")
        _check(absf(mica.global_position.y - y) < 12.0, "Barrier collision does not launch MICA off the ground lane")

    stage.queue_free()
    await _settle(2)
    print("SITE7_PLAYER_COVER_COLLISION: %s (%d checks)" % ["PASS" if failures.is_empty() else "FAIL", checks])
    quit(0 if failures.is_empty() else 1)
