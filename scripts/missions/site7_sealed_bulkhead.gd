extends Node2D
class_name Site7SealedBulkhead
## A closed steel door at an unused opening of the shared Stage 3 room kit.
## The same room plate can be traversed in three orders; its source pixels stay
## untouched while this world-space bulkhead blocks the unused painted apron.

const THICKNESS := 30.0

var _half := Vector2.ZERO
var _height := 100.0

func setup(room_id: String, side: String, first: Vector2, last: Vector2, wall_height: float) -> Site7SealedBulkhead:
    name = "Sealed_%s_%s" % [room_id, side]
    add_to_group("site7_sealed_bulkhead")
    set_meta("room_id", room_id)
    set_meta("side", side)
    position = (first + last) * 0.5
    _half = (last - first) * 0.5
    _height = wall_height
    z_index = 5  # above the plates, below gameplay actors
    var body := StaticBody2D.new()
    body.name = "Barrier"
    body.collision_layer = 1
    body.collision_mask = 0
    var shape := CollisionPolygon2D.new()
    var normal := _half.normalized().orthogonal() * (THICKNESS * 0.5)
    shape.polygon = PackedVector2Array([-_half-normal, _half-normal, _half+normal, -_half+normal])
    body.add_child(shape)
    add_child(body)
    queue_redraw()
    return self

func _draw() -> void:
    var top := Vector2(0.0, -_height)
    var left := -_half
    var right := _half
    var along := right - left
    var shadow := Color(0.025, 0.026, 0.030)
    var frame := Color(0.080, 0.077, 0.080)
    var steel := Color(0.120, 0.117, 0.119)
    var edge := Color(0.205, 0.190, 0.180)
    # Recess the hatch inside the existing illustrated wall, with deep ribs and
    # narrow panels so the closure reads as machinery rather than a flat slab.
    draw_colored_polygon(PackedVector2Array([left+top,right+top,right,left]),shadow)
    for index in range(5):
        var a := left + along * (float(index) / 5.0 + 0.012)
        var b := left + along * (float(index + 1) / 5.0 - 0.012)
        draw_colored_polygon(PackedVector2Array([a+top+Vector2(0,12),b+top+Vector2(0,12),b-Vector2(0,11),a-Vector2(0,11)]),frame)
        var pa := a + along * 0.010
        var pb := b - along * 0.010
        draw_colored_polygon(PackedVector2Array([pa+top+Vector2(0,21),pb+top+Vector2(0,21),pb-Vector2(0,20),pa-Vector2(0,20)]),steel)
        draw_line(pa+top+Vector2(0,22),pb+top+Vector2(0,22),edge,2.0,true)
        draw_line(pa-Vector2(0,22),pb-Vector2(0,22),Color(0.045,0.043,0.047),3.0,true)
        var centre := (a+b)*0.5
        draw_line(centre+top+Vector2(0,34),centre-Vector2(0,32),Color(0.055,0.052,0.057),4.0,true)
        draw_line(centre+top+Vector2(3,35),centre-Vector2(-3,32),Color(0.18,0.17,0.17),1.5,true)
        for height in [29.0, _height-27.0]:
            draw_circle(a+top+Vector2(0,height),2.7,Color(0.29,0.27,0.25))
            draw_circle(b+top+Vector2(0,height),2.7,Color(0.29,0.27,0.25))
    for index in range(1,5):
        var rib := left + along * (float(index)/5.0)
        draw_line(rib+top+Vector2(0,4),rib-Vector2(0,2),shadow,12.0,true)
        draw_line(rib+top+Vector2(3,7),rib-Vector2(-3,5),edge,3.0,true)
    draw_line(left+top,right+top,Color(0.045,0.043,0.044),14.0,true)
    draw_line(left+top+Vector2(0,4),right+top+Vector2(0,4),edge,3.0,true)
    draw_line(left,right,shadow,12.0,true)
    draw_line(left-Vector2(0,5),right-Vector2(0,5),Color(0.15,0.13,0.12),2.0,true)
    var stripe_a := left + along*0.40 + top + Vector2(0,20)
    var stripe_b := left + along*0.60 + top + Vector2(0,20)
    draw_line(stripe_a,stripe_b,Color(0.21,0.095,0.035),8.0,true)
    draw_line(stripe_a+Vector2(0,1),stripe_b+Vector2(0,1),Color(0.48,0.23,0.06),3.0,true)
