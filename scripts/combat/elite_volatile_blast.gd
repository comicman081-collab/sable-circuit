extends Node2D
## A VOLATILE elite's death burst: a warning circle for the windup, then one
## blast that ignores cover (like the boss area attacks) and hits each operator
## inside the circle once.

const SFX := preload("res://scripts/audio/combat_sfx_bank.gd")
const Painter := preload("res://scripts/vfx/vfx_painter.gd")

var source_id := ""
var color := Color("ffcf4a")
var radius := 150.0
var damage := 22.0
var windup := 0.9
var elapsed := 0.0
var detonated := false
var hits := 0
var _paint := Painter.new()

func setup(at: Vector2, id_value: String, tint: Color, radius_value: float, damage_value: float, windup_value: float) -> void:
    global_position = at
    source_id = id_value
    color = tint
    radius = radius_value
    damage = damage_value
    windup = windup_value
    z_index = 3050

func _ready() -> void:
    SFX.play(get_tree(), "boss_charge", self, global_position)

func _physics_process(delta: float) -> void:
    elapsed += delta
    if not detonated and elapsed >= windup:
        detonate()
    if detonated and elapsed >= windup + 0.35:
        queue_free()
    queue_redraw()

func detonate() -> void:
    if detonated: return
    detonated = true
    SFX.play(get_tree(), "boss_stomp", self, global_position)
    SquadCameraPresentation.kick(get_tree(), 0.35)
    CombatFeedback.spawn_explosion(get_tree(), global_position, "VOLATILE", color, radius)
    for node in get_tree().get_nodes_in_group("operators"):
        var actor := node as OperatorActor
        if actor != null and not actor.is_downed() and actor.global_position.distance_to(global_position) <= radius:
            actor.apply_damage(damage, source_id)
            hits += 1

func _draw() -> void:
    _paint.clear()
    if not detonated:
        var t := clampf(elapsed / maxf(0.01, windup), 0.0, 1.0)
        var pulse := 0.5 + 0.5 * sin(elapsed * (10.0 + 24.0 * t))
        _paint.disc(Vector2.ZERO, radius, Color(color, 0.08 + 0.1 * t), 36)
        _paint.ring(Vector2.ZERO, radius, 1.6 + pulse, Color(color, 0.55 + 0.35 * t), 44)
        _paint.ring(Vector2.ZERO, radius * t, 1.8, Color(color, 0.8), 40)
        _paint.glow(Vector2.ZERO, radius * 0.3 * (0.6 + 0.4 * pulse), Color(color, 0.25 + 0.35 * t), 14)
    else:
        var fade := 1.0 - clampf((elapsed - windup) / 0.35, 0.0, 1.0)
        _paint.disc(Vector2.ZERO, radius * (0.9 + 0.2 * (1.0 - fade)), Color(color, 0.22 * fade), 36)
    _paint.flush(get_canvas_item())
