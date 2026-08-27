extends Node2D
class_name Site7DepthPass

const ROOMS := [
    [Vector2(260,420), Vector2(330,255), Color("d88a32")],
    [Vector2(650,420), Vector2(330,255), Color("58cfe5")],
    [Vector2(1040,420), Vector2(330,255), Color("4de2c8")],
    [Vector2(1430,420), Vector2(330,255), Color("dc6549")],
    [Vector2(1820,420), Vector2(345,270), Color("8f65ee")],
    [Vector2(2210,420), Vector2(330,255), Color("58d889")],
    [Vector2(1040,720), Vector2(285,205), Color("d7953e")],
    [Vector2(1430,720), Vector2(285,205), Color("4adcca")]
]

var _phase: float = 0.0

func _ready() -> void:
    z_index = 0
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    _draw_corridor_depth()
    for row_variant in ROOMS:
        var row: Array = row_variant
        var center: Vector2 = row[0]
        var room_size: Vector2 = row[1]
        var accent: Color = row[2]
        _draw_room_depth(center, room_size, accent)

func _draw_corridor_depth() -> void:
    draw_rect(Rect2(36.0,248.0,2365.0,36.0),Color("04080b"),true)
    draw_rect(Rect2(48.0,257.0,2340.0,18.0),Color("1d2a32"),true)
    draw_line(Vector2(55.0,278.0),Vector2(2380.0,278.0),Color(0.32,0.48,0.56,0.24),2.0)
    draw_rect(Rect2(42.0,548.0,2355.0,44.0),Color(0.0,0.0,0.0,0.48),true)
    draw_rect(Rect2(55.0,548.0,2325.0,19.0),Color("263740"),true)
    for x_i in range(82,2360,86):
        var x: float = float(x_i)
        draw_line(Vector2(x,552.0),Vector2(x+24.0,566.0),Color(0.36,0.51,0.58,0.18),2.0)

func _draw_room_depth(center: Vector2, room_size: Vector2, accent: Color) -> void:
    var half: Vector2 = room_size * 0.5
    var p0: Vector2 = center - half
    var p1: Vector2 = Vector2(center.x + half.x, center.y - half.y)
    var p2: Vector2 = center + half
    var p3: Vector2 = Vector2(center.x - half.x, center.y + half.y)
    var top_depth: Vector2 = Vector2(0.0,-24.0)
    var right_depth: Vector2 = Vector2(22.0,15.0)

    var shadow: PackedVector2Array = PackedVector2Array([
        p0+Vector2(18.0,26.0),p1+Vector2(30.0,26.0),p2+Vector2(32.0,32.0),p3+Vector2(18.0,32.0)
    ])
    draw_colored_polygon(shadow,Color(0.0,0.0,0.0,0.46))

    var top_face: PackedVector2Array = PackedVector2Array([p0+top_depth,p1+top_depth,p1,p0])
    draw_colored_polygon(top_face,Color("334751"))
    draw_line(p0+top_depth+Vector2(10.0,2.0),p1+top_depth-Vector2(10.0,-2.0),Color(accent,0.48),3.0)
    draw_line(p0,p1,Color(0.07,0.10,0.12,0.90),3.0)

    var right_face: PackedVector2Array = PackedVector2Array([p1,p1+right_depth,p2+right_depth,p2])
    draw_colored_polygon(right_face,Color("18262e"))
    draw_line(p1+right_depth,p2+right_depth,Color(0.34,0.49,0.56,0.22),2.0)

    var left_face: PackedVector2Array = PackedVector2Array([p0+top_depth,p0,p3,p3+Vector2(-12.0,10.0)])
    draw_colored_polygon(left_face,Color("253841"))
    draw_rect(Rect2(p3+Vector2(8.0,-6.0),Vector2(room_size.x-16.0,13.0)),Color("2a3d46"),true)
    draw_line(p3+Vector2(18.0,2.0),p2-Vector2(18.0,-2.0),Color(0.38,0.55,0.61,0.16),2.0)

    for side_value in [-1.0,1.0]:
        var side: float = float(side_value)
        var x: float = center.x + side*(half.x-24.0)
        draw_rect(Rect2(x-7.0,p0.y-13.0,14.0,54.0),Color("0c151b"),true)
        draw_rect(Rect2(x-3.0,p0.y-8.0,6.0,32.0),Color(accent.r,accent.g,accent.b,0.34),true)
        draw_circle(Vector2(x,p0.y-12.0),3.5,Color(accent,0.88))

    var inset: Rect2 = Rect2(center-Vector2(room_size.x*0.31,room_size.y*0.25),Vector2(room_size.x*0.62,room_size.y*0.50))
    draw_rect(inset.grow(5.0),Color(0.0,0.0,0.0,0.30),true)
    draw_rect(inset,Color(0.04,0.075,0.095,0.30),true)
    draw_rect(inset,Color(accent.r,accent.g,accent.b,0.13),false,1.5)

    var seam_alpha: float = 0.08 + sin(_phase*0.7+center.x*0.01)*0.015
    for i in range(4):
        var y: float = p0.y + 36.0 + float(i)*46.0
        draw_line(Vector2(p0.x+22.0,y+12.0),Vector2(p1.x-22.0,y-12.0),Color(0.42,0.58,0.64,seam_alpha),1.0)

func debug_room_depth_count() -> int:
    return ROOMS.size()
