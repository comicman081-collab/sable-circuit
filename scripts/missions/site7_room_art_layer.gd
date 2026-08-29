extends Node2D
class_name Site7RoomArtLayer

const MANIFEST_PATH := "res://data/visual/site7_room_art.json"

var _asset_paths: Array[String] = []
var _sprites: Array[Sprite2D] = []
var _load_failures := 0

func _ready() -> void:
    # M7 room art is authored structure laid into the connected facility deck.
    # It remains behind gameplay actors and dynamic telegraphs.
    z_index = -3
    add_to_group("m6_room_art")
    _load_manifest()

func _load_manifest() -> void:
    if not FileAccess.file_exists(MANIFEST_PATH):
        push_error("Site7RoomArtLayer missing manifest")
        _load_failures += 1
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH))
    if not (parsed is Dictionary):
        push_error("Site7RoomArtLayer manifest parse failed")
        _load_failures += 1
        return
    for row_variant in parsed.get("rooms", []):
        if not (row_variant is Dictionary):
            continue
        var row: Dictionary = row_variant
        var rel_path := str(row.get("asset", ""))
        var resource_path := "res://" + rel_path
        if rel_path.is_empty() or not ResourceLoader.exists(resource_path):
            push_error("Site7RoomArtLayer missing asset: " + rel_path)
            _load_failures += 1
            continue
        var texture := load(resource_path) as Texture2D
        if texture == null:
            push_error("Site7RoomArtLayer asset failed to import: " + rel_path)
            _load_failures += 1
            continue
        var sprite := Sprite2D.new()
        sprite.name = str(row.get("asset_id", "RoomArt"))
        sprite.texture = texture
        sprite.centered = true
        var pos_value: Variant = row.get("position", [0, 0])
        if pos_value is Array and pos_value.size() >= 2:
            sprite.position = Vector2(float(pos_value[0]), float(pos_value[1]))
        var scale_value := float(row.get("scale", 0.30))
        sprite.scale = Vector2.ONE * scale_value
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
        # Let the connected procedural deck provide continuous floor geometry;
        # authored plates contribute walls, rails, pipes and room identity.
        sprite.modulate = Color(0.78, 0.84, 0.88, 0.70)
        add_child(sprite)
        _sprites.append(sprite)
        _asset_paths.append(rel_path)

func debug_asset_count() -> int:
    return _sprites.size()

func debug_unique_asset_count() -> int:
    var unique: Dictionary = {}
    for path in _asset_paths:
        unique[path] = true
    return unique.size()

func debug_all_assets_loaded() -> bool:
    return _load_failures == 0 and _sprites.size() == 8 and debug_unique_asset_count() == 8

func debug_primary_art_layer() -> bool:
    return z_index == -3

func debug_m7_blended_deck() -> bool:
    return z_index < 0
