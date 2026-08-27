extends Node2D
class_name Site7SurfaceDetail

const ROOMS := [
    [Vector2(260,420),Vector2(350,270),0,Color("d88a32")],
    [Vector2(650,420),Vector2(350,270),1,Color("58cfe5")],
    [Vector2(1040,420),Vector2(350,270),2,Color("4de2c8")],
    [Vector2(1430,420),Vector2(350,270),3,Color("dc6549")],
    [Vector2(1820,420),Vector2(370,290),4,Color("8f65ee")],
    [Vector2(2210,420),Vector2(350,270),5,Color("58d889")],
    [Vector2(1040,720),Vector2(300,220),6,Color("d7953e")],
    [Vector2(1430,720),Vector2(300,220),7,Color("4adcca")]
]

var _phase := 0.0

func _ready() -> void:
    z_index = -2
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    for row_variant in ROOMS:
        var row: Array = row_variant
        _draw_room_surface(row[0],row[1],int(row[2]),row[3])

func _draw_room_surface(center: Vector2, size: Vector2, seed: int, accent: Color) -> void:
    var floor_rect := Rect2(center-size*0.5,size)
    _draw_panel_field(floor_rect,seed,accent)
    _draw_grates(floor_rect,seed)
    _draw_service_trench(floor_rect,seed,accent)
    _draw_rivets(floor_rect,seed)
    _draw_wear(floor_rect,seed)
    _draw_identity_marking(floor_rect,seed,accent)

func _draw_panel_field(rect: Rect2, seed: int, accent: Color) -> void:
    var cols := 5 if rect.size.x > 330 else 4
    var rows := 4
    var cell_w := rect.size.x/float(cols)
    var cell_h := rect.size.y/float(rows)
    for y in range(rows):
        for x in range(cols):
            var jitter := float(((seed+3)*17+x*13+y*29)%11)-5.0
            var p := rect.position+Vector2(float(x)*cell_w,float(y)*cell_h)
            var panel := Rect2(p+Vector2(4,4),Vector2(cell_w-8,cell_h-8))
            var base := 0.075+0.010*float((x+y+seed)%4)
            draw_rect(panel,Color(base,base*1.18,base*1.30,0.78),true)
            draw_line(panel.position+Vector2(7,8+jitter*0.2),Vector2(panel.end.x-7,panel.position.y+5),Color(0.45,0.58,0.63,0.075),1.0)
            draw_line(Vector2(panel.position.x+6,panel.end.y-7),panel.end-Vector2(6,7),Color(0.02,0.03,0.04,0.35),1.0)
            if (x+y+seed)%5==0:
                draw_rect(Rect2(panel.position+Vector2(10,13),Vector2(panel.size.x-20,4)),Color(accent.r,accent.g,accent.b,0.065),true)

func _draw_grates(rect: Rect2, seed: int) -> void:
    var left_side := seed%2==0
    var x := rect.position.x+22.0 if left_side else rect.end.x-118.0
    var y := rect.end.y-76.0 if seed%3!=0 else rect.position.y+76.0
    var grate := Rect2(x,y,96,54)
    draw_rect(grate.grow(4),Color(0.01,0.015,0.02,0.62),true)
    draw_rect(grate,Color("10191e"),true)
    for gx in range(int(grate.position.x)+6,int(grate.end.x)-3,9):
        draw_line(Vector2(float(gx),grate.position.y+4),Vector2(float(gx)-13,grate.end.y-4),Color(0.30,0.38,0.42,0.26),2.0)
    for gy in range(int(grate.position.y)+8,int(grate.end.y)-3,11):
        draw_line(Vector2(grate.position.x+4,float(gy)),Vector2(grate.end.x-4,float(gy)),Color(0.07,0.10,0.12,0.72),2.0)

func _draw_service_trench(rect: Rect2, seed: int, accent: Color) -> void:
    var y := rect.position.y+rect.size.y*(0.68 if seed%2==0 else 0.31)
    var x0 := rect.position.x+24.0
    var x1 := rect.end.x-24.0
    draw_line(Vector2(x0,y),Vector2(x1,y-8),Color(0.015,0.025,0.032,0.85),11.0)
    draw_line(Vector2(x0,y-2),Vector2(x1,y-10),Color(0.25,0.38,0.43,0.18),2.0)
    for i in range(5):
        var t := float(i+1)/6.0
        var p := Vector2(lerpf(x0,x1,t),lerpf(y,y-8,t))
        draw_circle(p,2.3,Color(accent.r,accent.g,accent.b,0.42 if (i+seed)%2==0 else 0.16))

func _draw_rivets(rect: Rect2, seed: int) -> void:
    for i in range(26):
        var hx := float((i*79+seed*41)%997)/997.0
        var hy := float((i*131+seed*61)%991)/991.0
        var p := rect.position+Vector2(12+hx*(rect.size.x-24),12+hy*(rect.size.y-24))
        draw_circle(p,1.6,Color(0.44,0.56,0.60,0.25))
        draw_circle(p+Vector2(1.3,1.4),1.0,Color(0.0,0.0,0.0,0.36))

func _draw_wear(rect: Rect2, seed: int) -> void:
    for i in range(8):
        var hx := float((i*113+seed*73)%887)/887.0
        var hy := float((i*181+seed*37)%881)/881.0
        var center := rect.position+Vector2(30+hx*(rect.size.x-60),24+hy*(rect.size.y-48))
        var angle := float((i*47+seed*23)%360)*PI/180.0
        var dir := Vector2.RIGHT.rotated(angle)
        var length := 18.0+float((i*17+seed*7)%36)
        draw_line(center-dir*length*0.5,center+dir*length*0.5,Color(0.48,0.54,0.55,0.055),1.0)
        draw_line(center-dir*length*0.33+Vector2(2,2),center+dir*length*0.33+Vector2(2,2),Color(0,0,0,0.10),2.0)

func _draw_identity_marking(rect: Rect2, seed: int, accent: Color) -> void:
    var p := rect.position+Vector2(rect.size.x*0.62,rect.size.y*0.74)
    match seed:
        0:
            draw_arc(p,22.0,0,TAU,24,Color(accent.r,accent.g,accent.b,0.22),3.0)
            draw_line(p-Vector2(13,0),p+Vector2(13,0),Color(accent.r,accent.g,accent.b,0.26),2.0)
        1:
            for i in range(3):
                draw_arc(p,18.0+float(i)*11.0,-1.1,1.1,18,Color(accent.r,accent.g,accent.b,0.12),2.0)
        2:
            draw_rect(Rect2(p-Vector2(28,18),Vector2(56,36)),Color(accent.r,accent.g,accent.b,0.055),false,2.0)
            draw_line(p+Vector2(-23,-8),p+Vector2(23,-8),Color(accent.r,accent.g,accent.b,0.20),2.0)
        3:
            for i in range(4):
                draw_line(p+Vector2(-32+float(i)*18,-18),p+Vector2(-18+float(i)*18,18),Color(accent.r,accent.g,accent.b,0.18),4.0)
        4:
            for i in range(3):
                draw_arc(p,18.0+float(i)*15.0,_phase*0.05,float(i+1)*1.7+_phase*0.05,28,Color(accent.r,accent.g,accent.b,0.18),2.0)
        5:
            draw_line(p-Vector2(34,0),p+Vector2(34,0),Color(accent.r,accent.g,accent.b,0.20),5.0)
            for i in range(5): draw_circle(p+Vector2(-28+float(i)*14,0),2.2,Color(accent.r,accent.g,accent.b,0.42))
        6:
            draw_rect(Rect2(p-Vector2(32,16),Vector2(64,32)),Color(accent.r,accent.g,accent.b,0.12),false,3.0)
        7:
            var pts := PackedVector2Array()
            for i in range(24):
                var x := -38.0+float(i)*3.3
                pts.append(p+Vector2(x,sin(float(i)*0.78+_phase*2.4)*9.0))
            draw_polyline(pts,Color(accent.r,accent.g,accent.b,0.28),2.0)

func debug_surface_count() -> int:
    return ROOMS.size()
