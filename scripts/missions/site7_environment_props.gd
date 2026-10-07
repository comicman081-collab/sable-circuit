extends Node2D
## Four cached source textures, streamed with the selected existing room plate.
const CONFIG := "res://data/visual/site7_environment_props.json"
const PROP := preload("res://scripts/missions/site7_environment_prop.gd")
## The props are drawn at roughly a fifth of their 1920x1080 renders. The GPU copy keeps
## only the visible box at half size; bullet tests use that box at full source resolution.
const GPU_SCALE := 0.5
const REGION_MARGIN := 2
var entries: Array[Dictionary] = []
var textures: Dictionary = {}
var stage: StoryStage01
var art: Site7RoomArtLayer

func _ready() -> void:
    stage = get_parent() as StoryStage01
    art = stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    process_priority = 170
    call_deferred("_build")

func _build() -> void:
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
    var rooms: Dictionary = config.missions.get(stage.mission_id,{})
    if rooms.is_empty(): return
    var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(config.spec)))
    for room_id: String in rooms:
        var plate := art.get_room_plate(room_id)
        if plate == null: continue
        for row: Dictionary in rooms[room_id]:
            var id := str(row.asset)
            var asset: Dictionary = spec.props[id]
            if not textures.has(id):
                var key := str(asset.texture) + "|" + str(asset.sha256)
                if not _reduced.has(key):
                    var prepared := prepare_prop(str(asset.texture), str(asset.sha256))
                    if prepared.get("error", "") == "changed": push_error("Environment prop changed: " + id)
                    if prepared.has("error"): continue
                    adopt_prop(key, prepared)
                textures[id] = _reduced[key]
            var prop := PROP.new()
            prop.name = "KArchive_" + id + "_" + room_id
            add_child(prop)
            prop.configure(textures[id].texture,textures[id].alpha,asset,float(row.width),textures[id].region,textures[id].source_size)
            var point := Vector2(float(row.point[0]),float(row.point[1]))
            prop.global_position = plate.global_position + (point-Vector2.ONE*0.5)*plate.texture.get_size()*plate.scale
            entries.append({"prop":prop,"plate":plate,"room_id":room_id,"asset":id})
    _process(0)

static func reduced_prop_texture(decoded: Image) -> Dictionary:
    var reduced := _reduced_images(decoded)
    reduced["texture"] = ImageTexture.create_from_image(reduced.art)
    reduced.erase("art")
    return reduced

static func _reduced_images(decoded: Image) -> Dictionary:
    var full := Rect2i(Vector2i.ZERO, decoded.get_size())
    var region := decoded.get_used_rect().grow(REGION_MARGIN).intersection(full)
    if not region.has_area(): region = full
    var alpha := decoded.get_region(region)
    alpha.convert(Image.FORMAT_LA8)
    var art := decoded.get_region(region)
    art.resize(maxi(1, ceili(region.size.x * GPU_SCALE)), maxi(1, ceili(region.size.y * GPU_SCALE)), Image.INTERPOLATE_LANCZOS)
    art.generate_mipmaps()
    return {"art":art, "alpha":alpha, "region":region, "source_size":decoded.get_size()}

## Reduced prop art for the run, keyed by path|sha256. Every operation uses the same few
## licensed renders; hashing, decoding and shrinking them cost ~280 ms per deploy.
static var _reduced: Dictionary = {}

## Hash check, decode and reduction without shared state (DeployWarmer runs it on a worker
## thread). {"error": "changed"|"decode"} when the source is unusable.
static func prepare_prop(path: String, sha256: String) -> Dictionary:
    if FileAccess.get_sha256(path) != sha256: return {"error":"changed"}
    var decoded := Image.new()
    if decoded.load_png_from_buffer(FileAccess.get_file_as_bytes(path)) != OK: return {"error":"decode"}
    return _reduced_images(decoded)

static func adopt_prop(key: String, prepared: Dictionary) -> void:
    if prepared.has("error") or _reduced.has(key): return
    _reduced[key] = {"texture":ImageTexture.create_from_image(prepared.art), "alpha":prepared.alpha,
        "region":prepared.region, "source_size":prepared.source_size}

static func prop_cached(key: String) -> bool:
    return _reduced.has(key)

func _process(_delta: float) -> void:
    for entry in entries:
        entry.prop.set_active(entry.plate.is_visible_in_tree())

func debug_contract() -> Dictionary:
    var active_assets: Array[String] = []
    for entry in entries:
        if entry.prop.active: active_assets.append(entry.asset)
    return {"count":entries.size(),"unique_textures":textures.size(),"active_assets":active_assets,
        "ground_collision":true,"alpha_projectile_cover":true,"source":"kArchive / dogfooter"}
