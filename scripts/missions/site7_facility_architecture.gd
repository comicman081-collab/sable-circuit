extends Node2D
class_name Site7FacilityArchitecture

var _phase: float = 0.0

const MAIN_ROOMS := [
    [Vector2(260,420), Vector2(330,255), Color("d88a32")],
    [Vector2(650,420), Vector2(330,255), Color("58cfe5")],
    [Vector2(1040,420), Vector2(330,255), Color("4de2c8")],
    [Vector2(1430,420), Vector2(330,255), Color("dc6549")],
    [Vector2(1820,420), Vector2(345,270), Color("8f65ee")],
    [Vector2(2210,420), Vector2(330,255), Color("58d889")]
]
const OPTIONAL_ROOMS := [
    [Vector2(1040,720), Vector2(285,205), Color("d7953e")],
    [Vector2(1430,720), Vector2(285,205), Color("4adcca")]
]

func _ready() -> void:
    z_index = 0
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    draw_rect(Rect2(-900,-500,4300,1900), Color("070d12"), true)
    _draw_long_corridor()
    _draw_branch_corridors()
    for row in MAIN_ROOMS:
        _draw_room_shell(row[0], row[1], row[2], false)
    for row in OPTIONAL_ROOMS:
        _draw_room_shell(row[0], row[1], row[2], true)
    _draw_bulkheads()
    _draw_floor_markings()

func _draw_long_corridor() -> void:
    var rect: Rect2 = Rect2(55,292,2325,258)
    draw_rect(rect.grow(22), Color("05090d"), true)
    draw_rect(rect, Color("111b23"), true)
    draw_rect(Rect2(55,365,2325,112), Color("17242d"), true)
    for x_i in range(70,2380,52):
        var x: float = float(x_i)
        draw_line(Vector2(x,365),Vector2(x,477),Color(0.30,0.42,0.49,0.16),1.0)
    for x_i in range(100,2360,210):
        var x: float = float(x_i)
        draw_rect(Rect2(x,374,128,94),Color(0.06,0.10,0.13,0.36),false,2.0)
        draw_line(Vector2(x+12,421),Vector2(x+116,421),Color(0.35,0.52,0.60,0.16),1.0)
    _hazard_strip(Vector2(65,346), Vector2(2300,0), Color("d68a32"), 18)
    _hazard_strip(Vector2(65,496), Vector2(2300,0), Color("527887"), 18)

func _draw_branch_corridors() -> void:
    for x_value in [1040.0,1430.0]:
        var x: float = float(x_value)
        draw_rect(Rect2(x-76,515,152,175),Color("0d171e"),true)
        draw_rect(Rect2(x-54,515,108,175),Color("17242d"),true)
        draw_line(Vector2(x-54,515),Vector2(x-54,690),Color("35515f"),4.0)
        draw_line(Vector2(x+54,515),Vector2(x+54,690),Color("35515f"),4.0)
        for y_i in range(540,680,40):
            draw_line(Vector2(x-42,float(y_i)),Vector2(x+42,float(y_i)),Color(0.25,0.39,0.45,0.18),2.0)

func _draw_room_shell(center: Vector2, size: Vector2, accent: Color, optional: bool) -> void:
    var half: Vector2 = size * 0.5
    var floor_rect: Rect2 = Rect2(center-half,size)
    var shadow_rect: Rect2 = Rect2(floor_rect.position+Vector2(14,18),floor_rect.size).grow(18)
    draw_rect(shadow_rect,Color(0.0,0.0,0.0,0.55),true)
    draw_rect(floor_rect.grow(18),Color("0a1117"),true)
    draw_rect(floor_rect.grow(12),Color("263640"),true)
    draw_rect(floor_rect,Color("121e26") if not optional else Color("142027"),true)
    var top_poly := PackedVector2Array([
        floor_rect.position+Vector2(-12,-12),
        floor_rect.position+Vector2(size.x+12,-12),
        floor_rect.position+Vector2(size.x,0),
        floor_rect.position
    ])
    draw_polygon(top_poly,PackedColorArray([Color("40515a")]))
    var left_poly := PackedVector2Array([
        floor_rect.position+Vector2(-12,-12),
        floor_rect.position,
        floor_rect.position+Vector2(0,size.y),
        floor_rect.position+Vector2(-12,size.y+10)
    ])
    draw_polygon(left_poly,PackedColorArray([Color("263640")]))
    for ix in range(1,4):
        var px: float = floor_rect.position.x + size.x * float(ix)/4.0
        draw_line(Vector2(px,floor_rect.position.y+8),Vector2(px,floor_rect.end.y-8),Color(0.28,0.41,0.48,0.10),1.0)
    for iy in range(1,3):
        var py: float = floor_rect.position.y + size.y * float(iy)/3.0
        draw_line(Vector2(floor_rect.position.x+8,py),Vector2(floor_rect.end.x-8,py),Color(0.28,0.41,0.48,0.10),1.0)
    draw_line(floor_rect.position+Vector2(18,0),floor_rect.position+Vector2(size.x-18,0),Color(accent,0.70),3.0)
    var corners: Array[Vector2] = [
        floor_rect.position+Vector2(14,14),
        Vector2(floor_rect.end.x-14,floor_rect.position.y+14),
        Vector2(floor_rect.position.x+14,floor_rect.end.y-14),
        floor_rect.end-Vector2(14,14)
    ]
    for corner: Vector2 in corners:
        draw_circle(corner,4.0,Color(accent,0.92))
        for radius_value in [9.0,15.0,23.0]:
            var radius: float = float(radius_value)
            draw_circle(corner,radius,Color(accent.r,accent.g,accent.b,0.015),true)
    var plate: Rect2 = Rect2(center-Vector2(size.x*0.29,38),Vector2(size.x*0.58,76))
    draw_rect(plate,Color("0a1218"),true)
    draw_rect(plate,Color(0.35,0.55,0.63,0.18),false,2.0)
    draw_circle(center,8.0,Color(accent,0.50))

func _draw_bulkheads() -> void:
    for x_value in [435.0,825.0,1215.0,1605.0,1995.0]:
        var x: float = float(x_value)
        draw_rect(Rect2(x-16,304,32,234),Color("344650"),true)
        draw_rect(Rect2(x-8,318,16,206),Color("101920"),true)
        for y_value in [338.0,412.0,486.0]:
            var y: float = float(y_value)
            draw_circle(Vector2(x,y),4.0,Color("73d8e7"))
    for lane in range(3):
        var y: float = 260.0-float(lane)*13.0
        draw_line(Vector2(80,y),Vector2(2340,y),Color(0.06,0.09,0.11,0.95),7.0-float(lane))
        for x_i in range(120+lane*70,2320,330):
            draw_circle(Vector2(float(x_i),y),5.0,Color("1c343f"))

func _draw_floor_markings() -> void:
    for x_i in range(140,2300,390):
        var x: float = float(x_i)
        draw_line(Vector2(x,514),Vector2(x+96,514),Color(0.72,0.50,0.20,0.24),3.0)
        draw_line(Vector2(x+108,514),Vector2(x+142,514),Color(0.72,0.50,0.20,0.12),3.0)
    var pulse: float = 0.55+sin(_phase*1.5)*0.12
    for x_value in [260.0,650.0,1040.0,1430.0,1820.0,2210.0]:
        var x: float = float(x_value)
        draw_arc(Vector2(x,420),112.0,0.0,TAU,48,Color(0.22,0.48,0.58,0.06*pulse),2.0)

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
            draw_colored_polygon(PackedVector2Array([a,b,b+normal*8.0,a+normal*8.0]),Color(color,0.38))
