extends Node2D
class_name MotionLabCharacterRuntime

## Runtime bridge for the current Motion Studio sources.  It reads the exact
## project-local profile and authored WebP atlases instead of rebuilding a
## character in Godot.  The profile owns source size, root, per-frame muzzle
## anchors and optional non-uniform gait timing.

const FEATURE_SETTING := "sable_visuals/motion_lab_character_runtime"
const PROFILE_ROOT := "res://motion_lab_v1/public/assets/atlas/"
const SOURCE_ROOT := "res://motion_lab_v1/public/"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const DEFAULT_DISPLAY_HEIGHT_PX := 129.6
const PIXELS_PER_METRE := 100.0
const MOVE_EPSILON := 0.05
# The Web delivery uses separately derived half-resolution atlases. A cell is
# still three times taller than its 129.6 px on-map presentation; source art,
# profile coordinates, muzzle anchors and native atlases stay unchanged.
const WEB_ATLAS_SCALE := 0.5
## Per-frame walk x shifts that keep the torso on its cycle mean, measured from the
## atlases by tools/character_pipeline/build_walk_torso_registration.py.
const WALK_REGISTRATION_PATH := "res://data/art_profiles/motion_lab_walk_registration.json"

## Atlases DeployWarmer decoded on the briefing screen, each handed to the next
## _load_profile_assets that reads its path. The squad's atlases are ~400 MB of native
## VRAM, so nothing here outlives the deploy it was prepared for.
static var _prepared: Dictionary = {}

## The atlas files _load_profile_assets reads for a character, in the same order.
static func atlas_paths(character_id: String) -> Array[String]:
    var paths: Array[String] = []
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PROFILE_ROOT + character_id + "/profile.json"))
    if not (parsed is Dictionary) or not ((parsed as Dictionary).get("views", {}) is Dictionary): return paths
    var views: Dictionary = parsed.views
    for direction in DIRECTIONS:
        var clips: Variant = views.get(direction, {})
        for action in ["walk", "idle"]:
            var clip: Variant = clips.get(action, {}) if clips is Dictionary else {}
            if not (clip is Dictionary) or str(clip.get("image", "")).is_empty(): continue
            var path := SOURCE_ROOT + str(clip.image)
            paths.append(path.get_basename() + ".web.webp" if OS.has_feature("web") else path)
    return paths

## Worker-thread safe decode of one atlas; null when missing or undecodable.
static func decode_atlas(path: String) -> Image:
    var source_bytes := FileAccess.get_file_as_bytes(path)
    if source_bytes.is_empty(): return null
    var image := Image.new()
    if image.load_webp_from_buffer(source_bytes) != OK or image.is_empty(): return null
    return image

static func keep_prepared(path: String, image: Image) -> void:
    if image != null: _prepared[path] = ImageTexture.create_from_image(image)

static func has_prepared(path: String) -> bool:
    return _prepared.has(path)

static func drop_prepared() -> void:
    _prepared.clear()

var actor: OperatorActor
var visual: OperatorVisual
var sprite: Sprite2D

var _active := false
var _activation_attempted := false
var _status := "not_attempted"
var _character_id := ""
var _profile_path := ""
var _profile: Dictionary = {}
var _clips: Dictionary = {}
var _textures: Dictionary = {"walk": [], "idle": []}
var _cell_size := Vector2(768.0, 768.0)
var _root := Vector2(384.0, 716.0)
var _source_height := 656.0
var _display_height := DEFAULT_DISPLAY_HEIGHT_PX
var _display_scale := DEFAULT_DISPLAY_HEIGHT_PX / 656.0
var _atlas_scale := 1.0
var _walk_cycle_distance := 160.0
var _run_cycle_distance := 195.0
var _phase := 0.0
var _moving := false
var _running := false
var _move_sector := 0
var _move_direction := Vector2.RIGHT
var _active_sector := 0
var _active_frame := 0
var _active_action := "idle"
var _active_muzzle := Vector2.ZERO
var _visual_alpha_before_activation := 1.0
## Sprite position that puts the cell root on the actor.
var _base_sprite_position := Vector2.ZERO
## Direction -> PackedFloat32Array of walk-frame x shifts in cell px (may be empty).
var _walk_registration: Dictionary = {}


func _ready() -> void:
    process_priority = 144
    actor = get_parent() as OperatorActor
    visual = actor.get_node_or_null("VisualRoot") as OperatorVisual if actor else null
    sprite = Sprite2D.new()
    sprite.name = "MotionLabAuthoredRaster"
    sprite.centered = true
    sprite.region_enabled = true
    sprite.region_filter_clip_enabled = true
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
    sprite.z_index = 30
    sprite.visible = false
    add_child(sprite)
    if actor and not actor.primary_fired.is_connected(_on_primary_fired):
        actor.primary_fired.connect(_on_primary_fired)
    call_deferred("_refresh_activation")


func _feature_enabled() -> bool:
    return bool(ProjectSettings.get_setting(FEATURE_SETTING, true))


## True until this runtime has decided whether it owns the body. Older
## presentations wait instead of decoding atlases it would immediately hide.
func activation_pending() -> bool:
    return not _activation_attempted and actor != null and _feature_enabled() \
        and not str(actor.art_profile.get("motion_lab_character_id", "")).strip_edges().is_empty()


func _process(_delta: float) -> void:
    if actor == null:
        return
    if not _activation_attempted:
        _refresh_activation()
    if not _active:
        return
    if not _feature_enabled():
        _deactivate("feature_disabled")
        return
    _show_current_frame()
    sprite.modulate = Color(0.48, 0.50, 0.54, 0.72) if actor.is_downed() else Color.WHITE


func _refresh_activation() -> void:
    _activation_attempted = true
    if actor == null or not _feature_enabled():
        _status = "disabled_or_missing_actor"
        return
    _character_id = str(actor.art_profile.get("motion_lab_character_id", "")).strip_edges().to_lower()
    if _character_id.is_empty():
        _status = "profile_has_no_motion_lab_character"
        return
    if _character_id not in ["aster", "mica", "rook"]:
        _status = "unsupported_motion_lab_character"
        return
    _profile_path = PROFILE_ROOT + _character_id + "/profile.json"
    if not FileAccess.file_exists(_profile_path):
        _fail("profile_missing")
        return
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(_profile_path))
    if not (parsed is Dictionary):
        _fail("profile_parse_failed")
        return
    _profile = parsed as Dictionary
    var animation := _profile.get("animation", {}) as Dictionary
    # MICA's existing package predates the explicit `presentation` marker.
    # Its schema-3 authored_keyframes declaration is the equivalent
    # compatibility contract; do not rebuild, reinterpret, or substitute its
    # visible source pixels merely to add metadata.
    var authored_presentation := str(animation.get("presentation", "")) == "authored_frames" or str(animation.get("kind", "")) == "authored_keyframes"
    if str(_profile.get("id", "")) != _character_id or not authored_presentation:
        _fail("profile_identity_or_presentation_invalid")
        return
    if not _load_profile_assets():
        return
    _active = true
    _status = "active"
    _deactivate_older_presentations()
    if visual:
        _visual_alpha_before_activation = visual.modulate.a
        visual.modulate.a = 0.0
        # The hidden vector rig keeps its bones and sockets, but its 2048px
        # sheet and detail overlay were ~128 MB of unseen VRAM per squad.
        visual.release_hidden_art()
        var detail := actor.get_node_or_null("DetailOverlayPresentation")
        if detail != null and detail.has_method("release_hidden_art"):
            detail.call("release_hidden_art")
    sprite.visible = true
    _phase = 0.0
    _moving = false
    _show_current_frame()


func _load_profile_assets() -> bool:
    var views_variant: Variant = _profile.get("views", {})
    if not (views_variant is Dictionary):
        return _fail("views_missing")
    var views := views_variant as Dictionary
    _clips.clear()
    _textures = {"walk": [], "idle": []}
    for direction in DIRECTIONS:
        var direction_variant: Variant = views.get(direction, {})
        if not (direction_variant is Dictionary):
            return _fail("missing_direction_" + direction)
        var direction_clips := direction_variant as Dictionary
        var stored: Dictionary = {}
        for action in ["walk", "idle"]:
            var clip_variant: Variant = direction_clips.get(action, {})
            if not (clip_variant is Dictionary):
                return _fail("missing_" + action + "_" + direction)
            var clip := (clip_variant as Dictionary).duplicate(true)
            if not _validate_clip(clip, direction, action):
                return false
            var texture_path := SOURCE_ROOT + str(clip.get("image", ""))
            if OS.has_feature("web"):
                texture_path = texture_path.get_basename() + ".web.webp"
                if not FileAccess.file_exists(texture_path):
                    return _fail("web_texture_missing_" + direction + "_" + action)
            var texture: Texture2D = _prepared.get(texture_path)
            _prepared.erase(texture_path)
            if texture == null:
                var source_bytes := FileAccess.get_file_as_bytes(texture_path)
                if source_bytes.is_empty():
                    return _fail("texture_missing_" + direction + "_" + action)
                var source_image := Image.new()
                if source_image.load_webp_from_buffer(source_bytes) != OK or source_image.is_empty():
                    return _fail("texture_decode_failed_" + direction + "_" + action)
                texture = ImageTexture.create_from_image(source_image)
            var cell := _point(clip.get("cell", []))
            var columns := int(clip.get("columns", 0))
            var frames := int(clip.get("frames", 0))
            var expected_rows := int(ceil(float(frames) / float(columns)))
            var atlas_scale := WEB_ATLAS_SCALE if OS.has_feature("web") else 1.0
            if texture.get_width() != int(cell.x * columns * atlas_scale) or texture.get_height() != int(cell.y * expected_rows * atlas_scale):
                return _fail("texture_dimensions_invalid_" + direction + "_" + action)
            _atlas_scale = atlas_scale
            if direction == "E" and action == "walk":
                _cell_size = cell
                _root = _point(clip.get("root", []))
                _source_height = float(clip.get("height", 0.0))
            elif cell != _cell_size or _point(clip.get("root", [])) != _root or not is_equal_approx(float(clip.get("height", 0.0)), _source_height):
                return _fail("inconsistent_geometry_" + direction + "_" + action)
            (_textures[action] as Array).append(texture)
            stored[action] = clip
        _clips[direction] = stored
    if _source_height <= 0.0 or _cell_size.x <= 0.0 or _cell_size.y <= 0.0:
        return _fail("invalid_source_geometry")
    _display_height = clampf(float(actor.art_profile.get("motion_lab_display_height_px", DEFAULT_DISPLAY_HEIGHT_PX)), 56.0, 240.0)
    _display_scale = _display_height / _source_height
    var locomotion := _profile.get("locomotion", {}) as Dictionary
    # Every operator walks one gait cycle per walkStride x 100 map px. ASTER once
    # scaled hers to her 129.6 px height (120.6 px), which drove 164 steps a minute
    # against MICA's 114 and ROOK's 104 and read as a scurry.
    _walk_cycle_distance = maxf(1.0, float(locomotion.get("walkStride", 1.6)) * PIXELS_PER_METRE)
    _run_cycle_distance = maxf(1.0, float(locomotion.get("runStride", 1.95)) * PIXELS_PER_METRE)
    _base_sprite_position = (_cell_size * 0.5 - _root) * _display_scale
    sprite.position = _base_sprite_position
    sprite.scale = Vector2.ONE * (_display_scale / _atlas_scale)
    _load_walk_registration()
    return true


## Reads this character's walk torso shifts; a direction whose frame sources no
## longer match the measured SHA-256 rows keeps the plain hip placement.
func _load_walk_registration() -> void:
    _walk_registration.clear()
    if not FileAccess.file_exists(WALK_REGISTRATION_PATH): return
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(WALK_REGISTRATION_PATH))
    if not (parsed is Dictionary): return
    var character: Variant = ((parsed as Dictionary).get("characters", {}) as Dictionary).get(_character_id, {})
    if not (character is Dictionary): return
    var walk: Variant = (character as Dictionary).get("walk", {})
    if not (walk is Dictionary): return
    for direction in DIRECTIONS:
        var rows: Variant = (walk as Dictionary).get(direction, [])
        var sources: Variant = (_clips[direction]["walk"] as Dictionary).get("sources", [])
        if not (rows is Array) or not (sources is Array) or (rows as Array).size() != (sources as Array).size() or (rows as Array).size() != int(_clips[direction]["walk"]["frames"]):
            continue
        var shifts := PackedFloat32Array()
        for index in range((rows as Array).size()):
            var row: Variant = (rows as Array)[index]
            var source: Variant = (sources as Array)[index]
            if not (row is Dictionary) or not (source is Dictionary) or str((row as Dictionary).get("source_sha256", "")) != str((source as Dictionary).get("sha256", "-")):
                shifts.clear()
                break
            shifts.append(float((row as Dictionary).get("offset_x", 0.0)))
        if not shifts.is_empty(): _walk_registration[direction] = shifts


## Sprite position while `frame` of `action` faces `direction`.
func _sprite_position_for(action: String, direction: String, frame: int) -> Vector2:
    if action != "walk" or not _walk_registration.has(direction): return _base_sprite_position
    var shifts: PackedFloat32Array = _walk_registration[direction]
    return _base_sprite_position + Vector2(shifts[frame] * _display_scale, 0.0)


func _validate_clip(clip: Dictionary, direction: String, action: String) -> bool:
    var frames := int(clip.get("frames", 0))
    var columns := int(clip.get("columns", 0))
    var cell := _point(clip.get("cell", []))
    var root := _point(clip.get("root", []))
    var muzzles: Variant = clip.get("muzzles", [])
    if frames < 1 or columns < 1 or cell.x <= 0.0 or cell.y <= 0.0 or root.x < 0.0 or root.y < 0.0 or not (muzzles is Array) or (muzzles as Array).size() != frames:
        _fail("invalid_clip_" + direction + "_" + action)
        return false
    for raw_muzzle in muzzles as Array:
        var muzzle := _point(raw_muzzle)
        if muzzle.x < 0.0 or muzzle.y < 0.0 or muzzle.x >= cell.x or muzzle.y >= cell.y:
            _fail("invalid_muzzle_" + direction + "_" + action)
            return false
    var starts: Variant = clip.get("phaseStarts", [])
    if starts is Array and not (starts as Array).is_empty():
        if (starts as Array).size() != frames or not is_equal_approx(float((starts as Array)[0]), 0.0):
            _fail("invalid_phase_starts_" + direction + "_" + action)
            return false
        var previous := -1.0
        for raw_start in starts as Array:
            if not (raw_start is int or raw_start is float):
                _fail("invalid_phase_starts_" + direction + "_" + action)
                return false
            var start := float(raw_start)
            if start < 0.0 or start >= 1.0 or start <= previous:
                _fail("invalid_phase_starts_" + direction + "_" + action)
                return false
            previous = start
    return true


func _point(value: Variant) -> Vector2:
    if not (value is Array) or (value as Array).size() != 2:
        return Vector2(-1.0, -1.0)
    var pair := value as Array
    return Vector2(float(pair[0]), float(pair[1]))


func _deactivate_older_presentations() -> void:
    var aster_preview := actor.get_node_or_null("AsterV4LocomotionPreview")
    if aster_preview != null and aster_preview.has_method("deactivate_for_motion_lab"):
        aster_preview.call("deactivate_for_motion_lab")
    var legacy_raster := actor.get_node_or_null("AuthoredRasterPresentation")
    if legacy_raster != null and legacy_raster.has_method("debug_loaded") and bool(legacy_raster.call("debug_loaded")) and legacy_raster.has_method("deactivate_for_motion_lab"):
        legacy_raster.call("deactivate_for_motion_lab")
    var fast_runtime := actor.get_node_or_null("FastCharacterRuntime")
    if fast_runtime != null and fast_runtime.has_method("is_runtime_active") and bool(fast_runtime.call("is_runtime_active")) and fast_runtime.has_method("deactivate_for_motion_lab"):
        fast_runtime.call("deactivate_for_motion_lab")


func set_motion_intent(move: Vector2, running: bool) -> void:
    if not _active:
        return
    _running = running
    if move.length_squared() > 0.0001:
        _move_sector = _sector_from_vector(move)


func commit_actor_displacement(displacement: Vector2, _delta: float) -> void:
    if not _active:
        return
    _moving = displacement.length() > MOVE_EPSILON and not actor.is_downed()
    if _moving:
        _move_sector = _sector_from_vector(displacement)
        _move_direction = displacement.normalized()
        var cycle_distance := _run_cycle_distance if _running else _walk_cycle_distance
        _phase = fposmod(_phase + displacement.length() / cycle_distance, 1.0)
    _show_current_frame()


func _on_primary_fired(fired_actor: OperatorActor) -> void:
    if _active and fired_actor == actor:
        # The approved Motion Studio walk/idle art remains whole-body while
        # firing. Do not replace its feet with a legacy split-fire layer.
        _show_current_frame()


func _show_current_frame() -> void:
    if not _active or actor == null:
        return
    var action := "walk" if _moving and not actor.is_downed() else "idle"
    var sector := posmod(actor.facing_sector, DIRECTIONS.size())
    _show(action, sector, _render_phase(sector))


func refresh_pose() -> void:
    # Pointer events may occur between physics ticks. Commit the visible body
    # and muzzle immediately without advancing distance, gait or ammunition.
    _show_current_frame()


func _render_phase(sector: int) -> float:
    # Same reverse-walk policy as Motion Studio Actor.renderPose. Resolve it
    # separately for each candidate facing, including its per-frame muzzle.
    var backwards := _move_direction.dot(Vector2.from_angle(float(sector) * PI / 4.0)) < -0.35
    return fposmod(1.0 - _phase, 1.0) if backwards else _phase


func _show(action: String, sector: int, phase: float) -> void:
    var direction := DIRECTIONS[posmod(sector, DIRECTIONS.size())]
    var direction_clips := _clips.get(direction, {}) as Dictionary
    var clip := direction_clips.get(action, {}) as Dictionary
    if clip.is_empty():
        return
    var frame := 0 if action == "idle" else _frame_for_phase(clip, phase)
    var columns := int(clip["columns"])
    var cell := _point(clip["cell"])
    sprite.texture = ((_textures[action] as Array)[posmod(sector, DIRECTIONS.size())]) as Texture2D
    sprite.region_rect = Rect2(
        float(frame % columns) * cell.x * _atlas_scale,
        float(floor(float(frame) / float(columns))) * cell.y * _atlas_scale,
        cell.x * _atlas_scale,
        cell.y * _atlas_scale
    )
    sprite.position = _sprite_position_for(action, direction, frame)
    _active_action = action
    _active_sector = posmod(sector, DIRECTIONS.size())
    _active_frame = frame
    _active_muzzle = _point((clip["muzzles"] as Array)[frame])


func _frame_for_phase(clip: Dictionary, phase: float) -> int:
    var frames := int(clip["frames"])
    var normalized := fposmod(phase, 1.0)
    var starts: Variant = clip.get("phaseStarts", [])
    if starts is Array and (starts as Array).size() == frames:
        for index in range(frames - 1, -1, -1):
            if normalized >= float((starts as Array)[index]):
                return index
    return clampi(int(floor(normalized * float(frames))), 0, frames - 1)


func _sector_from_vector(vector: Vector2) -> int:
    if vector.length_squared() < 0.0001:
        return actor.facing_sector if actor else 0
    return int(floor(fposmod(vector.angle() + PI / 8.0, TAU) / (PI / 4.0))) % DIRECTIONS.size()


func get_authored_muzzle_global_position() -> Vector2:
    var local_point := sprite.position + (_active_muzzle - _cell_size * 0.5) * _display_scale
    return to_global(local_point)

func resolve_pointer_aim(target: Vector2) -> Dictionary:
    # Direct adapter of public/combat-aim.js: choose facing and its illustrated
    # muzzle together; emit exactly that ray without changing the gait phase.
    var fallback := (target - actor.global_position).normalized()
    if fallback.length_squared() < 0.001: fallback = actor.aim_world
    var action := "walk" if _moving and not actor.is_downed() else "idle"
    var best_error := INF
    var best: Dictionary = {}
    var current: Dictionary = {}
    var reach := 0.0
    for sector in range(8):
        var clip: Dictionary = _clips[DIRECTIONS[sector]][action]
        var frame := 0 if action == "idle" else _frame_for_phase(clip, _render_phase(sector))
        var muzzle := to_global(_sprite_position_for(action, DIRECTIONS[sector], frame) + (_point(clip.muzzles[frame]) - _cell_size * 0.5) * _display_scale)
        var aim := (target - muzzle).normalized()
        if aim.length_squared() < 0.001: aim = fallback
        var error := absf(wrapf(aim.angle() - float(sector) * PI / 4.0, -PI, PI))
        reach = maxf(reach, muzzle.distance_to(actor.global_position))
        var row := {"aim":aim,"direction":sector,"error":error,"converges":true}
        if sector == actor.facing_sector: current = row
        if error < best_error:
            best_error = error
            best = row
    if target.distance_to(actor.global_position) > reach + 0.05:
        if not current.is_empty() and float(current.error) <= PI / 8.0 + 0.035: return current
        if best_error <= PI / 4.0: return best
    return {"aim":fallback,"direction":_sector_from_vector(fallback),"converges":false}


func is_runtime_active() -> bool:
    return _active


func _fail(reason: String) -> bool:
    _status = reason
    _active = false
    return false


func _deactivate(reason: String) -> void:
    _active = false
    _status = reason
    _moving = false
    if sprite:
        sprite.visible = false
    if visual:
        visual.restore_hidden_art()
        visual.modulate.a = _visual_alpha_before_activation


func debug_contract() -> Dictionary:
    return {
        "active": _active,
        "status": _status,
        "character_id": _character_id,
        "profile_path": _profile_path,
        "directions": _clips.size(),
        "display_height_px": _source_height * _display_scale,
        "display_scale": _display_scale,
        "atlas_scale": _atlas_scale,
        "ground_anchor_local": sprite.position + (_root - _cell_size * 0.5) * _display_scale if sprite else Vector2.INF,
        "action": _active_action,
        "sector": _active_sector,
        "direction": DIRECTIONS[_active_sector] if _active_sector >= 0 and _active_sector < DIRECTIONS.size() else "",
        "frame": _active_frame,
        "phase": _phase,
        "walk_cycle_distance": _walk_cycle_distance,
        "run_cycle_distance": _run_cycle_distance,
        "walk_registration_directions": _walk_registration.keys(),
        "registration_x": (sprite.position.x - _base_sprite_position.x) / _display_scale if sprite else 0.0,
        "muzzle_global": get_authored_muzzle_global_position() if _active else Vector2.INF,
        "whole_body_fire_policy": "shared_walk_or_idle_frame",
        "map_scale_policy": "129_6px_authored_subject_height_user_enlarged_20260911",
    }
