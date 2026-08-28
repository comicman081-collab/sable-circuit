extends Node2D
class_name OperatorSkillVFX

var skill_id := "GENERIC"
var accent := Color.WHITE
var radius := 120.0
var aim := Vector2.RIGHT
var life := 0.62
var max_life := 0.62

func setup(id_value: String, color: Color, radius_value: float, aim_value: Vector2, duration: float = 0.62) -> void:
    skill_id = id_value.to_upper()
    accent = color
    radius = radius_value
    aim = aim_value.normalized() if aim_value.length_squared() > 0.001 else Vector2.RIGHT
    life = duration
    max_life = duration
    z_index = 70
    queue_redraw()

func _process(delta: float) -> void:
    life -= delta
    if life <= 0.0:
        queue_free()
        return
    queue_redraw()

func _draw() -> void:
    var t := clampf(1.0 - life / maxf(0.001, max_life), 0.0, 1.0)
    var fade := 1.0 - t
    if "MICA_PULSE_SCAN" in skill_id:
        draw_arc(Vector2.ZERO, lerpf(26.0,radius,t), 0.0, TAU, 72, Color(accent,0.72*fade), 3.0)
        draw_arc(Vector2.ZERO, lerpf(12.0,radius*0.72,t), 0.0, TAU, 60, Color("cffff7",0.42*fade), 1.5)
        for i in range(6):
            var a := TAU*float(i)/6.0 + t*0.5
            draw_line(Vector2.RIGHT.rotated(a)*22.0,Vector2.RIGHT.rotated(a)*radius*0.78,Color(accent,0.18*fade),1.2)
    elif "ASTER_PRISM" in skill_id:
        var side := aim.rotated(PI*0.5)
        var tip := aim*radius
        draw_colored_polygon(PackedVector2Array([side*18.0,-side*18.0,tip]),Color(accent,0.11*fade))
        draw_line(Vector2.ZERO,tip,Color("effbff",0.82*fade),2.4)
        draw_line(side*18.0,tip,Color(accent,0.42*fade),1.6)
        draw_line(-side*18.0,tip,Color(accent,0.42*fade),1.6)
    elif "ROOK_BREACH_SLAM" in skill_id:
        var start := -0.95
        var finish := 0.95
        draw_arc(Vector2.ZERO,lerpf(28.0,radius,t),start,finish,40,Color(accent,0.78*fade),8.0)
        draw_arc(Vector2.ZERO,lerpf(18.0,radius*0.75,t),start,finish,32,Color("ffe0a4",0.42*fade),2.0)
        for i in range(5):
            var a := lerpf(start,finish,float(i)/4.0)
            draw_line(Vector2.RIGHT.rotated(a)*30.0,Vector2.RIGHT.rotated(a)*radius*0.82,Color(accent,0.22*fade),2.5)
    elif "SENSOR_BLOOM" in skill_id:
        for i in range(3):
            var rr := lerpf(34.0,radius*(0.48+float(i)*0.22),t)
            draw_arc(Vector2.ZERO,rr,0.0,TAU,72,Color(accent,(0.48-float(i)*0.10)*fade),2.3)
        for i in range(8):
            var a := TAU*float(i)/8.0 - t
            var p := Vector2.RIGHT.rotated(a)*radius*0.62
            draw_rect(Rect2(p-Vector2(4,4),Vector2(8,8)),Color(accent,0.38*fade),false,1.5)
    elif "OVERCLOCK" in skill_id:
        for i in range(5):
            var a := TAU*float(i)/5.0 + t*3.0
            draw_line(Vector2.RIGHT.rotated(a)*20.0,Vector2.RIGHT.rotated(a)*(45.0+20.0*t),Color(accent,0.72*fade),3.0)
        draw_arc(Vector2.ZERO,32.0+t*18.0,0.0,TAU,36,Color("fff1a8",0.65*fade),2.0)
    elif "SCATTER_CYCLE" in skill_id:
        for i in range(7):
            var a := -1.1 + 2.2*float(i)/6.0
            draw_line(Vector2.ZERO,Vector2.RIGHT.rotated(a)*lerpf(35.0,radius,t),Color(accent,(0.55-float(i%2)*0.16)*fade),4.0)
        draw_arc(Vector2.ZERO,28.0+t*24.0,-1.3,1.3,40,Color("ffe0aa",0.66*fade),3.0)
    elif "VECTOR_DASH" in skill_id or "RELAY_STEP" in skill_id:
        var side := aim.rotated(PI*0.5)
        for i in range(4):
            var back := -aim*(18.0+float(i)*19.0+t*34.0)
            draw_line(back-side*(10.0+float(i)*2.0),back+side*(10.0+float(i)*2.0),Color(accent,(0.62-float(i)*0.10)*fade),2.5)
    elif "BULWARK" in skill_id:
        var r := 34.0+t*10.0
        draw_arc(Vector2.ZERO,r,-2.65,-0.49,42,Color(accent,0.78*fade),6.0)
        draw_arc(Vector2.ZERO,r+7.0,-2.65,-0.49,42,Color("fff0c8",0.33*fade),2.0)
    else:
        draw_arc(Vector2.ZERO,lerpf(18.0,radius,t),0.0,TAU,48,Color(accent,0.55*fade),2.5)
