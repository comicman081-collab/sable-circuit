extends Node2D
class_name EnemyDeathSequence

const TILE := 512.0

var enemy_id := ""
var profile: Dictionary = {}
var _rig_texture: Texture2D
var _pieces: Array[Sprite2D] = []
var _velocities: Array[Vector2] = []
var _angular: Array[float] = []
var _age := 0.0
var _duration := 0.9
var _gravity := 280.0
var _mode := "metal"

func setup(origin: Vector2, id_value: String, profile_value: Dictionary) -> void:
    global_position = origin
    enemy_id = id_value
    profile = profile_value.duplicate(true)
    add_to_group("enemy_death_sequences")
    var rig_path := str(profile.get("rig_sheet", ""))
    if not rig_path.is_empty() and ResourceLoader.exists("res://" + rig_path):
        _rig_texture = load("res://" + rig_path) as Texture2D
    _configure_identity()
    _build_fragments()
    queue_redraw()

func _configure_identity() -> void:
    if "SHIELD" in enemy_id:
        _duration = 1.15; _gravity = 430.0; _mode = "shield"
    elif "DRONE" in enemy_id:
        _duration = 1.0; _gravity = 45.0; _mode = "drone"
    elif "ABERRANT" in enemy_id:
        _duration = 1.05; _gravity = 120.0; _mode = "bio"
    elif "BOSS" in enemy_id or "ANCHOR" in enemy_id:
        _duration = 1.55; _gravity = 35.0; _mode = "boss"
    else:
        _duration = 0.9; _gravity = 300.0; _mode = "metal"

func _cells() -> Array[Vector2i]:
    if _mode == "shield":
        return [Vector2i(3,0),Vector2i(1,0),Vector2i(0,1),Vector2i(2,2),Vector2i(0,3)]
    if _mode == "drone":
        return [Vector2i(0,0),Vector2i(1,0),Vector2i(2,0),Vector2i(0,1),Vector2i(1,1),Vector2i(0,2)]
    if _mode == "bio":
        return [Vector2i(0,0),Vector2i(1,0),Vector2i(3,0),Vector2i(0,1),Vector2i(1,2),Vector2i(3,1)]
    if _mode == "boss":
        return [Vector2i(0,0),Vector2i(1,0),Vector2i(2,0),Vector2i(3,0),Vector2i(0,1),Vector2i(1,1),Vector2i(2,1),Vector2i(3,1),Vector2i(0,2),Vector2i(1,2),Vector2i(0,3)]
    return [Vector2i(0,0),Vector2i(2,0),Vector2i(2,3),Vector2i(0,2),Vector2i(1,2)]

func _build_fragments() -> void:
    if _rig_texture == null:
        return
    var cells := _cells()
    var scale_value := 0.105
    if _mode == "shield": scale_value = 0.115
    elif _mode == "drone": scale_value = 0.125
    elif _mode == "bio": scale_value = 0.11
    elif _mode == "boss": scale_value = 0.18
    for i in range(cells.size()):
        var cell := cells[i]
        var sprite := Sprite2D.new()
        sprite.texture = _rig_texture
        sprite.region_enabled = true
        sprite.region_rect = Rect2(cell.x * TILE, cell.y * TILE, TILE, TILE)
        sprite.scale = Vector2.ONE * scale_value
        sprite.z_index = 20 + i
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
        add_child(sprite)
        _pieces.append(sprite)
        var angle := TAU * float(i) / maxf(1.0, float(cells.size())) + 0.31
        var speed := 75.0 + float((i * 37) % 90)
        if _mode == "drone": speed += 55.0
        if _mode == "boss": speed = 45.0 + float((i * 19) % 60)
        if _mode == "bio": angle += sin(float(i) * 1.7) * 0.55
        _velocities.append(Vector2.RIGHT.rotated(angle) * speed + Vector2(0, -55.0))
        _angular.append((-1.0 if i % 2 == 0 else 1.0) * (1.6 + float(i % 4) * 0.55))

func _process(delta: float) -> void:
    _age += delta
    var t := clampf(_age / _duration, 0.0, 1.0)
    for i in range(_pieces.size()):
        var piece := _pieces[i]
        if not is_instance_valid(piece):
            continue
        var v := _velocities[i]
        if _mode == "drone":
            v = v.rotated(delta * (1.4 if i % 2 == 0 else -1.1))
        elif _mode == "boss" and t < 0.28:
            v = -piece.position.normalized() * 85.0 if piece.position.length() > 2.0 else v * 0.3
        elif _mode == "bio":
            v += Vector2(sin(_age * 12.0 + i) * 20.0, 0)
        v.y += _gravity * delta
        _velocities[i] = v
        piece.position += v * delta
        piece.rotation += _angular[i] * delta
        var fade := pow(maxf(0.0, 1.0 - t), 0.72)
        if _mode == "bio":
            piece.scale *= Vector2(1.0 - delta * 0.12, 1.0 + delta * 0.08)
            piece.modulate = Color(0.9, 0.55, 0.82, fade)
        elif _mode == "drone":
            piece.modulate = Color(0.75, 0.92, 1.0, fade)
        elif _mode == "boss":
            piece.modulate = Color(0.84, 0.72, 1.0, fade)
        else:
            piece.modulate.a = fade
    queue_redraw()
    if _age >= _duration:
        queue_free()

func _draw() -> void:
    var t := clampf(_age / _duration, 0.0, 1.0)
    if _mode == "shield":
        draw_arc(Vector2.ZERO, 22.0 + t * 34.0, -2.7, -0.35, 24, Color(1.0,0.62,0.28,1.0-t), 5.0)
    elif _mode == "drone":
        for i in range(3):
            draw_arc(Vector2.ZERO, 18.0 + i * 9.0 + t * 24.0, t * 4.0 + i, t * 4.0 + i + 1.4, 18, Color(0.35,0.93,1.0,(1.0-t)*0.8), 2.0)
    elif _mode == "bio":
        draw_circle(Vector2.ZERO, 18.0 + t * 28.0, Color(0.62,0.16,0.48,(1.0-t)*0.22))
        for i in range(6):
            var a := float(i) * TAU / 6.0 + sin(_age * 3.0) * 0.2
            draw_line(Vector2.RIGHT.rotated(a) * 8.0, Vector2.RIGHT.rotated(a) * (34.0 + t * 25.0), Color(0.86,0.36,0.62,1.0-t), 2.0)
    elif _mode == "boss":
        draw_arc(Vector2.ZERO, 48.0 + t * 145.0, 0.0, TAU, 64, Color(0.58,0.40,1.0,1.0-t), 7.0)
        draw_arc(Vector2.ZERO, 86.0 - t * 38.0, -_age * 2.2, TAU - _age * 2.2, 64, Color(0.96,0.30,0.67,(1.0-t)*0.75), 3.0)
    else:
        for i in range(7):
            var a := float(i) * TAU / 7.0
            draw_line(Vector2.RIGHT.rotated(a) * 6.0, Vector2.RIGHT.rotated(a) * (22.0 + t * 28.0), Color(0.95,0.82,0.60,1.0-t), 2.0)

func debug_mode() -> String:
    return _mode

func debug_piece_count() -> int:
    var visible_count := 0
    for piece in _pieces:
        if is_instance_valid(piece) and piece.visible and piece.modulate.a > 0.02:
            visible_count += 1
    return visible_count

func debug_progress() -> float:
    return clampf(_age / maxf(_duration, 0.001), 0.0, 1.0)

func debug_duration() -> float:
    return _duration
