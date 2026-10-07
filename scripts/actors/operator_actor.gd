extends CharacterBody2D
class_name OperatorActor
const CombatSfx := preload("res://scripts/audio/combat_sfx_bank.gd")
const DemoInput := preload("res://scripts/ui/demo_input.gd")

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")
const CoverNavigation := preload("res://scripts/combat/cover_navigation.gd")
var _cover_navigation := CoverNavigation.new()
var _ai_target: Node2D

signal control_changed(actor: OperatorActor, controlled: bool)
signal ammo_changed(actor: OperatorActor, current: int, maximum: int)
signal health_changed(actor: OperatorActor, current: float, maximum: float)
signal downed(actor: OperatorActor)
signal primary_fired(actor: OperatorActor)
signal primary_hit(actor: OperatorActor, applied_damage: float)
signal hit_landed(actor: OperatorActor, target_id: String, applied_damage: float)
signal damage_taken(actor: OperatorActor, applied: float, source_id: String)
# Observation hook after actual projectile setup; does not drive gameplay.
signal projectile_spawned(projectile: Node2D)

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
var equipped_module_id := ""
var equipped_weapon_id := ""
var weapon_spec: Dictionary = {}

var run_speed_multiplier := 1.0
var run_incoming_damage_multiplier := 1.0
var run_primary_damage_multiplier := 1.0
## Hazard tokens are independent of FIELD STIM and other authored run boosts.
## Overlapping frost uses the strongest slow once, rather than compounding it.
var _hazard_speed_factors: Dictionary = {}

var _visual: OperatorVisual
var _fire_cooldown := 0.0
var _reload_left := 0.0
var _dash_left := 0.0
## Keep the original dash request apart from its current frost factor. Reading
## last tick's scaled velocity would compound the slow every physics frame.
var _dash_requested_velocity := Vector2.ZERO
var _last_motion_hazard_factor := 1.0
var _dash_cooldown := 0.0
var _dash_latch := false
var _reload_latch := false
var _ai_goal := Vector2.ZERO
var _ai_tactical_goal := Vector2.INF
var _debug_drive := false
var _debug_move := Vector2.ZERO
var _debug_aim := Vector2.RIGHT
var _debug_run := false
var _pointer_target := Vector2.INF
var _pointer_facing := -1
var _movement_aim_active := false
var _last_move_input := Vector2.ZERO
var _guard_left := 0.0
var _guard_reduction := 0.0
var _overclock_left := 0.0
var _scatter_cycle_left := 0.0
var _last_spore_flinch_msec := -1000

func set_hazard_speed_factor(token: String, factor: float) -> void:
    if downed_state: return
    _hazard_speed_factors[token] = clampf(factor, 0.5, 1.0)

func remove_hazard_speed_factor(token: String) -> void:
    _hazard_speed_factors.erase(token)

func hazard_speed_factor() -> float:
    var factor := 1.0
    for value in _hazard_speed_factors.values(): factor = minf(factor, float(value))
    return factor

func _ready() -> void:
    add_to_group("operators")
    # Top-down bodies ride nothing. In the default grounded mode a robot touched from
    # its north side counts as floor, and its velocity carried the operator like a
    # moving platform; a robot's stale velocity after a reposition threw one 200 px.
    platform_floor_layers = 0
    platform_wall_layers = 0
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
    # Every spawn (including training) has its operator's real default weapon.
    # Persistent campaign equipment can subsequently replace this valid default.
    _apply_weapon_loadout(WeaponRegistry.get_default_weapon(operator_id))
    if is_node_ready(): _visual.configure(display_name, accent_color, art_profile)

func _apply_profile_gamefeel() -> void:
    match str(art_profile.get("motion_profile", "")):
        "MOT_ASTER_01": walk_speed=165.0; run_speed=250.0; fire_interval=0.105; reload_duration=1.02; magazine_size=24; max_health=96.0
        "MOT_ROOK_01": walk_speed=138.0; run_speed=205.0; fire_interval=0.42; reload_duration=1.38; magazine_size=10; max_health=138.0
        "MOT_MICA_01": walk_speed=152.0; run_speed=224.0; fire_interval=0.17; reload_duration=1.12; magazine_size=18; max_health=112.0

func apply_campaign_modifiers(modifiers: Dictionary) -> void:
    campaign_damage_multiplier = clampf(float(modifiers.get("damage_multiplier", 1.0)), 1.0, 2.0)
    equipped_module_id = str(modifiers.get("module_id","")).to_upper()
    var weapon_id:=str(modifiers.get("weapon_id","")).to_upper()
    if not weapon_id.is_empty(): _apply_weapon_loadout(weapon_id)

func _apply_weapon_loadout(weapon_id:String)->void:
    var spec:=WeaponRegistry.get_weapon(weapon_id)
    if spec.is_empty() or not WeaponRegistry.is_compatible(operator_id,weapon_id): return
    equipped_weapon_id=weapon_id.to_upper(); weapon_spec=spec
    fire_interval=clampf(float(spec.get("fire_interval",fire_interval)),0.04,2.0)
    reload_duration=clampf(float(spec.get("reload_duration",reload_duration)),0.25,4.0)
    magazine_size=clampi(int(spec.get("magazine_size",magazine_size)),1,200)
    ammo=magazine_size; _reload_left=0.0; _fire_cooldown=0.0
    ammo_changed.emit(self,ammo,magazine_size)

func apply_run_boosts(modifiers: Dictionary) -> void:
    run_speed_multiplier=clampf(float(modifiers.get("operator_speed_multiplier",1.0)),0.75,1.50)
    run_incoming_damage_multiplier=clampf(float(modifiers.get("incoming_damage_multiplier",1.0)),0.50,1.50)
    run_primary_damage_multiplier=clampf(float(modifiers.get("primary_damage_multiplier",1.0)),0.75,1.75)

func has_module(module_id: String) -> bool: return not equipped_module_id.is_empty() and equipped_module_id==module_id.to_upper()
func set_controlled(value: bool) -> void:
    controlled=value and not downed_state
    if is_node_ready(): _visual.set_selected(controlled)
    control_changed.emit(self,controlled)
func set_ai_goal(world_pos: Vector2) -> void: _ai_goal=world_pos
func set_movement_bounds(bounds: Rect2) -> void: movement_bounds=bounds

func apply_damage(amount: float, source_id: String = "") -> void:
    if downed_state or amount<=0.0: return
    var reduction:=_guard_reduction if _guard_left>0.0 else 0.0
    var applied:=amount*(1.0-clampf(reduction,0.0,0.80))*run_incoming_damage_multiplier
    var before:=health
    health=maxf(0.0,health-applied)
    # Only the health actually lost counts, so a lethal hit does not report its overkill.
    damage_taken.emit(self,before-health,source_id)
    var reaction:=CombatFeedback.hurt_reaction(applied,health,max_health)
    var show_hurt := true
    if source_id == "HAZARD_SPORE_CLOUD" and reaction == "FLINCH":
        var now := Time.get_ticks_msec()
        show_hurt = now - _last_spore_flinch_msec >= 90
        if show_hurt: _last_spore_flinch_msec = now
    if show_hurt and is_node_ready(): _visual.trigger_hit()
    if is_inside_tree():
        if show_hurt: CombatFeedback.spawn_hurt(get_tree(),get_combat_hit_rect().get_center(),"OPERATOR",operator_id,reaction,accent_color)
        if reaction=="DOWNED": SquadCameraPresentation.kick(get_tree(),0.55)
        elif reaction=="HEAVY": SquadCameraPresentation.kick(get_tree(),0.4 if controlled else 0.2)
    if applied >= 0.5: _play_hurt_sfx()
    health_changed.emit(self,health,max_health)
    if health<=0.0:
        _hazard_speed_factors.clear()
        _dash_requested_velocity = Vector2.ZERO
        downed_state=true; controlled=false; velocity=Vector2.ZERO; downed.emit(self)
func heal(amount:float)->float:
    if downed_state or amount<=0.0: return 0.0
    var before:=health; health=minf(max_health,health+amount)
    if health>before: health_changed.emit(self,health,max_health)
    return health-before
func revive(ratio:float=0.35)->void:
    if not downed_state: return
    _hazard_speed_factors.clear()
    downed_state=false; health=maxf(1.0,max_health*clampf(ratio,0.05,1.0)); health_changed.emit(self,health,max_health)
func is_downed()->bool: return downed_state
func reset_for_battle_preview() -> void:
    _hazard_speed_factors.clear()
    downed_state = false
    health = max_health
    ammo = magazine_size
    velocity = Vector2.ZERO
    _reload_left = 0.0
    _fire_cooldown = 0.0
    _dash_left = 0.0
    _dash_requested_velocity = Vector2.ZERO
    _last_motion_hazard_factor = 1.0
    _last_spore_flinch_msec = -1000
    _guard_left = 0.0
    _overclock_left = 0.0
    _scatter_cycle_left = 0.0
    health_changed.emit(self,health,max_health)
    ammo_changed.emit(self,ammo,magazine_size)
func apply_guard(duration:float,reduction:float)->void:
    _guard_left=maxf(_guard_left,duration); _guard_reduction=maxf(_guard_reduction,clampf(reduction,0.0,0.80))
func skill_dash(direction:Vector2,distance:float)->void:
    if downed_state: return
    var dir:=direction.normalized() if direction.length_squared()>0.001 else aim_world
    _dash_requested_velocity = velocity / maxf(0.5, _last_motion_hazard_factor)
    # A skill dash used to write global_position directly.  That skipped the
    # StaticBody2D cover collision used by normal walking, so a player could
    # phase through a visible barrier or cabinet.  Use the body sweep for the
    # complete requested distance; it stops at the first real ground blocker
    # and preserves the ordinary battle-floor clamp for room edges.
    move_and_collide(dir * maxf(0.0,distance) * hazard_speed_factor(), false, 0.08, true)
    _clamp_to_arena()
    _dash_left=maxf(_dash_left,0.10); _dash_cooldown=maxf(_dash_cooldown,0.18)
    if is_node_ready(): _visual.trigger_evade()
func activate_overclock(duration:float)->void: _overclock_left=maxf(_overclock_left,duration); _reload_left=0.0
func activate_scatter_cycle(duration:float)->void:
    _scatter_cycle_left=maxf(_scatter_cycle_left,duration); _reload_left=0.0; ammo=magazine_size; ammo_changed.emit(self,ammo,magazine_size)
func trigger_skill_visual(slot:String)->void:
    if not is_node_ready(): return
    if slot.to_upper()=="E": _visual.trigger_evade()
    else: _visual.trigger_fire()
func on_projectile_hit(target:Node,applied_damage:float)->void:
    primary_hit.emit(self, applied_damage)
    hit_landed.emit(self, str(target.get("enemy_id")) if target.get("enemy_id") != null else target.name, applied_damage)
    var parent_squad:=get_parent() as SquadController
    if parent_squad==null: return
    parent_squad.add_energy(1.25,"primary_hit")
    if operator_id=="CHR_PROTO_01" and target.has_method("is_exposed") and bool(target.call("is_exposed")): parent_squad.add_energy(2.0,"aster_exposed_primary")

func debug_drive(move_vec:Vector2,aim_vec:Vector2)->void:
    _debug_drive=true; _debug_move=move_vec; _debug_aim=aim_vec
    # Capture harnesses sample presentation immediately after requesting an
    # input state. Mirror the normal physics-tick aim resolution here so that
    # the test never reports a one-frame-old aim sector as gameplay output.
    if _debug_aim.length_squared()>0.0001:
        aim_world=_debug_aim.normalized()
        facing_sector=_sector_from_vector(aim_world)
func debug_stop_drive()->void: _debug_drive=false
func debug_fire_once()->bool: return _try_fire(true)
func debug_begin_reload()->void: _begin_reload()
func debug_campaign_damage_multiplier()->float: return campaign_damage_multiplier
func debug_equipped_module()->String: return equipped_module_id
func debug_equipped_weapon()->String: return equipped_weapon_id
func debug_weapon_contract()->Dictionary:
    return {
        "weapon_id":equipped_weapon_id,"display_name":str(weapon_spec.get("display_name","LEGACY PRIMARY")),"class":str(weapon_spec.get("class","LEGACY")),
        "damage":float(weapon_spec.get("damage",0.0)),"projectile_speed":float(weapon_spec.get("projectile_speed",0.0)),"projectile_lifetime":float(weapon_spec.get("projectile_lifetime",0.0)),
        "fire_interval":fire_interval,"magazine_size":magazine_size,"reload_duration":reload_duration,"pellet_count":_weapon_pellet_count(),"ammo_per_trigger":_weapon_ammo_cost(),"engagement_range":_weapon_engagement_range(),"ammo":ammo
    }
func debug_run_boost_contract()->Dictionary: return {"operator_speed_multiplier":run_speed_multiplier,"incoming_damage_multiplier":run_incoming_damage_multiplier,"primary_damage_multiplier":run_primary_damage_multiplier}
func debug_runtime_skill_buffs()->Dictionary: return {"guard_left":_guard_left,"guard_reduction":_guard_reduction,"overclock_left":_overclock_left,"scatter_cycle_left":_scatter_cycle_left,"module_id":equipped_module_id}
func is_reloading()->bool: return _reload_left>0.0
func get_reload_progress()->float:
    if _reload_left<=0.0: return 0.0
    return 1.0-(_reload_left/reload_duration)

func _input(event: InputEvent) -> void:
    if not controlled or downed_state or _debug_drive or DemoInput.touch_mode:
        return
    if event is InputEventKey and event.pressed and not event.echo:
        var code: int = event.physical_keycode if event.physical_keycode != 0 else event.keycode
        if code in [KEY_W, KEY_A, KEY_S, KEY_D, KEY_UP, KEY_LEFT, KEY_DOWN, KEY_RIGHT]:
            _movement_aim_active = true
    if (event is InputEventMouseMotion and event.relative.length_squared() > 0.0) or (event is InputEventMouseButton and event.pressed):
        _movement_aim_active = false
        var runtime := get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
        if runtime and runtime.is_runtime_active():
            _pointer_target = get_canvas_transform().affine_inverse() * event.position
            _resolve_pointer_target()

func _process(_delta: float) -> void:
    if controlled and not downed_state and not _debug_drive and not DemoInput.touch_mode and not _movement_aim_active:
        var runtime := get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
        if runtime and runtime.is_runtime_active():
            _pointer_target = get_global_mouse_position()
            _resolve_pointer_target()

func _physics_process(delta:float)->void:
    _fire_cooldown=maxf(0.0,_fire_cooldown-delta); _dash_cooldown=maxf(0.0,_dash_cooldown-delta); _guard_left=maxf(0.0,_guard_left-delta)
    if _guard_left<=0.0: _guard_reduction=0.0
    _overclock_left=maxf(0.0,_overclock_left-delta); _scatter_cycle_left=maxf(0.0,_scatter_cycle_left-delta)
    if _reload_left>0.0:
        _reload_left=maxf(0.0,_reload_left-delta)
        if _reload_left<=0.0: ammo=magazine_size; ammo_changed.emit(self,ammo,magazine_size)
    if downed_state:
        velocity=Vector2.ZERO; _visual.set_runtime_state(Vector2.ZERO,aim_world,0.0,combat_mode,facing_sector,false,0.0); return
    var move_input:=Vector2.ZERO; var want_run:=false; var fire_requested:=false
    _pointer_target = Vector2.INF
    _pointer_facing = -1
    if _debug_drive:
        move_input=_debug_move.limit_length(1.0)
        want_run=_debug_run
        if _debug_aim.length_squared()>0.0001: aim_world=_debug_aim.normalized()
        _set_motion_presentation_intent(move_input, want_run)
    elif controlled:
        move_input=_read_move_input(); want_run=DemoInput.key(KEY_SHIFT)
        # Match the Studio: a new movement direction owns facing until actual
        # pointer motion/click takes it back. A stationary cursor is not new aim.
        if move_input.length_squared() > 0.01 and not move_input.is_equal_approx(_last_move_input):
            _movement_aim_active = true
        _last_move_input = move_input
        var target := global_position + (DemoInput.aim if DemoInput.aim.length_squared()>0.01 else aim_world)*800.0 if DemoInput.touch_mode else get_global_mouse_position()
        var mouse_vec:=target-global_position
        if DemoInput.touch_mode and DemoInput.aim.length_squared() > 0.01:
            _movement_aim_active = false
        if _movement_aim_active:
            if move_input.length_squared() > 0.01: aim_world = move_input.normalized()
        else:
            _pointer_target = target
            if mouse_vec.length_squared()>1.0: aim_world=mouse_vec.normalized()
        _set_motion_presentation_intent(move_input, want_run)
        _handle_player_actions(move_input)
        fire_requested=DemoInput.fire()
    else:
        move_input=_ai_move_vector()
        _set_motion_presentation_intent(move_input, want_run)
        fire_requested=_update_ai_aim_and_fire()
        if _ai_target == null and _pointer_target == Vector2.INF and move_input.length_squared() > 0.01:
            aim_world = move_input.normalized()
    var requested_velocity:=Vector2.ZERO
    var hazard_factor := hazard_speed_factor()
    var dash_active:=_dash_left>0.0
    if dash_active:
        _dash_left=maxf(0.0,_dash_left-delta)
        requested_velocity=_dash_requested_velocity*hazard_factor
    else:
        requested_velocity=move_input*(run_speed if want_run else walk_speed)*run_speed_multiplier*hazard_factor
    _last_motion_hazard_factor = hazard_factor
    # Fast raster atlases may intentionally hold one authored cell for two UAL
    # timing samples.  During that duplicate sample, advance_scale/hold_scale
    # keeps the gameplay root synchronized with the visible planted sole.  The
    # requested velocity remains the presentation/sector authority; only the
    # displacement fed to CharacterBody2D is cadence-synchronized.
    var displacement_velocity:=requested_velocity
    if not dash_active:
        var fast_runtime:=get_node_or_null("FastCharacterRuntime")
        if fast_runtime!=null and fast_runtime.has_method("is_runtime_active") and bool(fast_runtime.call("is_runtime_active")):
            # R21 frame-transition tracks advance the visible raster and its
            # matching root in the same physics tick.  A static 24fps cell
            # therefore holds its support sole in the world during repeated
            # 60Hz samples instead of being translated by an averaged speed.
            var tracked_root:=false
            if fast_runtime.has_method("prepare_root_motion"):
                tracked_root=bool(fast_runtime.call("prepare_root_motion",requested_velocity,delta))
            if tracked_root and fast_runtime.has_method("get_prepared_root_motion_velocity"):
                displacement_velocity=fast_runtime.call("get_prepared_root_motion_velocity",delta)
            elif fast_runtime.has_method("get_root_motion_scale"):
                var root_scale:=clampf(float(fast_runtime.call("get_root_motion_scale")),0.0,2.0)
                displacement_velocity*=root_scale
    velocity=displacement_velocity
    var before_displacement:=global_position
    move_and_slide(); _clamp_to_arena(); velocity=requested_velocity
    # Every active authored presentation consumes the same post-collision
    # displacement.  This keeps a Motion Studio gait phase tied to real map
    # progress while retaining the older runtime's optional root-motion path.
    for runtime_name in ["FastCharacterRuntime", "MotionLabCharacterRuntime"]:
        var committed_runtime:=get_node_or_null(runtime_name)
        if committed_runtime != null and committed_runtime.has_method("commit_actor_displacement"):
            committed_runtime.call("commit_actor_displacement",global_position-before_displacement,delta)
    if _pointer_target != Vector2.INF:
        _resolve_pointer_target()
    facing_sector=_pointer_facing if _pointer_facing >= 0 else _sector_from_vector(aim_world if combat_mode else (move_input if move_input.length_squared()>0.01 else aim_world))
    var motion_runtime:=get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
    if motion_runtime and motion_runtime.is_runtime_active(): motion_runtime.refresh_pose()
    var visual_speed_denominator:=maxf(1.0,run_speed*run_speed_multiplier); _visual.set_runtime_state(requested_velocity,aim_world,requested_velocity.length()/visual_speed_denominator,combat_mode,facing_sector,is_reloading(),get_reload_progress())
    # Spawn only after real collision/bounds displacement and the matching
    # visible gait cell are committed. Wall contact must not briefly select a
    # moving muzzle and then display a different stationary muzzle this tick.
    if fire_requested: _try_fire(false)

func _set_motion_presentation_intent(move:Vector2,running:bool)->void:
    for runtime_name in ["FastCharacterRuntime", "MotionLabCharacterRuntime"]:
        var runtime:=get_node_or_null(runtime_name)
        if runtime != null and runtime.has_method("set_motion_intent"):
            runtime.call("set_motion_intent",move,running)

func _read_move_input()->Vector2:
    return DemoInput.move_vector()
func _handle_player_actions(move_input:Vector2)->void:
    var reload_pressed:=DemoInput.key(KEY_R)
    if reload_pressed and not _reload_latch: _begin_reload()
    _reload_latch=reload_pressed
    var dash_pressed:=DemoInput.key(KEY_SPACE)
    if dash_pressed and not _dash_latch and _dash_cooldown<=0.0 and move_input.length_squared()>0.01:
        _dash_left=0.14; _dash_cooldown=0.65; _dash_requested_velocity=move_input.normalized()*520.0; velocity=_dash_requested_velocity; _visual.trigger_evade()
    _dash_latch=dash_pressed
func _ai_move_vector()->Vector2:
    # Formation remains the fallback. A follower that is outside its actual
    # weapon range, or whose lane is blocked by visible cover, owns a short
    # lived flank/approach goal instead of skating in place behind the lead.
    var leader := (get_parent() as SquadController).get_active_operator() if get_parent() is SquadController else null
    if leader != null and leader != self and global_position.distance_to(leader.global_position) > 520.0:
        _ai_tactical_goal = Vector2.INF
    var goal := _ai_tactical_goal if _ai_tactical_goal.is_finite() else _ai_goal
    # Keep off room hazards: never park on a vent, and step off one about to discharge.
    var safe := ZoneHazard.steer(get_tree(), global_position, goal, get_parent().get_parent() if get_parent() != null else null)
    if safe != goal:
        if global_position.distance_to(safe) <= 18.0: return Vector2.ZERO
        return _cover_navigation.direction(self,safe,get_physics_process_delta_time())
    var to_goal:=goal-global_position
    if _ai_tactical_goal.is_finite() and to_goal.length() <= 18.0:
        _ai_tactical_goal = Vector2.INF
        to_goal = _ai_goal - global_position
    if to_goal.length()<=18.0: return Vector2.ZERO
    return _cover_navigation.direction(self,goal,get_physics_process_delta_time())
func _update_ai_aim_and_fire()->bool:
    var nearest:Node2D=null; var nearest_d2:float=INF
    var fallback:Node2D=null; var fallback_d2:float=INF
    var fire_requested:=false
    _ai_target=null
    var leader := (get_parent() as SquadController).get_active_operator() if get_parent() is SquadController else null
    for target in get_tree().get_nodes_in_group("prototype_targets"):
        if target is Node2D:
            # Encounters can be registered ahead of the camera. Followers
            # must not abandon the controlled operator to chase a hostile in
            # a room that the player has not reached.
            if leader != null and leader != self and leader.global_position.distance_squared_to(target.global_position) > 900.0*900.0:
                continue
            var d2:float=global_position.distance_squared_to(target.global_position)
            if d2 < fallback_d2:
                fallback_d2=d2; fallback=target
            _pointer_target=target.get_combat_aim_point() if target.has_method("get_combat_aim_point") else target.global_position
            _resolve_pointer_target()
            if not CoverNavigation.clear_shot(get_tree(),_get_projectile_spawn_origin(),target): continue
            if d2>=nearest_d2: continue
            nearest_d2=d2; nearest=target
    if nearest:
        var toward:=nearest.global_position-global_position
        _pointer_target = nearest.call("get_combat_aim_point") if nearest.has_method("get_combat_aim_point") else nearest.global_position
        toward = _pointer_target - global_position
        if toward.length_squared()>1.0: aim_world=toward.normalized()
        var engagement:=_weapon_engagement_range()
        fire_requested=nearest_d2<=engagement*engagement
        _ai_target=nearest
        _refresh_ai_tactical_goal(nearest,nearest_d2,engagement,false)
    elif fallback:
        # Do not fire through a prop. Move around it to an authored-ground
        # firing lane, then reacquire on the next physics tick.
        _refresh_ai_tactical_goal(fallback,fallback_d2,_weapon_engagement_range(),true)
    else:
        _pointer_target=Vector2.INF
        _ai_tactical_goal=Vector2.INF
    if ammo<_weapon_ammo_cost() and not is_reloading(): _begin_reload()
    return fire_requested

func _refresh_ai_tactical_goal(target: Node2D, distance_squared: float, engagement: float, lane_blocked: bool) -> void:
    if not is_instance_valid(target):
        _ai_tactical_goal=Vector2.INF
        return
    # Keep a firing standoff suitable for each weapon. ROOK must close from
    # the entry formation; ASTER/MICA only flank when a cover silhouette
    # really blocks the muzzle-to-target ray.
    if not lane_blocked and distance_squared <= pow(engagement * 0.84, 2.0):
        _ai_tactical_goal=Vector2.INF
        return
    var target_point: Vector2 = target.get_combat_aim_point() if target.has_method("get_combat_aim_point") else target.global_position
    var away:=global_position-target_point
    if away.length_squared() < 1.0:
        away=Vector2.LEFT
    away=away.normalized()
    var standoff:=clampf(engagement*0.72,110.0,260.0)
    var base:=target_point+away*standoff
    var side:=Vector2(-away.y,away.x)
    var bias:=1.0 if operator_id=="CHR_PROTO_02" else -1.0
    var candidates: Array[Vector2] = [base+side*82.0*bias,base-side*82.0*bias,base]
    var stage: Node = get_parent().get_parent() if get_parent()!=null else null
    for candidate in candidates:
        var point:=candidate
        if stage!=null and stage.has_method("constrain_battle_position"):
            point=stage.call("constrain_battle_position",point)
        if CoverNavigation.first_cover(get_tree(),point,target_point)==null:
            _ai_tactical_goal=point
            return
    # The navigation graph will still seek an around-cover route. It never
    # authorizes a blocked shot; clear_shot remains the firing gate above.
    _ai_tactical_goal=base

func _try_fire(force:bool)->bool:
    if downed_state: return false
    var free_scatter:=operator_id=="CHR_PROTO_02" and _scatter_cycle_left>0.0
    var ammo_cost:=_weapon_ammo_cost()
    if not free_scatter and (_reload_left>0.0 or ammo<ammo_cost):
        if ammo<ammo_cost: _begin_reload()
        return false
    if not force and _fire_cooldown>0.0: return false
    if _pointer_target != Vector2.INF:
        _resolve_pointer_target()
    # Followers recheck AFTER movement/gait/muzzle commit. Never restrict the
    # controlled player's choice to fire into cover, nor debug shot fixtures.
    if not force and not controlled and not _debug_drive:
        if not CoverNavigation.clear_shot(get_tree(),_get_projectile_spawn_origin(),_ai_target): return false
    var interval_scale:=0.55 if _overclock_left>0.0 else (0.52 if free_scatter else 1.0); _fire_cooldown=fire_interval*interval_scale
    if not free_scatter: ammo-=ammo_cost; ammo_changed.emit(self,ammo,magazine_size)
    # Aim can change and fire in the same physics tick.  Resolve presentation
    # direction before the fire signal/projectile spawn so the authored muzzle
    # socket cannot lag one sector behind the actual shot direction.
    facing_sector=_pointer_facing if _pointer_facing >= 0 else _sector_from_vector(aim_world)
    _visual.trigger_fire(); primary_fired.emit(self); CombatFeedback.play_fire(get_tree(),art_profile,self)
    var count:=_weapon_pellet_count(); var spread:=float(weapon_spec.get("spread_radians",0.0)) if not weapon_spec.is_empty() else (0.065 if "ROOK" in str(art_profile.get("projectile_profile","")) else 0.0)
    if count<=1:
        var wobble:=0.0
        if spread>0.0: wobble=spread*float((ammo%3)-1)
        _spawn_projectile(aim_world.rotated(wobble))
    else:
        var center:=(float(count)-1.0)*0.5
        for i in range(count): _spawn_projectile(aim_world.rotated((float(i)-center)*spread))
    return true

func _spawn_projectile(dir:Vector2)->void:
    var projectile:=Projectile.new(); get_tree().root.add_child(projectile); projectile.setup(_get_projectile_spawn_origin(),dir,self,accent_color.lightened(0.35),_weapon_art_profile())
    projectile_spawned.emit(projectile)
    if not weapon_spec.is_empty():
        projectile.damage=clampf(float(weapon_spec.get("damage",projectile.damage)),0.1,200.0); projectile.speed=clampf(float(weapon_spec.get("projectile_speed",projectile.speed)),100.0,2400.0); projectile.lifetime=clampf(float(weapon_spec.get("projectile_lifetime",projectile.lifetime)),0.1,4.0)
    var skill_multiplier:=1.25 if _overclock_left>0.0 else (1.18 if _scatter_cycle_left>0.0 else 1.0); projectile.damage*=campaign_damage_multiplier*skill_multiplier*run_primary_damage_multiplier

# Built once per weapon instead of once per shot: a replaced `weapon_spec` or
# `art_profile` object rebuilds it, and Projectile.setup copies what it is handed.
var _shot_profile: Dictionary = {}
var _shot_profile_art: Dictionary = {}
var _shot_profile_spec: Dictionary = {}

## Only the shot's visual families may override an operator profile. Identity,
## authored hand art and both sound profiles remain the operator's original data.
func _weapon_art_profile() -> Dictionary:
    if _shot_profile.is_empty() or not is_same(_shot_profile_art, art_profile) or not is_same(_shot_profile_spec, weapon_spec):
        _shot_profile = art_profile.duplicate(true)
        for key in ["projectile_profile", "hit_vfx_profile"]:
            var requested := str(weapon_spec.get(key, ""))
            if not requested.is_empty(): _shot_profile[key] = requested
        _shot_profile_art = art_profile; _shot_profile_spec = weapon_spec
    return _shot_profile

func _get_projectile_spawn_origin()->Vector2:
    # Data-driven authored operators and ASTER both own visible per-direction
    # muzzle sockets.  Use the active authored presentation first so flash,
    # tracer, and projectile birth cannot diverge.
    var motion_lab_runtime:=get_node_or_null("MotionLabCharacterRuntime")
    if motion_lab_runtime!=null and motion_lab_runtime.has_method("is_runtime_active") and bool(motion_lab_runtime.call("is_runtime_active")) and motion_lab_runtime.has_method("get_authored_muzzle_global_position"):
        var motion_lab_origin:Vector2=motion_lab_runtime.call("get_authored_muzzle_global_position")
        return motion_lab_origin
    var fast_runtime:=get_node_or_null("FastCharacterRuntime")
    if fast_runtime!=null and fast_runtime.has_method("is_runtime_active") and bool(fast_runtime.call("is_runtime_active")) and fast_runtime.has_method("get_authored_muzzle_global_position"):
        var fast_origin:Vector2=fast_runtime.call("get_authored_muzzle_global_position")
        return fast_origin
    var authored_preview:=get_node_or_null("AsterV4LocomotionPreview")
    if authored_preview!=null and authored_preview.has_method("is_runtime_active") and bool(authored_preview.call("is_runtime_active")) and authored_preview.has_method("get_authored_muzzle_global_position"):
        var authored_origin:Vector2=authored_preview.call("get_authored_muzzle_global_position")
        return authored_origin
    return _visual.get_muzzle_global_position()

func _resolve_pointer_target() -> void:
    var runtime := get_node_or_null("MotionLabCharacterRuntime")
    if runtime and runtime.call("is_runtime_active"):
        var result: Dictionary = runtime.call("resolve_pointer_aim", _pointer_target)
        aim_world = result.aim
        _pointer_facing = int(result.direction)
        facing_sector = _pointer_facing
        runtime.call("refresh_pose")
    else:
        var toward := _pointer_target - _get_projectile_spawn_origin()
        if toward.length_squared() > 1.0:
            aim_world = toward.normalized()

func get_combat_hit_rect() -> Rect2:
    var height := float(art_profile.get("motion_lab_display_height_px", 129.6))
    return Rect2(global_position + Vector2(-height * 0.18, -height * 0.94), Vector2(height * 0.36, height * 0.94 + 4.0))

func get_combat_aim_point() -> Vector2:
    return get_combat_hit_rect().get_center()

func _weapon_pellet_count()->int:
    if not weapon_spec.is_empty(): return clampi(int(weapon_spec.get("pellet_count",1)),1,12)
    return 5 if "ROOK" in str(art_profile.get("projectile_profile","")) else 1
func _weapon_ammo_cost()->int:
    if not weapon_spec.is_empty(): return clampi(int(weapon_spec.get("ammo_per_trigger",1)),1,12)
    return 1
func _weapon_engagement_range()->float:
    if not weapon_spec.is_empty(): return clampf(float(weapon_spec.get("engagement_range",520.0)),160.0,800.0)
    return 520.0
func _begin_reload()->void:
    if downed_state or _reload_left>0.0 or ammo>=magazine_size: return
    if operator_id=="CHR_PROTO_02" and _scatter_cycle_left>0.0: return
    _reload_left=reload_duration
    if is_inside_tree(): CombatSfx.play(get_tree(), _voice_prefix()+"_reload", self)
## Suit impact layer plus this operator's own hurt voice.
func _play_hurt_sfx()->void:
    if not is_inside_tree(): return
    CombatSfx.play(get_tree(), "impact_body", self)
    CombatSfx.play(get_tree(), _voice_prefix()+"_hurt", self)
func _voice_prefix()->String:
    match operator_id:
        "CHR_PROTO_02": return "rook"
        "CHR_PROTO_03": return "mica"
    return "aster"
func _sector_from_vector(vec:Vector2)->int:
    if vec.length_squared()<0.0001: return facing_sector
    return int(floor(fposmod(vec.angle()+PI/8.0,TAU)/(PI/4.0)))%8
func _clamp_to_arena()->void:
    var stage := get_parent().get_parent() if get_parent() else null
    if stage and stage.has_method("has_battle_floor") and stage.call("has_battle_floor"):
        global_position = stage.call("constrain_battle_position", global_position)
        return
    global_position.x=clampf(global_position.x,movement_bounds.position.x,movement_bounds.end.x); global_position.y=clampf(global_position.y,movement_bounds.position.y,movement_bounds.end.y)
