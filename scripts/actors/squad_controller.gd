extends Node2D
class_name SquadController

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")

var operators: Array[OperatorActor] = []
var active_index := 0
var _key_latch := [false, false, false]

func _ready() -> void:
    add_to_group("squad_controller")
    _spawn_operator("CHR_PROTO_01", "ASTER", Color("69d2ff"), Vector2(410, 390))
    _spawn_operator("CHR_PROTO_02", "ROOK", Color("ff9d6c"), Vector2(350, 455))
    _spawn_operator("CHR_PROTO_03", "MICA", Color("a8f07a"), Vector2(470, 455))
    request_control(0)

func _process(_delta: float) -> void:
    for i in range(3):
        var pressed := Input.is_key_pressed(KEY_1 + i)
        if pressed and not _key_latch[i]:
            request_control(i)
        _key_latch[i] = pressed
    _update_formation()

func _spawn_operator(id_value: String, label: String, color: Color, pos: Vector2) -> void:
    var actor := OPERATOR_SCENE.instantiate() as OperatorActor
    actor.configure(id_value, label, color)
    actor.global_position = pos
    add_child(actor)
    operators.append(actor)

func request_control(index: int) -> void:
    if index < 0 or index >= operators.size():
        return
    active_index = index
    for i in range(operators.size()):
        operators[i].set_controlled(i == active_index)

func get_active_operator() -> OperatorActor:
    if operators.is_empty():
        return null
    return operators[active_index]

func _update_formation() -> void:
    var active := get_active_operator()
    if active == null:
        return
    var side := Vector2(-active.aim_world.y, active.aim_world.x)
    var rear := -active.aim_world
    var slots := [
        active.global_position,
        active.global_position + rear * 62.0 + side * 58.0,
        active.global_position + rear * 62.0 - side * 58.0,
    ]
    var follower_slot := 1
    for i in range(operators.size()):
        if i == active_index:
            continue
        operators[i].set_ai_goal(slots[follower_slot])
        follower_slot += 1
