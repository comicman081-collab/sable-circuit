extends Node2D
## Enemy attack controller. Authored art reads these states; it never supplies AI.
const Warning := preload("res://scripts/combat/site7_attack_warning.gd")
const CoverNavigation := preload("res://scripts/combat/cover_navigation.gd")
const MuzzleVFX := preload("res://scripts/vfx/combat_muzzle_vfx.gd")
const ROLES := {"ENM_SITE7_RIFLE_01":"rifle", "ENM_SITE7_SHIELD_01":"shield",
    "ENM_SITE7_DRONE_01":"drone", "ENM_SITE7_ABERRANT_01":"melee", "BOSS_SITE7_ANCHOR_01":"boss",
    "ENM_SITE7_BULWARK_01":"shield", "ENM_SITE7_RAM_01":"melee", "ENM_SITE7_MORTAR_01":"mortar",
    "ENM_SITE7_PRISM_01":"skimmer", "ENM_SITE7_NULL_PYLON_01":"mortar",
    "BOSS_SITE7_FORGE_01":"boss", "BOSS_SITE7_CARRIER_01":"boss",
    "BOSS_SITE7_RELAY_01":"boss", "BOSS_SITE7_REMNANT_01":"boss",
    "BOSS_SITE7_AERATOR_01":"boss", "BOSS_SITE7_CRYO_01":"boss", "BOSS_SITE7_GANTRY_01":"boss",
    "BOSS_SITE7_ARCHIVE_01":"boss", "BOSS_SITE7_ORIGIN_01":"boss"}
const LUNGE_SPEED := 360.0
const LUNGE_DURATION := 0.42
const LUNGE_RADIUS := 58.0
const MAX_CONCURRENT_ATTACKERS := 3
const ECHO_MEMORY := 3
## Length of CRYO's last-phase axis lane (compressor to target); see _frost_sweep_attack.
const FROST_AXIS_REACH := 300.0
## Wind-up (s) of GANTRY's phase-two diagonal rails and its phase-three star; see _rail_charge_attack.
const GANTRY_LATE_WINDUP := 1.6
## Wind-up (s) of INDEX SPIRE's newest echo circle; see _echo_copy_attack.
const ECHO_WINDUP := 1.3
## Wind-up (s) of every ORIGIN warning in its last phase; see _null_convergence_attack.
const ORIGIN_LATE_WINDUP := 1.6
signal attack_started(event: Dictionary)

var actor: EnemyActor
var state := "REPOSITION"
var state_left := 0.7
var state_duration := 0.7
var locked_aim := Vector2.LEFT
var locked_ground := Vector2.LEFT
var burst_left := 0
var burst_clock := 0.0
var phase := 1
var attack_serial := 0
var shots_fired := 0
var lunges := 0
var _struck: Array[int] = []
var _age := 0.0
var _lunge_origin := Vector2.ZERO
var _lunge_reach := 0.0
var _shot_ordinal := 0
var _cover_navigation := CoverNavigation.new()
var _flank_goal := Vector2.INF
var _flank_target := Vector2.INF
var _flank_still := 0.0
# Firing lanes given up on for the current target position. A lane whose view
# solution sits at the edge of the illustrated views can be invalid a few px
# short of it; choosing it again circled a drone in place for good.
var _spent_lanes: Array[Vector2] = []
var _last_position := Vector2.INF
var cover_repositions := 0
var locked_landing := Vector2.ZERO
var mortar_launches := 0
## echo_copy: where the target stood at its last attacks, newest last (never more than
## ECHO_MEMORY, never cleared by a phase change).
var _echo_points: Array[Vector2] = []
signal mortar_launched(event: Dictionary)

func _ready() -> void:
    actor = get_parent() as EnemyActor
    top_level = true
    z_index = 1

func _enter(next_state: String, duration: float) -> void:
    state = next_state
    state_left = duration
    state_duration = maxf(duration, 0.001)
    # Stagger skips step(). Invalidate THIS CanvasItem's cached warning now.
    queue_redraw()

func interrupt() -> void:
    burst_left = 0
    _struck.clear()
    _enter("RECOVER", 0.55)

func step(target: OperatorActor, delta: float) -> void:
    global_transform = Transform2D(0.0, actor.global_position)
    var role := str(ROLES.get(actor.enemy_id,""))
    if role.is_empty():
        actor.velocity = Vector2.ZERO
        _enter("UNSUPPORTED_ROLE",1.0)
        return
    _age += delta
    state_left -= delta
    var offset := target.global_position - actor.global_position
    var dist := offset.length()
    var toward := offset.normalized() if dist > 0.01 else Vector2.LEFT
    # Do not even resolve a new visual yaw while an announced attack is locked.
    # Its body, muzzle and shot must retain the same warning direction.
    var aim := locked_aim
    if state not in ["WINDUP", "BURST", "LUNGE"]:
        aim = actor.aim_from_emitter(target.get_combat_aim_point())
        if not _valid_aim(aim): aim = actor._aim_dir
    var boss := role == "boss"
    var rifle := role == "rifle"
    var shield := role == "shield"
    var drone := role == "drone"
    var skimmer := role == "skimmer"
    var melee := role == "melee"
    var mortar := role == "mortar"
    if state=="REPOSITION" and _flank_goal.is_finite():
        if _last_position.is_finite() and actor.global_position.distance_to(_last_position)<delta*4.0:
            _flank_still+=delta
        else: _flank_still=0.0
        var target_moved := _flank_target.distance_to(target.global_position)>85.0
        if actor.global_position.distance_to(_flank_goal)<8.0 or target_moved or _flank_still>0.8:
            if target_moved: _spent_lanes.clear()
            else: _spent_lanes.append(_flank_goal)
            _flank_goal=Vector2.INF
            _flank_still=0.0
    _last_position=actor.global_position
    phase = 1 if actor.health > actor.max_health * 0.66 else (2 if actor.health > actor.max_health * 0.33 else 3)
    actor.velocity = Vector2.ZERO
    actor._aim_dir = locked_aim if state in ["WINDUP", "BURST", "LUNGE"] else aim
    if state == "REPOSITION":
        if (drone or skimmer or shield) and _flank_goal.is_finite():
            actor.velocity=_move_to(_flank_goal,62.0 if shield else 118.0,delta)
        elif drone or skimmer:
            var tangent := toward.orthogonal() * actor._orbit_sign
            actor.velocity = (tangent * 0.72 + toward * clampf((dist - 280.0) / 160.0, -0.7, 0.7)).limit_length(1.0) * 118.0
            var next := actor.global_position+actor.velocity.normalized()*90.0
            # A local orbit waypoint off the room floor must not stop the drone
            # indefinitely; use its persistent combat lane on the next check.
            if not CoverNavigation._on_floor(actor,next): state_left=0.0
            actor.velocity = _move_to(next,actor.velocity.length(),delta)
        elif melee:
            var approach := dist>85.0 or not CoverNavigation._clear_ground(actor,actor.global_position,target.global_position,CoverNavigation.ground_obstacles(actor))
            actor.velocity = _move_to(target.global_position,112.0,delta) if approach else Vector2.ZERO
        elif shield:
            actor.velocity = _move_to(target.global_position,62.0,delta) if dist > 190.0 else Vector2.ZERO
        elif rifle:
            var radial := 1.0 if dist > 360.0 else (-0.7 if dist < 220.0 else 0.0)
            actor.velocity = (toward * radial + toward.orthogonal() * actor._orbit_sign * 0.38).limit_length(1.0) * 86.0
        if state_left <= 0.0 and (not melee or dist < 250.0):
            var reposition_velocity := actor.velocity
            actor.velocity = Vector2.ZERO
            # Stop/bank first, then freeze the actual emitter ray. Never home
            # a telegraphed shot onto the player's later position.
            var candidate_aim := toward if melee else actor.aim_from_emitter(target.get_combat_aim_point())
            if not _valid_aim(candidate_aim):
                # The target may be inside every authored emitter offset.
                # Keep moving normally; do not advertise or emit a reverse ray.
                if drone or skimmer or shield:
                    if not _flank_goal.is_finite(): _flank_goal=_choose_firing_lane(target)
                    actor.velocity=_move_to(_flank_goal,62.0 if shield else 118.0,delta)
                    state_left=0.2
                else: actor.velocity = reposition_velocity
                queue_redraw()
                return
            if melee and not CoverNavigation._clear_ground(actor,actor.global_position,target.global_position,CoverNavigation.ground_obstacles(actor)):
                # Reach the same side of cover BEFORE announcing a straight
                # charge. Collision still cancels cover added after the warning.
                actor.velocity=reposition_velocity
                state_left=0.2
                queue_redraw()
                return
            if (drone or skimmer or shield) and not CoverNavigation.clear_shot(get_tree(),actor.projectile_origin(candidate_aim),target):
                # The player keeps the protection of cover. Move to a real
                # firing lane and advertise a NEW shot; never home a warning.
                if not _flank_goal.is_finite():
                    _flank_goal=_choose_firing_lane(target)
                actor.velocity=_move_to(_flank_goal,62.0 if shield else 118.0,delta)
                if actor.velocity.length_squared()<0.01:
                    actor._orbit_sign *= -1.0
                    _flank_goal=Vector2.INF
                cover_repositions+=1
                state_left=0.2
                queue_redraw()
                return
            if not boss and _attack_slots_full():
                # Dense encounters keep many robots moving on screen, but only
                # a few may announce at once; the rest hold their lane.
                actor.velocity = reposition_velocity
                state_left = 0.25
                queue_redraw()
                return
            _flank_goal=Vector2.INF
            _spent_lanes.clear()
            locked_aim = candidate_aim
            locked_ground = toward
            locked_landing = target.global_position
            if actor.enemy_id == "ENM_SITE7_RAM_01":
                # This robot hits with its nose, not an elevated gun ray.
                actor.machine_sprite.face_direction(locked_ground)
                locked_aim = locked_ground
            _lunge_origin = actor.global_position
            _lunge_reach = LUNGE_SPEED * LUNGE_DURATION * actor.run_speed_multiplier
            actor._aim_dir = locked_aim
            actor.velocity = Vector2.ZERO
            _enter("WINDUP", 0.9 if mortar else ((0.95 if actor.enemy_id == "BOSS_SITE7_ANCHOR_01" else 1.1) if boss else (0.7 if shield else (0.6 if melee else 0.48))))
            # The emitter visibly gathers the shot it just announced (code-drawn, off the art).
            MuzzleVFX.spawn_charge(get_tree(), actor, str(actor.art_profile.get("projectile_profile", "")), actor._projectile_color(), state_duration)
    elif state == "WINDUP":
        if state_left <= 0.0:
            attack_serial += 1
            _shot_ordinal = 0
            attack_started.emit({"actor_id":actor.get_instance_id(),"enemy_id":actor.enemy_id,
                "attack_serial":attack_serial,"phase":phase,"owner_id":get_instance_id()})
            if melee:
                lunges += 1
                _struck.clear()
                _enter("LUNGE", LUNGE_DURATION)
                var wake := CombatFeedback.spawn_explosion(get_tree(), actor.global_position, "TRAIL", actor._projectile_color(), 20.0)
                if wake != null: wake.follow_node(actor)
            elif mortar:
                _launch_mortar()
                _enter("RECOVER",2.4 * actor.run_attack_interval_multiplier)
            elif boss:
                _boss_attack(target)
                _enter("RECOVER", (1.8 - float(phase) * 0.20) * actor.run_attack_interval_multiplier)
            else:
                burst_left = 3 if rifle else 1
                burst_clock = 0.0
                _enter("BURST", 0.5)
    elif state == "BURST":
        burst_clock -= delta
        if burst_left > 0 and burst_clock <= 0.0:
            _fire(locked_aim)
            burst_left -= 1
            burst_clock += 0.14
        if burst_left <= 0:
            _enter("RECOVER", (1.4 if shield else 0.85) * actor.run_attack_interval_multiplier)
    elif state == "LUNGE":
        actor.velocity = locked_ground * LUNGE_SPEED
        for victim in ([] if actor.enemy_id == "ENM_SITE7_RAM_01" else get_tree().get_nodes_in_group("operators")):
            if not victim is OperatorActor or victim.is_downed() or _struck.has(victim.get_instance_id()):
                continue
            if lunge_contains(victim.global_position) and actor.global_position.distance_to(victim.global_position) < LUNGE_RADIUS:
                victim.apply_damage(18.0 * actor.run_damage_multiplier, actor.enemy_id)
                _struck.append(victim.get_instance_id())
                _show_ram_hit(victim)
        if state_left <= 0.0:
            actor.velocity = Vector2.ZERO
            _enter("RECOVER", 1.1 * actor.run_attack_interval_multiplier)
    elif state == "RECOVER":
        if drone or skimmer:
            var next := actor.global_position+toward.orthogonal()*actor._orbit_sign*75.0
            actor.velocity = _move_to(next,62.0,delta)
        if state_left <= 0.0:
            _enter("REPOSITION", 0.9 if not boss else 0.45)
    queue_redraw()

## Attack tokens: at most MAX_CONCURRENT_ATTACKERS robots in a committed
## warning/shot/charge at once, bosses included in the count. A robot that is
## not simulating (frozen, despawning) cannot fire, so it holds no token.
func _attack_slots_full() -> bool:
    var busy := 0
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node == actor or not node is EnemyActor or node.health <= 0.0 or node.tactics == null: continue
        if node.is_queued_for_deletion() or not node.is_physics_processing(): continue
        if node.tactics.state in ["WINDUP", "BURST", "LUNGE"]: busy += 1
    return busy >= MAX_CONCURRENT_ATTACKERS

func _move_to(goal: Vector2, speed: float, delta: float) -> Vector2:
    return _cover_navigation.direction(actor,goal,delta,speed*actor.run_speed_multiplier*delta)*speed

func _choose_firing_lane(target: OperatorActor) -> Vector2:
    var obstacles := CoverNavigation.ground_obstacles(actor)
    var best := Vector2.INF
    var best_cost := INF
    var target_point := target.get_combat_aim_point()
    if not is_instance_valid(actor.machine_sprite): return best
    if _flank_target.is_finite() and _flank_target.distance_to(target.global_position)>85.0: _spent_lanes.clear()
    var routes := LaneRoutes.new(actor,actor.global_position,obstacles)
    for radius in [180.0,260.0,340.0]:
        for index in range(16):
            var point: Vector2 = target.global_position+Vector2.from_angle(float(index)*TAU/16.0)*float(radius)
            if not CoverNavigation._clear_ground(actor,point,point,obstacles): continue
            if _spent_lanes.any(func(spent: Vector2) -> bool: return spent.distance_to(point) < 12.0): continue
            var cost := routes.cost_to(point,best_cost)
            if cost>=best_cost: continue
            var solution: Dictionary=actor.machine_sprite.target_solution_from(point,target_point)
            if solution.is_empty() or not CoverNavigation.clear_shot(get_tree(),solution.origin,target): continue
            best=point; best_cost=cost
    _flank_target=target.global_position
    _flank_still=0.0
    return best

func commit_lunge_motion(from: Vector2, to: Vector2) -> void:
    if state != "LUNGE" or actor.enemy_id != "ENM_SITE7_RAM_01": return
    for victim in get_tree().get_nodes_in_group("operators"):
        if not victim is OperatorActor or victim.is_downed() or _struck.has(victim.get_instance_id()): continue
        var nearest := Geometry2D.get_closest_point_to_segment(victim.global_position,from,to)
        if lunge_contains(victim.global_position) and nearest.distance_to(victim.global_position) <= LUNGE_RADIUS:
            victim.apply_damage(18.0 * actor.run_damage_multiplier, actor.enemy_id)
            _struck.append(victim.get_instance_id())
            _show_ram_hit(victim)

## The charge connecting: the ram's slam burst on the operator it struck.
func _show_ram_hit(victim: OperatorActor) -> void:
    CombatFeedback.spawn_hit(get_tree(), victim.get_combat_hit_rect().get_center(), actor.art_profile, actor._projectile_color(), actor, locked_ground)

func _launch_mortar() -> void:
    var shell := preload("res://scripts/combat/site7_mortar_shell.gd").new()
    shell.source = actor
    shell.origin = actor.machine_sprite.muzzle_world()
    shell.landing = locked_landing
    actor.get_parent().add_child(shell)
    actor.machine_sprite.fired()
    MuzzleVFX.spawn(get_tree(), shell.origin, Vector2.UP, "MORTAR", actor._projectile_color(), actor)
    CombatFeedback.play_fire(get_tree(),actor.art_profile,actor)
    mortar_launches += 1
    mortar_launched.emit({"origin":shell.origin,"landing":shell.landing,"flight_seconds":shell.flight_seconds,
        "actor_id":actor.get_instance_id(),"shell_id":shell.get_instance_id(),"attack_serial":attack_serial})

func _valid_aim(direction: Vector2) -> bool:
    return direction.is_finite() and direction.length_squared() > 0.000001

func _fire(direction: Vector2) -> void:
    if not _valid_aim(direction): return
    shots_fired += 1
    CombatFeedback.play_fire(get_tree(), actor.art_profile, actor)
    actor._spawn_projectile(direction, self, attack_serial, _shot_ordinal)
    _shot_ordinal += 1

func _boss_attack(target: OperatorActor) -> void:
    match str(actor.art_profile.get("boss_pattern", "anchor_iris")):
        "relay_chain": _relay_chain_attack(target)
        "resonance_lanes": _resonance_attack(target)
        "forge_press": _forge_press_attack(target)
        "carrier_null": _carrier_null_attack(target)
        "bloom_field": _bloom_field_attack(target)
        "frost_sweep": _frost_sweep_attack(target)
        "rail_charge": _rail_charge_attack(target)
        "echo_copy": _echo_copy_attack(target)
        "null_convergence": _null_convergence_attack(target)
        _: _anchor_iris_attack(target)

func _anchor_iris_attack(target: OperatorActor) -> void:
    # Slow readable fan in phase one; frozen impact zones in two; cross lanes
    # in three. Large gaps are intentional. These are damaging, not fake decals.
    if phase >= 2 and attack_serial % 2 == 0:
        _warning("circle", target.global_position, Vector2.RIGHT)
        if phase == 3:
            var origin := actor.global_position
            for i in range(4):
                var ray := locked_ground.rotated(float(i) * PI * 0.5)
                _warning("lane", origin + ray * 100.0, ray)
    else:
        var count := 3 if phase == 1 else 5
        for i in range(count):
            _fire(locked_aim.rotated((float(i) - float(count - 1) * 0.5) * 0.22))

func _relay_chain_attack(target: OperatorActor) -> void:
    if phase >= 2 and attack_serial % 2 == 0:
        _fire(locked_aim.rotated(-0.15))
        _fire(locked_aim.rotated(0.15))
        return
    var count := 5 if phase == 3 else 3
    for i in range(count):
        var offset := (float(i) - float(count - 1) * 0.5) * 110.0
        _warning("circle", target.global_position + locked_ground * offset, Vector2.RIGHT,
            58.0, 430.0, 16.0, 1.1 + float(i) * 0.2)
    if phase >= 2:
        for node in get_tree().get_nodes_in_group("operators"):
            if node is OperatorActor and node != target and not node.is_downed():
                _warning("circle", node.global_position, Vector2.RIGHT, 58.0, 430.0, 16.0, 1.3)

func _resonance_attack(_target: OperatorActor) -> void:
    var origin := actor.global_position
    var burst := phase >= 2 and attack_serial % 2 == 0
    if burst:
        _warning("circle", origin, Vector2.RIGHT, 160.0, 430.0, 16.0, 1.2)
        for angle in [-0.8, 0.8]:
            var ray := locked_ground.rotated(angle)
            _warning("lane", origin, ray, 58.0, 700.0, 16.0, 1.2)
        return
    var angles := [-0.7, -0.35, 0.0, 0.35, 0.7] if phase == 3 else [-0.45, 0.0, 0.45]
    for angle in angles:
        _warning("lane", origin, locked_ground.rotated(angle), 58.0, 700.0, 16.0, 1.2)

func _forge_press_attack(target: OperatorActor) -> void:
    if attack_serial % 2 == 0:
        _fire(locked_aim.rotated(-0.2))
        _fire(locked_aim.rotated(0.2))
    else:
        _warning("circle", target.global_position, Vector2.RIGHT, 90.0, 430.0, 16.0, 1.2)
        if phase >= 2:
            _warning("circle", actor.global_position + locked_ground * 140.0, Vector2.RIGHT,
                160.0, 430.0, 16.0, 1.2)
    if phase == 3:
        for angle in [-PI * 0.25, PI * 0.25]:
            _warning("lane", actor.global_position, locked_ground.rotated(angle),
                58.0, 900.0, 16.0, 1.35)

func _carrier_null_attack(target: OperatorActor) -> void:
    var origin := actor.global_position
    var side := locked_ground.orthogonal()
    if phase == 1:
        _warning("lane", origin, locked_ground, 58.0, 1000.0, 22.0, 1.25)
        _fire(locked_aim.rotated(-0.3))
        _fire(locked_aim.rotated(0.3))
        return
    for offset in [-150.0, 0.0, 150.0]:
        _warning("lane", origin + side * offset, locked_ground, 58.0, 1000.0, 22.0, 1.25)
    if phase == 3:
        _warning("circle", target.global_position, Vector2.RIGHT, 120.0, 430.0, 16.0, 1.55)

## AERATOR TOWER, bloom_field: spore circles open one after another on a ring around the
## target. From phase two the target's own ground blooms too, so the way out of the middle is
## a gap in the ring, and the second attack turns the ring so the gap moves.
func _bloom_field_attack(target: OperatorActor) -> void:
    var turn := attack_serial % 2 == 0
    if turn and phase == 2:
        for offset in [-0.3, 0.0, 0.3]:
            _fire(locked_aim.rotated(offset))
        return
    var count := 4 if phase == 1 else (5 if phase == 2 else 6)
    var spin := (PI * 0.25 if phase == 1 else PI / 6.0) if turn else 0.0
    var ring := 190.0 + 10.0 * float(phase - 1)
    var centre := target.global_position
    for i in range(count):
        var angle := locked_ground.angle() + TAU * float(i) / float(count) + spin
        _warning("circle", centre + Vector2.from_angle(angle) * ring, Vector2.RIGHT,
            64.0, 430.0, 16.0, 1.2 + 0.1 * float(i))
    if phase >= 2:
        _warning("circle", centre, Vector2.RIGHT, 70.0, 430.0, 16.0, 1.7)

## CRYO COMPRESSOR, frost_sweep: frost bars cross the line from the compressor to the target,
## 150 px apart, and light up in a wave (outward; inward in the last phase's second attack).
## The way through is the gap a bar has just left behind. The nearest bar starts 130 px out,
## so standing at the stack's foot is not free either. The last phase adds an axis lane along the
## line; it reaches the second bar and stops (FROST_AXIS_REACH). At 900 px it also ran on over the
## target wherever the floor narrows, and on the operation 7 vault's west ledge and door mouth no
## 1.5-operator gap was left beside it (site7_boss_room_fairness_smoke.gd: 10 spots at a 25 px grid,
## none at 340 px or less on grids of 20-40 px).
func _frost_sweep_attack(_target: OperatorActor) -> void:
    var turn := attack_serial % 2 == 0
    if phase == 1 and turn:
        _fire(locked_aim.rotated(-0.2))
        _fire(locked_aim.rotated(0.2))
        return
    var bars := 2 if phase == 1 else (4 if turn or phase == 3 else 3)
    var origin := actor.global_position
    var along := locked_ground
    var across := along.orthogonal()
    var inward := phase == 3 and turn
    for i in range(bars):
        var wave := bars - 1 - i if inward else i
        _warning("lane", origin + along * (130.0 + 150.0 * float(i)) - across * 350.0, across,
            58.0, 700.0, 30.0, 1.1 + 0.2 * float(wave))
    if phase == 3:
        _warning("lane", origin, along, 58.0, FROST_AXIS_REACH, 22.0, 1.4)

## SIGNAL GANTRY, rail_charge: rail lines cross where the target stands; later the beam's ends
## come down as circles either side of it, and in the last phase the rails become a star. The
## wedge between two rails is the safe ground. Beside a wall the nearest wedge that holds a
## 1.5-operator gap can be 180 px away, which the slowest walk (138 px/s) covers in 1.30 s: on
## operation 8's terminal floor the old 1.4 s (diagonal rails) and 1.5 s (star and its circle)
## left 0.10-0.20 s where site7_boss_room_fairness_smoke.gd asks 0.25 s (101 of 1,410 attacks at
## a 50 px grid). Both now wind up GANTRY_LATE_WINDUP; the boss pattern smoke pins it.
func _rail_charge_attack(target: OperatorActor) -> void:
    var turn := attack_serial % 2 == 0
    var here := target.global_position
    var across := locked_ground.orthogonal()
    match phase:
        1:
            if turn: _warning("circle", here, Vector2.RIGHT, 100.0, 430.0, 16.0, 1.2)
            else: _rail_lines(here, [0.0, PI * 0.5], 26.0, 1.4)
        2:
            if turn:
                for side in [-1.0, 1.0]:
                    _warning("circle", here + across * 160.0 * side, Vector2.RIGHT, 90.0, 430.0, 16.0, 1.2)
            else:
                _rail_lines(here, [0.0, PI * 0.5], 26.0, GANTRY_LATE_WINDUP)
                _rail_lines(here, [PI * 0.25], 22.0, GANTRY_LATE_WINDUP)
        _:
            var turned := PI / 8.0 if turn else 0.0
            _rail_lines(here, [turned, turned + PI * 0.25, turned + PI * 0.5, turned + PI * 0.75], 20.0, GANTRY_LATE_WINDUP)
            if turn: _warning("circle", here, Vector2.RIGHT, 90.0, 430.0, 16.0, GANTRY_LATE_WINDUP)

## Rails through `here`, each `angle` off the boss-to-target line, 1100 px long.
func _rail_lines(here: Vector2, angles: Array, half_width: float, windup: float) -> void:
    for angle in angles:
        var direction := locked_ground.rotated(float(angle))
        _warning("lane", here - direction * 550.0, direction, 58.0, 1100.0, half_width, windup)

## INDEX SPIRE, echo_copy: the ground under the target blooms, and so does the ground it stood
## on at its last attacks (as many as the phase, newest first). Standing still, or walking the
## same line twice, is what the echoes catch. The memory outlives phase changes. The echoes go
## off first (the newest at ECHO_WINDUP, each older one 0.1 s later), then the target's own
## ground, then the last phase's lane. A target that stands still stacks every echo on its own
## spot, so the newest one is all the time it has to leave: beside a wall the nearest gap is
## 120 px, 0.87 s at the slowest walk, and the old 1.0 s left 0.13 s where
## site7_boss_room_fairness_smoke.gd asks 0.25 s (2 of 4,524 attacks on operation 9's stacks
## room at a 25 px grid, all of them the last phase's lane attack). The boss pattern smoke pins it.
func _echo_copy_attack(target: OperatorActor) -> void:
    var here := target.global_position
    _warning("circle", here, Vector2.RIGHT, 70.0, 430.0, 16.0, ECHO_WINDUP + 0.3)
    var recalled := mini(_echo_points.size(), phase)
    for i in range(recalled):
        _warning("circle", _echo_points[_echo_points.size() - 1 - i], Vector2.RIGHT, 70.0, 430.0, 16.0, ECHO_WINDUP + 0.1 * float(i))
    if phase == 3 and attack_serial % 2 == 0:
        _warning("lane", actor.global_position, locked_ground, 58.0, 900.0, 22.0, ECHO_WINDUP + 0.4)
    _echo_points.append(here)
    if _echo_points.size() > ECHO_MEMORY: _echo_points.pop_front()

## ORIGIN CORE, null_convergence: warning lanes run in from every side and meet on the target,
## the core's own ground closes as well, and the last phase does both at once. Stand in a
## gap between two lanes and never beside the core. In the last phase the lanes, the core's
## ground and the target's ground all wind up ORIGIN_LATE_WINDUP: beside a wall the nearest gap
## between its three lanes, the core's circle and the target's own circle is 150 px away
## (1.09 s at the slowest walk), and the old 1.2 s / 1.3 s left 0.11 s where
## site7_boss_room_fairness_smoke.gd asks 0.25 s (3 spots of 5,743 at a 10 px grid on operation
## 10's core room, all of the last phase's second attack). A 180 px gap, the most the room limit
## allows, needs 1.55 s. The boss pattern smoke pins it.
func _null_convergence_attack(target: OperatorActor) -> void:
    var turn := attack_serial % 2 == 0
    var here := target.global_position
    var lanes := 0
    var core_circle := false
    var target_circle := false
    var bolts := false
    match phase:
        1:
            lanes = 0 if turn else 3
            target_circle = turn
            bolts = turn
        2:
            lanes = 0 if turn else 4
            core_circle = turn
            target_circle = turn
            bolts = turn
        _:
            lanes = 3 if turn else 5
            core_circle = turn
            target_circle = true
    var last_phase := phase == 3
    for i in range(lanes):
        var direction := Vector2.from_angle(locked_ground.angle() + TAU * float(i) / float(lanes))
        _warning("lane", here + direction * 420.0, -direction, 58.0, 460.0, 22.0 if last_phase else 20.0, ORIGIN_LATE_WINDUP if last_phase else 1.3)
    if core_circle:
        _warning("circle", actor.global_position, Vector2.RIGHT, 150.0, 430.0, 16.0, ORIGIN_LATE_WINDUP if last_phase else 1.2)
    if target_circle:
        _warning("circle", here, Vector2.RIGHT, 90.0, 430.0, 16.0, ORIGIN_LATE_WINDUP if last_phase else 1.2)
    if bolts:
        _fire(locked_aim.rotated(-0.25))
        _fire(locked_aim.rotated(0.25))

func _warning(kind: String, location: Vector2, direction: Vector2,
        radius: float = 58.0, reach: float = 430.0, half_width: float = 16.0,
        windup: float = -1.0) -> void:
    var warning := Warning.new()
    warning.source = actor
    warning.kind = kind
    warning.top_level = true
    warning.ray = direction
    warning.radius = radius
    warning.reach = reach
    warning.half_width = half_width
    warning.windup = windup if windup >= 0.0 else (1.15 if kind == "circle" else 1.35)
    warning.damage = 20.0
    actor.get_parent().add_child(warning)
    warning.global_transform = Transform2D(0.0,location)

func lunge_contains(point: Vector2) -> bool:
    var offset := point - _lunge_origin
    var nearest := _lunge_origin + locked_ground * clampf(offset.dot(locked_ground),0.0,_lunge_reach)
    return point.distance_to(nearest) <= LUNGE_RADIUS

func _draw() -> void:
    if not is_instance_valid(actor) or actor.health <= 0.0 or state != "WINDUP":
        return
    var progress := 1.0 - clampf(state_left / state_duration, 0.0, 1.0)
    var color := Color("ef907e", 0.30 + progress * 0.42)
    if actor.enemy_id == "ENM_SITE7_MORTAR_01":
        var center := to_local(locked_landing)
        draw_circle(center,64.0,Color("cbadff",0.12))
        draw_arc(center,64.0,0,TAU,64,Color("dfb8ff",0.85),2.0)
        draw_arc(center,59.0,-PI/2,-PI/2+TAU*progress,64,Color("eacaff"),2.4)
    elif "ABERRANT" in actor.enemy_id or actor.enemy_id == "ENM_SITE7_RAM_01":
        var base := to_local(_lunge_origin)
        var side := locked_ground.orthogonal() * LUNGE_RADIUS
        var tip := base + locked_ground * _lunge_reach
        draw_colored_polygon(PackedVector2Array([base-side,base+side,tip+side,tip-side]),Color(color,0.12))
        draw_circle(base,LUNGE_RADIUS,Color(color,0.12))
        draw_circle(tip,LUNGE_RADIUS,Color(color,0.12))
        draw_line(base-side,tip-side,color,1.8)
        draw_line(base+side,tip+side,color,1.8)
        var angle := locked_ground.angle()
        draw_arc(base,LUNGE_RADIUS,angle+PI/2,angle+3*PI/2,32,color,1.8)
        draw_arc(tip,LUNGE_RADIUS,angle-PI/2,angle+PI/2,32,color,1.8)
    else:
        var origin := to_local(actor.projectile_origin(locked_aim))
        draw_line(origin, origin + locked_aim * 300.0, color, 1.1)
    draw_arc(Vector2(0,6), 23.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 32, color, 2.0)

func contract() -> Dictionary:
    return {"state": state, "state_left": state_left, "locked_aim": locked_aim,
        "phase": phase, "attacks": attack_serial, "shots": shots_fired, "lunges": lunges,
        "contract_is_intent_not_validation":true,
        "role":ROLES.get(actor.enemy_id,"unsupported"),"lunge_radius":LUNGE_RADIUS,"lunge_reach":_lunge_reach,
        "cover_repositions":cover_repositions,"navigation_replans":_cover_navigation.replans,
        "mortar_launches":mortar_launches,"locked_landing":locked_landing}

## Route lengths from a robot to its firing-lane candidates. Same graph, edge tests and
## visit order as CoverNavigation._plan, but searched once from the robot and resumed
## for each candidate: planning 48 candidates one by one re-tested every edge from the
## robot each time and stalled a new robot's first tick for 60-110 ms.
class LaneRoutes:
    var actor: Node2D
    var obstacles: Array[Rect2]
    var nodes := PackedVector2Array()
    var distance: Array[float] = []
    var visited: Array[bool] = []
    var order := PackedInt32Array()
    var _pairs: Dictionary
    # Fixed-node floor visibility, shared by searches over the same obstacles and
    # waypoints and cleared like CoverNavigation._edge_cache.
    static var _pair_cache: Dictionary = {}

    func _init(owner: Node2D, origin: Vector2, blocked: Array[Rect2]) -> void:
        actor = owner
        obstacles = blocked
        nodes.append(origin)
        var stage := CoverNavigation._stage(actor)
        var waypoints := PackedVector2Array()
        if stage and stage.get("battlefield") != null and stage.battlefield.has_method("navigation_waypoints"):
            waypoints = stage.battlefield.navigation_waypoints()
        var cache_key := hash([obstacles, waypoints, stage.get_instance_id() if stage else 0])
        if not _pair_cache.has(cache_key):
            if _pair_cache.size() > 48: _pair_cache.clear()
            _pair_cache[cache_key] = {}
        _pairs = _pair_cache[cache_key]
        # Use the planner's exact fixed nodes, including floor-clipped corners.
        # A separate corner loop would miss the new escape node and give a
        # different route length from CoverNavigation._plan.
        nodes.append_array(CoverNavigation._fixed_nodes(actor, waypoints, obstacles))
        for _index in range(nodes.size()):
            distance.append(INF); visited.append(false)
        distance[0]=0

    ## _plan's route length to goal, or INF when there is none. Once the route cannot be
    ## shorter than bound it stops early and returns a value >= bound.
    func cost_to(goal: Vector2, bound: float) -> float:
        var best := INF
        var k := 0
        while true:
            if k == order.size() and not _visit_next(bound): break
            var node := order[k]
            k += 1
            var d := distance[node]
            # _plan visits the goal before any other node at least as far away.
            if node != 0 and best <= d: break
            if d >= bound: break
            if nodes[node].distance_squared_to(goal) > CoverNavigation.MAX_GRAPH_EDGE*CoverNavigation.MAX_GRAPH_EDGE: continue
            # Only an edge that would shorten the route needs its floor test.
            var cost := d+nodes[node].distance_to(goal)
            if cost>=best or cost>=bound: continue
            if CoverNavigation._clear_ground(actor,nodes[node],goal,obstacles): best=cost
        return best

    ## Visits the next node as _plan does (lowest distance, then lowest index) and
    ## relaxes its edges. False once every reachable node has been visited. Edges that
    ## would not shorten a route, or only to bound or beyond, skip their floor test:
    ## bounds only fall, and nodes that far are never read.
    func _visit_next(bound: float) -> bool:
        var next := -1
        for index in range(nodes.size()):
            if not visited[index] and (next<0 or distance[index]<distance[next]): next=index
        if next<0 or distance[next]==INF: return false
        visited[next]=true
        order.append(next)
        for index in range(nodes.size()):
            if visited[index] or index==next: continue
            if nodes[next].distance_squared_to(nodes[index]) > CoverNavigation.MAX_GRAPH_EDGE*CoverNavigation.MAX_GRAPH_EDGE: continue
            var cost := distance[next]+nodes[next].distance_to(nodes[index])
            if cost>=distance[index] or cost>=bound: continue
            if next == 0 or index == 0:
                if not CoverNavigation._clear_ground(actor,nodes[next],nodes[index],obstacles): continue
            else:
                var pair := Vector4(nodes[next].x,nodes[next].y,nodes[index].x,nodes[index].y) if next < index else Vector4(nodes[index].x,nodes[index].y,nodes[next].x,nodes[next].y)
                if not _pairs.has(pair): _pairs[pair] = CoverNavigation._clear_ground(actor,nodes[next],nodes[index],obstacles)
                if not bool(_pairs[pair]): continue
            distance[index]=cost
        return true
