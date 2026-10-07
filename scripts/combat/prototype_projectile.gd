extends Node2D
class_name PrototypeProjectile

# Retained M5 projectile identity contract:
# ASTER — Precision coil dart
# ROOK — Heavy magnetic pellet
# MICA — Sensor pulse
# SIGNAL ANCHOR — Phase lance

const ASTER_PROJECTILE_V6_PATH := "res://assets/units/operators/aster/vfx/ASTER_COIL_PROJECTILE_V6_RGBA.webp"
const ASTER_PROJECTILE_V6_SOURCE_SIZE := Vector2(768.0, 192.0)
const ASTER_PROJECTILE_V6_SCALE := 0.102
const ASTER_PROJECTILE_V6_TIP_X := 0.862
const ASTER_PROJECTILE_COLLISION_TIP_X := 17.0
const Painter := preload("res://scripts/vfx/vfx_painter.gd")
const Muzzle := preload("res://scripts/vfx/combat_muzzle_vfx.gd")
## Trail length each family reaches once it has flown that far.
const TRAIL_LENGTH := {"ASTER": 84.0, "ROOK": 38.0, "MICA": 64.0, "DRONE": 60.0, "BULWARK": 74.0,
    "PRISM": 70.0, "ANCHOR": 96.0, "RELAY": 74.0, "REMNANT": 86.0,
    "FORGE": 96.0, "CARRIER": 96.0, "AERATOR": 78.0, "CRYO": 84.0, "GANTRY": 100.0,
    "ARCHIVE": 80.0, "ORIGIN": 90.0, "GENERIC": 50.0, "WEAPON_RAIL": 105.0, "WEAPON_NULL": 44.0}
## Families whose body keeps moving on its own (spinning rings, pulsing cores).
const ANIMATED := ["MICA", "ANCHOR", "RELAY", "REMNANT", "FORGE", "CARRIER",
    "AERATOR", "CRYO", "ARCHIVE", "ORIGIN"]

static var _aster_projectile_v6_texture: Texture2D
## One light texture for every ASTER projectile. A new texture per shot was drawn on
## the CPU each time and, being new to the renderer's 2D light atlas, rebuilt that
## atlas; the gradient is the same for all of them.
static var _aster_projectile_v6_light_texture: GradientTexture2D

var direction := Vector2.RIGHT
var speed := 720.0
var damage := 10.0
var lifetime := 1.1
var owner_actor: Node = null
var _had_owner := false
var tint := Color("fff0a8")
var art_profile: Dictionary = {}
var projectile_profile := "PRJ_GENERIC"
var target_group := "prototype_targets"
var _aster_projectile_v6_sprite: Sprite2D
var _aster_projectile_v6_ghosts: Array[Sprite2D] = []
var _aster_projectile_v6_light: PointLight2D
## Code-drawn body, glow and trail. The trail grows with the distance flown, so it never
## reaches back past the muzzle into the shooter; once full it stays still (the node's
## transform carries it) unless the family animates.
var _paint := Painter.new()
var _family := "GENERIC"
var _travelled := 0.0
var _age := 0.0
var _trail_settled := false

func setup(origin: Vector2, dir: Vector2, source: Node, color: Color, profile: Dictionary = {}, hit_group: String = "prototype_targets") -> void:
    global_position = origin
    direction = dir.normalized() if dir.length_squared() > 0.0 else Vector2.RIGHT
    owner_actor = source
    _had_owner = is_instance_valid(source)
    tint = color
    art_profile = profile.duplicate(true)
    projectile_profile = str(art_profile.get("projectile_profile", "PRJ_GENERIC"))
    target_group = hit_group
    rotation = direction.angle()
    _family = Muzzle.family_for(projectile_profile)
    _travelled = 0.0
    _age = 0.0
    _trail_settled = false
    material = Painter.additive_material()
    _apply_profile_tuning()
    _configure_authored_projectile_vfx()
    z_index = 3000
    if is_inside_tree():
        Muzzle.spawn(get_tree(), origin, direction, projectile_profile, tint, source)
    queue_redraw()

func _configure_authored_projectile_vfx() -> void:
    if "ASTER" not in projectile_profile:
        return
    if _aster_projectile_v6_texture == null:
        var image := Image.new()
        # Packed Web resources have no OS path; decode the same authored bytes.
        var error := image.load_webp_from_buffer(FileAccess.get_file_as_bytes(ASTER_PROJECTILE_V6_PATH))
        if error == OK and image.get_size() == Vector2i(ASTER_PROJECTILE_V6_SOURCE_SIZE):
            _aster_projectile_v6_texture = ImageTexture.create_from_image(image)
    if _aster_projectile_v6_texture == null:
        return
    var source_tip_from_center := (ASTER_PROJECTILE_V6_TIP_X - 0.5) * ASTER_PROJECTILE_V6_SOURCE_SIZE.x
    var authored_position := Vector2(
        ASTER_PROJECTILE_COLLISION_TIP_X - source_tip_from_center * ASTER_PROJECTILE_V6_SCALE,
        0.0,
    )
    # Two restrained opacity-stepped duplicates trail in local -X, so all
    # eight/world-space firing angles remain correct.
    for index in range(2):
        var ghost := Sprite2D.new()
        ghost.name = "AsterCoilProjectileV6Afterimage%d" % (index + 1)
        ghost.texture = _aster_projectile_v6_texture
        ghost.centered = true
        ghost.scale = Vector2.ONE * ASTER_PROJECTILE_V6_SCALE * (0.94 - float(index) * 0.08)
        ghost.position = authored_position + Vector2(-15.0 - float(index) * 17.0, 0.0)
        ghost.modulate = Color(1.0, 0.72, 0.38, 0.16 - float(index) * 0.08)
        ghost.z_index = -2 + index
        ghost.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
        add_child(ghost)
        _aster_projectile_v6_ghosts.append(ghost)

    _aster_projectile_v6_sprite = Sprite2D.new()
    _aster_projectile_v6_sprite.name = "AsterCoilProjectileV6"
    _aster_projectile_v6_sprite.texture = _aster_projectile_v6_texture
    _aster_projectile_v6_sprite.centered = true
    _aster_projectile_v6_sprite.scale = Vector2.ONE * ASTER_PROJECTILE_V6_SCALE
    _aster_projectile_v6_sprite.position = authored_position
    _aster_projectile_v6_sprite.z_index = 1
    _aster_projectile_v6_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    add_child(_aster_projectile_v6_sprite)
    _aster_projectile_v6_light = _make_aster_projectile_light()
    add_child(_aster_projectile_v6_light)

static func _aster_projectile_light_texture() -> GradientTexture2D:
    if _aster_projectile_v6_light_texture != null:
        return _aster_projectile_v6_light_texture
    var gradient := Gradient.new()
    gradient.offsets = PackedFloat32Array([0.0, 0.28, 1.0])
    gradient.colors = PackedColorArray([
        Color(1.0, 0.92, 0.70, 1.0),
        Color(1.0, 0.46, 0.12, 0.46),
        Color(0.12, 0.72, 0.86, 0.0),
    ])
    var texture := GradientTexture2D.new()
    texture.width = 128
    texture.height = 64
    texture.fill = GradientTexture2D.FILL_RADIAL
    texture.fill_from = Vector2(0.5, 0.5)
    texture.fill_to = Vector2(1.0, 0.5)
    texture.gradient = gradient
    _aster_projectile_v6_light_texture = texture
    return texture

func _make_aster_projectile_light() -> PointLight2D:
    var light := PointLight2D.new()
    light.name = "AsterCoilProjectileV6LocalLight"
    light.texture = _aster_projectile_light_texture()
    light.position = Vector2(1.0, 0.0)
    light.color = Color(1.0, 0.64, 0.27)
    light.energy = 0.34
    light.texture_scale = 0.48
    light.z_index = -3
    return light

func _apply_profile_tuning() -> void:
    if "ASTER" in projectile_profile:
        speed = 1040.0; damage = 10.0; lifetime = 0.9
    elif "ROOK" in projectile_profile:
        speed = 760.0; damage = 7.0; lifetime = 0.58
    elif "MICA" in projectile_profile:
        speed = 640.0; damage = 8.0; lifetime = 1.22
    elif "RIFLE" in projectile_profile:
        speed = 900.0; damage = 8.0
    elif "SHIELD" in projectile_profile:
        speed = 620.0; damage = 16.0
    elif "DRONE" in projectile_profile:
        speed = 780.0; damage = 7.0
    elif "ABERRANT" in projectile_profile:
        speed = 440.0; damage = 12.0; lifetime = 1.5
    elif "ANCHOR" in projectile_profile:
        speed = 560.0; damage = 24.0; lifetime = 1.6
    elif "RELAY" in projectile_profile:
        speed = 630.0; damage = 16.0; lifetime = 1.5
    elif "REMNANT" in projectile_profile:
        speed = 600.0; damage = 18.0; lifetime = 1.6
    elif "FORGE" in projectile_profile:
        speed = 640.0; damage = 18.0; lifetime = 1.5
    elif "CARRIER" in projectile_profile:
        speed = 680.0; damage = 16.0; lifetime = 1.5
    elif "AERATOR" in projectile_profile:
        speed = 560.0; damage = 16.0; lifetime = 1.6
    elif "CRYO" in projectile_profile:
        speed = 680.0; damage = 18.0; lifetime = 1.5
    elif "GANTRY" in projectile_profile:
        speed = 720.0; damage = 20.0; lifetime = 1.5
    elif "ARCHIVE" in projectile_profile:
        speed = 620.0; damage = 18.0; lifetime = 1.6
    elif "ORIGIN" in projectile_profile:
        speed = 640.0; damage = 20.0; lifetime = 1.6

func _physics_process(delta: float) -> void:
    if _had_owner and not is_instance_valid(owner_actor):
        queue_free()
        return
    var from := global_position
    var to := from + direction * speed * delta
    lifetime -= delta
    var nearest: Node2D = null
    var contact := Vector2.INF
    var nearest_distance := INF
    var cover_contact := Vector2.INF
    var hit_cover: Node = null
    for cover in get_tree().get_nodes_in_group("sable_environment_cover"):
        if not is_instance_valid(cover): continue
        var point: Vector2 = cover.projectile_hit(from,to)
        if point != Vector2.INF and from.distance_squared_to(point) < nearest_distance:
            nearest_distance = from.distance_squared_to(point)
            cover_contact = point
            hit_cover = cover
    var targets := get_tree().get_nodes_in_group(target_group)
    if target_group=="prototype_targets":
        # A phase shield removes auto-targeting, not the physical machine.
        for guarded in get_tree().get_nodes_in_group("site7_guarded_targets"):
            if is_instance_valid(guarded) and guarded.health>0.0 and not targets.has(guarded): targets.append(guarded)
    for target in targets:
        if not is_instance_valid(target) or target == owner_actor or not (target is Node2D):
            continue
        var rect: Rect2 = target.call("get_combat_hit_rect") if target.has_method("get_combat_hit_rect") else Rect2(target.global_position - Vector2(24,24), Vector2(48,48))
        var point: Vector2 = preload("res://scripts/combat/combat_hit_geometry.gd").hit_point(from, to, rect.grow(2.0))
        if point != Vector2.INF and from.distance_squared_to(point) < nearest_distance:
            nearest_distance = from.distance_squared_to(point)
            nearest = target
            contact = point
    global_position = to
    _travelled += from.distance_to(to)
    _age += delta
    if not _trail_settled or _family in ANIMATED:
        _trail_settled = _travelled >= float(TRAIL_LENGTH.get(_family, 50.0))
        queue_redraw()
    if nearest == null and cover_contact != Vector2.INF:
        hit_cover.record_projectile_block(owner_actor if is_instance_valid(owner_actor) else null)
        CombatFeedback.spawn_cover_hit(get_tree(), cover_contact, art_profile, tint, owner_actor if is_instance_valid(owner_actor) else null, direction)
        queue_free()
        return
    if nearest:
        var guard := nearest.get_node_or_null("BossPhaseTransitionGuard")
        if guard and guard.debug_guard_active():
            CombatFeedback.spawn_hit(get_tree(),contact,art_profile,Color("a5e8fa"),owner_actor if is_instance_valid(owner_actor) else null,direction,"HIT_BARRIER_GUARD_01")
            CombatFeedback.play_layer(get_tree(), "shield_hit", nearest, contact)
            queue_free()
            return
        var applied_damage := damage
        var impact_look := ""
        if is_instance_valid(owner_actor) and owner_actor is OperatorActor and (owner_actor as OperatorActor).operator_id == "CHR_PROTO_01":
            if nearest.has_method("is_exposed") and bool(nearest.call("is_exposed")):
                applied_damage *= 1.35
                if (owner_actor as OperatorActor).has_module("MOD_PRISM_FOCUS") and _is_security_target(nearest):
                    applied_damage *= 1.15
        if nearest.has_method("projectile_damage_multiplier"):
            var armour := float(nearest.projectile_damage_multiplier(direction))
            applied_damage *= armour
            if armour < 1.0:
                CombatFeedback.play_layer(get_tree(), "shield_hit", nearest, contact)
                impact_look = "HIT_ARMOR_DEFLECT_01"
        if nearest is OperatorActor:
            var source_id := str(owner_actor.get("enemy_id")) if is_instance_valid(owner_actor) and owner_actor.get("enemy_id") != null else ""
            (nearest as OperatorActor).apply_damage(applied_damage, source_id)
        elif nearest.has_method("apply_damage"): nearest.apply_damage(applied_damage)
        if is_instance_valid(owner_actor) and owner_actor.has_method("on_projectile_hit"):
            owner_actor.call("on_projectile_hit", nearest, applied_damage)
        CombatFeedback.spawn_hit(get_tree(), contact, art_profile, Color("ffe09a") if not impact_look.is_empty() else tint, owner_actor if is_instance_valid(owner_actor) else null, direction, impact_look)
        queue_free()
        return
    if lifetime <= 0.0: queue_free()

func _is_security_target(target: Node) -> bool:
    if not (target is EnemyActor): return false
    var id := (target as EnemyActor).enemy_id.to_upper()
    return "RIFLE" in id or "SHIELD" in id or "DRONE" in id or "BULWARK" in id or "MORTAR" in id

func _draw() -> void:
    _paint.clear()
    var trail := minf(_travelled, float(TRAIL_LENGTH.get(_family, 50.0)))
    match _family:
        "WEAPON_RAIL": _draw_weapon_rail(trail)
        "WEAPON_NULL": _draw_weapon_null(trail)
        "ASTER": _draw_aster(trail)
        "ROOK": _draw_rook(trail)
        "MICA": _draw_mica(trail)
        "DRONE": _draw_drone(trail)
        "BULWARK": _draw_bulwark(trail)
        "PRISM": _draw_prism(trail)
        "ANCHOR", "FORGE", "CARRIER": _draw_lance(trail)
        "RELAY": _draw_relay(trail)
        "REMNANT": _draw_remnant(trail)
        "AERATOR": _draw_spore(trail)
        "CRYO": _draw_frost(trail)
        "GANTRY": _draw_rail(trail)
        "ARCHIVE": _draw_echo(trail)
        "ORIGIN": _draw_null(trail)
        _: _draw_generic(trail)
    _paint.flush(get_canvas_item())

## Coil dart: the authored ImageGen dart stays the body; code adds only its cyan wake
## and a hot point under the tip. Without the art, a code-drawn dart stands in.
func _draw_aster(trail: float) -> void:
    var tip := Vector2(ASTER_PROJECTILE_COLLISION_TIP_X, 0.0)
    _paint.fading_beam(tip - Vector2(trail, 0.0), tip - Vector2(6.0, 0.0), 11.0, Color(0.3, 0.7, 1.0, 0.28), 0.0, 1.0)
    _paint.fading_beam(tip - Vector2(trail, 0.0), tip - Vector2(8.0, 0.0), 5.5, Color(0.4, 0.86, 1.0, 0.7), 0.0, 1.0)
    _paint.fading_beam(tip - Vector2(trail * 0.65, 0.0), tip - Vector2(6.0, 0.0), 2.0, Color(0.88, 0.98, 1.0, 0.9), 0.0, 1.0)
    _paint.glow(tip, 15.0, Color(1.0, 0.82, 0.5, 0.5))
    if is_instance_valid(_aster_projectile_v6_sprite):
        return
    _paint.streak(Vector2(-18.0, 0.0), tip, 2.6, Color(0.9, 0.98, 1.0, 1.0), true)
    _paint.glow(tip, 7.0, Color(1.0, 0.8, 0.44, 0.95))

## Heavy magnetic pellet: short white-hot slug with an ember tail. Five fly together, so
## each stays narrow and the fan reads as a scatter burst, not one slab.
func _draw_rook(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(2.0, 0.0), 4.6, Color(1.0, 0.52, 0.18, 0.62), 0.0, 1.0)
    _paint.glow(Vector2(4.0, 0.0), 13.0, Color(1.0, 0.6, 0.26, 0.5), 8)
    _paint.streak(Vector2(-14.0, 0.0), Vector2(11.0, 0.0), 3.2, Color(1.0, 0.86, 0.55, 1.0), true)

## Sensor pulse: a teal orb in a spinning broken ring, trailing a sine ripple.
func _draw_mica(trail: float) -> void:
    var wave_color := Color(0.38, 0.9, 0.8, 0.6)
    var previous := Vector2.ZERO
    for i in range(9):
        var x := -trail * float(i) / 8.0
        var point := Vector2(x, sin(x * 0.2 + _age * 18.0) * 3.6 * (float(i) / 8.0))
        if i > 0:
            _paint.fading_beam(previous, point, 3.0, wave_color, 1.0 - float(i - 1) / 8.0, 1.0 - float(i) / 8.0)
        previous = point
    _paint.fading_beam(Vector2(-trail * 0.7, 0.0), Vector2.ZERO, 9.0, Color(0.3, 0.9, 0.8, 0.22), 0.0, 1.0)
    _paint.glow(Vector2.ZERO, 20.0, Color(0.38, 0.95, 0.85, 0.5))
    _paint.ring(Vector2.ZERO, 9.5, 2.0, Color(0.55, 1.0, 0.92, 1.0), 12, _age * 9.0, _age * 9.0 + PI * 0.7)
    _paint.ring(Vector2.ZERO, 9.5, 2.0, Color(0.55, 1.0, 0.92, 1.0), 12, _age * 9.0 + PI, _age * 9.0 + PI * 1.7)
    _paint.dot(Vector2.ZERO, 5.5, Color(0.92, 1.0, 0.98, 1.0))

## Recon drone beamlet: magenta bolt with a cyan-white core.
func _draw_drone(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(6.0, 0.0), 8.5, Color(0.92, 0.28, 0.6, 0.66), 0.0, 1.0)
    _paint.streak(Vector2(-trail * 0.6, 0.0), Vector2(13.0, 0.0), 3.0, Color(0.55, 0.96, 1.0, 1.0), true)
    _paint.glow(Vector2(10.0, 0.0), 16.0, Color(0.95, 0.4, 0.75, 0.5), 10)
    _paint.glow(Vector2(11.0, 0.0), 6.0, Color(0.9, 1.0, 1.0, 0.95), 8)

## BULWARK cannon slug: a heavy amber round in a heat wake.
func _draw_bulwark(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(0.0, 0.0), 10.0, Color(1.0, 0.5, 0.18, 0.5), 0.0, 1.0)
    _paint.glow(Vector2(2.0, 0.0), 24.0, Color(1.0, 0.66, 0.26, 0.5))
    _paint.ellipse_glow(Vector2(4.0, 0.0), Vector2(16.0, 7.0), Color(1.0, 0.84, 0.45, 0.95), 10)
    _paint.streak(Vector2(-10.0, 0.0), Vector2(17.0, 0.0), 2.8, Color(1.0, 0.95, 0.8, 1.0), true)

## PRISM skimmer needle: three spectral lines converging on a white point.
func _draw_prism(trail: float) -> void:
    var spectrum := [Color(1.0, 0.44, 0.85, 0.8), Color(0.54, 0.48, 1.0, 0.8), Color(0.44, 0.9, 1.0, 0.8)]
    for i in range(3):
        var offset := (float(i) - 1.0) * 3.8
        _paint.fading_beam(Vector2(-trail, offset), Vector2(8.0, offset * 0.2), 3.2, spectrum[i], 0.0, 1.0)
    _paint.glow(Vector2(8.0, 0.0), 16.0, Color(0.7, 0.62, 1.0, 0.55), 10)
    _paint.flare(Vector2(9.0, 0.0), Vector2.RIGHT, 18.0, 1.8, Color(0.92, 0.9, 1.0, 1.0), 0.6)

## Boss lance: a long pulsing body in the boss's colour with a white spine and orbiting sparks.
func _draw_lance(trail: float) -> void:
    var pulse := 0.85 + 0.15 * sin(_age * 22.0)
    var hot := tint.lightened(0.45)
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(0.0, 0.0), 16.0, Color(tint, 0.55), 0.0, 1.0)
    _paint.fading_beam(Vector2(-trail * 0.6, 0.0), Vector2(0.0, 0.0), 5.0, Color(hot, 0.8), 0.0, 1.0)
    _paint.glow(Vector2(4.0, 0.0), 28.0 * pulse, Color(tint, 0.5))
    _paint.ellipse_glow(Vector2(4.0, 0.0), Vector2(26.0, 9.0) * pulse, Color(hot, 0.95), 12)
    _paint.streak(Vector2(-22.0, 0.0), Vector2(18.0, 0.0), 3.0, Color(1.0, 1.0, 1.0, 1.0), true)
    for i in range(2):
        var angle := _age * 16.0 + float(i) * PI
        _paint.dot(Vector2(-4.0 + cos(angle) * 14.0, sin(angle) * 7.0), 3.6, Color(hot, 0.95))

func _draw_relay(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(4.0, 0.0), 12.0, Color("d8283c", 0.62), 0.0, 1.0)
    _paint.streak(Vector2(-trail * 0.7, -5.0), Vector2(12.0, 0.0), 2.4, Color("ff9ca6"), true)
    _paint.streak(Vector2(-trail * 0.7, 5.0), Vector2(12.0, 0.0), 2.4, Color("ff9ca6"), true)
    _paint.glow(Vector2(12.0, 0.0), 21.0, Color("ff5266", 0.68))
    _paint.dot(Vector2(12.0, 0.0), 5.0, Color("ffe8eb"))

func _draw_remnant(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(6.0, 0.0), 11.0, Color("bfe8ff", 0.50), 0.0, 1.0)
    for fork in [-1.0, 1.0]:
        _paint.streak(Vector2(-trail * 0.5, fork * 5.0), Vector2(14.0, fork * 2.0), 2.0, Color("f1fbff"), true)
    _paint.glow(Vector2(12.0, 0.0), 23.0, Color("bfe8ff", 0.58))
    _paint.dot(Vector2(13.0, 0.0), 5.0, Color.WHITE)

## AERATOR spore: a lime bud with three turning petals, trailing drifting motes.
func _draw_spore(trail: float) -> void:
    var pulse := 0.85 + 0.15 * sin(_age * 14.0)
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(4.0, 0.0), 12.0, Color("8fdc4a", 0.5), 0.0, 1.0)
    for i in range(4):
        var back := trail * (0.25 + 0.2 * float(i))
        var drift := sin(_age * 7.0 + float(i) * 1.9) * 5.0
        _paint.dot(Vector2(-back, drift), 4.5 - float(i) * 0.7, Color("d6ff9a", 0.75 - 0.12 * float(i)))
    _paint.glow(Vector2(12.0, 0.0), 24.0 * pulse, Color("8fdc4a", 0.6))
    for i in range(3):
        var angle := _age * 6.0 + TAU * float(i) / 3.0
        _paint.shard(Vector2(12.0, 0.0) + Vector2.from_angle(angle) * 8.0, angle, 5.0, Color("d6ff9a", 0.9))
    _paint.dot(Vector2(12.0, 0.0), 5.5, Color("f2ffd0"))

## CRYO shard: a pointed ice splinter in a pale-pink glow with a glittering wake.
func _draw_frost(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(6.0, 0.0), 9.0, Color("ff7fc8", 0.42), 0.0, 1.0)
    _paint.shard(Vector2(4.0, 0.0), 0.0, 20.0, Color("ffe1f2", 0.95))
    _paint.streak(Vector2(-trail * 0.6, 0.0), Vector2(16.0, 0.0), 2.6, Color("fff0fa"), true)
    _paint.glow(Vector2(10.0, 0.0), 20.0, Color("ff7fc8", 0.55))
    for i in range(3):
        var back := 20.0 + float(i) * trail * 0.22
        var glint := 0.5 + 0.5 * sin(_age * 30.0 + float(i) * 2.3)
        _paint.dot(Vector2(-back, (float(i) - 1.0) * 6.0), 2.4, Color(1.0, 1.0, 1.0, glint))

## GANTRY rail slug: a long yellow bar between two thin rails, tipped white.
func _draw_rail(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(8.0, 0.0), 10.0, Color("ffd84a", 0.5), 0.0, 1.0)
    for rail in [-1.0, 1.0]:
        _paint.streak(Vector2(-trail * 0.8, rail * 6.0), Vector2(20.0, rail * 6.0), 1.8, Color("fff4b0"), true)
    _paint.ellipse_glow(Vector2(8.0, 0.0), Vector2(24.0, 7.0), Color("ffd84a", 0.9), 10)
    _paint.glow(Vector2(18.0, 0.0), 20.0, Color("ffe16b", 0.6))
    _paint.dot(Vector2(19.0, 0.0), 5.0, Color.WHITE)

## ARCHIVE echo packet: a teal data square that leaves fading copies of itself behind.
func _draw_echo(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(4.0, 0.0), 8.0, Color("2fe0b4", 0.4), 0.0, 1.0)
    for i in range(4):
        var back := 18.0 + float(i) * trail * 0.2
        _paint.polygon_outline(Vector2(-back, 0.0), 7.0 - float(i) * 1.1, 4, PI * 0.25, 1.3, Color("2fe0b4", 0.7 - 0.14 * float(i)))
    _paint.glow(Vector2(12.0, 0.0), 22.0, Color("2fe0b4", 0.6))
    _paint.polygon_outline(Vector2(12.0, 0.0), 8.5, 4, PI * 0.25 + _age * 3.0, 1.8, Color("c8fff0"))
    _paint.dot(Vector2(12.0, 0.0), 4.5, Color.WHITE)

## ORIGIN null bolt: a white point with hairline cracks flickering off its wake.
func _draw_null(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(6.0, 0.0), 9.0, Color("f4efe8", 0.42), 0.0, 1.0)
    var strike := int(_age * 24.0)
    for i in range(3):
        var side := -1.0 if i % 2 == 0 else 1.0
        var from := Vector2(-trail * (0.15 + 0.3 * float(i)), 0.0)
        _paint.bolt(from, from + Vector2(-8.0, side * (12.0 + 4.0 * float(i))), 3, 3.0, 1.4, Color(1.0, 1.0, 1.0, 0.7), strike * 7 + i)
    _paint.glow(Vector2(12.0, 0.0), 24.0, Color("f4efe8", 0.6))
    _paint.streak(Vector2(-20.0, 0.0), Vector2(20.0, 0.0), 3.0, Color.WHITE, true)
    _paint.dot(Vector2(13.0, 0.0), 5.5, Color.WHITE)

func _draw_weapon_rail(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail,0),Vector2(10,0),6.0,Color("62d9ef",0.45),0.0,1.0)
    _paint.streak(Vector2(-20,0),Vector2(22,0),1.8,Color.WHITE,true)
    for sign_value in [-1.0,1.0]:
        _paint.streak(Vector2(-trail*0.65,sign_value*3.5),Vector2(12,sign_value*3.5),1.0,Color("b9f7ff"),true)
    _paint.dot(Vector2(20,0),3.0,Color.WHITE)

func _draw_weapon_null(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail,0),Vector2(3,0),8.0,Color("d68eb5",0.4),0.0,1.0)
    _paint.streak(Vector2(-10,0),Vector2(12,0),3.4,Color("ffd8ed"),true)
    for sign_value in [-1.0,1.0]:
        _paint.streak(Vector2(-5,sign_value*4),Vector2(8,sign_value*2),1.5,Color.WHITE,true)
    _paint.glow(Vector2(8,0),8.0,Color("ffd8ed",0.7))

func _draw_generic(trail: float) -> void:
    _paint.fading_beam(Vector2(-trail, 0.0), Vector2(6.0, 0.0), 7.0, Color(tint, 0.6), 0.0, 1.0)
    _paint.streak(Vector2(-10.0, 0.0), Vector2(10.0, 0.0), 2.6, Color(tint.lightened(0.4), 1.0), true)
    _paint.glow(Vector2(8.0, 0.0), 12.0, Color(tint, 0.55), 8)

func debug_anchor_visual_width() -> float:
    return 10.0

func debug_visual_contract() -> Dictionary:
    return {
        "projectile_profile": projectile_profile,
        "aster_v6_requested": "ASTER" in projectile_profile,
        "aster_v6_path": ASTER_PROJECTILE_V6_PATH,
        "aster_v6_loaded": _aster_projectile_v6_texture != null,
        "aster_v6_sprite_active": is_instance_valid(_aster_projectile_v6_sprite),
        "aster_v6_afterimage_count": _aster_projectile_v6_ghosts.size(),
        "aster_v6_local_light_active": is_instance_valid(_aster_projectile_v6_light),
        "aster_v6_resolution": _aster_projectile_v6_texture.get_size() if _aster_projectile_v6_texture else Vector2.ZERO,
        "aster_v6_scale": ASTER_PROJECTILE_V6_SCALE,
        "aster_v6_tip_anchor": ASTER_PROJECTILE_V6_TIP_X,
        "hit_feedback_authority": "CombatFeedback.spawn_hit",
        "hurt_feedback_called_by_projectile": false,
        "gameplay_speed_unchanged_by_visual": true,
        "collision_radius_unchanged_by_visual": true,
    }
