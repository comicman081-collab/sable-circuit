extends CharacterBody2D
class_name OperatorActor

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")

signal control_changed(actor: OperatorActor, controlled: bool)
signal ammo_changed(actor: OperatorActor, current: int, maximum: int)
signal health_changed(actor: OperatorActor, current: float, maximum: float)
signal downed(actor: OperatorActor)

@export var walk_speed := 150.0
@export var run_speed := 230.0
@export var fire_interval := 0.115
@export var reload_duration := 1.15
@export var magazine_size := 24
@export var max_health := 100.0

var operator_id := "CHR_PROTO_01"
var display_name := "ALPHA"
var accent_color := Color("69d2ff")
var controlled := false
var combat_mode := true
var aim_world := Vector2.RIGHT
var facing_sector := 0
var ammo := 24
var health := 100.0
var downed_state := false
var movement_bounds := Rect2(90.0, 110.0, 1100.0, 540.0)
var art_profile: Dictionary = {}
var campaign_damage_multiplier := 1.0

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

var _guard_left := 0.0
var _guard_reduction := 0.0
var _overclock_left := 0.0
var _scatter_cycle_left := 0.0

func _ready() -> void:
    add_to_group("operators")
    _visual = $VisualRoot as OperatorVisual
    ammo = magazine_size
    health = max_health
    if art_profile.is_empty():
        art_profile = ArtProfileRegistry.get_profile(operator_id)
        _apply_profile_gamefeel()
        health = max_health
    _visual.configure(display_name, accent_color, art_profile)

func configure(id_value: String, label: String, color: Color) -> void:
    operator_id = id_value
    display_name = label
    accent_color = color
    art_profile = ArtProfileRegistry.get_profile(operator_id)
    _apply_profile_gamefeel()
    health = max_health
    ammo = magazine_size
    if is_node_ready():
        _visual.configure(display_name, accent_color, art_profile)

func _apply_profile_gamefeel() -> void:
    match str(art_profile.get("motion_profile", "")):
        "MOT_ASTER_01":
            walk_speed=165.0; run_speed=250.0; fire_interval=0.105; reload_duration=1.02; magazine_size=24; max_health=96.0
        "MOT_ROOK_01":
            walk_speed=138.0; run_speed=205.0; fire_interval=0.42; reload_duration=1.38; magazine_size=10; max_health=138.0
        "MOT_MICA_01":
            walk_speed=152.0; run_speed=224.0; fire_interval=0.17; reload_duration=1.12; magazine_size=18; max_health=112.0

func apply_campaign_modifiers(modifiers: Dictionary) -> void:
    campaign_damage_multiplier = clampf(float(modifiers.get("damage_multiplier", 1.0)), 1.0, 2.0)

func set_controlled(value: bool) -> void:
    controlled = value and not downed_state
    if is_node_ready():
        _visual.set_selected(controlled)
    control_changed.emit(self, controlled)

func set_ai_goal(world_pos: Vector2) -> void:
    _ai_goal = world_pos

func set_movement_bounds(bounds: Rect2) -> void:
    movement_bounds = bounds

func apply_damage(amount: float) -> void:
    if downed_state or amount <= 0.0:
        return
    var reduction := _guard_reduction if _guard_left>0.0 else 0.0
    var applied := amount * (1.0-clampf(reduction,0.0,0.80))
    health = maxf(0.0, health - applied)
    if is_node_ready():
        _visual.trigger_hit()
    health_changed.emit(self, health, max_health)
    if health <= 0.0:
        downed_state = true
        controlled = false
        velocity = Vector2.ZERO
        downed.emit(self)

func heal(amount: float) -> float:
    if downed_state or amount<=0.0: return 0.0
    var before := health
    health = minf(max_health,health+amount)
    if health>before: health_changed.emit(self,health,max_health)
    return health-before

func revive(ratio: float = 0.35) -> void:
    if not downed_state:
        return
    downed_state = false
    health = maxf(1.0, max_health * clampf(ratio, 0.05, 1.0))
    health_changed.emit(self, health, max_health)

func is_downed() -> bool:
    return downed_state

func apply_guard(duration: float, reduction: float) -> void:
    _guard_left=maxf(_guard_left,duration)
    _guard_reduction=maxf(_guard_reduction,clampf(reduction,0.0,0.80))

func skill_dash(direction: Vector2, distance: float) -> void:
    if downed_state: return
    var dir := direction.normalized() if direction.length_squared()>0.001 else aim_world
    global_position += dir*distance
    _clamp_to_arena()
    _dash_left=maxf(_dash_left,0.10)
    _dash_cooldown=maxf(_dash_cooldown,0.18)
    if is_node_ready(): _visual.trigger_evade()

func activate_overclock(duration: float) -> void:
    _overclock_left=maxf(_overclock_left,duration)
    _reload_left=0.0

func activate_scatter_cycle(duration: float) -> void:
    _scatter_cycle_left=maxf(_scatter_cycle_left,duration)
    _reload_left=0.0
    ammo=magazine_size
    ammo_changed.emit(self,ammo,magazine_size)

func trigger_skill_visual(slot: String) -> void:
    if not is_node_ready(): return
    if slot.to_upper()=="E": _visual.trigger_evade()
    else: _visual.trigger_fire()

func on_projectile_hit(target: Node, applied_damage: float) -> void:
    var parent_squad := get_parent() as SquadController
    if parent_squad==null: return
    parent_squad.add_energy(1.25,"primary_hit")
    if operator_id=="CHR_PROTO_01" and target.has_method("is_exposed") and bool(target.call("is_exposed")):
        parent_squad.add_energy(2.0,"aster_exposed_primary")

func debug_drive(move_vec: Vector2, aim_vec: Vector2) -> void:
    _debug_drive=true; _debug_move=move_vec; _debug_aim=aim_vec
func debug_stop_drive() -> void: _debug_drive=false
func debug_fire_once() -> bool: return _try_fire(true)
func debug_begin_reload() -> void: _begin_reload()
func debug_campaign_damage_multiplier() -> float: return campaign_damage_multiplier
func debug_runtime_skill_buffs() -> Dictionary:
    return {"guard_left":_guard_left,"guard_reduction":_guard_reduction,"overclock_left":_overclock_left,"scatter_cycle_left":_scatter_cycle_left}
func is_reloading() -> bool: return _reload_left>0.0
func get_reload_progress() -> float:
    if _reload_left<=0.0: return 0.0
    return 1.0-(_reload_left/reload_duration)

func _physics_process(delta: float) -> void:
    _fire_cooldown=maxf(0.0,_fire_cooldown-delta); _dash_cooldown=maxf(0.0,_dash_cooldown-delta)
    _guard_left=maxf(0.0,_guard_left-delta)
    if _guard_left<=0.0: _guard_reduction=0.0
    _overclock_left=maxf(0.0,_overclock_left-delta)
    _scatter_cycle_left=maxf(0.0,_scatter_cycle_left-delta)
    if _reload_left>0.0:
        _reload_left=maxf(0.0,_reload_left-delta)
        if _reload_left<=0.0:
            ammo=magazine_size; ammo_changed.emit(self,ammo,magazine_size)

    if downed_state:
        velocity=Vector2.ZERO
        _visual.set_runtime_state(Vector2.ZERO,aim_world,0.0,combat_mode,facing_sector,false,0.0)
        return

    var move_input:=Vector2.ZERO
    var want_run:=false
    if _debug_drive:
        move_input=_debug_move.limit_length(1.0)
        if _debug_aim.length_squared()>0.0001: aim_world=_debug_aim.normalized()
    elif controlled:
        move_input=_read_move_input(); want_run=Input.is_key_pressed(KEY_SHIFT)
        var mouse_vec:=get_global_mouse_position()-global_position
        if mouse_vec.length_squared()>1.0: aim_world=mouse_vec.normalized()
        _handle_player_actions(move_input)
    else:
        move_input=_ai_move_vector(); _update_ai_aim_and_fire()

    if _dash_left>0.0: _dash_left=maxf(0.0,_dash_left-delta)
    else: velocity=move_input*(run_speed if want_run else walk_speed)
    move_and_slide(); _clamp_to_arena()
    facing_sector=_sector_from_vector(aim_world if combat_mode else (move_input if move_input.length_squared()>0.01 else aim_world))
    _visual.set_runtime_state(velocity,aim_world,velocity.length()/run_speed,combat_mode,facing_sector,is_reloading(),get_reload_progress())

func _read_move_input() -> Vector2:
    var move:=Vector2(float(Input.is_key_pressed(KEY_D))-float(Input.is_key_pressed(KEY_A)),float(Input.is_key_pressed(KEY_S))-float(Input.is_key_pressed(KEY_W)))
    return move.normalized() if move.length_squared()>1.0 else move

func _handle_player_actions(move_input: Vector2) -> void:
    if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT): _try_fire(false)
    var reload_pressed:=Input.is_key_pressed(KEY_R)
    if reload_pressed and not _reload_latch: _begin_reload()
    _reload_latch=reload_pressed
    var dash_pressed:=Input.is_key_pressed(KEY_SPACE)
    if dash_pressed and not _dash_latch and _dash_cooldown<=0.0 and move_input.length_squared()>0.01:
        _dash_left=0.14; _dash_cooldown=0.65; velocity=move_input.normalized()*520.0; _visual.trigger_evade()
    _dash_latch=dash_pressed

func _ai_move_vector() -> Vector2:
    var to_goal:=_ai_goal-global_position
    if to_goal.length()<=18.0: return Vector2.ZERO
    return to_goal.normalized()

func _update_ai_aim_and_fire() -> void:
    var nearest:Node2D=null
    var nearest_d2:float=INF
    for target in get_tree().get_nodes_in_group("prototype_targets"):
        if target is Node2D:
            var d2:float=global_position.distance_squared_to(target.global_position)
            if d2<nearest_d2: nearest_d2=d2; nearest=target
    if nearest:
        var toward:=nearest.global_position-global_position
        if toward.length_squared()>1.0: aim_world=toward.normalized()
        if nearest_d2<=520.0*520.0: _try_fire(false)
    if ammo<=0 and not is_reloading(): _begin_reload()

func _try_fire(force: bool) -> bool:
    if downed_state: return false
    var free_scatter := operator_id=="CHR_PROTO_02" and _scatter_cycle_left>0.0
    if not free_scatter and (_reload_left>0.0 or ammo<=0):
        if ammo<=0: _begin_reload()
        return false
    if not force and _fire_cooldown>0.0: return false
    var interval_scale := 0.55 if _overclock_left>0.0 else (0.52 if free_scatter else 1.0)
    _fire_cooldown=fire_interval*interval_scale
    if not free_scatter:
        ammo-=1; ammo_changed.emit(self,ammo,magazine_size)
    _visual.trigger_fire(); CombatFeedback.play_fire(get_tree(),art_profile)
    if "ROOK" in str(art_profile.get("projectile_profile","")):
        for spread in [-0.13,-0.065,0.0,0.065,0.13]: _spawn_projectile(aim_world.rotated(spread))
    else: _spawn_projectile(aim_world)
    return true

func _spawn_projectile(dir: Vector2) -> void:
    var projectile:=Projectile.new(); get_tree().root.add_child(projectile); projectile.setup(_visual.get_muzzle_global_position(),dir,self,accent_color.lightened(0.35),art_profile)
    var skill_multiplier := 1.25 if _overclock_left>0.0 else (1.18 if _scatter_cycle_left>0.0 else 1.0)
    projectile.damage *= campaign_damage_multiplier*skill_multiplier

func _begin_reload() -> void:
    if downed_state or _reload_left>0.0 or ammo>=magazine_size: return
    if operator_id=="CHR_PROTO_02" and _scatter_cycle_left>0.0: return
    _reload_left=reload_duration

func _sector_from_vector(vec: Vector2) -> int:
    if vec.length_squared()<0.0001: return facing_sector
    return int(floor(fposmod(vec.angle()+PI/8.0,TAU)/(PI/4.0)))%8

func _clamp_to_arena() -> void:
    global_position.x=clampf(global_position.x,movement_bounds.position.x,movement_bounds.end.x)
    global_position.y=clampf(global_position.y,movement_bounds.position.y,movement_bounds.end.y)
