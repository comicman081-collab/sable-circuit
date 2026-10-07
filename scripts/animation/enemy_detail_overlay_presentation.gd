extends Node
class_name EnemyDetailOverlayPresentation

const MANIFEST_PATH := "res://data/visual/enemy_detail_overlays.json"

var actor: EnemyActor
var _detail_texture: Texture2D
var _overlay_count := 0
var _source_path := ""

func _ready() -> void:
    actor = get_parent() as EnemyActor
    call_deferred("_bind")

func _bind() -> void:
    if not is_instance_valid(actor) or actor.is_queued_for_deletion() or actor.art_profile.is_empty():
        return
    if actor.enemy_id in ["ENM_SITE7_BULWARK_01","ENM_SITE7_RAM_01","ENM_SITE7_MORTAR_01",
        "ENM_SITE7_PRISM_01","ENM_SITE7_NULL_PYLON_01","BOSS_SITE7_FORGE_01","BOSS_SITE7_CARRIER_01",
        "BOSS_SITE7_RELAY_01","BOSS_SITE7_REMNANT_01","BOSS_SITE7_AERATOR_01","BOSS_SITE7_CRYO_01",
        "BOSS_SITE7_GANTRY_01","BOSS_SITE7_ARCHIVE_01","BOSS_SITE7_ORIGIN_01"]:
        # Native PBR robot artwork already contains its material detail.
        # No legacy cut-up overlay, especially not a retired humanoid sheet.
        return
    _source_path = detail_asset(actor.enemy_id)
    if _source_path.is_empty():
        push_error("EnemyDetailOverlayPresentation missing identity mapping: " + actor.enemy_id)
        return
    var resource_path := _source_path if _source_path.begins_with("res://") else "res://" + _source_path
    if not ResourceLoader.exists(resource_path):
        push_error("EnemyDetailOverlayPresentation missing asset: " + _source_path)
        return
    _detail_texture = EnemyActor.cached_texture(resource_path)
    if _detail_texture == null:
        push_error("EnemyDetailOverlayPresentation failed to import: " + _source_path)
        return

    var root := actor.get("_visual_root") as Node2D
    if root == null:
        return
    var bases: Array[Sprite2D] = []
    _collect_articulated_sprites(root, bases)
    for base in bases:
        var overlay := Sprite2D.new()
        overlay.name = base.name + "Detail"
        overlay.texture = _detail_texture
        overlay.region_enabled = true
        overlay.region_rect = base.region_rect
        overlay.centered = base.centered
        overlay.position = Vector2.ZERO
        overlay.offset = base.offset
        overlay.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
        overlay.z_index = 1
        overlay.material = base.material
        base.add_child(overlay)
        _overlay_count += 1

## The manifest's overlay asset for a robot, or "" (read once per run).
static var _assets: Dictionary = {}
static var _manifest_read := false
static func detail_asset(identity: String) -> String:
    if not _manifest_read:
        _manifest_read = true
        var parsed = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH)) if FileAccess.file_exists(MANIFEST_PATH) else null
        if parsed is Dictionary:
            for row_variant in parsed.get("overlays", []):
                if row_variant is Dictionary:
                    var row: Dictionary = row_variant
                    var id := str(row.get("enemy_id", ""))
                    if not _assets.has(id): _assets[id] = str(row.get("asset", ""))
    return str(_assets.get(identity, ""))

func _collect_articulated_sprites(node: Node, out: Array[Sprite2D]) -> void:
    for child in node.get_children():
        if child is Sprite2D:
            var sprite := child as Sprite2D
            if sprite.region_enabled and sprite.name != "UniqueMasterSprite" and not sprite.name.ends_with("Detail"):
                out.append(sprite)
        _collect_articulated_sprites(child, out)

func debug_overlay_count() -> int:
    return _overlay_count

func debug_source_path() -> String:
    return _source_path

func debug_loaded() -> bool:
    return _detail_texture != null and _overlay_count >= 6
