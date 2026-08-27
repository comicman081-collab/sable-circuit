extends Control
class_name TacticalMinimap

var stage: StoryStage01
var _route: Array[Vector2] = [
    Vector2(280,470), Vector2(690,350), Vector2(1100,490),
    Vector2(1510,350), Vector2(1920,490), Vector2(2330,350)
]
var _optional: Array[Vector2] = [Vector2(1100,705),Vector2(1510,705)]

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    queue_redraw()

func bind_stage(value: StoryStage01) -> void:
    stage = value
    queue_redraw()

func _process(_delta: float) -> void:
    queue_redraw()

func _map(world: Vector2) -> Vector2:
    var min_world := Vector2(80,180)
    var max_world := Vector2(2500,800)
    var usable := size-Vector2(24,24)
    return Vector2(12,12)+(world-min_world)/(max_world-min_world)*usable

func _room_poly(center: Vector2, half: Vector2) -> PackedVector2Array:
    return PackedVector2Array([
        center+Vector2(-half.x,-half.y*0.72),
        center+Vector2(half.x,-half.y),
        center+Vector2(half.x*0.92,half.y*0.78),
        center+Vector2(-half.x*0.92,half.y)
    ])

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO,size),Color("070c10"),true)
    draw_rect(Rect2(Vector2.ZERO,size),Color("536f7b"),false,1.5)
    var current := stage.current_step if stage else 0

    for i in range(_route.size()-1):
        var a := _map(_route[i])
        var b := _map(_route[i+1])
        draw_line(a,b,Color("263840"),13.0)
        draw_line(a,b,Color("607983"),2.0)

    for i in range(_route.size()):
        var p := _map(_route[i])
        var unlocked := i<=current
        var fill := Color("29434d") if unlocked else Color("151f25")
        if i==current:
            fill = Color("1d5560")
        var poly := _room_poly(p,Vector2(14,9))
        draw_colored_polygon(poly,fill)
        draw_polyline(PackedVector2Array([poly[0],poly[1],poly[2],poly[3],poly[0]]),Color("748c97") if unlocked else Color("314047"),1.4)
        if i==current:
            draw_arc(p,12.5,0.0,TAU,24,Color(0.36,0.93,1.0,0.58),2.0)

    for branch_i in range(_optional.size()):
        var main_i := branch_i+2
        var a := _map(_route[main_i])
        var p := _map(_optional[branch_i])
        draw_line(a,p,Color("2d454f"),8.0)
        var poly := _room_poly(p,Vector2(11,7))
        draw_colored_polygon(poly,Color("403323"))
        draw_polyline(PackedVector2Array([poly[0],poly[1],poly[2],poly[3],poly[0]]),Color("d19a50"),1.2)

    if stage and stage.squad:
        var active := stage.squad.get_active_operator()
        if active:
            var p := _map(active.global_position)
            var d := active.aim_world.normalized()
            var side := Vector2(-d.y,d.x)
            draw_colored_polygon(PackedVector2Array([p+d*8.0,p-d*5.0+side*4.5,p-d*5.0-side*4.5]),Color("69e5ef"))
            draw_circle(p,9.0,Color(0.24,0.86,0.92,0.18),false,1.4)

    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            var ep := _map(node.global_position)
            draw_colored_polygon(PackedVector2Array([ep+Vector2(0,-4),ep+Vector2(4,3),ep+Vector2(-4,3)]),Color("f05b68"))

func debug_diagonal_route() -> bool:
    for i in range(_route.size()-1):
        var delta := _route[i+1]-_route[i]
        if absf(delta.y)<80.0:
            return false
    return true
