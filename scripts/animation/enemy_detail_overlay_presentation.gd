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
    if actor == null or actor.enemy_id.is_empty():
        return
    _source_path = _resolve_asset(actor.enemy_id)
    if _source_path.is_empty():
        push_error("EnemyDetailOverlayPresentation missing identity mapping: " + actor.enemy_id)
        return
    var resource_path := _source_path if _source_path.begins_with("res://") else "res://" + _source_path
    if not ResourceLoader.exists(resource_path):
        push_error("EnemyDetailOverlayPresentation missing asset: " + _source_path)
        return
    _detail_texture = load(resource_path) as Texture2D
    if _detail_texture == null:
        push_error("EnemyDetailOverlayPresentation failed to import: " + _source_path)
        return

    var root := actor.get("_visual_root") as Node2D
    if root == null:
        call_deferred("_bind")
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

func _resolve_asset(identity: String) -> String:
    if not FileAccess.file_exists(MANIFEST_PATH):
        return ""
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH))
    if not (parsed is Dictionary):
        return ""
    for row_variant in parsed.get("overlays", []):
        if row_variant is Dictionary:
            var row: Dictionary = row_variant
            if str(row.get("enemy_id", "")) == identity:
                return str(row.get("asset", ""))
    return ""

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
