extends Node2D
class_name EnemyOverheadUI

var actor: EnemyActor
var _phase := 0.0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    z_index = 60
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    if actor == null:
        return
    var ratio := clampf(actor.health/maxf(1.0,actor.max_health),0.0,1.0)
    var boss := "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id
    var drone := "DRONE" in actor.enemy_id
    var width := 152.0 if boss else 68.0
    var y := -248.0 if boss else (-112.0 if drone else -94.0)
    var accent := _accent()

    # Backplate + thin luminous outline.
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(0.015,0.022,0.028,0.88),true)
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(accent.r,accent.g,accent.b,0.24),false,1.0)
    draw_rect(Rect2(-width*0.5,y,width,4.0),Color("182329"),true)

    # Segmented health fill.
    var segments := 12 if boss else 6
    var segment_w := (width-float(segments-1)*2.0)/float(segments)
    for i in range(segments):
        var threshold := float(i)/float(segments)
        var filled := ratio > threshold
        var x := -width*0.5 + float(i)*(segment_w+2.0)
        draw_rect(Rect2(x,y,segment_w,4.0),Color(accent,0.95 if filled else 0.12),true)

    # Small threat chevron. Boss gets a phase-reactive double marker.
    var pulse := 0.72 + sin(_phase*4.0)*0.16
    var marker_y := y-10.0
    var pts := PackedVector2Array([Vector2(-6,marker_y),Vector2(6,marker_y),Vector2(0,marker_y+6)])
    draw_colored_polygon(pts,Color(accent.r,accent.g,accent.b,pulse))
    if boss:
        var phase := 1 if ratio>0.66 else (2 if ratio>0.33 else 3)
        if phase>=2:
            draw_arc(Vector2.ZERO,94.0+phase*5.0,-PI*0.82,-PI*0.18,28,Color(accent.r,accent.g,accent.b,0.18+phase*0.06),2.0+phase)

func _accent() -> Color:
    if actor == null: return Color("f05b68")
    if "RIFLE" in actor.enemy_id: return Color("ef6470")
    if "SHIELD" in actor.enemy_id: return Color("e5a94d")
    if "DRONE" in actor.enemy_id: return Color("e45a91")
    if "ABERRANT" in actor.enemy_id: return Color("bd61da")
    if "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id:
        var ratio := actor.health/maxf(1.0,actor.max_health)
        return Color("f0529d") if ratio<=0.33 else Color("9179ff")
    return Color("f05b68")
