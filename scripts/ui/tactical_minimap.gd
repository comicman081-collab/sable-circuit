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
    var min_world := Vector2(80,250)
    var max_world := Vector2(2360,830)
    var usable := size-Vector2(24,24)
    return Vector2(12,12)+(world-min_world)/(max_world-min_world)*usable

func _room_poly(center: Vector2, half: Vector2) -> PackedVector2Array:
    # Slight trapezoid instead of flat dots; reads like the actual 3/4 floor deck.
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

    # Connected deck silhouette.
    for i in range(_route.size()-1):
        var a := _map(_route[i])
        var b := _map(_route[i+1])
        draw_line(a,b,Color("283941"),15.0)
        draw_line(a,b,Color("536a75"),2.0)

    # Main authored room plates.
    for i in range(_route.size()):
        var p := _map(_route[i])
        var unlocked := i<=current
        var fill := Color("29434d") if unlocked else Color("151f25")
        if i==current:
            fill = Color("1d5560")
        var poly := _room_poly(p,Vector2(15,10))
        draw_colored_polygon(poly,fill)
        draw_polyline(PackedVector2Array([poly[0],poly[1],poly[2],poly[3],poly[0]]),Color("748c97") if unlocked else Color("314047"),1.5)
        if i==current:
            draw_arc(p,13.0,0.0,TAU,24,Color(0.36,0.93,1.0,0.58),2.0)

    # Optional branch silhouettes.
    for branch_i in range(_optional.size()):
        var main_i := branch_i+2
        var a := _map(_route[main_i])
        var p := _map(_optional[branch_i])
        draw_line(a,p,Color("2d454f"),9.0)
        var poly := _room_poly(p,Vector2(12,8))
        draw_colored_polygon(poly,Color("403323"))
        draw_polyline(PackedVector2Array([poly[0],poly[1],poly[2],poly[3],poly[0]]),Color("d19a50"),1.3)

    # Active squad arrow.
    if stage and stage.squad:
        var active := stage.squad.get_active_operator()
        if active:
            var p := _map(active.global_position)
            var d := active.aim_world.normalized()
            var side := Vector2(-d.y,d.x)
            draw_colored_polygon(PackedVector2Array([p+d*9.0,p-d*5.0+side*5.0,p-d*5.0-side*5.0]),Color("69e5ef"))
            draw_circle(p,10.0,Color(0.24,0.86,0.92,0.18),false,1.5)

    # Enemy contacts remain red and spatially mapped.
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            var ep := _map(node.global_position)
            draw_colored_polygon(PackedVector2Array([ep+Vector2(0,-4),ep+Vector2(4,3),ep+Vector2(-4,3)]),Color("f05b68"))
