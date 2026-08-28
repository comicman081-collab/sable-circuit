extends Node
class_name OperatorSkillController

const SkillVFX := preload("res://scripts/vfx/operator_skill_vfx.gd")

const Q_COOLDOWNS := {"CHR_PROTO_01":4.0,"CHR_PROTO_02":5.0,"CHR_PROTO_03":6.0}
const E_COOLDOWNS := {"CHR_PROTO_01":5.0,"CHR_PROTO_02":8.0,"CHR_PROTO_03":8.0}

var actor: OperatorActor
var squad: SquadController
var q_left := 0.0
var e_left := 0.0
var _passive_left := 1.0
var _passive_pulses := 0
var _q_latch := false
var _e_latch := false
var _x_latch := false
var _last_skill := "NONE"
var _last_target_id := ""
var _last_synergy := "NONE"
var _last_hits := 0

func _ready() -> void:
    actor = get_parent() as OperatorActor
    call_deferred("_bind_squad")

func _bind_squad() -> void:
    if actor != null:
        squad = actor.get_parent() as SquadController

func _process(delta: float) -> void:
    q_left = maxf(0.0,q_left-delta)
    e_left = maxf(0.0,e_left-delta)
    _passive_left = maxf(0.0,_passive_left-delta)
    if actor == null or squad == null or actor.is_downed():
        _q_latch=false; _e_latch=false; _x_latch=false
        return
    if _passive_left<=0.0:
        _tick_passive()
        _passive_left=1.0
    if not actor.controlled:
        _q_latch=false; _e_latch=false; _x_latch=false
        return
    var q_pressed := Input.is_key_pressed(KEY_Q)
    var e_pressed := Input.is_key_pressed(KEY_E)
    var x_pressed := Input.is_key_pressed(KEY_X)
    if q_pressed and not _q_latch: try_cast("Q")
    if e_pressed and not _e_latch: try_cast("E")
    if x_pressed and not _x_latch: try_cast("X")
    _q_latch=q_pressed; _e_latch=e_pressed; _x_latch=x_pressed

func try_cast(slot: String) -> bool:
    if actor == null or squad == null or actor.is_downed(): return false
    var key := slot.to_upper()
    if key == "Q":
        if q_left > 0.0: return false
        if not _cast_q(): return false
        q_left = float(Q_COOLDOWNS.get(actor.operator_id,5.0))
        return true
    if key == "E":
        if e_left > 0.0: return false
        if not _cast_e(): return false
        e_left = float(E_COOLDOWNS.get(actor.operator_id,7.0))
        return true
    if key == "X":
        if not squad.spend_energy(100.0,"ultimate:"+actor.display_name): return false
        if not _cast_ultimate():
            squad.add_energy(100.0,"ultimate_refund")
            return false
        return true
    return false

func _tick_passive() -> bool:
    if actor==null or squad==null or actor.is_downed(): return false
    match actor.operator_id:
        "CHR_PROTO_02":
            if _any_hostile_status("is_staggered"):
                squad.add_energy(1.5,"rook_breach_momentum")
                _passive_pulses+=1
                return true
        "CHR_PROTO_03":
            if _any_hostile_status("is_exposed"):
                squad.add_energy(1.0,"mica_sensor_feedback")
                _passive_pulses+=1
                return true
    return false

func _passive_id() -> String:
    match actor.operator_id if actor else "":
        "CHR_PROTO_01": return "ASTER_PRISM_LOCK"
        "CHR_PROTO_02": return "ROOK_BREACH_MOMENTUM"
        "CHR_PROTO_03": return "MICA_SENSOR_FEEDBACK"
    return "UNKNOWN_PASSIVE"

func _any_hostile_status(method_name: String) -> bool:
    if actor==null: return false
    for node in actor.get_tree().get_nodes_in_group("prototype_targets"):
        if is_instance_valid(node) and node.has_method(method_name) and bool(node.call(method_name)):
            return true
    return false

func _cast_q() -> bool:
    _last_hits = 0; _last_synergy = "NONE"; _last_target_id = ""
    match actor.operator_id:
        "CHR_PROTO_01": return _aster_prism()
        "CHR_PROTO_02": return _rook_breach_slam()
        "CHR_PROTO_03": return _mica_pulse_scan()
    return false

func _cast_e() -> bool:
    _last_hits = 0; _last_synergy = "NONE"; _last_target_id = ""
    match actor.operator_id:
        "CHR_PROTO_01":
            actor.skill_dash(actor.aim_world,150.0)
            actor.trigger_skill_visual("E")
            _spawn_vfx("VECTOR_DASH",85.0,actor.aim_world)
            _last_skill="ASTER_VECTOR_DASH"; return true
        "CHR_PROTO_02":
            actor.apply_guard(5.0,0.50)
            actor.trigger_skill_visual("E")
            _spawn_vfx("BULWARK",70.0,actor.aim_world)
            _last_skill="ROOK_BULWARK"; return true
        "CHR_PROTO_03":
            actor.skill_dash(-actor.aim_world,105.0)
            squad.apply_relay_support(0.10,4.0,0.20)
            actor.trigger_skill_visual("E")
            _spawn_vfx("RELAY_STEP",90.0,-actor.aim_world)
            _last_skill="MICA_RELAY_STEP"; _last_synergy="SQUAD_RECOVERY_GUARD"; return true
    return false

func _cast_ultimate() -> bool:
    _last_hits = 0; _last_synergy = "NONE"; _last_target_id = ""
    match actor.operator_id:
        "CHR_PROTO_01":
            actor.activate_overclock(5.0)
            actor.trigger_skill_visual("X")
            _spawn_vfx("OVERCLOCK",105.0,actor.aim_world,0.85)
            _last_skill="ASTER_OVERCLOCK"; return true
        "CHR_PROTO_02":
            actor.activate_scatter_cycle(5.0)
            actor.apply_guard(5.0,0.22)
            actor.trigger_skill_visual("X")
            _spawn_vfx("SCATTER_CYCLE",160.0,actor.aim_world,0.85)
            _last_skill="ROOK_SCATTER_CYCLE"; return true
        "CHR_PROTO_03":
            var targets := _hostiles_in_radius(620.0)
            for enemy in targets:
                enemy.apply_exposed(10.0,"MICA_SENSOR_BLOOM")
                enemy.apply_damage(18.0)
                if not ("BOSS" in enemy.enemy_id or "ANCHOR" in enemy.enemy_id): enemy.apply_stagger(0.8,"MICA_SENSOR_BLOOM")
            squad.apply_relay_support(0.08,6.0,0.15)
            actor.trigger_skill_visual("X")
            _spawn_vfx("SENSOR_BLOOM",360.0,actor.aim_world,1.0)
            _last_skill="MICA_SENSOR_BLOOM"; _last_hits=targets.size(); _last_synergy="AREA_EXPOSED_RECOVERY"; return true
    return false

func _aster_prism() -> bool:
    var target := _nearest_in_aim(560.0,0.35)
    if target == null: return false
    var exploited := target.is_exposed()
    var amount := 26.0 * (1.65 if exploited else 1.0)
    target.apply_damage(amount)
    if exploited:
        squad.add_energy(8.0,"aster_exploit")
        _last_synergy="EXPOSED_EXPLOIT"
    actor.trigger_skill_visual("Q")
    _spawn_vfx("ASTER_PRISM",minf(520.0,actor.global_position.distance_to(target.global_position)),(target.global_position-actor.global_position).normalized())
    _last_skill="ASTER_PRISM"; _last_hits=1; _last_target_id=target.enemy_id
    return true

func _rook_breach_slam() -> bool:
    var target := _nearest_in_aim(220.0,-0.10)
    if target == null: return false
    var consumed := target.consume_exposed_for_stagger(2.4,"ROOK_BREACH_SLAM")
    target.apply_damage(42.0 if consumed else 30.0)
    if consumed:
        squad.add_energy(28.0,"rook_exposed_stagger")
        _last_synergy="EXPOSED_CONSUMED_STAGGER"
    actor.trigger_skill_visual("Q")
    _spawn_vfx("ROOK_BREACH_SLAM",150.0,actor.aim_world)
    _last_skill="ROOK_BREACH_SLAM"; _last_hits=1; _last_target_id=target.enemy_id
    return true

func _mica_pulse_scan() -> bool:
    var targets := _hostiles_in_radius(420.0)
    if targets.is_empty(): return false
    for enemy in targets: enemy.apply_exposed(6.0,"MICA_PULSE_SCAN")
    squad.add_energy(minf(8.0,2.0+float(targets.size())*1.5),"mica_scan")
    actor.trigger_skill_visual("Q")
    _spawn_vfx("MICA_PULSE_SCAN",300.0,actor.aim_world,0.82)
    _last_skill="MICA_PULSE_SCAN"; _last_hits=targets.size(); _last_synergy="EXPOSED_SETUP"
    return true

func _hostiles_in_radius(radius: float) -> Array[EnemyActor]:
    var out: Array[EnemyActor] = []
    var r2 := radius*radius
    for node in actor.get_tree().get_nodes_in_group("prototype_targets"):
        if node is EnemyActor and is_instance_valid(node) and node.health>0.0 and actor.global_position.distance_squared_to(node.global_position)<=r2:
            out.append(node as EnemyActor)
    return out

func _nearest_in_aim(radius: float, min_dot: float) -> EnemyActor:
    var best: EnemyActor = null
    var best_score := INF
    var aim_dir := actor.aim_world.normalized() if actor.aim_world.length_squared()>0.001 else Vector2.RIGHT
    for enemy in _hostiles_in_radius(radius):
        var delta := enemy.global_position-actor.global_position
        var dist := delta.length()
        if dist<=0.001: continue
        var dot := aim_dir.dot(delta/dist)
        if dot<min_dot: continue
        var score := dist + (1.0-dot)*160.0
        if score<best_score:
            best_score=score; best=enemy
    return best

func _spawn_vfx(id_value: String, radius: float, aim_value: Vector2, duration: float = 0.62) -> void:
    var fx := SkillVFX.new()
    actor.get_tree().root.add_child(fx)
    fx.global_position = actor.global_position + Vector2(0,-18)
    fx.setup(id_value,actor.accent_color.lightened(0.12),radius,aim_value,duration)

func debug_force_cast(slot: String) -> bool:
    if slot.to_upper()=="Q": q_left=0.0
    if slot.to_upper()=="E": e_left=0.0
    return try_cast(slot)

func debug_force_passive_tick() -> bool:
    return _tick_passive()

func debug_contract() -> Dictionary:
    return {
        "operator_id":actor.operator_id if actor else "",
        "passive_id":_passive_id(),
        "passive_pulses":_passive_pulses,
        "q_cooldown":q_left,
        "e_cooldown":e_left,
        "q_ready":q_left<=0.0,
        "e_ready":e_left<=0.0,
        "ultimate_key":"X",
        "reload_key":"R",
        "last_skill":_last_skill,
        "last_target_id":_last_target_id,
        "last_synergy":_last_synergy,
        "last_hits":_last_hits,
        "skill_icons":actor.art_profile.get("hud_action_icon_assets",[]) if actor else []
    }
