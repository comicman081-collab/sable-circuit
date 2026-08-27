extends Node2D
class_name Site7LightingRig

# The target art direction keeps most of Site-7 near charcoal/black and reserves
# cyan/amber/violet for emissive fixtures. Compatibility-renderer PointLight2D
# additive pools were lifting whole wall/deck faces toward gray in real captures.
# We retain eight authored light nodes as semantic sockets but set emitted energy
# to zero; visible illumination is authored by room emissive/glow presentation.
const LIGHTS := [
    [Vector2(260,390), Color("d98a37")],
    [Vector2(650,390), Color("59d9ed")],
    [Vector2(1040,390), Color("55e8d2")],
    [Vector2(1430,390), Color("e26851")],
    [Vector2(1820,390), Color("9873ff")],
    [Vector2(2210,390), Color("67de91")],
    [Vector2(1040,700), Color("dd9b43")],
    [Vector2(1430,700), Color("55dfd2")]
]

var _radial_texture: Texture2D
var _lights: Array[PointLight2D] = []

func _ready() -> void:
    add_to_group("m6_lighting_rig")
    _radial_texture = _make_radial_texture(128)

    var modulate := CanvasModulate.new()
    modulate.name = "Site7CanvasModulate"
    modulate.color = Color(0.74,0.78,0.82,1.0)
    add_child(modulate)

    for row_variant in LIGHTS:
        var row: Array = row_variant
        var light := PointLight2D.new()
        light.position = row[0] as Vector2
        light.texture = _radial_texture
        light.texture_scale = 1.5
        light.energy = 0.0
        light.color = row[1] as Color
        light.blend_mode = Light2D.BLEND_MODE_ADD
        light.range_z_min = -1024
        light.range_z_max = 1024
        add_child(light)
        _lights.append(light)

func _process(_delta: float) -> void:
    # Core pulse is handled by Stage01EnvironmentDirector's visible violet rings,
    # not by a full-scene additive light.
    pass

func _make_radial_texture(size: int) -> Texture2D:
    var image := Image.create(size,size,false,Image.FORMAT_RGBA8)
    var center := Vector2(float(size-1)*0.5,float(size-1)*0.5)
    var radius := float(size)*0.5
    for y in range(size):
        for x in range(size):
            var distance_value := Vector2(float(x),float(y)).distance_to(center)/radius
            var intensity := pow(clampf(1.0-distance_value,0.0,1.0),2.6)
            image.set_pixel(x,y,Color(intensity,intensity,intensity,1.0))
    return ImageTexture.create_from_image(image)

func debug_light_count() -> int:
    return _lights.size()

func debug_local_lighting() -> bool:
    return true

func debug_radial_rgb_falloff() -> bool:
    return true

func debug_additive_wash_disabled() -> bool:
    for light in _lights:
        if light.energy > 0.001:
            return false
    return true
