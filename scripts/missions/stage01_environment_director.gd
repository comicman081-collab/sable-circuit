extends Node2D
class_name Stage01EnvironmentDirector

var _phase: float = 0.0
var _stage: StoryStage01
var _room_signatures: Array[String] = [
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
    z_index = -1
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    _draw_global_floor_detail()
    _draw_outer_gate(Vector2(260.0,420.0))
    _draw_decon(Vector2(650.0,420.0))
    _draw_archive(Vector2(1040.0,420.0))
    _draw_containment(Vector2(1430.0,420.0))
    _draw_core(Vector2(1820.0,420.0))
    _draw_lift(Vector2(2210.0,420.0))
    _draw_supply(Vector2(1040.0,720.0))
    _draw_signal_lab(Vector2(1430.0,720.0))
    _draw_ambient_particles()

func _draw_global_floor_detail() -> void:
    # Sparse deck markings only; base architecture now owns the actual floor plane.
    for x_i in range(110,2350,260):
        var x: float = float(x_i)
        draw_line(Vector2(x,333.0),Vector2(x+82.0,326.0),Color(0.42,0.61,0.68,0.08),2.0)
        draw_line(Vector2(x+18.0,506.0),Vector2(x+98.0,499.0),Color(0.42,0.61,0.68,0.055),2.0)
    for x_i in range(140,2320,420):
        var x: float = float(x_i)
        _deck_stencil(Vector2(x,474.0),"A%d" % int(x_i/140))

func _deck_stencil(p: Vector2, text_value: String) -> void:
    # Typography is represented as industrial bars so this presentation does not
    # depend on a world font resource.
    draw_line(p,p+Vector2(34.0,-3.0),Color(0.65,0.48,0.24,0.18),3.0)
    draw_line(p+Vector2(40.0,-4.0),p+Vector2(61.0,-6.0),Color(0.65,0.48,0.24,0.10),3.0)

func _glow(center: Vector2, color: Color, radius: float, energy: float = 1.0) -> void:
    for i in range(6,0,-1):
        var f: float = float(i)/6.0
        var alpha: float = 0.012*energy*float(7-i)
        draw_circle(center,radius*f,Color(color.r,color.g,color.b,alpha))

func _console(p: Vector2, accent: Color, width: float = 66.0) -> void:
    draw_rect(Rect2(p-Vector2(width*0.5,18.0),Vector2(width,36.0)),Color("26353d"),true)
    draw_rect(Rect2(p-Vector2(width*0.5-5.0,12.0),Vector2(width-10.0,24.0)),Color("0a141a"),true)
    draw_line(p+Vector2(-width*0.34,3.0),p+Vector2(width*0.34,-1.0),Color(accent.r,accent.g,accent.b,0.58),2.0)
    draw_circle(p+Vector2(width*0.35,-7.0),3.0,Color(accent,0.84))

func _crate(p: Vector2, accent: Color, size: Vector2 = Vector2(54,40)) -> void:
    draw_rect(Rect2(p-size*0.5,size),Color("29343a"),true)
    draw_rect(Rect2(p-size*0.5+Vector2(4,4),size-Vector2(8,8)),Color("111a20"),false,2.0)
    draw_line(p+Vector2(-size.x*0.35,0),p+Vector2(size.x*0.35,-2),Color(accent.r,accent.g,accent.b,0.52),3.0)
    draw_line(p+Vector2(0,-size.y*0.35),p+Vector2(0,size.y*0.35),Color(0.38,0.49,0.54,0.20),2.0)

func _draw_outer_gate(c: Vector2) -> void:
    # Gate hardware is now concentrated on the rear wall instead of filling the
    # playable floor with vertical bars.
    for i in range(-3,4):
        var x: float = c.x+float(i)*34.0
        draw_rect(Rect2(x-6.0,c.y-126.0,12.0,52.0),Color("2b3940"),true)
        draw_line(Vector2(x,c.y-120.0),Vector2(x+4.0,c.y-82.0),Color(0.46,0.60,0.66,0.22),2.0)
    var pulse: float = 0.66+sin(_phase*2.4)*0.22
    _console(c+Vector2(0,-82),Color("f2a13b"),82.0)
    draw_arc(c+Vector2(0,-82),32.0,0.0,TAU,32,Color(1.0,0.66,0.25,0.28*pulse),3.0)
    _glow(c+Vector2(0,-82),Color("ff9d3b"),70.0,pulse)

func _draw_decon(c: Vector2) -> void:
    # Paired decontamination columns sit against the back corners; mist drifts over
    # the floor plane where the squad actually walks.
    for side in [-1.0,1.0]:
        var p := c+Vector2(side*122.0,-78.0)
        draw_rect(Rect2(p-Vector2(13,31),Vector2(26,62)),Color("233740"),true)
        for j in range(4):
            draw_circle(p+Vector2(0,-20.0+float(j)*14.0),3.5,Color("74e8f6"))
        draw_line(p+Vector2(-9,25),p+Vector2(9,25),Color(0.42,0.85,0.92,0.40),3.0)
    for i in range(8):
        var drift: float = fposmod(_phase*28.0+float(i)*52.0,290.0)
        var p := c+Vector2(-145.0+drift,18.0+sin(_phase*1.3+float(i))*58.0)
        var r: float = 16.0+sin(_phase*1.9+float(i))*5.0
        draw_circle(p,r,Color(0.55,0.94,1.0,0.025))
    draw_line(c+Vector2(-138,-74),c+Vector2(138,-82),Color(0.39,0.86,0.95,0.42),4.0)
    _glow(c+Vector2(0,-56),Color("62dff1"),125.0,0.55)

func _draw_archive(c: Vector2) -> void:
    # Low archive cabinets hug the rear/side edges and leave the center open.
    for side in [-1.0,1.0]:
        for row in range(2):
            var p := c+Vector2(side*118.0,-58.0+float(row)*76.0)
            _crate(p,Color("59e8d4"),Vector2(62,48))
            for slot in range(3):
                draw_line(p+Vector2(-18+float(slot)*18,-13),p+Vector2(-18+float(slot)*18,13),Color(0.38,0.58,0.63,0.25),2.0)
    var holo := c+Vector2(0,-18)
    draw_rect(Rect2(holo-Vector2(54,36),Vector2(108,72)),Color(0.24,0.82,0.78,0.025),true)
    var scan: float = fposmod(_phase*44.0,64.0)
    draw_line(holo+Vector2(-45,-28+scan),holo+Vector2(45,-28+scan),Color(0.48,1.0,0.92,0.52),2.0)
    draw_arc(holo,58.0,-1.2,1.2,24,Color(0.38,0.92,0.84,0.23),2.0)
    _glow(holo,Color("55ead7"),95.0,0.45)

func _draw_containment(c: Vector2) -> void:
    # Red containment braces on the rear wall plus low floor barricades.
    for i in range(-3,4):
        var x: float = c.x+float(i)*40.0
        draw_line(Vector2(x,c.y-118),Vector2(x+22,c.y-92),Color("843b35"),6.0)
        draw_line(Vector2(x+22,c.y-92),Vector2(x,c.y-70),Color("392526"),6.0)
    for side in [-1.0,1.0]:
        var p := c+Vector2(side*92.0,42.0)
        draw_rect(Rect2(p-Vector2(48,10),Vector2(96,20)),Color("313a3f"),true)
        draw_line(p+Vector2(-38,-7),p+Vector2(38,7),Color("de6843"),4.0)
        draw_line(p+Vector2(-38,7),p+Vector2(38,-7),Color("de6843"),4.0)
    var alarm: float = 0.32+0.68*maxf(0.0,sin(_phase*4.1))
    _glow(c+Vector2(0,-82),Color("ff5145"),125.0,alarm)

func _draw_core(c: Vector2) -> void:
    var boss_alive := false
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            boss_alive = true
    var intensity: float = 1.0 if boss_alive else 0.42
    # Core C is a floor iris / containment dais rather than a wall target.
    for i in range(6):
        var r: float = 44.0+float(i)*23.0+sin(_phase*(0.8+float(i)*0.06)+float(i))*4.0
        var start: float = _phase*(0.10+float(i)*0.018)
        draw_arc(c,r,start,TAU+start,72,Color(0.56,0.39,1.0,0.10*intensity),3.0 if i<3 else 2.0)
    for side in [-1.0,1.0]:
        var p := c+Vector2(side*125.0,-48.0)
        draw_rect(Rect2(p-Vector2(13,42),Vector2(26,84)),Color("252836"),true)
        draw_line(p+Vector2(0,-32),p+Vector2(0,32),Color(0.77,0.37,1.0,0.52*intensity),5.0)
    _glow(c,Color("946aff"),175.0,1.0*intensity)

func _draw_lift(c: Vector2) -> void:
    # Parallel floor rails and rear lift console read naturally from above.
    for side in [-1.0,1.0]:
        var x: float = c.x+side*82.0
        draw_line(Vector2(x,c.y-84),Vector2(x+16,c.y+88),Color("2f4147"),10.0)
        for j in range(7):
            var y: float = c.y-70.0+float(j)*24.0+fposmod(_phase*16.0,24.0)
            draw_line(Vector2(x-4,y),Vector2(x+7,y-1),Color(0.42,0.94,0.59,0.62),3.0)
    _console(c+Vector2(0,-85),Color("5ae287"),74.0)
    _glow(c,Color("59e48b"),115.0,0.55)

func _draw_supply(c: Vector2) -> void:
    var positions: Array[Vector2] = [
        Vector2(-92,-46),Vector2(-28,-62),Vector2(74,-42),
        Vector2(-76,34),Vector2(66,42)
    ]
    for offset in positions:
        _crate(c+offset,Color("e3a247"),Vector2(56,42))
    _console(c+Vector2(0,-74),Color("e0a14a"),66.0)
    _glow(c,Color("e59b43"),98.0,0.35)

func _draw_signal_lab(c: Vector2) -> void:
    _console(c+Vector2(0,-72),Color("54e5d5"),94.0)
    var holo_center := c+Vector2(0,5)
    var points := PackedVector2Array()
    for i in range(45):
        var x: float = -94.0+float(i)*4.3
        var y: float = sin(float(i)*0.58+_phase*3.2)*17.0+sin(float(i)*0.17-_phase)*7.0
        points.append(holo_center+Vector2(x,y))
    draw_polyline(points,Color(0.38,0.98,0.89,0.66),2.3)
    for i in range(3):
        var r: float = 30.0+float(i)*18.0
        draw_arc(holo_center,r,-_phase*(0.44+float(i)*0.10),1.55*PI-_phase*(0.44+float(i)*0.10),32,Color(0.35,0.91,0.84,0.20),2.0)
    _glow(holo_center,Color("58e7d8"),112.0,0.45)

func _draw_ambient_particles() -> void:
    for i in range(38):
        var seed: float = float((i*137)%997)
        var x: float = 72.0+fposmod(seed*2.15+_phase*(4.0+float(i%4)),2300.0)
        var y: float = 300.0+fposmod(seed*0.47+sin(_phase*0.24+float(i))*28.0,260.0)
        var alpha: float = 0.08+0.05*float(i%3)
        draw_circle(Vector2(x,y),1.2+float(i%2),Color(0.44,0.73,0.78,alpha))

func debug_room_style_count() -> int:
    return _room_signatures.size()

func debug_room_signatures() -> Array[String]:
    return _room_signatures.duplicate()
