extends Node2D
## Whole authored Motion Studio frames for enemy bipeds. Candidate intake does
## not publish a registry entry or authorize art. AI owns speeds and attacks;
## this node owns only source pixels, distance phase and the visible muzzle.
const DIRECTIONS := ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const MAX_TARGET_ERROR := PI / 8.0 + 0.02
# Latest user roster: one reusable humanoid enemy, every other role is a robot.
const IDENTITIES := {"ENM_SITE7_RIFLE_01":"site7_rifle"}
var actor: EnemyActor
var sprite: Sprite2D
var configured := false
var clips: Dictionary = {}
var textures: Dictionary = {}
var facing := 4
var phase := 0.0
var moving := false
var move_direction := Vector2.RIGHT
var action := "idle"
var frame := 0
var cell := Vector2.ZERO
var root_px := Vector2.ZERO
var display_height := 129.6
var render_scale := 1.0
var cycle_distance := 1.0
var emitter_px := Vector2.ZERO
static var _pixel_hash_cache: Dictionary = {}

static func _used_sequence_hash(image: Image, file_hash: String, size: Vector2i, columns: int, count: int) -> String:
    # Hash the displayed cells in order, not atlas packaging/padding. The same
    # page can be interpreted differently, so geometry belongs in the cache key.
    var cache_key := file_hash+":"+str(size)+":"+str(columns)+":"+str(count)
    if _pixel_hash_cache.has(cache_key): return _pixel_hash_cache[cache_key]
    var canonical := image.duplicate() as Image
    canonical.convert(Image.FORMAT_RGBA8)
    var digest := HashingContext.new()
    digest.start(HashingContext.HASH_SHA256)
    digest.update((str(size)+":"+str(count)+":ordered-used-RGBA8:").to_utf8_buffer())
    for index in range(count):
        var used := canonical.get_region(Rect2i(Vector2i(index%columns,int(index/columns))*size,size))
        if used.is_invisible(): return ""
        var bytes := used.get_data()
        for alpha in range(3,bytes.size(),4):
            if bytes[alpha]==0:
                bytes[alpha-3]=0;bytes[alpha-2]=0;bytes[alpha-1]=0
        digest.update(bytes)
    var value := digest.finish().hex_encode()
    _pixel_hash_cache[cache_key]=value
    return value

static func _number(value: Variant) -> bool:
    return (value is int or value is float) and is_finite(float(value))

static func _point(value: Variant) -> Vector2:
    if not value is Array or value.size() != 2 or not _number(value[0]) or not _number(value[1]): return Vector2.INF
    return Vector2(float(value[0]),float(value[1]))

static func _path(value: Variant) -> bool:
    return value is String and value.begins_with("res://") and not ".." in value and not "\\" in value

func configure(owner_actor: EnemyActor, spec: Dictionary) -> bool:
    if configured or not is_instance_valid(owner_actor): return false
    var identity := str(IDENTITIES.get(owner_actor.enemy_id,""))
    if identity.is_empty() or str(spec.get("character_id","")) != identity or str(spec.get("enemy_id","")) != owner_actor.enemy_id or spec.get("kind","") != "authored_biped8": return false
    var path: Variant = spec.get("profile","")
    if not _path(path) or not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != str(spec.get("profile_sha256","")): return false
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if not parsed is Dictionary or parsed.get("id","") != identity: return false
    var animation: Variant = parsed.get("animation",{})
    var locomotion: Variant = parsed.get("locomotion",{})
    var views: Variant = parsed.get("views",{})
    var atlas_files: Variant = spec.get("atlas_files",{})
    if not animation is Dictionary or animation.get("presentation","") != "authored_frames" or not locomotion is Dictionary or not views is Dictionary or not atlas_files is Dictionary: return false
    var height: Variant = spec.get("display_height",129.6)
    var metres: Variant = parsed.get("heightMetres",0)
    var stride: Variant = locomotion.get("walkStride",0)
    if not _number(height) or not _number(metres) or not _number(stride): return false
    if height < 56 or height > 240 or metres <= 0 or stride <= 0: return false
    var staged_distance := float(stride)*float(height)/float(metres)
    if not is_finite(staged_distance) or staged_distance <= 0.0: return false
    if views.size() != 8: return false
    var staged_clips: Dictionary = {}
    var staged_textures: Dictionary = {}
    var geometry: Dictionary = {}
    # No state/visible node is published until the complete set validates.
    for clip_action in ["idle","walk"]:
        var hashes: Array[String] = []
        var pixel_hashes: Array[String] = []
        for direction in DIRECTIONS:
            var view: Variant = views.get(direction,{})
            if not view is Dictionary: return false
            var clip: Variant = view.get(clip_action,{})
            if not clip is Dictionary: return false
            var size := _point(clip.get("cell",[]))
            var origin := _point(clip.get("root",[]))
            var source_height: Variant = clip.get("height",0)
            var count: Variant = clip.get("frames",0)
            var columns: Variant = clip.get("columns",0)
            if not size.is_finite() or not origin.is_finite() or size.x <= 0 or size.y <= 0: return false
            if size.x != floor(size.x) or size.y != floor(size.y): return false
            if not _number(source_height) or source_height <= 0 or source_height > size.y: return false
            var staged_scale := float(height)/float(source_height)
            if not is_finite(staged_scale) or staged_scale <= 0.0 or not (size*staged_scale).is_finite() or not (origin*staged_scale).is_finite(): return false
            if not Rect2(Vector2.ZERO,size).has_point(origin): return false
            if not _number(count) or count != (1 if clip_action == "idle" else 6) or not _number(columns) or columns < 1 or floor(float(columns)) != float(columns) or columns > count: return false
            var muzzles: Variant = clip.get("muzzles",[])
            if not muzzles is Array or muzzles.size() != count: return false
            for value in muzzles:
                if not Rect2(Vector2.ZERO,size).has_point(_point(value)): return false
            var starts: Variant = clip.get("phaseStarts",[])
            if clip_action == "walk":
                if not starts is Array or starts.size() != count: return false
                var previous := -1.0
                for value in starts:
                    if not _number(value) or value < 0 or value >= 1 or value <= previous: return false
                    previous = float(value)
                if float(starts[0]) != 0.0: return false
            if geometry.is_empty(): geometry={"cell":size,"root":origin,"height":float(source_height)}
            elif size != geometry.cell or origin != geometry.root or float(source_height) != geometry.height: return false
            var asset: Variant = clip.get("image","")
            if not asset is String or asset.is_empty() or asset.begins_with("/") or ":" in asset or ".." in asset or "\\" in asset: return false
            var asset_root: Variant = spec.get("asset_root","")
            if not _path(asset_root) or not asset_root.ends_with("/"): return false
            var texture_path: String = asset_root+asset
            var expected := str(atlas_files.get(texture_path,""))
            if expected.length() != 64 or not FileAccess.file_exists(texture_path) or FileAccess.get_sha256(texture_path) != expected or hashes.has(expected): return false
            var image := Image.load_from_file(texture_path)
            if image == null or image.is_empty() or image.detect_alpha() == Image.ALPHA_NONE: return false
            if Vector2(image.get_size()) != Vector2(size.x*columns,size.y*ceil(float(count)/columns)): return false
            var pixel_hash := _used_sequence_hash(image,expected,Vector2i(size),int(columns),int(count))
            if pixel_hash.is_empty() or pixel_hashes.has(pixel_hash): return false
            pixel_hashes.append(pixel_hash)
            hashes.append(expected)
            var key: String = direction+"/"+clip_action
            staged_clips[key] = clip.duplicate(true)
            staged_textures[key] = ImageTexture.create_from_image(image)
    actor=owner_actor
    var initial_aim := global_transform.affine_inverse().basis_xform(actor._aim_dir)
    if initial_aim.is_finite() and initial_aim.length_squared()>0.000001:
        facing=int(floor(fposmod(initial_aim.angle()+PI/8.0,TAU)/(PI/4.0)))%8
    clips=staged_clips
    textures=staged_textures
    cell=geometry.cell
    root_px=geometry.root
    display_height=float(height)
    render_scale=display_height/float(geometry.height)
    # Metres are converted using THIS source height, not player speed or a
    # hard-coded 100px/m. Actual world displacement is the sole phase clock.
    cycle_distance=staged_distance
    sprite=Sprite2D.new()
    sprite.name="AuthoredBipedPixels"
    sprite.centered=false
    sprite.region_enabled=true
    sprite.region_filter_clip_enabled=true
    sprite.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.set_meta("preserve_authored_material",true)
    sprite.position=-root_px*render_scale
    sprite.scale=Vector2.ONE*render_scale
    add_child(sprite)
    configured=true
    sync_pose()
    return true

func _render_phase(sector: int) -> float:
    var heading := global_transform.basis_xform(Vector2.from_angle(sector*PI/4.0)).normalized()
    return fposmod(1.0-phase,1.0) if move_direction.dot(heading) < -0.35 else phase

func _frame_for(clip: Dictionary, at_phase: float) -> int:
    var starts: Array=clip.get("phaseStarts",[0.0])
    for index in range(starts.size()-1,-1,-1):
        if at_phase >= float(starts[index]): return index
    return 0

func commit_displacement(displacement: Vector2) -> void:
    if not configured or not displacement.is_finite(): return
    moving=displacement.length() > 0.000001 and actor.health > 0.0
    if moving:
        move_direction=displacement.normalized()
        phase=fposmod(phase+displacement.length()/cycle_distance,1.0)
    sync_pose()

func sync_pose() -> void:
    if not configured: return
    action="walk" if moving and actor.health > 0.0 else "idle"
    var key: String=DIRECTIONS[facing]+"/"+action
    var clip: Dictionary=clips[key]
    frame=_frame_for(clip,_render_phase(facing)) if action == "walk" else 0
    var columns: int=clip.columns
    sprite.texture=textures[key]
    sprite.region_rect=Rect2(Vector2(frame%columns,floor(float(frame)/columns))*cell,cell)
    emitter_px=_point(clip.muzzles[frame])
    sprite.modulate=Color.WHITE.lerp(Color(1.3,1.15,1.25),actor._hit_flash*0.4)

func resolve_target(target: Vector2, stationary: bool = false) -> Vector2:
    if not configured or not target.is_finite(): return Vector2.INF
    if stationary: moving=false
    var selected_action := "walk" if moving else "idle"
    var best := facing
    var error := INF
    for sector in range(8):
        var clip: Dictionary=clips[DIRECTIONS[sector]+"/"+selected_action]
        var index := _frame_for(clip,_render_phase(sector)) if selected_action == "walk" else 0
        var muzzle := to_global((_point(clip.muzzles[index])-root_px)*render_scale)
        var offset := target-muzzle
        if offset.length_squared() < 0.000001: continue
        var heading := global_transform.basis_xform(Vector2.from_angle(sector*PI/4.0)).normalized()
        var candidate_error := absf(heading.angle_to(offset.normalized()))
        if candidate_error < error:
            error=candidate_error
            best=sector
    sync_pose()
    if error > MAX_TARGET_ERROR: return Vector2.INF
    facing=best
    sync_pose()
    return (target-muzzle_world()).normalized()

func muzzle_world() -> Vector2:
    sync_pose()
    return to_global((emitter_px-root_px)*render_scale)

func visible_heading_world() -> Vector2:
    return global_transform.basis_xform(Vector2.from_angle(facing*PI/4.0)).normalized()

func hit_rect_world() -> Rect2:
    return _world_rect(Rect2(Vector2(-display_height*0.17,-display_height*0.81),Vector2(display_height*0.34,display_height*0.79)))

func visual_rect_world() -> Rect2:
    return _world_rect(Rect2(-root_px*render_scale,cell*render_scale))

func _world_rect(local_rect: Rect2) -> Rect2:
    var result := Rect2(to_global(local_rect.position),Vector2.ZERO)
    for corner in [local_rect.position+Vector2(local_rect.size.x,0),local_rect.end,local_rect.position+Vector2(0,local_rect.size.y)]:
        result=result.expand(to_global(corner))
    return result
