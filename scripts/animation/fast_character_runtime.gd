extends Node2D
class_name FastCharacterRuntime

## Reviewed authored_8x8 clips use independent move/aim selection and a
## distance-driven gait clock. Descriptors without a representation retain
## their legacy diagnostic playback; that is not production approval.

const FEATURE_SETTING := "sable_visuals/fast_character_runtime"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const MOVE_THRESHOLD := 12.0

var actor: OperatorActor
var visual: OperatorVisual
var sprite: Sprite2D

var _descriptor_path := ""
var _descriptor: Dictionary = {}
var _textures: Dictionary = {"idle": [], "move": [], "fire": []}
var _frame_counts: Dictionary = {"idle": 1, "move": 1, "fire": 1}
var _fps: Dictionary = {"idle": 4.0, "move": 12.0, "fire": 12.0}
var _muzzle_points: Array[Vector2] = []
# Schema 2 descriptors pin a muzzle socket for every state/frame, rather than
# projecting all shots from one direction-level approximation.  This is kept
# alongside the schema 1 scalar table so already-shipped character descriptors
# remain valid.
var _frame_muzzle_points: Dictionary = {"idle": [], "move": [], "fire": []}
var _descriptor_schema := 0
var _cell_size := 384.0
var _display_scale := 0.34
var _display_offset := Vector2(0.0, -49.0)
var _cursor := 0.0
var _fire_elapsed := -1.0
var _active_state := "idle"
var _active_sector := 0
var _active_frame := 0
var _active := false
var _activation_attempted := false
var _status := "not_attempted"
var _legacy_alpha := 1.0
# The MICA fast atlas contains twelve authored poses sampled into twenty-four
# UAL timing slots.  A repeated raster cell must not be allowed to advance the
# gameplay root for a second time: doing so makes a planted sole skate while
# the same pose is displayed.  The descriptor opts into a deterministic
# advance/hold cadence; other fast-runtime operators keep the legacy scale 1.
var _move_root_sync_enabled := false
var _move_root_samples_per_pose := 2
var _move_root_advance_scale := 1.0
var _move_root_hold_scale := 1.0
var _root_motion_scale := 1.0
# R21 adds a different, opt-in contract for authored 24 fps gait plates.  A
# shared velocity multiplier cannot keep a sole planted when the same raster
# cell is rendered for multiple high-rate samples.  The frame-transition track
# records the authored root position at each visible cell and emits movement
# only when that visible cell changes.  Existing descriptors stay on the
# scalar path above.
var _move_root_mode := "scalar"
var _move_root_tracks: Dictionary = {}
var _prepared_root_motion := Vector2.ZERO
var _prepared_root_motion_active := false
var _root_track_last_sector := -1
var _root_track_last_frame := -1
var _root_track_last_state := ""
# The native temporal capture is allowed to use a deterministic presentation
# clock.  Saving a 1920x1080 PNG can stall the headless render thread for
# longer than one wall-clock frame; deriving the atlas cursor from that stall
# would skip authored cells and invalidate the very gait cadence we are
# measuring.  Production runs leave this at 0 and use the physics delta.
var _capture_timeline_step := 0.0
var _combined_clips: Dictionary = {}
var _combined_kind := ""
var _combined_phase := 0.0
var _combined_moving := false
var _combined_running := false
var _combined_move_sector := 0
var _combined_key := ""
var _combined_muzzle := Vector2.ZERO
var _combined_texture_path := ""
var _combined_texture_cache: Dictionary = {}
var _combined_texture_lru: Array[String] = []


func _ready() -> void:
    process_priority = 146
    actor = get_parent() as OperatorActor
    visual = actor.get_node_or_null("VisualRoot") as OperatorVisual if actor else null
    sprite = Sprite2D.new()
    sprite.name = "FastCharacterAuthoredRaster"
    sprite.centered = true
    sprite.region_enabled = true
    sprite.region_filter_clip_enabled = true
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.z_index = 20
    sprite.visible = false
    if actor and actor.operator_id == "CHR_PROTO_02":
        # ROOK is an explicitly temporary squad slot, not a new approved build.
        var keyed := ShaderMaterial.new()
        keyed.shader = preload("res://assets/shaders/mockup_chroma.gdshader")
        sprite.material = keyed
    add_child(sprite)
    if actor and not actor.primary_fired.is_connected(_on_primary_fired):
        actor.primary_fired.connect(_on_primary_fired)
    if OS.get_environment("SABLE_RUNTIME_CAPTURE_MODE").strip_edges().to_lower() == "r21_60hz":
        _capture_timeline_step = 1.0 / 60.0
    call_deferred("_refresh_activation")


func _feature_enabled() -> bool:
    return bool(ProjectSettings.get_setting(FEATURE_SETTING, true))


func _motion_lab_active() -> bool:
    if actor == null:
        return false
    var runtime := actor.get_node_or_null("MotionLabCharacterRuntime")
    return runtime != null and runtime.has_method("is_runtime_active") and bool(runtime.call("is_runtime_active"))


func _process(delta: float) -> void:
    if actor == null:
        return
    if _motion_lab_active():
        if _active:
            _deactivate("superseded_by_motion_lab")
        _activation_attempted = true
        return
    if not _activation_attempted:
        _refresh_activation()
    if not _active:
        return
    if not _feature_enabled():
        _deactivate("feature_disabled")
        return

    if _combined_kind == "authored_8x8":
        # The real actor commits this clock after collision/bounds resolution.
        # A render stall or a shot must not advance/reset the lower-body phase.
        return

    # Frame-transition sole-lock candidates are advanced by OperatorActor
    # immediately before its physics displacement.  Updating here would make
    # the visible cell and root one physics tick out of phase.
    if _move_root_mode == "frame_transition_sole_lock":
        return

    var sector := posmod(actor.facing_sector, DIRECTIONS.size())
    if _fire_elapsed >= 0.0:
        _fire_elapsed += delta
        var fire_frame := mini(
            int(floor(_fire_elapsed * float(_fps["fire"]))),
            int(_frame_counts["fire"]) - 1
        )
        _show("fire", sector, fire_frame)
        if _fire_elapsed >= float(_frame_counts["fire"]) / float(_fps["fire"]):
            _fire_elapsed = -1.0
            _cursor = 0.0
        return

    var state := "move" if actor.velocity.length() > MOVE_THRESHOLD and not actor.is_downed() else "idle"
    _cursor = fposmod(_cursor + delta * float(_fps[state]), float(_frame_counts[state]))
    _show(state, sector, int(floor(_cursor)))


func _on_primary_fired(fired_actor: OperatorActor) -> void:
    if _active and fired_actor == actor:
        _fire_elapsed = 0.0
        if _combined_kind == "authored_8x8":
            _show_combined()
            return
        # The projectile is spawned synchronously after this signal.  Select
        # the same authored fire cell now, before returning control to the
        # actor, so the new frame-indexed socket and visible muzzle cannot be
        # one process tick out of sync.
        _show("fire", posmod(actor.facing_sector, DIRECTIONS.size()), 0)


func _refresh_activation() -> void:
    _activation_attempted = true
    if _motion_lab_active():
        if _active:
            _deactivate("superseded_by_motion_lab")
        _status = "superseded_by_motion_lab"
        return
    if actor == null or not _feature_enabled():
        _status = "disabled_or_missing_actor"
        return
    # Candidate captures may inject a project-local descriptor override at
    # process start.  It is deliberately opt-in and never changes the art
    # profile or the promoted runtime descriptor; this keeps R14 QA isolated
    # while exercising the real StoryStage/FastCharacterRuntime path.
    var descriptor_override := str(ProjectSettings.get_setting("sable_visuals/fast_character_runtime_descriptor_override", ""))
    if actor.operator_id == "CHR_PROTO_03" and not descriptor_override.is_empty():
        _descriptor_path = descriptor_override
    else:
        _descriptor_path = str(actor.art_profile.get("authored_runtime_descriptor", ""))
    if _descriptor_path.is_empty():
        _status = "profile_has_no_fast_descriptor"
        return
    if not _descriptor_path.begins_with("res://"):
        _descriptor_path = "res://" + _descriptor_path
    if not FileAccess.file_exists(_descriptor_path):
        _status = "descriptor_missing"
        push_error("FastCharacterRuntime missing descriptor: " + _descriptor_path)
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(_descriptor_path))
    if not (parsed is Dictionary):
        _status = "descriptor_parse_failed"
        push_error("FastCharacterRuntime invalid descriptor: " + _descriptor_path)
        return
    _descriptor = parsed as Dictionary
    if not _load_descriptor():
        return
    _legacy_alpha = visual.modulate.a if visual else 1.0
    if visual:
        visual.modulate.a = 0.0
    sprite.visible = true
    _active = true
    _status = "active"
    var legacy_raster := actor.get_node_or_null("AuthoredRasterPresentation")
    if legacy_raster != null and legacy_raster.has_method("deactivate_for_fast_runtime"):
        legacy_raster.call("deactivate_for_fast_runtime")
    _show("idle", 0, 0)


func _load_descriptor() -> bool:
    _descriptor_schema = int(_descriptor.get("schema", 0))
    if _descriptor_schema not in [1, 2]:
        return _fail_load("unsupported_schema")
    if str(_descriptor.get("actor_id", "")) != actor.operator_id:
        return _fail_load("actor_id_mismatch")

    _cell_size = float(_descriptor.get("cell_size", 384))
    _display_scale = float(_descriptor.get("display_scale", 0.34))
    var display_offset = _descriptor.get("display_offset", [0.0, -49.0])
    if not (display_offset is Array) or (display_offset as Array).size() != 2:
        return _fail_load("invalid_display_offset")
    _display_offset = Vector2(float(display_offset[0]), float(display_offset[1]))

    var root_sync = _descriptor.get("move_root_sync", {})
    if root_sync is Dictionary:
        _move_root_sync_enabled = bool((root_sync as Dictionary).get("enabled", false))
        _move_root_samples_per_pose = maxi(1, int((root_sync as Dictionary).get("samples_per_pose", 2)))
        _move_root_advance_scale = clampf(float((root_sync as Dictionary).get("advance_scale", 1.0)), 0.0, 2.0)
        _move_root_hold_scale = clampf(float((root_sync as Dictionary).get("hold_scale", 1.0)), 0.0, 2.0)
        _move_root_mode = str((root_sync as Dictionary).get("mode", "scalar"))
    else:
        _move_root_sync_enabled = false
        _move_root_samples_per_pose = 2
        _move_root_advance_scale = 1.0
        _move_root_hold_scale = 1.0
        _move_root_mode = "scalar"
    _root_motion_scale = 1.0
    _prepared_root_motion = Vector2.ZERO
    _prepared_root_motion_active = false
    _root_track_last_sector = -1
    _root_track_last_frame = -1
    _root_track_last_state = ""
    _move_root_tracks.clear()
    var states = _descriptor.get("states", {})
    var directions = _descriptor.get("directions", {})
    if not (states is Dictionary) or not (directions is Dictionary):
        return _fail_load("missing_states_or_directions")
    for state in ["idle", "move", "fire"]:
        var state_spec = (states as Dictionary).get(state, {})
        if not (state_spec is Dictionary):
            return _fail_load("invalid_state_" + state)
        _frame_counts[state] = maxi(1, int(state_spec.get("frames", 1)))
        _fps[state] = maxf(0.1, float(state_spec.get("fps", 1.0)))

    if _move_root_mode == "frame_transition_sole_lock":
        if not _move_root_sync_enabled:
            return _fail_load("sole_lock_mode_without_root_sync")
        var track_count := int((root_sync as Dictionary).get("frame_count", 0))
        var raw_tracks: Variant = (root_sync as Dictionary).get("directional_tracks", {})
        if track_count != int(_frame_counts.get("move", 0)) or not (raw_tracks is Dictionary):
            return _fail_load("invalid_sole_lock_track_header")
        for direction in DIRECTIONS:
            var raw_track: Variant = (raw_tracks as Dictionary).get(direction, {})
            if not (raw_track is Dictionary):
                return _fail_load("missing_sole_lock_track_" + direction)
            var raw_positions: Variant = (raw_track as Dictionary).get("frame_positions", [])
            if not (raw_positions is Array) or (raw_positions as Array).size() != track_count:
                return _fail_load("invalid_sole_lock_positions_" + direction)
            var positions: Array[float] = []
            for raw_position in raw_positions as Array:
                positions.append(float(raw_position))
            if positions.is_empty() or abs(positions[0]) > 0.001:
                return _fail_load("sole_lock_track_must_start_at_zero_" + direction)
            var cycle_advance := float((raw_track as Dictionary).get("cycle_advance", 0.0))
            if cycle_advance <= positions[-1]:
                return _fail_load("invalid_sole_lock_cycle_advance_" + direction)
            for frame_index in range(1, positions.size()):
                if positions[frame_index] <= positions[frame_index - 1]:
                    return _fail_load("non_monotonic_sole_lock_track_" + direction)
            _move_root_tracks[direction] = {
                "positions": positions,
                "cycle_advance": cycle_advance,
            }
    elif _move_root_mode != "scalar":
        return _fail_load("unsupported_move_root_mode")

    _textures = {"idle": [], "move": [], "fire": []}
    _muzzle_points.clear()
    _frame_muzzle_points = {"idle": [], "move": [], "fire": []}
    for direction in DIRECTIONS:
        var direction_spec = (directions as Dictionary).get(direction, {})
        if not (direction_spec is Dictionary):
            return _fail_load("missing_direction_" + direction)
        for state in ["idle", "move", "fire"]:
            var path := str((direction_spec as Dictionary).get(state + "_atlas", ""))
            if not path.begins_with("res://"):
                path = "res://" + path
            var texture := _load_runtime_texture(path)
            var expected := Vector2(_cell_size, _cell_size * int(_frame_counts[state]))
            if texture == null or texture.get_size() != expected:
                return _fail_load("invalid_%s_atlas_%s" % [state, direction])
            (_textures[state] as Array).append(texture)
            if _descriptor_schema == 2:
                var tracked_points := _parse_frame_muzzles(
                    (direction_spec as Dictionary).get(state + "_muzzle_xy", []),
                    int(_frame_counts[state])
                )
                if tracked_points.is_empty():
                    return _fail_load("invalid_%s_frame_muzzles_%s" % [state, direction])
                (_frame_muzzle_points[state] as Array).append(tracked_points)
        var muzzle = (direction_spec as Dictionary).get("muzzle_xy", [])
        if not (muzzle is Array) or (muzzle as Array).size() != 2:
            return _fail_load("invalid_muzzle_" + direction)
        _muzzle_points.append(Vector2(float(muzzle[0]), float(muzzle[1])))

    sprite.position = _display_offset
    sprite.scale = Vector2.ONE * _display_scale
    sprite.region_rect = Rect2(0.0, 0.0, _cell_size, _cell_size)
    if _descriptor.has("representation") and not _load_combined_representation():
        return false
    return true


func _clip_key(mode: String, move: String, aim: String, firing: bool) -> String:
    return "%s/%s/%s/%s" % [mode, move, aim, "fire" if firing else "travel"]


func _load_combined_representation() -> bool:
    var representation: Variant = _descriptor.get("representation")
    if not representation is Dictionary or representation.get("schema") != 1:
        return _fail_load("invalid_representation")
    # Do not silently fall back to the old full-body fire atlas for an
    # advertised but unimplemented representation.
    if representation.get("kind") != "authored_8x8" or _descriptor.get("aim_move_policy") != "authored_8x8":
        return _fail_load("unsupported_move_aim_representation")
    if _descriptor_schema != 2 or _move_root_sync_enabled:
        return _fail_load("combined_requires_schema2_actor_owned_displacement")
    var rows: Variant = representation.get("assets", [])
    if not rows is Array or rows.size() != 256:
        return _fail_load("incomplete_combined_coverage")
    var cadence: Dictionary = {}
    var inspected_paths: Dictionary = {}
    _combined_clips.clear()
    for row: Variant in rows:
        if not row is Dictionary or row.get("mode") not in ["walk", "run"] or row.get("move") not in DIRECTIONS or row.get("aim") not in DIRECTIONS or not row.get("firing") is bool:
            return _fail_load("invalid_combined_channel")
        var mode: String = row["mode"]
        var key := _clip_key(mode, row["move"], row["aim"], row["firing"])
        var frames := int(row.get("frames", 0))
        var fps := float(row.get("fps", 0))
        if _combined_clips.has(key) or int(row.get("cell_size", 0)) != int(_cell_size) or frames < 8 or frames > 512 or not is_finite(fps) or fps <= 0:
            return _fail_load("invalid_combined_timing_or_cell")
        var phase_starts: Array[float] = []
        var raw_phases: Variant = row.get("phase_starts", [])
        if row.has("phase_starts"):
            if not raw_phases is Array or raw_phases.size() != frames:
                return _fail_load("invalid_combined_phase_starts")
            for raw_phase: Variant in raw_phases:
                if not (raw_phase is float or raw_phase is int):
                    return _fail_load("invalid_combined_phase_starts")
                var phase_value := float(raw_phase)
                if not is_finite(phase_value) or phase_value < 0.0 or phase_value >= 1.0 or (not phase_starts.is_empty() and phase_value <= phase_starts[-1]):
                    return _fail_load("invalid_combined_phase_starts")
                phase_starts.append(phase_value)
            if phase_starts[0] != 0.0:
                return _fail_load("combined_phase_must_start_at_zero")
        else:
            for index in range(frames):
                phase_starts.append(float(index) / frames)
        var timing := {"frames": frames, "fps": fps, "phase_starts": phase_starts}
        if cadence.has(mode) and cadence[mode] != timing:
            return _fail_load("combined_phase_cadence_mismatch")
        cadence[mode] = timing
        var points := _parse_frame_muzzles(row.get("muzzle_xy", []), frames)
        if points.is_empty():
            return _fail_load("combined_frame_muzzles_required")
        for point in points:
            if not point.is_finite() or point.x < 0 or point.y < 0 or point.x >= _cell_size or point.y >= _cell_size:
                return _fail_load("combined_muzzle_out_of_cell")
        var path := str(row.get("path", ""))
        if not path.begins_with("res://"):
            path = "res://" + path
        if not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != row.get("sha256", ""):
            return _fail_load("stale_combined_atlas")
        if not inspected_paths.has(path):
            var image := Image.new()
            if image.load(ProjectSettings.globalize_path(path)) != OK:
                return _fail_load("invalid_combined_atlas")
            inspected_paths[path] = image.get_size()
        if inspected_paths[path] != Vector2i(int(_cell_size), int(_cell_size) * frames):
            return _fail_load("invalid_combined_atlas")
        _combined_clips[key] = {"path": path, "frames": frames, "fps": fps, "muzzles": points, "phase_starts": phase_starts}
    _combined_kind = "authored_8x8"
    return true


func set_motion_intent(move: Vector2, running: bool) -> void:
    if not _active or _combined_kind != "authored_8x8":
        return
    _combined_moving = move.length_squared() > 0.0001 and not actor.is_downed()
    _combined_running = running
    if _combined_moving:
        _combined_move_sector = _sector_from_vector(move)


func commit_actor_displacement(displacement: Vector2, delta: float) -> void:
    if not _active or _combined_kind != "authored_8x8":
        return
    if not _feature_enabled():
        _deactivate("feature_disabled")
        return
    if _fire_elapsed >= 0:
        _fire_elapsed += delta
        if _fire_elapsed >= float(_frame_counts["fire"]) / float(_fps["fire"]):
            _fire_elapsed = -1.0
    # Collision recovery can move the root by tiny alternating amounts even
    # while blocked. Use the existing presentation speed deadband (px/second),
    # not a per-frame position epsilon that changes with physics frequency.
    _combined_moving = delta > 0.0 and displacement.length() / delta > MOVE_THRESHOLD and not actor.is_downed()
    if _combined_moving:
        # Collision sliding chooses the observed travel direction, not the
        # requested wall normal. Intended velocity is not foot displacement.
        _combined_move_sector = _sector_from_vector(displacement.normalized())
        var mode := "run" if _combined_running else "walk"
        var clip: Dictionary = _combined_clips[_clip_key(mode, DIRECTIONS[_combined_move_sector], DIRECTIONS[_sector_from_vector(actor.aim_world)], false)]
        var base_speed: float = actor.run_speed if _combined_running else actor.walk_speed
        var cycle_distance := base_speed * float(clip["frames"]) / float(clip["fps"])
        _combined_phase = fposmod(_combined_phase + displacement.length() / cycle_distance, 1.0)
    else:
        _cursor = fposmod(_cursor + delta * float(_fps["idle"]), float(_frame_counts["idle"]))
    _show_combined()


func _show_combined() -> void:
    var aim := _sector_from_vector(actor.aim_world)
    if not _combined_moving:
        _combined_key = ""
        _combined_texture_path = ""
        if _fire_elapsed >= 0:
            _show("fire", aim, mini(int(_fire_elapsed * float(_fps["fire"])), int(_frame_counts["fire"]) - 1))
        else:
            _show("idle", aim, int(_cursor))
        return
    var mode := "run" if _combined_running else "walk"
    var firing := _fire_elapsed >= 0
    _combined_key = _clip_key(mode, DIRECTIONS[_combined_move_sector], DIRECTIONS[aim], firing)
    var clip: Dictionary = _combined_clips[_combined_key]
    _active_state = ("run" if _combined_running else "move") + ("_fire" if firing else "")
    _active_sector = aim
    # Contact/down/passing/flight may be authored at unequal phase intervals.
    # Every move/aim/fire channel shares these boundaries, so a shot or turn
    # changes the upper pose without restarting or retiming the lower body.
    _active_frame = 0
    var starts: Array = clip["phase_starts"]
    for index in range(1, starts.size()):
        if _combined_phase < float(starts[index]):
            break
        _active_frame = index
    _combined_muzzle = clip["muzzles"][_active_frame]
    _combined_texture_path = clip["path"]
    _root_motion_scale = 1.0
    # 256 native atlases must not all remain resident. Four recently used
    # channels cover travel/fire toggles and direction transitions.
    if not _combined_texture_cache.has(_combined_texture_path):
        var texture := _load_runtime_texture(_combined_texture_path)
        if texture == null:
            _deactivate("combined_atlas_unavailable_during_playback")
            return
        _combined_texture_cache[_combined_texture_path] = texture
    _combined_texture_lru.erase(_combined_texture_path)
    _combined_texture_lru.append(_combined_texture_path)
    while _combined_texture_lru.size() > 4:
        _combined_texture_cache.erase(_combined_texture_lru.pop_front())
    sprite.texture = _combined_texture_cache[_combined_texture_path]
    sprite.region_rect = Rect2(0, _active_frame * _cell_size, _cell_size, _cell_size)


func _parse_frame_muzzles(value: Variant, expected_count: int) -> Array[Vector2]:
    if not (value is Array) or (value as Array).size() != expected_count:
        return []
    var points: Array[Vector2] = []
    for point in value as Array:
        if not (point is Array) or (point as Array).size() != 2:
            return []
        points.append(Vector2(float(point[0]), float(point[1])))
    return points


func _load_runtime_texture(path: String) -> Texture2D:
    var image := Image.new()
    var error := image.load(ProjectSettings.globalize_path(path))
    if error != OK:
        return null
    return ImageTexture.create_from_image(image)


func _fail_load(reason: String) -> bool:
    _status = reason
    push_error("FastCharacterRuntime activation failed: " + reason)
    return false


func _show(state: String, sector: int, frame: int) -> void:
    var state_textures = _textures.get(state, []) as Array
    if state_textures.size() != DIRECTIONS.size():
        return
    _active_state = state
    _active_sector = posmod(sector, DIRECTIONS.size())
    _active_frame = posmod(frame, int(_frame_counts[state]))
    if state == "move" and _move_root_sync_enabled and _move_root_mode == "scalar":
        var pose_sample := _active_frame % _move_root_samples_per_pose
        _root_motion_scale = _move_root_advance_scale if pose_sample == 0 else _move_root_hold_scale
    elif state == "move" and _move_root_mode == "frame_transition_sole_lock":
        _root_motion_scale = 0.0
    else:
        _root_motion_scale = 1.0
    sprite.texture = state_textures[_active_sector] as Texture2D
    sprite.region_rect = Rect2(
        0.0,
        float(_active_frame) * _cell_size,
        _cell_size,
        _cell_size
    )


func _deactivate(reason: String) -> void:
    _active = false
    _status = reason
    if sprite:
        sprite.visible = false
    if visual and not _motion_lab_active():
        visual.modulate.a = _legacy_alpha


func deactivate_for_motion_lab() -> void:
    # The current Motion Studio source owns ASTER/MICA's full body.  Keep this
    # older candidate runtime available for historical diagnostics only.
    if _active:
        _deactivate("superseded_by_motion_lab")
    else:
        _status = "superseded_by_motion_lab"
    _activation_attempted = true


func is_runtime_active() -> bool:
    return _active


func get_root_motion_scale() -> float:
    """Return the root advance factor for the currently displayed state/frame.

    This is intentionally a presentation contract consumed by OperatorActor.
    For a two-sample hold, the first sample advances the actor at 2x and the
    second sample holds it at 0x, preserving average speed while keeping the
    duplicate raster pose planted in world space.  Fire, idle, and descriptors
    without the opt-in remain at 1x.
    """
    return _root_motion_scale if _active else 1.0


func prepare_root_motion(requested_velocity: Vector2, delta: float) -> bool:
    """Advance an opt-in R21 gait timeline before Actor physics movement.

    Returns true only when a sole-lock root track supplies the actual
    displacement.  Scalar/legacy runtimes retain the existing Actor-owned
    velocity path unchanged.
    """
    _prepared_root_motion = Vector2.ZERO
    _prepared_root_motion_active = false
    if not _active or _move_root_mode != "frame_transition_sole_lock":
        return false
    if not _feature_enabled():
        return false

    # Keep the authored 24fps cursor at the requested 60Hz review cadence
    # even when native PNG capture temporarily blocks the render thread.  The
    # actor still receives a displacement velocity divided by the real
    # physics delta below, so the world root follows the same track without
    # pretending the capture took less wall-clock time.
    var timeline_delta := _capture_timeline_step if _capture_timeline_step > 0.0 else delta

    if _fire_elapsed >= 0.0:
        _fire_elapsed += timeline_delta
        var fire_frame := mini(
            int(floor(_fire_elapsed * float(_fps["fire"]))),
            int(_frame_counts["fire"]) - 1
        )
        _show("fire", posmod(actor.facing_sector, DIRECTIONS.size()), fire_frame)
        _reset_root_track()
        if _fire_elapsed >= float(_frame_counts["fire"]) / float(_fps["fire"]):
            _fire_elapsed = -1.0
            _cursor = 0.0
        return false

    var moving := requested_velocity.length() > MOVE_THRESHOLD and not actor.is_downed()
    var state := "move" if moving else "idle"
    var sector := _sector_from_vector(requested_velocity) if moving else posmod(actor.facing_sector, DIRECTIONS.size())
    if state != _active_state:
        _cursor = 0.0
        _reset_root_track()
    _cursor = fposmod(_cursor + timeline_delta * float(_fps[state]), float(_frame_counts[state]))
    _show(state, sector, int(floor(_cursor)))
    if state != "move":
        _reset_root_track()
        return false

    var direction := DIRECTIONS[sector]
    var track := _move_root_tracks.get(direction, {}) as Dictionary
    var positions := track.get("positions", []) as Array
    if positions.size() != int(_frame_counts["move"]):
        _reset_root_track()
        return false
    var current_frame := _active_frame
    if _root_track_last_state != "move" or _root_track_last_sector != sector or _root_track_last_frame < 0:
        _root_track_last_state = "move"
        _root_track_last_sector = sector
        _root_track_last_frame = current_frame
        return true

    var delta_along := 0.0
    if current_frame > _root_track_last_frame:
        delta_along = float(positions[current_frame]) - float(positions[_root_track_last_frame])
    elif current_frame < _root_track_last_frame:
        delta_along = float(track.get("cycle_advance", 0.0)) - float(positions[_root_track_last_frame]) + float(positions[current_frame])
    # The same 24fps raster cell can occupy multiple 60Hz presentation ticks.
    # Keep that static cell's sole in world space instead of translating it.
    _root_track_last_frame = current_frame
    if delta_along < -0.0001:
        _reset_root_track()
        return false
    if requested_velocity.length() > 0.001:
        _prepared_root_motion = requested_velocity.normalized() * maxf(0.0, delta_along)
    _prepared_root_motion_active = true
    _root_motion_scale = _prepared_root_motion.length() / maxf(0.001, requested_velocity.length() * delta)
    return true


func get_prepared_root_motion_velocity(delta: float) -> Vector2:
    if not _prepared_root_motion_active or delta <= 0.000001:
        return Vector2.ZERO
    return _prepared_root_motion / delta


func _reset_root_track() -> void:
    _prepared_root_motion = Vector2.ZERO
    _prepared_root_motion_active = false
    _root_track_last_sector = -1
    _root_track_last_frame = -1
    _root_track_last_state = ""


func _sector_from_vector(vector: Vector2) -> int:
    if vector.length_squared() < 0.0001:
        return posmod(actor.facing_sector, DIRECTIONS.size()) if actor else 0
    return int(floor(fposmod(vector.angle() + PI / 8.0, TAU) / (PI / 4.0))) % DIRECTIONS.size()


func get_authored_muzzle_global_position() -> Vector2:
    if not _active or _muzzle_points.size() != DIRECTIONS.size():
        return global_position
    if not _combined_key.is_empty():
        return to_global(_display_offset + (_combined_muzzle - Vector2.ONE * (_cell_size * 0.5)) * _display_scale)
    var source_point := _muzzle_points[_active_sector]
    if _descriptor_schema == 2:
        var state_points := _frame_muzzle_points.get(_active_state, []) as Array
        if state_points.size() == DIRECTIONS.size():
            var direction_points := state_points[_active_sector] as Array
            if direction_points.size() == int(_frame_counts[_active_state]):
                source_point = direction_points[_active_frame] as Vector2
    var local_point := _display_offset + (source_point - Vector2.ONE * (_cell_size * 0.5)) * _display_scale
    return to_global(local_point)


func debug_contract() -> Dictionary:
    return {
        "active": _active,
        "status": _status,
        "descriptor": _descriptor_path,
        "descriptor_schema": _descriptor_schema,
        "actor_id": actor.operator_id if actor else "",
        "directions": DIRECTIONS.size(),
        "cell_size": _cell_size,
        "frame_counts": _frame_counts.duplicate(true),
        "frame_muzzle_tracking": _descriptor_schema == 2,
        "active_state": _active_state,
        "active_sector": _active_sector,
        "active_frame": _active_frame,
        "representation_kind": _combined_kind,
        "representation_channel": _combined_key,
        "representation_atlas": _combined_texture_path,
        "movement_sector": _combined_move_sector,
        "locomotion_phase": _combined_phase,
        "resident_combined_atlases": _combined_texture_cache.size(),
        "move_root_sync_enabled": _move_root_sync_enabled,
        "move_root_mode": _move_root_mode,
        "move_root_samples_per_pose": _move_root_samples_per_pose,
        "root_motion_scale": _root_motion_scale,
        "prepared_root_motion": [_prepared_root_motion.x, _prepared_root_motion.y],
        "prepared_root_motion_active": _prepared_root_motion_active,
        "root_track_last_sector": _root_track_last_sector,
        "root_track_last_frame": _root_track_last_frame,
    }
