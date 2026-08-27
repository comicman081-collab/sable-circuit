extends Node2D
class_name Site7DepthPass

const ROOMS := [
    [Vector2(260,420), Vector2(350,270), Color("d88a32")],
    [Vector2(650,420), Vector2(350,270), Color("58cfe5")],
    [Vector2(1040,420), Vector2(350,270), Color("4de2c8")],
    [Vector2(1430,420), Vector2(350,270), Color("dc6549")],
    [Vector2(1820,420), Vector2(370,290), Color("8f65ee")],
    [Vector2(2210,420), Vector2(350,270), Color("58d889")],
    [Vector2(1040,720), Vector2(300,220), Color("d7953e")],
    [Vector2(1430,720), Vector2(300,220), Color("4adcca")]
]

var _phase: float = 0.0

func _ready() -> void:
    z_index = -3
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
    # Foreground deck lips and under-structure silhouettes. Kept below actors.
    draw_rect(Rect2(42.0,578.0,2365.0,30.0),Color(0.0,0.0,0.0,0.52),true)
    draw_rect(Rect2(54.0,570.0,2338.0,15.0),Color("25363f"),true)
    for x_i in range(78,2380,92):
        var x: float = float(x_i)
        draw_line(Vector2(x,573.0),Vector2(x+26.0,586.0),Color(0.36,0.52,0.58,0.16),2.0)

func _draw_room_depth(center: Vector2, room_size: Vector2, accent: Color) -> void:
    var half: Vector2 = room_size * 0.5
    var floor_top: float = center.y-half.y
    var floor_bottom: float = center.y+half.y
    var left_x: float = center.x-half.x
    var right_x: float = center.x+half.x

    # Wall cast shadows project down-right onto the deck, selling height without
    # blocking the playable floor.
    var back_shadow := PackedVector2Array([
        Vector2(left_x+14.0,floor_top+8.0),
        Vector2(right_x+10.0,floor_top+8.0),
        Vector2(right_x+42.0,floor_top+44.0),
        Vector2(left_x+42.0,floor_top+44.0)
    ])
    draw_colored_polygon(back_shadow,Color(0.0,0.0,0.0,0.20))

    var side_shadow := PackedVector2Array([
        Vector2(right_x,floor_top+18.0),
        Vector2(right_x+22.0,floor_top+28.0),
        Vector2(right_x+22.0,floor_bottom+12.0),
        Vector2(right_x,floor_bottom)
    ])
    draw_colored_polygon(side_shadow,Color(0.0,0.0,0.0,0.28))

    # Thin luminous kick along the rear wall and edge lights on the floor.
    var pulse: float = 0.54+sin(_phase*1.25+center.x*0.004)*0.08
    draw_line(Vector2(left_x+26.0,floor_top+4.0),Vector2(right_x-26.0,floor_top+4.0),Color(accent.r,accent.g,accent.b,0.15+pulse*0.18),2.0)
    for side in [-1.0,1.0]:
        var x: float = center.x+side*(half.x-20.0)
        draw_circle(Vector2(x,floor_top+26.0),4.5,Color(accent.r,accent.g,accent.b,0.70))
        draw_circle(Vector2(x,floor_top+26.0),22.0,Color(accent.r,accent.g,accent.b,0.018),true)

    # Perspective guide seams on the playable floor.
    var seam_alpha: float = 0.055+sin(_phase*0.55+center.x*0.01)*0.010
    for i in range(4):
        var y: float = floor_top+54.0+float(i)*44.0
        draw_line(Vector2(left_x+26.0,y+12.0),Vector2(right_x-26.0,y-10.0),Color(0.42,0.58,0.64,seam_alpha),1.0)

func debug_room_depth_count() -> int:
    return ROOMS.size()
