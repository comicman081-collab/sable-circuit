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
        return
    var identity := _identity_key()
    if identity.is_empty():
        return
    var prefix := "res://assets/generated/raster/%s/%s_direction_atlas.webp.b64." % [identity, identity]
    var dir_path := prefix.get_base_dir()
    var base_name := prefix.get_file()
    if not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(dir_path)):
        return
    var files: Array[String] = []
    var dir := DirAccess.open(dir_path)
    if dir == null:
        return
    dir.list_dir_begin()
    var name := dir.get_next()
    while not name.is_empty():
        if not dir.current_is_dir() and name.begins_with(base_name):
            files.append(name)
        name = dir.get_next()
    dir.list_dir_end()
    files.sort()
    if files.is_empty():
        return
    var encoded := ""
    for filename in files:
        encoded += FileAccess.get_file_as_string(dir_path.path_join(filename)).strip_edges()
    var bytes := Marshalls.base64_to_raw(encoded)
    if bytes.is_empty():
        push_warning("M7 raster decode empty for " + identity)
        return
    var image := Image.new()
    var err := image.load_webp_from_buffer(bytes)
    if err != OK:
        push_warning("M7 raster WebP incomplete for %s err=%d" % [identity, err])
        return
    if image.get_width() % ATLAS_CELLS_X != 0 or image.get_height() % ATLAS_CELLS_Y != 0:
        push_error("M7 raster atlas dimensions invalid: %s" % identity)
        return
    sprite.texture = ImageTexture.create_from_image(image)
    sprite.region_enabled = true
    sprite.scale = Vector2.ONE * BASE_SCALE
    _source_id = identity
    _loaded = true
    if visual:
        # Keep the articulated visual processing for muzzle/socket/IK authority,
        # but stop drawing the old SVG body once the authored raster is valid.
        visual.modulate.a = 0.0
    _sync_sector(true)

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

func debug_svg_hidden() -> bool:
    return visual != null and visual.modulate.a <= 0.01

func debug_contract() -> Dictionary:
    return {
        "authored_raster": _loaded,
        "source": _source_id,
        "sector": _last_sector,
        "svg_socket_authority_retained": visual != null,
        "svg_render_hidden": debug_svg_hidden(),
        "atlas_direction_count": 8,
        "m7_raster": true
    }
