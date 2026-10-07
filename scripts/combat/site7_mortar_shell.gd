extends Node2D
## One immutable landing point owns arc, warning and damage. No retargeting.
const Painter := preload("res://scripts/vfx/vfx_painter.gd")
const SHELL_HISTORY := 7

var source: EnemyActor
var origin := Vector2.ZERO
var landing := Vector2.ZERO
var flight_seconds := 1.05
var radius := 64.0
var damage := 18.0
var age := 0.0
var impacted := false
var damage_events := 0
var _warning := Painter.new()
var _glow := Painter.new()
## The glowing shell and its wake blend additively on their own layer above the bodies;
## the landing warning stays a floor marking under them.
var _shell_layer := RID()
var _tint := Color("c097fa")

func _ready() -> void:
    top_level = true
    global_position = landing
    add_to_group("site7_mortar_shells")
    if is_instance_valid(source):
        _tint = source._projectile_color()
    _shell_layer = Painter.make_layer(self, true)
    RenderingServer.canvas_item_set_z_as_relative_to_parent(_shell_layer, false)
    RenderingServer.canvas_item_set_z_index(_shell_layer, 3000)

func _notification(what: int) -> void:
    if what == NOTIFICATION_PREDELETE:
        Painter.free_layer(_shell_layer)
        _shell_layer = RID()

func _physics_process(delta: float) -> void:
    if not is_instance_valid(source) or source.health <= 0:
        queue_free()
        return
    age += delta
    if age >= flight_seconds and not impacted:
        impacted = true
        preload("res://scripts/audio/combat_sfx_bank.gd").play(get_tree(),"boss_stomp",source)
        SquadCameraPresentation.kick(get_tree(),0.3)
        for victim in get_tree().get_nodes_in_group("operators"):
            if victim is OperatorActor and not victim.is_downed() and victim.global_position.distance_to(landing) <= radius:
                victim.apply_damage(damage * source.run_damage_multiplier, source.enemy_id)
                damage_events += 1
        CombatFeedback.spawn_explosion(get_tree(), landing, "MORTAR", _tint, radius)
        var impact_sfx := str(source.art_profile.get("impact_sfx_profile", ""))
        if not impact_sfx.is_empty():
            preload("res://scripts/audio/combat_sfx_bank.gd").play(get_tree(), impact_sfx, source, landing)
    if age >= flight_seconds + 0.3: queue_free()
    queue_redraw()

func arc_point(t: float) -> Vector2:
    # Initial travel ascends from the actual vertical barrel, never sideways.
    var horizontal := t*t
    return origin.lerp(landing,horizontal) + Vector2.UP * (210.0 * sin(PI*t))

func _draw() -> void:
    var t := clampf(age / flight_seconds,0.0,1.0)
    var color := Color("e2bdff")
    _warning.clear()
    _glow.clear()
    # Floor warning: the exact damage circle, filling as the shell falls.
    var urgency := 0.5 + 0.5 * sin(age * (10.0 + 18.0 * t))
    _warning.disc(Vector2.ZERO, radius, Color(color, 0.1 + 0.08 * t if not impacted else 0.3), 32)
    _warning.disc(Vector2.ZERO, radius * t, Color(color, 0.12 + 0.06 * urgency), 32)
    _warning.ring(Vector2.ZERO, radius, 1.6, Color(color, 0.9), 40)
    _warning.ring(Vector2.ZERO, radius - 5.0, 1.4, Color(color, 1.0), 40, -PI / 2.0, -PI / 2.0 + TAU * t)
    _warning.beam(Vector2(-7, 0), Vector2(7, 0), 1.2, color)
    _warning.beam(Vector2(0, -7), Vector2(0, 7), 1.2, color)
    _warning.flush(get_canvas_item())
    if not _shell_layer.is_valid():
        return
    RenderingServer.canvas_item_clear(_shell_layer)
    if impacted:
        return
    # The shell, its wake along the arc, and its shadow closing on the landing point.
    var head := to_local(arc_point(t))
    var previous := head
    for i in range(1, SHELL_HISTORY + 1):
        var back := to_local(arc_point(maxf(0.0, t - 0.022 * float(i))))
        var f0 := 1.0 - float(i - 1) / float(SHELL_HISTORY)
        var f1 := 1.0 - float(i) / float(SHELL_HISTORY)
        _glow.fading_beam(back, previous, 7.0 * f0 + 2.0, Color(_tint, 0.55), f1, f0)
        previous = back
    _glow.glow(head, 16.0, Color(_tint.lightened(0.2), 0.65))
    _glow.glow(head, 6.0, Color(1.0, 0.96, 1.0, 1.0), 8)
    var ground := to_local(origin.lerp(landing, t * t))
    _glow.ellipse_glow(ground, Vector2(10.0 + 12.0 * t, 5.0 + 6.0 * t), Color(_tint, 0.25 + 0.35 * t), 10)
    _glow.flush(_shell_layer)
