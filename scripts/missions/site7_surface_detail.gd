extends Node2D
class_name Site7SurfaceDetail

const ROOMS := [
    [Vector2(280,470),Vector2(350,250),0,Color("d88a32")],
    [Vector2(690,350),Vector2(350,250),1,Color("58cfe5")],
    [Vector2(1100,490),Vector2(350,250),2,Color("4de2c8")],
    [Vector2(1510,350),Vector2(350,250),3,Color("dc6549")],
    [Vector2(1920,490),Vector2(380,270),4,Color("8f65ee")],
    [Vector2(2330,350),Vector2(350,250),5,Color("58d889")],
    [Vector2(1100,705),Vector2(300,205),6,Color("d7953e")],
    [Vector2(1510,705),Vector2(300,205),7,Color("4adcca")]
]

var _phase: float = 0.0

func _ready() -> void:
    z_index = -2
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    for row_variant in ROOMS:
        var row: Array = row_variant
        _draw_room_surface(row[0] as Vector2,row[1] as Vector2,int(row[2]),row[3] as Color)

func _draw_room_surface(center: Vector2, size: Vector2, seed: int, accent: Color) -> void:
    var floor_rect: Rect2 = Rect2(center-size*0.5,size)
    _draw_panel_field(floor_rect,seed,accent)
    _draw_grates(floor_rect,seed)
    _draw_service_trench(floor_rect,seed,accent)
    _draw_rivets(floor_rect,seed)
    _draw_wear(floor_rect,seed)
    _draw_identity_marking(floor_rect,seed,accent)

func _draw_panel_field(rect: Rect2, seed: int, accent: Color) -> void:
    var cols: int = 5 if rect.size.x > 330 else 4
    var rows: int = 4
    var cell_w: float = rect.size.x/float(cols)
    var cell_h: float = rect.size.y/float(rows)
    for y in range(rows):
        for x in range(cols):
            var jitter: float = float(((seed+3)*17+x*13+y*29)%11)-5.0
            var p: Vector2 = rect.position+Vector2(float(x)*cell_w,float(y)*cell_h)
            var panel: Rect2 = Rect2(p+Vector2(4,4),Vector2(cell_w-8,cell_h-8))
            var base: float = 0.065+0.008*float((x+y+seed)%4)
            draw_rect(panel,Color(base,base*1.18,base*1.30,0.42),true)
            draw_line(panel.position+Vector2(7,8+jitter*0.2),Vector2(panel.end.x-7,panel.position.y+5),Color(0.45,0.58,0.63,0.055),1.0)
            draw_line(Vector2(panel.position.x+6,panel.end.y-7),panel.end-Vector2(6,7),Color(0.02,0.03,0.04,0.24),1.0)
            if (x+y+seed)%5==0:
                draw_rect(Rect2(panel.position+Vector2(10,13),Vector2(panel.size.x-20,3)),Color(accent.r,accent.g,accent.b,0.050),true)

func _draw_grates(rect: Rect2, seed: int) -> void:
    var left_side: bool = seed%2==0
    var x: float = rect.position.x+22.0 if left_side else rect.end.x-118.0
    var y: float = rect.end.y-70.0 if seed%3!=0 else rect.position.y+64.0
    var grate: Rect2 = Rect2(x,y,96,50)
    draw_rect(grate.grow(4),Color(0.01,0.015,0.02,0.48),true)
    draw_rect(grate,Color("0c1419"),true)
    for gx in range(int(grate.position.x)+6,int(grate.end.x)-3,9):
        draw_line(Vector2(float(gx),grate.position.y+4),Vector2(float(gx)-13,grate.end.y-4),Color(0.30,0.38,0.42,0.20),2.0)
    for gy in range(int(grate.position.y)+8,int(grate.end.y)-3,11):
        draw_line(Vector2(grate.position.x+4,float(gy)),Vector2(grate.end.x-4,float(gy)),Color(0.07,0.10,0.12,0.55),2.0)

func _draw_service_trench(rect: Rect2, seed: int, accent: Color) -> void:
    var y: float = rect.position.y+rect.size.y*(0.68 if seed%2==0 else 0.31)
    var x0: float = rect.position.x+24.0
    var x1: float = rect.end.x-24.0
    draw_line(Vector2(x0,y),Vector2(x1,y-8),Color(0.015,0.025,0.032,0.62),9.0)
    draw_line(Vector2(x0,y-2),Vector2(x1,y-10),Color(0.25,0.38,0.43,0.14),2.0)
    for i in range(5):
        var t: float = float(i+1)/6.0
        var p: Vector2 = Vector2(lerpf(x0,x1,t),lerpf(y,y-8,t))
        draw_circle(p,2.0,Color(accent.r,accent.g,accent.b,0.32 if (i+seed)%2==0 else 0.12))

func _draw_rivets(rect: Rect2, seed: int) -> void:
    for i in range(20):
        var hx: float = float((i*79+seed*41)%997)/997.0
        var hy: float = float((i*131+seed*61)%991)/991.0
        var p: Vector2 = rect.position+Vector2(12+hx*(rect.size.x-24),12+hy*(rect.size.y-24))
        draw_circle(p,1.4,Color(0.44,0.56,0.60,0.18))

func _draw_wear(rect: Rect2, seed: int) -> void:
    for i in range(7):
        var hx: float = float((i*113+seed*73)%887)/887.0
        var hy: float = float((i*181+seed*37)%881)/881.0
        var center: Vector2 = rect.position+Vector2(30+hx*(rect.size.x-60),24+hy*(rect.size.y-48))
        var angle: float = float((i*47+seed*23)%360)*PI/180.0
        var dir: Vector2 = Vector2.RIGHT.rotated(angle)
        var length: float = 18.0+float((i*17+seed*7)%36)
        draw_line(center-dir*length*0.5,center+dir*length*0.5,Color(0.48,0.54,0.55,0.040),1.0)

func _draw_identity_marking(rect: Rect2, seed: int, accent: Color) -> void:
    var p: Vector2 = rect.position+Vector2(rect.size.x*0.62,rect.size.y*0.74)
    match seed:
        0:
            draw_arc(p,22.0,0,TAU,24,Color(accent.r,accent.g,accent.b,0.18),3.0)
            draw_line(p-Vector2(13,0),p+Vector2(13,0),Color(accent.r,accent.g,accent.b,0.22),2.0)
        1:
            for i in range(3): draw_arc(p,18.0+float(i)*11.0,-1.1,1.1,18,Color(accent.r,accent.g,accent.b,0.10),2.0)
        2:
            draw_rect(Rect2(p-Vector2(28,18),Vector2(56,36)),Color(accent.r,accent.g,accent.b,0.045),false,2.0)
        3:
            for i in range(4): draw_line(p+Vector2(-32+float(i)*18,-18),p+Vector2(-18+float(i)*18,18),Color(accent.r,accent.g,accent.b,0.15),4.0)
        4:
            for i in range(3): draw_arc(p,18.0+float(i)*15.0,_phase*0.05,float(i+1)*1.7+_phase*0.05,28,Color(accent.r,accent.g,accent.b,0.15),2.0)
        5:
            draw_line(p-Vector2(34,0),p+Vector2(34,0),Color(accent.r,accent.g,accent.b,0.18),5.0)
        6:
            draw_rect(Rect2(p-Vector2(32,16),Vector2(64,32)),Color(accent.r,accent.g,accent.b,0.10),false,3.0)
        7:
            var pts := PackedVector2Array()
            for i in range(24):
                var px: float = -38.0+float(i)*3.3
                pts.append(p+Vector2(px,sin(float(i)*0.78+_phase*2.4)*9.0))
            draw_polyline(pts,Color(accent.r,accent.g,accent.b,0.24),2.0)

func debug_surface_count() -> int:
    return ROOMS.size()
