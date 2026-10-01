extends Node
class_name ImpactFeel

## Presentation-only hit feel: camera shake and hit-stop.
## Gameplay never reads or waits on this node. It only nudges Camera2D.offset and briefly scales
## Engine.time_scale, and it always restores both (real-time clock, so a frozen frame still ends).
##
## Shake curve and numbers come from the awesome-ai-motion `camera-shake` card
## (github.com/gongnyang/awesome-ai-motion, MIT): 300 ms, 6 px at 1080p, exp(-5p)*(1-p) decay,
## y at 4/6 of x amplitude and 1.7x its frequency. Strength 0.5 reproduces those defaults and
## 0..1 spans the card ranges (150-450 ms, 2-10 px). The card's 0.6 degree rotation is not used.
## Hit-stop timings are SABLE tuning; the catalog has no hit-stop card.

const DIRECTOR_NAME := "ImpactFeelDirector"
const REF_SCALE := 720.0 / 1080.0

const SHAKE_MIN_STRENGTH := 0.05
const SHAKE_DURATION_MIN := 0.15
const SHAKE_DURATION_MAX := 0.45
const SHAKE_PX_MIN := 2.0
const SHAKE_PX_MAX := 10.0
const SHAKE_Y_RATIO := 4.0 / 6.0
const SHAKE_Y_FREQ := 1.7
const SHAKE_HZ := 20.0
const SHAKE_DECAY := 5.0

const HIT_STOP_MAX_SEC := 0.12
const HIT_STOP_TIME_SCALE := 0.05
const HIT_STOP_COOLDOWN_SEC := 0.10
const HIT_STOP_MIN_WEIGHT := 0.28

## Accessibility / test switches. shake_scale 0 disables shake, hit_stop_enabled false disables freezes.
static var shake_scale := 1.0
static var hit_stop_enabled := true
static var _instance: ImpactFeel

var _camera: Camera2D
var _base_offset := Vector2.ZERO
var _shaking := false
var _shake_start_us := 0
var _shake_duration := 0.0
var _shake_amp := 0.0
var _shake_sign := 1.0
var _shake_count := 0

var _stop_end_us := 0
var _stop_ready_us := 0
var _saved_time_scale := 1.0
var _stop_count := 0

static func director(tree: SceneTree) -> ImpactFeel:
    if tree == null or tree.root == null:
        return null
    if is_instance_valid(_instance):
        return _instance
    _instance = ImpactFeel.new()
    _instance.name = DIRECTOR_NAME
    _instance.process_mode = Node.PROCESS_MODE_ALWAYS
    _instance.process_priority = 100
    tree.root.add_child.call_deferred(_instance)
    return _instance

static func shake(tree: SceneTree, strength: float) -> void:
    var d := director(tree)
    if d:
        d._begin_shake(strength)

static func hit_stop(tree: SceneTree, seconds: float) -> void:
    var d := director(tree)
    if d:
        d._begin_hit_stop(seconds)

static func impact(tree: SceneTree, strength: float, stop_seconds: float) -> void:
    shake(tree, strength)
    hit_stop(tree, stop_seconds)

## weight is the projectile identity's impact weight (0 = no feedback). Used for hits dealt and taken.
static func projectile_hit(tree: SceneTree, weight: float) -> void:
    impact(tree, weight, stop_for_weight(weight))

static func enemy_defeated(tree: SceneTree, enemy_id: String) -> void:
    if "BOSS" in enemy_id or "ANCHOR" in enemy_id:
        impact(tree, 0.95, 0.12)
    elif "SHIELD" in enemy_id:
        impact(tree, 0.6, 0.08)
    else:
        impact(tree, 0.45, 0.06)

static func operator_downed(tree: SceneTree) -> void:
    impact(tree, 0.7, 0.09)

static func boss_phase_changed(tree: SceneTree, phase: int) -> void:
    impact(tree, 0.7 if phase <= 2 else 0.9, 0.06)

static func stop_for_weight(weight: float) -> float:
    return 0.0 if weight < HIT_STOP_MIN_WEIGHT else 0.015 + 0.06 * weight

func _process(_delta: float) -> void:
    var now := Time.get_ticks_usec()
    _tick_hit_stop(now)
    _tick_shake(now)

func _exit_tree() -> void:
    if _stop_end_us != 0:
        Engine.time_scale = _saved_time_scale
        _stop_end_us = 0
    _release_camera()
    if _instance == self:
        _instance = null

func _begin_shake(strength: float) -> void:
    if shake_scale <= 0.0 or strength < SHAKE_MIN_STRENGTH:
        return
    var s := clampf(strength, 0.0, 1.0)
    var amp := lerpf(SHAKE_PX_MIN, SHAKE_PX_MAX, s) * REF_SCALE * shake_scale
    var now := Time.get_ticks_usec()
    if amp <= _envelope_amp(now):
        return
    _shake_amp = amp
    _shake_duration = lerpf(SHAKE_DURATION_MIN, SHAKE_DURATION_MAX, s)
    _shake_start_us = now
    _shake_sign = -_shake_sign
    _shake_count += 1

func _begin_hit_stop(seconds: float) -> void:
    if not hit_stop_enabled:
        return
    var sec := minf(seconds, HIT_STOP_MAX_SEC)
    if sec <= 0.0:
        return
    var now := Time.get_ticks_usec()
    var end_us := now + int(sec * 1000000.0)
    if _stop_end_us != 0:
        _stop_end_us = maxi(_stop_end_us, end_us)
        return
    if now < _stop_ready_us:
        return
    _saved_time_scale = Engine.time_scale
    Engine.time_scale = minf(_saved_time_scale, HIT_STOP_TIME_SCALE)
    _stop_end_us = end_us
    _stop_count += 1

func _tick_hit_stop(now: int) -> void:
    if _stop_end_us == 0 or now < _stop_end_us:
        return
    Engine.time_scale = _saved_time_scale
    _stop_end_us = 0
    _stop_ready_us = now + int(HIT_STOP_COOLDOWN_SEC * 1000000.0)

func _tick_shake(now: int) -> void:
    var cam := get_viewport().get_camera_2d()
    if cam != _camera:
        _release_camera()
        _camera = cam
    if _camera == null:
        return
    var o := _shake_offset(now)
    if o == Vector2.ZERO:
        if _shaking:
            _camera.offset = _base_offset
            _shaking = false
        return
    if not _shaking:
        _base_offset = _camera.offset
        _shaking = true
    _camera.offset = _base_offset + o

func _release_camera() -> void:
    if _shaking and is_instance_valid(_camera):
        _camera.offset = _base_offset
    _shaking = false

func _envelope_amp(now: int) -> float:
    var elapsed := float(now - _shake_start_us) / 1000000.0
    if _shake_duration <= 0.0 or elapsed >= _shake_duration:
        return 0.0
    var p := elapsed / _shake_duration
    return _shake_amp * exp(-SHAKE_DECAY * p) * (1.0 - p)

func _shake_offset(now: int) -> Vector2:
    var elapsed := float(now - _shake_start_us) / 1000000.0
    if _shake_duration <= 0.0 or elapsed >= _shake_duration:
        return Vector2.ZERO
    var a := _envelope_amp(now)
    var w := TAU * SHAKE_HZ * elapsed
    return Vector2(sin(w) * _shake_sign, sin(w * SHAKE_Y_FREQ) * SHAKE_Y_RATIO) * a

func debug_shake_active() -> bool:
    return _shaking

func debug_shake_count() -> int:
    return _shake_count

func debug_hit_stop_active() -> bool:
    return _stop_end_us != 0

func debug_hit_stop_count() -> int:
    return _stop_count
