extends Node2D
class_name Site7LightingRig

const LIGHTS := [
    [Vector2(260,390), Color("d98a37"), 0.70, 2.8],
    [Vector2(650,390), Color("59d9ed"), 0.78, 3.0],
    [Vector2(1040,390), Color("55e8d2"), 0.68, 2.9],
    [Vector2(1430,390), Color("e26851"), 0.72, 2.9],
    [Vector2(1820,390), Color("9873ff"), 0.90, 3.4],
    [Vector2(2210,390), Color("67de91"), 0.68, 2.9],
    [Vector2(1040,700), Color("dd9b43"), 0.58, 2.4],
    [Vector2(1430,700), Color("55dfd2"), 0.62, 2.5]
]

var _radial_texture: Texture2D
var _lights: Array[PointLight2D] = []

func _ready() -> void:
    add_to_group("m6_lighting_rig")
    _radial_texture = _make_radial_texture(128)
    var modulate := CanvasModulate.new()
    modulate.name = "Site7CanvasModulate"
    modulate.color = Color(0.72,0.78,0.82,1.0)
    add_child(modulate)

    for row_variant in LIGHTS:
        var row: Array = row_variant
        var position_value: Vector2 = row[0]
        var color_value: Color = row[1]
        var energy_value: float = row[2]
        var scale_value: float = row[3]
        var light := PointLight2D.new()
        light.position = position_value
        light.texture = _radial_texture
        light.texture_scale = scale_value
        light.energy = energy_value
        light.color = color_value
        light.blend_mode = Light2D.BLEND_MODE_ADD
        light.range_z_min = -1024
        light.range_z_max = 1024
        add_child(light)
        _lights.append(light)

func _process(_delta: float) -> void:
    # Core C breathes subtly in sync with the signal-anchor ambience. The rest
    # remain stable so gameplay readability does not pulse.
    if _lights.size() >= 5:
        var core := _lights[4]
        core.energy = 0.88 + sin(Time.get_ticks_msec()*0.0015)*0.08

func _make_radial_texture(size: int) -> Texture2D:
    var image := Image.create(size,size,false,Image.FORMAT_RGBA8)
    var center := Vector2(float(size-1)*0.5,float(size-1)*0.5)
    var radius := float(size)*0.5
    for y in range(size):
        for x in range(size):
            var distance_value := Vector2(float(x),float(y)).distance_to(center)/radius
            var alpha := clampf(1.0-distance_value,0.0,1.0)
            alpha = alpha*alpha*(3.0-2.0*alpha)
            image.set_pixel(x,y,Color(1.0,1.0,1.0,alpha))
    return ImageTexture.create_from_image(image)

func debug_light_count() -> int:
    return _lights.size()
