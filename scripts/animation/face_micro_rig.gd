extends Node2D
class_name FaceMicroRig

var identity := "GENERIC"
var facing_sector := 0
var aim_dir := Vector2.RIGHT
var speed_norm := 0.0
var hit_weight := 0.0
var _phase := 0.0
var _seed := 0.0

func configure(identity_value: String) -> void:
    identity = identity_value.to_upper()
    _seed = float(abs(identity.hash()) % 97) * 0.071
    queue_redraw()

func set_state(sector: int, aim: Vector2, speed: float, hit: float, delta: float) -> void:
    facing_sector = sector
    aim_dir = aim.normalized() if aim.length_squared() > 0.001 else Vector2.RIGHT
    speed_norm = speed
    hit_weight = hit
    _phase += delta
    visible = sector not in [5, 6, 7]
    queue_redraw()

func _draw() -> void:
    if not visible:
        return
    var look_x := clampf(aim_dir.x * 1.25, -1.25, 1.25)
    var look_y := clampf(aim_dir.y * 0.55, -0.55, 0.55)
    var blink_wave := absf(sin(_phase * 0.83 + _seed))
    var blink := blink_wave > 0.992
    var eye_y := -2.0
    var eye_gap := 5.2
    var eye_len := 3.4
    var eye_color := Color("18323f")
    var accent := Color("8cecff")
    if "ROOK" in identity:
        eye_color = Color("3e2025")
        accent = Color("ffb06f")
        eye_gap = 5.7
        eye_len = 3.8
    elif "MICA" in identity:
        eye_color = Color("14382f")
        accent = Color("7cf4e7")
        eye_gap = 5.0
        eye_len = 3.1

    var squeeze := 0.25 if blink else 1.0
    draw_line(Vector2(-eye_gap - eye_len * 0.5, eye_y), Vector2(-eye_gap + eye_len * 0.5, eye_y), eye_color, maxf(0.8, 1.35 * squeeze))
    draw_line(Vector2(eye_gap - eye_len * 0.5, eye_y), Vector2(eye_gap + eye_len * 0.5, eye_y), eye_color, maxf(0.8, 1.35 * squeeze))
    if not blink:
        draw_circle(Vector2(-eye_gap + look_x, eye_y + look_y), 0.95, accent)
        draw_circle(Vector2(eye_gap + look_x, eye_y + look_y), 0.95, accent)

    if "ASTER" in identity:
        draw_line(Vector2(-9.0, -6.2), Vector2(-3.0, -5.0), eye_color, 1.0)
        draw_line(Vector2(3.0, -5.0), Vector2(9.0, -6.2), eye_color, 1.0)
    elif "ROOK" in identity:
        draw_line(Vector2(-9.2, -5.0), Vector2(-3.1, -6.4), eye_color, 1.4)
        draw_line(Vector2(3.1, -6.4), Vector2(9.2, -5.0), eye_color, 1.4)
    else:
        draw_arc(Vector2(-5.0, -5.3), 3.4, PI * 1.1, PI * 1.85, 8, eye_color, 0.9)
        draw_arc(Vector2(5.0, -5.3), 3.4, PI * 1.15, PI * 1.9, 8, eye_color, 0.9)

    var mouth_y := 5.0 + hit_weight * 1.6
    if hit_weight > 0.35:
        draw_arc(Vector2(0, mouth_y), 2.6, 0.0, PI, 10, eye_color, 1.0)
    elif "MICA" in identity:
        draw_arc(Vector2(0, mouth_y), 2.2, 0.15, PI - 0.15, 10, eye_color, 0.8)
    else:
        draw_line(Vector2(-2.0, mouth_y), Vector2(2.0, mouth_y), eye_color, 0.9)
