extends Node
class_name OperatorDetailOverlayPresentation

var actor: OperatorActor
var visual: OperatorVisual
var _detail_texture: Texture2D
var _overlay_count := 0
var _source_path := ""

func _ready() -> void:
    actor = get_parent() as OperatorActor
    if actor:
        visual = actor.get_node_or_null("VisualRoot") as OperatorVisual
    call_deferred("_bind")

func _bind() -> void:
    if actor == null or visual == null:
        return
    var raster := actor.get_node_or_null("MotionLabCharacterRuntime")
    if raster != null and raster.has_method("is_runtime_active") and bool(raster.call("is_runtime_active")):
        return
    var profile := actor.art_profile
    if profile.is_empty():
        profile = ArtProfileRegistry.get_profile(actor.operator_id)
    _source_path = str(profile.get("detail_overlay_asset", ""))
    if _source_path.is_empty():
        return
    var resource_path := _source_path if _source_path.begins_with("res://") else "res://" + _source_path
    if not ResourceLoader.exists(resource_path):
        push_error("OperatorDetailOverlayPresentation missing asset: " + _source_path)
        return
    _detail_texture = load(resource_path) as Texture2D
    if _detail_texture == null:
        push_error("OperatorDetailOverlayPresentation failed to import: " + _source_path)
        return

    var bases: Array[Sprite2D] = []
    _collect_base_hr_sprites(visual, bases)
    for base in bases:
        var overlay := Sprite2D.new()
        overlay.name = base.name + "Detail"
        overlay.texture = _detail_texture
        overlay.region_enabled = base.region_enabled
        overlay.region_rect = base.region_rect
        overlay.centered = base.centered
        overlay.position = Vector2.ZERO
        overlay.offset = base.offset
        overlay.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
        overlay.z_index = 1
        overlay.material = base.material
        base.add_child(overlay)
        _overlay_count += 1

func _collect_base_hr_sprites(node: Node, out: Array[Sprite2D]) -> void:
    for child in node.get_children():
        if child is Sprite2D:
            var sprite := child as Sprite2D
            if sprite.name.ends_with("HR") and not sprite.name.ends_with("Detail"):
                out.append(sprite)
        _collect_base_hr_sprites(child, out)

## The overlays sit on the hidden vector rig; OperatorVisual clears their
## sprites, and this drops the last reference to the 2048px sheet.
func release_hidden_art() -> void:
    _detail_texture = null

func debug_overlay_count() -> int:
    return _overlay_count

func debug_source_path() -> String:
    return _source_path

func debug_loaded() -> bool:
    return _detail_texture != null and _overlay_count >= 15
