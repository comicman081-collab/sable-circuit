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
    lifetime = 0.48 if "BOSS_ANCHOR" in profile_id else (0.36 if "ROOK" in profile_id or "SHIELD" in profile_id else 0.28)
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
        draw_circle(Vector2.ZERO, 5.0 + t * 18.0, Color(tint, fade * 0.7), false, 3.0)

func _draw_aster(t: float, fade: float) -> void:
    var r := 10.0 + 34.0 * t
    for a in [-0.42, 0.0, 0.46]:
        var d := Vector2.RIGHT.rotated(a)
        draw_line(d * 3.0, d * r, Color(tint.lightened(0.25), fade), 3.0)
    draw_circle(Vector2.ZERO, 3.5 + t * 2.0, Color.WHITE, fade)

func _draw_rook(t: float, fade: float) -> void:
    draw_arc(Vector2.ZERO, 8.0 + 40.0 * t, 0.0, TAU, 30, Color(tint, fade * 0.85), 5.0)
    for i in range(5):
        var a := float(i) * TAU / 5.0 + 0.22
        var p := Vector2.RIGHT.rotated(a) * (12.0 + 34.0 * t)
        draw_rect(Rect2(p - Vector2(4, 4), Vector2(8, 8)), Color(tint.darkened(0.22), fade), true)

func _draw_mica(t: float, fade: float) -> void:
    var pts := PackedVector2Array()
    var r := 8.0 + 31.0 * t
    for i in range(6):
        pts.append(Vector2.RIGHT.rotated(float(i) * TAU / 6.0) * r)
    pts.append(pts[0])
    draw_polyline(pts, Color(tint, fade), 3.0)
    draw_arc(Vector2.ZERO, r + 8.0, -1.2 + t, 0.6 + t, 20, Color(tint.lightened(0.25), fade * 0.7), 2.0)

func _draw_rifle(t: float, fade: float) -> void:
    for a in [-0.7, -0.16, 0.46]:
        var d := Vector2.RIGHT.rotated(a)
        draw_line(d * 2.0, d * (11.0 + 26.0 * t), Color("e6eef1", fade), 2.0)
    draw_circle(Vector2(-4, 4), 2.0 + 3.0 * t, Color("b83b45", fade), true)

func _draw_shield(t: float, fade: float) -> void:
    var x := 8.0 + 38.0 * t
    for i in range(4):
        var y := -20.0 + i * 13.0
        draw_line(Vector2(-x * 0.4, y), Vector2(x, y - 7.0), Color("e2a94e", fade * (1.0 - i * 0.1)), 4.0)

func _draw_drone(t: float, fade: float) -> void:
    var r := 8.0 + 28.0 * t
    draw_arc(Vector2.ZERO, r, -1.3, 0.5, 18, Color("65e1e8", fade), 3.0)
    draw_arc(Vector2.ZERO, r + 8.0, 1.5, 3.5, 18, Color("d9577d", fade), 2.0)
    for i in range(3):
        draw_circle(Vector2(-10 + i * 10, 12 + 16 * t), 2.5, Color("65e1e8", fade), true)

func _draw_aberrant(t: float, fade: float) -> void:
    var r := 7.0 + 29.0 * t
    var membrane := PackedVector2Array([
        Vector2(-r, 2), Vector2(-r * 0.45, -r * 0.8), Vector2(r * 0.25, -r * 0.65),
        Vector2(r, 0), Vector2(r * 0.35, r * 0.72), Vector2(-r * 0.5, r * 0.6)
    ])
    draw_polyline(membrane, Color("da6b83", fade), 4.0)
    draw_line(Vector2(-r, 0), Vector2(r * 1.4, -r * 0.35), Color("7f3fa4", fade * 0.8), 3.0)

func _draw_anchor(t: float, fade: float) -> void:
    var r := 14.0 + 58.0 * t
    draw_arc(Vector2.ZERO, r, 0.0, TAU, 42, Color("8572ff", fade), 5.0)
    draw_arc(Vector2.ZERO, r * 0.62, 0.0, TAU, 32, Color("f0529d", fade * 0.9), 4.0)
    for i in range(8):
        var a := float(i) * TAU / 8.0 + t * 0.5
        var d := Vector2.RIGHT.rotated(a)
        draw_line(d * r * 0.45, d * r * 1.35, Color("e7e0ff", fade * 0.7), 2.0)
