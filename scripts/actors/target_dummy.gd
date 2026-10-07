extends Node2D
class_name PrototypeTargetDummy

signal defeated(target: PrototypeTargetDummy)

@export var max_health := 100.0
@export var reset_on_zero := true
@export var body_color := Color("c8d0d9")
var health := 100.0
var _hit_flash := 0.0

func _ready() -> void:
    health = max_health
    add_to_group("prototype_targets")
    queue_redraw()

func apply_damage(amount: float) -> void:
    health = maxf(0.0, health - amount)
    _hit_flash = 1.0
    if health <= 0.0:
        if reset_on_zero:
            health = max_health
        else:
            remove_from_group("prototype_targets")
            defeated.emit(self)
            queue_free()
            return
    queue_redraw()

func _process(delta: float) -> void:
    _hit_flash = move_toward(_hit_flash, 0.0, delta * 5.0)
    queue_redraw()

func _draw() -> void:
    var body := body_color.lerp(Color("ff756c"), _hit_flash)
    draw_circle(Vector2(0, -25), 16.0, body)
    draw_rect(Rect2(-14, -10, 28, 42), body.darkened(0.20), true)
    draw_line(Vector2(-14, 6), Vector2(-28, 21), body.darkened(0.10), 6.0)
    draw_line(Vector2(14, 6), Vector2(28, 21), body.darkened(0.10), 6.0)
    draw_line(Vector2(-7, 31), Vector2(-10, 48), body.darkened(0.35), 7.0)
    draw_line(Vector2(7, 31), Vector2(10, 48), body.darkened(0.35), 7.0)
    draw_rect(Rect2(-24, -55, 48, 6), Color("26313b"), true)
    draw_rect(Rect2(-23, -54, 46 * (health / max_health), 4), Color("ff6d6d"), true)
