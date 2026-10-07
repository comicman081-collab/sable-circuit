extends RefCounted
class_name BattleTextureLibrary

## Runtime plates/portraits are source PNGs, not stale editor import caches.
## Reading from bytes also works for the project's raw-file export route.
static func has_texture(path: String) -> bool:
    return FileAccess.file_exists(path) or (OS.has_feature("web") and path.begins_with("res://assets/environments/") and FileAccess.file_exists(path.get_basename() + ".webp"))

static func texture(path: String) -> Texture2D:
    if _prepared.has(path):
        var ready: Texture2D = _prepared[path]
        _prepared.erase(path)
        return ready
    var image := decode_image(path)
    return ImageTexture.create_from_image(image) if image != null else null

## The mipmapped pixels texture() uploads. Touches no shared state, so DeployWarmer runs
## it on a worker thread.
static func decode_image(path: String) -> Image:
    # Web exports may provide an explicitly generated same-resolution plate.
    # Native PNG masters, actor sprites and hash-bound cover masks stay intact.
    var web_path := path.get_basename() + ".webp"
    if OS.has_feature("web") and path.begins_with("res://assets/environments/") and FileAccess.file_exists(web_path):
        var web_image := Image.new()
        if web_image.load_webp_from_buffer(FileAccess.get_file_as_bytes(web_path)) == OK:
            web_image.generate_mipmaps()
            return web_image
    if not FileAccess.file_exists(path):
        return null
    var image := Image.new()
    var bytes := FileAccess.get_file_as_bytes(path)
    var error := image.load_png_from_buffer(bytes)
    if error != OK:
        push_error("Battle texture could not decode: " + path)
        return null
    image.generate_mipmaps()
    return image

## Plates DeployWarmer decoded on the briefing screen, each handed to the next texture()
## call for its path and then forgotten, so a stage's plates do not stay in memory.
static var _prepared: Dictionary = {}

static func keep_prepared(path: String, image: Image) -> void:
    if image != null: _prepared[path] = ImageTexture.create_from_image(image)

static func has_prepared(path: String) -> bool:
    return _prepared.has(path)

static func drop_prepared() -> void:
    _prepared.clear()

static func portrait(profile: Dictionary) -> Texture2D:
    var path := str(profile.get("portrait_asset", ""))
    var region: Array = profile.get("portrait_region", [])
    if path.is_empty() or region.size() != 4:
        return null
    var source := texture("res://" + path.trim_prefix("res://"))
    if source == null:
        return null
    var crop := Rect2(float(region[0]), float(region[1]), float(region[2]), float(region[3]))
    if not Rect2(Vector2.ZERO, source.get_size()).encloses(crop) or not crop.has_area():
        push_error("Portrait region outside source: " + path)
        return null
    var atlas := AtlasTexture.new()
    atlas.atlas = source
    atlas.region = crop
    atlas.filter_clip = true
    return atlas
