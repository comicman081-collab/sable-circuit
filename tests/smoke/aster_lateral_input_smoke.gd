extends SceneTree

## Real scene, physical key events, authored ASTER atlas and held fire.
## This is an input/phase regression, not visual gait approval.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const DemoInput := preload("res://scripts/ui/demo_input.gd")
var failed: Array[String] = []
var checks := 0

func _initialize() -> void:
    call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failed.append(label)
        push_error(label)

func key(code: int, pressed: bool) -> void:
    if pressed: DemoInput.held[code] = true
    else: DemoInput.held.erase(code)
    var event := InputEventKey.new()
    event.keycode = code
    event.physical_keycode = code
    event.pressed = pressed
    root.push_input(event, true)

func frames(count: int) -> void:
    for i in range(count): await physics_frame

func run() -> void:
    DemoInput.reset()
    var stage := STAGE.instantiate() as StoryStage01
    root.add_child(stage)
    await frames(8)
    var actor := stage.squad.operators[0]
    var runtime := actor.get_node("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
    actor.set_movement_bounds(Rect2(-10000,-10000,20000,20000))
    var entry: Dictionary = stage.main_route[0]
    actor.global_position = Vector2(float(entry.x), float(entry.y))
    check(runtime.is_runtime_active(), "ASTER uses the authored Motion Studio body")
    for direction in [
        {"code":KEY_A,"expected":"W","sector":4},
        {"code":KEY_D,"expected":"E","sector":0}
    ]:
        var code: int = direction.code
        key(code, true)
        DemoInput.firing = true
        var seen := {}
        var before := actor.global_position
        var before_ammo := actor.ammo
        for tick in range(36):
            await physics_frame
            var state := runtime.debug_contract()
            seen[int(state.frame)] = true
            check(str(state.direction) == str(direction.expected), "ASTER faces held lateral input %s at tick %d" % [direction.expected,tick])
        check(runtime.debug_contract().action == "walk", "ASTER walks during lateral fire")
        check(seen.size() >= 3, "ASTER cycles distinct authored lateral gait cells")
        check(absf(actor.global_position.x-before.x) > 25.0, "ASTER moves with its lateral gait %s delta %.2f at %s" % [direction.expected, actor.global_position.x-before.x, str(actor.global_position)])
        check(actor.ammo < before_ammo, "Held lateral fire uses the real weapon")
        key(code, false)
        DemoInput.firing = false
        await frames(3)
    key(KEY_W,true)
    key(KEY_D,true)
    await frames(4)
    check(str(runtime.debug_contract().direction) == "NE", "Two simultaneous keys choose diagonal gait")
    key(KEY_W,false)
    key(KEY_D,false)
    await frames(3)
    check(str(runtime.debug_contract().action) == "idle", "Release plants ASTER feet")
    DemoInput.reset()
    stage.queue_free()
    await process_frame
    print("ASTER_LATERAL_INPUT: %s (%d checks)" % ["PASS" if failed.is_empty() else "FAIL",checks])
    quit(0 if failed.is_empty() else 1)
