extends Node2D
class_name OperatorGroundShadow

var actor: OperatorActor
var _phase := 0.0

func _ready() -> void:
    actor = get_parent() as OperatorActor
    z_index = -30
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    if actor == null:
        return
    var speed_ratio := clampf(actor.velocity.length()/maxf(1.0,actor.run_speed),0.0,1.2)
    var rx := 26.0 + speed_ratio*5.0
    var ry := 7.5 - speed_ratio*1.2
    var offset := Vector2(3.0,8.0) - actor.velocity.normalized()*2.5 if actor.velocity.length_squared()>1.0 else Vector2(3.0,8.0)
    _ellipse(offset,rx+8.0,ry+4.0,Color(0.0,0.0,0.0,0.16),28)
    _ellipse(offset,rx,ry,Color(0.0,0.0,0.0,0.36),28)
    if actor.controlled:
        var pulse := 0.42 + sin(_phase*3.0)*0.08
        _ellipse(offset,rx+6.0,ry+4.0,Color(actor.accent_color.r,actor.accent_color.g,actor.accent_color.b,pulse*0.20),28,false,1.6)

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
