extends Node2D
class_name OperatorAuthoredRasterPresentation

const ATLAS_CELLS_X := 4
const ATLAS_CELLS_Y := 2
const ENGINE_TO_ATLAS: Array[int] = [2,1,0,7,6,5,4,3]
const BASE_SCALE := 0.46

var actor: OperatorActor
var visual: OperatorVisual
var sprite: Sprite2D
var _loaded := false
var _source_id := ""
var _last_sector := -1
var _recoil_visual := 0.0
var _phase := 0.0
var _status := "not_attempted"
var _chunk_count := 0
var _encoded_chars := 0
var _decoded_bytes := 0
var _declared_bytes := 0

func _ready() -> void:
    process_priority = 132
    actor = get_parent() as OperatorActor
    if actor:
        visual = actor.get_node_or_null("VisualRoot") as OperatorVisual
    sprite = Sprite2D.new()
    sprite.name = "AuthoredRasterSprite"
    sprite.centered = true
    sprite.z_index = 12
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
    add_child(sprite)
    call_deferred("_load_for_actor")

func _load_for_actor() -> void:
    if actor == null:
        _status = "no_actor"
        return
    var identity := _identity_key()
    if identity.is_empty():
        _status = "unknown_identity"
        return
    _source_id = identity
    var prefix := "res://assets/generated/raster/%s/%s_direction_atlas.webp.b64." % [identity, identity]
    var dir_path := prefix.get_base_dir()
    var base_name := prefix.get_file()
    if not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(dir_path)):
        _status = "missing"
        return
    var files: Array[String] = []
    var dir := DirAccess.open(dir_path)
    if dir == null:
        _status = "missing"
        return
    dir.list_dir_begin()
    var name := dir.get_next()
    while not name.is_empty():
        if not dir.current_is_dir() and name.begins_with(base_name):
            files.append(name)
        name = dir.get_next()
    dir.list_dir_end()
    files.sort()
    _chunk_count = files.size()
    if files.is_empty():
        _status = "missing"
        return

    var encoded := ""
    for filename in files:
        encoded += FileAccess.get_file_as_string(dir_path.path_join(filename)).strip_edges()
    _encoded_chars = encoded.length()
    var bytes := Marshalls.base64_to_raw(encoded)
    _decoded_bytes = bytes.size()
    if bytes.size() < 12:
        _status = "invalid_header"
        print("M7_RASTER_QUARANTINED identity=%s status=%s chunks=%d bytes=%d" % [identity, _status, _chunk_count, _decoded_bytes])
        return

    if not _has_webp_riff_header(bytes):
        _status = "invalid_header"
        print("M7_RASTER_QUARANTINED identity=%s status=%s chunks=%d bytes=%d" % [identity, _status, _chunk_count, _decoded_bytes])
        return

    _declared_bytes = _riff_declared_total_bytes(bytes)
    # A truncated RIFF/WebP can still have a valid header and base64-decode cleanly.
    # Calling Image.load_webp_from_buffer on such a payload produces a noisy engine
    # decode error. Treat the RIFF length as the authority and quarantine partial
    # uploads before the image decoder is ever invoked.
    if _declared_bytes <= 12 or _decoded_bytes != _declared_bytes:
        _status = "partial" if _decoded_bytes < _declared_bytes else "length_mismatch"
        print("M7_RASTER_QUARANTINED identity=%s status=%s chunks=%d encoded=%d present=%d declared=%d" % [
            identity, _status, _chunk_count, _encoded_chars, _decoded_bytes, _declared_bytes
        ])
        return

    var image := Image.new()
    var err := image.load_webp_from_buffer(bytes)
    if err != OK:
        _status = "decode_error"
        push_error("M7 raster WebP decode failed for %s err=%d" % [identity, err])
        return
    if image.get_width() % ATLAS_CELLS_X != 0 or image.get_height() % ATLAS_CELLS_Y != 0:
        _status = "invalid_dimensions"
        push_error("M7 raster atlas dimensions invalid: %s" % identity)
        return

    sprite.texture = ImageTexture.create_from_image(image)
    sprite.region_enabled = true
    sprite.scale = Vector2.ONE * BASE_SCALE
    _loaded = true
    _status = "loaded"
    if visual:
        # Keep the articulated visual processing for muzzle/socket/IK authority,
        # but stop drawing the old SVG/directional body only after the raster payload
        # has passed RIFF completeness, WebP decode and atlas dimension validation.
        visual.modulate.a = 0.0
    _sync_sector(true)

func _has_webp_riff_header(bytes: PackedByteArray) -> bool:
    return (
        bytes[0] == 82 and bytes[1] == 73 and bytes[2] == 70 and bytes[3] == 70
        and bytes[8] == 87 and bytes[9] == 69 and bytes[10] == 66 and bytes[11] == 80
    )

func _riff_declared_total_bytes(bytes: PackedByteArray) -> int:
    # RIFF byte 4..7 stores little-endian file size minus the 8-byte RIFF prefix.
    return (
        int(bytes[4])
        | (int(bytes[5]) << 8)
        | (int(bytes[6]) << 16)
        | (int(bytes[7]) << 24)
    ) + 8

func _identity_key() -> String:
    match actor.operator_id:
        "CHR_PROTO_01": return "aster"
        "CHR_PROTO_02": return "rook"
        "CHR_PROTO_03": return "mica"
    return ""

func _process(delta: float) -> void:
    if not _loaded or actor == null:
        return
    _phase += delta * (7.5 if actor.velocity.length() > 12.0 else 2.2)
    _sync_sector(false)
    var moving := clampf(actor.velocity.length() / maxf(1.0, actor.run_speed), 0.0, 1.0)
    var bob := sin(_phase) * lerpf(0.45, 2.2, moving)
    var lateral := 0.0
    if actor.velocity.length_squared() > 1.0:
        var side := Vector2(-actor.aim_world.y, actor.aim_world.x)
        lateral = actor.velocity.normalized().dot(side)
    var recoil_target := 0.0
    if visual != null:
        recoil_target = float(visual.get("_recoil"))
    _recoil_visual = lerpf(_recoil_visual, recoil_target, clampf(delta * 18.0, 0.0, 1.0))
    sprite.position = Vector2(-actor.aim_world.x * _recoil_visual * 4.0, -50.0 + bob)
    sprite.rotation = lateral * 0.025
    sprite.modulate = Color.WHITE
    if actor.is_downed():
        sprite.modulate = Color(0.48,0.50,0.54,0.72)
        sprite.rotation = 0.16

func _sync_sector(force: bool) -> void:
    if not _loaded or sprite.texture == null:
        return
    var sector := posmod(actor.facing_sector, 8)
    if not force and sector == _last_sector:
        return
    var atlas_index := ENGINE_TO_ATLAS[sector]
    var texture_size := sprite.texture.get_size()
    var cell_w := texture_size.x / float(ATLAS_CELLS_X)
    var cell_h := texture_size.y / float(ATLAS_CELLS_Y)
    sprite.region_rect = Rect2(
        float(atlas_index % ATLAS_CELLS_X) * cell_w,
        float(atlas_index / ATLAS_CELLS_X) * cell_h,
        cell_w,
        cell_h
    )
    _last_sector = sector

func debug_loaded() -> bool:
    return _loaded

func debug_source_id() -> String:
    return _source_id

func debug_sector() -> int:
    return _last_sector

func debug_status() -> String:
    return _status

func debug_svg_hidden() -> bool:
    return visual != null and visual.modulate.a <= 0.01

func debug_contract() -> Dictionary:
    return {
        "authored_raster": _loaded,
        "source": _source_id,
        "status": _status,
        "sector": _last_sector,
        "chunk_count": _chunk_count,
        "encoded_chars": _encoded_chars,
        "decoded_bytes": _decoded_bytes,
        "declared_bytes": _declared_bytes,
        "payload_complete": _declared_bytes > 0 and _decoded_bytes == _declared_bytes,
        "partial_payload_quarantined": _status in ["partial", "length_mismatch", "invalid_header"],
        "svg_socket_authority_retained": visual != null,
        "svg_render_hidden": debug_svg_hidden(),
        "atlas_direction_count": 8,
        "m7_raster": true
    }
