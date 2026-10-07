extends Control
class_name MenuAtmosphere
## Additive light shafts and drifting dust over a menu backdrop.

var beam_color := Color(0.55, 0.95, 0.92)
var beam_alpha := 0.07
var beams: Array[Vector3] = [Vector3(0.58, 150.0, 0.0), Vector3(0.74, 110.0, 1.9), Vector3(0.9, 190.0, 3.4)]
var mote_count := 72
var mote_color := Color(0.75, 0.97, 1.0)
var _motes: Array[Dictionary] = []
var _time := 0.0
var _rng := RandomNumberGenerator.new()

func _init() -> void:
    name = "MenuAtmosphere"
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    var additive := CanvasItemMaterial.new()
    additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
    material = additive

func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _rng.seed = 7707
    for i in range(mote_count):
        _motes.append(_new_mote(true))

func _new_mote(anywhere: bool) -> Dictionary:
    var area := size if size.x > 0.0 else Vector2(1280, 720)
    return {
        "pos": Vector2(_rng.randf() * area.x, _rng.randf() * area.y if anywhere else area.y + 8.0),
        "vel": Vector2(_rng.randf_range(4.0, 14.0), -_rng.randf_range(5.0, 18.0)),
        "size": _rng.randf_range(0.7, 2.1),
        "phase": _rng.randf() * TAU,
        "alpha": _rng.randf_range(0.18, 0.55),
    }

func _process(delta: float) -> void:
    _time += delta
    for i in range(_motes.size()):
        var mote: Dictionary = _motes[i]
        var pos: Vector2 = mote["pos"] + mote["vel"] * delta
        mote["pos"] = pos
        if pos.y < -10.0 or pos.x > size.x + 10.0:
            var fresh := _new_mote(false)
            fresh["pos"] = Vector2(_rng.randf() * size.x * 0.8, (fresh["pos"] as Vector2).y)
            _motes[i] = fresh
    queue_redraw()

func _draw() -> void:
    for beam in beams:
        var sway := sin(_time * 0.21 + beam.z) * 38.0
        var top_x := size.x * beam.x + sway
        var width := beam.y
        var pulse := 0.75 + 0.25 * sin(_time * 0.37 + beam.z * 1.7)
        var top := Color(beam_color, beam_alpha * pulse)
        var bottom := Color(beam_color, 0.0)
        draw_polygon(
            PackedVector2Array([Vector2(top_x - width * 0.25, -10), Vector2(top_x + width * 0.25, -10),
                Vector2(top_x - 260 + width, size.y * 0.95), Vector2(top_x - 260 - width * 0.6, size.y * 0.95)]),
            PackedColorArray([top, top, bottom, bottom]))
    for mote: Dictionary in _motes:
        var twinkle := 0.55 + 0.45 * sin(_time * 1.6 + float(mote.phase))
        draw_circle(mote.pos, float(mote.size), Color(mote_color, float(mote.alpha) * twinkle))
