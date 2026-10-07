extends Node2D
class_name CombatExplosionVFX
## Code-drawn blasts: robot and boss destruction, mortar landings, boss slams and lanes,
## an elite's death burst, a damaged robot's smoulder and the CINDER ram's charge trail.
## Light (flash, heat bloom, rings, sparks, embers) blends additively in this node; the
## bodies of fire and smoke, floor dust and falling debris are solid-edged puffs in a
## normal-blend layer drawn behind it, so they read as volume over any floor. Ground-level scorch is a
## separate GroundMark under the bodies. Gameplay (damage, radius, timing) stays with the
## caller; this only shows it, sized to the same radius.

const Painter := preload("res://scripts/vfx/vfx_painter.gd")
const HIT := preload("res://scripts/vfx/combat_hit_vfx.gd")

const KINDS := ["ROBOT_SMALL", "ROBOT_HEAVY", "BOSS", "MORTAR", "VOLATILE", "SLAM", "LANE", "SMOLDER", "TRAIL"]
## Seconds each kind stays alive.
const DURATIONS := {"ROBOT_SMALL": 1.0, "ROBOT_HEAVY": 1.45, "BOSS": 2.9, "MORTAR": 1.15,
    "VOLATILE": 1.2, "SLAM": 0.95, "LANE": 0.6, "SMOLDER": 1.1, "TRAIL": 0.85}
## Kinds whose fire is the source's energy colour rather than burning fuel.
const ENERGY_KINDS := ["MORTAR", "VOLATILE", "SLAM", "LANE"]
## Kinds that burn: a rolling fireball under the smoke instead of a plasma bloom.
const FUEL_KINDS := ["ROBOT_SMALL", "ROBOT_HEAVY", "BOSS", "VOLATILE"]
## Boss destruction: small bursts round the body, then the core goes.
const BOSS_BURSTS := [0.0, 0.2, 0.38, 0.58, 0.8]
const BOSS_FINAL := 1.02

var kind := "ROBOT_SMALL"
var color := Color("ff9a4a")
var radius := 80.0
var ray := Vector2.RIGHT
var reach := 0.0
var age := 0.0
var duration := 1.0
var follow: Node2D
var _seed := 0
var _paint := Painter.new()
var _noise := Painter.noise()
var _smoke := Painter.new()
var _smoke_layer := RID()
var _light: PointLight2D
var _trail: PackedVector2Array = PackedVector2Array()

func _init() -> void:
    material = Painter.additive_material()

func setup(kind_value: String, tint: Color, radius_value: float, direction := Vector2.RIGHT, reach_value := 0.0) -> void:
    kind = kind_value.to_upper() if KINDS.has(kind_value.to_upper()) else "ROBOT_SMALL"
    color = tint
    radius = maxf(8.0, radius_value)
    ray = direction.normalized() if direction.length_squared() > 0.0001 else Vector2.RIGHT
    reach = reach_value
    duration = float(DURATIONS[kind])
    age = 0.0
    _seed = abs(int(get_instance_id()) + kind.hash())
    z_index = 3090
    if kind != "SMOLDER" and kind != "TRAIL":
        _make_light()
    queue_redraw()

## The trail follows this body until the effect ends (the CINDER ram's charge).
func follow_node(target: Node2D) -> void:
    follow = target
    _trail.clear()
    if is_instance_valid(target):
        _trail.append(_trail_point(target))

func _ready() -> void:
    _smoke_layer = Painter.make_layer(self, false, true)

func _notification(what: int) -> void:
    if what == NOTIFICATION_PREDELETE:
        Painter.free_layer(_smoke_layer)
        _smoke_layer = RID()

func _make_light() -> void:
    # Desktop only, like the impact light; the web renderer pays a canvas pass per light.
    if OS.has_feature("web"):
        return
    _light = PointLight2D.new()
    _light.texture = HIT._shared_radial_texture()
    _light.color = _energy_color(0.05).lightened(0.2) if kind in ENERGY_KINDS else Color("ffb46a")
    _light.texture_scale = radius / 40.0
    _light.energy = 0.0
    _light.range_z_min = -1024
    _light.range_z_max = 1024
    _light.shadow_enabled = false
    add_child(_light)

func _process(delta: float) -> void:
    age += delta
    if kind == "TRAIL" and is_instance_valid(follow) and age < duration - 0.35:
        var point := _trail_point(follow)
        if _trail.is_empty() or _trail[_trail.size() - 1].distance_to(point) > 6.0:
            _trail.append(point)
            if _trail.size() > 18:
                _trail.remove_at(0)
    if age >= duration:
        queue_free()
        return
    if is_instance_valid(_light):
        var flash := _light_curve()
        _light.enabled = flash > 0.01
        _light.energy = flash
    queue_redraw()

func _trail_point(target: Node2D) -> Vector2:
    return target.global_position + Vector2(0.0, -24.0)

func _light_curve() -> float:
    if kind == "BOSS":
        var strongest := 0.0
        for start in BOSS_BURSTS:
            strongest = maxf(strongest, 1.4 * Painter.fade_window(age - start, 0.0, 0.3) * (1.0 if age >= start else 0.0))
        return maxf(strongest, 2.6 * Painter.fade_window(age - BOSS_FINAL, 0.0, 0.5) * (1.0 if age >= BOSS_FINAL else 0.0))
    var peak := 1.8 if kind in ["ROBOT_HEAVY", "VOLATILE", "MORTAR"] else 1.3
    return peak * Painter.fade_window(age, 0.0, 0.34)

func _draw() -> void:
    _paint.clear()
    _smoke.clear()
    match kind:
        "ROBOT_SMALL":
            _burst(Vector2.ZERO, radius, age, 0, 1.0)
        "ROBOT_HEAVY":
            _burst(Vector2.ZERO, radius, age, 0, 1.25)
        "BOSS":
            for i in range(BOSS_BURSTS.size()):
                var start: float = BOSS_BURSTS[i]
                if age >= start:
                    var offset := Vector2((_rand(10 + i) - 0.5) * radius * 0.9, (_rand(20 + i) - 0.75) * radius * 0.8)
                    _burst(offset, radius * 0.42, age - start, 100 * (i + 1), 0.8)
            if age >= BOSS_FINAL:
                _burst(Vector2(0.0, -radius * 0.25), radius, age - BOSS_FINAL, 900, 1.6)
        "MORTAR", "VOLATILE", "SLAM":
            _burst(Vector2.ZERO, radius, age, 0, 1.1 if kind == "SLAM" else 1.2)
        "LANE":
            _lane(age)
        "SMOLDER":
            _smolder(age)
        "TRAIL":
            _ram_trail(age)
    _paint.flush(get_canvas_item())
    if _smoke_layer.is_valid():
        RenderingServer.canvas_item_clear(_smoke_layer)
        _smoke.flush(_smoke_layer)

## One blast at `origin`, `s` seconds after it went off. `strength` scales counts and
## brightness; `offset` keeps each burst of a boss sequence laid out differently.
## The normal-blend layer is filled in order: floor dust, smoke, then the fireball over
## it, then dark debris on top. Light (flash, heat bloom, rings, sparks, embers) is
## additive in this node, over all of it.
func _burst(origin: Vector2, r: float, s: float, offset: int, strength: float) -> void:
    var energy := kind in ENERGY_KINDS
    var fuel := kind in FUEL_KINDS
    var size := clampf(r / 80.0, 0.5, 3.0)
    var grow := sqrt(size)
    _floor_dust(origin, r, s, grow)
    _smoke_column(origin, r, s, offset, strength, grow, fuel)
    if fuel:
        _fireball(origin, r, s, offset, strength, grow)
    else:
        _plasma(origin, r, s, offset, strength, size)
    # Flash: a white-hot point for the first tenth of a second.
    var flash := Painter.fade_window(s, 0.0, 0.1)
    if flash > 0.0:
        _paint.glow(origin, r * 0.5 * (0.6 + 0.5 * Painter.ease_out(s / 0.04)), Color(1.0, 0.96, 0.86, 0.9 * flash), 12)
        _paint.flare(origin, Vector2.RIGHT, r * 1.25 * flash, 3.0 * size, Color(_energy_color(0.0) if energy else Color("ffe2a8"), 0.75 * flash), 0.3)
    # Shock ring along the floor; an area attack's is a circle at its damage radius.
    var shock_time := 0.36 * grow
    if s < shock_time:
        var k := s / shock_time
        var ring_color := _energy_color(0.1) if energy else Color("ffc47a")
        var reach_scale := 0.85 if energy else 1.1
        var squash := 1.0 if energy else 0.58
        _paint.ring(origin, r * (0.15 + reach_scale * Painter.ease_out(k)), 7.0 * size * (1.0 - 0.6 * k), Color(ring_color, 0.85 * (1.0 - k) * (1.0 - k)), 32, 0.0, TAU, squash)
        if energy and k > 0.2:
            var k2 := (k - 0.2) / 0.8
            _paint.ring(origin, r * (0.1 + 0.7 * Painter.ease_out(k2)), 3.0 * size, Color(ring_color.lightened(0.3), 0.6 * (1.0 - k2)), 28)
    # Sparks flung in every direction, arcing down.
    var spark_life := 0.6
    if s < spark_life:
        var k := s / spark_life
        var k0 := maxf(0.0, k - 0.09)
        var spark_color := _energy_color(0.05).lightened(0.3) if energy else Color("ffd690")
        for i in range(int(16.0 * strength)):
            var direction := Vector2.from_angle(_rand(offset + 70 + i) * TAU)
            var distance := r * (0.8 + 1.2 * _rand(offset + 80 + i))
            var g := r * (0.8 + _rand(offset + 90 + i))
            var head := origin + direction * distance * Painter.ease_out(k * 1.5) + Vector2(0.0, g * k * k)
            var tail := origin + direction * distance * Painter.ease_out(k0 * 1.5) + Vector2(0.0, g * k0 * k0)
            _paint.streak(tail, head, 1.8 * size * (1.0 - 0.5 * k), Color(spark_color, 1.0 - k), i < 5)
    # Embers: slow, flickering, lifted by the heat and settling.
    var ember_life := 1.4 * grow
    if s < ember_life:
        var k := s / ember_life
        var ember_color := _energy_color(0.2) if energy else Color("ff9c48")
        for i in range(int(12.0 * strength)):
            var direction := Vector2.from_angle(_rand(offset + 110 + i) * TAU)
            var lift := r * (0.3 + 0.9 * _rand(offset + 130 + i)) * sin(minf(1.0, k * 1.3) * PI * 0.5)
            var position := origin + direction * r * (0.3 + 0.9 * _rand(offset + 120 + i)) * Painter.ease_out(k * 1.4) * Vector2(1.0, 0.7) + Vector2(0.0, -lift)
            var flicker := 0.55 + 0.45 * sin(age * 29.0 + float(i) * 1.7)
            _paint.dot(position, 1.6 + 1.8 * _rand(offset + 140 + i), Color(ember_color.lightened(0.4), (1.0 - k) * flicker))
            _paint.dot(position, 5.0, Color(ember_color, 0.32 * (1.0 - k) * flicker))
    # Debris thrown up and falling: glowing chunks give light, dark ones sit over the smoke.
    var debris_life := 0.95
    if s < debris_life and (fuel or kind == "MORTAR" or kind == "SLAM"):
        var k := s / debris_life
        for i in range(int(9.0 * strength)):
            var direction := Vector2.from_angle(_rand(offset + 150 + i) * TAU) * Vector2(1.0, 0.6) + Vector2(0.0, -0.6)
            var distance := r * (0.6 + 1.0 * _rand(offset + 160 + i))
            var position := origin + direction * distance * Painter.ease_out(k * 1.2) + Vector2(0.0, r * 1.5 * k * k)
            var spin := _rand(offset + 170 + i) * TAU + k * (5.0 + 6.0 * _rand(offset + 180 + i))
            var chunk := (3.0 + 5.0 * _rand(offset + 190 + i)) * size
            if fuel and i % 3 == 0:
                _paint.shard(position, spin, chunk, Color(HIT.fire_color(k * 0.8), 1.0 - k))
            else:
                _smoke.shard(position, spin, chunk, Color(0.1, 0.09, 0.09, 0.95 * (1.0 - k * k)))
    # A slam or a shell landing cracks the floor with light for a moment.
    if kind == "SLAM" or kind == "MORTAR":
        var crack := Painter.fade_window(s, 0.12, 0.7)
        if crack > 0.0:
            for i in range(6):
                var direction := Vector2.from_angle(_rand(offset + 240 + i) * TAU)
                var tip := origin + direction * r * (0.55 + 0.35 * _rand(offset + 250 + i)) * Painter.ease_out(minf(1.0, s * 9.0)) * Vector2(1.0, 0.62)
                _paint.bolt(origin, tip, 4, r * 0.09, 1.4 * size, Color(_energy_color(0.08), 0.8 * crack), _seed + offset + i)

## Dust thrown out along the floor by the blast front (at the feet for a body's blast).
func _floor_dust(origin: Vector2, r: float, s: float, grow: float) -> void:
    var dust_time := 0.9 * grow
    if s >= dust_time:
        return
    var k := s / dust_time
    var floor_point := origin + (Vector2(0.0, r * 0.3) if kind in ["ROBOT_SMALL", "ROBOT_HEAVY", "BOSS"] else Vector2.ZERO)
    var shade := Color(0.46, 0.42, 0.38) if kind in FUEL_KINDS else Color(0.42, 0.42, 0.47)
    _smoke.ring(floor_point, r * (0.35 + 1.05 * Painter.ease_out(k)), r * 0.2 * (1.0 - 0.4 * k), Color(shade, 0.36 * (1.0 - k) * minf(1.0, k * 8.0)), 28, 0.0, TAU, 0.55)

## Smoke rising off the blast: lit from below by the fire at first, then grey, spreading.
func _smoke_column(origin: Vector2, r: float, s: float, offset: int, strength: float, grow: float, fuel: bool) -> void:
    var smoke_life := (2.0 if fuel else 1.2) * grow
    var fire_lit := Color(0.8, 0.42, 0.18) if fuel else _energy_color(0.3)
    for i in range(int((10.0 if fuel else 5.0) * strength)):
        var born := 0.05 + _rand(offset + 200 + i) * 0.22
        var k := (s - born) / smoke_life
        if k <= 0.0 or k >= 1.0:
            continue
        var direction := Vector2.from_angle(_rand(offset + 205 + i) * TAU)
        var spread := r * (0.2 + 0.6 * _rand(offset + 210 + i)) * Painter.ease_out(minf(1.0, k * 1.4))
        var rise := r * (0.25 + 1.0 * k) * (0.6 + 0.8 * _rand(offset + 215 + i))
        var position := origin + direction * spread * Vector2(1.0, 0.55) + Vector2(r * 0.25 * k * (_rand(offset + 218 + i) - 0.3), -rise)
        var radius_now := r * (0.26 + 0.18 * _rand(offset + 220 + i)) * (0.7 + 1.0 * Painter.ease_out(k))
        var shade := 0.36 + 0.12 * _rand(offset + 230 + i)
        var grey := Color(shade, shade * 0.97, shade * 0.95)
        if not fuel:
            grey = grey.lerp(color.darkened(0.3), 0.25)
        var alpha := (0.72 if fuel else 0.46) * minf(1.0, k * 6.0) * Painter.fade_window(k, 0.3, 1.0)
        var lit := grey.lightened(0.12).lerp(fire_lit, 0.85 * pow(maxf(0.0, 1.0 - k * 2.2), 1.5))
        _smoke.puff(position, radius_now, Color(grey.darkened(0.12), alpha), lit, 10)

## Fuel fireball: puffs that swell, rise and cool from yellow-white through orange to dark
## red, under an additive heat bloom.
func _fireball(origin: Vector2, r: float, s: float, offset: int, strength: float, grow: float) -> void:
    var fire_time := 0.7 * grow
    for i in range(int(9.0 * strength)):
        var born := 0.0 if i == 0 else _rand(offset + 30 + i) * 0.12
        var k := (s - born) / fire_time
        if k <= 0.0 or k >= 1.0:
            continue
        var direction := Vector2.from_angle(_rand(offset + 40 + i) * TAU)
        var travel := r * (0.08 + 0.42 * _rand(offset + 50 + i)) * Painter.ease_out(minf(1.0, k * 1.8))
        var position := origin + direction * travel * Vector2(1.0, 0.7) + Vector2(0.0, -r * 0.5 * k * k)
        var blob := r * (0.28 + 0.2 * _rand(offset + 60 + i)) * (0.5 + 0.75 * Painter.ease_out(minf(1.0, k * 2.5)))
        var heat := clampf(k * 1.1 + 0.3 * (_rand(offset + 65 + i) - 0.5), 0.0, 1.0)
        var alpha := 0.96 * Painter.fade_window(k, 0.6, 1.0)
        # A darker, cooler billow behind each puff gives the fireball folds and depth.
        _smoke.puff(position + Vector2(blob * 0.14, blob * 0.2), blob * 1.05, Color(_cooling_fire(minf(1.0, heat + 0.4)), alpha * 0.9), Color(0, 0, 0, 0), 10)
        _smoke.puff(position, blob * 0.88, Color(_cooling_fire(heat), alpha), _cooling_fire(maxf(0.0, heat - 0.3)), 10)
        if k < 0.45:
            _smoke.puff(position + Vector2(0.0, -blob * 0.12), blob * 0.48, Color(_cooling_fire(maxf(0.0, heat - 0.35)), alpha * (1.0 - k / 0.45)), Color(0, 0, 0, 0), 8)
    var bloom := s / fire_time
    if bloom < 1.0:
        _paint.glow(origin + Vector2(0.0, -r * 0.25 * bloom), r * (0.8 + 0.5 * Painter.ease_out(bloom)), Color("ff8a3a", 0.5 * pow(1.0 - bloom, 1.5)), 14)

## Fire colour through the fireball's life: white-hot, orange, deep red, then the brown
## grey of the smoke it turns into, never a flat red haze.
func _cooling_fire(heat: float) -> Color:
    if heat < 0.55:
        return HIT.fire_color(heat / 0.55 * 0.62)
    return HIT.fire_color(0.62).lerp(Color(0.3, 0.25, 0.23), minf(1.0, (heat - 0.55) / 0.25))

## Energy blast body: a plasma bloom in the source's colour with arcs crawling out of it.
func _plasma(origin: Vector2, r: float, s: float, offset: int, strength: float, size: float) -> void:
    var plasma_time := 0.5 * sqrt(size)
    if s < plasma_time:
        var k := s / plasma_time
        _paint.glow(origin, r * (0.45 + 0.4 * Painter.ease_out(k)), Color(_energy_color(k * 0.8), 0.85 * pow(1.0 - k, 1.3)), 14)
        _paint.glow(origin, r * 0.22 * (1.0 - k * 0.5), Color(1.0, 1.0, 1.0, 0.8 * pow(1.0 - k, 2.0)), 10)
    var arc_time := 0.36
    if s < arc_time:
        var k := s / arc_time
        var strike := int(s * 22.0)
        for i in range(int(5.0 * strength)):
            var direction := Vector2.from_angle(_rand(offset + 260 + i + strike * 7) * TAU)
            var reach_now := r * (0.5 + 0.5 * _rand(offset + 270 + i + strike * 7))
            _paint.bolt(origin + direction * r * 0.12, origin + direction * reach_now * Vector2(1.0, 0.75), 5, r * 0.08, 1.3 * size, Color(_energy_color(0.05).lightened(0.25), 0.9 * (1.0 - k)), _seed + offset + i + strike * 13)

## Boss lane attack: a beam fired down the frozen warning lane, tearing up the floor
## from the emitter outward. Its ends taper so it never reads as a lit slab.
func _lane(s: float) -> void:
    var k := clampf(s / duration, 0.0, 1.0)
    var end := ray * reach
    var side := ray.orthogonal()
    var fade := pow(1.0 - k, 1.4)
    var hot := _energy_color(0.05)
    var width := radius * (1.3 - 0.9 * Painter.ease_out(k))
    var taper := minf(reach * 0.15, radius * 3.0)
    var a := ray * taper
    var b := end - ray * taper
    for layer in [[width * 2.4, Color(color, 0.42 * fade)], [width * 0.8, Color(hot, 0.95 * fade)], [width * 0.22, Color(1.0, 1.0, 1.0, fade * Painter.fade_window(k, 0.2, 0.6))]]:
        var w: float = layer[0]
        var c: Color = layer[1]
        _paint.fading_beam(Vector2.ZERO, a, w, c, 0.35, 1.0)
        _paint.fading_beam(a, b, w, c, 1.0, 1.0)
        _paint.fading_beam(b, end, w, c, 1.0, 0.0)
    for i in range(9):
        var along := reach * (float(i) + 0.5 + (_rand(300 + i) - 0.5) * 0.6) / 9.0
        var local := (s - 0.12 * along / maxf(1.0, reach)) / 0.5
        if local <= 0.0 or local >= 1.0:
            continue
        var at := ray * along + side * (_rand(320 + i) - 0.5) * radius * 1.2
        _paint.glow(at, radius * (1.0 + 1.4 * Painter.ease_out(local)), Color(hot, 0.55 * (1.0 - local) * (1.0 - local)), 8)
        _smoke.puff(at + Vector2(0.0, -radius * 1.5 * local), radius * (0.8 + 1.6 * Painter.ease_out(local)), Color(0.42, 0.42, 0.46, 0.45 * minf(1.0, local * 5.0) * (1.0 - local)), Color(0, 0, 0, 0), 8)
        var fling := (side * (1.0 if i % 2 == 0 else -1.0) + ray * (_rand(330 + i) - 0.3)).normalized()
        var out := fling * radius * (1.2 + 1.8 * _rand(310 + i)) * Painter.ease_out(minf(1.0, local * 2.5))
        _paint.streak(at + out * 0.3, at + out + Vector2(0.0, radius * 1.5 * local * local), 1.4, Color(hot.lightened(0.3), 1.0 - local), i < 3)
    _paint.glow(Vector2.ZERO, radius * 2.4, Color(_energy_color(0.0), 0.8 * Painter.fade_window(s, 0.0, 0.15)), 12)
    _paint.glow(end, radius * 2.2, Color(hot, 0.6 * fade), 10)
    _paint.flare(end, ray, radius * 3.0 * fade, 2.4, Color(_energy_color(0.0), 0.8 * fade))
    _paint.ring(end, radius * (0.8 + 2.4 * Painter.ease_out(minf(1.0, k * 2.0))), 3.0, Color(color, 0.7 * fade), 18)

## A damaged robot leaking smoke, lit orange as it leaves the hull, with the odd spark.
func _smolder(s: float) -> void:
    var k := s / duration
    for i in range(3):
        var local := (s - float(i) * 0.18) / 0.9
        if local <= 0.0 or local >= 1.0:
            continue
        var position := Vector2((_rand(400 + i) - 0.5) * radius * 0.8 + radius * 0.4 * local, -radius * 1.8 * local)
        var shade := 0.36 + 0.1 * _rand(405 + i)
        var grey := Color(shade, shade * 0.97, shade * 0.95)
        var alpha := 0.55 * Painter.fade_window(local, 0.25, 1.0) * minf(1.0, local * 5.0)
        _smoke.puff(position, radius * (0.4 + 0.9 * local), Color(grey, alpha), grey.lerp(Color(0.62, 0.32, 0.15), maxf(0.0, 1.0 - local * 3.0)), 8)
    var heat := Painter.fade_window(k, 0.0, 0.45)
    if heat > 0.0:
        _paint.glow(Vector2.ZERO, radius * 0.9, Color("ff8a3a", 0.35 * heat), 8)
    if _rand(410) < 0.7 and k < 0.35:
        var direction := Vector2.from_angle(-PI * 0.5 + (_rand(420) - 0.5) * 2.2)
        var spark_k := k / 0.35
        var head := direction * radius * 1.2 * Painter.ease_out(spark_k) + Vector2(0.0, radius * 0.8 * spark_k * spark_k)
        _paint.streak(head - direction * radius * 0.35, head, 1.3, Color(color.lightened(0.4), 1.0 - spark_k), true)

## The CINDER ram's thruster wake along the path it charged.
func _ram_trail(s: float) -> void:
    if _trail.size() < 1:
        return
    var fade := Painter.fade_window(s, duration - 0.4, duration)
    var count := _trail.size()
    var points := PackedVector2Array()
    var outer := PackedFloat32Array()
    var inner := PackedFloat32Array()
    var alphas := PackedFloat32Array()
    for i in range(count):
        var f := float(i + 1) / float(count)
        points.append(to_local(_trail[i]))
        outer.append(10.0 + 14.0 * f)
        inner.append(3.0 + 3.5 * f)
        alphas.append(f)
    _paint.ribbon(points, outer, Color(color, 0.6 * fade), alphas)
    _paint.ribbon(points, inner, Color(1.0, 0.85, 0.6, 0.95 * fade), alphas)
    var head := to_local(_trail[count - 1])
    if is_instance_valid(follow) and s < duration - 0.35:
        var flicker := 0.75 + 0.25 * sin(age * 50.0)
        _paint.glow(head, 26.0 * flicker, Color(color.lightened(0.2), 0.6), 10)
        for i in range(4):
            var back := (to_local(_trail[maxi(0, count - 3)]) - head).normalized() if count > 2 else Vector2.LEFT
            var spray := back.rotated((_rand(500 + i + int(age * 20.0)) - 0.5) * 1.2) * (26.0 + 30.0 * _rand(510 + i + int(age * 20.0)))
            _paint.streak(head, head + spray, 1.8, Color(1.0, 0.8, 0.5, 0.8), true)
    for i in range(count):
        if i % 3 != 0:
            continue
        var at := to_local(_trail[i]) + Vector2(0.0, 22.0)
        var puff := 12.0 + 18.0 * minf(1.0, s * 2.0)
        _smoke.glow(at, puff, Color(0.2, 0.17, 0.15, 0.3 * fade * float(i + 1) / float(count)), 8)

## Energy blasts run white -> the source colour -> its dark shade instead of fire colours.
func _energy_color(k: float) -> Color:
    if k < 0.12:
        return Color(1.0, 1.0, 1.0).lerp(color.lightened(0.35), k / 0.12)
    if k < 0.55:
        return color.lightened(0.35).lerp(color, (k - 0.12) / 0.43)
    return color.lerp(color.darkened(0.55), (k - 0.55) / 0.45)

func _rand(index: int) -> float:
    return _noise[(_seed * 7919 + index) & (Painter.NOISE_SIZE - 1)]

func debug_contract() -> Dictionary:
    return {"kind": kind, "radius": radius, "duration": duration, "age": age,
        "light": is_instance_valid(_light), "smoke_layer": _smoke_layer.is_valid(),
        "triangles": _paint.triangle_count() + _smoke.triangle_count()}


## Scorch left on the floor by a blast, drawn under every body and cover prop.
class GroundMark extends Node2D:
    const P := preload("res://scripts/vfx/vfx_painter.gd")
    const LIFE := 4.5
    var radius := 60.0
    var tint := Color("ff8a3d")
    var age := 0.0
    var _paint := P.new()
    var _glow := P.new()
    var _glow_layer := RID()
    var _seed := 0

    func setup(radius_value: float, color: Color) -> void:
        radius = radius_value
        tint = color
        _seed = int(get_instance_id()) % 100003
        # Above the floor art (-100), floor guide (-60) and body shadows (-50/-40); below
        # hazards and attack warnings (-2), so a warning is never hidden by old scorch.
        z_index = -30
        queue_redraw()

    func _ready() -> void:
        add_to_group("vfx_ground_marks")
        _glow_layer = P.make_layer(self, true)
        # Keep only the newest dozen scorches; older ones hurry to fade out.
        var marks := get_tree().get_nodes_in_group("vfx_ground_marks")
        if marks.size() > 12:
            for i in range(marks.size() - 12):
                var old: Node = marks[i]
                if old != self and old.get("age") != null:
                    old.set("age", maxf(float(old.get("age")), LIFE - 0.6))

    func _notification(what: int) -> void:
        if what == NOTIFICATION_PREDELETE:
            P.free_layer(_glow_layer)
            _glow_layer = RID()

    func _process(delta: float) -> void:
        age += delta
        if age >= LIFE:
            queue_free()
            return
        # Only the hot rim changes quickly; after it cools, redraw a few times a second.
        if age < 2.2 or Engine.get_process_frames() % 6 == 0:
            queue_redraw()

    func _draw() -> void:
        _paint.clear()
        _glow.clear()
        var fade := P.fade_window(age, LIFE - 1.6, LIFE)
        var appear := minf(1.0, age * 10.0)
        # A few overlapping blotches, so the scorch is never a clean ellipse.
        for i in range(3):
            var offset := Vector2(P.rand(_seed, 20 + i) - 0.5, (P.rand(_seed, 30 + i) - 0.5) * 0.62) * radius * 0.45
            var size := radius * (0.62 + 0.35 * P.rand(_seed, 40 + i))
            _paint.ellipse_glow(offset, Vector2(size, size * 0.62), Color(0.03, 0.025, 0.02, 0.6 * fade * appear), 12)
        for i in range(5):
            var angle := P.rand(_seed, i) * TAU
            var length := radius * (0.55 + 0.4 * P.rand(_seed, 10 + i))
            var tip := Vector2.from_angle(angle) * length * Vector2(1.0, 0.62)
            _paint.fading_beam(Vector2.ZERO, tip, 3.0, Color(0.02, 0.018, 0.015, 0.5 * fade * appear), 1.0, 0.0)
        var heat := P.fade_window(age, 0.0, 1.1)
        if heat > 0.0:
            _glow.ellipse_glow(Vector2.ZERO, Vector2(radius * 0.62, radius * 0.38), Color(tint, 0.5 * heat), 12)
        var embers := P.fade_window(age, 0.3, 2.2)
        if embers > 0.0:
            for i in range(8):
                var at := Vector2.from_angle(P.rand(_seed, 50 + i) * TAU) * radius * (0.15 + 0.6 * P.rand(_seed, 60 + i)) * Vector2(1.0, 0.62)
                var flicker := 0.55 + 0.45 * sin(age * (9.0 + 7.0 * P.rand(_seed, 70 + i)) + float(i))
                _glow.dot(at, 2.0 + 2.5 * P.rand(_seed, 80 + i), Color(tint.lightened(0.35), embers * flicker), 6)
                _glow.dot(at, 7.0, Color(tint, 0.3 * embers * flicker), 6)
        _paint.flush(get_canvas_item())
        if _glow_layer.is_valid():
            RenderingServer.canvas_item_clear(_glow_layer)
            _glow.flush(_glow_layer)
