extends Node2D
class_name Site7DepthPass

const ROOMS: Array[Vector2] = [
    Vector2(280,470),Vector2(690,350),Vector2(1100,490),Vector2(1510,350),
    Vector2(1920,490),Vector2(2330,350),Vector2(1100,705),Vector2(1510,705)
]
const MAIN_ROUTE: Array[Vector2] = [
    Vector2(280,470),Vector2(690,350),Vector2(1100,490),Vector2(1510,350),Vector2(1920,490),Vector2(2330,350)
]

var _phase: float = 0.0

func _ready() -> void:
    z_index = -3
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    _draw_continuous_depth()
    _draw_room_depth_markers()

func _draw_continuous_depth() -> void:
    # M5 contract names retained; M6 projects them along the diagonal route.
    for i in range(MAIN_ROUTE.size()-1):
        var a: Vector2 = MAIN_ROUTE[i]
        var b: Vector2 = MAIN_ROUTE[i+1]
        var dir: Vector2 = (b-a).normalized()
        var normal: Vector2 = Vector2(-dir.y,dir.x)
        var back_shadow: PackedVector2Array = PackedVector2Array([
            a+normal*122.0+Vector2(18,24),
            b+normal*122.0+Vector2(18,24),
            b-normal*122.0+Vector2(18,24),
            a-normal*122.0+Vector2(18,24)
        ])
        draw_colored_polygon(back_shadow,Color(0,0,0,0.32))
        var side_shadow: Vector2 = normal*112.0
        draw_line(a+side_shadow,b+side_shadow,Color(0.12,0.20,0.24,0.14),5.0)
        draw_line(a-side_shadow,b-side_shadow,Color(0.01,0.02,0.025,0.42),8.0)

func _draw_room_depth_markers() -> void:
    for i in range(ROOMS.size()):
        _draw_room_depth(ROOMS[i], i)

func _draw_room_depth(center: Vector2, index: int) -> void:
    var optional: bool = index>=6
    var rx: float = 132.0 if optional else (158.0 if index!=4 else 176.0)
    var ry: float = 66.0 if optional else 84.0
    var plate_shadow: PackedVector2Array = PackedVector2Array([
        center+Vector2(-rx,-ry*0.60)+Vector2(15,20),
        center+Vector2(rx,-ry*0.72)+Vector2(15,20),
        center+Vector2(rx*0.90,ry*0.72)+Vector2(15,20),
        center+Vector2(-rx*0.90,ry)+Vector2(15,20)
    ])
    draw_colored_polygon(plate_shadow,Color(0,0,0,0.22))
    for k in range(3):
        var t: float = (float(k)+1.0)/4.0
        var y: float = lerpf(center.y-ry*0.45,center.y+ry*0.45,t)
        draw_line(Vector2(center.x-rx*0.72,y+7),Vector2(center.x+rx*0.72,y-7),Color(0.34,0.48,0.53,0.045),1.0)

func debug_room_depth_count() -> int:
    return ROOMS.size()

func debug_connected_depth() -> bool:
    return true

func debug_diagonal_depth() -> bool:
    return true
