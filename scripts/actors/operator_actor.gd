extends CharacterBody2D
class_name OperatorActor

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")

signal control_changed(actor: OperatorActor, controlled: bool)
signal ammo_changed(actor: OperatorActor, current: int, maximum: int)

@export var walk_speed := 150.0
@export var run_speed := 230.0
@export var fire_interval := 0.115
@export var reload_duration := 1.15
@export var magazine_size := 24

var operator_id := "CHR_PROTO_01"
var display_name := "ALPHA"
var accent_color := Color("69d2ff")
var controlled := false
var combat_mode := true
var aim_world := Vector2.RIGHT
var facing_sector := 0
var ammo := 24
var movement_bounds := Rect2(90.0, 110.0, 1100.0, 540.0)
var art_profile: Dictionary = {}

var _visual: OperatorVisual
var _fire_cooldown := 0.0
var _reload_left := 0.0
var _dash_left := 0.0
var _dash_cooldown := 0.0
var _dash_latch := false
var _reload_latch := false
var _ai_goal := Vector2.ZERO
var _debug_drive := false
var _debug_move := Vector2.ZERO
var _debug_aim := Vector2.RIGHT

func _ready() -> void:
    add_to_group("operators")
    _visual = $VisualRoot as OperatorVisual
    ammo = magazine_size
    if art_profile.is_empty():
        art_profile = ArtProfileRegistry.get_profile(operator_id)
    _visual.configure(display_name, accent_color, art_profile)

func configure(id_value: String, label: String, color: Color) -> void:
    operator_id = id_value
    display_name = label
    accent_color = color
    art_profile = ArtProfileRegistry.get_profile(operator_id)
    _apply_profile_gamefeel()
    if is_node_ready():
        _visual.configure(display_name, accent_color, art_profile)

func _apply_profile_gamefeel() -> void:
    match str(art_profile.get("motion_profile", "")):
        "MOT_ASTER_01":
            walk_speed = 165.0; run_speed = 250.0; fire_interval = 0.105; reload_duration = 1.02
        "MOT_ROOK_01":
            walk_speed = 138.0; run_speed = 205.0; fire_interval = 0.42; reload_duration = 1.38; magazine_size = 10
        "MOT_MICA_01":
            walk_speed = 152.0; run_speed = 224.0; fire_interval = 0.17; reload_duration = 1.12; magazine_size = 18

func set_controlled(value: bool) -> void:
    controlled = value
    if is_node_ready():
        _visual.set_selected(value)
    control_changed.emit(self, value)

func set_ai_goal(world_pos: Vector2) -> void:
    _ai_goal = world_pos

func set_movement_bounds(bounds: Rect2) -> void:
    movement_bounds = bounds

func debug_drive(move_vec: Vector2, aim_vec: Vector2) -> void:
    _debug_drive = true
    _debug_move = move_vec
    _debug_aim = aim_vec

func debug_stop_drive() -> void:
    _debug_drive = false

func debug_fire_once() -> bool:
    return _try_fire(true)

func debug_begin_reload() -> void:
    _begin_reload()

func is_reloading() -> bool:
    return _reload_left > 0.0

func get_reload_progress() -> float:
    if _reload_left <= 0.0:
        return 0.0
    return 1.0 - (_reload_left / reload_duration)

func _physics_process(delta: float) -> void:
    _fire_cooldown = maxf(0.0, _fire_cooldown - delta)
    _dash_cooldown = maxf(0.0, _dash_cooldown - delta)
    if _reload_left > 0.0:
        _reload_left = maxf(0.0, _reload_left - delta)
        if _reload_left <= 0.0:
            ammo = magazine_size
            ammo_changed.emit(self, ammo, magazine_size)

    var move_input := Vector2.ZERO
    var want_run := false

    if _debug_drive:
        move_input = _debug_move.limit_length(1.0)
        if _debug_aim.length_squared() > 0.0001:
            aim_world = _debug_aim.normalized()
    elif controlled:
        move_input = _read_move_input()
        want_run = Input.is_key_pressed(KEY_SHIFT)
        var mouse_vec := get_global_mouse_position() - global_position
        if mouse_vec.length_squared() > 1.0:
            aim_world = mouse_vec.normalized()
        _handle_player_actions(move_input)
    else:
        move_input = _ai_move_vector()
        _update_ai_aim_and_fire()

    if _dash_left > 0.0:
        _dash_left = maxf(0.0, _dash_left - delta)
    else:
        var target_speed := run_speed if want_run else walk_speed
        velocity = move_input * target_speed

    move_and_slide()
    _clamp_to_arena()

    facing_sector = _sector_from_vector(aim_world if combat_mode else (move_input if move_input.length_squared() > 0.01 else aim_world))
    var normalized_speed := velocity.length() / run_speed
    _visual.set_runtime_state(velocity, aim_world, normalized_speed, combat_mode, facing_sector, is_reloading(), get_reload_progress())

func _read_move_input() -> Vector2:
    var move := Vector2(
        float(Input.is_key_pressed(KEY_D)) - float(Input.is_key_pressed(KEY_A)),
        float(Input.is_key_pressed(KEY_S)) - float(Input.is_key_pressed(KEY_W))
    )
    return move.normalized() if move.length_squared() > 1.0 else move

func _handle_player_actions(move_input: Vector2) -> void:
    if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
        _try_fire(false)

    var reload_pressed := Input.is_key_pressed(KEY_R)
    if reload_pressed and not _reload_latch:
        _begin_reload()
    _reload_latch = reload_pressed

    var dash_pressed := Input.is_key_pressed(KEY_SPACE)
    if dash_pressed and not _dash_latch and _dash_cooldown <= 0.0 and move_input.length_squared() > 0.01:
        _dash_left = 0.14
        _dash_cooldown = 0.65
        velocity = move_input.normalized() * 520.0
        _visual.trigger_evade()
    _dash_latch = dash_pressed

func _ai_move_vector() -> Vector2:
    var to_goal := _ai_goal - global_position
    if to_goal.length() <= 18.0:
        return Vector2.ZERO
    return to_goal.normalized()

func _update_ai_aim_and_fire() -> void:
    var nearest: Node2D = null
    var nearest_d2 := INF
    for target in get_tree().get_nodes_in_group("prototype_targets"):
        if target is Node2D:
            var d2 := global_position.distance_squared_to(target.global_position)
            if d2 < nearest_d2:
                nearest_d2 = d2
                nearest = target
    if nearest:
        var toward := nearest.global_position - global_position
        if toward.length_squared() > 1.0:
            aim_world = toward.normalized()
        if nearest_d2 <= 520.0 * 520.0:
            _try_fire(false)
    if ammo <= 0 and not is_reloading():
        _begin_reload()

func _try_fire(force: bool) -> bool:
    if _reload_left > 0.0 or ammo <= 0:
        if ammo <= 0:
            _begin_reload()
        return false
    if not force and _fire_cooldown > 0.0:
        return false

    _fire_cooldown = fire_interval
    ammo -= 1
    ammo_changed.emit(self, ammo, magazine_size)
    _visual.trigger_fire()
    CombatFeedback.play_fire(get_tree(), art_profile)

    if "ROOK" in str(art_profile.get("projectile_profile", "")):
        for spread in [-0.13, -0.065, 0.0, 0.065, 0.13]:
            _spawn_projectile(aim_world.rotated(spread))
    else:
        _spawn_projectile(aim_world)
    return true

func _spawn_projectile(dir: Vector2) -> void:
    var projectile := Projectile.new()
    get_tree().root.add_child(projectile)
    projectile.setup(_visual.get_muzzle_global_position(), dir, self, accent_color.lightened(0.35), art_profile)

func _begin_reload() -> void:
    if _reload_left > 0.0 or ammo >= magazine_size:
        return
    _reload_left = reload_duration

func _sector_from_vector(vec: Vector2) -> int:
    if vec.length_squared() < 0.0001:
        return facing_sector
    var wrapped := fposmod(vec.angle() + PI / 8.0, TAU)
    return int(floor(wrapped / (PI / 4.0))) % 8

func _clamp_to_arena() -> void:
    var left := movement_bounds.position.x
    var top := movement_bounds.position.y
    var right := movement_bounds.position.x + movement_bounds.size.x
    var bottom := movement_bounds.position.y + movement_bounds.size.y
    global_position.x = clampf(global_position.x, left, right)
    global_position.y = clampf(global_position.y, top, bottom)
