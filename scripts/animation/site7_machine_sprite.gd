extends Node2D
## Source-preserving preview/runtime for non-walking machines only.
## A drone banks as one rigid object; an anchor stays anchored. Neither is a
## humanoid gait and neither may use a six-frame foot-cycle approval as proof.

var actor: EnemyActor
var sprite: Sprite2D
var kind := ""
var emitter_px := Vector2.ZERO
var image_size := Vector2.ZERO
## The machine's own mass inside the picture, in texture pixels. A spec without
## `visible_rect_px` claims the whole image (the shipped bosses fill theirs); a machine drawn
## small in a large transparent canvas names its bounds so the damage box and the health bar
## follow the art and not the empty margin.
var visible_rect := Rect2()
var age := 0.0
var flash := 0.0
var render_scale := 1.0
var body_origin := Vector2.ZERO
var configured := false
var weathering: ShaderMaterial
var bank := 0.0
var suspension := 0.0
var motion_speed := 0.0
var travel := 0.0
var last_root := Vector2.ZERO
var recoil := Vector2.ZERO
var pending_recoil := Vector2.ZERO
const DIRECTIONS := ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
var views: Dictionary = {}
var facing := ""
var emitter_visible := true
const MAX_TARGET_ERROR := PI / 8.0 + 0.02
static var _pixel_hash_cache: Dictionary = {}
static var _texture_cache: Dictionary = {}
static var _verified_sources: Dictionary = {}

static func _visible_pixel_hash(image: Image, file_hash: String) -> String:
    if _pixel_hash_cache.has(file_hash): return _pixel_hash_cache[file_hash]
    var result := _pixel_hash_of(image)
    _pixel_hash_cache[file_hash]=result
    return result

static func _pixel_hash_of(image: Image) -> String:
    var canonical := image.duplicate() as Image
    canonical.convert(Image.FORMAT_RGBA8)
    # Invisible RGB is not another direction. Do not change the source or the
    # displayed texture; canonicalize only the comparison buffer: a masked blit
    # onto zeroed pixels keeps every pixel whose alpha is not 0 and clears the rest
    # (the same bytes as the old per-byte loop, 3x faster; qa/spawn_hitch_20260925).
    var visible := Image.create_empty(canonical.get_width(), canonical.get_height(), false, Image.FORMAT_RGBA8)
    visible.blit_rect_mask(canonical, canonical, Rect2i(Vector2i.ZERO, canonical.get_size()), Vector2i.ZERO)
    var hash := HashingContext.new()
    hash.start(HashingContext.HASH_SHA256)
    hash.update((str(image.get_width())+"x"+str(image.get_height())+":RGBA8:").to_utf8_buffer())
    hash.update(visible.get_data())
    return hash.finish().hex_encode()

## Checks a view's source bytes against the reviewed hash once per run. Hashing up to
## 18 MB of source PNG on every spawn stalled combat 50-100 ms per robot.
static func _verified_size(path: String, source_hash: String) -> Vector2i:
    var key := path + "|" + source_hash
    if not _verified_sources.has(key):
        if FileAccess.get_sha256(path) != source_hash: return Vector2i.ZERO
        _verified_sources[key] = _png_dimensions(path)
    return _verified_sources[key]

## Verifies and decodes every view of a reviewed machine before combat, so the first
## spawn of a robot type does not decode and hash its sources mid-fight.
static func warm(spec: Dictionary) -> void:
    for view in view_specs(spec): _read_view(view)

## The per-view specs of a reviewed machine: its eight authored views, or the one view of an
## anchored machine.
static func view_specs(spec: Dictionary) -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    var authored: Dictionary = spec.get("views", {})
    if authored.is_empty():
        result.append(spec)
        return result
    for direction in authored:
        if authored[direction] is Dictionary: result.append(authored[direction])
    return result

static func _cache_key(source_hash: String) -> String:
    return source_hash + (":web" if OS.has_feature("web") else ":native")

## True once a view's source is verified and its texture is in the run cache.
static func view_cached(spec: Dictionary) -> bool:
    var source_hash := str(spec.get("texture_sha256", ""))
    return _verified_sources.has(str(spec.get("texture", "")) + "|" + source_hash) and _texture_cache.has(_cache_key(source_hash))

## The slow part of _read_view — reviewed-hash check, decode, visible-pixel hash — without
## touching the shared caches, so DeployWarmer can run it on a worker thread. {} when the
## source fails its hash or decode; adopt_view then stores nothing and _read_view rejects it
## as before.
static func prepare_view(spec: Dictionary) -> Dictionary:
    var path := str(spec.get("texture", ""))
    var source_hash := str(spec.get("texture_sha256", ""))
    if FileAccess.get_sha256(path) != source_hash: return {}
    var original_size := _png_dimensions(path)
    if original_size.x <= 0 or original_size.y <= 0: return {}
    var image := _decode_view(path, Vector2(original_size))
    if image == null: return {}
    return {"source_key":path + "|" + source_hash, "original_size":original_size,
        "cache_key":_cache_key(source_hash), "image":image, "pixel_sha256":_pixel_hash_of(image)}

## Main thread: stores a prepare_view result in the caches _read_view reads.
static func adopt_view(prepared: Dictionary) -> void:
    if prepared.is_empty(): return
    _verified_sources[prepared.source_key] = prepared.original_size
    if _texture_cache.has(prepared.cache_key): return
    var image: Image = prepared.image
    _pixel_hash_cache[prepared.cache_key] = prepared.pixel_sha256
    _texture_cache[prepared.cache_key] = {"texture":ImageTexture.create_from_image(image),
        "size":Vector2(image.get_size()),"pixel_sha256":prepared.pixel_sha256}

static func _decode_view(path: String, size: Vector2) -> Image:
    var image: Image
    if OS.has_feature("web"):
        var derivative_path := path.get_basename() + ".web.webp"
        if not FileAccess.file_exists(derivative_path): return null
        image = Image.new()
        if image.load_webp_from_buffer(FileAccess.get_file_as_bytes(derivative_path)) != OK: return null
        if image.get_size() != Vector2i(int(size.x) / 2, int(size.y) / 2): return null
    else:
        image = Image.load_from_file(path)
    if image == null or image.is_empty(): return null
    return image

static func _read_view(spec: Dictionary) -> Dictionary:
    var path := str(spec.get("texture", ""))
    var source_hash := str(spec.get("texture_sha256", ""))
    var original_size := _verified_size(path, source_hash)
    if original_size.x <= 0 or original_size.y <= 0: return {}
    var root_xy: Array = spec.get("root_px", [])
    var emitter_xy: Array = spec.get("emitter_px", [])
    if root_xy.size() != 2 or emitter_xy.size() != 2: return {}
    var size := Vector2(original_size)
    var origin := Vector2(float(root_xy[0]),float(root_xy[1]))
    var emitter := Vector2(float(emitter_xy[0]),float(emitter_xy[1]))
    var ratio := float(spec.get("display_height",110.0)) / size.y
    if not origin.is_finite() or not emitter.is_finite() or not is_finite(ratio): return {}
    if ratio <= 0.0 or ratio > 1.0 or not Rect2(Vector2.ZERO,size).has_point(emitter): return {}
    var visible := Rect2(Vector2.ZERO,size)
    var visible_xy: Array = spec.get("visible_rect_px", [])
    if not visible_xy.is_empty():
        if visible_xy.size() != 4: return {}
        var corner := Vector2(float(visible_xy[0]),float(visible_xy[1]))
        visible = Rect2(corner,Vector2(float(visible_xy[2]),float(visible_xy[3]))-corner)
        if visible.size.x <= 0.0 or visible.size.y <= 0.0 or not Rect2(Vector2.ZERO,size).encloses(visible): return {}
        if not visible.has_point(emitter) or not visible.grow(12.0).has_point(origin): return {}
    var cache_key := _cache_key(source_hash)
    if not _texture_cache.has(cache_key):
        var image := _decode_view(path, size)
        if image == null: return {}
        _texture_cache[cache_key] = {"texture":ImageTexture.create_from_image(image),
            "size":Vector2(image.get_size()),"pixel_sha256":_visible_pixel_hash(image,cache_key)}
    var cached: Dictionary = _texture_cache[cache_key]
    var pixel_scale: Vector2 = (cached["size"] as Vector2) / size
    return {"texture":cached["texture"],"size":cached["size"],"root":origin,"visible":visible,
        "emitter":emitter,"scale":ratio,"emitter_visible":bool(spec.get("emitter_visible",true)),
        "texture_sha256":source_hash,"pixel_sha256":cached.pixel_sha256,"pixel_scale":pixel_scale}

static func _png_dimensions(path: String) -> Vector2i:
    var file := FileAccess.open(path,FileAccess.READ)
    if file == null: return Vector2i.ZERO
    var header := file.get_buffer(24)
    if header.size() != 24 or header[0] != 137 or header[1] != 80 or header[2] != 78 or header[3] != 71 or header[12] != 73 or header[13] != 72 or header[14] != 68 or header[15] != 82:
        return Vector2i.ZERO
    var width := (int(header[16]) << 24) | (int(header[17]) << 16) | (int(header[18]) << 8) | int(header[19])
    var height := (int(header[20]) << 24) | (int(header[21]) << 16) | (int(header[22]) << 8) | int(header[23])
    return Vector2i(width,height)

func configure(owner_actor: EnemyActor, spec: Dictionary) -> bool:
    if configured or not is_instance_valid(owner_actor): return false
    var staged_kind := str(spec.get("kind", ""))
    var expected_kind := {"ENM_SITE7_DRONE_01":"hover_machine", "BOSS_SITE7_ANCHOR_01":"anchored_machine",
        "ENM_SITE7_BULWARK_01":"tracked_machine", "ENM_SITE7_RAM_01":"hover_machine",
        "ENM_SITE7_MORTAR_01":"anchored_machine", "ENM_SITE7_PRISM_01":"hover_machine",
        "ENM_SITE7_NULL_PYLON_01":"anchored_machine", "BOSS_SITE7_FORGE_01":"anchored_machine",
        "BOSS_SITE7_CARRIER_01":"anchored_machine", "BOSS_SITE7_RELAY_01":"anchored_machine",
        "BOSS_SITE7_REMNANT_01":"anchored_machine", "BOSS_SITE7_AERATOR_01":"anchored_machine",
        "BOSS_SITE7_CRYO_01":"anchored_machine", "BOSS_SITE7_GANTRY_01":"anchored_machine",
        "BOSS_SITE7_ARCHIVE_01":"anchored_machine", "BOSS_SITE7_ORIGIN_01":"anchored_machine"}
    if expected_kind.get(owner_actor.enemy_id,"") != staged_kind or staged_kind.is_empty(): return false
    # Load the complete set before publishing any node/state. A single front
    # illustration is NOT an omnidirectional drone, even with an omni emitter.
    var staged: Dictionary = {}
    if staged_kind in ["hover_machine", "tracked_machine"]:
        if str(spec.get("facing_mode","")) != "authored_yaw8": return false
        var authored: Dictionary = spec.get("views",{})
        if authored.size() != 8: return false
        var hashes: Array[String] = []
        var pixel_hashes: Array[String] = []
        for direction in DIRECTIONS:
            if not authored.has(direction): return false
            var view := _read_view(authored[direction])
            if view.is_empty() or hashes.has(view.texture_sha256) or pixel_hashes.has(view.pixel_sha256): return false
            hashes.append(view.texture_sha256)
            pixel_hashes.append(view.pixel_sha256)
            staged[direction] = view
    else:
        var fixed := _read_view(spec)
        if fixed.is_empty(): return false
        staged["ANCHORED"] = fixed
    actor = owner_actor
    kind = staged_kind
    sprite = Sprite2D.new()
    sprite.name = "AuthoredMachinePixels"
    sprite.set_meta("preserve_authored_material", true)
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.centered = false
    weathering = ShaderMaterial.new()
    weathering.shader = preload("res://assets/shaders/machine_weathering.gdshader")
    weathering.set_shader_parameter("wear", 0.82 if staged_kind != "hover_machine" else 0.66)
    sprite.material = weathering
    add_child(sprite)
    views = staged
    _apply_view("E" if is_directional() else "ANCHORED")
    configured = true
    last_root = actor.global_position
    age = float(posmod(actor.get_instance_id(), 997)) / 73.0
    face_direction(actor._aim_dir)
    return true

func _apply_view(direction: String) -> void:
    if facing == direction: return
    var view: Dictionary = views[direction]
    facing = direction
    image_size = view.size
    emitter_px = view.emitter
    emitter_visible = view.emitter_visible
    render_scale = float(view.scale)
    sprite.texture = view.texture
    var pixel_scale: Vector2 = view.pixel_scale
    sprite.scale = Vector2(render_scale / pixel_scale.x,render_scale / pixel_scale.y)
    body_origin = -view.root * render_scale
    sprite.position = body_origin
    emitter_px = view.emitter * pixel_scale
    var visible: Rect2 = view.visible
    visible_rect = Rect2(visible.position * pixel_scale, visible.size * pixel_scale)

func face_direction(direction: Vector2) -> void:
    if not configured or not is_directional() or direction.length_squared() < 0.000001: return
    var local_dir := actor.global_transform.affine_inverse().basis_xform(direction)
    var sector := int(floor(fposmod(local_dir.angle()+PI/8.0,TAU)/(PI/4.0)))%8
    _apply_view(DIRECTIONS[sector])

func visible_heading_world() -> Vector2:
    if not is_directional(): return Vector2.ZERO
    var index := DIRECTIONS.find(facing)
    return global_transform.basis_xform(Vector2.from_angle(index*PI/4.0)).normalized()

func resolve_target(target: Vector2) -> Vector2:
    if not configured or not target.is_finite(): return Vector2.INF
    if not is_directional(): return (target-muzzle_world()).normalized()
    # Each authored yaw has a different physical emitter offset. Evaluate its
    # own ray, then keep the pose whose front actually agrees with that ray.
    # No interpolation, horizontal mirroring, or whole-bitmap screen rotation.
    sync_pose()
    var solution := target_solution_from(actor.global_position,target)
    if solution.is_empty(): return Vector2.INF
    _apply_view(solution.facing)
    return (target-muzzle_world()).normalized()

func target_solution_from(root_position: Vector2, target: Vector2) -> Dictionary:
    # Read-only prospective firing lane: do not teleport the body or cycle its
    # visible poses while tactics evaluate reachable destinations.
    if not configured or not target.is_finite() or not root_position.is_finite(): return {}
    var translation := root_position-actor.global_position
    var best := facing
    var error := INF
    var origin := Vector2.INF
    for i in range(DIRECTIONS.size()):
        var direction: String = DIRECTIONS[i]
        if not views.has(direction): continue
        var view: Dictionary = views[direction]
        var local_emitter: Vector2 = (view.emitter-view.root)*float(view.scale)
        var candidate_origin := to_global(local_emitter)+translation
        var ray := (target-candidate_origin).normalized()
        var heading := global_transform.basis_xform(Vector2.from_angle(i*PI/4.0)).normalized()
        var candidate_error := absf(heading.angle_to(ray))
        if candidate_error < error:
            best = direction
            error = candidate_error
            origin = candidate_origin
    # "Least wrong" is not necessarily forward. Inside the illustrated gun's
    # reach there may be no legal view. Retain the pose and explicitly reject
    # this target; the tactics controller must reposition without winding up.
    if error > MAX_TARGET_ERROR: return {}
    return {"facing":best,"origin":origin,"direction":(target-origin).normalized()}

func _process(delta: float) -> void:
    if not configured: return
    age += delta
    flash = move_toward(flash, 0.0, delta * 7.0)
    var displacement := actor.global_position-last_root
    last_root = actor.global_position
    var speed := displacement.length()/maxf(delta,0.001)
    travel += minf(displacement.length(),20.0)
    motion_speed = lerpf(motion_speed,minf(speed,360.0),1.0-exp(-delta*9.0))
    var locked: bool = actor.tactics != null and actor.tactics.state in ["WINDUP","BURST","LUNGE"]
    # Freeze emitter geometry throughout a telegraph and its burst. Recoil
    # settles after emission, so the advertised shot never drifts off its ray.
    if not locked:
        if pending_recoil != Vector2.ZERO:
            recoil = pending_recoil
            pending_recoil = Vector2.ZERO
        bank = lerpf(bank,clampf(actor.velocity.x/118.0,-1.0,1.0)*0.045,1.0-exp(-delta*7.0))
        suspension = lerpf(suspension,sin(age*2.2)*1.6+sin(age*3.7)*0.5,1.0-exp(-delta*6.0))
        recoil = recoil.lerp(Vector2.ZERO,1.0-exp(-delta*12.0))
    var charge := 0.0
    if actor.tactics and actor.tactics.state == "WINDUP":
        charge = clampf(1.0-actor.tactics.state_left/actor.tactics.state_duration,0.0,1.0)
    weathering.set_shader_parameter("heat",maxf(charge,flash))
    weathering.set_shader_parameter("damage",1.0-actor.health/maxf(actor.max_health,1.0))
    sync_pose()
    queue_redraw()

func sync_pose() -> void:
    if not configured: return
    # Use bounded rigid-body motion only. No image stretching or cut-up limbs.
    if kind == "hover_machine":
        rotation = bank
        position = Vector2(0,suspension)+recoil
        if actor.health <= 0.0:
            rotation += (0.55 - actor._death_left) * 1.2
            position.y += (0.55 - actor._death_left) * 65.0
    elif kind == "tracked_machine":
        # Treads stay grounded. Never apply drone hover or bitmap yaw here.
        rotation = 0.0
        position = Vector2.ZERO
    else:
        rotation = 0.0
        position = Vector2.ZERO
    sprite.modulate = Color.WHITE.lerp(Color(1.3,1.15,1.25),actor._hit_flash * 0.4)

func is_directional() -> bool:
    return kind in ["hover_machine", "tracked_machine"]

func muzzle_world() -> Vector2:
    sync_pose()
    return sprite.to_global(emitter_px)

func fired() -> void:
    flash = 1.0
    # Anchored chassis retain a fixed root. Their recoil is light/heat only.
    if kind == "hover_machine":
        pending_recoil = -actor._aim_dir*2.2
    queue_redraw()

func hit_rect_world() -> Rect2:
    var shape := Rect2(visible_rect.position + visible_rect.size * Vector2(0.12,0.15), visible_rect.size * Vector2(0.76,0.70))
    var bounds := Rect2(sprite.to_global(shape.position),Vector2.ZERO)
    for corner in [shape.position + Vector2(shape.size.x,0), shape.end, shape.position + Vector2(0,shape.size.y)]:
        bounds = bounds.expand(sprite.to_global(corner))
    return bounds

func _draw() -> void:
    if not configured or actor.health <= 0.0: return
    # Short-lived ground dust and ion wakes, tied to travelled distance rather
    # than every unit sharing one perpetual sine-wave animation.
    if motion_speed > 8.0 and kind in ["hover_machine","tracked_machine"]:
        var aft := -actor.velocity.normalized()
        for i in range(5):
            var phase := fposmod(travel/34.0+float(i)/5.0,1.0)
            var side := aft.orthogonal()*sin(float(i)*7.1)*8.0
            var point := aft*(10.0+phase*28.0)+side+Vector2(0,3)
            var tint := Color(0.40,0.34,0.25,(1.0-phase)*0.13) if kind == "tracked_machine" else Color(0.35,0.65,0.72,(1.0-phase)*0.10)
            draw_circle(point,2.0+phase*5.0,tint)
    var center := to_local(sprite.to_global(emitter_px))
    var charge := 0.0
    if actor.tactics and actor.tactics.state == "WINDUP":
        charge = clampf(1.0 - actor.tactics.state_left / actor.tactics.state_duration, 0.0, 1.0)
    var radius := 8.0 if kind == "hover_machine" else 26.0
    var tint := Color(0.94,0.25,0.75)
    if actor.enemy_id == "ENM_SITE7_BULWARK_01":
        radius = 7.0
        tint = Color(1.0,0.69,0.24)
    elif actor.enemy_id == "ENM_SITE7_RAM_01":
        radius = 5.0
        tint = Color(1.0,0.35,0.10)
    elif actor.enemy_id == "ENM_SITE7_MORTAR_01":
        radius = 9.0
        tint = Color(0.70,0.45,1.0)
    elif actor.enemy_id == "BOSS_SITE7_RELAY_01":
        tint = Color("d8283c")
    elif actor.enemy_id == "BOSS_SITE7_REMNANT_01":
        tint = Color("bfe8ff")
    elif actor.enemy_id == "BOSS_SITE7_AERATOR_01":
        tint = Color("8fdc4a")
    elif actor.enemy_id == "BOSS_SITE7_CRYO_01":
        tint = Color("ff7fc8")
    elif actor.enemy_id == "BOSS_SITE7_GANTRY_01":
        tint = Color("ffd84a")
    elif actor.enemy_id == "BOSS_SITE7_ARCHIVE_01":
        tint = Color("2fe0b4")
    elif actor.enemy_id == "BOSS_SITE7_ORIGIN_01":
        tint = Color("f4efe8")
    var power := maxf(flash, charge * 0.5)
    if power > 0.0 and emitter_visible:
        draw_circle(center, radius * (1.0 + power), Color(tint,power * 0.22))
        var rim := Color(0.8,0.45,1.0) if actor.enemy_id in ["ENM_SITE7_DRONE_01","BOSS_SITE7_ANCHOR_01"] else tint
        draw_arc(center, radius * 1.4, -age, TAU-age, 32, Color(rim,power * 0.75),1.5)

func debug_contract() -> Dictionary:
    return {"kind":kind,"configured":configured,"art_warp":false,
        "gait_claim":false,"emitter_px":emitter_px,"emitter_world":muzzle_world(),
        "native_size":image_size,"visible_rect":visible_rect,"display_height":image_size.y * render_scale,
        "facing":facing,"view_count":views.size(),"heading_world":visible_heading_world(),
        "emitter_visible":emitter_visible,"texture_sha256":views[facing].texture_sha256,
        "mirrored":false}
