extends RefCounted
## Shared physical and touch input; no synthetic keyboard events or sticky keys.
static var movement := Vector2.ZERO
static var aim := Vector2.ZERO
static var firing := false
static var held: Dictionary = {}
static var touch_mode := false
static var mouse_blocked := false
static var taps: Dictionary = {}

static func remember_press(code: int) -> void:
    # A web keydown+keyup can both arrive between physics ticks. Preserve only
    # discrete actions briefly; movement must never coast after release.
    if code in [KEY_1,KEY_2,KEY_3,KEY_F,KEY_C,KEY_R,KEY_SPACE,KEY_Q,KEY_E,KEY_X]:
        taps[code] = Engine.get_process_frames() + 2

static func key(code: int) -> bool:
    return bool(held.get(code, false)) or Input.is_physical_key_pressed(code) or Input.is_key_pressed(code) or int(taps.get(code,-1)) >= Engine.get_process_frames()

static func move_vector() -> Vector2:
    var keyboard := Vector2(float(key(KEY_D) or key(KEY_RIGHT)) - float(key(KEY_A) or key(KEY_LEFT)), float(key(KEY_S) or key(KEY_DOWN)) - float(key(KEY_W) or key(KEY_UP)))
    return (keyboard + movement).limit_length(1.0)

static func fire() -> bool:
    return firing or (not touch_mode and not mouse_blocked and Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT))

static func reset() -> void:
    movement = Vector2.ZERO
    aim = Vector2.ZERO
    firing = false
    held.clear()
    taps.clear()
    mouse_blocked = false
