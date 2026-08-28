extends Node2D
class_name SquadController

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")

signal energy_changed(current: float, maximum: float)
signal revive_state_changed(active: bool, target_name: String, progress: float)
signal revive_completed(target: OperatorActor)

const MAX_ENERGY := 100.0
const REVIVE_RANGE := 92.0
const REVIVE_DURATION := 2.20
const REVIVE_HEALTH_RATIO := 0.35
const REVIVE_GUARD_DURATION := 1.25
const REVIVE_GUARD_REDUCTION := 0.65

var operators: Array[OperatorActor] = []
var active_index := 0
var _key_latch := [false, false, false]
var squad_energy := 0.0
var _last_energy_reason := "INIT"
var run_energy_gain_multiplier := 1.0

var _reviver: OperatorActor = null
var _revive_target: OperatorActor = null
var _revive_elapsed := 0.0
var _completed_revives := 0
var _last_revived_operator_id := ""

func _ready() -> void:
    add_to_group("squad_controller")
    _spawn_operator("CHR_PROTO_01", "ASTER", Color("69d2ff"), Vector2(410,390))
    _spawn_operator("CHR_PROTO_02", "ROOK", Color("d39a58"), Vector2(330,470))
    _spawn_operator("CHR_PROTO_03", "MICA", Color("62d8c8"), Vector2(485,475))
    request_control(0)

func _process(delta: float) -> void:
    for i in range(3):
        var pressed:=Input.is_key_pressed(KEY_1+i)
        if pressed and not _key_latch[i]: request_control(i)
        _key_latch[i]=pressed
    _update_revive(delta,Input.is_key_pressed(KEY_F))
    _update_formation()

func _spawn_operator(id_value:String,label:String,color:Color,pos:Vector2) -> void:
    var actor:=OPERATOR_SCENE.instantiate() as OperatorActor
    actor.configure(id_value,label,color)
    actor.global_position=pos
    actor.downed.connect(_on_operator_downed)
    add_child(actor)
    operators.append(actor)

func request_control(index:int) -> void:
    if index<0 or index>=operators.size(): return
    if operators[index].is_downed(): return
    if index!=active_index:
        _reset_revive_state()
    active_index=index
    for i in range(operators.size()):
        operators[i].set_controlled(i==active_index)

func get_active_operator() -> OperatorActor:
    if operators.is_empty(): return null
    if active_index<operators.size() and not operators[active_index].is_downed(): return operators[active_index]
    for i in range(operators.size()):
        if not operators[i].is_downed():
            active_index=i
            return operators[i]
    return null

func configure_run_energy_multiplier(value: float) -> void:
    run_energy_gain_multiplier=clampf(value,0.5,2.0)

func add_energy(amount: float, reason: String = "", apply_run_multiplier: bool = true) -> float:
    if amount<=0.0: return squad_energy
    var credited:=amount*(run_energy_gain_multiplier if apply_run_multiplier else 1.0)
    var before:=squad_energy
    squad_energy=clampf(squad_energy+credited,0.0,MAX_ENERGY)
    _last_energy_reason=reason
    if not is_equal_approx(before,squad_energy): energy_changed.emit(squad_energy,MAX_ENERGY)
    return squad_energy

func spend_energy(amount: float, reason: String = "") -> bool:
    if amount<=0.0: return true
    if squad_energy+0.001<amount: return false
    squad_energy=maxf(0.0,squad_energy-amount)
    _last_energy_reason=reason
    energy_changed.emit(squad_energy,MAX_ENERGY)
    return true

func apply_relay_support(heal_ratio: float, guard_duration: float, guard_reduction: float) -> void:
    for actor in operators:
        if actor==null: continue
        if not actor.is_downed():
            actor.heal(actor.max_health*clampf(heal_ratio,0.0,0.5))
            actor.apply_guard(guard_duration,guard_reduction)

func has_revivable_target_in_range() -> bool:
    var active:=get_active_operator()
    if active==null or active.is_downed(): return false
    return _nearest_downed_operator(active)!=null

func is_reviving() -> bool:
    return _reviver!=null and _revive_target!=null and _revive_elapsed>0.0

func _update_revive(delta: float, interact_held: bool) -> void:
    var active:=get_active_operator()
    if active==null or active.is_downed() or not interact_held:
        _reset_revive_state()
        return

    var target:=_nearest_downed_operator(active)
    if target==null:
        _reset_revive_state()
        return

    if _reviver!=active or _revive_target!=target:
        _reviver=active
        _revive_target=target
        _revive_elapsed=0.0
        revive_state_changed.emit(true,target.display_name,0.0)

    _revive_elapsed=minf(REVIVE_DURATION,_revive_elapsed+maxf(0.0,delta))
    var progress:=clampf(_revive_elapsed/REVIVE_DURATION,0.0,1.0)
    revive_state_changed.emit(true,target.display_name,progress)
    if _revive_elapsed+0.0001<REVIVE_DURATION:
        return

    target.revive(REVIVE_HEALTH_RATIO)
    target.apply_guard(REVIVE_GUARD_DURATION,REVIVE_GUARD_REDUCTION)
    _completed_revives+=1
    _last_revived_operator_id=target.operator_id
    revive_completed.emit(target)
    revive_state_changed.emit(false,target.display_name,1.0)
    _clear_revive_state_without_signal()

func _nearest_downed_operator(reviver: OperatorActor) -> OperatorActor:
    var best:OperatorActor=null
    var best_d2:=REVIVE_RANGE*REVIVE_RANGE
    for actor in operators:
        if actor==null or actor==reviver or not actor.is_downed(): continue
        var d2:=reviver.global_position.distance_squared_to(actor.global_position)
        if d2<=best_d2:
            best_d2=d2
            best=actor
    return best

func _reset_revive_state() -> void:
    if _reviver!=null or _revive_target!=null or _revive_elapsed>0.0:
        var target_name:=_revive_target.display_name if is_instance_valid(_revive_target) else ""
        revive_state_changed.emit(false,target_name,0.0)
    _clear_revive_state_without_signal()

func _clear_revive_state_without_signal() -> void:
    _reviver=null
    _revive_target=null
    _revive_elapsed=0.0

func _on_operator_downed(actor: OperatorActor) -> void:
    if _reviver==actor:
        _reset_revive_state()
    if active_index<operators.size() and operators[active_index]==actor:
        for i in range(operators.size()):
            if not operators[i].is_downed():
                request_control(i)
                return

func _update_formation() -> void:
    var active:=get_active_operator()
    if active==null: return
    var aim:=active.aim_world.normalized() if active.aim_world.length_squared()>0.001 else Vector2.RIGHT
    var side:=Vector2(-aim.y,aim.x)
    var rear:=-aim
    var slots: Array[Vector2] = [
        active.global_position,
        active.global_position+rear*82.0+side*72.0,
        active.global_position+rear*118.0-side*48.0
    ]
    var follower_slot:=1
    for i in range(operators.size()):
        if i==active_index or operators[i].is_downed(): continue
        operators[i].set_ai_goal(slots[mini(follower_slot,slots.size()-1)])
        follower_slot+=1

func debug_set_energy(value: float) -> void:
    squad_energy=clampf(value,0.0,MAX_ENERGY)
    _last_energy_reason="DEBUG"
    energy_changed.emit(squad_energy,MAX_ENERGY)

func debug_energy_contract() -> Dictionary:
    return {
        "current":squad_energy,
        "maximum":MAX_ENERGY,
        "ultimate_ready":squad_energy>=MAX_ENERGY-0.001,
        "last_reason":_last_energy_reason,
        "run_energy_gain_multiplier":run_energy_gain_multiplier
    }

func debug_step_revive(delta: float, interact_held: bool) -> void:
    _update_revive(delta,interact_held)

func debug_revive_contract() -> Dictionary:
    return {
        "active":is_reviving(),
        "reviver_id":_reviver.operator_id if is_instance_valid(_reviver) else "",
        "target_id":_revive_target.operator_id if is_instance_valid(_revive_target) else "",
        "elapsed":_revive_elapsed,
        "progress":clampf(_revive_elapsed/REVIVE_DURATION,0.0,1.0),
        "range":REVIVE_RANGE,
        "duration":REVIVE_DURATION,
        "health_ratio":REVIVE_HEALTH_RATIO,
        "guard_duration":REVIVE_GUARD_DURATION,
        "guard_reduction":REVIVE_GUARD_REDUCTION,
        "completed_revives":_completed_revives,
        "last_revived_operator_id":_last_revived_operator_id
    }

func debug_has_revivable_target_in_range() -> bool:
    return has_revivable_target_in_range()

func debug_formation_contract() -> Dictionary:
    return {
        "rear_a":82.0,
        "rear_b":118.0,
        "side_a":72.0,
        "side_b":48.0,
        "compact":false,
        "m7_echelon":true,
        "open_aim_lane":true
    }
