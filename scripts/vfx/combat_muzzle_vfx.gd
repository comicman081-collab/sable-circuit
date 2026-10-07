extends Node2D
class_name CombatMuzzleVFX
## Code-drawn muzzle flash at the actual projectile origin, and the charge glow a robot's
## emitter builds while it winds up an announced shot. A flash rides with its shooter for
## its few frames of life, so a strafing operator does not leave it hanging in the air.
## One flash per shooter per physics tick: ROOK's five pellets and a boss fan share one.

const Painter := preload("res://scripts/vfx/vfx_painter.gd")
const MODE_FLASH := "FLASH"
const MODE_CHARGE := "CHARGE"
const LIFE := {"ASTER": 0.075, "ROOK": 0.11, "MICA": 0.1, "DRONE": 0.085, "BULWARK": 0.13,
    "PRISM": 0.09, "ANCHOR": 0.17, "RELAY": 0.16, "REMNANT": 0.16,
    "FORGE": 0.17, "CARRIER": 0.17, "AERATOR": 0.17, "CRYO": 0.16, "GANTRY": 0.16, "ARCHIVE": 0.16,
    "ORIGIN": 0.17, "MORTAR": 0.22, "GENERIC": 0.08, "WEAPON_RAIL": 0.09, "WEAPON_NULL": 0.12}
## Robots the charge glow draws at boss size.
const BOSS_FAMILIES := ["ANCHOR", "RELAY", "REMNANT", "FORGE", "CARRIER",
    "AERATOR", "CRYO", "GANTRY", "ARCHIVE", "ORIGIN"]

static var _last_flash_tick := {}

var mode := MODE_FLASH
var family := "GENERIC"
var color := Color.WHITE
var axis := Vector2.RIGHT
var age := 0.0
var life := 0.08
var shooter: Node2D
var _offset := Vector2.ZERO
var _seed := 0
var _paint := Painter.new()
var _noise := Painter.noise()
# Charge mode: the robot whose emitter glows, and the warning it is winding up.
var _charge_enemy: Node2D
var _released := false

func _init() -> void:
    material = Painter.additive_material()

static func family_for(profile: String) -> String:
    var id := profile.to_upper()
    if "WEAPON_RAIL" in id: return "WEAPON_RAIL"
    if "WEAPON_NULL" in id: return "WEAPON_NULL"
    if "ASTER" in id: return "ASTER"
    if "ROOK" in id: return "ROOK"
    if "MICA" in id: return "MICA"
    if "DRONE" in id: return "DRONE"
    if "SHIELD" in id or "BULWARK" in id: return "BULWARK"
    if "PRISM" in id: return "PRISM"
    if "FORGE" in id: return "FORGE"
    if "CARRIER" in id: return "CARRIER"
    if "RELAY" in id: return "RELAY"
    if "REMNANT" in id: return "REMNANT"
    if "AERATOR" in id: return "AERATOR"
    if "CRYO" in id: return "CRYO"
    if "GANTRY" in id: return "GANTRY"
    if "ARCHIVE" in id: return "ARCHIVE"
    if "ORIGIN" in id: return "ORIGIN"
    if "ANCHOR" in id: return "ANCHOR"
    if "MORTAR" in id: return "MORTAR"
    return "GENERIC"

## A flash at `origin` along `direction`; `owner_node` both dedupes a volley and carries it.
static func spawn(tree: SceneTree, origin: Vector2, direction: Vector2, profile: String, tint: Color, owner_node: Node = null) -> CombatMuzzleVFX:
    if tree == null or tree.root == null:
        return null
    if is_instance_valid(owner_node):
        var key := owner_node.get_instance_id()
        var tick := Engine.get_physics_frames()
        if int(_last_flash_tick.get(key, -1)) == tick:
            return null
        if _last_flash_tick.size() > 512:
            _last_flash_tick.clear()
        _last_flash_tick[key] = tick
    var fx := CombatMuzzleVFX.new()
    tree.root.add_child(fx)
    fx.global_position = origin
    fx.setup(profile, tint, direction, owner_node as Node2D)
    return fx

## The glow a robot's emitter builds through its WINDUP; it fades if the warning is
## cancelled and releases into nothing (the real shot brings its own flash).
static func spawn_charge(tree: SceneTree, enemy: Node2D, profile: String, tint: Color, windup: float) -> CombatMuzzleVFX:
    if tree == null or tree.root == null or not is_instance_valid(enemy):
        return null
    var fx := CombatMuzzleVFX.new()
    tree.root.add_child(fx)
    fx.mode = MODE_CHARGE
    fx.family = family_for(profile)
    fx.color = tint
    fx.life = maxf(0.1, windup)
    fx._charge_enemy = enemy
    fx._seed = int(fx.get_instance_id()) % 100003
    fx.z_index = 3050
    fx._follow_charge()
    return fx

func setup(profile: String, tint: Color, direction: Vector2, owner_node: Node2D = null) -> void:
    mode = MODE_FLASH
    family = family_for(profile)
    color = tint
    axis = direction.normalized() if direction.length_squared() > 0.0001 else Vector2.RIGHT
    if family == "MORTAR":
        axis = Vector2.UP
    life = float(LIFE[family])
    age = 0.0
    _seed = int(get_instance_id()) % 100003
    z_index = 3050
    shooter = owner_node
    if is_instance_valid(shooter):
        _offset = global_position - shooter.global_position
    queue_redraw()

func _process(delta: float) -> void:
    age += delta
    if mode == MODE_CHARGE:
        _follow_charge()
    elif is_instance_valid(shooter):
        global_position = shooter.global_position + _offset
    if age >= life:
        queue_free()
        return
    queue_redraw()

func _follow_charge() -> void:
    if not is_instance_valid(_charge_enemy) or float(_charge_enemy.get("health")) <= 0.0:
        _released = true
        age = maxf(age, life - 0.06)
        return
    var tactics: Variant = _charge_enemy.get("tactics")
    if tactics == null or str(tactics.get("state")) != "WINDUP":
        # Stagger or a fired shot ends the charge; let it vanish over two frames.
        if not _released:
            _released = true
            age = maxf(age, life - 0.05)
        return
    var aim: Vector2 = tactics.get("locked_aim")
    axis = aim
    if _charge_enemy.has_method("projectile_origin"):
        global_position = _charge_enemy.call("projectile_origin", aim)
    else:
        global_position = _charge_enemy.global_position

func _draw() -> void:
    _paint.clear()
    if mode == MODE_CHARGE:
        _draw_charge(clampf(age / life, 0.0, 1.0))
    else:
        _draw_flash(clampf(age / life, 0.0, 1.0))
    _paint.flush(get_canvas_item())

func _draw_flash(t: float) -> void:
    var a := axis
    var side := a.orthogonal()
    var fade := 1.0 - t
    var pop := 0.7 + 0.3 * Painter.ease_out(t * 4.0)
    match family:
        "WEAPON_RAIL":
            # A compact twin accelerator fork, unlike a boss rail's broad bar.
            for sign_value in [-1.0,1.0]:
                _paint.streak(side * sign_value * 4.0, a * 38.0 * pop + side * sign_value * 4.0, 1.4, Color("b9f7ff",fade), true)
            _paint.streak(Vector2.ZERO,a * 50.0 * pop,1.8,Color(1,1,1,fade),true)
            _paint.glow(a * 7.0,12.0,Color("62d9ef",fade * 0.6))
        "WEAPON_NULL":
            # Three separated square-ended lobes follow the three-pellet volley.
            for i in range(3):
                var ray := a.rotated((float(i)-1.0)*0.32)
                _paint.streak(ray * 7.0,ray * 30.0 * pop,4.0,Color("ffd8ed",fade),true)
            _paint.oval_ring(a * (5.0+10.0*t),Vector2(5.0,15.0),a.angle(),2.0,Color("d68eb5",fade))
            _paint.glow(a * 4.0,14.0,Color("ffffff",fade * 0.65))
        "ASTER":
            # Coil rifle: a tight cyan cone through two accelerator rings, gold at the tip.
            _cone(a, 26.0 * pop, 7.0, Color(0.5, 0.9, 1.0, 0.8 * fade))
            _paint.glow(a * 3.0, 11.0 * pop, Color(0.85, 0.97, 1.0, 0.9 * fade), 8)
            _paint.streak(Vector2.ZERO, a * 42.0 * pop, 3.2 * fade + 0.8, Color(0.62, 0.92, 1.0, fade), true)
            _paint.streak(a * 30.0 * pop, a * 46.0 * pop, 2.0, Color(1.0, 0.82, 0.45, fade), true)
            for i in range(2):
                _paint.oval_ring(a * (7.0 + 9.0 * float(i) + 8.0 * t), Vector2(3.0, 8.0 + 3.0 * float(i) + 6.0 * t), a.angle(), 1.4, Color(0.6, 0.55, 1.0, 0.85 * fade))
            _petals(a, 2, 0.95, 13.0 * pop, 1.8, Color(0.55, 0.88, 1.0, 0.8 * fade))
            _sparks(a, 3, 0.9, 22.0, t, Color(0.75, 0.95, 1.0, fade))
        "ROOK":
            # Scattergun: a wide orange blast with a white heart, petals and a spray of sparks.
            _cone(a, 34.0 * pop, 16.0, Color(1.0, 0.62, 0.24, 0.75 * fade))
            _paint.glow(a * 8.0, 24.0 * pop, Color(1.0, 0.7, 0.3, 0.6 * fade))
            _paint.glow(a * 4.0, 11.0 * pop, Color(1.0, 0.96, 0.85, 0.95 * fade), 8)
            for i in range(5):
                var petal := a.rotated((float(i) - 2.0) * 0.26)
                var length := (36.0 if i == 2 else 22.0 + 10.0 * _rand(i)) * pop
                _paint.streak(Vector2.ZERO, petal * length, 5.0 * fade + 1.0, Color(1.0, 0.82, 0.45, fade), i == 2)
            _petals(a, 2, 1.35, 16.0 * pop, 3.0, Color(1.0, 0.7, 0.35, 0.8 * fade))
            _sparks(a, 7, 1.3, 46.0, t, Color(1.0, 0.85, 0.55, fade))
        "MICA":
            # Pulse carbine: a mint cone and a small pulse ring leaving the muzzle.
            _cone(a, 24.0 * pop, 8.0, Color(0.4, 1.0, 0.86, 0.75 * fade))
            _paint.glow(a * 4.0, 10.0 * pop, Color(0.85, 1.0, 0.97, 0.9 * fade), 8)
            _paint.oval_ring(a * (6.0 + 14.0 * t), Vector2(3.0 + 2.0 * t, 7.0 + 7.0 * Painter.ease_out(t)), a.angle(), 1.8, Color(0.55, 1.0, 0.9, fade))
            _paint.flare(a * 5.0, a, 22.0 * fade + 6.0, 2.0, Color(0.8, 1.0, 0.96, fade), 0.45)
            _sparks(a, 3, 0.8, 20.0, t, Color(0.6, 1.0, 0.92, fade))
        "DRONE":
            _cone(a, 24.0 * pop, 8.0, Color(0.95, 0.35, 0.65, 0.75 * fade))
            _paint.glow(Vector2.ZERO, 10.0 * pop, Color(0.8, 0.98, 1.0, 0.85 * fade), 8)
            _paint.streak(Vector2.ZERO, a * 30.0 * pop, 2.6, Color(0.6, 0.97, 1.0, fade), true)
            _petals(a, 2, 1.0, 12.0 * pop, 1.8, Color(1.0, 0.5, 0.8, 0.85 * fade))
            _sparks(a, 3, 0.9, 20.0, t, Color(1.0, 0.6, 0.85, fade))
        "BULWARK":
            _cone(a, 44.0 * pop, 18.0, Color(1.0, 0.64, 0.24, 0.75 * fade))
            _paint.glow(a * 10.0, 28.0 * pop, Color(1.0, 0.7, 0.28, 0.6 * fade))
            _paint.glow(a * 5.0, 13.0 * pop, Color(1.0, 0.95, 0.8, 0.95 * fade), 8)
            for i in range(3):
                var petal := a.rotated((float(i) - 1.0) * 0.3)
                _paint.streak(Vector2.ZERO, petal * (50.0 if i == 1 else 32.0) * pop, 7.0 * fade + 1.5, Color(1.0, 0.86, 0.5, fade), i == 1)
            _petals(a, 2, 1.45, 20.0 * pop, 3.0, Color(1.0, 0.7, 0.35, 0.75 * fade))
            _sparks(a, 6, 1.1, 50.0, t, Color(1.0, 0.85, 0.5, fade))
        "PRISM":
            var spectrum := [Color("ff6fd8"), Color("8a7bff"), Color("6fe7ff")]
            _cone(a, 26.0 * pop, 9.0, Color(0.62, 0.55, 1.0, 0.7 * fade))
            _paint.glow(Vector2.ZERO, 10.0 * pop, Color(0.92, 0.9, 1.0, 0.85 * fade), 8)
            for i in range(3):
                _paint.streak(Vector2.ZERO, a.rotated((float(i) - 1.0) * 0.22) * 34.0 * pop, 2.2, Color(spectrum[i], fade), i == 1)
            _sparks(a, 3, 1.0, 22.0, t, Color(0.85, 0.8, 1.0, fade))
        "RELAY":
            _cone(a, 48.0 * pop, 13.0, Color(color, 0.75 * fade))
            _paint.glow(a * 4.0, 26.0 * pop, Color("ff6472", 0.65 * fade))
            _paint.streak(a * -12.0, a * 52.0 * pop, 3.0, Color("ffe4e7", fade), true)
            _sparks(a, 5, 0.9, 48.0, t, Color("ff9ca6", fade))
        "REMNANT":
            _paint.glow(Vector2.ZERO, 29.0 * pop, Color(color, 0.65 * fade))
            for fork in [-1.0, 1.0]:
                _paint.streak(side * fork * 8.0, a * 54.0 * pop + side * fork * 5.0, 2.3, Color("f1fbff", fade), true)
            _paint.flare(a * 7.0, a, 40.0 * pop, 2.0, Color("ffffff", fade), 0.55)
        "AERATOR":
            # Spore volley: a lime puff, five petals open at the bud and spores drifting off.
            var hot := color.lightened(0.45)
            _cone(a, 54.0 * pop, 18.0, Color(color, 0.65 * fade))
            _paint.glow(a * 8.0, 32.0 * pop, Color(color, 0.5 * fade))
            _paint.glow(a * 6.0, 14.0 * pop, Color(1.0, 1.0, 0.9, 0.85 * fade), 10)
            for i in range(5):
                var petal := a.rotated((float(i) - 2.0) * 0.42)
                _paint.streak(Vector2.ZERO, petal * (44.0 if i == 2 else 30.0 + 10.0 * _rand(30 + i)) * pop, 5.0 * fade + 1.2, Color(hot, fade), i == 2)
            for i in range(5):
                var drift := a.rotated((_rand(60 + i) - 0.5) * 1.6) * (14.0 + 40.0 * _rand(70 + i)) * Painter.ease_out(t * 1.3)
                _paint.dot(drift + Vector2(0.0, -10.0 * t), 3.2, Color(hot, 0.9 * fade))
        "CRYO":
            # Ice volley: a pale-pink cone, two long splinters and a frost ring.
            var hot := color.lightened(0.45)
            _cone(a, 52.0 * pop, 13.0, Color(color, 0.65 * fade))
            _paint.glow(a * 6.0, 28.0 * pop, Color(color, 0.5 * fade))
            for fork in [-1.0, 1.0]:
                _paint.streak(a * 2.0, a.rotated(0.2 * fork) * 68.0 * pop, 3.0 * fade + 1.0, Color("fff0fa", fade), true)
            _paint.ring(a * 6.0, 8.0 + 20.0 * Painter.ease_out(t), 2.4 * fade + 0.5, Color(hot, 0.85 * fade), 16)
            _sparks(a, 6, 1.1, 54.0, t, Color("ffd4ee", fade))
        "GANTRY":
            # Rail shot: a flat flash along the shot between two rails.
            _paint.flare(a * 8.0, a, 62.0 * pop, 3.4, Color("fff4b0", fade), 0.5)
            _paint.glow(a * 6.0, 30.0 * pop, Color(color, 0.6 * fade))
            for rail in [-1.0, 1.0]:
                _paint.streak(side * rail * 6.0, a * 56.0 * pop + side * rail * 6.0, 2.0, Color("ffe16b", fade), true)
            _sparks(a, 6, 0.9, 56.0, t, Color("fff2a0", fade))
        "ARCHIVE":
            # Echo packet: a teal flash and a bracket that leaves the emitter.
            _cone(a, 44.0 * pop, 12.0, Color(color, 0.6 * fade))
            _paint.glow(a * 6.0, 26.0 * pop, Color(color, 0.5 * fade))
            _paint.polygon_outline(a * (10.0 + 24.0 * t), 9.0 + 6.0 * t, 4, a.angle() + PI * 0.25, 1.8, Color("c8fff0", 0.9 * fade))
            _sparks(a, 5, 1.0, 46.0, t, Color("c8fff0", fade))
        "ORIGIN":
            # Null bolt: a white heart with hairline cracks thrown sideways.
            _paint.glow(a * 6.0, 30.0 * pop, Color(color, 0.55 * fade))
            _paint.glow(a * 5.0, 15.0 * pop, Color(1.0, 1.0, 1.0, 0.95 * fade), 10)
            for i in range(3):
                var crack := a.rotated((float(i) - 1.0) * 0.9)
                _paint.bolt(Vector2.ZERO, crack * 46.0 * pop, 3, 5.0, 1.4, Color("ffffff", 0.85 * fade), _seed + i)
            _paint.flare(a * 6.0, a, 46.0 * pop, 2.2, Color("ffffff", fade), 0.5)
            _sparks(a, 6, 1.2, 54.0, t, Color("ffffff", fade))
        "ANCHOR", "FORGE", "CARRIER":
            # Boss lance: a heavy plasma cone and petals, a tight shock ring at the emitter.
            var hot := color.lightened(0.45)
            _cone(a, 62.0 * pop, 20.0, Color(color, 0.7 * fade))
            _paint.glow(a * 8.0, 34.0 * pop, Color(color, 0.55 * fade))
            _paint.glow(a * 6.0, 15.0 * pop, Color(1.0, 1.0, 1.0, 0.9 * fade), 10)
            for i in range(5):
                var petal := a.rotated((float(i) - 2.0) * 0.28)
                _paint.streak(Vector2.ZERO, petal * (74.0 if i == 2 else 38.0 + 12.0 * _rand(30 + i)) * pop, 6.0 * fade + 1.5, Color(hot, fade), i == 2)
            _paint.ring(a * 6.0, 8.0 + 22.0 * Painter.ease_out(t), 3.0 * fade + 0.5, Color(hot, 0.9 * fade), 18)
            _sparks(a, 6, 1.2, 58.0, t, Color(hot, fade))
        "MORTAR":
            _paint.glow(Vector2(0.0, -12.0), 26.0 * pop, Color(color.lightened(0.3), 0.8 * fade))
            _paint.streak(Vector2(0.0, 8.0), Vector2(0.0, -64.0 * pop), 7.0 * fade + 1.0, Color(color.lightened(0.5), fade), true)
            _paint.oval_ring(Vector2(0.0, 4.0), Vector2(10.0 + 34.0 * Painter.ease_out(t), 5.0 + 14.0 * Painter.ease_out(t)), 0.0, 3.0, Color(color.lightened(0.2), 0.8 * fade))
            _paint.glow(Vector2(0.0, -30.0 - 20.0 * t), 22.0 + 20.0 * t, Color(0.5, 0.42, 0.6, 0.3 * fade))
            _sparks(Vector2.UP, 5, 0.9, 50.0, t, Color(color.lightened(0.4), fade))
        _:
            _cone(a, 22.0 * pop, 8.0, Color(color, 0.7 * fade))
            _paint.glow(Vector2.ZERO, 10.0 * pop, Color(color.lightened(0.5), 0.8 * fade), 8)
            _paint.streak(Vector2.ZERO, a * 28.0 * pop, 3.0, Color(color.lightened(0.4), fade), true)

## The flash's body: a soft teardrop reaching `length` along the shot.
func _cone(a: Vector2, length: float, width: float, color: Color) -> void:
    _paint.ellipse_glow(a * length * 0.42, Vector2(length * 0.62, width), color, 12, a.angle())

## Side petals, `count` a side at `spread` radians off the shot.
func _petals(a: Vector2, count: int, spread: float, length: float, width: float, color: Color) -> void:
    for i in range(count):
        var turn := spread * (0.6 + 0.4 * float(i) / maxf(1.0, float(count - 1)))
        for sign_value in [-1.0, 1.0]:
            var petal := a.rotated(turn * sign_value)
            _paint.streak(petal * 2.0, petal * length * (1.0 - 0.3 * float(i)), width, color)

## Sparks thrown forward in a cone of `spread` radians, sagging as they fly.
func _sparks(a: Vector2, count: int, spread: float, reach: float, t: float, color: Color) -> void:
    for i in range(count):
        var direction := a.rotated((_rand(40 + i) - 0.5) * spread)
        var distance := reach * (0.5 + 0.5 * _rand(50 + i))
        var k := Painter.ease_out(t * 1.4)
        var head := direction * distance * k + Vector2(0.0, 10.0 * t * t)
        var tail := direction * distance * maxf(0.0, k - 0.25)
        _paint.streak(tail, head, 1.2, color, i == 0)

## Emitter charge: a swelling core, energy drawn in from around it, and a thin sight
## line that brightens as the shot nears (the same frozen ray the warning shows).
func _draw_charge(t: float) -> void:
    var build := Painter.ease_in(t)
    var fade := 1.0 if not _released else 0.4
    var hot := color.lightened(0.4)
    var boss := family in BOSS_FAMILIES
    var size := 1.8 if boss else (1.3 if family == "BULWARK" or family == "MORTAR" else 1.0)
    _paint.glow(Vector2.ZERO, (8.0 + 16.0 * build) * size, Color(color, (0.35 + 0.5 * build) * fade))
    _paint.glow(Vector2.ZERO, (3.0 + 6.0 * build) * size, Color(1.0, 1.0, 1.0, (0.4 + 0.6 * build) * fade))
    var motes := 6 if boss else 4
    for i in range(motes):
        var cycle := fposmod(age * 2.2 + _rand(i), 1.0)
        var angle := _rand(10 + i) * TAU + age * 1.5
        var distance := (34.0 * size) * (1.0 - cycle)
        var head := Vector2.from_angle(angle) * distance
        _paint.streak(Vector2.from_angle(angle) * (distance + 10.0 * size), head, 1.4, Color(hot, (0.3 + 0.7 * build) * cycle * fade))
    if boss:
        _paint.ring(Vector2.ZERO, (40.0 - 26.0 * build) * size * 0.6, 2.0, Color(hot, 0.7 * build * fade), 18)
    if t > 0.75 and int(age * 30.0) % 2 == 0:
        _paint.flare(Vector2.ZERO, axis, 22.0 * size, 1.6, Color(hot, 0.8 * fade), 0.7)

func _rand(index: int) -> float:
    return _noise[(_seed * 7919 + index) & (Painter.NOISE_SIZE - 1)]

func debug_contract() -> Dictionary:
    return {"mode": mode, "family": family, "life": life, "age": age, "released": _released}
