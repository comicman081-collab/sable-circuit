extends Node2D
class_name PrototypeProjectile

var direction := Vector2.RIGHT
var speed := 720.0
var damage := 10.0
var lifetime := 1.1
var owner_actor: Node = null
var tint := Color("fff0a8")

func setup(origin: Vector2, dir: Vector2, source: Node, color: Color) -> void:
    global_position = origin
    direction = dir.normalized() if dir.length_squared() > 0.0 else Vector2.RIGHT
    owner_actor = source
    tint = color
    rotation = direction.angle()
    queue_redraw()

func _physics_process(delta: float) -> void:
    global_position += direction * speed * delta
    lifetime -= delta
    for target in get_tree().get_nodes_in_group("prototype_targets"):
        if not is_instance_valid(target):
            continue
        if global_position.distance_squared_to(target.global_position) <= 24.0 * 24.0:
            if target.has_method("apply_damage"):
                target.apply_damage(damage)
            queue_free()
            return
    if lifetime <= 0.0:
        queue_free()

func _draw() -> void:
    draw_line(Vector2(-10, 0), Vector2(5, 0), Color(tint, 0.55), 3.0)
    draw_circle(Vector2(5, 0), 3.0, tint)
