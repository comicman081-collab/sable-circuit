extends Node2D
class_name AsterV4LocomotionPreview

## Preview-gated ASTER authored sprite playback.
##
## This node is presentation-only. It never writes velocity, facing, collision,
## weapon timing, damage, or save data. Disable instantly through
## `sable_visuals/aster_v4_locomotion_preview` in project.godot.

const FEATURE_SETTING := "sable_visuals/aster_v4_locomotion_preview"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
## Lower-body locomotion and upper-body aim intentionally have independent
## direction schemas.  Both use the authored eight-way set today; upper
## selection is count-driven so a future sixteen-way upper set does not need
## to change locomotion-sector ownership.
const LOWER_DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const UPPER_DIRECTIONS_8: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const UPPER_DIRECTIONS_16: Array[String] = [
    "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW", "N", "NNE", "NE", "ENE",
]
const DIRECTION_HYSTERESIS_DEGREES := 4.0
const LOCOMOTION_SPEED_THRESHOLD := 12.0
const MOVE_AIM_READY_UPPER_FRAME := 0
const IDLE_FRAME_COUNT := 4
const MOVE_V6_FRAME_COUNT := 24
const MOVE_V5_FRAME_COUNT := 24
const MOVE_V4_FRAME_COUNT := 12
const FIRE_FRAME_COUNT := 6
const FIRE_FRAME_LABELS: Array[String] = [
    "aim", "preload", "recoil_contact_clean", "recover_early_clean", "recover", "ready_return",
]
const CELL_SIZE := 384.0
const IDLE_FPS := 4.0
const MOVE_V6_FPS := 24.0
const MOVE_V5_FPS := 24.0
const MOVE_V4_FPS := 12.0
const FIRE_FPS := 12.0
const FIRE_CONTACT_FRAME := 2
const DISPLAY_SCALE := 0.34
const DISPLAY_OFFSET := Vector2(0.0, -49.0)
const MUZZLE_FLASH_SIZE := Vector2(164.0, 135.0)
const MUZZLE_FLASH_ANCHOR := Vector2(38.0, 60.0)
const MUZZLE_FLASH_DURATION := 0.06
const MUZZLE_ALIGNMENT_PATH := "res://assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json"
const TORSO_SOCKET_PATH := "res://assets/units/operators/aster/ASTER_TORSO_SOCKET_V1.json"
const TORSO_BRIDGE_MANIFEST_PATH := "res://assets/units/operators/aster/torso_bridge_v1/ASTER_TORSO_BRIDGE_V1_MANIFEST.json"
const COMPOSITE_V6_MANIFEST_PATH := "res://assets/units/operators/aster/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"
const UPPER_16_ROOT := "res://assets/units/operators/aster/fire_upper_16_no_shoulder_v2"
const UPPER_16_CANDIDATE_ID := "fire_upper_16_no_shoulder_v2"
const UPPER_16_MANIFEST_PATH := UPPER_16_ROOT + "/ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_MANIFEST.json"
const UPPER_16_MUZZLE_ALIGNMENT_PATH := UPPER_16_ROOT + "/ASTER_MUZZLE_ALIGNMENT_16_NO_SHOULDER_V2.json"
const TORSO_SOCKET_16_PATH := "res://assets/units/operators/aster/ASTER_TORSO_SOCKET_16_NO_SHOULDER_V4.json"

var actor: OperatorActor
var visual: OperatorVisual
var primary: Sprite2D
var blend: Sprite2D
var torso_bridge: Sprite2D
var fire_upper: Sprite2D
var muzzle_flash: Sprite2D
var _idle_textures: Array[Texture2D] = []
var _move_textures: Array[Texture2D] = []
var _fire_textures: Array[Texture2D] = []
var _idle_lower_textures: Array[Texture2D] = []
var _move_lower_textures: Array[Texture2D] = []
var _fire_upper_textures: Array[Texture2D] = []
var _torso_bridge_textures: Array[Texture2D] = []
var _active_upper_directions: Array[String] = UPPER_DIRECTIONS_8.duplicate()
var _upper_offsets_source_px: Dictionary = {}
var _upper_offsets_are_per_frame := false
var _torso_socket_loaded := false
var _torso_bridge_loaded := false
var _independent_aim_composite_valid := false
var _independent_aim_failure_reason := "not_loaded"
var _upper_presentation_offset_runtime := Vector2.ZERO
var _move_aim_ready_upper_active := false
var _muzzle_texture: Texture2D
var _muzzle_source_points: Array[Vector2] = []
var _barrel_tangent_radians: Array[float] = []
var _muzzle_alignment_loaded := false
var _active_torso_socket_path := TORSO_SOCKET_PATH
var _active_muzzle_alignment_path := MUZZLE_ALIGNMENT_PATH
var _upper_runtime_asset_family := "not_loaded"
var _upper_pair_qa := "HOLD"
var _upper16_candidate_detected := false
var _upper16_promoted := false
var _upper16_failure_reason := "not_evaluated"
var _active := false
var _activation_attempted := false
var _status := "not_attempted"
# `_sector` remains the compatibility alias exposed to the existing capture
# harnesses.  It always mirrors `_upper_sector`; locomotion reads only
# `_lower_sector`.
var _sector := -1
var _upper_sector := -1
var _lower_sector := -1
var _idle_cursor := 0.0
var _move_cursor := 0.0
var _move_frame_count := MOVE_V5_FRAME_COUNT
var _move_fps := MOVE_V5_FPS
var _move_runtime_asset_family := "not_loaded"
var _composite_runtime_asset_family := "not_loaded"
var _move_fallback_reason := ""
var _move_cadence_scale := 0.0
var _move_phase_advance_total := 0.0
var _split_fire_set_valid := false
var _split_fire_failure_reason := "not_loaded"
var _fire_elapsed := -1.0
var _muzzle_flash_remaining := 0.0
var _muzzle_flash_trigger_count := 0
var _muzzle_flash_shot_sector := 0
var _muzzle_flash_shot_direction := Vector2.RIGHT
var _muzzle_flash_shot_local := Vector2.ZERO
var _muzzle_flash_barrel_residual_radians := 0.0
var _previous_recoil := 0.0
var _completed_move_loops := 0
var _last_frame := 0
var _fire_event_count := 0
var _moving_fire_active := false
var _moving_fire_move_advance_count := 0
var _moving_fire_cursor_before := 0.0
var _moving_fire_cursor_after := 0.0
var _lower_body_atlas_selected := "none"
var _legacy_was_visible := true
var _visual_alpha_before_activation := 1.0
var _playback_state := "idle"


func _ready() -> void:
    process_priority = 145
    actor = get_parent() as OperatorActor
    visual = actor.get_node_or_null("VisualRoot") as OperatorVisual if actor else null
    if actor and not actor.primary_fired.is_connected(_on_primary_fired):
        actor.primary_fired.connect(_on_primary_fired)
    primary = _make_sprite("AsterV4Primary", 20)
    blend = _make_sprite("AsterV4Blend", 21)
    torso_bridge = _make_sprite("AsterTorsoBridgeV1", 21)
    fire_upper = _make_sprite("AsterV5FireUpper", 22)
    muzzle_flash = _make_muzzle_sprite()
    primary.visible = false
    blend.visible = false
    torso_bridge.visible = false
    fire_upper.visible = false
    muzzle_flash.visible = false
    call_deferred("_refresh_activation")


func _make_sprite(node_name: String, z: int) -> Sprite2D:
    var result := Sprite2D.new()
    result.name = node_name
    result.centered = true
    result.region_enabled = true
    result.region_rect = Rect2(0.0, 0.0, CELL_SIZE, CELL_SIZE)
    result.position = DISPLAY_OFFSET
    result.scale = Vector2.ONE * DISPLAY_SCALE
    result.z_index = z
    # Atlas mipmaps can bleed neighboring 384px cells into the active region.
    result.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    result.region_filter_clip_enabled = true
    add_child(result)
    return result


func _make_muzzle_sprite() -> Sprite2D:
    var result := Sprite2D.new()
    result.name = "AsterV4RuntimeMuzzleFlash"
    result.centered = false
    result.offset = -MUZZLE_FLASH_ANCHOR
    result.scale = Vector2.ONE * DISPLAY_SCALE
    result.z_index = 24
    result.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    add_child(result)
    return result


func _feature_enabled() -> bool:
    return bool(ProjectSettings.get_setting(FEATURE_SETTING, false))


func _on_primary_fired(fired_actor: OperatorActor) -> void:
    if fired_actor != actor or not _active:
        return
    # The gameplay shot has already happened when this signal arrives, so the
    # raster fire sequence begins on its authored contact pose rather than
    # playing two pre-fire frames after the projectile has left the weapon.
    _fire_elapsed = float(FIRE_CONTACT_FRAME) / FIRE_FPS
    _fire_event_count += 1
    _begin_muzzle_flash()


func is_runtime_active() -> bool:
    return _active


func _motion_lab_active() -> bool:
    if actor == null:
        return false
    var runtime := actor.get_node_or_null("MotionLabCharacterRuntime")
    return runtime != null and runtime.has_method("is_runtime_active") and bool(runtime.call("is_runtime_active"))


func _motion_lab_pending() -> bool:
    if actor == null:
        return false
    var runtime := actor.get_node_or_null("MotionLabCharacterRuntime")
    return runtime != null and runtime.has_method("activation_pending") and bool(runtime.call("activation_pending"))


func deactivate_for_motion_lab() -> void:
    # Motion Studio is the current ASTER body authority.  Preserve this older
    # preview node and its provenance, but never let it draw a second body.
    if _active:
        _deactivate("superseded_by_motion_lab")
    else:
        _status = "superseded_by_motion_lab"
    _activation_attempted = true
    _release_superseded_textures()


# The superseded atlases were ~0.6 GB of hidden VRAM on native builds. The
# files are untouched; _load_textures() rebuilds every array if Motion Studio
# ever stops owning the body.
func _release_superseded_textures() -> void:
    for textures: Array[Texture2D] in [_idle_textures, _move_textures, _fire_textures, _idle_lower_textures, _move_lower_textures, _fire_upper_textures, _torso_bridge_textures]:
        textures.clear()
    for sprite: Sprite2D in [primary, blend, torso_bridge, fire_upper]:
        if sprite:
            sprite.texture = null


func get_authored_muzzle_local_position() -> Vector2:
    var authored_sector := _muzzle_sector_for_upper(_upper_sector if _upper_sector >= 0 else maxi(_sector, 0))
    if _muzzle_source_points.size() != _active_upper_directions.size():
        return DISPLAY_OFFSET
    # Alignment points are measured directly in the authoritative 384px Fire
    # V4 contact cell.  Sprite2D is centred on that cell, so convert the point
    # to a centre-relative runtime offset instead of reusing the former weapon-
    # corridor endpoints that sat visibly inside the barrel.
    var cell_centre := Vector2.ONE * (CELL_SIZE * 0.5)
    return (
        DISPLAY_OFFSET
        + (_muzzle_source_points[authored_sector] - cell_centre) * DISPLAY_SCALE
        + _muzzle_upper_presentation_offset()
    )


func get_authored_muzzle_global_position() -> Vector2:
    return to_global(get_authored_muzzle_local_position())


func get_authored_barrel_tangent(sector: int = -1) -> Vector2:
    var resolved_sector := posmod(sector, _active_upper_directions.size()) if sector >= 0 else _muzzle_sector_for_upper(_upper_sector if _upper_sector >= 0 else maxi(_sector, 0))
    if _barrel_tangent_radians.size() != _active_upper_directions.size():
        return Vector2.from_angle(float(resolved_sector) * TAU / float(_active_upper_directions.size()))
    return Vector2.from_angle(_barrel_tangent_radians[resolved_sector])


func _muzzle_sector_for_upper(upper_sector: int) -> int:
    return posmod(upper_sector, _active_upper_directions.size())


func _process(delta: float) -> void:
    if actor == null:
        return
    if _motion_lab_active():
        if _active:
            _deactivate("superseded_by_motion_lab")
            _release_superseded_textures()
        _activation_attempted = true
        return
    if _status == "superseded_by_motion_lab":
        _activation_attempted = false
    var should_run := _feature_enabled() and actor.operator_id == "CHR_PROTO_01"
    if should_run and not _active and not _activation_attempted:
        _refresh_activation()
    elif not should_run and (_active or _activation_attempted):
        _deactivate("disabled_or_non_aster")
        _activation_attempted = false
    if not _active:
        return

    _sync_sector()
    _update_muzzle_flash(delta)
    var recoil := float(visual.get("_recoil")) if visual else 0.0
    if recoil >= 0.78 and _previous_recoil < 0.78 and _fire_elapsed < 0.0:
        # Legacy fallback for a recoil source that did not emit primary_fired.
        # It still starts at contact so presentation never trails the shot.
        _fire_elapsed = float(FIRE_CONTACT_FRAME) / FIRE_FPS
    _previous_recoil = recoil
    if _fire_elapsed >= 0.0:
        _fire_elapsed += delta
        var fire_frame := mini(int(floor(_fire_elapsed * FIRE_FPS)), FIRE_FRAME_COUNT - 1)
        var moving_fire := actor.velocity.length() > LOCOMOTION_SPEED_THRESHOLD and not actor.is_downed()
        _moving_fire_active = moving_fire
        if moving_fire:
            _playback_state = "moving_fire"
            _advance_move(delta, true)
            if _independent_aim_composite_valid:
                _show_composite_fire_frame(fire_frame, true)
            else:
                # A missing split set must never fall back to the static
                # full-body fire pose while the actor is moving.  Preserve the
                # advancing locomotion body and runtime muzzle until the
                # authored upper overlay is available.
                _show_move_frame(int(floor(_move_cursor)))
                _show_muzzle_frame(fire_frame)
                _last_frame = fire_frame
        elif _split_fire_set_valid:
            _playback_state = "stationary_fire"
            _idle_cursor = fposmod(_idle_cursor + delta * IDLE_FPS, float(IDLE_FRAME_COUNT))
            _show_composite_fire_frame(fire_frame, false)
        else:
            _playback_state = "fire"
            _lower_body_atlas_selected = "fire_360_clean_v4_full_body"
            _show_fire_frame(fire_frame)
        if _fire_elapsed >= float(FIRE_FRAME_COUNT) / FIRE_FPS:
            _fire_elapsed = -1.0
        return

    _moving_fire_active = false
    var moving := actor.velocity.length() > LOCOMOTION_SPEED_THRESHOLD and not actor.is_downed()
    if moving:
        if _playback_state not in ["move", "moving_fire"]:
            _move_cursor = 0.0
        _playback_state = "move"
        _advance_move(delta, false)
        _show_move_frame(int(floor(_move_cursor)))
    else:
        _move_cadence_scale = 0.0
        if _playback_state != "idle":
            _idle_cursor = 0.0
        _playback_state = "idle"
        _idle_cursor = fposmod(_idle_cursor + delta * IDLE_FPS, float(IDLE_FRAME_COUNT))
        _lower_body_atlas_selected = "idle_360_clean_v5"
        _show_idle_frame(int(floor(_idle_cursor)))


func _advance_move(delta: float, during_fire: bool) -> void:
    var before := _move_cursor
    # Match the UAL gait cadence to actual ground speed.  Walking remains the
    # authored 1.0x reference; analog movement slows the cycle and sprint/run
    # speeds it up, preventing one fixed foot cycle from skating at every speed.
    var reference_speed := maxf(actor.walk_speed * actor.run_speed_multiplier, 1.0)
    _move_cadence_scale = clampf(actor.velocity.length() / reference_speed, 0.08, 1.65)
    var phase_advance := delta * _move_fps * _move_cadence_scale
    _move_cursor = fposmod(_move_cursor + phase_advance, float(_move_frame_count))
    _move_phase_advance_total += phase_advance
    if _move_cursor < before:
        _completed_move_loops += 1
    if during_fire:
        _moving_fire_cursor_before = before
        _moving_fire_cursor_after = _move_cursor
        _moving_fire_move_advance_count += 1


func _refresh_activation() -> void:
    if _motion_lab_active():
        if _active:
            _deactivate("superseded_by_motion_lab")
        _status = "superseded_by_motion_lab"
        _activation_attempted = true
        _release_superseded_textures()
        return
    # Motion Studio decides on its own deferred call. Leave _activation_attempted
    # unset so _process() retries next frame rather than decoding atlases that
    # would be hidden immediately.
    if _motion_lab_pending():
        return
    if actor == null or not _feature_enabled() or actor.operator_id != "CHR_PROTO_01":
        return
    _activation_attempted = true
    if not _load_textures():
        _deactivate(_status)
        return
    _active = true
    _status = "preview_loaded"
    var legacy := actor.get_node_or_null("AuthoredRasterPresentation") as CanvasItem
    if legacy:
        _legacy_was_visible = legacy.visible
        legacy.visible = false
    if visual:
        _visual_alpha_before_activation = visual.modulate.a
        visual.modulate.a = 0.0
    primary.visible = true
    blend.visible = false
    torso_bridge.visible = false
    fire_upper.visible = false
    _sync_sector(true)
    _playback_state = "idle"
    _idle_cursor = 0.0
    _show_idle_frame(0)


func _load_textures() -> bool:
    _idle_textures.clear()
    _move_textures.clear()
    _fire_textures.clear()
    _idle_lower_textures.clear()
    _move_lower_textures.clear()
    _fire_upper_textures.clear()
    _torso_bridge_textures.clear()
    _upper_offsets_source_px.clear()
    _active_upper_directions = UPPER_DIRECTIONS_8.duplicate()
    _upper_offsets_are_per_frame = false
    _torso_socket_loaded = false
    _torso_bridge_loaded = false
    _independent_aim_composite_valid = false
    _independent_aim_failure_reason = "not_loaded"
    _move_runtime_asset_family = "not_loaded"
    _composite_runtime_asset_family = "not_loaded"
    _split_fire_set_valid = false
    _split_fire_failure_reason = "not_loaded"
    _move_fallback_reason = ""
    _active_torso_socket_path = TORSO_SOCKET_PATH
    _active_muzzle_alignment_path = MUZZLE_ALIGNMENT_PATH
    _upper_runtime_asset_family = "not_loaded"
    _upper_pair_qa = "HOLD"
    _upper16_candidate_detected = FileAccess.file_exists(UPPER_16_MANIFEST_PATH)
    _upper16_promoted = false
    _upper16_failure_reason = "not_evaluated"
    _muzzle_alignment_loaded = false
    _muzzle_source_points.clear()
    _barrel_tangent_radians.clear()
    if not _load_muzzle_alignment():
        return false

    # V6 is promoted only as one complete locomotion + moving-fire bundle.  A
    # partial V6 export must never mix with V5 lower/upper layers because that
    # would reintroduce leg freezes, costume swaps, and one-frame silhouettes
    # at direction boundaries.
    var v6_move_textures: Array[Texture2D] = []
    var v6_idle_lower_textures: Array[Texture2D] = []
    var v6_move_lower_textures: Array[Texture2D] = []
    var v6_fire_upper_textures: Array[Texture2D] = []
    for direction in LOWER_DIRECTIONS:
        var v6_path := "res://assets/units/operators/aster/move_360_ual_v6/%s/ASTER_MOVE_%s_360_UAL_V6_ATLAS.webp" % [direction, direction]
        var v6_idle_lower_path := "res://assets/units/operators/aster/composite_fire_v6/idle_lower/%s/ASTER_IDLE_%s_LOWER_V6_ATLAS.webp" % [direction, direction]
        var v6_move_lower_path := "res://assets/units/operators/aster/composite_fire_v6/move_lower/%s/ASTER_MOVE_%s_LOWER_V6_ATLAS.webp" % [direction, direction]
        var v6_texture := _load_runtime_texture(v6_path)
        var v6_idle_lower := _load_runtime_texture(v6_idle_lower_path)
        var v6_move_lower := _load_runtime_texture(v6_move_lower_path)
        if (
            v6_texture == null
            or v6_texture.get_size() != Vector2(CELL_SIZE, CELL_SIZE * MOVE_V6_FRAME_COUNT)
            or v6_idle_lower == null
            or v6_idle_lower.get_size() != Vector2(CELL_SIZE, CELL_SIZE * IDLE_FRAME_COUNT)
            or v6_move_lower == null
            or v6_move_lower.get_size() != Vector2(CELL_SIZE, CELL_SIZE * MOVE_V6_FRAME_COUNT)
        ):
            v6_move_textures.clear()
            v6_idle_lower_textures.clear()
            v6_move_lower_textures.clear()
            _move_fallback_reason = "v6_bundle_missing_or_invalid_at_" + direction
            break
        v6_move_textures.append(v6_texture)
        v6_idle_lower_textures.append(v6_idle_lower)
        v6_move_lower_textures.append(v6_move_lower)

    for direction in UPPER_DIRECTIONS_8:
        var v6_fire_upper_path := "res://assets/units/operators/aster/composite_fire_v6/fire_upper/%s/ASTER_FIRE_%s_UPPER_V6_ATLAS.webp" % [direction, direction]
        var v6_fire_upper := _load_runtime_texture(v6_fire_upper_path)
        if v6_fire_upper == null or v6_fire_upper.get_size() != Vector2(CELL_SIZE, CELL_SIZE * FIRE_FRAME_COUNT):
            v6_fire_upper_textures.clear()
            _move_fallback_reason = "v6_bundle_missing_or_invalid_upper_at_" + direction
            break
        v6_fire_upper_textures.append(v6_fire_upper)

    if (
        v6_move_textures.size() == LOWER_DIRECTIONS.size()
        and v6_idle_lower_textures.size() == LOWER_DIRECTIONS.size()
        and v6_move_lower_textures.size() == LOWER_DIRECTIONS.size()
        and v6_fire_upper_textures.size() == UPPER_DIRECTIONS_8.size()
    ):
        _move_textures.append_array(v6_move_textures)
        _idle_lower_textures.append_array(v6_idle_lower_textures)
        _move_lower_textures.append_array(v6_move_lower_textures)
        _fire_upper_textures.append_array(v6_fire_upper_textures)
        _move_frame_count = MOVE_V6_FRAME_COUNT
        _move_fps = MOVE_V6_FPS
        _move_runtime_asset_family = "move_360_ual_v6"
        _composite_runtime_asset_family = "composite_fire_v6"
        _upper_runtime_asset_family = "composite_fire_v6/fire_upper"
        _split_fire_set_valid = true
        _split_fire_failure_reason = ""
        _move_fallback_reason = ""

    # V5 remains the complete rollback family.  Never mix V5 and V4
    # directions in one loop: partial atlas sets create visible timing and
    # silhouette discontinuities whenever aim changes.
    var v5_move_textures: Array[Texture2D] = []
    if _move_textures.is_empty():
        for direction in LOWER_DIRECTIONS:
            var v5_path := "res://assets/units/operators/aster/move_360_ual_v5/%s/ASTER_MOVE_%s_360_UAL_V5_ATLAS.webp" % [direction, direction]
            var v5_texture := _load_runtime_texture(v5_path)
            if v5_texture == null or v5_texture.get_size() != Vector2(CELL_SIZE, CELL_SIZE * MOVE_V5_FRAME_COUNT):
                v5_move_textures.clear()
                _move_fallback_reason += ";v5_set_missing_or_invalid_at_" + direction
                break
            v5_move_textures.append(v5_texture)

    if _move_textures.is_empty() and v5_move_textures.size() == LOWER_DIRECTIONS.size():
        _move_textures.append_array(v5_move_textures)
        _move_frame_count = MOVE_V5_FRAME_COUNT
        _move_fps = MOVE_V5_FPS
        _move_runtime_asset_family = "move_360_ual_v5"
        _move_fallback_reason = ""
    elif _move_textures.is_empty():
        for direction in LOWER_DIRECTIONS:
            var v4_path := "res://assets/units/operators/aster/move_360_interpolated_v4/%s/ASTER_MOVE_%s_360_INTERPOLATED_V4_ATLAS.webp" % [direction, direction]
            var v4_texture := _load_runtime_texture(v4_path)
            if v4_texture == null or v4_texture.get_size() != Vector2(CELL_SIZE, CELL_SIZE * MOVE_V4_FRAME_COUNT):
                _status = "invalid_move_fallback_atlas_" + direction
                return false
            _move_textures.append(v4_texture)
        _move_frame_count = MOVE_V4_FRAME_COUNT
        _move_fps = MOVE_V4_FPS
        _move_runtime_asset_family = "move_360_interpolated_v4_fallback"

    for direction in UPPER_DIRECTIONS_8:
        var idle_path := "res://assets/units/operators/aster/idle_360_clean_v5/%s/ASTER_IDLE_%s_CLEAN_V5_ATLAS.webp" % [direction, direction]
        var fire_path := "res://assets/units/operators/aster/fire_360_clean_v4/ASTER_FIRE_%s_CLEAN_RGBA.webp" % direction
        var idle_texture := _load_runtime_texture(idle_path)
        var fire_texture := _load_runtime_texture(fire_path)
        if idle_texture == null or idle_texture.get_size() != Vector2(CELL_SIZE, CELL_SIZE * IDLE_FRAME_COUNT):
            _status = "invalid_idle_atlas_" + direction
            return false
        if fire_texture == null or fire_texture.get_size() != Vector2(CELL_SIZE, CELL_SIZE * FIRE_FRAME_COUNT):
            _status = "invalid_fire_atlas_" + direction
            return false
        _idle_textures.append(idle_texture)
        _fire_textures.append(fire_texture)

    # V5 moving-fire composition is only considered when V6 did not already
    # promote its complete bundle.  Partial split sets stay invisible.
    var staged_idle_lower: Array[Texture2D] = []
    var staged_move_lower: Array[Texture2D] = []
    var staged_fire_upper: Array[Texture2D] = []
    if _move_runtime_asset_family == "move_360_ual_v5":
        _split_fire_failure_reason = ""
        for direction in LOWER_DIRECTIONS:
            var idle_lower_path := "res://assets/units/operators/aster/composite_fire_v5/idle_lower/%s/ASTER_IDLE_%s_LOWER_V5_ATLAS.webp" % [direction, direction]
            var move_lower_path := "res://assets/units/operators/aster/composite_fire_v5/move_lower/%s/ASTER_MOVE_%s_LOWER_V5_ATLAS.webp" % [direction, direction]
            var idle_lower := _load_runtime_texture(idle_lower_path)
            var move_lower := _load_runtime_texture(move_lower_path)
            if idle_lower == null or idle_lower.get_size() != Vector2(CELL_SIZE, CELL_SIZE * IDLE_FRAME_COUNT):
                _split_fire_failure_reason = "invalid_idle_lower_at_" + direction
                break
            if move_lower == null or move_lower.get_size() != Vector2(CELL_SIZE, CELL_SIZE * MOVE_V5_FRAME_COUNT):
                _split_fire_failure_reason = "invalid_move_lower_at_" + direction
                break
            staged_idle_lower.append(idle_lower)
            staged_move_lower.append(move_lower)

        for direction in UPPER_DIRECTIONS_8:
            var fire_upper_path := "res://assets/units/operators/aster/composite_fire_v5/fire_upper/%s/ASTER_FIRE_%s_UPPER_V5_ATLAS.webp" % [direction, direction]
            var upper := _load_runtime_texture(fire_upper_path)
            if upper == null or upper.get_size() != Vector2(CELL_SIZE, CELL_SIZE * FIRE_FRAME_COUNT):
                _split_fire_failure_reason = "invalid_fire_upper_at_" + direction
                break
            staged_fire_upper.append(upper)

        _split_fire_set_valid = (
            staged_idle_lower.size() == LOWER_DIRECTIONS.size()
            and staged_move_lower.size() == LOWER_DIRECTIONS.size()
            and staged_fire_upper.size() == UPPER_DIRECTIONS_8.size()
        )
        if _split_fire_set_valid:
            _idle_lower_textures.append_array(staged_idle_lower)
            _move_lower_textures.append_array(staged_move_lower)
            _fire_upper_textures.append_array(staged_fire_upper)
            _composite_runtime_asset_family = "composite_fire_v5"
            _upper_runtime_asset_family = "composite_fire_v5/fire_upper"
            _split_fire_failure_reason = ""
    elif _move_runtime_asset_family != "move_360_ual_v6":
        _split_fire_set_valid = false
        _composite_runtime_asset_family = "not_loaded"
        _split_fire_failure_reason = "authored_ual_bundle_not_selected"

    # Cross-direction lower/upper composition is a stricter promotion than the
    # same-direction split-fire set.  It becomes visible only when the 64-pair
    # torso-socket QA contract and every lower-phase bridge atlas validate as
    # one bundle.  The ordinary full-body locomotion remains a safe fallback.
    if _move_runtime_asset_family == "move_360_ual_v6" and _split_fire_set_valid:
        _load_independent_aim_composition_bundle()
        # The 16-way upper is staged and committed only after its own visual,
        # technical, hash, muzzle and 8x16 socket contracts all pass.  A single
        # failure leaves every active pointer on the coherent eight-way V6
        # fallback; no partial 8/16 combination can escape this function.
        _try_promote_upper16_bundle()
    else:
        _independent_aim_failure_reason = "requires_complete_v6_split_bundle"

    _muzzle_texture = _load_runtime_texture("res://assets/units/operators/aster/vfx/ASTER_MUZZLE_FLASH_E_V2_RGBA.webp")
    if _muzzle_texture == null or _muzzle_texture.get_size() != MUZZLE_FLASH_SIZE:
        _status = "invalid_runtime_muzzle_vfx"
        return false
    muzzle_flash.texture = _muzzle_texture
    return true


func _load_independent_aim_composition_bundle() -> bool:
    _torso_socket_loaded = false
    _torso_bridge_loaded = false
    _independent_aim_composite_valid = false
    _independent_aim_failure_reason = "not_loaded"
    _torso_bridge_textures.clear()
    _upper_offsets_source_px.clear()

    var socket_payload := _read_json_dictionary(TORSO_SOCKET_PATH)
    if socket_payload.is_empty():
        _independent_aim_failure_reason = "missing_or_invalid_torso_socket_v1"
        return false
    var lower_contract: Array = socket_payload.get("lower_directions", [])
    var upper_contract: Array = socket_payload.get("upper_directions", [])
    if (
        int(socket_payload.get("schema", 0)) != 1
        or not is_equal_approx(float(socket_payload.get("display_scale", -1.0)), DISPLAY_SCALE)
        or lower_contract.size() != LOWER_DIRECTIONS.size()
        or upper_contract.size() != UPPER_DIRECTIONS_8.size()
    ):
        _independent_aim_failure_reason = "invalid_torso_socket_v1_header"
        return false
    for index in range(LOWER_DIRECTIONS.size()):
        if str(lower_contract[index]) != LOWER_DIRECTIONS[index]:
            _independent_aim_failure_reason = "invalid_torso_socket_lower_direction_" + LOWER_DIRECTIONS[index]
            return false
    for index in range(UPPER_DIRECTIONS_8.size()):
        if str(upper_contract[index]) != UPPER_DIRECTIONS_8[index]:
            _independent_aim_failure_reason = "invalid_torso_socket_upper_direction_" + UPPER_DIRECTIONS_8[index]
            return false

    var socket_qa: Dictionary = socket_payload.get("qa", {})
    if (
        str(socket_qa.get("gate", "")) != "PASS"
        or int(socket_qa.get("pairs_scanned", 0)) != LOWER_DIRECTIONS.size() * UPPER_DIRECTIONS_8.size()
        or int(socket_qa.get("passed_pairs", 0)) != LOWER_DIRECTIONS.size() * UPPER_DIRECTIONS_8.size()
        or int(socket_qa.get("failed_pairs", -1)) != 0
        or not bool(socket_qa.get("all_64_connected", false))
        or not bool(socket_qa.get("same_direction_zero", false))
        or not bool(socket_qa.get("torso_bridge_required", false))
    ):
        _independent_aim_failure_reason = "torso_socket_v1_qa_not_pass"
        return false

    var declared_composite_hash := str(socket_payload.get("source_manifest_sha256", "")).to_lower()
    if declared_composite_hash.is_empty() or FileAccess.get_sha256(COMPOSITE_V6_MANIFEST_PATH).to_lower() != declared_composite_hash:
        _independent_aim_failure_reason = "torso_socket_v1_source_manifest_hash_mismatch"
        return false
    var declared_bridge_path := str(socket_payload.get("torso_bridge_manifest", ""))
    if "res://" + declared_bridge_path != TORSO_BRIDGE_MANIFEST_PATH:
        _independent_aim_failure_reason = "torso_socket_v1_bridge_path_mismatch"
        return false
    var declared_bridge_hash := str(socket_payload.get("torso_bridge_manifest_sha256", "")).to_lower()
    if declared_bridge_hash.is_empty() or FileAccess.get_sha256(TORSO_BRIDGE_MANIFEST_PATH).to_lower() != declared_bridge_hash:
        _independent_aim_failure_reason = "torso_bridge_v1_manifest_hash_mismatch"
        return false

    var offsets_payload: Dictionary = socket_payload.get("offsets_source_px", {})
    var staged_offsets: Dictionary = {}
    for lower_direction in LOWER_DIRECTIONS:
        var raw_row = offsets_payload.get(lower_direction, {})
        if not raw_row is Dictionary:
            _independent_aim_failure_reason = "missing_torso_socket_row_" + lower_direction
            return false
        var staged_row: Dictionary = {}
        for upper_direction in UPPER_DIRECTIONS_8:
            var raw_xy: Array = (raw_row as Dictionary).get(upper_direction, [])
            if raw_xy.size() != 2:
                _independent_aim_failure_reason = "missing_torso_socket_pair_%s_%s" % [lower_direction, upper_direction]
                return false
            var offset := Vector2(float(raw_xy[0]), float(raw_xy[1]))
            if offset.x != offset.x or offset.y != offset.y or absf(offset.x) > CELL_SIZE or absf(offset.y) > CELL_SIZE:
                _independent_aim_failure_reason = "invalid_torso_socket_pair_%s_%s" % [lower_direction, upper_direction]
                return false
            if lower_direction == upper_direction and offset.length() > 0.001:
                _independent_aim_failure_reason = "nonzero_same_direction_socket_" + lower_direction
                return false
            staged_row[upper_direction] = offset
        staged_offsets[lower_direction] = staged_row
    _torso_socket_loaded = true

    var bridge_payload := _read_json_dictionary(TORSO_BRIDGE_MANIFEST_PATH)
    var bridge_directions: Array = bridge_payload.get("directions", [])
    var bridge_cell: Array = bridge_payload.get("cell", [])
    if (
        int(bridge_payload.get("schema", 0)) != 1
        or int(bridge_payload.get("frame_count", 0)) != MOVE_V6_FRAME_COUNT
        or int(bridge_payload.get("fps", 0)) != int(MOVE_V6_FPS)
        or bridge_cell.size() != 2
        or int(bridge_cell[0]) != int(CELL_SIZE)
        or int(bridge_cell[1]) != int(CELL_SIZE)
        or bridge_directions.size() != LOWER_DIRECTIONS.size()
        or str(bridge_payload.get("source_manifest_sha256", "")).to_lower() != declared_composite_hash
        or bool(bridge_payload.get("baked_muzzle_vfx", true))
        or str(bridge_payload.get("runtime_authority", "")) != "presentation only"
    ):
        _independent_aim_failure_reason = "invalid_torso_bridge_v1_header"
        return false

    var bridge_records: Dictionary = bridge_payload.get("records", {})
    var staged_bridge_textures: Array[Texture2D] = []
    for index in range(LOWER_DIRECTIONS.size()):
        var direction := LOWER_DIRECTIONS[index]
        if str(bridge_directions[index]) != direction:
            _independent_aim_failure_reason = "invalid_torso_bridge_direction_" + direction
            return false
        var raw_record = bridge_records.get(direction, {})
        if not raw_record is Dictionary:
            _independent_aim_failure_reason = "missing_torso_bridge_record_" + direction
            return false
        var record := raw_record as Dictionary
        var expected_path := "res://assets/units/operators/aster/torso_bridge_v1/%s/ASTER_TORSO_BRIDGE_%s_V1_ATLAS.webp" % [direction, direction]
        if "res://" + str(record.get("output", "")) != expected_path:
            _independent_aim_failure_reason = "torso_bridge_path_mismatch_" + direction
            return false
        var expected_hash := str(record.get("output_sha256", "")).to_lower()
        if expected_hash.is_empty() or FileAccess.get_sha256(expected_path).to_lower() != expected_hash:
            _independent_aim_failure_reason = "torso_bridge_hash_mismatch_" + direction
            return false
        var bridge_texture := _load_runtime_texture(expected_path)
        if bridge_texture == null or bridge_texture.get_size() != Vector2(CELL_SIZE, CELL_SIZE * MOVE_V6_FRAME_COUNT):
            _independent_aim_failure_reason = "invalid_torso_bridge_atlas_" + direction
            return false
        staged_bridge_textures.append(bridge_texture)

    _upper_offsets_source_px = staged_offsets
    _torso_bridge_textures.append_array(staged_bridge_textures)
    _torso_bridge_loaded = true
    _independent_aim_composite_valid = true
    _independent_aim_failure_reason = ""
    _upper_pair_qa = "64_of_64_connected"
    return true


func _try_promote_upper16_bundle() -> bool:
    _upper16_promoted = false
    _upper16_failure_reason = "not_evaluated"
    if not _independent_aim_composite_valid:
        _upper16_failure_reason = "eight_way_safe_fallback_not_valid"
        return false
    if not FileAccess.file_exists(UPPER_16_MANIFEST_PATH):
        _upper16_failure_reason = "upper16_manifest_missing"
        return false

    # Read and validate everything into locals.  None of the active eight-way
    # arrays or authorities are mutated until the final commit block.
    var manifest := _read_json_dictionary(UPPER_16_MANIFEST_PATH)
    if manifest.is_empty():
        _upper16_failure_reason = "upper16_manifest_invalid_json"
        return false
    if int(manifest.get("schema", 0)) != 1 or str(manifest.get("candidate_id", "")) != UPPER_16_CANDIDATE_ID:
        _upper16_failure_reason = "upper16_manifest_invalid_header"
        return false
    if str(manifest.get("candidate_status", "")) != "PASS":
        _upper16_failure_reason = "upper16_candidate_status_hold"
        return false
    if not bool(manifest.get("promotion_ready", false)):
        _upper16_failure_reason = "upper16_promotion_not_ready"
        return false
    if str(manifest.get("visual_gate", "")) != "PASS":
        _upper16_failure_reason = "upper16_visual_gate_not_pass"
        return false
    if not _upper16_manifest_technical_pass(manifest):
        _upper16_failure_reason = "upper16_technical_result_not_pass"
        return false
    if not bool(manifest.get("runtime_eligible", false)):
        _upper16_failure_reason = "upper16_manifest_not_runtime_eligible"
        return false
    if not _upper16_manifest_status_gate(manifest):
        _upper16_failure_reason = "upper16_manifest_status_gate_not_pass"
        return false
    if (
        int(manifest.get("frame_count_per_direction", 0)) != FIRE_FRAME_COUNT
        or int(manifest.get("atlas_cell", 0)) != int(CELL_SIZE)
        or not _ordered_strings_equal(manifest.get("directions", []), UPPER_DIRECTIONS_16)
        or not _ordered_strings_equal(manifest.get("frame_labels", []), FIRE_FRAME_LABELS)
        or bool(manifest.get("krea2_used", true))
        or bool(manifest.get("cloud_inference_used", true))
    ):
        _upper16_failure_reason = "upper16_manifest_contract_mismatch"
        return false

    var directions_output = manifest.get("directions_output", {})
    if not directions_output is Dictionary or (directions_output as Dictionary).size() != UPPER_DIRECTIONS_16.size():
        _upper16_failure_reason = "upper16_atlas_record_count_mismatch"
        return false
    var staged_upper_textures: Array[Texture2D] = []
    for direction in UPPER_DIRECTIONS_16:
        var raw_record = (directions_output as Dictionary).get(direction, {})
        if not raw_record is Dictionary:
            _upper16_failure_reason = "upper16_missing_atlas_record_" + direction
            return false
        var record := raw_record as Dictionary
        var expected_path := UPPER_16_ROOT + "/%s/ASTER_FIRE_%s_UPPER_16_NO_SHOULDER_V2_ATLAS.png" % [direction, direction]
        if _as_res_path(str(record.get("output_atlas", ""))) != expected_path:
            _upper16_failure_reason = "upper16_atlas_path_mismatch_" + direction
            return false
        if not _file_matches_sha256(expected_path, str(record.get("output_sha256", ""))):
            _upper16_failure_reason = "upper16_atlas_hash_mismatch_" + direction
            return false
        var frames = record.get("frames", [])
        if not frames is Array or (frames as Array).size() != FIRE_FRAME_COUNT:
            _upper16_failure_reason = "upper16_frame_record_count_mismatch_" + direction
            return false
        for frame_index in range(FIRE_FRAME_COUNT):
            var raw_frame = (frames as Array)[frame_index]
            if not raw_frame is Dictionary:
                _upper16_failure_reason = "upper16_invalid_frame_record_%s_%d" % [direction, frame_index]
                return false
            var frame_record := raw_frame as Dictionary
            if int(frame_record.get("index", frame_index)) != frame_index or bool(frame_record.get("baked_muzzle_vfx", manifest.get("baked_muzzle_vfx", true))):
                _upper16_failure_reason = "upper16_frame_contract_mismatch_%s_%d" % [direction, frame_index]
                return false
        var atlas := _load_runtime_texture(expected_path)
        if atlas == null or atlas.get_size() != Vector2(CELL_SIZE, CELL_SIZE * FIRE_FRAME_COUNT):
            _upper16_failure_reason = "upper16_atlas_decode_failed_" + direction
            return false
        staged_upper_textures.append(atlas)

    var declared_alignment_path := _as_res_path(str(manifest.get("muzzle_alignment_16_v2", "")))
    if declared_alignment_path != UPPER_16_MUZZLE_ALIGNMENT_PATH:
        _upper16_failure_reason = "upper16_muzzle_alignment_path_mismatch"
        return false
    if not _file_matches_sha256(declared_alignment_path, str(manifest.get("muzzle_alignment_16_v2_sha256", ""))):
        _upper16_failure_reason = "upper16_muzzle_alignment_hash_mismatch"
        return false
    var staged_alignment := _stage_upper16_muzzle_alignment(declared_alignment_path)
    if staged_alignment.is_empty():
        return false

    var socket := _read_json_dictionary(TORSO_SOCKET_16_PATH)
    if socket.is_empty():
        _upper16_failure_reason = "upper16_torso_socket_missing_or_invalid"
        return false
    if (
        int(socket.get("schema", 0)) != 2
        or int(socket.get("cell_size", 0)) != int(CELL_SIZE)
        or int(socket.get("lower_frame_count", 0)) != MOVE_V6_FRAME_COUNT
        or int(socket.get("upper_frame_count", 0)) != FIRE_FRAME_COUNT
        or not _ordered_strings_equal(socket.get("lower_directions", []), LOWER_DIRECTIONS)
        or not _ordered_strings_equal(socket.get("upper_directions", []), UPPER_DIRECTIONS_16)
        or not _ordered_strings_equal(socket.get("upper_frame_labels", []), FIRE_FRAME_LABELS)
        or not _ordered_strings_equal(socket.get("composition_order", []), ["velocity_lower", "translated_aim_upper", "velocity_torso_bridge"])
    ):
        _upper16_failure_reason = "upper16_torso_socket_header_mismatch"
        return false
    if not _upper16_socket_status_gate(socket):
        _upper16_failure_reason = "upper16_torso_socket_not_runtime_eligible"
        return false
    var dependency = socket.get("dependency", {})
    var socket_qa = socket.get("qa", {})
    if not dependency is Dictionary or not socket_qa is Dictionary:
        _upper16_failure_reason = "upper16_torso_socket_gate_records_missing"
        return false
    var dependency_dict := dependency as Dictionary
    var qa_dict := socket_qa as Dictionary
    if (
        str(dependency_dict.get("gate", "")) != "PASS"
        or not bool(dependency_dict.get("candidate_or_promotion_pass", false))
        or not bool(dependency_dict.get("visual_pass", false))
        or not bool(dependency_dict.get("technical_pass", false))
        or str(qa_dict.get("technical_gate", "")) != "PASS"
        or str(qa_dict.get("dependency_gate", "")) != "PASS"
        or str(qa_dict.get("promotion_gate", "")) != "PASS"
        or int(qa_dict.get("pair_count", 0)) != LOWER_DIRECTIONS.size() * UPPER_DIRECTIONS_16.size()
        or int(qa_dict.get("passed_pairs", 0)) != LOWER_DIRECTIONS.size() * UPPER_DIRECTIONS_16.size()
        or int(qa_dict.get("failed_pairs", -1)) != 0
        or not bool(qa_dict.get("all_128_pairs_connected", false))
        or not bool(qa_dict.get("all_24_lower_phases_scanned", false))
        or int(qa_dict.get("lower_phases_per_pair", 0)) != MOVE_V6_FRAME_COUNT
        or int(qa_dict.get("upper_frames_per_lower_phase", 0)) != FIRE_FRAME_COUNT
        or int(qa_dict.get("samples_scanned", 0)) != LOWER_DIRECTIONS.size() * UPPER_DIRECTIONS_16.size() * MOVE_V6_FRAME_COUNT * FIRE_FRAME_COUNT
        or int(qa_dict.get("expected_samples", 0)) != LOWER_DIRECTIONS.size() * UPPER_DIRECTIONS_16.size() * MOVE_V6_FRAME_COUNT * FIRE_FRAME_COUNT
        or int(qa_dict.get("unsafe_locked_lower_overwrite_samples", -1)) != 0
        or str(qa_dict.get("safe_seam_gate", "")) != "PASS"
        or str(qa_dict.get("locked_lower_preservation_gate", "")) != "PASS"
        or not bool(qa_dict.get("cardinal_same_direction_offsets_zero", false))
    ):
        _upper16_failure_reason = "upper16_torso_socket_qa_not_pass"
        return false

    var protection_policy = socket.get("upper_lower_protection_policy", {})
    if (
        not protection_policy is Dictionary
        or not bool((protection_policy as Dictionary).get("presentation_only", false))
        or not bool((protection_policy as Dictionary).get("torso_bridge_last", false))
        or not bool((protection_policy as Dictionary).get("weapon_corridor_exempt", false))
    ):
        _upper16_failure_reason = "upper16_torso_socket_protection_policy_mismatch"
        return false

    var sources = socket.get("sources", {})
    if not sources is Dictionary:
        _upper16_failure_reason = "upper16_torso_socket_sources_missing"
        return false
    var source_dict := sources as Dictionary
    if (
        _as_res_path(str(source_dict.get("fire_upper_16_manifest", ""))) != UPPER_16_MANIFEST_PATH
        or not _file_matches_sha256(UPPER_16_MANIFEST_PATH, str(source_dict.get("fire_upper_16_manifest_sha256", "")))
        or _as_res_path(str(source_dict.get("composite_manifest", ""))) != COMPOSITE_V6_MANIFEST_PATH
        or not _file_matches_sha256(COMPOSITE_V6_MANIFEST_PATH, str(source_dict.get("composite_manifest_sha256", "")))
        or _as_res_path(str(source_dict.get("torso_bridge_manifest", ""))) != TORSO_BRIDGE_MANIFEST_PATH
        or not _file_matches_sha256(TORSO_BRIDGE_MANIFEST_PATH, str(source_dict.get("torso_bridge_manifest_sha256", "")))
        or _as_res_path(str(source_dict.get("approved_torso_v1", ""))) != TORSO_SOCKET_PATH
        or not _file_matches_sha256(TORSO_SOCKET_PATH, str(source_dict.get("approved_torso_v1_sha256", "")))
    ):
        _upper16_failure_reason = "upper16_torso_socket_source_hash_mismatch"
        return false

    var staged_offsets := _stage_upper16_socket_offsets(socket)
    if staged_offsets.is_empty():
        return false
    var staged_bridge_textures := _stage_upper16_lower_and_bridge_hashes(source_dict)
    if staged_bridge_textures.is_empty():
        return false

    # Atomic commit: all 16 upper atlases, their muzzle authority, the 8x16
    # per-fire-frame socket table and every bridge dependency swap together.
    var old_upper_count := _active_upper_directions.size()
    _active_upper_directions = UPPER_DIRECTIONS_16.duplicate()
    if _upper_sector >= 0:
        _upper_sector = _remap_sector(_upper_sector, old_upper_count, _active_upper_directions.size())
        _sector = _upper_sector
    _fire_upper_textures.clear()
    _fire_upper_textures.append_array(staged_upper_textures)
    _torso_bridge_textures.clear()
    _torso_bridge_textures.append_array(staged_bridge_textures)
    _upper_offsets_source_px = staged_offsets
    _upper_offsets_are_per_frame = true
    _muzzle_source_points = staged_alignment["muzzle_points"]
    _barrel_tangent_radians = staged_alignment["barrel_tangents"]
    _muzzle_alignment_loaded = true
    _active_torso_socket_path = TORSO_SOCKET_16_PATH
    _active_muzzle_alignment_path = UPPER_16_MUZZLE_ALIGNMENT_PATH
    _upper_runtime_asset_family = UPPER_16_CANDIDATE_ID
    _upper_pair_qa = "128_of_128_connected_all_24_lower_phases"
    _torso_socket_loaded = true
    _torso_bridge_loaded = true
    _independent_aim_composite_valid = true
    _independent_aim_failure_reason = ""
    _upper16_promoted = true
    _upper16_failure_reason = ""
    return true


func _stage_upper16_muzzle_alignment(path: String) -> Dictionary:
    var payload := _read_json_dictionary(path)
    if payload.is_empty() or int(payload.get("schema", 0)) != 1:
        _upper16_failure_reason = "upper16_muzzle_alignment_invalid_json_or_schema"
        return {}
    if not _upper16_alignment_status_gate(payload):
        _upper16_failure_reason = "upper16_muzzle_alignment_status_hold"
        return {}
    if (
        int(payload.get("cell_size", 0)) != int(CELL_SIZE)
        or int(payload.get("source_frame", -1)) != FIRE_CONTACT_FRAME
        or not _ordered_strings_equal(payload.get("directions", []), UPPER_DIRECTIONS_16)
    ):
        _upper16_failure_reason = "upper16_muzzle_alignment_header_mismatch"
        return {}
    var runtime_contract = payload.get("runtime_contract", {})
    if (
        not runtime_contract is Dictionary
        or not bool((runtime_contract as Dictionary).get("projectile_spawn_equals_flash_socket", false))
        or bool((runtime_contract as Dictionary).get("character_raster_rotated", true))
        or not bool((runtime_contract as Dictionary).get("gameplay_aim_direction_unchanged", false))
        or bool((runtime_contract as Dictionary).get("baked_muzzle_vfx", true))
    ):
        _upper16_failure_reason = "upper16_muzzle_alignment_runtime_contract_mismatch"
        return {}
    var calibration = payload.get("calibration", {})
    if not calibration is Dictionary or (calibration as Dictionary).size() != UPPER_DIRECTIONS_16.size():
        _upper16_failure_reason = "upper16_muzzle_alignment_count_mismatch"
        return {}
    var muzzle_points: Array[Vector2] = []
    var barrel_tangents: Array[float] = []
    for direction in UPPER_DIRECTIONS_16:
        var raw_entry = (calibration as Dictionary).get(direction, {})
        if not raw_entry is Dictionary:
            _upper16_failure_reason = "upper16_muzzle_alignment_missing_" + direction
            return {}
        var entry := raw_entry as Dictionary
        var muzzle_xy = entry.get("muzzle_xy", [])
        var inner_xy = entry.get("barrel_inner_xy", [])
        if not muzzle_xy is Array or not inner_xy is Array or (muzzle_xy as Array).size() != 2 or (inner_xy as Array).size() != 2:
            _upper16_failure_reason = "upper16_muzzle_alignment_fields_invalid_" + direction
            return {}
        var muzzle := Vector2(float(muzzle_xy[0]), float(muzzle_xy[1]))
        var inner := Vector2(float(inner_xy[0]), float(inner_xy[1]))
        if (
            muzzle.x < 0.0 or muzzle.x >= CELL_SIZE or muzzle.y < 0.0 or muzzle.y >= CELL_SIZE
            or inner.x < 0.0 or inner.x >= CELL_SIZE or inner.y < 0.0 or inner.y >= CELL_SIZE
            or muzzle.distance_to(inner) < 24.0
        ):
            _upper16_failure_reason = "upper16_muzzle_alignment_geometry_invalid_" + direction
            return {}
        var declared := deg_to_rad(float(entry.get("barrel_tangent_degrees", 9999.0)))
        if absf(angle_difference(declared, (muzzle - inner).angle())) > deg_to_rad(0.05):
            _upper16_failure_reason = "upper16_muzzle_alignment_tangent_invalid_" + direction
            return {}
        muzzle_points.append(muzzle)
        barrel_tangents.append(declared)
    return {"muzzle_points": muzzle_points, "barrel_tangents": barrel_tangents}


func _stage_upper16_socket_offsets(socket: Dictionary) -> Dictionary:
    var raw_offsets = socket.get("offsets_source_px_by_frame", {})
    if not raw_offsets is Dictionary:
        _upper16_failure_reason = "upper16_socket_offsets_missing"
        return {}
    var staged: Dictionary = {}
    for lower_direction in LOWER_DIRECTIONS:
        var raw_row = (raw_offsets as Dictionary).get(lower_direction, {})
        if not raw_row is Dictionary:
            _upper16_failure_reason = "upper16_socket_row_missing_" + lower_direction
            return {}
        var staged_row: Dictionary = {}
        for upper_direction in UPPER_DIRECTIONS_16:
            var raw_frames = (raw_row as Dictionary).get(upper_direction, {})
            if not raw_frames is Dictionary:
                _upper16_failure_reason = "upper16_socket_pair_missing_%s_%s" % [lower_direction, upper_direction]
                return {}
            var staged_frames: Dictionary = {}
            for frame_label in FIRE_FRAME_LABELS:
                var raw_xy = (raw_frames as Dictionary).get(frame_label, [])
                if not raw_xy is Array or (raw_xy as Array).size() != 2:
                    _upper16_failure_reason = "upper16_socket_frame_missing_%s_%s_%s" % [lower_direction, upper_direction, frame_label]
                    return {}
                var offset := Vector2(float(raw_xy[0]), float(raw_xy[1]))
                if offset.x != offset.x or offset.y != offset.y or absf(offset.x) > CELL_SIZE or absf(offset.y) > CELL_SIZE:
                    _upper16_failure_reason = "upper16_socket_frame_invalid_%s_%s_%s" % [lower_direction, upper_direction, frame_label]
                    return {}
                if lower_direction == upper_direction and offset.length() > 0.001:
                    _upper16_failure_reason = "upper16_socket_cardinal_zero_mismatch_%s_%s" % [lower_direction, frame_label]
                    return {}
                staged_frames[frame_label] = offset
            staged_row[upper_direction] = staged_frames
        staged[lower_direction] = staged_row
    return staged


func _stage_upper16_lower_and_bridge_hashes(source_dict: Dictionary) -> Array[Texture2D]:
    var atlas_sha = source_dict.get("atlas_sha256", {})
    if not atlas_sha is Dictionary:
        _upper16_failure_reason = "upper16_socket_atlas_hashes_missing"
        return []
    var lower_sha = (atlas_sha as Dictionary).get("lower", {})
    var bridge_sha = (atlas_sha as Dictionary).get("bridge", {})
    var upper_sha = (atlas_sha as Dictionary).get("upper", {})
    if not lower_sha is Dictionary or not bridge_sha is Dictionary or not upper_sha is Dictionary:
        _upper16_failure_reason = "upper16_socket_lower_upper_or_bridge_hashes_missing"
        return []
    var staged_bridge: Array[Texture2D] = []
    for direction in LOWER_DIRECTIONS:
        var lower_path := "res://assets/units/operators/aster/composite_fire_v6/move_lower/%s/ASTER_MOVE_%s_LOWER_V6_ATLAS.webp" % [direction, direction]
        var bridge_path := "res://assets/units/operators/aster/torso_bridge_v1/%s/ASTER_TORSO_BRIDGE_%s_V1_ATLAS.webp" % [direction, direction]
        if not _file_matches_sha256(lower_path, str((lower_sha as Dictionary).get(direction, ""))):
            _upper16_failure_reason = "upper16_socket_lower_hash_mismatch_" + direction
            return []
        if not _file_matches_sha256(bridge_path, str((bridge_sha as Dictionary).get(direction, ""))):
            _upper16_failure_reason = "upper16_socket_bridge_hash_mismatch_" + direction
            return []
        var bridge := _load_runtime_texture(bridge_path)
        if bridge == null or bridge.get_size() != Vector2(CELL_SIZE, CELL_SIZE * MOVE_V6_FRAME_COUNT):
            _upper16_failure_reason = "upper16_socket_bridge_decode_failed_" + direction
            return []
        staged_bridge.append(bridge)
    for direction in UPPER_DIRECTIONS_16:
        var upper_path := UPPER_16_ROOT + "/%s/ASTER_FIRE_%s_UPPER_16_NO_SHOULDER_V2_ATLAS.png" % [direction, direction]
        if not _file_matches_sha256(upper_path, str((upper_sha as Dictionary).get(direction, ""))):
            _upper16_failure_reason = "upper16_socket_upper_hash_mismatch_" + direction
            return []
    return staged_bridge


func _upper16_manifest_technical_pass(payload: Dictionary) -> bool:
    var qa = payload.get("qa", {})
    return qa is Dictionary and str((qa as Dictionary).get("technical_result", "")) == "PASS"


func _upper16_manifest_status_gate(payload: Dictionary) -> bool:
    # The upper manifest is the root promotion authority.  Unlike dependent
    # alignment/socket payloads, both its reviewed candidate marker and its
    # explicit promotion marker must be present.  This mirrors the HTML review
    # gate exactly and prevents either consumer from entering sixteen-way mode
    # while the other remains on the coherent eight-way fallback.
    return (
        str(payload.get("candidate_status", "")) == "PASS"
        and bool(payload.get("promotion_ready", false))
        and str(payload.get("visual_gate", "")) == "PASS"
        and _upper16_manifest_technical_pass(payload)
        and bool(payload.get("runtime_eligible", false))
    )


func _upper16_alignment_status_gate(payload: Dictionary) -> bool:
    return str(payload.get("candidate_status", "")) == "PASS"


func _upper16_socket_status_gate(payload: Dictionary) -> bool:
    var dependency = payload.get("dependency", {})
    var qa = payload.get("qa", {})
    return (
        str(payload.get("candidate_status", "")) == "PASS"
        and str(payload.get("visual_gate", "")) == "PASS"
        and bool(payload.get("runtime_eligible", false))
        and dependency is Dictionary
        and str((dependency as Dictionary).get("candidate_status", "")) == "PASS"
        and bool((dependency as Dictionary).get("promotion_ready", false))
        and str((dependency as Dictionary).get("visual_gate", "")) == "PASS"
        and str((dependency as Dictionary).get("technical_result", "")) == "PASS"
        and str((dependency as Dictionary).get("gate", "")) == "PASS"
        and bool((dependency as Dictionary).get("candidate_or_promotion_pass", false))
        and bool((dependency as Dictionary).get("visual_pass", false))
        and bool((dependency as Dictionary).get("technical_pass", false))
        and qa is Dictionary
        and str((qa as Dictionary).get("technical_gate", "")) == "PASS"
        and str((qa as Dictionary).get("dependency_gate", "")) == "PASS"
        and str((qa as Dictionary).get("promotion_gate", "")) == "PASS"
    )


func _ordered_strings_equal(raw: Variant, expected: Array[String]) -> bool:
    if not raw is Array or (raw as Array).size() != expected.size():
        return false
    for index in range(expected.size()):
        if str((raw as Array)[index]) != expected[index]:
            return false
    return true


func _as_res_path(path: String) -> String:
    if path.begins_with("res://"):
        return path
    return "res://" + path.trim_prefix("./")


func _file_matches_sha256(path: String, expected_sha256: String) -> bool:
    var expected := expected_sha256.to_lower()
    return not expected.is_empty() and FileAccess.file_exists(path) and FileAccess.get_sha256(path).to_lower() == expected


func _read_json_dictionary(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    return parsed as Dictionary if parsed is Dictionary else {}


func _load_muzzle_alignment() -> bool:
    if _muzzle_alignment_loaded and _muzzle_source_points.size() == DIRECTIONS.size() and _barrel_tangent_radians.size() == DIRECTIONS.size():
        return true
    _muzzle_alignment_loaded = false
    _muzzle_source_points.clear()
    _barrel_tangent_radians.clear()
    if not FileAccess.file_exists(MUZZLE_ALIGNMENT_PATH):
        _status = "missing_muzzle_alignment_v7"
        return false
    var file := FileAccess.open(MUZZLE_ALIGNMENT_PATH, FileAccess.READ)
    if file == null:
        _status = "unreadable_muzzle_alignment_v7"
        return false
    var parsed = JSON.parse_string(file.get_as_text())
    if not parsed is Dictionary:
        _status = "invalid_muzzle_alignment_v7_json"
        return false
    var payload := parsed as Dictionary
    if int(payload.get("schema", 0)) != 1 or int(payload.get("cell_size", 0)) != int(CELL_SIZE) or int(payload.get("source_frame", -1)) != FIRE_CONTACT_FRAME:
        _status = "invalid_muzzle_alignment_v7_header"
        return false
    var contract_directions: Array = payload.get("directions", [])
    var calibration: Dictionary = payload.get("calibration", {})
    if contract_directions.size() != DIRECTIONS.size() or calibration.size() != DIRECTIONS.size():
        _status = "invalid_muzzle_alignment_v7_count"
        return false
    for index in range(DIRECTIONS.size()):
        var direction := DIRECTIONS[index]
        if str(contract_directions[index]) != direction or not calibration.has(direction):
            _status = "invalid_muzzle_alignment_v7_direction_" + direction
            return false
        var entry = calibration[direction]
        if not entry is Dictionary:
            _status = "invalid_muzzle_alignment_v7_entry_" + direction
            return false
        var entry_dict := entry as Dictionary
        var muzzle_xy: Array = entry_dict.get("muzzle_xy", [])
        var inner_xy: Array = entry_dict.get("barrel_inner_xy", [])
        if muzzle_xy.size() != 2 or inner_xy.size() != 2 or not entry_dict.has("barrel_tangent_degrees"):
            _status = "invalid_muzzle_alignment_v7_fields_" + direction
            return false
        var muzzle := Vector2(float(muzzle_xy[0]), float(muzzle_xy[1]))
        var inner := Vector2(float(inner_xy[0]), float(inner_xy[1]))
        if muzzle.x < 0.0 or muzzle.x >= CELL_SIZE or muzzle.y < 0.0 or muzzle.y >= CELL_SIZE or muzzle.distance_to(inner) < 24.0:
            _status = "invalid_muzzle_alignment_v7_geometry_" + direction
            return false
        var declared_radians := deg_to_rad(float(entry_dict["barrel_tangent_degrees"]))
        var measured_radians := (muzzle - inner).angle()
        if absf(wrapf(declared_radians - measured_radians, -PI, PI)) > deg_to_rad(0.02):
            _status = "invalid_muzzle_alignment_v7_tangent_" + direction
            return false
        _muzzle_source_points.append(muzzle)
        _barrel_tangent_radians.append(declared_radians)
    _muzzle_alignment_loaded = true
    return true


func _load_runtime_texture(resource_path: String) -> Texture2D:
    # These pilot atlases are deliberately kept as raw lossless WebP files so
    # the browser review and Godot runtime consume the exact same bytes.  Load
    # through Image instead of relying on editor-generated .import sidecars.
    if not FileAccess.file_exists(resource_path):
        return null
    var image := Image.new()
    var error := image.load(ProjectSettings.globalize_path(resource_path))
    if error != OK:
        return null
    return ImageTexture.create_from_image(image)


func _sync_sector(force: bool = false) -> void:
    if actor == null:
        return

    # Upper presentation follows continuous aim.  `facing_sector` is only the
    # zero-vector fallback; neither value is ever written by this renderer.
    var upper_direction := actor.aim_world
    if upper_direction.length_squared() <= 0.0001:
        upper_direction = Vector2.from_angle(
            float(posmod(actor.facing_sector, DIRECTIONS.size())) * TAU / float(DIRECTIONS.size())
        )
    _upper_sector = _resolve_direction_sector(
        upper_direction,
        _upper_sector,
        _active_upper_directions.size(),
        force,
    )

    # A stationary body has no locomotion direction.  Preserve its most recent
    # lower sector (or initialize from upper on activation); once moving, only
    # actual velocity may steer the legs.  Direction changes deliberately do
    # not touch `_move_cursor`, so gait phase survives strafe/turn boundaries.
    if actor.velocity.length() > LOCOMOTION_SPEED_THRESHOLD:
        _lower_sector = _resolve_direction_sector(
            actor.velocity,
            _lower_sector,
            LOWER_DIRECTIONS.size(),
            force,
        )
    elif _lower_sector < 0:
        _lower_sector = _remap_sector(_upper_sector, _active_upper_directions.size(), LOWER_DIRECTIONS.size())

    # Compatibility for existing captures/tests that read `sector` as the
    # aim-facing sector.
    _sector = _upper_sector


func _resolve_direction_sector(
    direction: Vector2,
    current_sector: int,
    sector_count: int,
    force: bool = false,
) -> int:
    if sector_count <= 0:
        return -1
    if direction.length_squared() <= 0.0001:
        return posmod(current_sector, sector_count) if current_sector >= 0 else 0
    var angle := fposmod(direction.angle(), TAU)
    var candidate := int(floor((angle + PI / float(sector_count)) / (TAU / float(sector_count)))) % sector_count
    if force or current_sector < 0:
        return candidate
    var current := posmod(current_sector, sector_count)
    var current_centre := float(current) * TAU / float(sector_count)
    var hold_half_width := PI / float(sector_count) + deg_to_rad(DIRECTION_HYSTERESIS_DEGREES)
    if absf(angle_difference(angle, current_centre)) <= hold_half_width:
        return current
    return candidate


func _remap_sector(source_sector: int, source_count: int, target_count: int) -> int:
    if source_count <= 0 or target_count <= 0:
        return 0
    return posmod(int(round(float(posmod(source_sector, source_count)) * float(target_count) / float(source_count))), target_count)


func _upper_alignment_offset(lower_sector: int, upper_sector: int, upper_frame: int = 0) -> Vector2:
    if not _independent_aim_composite_valid or lower_sector < 0 or upper_sector < 0:
        return Vector2.ZERO
    var lower_direction := LOWER_DIRECTIONS[posmod(lower_sector, LOWER_DIRECTIONS.size())]
    var upper_direction := _active_upper_directions[posmod(upper_sector, _active_upper_directions.size())]
    var row = _upper_offsets_source_px.get(lower_direction, {})
    if not row is Dictionary:
        return Vector2.ZERO
    var source_offset = (row as Dictionary).get(upper_direction, Vector2.ZERO)
    if _upper_offsets_are_per_frame:
        if not source_offset is Dictionary:
            return Vector2.ZERO
        var frame_label := FIRE_FRAME_LABELS[posmod(upper_frame, FIRE_FRAME_COUNT)]
        source_offset = (source_offset as Dictionary).get(frame_label, Vector2.ZERO)
    return source_offset * DISPLAY_SCALE if source_offset is Vector2 else Vector2.ZERO


func _muzzle_upper_presentation_offset() -> Vector2:
    if actor == null or actor.is_downed() or not _independent_aim_composite_valid:
        return Vector2.ZERO
    var moving := actor.velocity.length() > LOCOMOTION_SPEED_THRESHOLD
    var lower_sector := _lower_sector if moving else _remap_sector(_upper_sector, _active_upper_directions.size(), LOWER_DIRECTIONS.size())
    return _upper_alignment_offset(lower_sector, _upper_sector, FIRE_CONTACT_FRAME)


func _apply_upper_presentation_offset(composite: bool, upper_frame: int = 0, lower_sector_override: int = -1) -> void:
    var resolved_lower := lower_sector_override
    if resolved_lower < 0:
        resolved_lower = _lower_sector
    _upper_presentation_offset_runtime = _upper_alignment_offset(resolved_lower, _upper_sector, upper_frame) if composite else Vector2.ZERO
    fire_upper.position = DISPLAY_OFFSET + _upper_presentation_offset_runtime


func _show_idle_frame(frame: int) -> void:
    var idle_sector := _remap_sector(_upper_sector, _active_upper_directions.size(), DIRECTIONS.size())
    primary.texture = _idle_textures[idle_sector]
    primary.region_rect = Rect2(0.0, float(posmod(frame, IDLE_FRAME_COUNT)) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    primary.position = DISPLAY_OFFSET
    torso_bridge.visible = false
    _apply_upper_presentation_offset(false)
    _move_aim_ready_upper_active = false
    _apply_tint(1.0, 0.0)
    primary.visible = true
    blend.visible = false
    fire_upper.visible = false
    _last_frame = posmod(frame, IDLE_FRAME_COUNT)


func _show_move_frame(frame: int) -> void:
    var current := posmod(frame, _move_frame_count)
    primary.position = DISPLAY_OFFSET
    if _independent_aim_composite_valid:
        primary.texture = _move_lower_textures[_lower_sector]
        torso_bridge.texture = _torso_bridge_textures[_lower_sector]
        fire_upper.texture = _fire_upper_textures[_upper_sector]
        primary.region_rect = Rect2(0.0, float(current) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        torso_bridge.region_rect = primary.region_rect
        fire_upper.region_rect = Rect2(0.0, float(MOVE_AIM_READY_UPPER_FRAME) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        torso_bridge.position = DISPLAY_OFFSET
        _apply_upper_presentation_offset(true)
        torso_bridge.visible = true
        fire_upper.visible = true
        _move_aim_ready_upper_active = true
        _lower_body_atlas_selected = _composite_runtime_asset_family + "/move_lower"
    else:
        primary.texture = _move_textures[_lower_sector]
        primary.region_rect = Rect2(0.0, float(current) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        torso_bridge.visible = false
        _apply_upper_presentation_offset(false)
        fire_upper.visible = false
        _move_aim_ready_upper_active = false
        _lower_body_atlas_selected = _move_runtime_asset_family
    _apply_tint(1.0, 0.0)
    torso_bridge.modulate = primary.modulate
    fire_upper.modulate = primary.modulate
    primary.visible = true
    blend.visible = false
    _last_frame = current


func _show_fire_frame(frame: int) -> void:
    var fire_sector := _remap_sector(_upper_sector, _active_upper_directions.size(), DIRECTIONS.size())
    primary.texture = _fire_textures[fire_sector]
    primary.region_rect = Rect2(0.0, float(frame) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    primary.position = DISPLAY_OFFSET
    torso_bridge.visible = false
    _apply_upper_presentation_offset(false)
    _move_aim_ready_upper_active = false
    _apply_tint(1.0, 0.0)
    primary.visible = true
    blend.visible = false
    fire_upper.visible = false
    _show_muzzle_frame(frame)
    _last_frame = frame


func _show_composite_fire_frame(frame: int, moving: bool) -> void:
    var lower_frame := posmod(int(floor(_move_cursor)), _move_frame_count) if moving else posmod(int(floor(_idle_cursor)), IDLE_FRAME_COUNT)
    var lower_sector := _lower_sector if moving else _remap_sector(_upper_sector, _active_upper_directions.size(), LOWER_DIRECTIONS.size())
    primary.texture = _move_lower_textures[lower_sector] if moving else _idle_lower_textures[lower_sector]
    primary.region_rect = Rect2(0.0, float(lower_frame) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    primary.position = DISPLAY_OFFSET
    fire_upper.texture = _fire_upper_textures[_upper_sector]
    fire_upper.region_rect = Rect2(0.0, float(frame) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    if moving:
        torso_bridge.texture = _torso_bridge_textures[lower_sector]
        torso_bridge.region_rect = primary.region_rect
        torso_bridge.position = DISPLAY_OFFSET
        torso_bridge.visible = true
        _apply_upper_presentation_offset(true, frame, lower_sector)
    else:
        torso_bridge.visible = false
        _apply_upper_presentation_offset(true, frame, lower_sector)
    _move_aim_ready_upper_active = false
    _apply_tint(1.0, 0.0)
    torso_bridge.modulate = primary.modulate
    fire_upper.modulate = primary.modulate
    primary.visible = true
    blend.visible = false
    fire_upper.visible = true
    _lower_body_atlas_selected = _composite_runtime_asset_family + ("/move_lower" if moving else "/idle_lower")
    _show_muzzle_frame(frame)
    _last_frame = frame


func _show_muzzle_frame(_frame: int) -> void:
    # Body pose playback must not own muzzle timing.  A separate short burst is
    # triggered synchronously by primary_fired and survives body-state changes.
    if _muzzle_flash_remaining > 0.0:
        _sync_muzzle_flash_transform()


func _begin_muzzle_flash() -> void:
    _sync_sector()
    _muzzle_flash_shot_sector = _muzzle_sector_for_upper(_upper_sector)
    _muzzle_flash_shot_direction = actor.aim_world.normalized() if actor.aim_world.length_squared() > 0.0001 else Vector2.from_angle(float(_muzzle_flash_shot_sector) * TAU / float(_active_upper_directions.size()))
    _muzzle_flash_shot_local = get_authored_muzzle_local_position()
    _muzzle_flash_barrel_residual_radians = absf(wrapf(_muzzle_flash_shot_direction.angle() - get_authored_barrel_tangent(_muzzle_flash_shot_sector).angle(), -PI, PI))
    _muzzle_flash_remaining = MUZZLE_FLASH_DURATION
    _muzzle_flash_trigger_count += 1
    _sync_muzzle_flash_transform()
    muzzle_flash.visible = true


func _update_muzzle_flash(delta: float) -> void:
    if _muzzle_flash_remaining <= 0.0:
        muzzle_flash.visible = false
        return
    _sync_muzzle_flash_transform()
    muzzle_flash.visible = true
    _muzzle_flash_remaining = maxf(_muzzle_flash_remaining - delta, 0.0)


func _sync_muzzle_flash_transform() -> void:
    # Position is the same contact-frame socket queried for projectile birth,
    # while rotation remains the unchanged continuous gameplay aim.  The body
    # raster is never rotated; its unavoidable eight-sector tangent residual is
    # exposed in debug_contract instead of hidden by changing combat authority.
    # Both values are captured at trigger time, so later aim changes cannot
    # teleport or rotate an in-flight muzzle burst.
    muzzle_flash.position = _muzzle_flash_shot_local
    muzzle_flash.rotation = _muzzle_flash_shot_direction.angle()


func _apply_tint(primary_alpha: float, blend_alpha: float) -> void:
    var tint := Color(0.48, 0.50, 0.54, 0.72) if actor.is_downed() else Color.WHITE
    primary.modulate = Color(tint.r, tint.g, tint.b, tint.a * primary_alpha)
    blend.modulate = Color(tint.r, tint.g, tint.b, tint.a * blend_alpha)
    if torso_bridge:
        torso_bridge.modulate = primary.modulate


func _deactivate(reason: String) -> void:
    _active = false
    _status = reason
    if primary:
        primary.visible = false
    if blend:
        blend.visible = false
    if torso_bridge:
        torso_bridge.visible = false
    if fire_upper:
        fire_upper.visible = false
    if muzzle_flash:
        muzzle_flash.visible = false
    _muzzle_flash_remaining = 0.0
    if actor:
        var legacy := actor.get_node_or_null("AuthoredRasterPresentation") as CanvasItem
        if legacy and not _motion_lab_active():
            legacy.visible = _legacy_was_visible
    if visual and not _motion_lab_active():
        visual.modulate.a = _visual_alpha_before_activation


func debug_contract() -> Dictionary:
    return {
        "feature_setting": FEATURE_SETTING,
        "feature_enabled": _feature_enabled(),
        "activation_attempted": _activation_attempted,
        "active": _active,
        "status": _status,
        "identity": actor.operator_id if actor else "",
        "direction": _active_upper_directions[_upper_sector] if _upper_sector >= 0 else "",
        "sector": _sector,
        "upper_direction": _active_upper_directions[_upper_sector] if _upper_sector >= 0 else "",
        "upper_sector": _upper_sector,
        "upper_direction_count": _active_upper_directions.size(),
        "upper_direction_api": "count_driven_continuous_aim",
        "upper_runtime_asset_family": _upper_runtime_asset_family if _split_fire_set_valid else "not_loaded",
        "upper_alignment_path": _active_torso_socket_path,
        "upper_contact_frame_alignment_path": _active_muzzle_alignment_path,
        "upper_alignment_promoted": _independent_aim_composite_valid,
        "upper_alignment_status": "validated_%d_way" % _active_upper_directions.size() if _independent_aim_composite_valid else "HOLD",
        "upper_runtime_promotion_contract": "upper_atlases_plus_torso_socket_plus_muzzle_alignment_atomic",
        "upper16_candidate_detected": _upper16_candidate_detected,
        "upper16_promoted": _upper16_promoted,
        "upper16_failure_reason": _upper16_failure_reason,
        "upper16_manifest_path": UPPER_16_MANIFEST_PATH,
        "upper16_muzzle_alignment_path": UPPER_16_MUZZLE_ALIGNMENT_PATH,
        "upper16_torso_socket_path": TORSO_SOCKET_16_PATH,
        "upper16_atomic_no_partial_mix": true,
        "upper16_safe_fallback_active": not _upper16_promoted and _active_upper_directions.size() == 8,
        "upper_socket_offsets_per_fire_frame": _upper_offsets_are_per_frame,
        "upper_socket_frame_authority": FIRE_FRAME_LABELS if _upper_offsets_are_per_frame else ["all_frames_shared"],
        "lower_direction": LOWER_DIRECTIONS[_lower_sector] if _lower_sector >= 0 else "",
        "lower_sector": _lower_sector,
        "lower_direction_count": LOWER_DIRECTIONS.size(),
        "lower_direction_authority": "actual_velocity",
        "upper_direction_authority": "continuous_aim_with_facing_fallback",
        "direction_hysteresis_degrees": DIRECTION_HYSTERESIS_DEGREES,
        "move_cursor_preserved_on_sector_change": true,
        "idle_texture_count": _idle_textures.size(),
        "move_texture_count": _move_textures.size(),
        "fire_texture_count": _fire_textures.size(),
        "full_body_idle_fire_direction_count": DIRECTIONS.size(),
        "full_body_upper_sector_remap_active": _active_upper_directions.size() != DIRECTIONS.size(),
        "idle_lower_texture_count": _idle_lower_textures.size(),
        "move_lower_texture_count": _move_lower_textures.size(),
        "fire_upper_texture_count": _fire_upper_textures.size(),
        "torso_bridge_texture_count": _torso_bridge_textures.size(),
        "torso_socket_loaded": _torso_socket_loaded,
        "torso_socket_path": _active_torso_socket_path,
        "torso_bridge_loaded": _torso_bridge_loaded,
        "torso_bridge_manifest_path": TORSO_BRIDGE_MANIFEST_PATH,
        "torso_bridge_visible": torso_bridge.visible if torso_bridge else false,
        "independent_aim_composite_valid": _independent_aim_composite_valid,
        "independent_aim_failure_reason": _independent_aim_failure_reason,
        "independent_aim_pair_qa": _upper_pair_qa if _independent_aim_composite_valid else "HOLD",
        "raw_cross_direction_splice_used": false,
        "upper_presentation_offset_runtime": _upper_presentation_offset_runtime,
        "torso_offset_source_px": _upper_presentation_offset_runtime / DISPLAY_SCALE,
        "torso_offset_runtime_px": _upper_presentation_offset_runtime,
        "torso_bridge_state": "visible_lower_phase" if torso_bridge and torso_bridge.visible else ("loaded" if _torso_bridge_loaded else "HOLD"),
        "move_aim_ready_upper_active": _move_aim_ready_upper_active,
        "move_aim_ready_upper_frame": MOVE_AIM_READY_UPPER_FRAME,
        "true_strafe_backpedal_presentation": _independent_aim_composite_valid,
        "muzzle_texture_loaded": _muzzle_texture != null,
        "muzzle_alignment_loaded": _muzzle_alignment_loaded,
        "muzzle_alignment_path": _active_muzzle_alignment_path,
        "muzzle_alignment_source_frame": FIRE_CONTACT_FRAME,
        "muzzle_source_points": _muzzle_source_points,
        "barrel_tangent_radians": _barrel_tangent_radians,
        "muzzle_alignment_record_count": _muzzle_source_points.size(),
        "character_raster_rotated": false,
        "gameplay_aim_direction_unchanged": true,
        "eight_sector_off_axis_residual_reported": _active_upper_directions.size() == 8,
        "sixteen_sector_off_axis_residual_reported": _active_upper_directions.size() == 16,
        "idle_frame_count": IDLE_FRAME_COUNT,
        "move_frame_count": _move_frame_count,
        "fire_frame_count": FIRE_FRAME_COUNT,
        "idle_fps": IDLE_FPS,
        "idle_runtime_asset_family": "idle_360_clean_v5",
        "move_fps": _move_fps,
        "move_cadence_scale": _move_cadence_scale,
        "move_phase_advance_total": _move_phase_advance_total,
        "move_cadence_authority": "velocity_scaled_from_walk_speed",
        "fire_fps": FIRE_FPS,
        "fire_contact_frame": FIRE_CONTACT_FRAME,
        "fire_elapsed": _fire_elapsed,
        "previous_recoil": _previous_recoil,
        "visual_recoil": float(visual.get("_recoil")) if visual else 0.0,
        "fire_event_count": _fire_event_count,
        "last_frame": _last_frame,
        "playback_state": _playback_state,
        "blend_sprite_visible": blend.visible if blend else false,
        "split_fire_set_valid": _split_fire_set_valid,
        "moving_fire_split_fix_claimed": _independent_aim_composite_valid,
        "split_fire_failure_reason": _split_fire_failure_reason,
        "moving_fire_active": _moving_fire_active,
        "moving_fire_move_advance_count": _moving_fire_move_advance_count,
        "moving_fire_cursor_before": _moving_fire_cursor_before,
        "moving_fire_cursor_after": _moving_fire_cursor_after,
        "lower_body_atlas_selected": _lower_body_atlas_selected,
        "fire_upper_visible": fire_upper.visible if fire_upper else false,
        "completed_move_loops": _completed_move_loops,
        "continuous_render_blend": false,
        "adjacent_frame_crossfade": false,
        "stationary_uses_idle_atlas": true,
        "move_motion_authority": "UAL1 Jog_Fwd_Loop joint-curve timing; root motion removed; ASTER authored raster body",
        "move_runtime_asset_family": _move_runtime_asset_family,
        "composite_runtime_asset_family": _composite_runtime_asset_family,
        "move_v6_selected": _move_runtime_asset_family == "move_360_ual_v6",
        "move_v5_selected": _move_runtime_asset_family == "move_360_ual_v5",
        "move_fallback_reason": _move_fallback_reason,
        "fixed_visual_origin": DISPLAY_OFFSET,
        "display_scale": DISPLAY_SCALE,
        "cell_size": CELL_SIZE,
        "atlas_region_filter_clipped": true,
        "muzzle_vfx_embedded_in_character_frames": false,
        "muzzle_vfx_runtime_only": true,
        "muzzle_anchor_source": "fire_v4_contact_frame_v7_json",
        "muzzle_anchor_local": get_authored_muzzle_local_position(),
        "authored_muzzle_local": get_authored_muzzle_local_position(),
        "authored_muzzle_global": get_authored_muzzle_global_position(),
        "muzzle_vfx_visible": muzzle_flash.visible if muzzle_flash else false,
        "muzzle_vfx_remaining": _muzzle_flash_remaining,
        "muzzle_vfx_duration": MUZZLE_FLASH_DURATION,
        "muzzle_vfx_trigger_count": _muzzle_flash_trigger_count,
        "muzzle_vfx_shot_sector": _muzzle_flash_shot_sector,
        "muzzle_vfx_shot_direction": _muzzle_flash_shot_direction,
        "muzzle_vfx_shot_local": _muzzle_flash_shot_local,
        "muzzle_vfx_barrel_residual_radians": _muzzle_flash_barrel_residual_radians,
        "muzzle_vfx_rotation": muzzle_flash.rotation if muzzle_flash else 0.0,
        "muzzle_vfx_global_position": muzzle_flash.global_position if muzzle_flash else Vector2.ZERO,
        "muzzle_vfx_timing_authority": "primary_fired_immediate_burst",
        "rendering_only": true,
        "gameplay_timing_coupled": false,
        "collision_coupled": false,
        "production_visual_gate": "NOT_CLAIMED",
    }
