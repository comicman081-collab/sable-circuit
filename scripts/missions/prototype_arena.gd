extends Node2D
class_name PrototypeArena

var squad: SquadController
var camera: Camera2D

func _ready() -> void:
    add_to_group("prototype_arena")
    squad = $SquadController as SquadController
    camera = $Camera2D as Camera2D
    queue_redraw()

func _process(delta: float) -> void:
    if squad == null or camera == null:
        return
    var active := squad.get_active_operator()
    if active:
        camera.global_position = camera.global_position.lerp(active.global_position, 1.0 - pow(0.0004, delta))

func _draw() -> void:
    draw_rect(Rect2(55, 75, 1170, 600), Color("111820"), true)
    draw_rect(Rect2(70, 90, 1140, 570), Color("18232c"), true)
    for x in range(90, 1210, 64):
        draw_line(Vector2(x, 100), Vector2(x, 650), Color(0.18, 0.25, 0.31, 0.35), 1.0)
    for y in range(110, 660, 64):
        draw_line(Vector2(80, y), Vector2(1200, y), Color(0.18, 0.25, 0.31, 0.35), 1.0)
    for rect in [Rect2(610, 220, 120, 36), Rect2(740, 470, 160, 36), Rect2(250, 200, 110, 36)]:
        draw_rect(rect, Color("2b3944"), true)
        draw_rect(rect.grow(-4), Color("344754"), false, 2.0)
