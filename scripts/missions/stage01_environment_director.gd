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
    for x_i in range(120,2350,330):
        var x: float = float(x_i)
        draw_line(Vector2(x,344),Vector2(x+72,338),Color(0.42,0.61,0.68,0.045),1.5)
        draw_line(Vector2(x+18,522),Vector2(x+84,516),Color(0.42,0.61,0.68,0.035),1.5)

func _glow(center: Vector2, color: Color, radius: float, energy: float = 1.0) -> void:
    for i in range(6,0,-1):
        var f: float = float(i)/6.0
        var alpha: float = 0.009*energy*float(7-i)
        draw_circle(center,radius*f,Color(color.r,color.g,color.b,alpha))

func _draw_outer_gate(c: Vector2) -> void:
    var pulse: float = 0.55+sin(_phase*2.4)*0.22
    draw_arc(c+Vector2(92,-69),17.0,0.0,TAU,28,Color(1.0,0.66,0.25,0.52*pulse),2.2)
    _glow(c+Vector2(92,-69),Color("ff9d3b"),52.0,pulse)

func _draw_decon(c: Vector2) -> void:
    for i in range(9):
        var drift: float = fposmod(_phase*23.0+float(i)*43.0,260.0)
        var p: Vector2 = c+Vector2(-130.0+drift,12.0+sin(_phase*1.25+float(i))*55.0)
        draw_circle(p,13.0+float(i%3)*5.0,Color(0.55,0.94,1.0,0.020))
    _glow(c+Vector2(0,-38),Color("62dff1"),105.0,0.34)

func _draw_archive(c: Vector2) -> void:
    var scan: float = fposmod(_phase*39.0,54.0)
    draw_line(c+Vector2(-51,-20+scan),c+Vector2(51,-20+scan),Color(0.48,1.0,0.92,0.48),1.8)
    draw_arc(c+Vector2(0,1),48.0,-1.1,1.1,24,Color(0.38,0.92,0.84,0.18),1.8)

func _draw_containment(c: Vector2) -> void:
    var alarm: float = 0.20+0.80*maxf(0.0,sin(_phase*4.1))
    draw_arc(c+Vector2(-92,-74),15.0,0.0,TAU,20,Color(1.0,0.32,0.27,0.46*alarm),2.0)
    draw_arc(c+Vector2(92,-74),15.0,0.0,TAU,20,Color(1.0,0.32,0.27,0.46*alarm),2.0)
    _glow(c+Vector2(0,-65),Color("ff5145"),94.0,alarm*0.50)

func _draw_core(c: Vector2) -> void:
    var boss_alive: bool = false
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            boss_alive = true
    var intensity: float = 1.0 if boss_alive else 0.42
    for i in range(4):
        var r: float = 46.0+float(i)*22.0+sin(_phase*(0.8+float(i)*0.07)+float(i))*3.0
        var start: float = _phase*(0.11+float(i)*0.02)
        draw_arc(c,r,start,TAU+start,64,Color(0.56,0.39,1.0,0.12*intensity),2.4)
    _glow(c,Color("946aff"),142.0,0.65*intensity)

func _draw_lift(c: Vector2) -> void:
    var offset: float = fposmod(_phase*17.0,24.0)
    for side_value in [-1.0,1.0]:
        var side: float = float(side_value)
        var x: float = c.x+side*82.0
        for j in range(6):
            var y: float = c.y-66.0+float(j)*24.0+offset
            draw_line(Vector2(x-4,y),Vector2(x+7,y-1),Color(0.42,0.94,0.59,0.52),2.4)

func _draw_supply(c: Vector2) -> void:
    var pulse: float = 0.45+sin(_phase*2.1)*0.18
    var points: Array[Vector2] = [c+Vector2(-72,34),c+Vector2(62,40),c+Vector2(0,-18)]
    for p in points:
        draw_circle(p,4.0,Color(0.90,0.64,0.28,0.48*pulse))
        draw_circle(p,16.0,Color(0.90,0.55,0.18,0.018*pulse))

func _draw_signal_lab(c: Vector2) -> void:
    var points := PackedVector2Array()
    for i in range(45):
        var x: float = -92.0+float(i)*4.2
        var y: float = sin(float(i)*0.58+_phase*3.2)*15.0+sin(float(i)*0.17-_phase)*6.0
        points.append(c+Vector2(x,8+y))
    draw_polyline(points,Color(0.38,0.98,0.89,0.62),2.0)
    for i in range(2):
        var r: float = 34.0+float(i)*20.0
        draw_arc(c+Vector2(0,8),r,-_phase*(0.44+float(i)*0.10),1.45*PI-_phase*(0.44+float(i)*0.10),30,Color(0.35,0.91,0.84,0.16),1.8)

func _draw_ambient_particles() -> void:
    for i in range(24):
        var seed: float = float((i*137)%997)
        var x: float = 72.0+fposmod(seed*2.15+_phase*(3.5+float(i%4)),2300.0)
        var y: float = 300.0+fposmod(seed*0.47+sin(_phase*0.24+float(i))*26.0,260.0)
        draw_circle(Vector2(x,y),1.0+float(i%2),Color(0.44,0.73,0.78,0.065+0.035*float(i%3)))

func debug_room_style_count() -> int:
    return _room_signatures.size()

func debug_room_signatures() -> Array[String]:
    return _room_signatures.duplicate()

func debug_dynamic_overlay_only() -> bool:
    return true
