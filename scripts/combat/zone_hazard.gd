extends Node2D
class_name ZoneHazard
## A room hazard (data/progression/zone_hazards.json). ARC_VENT is a floor grate that
## idles, crackles through its telegraph, then discharges once into every operator and
## robot standing on it. Like the other area attacks it ignores cover. Drawn in code on
## the floor as an ellipse; the hit test uses the same ellipse.

const DATA_PATH := "res://data/progression/zone_hazards.json"
const SFX := preload("res://scripts/audio/combat_sfx_bank.gd")
## Floor ellipse height relative to its width, matching the room plates' viewing angle.
const FLOOR_RATIO := 0.55
## Clearance AI operators keep from a vent's rim, and how early before the telegraph they react.
const SAFE_MARGIN := 24.0
const REACT_LEAD := 0.6
enum Phase { IDLE, TELEGRAPH, DISCHARGE }

static var _table: Dictionary = {}

var hazard_id := ""
var spec: Dictionary = {}
var color := Color.WHITE
var radius := 70.0
var phase := Phase.IDLE
var phase_left := 0.0
var discharges := 0
var last_hits: Array[String] = []
var _crackle := RandomNumberGenerator.new()
var _painter := VfxPainter.new()
var _age := 0.0
var _slowed: Dictionary = {}

func is_band() -> bool:
    return str(spec.get("shape", "ellipse")) == "band"

func is_slowing() -> bool:
    return str(spec.get("mode", "burst")) == "slow"

func _band_angle() -> float:
    return deg_to_rad(float(spec.get("angle_degrees", -26.565051177)))

func _slow_token() -> String:
    return "HAZARD_%s_%d" % [hazard_id, get_instance_id()]

static func table() -> Dictionary:
    if _table.is_empty():
        var parsed = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
        _table = (parsed.get("hazards", {}) as Dictionary) if parsed is Dictionary else {}
    return _table

## A hazard at `at` (stage space). `index` staggers the first discharge so a room's vents
## never fire together. Unknown ids return null.
static func create(id_value: String, at: Vector2, index: int) -> ZoneHazard:
    var key := id_value.strip_edges().to_upper()
    if not table().has(key): return null
    var hazard := ZoneHazard.new()
    hazard.name = "ZoneHazard%d" % index
    hazard.hazard_id = key
    hazard.spec = table()[key]
    hazard.color = Color(str(hazard.spec.get("color", "ffffff")))
    hazard.radius = float(hazard.spec.get("radius", 70.0))
    hazard.position = at
    hazard.phase_left = float(hazard.spec.get("first_delay", 2.4)) + float(index) * float(hazard.spec.get("phase_step", 1.35))
    hazard._crackle.seed = hash(key) + index
    return hazard

static func tip(id_value: String) -> String:
    return str(table().get(id_value.strip_edges().to_upper(), {}).get("tip", ""))

func _ready() -> void:
    z_index = -2
    add_to_group("zone_hazards")

func contains(point: Vector2, margin := 0.0) -> bool:
    if not point.is_finite(): return false
    if is_band():
        var local_band := (point - global_position).rotated(-_band_angle())
        return absf(local_band.x) <= float(spec.get("half_length", 90.0)) + margin and absf(local_band.y) <= float(spec.get("half_width", 24.0)) + margin
    var local := (point - global_position) / Vector2(radius + margin, radius * FLOOR_RATIO + margin)
    return local.length_squared() <= 1.0

## The painted/hit boundary in world space; placement and tests use the actual
## band rather than treating a rail's bounding circle as its damage shape.
func boundary_points(samples := 16, margin := 0.0) -> PackedVector2Array:
    var result := PackedVector2Array()
    if is_band():
        var half := Vector2(float(spec.get("half_length", 90.0)) + margin, float(spec.get("half_width", 24.0)) + margin)
        for corner: Vector2 in [Vector2(-half.x, -half.y), Vector2(half.x, -half.y), Vector2(half.x, half.y), Vector2(-half.x, half.y)]:
            result.append(global_position + corner.rotated(_band_angle()))
    else:
        for i in range(samples):
            result.append(global_position + Vector2.from_angle(TAU * float(i) / float(samples)) * Vector2(radius + margin, radius * FLOOR_RATIO + margin))
    return result

## True from shortly before the telegraph until the discharge lands.
func charging() -> bool:
    if is_slowing(): return phase == Phase.DISCHARGE
    if str(spec.get("mode", "burst")) == "continuous" and phase == Phase.DISCHARGE: return true
    return phase == Phase.TELEGRAPH or (phase == Phase.IDLE and phase_left <= REACT_LEAD)

## Where an AI operator heading for `goal` should go instead: a goal on a vent moves to its rim,
## and an operator standing on a vent that is about to discharge heads for the rim. Returns
## `goal` unchanged (INF included) when neither applies.
static func steer(tree: SceneTree, position: Vector2, goal: Vector2, stage: Node) -> Vector2:
    for node in tree.get_nodes_in_group("zone_hazards"):
        var vent := node as ZoneHazard
        if vent == null or vent.is_queued_for_deletion(): continue
        if vent.contains(goal, SAFE_MARGIN): return vent._rim_exit(goal, stage)
        if vent.charging() and vent.contains(position, SAFE_MARGIN): return vent._rim_exit(position, stage)
    return goal

## The nearest walkable point just outside the vent, leaving on the side `from` already lies.
func _rim_exit(from: Vector2, stage: Node) -> Vector2:
    if is_band(): return _band_exit(from, stage)
    var away := from - global_position
    if away.length_squared() < 1.0: away = Vector2.DOWN
    var semi := Vector2(radius + SAFE_MARGIN + 12.0, radius * FLOOR_RATIO + SAFE_MARGIN + 12.0)
    for turn in [0.0, PI * 0.5, -PI * 0.5, PI]:
        var d := away.normalized().rotated(turn)
        var point := global_position + d / sqrt(pow(d.x / semi.x, 2.0) + pow(d.y / semi.y, 2.0))
        if stage != null and stage.has_method("constrain_battle_position"):
            point = stage.call("constrain_battle_position", point)
        if not contains(point, SAFE_MARGIN): return point
    return from

func _band_exit(from: Vector2, stage: Node) -> Vector2:
    var local := (from - global_position).rotated(-_band_angle())
    var half := Vector2(float(spec.get("half_length", 90.0)), float(spec.get("half_width", 24.0))) + Vector2.ONE * (SAFE_MARGIN + 12.0)
    var candidates: Array[Vector2] = [Vector2(clampf(local.x, -half.x, half.x), half.y), Vector2(clampf(local.x, -half.x, half.x), -half.y),
        Vector2(half.x, clampf(local.y, -half.y, half.y)), Vector2(-half.x, clampf(local.y, -half.y, half.y))]
    candidates.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.distance_squared_to(local) < b.distance_squared_to(local))
    for candidate in candidates:
        var point := global_position + candidate.rotated(_band_angle())
        if stage != null and stage.has_method("constrain_battle_position"):
            point = stage.call("constrain_battle_position", point)
        if not contains(point, SAFE_MARGIN): return point
    return from

func _physics_process(delta: float) -> void:
    if hazard_id == "ARC_VENT":
        _arc_process(delta)
        return
    _age += delta
    if is_slowing():
        phase_left = maxf(0.0, phase_left - delta)
        if phase_left <= 0.0: phase = Phase.DISCHARGE
        _sync_slowing()
        queue_redraw()
        return
    # Integrate only the portion of a tick that actually lies in DISCHARGE.
    # A tick spanning the warning boundary never charges damage to the warning.
    var remaining := maxf(0.0, delta)
    while remaining > 0.000001:
        var step := minf(remaining, maxf(0.0, phase_left))
        if phase == Phase.DISCHARGE and str(spec.get("mode", "burst")) == "continuous": _continuous_damage(step)
        phase_left -= step
        remaining -= step
        if phase_left > 0.000001: break
        match phase:
            Phase.IDLE:
                phase = Phase.TELEGRAPH
                phase_left = float(spec.get("telegraph", 1.1))
                SFX.play(get_tree(), "shield_hit", self, global_position)
            Phase.TELEGRAPH:
                phase = Phase.DISCHARGE
                phase_left = float(spec.get("discharge", 0.3))
                if str(spec.get("mode", "burst")) == "continuous":
                    discharges += 1
                    last_hits.clear()
                    SFX.play(get_tree(), "boss_cross_beam", self, global_position)
                else: _discharge()
            _:
                phase = Phase.IDLE
                phase_left = float(spec.get("idle", 3.0))
        queue_redraw()
    if phase != Phase.IDLE: queue_redraw()

## Legacy ARC_VENT timing, phase carry and burst are deliberately unchanged.
func _arc_process(delta: float) -> void:
    phase_left -= delta
    while phase_left <= 0.0:
        match phase:
            Phase.IDLE:
                phase = Phase.TELEGRAPH
                phase_left += float(spec.get("telegraph", 1.1))
                SFX.play(get_tree(), "shield_hit", self, global_position)
            Phase.TELEGRAPH:
                phase = Phase.DISCHARGE
                phase_left += float(spec.get("discharge", 0.3))
                _discharge()
            _:
                phase = Phase.IDLE
                phase_left += float(spec.get("idle", 3.0))
        queue_redraw()
    if phase != Phase.IDLE: queue_redraw()

func _discharge() -> void:
    discharges += 1
    last_hits.clear()
    SFX.play(get_tree(), "boss_cross_beam", self, global_position)
    CombatFeedback.spawn_hit(get_tree(), global_position, {"hit_vfx_profile": "HIT_MICA_SCANBURST_01"}, color)
    for node in get_tree().get_nodes_in_group("operators"):
        var actor := node as OperatorActor
        if actor != null and not actor.is_downed() and contains(actor.global_position):
            actor.apply_damage(float(spec.get("operator_damage", 14.0)), "HAZARD_" + hazard_id)
            last_hits.append(actor.operator_id)
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        var enemy := node as EnemyActor
        if enemy != null and enemy.health > 0.0 and not enemy.enemy_id.begins_with("BOSS_") and contains(enemy.global_position):
            enemy.apply_damage(float(spec.get("enemy_damage", 24.0)), "HAZARD_" + hazard_id)
            last_hits.append(enemy.enemy_id)

func _continuous_damage(delta: float) -> void:
    if delta <= 0.0: return
    for node in get_tree().get_nodes_in_group("operators"):
        var actor := node as OperatorActor
        if actor != null and not actor.is_downed() and contains(actor.global_position):
            actor.apply_damage(float(spec.get("operator_dps", 0.0)) * delta, "HAZARD_" + hazard_id)
            if not actor.operator_id in last_hits: last_hits.append(actor.operator_id)
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        var enemy := node as EnemyActor
        if enemy != null and enemy.health > 0.0 and not enemy.enemy_id.begins_with("BOSS_") and contains(enemy.global_position):
            enemy.apply_damage(float(spec.get("enemy_dps", 0.0)) * delta, "HAZARD_" + hazard_id)
            if not enemy.enemy_id in last_hits: last_hits.append(enemy.enemy_id)

func _sync_slowing() -> void:
    var inside: Dictionary = {}
    if phase == Phase.DISCHARGE:
        var actors := get_tree().get_nodes_in_group("operators")
        actors.append_array(get_tree().get_nodes_in_group("m3_enemies"))
        for actor in actors:
            if not is_instance_valid(actor) or actor.is_queued_for_deletion() or not actor.has_method("set_hazard_speed_factor"): continue
            if actor is OperatorActor and actor.is_downed(): continue
            if actor is EnemyActor and actor.health <= 0.0: continue
            if actor is Node2D and contains((actor as Node2D).global_position):
                actor.call("set_hazard_speed_factor", _slow_token(), float(spec.get("slow_multiplier", 0.7)))
                inside[actor.get_instance_id()] = weakref(actor)
    for id in _slowed:
        if inside.has(id): continue
        var actor = (_slowed[id] as WeakRef).get_ref()
        if is_instance_valid(actor): actor.call("remove_hazard_speed_factor", _slow_token())
    _slowed = inside

## Called before queue_free when a room clears; movement is restored this frame.
## A token removes only this plate's part, preserving another frost plate/run boost.
func release_effects() -> void:
    for id in _slowed:
        var actor = (_slowed[id] as WeakRef).get_ref()
        if is_instance_valid(actor): actor.call("remove_hazard_speed_factor", _slow_token())
    _slowed.clear()

func _exit_tree() -> void:
    release_effects()

func _draw() -> void:
    if hazard_id != "ARC_VENT":
        _draw_expansion()
        return
    var telegraph := maxf(0.01, float(spec.get("telegraph", 1.1)))
    var charge := 0.0
    if phase == Phase.TELEGRAPH: charge = clampf(1.0 - phase_left / telegraph, 0.0, 1.0)
    elif phase == Phase.DISCHARGE: charge = 1.0
    draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, FLOOR_RATIO))
    draw_circle(Vector2.ZERO, radius, Color(0.02, 0.04, 0.05, 0.5))
    # Grate slats inside the rim.
    for i in range(-3, 4):
        var x := float(i) * radius / 4.0
        var half := sqrt(maxf(0.0, radius * radius * 0.82 - x * x))
        draw_line(Vector2(x, -half), Vector2(x, half), Color(color, 0.14 + 0.3 * charge), 2.0)
    draw_arc(Vector2.ZERO, radius, 0.0, TAU, 56, Color(color, 0.38 + 0.5 * charge), 2.0 + 1.5 * charge)
    if phase == Phase.TELEGRAPH:
        draw_circle(Vector2.ZERO, radius, Color(color, 0.06 + 0.16 * charge))
        draw_arc(Vector2.ZERO, radius - 7.0, -PI * 0.5, -PI * 0.5 + TAU * charge, 48, Color(color, 0.95), 2.6)
        for i in range(2 + int(charge * 3.0)):
            _bolt(Vector2.ZERO, Vector2.RIGHT.rotated(_crackle.randf() * TAU) * radius * (0.35 + 0.5 * charge), Color(color, 0.55), 1.4)
    elif phase == Phase.DISCHARGE:
        var fade := clampf(phase_left / maxf(0.01, float(spec.get("discharge", 0.3))), 0.0, 1.0)
        draw_circle(Vector2.ZERO, radius, Color(color, 0.45 * fade))
        draw_circle(Vector2.ZERO, radius * 0.45, Color(color.lightened(0.6), 0.55 * fade))
        for i in range(7):
            _bolt(Vector2.ZERO, Vector2.RIGHT.rotated(float(i) * TAU / 7.0 + _crackle.randf() * 0.5) * radius, Color(color.lightened(0.5), 0.9 * fade), 2.6)
    draw_set_transform(Vector2.ZERO)
    # Arcs rise off the grate: short sparks while charging, tall bolts on discharge.
    var rising := 0
    var height := 0.0
    if phase == Phase.TELEGRAPH and charge > 0.35:
        rising = 2
        height = 22.0 * charge
    elif phase == Phase.DISCHARGE:
        rising = 5
        height = 84.0
    for i in range(rising):
        var foot := Vector2.RIGHT.rotated(_crackle.randf() * TAU) * Vector2(radius, radius * FLOOR_RATIO) * _crackle.randf_range(0.2, 0.9)
        _bolt(foot, foot + Vector2(_crackle.randf_range(-12.0, 12.0), -height * _crackle.randf_range(0.7, 1.0)), Color(color.lightened(0.55), 0.85), 2.2 if phase == Phase.DISCHARGE else 1.4)

func _draw_expansion() -> void:
    _painter.clear()
    var charge := clampf(1.0 - phase_left / maxf(0.01, float(spec.get("telegraph", 1.1))), 0.0, 1.0) if phase == Phase.TELEGRAPH else (1.0 if phase == Phase.DISCHARGE else 0.0)
    if is_band():
        var half := Vector2(float(spec.get("half_length", 90.0)), float(spec.get("half_width", 24.0)))
        var angle := _band_angle()
        var corners: Array[Vector2] = [Vector2(-half.x, -half.y).rotated(angle), Vector2(half.x, -half.y).rotated(angle), Vector2(half.x, half.y).rotated(angle), Vector2(-half.x, half.y).rotated(angle)]
        _painter.quad(corners[0], corners[1], corners[2], corners[3], Color(color, 0.09 + 0.25 * charge))
        for sign_value: float in [-1.0, 1.0]:
            _painter.streak(Vector2(-half.x, sign_value * half.y).rotated(angle), Vector2(half.x, sign_value * half.y).rotated(angle), 1.7 + charge, Color(color, 0.55 + 0.4 * charge))
        for i in range(9):
            var x := lerpf(-half.x + 6.0, half.x - 6.0, float(i) / 8.0)
            _painter.streak(Vector2(x, -half.y).rotated(angle), Vector2(x, half.y).rotated(angle), 1.4 + charge, Color(color, 0.18 + 0.65 * charge))
        if phase == Phase.TELEGRAPH:
            _painter.streak(Vector2(-half.x, 0).rotated(angle), Vector2(lerpf(-half.x, half.x, charge), 0).rotated(angle), 3.0, Color.WHITE)
    elif is_slowing():
        var active := phase == Phase.DISCHARGE
        _painter.puff(Vector2.ZERO, radius, Color(color, 0.22 if active else 0.06), Color(0, 0, 0, 0), 10, FLOOR_RATIO)
        _painter.ring(Vector2.ZERO, radius, 1.8, Color(color, 0.8 if active else 0.32), 20, 0.0, TAU, FLOOR_RATIO)
        # Six floor crystals, batched as one triangle array rather than six calls.
        for i in range(6):
            var foot := Vector2.from_angle(TAU * float(i) / 6.0) * Vector2(radius * 0.5, radius * FLOOR_RATIO * 0.5)
            for arm in range(3):
                var ray := Vector2.from_angle(PI * float(arm) / 3.0) * Vector2(10.0, 5.5)
                _painter.streak(foot - ray, foot + ray, 1.1, Color(color, 0.64 if active else 0.2))
    else:
        _painter.ring(Vector2.ZERO, radius, 1.8 + charge, Color(color, 0.4 + 0.5 * charge), 20, 0.0, TAU, FLOOR_RATIO)
        var density := 0.06 + charge * 0.2
        _painter.puff(Vector2.ZERO, radius, Color(color, density), Color(0, 0, 0, 0), 10, FLOOR_RATIO)
        var noise := VfxPainter.noise()
        var seed_value := int(get_instance_id()) & (VfxPainter.NOISE_SIZE - 1)
        for i in range(12):
            var theta := noise[(seed_value + i * 13) & (VfxPainter.NOISE_SIZE - 1)] * TAU + _age * 0.18
            var distance := radius * (0.2 + 0.6 * noise[(seed_value + i * 17 + 2) & (VfxPainter.NOISE_SIZE - 1)])
            var at := Vector2.from_angle(theta) * Vector2(distance, distance * FLOOR_RATIO)
            _painter.dot(at, 1.5 + 2.2 * charge, Color(color, 0.14 + 0.6 * charge))
    _painter.flush(get_canvas_item())

func _bolt(from: Vector2, to: Vector2, tint: Color, width: float) -> void:
    var points := PackedVector2Array([from])
    var normal := (to - from).orthogonal().normalized()
    for step in range(1, 5):
        points.append(from.lerp(to, float(step) / 5.0) + normal * _crackle.randf_range(-9.0, 9.0))
    points.append(to)
    draw_polyline(points, tint, width)

func debug_contract() -> Dictionary:
    return {"hazard": hazard_id, "phase": Phase.keys()[phase], "phase_left": phase_left, "discharges": discharges,
        "radius": radius, "position": [global_position.x, global_position.y], "shape": "band" if is_band() else "ellipse",
        "mode": str(spec.get("mode", "burst")), "slow_actor_count": _slowed.size(), "draw_commands_max": 23 if hazard_id == "ARC_VENT" else 2}
