extends Node2D
class_name CombatHitVFX

var profile_id := "HIT_GENERIC"
var tint := Color.WHITE
var age := 0.0
var lifetime := 0.28
var _seed := 0

func setup(id_value: String, color: Color) -> void:
    profile_id = id_value
    tint = color
    _seed = abs(profile_id.hash())
    lifetime = 0.52 if "BOSS_ANCHOR" in profile_id else (0.40 if "ROOK" in profile_id or "SHIELD" in profile_id else 0.32)
    z_index = 70
    queue_redraw()

func _process(delta: float) -> void:
    age += delta
    if age >= lifetime:
        queue_free()
        return
    queue_redraw()

func _draw() -> void:
    var t := clampf(age / lifetime, 0.0, 1.0)
    var fade := 1.0 - t
    _base_flash(t,fade)
    if "ASTER" in profile_id:
        _draw_aster(t, fade)
    elif "ROOK" in profile_id:
        _draw_rook(t, fade)
    elif "MICA" in profile_id:
        _draw_mica(t, fade)
    elif "RIFLE" in profile_id:
        _draw_rifle(t, fade)
    elif "SHIELD" in profile_id:
        _draw_shield(t, fade)
    elif "DRONE" in profile_id:
        _draw_drone(t, fade)
    elif "ABERRANT" in profile_id:
        _draw_aberrant(t, fade)
    elif "BOSS_ANCHOR" in profile_id or "ANCHOR" in profile_id:
        _draw_anchor(t, fade)
    else:
        draw_circle(Vector2.ZERO, 5.0 + t * 24.0, Color(tint, fade * 0.7), false, 3.0)

func _base_flash(t: float, fade: float) -> void:
    var r := 8.0 + t*18.0
    draw_circle(Vector2.ZERO,r,Color(tint.r,tint.g,tint.b,0.055*fade),true)
    draw_circle(Vector2.ZERO,maxf(1.0,4.5*(1.0-t)),Color(1,1,1,0.85*fade),true)

func _draw_aster(t: float, fade: float) -> void:
    var r := 12.0 + 46.0 * t
    for a in [-0.62,-0.28,0.0,0.31,0.66]:
        var d := Vector2.RIGHT.rotated(a)
        draw_line(d * 3.0, d * r, Color(tint.lightened(0.28), fade), 2.6)
    draw_arc(Vector2.ZERO,10.0+20.0*t,-1.2,1.2,20,Color("ffcf70",fade*0.75),2.0)

func _draw_rook(t: float, fade: float) -> void:
    draw_arc(Vector2.ZERO, 10.0 + 52.0 * t, 0.0, TAU, 36, Color("d39a58", fade * 0.82), 6.0)
    draw_arc(Vector2.ZERO, 6.0 + 34.0 * t, 0.0, TAU, 30, Color("ffe0ad", fade * 0.42), 3.0)
    for i in range(7):
        var a := float(i) * TAU / 7.0 + 0.18
        var p := Vector2.RIGHT.rotated(a) * (14.0 + 45.0 * t)
        draw_rect(Rect2(p - Vector2(4, 4), Vector2(8, 8)), Color("a56f3d", fade), true)

func _draw_mica(t: float, fade: float) -> void:
    var pts := PackedVector2Array()
    var r := 9.0 + 38.0 * t
    for i in range(6):
        pts.append(Vector2.RIGHT.rotated(float(i) * TAU / 6.0) * r)
    pts.append(pts[0])
    draw_polyline(pts, Color("62d8c8", fade), 3.0)
    draw_arc(Vector2.ZERO, r + 11.0, -1.2 + t*1.4, 0.9 + t*1.4, 24, Color("a3fff2", fade * 0.7), 2.2)
    for i in range(3):
        var a := -0.6 + float(i)*0.6
        draw_circle(Vector2.RIGHT.rotated(a)*(12.0+t*42.0),2.0,Color("e7fff9",fade*0.8),true)

func _draw_rifle(t: float, fade: float) -> void:
    for a in [-0.86,-0.42,-0.08,0.34,0.72]:
        var d := Vector2.RIGHT.rotated(a)
        draw_line(d * 2.0, d * (13.0 + 34.0 * t), Color("f0f5f7", fade), 1.8)
    draw_circle(Vector2(-4, 4), 3.0 + 5.0 * t, Color("d84d59", fade), true)

func _draw_shield(t: float, fade: float) -> void:
    var x := 10.0 + 48.0 * t
    for i in range(5):
        var y := -25.0 + i * 12.0
        draw_line(Vector2(-x * 0.5, y), Vector2(x, y - 8.0), Color("e2a94e", fade * (1.0 - i * 0.08)), 4.0)
    draw_arc(Vector2.ZERO,14.0+38.0*t,-1.0,1.0,20,Color("fff0b2",fade*0.55),3.0)

func _draw_drone(t: float, fade: float) -> void:
    var r := 10.0 + 35.0 * t
    draw_arc(Vector2.ZERO, r, -1.5+t*1.8, 0.6+t*1.8, 22, Color("65e1e8", fade), 3.2)
    draw_arc(Vector2.ZERO, r + 10.0, 1.5-t*1.4, 3.8-t*1.4, 22, Color("e45a91", fade), 2.2)
    for i in range(4):
        draw_circle(Vector2(-15 + i * 10, 14 + 18 * t), 2.8, Color("65e1e8", fade), true)

func _draw_aberrant(t: float, fade: float) -> void:
    var r := 9.0 + 38.0 * t
    var membrane := PackedVector2Array([
        Vector2(-r, 2), Vector2(-r * 0.45, -r * 0.8), Vector2(r * 0.25, -r * 0.65),
        Vector2(r, 0), Vector2(r * 0.35, r * 0.72), Vector2(-r * 0.5, r * 0.6), Vector2(-r,2)
    ])
    draw_polyline(membrane, Color("ef7898", fade), 4.0)
    draw_line(Vector2(-r, 0), Vector2(r * 1.55, -r * 0.35), Color("934eb4", fade * 0.85), 3.4)
    for i in range(4):
        var a := float(i)*1.5+t
        draw_circle(Vector2.RIGHT.rotated(a)*(10.0+r*0.7),2.4,Color("d95f87",fade),true)

func _draw_anchor(t: float, fade: float) -> void:
    var r := 16.0 + 72.0 * t
    draw_arc(Vector2.ZERO, r, 0.0, TAU, 48, Color("9179ff", fade), 6.0)
    draw_arc(Vector2.ZERO, r * 0.62, 0.0, TAU, 38, Color("f0529d", fade * 0.9), 4.5)
    draw_arc(Vector2.ZERO, r*1.22,-age*4.0,PI*1.55-age*4.0,40,Color("e7e0ff",fade*0.34),2.0)
    for i in range(10):
        var a := float(i) * TAU / 10.0 + t * 0.55
        var d := Vector2.RIGHT.rotated(a)
        draw_line(d * r * 0.42, d * r * 1.45, Color("f4eaff", fade * 0.72), 2.2)
