extends Node2D
class_name Site7DepthPass

const ROOMS := [
    Vector2(260,420),Vector2(650,420),Vector2(1040,420),Vector2(1430,420),
    Vector2(1820,420),Vector2(2210,420),Vector2(1040,720),Vector2(1430,720)
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
    # Keep M5/M6 contract names while changing the visual structure from boxed
    # rooms to one connected 3/4-view facility deck.
    var back_shadow := Rect2(30,151,2395,38)
    draw_rect(back_shadow,Color(0,0,0,0.48),true)
    draw_rect(Rect2(38,153,2378,20),Color("293941"),true)
    draw_line(Vector2(52,153),Vector2(2402,153),Color(0.45,0.60,0.65,0.18),2.0)

    # Left/right far structural faces anchor the camera perspective.
    var side_shadow := PackedVector2Array([
        Vector2(18,173),Vector2(42,188),Vector2(42,612),Vector2(18,647)
    ])
    draw_colored_polygon(side_shadow,Color("10181e"))
    draw_line(Vector2(42,188),Vector2(42,612),Color(0.39,0.52,0.57,0.16),2.0)

    var right_face := PackedVector2Array([
        Vector2(2416,173),Vector2(2442,193),Vector2(2442,622),Vector2(2416,596)
    ])
    draw_colored_polygon(right_face,Color("090e12"))

    # Near-camera foreground railing/understructure.
    var foreground_shadow := PackedVector2Array([
        Vector2(20,614),Vector2(2425,614),Vector2(2460,682),Vector2(-10,682)
    ])
    draw_colored_polygon(foreground_shadow,Color(0,0,0,0.58))
    draw_rect(Rect2(28,614,2398,18),Color("33454e"),true)
    for x_i in range(60,2400,104):
        var x := float(x_i)
        draw_line(Vector2(x,632),Vector2(x+28,675),Color(0.22,0.31,0.35,0.26),5.0)
        draw_line(Vector2(x+28,675),Vector2(x+70,632),Color(0.16,0.23,0.27,0.18),3.0)

func _draw_room_depth_markers() -> void:
    # Room identities retain local depth cues (recessed panels / projected shadows)
    # without rebuilding walls around each logical story zone.
    for i in range(ROOMS.size()):
        _draw_room_depth(ROOMS[i], i)

func _draw_room_depth(center: Vector2, index: int) -> void:
    var optional := index >= 6
    var rx := 132.0 if optional else (158.0 if index != 4 else 174.0)
    var ry := 70.0 if optional else 88.0
    var plate_shadow := Rect2(center-Vector2(rx,ry)+Vector2(12,15),Vector2(rx*2.0,ry*2.0))
    draw_rect(plate_shadow,Color(0,0,0,0.18),true)
    # A few diagonal service seams create perspective but never form a box.
    for k in range(4):
        var y := center.y-ry+28.0+float(k)*34.0
        draw_line(Vector2(center.x-rx+18,y+8),Vector2(center.x+rx-18,y-8),Color(0.34,0.48,0.53,0.055),1.0)

func debug_room_depth_count() -> int:
    return ROOMS.size()

func debug_connected_depth() -> bool:
    return true
