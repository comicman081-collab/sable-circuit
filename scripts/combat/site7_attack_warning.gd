extends Node2D
## A floor warning and its damage share the same frozen geometry and clock.
## No invisible homing: moving out of the marked region always evades the hit.

const Painter := preload("res://scripts/vfx/vfx_painter.gd")

var source: EnemyActor
var kind := "circle"
var radius := 58.0
var ray := Vector2.RIGHT
var reach := 430.0
var half_width := 16.0
var windup := 1.05
var damage := 16.0
var elapsed := 0.0
var fired := false
var _paint := Painter.new()

func _ready() -> void:
    z_index = -2
    add_to_group("site7_attack_warnings")
    # Boss wind-up: the rising charge that tells the player to move now.
    if is_instance_valid(source) and source.health > 0.0 and source.enemy_id.begins_with("BOSS_"):
        preload("res://scripts/audio/combat_sfx_bank.gd").play(get_tree(), "boss_charge", source)

func _physics_process(delta: float) -> void:
    if not is_instance_valid(source) or source.health <= 0.0:
        queue_free()
        return
    elapsed += delta
    if elapsed >= windup and not fired:
        fired = true
        preload("res://scripts/audio/combat_sfx_bank.gd").play(get_tree(),
            "boss_stomp" if kind == "circle" else "boss_cross_beam", source)
        SquadCameraPresentation.kick(get_tree(), 0.35)
        _show_blast()
        for actor in get_tree().get_nodes_in_group("operators"):
            if actor is OperatorActor and not actor.is_downed() and contains(actor.global_position):
                actor.apply_damage(damage * source.run_damage_multiplier, source.enemy_id)
    if elapsed > windup + 0.26:
        queue_free()
    queue_redraw()

func contains(point: Vector2) -> bool:
    var offset := to_local(point)
    if kind == "circle":
        return offset.length() <= radius
    var forward := offset.dot(ray)
    return forward >= 0.0 and forward <= reach and absf(offset.dot(ray.orthogonal())) <= half_width

## The attack going off over exactly the warned area: a slam blast filling the circle, or a
## beam down the lane.
func _show_blast() -> void:
    var tint := source._projectile_color() if is_instance_valid(source) else Color("f48caa")
    if kind == "circle":
        CombatFeedback.spawn_explosion(get_tree(), global_position, "SLAM", tint, radius)
    else:
        CombatFeedback.spawn_explosion(get_tree(), global_position, "LANE", tint, half_width, ray, reach)

func _draw() -> void:
    var progress := clampf(elapsed / windup, 0.0, 1.0)
    var color := Color("f48caa")
    if fired:
        color = Color("eee2ff")
    # Faster pulse as the hit nears; the shape itself never moves.
    var pulse := 0.5 + 0.5 * sin(elapsed * (8.0 + 16.0 * progress))
    var fill := Color(color, (0.1 + 0.05 * pulse) if not fired else 0.36)
    _paint.clear()
    if kind == "circle":
        _paint.disc(Vector2.ZERO, radius, fill, 32)
        _paint.disc(Vector2.ZERO, radius * progress, Color(color, 0.14), 32)
        _paint.ring(Vector2.ZERO, radius, 1.4 + pulse, Color(color, 0.8), 40)
        _paint.ring(Vector2.ZERO, radius - 5.0, 1.5, color, 40, -PI * 0.5, -PI * 0.5 + TAU * progress)
        _paint.beam(Vector2(-7, 0), Vector2(7, 0), 1.1, color)
        _paint.beam(Vector2(0, -7), Vector2(0, 7), 1.1, color)
    else:
        var side := ray.orthogonal() * half_width
        _paint.quad(-side, side, ray * reach + side, ray * reach - side, fill)
        _paint.quad(-side, side, ray * reach * progress + side, ray * reach * progress - side, Color(color, 0.14))
        _paint.beam(-side, ray * reach - side, 1.0 + 0.5 * pulse, Color(color, 0.8))
        _paint.beam(side, ray * reach + side, 1.0 + 0.5 * pulse, Color(color, 0.8))
        _paint.beam(Vector2.ZERO, ray * reach * progress, 1.4 if not fired else 4.0, color, 0.6)
        # Chevrons marching down the lane show which way the beam will run.
        for i in range(4):
            var along := fposmod(elapsed * 1.6 + float(i) * 0.25, 1.0) * reach
            var tip := ray * (along + 8.0)
            _paint.beam(ray * along + side * 0.6, tip, 1.0, Color(color, 0.55))
            _paint.beam(ray * along - side * 0.6, tip, 1.0, Color(color, 0.55))
    _paint.flush(get_canvas_item())
