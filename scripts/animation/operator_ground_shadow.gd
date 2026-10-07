extends Node2D
class_name OperatorGroundShadow
## Contact shadow plus the tactical selection ring painted on the floor plane:
## the controlled operator gets a lit cyan ring with rotating ticks and an aim
## notch; squadmates get a faint ring in their accent colour; downed operators
## a pulsing red ring. Drawn below every actor (see Site7Battlefield depth).

const RING_SQUASH := 0.42
const CONTROL_CYAN := Color(0.25, 0.86, 0.92)
const DOWNED_RED := Color(0.95, 0.35, 0.4)

var actor: OperatorActor
var _phase := 0.0
## What a squadmate's drawing depends on. The controlled or downed ring animates
## with _phase and redraws every frame; a squadmate's is redrawn only when this
## changes (each redraw rebuilds the polygons on the web renderer).
var _drawn_inputs: Array = []

func _ready() -> void:
    actor = get_parent() as OperatorActor
    z_index = -30
    # Foot-anchored presentation size, independent of movement/collision speed.
    var height := float(actor.art_profile.get("motion_lab_display_height_px", 129.6)) if actor else 129.6
    scale = Vector2.ONE * height / 72.0
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    if actor == null or actor.controlled or actor.is_downed() or _drawn_inputs != _inputs():
        queue_redraw()

func _inputs() -> Array:
    return [actor.controlled, actor.is_downed(), _speed_ratio(), actor.accent_color]

func _speed_ratio() -> float:
    return clampf(actor.velocity.length()/maxf(1.0,actor.run_speed),0.0,1.2)

func _draw() -> void:
    if actor == null:
        return
    _drawn_inputs = _inputs()
    var speed_ratio := _speed_ratio()
    var rx := 16.0 + speed_ratio*2.5
    var ry := 4.5 - speed_ratio*0.5
    var offset := Vector2(0.0,1.0)
    _ellipse(offset,rx+8.0,ry+4.0,Color(0.0,0.0,0.0,0.08),28)
    _ellipse(offset,rx,ry,Color(0.0,0.0,0.0,0.23),28)
    _draw_selection_ring(offset)

func _draw_selection_ring(center: Vector2) -> void:
    var ring_rx := 23.0
    var ring_ry := ring_rx * RING_SQUASH
    if actor.is_downed():
        var pulse := 0.5 + 0.5 * sin(_phase * 5.0)
        _ellipse(center, ring_rx, ring_ry, Color(DOWNED_RED, 0.10 + 0.08 * pulse), 40)
        _dashed_ellipse(center, ring_rx, ring_ry, Color(DOWNED_RED, 0.55 + 0.35 * pulse), 12, 1.3, _phase * 0.6)
        return
    var health_ratio := clampf(actor.health / maxf(1.0, actor.max_health), 0.0, 1.0)
    if not actor.controlled:
        # Squadmates: quiet identification ring in their own accent.
        _ellipse(center, ring_rx, ring_ry, Color(actor.accent_color, 0.22), 40, false, 0.8)
        return
    var tint := CONTROL_CYAN if health_ratio > 0.3 else CONTROL_CYAN.lerp(DOWNED_RED, 0.75)
    var breathe := 0.82 + 0.18 * sin(_phase * 2.4)
    # Soft floor glow, crisp inner ring, rotating outer ticks.
    _ellipse(center, ring_rx + 2.0, ring_ry + 1.0, Color(tint, 0.10 * breathe), 40)
    _ellipse(center, ring_rx, ring_ry, Color(tint, 0.85 * breathe), 48, false, 1.25)
    var outer_rx := ring_rx + 4.0
    var outer_ry := outer_rx * RING_SQUASH
    for quadrant in range(4):
        var start := _phase * 0.55 + float(quadrant) * TAU / 4.0
        _arc(center, outer_rx, outer_ry, start, start + 0.62, Color(tint, 0.55 * breathe), 1.0)
    # Aim notch: a small wedge on the outer ring in the aiming direction.
    var aim := actor.aim_world
    if aim.length_squared() > 0.0001:
        var t := atan2(aim.y * outer_rx, aim.x * outer_ry)
        var tip := center + Vector2(cos(t) * (outer_rx + 3.5), sin(t) * (outer_ry + 3.5 * RING_SQUASH))
        var base := center + Vector2(cos(t) * (outer_rx - 1.0), sin(t) * (outer_ry - 1.0 * RING_SQUASH))
        var side := Vector2(-sin(t) * outer_rx, cos(t) * outer_ry).normalized() * 2.4
        draw_colored_polygon(PackedVector2Array([tip, base + side, base - side]), Color(tint, 0.95))

func _ellipse(center: Vector2, rx: float, ry: float, color: Color, segments: int, filled: bool=true, width: float=1.0) -> void:
    var points := PackedVector2Array()
    for i in range(segments+1):
        var a := TAU*float(i)/float(segments)
        points.append(center+Vector2(cos(a)*rx,sin(a)*ry))
    if filled:
        points.remove_at(points.size()-1)
        draw_colored_polygon(points,color)
    else:
        draw_polyline(points,color,width,true)

func _arc(center: Vector2, rx: float, ry: float, from: float, to: float, color: Color, width: float) -> void:
    var points := PackedVector2Array()
    for i in range(9):
        var a := lerpf(from, to, float(i) / 8.0)
        points.append(center + Vector2(cos(a) * rx, sin(a) * ry))
    draw_polyline(points, color, width, true)

func _dashed_ellipse(center: Vector2, rx: float, ry: float, color: Color, dashes: int, width: float, rotation_offset: float) -> void:
    for i in range(dashes):
        var from := rotation_offset + TAU * float(i) / float(dashes)
        _arc(center, rx, ry, from, from + TAU / float(dashes) * 0.55, color, width)

func debug_selection_state() -> String:
    if actor == null: return "none"
    if actor.is_downed(): return "downed"
    return "controlled" if actor.controlled else "squadmate"
