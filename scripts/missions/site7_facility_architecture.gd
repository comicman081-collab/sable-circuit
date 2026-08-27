extends Node2D
class_name Site7FacilityArchitecture

var _phase: float = 0.0

const MAIN_ROOMS := [
    [Vector2(260,420), Vector2(350,270), Color("d88a32")],
    [Vector2(650,420), Vector2(350,270), Color("58cfe5")],
    [Vector2(1040,420), Vector2(350,270), Color("4de2c8")],
    [Vector2(1430,420), Vector2(350,270), Color("dc6549")],
    [Vector2(1820,420), Vector2(370,290), Color("8f65ee")],
    [Vector2(2210,420), Vector2(350,270), Color("58d889")]
]
const OPTIONAL_ROOMS := [
    [Vector2(1040,720), Vector2(300,220), Color("d7953e")],
    [Vector2(1430,720), Vector2(300,220), Color("4adcca")]
]

func _ready() -> void:
    z_index = -4
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    draw_rect(Rect2(-900,-500,4300,1900), Color("05090d"), true)
    _draw_long_corridor()
    _draw_branch_corridors()
    for row in MAIN_ROOMS:
        var center: Vector2 = row[0]
        var size: Vector2 = row[1]
        var accent: Color = row[2]
        _draw_room_shell(center, size, accent, false)
    for row in OPTIONAL_ROOMS:
        var center: Vector2 = row[0]
        var size: Vector2 = row[1]
        var accent: Color = row[2]
        _draw_room_shell(center, size, accent, true)
    _draw_bulkheads()
    _draw_floor_markings()
    _draw_overhead_services()

func _draw_long_corridor() -> void:
    # World-space gameplay deck. The playable space is now read as a floor plane,
    # not a vertical wall panel.
    var deck := Rect2(48,276,2358,306)
    draw_rect(deck.grow(34), Color(0,0,0,0.68), true)
    draw_rect(deck.grow(18), Color("111a21"), true)
    draw_rect(deck, Color("18252d"), true)

    # Long perspective seams and recessed maintenance lanes.
    for y_value in [318.0, 420.0, 528.0]:
        var y: float = y_value
        draw_line(Vector2(58,y),Vector2(2394,y-18.0),Color(0.30,0.43,0.50,0.12),2.0)
    for x_i in range(72,2380,82):
        var x: float = float(x_i)
        draw_line(Vector2(x,286),Vector2(x+26,568),Color(0.28,0.40,0.47,0.07),1.0)

    draw_rect(Rect2(58,298,2334,32),Color("0b1218"),true)
    draw_rect(Rect2(58,532,2334,31),Color("0b1218"),true)
    for x_i in range(80,2380,120):
        var x: float = float(x_i)
        draw_line(Vector2(x,304),Vector2(x+54,304),Color(0.45,0.62,0.68,0.12),3.0)
        draw_line(Vector2(x+18,550),Vector2(x+72,550),Color(0.45,0.62,0.68,0.08),3.0)

    _hazard_strip(Vector2(72,337),Vector2(2300,-14),Color("b97b31"),26)
    _hazard_strip(Vector2(72,505),Vector2(2300,-14),Color("456470"),26)

func _draw_branch_corridors() -> void:
    for x_value in [1040.0,1430.0]:
        var x: float = x_value
        var floor_poly := PackedVector2Array([
            Vector2(x-72,548),Vector2(x+72,548),Vector2(x+105,692),Vector2(x-105,692)
        ])
        draw_colored_polygon(floor_poly,Color("152229"))
        draw_polyline(PackedVector2Array([floor_poly[0],floor_poly[1],floor_poly[2],floor_poly[3],floor_poly[0]]),Color(0.32,0.50,0.57,0.18),2.0)
        for y_i in range(568,684,28):
            var y: float = float(y_i)
            var expand: float = (y-548.0)*0.18
            draw_line(Vector2(x-52-expand,y),Vector2(x+52+expand,y),Color(0.30,0.45,0.51,0.10),1.0)

func _draw_room_shell(center: Vector2, size: Vector2, accent: Color, optional: bool) -> void:
    var half: Vector2 = size * 0.5
    var floor_rect := Rect2(center-half,size)
    var wall_h: float = 62.0 if not optional else 48.0
    var side_w: float = 22.0

    # Deep ambient cast shadow underneath the raised room shell.
    draw_rect(Rect2(floor_rect.position+Vector2(22,24),floor_rect.size).grow(22),Color(0,0,0,0.46),true)

    # Actual floor plane.
    draw_rect(floor_rect,Color("17242c") if not optional else Color("18252b"),true)
    draw_rect(floor_rect,Color(0.31,0.46,0.53,0.16),false,2.0)

    # Back wall vertical face, then its top cap. This is the main 3/4-view depth cue.
    var back_face := Rect2(floor_rect.position+Vector2(0,-wall_h),Vector2(size.x,wall_h))
    draw_rect(back_face,Color("18242c"),true)
    for x_i in range(int(floor_rect.position.x)+14,int(floor_rect.end.x)-10,46):
        var x: float = float(x_i)
        draw_rect(Rect2(x,back_face.position.y+9,31,wall_h-17),Color("202f38"),true)
        draw_line(Vector2(x+4,back_face.end.y-8),Vector2(x+27,back_face.end.y-8),Color(0.42,0.59,0.65,0.12),2.0)
    var cap := PackedVector2Array([
        back_face.position+Vector2(-12,-13),
        Vector2(back_face.end.x+12,back_face.position.y-13),
        back_face.end+Vector2(12,-wall_h),
        back_face.position+Vector2(-12,wall_h)
    ])
    # Simpler top ledge drawn over wall face to avoid confusing the floor silhouette.
    draw_rect(Rect2(back_face.position+Vector2(-10,-14),Vector2(size.x+20,15)),Color("354650"),true)
    draw_line(Vector2(floor_rect.position.x+16,back_face.position.y-13),Vector2(floor_rect.end.x-16,back_face.position.y-13),Color(accent.r,accent.g,accent.b,0.52),3.0)

    # Left/right side wall faces taper toward the front to imply camera elevation.
    var left_face := PackedVector2Array([
        floor_rect.position+Vector2(-side_w,-wall_h),
        floor_rect.position+Vector2(0,-wall_h),
        Vector2(floor_rect.position.x,floor_rect.end.y),
        Vector2(floor_rect.position.x-side_w,floor_rect.end.y+12)
    ])
    var right_face := PackedVector2Array([
        Vector2(floor_rect.end.x,floor_rect.position.y-wall_h),
        Vector2(floor_rect.end.x+side_w,floor_rect.position.y-wall_h+10),
        floor_rect.end+Vector2(side_w,12),
        floor_rect.end
    ])
    draw_colored_polygon(left_face,Color("24343d"))
    draw_colored_polygon(right_face,Color("111b22"))

    # Foreground floor lip and under-shadow; no opaque front wall blocking actors.
    draw_rect(Rect2(floor_rect.position+Vector2(0,size.y-11),Vector2(size.x,12)),Color("31424b"),true)
    draw_rect(Rect2(floor_rect.position+Vector2(8,size.y+1),Vector2(size.x-16,15)),Color(0,0,0,0.34),true)

    # Metallic panel layout with anisotropic perspective seams.
    for ix in range(1,5):
        var px: float = floor_rect.position.x + size.x*float(ix)/5.0
        draw_line(Vector2(px,floor_rect.position.y+8),Vector2(px+15,floor_rect.end.y-20),Color(0.32,0.48,0.54,0.10),1.0)
    for iy in range(1,4):
        var py: float = floor_rect.position.y + size.y*float(iy)/4.0
        draw_line(Vector2(floor_rect.position.x+12,py),Vector2(floor_rect.end.x-12,py-8),Color(0.32,0.48,0.54,0.10),1.0)

    # Recessed central deck/grate.
    var inset := Rect2(center-Vector2(size.x*0.27,size.y*0.20),Vector2(size.x*0.54,size.y*0.40))
    draw_rect(inset.grow(6),Color(0,0,0,0.36),true)
    draw_rect(inset,Color("0e171d"),true)
    for gx in range(int(inset.position.x)+8,int(inset.end.x)-4,18):
        draw_line(Vector2(float(gx),inset.position.y+6),Vector2(float(gx)+22,inset.end.y-6),Color(0.30,0.45,0.51,0.11),1.0)
    draw_rect(inset,Color(accent.r,accent.g,accent.b,0.12),false,1.5)

    # Embedded floor lamps and room accent strips.
    draw_line(floor_rect.position+Vector2(28,7),Vector2(floor_rect.end.x-28,floor_rect.position.y+7),Color(accent.r,accent.g,accent.b,0.46),3.0)
    var lamp_points: Array[Vector2] = [
        floor_rect.position+Vector2(18,22),
        Vector2(floor_rect.end.x-18,floor_rect.position.y+22),
        Vector2(floor_rect.position.x+28,floor_rect.end.y-22),
        floor_rect.end-Vector2(28,22)
    ]
    for lamp in lamp_points:
        draw_circle(lamp,3.8,Color(accent,0.86))
        draw_circle(lamp,13.0,Color(accent.r,accent.g,accent.b,0.025),true)

    # Small industrial props along back wall create scale without obstructing play.
    for prop_x in [-0.34,0.34]:
        var p := center+Vector2(size.x*prop_x,-half.y+24)
        draw_rect(Rect2(p-Vector2(20,14),Vector2(40,28)),Color("263740"),true)
        draw_rect(Rect2(p-Vector2(14,9),Vector2(28,18)),Color("0d171d"),true)
        draw_line(p+Vector2(-9,4),p+Vector2(9,4),Color(accent.r,accent.g,accent.b,0.42),2.0)

func _draw_bulkheads() -> void:
    # Door frames between authored rooms. Open centers keep traversal visually clear.
    for x_value in [435.0,825.0,1215.0,1605.0,1995.0]:
        var x: float = x_value
        draw_rect(Rect2(x-20,280,14,76),Color("3a4c55"),true)
        draw_rect(Rect2(x+6,280,14,76),Color("172229"),true)
        draw_rect(Rect2(x-20,280,40,11),Color("425762"),true)
        draw_line(Vector2(x-13,296),Vector2(x-13,340),Color(0.39,0.78,0.84,0.38),3.0)
        draw_circle(Vector2(x+13,300),3.2,Color("d99849"))

func _draw_floor_markings() -> void:
    var pulse: float = 0.55+sin(_phase*1.5)*0.12
    for x_value in [260.0,650.0,1040.0,1430.0,1820.0,2210.0]:
        var x: float = x_value
        draw_arc(Vector2(x,430),72.0,0.0,TAU,48,Color(0.28,0.62,0.69,0.045*pulse),2.0)
        draw_line(Vector2(x-42,542),Vector2(x+18,538),Color(0.85,0.59,0.24,0.18),3.0)
        draw_line(Vector2(x+30,536),Vector2(x+64,534),Color(0.85,0.59,0.24,0.10),3.0)

func _draw_overhead_services() -> void:
    # Ceiling/service silhouettes are kept near the back wall so the center remains readable.
    for lane in range(3):
        var y: float = 202.0-float(lane)*13.0
        draw_line(Vector2(70,y),Vector2(2385,y),Color(0.025,0.04,0.05,0.94),8.0-float(lane))
        for x_i in range(130+lane*70,2350,360):
            draw_circle(Vector2(float(x_i),y),5.0,Color("203640"))
            draw_circle(Vector2(float(x_i),y),2.0,Color(0.37,0.75,0.82,0.26))

func _hazard_strip(origin: Vector2, span: Vector2, color: Color, segments: int) -> void:
    var length: float = span.length()
    if length <= 0.0:
        return
    var dir: Vector2 = span.normalized()
    var normal: Vector2 = Vector2(-dir.y,dir.x)
    for i in range(segments):
        var t0: float = length*float(i)/float(segments)
        var t1: float = length*float(i+1)/float(segments)
        if i%2==0:
            var a: Vector2 = origin+dir*t0
            var b: Vector2 = origin+dir*t1
            draw_colored_polygon(PackedVector2Array([a,b,b+normal*7.0,a+normal*7.0]),Color(color,0.34))
