extends Node2D
class_name OperatorSkillVFX
## Code-drawn operator skills (Q / E / X) and the auras of timed buffs. Three layers:
## this node draws floor-level light under the bodies, an additive air layer draws beams,
## bursts and target pings over them, and a normal-blend layer carries dust that darkens.
## The node sits 18 px above the caster's feet, as the controller places it.

const Painter := preload("res://scripts/vfx/vfx_painter.gd")
const FEET := Vector2(0.0, 18.0)
const AIR_Z := 3060
## Buff auras that ride with their caster for the buff's duration.
const AURAS := ["OVERCLOCK_AURA", "SCATTER_AURA", "GUARD_AURA"]

var skill_id := "GENERIC"
var accent := Color.WHITE
var radius := 120.0
var aim := Vector2.RIGHT
var life := 0.62
var max_life := 0.62
var follow: Node2D
## Set while an aura rides a caster; a freed caster compares equal to null, so the aura
## needs its own flag to notice it left.
var _following := false
## Robots or squadmates this cast touched; pings and links track them while they live.
var targets: Array[Node2D] = []
var _target_points: Array[Vector2] = []
var _age := 0.0
var _seed := 0
var _ground := Painter.new()
var _air := Painter.new()
var _dust := Painter.new()
var _noise := Painter.noise()
var _air_layer := RID()
var _dust_layer := RID()

func _init() -> void:
    material = Painter.additive_material()

func setup(id_value: String, color: Color, radius_value: float, aim_value: Vector2, duration: float = 0.62) -> void:
    skill_id = id_value.to_upper()
    accent = color
    radius = radius_value
    aim = aim_value.normalized() if aim_value.length_squared() > 0.001 else Vector2.RIGHT
    life = duration
    max_life = duration
    _age = 0.0
    _seed = int(get_instance_id()) % 100003
    z_index = 70
    queue_redraw()

## Keeps the effect on its caster (auras); it ends early if the caster goes down.
func follow_actor(actor: Node2D) -> void:
    follow = actor
    _following = actor != null

func mark_targets(nodes: Array) -> void:
    targets.clear()
    _target_points.clear()
    for node in nodes:
        if node is Node2D and is_instance_valid(node):
            targets.append(node)
            _target_points.append(_aim_point(node))

func _ready() -> void:
    _air_layer = Painter.make_layer(self, true)
    RenderingServer.canvas_item_set_z_as_relative_to_parent(_air_layer, false)
    RenderingServer.canvas_item_set_z_index(_air_layer, AIR_Z)
    _dust_layer = Painter.make_layer(self, false)

func _notification(what: int) -> void:
    if what == NOTIFICATION_PREDELETE:
        Painter.free_layer(_air_layer)
        Painter.free_layer(_dust_layer)
        _air_layer = RID()
        _dust_layer = RID()

func _process(delta: float) -> void:
    life -= delta
    _age += delta
    if _following:
        if not is_instance_valid(follow) or (follow.has_method("is_downed") and bool(follow.call("is_downed"))):
            life = minf(life, 0.25)
            follow = null
            _following = false
        else:
            global_position = follow.global_position + Vector2(0.0, -18.0)
    for i in range(targets.size()):
        if is_instance_valid(targets[i]):
            _target_points[i] = _aim_point(targets[i])
    if life <= 0.0:
        queue_free()
        return
    queue_redraw()

func _aim_point(node: Node2D) -> Vector2:
    if node.has_method("get_combat_aim_point"):
        return node.call("get_combat_aim_point")
    return node.global_position

func _draw() -> void:
    var t := clampf(1.0 - life / maxf(0.001, max_life), 0.0, 1.0)
    _ground.clear()
    _air.clear()
    _dust.clear()
    if "MICA_PULSE_SCAN" in skill_id: _pulse_scan(t)
    elif "ASTER_PRISM" in skill_id: _prism_lance(t)
    elif "ROOK_BREACH_SLAM" in skill_id: _breach_slam(t)
    elif "SENSOR_BLOOM" in skill_id: _sensor_bloom(t)
    elif skill_id == "OVERCLOCK_AURA": _overclock_aura(t)
    elif skill_id == "SCATTER_AURA": _scatter_aura(t)
    elif skill_id == "GUARD_AURA": _guard_aura(t)
    elif "OVERCLOCK" in skill_id: _overclock(t)
    elif "SCATTER_CYCLE" in skill_id: _scatter_cycle(t)
    elif "VECTOR_DASH" in skill_id: _dash_wake(t, Color(0.45, 0.88, 1.0), Color(0.62, 0.5, 1.0))
    elif "RELAY_STEP" in skill_id: _relay_step(t)
    elif "BULWARK" in skill_id: _bulwark(t)
    else:
        _ground.ring(FEET, lerpf(18.0, radius, Painter.ease_out(t)), 3.0, Color(accent, 0.7 * (1.0 - t)), 32)
    _ground.flush(get_canvas_item())
    if _air_layer.is_valid():
        RenderingServer.canvas_item_clear(_air_layer)
        _air.flush(_air_layer)
    if _dust_layer.is_valid():
        RenderingServer.canvas_item_clear(_dust_layer)
        _dust.flush(_dust_layer)

# --- ASTER ---------------------------------------------------------------------------

## Q: a prism lance straight to the target. The beam lands at once and thins away; two
## refracted rays bow out and meet again on the target; the target erupts in glass.
func _prism_lance(t: float) -> void:
    var end := aim * radius
    if not _target_points.is_empty():
        end = to_local(_target_points[0])
    var span := end.length()
    var dir := end / maxf(1.0, span)
    var side := dir.orthogonal()
    var fade := 1.0 - t
    var lance := Painter.fade_window(t, 0.05, 0.7)
    var width := 11.0 * Painter.fade_window(t, 0.0, 0.6) + 1.5
    var start := dir * 20.0
    _air.beam(start, end, width * 2.4, Color(0.4, 0.8, 1.0, 0.35 * lance))
    _air.beam(start, end, width, Color(0.7, 0.95, 1.0, 0.95 * lance), lance)
    for k in range(2):
        var sign := 1.0 if k == 0 else -1.0
        var bow := side * sign * minf(46.0, span * 0.14) * (1.0 - 0.5 * t)
        var mid := start + (end - start) * 0.5 + bow
        var ray_color := Color(0.46, 0.9, 1.0) if k == 0 else Color(0.62, 0.48, 1.0)
        _air.beam(start, mid, 2.2, Color(ray_color, 0.85 * lance))
        _air.beam(mid, end, 2.2, Color(ray_color, 0.85 * lance))
    # Prism at the muzzle end.
    var spin := _age * 5.0
    _air.polygon_outline(start, 13.0 + 4.0 * t, 3, spin, 1.8, Color(0.85, 0.97, 1.0, 0.9 * fade))
    _air.glow(start, 24.0, Color(0.5, 0.86, 1.0, 0.6 * fade))
    # Motes drifting off the lance.
    for i in range(10):
        var along := _rand(i) * span
        var drift := side * (_rand(20 + i) - 0.5) * 40.0 * t + Vector2(0.0, -18.0 * t)
        _air.dot(dir * along + drift, 2.6, Color(0.7, 0.95, 1.0, 0.9 * fade))
    # The target erupts.
    var hit := Painter.fade_window(t, 0.0, 0.5)
    _air.glow(end, 46.0 * (0.6 + 0.6 * Painter.ease_out(t * 4.0)), Color(0.55, 0.9, 1.0, 0.7 * hit))
    _air.glow(end, 18.0, Color(1.0, 1.0, 1.0, hit))
    _air.flare(end, side, 90.0 * hit, 3.4, Color(0.8, 0.96, 1.0, hit), 0.45)
    _air.ring(end, 14.0 + 70.0 * Painter.ease_out(t * 1.6), 3.0 * fade, Color(0.5, 0.85, 1.0, 0.8 * fade), 22)
    _air.polygon_outline(end, 30.0 + 10.0 * t, 6, PI / 6.0, 1.8, Color(0.6, 0.55, 1.0, 0.7 * fade), 0.8)
    for i in range(9):
        var direction := (-dir).rotated((_rand(40 + i) - 0.5) * 2.6)
        var position := end + direction * (30.0 + 60.0 * _rand(50 + i)) * Painter.ease_out(t * 1.4) + Vector2(0.0, 40.0 * t * t)
        _air.shard(position, direction.angle() + t * 7.0, 4.0 + 4.0 * _rand(60 + i), Color(0.82, 0.96, 1.0, 0.9 * fade) if i % 2 == 0 else Color(0.66, 0.54, 1.0, 0.9 * fade))
    _ground.ring(FEET, 16.0 + 30.0 * Painter.ease_out(t * 2.0), 2.0, Color(0.45, 0.88, 1.0, 0.6 * fade), 20, 0.0, TAU, 0.5)

## E (ASTER) / RELAY: the afterimage wake of a dash that ended here, along `aim`.
func _dash_wake(t: float, color_a: Color, color_b: Color) -> void:
    var fade := 1.0 - t
    var length := radius
    var back := -aim
    var side := aim.orthogonal()
    for i in range(6):
        var lateral := (float(i) - 2.5) * 7.0
        var reach := length * (0.55 + 0.45 * _rand(i)) * (1.0 - 0.35 * t)
        var from := side * lateral + back * (reach + 10.0 * t)
        var color := color_a if i % 2 == 0 else color_b
        _air.fading_beam(from, side * lateral * 0.4, 2.4, Color(color, 0.85 * fade), 0.0, 1.0)
    for i in range(3):
        var at := back * (length * (0.3 + 0.25 * float(i))) + Vector2(0.0, -4.0)
        var chevron := 14.0 - float(i) * 2.0
        var alpha := fade * (1.0 - float(i) * 0.25)
        _air.beam(at + side * chevron, at + aim * chevron * 0.8, 2.0, Color(color_a, alpha))
        _air.beam(at - side * chevron, at + aim * chevron * 0.8, 2.0, Color(color_a, alpha))
    var depart := back * length
    _air.glow(depart, 30.0 * fade, Color(color_b, 0.5 * fade))
    _ground.ring(depart + FEET, 10.0 + 34.0 * Painter.ease_out(t * 2.0), 2.4, Color(color_b, 0.7 * fade), 18, 0.0, TAU, 0.5)
    _ground.ring(FEET, 10.0 + 44.0 * Painter.ease_out(t * 1.6), 3.0, Color(color_a, 0.8 * fade), 20, 0.0, TAU, 0.5)
    _air.glow(Vector2.ZERO, 34.0 * Painter.fade_window(t, 0.0, 0.4), Color(color_a, 0.6 * fade))
    for i in range(8):
        var direction := aim.rotated((_rand(30 + i) - 0.5) * 2.8)
        var p := direction * 50.0 * Painter.ease_out(t * 1.5) + Vector2(0.0, -20.0 * t)
        _air.dot(p, 2.4, Color(color_a, fade))

## X: overclock burst. A light column, lightning out to the floor and a hex ring.
func _overclock(t: float) -> void:
    var fade := 1.0 - t
    var burst := Painter.fade_window(t, 0.0, 0.45)
    var hot := Color(1.0, 0.92, 0.6)
    _air.beam(FEET + Vector2(0.0, 4.0), FEET + Vector2(0.0, -150.0 * (0.5 + 0.5 * Painter.ease_out(t * 4.0))), 26.0 * burst, Color(0.5, 0.88, 1.0, 0.55 * burst), 0.8 * burst)
    _air.glow(Vector2(0.0, -30.0), 70.0 * (0.5 + 0.5 * Painter.ease_out(t * 3.0)), Color(0.5, 0.86, 1.0, 0.5 * burst))
    for i in range(6):
        var direction := Vector2.from_angle(TAU * float(i) / 6.0 + 0.3)
        var tip := FEET + direction * Vector2(1.0, 0.5) * (70.0 + 30.0 * _rand(i))
        _air.bolt(Vector2(0.0, -20.0), tip, 5, 16.0, 1.6, Color(0.7, 0.95, 1.0, 0.9 * burst), _seed + int(_age * 30.0) * 13 + i)
    _ground.polygon_outline(FEET, 30.0 + radius * Painter.ease_out(t), 6, 0.0, 3.0 * fade + 0.5, Color(0.45, 0.88, 1.0, 0.85 * fade), 0.5)
    _ground.ellipse_glow(FEET, Vector2(radius, radius * 0.5) * (0.4 + 0.6 * Painter.ease_out(t)), Color(0.35, 0.7, 1.0, 0.3 * fade), 16)
    for i in range(5):
        var rise := fposmod(t * 1.6 + float(i) * 0.2, 1.0)
        var at := Vector2((float(i) - 2.0) * 16.0, 10.0 - 120.0 * rise)
        _air.beam(at + Vector2(-9.0, 5.0), at, 2.0, Color(hot, fade * (1.0 - rise)))
        _air.beam(at + Vector2(9.0, 5.0), at, 2.0, Color(hot, fade * (1.0 - rise)))

## Overclock running: a turning hex ring underfoot and cyan-gold motes streaming up.
func _overclock_aura(t: float) -> void:
    var presence := _aura_presence()
    var turn := _age * 1.4
    _ground.ellipse_glow(FEET, Vector2(40.0, 20.0), Color(0.35, 0.75, 1.0, 0.3 * presence), 14)
    _ground.polygon_outline(FEET, 34.0, 6, turn, 2.0, Color(0.45, 0.88, 1.0, 0.75 * presence), 0.5)
    _ground.polygon_outline(FEET, 26.0, 6, -turn * 1.3, 1.2, Color(1.0, 0.85, 0.5, 0.4 * presence), 0.5)
    for i in range(7):
        var cycle := fposmod(_age * 0.9 + _rand(i), 1.0)
        var at := Vector2((_rand(10 + i) - 0.5) * 50.0, 10.0 - 110.0 * cycle)
        var color := Color(0.55, 0.92, 1.0) if i % 2 == 0 else Color(1.0, 0.86, 0.5)
        _air.streak(at + Vector2(0.0, 14.0), at, 2.0, Color(color, presence * sin(cycle * PI)), true)
    if int(_age * 8.0) % 5 == 0:
        var a := Vector2((_rand(int(_age * 8.0)) - 0.5) * 40.0, -60.0 * _rand(int(_age * 8.0) + 3))
        _air.bolt(a, a + Vector2.from_angle(_rand(int(_age * 8.0) + 5) * TAU) * 24.0, 3, 6.0, 1.0, Color(0.7, 0.95, 1.0, 0.8 * presence), _seed + int(_age * 30.0))

# --- ROOK ----------------------------------------------------------------------------

## Q: breach slam. A shock wedge rolls across the floor in the aim cone, cracks spread,
## rubble and dust kick up; the front of the wedge flashes where the target stood.
func _breach_slam(t: float) -> void:
    var fade := 1.0 - t
    var angle := aim.angle()
    var from := angle - 0.95
    var to := angle + 0.95
    var front := lerpf(28.0, radius, Painter.ease_out(t * 1.3))
    _ground.ring(FEET, front, 9.0 * fade + 1.0, Color(1.0, 0.62, 0.25, 0.95 * fade), 26, from, to, 0.6)
    _ground.ring(FEET, front * 0.72, 4.0 * fade + 0.5, Color(1.0, 0.86, 0.6, 0.6 * fade), 22, from, to, 0.6)
    for i in range(7):
        var a := lerpf(from, to, (float(i) + 0.5) / 7.0)
        var tip := FEET + Vector2.from_angle(a) * Vector2(1.0, 0.6) * front * (0.75 + 0.25 * _rand(i))
        _ground.bolt(FEET, tip, 5, 10.0, 1.4, Color(1.0, 0.55, 0.2, 0.8 * fade), _seed + i * 31)
    var impact := FEET + aim * Vector2(1.0, 0.6) * 46.0 + Vector2(0.0, -12.0)
    var flash := Painter.fade_window(t, 0.0, 0.35)
    _ground.ellipse_glow(FEET + aim * Vector2(1.0, 0.6) * front * 0.5, Vector2(front * 0.75, front * 0.42), Color(1.0, 0.5, 0.18, 0.4 * fade), 16, aim.angle())
    _air.glow(impact, 70.0 * (0.6 + 0.4 * Painter.ease_out(t * 4.0)), Color(1.0, 0.6, 0.26, 0.7 * flash))
    _air.glow(impact, 26.0, Color(1.0, 0.95, 0.85, flash))
    _air.flare(impact, Vector2.RIGHT, 110.0 * flash, 4.5, Color(1.0, 0.82, 0.5, flash), 0.4)
    for i in range(8):
        var direction := aim.rotated((_rand(80 + i) - 0.5) * 2.2) * Vector2(1.0, 0.7) + Vector2(0.0, -0.5)
        var head := impact + direction * (40.0 + 60.0 * _rand(90 + i)) * Painter.ease_out(t * 1.8) + Vector2(0.0, 60.0 * t * t)
        _air.streak(head - direction * 16.0, head, 1.6, Color(1.0, 0.8, 0.45, fade), i < 3)
    for i in range(12):
        var a := lerpf(from, to, _rand(40 + i))
        var direction := Vector2.from_angle(a) * Vector2(1.0, 0.6) + Vector2(0.0, -0.9)
        var p := FEET + direction * (40.0 + 70.0 * _rand(50 + i)) * Painter.ease_out(t * 1.3) + Vector2(0.0, 160.0 * t * t)
        _dust.shard(p, _rand(60 + i) * TAU + t * 8.0, 3.0 + 4.0 * _rand(70 + i), Color(0.16, 0.13, 0.11, 0.95 * fade))
        if i % 3 == 0:
            _air.shard(p, _rand(60 + i) * TAU + t * 8.0, 3.0 + 3.0 * _rand(70 + i), Color(1.0, 0.6, 0.25, fade))
    for i in range(7):
        var a := lerpf(from, to, (float(i) + 0.5) / 7.0)
        var p := FEET + Vector2.from_angle(a) * Vector2(1.0, 0.6) * front * (0.8 + 0.2 * _rand(100 + i)) + Vector2(0.0, -10.0 - 22.0 * t)
        var shade := 0.4 + 0.1 * _rand(110 + i)
        _dust.puff(p, 16.0 + 30.0 * Painter.ease_out(t), Color(shade, shade * 0.93, shade * 0.86, 0.55 * Painter.fade_window(t, 0.35, 1.0) * minf(1.0, t * 8.0)), Color(0.72, 0.5, 0.3), 8)

## E: bulwark guard raised. Hex panels snap into place in front, then the dome shows.
func _bulwark(t: float) -> void:
    var fade := 1.0 - t
    var angle := aim.angle()
    for i in range(5):
        var a := angle + (float(i) - 2.0) * 0.36
        var center := Vector2.from_angle(a) * Vector2(1.0, 0.7) * (38.0 + 6.0 * t) + Vector2(0.0, -6.0)
        var appear := Painter.ease_out((t - float(i) * 0.04) * 5.0)
        _air.polygon_outline(center, 16.0 * appear, 6, a, 2.2, Color(1.0, 0.8, 0.45, 0.95 * fade), 1.0)
        _air.glow(center, 18.0 * appear, Color(1.0, 0.7, 0.35, 0.4 * fade), 8)
    _air.ring(Vector2(0.0, -6.0), 44.0 + 6.0 * t, 8.0, Color(1.0, 0.72, 0.36, 0.45 * fade), 22, angle - 1.0, angle + 1.0, 0.7)
    _air.glow(Vector2(0.0, -10.0), 56.0 * Painter.fade_window(t, 0.0, 0.4), Color(1.0, 0.75, 0.4, 0.5))
    _ground.ring(FEET, 20.0 + 26.0 * Painter.ease_out(t * 2.0), 3.0, Color(1.0, 0.7, 0.35, 0.8 * fade), 22, 0.0, TAU, 0.5)

## Guard running: a faint amber dome of hex cells round ROOK.
func _guard_aura(t: float) -> void:
    var presence := _aura_presence()
    var shimmer := 0.75 + 0.25 * sin(_age * 5.0)
    _ground.ellipse_glow(FEET, Vector2(46.0, 23.0), Color(1.0, 0.62, 0.28, 0.3 * presence), 14)
    _ground.ring(FEET, 42.0, 2.4, Color(1.0, 0.72, 0.35, 0.7 * presence * shimmer), 26, 0.0, TAU, 0.5)
    _air.oval_ring(Vector2(0.0, -30.0), Vector2(44.0, 66.0), 0.0, 2.2, Color(1.0, 0.74, 0.38, 0.4 * presence * shimmer), 22)
    for i in range(6):
        var a := _age * 0.8 + TAU * float(i) / 6.0
        var p := Vector2(cos(a) * 40.0, -30.0 + sin(a) * 18.0 - 30.0 * _rand(i))
        if sin(a) > -0.2:
            _air.polygon_outline(p, 8.0, 6, 0.0, 1.4, Color(1.0, 0.8, 0.45, 0.6 * presence), 1.0)

## X: scatter cycle. A forward fan of hot rays, a spinning ring and a heat pulse.
func _scatter_cycle(t: float) -> void:
    var fade := 1.0 - t
    var burst := Painter.fade_window(t, 0.0, 0.5)
    for i in range(7):
        var direction := aim.rotated(-1.1 + 2.2 * float(i) / 6.0)
        var reach := lerpf(40.0, radius, Painter.ease_out(t * 1.4))
        _air.fading_beam(direction * 20.0, direction * reach, 4.0 if i % 2 == 0 else 2.6, Color(1.0, 0.7, 0.3, 0.9 * burst), 1.0, 0.0)
    _air.glow(Vector2.ZERO, 60.0 * burst, Color(1.0, 0.62, 0.28, 0.55 * burst))
    _air.glow(Vector2.ZERO, 20.0 * burst, Color(1.0, 0.95, 0.85, burst))
    _air.ring(Vector2.ZERO, 26.0 + 36.0 * Painter.ease_out(t), 3.0, Color(1.0, 0.86, 0.6, 0.8 * fade), 20, _age * 6.0, _age * 6.0 + PI * 1.4)
    for i in range(14):
        var direction := aim.rotated((_rand(120 + i) - 0.5) * 2.3)
        var reach := radius * (0.45 + 0.6 * _rand(130 + i))
        var k := Painter.ease_out(t * 1.6)
        var head := direction * reach * k + Vector2(0.0, 30.0 * t * t)
        _air.streak(direction * reach * maxf(0.0, k - 0.2), head, 1.8, Color(1.0, 0.82, 0.5, fade), i < 4)
    _ground.ellipse_glow(FEET, Vector2(radius * 0.55, radius * 0.28) * (0.5 + 0.5 * Painter.ease_out(t * 2.0)), Color(1.0, 0.5, 0.2, 0.35 * burst), 16)
    _ground.ring(FEET, 20.0 + radius * 0.6 * Painter.ease_out(t), 5.0 * fade + 0.5, Color(1.0, 0.6, 0.25, 0.8 * fade), 26, 0.0, TAU, 0.5)

## Scatter cycle running: embers swirling round ROOK's feet.
func _scatter_aura(t: float) -> void:
    var presence := _aura_presence()
    for i in range(8):
        var a := _age * (1.6 + 0.3 * _rand(i)) + TAU * float(i) / 8.0
        var lift := fposmod(_age * 0.6 + _rand(10 + i), 1.0)
        var p := FEET + Vector2(cos(a) * 30.0, sin(a) * 12.0 - 70.0 * lift)
        _air.dot(p, 3.4, Color(1.0, 0.82, 0.5, presence * (1.0 - lift)))
        _air.dot(p, 8.0, Color(1.0, 0.55, 0.22, 0.35 * presence * (1.0 - lift)))
    _ground.ellipse_glow(FEET, Vector2(36.0, 18.0), Color(1.0, 0.5, 0.2, 0.3 * presence), 12)
    _ground.ring(FEET, 30.0, 2.2, Color(1.0, 0.6, 0.25, 0.7 * presence * (0.7 + 0.3 * sin(_age * 7.0))), 22, 0.0, TAU, 0.5)

# --- MICA ----------------------------------------------------------------------------

## Q: pulse scan. A sonar front runs out to the scan radius with a sweeping wedge behind
## it; each robot it tags gets a bracket and a ping.
func _pulse_scan(t: float) -> void:
    var fade := 1.0 - t
    var front := lerpf(24.0, radius, Painter.ease_out(t * 1.2))
    _ground.ring(FEET, front, 4.0 * fade + 1.0, Color(accent, 0.9 * fade), 48)
    _ground.ring(FEET, front * 0.7, 1.6, Color(0.8, 1.0, 0.96, 0.45 * fade), 40)
    var sweep := _age * 7.0
    for i in range(10):
        var a0 := sweep - float(i) * 0.08
        var a1 := sweep - float(i + 1) * 0.08
        var alpha := 0.35 * fade * (1.0 - float(i) / 10.0)
        _ground.tri3(FEET, FEET + Vector2.from_angle(a0) * front, FEET + Vector2.from_angle(a1) * front, Color(accent, alpha), Color(accent, alpha * 0.4), Color(accent, alpha * 0.4))
    for i in range(14):
        var a := _rand(i) * TAU
        var d := radius * (0.2 + 0.8 * _rand(20 + i))
        if d > front:
            continue
        var blink := 1.0 if int(_age * 14.0 + i) % 3 != 0 else 0.3
        var p := FEET + Vector2.from_angle(a) * d
        _ground.quad(p + Vector2(-2, -2), p + Vector2(2, -2), p + Vector2(2, 2), p + Vector2(-2, 2), Color(accent, 0.8 * fade * blink))
    _air.glow(Vector2.ZERO, 40.0 * Painter.fade_window(t, 0.0, 0.4), Color(accent, 0.6))
    _ping_targets(t, accent, 1.0)

## E: relay step back, with a link of light to each squadmate it shored up.
func _relay_step(t: float) -> void:
    _dash_wake(t, Color(0.45, 1.0, 0.88), Color(0.35, 0.8, 1.0))
    var fade := 1.0 - t
    var reveal := Painter.ease_out(t * 3.0)
    for point in _target_points:
        var other := to_local(point)
        var link_end := other * reveal
        _air.beam(Vector2(0.0, -10.0), link_end, 2.0, Color(0.5, 1.0, 0.9, 0.8 * fade), 0.5 * fade)
        _air.glow(other, 26.0 * reveal, Color(0.45, 1.0, 0.85, 0.5 * fade))
        for k in range(3):
            var rise := fposmod(t * 2.0 + float(k) * 0.33, 1.0)
            var p := other + Vector2((float(k) - 1.0) * 12.0, -30.0 * rise)
            var a := fade * (1.0 - rise)
            _air.beam(p + Vector2(-4, 0), p + Vector2(4, 0), 1.3, Color(0.6, 1.0, 0.9, a))
            _air.beam(p + Vector2(0, -4), p + Vector2(0, 4), 1.3, Color(0.6, 1.0, 0.9, a))

## X: sensor bloom. A flash, three rolling rings out to the bloom radius, radial sensor
## rays and a strike on every robot caught in it.
func _sensor_bloom(t: float) -> void:
    var fade := 1.0 - t
    var flash := Painter.fade_window(t, 0.0, 0.3)
    _air.glow(Vector2(0.0, -20.0), 110.0 * (0.4 + 0.6 * Painter.ease_out(t * 3.0)), Color(accent, 0.55 * flash))
    _air.glow(Vector2(0.0, -20.0), 36.0, Color(1.0, 1.0, 1.0, 0.9 * flash))
    for i in range(3):
        var k := clampf((t - float(i) * 0.12) / 0.75, 0.0, 1.0)
        if k <= 0.0 or k >= 1.0:
            continue
        _ground.ring(FEET, radius * Painter.ease_out(k), 5.0 * (1.0 - k) + 1.0, Color(accent if i != 1 else Color(0.85, 1.0, 0.96), 0.85 * (1.0 - k)), 56)
    for i in range(16):
        var direction := Vector2.from_angle(TAU * float(i) / 16.0 + 0.1)
        var reach := radius * Painter.ease_out(t * 1.5)
        _ground.fading_beam(FEET + direction * 30.0, FEET + direction * reach, 1.6, Color(accent, 0.6 * fade), 1.0, 0.0)
    _ground.ellipse_glow(FEET, Vector2(radius, radius) * Painter.ease_out(t * 1.2), Color(accent, 0.12 * fade), 24)
    _ping_targets(t, accent, 1.6)

## Bracket, ping ring and strike flash on each tagged robot.
func _ping_targets(t: float, color: Color, strength: float) -> void:
    var fade := 1.0 - t
    for i in range(_target_points.size()):
        var p := to_local(_target_points[i])
        var arrive := Painter.ease_out((t - 0.08 - 0.03 * float(i)) * 4.0)
        if arrive <= 0.0:
            continue
        var size := 34.0 * (1.6 - 0.6 * arrive)
        for c in range(4):
            var corner := Vector2(1.0 if c % 2 == 0 else -1.0, 1.0 if c < 2 else -1.0) * size
            _air.beam(p + corner, p + corner - Vector2(corner.x * 0.4, 0.0), 1.6, Color(color, fade))
            _air.beam(p + corner, p + corner - Vector2(0.0, corner.y * 0.4), 1.6, Color(color, fade))
        _air.ring(p, 10.0 + 40.0 * fposmod(_age * 1.8, 1.0), 2.0, Color(color, 0.8 * fade * (1.0 - fposmod(_age * 1.8, 1.0))), 18)
        var strike := Painter.fade_window(t - 0.08 - 0.03 * float(i), 0.0, 0.25) * (1.0 if t >= 0.08 + 0.03 * float(i) else 0.0)
        if strike > 0.0:
            _air.glow(p, 30.0 * strength, Color(color, 0.7 * strike))
            _air.flare(p, Vector2.RIGHT, 50.0 * strength * strike, 2.4, Color(0.9, 1.0, 0.98, strike), 0.6)

# --- helpers -------------------------------------------------------------------------

## Auras fade in over a fifth of a second and out over their last half second.
func _aura_presence() -> float:
    return minf(1.0, _age * 5.0) * clampf(life / 0.5, 0.0, 1.0)

func _rand(index: int) -> float:
    return _noise[(_seed * 7919 + index) & (Painter.NOISE_SIZE - 1)]

func debug_contract() -> Dictionary:
    return {"skill_id": skill_id, "life": life, "max_life": max_life, "targets": targets.size(),
        "following": _following, "air_layer": _air_layer.is_valid()}
