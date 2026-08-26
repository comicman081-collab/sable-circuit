extends Node2D
class_name Stage01EnvironmentDirector

var _phase := 0.0
var _stage: StoryStage01
var _room_signatures := [
    "GATE_RIBS_AMBER_TERMINAL",
    "DECON_CYAN_MIST",
    "ARCHIVE_SHELVES_HOLOGRAM",
    "CONTAINMENT_RED_BARRICADE",
    "CORE_VIOLET_IRIS",
    "LIFT_GREEN_RAILS",
    "SUPPLY_AMBER_CRATES",
    "SIGNAL_TEAL_WAVEFORM"
]

func _ready() -> void:
    _stage = get_parent() as StoryStage01
    z_index = 0
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    _draw_global_floor_detail()
    _draw_outer_gate(Vector2(260,420))
    _draw_decon(Vector2(650,420))
    _draw_archive(Vector2(1040,420))
    _draw_containment(Vector2(1430,420))
    _draw_core(Vector2(1820,420))
    _draw_lift(Vector2(2210,420))
    _draw_supply(Vector2(1040,720))
    _draw_signal_lab(Vector2(1430,720))
    _draw_ambient_particles()

func _draw_global_floor_detail() -> void:
    for x in range(70, 2400, 48):
        var alpha := 0.055 if int(x / 48) % 2 == 0 else 0.035
        draw_line(Vector2(x,105), Vector2(x,845), Color(0.30,0.46,0.54,alpha), 1.0)
    for y in range(115, 840, 48):
        draw_line(Vector2(60,y), Vector2(2400,y), Color(0.28,0.42,0.49,0.035), 1.0)
    for x in range(120, 2350, 270):
        draw_line(Vector2(x,105), Vector2(x+120,105), Color(0.42,0.62,0.70,0.14), 4.0)
        draw_circle(Vector2(x+60,105), 5.0, Color(0.46,0.82,0.90,0.28))
    for x in range(120, 2350, 340):
        var wobble := sin(_phase*0.55 + x*0.01) * 8.0
        draw_bezier(Vector2(x,790),Vector2(x+50,740+wobble),Vector2(x+115,825-wobble),Vector2(x+170,770),Color(0.08,0.13,0.16,0.72),5.0)

func draw_bezier(p0:Vector2,p1:Vector2,p2:Vector2,p3:Vector2,color:Color,width:float) -> void:
    var prev := p0
    for i in range(1,17):
        var t := float(i)/16.0
        var u := 1.0-t
        var p := u*u*u*p0 + 3.0*u*u*t*p1 + 3.0*u*t*t*p2 + t*t*t*p3
        draw_line(prev,p,color,width)
        prev=p

func _glow(center: Vector2, color: Color, radius: float, energy: float=1.0) -> void:
    for i in range(6,0,-1):
        var f := float(i)/6.0
        draw_circle(center, radius*f, Color(color.r,color.g,color.b,0.018*energy*(7-i)))

func _draw_outer_gate(c: Vector2) -> void:
    for i in range(-4,5):
        var x := c.x + i*28.0
        draw_rect(Rect2(x-7,c.y-105,14,205),Color("1d2b33"),true)
        draw_line(Vector2(x,c.y-95),Vector2(x,c.y+90),Color(0.33,0.49,0.56,0.28),2.0)
    var pulse := 0.65+sin(_phase*2.3)*0.25
    draw_rect(Rect2(c+Vector2(-44,-38),Vector2(88,76)),Color("15242c"),true)
    draw_rect(Rect2(c+Vector2(-35,-29),Vector2(70,58)),Color(0.96,0.58,0.18,0.14*pulse),true)
    draw_line(c+Vector2(-22,0),c+Vector2(22,0),Color(1.0,0.70,0.30,pulse),3.0)
    _glow(c,Color("ff9a35"),80,pulse)

func _draw_decon(c: Vector2) -> void:
    for side in [-1.0,1.0]:
        draw_rect(Rect2(c+Vector2(side*120-14,-100),Vector2(28,200)),Color("213944"),true)
        for y in [-70.0,-20.0,30.0,80.0]:
            draw_circle(c+Vector2(side*120,y),5.0,Color("79e8ff"))
    for i in range(6):
        var drift := fposmod(_phase*34.0 + i*47.0,260.0)
        var p := c + Vector2(-125+drift, sin(_phase*1.7+i)*55.0)
        draw_circle(p,18.0+sin(_phase*2.0+i)*5.0,Color(0.55,0.91,0.96,0.035))
    draw_line(c+Vector2(-125,-86),c+Vector2(125,-86),Color(0.38,0.86,0.95,0.45),5.0)
    _glow(c+Vector2(0,-75),Color("66dff5"),110,0.75)

func _draw_archive(c: Vector2) -> void:
    for side in [-1.0,1.0]:
        for row in range(3):
            var r := Rect2(c+Vector2(side*88-32,-88+row*58),Vector2(64,46))
            draw_rect(r,Color("26343b"),true)
            for k in range(4):
                draw_line(r.position+Vector2(8+k*13,8),r.position+Vector2(8+k*13,36),Color(0.36,0.54,0.60,0.32),3.0)
    var scan := fposmod(_phase*52.0,92.0)
    draw_rect(Rect2(c+Vector2(-55,-45),Vector2(110,90)),Color(0.20,0.72,0.78,0.05),true)
    draw_line(c+Vector2(-48,-38+scan),c+Vector2(48,-38+scan),Color(0.45,1.0,0.95,0.55),2.0)
    _glow(c,Color("5df1df"),95,0.65)

func _draw_containment(c: Vector2) -> void:
    for i in range(-4,5):
        var x := c.x+i*31.0
        draw_line(Vector2(x,c.y-105),Vector2(x+20,c.y-70),Color("8a3e35"),7.0)
        draw_line(Vector2(x+20,c.y-70),Vector2(x,c.y-35),Color("3c2928"),7.0)
    for side in [-1.0,1.0]:
        var base := c+Vector2(side*96,48)
        draw_rect(Rect2(base-Vector2(42,15),Vector2(84,30)),Color("343c40"),true)
        draw_line(base+Vector2(-36,-10),base+Vector2(36,10),Color("d96b3e"),5.0)
        draw_line(base+Vector2(-36,10),base+Vector2(36,-10),Color("d96b3e"),5.0)
    var alarm := 0.3+0.7*maxf(0.0,sin(_phase*4.2))
    _glow(c+Vector2(0,-92),Color("ff4e3f"),125,alarm)

func _draw_core(c: Vector2) -> void:
    var boss_alive := false
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            boss_alive = true
    var intensity := 1.0 if boss_alive else 0.45
    for i in range(5):
        var radius := 54.0+i*27.0+sin(_phase*(0.9+i*0.08)+i)*5.0
        draw_arc(c,radius,_phase*(0.10+i*0.025),TAU+_phase*(0.10+i*0.025),72,Color(0.48+0.06*i,0.32,0.95,0.12*intensity),3.0 if i<3 else 2.0)
    for side in [-1.0,1.0]:
        var p := c+Vector2(side*120,0)
        draw_rect(Rect2(p-Vector2(18,95),Vector2(36,190)),Color("202533"),true)
        draw_line(p+Vector2(0,-78),p+Vector2(0,78),Color(0.76,0.34,1.0,0.52*intensity),6.0)
    _glow(c,Color("8e5cff"),180,1.4*intensity)

func _draw_lift(c: Vector2) -> void:
    for side in [-1.0,1.0]:
        var x := c.x+side*100
        draw_rect(Rect2(x-9,c.y-108,18,216),Color("263138"),true)
        for i in range(8):
            var y := c.y-92+i*27+fposmod(_phase*18.0,27.0)
            draw_line(Vector2(x-5,y),Vector2(x+5,y),Color(0.40,0.95,0.58,0.65),3.0)
    draw_rect(Rect2(c-Vector2(72,70),Vector2(144,140)),Color(0.11,0.22,0.19,0.24),true)
    _glow(c,Color("55e68a"),115,0.8)

func _draw_supply(c: Vector2) -> void:
    for i in range(5):
        var p := c+Vector2(-82+(i%3)*72,-46+(i/3)*62)
        draw_rect(Rect2(p,Vector2(58,46)),Color("3b3328"),true)
        draw_rect(Rect2(p+Vector2(4,4),Vector2(50,38)),Color("6a5230"),false,3.0)
        draw_line(p+Vector2(9,23),p+Vector2(49,23),Color("f0a33d"),3.0)
    _glow(c,Color("e7993b"),105,0.45)

func _draw_signal_lab(c: Vector2) -> void:
    draw_rect(Rect2(c-Vector2(112,76),Vector2(224,152)),Color("142a2c"),true)
    var points := PackedVector2Array()
    for i in range(41):
        var x := -94.0+float(i)*4.7
        var y := sin(float(i)*0.62+_phase*3.4)*20.0 + sin(float(i)*0.17-_phase)*9.0
        points.append(c+Vector2(x,y))
    draw_polyline(points,Color(0.36,0.96,0.87,0.72),2.5)
    for i in range(3):
        draw_arc(c,34.0+i*18.0,-_phase*(0.45+i*0.12),PI*1.55-_phase*(0.45+i*0.12),32,Color(0.34,0.89,0.83,0.24),2.0)
    _glow(c,Color("57e7d7"),120,0.55)

func _draw_ambient_particles() -> void:
    for i in range(48):
        var seed := float(i*137 % 997)
        var x := 70.0 + fposmod(seed*2.3 + _phase*(7.0+float(i%5)),2300.0)
        var y := 125.0 + fposmod(seed*0.83 + sin(_phase*0.3+i)*45.0,690.0)
        var a := 0.05+0.04*sin(_phase*0.7+i)
        draw_circle(Vector2(x,y),1.0+float(i%3)*0.6,Color(0.64,0.80,0.86,maxf(0.015,a)))

func debug_room_style_count() -> int:
    return _room_signatures.size()

func debug_room_signatures() -> Array:
    return _room_signatures.duplicate()
