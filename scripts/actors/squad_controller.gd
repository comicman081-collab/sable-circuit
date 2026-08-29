extends Node2D
class_name SquadController

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")

var operators: Array[OperatorActor] = []
var active_index := 0
var _key_latch := [false, false, false]

func _ready() -> void:
    add_to_group("squad_controller")
    _spawn_operator("CHR_PROTO_01", "ASTER", Color("69d2ff"), Vector2(410,390))
    _spawn_operator("CHR_PROTO_02", "ROOK", Color("d39a58"), Vector2(330,470))
    _spawn_operator("CHR_PROTO_03", "MICA", Color("62d8c8"), Vector2(485,475))
    request_control(0)

func _process(_delta: float) -> void:
    for i in range(3):
        var pressed:=Input.is_key_pressed(KEY_1+i)
        if pressed and not _key_latch[i]: request_control(i)
        _key_latch[i]=pressed
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

func _on_operator_downed(actor: OperatorActor) -> void:
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
    # M7 combat echelon: one wingman close-rear/high side, the other deeper-rear
    # on the opposite side. This keeps all three readable as a triangular squad
    # while leaving the aim-side of the screen open for hostiles and projectiles.
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
