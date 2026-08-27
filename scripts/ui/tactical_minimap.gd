extends Control
class_name TacticalMinimap

var stage: StoryStage01
var _route: Array[Vector2] = [
    Vector2(260,420), Vector2(650,420), Vector2(1040,420),
    Vector2(1430,420), Vector2(1820,420), Vector2(2210,420)
]
var _optional: Array[Vector2] = [Vector2(1040,720),Vector2(1430,720)]

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    queue_redraw()

func bind_stage(value: StoryStage01) -> void:
    stage = value
    queue_redraw()

func _process(_delta: float) -> void:
    queue_redraw()

func _map(world: Vector2) -> Vector2:
    var min_world := Vector2(120,280)
    var max_world := Vector2(2320,800)
    var usable := size-Vector2(20,20)
    return Vector2(10,10)+(world-min_world)/(max_world-min_world)*usable

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO,size),Color("080d12"),true)
    draw_rect(Rect2(Vector2.ZERO,size),Color("496775"),false,1.5)
    # authored route
    for i in range(_route.size()-1):
        draw_line(_map(_route[i]),_map(_route[i+1]),Color("405866"),9.0)
        draw_line(_map(_route[i]),_map(_route[i+1]),Color("748c97"),2.0)
    for branch_i in range(_optional.size()):
        var main_i := branch_i+2
        draw_line(_map(_route[main_i]),_map(_optional[branch_i]),Color("39515c"),6.0)
    var current := stage.current_step if stage else 0
    for i in range(_route.size()):
        var unlocked := i<=current
        var c := Color("70d9e8") if i==current else (Color("718995") if unlocked else Color("2b3941"))
        draw_circle(_map(_route[i]),5.5,c)
        if i==current:
            draw_arc(_map(_route[i]),10.0,0.0,TAU,20,Color(0.38,0.96,1.0,0.45),2.0)
    for p in _optional:
        draw_circle(_map(p),4.2,Color("d99b49"))
    if stage and stage.squad:
        var active := stage.squad.get_active_operator()
        if active:
            var p := _map(active.global_position)
            var d := active.aim_world.normalized()
            var side := Vector2(-d.y,d.x)
            draw_colored_polygon(PackedVector2Array([p+d*8.0,p-d*5.0+side*5.0,p-d*5.0-side*5.0]),Color("69e5ef"))
    # enemy contacts
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            var ep := _map(node.global_position)
            draw_circle(ep,3.2,Color("f05b68"))
