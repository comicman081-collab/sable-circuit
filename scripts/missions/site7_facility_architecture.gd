extends Node2D
class_name Site7FacilityArchitecture

var _phase: float = 0.0

const ROOM_CENTERS: Array[Vector2] = [
    Vector2(260,420), Vector2(650,420), Vector2(1040,420), Vector2(1430,420),
    Vector2(1820,420), Vector2(2210,420), Vector2(1040,720), Vector2(1430,720)
]
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
    draw_rect(Rect2(-900,-500,4300,1900), Color("04080c"), true)
    _draw_connected_main_deck()
    _draw_back_wall()
    _draw_foreground_structure()
    _draw_branch_decks()
    _draw_section_frames()
    _draw_room_floor_languages()
    _draw_overhead_services()

func _draw_connected_main_deck() -> void:
    # One continuous facility deck. Story rooms are logical zones on this deck,
    # not eight visible boxes. This matches the target 3/4 facility composition.
    var deck := Rect2(38,286,2375,310)
    draw_rect(deck.grow(44),Color(0,0,0,0.72),true)
    draw_rect(deck.grow(22),Color("101820"),true)
    draw_rect(deck,Color("1a252c"),true)

    # Wide floor lanes / maintenance trenches.
    draw_rect(Rect2(48,312,2352,34),Color("0a1117"),true)
    draw_rect(Rect2(48,520,2352,42),Color("0b1319"),true)
    for x_i in range(70,2390,92):
        var x := float(x_i)
        draw_line(Vector2(x,292),Vector2(x+26,586),Color(0.31,0.44,0.50,0.075),1.0)
    for y in [370.0,446.0,503.0]:
        draw_line(Vector2(55,y),Vector2(2395,y-15.0),Color(0.34,0.47,0.53,0.10),1.0)

    # Recessed grating strips like the target image.
    for start_x in range(120,2300,410):
        var grate := Rect2(float(start_x),462,260,48)
        draw_rect(grate.grow(5),Color(0,0,0,0.28),true)
        draw_rect(grate,Color("0b1217"),true)
        for gx in range(int(grate.position.x)+6,int(grate.end.x)-4,15):
            draw_line(Vector2(float(gx),grate.position.y+4),Vector2(float(gx)+28,grate.end.y-4),Color(0.38,0.52,0.57,0.13),1.0)

    # Floor studs and amber service lights.
    for x_i in range(90,2380,120):
        var x := float(x_i)
        draw_circle(Vector2(x,352+float((x_i/120)%2)*166),2.5,Color("e1a54c"))
        draw_circle(Vector2(x,352+float((x_i/120)%2)*166),9.0,Color(0.95,0.57,0.20,0.025))

func _draw_back_wall() -> void:
    # A single continuous rear wall with repeated structural bays.
    var wall := Rect2(38,170,2375,122)
    draw_rect(wall,Color("111a20"),true)
    draw_rect(Rect2(38,170,2375,18),Color("34434b"),true)
    draw_line(Vector2(55,187),Vector2(2392,187),Color(0.44,0.62,0.68,0.16),2.0)

    for x_i in range(55,2395,92):
        var x := float(x_i)
        draw_rect(Rect2(x,202,66,65),Color("1e2b32"),true)
        draw_rect(Rect2(x+8,211,50,43),Color("172229"),true)
        draw_line(Vector2(x+10,259),Vector2(x+55,259),Color(0.39,0.55,0.61,0.12),2.0)

    # Sector lettering / maintenance stencil shapes.
    for x_i in [245,635,1025,1415,1805,2195]:
        var x := float(x_i)
        draw_line(Vector2(x-56,226),Vector2(x+46,226),Color(0.44,0.56,0.61,0.10),5.0)
        draw_line(Vector2(x-56,238),Vector2(x+8,238),Color(0.44,0.56,0.61,0.07),3.0)

func _draw_foreground_structure() -> void:
    # Near-camera service lip/rail gives depth without enclosing each room.
    draw_rect(Rect2(28,590,2398,25),Color("293941"),true)
    draw_rect(Rect2(28,615,2398,38),Color("070b0e"),true)
    draw_line(Vector2(44,592),Vector2(2405,592),Color(0.42,0.58,0.64,0.18),2.0)
    for x_i in range(65,2390,126):
        var x := float(x_i)
        draw_rect(Rect2(x,598,72,8),Color("0d151a"),true)
        draw_line(Vector2(x+4,601),Vector2(x+68,601),Color(0.54,0.68,0.70,0.08),2.0)

func _draw_branch_decks() -> void:
    # Optional spaces branch from the same deck rather than separate boxes.
    for x_value in [1040.0,1430.0]:
        var x := x_value
        var poly := PackedVector2Array([
            Vector2(x-70,565),Vector2(x+70,565),Vector2(x+118,806),Vector2(x-118,806)
        ])
        draw_colored_polygon(poly,Color("151f25"))
        draw_polyline(PackedVector2Array([poly[0],poly[1],poly[2],poly[3],poly[0]]),Color(0.36,0.50,0.55,0.18),2.0)
        for y_i in range(596,790,34):
            var y := float(y_i)
            var expand := (y-565.0)*0.18
            draw_line(Vector2(x-48-expand,y),Vector2(x+48+expand,y),Color(0.33,0.47,0.51,0.10),1.0)

func _draw_section_frames() -> void:
    # Sparse bulkhead posts signal room transitions while keeping the playfield open.
    for x_value in [435.0,825.0,1215.0,1605.0,1995.0]:
        var x := x_value
        draw_rect(Rect2(x-15,185,11,112),Color("40515a"),true)
        draw_rect(Rect2(x+5,185,11,112),Color("1b272e"),true)
        draw_rect(Rect2(x-15,185,31,10),Color("465b64"),true)
        draw_line(Vector2(x-9,207),Vector2(x-9,269),Color(0.35,0.80,0.87,0.32),2.0)
        draw_circle(Vector2(x+10,212),3.2,Color("d69b4b"))

func _draw_room_floor_languages() -> void:
    for i in range(ROOM_CENTERS.size()):
        var c := ROOM_CENTERS[i]
        var accent := ROOM_ACCENTS[i]
        var optional := i >= 6
        var w := 290.0 if optional else (320.0 if i != 4 else 350.0)
        var h := 170.0 if optional else 205.0
        var plate := Rect2(c-Vector2(w*0.5,h*0.5),Vector2(w,h))
        # Very subtle zone plate; no enclosing wall.
        draw_rect(plate,Color(accent.r*0.08,accent.g*0.08,accent.b*0.08,0.20),true)
        draw_rect(plate,Color(accent.r,accent.g,accent.b,0.10),false,1.5)
        draw_line(Vector2(plate.position.x+20,plate.position.y+6),Vector2(plate.end.x-20,plate.position.y+6),Color(accent.r,accent.g,accent.b,0.34),2.5)
        # Directional floor stencil.
        draw_line(c+Vector2(-54,72),c+Vector2(18,65),Color(accent.r,accent.g,accent.b,0.20),3.0)
        draw_line(c+Vector2(30,64),c+Vector2(60,61),Color(accent.r,accent.g,accent.b,0.10),3.0)
        for p in [plate.position+Vector2(14,14),Vector2(plate.end.x-14,plate.position.y+14)]:
            draw_circle(p,3.0,Color(accent,0.74))

func _draw_overhead_services() -> void:
    for lane in range(3):
        var y := 140.0-float(lane)*13.0
        draw_line(Vector2(58,y),Vector2(2400,y),Color(0.02,0.03,0.04,0.94),8.0-float(lane))
        for x_i in range(110+lane*65,2380,350):
            var x := float(x_i)
            draw_circle(Vector2(x,y),5.0,Color("20333b"))
            draw_circle(Vector2(x,y),2.0,Color(0.36,0.76,0.83,0.25))

func debug_connected_deck() -> bool:
    return true
