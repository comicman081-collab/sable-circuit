extends Control
class_name CinematicFieldOverlay

var _phase := 0.0

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    set_process(true)
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func _draw() -> void:
    var w := size.x
    var h := size.y
    if w <= 1.0 or h <= 1.0:
        return

    # Multi-band vignette. HUD is on a higher CanvasLayer and remains untouched.
    for i in range(10):
        var t := float(i + 1) / 10.0
        var a := 0.010 + t * 0.018
        var inset := float(i) * 15.0
        draw_rect(Rect2(inset,inset,w-inset*2.0,h-inset*2.0),Color(0.0,0.0,0.0,a),false,18.0)

    # Cinematic top/bottom attenuation without letterboxing gameplay.
    for i in range(8):
        var y := float(i) * 7.0
        var a := 0.075 * (1.0 - float(i)/8.0)
        draw_rect(Rect2(0,y,w,7),Color(0,0,0,a),true)
        draw_rect(Rect2(0,h-y-7,w,7),Color(0,0,0,a),true)

    # Faint field scanlines / HUD-integrated texture.
    var pulse := 0.012 + sin(_phase*0.75)*0.003
    for y_i in range(0,int(h),6):
        draw_line(Vector2(0,float(y_i)),Vector2(w,float(y_i)),Color(0.32,0.55,0.62,pulse),1.0)

    # Subtle cool/amber corner blooms echo Site-7 lighting language.
    _soft_disc(Vector2(w*0.08,h*0.82),230.0,Color(0.10,0.55,0.64,0.025))
    _soft_disc(Vector2(w*0.88,h*0.14),210.0,Color(0.86,0.43,0.13,0.018))

func _soft_disc(center: Vector2, radius: float, color: Color) -> void:
    for i in range(7,0,-1):
        var f := float(i)/7.0
        draw_circle(center,radius*f,Color(color.r,color.g,color.b,color.a*(1.0-f*0.72)))
