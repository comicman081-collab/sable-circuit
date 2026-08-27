extends Node2D
class_name EnemyGroundShadow

var actor: EnemyActor

func _ready() -> void:
    actor = get_parent() as EnemyActor
    z_index = -30
    queue_redraw()

func _process(_delta: float) -> void:
    queue_redraw()

func _draw() -> void:
    if actor == null:
        return
    var boss := "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id
    var drone := "DRONE" in actor.enemy_id
    var rx := 74.0 if boss else (34.0 if "SHIELD" in actor.enemy_id else 26.0)
    var ry := 18.0 if boss else 7.0
    var y := 11.0 if not drone else 20.0
    var alpha := 0.33 if not drone else 0.19
    _ellipse(Vector2(5,y),rx+7.0,ry+4.0,Color(0,0,0,alpha*0.45),32)
    _ellipse(Vector2(5,y),rx,ry,Color(0,0,0,alpha),32)
    if drone:
        _ellipse(Vector2(4,y),rx*0.72,ry*0.72,Color(0.25,0.78,0.86,0.06),28)

func _ellipse(center: Vector2, rx: float, ry: float, color: Color, segments: int) -> void:
    var points := PackedVector2Array()
    for i in range(segments):
        var a := TAU*float(i)/float(segments)
        points.append(center+Vector2(cos(a)*rx,sin(a)*ry))
    draw_colored_polygon(points,color)
