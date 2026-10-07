extends Node2D
class_name Site7LightingRig

# Compatibility renderer additive lights remain semantic-only. Visible lighting
# comes from authored room SVG emissives and dynamic overlay glows.
const LIGHTS := [
    [Vector2(280,440), Color("d98a37")],
    [Vector2(690,320), Color("59d9ed")],
    [Vector2(1100,460), Color("55e8d2")],
    [Vector2(1510,320), Color("e26851")],
    [Vector2(1920,460), Color("9873ff")],
    [Vector2(2330,320), Color("67de91")],
    [Vector2(1100,685), Color("dd9b43")],
    [Vector2(1510,685), Color("55dfd2")]
]

var _radial_texture: Texture2D
var _lights: Array[PointLight2D] = []

func _ready() -> void:
    add_to_group("m6_lighting_rig")
    _radial_texture = _make_radial_texture(128)
    var modulate := CanvasModulate.new()
    modulate.name = "Site7CanvasModulate"
    # Production plates already contain their authored light and shadow.
    # A second blue grade obscures both these plates and the accepted actors.
    modulate.color = Color.WHITE
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
