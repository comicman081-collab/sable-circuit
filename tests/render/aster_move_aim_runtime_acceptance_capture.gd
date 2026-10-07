extends SceneTree

const PROJECTILE_SCRIPT := preload("res://scripts/combat/prototype_projectile.gd")

## Production-scene acceptance capture for ASTER's independent lower/upper
## presentation contract.  This harness drives the real OperatorActor through
## its public debug input, so CharacterBody2D velocity, move_and_slide(), the
## production camera, authored raster renderer, muzzle socket, and projectile
## path all execute together.  It never rewrites gameplay movement or aim.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const FEATURE_SETTING := "sable_visuals/aster_v4_locomotion_preview"
const OUT_DIR := "res://artifacts/aster_move_aim_runtime_acceptance"
const VIEWPORT_SIZE := Vector2i(1920, 1080)
const CONTACT_SIZE := Vector2i(1920, 1080)
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const UPPER_DIRECTIONS_16: Array[String] = [
    "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW", "N", "NNE", "NE", "ENE",
]
const UPPER_16_MANIFEST_PATH := "res://assets/units/operators/aster/fire_upper_16_no_shoulder_v2/ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_MANIFEST.json"
const UPPER_16_MUZZLE_ALIGNMENT_PATH := "res://assets/units/operators/aster/fire_upper_16_no_shoulder_v2/ASTER_MUZZLE_ALIGNMENT_16_NO_SHOULDER_V2.json"
const TORSO_SOCKET_16_V2_PATH := "res://assets/units/operators/aster/ASTER_TORSO_SOCKET_16_NO_SHOULDER_V4.json"
const COMPOSITE_V6_MANIFEST_PATH := "res://assets/units/operators/aster/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"
const VISIBLE_BARREL_PROJECTILE_MAX_RESIDUAL_DEGREES := 6.0
const GAIT_PHASE_FRAME_COUNT := 24.0
const MAX_MOVING_GAIT_STEP_FRAMES := 2.0
const VECTORS: Array[Vector2] = [
    Vector2.RIGHT,
    Vector2(0.70710678, 0.70710678),
    Vector2.DOWN,
    Vector2(-0.70710678, 0.70710678),
    Vector2.LEFT,
    Vector2(-0.70710678, -0.70710678),
    Vector2.UP,
    Vector2(0.70710678, -0.70710678),
]
const MOVE_DIRECTION_FRAMES := 20
const AIM_ROTATION_FRAMES := 160
const STOP_FRAMES := 18
const REVERSAL_FRAMES := 28

var failed := false
var failures: Array[String] = []
var barrel_projectile_residual_limit_degrees := VISIBLE_BARREL_PROJECTILE_MAX_RESIDUAL_DEGREES
var evidence: Dictionary = {
    "harness": "ASTER production scene move/aim independence acceptance",
    "runtime_changes_made_by_harness": false,
    "gameplay_movement_authority_changed": false,
    "gameplay_aim_authority_changed": false,
    "collision_override": false,
    "actual_characterbody_motion": true,
    "actual_move_and_slide": true,
    "production_camera_active": true,
    "resolution_contract": {
        "source_master_resolution": [1254, 1254],
        "runtime_atlas_cell_resolution": [384, 384],
        "runtime_display_scale": 0.34,
        "runtime_display_size_px": [130.56, 130.56],
        "review_capture_resolution": [1920, 1080],
        "contact_sheet_resolution": [1920, 1080],
        "review_capture_scaling": "native_window_capture",
        "contact_scaling": "downscale native 1920x1080 captures into the contact; preserve originals",
        "original_scale_quality_panel": "owned by V9 no-shoulder upper 1080p visual QA",
        "upscaled_source_claim": false,
    },
    "aim_e_move_8": [],
    "move_e_aim_360": {},
    "stop_and_reversal": {},
}

var overlay_title: Label
var overlay_detail: Label


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    var previous_setting := bool(ProjectSettings.get_setting(FEATURE_SETTING, false))
    ProjectSettings.set_setting(FEATURE_SETTING, true)
    DisplayServer.window_set_size(VIEWPORT_SIZE)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    _make_overlay()

    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(18)

    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.queue_free()
    await _frames(2)

    var actor := stage.squad.get_active_operator() as OperatorActor
    var preview := actor.get_node_or_null("AsterV4LocomotionPreview") as AsterV4LocomotionPreview if actor else null
    if actor == null or actor.operator_id != "CHR_PROTO_01" or preview == null:
        _fail("could not resolve active ASTER preview")
        await _finish(stage, actor, previous_setting)
        return

    # Keep the real production camera but remove inactive squad members from its
    # centroid so the capture follows the actual moving ASTER without a harness
    # camera substitute.
    for operator in stage.squad.operators:
        if operator != actor:
            operator.downed_state = true
            operator.velocity = Vector2.ZERO
            operator.visible = false
    actor.visible = true
    actor.set_movement_bounds(Rect2(260.0, 120.0, 1740.0, 820.0))
    actor.global_position = Vector2(1040.0, 500.0)
    actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    await _physics_and_render_frames(8)

    var initial := preview.debug_contract()
    _require(bool(initial.get("active", false)), "ASTER authored raster preview is active")
    _require(str(initial.get("lower_direction_authority", "")) == "actual_velocity", "lower direction authority is actual velocity")
    _require(str(initial.get("upper_direction_authority", "")) == "continuous_aim_with_facing_fallback", "upper direction authority is continuous aim")
    _require(bool(initial.get("move_cursor_preserved_on_sector_change", false)), "gait cursor survives sector changes")
    _require(is_equal_approx(float(initial.get("direction_hysteresis_degrees", -1.0)), 4.0), "direction hysteresis is four degrees")
    _require(int(initial.get("lower_direction_count", 0)) == 8, "lower body uses eight velocity directions")
    _require(int(initial.get("upper_direction_count", 0)) == 16, "upper aim/fire uses sixteen directions")

    evidence["upper16_atomic_bundle"] = _validate_promoted_upper16_bundle(initial)

    evidence["godot_version"] = str(Engine.get_version_info().get("string", "unknown"))
    evidence["rendering_driver"] = RenderingServer.get_current_rendering_driver_name()
    evidence["video_adapter"] = RenderingServer.get_video_adapter_name()
    evidence["viewport"] = [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y]
    evidence["initial_contract"] = _serializable_contract(initial)

    # This capture is production acceptance for the promoted sixteen-way
    # bundle.  A fallback render is useful for development, but must never be
    # emitted or mistaken for sixteen-way acceptance evidence.
    if failed:
        evidence["result"] = "FAIL"
        evidence["failures"] = failures
        evidence["execution_blocked"] = "upper16_atomic_bundle_not_promoted"
        evidence["visual_foot_sliding_gate"] = "NOT_RUN"
        evidence["production_visual_gate"] = "NOT_CLAIMED"
        _write_json("ASTER_MOVE_AIM_RUNTIME_ACCEPTANCE_EVIDENCE.json", evidence)
        await _finish(stage, actor, previous_setting)
        return

    var move_contact_paths: Array[String] = []
    for index in range(DIRECTIONS.size()):
        var result := await _exercise_move_direction(actor, preview, DIRECTIONS[index], VECTORS[index])
        evidence["aim_e_move_8"].append(result)
        move_contact_paths.append(str(result.get("capture", "")))
    _make_contact(move_contact_paths, "ASTER_AIM_E_MOVE_8_ACTUAL_WORLD_CONTACT.png", 4, 2)

    evidence["move_e_aim_360"] = await _exercise_aim_rotation(actor, preview)
    evidence["stop_and_reversal"] = await _exercise_stop_reversal(actor, preview)
    evidence["all_move_directions_match_velocity"] = _all_move_cases_match()
    evidence["normalized_cardinal_diagonal_speed"] = _normalized_speed_gate()
    evidence["result"] = "FAIL" if failed else "PASS"
    evidence["failures"] = failures
    evidence["visual_foot_sliding_gate"] = "USER_REVIEW_REQUIRED"
    evidence["production_visual_gate"] = "NOT_CLAIMED"
    _write_json("ASTER_MOVE_AIM_RUNTIME_ACCEPTANCE_EVIDENCE.json", evidence)

    await _finish(stage, actor, previous_setting)


func _exercise_move_direction(actor: OperatorActor, preview: AsterV4LocomotionPreview, label: String, move_vector: Vector2) -> Dictionary:
    var start := actor.global_position
    var phase_before := float(preview.get("_move_cursor"))
    var was_already_moving := str(preview.get("_playback_state")) in ["move", "moving_fire"]
    var previous_phase := phase_before
    var maximum_phase_step := 0.0
    var fire_phase_delta := -1.0
    actor.debug_drive(move_vector, Vector2.RIGHT)
    var sampled_speeds: Array[float] = []
    for frame in range(MOVE_DIRECTION_FRAMES):
        await _physics_and_render_frames(1)
        sampled_speeds.append(actor.velocity.length())
        var current_phase := float(preview.get("_move_cursor"))
        var phase_step := _gait_forward_delta(previous_phase, current_phase)
        maximum_phase_step = maxf(maximum_phase_step, phase_step)
        # `physics_frame` is emitted immediately before node physics.  The
        # first sample after changing a debug move vector may therefore still
        # be the prior movement state; evaluate the first committed state.
        if frame > 0:
            _require(
                phase_step > 0.0 and phase_step <= MAX_MOVING_GAIT_STEP_FRAMES,
                "MOVE %s frame %d advances gait without a sector-reset jump" % [label, frame],
            )
        previous_phase = current_phase
        _set_overlay(
            "TEST 1/3  AIM E FIXED  |  MOVE %s" % label,
            _runtime_line(actor, preview) + "\nActual CharacterBody2D movement + production camera",
        )
        if frame == 9:
            var fire_phase_before := float(preview.get("_move_cursor"))
            var fired := actor.debug_fire_once()
            var fire_phase_after := float(preview.get("_move_cursor"))
            fire_phase_delta = absf(fire_phase_after - fire_phase_before)
            _require(fired, "MOVE %s triggers the moving-fire path" % label)
            _require(fire_phase_delta <= 0.0001, "MOVE %s fire event does not reset gait phase" % label)
    var contract := preview.debug_contract()
    var capture := await _save("ASTER_AIM_E_MOVE_%s.png" % label)
    var displacement := actor.global_position - start
    var mean_speed := _mean(sampled_speeds)
    var direction_match := str(contract.get("lower_direction", "")) == label
    var upper_match := str(contract.get("upper_direction", "")) == "E"
    _require(direction_match, "MOVE %s selects lower %s" % [label, label])
    _require(upper_match, "MOVE %s preserves upper E" % label)
    _require(displacement.dot(move_vector) > 35.0, "MOVE %s produces real world displacement" % label)
    return {
        "move_direction": label,
        "aim_direction": "E",
        "start_world": _v2(start),
        "end_world": _v2(actor.global_position),
        "displacement": _v2(displacement),
        "distance": displacement.length(),
        "mean_speed": mean_speed,
        "lower_direction": str(contract.get("lower_direction", "")),
        "upper_direction": str(contract.get("upper_direction", "")),
        "direction_match": direction_match,
        "upper_match": upper_match,
        "move_cursor_before": phase_before,
        "move_cursor_after": float(preview.get("_move_cursor")),
        "maximum_phase_step_frames": maximum_phase_step,
        "fire_phase_reset_delta": fire_phase_delta,
        "capture": capture,
    }


func _exercise_aim_rotation(actor: OperatorActor, preview: AsterV4LocomotionPreview) -> Dictionary:
    # Keep the acceptance sweep independent of magazine depletion from Test 1;
    # weapon timing, projectile setup, and gameplay code remain unchanged.
    actor.ammo = actor.magazine_size
    actor.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    await _physics_and_render_frames(1)
    var transitions: Array[Dictionary] = []
    var boundary_samples: Array[Dictionary] = []
    var shot_residuals: Array[Dictionary] = []
    var captures: Array[String] = []
    var previous_upper := -1
    var lower_e_all_frames := true
    var phase_before := float(preview.get("_move_cursor"))
    var previous_phase := phase_before
    var maximum_phase_step := 0.0
    var start := actor.global_position
    var sector_step_degrees := 360.0 / float(UPPER_DIRECTIONS_16.size())
    var sweep_step_degrees := 360.0 / float(AIM_ROTATION_FRAMES)
    for frame in range(AIM_ROTATION_FRAMES):
        var angle := TAU * float(frame) / float(AIM_ROTATION_FRAMES)
        var aim := Vector2.from_angle(angle)
        actor.debug_drive(Vector2.RIGHT, aim)
        await _physics_and_render_frames(1)
        var contract := preview.debug_contract()
        var upper_sector := int(contract.get("upper_sector", -1))
        var current_phase := float(preview.get("_move_cursor"))
        var phase_step := _gait_forward_delta(previous_phase, current_phase)
        maximum_phase_step = maxf(maximum_phase_step, phase_step)
        _require(
            phase_step > 0.0 and phase_step <= MAX_MOVING_GAIT_STEP_FRAMES,
            "360 aim frame %d advances the lower gait without a sector/fire reset" % frame,
        )
        previous_phase = current_phase
        lower_e_all_frames = lower_e_all_frames and str(contract.get("lower_direction", "")) == "E"
        if upper_sector != previous_upper:
            var transition := {
                "frame": frame,
                "aim_degrees": rad_to_deg(angle),
                "upper_sector": upper_sector,
                "upper_direction": str(contract.get("upper_direction", "")),
            }
            if previous_upper >= 0:
                var expected_sector := posmod(previous_upper + 1, UPPER_DIRECTIONS_16.size())
                var boundary_degrees := fposmod((float(previous_upper) + 0.5) * sector_step_degrees, 360.0)
                var overshoot_degrees := fposmod(rad_to_deg(angle) - boundary_degrees, 360.0)
                transition["from_sector"] = previous_upper
                transition["expected_sector"] = expected_sector
                transition["boundary_degrees"] = boundary_degrees
                transition["boundary_overshoot_degrees"] = overshoot_degrees
                boundary_samples.append(transition.duplicate(true))
                _require(upper_sector == expected_sector, "360 aim advances exactly one upper sector at frame %d" % frame)
            transitions.append(transition)
            previous_upper = upper_sector
        if frame % 10 == 0:
            var previous_projectile_id := _latest_projectile_id_for_actor(actor)
            var fire_phase_before := float(preview.get("_move_cursor"))
            var fired := actor.debug_fire_once()
            var fire_phase_after := float(preview.get("_move_cursor"))
            _require(fired, "16-direction centre %.1f degrees fires" % rad_to_deg(angle))
            _require(absf(fire_phase_after - fire_phase_before) <= 0.0001, "shot at %.1f degrees does not reset lower gait" % rad_to_deg(angle))
            var projectile := _latest_projectile_for_actor(actor)
            _require(projectile != null and projectile.get_instance_id() != previous_projectile_id, "shot at %.1f degrees creates a new projectile" % rad_to_deg(angle))
            var projectile_direction := aim
            var projectile_origin := Vector2.ZERO
            if projectile != null:
                var raw_projectile_direction = projectile.get("direction")
                if raw_projectile_direction is Vector2:
                    projectile_direction = raw_projectile_direction
                projectile_origin = projectile.global_position
            var visible_tangent := preview.get_authored_barrel_tangent(upper_sector)
            var residual_degrees := absf(rad_to_deg(angle_difference(projectile_direction.angle(), visible_tangent.angle())))
            var authored_origin := preview.get_authored_muzzle_global_position()
            _require(projectile == null or projectile_origin.distance_to(authored_origin) <= 0.05, "shot at %.1f degrees is born at the visible muzzle" % rad_to_deg(angle))
            _require(residual_degrees <= barrel_projectile_residual_limit_degrees + 0.001, "visible barrel/projectile residual %.3f degrees is within %.3f at %s" % [residual_degrees, barrel_projectile_residual_limit_degrees, str(contract.get("upper_direction", ""))])
            shot_residuals.append({
                "frame": frame,
                "upper_direction": str(contract.get("upper_direction", "")),
                "continuous_projectile_degrees": rad_to_deg(projectile_direction.angle()),
                "visible_barrel_tangent_degrees": rad_to_deg(visible_tangent.angle()),
                "residual_degrees": residual_degrees,
                "limit_degrees": barrel_projectile_residual_limit_degrees,
                "projectile_origin": _v2(projectile_origin),
                "authored_muzzle_origin": _v2(authored_origin),
            })
            _set_overlay(
                "TEST 2/3  MOVE E FIXED  |  AIM 360°",
                _runtime_line(actor, preview) + "\n16-direction upper aim/fire; lower gait phase remains continuous",
            )
            captures.append(await _save("ASTER_MOVE_E_AIM_%03d.png" % int(round(rad_to_deg(angle)))))
        else:
            _set_overlay(
                "TEST 2/3  MOVE E FIXED  |  AIM %05.1f°" % rad_to_deg(angle),
                _runtime_line(actor, preview) + "\n16-direction upper aim/fire; lower gait phase remains continuous",
            )
    _make_contact(captures, "ASTER_MOVE_E_AIM_360_16_DIRECTION_CONTACT.png", 4, 4)
    var unique_upper_sectors: Dictionary = {}
    for transition in transitions:
        unique_upper_sectors[int(transition.get("upper_sector", -1))] = true
    _require(lower_e_all_frames, "MOVE E holds lower E for the complete 360-degree aim sweep")
    _require(unique_upper_sectors.size() == UPPER_DIRECTIONS_16.size(), "360-degree sweep visits every sixteen-sector upper direction")
    _require(boundary_samples.size() == UPPER_DIRECTIONS_16.size(), "360-degree sweep measures every reachable hysteresis boundary including the E wrap")
    var minimum_overshoot := 0.0
    var maximum_overshoot := 0.0
    if not boundary_samples.is_empty():
        minimum_overshoot = INF
        maximum_overshoot = -INF
    for sample in boundary_samples:
        var overshoot := float(sample.get("boundary_overshoot_degrees", INF))
        minimum_overshoot = minf(minimum_overshoot, overshoot)
        maximum_overshoot = maxf(maximum_overshoot, overshoot)
        _require(overshoot + 0.001 >= 4.0, "runtime hysteresis holds at least four degrees past each boundary")
        _require(overshoot <= 4.0 + sweep_step_degrees + 0.05, "runtime hysteresis changes within one sampled frame after four degrees")
    _require(shot_residuals.size() == UPPER_DIRECTIONS_16.size(), "one visible barrel/projectile residual is measured per upper direction")
    return {
        "move_direction": "E",
        "aim_sweep_degrees": 360.0,
        "frames": AIM_ROTATION_FRAMES,
        "start_world": _v2(start),
        "end_world": _v2(actor.global_position),
        "distance": actor.global_position.distance_to(start),
        "lower_e_all_frames": lower_e_all_frames,
        "upper_transition_count": transitions.size(),
        "unique_upper_sector_count": unique_upper_sectors.size(),
        "upper_transitions": transitions,
        "hysteresis_boundary_samples": boundary_samples,
        "hysteresis_target_degrees": 4.0,
        "hysteresis_sample_step_degrees": sweep_step_degrees,
        "minimum_boundary_overshoot_degrees": minimum_overshoot,
        "maximum_boundary_overshoot_degrees": maximum_overshoot,
        "visible_barrel_projectile_residuals": shot_residuals,
        "visible_barrel_projectile_limit_degrees": barrel_projectile_residual_limit_degrees,
        "maximum_gait_phase_step_frames": maximum_phase_step,
        "move_cursor_before": phase_before,
        "move_cursor_after": float(preview.get("_move_cursor")),
        "contact_sheet": ProjectSettings.globalize_path(OUT_DIR + "/ASTER_MOVE_E_AIM_360_16_DIRECTION_CONTACT.png"),
    }


func _exercise_stop_reversal(actor: OperatorActor, preview: AsterV4LocomotionPreview) -> Dictionary:
    actor.ammo = actor.magazine_size
    actor.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    await _physics_and_render_frames(18)
    actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    await _physics_and_render_frames(1)
    var before_stop := float(preview.get("_move_cursor"))
    var stop_world_start := actor.global_position
    for frame in range(STOP_FRAMES):
        await _physics_and_render_frames(1)
        _set_overlay(
            "TEST 3/3  RAPID STOP",
            _runtime_line(actor, preview) + "\nZero velocity must stop ground displacement and gait advance",
        )
    var after_stop := float(preview.get("_move_cursor"))
    var stop_world_end := actor.global_position
    var stop_world_displacement := stop_world_end.distance_to(stop_world_start)
    var reversal_start := actor.global_position
    actor.debug_drive(Vector2.LEFT, Vector2.RIGHT)
    var reversal_capture := ""
    for frame in range(REVERSAL_FRAMES):
        await _physics_and_render_frames(1)
        _set_overlay(
            "TEST 3/3  180° REVERSAL  |  MOVE W / AIM E",
            _runtime_line(actor, preview) + "\nLower switches from velocity; upper remains independent",
        )
        if frame == 8:
            actor.debug_fire_once()
            reversal_capture = await _save("ASTER_MOVE_W_AIM_E_REVERSAL.png")
    var contract := preview.debug_contract()
    var stop_phase_delta := absf(after_stop - before_stop)
    _require(actor.global_position.x < reversal_start.x - 60.0, "180-degree reversal moves the CharacterBody west")
    _require(str(contract.get("lower_direction", "")) == "W", "180-degree reversal selects lower W")
    _require(str(contract.get("upper_direction", "")) == "E", "180-degree reversal keeps upper E")
    _require(stop_phase_delta <= 0.05, "zero velocity pauses the move cursor")
    _require(stop_world_displacement <= 0.05, "zero velocity produces zero world displacement during the stop window")
    return {
        "stop_frames": STOP_FRAMES,
        "move_cursor_before_stop": before_stop,
        "move_cursor_after_stop": after_stop,
        "stop_phase_delta": stop_phase_delta,
        "stop_world_start": _v2(stop_world_start),
        "stop_world_end": _v2(stop_world_end),
        "stop_world_displacement": stop_world_displacement,
        "reversal_frames": REVERSAL_FRAMES,
        "reversal_start_world": _v2(reversal_start),
        "reversal_end_world": _v2(actor.global_position),
        "lower_direction": str(contract.get("lower_direction", "")),
        "upper_direction": str(contract.get("upper_direction", "")),
        "capture": reversal_capture,
    }


func _runtime_line(actor: OperatorActor, preview: AsterV4LocomotionPreview) -> String:
    var contract := preview.debug_contract()
    return "LOWER %s (velocity)  |  UPPER %s (aim)  |  speed %.1f  |  world %.1f, %.1f" % [
        str(contract.get("lower_direction", "?")),
        str(contract.get("upper_direction", "?")),
        actor.velocity.length(), actor.global_position.x, actor.global_position.y,
    ]


func _validate_promoted_upper16_bundle(contract: Dictionary) -> Dictionary:
    var manifest := _read_json_dictionary(UPPER_16_MANIFEST_PATH)
    var socket := _read_json_dictionary(TORSO_SOCKET_16_V2_PATH)
    var alignment := _read_json_dictionary(UPPER_16_MUZZLE_ALIGNMENT_PATH)
    var manifest_hash := _sha256(UPPER_16_MANIFEST_PATH)
    var socket_hash := _sha256(TORSO_SOCKET_16_V2_PATH)
    var alignment_hash := _sha256(UPPER_16_MUZZLE_ALIGNMENT_PATH)

    _require(bool(contract.get("upper16_promoted", false)), "acceptance requires the atomically promoted upper16 bundle")
    _require(not bool(contract.get("upper16_safe_fallback_active", true)), "acceptance forbids the eight-way fallback")
    _require(bool(contract.get("upper16_atomic_no_partial_mix", false)), "runtime declares no partial eight/sixteen asset mixing")
    _require(int(contract.get("upper_direction_count", 0)) == 16, "runtime exposes sixteen active upper directions")
    _require(str(contract.get("upper_runtime_asset_family", "")) == "fire_upper_16_no_shoulder_v2", "runtime uses the promoted no-shoulder upper family")
    _require(str(contract.get("torso_socket_path", "")) == TORSO_SOCKET_16_V2_PATH, "runtime uses ASTER_TORSO_SOCKET_16_NO_SHOULDER_V4")
    _require(str(contract.get("upper_alignment_path", "")) == TORSO_SOCKET_16_V2_PATH, "runtime reports the no-shoulder torso socket as upper alignment authority")
    _require(str(contract.get("muzzle_alignment_path", "")) == UPPER_16_MUZZLE_ALIGNMENT_PATH, "runtime uses the sixteen-way muzzle authority")
    _require(str(contract.get("upper_contact_frame_alignment_path", "")) == UPPER_16_MUZZLE_ALIGNMENT_PATH, "runtime contact-frame path is the sixteen-way muzzle authority")
    _require(int(contract.get("fire_upper_texture_count", 0)) == 16, "all sixteen upper atlases are active together")
    _require(int(contract.get("muzzle_alignment_record_count", 0)) == 16, "all sixteen muzzle records are active together")
    _require(bool(contract.get("upper_socket_offsets_per_fire_frame", false)), "the active 8x16 socket supplies offsets per fire frame")
    _require(str(contract.get("independent_aim_pair_qa", "")) == "128_of_128_connected_all_24_lower_phases", "runtime exposes the complete 128-pair socket QA authority")

    _require(not manifest.is_empty(), "upper16 manifest exists and parses")
    _require(int(manifest.get("schema", 0)) == 1 and str(manifest.get("candidate_id", "")) == "fire_upper_16_no_shoulder_v2", "upper16 manifest schema and candidate identity match")
    _require(str(manifest.get("candidate_status", "")) == "PASS", "upper16 manifest candidate_status is PASS")
    _require(bool(manifest.get("promotion_ready", false)), "upper16 manifest promotion_ready is true")
    _require(str(manifest.get("visual_gate", "")) == "PASS", "upper16 manifest visual gate is PASS")
    var manifest_qa: Dictionary = manifest.get("qa", {})
    _require(str(manifest_qa.get("technical_result", "")) == "PASS", "upper16 manifest technical result is PASS")
    _require(bool(manifest.get("runtime_eligible", false)), "upper16 manifest runtime_eligible is true")
    _require(_ordered_strings_equal(manifest.get("directions", []), UPPER_DIRECTIONS_16), "upper16 manifest direction order matches runtime")
    _require(int(manifest.get("frame_count_per_direction", 0)) == 6 and int(manifest.get("atlas_cell", 0)) == 384, "upper16 manifest frame/cell contract matches runtime")

    _require(not socket.is_empty(), "8x16 torso socket exists and parses")
    _require(int(socket.get("schema", 0)) == 2, "8x16 torso socket uses schema 2")
    _require(str(socket.get("candidate_status", "")) == "PASS", "8x16 torso socket candidate status is PASS")
    _require(str(socket.get("visual_gate", "")) == "PASS", "8x16 torso socket visual gate is PASS")
    _require(bool(socket.get("runtime_eligible", false)), "8x16 torso socket is runtime eligible")
    _require(_ordered_strings_equal(socket.get("lower_directions", []), DIRECTIONS), "8x16 socket lower direction order matches velocity sectors")
    _require(_ordered_strings_equal(socket.get("upper_directions", []), UPPER_DIRECTIONS_16), "8x16 socket upper direction order matches aim sectors")
    var dependency: Dictionary = socket.get("dependency", {})
    _require(
        str(dependency.get("candidate_status", "")) == "PASS"
        and bool(dependency.get("promotion_ready", false))
        and str(dependency.get("visual_gate", "")) == "PASS"
        and str(dependency.get("technical_result", "")) == "PASS"
        and bool(dependency.get("technical_pass", false))
        and bool(dependency.get("candidate_or_promotion_pass", false))
        and bool(dependency.get("visual_pass", false))
        and str(dependency.get("gate", "")) == "PASS",
        "8x16 socket dependency is the same fully promoted upper16 manifest",
    )
    var socket_qa: Dictionary = socket.get("qa", {})
    _require(
        int(socket_qa.get("pair_count", 0)) == 128
        and int(socket_qa.get("passed_pairs", 0)) == 128
        and int(socket_qa.get("failed_pairs", -1)) == 0
        and bool(socket_qa.get("all_128_pairs_connected", false)),
        "8x16 socket covers and passes all 128 lower/upper pairs",
    )
    _require(
        bool(socket_qa.get("all_24_lower_phases_scanned", false))
        and int(socket_qa.get("lower_phases_per_pair", 0)) == 24
        and int(socket_qa.get("upper_frames_per_lower_phase", 0)) == 6,
        "8x16 socket scans every lower gait phase and upper fire frame",
    )
    _require(
        int(socket_qa.get("samples_scanned", 0)) == 18432
        and int(socket_qa.get("expected_samples", 0)) == 18432
        and int(socket_qa.get("disconnected_samples", -1)) == 0
        and int(socket_qa.get("unsafe_locked_lower_overwrite_samples", -1)) == 0,
        "8x16 socket passes all 18,432 composition samples without disconnects or lower overwrite",
    )
    _require(
        str(socket_qa.get("safe_seam_gate", "")) == "PASS"
        and str(socket_qa.get("locked_lower_preservation_gate", "")) == "PASS"
        and bool(socket_qa.get("cardinal_same_direction_offsets_zero", false))
        and str(socket_qa.get("technical_gate", "")) == "PASS"
        and str(socket_qa.get("dependency_gate", "")) == "PASS"
        and str(socket_qa.get("promotion_gate", "")) == "PASS",
        "8x16 socket seam, lower preservation, technical, dependency, and promotion gates PASS",
    )

    var sources: Dictionary = socket.get("sources", {})
    _require(str(sources.get("fire_upper_16_manifest", "")) == _project_path(UPPER_16_MANIFEST_PATH), "8x16 socket pins the upper16 manifest path")
    _require(str(sources.get("fire_upper_16_manifest_sha256", "")).to_lower() == manifest_hash, "8x16 socket pins the exact upper16 manifest hash")
    _require(str(sources.get("composite_manifest", "")) == _project_path(COMPOSITE_V6_MANIFEST_PATH), "8x16 socket pins the V6 composite manifest path")
    _require(str(sources.get("composite_manifest_sha256", "")).to_lower() == _sha256(COMPOSITE_V6_MANIFEST_PATH), "8x16 socket pins the exact V6 composite manifest hash")

    _require(not alignment.is_empty(), "sixteen-way muzzle alignment exists and parses")
    _require(int(alignment.get("schema", 0)) == 1 and str(alignment.get("source_asset_family", "")) == "fire_upper_16_no_shoulder_v2", "sixteen-way muzzle schema and source family match")
    _require(str(alignment.get("candidate_status", "")) == "PASS", "sixteen-way muzzle alignment candidate status is PASS")
    _require(_ordered_strings_equal(alignment.get("directions", []), UPPER_DIRECTIONS_16), "sixteen-way muzzle direction order matches runtime")
    var calibration: Dictionary = alignment.get("calibration", {})
    _require(calibration.size() == UPPER_DIRECTIONS_16.size(), "sixteen-way muzzle alignment has exactly sixteen records")
    for direction in UPPER_DIRECTIONS_16:
        var entry = calibration.get(direction, {})
        _require(entry is Dictionary and (entry as Dictionary).has("muzzle_xy") and (entry as Dictionary).has("barrel_tangent_degrees"), "sixteen-way muzzle record %s has socket and visible tangent" % direction)
    _require(str(manifest.get("muzzle_alignment_16_v2", "")) == _project_path(UPPER_16_MUZZLE_ALIGNMENT_PATH), "upper16 manifest pins the muzzle alignment path")
    _require(str(manifest.get("muzzle_alignment_16_v2_sha256", "")).to_lower() == alignment_hash, "upper16 manifest pins the exact muzzle alignment hash")

    var runtime_contract: Dictionary = alignment.get("runtime_contract", {})
    var declared_residual_limit := float(runtime_contract.get("mid_direction_target_tangent_tolerance_degrees", 0.0))
    _require(declared_residual_limit > 0.0 and declared_residual_limit <= VISIBLE_BARREL_PROJECTILE_MAX_RESIDUAL_DEGREES, "muzzle contract residual limit is positive and no looser than six degrees")
    barrel_projectile_residual_limit_degrees = minf(maxf(declared_residual_limit, 0.001), VISIBLE_BARREL_PROJECTILE_MAX_RESIDUAL_DEGREES)

    var direction_outputs: Dictionary = manifest.get("directions_output", {})
    var atlas_hashes: Dictionary = sources.get("atlas_sha256", {})
    var upper_hashes: Dictionary = atlas_hashes.get("upper", {})
    _require(direction_outputs.size() == UPPER_DIRECTIONS_16.size() and upper_hashes.size() == UPPER_DIRECTIONS_16.size(), "manifest and socket each pin sixteen upper atlas hashes")
    for direction in UPPER_DIRECTIONS_16:
        var expected_project_path := "assets/units/operators/aster/fire_upper_16_no_shoulder_v2/%s/ASTER_FIRE_%s_UPPER_16_NO_SHOULDER_V2_ATLAS.png" % [direction, direction]
        var record = direction_outputs.get(direction, {})
        var record_dictionary: Dictionary = record if record is Dictionary else {}
        var actual_hash := _sha256("res://" + expected_project_path)
        _require(str(record_dictionary.get("output_atlas", "")) == expected_project_path, "upper atlas %s path matches the manifest" % direction)
        _require(not actual_hash.is_empty() and str(record_dictionary.get("output_sha256", "")).to_lower() == actual_hash, "upper atlas %s matches its manifest hash" % direction)
        _require(str(upper_hashes.get(direction, "")).to_lower() == actual_hash, "upper atlas %s matches the V2 socket hash" % direction)

    return {
        "manifest": UPPER_16_MANIFEST_PATH,
        "manifest_sha256": manifest_hash,
        "socket": TORSO_SOCKET_16_V2_PATH,
        "socket_sha256": socket_hash,
        "muzzle_alignment": UPPER_16_MUZZLE_ALIGNMENT_PATH,
        "muzzle_alignment_sha256": alignment_hash,
        "upper_direction_count": int(contract.get("upper_direction_count", 0)),
        "upper_texture_count": int(contract.get("fire_upper_texture_count", 0)),
        "muzzle_record_count": int(contract.get("muzzle_alignment_record_count", 0)),
        "socket_pair_count": int(socket_qa.get("pair_count", 0)),
        "socket_samples_scanned": int(socket_qa.get("samples_scanned", 0)),
        "visible_barrel_projectile_limit_degrees": barrel_projectile_residual_limit_degrees,
        "fallback_forbidden": true,
    }


func _serializable_contract(contract: Dictionary) -> Dictionary:
    return {
        "active": bool(contract.get("active", false)),
        "status": str(contract.get("status", "")),
        "lower_direction_count": int(contract.get("lower_direction_count", 0)),
        "upper_direction_count": int(contract.get("upper_direction_count", 0)),
        "lower_direction_authority": str(contract.get("lower_direction_authority", "")),
        "upper_direction_authority": str(contract.get("upper_direction_authority", "")),
        "direction_hysteresis_degrees": float(contract.get("direction_hysteresis_degrees", 0.0)),
        "move_cursor_preserved_on_sector_change": bool(contract.get("move_cursor_preserved_on_sector_change", false)),
        "move_runtime_asset_family": str(contract.get("move_runtime_asset_family", "")),
        "composite_runtime_asset_family": str(contract.get("composite_runtime_asset_family", "")),
        "upper_runtime_asset_family": str(contract.get("upper_runtime_asset_family", "")),
        "upper16_promoted": bool(contract.get("upper16_promoted", false)),
        "upper16_safe_fallback_active": bool(contract.get("upper16_safe_fallback_active", false)),
        "upper16_atomic_no_partial_mix": bool(contract.get("upper16_atomic_no_partial_mix", false)),
        "upper16_failure_reason": str(contract.get("upper16_failure_reason", "")),
        "fire_upper_texture_count": int(contract.get("fire_upper_texture_count", 0)),
        "muzzle_alignment_record_count": int(contract.get("muzzle_alignment_record_count", 0)),
        "upper_socket_offsets_per_fire_frame": bool(contract.get("upper_socket_offsets_per_fire_frame", false)),
        "independent_aim_pair_qa": str(contract.get("independent_aim_pair_qa", "")),
        "torso_socket_path": str(contract.get("torso_socket_path", "")),
        "muzzle_alignment_path": str(contract.get("muzzle_alignment_path", "")),
        "torso_socket_loaded": bool(contract.get("torso_socket_loaded", false)),
        "torso_bridge_loaded": bool(contract.get("torso_bridge_loaded", false)),
        "muzzle_alignment_loaded": bool(contract.get("muzzle_alignment_loaded", false)),
    }


func _all_move_cases_match() -> bool:
    for case in evidence["aim_e_move_8"]:
        if not bool(case.get("direction_match", false)) or not bool(case.get("upper_match", false)):
            return false
    return true


func _normalized_speed_gate() -> bool:
    var speeds: Array[float] = []
    for case in evidence["aim_e_move_8"]:
        speeds.append(float(case.get("mean_speed", 0.0)))
    if speeds.is_empty():
        return false
    var minimum: float = float(speeds.min())
    var maximum: float = float(speeds.max())
    var passed: bool = minimum > 1.0 and maximum / minimum <= 1.02
    _require(passed, "cardinal and diagonal CharacterBody speeds are normalized within two percent")
    return passed


func _make_overlay() -> void:
    var layer := CanvasLayer.new()
    layer.layer = 200
    root.add_child(layer)
    var panel := ColorRect.new()
    panel.position = Vector2(18.0, 18.0)
    panel.size = Vector2(1160.0, 116.0)
    panel.color = Color(0.005, 0.018, 0.026, 0.88)
    panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    layer.add_child(panel)
    overlay_title = Label.new()
    overlay_title.position = Vector2(34.0, 28.0)
    overlay_title.add_theme_color_override("font_color", Color("66f4ff"))
    overlay_title.add_theme_font_size_override("font_size", 28)
    layer.add_child(overlay_title)
    overlay_detail = Label.new()
    overlay_detail.position = Vector2(34.0, 66.0)
    overlay_detail.add_theme_color_override("font_color", Color("dceaf0"))
    overlay_detail.add_theme_font_size_override("font_size", 20)
    layer.add_child(overlay_detail)


func _set_overlay(title: String, detail: String) -> void:
    overlay_title.text = title
    overlay_detail.text = detail


func _save(filename: String) -> String:
    await RenderingServer.frame_post_draw
    var path := OUT_DIR + "/" + filename
    var image := root.get_viewport().get_texture().get_image()
    _require(image != null and not image.is_empty(), "capture returns a decodable image for " + filename)
    if image == null or image.is_empty():
        return ""
    _require(image.get_size() == VIEWPORT_SIZE, "capture is native 1920x1080 for " + filename)
    if image.get_size() != VIEWPORT_SIZE:
        return ""
    var error := image.save_png(ProjectSettings.globalize_path(path))
    _require(error == OK, "capture writes " + filename)
    return ProjectSettings.globalize_path(path)


func _make_contact(paths: Array[String], filename: String, columns: int, rows: int) -> void:
    if paths.size() != columns * rows:
        _fail("contact %s expected %d cells, got %d" % [filename, columns * rows, paths.size()])
        return
    var source := Image.load_from_file(paths[0])
    if source == null or source.is_empty():
        _fail("contact %s could not read source" % filename)
        return
    if source.get_size() != VIEWPORT_SIZE:
        _fail("contact %s source is not native 1920x1080" % filename)
        return
    var cell_size := Vector2i(CONTACT_SIZE.x / columns, CONTACT_SIZE.y / rows)
    var contact := Image.create(CONTACT_SIZE.x, CONTACT_SIZE.y, false, Image.FORMAT_RGBA8)
    contact.fill(Color("071117"))
    for index in range(paths.size()):
        var image := Image.load_from_file(paths[index])
        if image == null or image.is_empty() or image.get_size() != VIEWPORT_SIZE:
            _fail("contact %s has invalid cell %d" % [filename, index])
            return
        var scale := minf(float(cell_size.x) / float(image.get_width()), float(cell_size.y) / float(image.get_height()))
        var scaled_size := Vector2i(
            maxi(1, int(round(float(image.get_width()) * scale))),
            maxi(1, int(round(float(image.get_height()) * scale))),
        )
        image.resize(scaled_size.x, scaled_size.y, Image.INTERPOLATE_LANCZOS)
        var cell_origin := Vector2i(index % columns, int(index / columns)) * cell_size
        var inset := (cell_size - scaled_size) / 2
        contact.blit_rect(image, Rect2i(Vector2i.ZERO, scaled_size), cell_origin + inset)
    var error := contact.save_png(ProjectSettings.globalize_path(OUT_DIR + "/" + filename))
    _require(error == OK, "contact writes " + filename)


func _write_json(filename: String, payload: Dictionary) -> void:
    var file := FileAccess.open(OUT_DIR + "/" + filename, FileAccess.WRITE)
    if file == null:
        _fail("could not write " + filename)
        return
    file.store_string(JSON.stringify(payload, "  ") + "\n")
    file.close()


func _physics_and_render_frames(count: int) -> void:
    for _index in range(count):
        await physics_frame
        await process_frame


func _frames(count: int) -> void:
    for _index in range(count):
        await process_frame


func _gait_forward_delta(before: float, after: float) -> float:
    return fposmod(after - before, GAIT_PHASE_FRAME_COUNT)


func _latest_projectile_for_actor(actor: OperatorActor) -> Node2D:
    var latest: Node2D = null
    var latest_id := -1
    for child in root.get_children():
        if child is Node2D and child.get_script() == PROJECTILE_SCRIPT and child.get("owner_actor") == actor:
            var candidate := child as Node2D
            if candidate.get_instance_id() > latest_id:
                latest = candidate
                latest_id = candidate.get_instance_id()
    return latest


func _latest_projectile_id_for_actor(actor: OperatorActor) -> int:
    var projectile := _latest_projectile_for_actor(actor)
    return projectile.get_instance_id() if projectile else -1


func _project_path(path: String) -> String:
    return path.trim_prefix("res://")


func _sha256(path: String) -> String:
    if not FileAccess.file_exists(path):
        return ""
    return FileAccess.get_sha256(path).to_lower()


func _ordered_strings_equal(raw: Variant, expected: Array[String]) -> bool:
    if not raw is Array:
        return false
    var values := raw as Array
    if values.size() != expected.size():
        return false
    for index in range(expected.size()):
        if str(values[index]) != expected[index]:
            return false
    return true


func _read_json_dictionary(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    file.close()
    return parsed if parsed is Dictionary else {}


func _mean(values: Array[float]) -> float:
    if values.is_empty():
        return 0.0
    var total := 0.0
    for value in values:
        total += value
    return total / float(values.size())


func _v2(value: Vector2) -> Array[float]:
    return [value.x, value.y]


func _require(condition: bool, message: String) -> void:
    if not condition:
        _fail(message)


func _fail(message: String) -> void:
    failed = true
    failures.append(message)
    push_error(message)


func _finish(stage: Node, actor: OperatorActor, previous_setting: bool) -> void:
    if actor:
        actor.debug_stop_drive()
    ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
    if stage:
        stage.queue_free()
    await _frames(3)
    print("ASTER_MOVE_AIM_RUNTIME_ACCEPTANCE: " + ("FAIL" if failed else "PASS"))
    quit(1 if failed else 0)
