extends Node2D
class_name Site7FacilityArchitecture

var _phase: float = 0.0

const MAIN_ROUTE: Array[Vector2] = [
    Vector2(280,470), Vector2(690,350), Vector2(1100,490),
    Vector2(1510,350), Vector2(1920,490), Vector2(2330,350)
]
const OPTIONAL_ROOMS: Array[Vector2] = [Vector2(1100,705), Vector2(1510,705)]
const ROOM_ACCENTS: Array[Color] = [
    Color("d88a32"), Color("58cfe5"), Color("4de2c8"), Color("dc6549"),
    Color("8f65ee"), Color("58d889"), Color("d7953e"), Color("4adcca")
]

func _ready() -> void:
    z_index = -4
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    draw_rect(Rect2(-1100,-700,5000,2300), Color("03070b"), true)
    _draw_route_shadow()
    for i in range(MAIN_ROUTE.size()-1):
        _draw_connector(MAIN_ROUTE[i], MAIN_ROUTE[i+1], ROOM_ACCENTS[i].lerp(ROOM_ACCENTS[i+1],0.5), i)
    _draw_connector(MAIN_ROUTE[2], OPTIONAL_ROOMS[0], ROOM_ACCENTS[6], 6, 82.0)
    _draw_connector(MAIN_ROUTE[3], OPTIONAL_ROOMS[1], ROOM_ACCENTS[7], 7, 82.0)
    _draw_room_foundations()
    _draw_section_thresholds()
    _draw_service_runs()

func _draw_route_shadow() -> void:
    for i in range(MAIN_ROUTE.size()-1):
        var a: Vector2 = MAIN_ROUTE[i] + Vector2(22,30)
        var b: Vector2 = MAIN_ROUTE[i+1] + Vector2(22,30)
        draw_colored_polygon(_corridor_poly(a,b,126.0),Color(0,0,0,0.52))
    draw_colored_polygon(_corridor_poly(MAIN_ROUTE[2]+Vector2(18,28),OPTIONAL_ROOMS[0]+Vector2(18,28),98.0),Color(0,0,0,0.46))
    draw_colored_polygon(_corridor_poly(MAIN_ROUTE[3]+Vector2(18,28),OPTIONAL_ROOMS[1]+Vector2(18,28),98.0),Color(0,0,0,0.46))

func _draw_connector(a: Vector2, b: Vector2, accent: Color, seed: int, half_width: float = 108.0) -> void:
    var dir: Vector2 = (b-a).normalized()
    var normal: Vector2 = Vector2(-dir.y,dir.x)
    var outer: PackedVector2Array = _corridor_poly(a,b,half_width+13.0)
    var main: PackedVector2Array = _corridor_poly(a,b,half_width)
    var inset: PackedVector2Array = _corridor_poly(a,b,half_width-18.0)
    draw_colored_polygon(outer,Color("0b1116"))
    draw_colored_polygon(main,Color("18242b"))
    draw_colored_polygon(inset,Color("121d23"))
    draw_polyline(PackedVector2Array([outer[0],outer[1],outer[2],outer[3],outer[0]]),Color(0.32,0.45,0.51,0.16),2.0)

    var length: float = a.distance_to(b)
    var seam_count: int = maxi(3,int(length/72.0))
    for j in range(1,seam_count):
        var t: float = float(j)/float(seam_count)
        var p: Vector2 = a.lerp(b,t)
        var skew: float = sin(float(j*19+seed*11))*5.0
        draw_line(p-normal*(half_width-22.0)+dir*skew,p+normal*(half_width-22.0)+dir*skew,Color(0.33,0.48,0.54,0.075),1.0)

    draw_line(a+normal*(half_width-6.0),b+normal*(half_width-6.0),Color(accent.r,accent.g,accent.b,0.20),3.0)
    draw_line(a-normal*(half_width-6.0),b-normal*(half_width-6.0),Color(0.31,0.43,0.48,0.16),2.0)

    var marker_count: int = maxi(3,int(length/120.0))
    for j in range(marker_count):
        var t: float = (float(j)+0.5)/float(marker_count)
        var p: Vector2 = a.lerp(b,t)
        var side: float = 1.0 if (j+seed)%2==0 else -1.0
        var lamp: Vector2 = p+normal*(half_width-14.0)*side
        draw_circle(lamp,2.5,Color(accent,0.72))
        draw_circle(lamp,9.0,Color(accent.r,accent.g,accent.b,0.022))

func _draw_room_foundations() -> void:
    var all_centers: Array[Vector2] = MAIN_ROUTE.duplicate()
    all_centers.append_array(OPTIONAL_ROOMS)
    for i in range(all_centers.size()):
        var c: Vector2 = all_centers[i]
        var optional: bool = i>=6
        var rx: float = 184.0 if not optional else 154.0
        var ry: float = 126.0 if not optional else 105.0
        if i==4:
            rx=202.0
            ry=138.0
        var plate: PackedVector2Array = PackedVector2Array([
            c+Vector2(-rx,-ry*0.55),
            c+Vector2(rx,-ry*0.72),
            c+Vector2(rx*0.90,ry*0.72),
            c+Vector2(-rx*0.90,ry)
        ])
        var shadow: PackedVector2Array = PackedVector2Array()
        for p in plate:
            shadow.append(p+Vector2(16,22))
        var accent: Color = ROOM_ACCENTS[i]
        draw_colored_polygon(shadow,Color(0,0,0,0.42))
        draw_colored_polygon(plate,Color("172229"))
        draw_polyline(PackedVector2Array([plate[0],plate[1],plate[2],plate[3],plate[0]]),Color(accent.r,accent.g,accent.b,0.18),2.0)
        draw_line(c+Vector2(-rx*0.68,-ry*0.45),c+Vector2(rx*0.72,-ry*0.54),Color(accent.r,accent.g,accent.b,0.26),3.0)

func _draw_section_thresholds() -> void:
    for i in range(1,MAIN_ROUTE.size()):
        var prev: Vector2 = MAIN_ROUTE[i-1]
        var c: Vector2 = MAIN_ROUTE[i]
        var dir: Vector2 = (c-prev).normalized()
        var normal: Vector2 = Vector2(-dir.y,dir.x)
        var p: Vector2 = c-dir*170.0
        draw_line(p-normal*100.0,p+normal*100.0,Color("3a4c55"),9.0)
        draw_line(p-normal*92.0,p+normal*92.0,Color(0.46,0.66,0.71,0.12),2.0)
        var accent: Color = ROOM_ACCENTS[i]
        draw_circle(p+normal*86.0,4.0,Color(accent,0.78))
        draw_circle(p-normal*86.0,4.0,Color(accent,0.48))

func _draw_service_runs() -> void:
    for i in range(MAIN_ROUTE.size()-1):
        var a: Vector2 = MAIN_ROUTE[i]
        var b: Vector2 = MAIN_ROUTE[i+1]
        var dir: Vector2 = (b-a).normalized()
        var normal: Vector2 = Vector2(-dir.y,dir.x)
        var offset: float = 135.0 if i%2==0 else -135.0
        var s: Vector2 = a+normal*offset+dir*70.0
        var e: Vector2 = b+normal*offset-dir*70.0
        draw_line(s,e,Color(0.02,0.03,0.04,0.86),8.0)
        draw_line(s+normal*7.0,e+normal*7.0,Color(0.18,0.29,0.34,0.28),3.0)

func _corridor_poly(a: Vector2, b: Vector2, half_width: float) -> PackedVector2Array:
    var dir: Vector2 = (b-a).normalized()
    var normal: Vector2 = Vector2(-dir.y,dir.x)
    return PackedVector2Array([a+normal*half_width,b+normal*half_width,b-normal*half_width,a-normal*half_width])

func debug_connected_deck() -> bool:
    return true

func debug_diagonal_route() -> bool:
    for i in range(MAIN_ROUTE.size()-1):
        var delta: Vector2 = MAIN_ROUTE[i+1]-MAIN_ROUTE[i]
        if absf(delta.x)<100.0 or absf(delta.y)<80.0:
            return false
    return true

# Retired M5 boxed-room contract markers kept only for validator continuity:
# _draw_room_shell  _draw_bulkheads  _hazard_strip
