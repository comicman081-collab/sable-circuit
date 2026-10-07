extends Node2D
class_name CombatHitVFX

const EFFECT_IMPACT := "IMPACT"
const EFFECT_HURT := "HURT"
const REACTIONS := ["FLINCH", "LIGHT", "HEAVY", "DOWNED"]
const VOLUME_SHADER := preload("res://assets/shaders/combat_impact_volume.gdshader")
const Painter := preload("res://scripts/vfx/vfx_painter.gd")
# Impact art is authored at full size and drawn at the scale the 1.8x actors read best at.
const IMPACT_SCALE := 0.6
# Boss rounds (ANCHOR, FORGE, CARRIER lances) land larger.
const ANCHOR_IMPACT_SCALE := 0.86
const BOSS_FAMILIES := ["ANCHOR", "RELAY", "REMNANT", "FORGE", "CARRIER",
    "AERATOR", "CRYO", "GANTRY", "ARCHIVE", "ORIGIN"]
const HURT_SCALE := 0.62
const BOSS_HURT_SCALE := 0.86
## Share of the volume plume's authored size and energy drawn under the shapes.
const VOLUME_SIZE := 0.78
const VOLUME_ENERGY := 0.62

## Impact family per profile id: flavour, lifetime, volume palette/size/energy/shader style.
const FAMILIES := {
    "WEAPON_RAIL": {"life": 0.42, "palette": ["b9f7ff", "62d9ef"], "radius": 58.0, "energy": 0.85, "style": 0.6},
    "WEAPON_NULL": {"life": 0.48, "palette": ["ffd8ed", "d68eb5"], "radius": 68.0, "energy": 0.9, "style": 1.4},
    "ASTER": {"life": 0.40, "palette": ["79ddff", "8d78ff"], "radius": 60.0, "energy": 0.9, "style": 0.8},
    "ROOK": {"life": 0.50, "palette": ["ffc46b", "8f4829"], "radius": 78.0, "energy": 1.0, "style": 2.2},
    "MICA": {"life": 0.46, "palette": ["74f0da", "247f91"], "radius": 62.0, "energy": 0.9, "style": 1.0},
    "DRONE": {"life": 0.42, "palette": ["78f1ff", "e64f9d"], "radius": 58.0, "energy": 0.9, "style": 1.2},
    "BULWARK": {"life": 0.55, "palette": ["ffd073", "b8612a"], "radius": 84.0, "energy": 1.05, "style": 2.2},
    "PRISM": {"life": 0.44, "palette": ["b3a6ff", "ff6fd8"], "radius": 62.0, "energy": 0.95, "style": 1.4},
    "RAM": {"life": 0.55, "palette": ["ffb070", "c2401f"], "radius": 88.0, "energy": 1.05, "style": 2.4},
    "ANCHOR": {"life": 0.66, "palette": ["c0a2ff", "ed4ca4"], "radius": 108.0, "energy": 1.2, "style": 3.6},
    "RELAY": {"life": 0.60, "palette": ["ff9ca6", "d8283c"], "radius": 98.0, "energy": 1.1, "style": 1.6},
    "REMNANT": {"life": 0.62, "palette": ["f1fbff", "bfe8ff"], "radius": 102.0, "energy": 1.1, "style": 1.2},
    "FORGE": {"life": 0.66, "palette": ["8ff8ff", "1f8fa0"], "radius": 112.0, "energy": 1.2, "style": 3.0},
    "CARRIER": {"life": 0.70, "palette": ["b89aff", "5a2fb0"], "radius": 116.0, "energy": 1.2, "style": 3.6},
    "AERATOR": {"life": 0.66, "palette": ["d6ff9a", "8fdc4a"], "radius": 112.0, "energy": 1.15, "style": 2.4},
    "CRYO": {"life": 0.62, "palette": ["ffe1f2", "ff7fc8"], "radius": 104.0, "energy": 1.1, "style": 1.0},
    "GANTRY": {"life": 0.56, "palette": ["fff4b0", "ffd84a"], "radius": 108.0, "energy": 1.2, "style": 0.8},
    "ARCHIVE": {"life": 0.64, "palette": ["c8fff0", "2fe0b4"], "radius": 104.0, "energy": 1.1, "style": 1.4},
    "ORIGIN": {"life": 0.68, "palette": ["ffffff", "f4efe8"], "radius": 116.0, "energy": 1.25, "style": 2.0},
    "DEFLECT": {"life": 0.40, "palette": ["ffe8b0", "c98a3a"], "radius": 50.0, "energy": 0.75, "style": 0.6},
    "BARRIER": {"life": 0.48, "palette": ["a5e8fa", "5a8dff"], "radius": 72.0, "energy": 0.9, "style": 1.0},
    "GENERIC": {"life": 0.40, "palette": [], "radius": 58.0, "energy": 0.85, "style": 0.8},
}

static var _radial_texture: GradientTexture2D
## Impacts alive now. Past CROWD, a new impact draws fewer particles (never under
## CROWD_FLOOR of them), so a shotgun volley into a crowd costs about what a few
## single hits do; its flash, flare and rings stay whole.
static var _live_impacts := 0
const CROWD := 6
const CROWD_FLOOR := 0.45

var profile_id := "HIT_GENERIC"
var tint := Color.WHITE
var age := 0.0
var lifetime := 0.28
var effect_kind := EFFECT_IMPACT
var reaction := "NONE"
var target_kind := ""
var target_id := ""
var critical := false
## "COVER" when the round stopped on a prop: adds concrete dust and chips.
var surface := "BODY"
var family := "GENERIC"
var _seed := 0
var _flash_scale := 1.0
var _intensity := 0.82
var _retiring := false
var _impact_axis := Vector2.RIGHT
var _volume_sprite: Sprite2D
var _volume_material: ShaderMaterial
var _flash_light: PointLight2D
# All of one frame's shapes go out as a single triangle list. Each draw_colored_polygon /
# draw_circle was its own polygon command with its own buffer, hundreds a frame in a busy
# fight. The node blends additively, so order does not matter.
var _paint := Painter.new()
var _density := 1.0
var _counted := false
var _noise := Painter.noise()
var _noise_base := 0

func _init() -> void:
    var additive := CanvasItemMaterial.new()
    additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
    material = additive

func _notification(what: int) -> void:
    if what == NOTIFICATION_PREDELETE and _counted:
        _live_impacts -= 1

static func family_for(id_value: String) -> String:
    var id := id_value.to_upper()
    if "WEAPON_RAIL" in id: return "WEAPON_RAIL"
    if "WEAPON_NULL" in id: return "WEAPON_NULL"
    if "ASTER" in id: return "ASTER"
    if "ROOK" in id: return "ROOK"
    if "MICA" in id: return "MICA"
    if "DRONE" in id: return "DRONE"
    if "BULWARK" in id or "SHIELD" in id: return "BULWARK"
    if "PRISM" in id: return "PRISM"
    if "_RAM_" in id or "ABERRANT" in id: return "RAM"
    if "FORGE" in id: return "FORGE"
    if "CARRIER" in id or "PYLON" in id: return "CARRIER"
    if "RELAY" in id: return "RELAY"
    if "REMNANT" in id: return "REMNANT"
    if "AERATOR" in id: return "AERATOR"
    if "CRYO" in id: return "CRYO"
    if "GANTRY" in id: return "GANTRY"
    if "ARCHIVE" in id: return "ARCHIVE"
    if "ORIGIN" in id: return "ORIGIN"
    if "ANCHOR" in id: return "ANCHOR"
    if "DEFLECT" in id: return "DEFLECT"
    if "BARRIER" in id or "GUARD" in id: return "BARRIER"
    return "GENERIC"

func setup(id_value: String, color: Color, incoming_direction: Vector2 = Vector2.ZERO) -> void:
    _ensure_visual_layers()
    age = 0.0
    _retiring = false
    visible = true
    set_process(true)
    effect_kind = EFFECT_IMPACT
    reaction = "NONE"
    target_kind = ""
    target_id = ""
    critical = false
    surface = "BODY"
    profile_id = id_value.strip_edges().to_upper()
    family = family_for(profile_id)
    tint = color
    _seed = abs(profile_id.hash() + get_instance_id())
    _noise_base = _seed * 7919
    if not _counted:
        _counted = true
        _live_impacts += 1
    _density = clampf(float(CROWD) / float(maxi(CROWD, _live_impacts)), CROWD_FLOOR, 1.0)
    _impact_axis = incoming_direction.normalized() if incoming_direction.length_squared() > 0.001 else Vector2.RIGHT.rotated(_seed_angle(17))
    lifetime = float(FAMILIES[family].life)
    z_index = 3100
    scale = Vector2.ONE * (ANCHOR_IMPACT_SCALE if family in BOSS_FAMILIES else IMPACT_SCALE)
    _configure_visual_layers()
    _sync_visual_layers(0.0)
    queue_redraw()

## A round stopped by cover: concrete dust and chips join the weapon's own impact.
func mark_cover_surface() -> void:
    surface = "COVER"
    queue_redraw()

func setup_hurt(kind_value: String, id_value: String, reaction_value: String, color: Color, is_critical: bool = false, incoming_direction: Vector2 = Vector2.ZERO) -> void:
    _ensure_visual_layers()
    age = 0.0
    _retiring = false
    visible = true
    set_process(true)
    effect_kind = EFFECT_HURT
    surface = "BODY"
    target_kind = kind_value.strip_edges().to_upper()
    target_id = id_value.strip_edges().to_upper()
    reaction = reaction_value.strip_edges().to_upper()
    if not REACTIONS.has(reaction):
        reaction = "FLINCH"
    critical = is_critical
    profile_id = "HURT_%s_%s" % [target_kind, reaction]
    family = "HURT"
    tint = color
    _seed = abs(profile_id.hash() + target_id.hash() + get_instance_id())
    _noise_base = _seed * 7919
    _density = 1.0
    _impact_axis = incoming_direction.normalized() if incoming_direction.length_squared() > 0.001 else Vector2.RIGHT.rotated(_seed_angle(29))
    match reaction:
        "DOWNED": lifetime = 0.66
        "HEAVY": lifetime = 0.52
        "LIGHT": lifetime = 0.40
        _: lifetime = 0.30
    if "BOSS" in target_id:
        lifetime += 0.14
    z_index = 3101
    scale = Vector2.ONE * (BOSS_HURT_SCALE if target_kind == "BOSS" else HURT_SCALE)
    _configure_visual_layers()
    _sync_visual_layers(0.0)
    queue_redraw()

func _process(delta: float) -> void:
    age += delta
    if age >= lifetime:
        _retire()
        return
    _sync_visual_layers(clampf(age / lifetime, 0.0, 1.0))
    queue_redraw()

func _retire() -> void:
    if _retiring:
        return
    _retiring = true
    set_process(false)
    if _volume_sprite != null:
        _volume_sprite.visible = false
    if _flash_light != null:
        _flash_light.enabled = false
        _flash_light.energy = 0.0
    queue_free()

func _draw() -> void:
    var t := clampf(age / lifetime, 0.0, 1.0)
    _paint.clear()
    if effect_kind == EFFECT_HURT:
        _draw_hurt(t)
    else:
        _draw_impact(t)
        if surface == "COVER":
            _draw_cover_chips(t)
    _paint.flush(get_canvas_item())

func debug_flash_scale() -> float:
    return _flash_scale

func debug_vfx_contract() -> Dictionary:
    return {
        "effect_kind": effect_kind,
        "profile_id": profile_id,
        "family": family,
        "surface": surface,
        "reaction": reaction,
        "target_kind": target_kind,
        "target_id": target_id,
        "critical": critical,
        "lifetime": lifetime,
        "flash_scale": _flash_scale,
        "volumetric_layer": _volume_sprite != null,
        "practical_light": _flash_light != null,
        "directional_axis": _impact_axis
    }

func debug_triangle_count() -> int:
    return _paint.triangle_count()

func _ensure_visual_layers() -> void:
    if _volume_sprite != null:
        return
    _volume_material = ShaderMaterial.new()
    _volume_material.shader = VOLUME_SHADER
    _volume_sprite = Sprite2D.new()
    _volume_sprite.name = "VolumetricImpact"
    _volume_sprite.texture = _shared_radial_texture()
    _volume_sprite.material = _volume_material
    _volume_sprite.show_behind_parent = true
    _volume_sprite.z_index = -1
    add_child(_volume_sprite)
    # The practical flash light is desktop only; on the web each live 2D light costs a canvas pass.
    if OS.has_feature("web"):
        return
    _flash_light = PointLight2D.new()
    _flash_light.name = "ImpactPracticalLight"
    _flash_light.texture = _shared_radial_texture()
    _flash_light.shadow_enabled = false
    _flash_light.enabled = false
    _flash_light.energy = 0.0
    _flash_light.range_z_min = -1024
    _flash_light.range_z_max = 1024
    add_child(_flash_light)

static func _shared_radial_texture() -> GradientTexture2D:
    if _radial_texture != null:
        return _radial_texture
    var gradient := Gradient.new()
    gradient.offsets = PackedFloat32Array([0.0, 0.18, 0.52, 1.0])
    gradient.colors = PackedColorArray([
        Color(1.0, 1.0, 1.0, 1.0), Color(1.0, 1.0, 1.0, 0.92),
        Color(1.0, 1.0, 1.0, 0.34), Color(1.0, 1.0, 1.0, 0.0)
    ])
    _radial_texture = GradientTexture2D.new()
    _radial_texture.gradient = gradient
    _radial_texture.width = 128
    _radial_texture.height = 128
    _radial_texture.fill = GradientTexture2D.FILL_RADIAL
    _radial_texture.fill_from = Vector2(0.5, 0.5)
    _radial_texture.fill_to = Vector2(1.0, 0.5)
    return _radial_texture

## Everything about the volume layer and light that is fixed for the effect's life; set
## once per setup so the per-frame sync touches only progress and the light's fade.
func _configure_visual_layers() -> void:
    if _volume_sprite == null or _volume_material == null:
        return
    var palette := _volume_palette()
    var radius := _volume_radius()
    _intensity = _volume_intensity()
    _volume_sprite.rotation = _impact_axis.angle()
    # The plume sits under the code-drawn shapes; at full size and energy the two added up
    # to a flat white disc that hid the robot being hit.
    _volume_sprite.scale = Vector2.ONE * (radius * VOLUME_SIZE * 2.0 / 128.0)
    _volume_material.set_shader_parameter("primary_color", palette[0])
    _volume_material.set_shader_parameter("secondary_color", palette[1])
    _volume_material.set_shader_parameter("energy", _intensity * _flash_scale * VOLUME_ENERGY)
    _volume_material.set_shader_parameter("seed", float(_seed % 997))
    _volume_material.set_shader_parameter("style", _volume_style())
    if _flash_light == null:
        return
    _flash_light.position = _impact_axis * radius * 0.08
    _flash_light.color = Color(palette[0]).lightened(0.18)
    _flash_light.texture_scale = radius / 56.0

func _sync_visual_layers(t: float) -> void:
    if _volume_sprite == null or _volume_material == null:
        return
    _volume_sprite.visible = visible and not _retiring
    _volume_material.set_shader_parameter("progress", t)
    if _flash_light == null:
        return
    var flash := maxf(0.0, 1.0 - t / 0.24)
    _flash_light.enabled = flash > 0.01 and visible and not _retiring
    _flash_light.energy = flash * _intensity * 0.9 * _flash_scale

func _volume_palette() -> Array:
    if effect_kind == EFFECT_HURT:
        var hurt_color := Color("ff766b") if target_kind == "OPERATOR" else tint.lightened(0.12)
        var secondary := Color("ffb06f") if target_kind == "OPERATOR" else tint.darkened(0.24)
        if "BOSS" in target_id:
            secondary = Color("ef4fa8")
        return [hurt_color, secondary]
    var palette: Array = FAMILIES[family].palette
    if palette.is_empty():
        return [tint, tint.darkened(0.24)]
    return [Color(str(palette[0])), Color(str(palette[1]))]

func _volume_radius() -> float:
    if effect_kind == EFFECT_HURT:
        if "BOSS" in target_id: return 96.0
        match reaction:
            "DOWNED": return 76.0
            "HEAVY": return 62.0
            "LIGHT": return 48.0
            _: return 38.0
    return float(FAMILIES[family].radius)

func _volume_intensity() -> float:
    if effect_kind == EFFECT_HURT:
        var strength := 0.62
        match reaction:
            "LIGHT": strength = 0.76
            "HEAVY": strength = 0.98
            "DOWNED": strength = 1.16
        if critical: strength += 0.18
        if "BOSS" in target_id: strength += 0.22
        return strength
    return float(FAMILIES[family].energy)

func _volume_style() -> float:
    if effect_kind == EFFECT_HURT:
        return 1.2 if "BOSS" not in target_id else 3.5
    return float(FAMILIES[family].style)

# --- impacts -----------------------------------------------------------------------

func _draw_impact(t: float) -> void:
    var a := _impact_axis
    match family:
        "WEAPON_RAIL":
            _core(Vector2.ZERO,18.0,Color.WHITE,Color("62d9ef"),t)
            var reach := 22.0+48.0*Painter.ease_out(t)
            var side := a.orthogonal()
            for sign_value in [-1.0,1.0]:
                _paint.streak(-a*reach+side*sign_value*5.0,a*reach+side*sign_value*5.0,1.6,Color("b9f7ff",1.0-t),true)
            _sparks(Vector2.ZERO,a,5,0.55,30.0,80.0,t,Color("b9f7ff"),12.0,1.2,0)
        "WEAPON_NULL":
            _core(Vector2.ZERO,22.0,Color.WHITE,Color("d68eb5"),t)
            for i in range(3):
                var ray := a.rotated((float(i)-1.0)*0.7)
                _paint.streak(ray*(10.0+30.0*t),ray*(28.0+42.0*t),3.5*(1.0-t),Color("ffd8ed",1.0-t),true)
            _shock(Vector2.ZERO,8.0,58.0,0.40,t,Color("d68eb5"),2.4)
            _debris(Vector2.ZERO,a,5,1.8,18.0,58.0,t,Color("aa809e"),25.0,0)
        "ASTER":
            _core(Vector2.ZERO, 22.0, Color("c6f6ff"), Color("79ddff"), t)
            _star(Vector2.ZERO, a, 76.0, 3.2, Color("a8ecff"), t)
            _shock(Vector2.ZERO, 8.0, 58.0, 0.42, t, Color("7fdcff"), 3.2)
            _sparks(Vector2.ZERO, a, 12, 1.2, 44.0, 108.0, t, Color("8fe6ff"), 36.0, 1.7, 0)
            _sparks(Vector2.ZERO, a.rotated(0.22), 5, 0.9, 30.0, 72.0, t, Color("a48cff"), 24.0, 1.3, 40)
            _prism_shards(Vector2.ZERO, a, 7, 1.7, 30.0, 76.0, t, Color("d9f8ff"), Color("9a86ff"))
            _embers(Vector2.ZERO, a, 5, 54.0, t, Color("9fe8ff"), 80)
        "ROOK":
            _core(Vector2.ZERO, 28.0, Color("ffe2b0"), Color("ff9b45"), t)
            _star(Vector2.ZERO, a, 58.0, 4.2, Color("ffc46b"), t)
            _shock(Vector2.ZERO, 10.0, 66.0, 0.40, t, Color("ff9b45"), 4.4)
            _sparks(Vector2.ZERO, a, 14, 2.4, 36.0, 108.0, t, Color("ffc46b"), 70.0, 2.1, 0)
            _debris(Vector2.ZERO, a, 9, 2.6, 26.0, 84.0, t, Color("d08a50"), 90.0, 0)
            _embers(Vector2.ZERO, a, 7, 64.0, t, Color("ffae55"), 80)
            _dust(Vector2.ZERO, -a, 4, 30.0, t, Color("9a6038"), 0)
        "MICA":
            _core(Vector2.ZERO, 20.0, Color("c8fff6"), Color("74f0da"), t)
            _shock(Vector2.ZERO, 6.0, 66.0, 0.5, t, Color("74f0da"), 2.6)
            _shock(Vector2.ZERO, 4.0, 44.0, 0.5, maxf(0.0, t - 0.12), Color("c8fff6"), 1.8)
            _data_bits(Vector2.ZERO, a, 12, 70.0, t, Color("8effee"))
            _sparks(Vector2.ZERO, a, 8, 1.6, 26.0, 72.0, t, Color("b8fff4"), 10.0, 1.4, 0)
        "DRONE":
            _core(Vector2.ZERO, 20.0, Color("d0fbff"), Color("87f6ff"), t)
            _arcs(Vector2.ZERO, a, 4, 1.8, 74.0, t, Color("87f6ff"), 2.2, 0)
            _arcs(Vector2.ZERO, a.rotated(PI * 0.7), 2, 1.2, 52.0, t, Color("f15ba7"), 1.8, 20)
            _shock(Vector2.ZERO, 6.0, 48.0, 0.36, t, Color("f15ba7"), 2.2)
            _sparks(Vector2.ZERO, a, 8, 2.2, 24.0, 66.0, t, Color("b5ffff"), 14.0, 1.4, 0)
            _embers(Vector2.ZERO, a, 5, 44.0, t, Color("79efff"), 80)
        "BULWARK":
            _core(Vector2.ZERO, 32.0, Color("fff0c0"), Color("ffb347"), t)
            _star(Vector2.ZERO, a, 70.0, 4.6, Color("ffd073"), t)
            _shock(Vector2.ZERO, 12.0, 82.0, 0.42, t, Color("ffb347"), 5.0)
            _fireball(Vector2.ZERO, a, 6, 30.0, 34.0, t, 0)
            _sparks(Vector2.ZERO, a, 15, 2.3, 36.0, 116.0, t, Color("ffe09a"), 60.0, 2.1, 0)
            _debris(Vector2.ZERO, a, 8, 2.4, 26.0, 80.0, t, Color("d58a3e"), 80.0, 0)
            _embers(Vector2.ZERO, a, 7, 64.0, t, Color("ffc070"), 80)
        "PRISM":
            _core(Vector2.ZERO, 22.0, Color("ebe4ff"), Color("8a7bff"), t)
            _refraction(Vector2.ZERO, a, t)
            _prism_shards(Vector2.ZERO, a, 6, 2.0, 28.0, 72.0, t, Color("e2dcff"), Color("ff7ad9"))
            _shock(Vector2.ZERO, 8.0, 52.0, 0.4, t, Color("8a7bff"), 2.6)
            _sparks(Vector2.ZERO, a, 8, 1.8, 26.0, 76.0, t, Color("c6bcff"), 16.0, 1.4, 0)
        "RAM":
            _core(Vector2.ZERO, 32.0, Color("ffe8c0"), Color("ff8a3d"), t)
            _fireball(Vector2.ZERO, a, 7, 34.0, 40.0, t, 0)
            _shock(Vector2.ZERO, 12.0, 90.0, 0.42, t, Color("ef9251"), 5.2)
            _sparks(Vector2.ZERO, a, 14, 2.6, 38.0, 116.0, t, Color("ffb070"), 70.0, 2.0, 0)
            _debris(Vector2.ZERO, a, 8, 2.8, 30.0, 90.0, t, Color("c86a38"), 90.0, 0)
            _embers(Vector2.ZERO, a, 9, 70.0, t, Color("ff9c50"), 80)
        "ANCHOR":
            _rift(Vector2.ZERO, t, Color("c9b2ff"), Color("f05aa8"), 96.0)
            _core(Vector2.ZERO, 38.0, Color("eadcff"), Color("9b62ff"), maxf(0.0, t - 0.06))
            _shock(Vector2.ZERO, 14.0, 124.0, 0.5, maxf(0.0, t - 0.06), Color("b9a0ff"), 5.6)
            _arcs(Vector2.ZERO, a, 4, 2.6, 112.0, t, Color("c0a2ff"), 2.8, 0)
            _sparks(Vector2.ZERO, a, 16, 3.6, 40.0, 134.0, t, Color("dbc9ff"), 18.0, 2.2, 0)
            _debris(Vector2.ZERO, -a, 8, 3.1, 30.0, 92.0, t, Color("c35aa8"), 20.0, 0)
            _embers(Vector2.ZERO, a, 9, 96.0, t, Color("d9b8ff"), 80)
        "RELAY":
            _core(Vector2.ZERO, 32.0, Color("ffe4e7"), Color("d8283c"), t)
            _shock(Vector2.ZERO, 12.0, 104.0, 0.46, t, Color("d8283c"), 4.8)
            _arcs(Vector2.ZERO, a, 5, 2.4, 104.0, t, Color("ff6d7d"), 2.3, 0)
            _sparks(Vector2.ZERO, a, 13, 2.4, 28.0, 118.0, t, Color("ffd0d5"), 20.0, 1.8, 0)
        "REMNANT":
            _core(Vector2.ZERO, 30.0, Color("ffffff"), Color("bfe8ff"), t)
            _shock(Vector2.ZERO, 9.0, 100.0, 0.40, t, Color("bfe8ff"), 3.8)
            _arcs(Vector2.ZERO, a.rotated(0.6), 6, 2.9, 112.0, t, Color("e8f7ff"), 2.5, 0)
            _sparks(Vector2.ZERO, a, 11, 3.0, 24.0, 116.0, t, Color("ffffff"), 10.0, 1.5, 0)
        "FORGE":
            _core(Vector2.ZERO, 38.0, Color("e2ffff"), Color("56e3e8"), t)
            _star(Vector2.ZERO, a, 96.0, 5.2, Color("8ff8ff"), t)
            _shock(Vector2.ZERO, 14.0, 106.0, 0.46, t, Color("56e3e8"), 5.4)
            _molten(Vector2.ZERO, a, 11, 96.0, t, Color("a8fbff"))
            _sparks(Vector2.ZERO, a, 15, 3.0, 40.0, 126.0, t, Color("c8ffff"), 60.0, 2.2, 0)
            _embers(Vector2.ZERO, a, 9, 90.0, t, Color("56e3e8"), 80)
        "CARRIER":
            _rift(Vector2.ZERO, t, Color("c8b0ff"), Color("7b4dff"), 104.0)
            _core(Vector2.ZERO, 36.0, Color("efe6ff"), Color("a27aff"), maxf(0.0, t - 0.08))
            _shock(Vector2.ZERO, 10.0, 118.0, 0.5, maxf(0.0, t - 0.08), Color("a27aff"), 5.0)
            _hex(Vector2.ZERO, 26.0 + 60.0 * Painter.ease_out(t * 2.0), t, Color("d0b8ff"), 0.0)
            _arcs(Vector2.ZERO, a, 3, TAU, 96.0, t, Color("d0b8ff"), 2.4, 0)
            _sparks(Vector2.ZERO, a, 14, TAU, 40.0, 116.0, t, Color("e2d4ff"), 12.0, 2.0, 0)
        "AERATOR":
            # A spore burst: a lime bloom of petals, drifting spores and lit vapour.
            _core(Vector2.ZERO, 34.0, Color("f2ffd0"), Color("8fdc4a"), t)
            _shock(Vector2.ZERO, 12.0, 112.0, 0.48, t, Color("8fdc4a"), 4.6)
            _bloom(Vector2.ZERO, a, t, Color("d6ff9a"), Color("8fdc4a"))
            _dust(Vector2.ZERO, a, 6, 78.0, t, Color("8fdc4a"), 0)
            _spores(Vector2.ZERO, a, 12, 104.0, t, Color("b8f070"), 0)
        "CRYO":
            # Frost shatter: a six-armed crystal flashes, glass splinters fly.
            _core(Vector2.ZERO, 32.0, Color("fff2fa"), Color("ff7fc8"), t)
            _crystal(Vector2.ZERO, a, t, Color("ffe1f2"))
            _shock(Vector2.ZERO, 10.0, 104.0, 0.44, t, Color("ff7fc8"), 4.0)
            _prism_shards(Vector2.ZERO, a, 9, 2.4, 30.0, 96.0, t, Color("fff0fa"), Color("ff7fc8"))
            _sparks(Vector2.ZERO, a, 8, 2.0, 30.0, 96.0, t, Color("ffd4ee"), 30.0, 1.5, 0)
        "GANTRY":
            # Rail arc: a bright line through the hit, yellow arcs and long sparks.
            _core(Vector2.ZERO, 34.0, Color("fffbe0"), Color("ffd84a"), t)
            _rail_flash(Vector2.ZERO, a, t, Color("fff4b0"))
            _arcs(Vector2.ZERO, a, 6, TAU, 108.0, t, Color("ffe16b"), 2.6, 0)
            _shock(Vector2.ZERO, 10.0, 108.0, 0.42, t, Color("ffd84a"), 4.4, 0.7)
            _sparks(Vector2.ZERO, a, 16, 3.2, 34.0, 132.0, t, Color("fff2a0"), 50.0, 2.0, 0)
        "ARCHIVE":
            # Glyph scatter: teal brackets and data bits blown out of the record.
            _core(Vector2.ZERO, 30.0, Color("e6fff8"), Color("2fe0b4"), t)
            _glyphs(Vector2.ZERO, a, 6, 96.0, t, Color("2fe0b4"))
            _data_bits(Vector2.ZERO, a, 14, 96.0, t, Color("8effe0"))
            _shock(Vector2.ZERO, 9.0, 100.0, 0.44, t, Color("2fe0b4"), 3.6)
            _sparks(Vector2.ZERO, a, 8, 1.6, 26.0, 84.0, t, Color("c8fff0"), 10.0, 1.4, 0)
        "ORIGIN":
            # A fracture: white cracks run out of the hit and dark alloy chips fly.
            _core(Vector2.ZERO, 38.0, Color("ffffff"), Color("f4efe8"), t)
            _cracks(Vector2.ZERO, a, 7, 118.0, t, Color("ffffff"))
            _shock(Vector2.ZERO, 12.0, 118.0, 0.46, t, Color("f4efe8"), 4.8)
            _debris(Vector2.ZERO, a, 8, 2.8, 28.0, 96.0, t, Color("9a968f"), 60.0, 0)
            _sparks(Vector2.ZERO, a, 14, 3.0, 36.0, 128.0, t, Color("ffffff"), 40.0, 1.8, 0)
        "DEFLECT":
            var face := Vector2(-a.y, a.x)
            _core(Vector2.ZERO, 18.0, Color("fff2cc"), Color("ffc864"), t)
            _hex(Vector2.ZERO, 30.0 + 8.0 * t, t, Color("ffe09a"), a.angle())
            _sparks(Vector2.ZERO, (a + face * 1.4).normalized(), 7, 0.6, 40.0, 110.0, t, Color("fff0c0"), 30.0, 1.4, 0)
            _sparks(Vector2.ZERO, (a - face * 1.4).normalized(), 7, 0.6, 40.0, 110.0, t, Color("ffd080"), 30.0, 1.4, 30)
        "BARRIER":
            _core(Vector2.ZERO, 22.0, Color("e6fbff"), Color("a5e8fa"), t)
            _hex(Vector2.ZERO, 36.0 + 18.0 * Painter.ease_out(t * 2.0), t, Color("a5e8fa"), a.angle())
            _shock(Vector2.ZERO, 10.0, 70.0, 0.5, t, Color("7fb8ff"), 3.0)
            _shock(Vector2.ZERO, 6.0, 46.0, 0.5, maxf(0.0, t - 0.14), Color("c8f4ff"), 2.0)
            _sparks(Vector2.ZERO, a, 9, 2.0, 26.0, 74.0, t, Color("d2f6ff"), 10.0, 1.4, 0)
        _:
            var hot := tint.lightened(0.45)
            _core(Vector2.ZERO, 22.0, hot, tint, t)
            _star(Vector2.ZERO, a, 56.0, 3.0, hot, t)
            _shock(Vector2.ZERO, 8.0, 56.0, 0.4, t, tint, 3.0)
            _sparks(Vector2.ZERO, a, 10, 1.9, 30.0, 86.0, t, hot, 30.0, 1.6, 0)
            _embers(Vector2.ZERO, a, 5, 52.0, t, tint, 80)

func _draw_cover_chips(t: float) -> void:
    _dust(Vector2.ZERO, _impact_axis, 5, 38.0, t, Color("8c8272"), 200)
    _debris(Vector2.ZERO, _impact_axis, 7, 2.2, 22.0, 70.0, t, Color("b7ad9c"), 110.0, 200)

# --- hurt reactions ------------------------------------------------------------------

func _draw_hurt(t: float) -> void:
    var is_boss := "BOSS" in target_id
    var is_drone := "DRONE" in target_id or "PRISM" in target_id
    var radius := 76.0 if is_boss else (32.0 if is_drone else (40.0 if target_kind == "OPERATOR" else 48.0))
    var strength := 0.7
    match reaction:
        "LIGHT": strength = 0.86
        "HEAVY": strength = 1.1
        "DOWNED": strength = 1.3
    var a := _impact_axis
    var contact := a * radius * 0.12
    if target_kind == "OPERATOR":
        var hurt := Color("ff7a66")
        _core(contact, radius * 0.48 * strength, Color("ffd2c4"), hurt, t)
        _shock(contact, radius * 0.2, radius * (0.9 + 0.5 * strength), 0.4, t, Color("ff5c4f"), 2.2 + strength)
        # The player's own squad getting hit must read at a glance: a red star and armour
        # shards thrown off the suit.
        _star(contact, a, radius * (0.7 + 0.5 * strength), 2.2, Color("ff6a5a"), t)
        _prism_shards(contact, a, 4 + int(strength * 4.0), 3.2, radius * 0.4, radius * 1.3, t, Color("ffb09a"), Color("ff4f5e"))
        _sparks(contact, a, 5 + int(strength * 4.0), 1.8, radius * 0.4, radius * 1.2, t, Color("ffc2a8"), radius * 0.3, 1.5, 0)
        if reaction == "DOWNED":
            _shock(Vector2(0.0, radius * 0.9), radius * 0.4, radius * 2.2, 0.6, t, Color("ff5c4f"), 4.0, 0.45)
            _embers(contact, Vector2.UP, 8, radius * 1.4, t, Color("ff8a70"), 80)
    else:
        var hurt := tint.lightened(0.18)
        _core(contact, radius * 0.42 * strength, hurt.lightened(0.4), hurt, t)
        _arcs(contact, a, 1 + int(strength * 2.0), 2.4, radius * (0.9 + 0.4 * strength), t, hurt.lightened(0.25), 1.6 + strength, 0)
        _sparks(contact, a, 4 + int(strength * 5.0), 1.5, radius * 0.4, radius * 1.15, t, Color("fff0d0"), radius * 0.5, 1.5, 0)
        _embers(contact, a, 2 + int(strength * 3.0), radius * 0.9, t, hurt, 80)
        if reaction == "HEAVY" or reaction == "DOWNED":
            _shock(contact, radius * 0.16, radius * (1.0 + 0.4 * strength), 0.4, t, hurt, 2.8)
            _debris(contact, a, 5 + int(strength * 3.0), 2.4, radius * 0.36, radius * 1.1, t, Color("c8c2b8"), radius * 1.2, 0)
            _dust(contact, -a, 4, radius * 0.6, t, hurt.darkened(0.4), 60)
    if critical:
        _star(contact, a.rotated(0.5), radius * 1.3, 2.6, Color("ffd37d"), t)

# --- shape vocabulary ---------------------------------------------------------------

## White-hot centre over a tinted bloom; gone in the first quarter of the life.
func _core(origin: Vector2, radius: float, hot: Color, color: Color, t: float) -> void:
    var flash := Painter.fade_window(t, 0.0, 0.2)
    if flash > 0.0:
        _paint.glow(origin, radius * (0.4 + 0.45 * Painter.ease_out(t * 5.0)), Color(hot, 0.9 * flash), 10)
    var bloom := Painter.fade_window(t, 0.05, 0.55)
    if bloom > 0.0:
        _paint.glow(origin, radius * (1.1 + 0.8 * Painter.ease_out(t * 2.5)), Color(color, 0.3 * bloom), 12)

## Anamorphic star flare in the first frames of the hit.
func _star(origin: Vector2, axis: Vector2, length: float, width: float, color: Color, t: float) -> void:
    var life := Painter.fade_window(t, 0.0, 0.24)
    if life <= 0.0:
        return
    var grow := 0.55 + 0.6 * Painter.ease_out(t * 8.0)
    _paint.flare(origin, axis.orthogonal(), length * grow * life, width * (0.5 + 0.5 * life), Color(color, 0.9 * life), 0.42)

## Expanding soft ring, `duration` in fractions of the life.
func _shock(origin: Vector2, r0: float, r1: float, duration: float, t: float, color: Color, width: float, squash := 1.0) -> void:
    if t >= duration:
        return
    var k := t / duration
    var fade := (1.0 - k) * (1.0 - k)
    _paint.ring(origin, lerpf(r0, r1, Painter.ease_out(k)), width * (1.0 - 0.5 * k), Color(color, 0.85 * fade), 20, 0.0, TAU, squash)

func _ballistic(origin: Vector2, direction: Vector2, distance: float, gravity: float, t: float, speed: float) -> Vector2:
    var e := 1.0 - minf(1.0, t * speed)
    return origin + direction * (distance * (1.0 - e * e * e)) + Vector2(0.0, gravity * t * t)

## Particle count after crowd thinning (see CROWD).
func _thin(count: int) -> int:
    return count if _density >= 1.0 else maxi(1, ceili(float(count) * _density))

## Fast streaks fanning out around `axis`, curving under gravity. Each tail is where the
## spark was a moment earlier, so early sparks are long and late ones short.
func _sparks(origin: Vector2, axis: Vector2, count: int, spread: float, min_length: float, max_length: float, t: float, color: Color, gravity: float, width: float, offset: int) -> void:
    count = _thin(count)
    var alpha := 1.0 - t * 1.1
    if alpha <= 0.0:
        return
    for i in range(count):
        var r0 := _random01(400 + offset + i)
        var direction := axis.rotated((_random01(440 + offset + i) - 0.5) * spread)
        var distance := lerpf(min_length, max_length, r0)
        var g := gravity * (0.4 + _random01(460 + offset + i))
        var speed := 1.3 + 0.6 * _random01(480 + offset + i)
        var head := _ballistic(origin, direction, distance, g, t, speed)
        var tail := _ballistic(origin, direction, distance, g, maxf(0.0, t - 0.07), speed)
        var w := width * (0.6 + 0.8 * _random01(500 + offset + i)) * (1.0 - 0.5 * t)
        _paint.streak(tail, head, w, Color(color, alpha * (0.6 + 0.4 * _random01(520 + offset + i))), i < 3)

## Spinning metal / stone fragments thrown along `axis`.
func _debris(origin: Vector2, axis: Vector2, count: int, spread: float, min_distance: float, max_distance: float, t: float, color: Color, gravity: float, offset: int) -> void:
    count = _thin(count)
    var alpha := 1.0 - t * 0.95
    if alpha <= 0.0:
        return
    for i in range(count):
        var direction := axis.rotated((_random01(560 + offset + i) - 0.5) * spread)
        var distance := lerpf(min_distance, max_distance, _random01(580 + offset + i))
        var position := _ballistic(origin, direction, distance, gravity * (0.4 + _random01(600 + offset + i)), t, 1.15)
        var spin := (_random01(620 + offset + i) - 0.5) * PI + t * (3.0 + _random01(640 + offset + i) * 6.0)
        _paint.shard(position, spin, 2.6 + _random01(660 + offset + i) * 4.4, Color(color, alpha * (0.55 + 0.35 * _random01(680 + offset + i))))

## Glass fragments in two alternating colours with a bright glint each.
func _prism_shards(origin: Vector2, axis: Vector2, count: int, spread: float, min_distance: float, max_distance: float, t: float, color_a: Color, color_b: Color) -> void:
    count = _thin(count)
    var alpha := 1.0 - t * 1.05
    if alpha <= 0.0:
        return
    for i in range(count):
        var direction := axis.rotated((_random01(700 + i) - 0.5) * spread)
        var distance := lerpf(min_distance, max_distance, _random01(720 + i))
        var position := _ballistic(origin, direction, distance, 20.0 * _random01(740 + i), t, 1.3)
        var spin := direction.angle() + t * (4.0 + 5.0 * _random01(760 + i))
        var size := 3.4 + 4.0 * _random01(780 + i)
        var color := color_a if i % 2 == 0 else color_b
        _paint.shard(position, spin, size, Color(color, alpha * 0.8))
        _paint.dot(position, size * 1.6, Color(color, alpha * 0.28))

## Small glowing specks drifting out and settling, flickering.
func _embers(origin: Vector2, axis: Vector2, count: int, reach: float, t: float, color: Color, offset: int) -> void:
    count = _thin(count)
    var alpha := 1.0 - t
    if alpha <= 0.0:
        return
    for i in range(count):
        var direction := axis.rotated((_random01(800 + offset + i) - 0.5) * 3.0)
        var distance := reach * (0.3 + 0.7 * _random01(820 + offset + i))
        var position := _ballistic(origin, direction, distance, reach * 0.35, t, 1.0)
        var flicker := 0.65 + 0.35 * sin(age * 38.0 + float(i) * 2.1)
        var size := 1.6 + 1.8 * _random01(840 + offset + i)
        _paint.dot(position, size * 2.6, Color(color, alpha * 0.45 * flicker))
        _paint.dot(position, size, Color(color.lightened(0.5), alpha * flicker))

## Dim additive puffs: lit dust / vapour hanging where the round struck.
func _dust(origin: Vector2, axis: Vector2, count: int, radius: float, t: float, color: Color, offset: int) -> void:
    count = _thin(count)
    var alpha := 1.0 - t
    if alpha <= 0.0:
        return
    var drift := Painter.ease_out(t)
    for i in range(count):
        var direction := axis.rotated((_random01(860 + offset + i) - 0.5) * 2.4)
        var position := origin + direction * radius * drift * (0.4 + 0.8 * _random01(870 + offset + i)) + Vector2(0.0, -radius * 0.3 * t)
        var puff := radius * (0.35 + 0.3 * _random01(880 + offset + i)) * (0.7 + 0.8 * t)
        _paint.glow(position, puff, Color(color, alpha * 0.22), 8)

## Hot gas blobs that cool from white through orange to dull red.
func _fireball(origin: Vector2, axis: Vector2, count: int, reach: float, blob: float, t: float, offset: int) -> void:
    count = _thin(count)
    var alpha := pow(maxf(0.0, 1.0 - t), 1.3)
    if alpha <= 0.0:
        return
    var color := fire_color(t)
    for i in range(count):
        var direction := axis.rotated((_random01(900 + offset + i) - 0.5) * 3.2)
        var position := origin + direction * reach * Painter.ease_out(t * 1.8) * (0.3 + 0.7 * _random01(910 + offset + i)) + Vector2(0.0, -blob * 0.5 * t)
        var size := blob * (0.5 + 0.5 * _random01(920 + offset + i)) * (0.6 + 0.9 * Painter.ease_out(t * 2.2))
        _paint.glow(position, size, Color(color, alpha * 0.55), 10)

## Colour of cooling fire at life fraction t.
static func fire_color(t: float) -> Color:
    if t < 0.12: return Color("fff6d8").lerp(Color("ffcf5c"), t / 0.12)
    if t < 0.4: return Color("ffcf5c").lerp(Color("ff7a2a"), (t - 0.12) / 0.28)
    if t < 0.75: return Color("ff7a2a").lerp(Color("b8321a"), (t - 0.4) / 0.35)
    return Color("b8321a").lerp(Color("4a1208"), (t - 0.75) / 0.25)

## Electric arcs that re-strike about 30 times a second.
func _arcs(origin: Vector2, axis: Vector2, count: int, spread: float, length: float, t: float, color: Color, width: float, offset: int) -> void:
    count = _thin(count)
    var alpha := 1.0 - t * 1.4
    if alpha <= 0.0:
        return
    var strike := int(age * 30.0)
    for i in range(count):
        var direction := axis.rotated((_random01(940 + offset + i) - 0.5) * spread)
        var reach := length * (0.55 + 0.45 * _random01(950 + offset + i)) * Painter.ease_out(t * 6.0)
        _paint.bolt(origin, origin + direction * reach, 5, reach * 0.22, width, Color(color, alpha), _seed + strike * 131 + i * 17 + offset)

## Tiny squares (sensor data) spreading from the hit and blinking out.
func _data_bits(origin: Vector2, axis: Vector2, count: int, reach: float, t: float, color: Color) -> void:
    count = _thin(count)
    for i in range(count):
        var born := _random01(960 + i) * 0.3
        var local_t := (t - born) / 0.7
        if local_t <= 0.0 or local_t >= 1.0:
            continue
        var direction := axis.rotated((_random01(970 + i) - 0.5) * 3.4)
        var position := origin + direction * reach * (0.3 + 0.7 * _random01(980 + i)) * Painter.ease_out(local_t)
        var size := 2.0 + 2.2 * _random01(990 + i)
        var blink := 1.0 if int(age * 24.0 + i) % 3 != 0 else 0.35
        var c := Color(color, (1.0 - local_t) * blink)
        _paint.quad(position + Vector2(-size, -size), position + Vector2(size, -size), position + Vector2(size, size), position + Vector2(-size, size), c)

## Three rays split into the spectrum, like light through a prism.
func _refraction(origin: Vector2, axis: Vector2, t: float) -> void:
    var alpha := 1.0 - t * 1.3
    if alpha <= 0.0:
        return
    var colors := [Color("ff6fd8"), Color("8a7bff"), Color("6fe7ff")]
    var reach := 96.0 * Painter.ease_out(t * 4.0)
    for i in range(3):
        var direction := axis.rotated((float(i) - 1.0) * 0.34)
        _paint.fading_beam(origin, origin + direction * reach, 3.6, Color(colors[i], alpha), 1.0, 0.0)

## Space folding in, then bursting: particles converge for the first 20 %, then fly out.
func _rift(origin: Vector2, t: float, color: Color, accent: Color, reach: float) -> void:
    if t < 0.2:
        var k := t / 0.2
        for i in range(12):
            var direction := Vector2.from_angle(TAU * float(i) / 12.0 + _random01(1000 + i) * 0.4)
            var distance := reach * (1.0 - Painter.ease_in(k)) * (0.7 + 0.3 * _random01(1010 + i))
            var head := origin + direction * distance
            _paint.streak(head + direction * reach * 0.22, head, 1.8, Color(color if i % 2 == 0 else accent, 0.5 + 0.5 * k))
        _paint.ring(origin, reach * (1.0 - 0.8 * Painter.ease_in(k)), 4.0, Color(accent, 0.5 * k), 20)
    else:
        var k2 := (t - 0.2) / 0.8
        _paint.ring(origin, reach * 0.2 + reach * 0.5 * Painter.ease_out(k2), 3.0 * (1.0 - k2), Color(accent, 0.7 * (1.0 - k2)), 20)

## Molten droplets thrown in arcs, each with a short glowing tail.
func _molten(origin: Vector2, axis: Vector2, count: int, reach: float, t: float, color: Color) -> void:
    count = _thin(count)
    var alpha := 1.0 - t
    if alpha <= 0.0:
        return
    for i in range(count):
        var direction := axis.rotated((_random01(1100 + i) - 0.5) * 2.6)
        var distance := reach * (0.4 + 0.6 * _random01(1110 + i))
        var g := reach * (1.0 + _random01(1120 + i))
        var head := _ballistic(origin, direction + Vector2(0.0, -0.5), distance, g, t, 1.1)
        var tail := _ballistic(origin, direction + Vector2(0.0, -0.5), distance, g, maxf(0.0, t - 0.1), 1.1)
        _paint.streak(tail, head, 2.6, Color(color, alpha * 0.8))
        _paint.dot(head, 5.0, Color(color, alpha * 0.6))

## Five petals opening around the hit and turning slowly: the bloom of a spore burst.
func _bloom(origin: Vector2, axis: Vector2, t: float, color_a: Color, color_b: Color) -> void:
    var alpha := Painter.fade_window(t, 0.02, 0.85)
    if alpha <= 0.0:
        return
    var open := Painter.ease_out(t * 2.4)
    for i in range(5):
        var angle := axis.angle() + TAU * float(i) / 5.0 + t * 0.9
        var tip := origin + Vector2.from_angle(angle) * (16.0 + 44.0 * open)
        var color := color_a if i % 2 == 0 else color_b
        _paint.shard(tip, angle, 7.0 + 15.0 * open, Color(color, alpha * 0.85))
        _paint.dot(tip, 9.0 + 6.0 * open, Color(color_b, alpha * 0.3))

## Soft lit motes that swell as they drift out and up, each with a halo, swaying.
func _spores(origin: Vector2, axis: Vector2, count: int, reach: float, t: float, color: Color, offset: int) -> void:
    count = _thin(count)
    var alpha := pow(maxf(0.0, 1.0 - t), 1.2)
    if alpha <= 0.0:
        return
    for i in range(count):
        var direction := axis.rotated((_random01(1200 + offset + i) - 0.5) * 3.6)
        var position := origin + direction * reach * Painter.ease_out(t * 1.6) * (0.35 + 0.65 * _random01(1220 + offset + i)) + Vector2(0.0, -reach * 0.22 * t)
        var size := 3.0 + 3.6 * _random01(1240 + offset + i)
        var sway := 0.7 + 0.3 * sin(age * 9.0 + float(i) * 1.7)
        _paint.glow(position, size * 3.2 * (0.7 + 0.6 * t), Color(color, alpha * 0.22 * sway), 8)
        _paint.dot(position, size, Color(color.lightened(0.5), alpha * sway))

## A six-armed frost crystal that flashes out from the hit; each arm has two barbs.
func _crystal(origin: Vector2, axis: Vector2, t: float, color: Color) -> void:
    var alpha := Painter.fade_window(t, 0.0, 0.5)
    if alpha <= 0.0:
        return
    var reach := 88.0 * Painter.ease_out(t * 5.0)
    for i in range(6):
        var direction := Vector2.from_angle(axis.angle() + TAU * float(i) / 6.0)
        _paint.streak(origin + direction * reach * 0.08, origin + direction * reach, 2.4, Color(color, alpha))
        for side in [-1.0, 1.0]:
            var barb := direction.rotated(0.6 * side)
            _paint.streak(origin + direction * reach * 0.55, origin + direction * reach * 0.55 + barb * reach * 0.28, 1.5, Color(color, alpha * 0.8))

## A bright rail of light through the hit, along the shot both ways, and a short cross line.
func _rail_flash(origin: Vector2, axis: Vector2, t: float, color: Color) -> void:
    var alpha := Painter.fade_window(t, 0.0, 0.34)
    if alpha <= 0.0:
        return
    var length := 128.0 * Painter.ease_out(t * 6.0)
    _paint.fading_beam(origin, origin + axis * length, 5.0, Color(color, alpha), 1.0, 0.0)
    _paint.fading_beam(origin, origin - axis * length, 5.0, Color(color, alpha), 1.0, 0.0)
    _paint.fading_beam(origin, origin + axis.orthogonal() * length * 0.4, 3.0, Color(color, alpha * 0.8), 1.0, 0.0)
    _paint.fading_beam(origin, origin - axis.orthogonal() * length * 0.4, 3.0, Color(color, alpha * 0.8), 1.0, 0.0)

## Square brackets (index glyphs) blown out from the hit, turning and fading.
func _glyphs(origin: Vector2, axis: Vector2, count: int, reach: float, t: float, color: Color) -> void:
    count = _thin(count)
    var alpha := 1.0 - t
    if alpha <= 0.0:
        return
    for i in range(count):
        var direction := axis.rotated((_random01(1300 + i) - 0.5) * 3.4)
        var position := origin + direction * reach * Painter.ease_out(t * 1.8) * (0.35 + 0.65 * _random01(1320 + i))
        var size := 5.0 + 6.0 * _random01(1340 + i)
        var spin := _random01(1360 + i) * PI + t * (1.5 + 2.0 * _random01(1380 + i))
        _paint.polygon_outline(position, size, 4, spin, 1.5, Color(color, alpha * 0.85))

## Hairline cracks running out of the hit: fixed jagged lines that lengthen and dim.
func _cracks(origin: Vector2, axis: Vector2, count: int, reach: float, t: float, color: Color) -> void:
    var alpha := 1.0 - t * 1.15
    if alpha <= 0.0:
        return
    var run := reach * Painter.ease_out(t * 5.0)
    for i in range(count):
        var direction := axis.rotated((_random01(1400 + i) - 0.5) * TAU)
        var length := run * (0.5 + 0.5 * _random01(1420 + i))
        _paint.bolt(origin, origin + direction * length, 4, length * 0.12, 1.5, Color(color, alpha), _seed + i * 31)

## Hexagonal barrier plate flashing at the contact point.
func _hex(origin: Vector2, radius: float, t: float, color: Color, angle: float) -> void:
    var alpha := Painter.fade_window(t, 0.1, 0.7)
    if alpha <= 0.0:
        return
    _paint.polygon_outline(origin, radius, 6, angle, 2.4, Color(color, 0.85 * alpha), 0.7)
    _paint.polygon_outline(origin, radius * 0.62, 6, angle + PI / 6.0, 1.4, Color(color, 0.45 * alpha), 0.7)

func _random01(index: int) -> float:
    return _noise[(_noise_base + index) & (Painter.NOISE_SIZE - 1)]

func _seed_angle(index: int) -> float:
    return _random01(index) * TAU - PI
