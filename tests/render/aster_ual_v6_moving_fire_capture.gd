extends SceneTree

## Non-headless proof for the current ASTER moving-fire contract:
## immediate 0.06 s primary_fired muzzle burst, Fire contact frame 2,
## immutable shot-sector/continuous-aim/socket snapshots, shared projectile
## birth socket, velocity-scaled UAL cadence, and advancing firing legs.
## The harness changes no gameplay timing, projectile speed, or collision.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const OUT_DIR := "res://artifacts/aster_ual_v6_moving_fire_capture"
const FEATURE_SETTING := "sable_visuals/aster_v4_locomotion_preview"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
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
# One shot 0.4 degrees before every eight-way sector boundary. Retargeting by
# +0.8 degrees crosses the boundary while the short flash must stay immutable.
const OFF_AXIS_BOUNDARY_DEGREES: Array[float] = [
    22.1, 67.1, 112.1, 157.1, 202.1, 247.1, 292.1, 337.1,
]
const BOUNDARY_CROSS_DELTA_DEGREES := 0.8
const REPRESENTATIVE_CENTER_CASES: Array[int] = [0, 5]
const VIEWPORT_SIZE := Vector2i(1920, 1080)
const CONTACT_CROP := Rect2i(480, 220, 960, 640)
const CONTACT_CELL := Vector2i(480, 320)
const CONTACT_MIN_SIZE := Vector2i(1920, 1080)

var failed := false
var failures: Array[String] = []
var evidence: Dictionary = {
    "harness": "ASTER UAL V6 articulated legs + costume continuity + muzzle alignment capture",
    "runtime_changes_made_by_harness": false,
    "projectile_speed_override": false,
    "gameplay_timing_override": false,
    "collision_override": false,
    "capture_render_pause_only": true,
    "native_review_resolution": [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y],
    "contact_minimum_resolution": [CONTACT_MIN_SIZE.x, CONTACT_MIN_SIZE.y],
    "contact_cells_are_downsampled_overview_only": true,
    "native_runtime_captures_retained_for_actual_scale_review": true,
    "primary_fired_immediate_burst_exercised": true,
    "same_tick_aim_fire_sector_switch_exercised": true,
    "center_cases": [],
    "off_axis_boundary_cases": [],
}
var overlay_layer: CanvasLayer
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
    await _frames(16)
    for enemy in get_nodes_in_group("m3_enemies"):
        enemy.queue_free()
    await _frames(2)

    var actor := stage.squad.get_active_operator() as OperatorActor
    var preview := actor.get_node_or_null("AsterV4LocomotionPreview") as AsterV4LocomotionPreview if actor else null
    if actor == null or actor.operator_id != "CHR_PROTO_01" or preview == null:
        _fail("could not resolve active ASTER V6 preview")
        await _finish(stage, actor, previous_setting)
        return

    var initial_contract := preview.debug_contract()
    _require(bool(initial_contract.get("active", false)), "ASTER preview is active")
    _require(str(initial_contract.get("move_runtime_asset_family", "")) == "move_360_ual_v6", "UAL V6 move family is active")
    _require(str(initial_contract.get("composite_runtime_asset_family", "")) == "composite_fire_v6", "V6 moving-fire composite is active")
    _require(bool(initial_contract.get("split_fire_set_valid", false)), "all eight split moving-fire sets are valid")
    _require(int(initial_contract.get("move_frame_count", 0)) == 24, "UAL V6 exposes 24 move frames")
    _require(is_equal_approx(float(initial_contract.get("move_fps", 0.0)), 24.0), "UAL V6 owns the 24 fps reference cadence")
    _require(str(initial_contract.get("move_cadence_authority", "")) == "velocity_scaled_from_walk_speed", "move cadence is velocity-scaled")
    _require(str(initial_contract.get("muzzle_vfx_timing_authority", "")) == "primary_fired_immediate_burst", "muzzle timing is the immediate shot event")
    _require(is_equal_approx(float(initial_contract.get("muzzle_vfx_duration", 0.0)), 0.06), "muzzle burst duration is 0.06 seconds")
    _require(int(initial_contract.get("fire_contact_frame", -1)) == 2, "fire presentation contact frame is 2")

    evidence["godot_version"] = str(Engine.get_version_info().get("string", "unknown"))
    evidence["rendering_driver"] = RenderingServer.get_current_rendering_driver_name()
    evidence["video_adapter"] = RenderingServer.get_video_adapter_name()
    evidence["viewport"] = [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y]
    evidence["capture_command"] = "Godot_v4.7.1-stable_win64_console.exe --display-driver windows --rendering-method gl_compatibility --rendering-driver opengl3 --script res://tests/render/aster_ual_v6_moving_fire_capture.gd"
    evidence["idle_runtime_asset_family"] = str(initial_contract.get("idle_runtime_asset_family", ""))
    evidence["move_runtime_asset_family"] = str(initial_contract.get("move_runtime_asset_family", ""))
    evidence["composite_runtime_asset_family"] = str(initial_contract.get("composite_runtime_asset_family", ""))
    evidence["split_fire_set_valid"] = bool(initial_contract.get("split_fire_set_valid", false))
    evidence["muzzle_vfx_timing_authority"] = str(initial_contract.get("muzzle_vfx_timing_authority", ""))
    evidence["muzzle_vfx_duration_seconds"] = float(initial_contract.get("muzzle_vfx_duration", 0.0))
    evidence["fire_contact_frame"] = int(initial_contract.get("fire_contact_frame", -1))

    for operator in stage.squad.operators:
        operator.visible = operator == actor
    actor.set_movement_bounds(Rect2(360.0, 160.0, 1480.0, 680.0))

    var camera := stage.get_node("Camera2D") as Camera2D
    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as Node
    if camera_presentation:
        camera_presentation.set_process(false)
    camera.position_smoothing_enabled = false
    camera.zoom = Vector2.ONE * 1.55

    evidence["velocity_cadence"] = await _capture_velocity_cadence(actor, preview, camera)
    evidence["leg_phase_contact"] = await _capture_leg_phase_contact(actor, preview, camera)

    var center_shot_paths: Array[String] = []
    var center_birth_paths: Array[String] = []
    var temporal_paths: Array[String] = []
    for sector in range(DIRECTIONS.size()):
        var center_result := await _capture_case(
            actor, preview, camera,
            "CENTER_%s" % DIRECTIONS[sector],
            VECTORS[sector],
            VECTORS[posmod(sector + 2, DIRECTIONS.size())],
            sector,
            sector in REPRESENTATIVE_CENTER_CASES,
        )
        evidence["center_cases"].append(center_result)
        center_birth_paths.append(str(center_result.get("birth_capture", "")))
        center_shot_paths.append(str(center_result.get("shot_capture", "")))
        if sector in REPRESENTATIVE_CENTER_CASES:
            for key in ["birth_capture", "shot_capture", "late_capture"]:
                temporal_paths.append(str(center_result.get(key, "")))

    var off_axis_shot_paths: Array[String] = []
    var off_axis_snapshot_paths: Array[String] = []
    var off_axis_pair_paths: Array[String] = []
    for index in range(OFF_AXIS_BOUNDARY_DEGREES.size()):
        var shot_degrees := OFF_AXIS_BOUNDARY_DEGREES[index]
        var retarget_degrees := shot_degrees + BOUNDARY_CROSS_DELTA_DEGREES
        var shot_aim := Vector2.from_angle(deg_to_rad(shot_degrees))
        var retarget_aim := Vector2.from_angle(deg_to_rad(retarget_degrees))
        var off_axis_result := await _capture_case(
            actor, preview, camera,
            "BOUNDARY_%03d" % int(round(shot_degrees * 10.0)),
            shot_aim, retarget_aim,
            index + DIRECTIONS.size(), false,
        )
        off_axis_result["shot_angle_degrees"] = shot_degrees
        off_axis_result["retarget_angle_degrees"] = retarget_degrees
        off_axis_result["crosses_sector_boundary"] = int(off_axis_result.get("shot_sector", -1)) != int(off_axis_result.get("retarget_sector", -1))
        _require(bool(off_axis_result["crosses_sector_boundary"]), "off-axis case %.1f crosses an authored sector boundary" % shot_degrees)
        evidence["off_axis_boundary_cases"].append(off_axis_result)
        var shot_path := str(off_axis_result.get("shot_capture", ""))
        var snapshot_path := str(off_axis_result.get("snapshot_capture", ""))
        off_axis_shot_paths.append(shot_path)
        off_axis_snapshot_paths.append(snapshot_path)
        off_axis_pair_paths.append(shot_path)
        off_axis_pair_paths.append(snapshot_path)

    _make_required_contact(center_shot_paths, "ASTER_UAL_V6_8_DIRECTION_MOVING_FIRE_CONTACT.png", 4, 2, 8, "center moving-fire")
    _make_required_contact(center_birth_paths, "ASTER_UAL_V6_8_DIRECTION_SOCKET_BIRTH_CONTACT.png", 4, 2, 8, "center socket-birth")
    _make_required_contact(temporal_paths, "ASTER_UAL_V6_MOVING_FIRE_TEMPORAL_CONTACT.png", 3, 2, 6, "moving-fire temporal")
    _make_required_contact(off_axis_shot_paths, "ASTER_UAL_V6_OFF_AXIS_BOUNDARY_SHOT_CONTACT.png", 4, 2, 8, "off-axis shot")
    _make_required_contact(off_axis_snapshot_paths, "ASTER_UAL_V6_OFF_AXIS_BOUNDARY_SNAPSHOT_CONTACT.png", 4, 2, 8, "off-axis snapshot")
    _make_required_contact(off_axis_pair_paths, "ASTER_UAL_V6_OFF_AXIS_BOUNDARY_PAIRED_CONTACT.png", 4, 4, 16, "off-axis paired")

    evidence["all_eight_center_projectiles_match_authored_socket"] = _all_case_bool("center_cases", "projectile_birth_matches_socket")
    evidence["all_eight_center_flashes_match_socket_at_shot"] = _all_case_bool("center_cases", "flash_matches_shot_socket")
    evidence["all_eight_center_flashes_follow_continuous_aim"] = _all_case_bool("center_cases", "flash_angle_matches_continuous_aim")
    evidence["all_eight_center_snapshots_do_not_teleport"] = _all_case_bool("center_cases", "snapshot_does_not_teleport")
    evidence["all_eight_center_lower_bodies_advance"] = _all_case_bool("center_cases", "lower_body_advanced_during_fire")
    evidence["all_eight_off_axis_projectiles_match_authored_socket"] = _all_case_bool("off_axis_boundary_cases", "projectile_birth_matches_socket")
    evidence["all_eight_off_axis_flashes_match_socket_at_shot"] = _all_case_bool("off_axis_boundary_cases", "flash_matches_shot_socket")
    evidence["all_eight_off_axis_flashes_follow_continuous_aim"] = _all_case_bool("off_axis_boundary_cases", "flash_angle_matches_continuous_aim")
    evidence["all_eight_off_axis_snapshots_do_not_teleport"] = _all_case_bool("off_axis_boundary_cases", "snapshot_does_not_teleport")
    evidence["all_eight_off_axis_lower_bodies_advance"] = _all_case_bool("off_axis_boundary_cases", "lower_body_advanced_during_fire")
    evidence["all_eight_off_axis_cases_cross_sector_boundaries"] = _all_case_bool("off_axis_boundary_cases", "crosses_sector_boundary")
    evidence["center_moving_fire_contact_sheet"] = _global_output("ASTER_UAL_V6_8_DIRECTION_MOVING_FIRE_CONTACT.png")
    evidence["center_socket_birth_contact_sheet"] = _global_output("ASTER_UAL_V6_8_DIRECTION_SOCKET_BIRTH_CONTACT.png")
    evidence["temporal_contact_sheet"] = _global_output("ASTER_UAL_V6_MOVING_FIRE_TEMPORAL_CONTACT.png")
    evidence["off_axis_shot_contact_sheet"] = _global_output("ASTER_UAL_V6_OFF_AXIS_BOUNDARY_SHOT_CONTACT.png")
    evidence["off_axis_snapshot_contact_sheet"] = _global_output("ASTER_UAL_V6_OFF_AXIS_BOUNDARY_SNAPSHOT_CONTACT.png")
    evidence["off_axis_paired_contact_sheet"] = _global_output("ASTER_UAL_V6_OFF_AXIS_BOUNDARY_PAIRED_CONTACT.png")
    evidence["result"] = "FAIL" if failed else "PASS"
    evidence["failures"] = failures
    _write_json("ASTER_UAL_V6_MOVING_FIRE_EVIDENCE.json", evidence)
    await _finish(stage, actor, previous_setting)


func _capture_leg_phase_contact(actor: OperatorActor, preview: AsterV4LocomotionPreview, camera: Camera2D) -> Dictionary:
    var phases: Array[int] = [0, 4, 8, 12, 16, 20]
    var paths: Array[String] = []
    var captured_sectors: Array[int] = []
    var sector_sync_pass := true
    for sector in range(DIRECTIONS.size()):
        actor.global_position = Vector2(1100.0, 500.0)
        actor.debug_drive(Vector2.RIGHT, VECTORS[sector])
        await _physics_frames(2)
        # `_physics_frames()` resumes before the following process tick.  The
        # preview normally consumes `actor.facing_sector` in `_process()`, so a
        # direct evidence capture here used the previous sector and produced a
        # one-row-stale contact sheet.  Synchronize explicitly before selecting
        # a source atlas and record the resolved sector as part of the proof.
        preview.call("_sync_sector", true)
        var resolved_sector := int(preview.debug_contract().get("sector", -1))
        captured_sectors.append(resolved_sector)
        var row_synced := resolved_sector == sector
        sector_sync_pass = sector_sync_pass and row_synced
        _require(row_synced, "V6 leg contact row %s resolves authored sector %d" % [DIRECTIONS[sector], sector])
        camera.global_position = actor.global_position
        for phase in phases:
            preview.set("_fire_elapsed", -1.0)
            preview.set("_move_cursor", float(phase))
            preview.call("_show_move_frame", phase)
            _set_overlay(
                "%s  |  V6 LEG PHASE F%02d" % [DIRECTIONS[sector], phase],
                "UAL1 Jog_Fwd_Loop  |  articulated lower body  |  weapon corridor locked",
            )
            paths.append(await _save("ASTER_UAL_V6_%s_LEG_F%02d.png" % [DIRECTIONS[sector], phase]))
    var contact_name := "ASTER_UAL_V6_8_DIRECTION_LEG_PHASE_CONTACT.png"
    _make_required_contact(paths, contact_name, phases.size(), DIRECTIONS.size(), DIRECTIONS.size() * phases.size(), "V6 leg phase")
    return {
        "directions": DIRECTIONS,
        "captured_sectors": captured_sectors,
        "sector_sync_pass": sector_sync_pass,
        "phases": phases,
        "frame_count": paths.size(),
        "contact_sheet": _global_output(contact_name),
        "visual_gate": "USER_REVIEW_REQUIRED",
    }


func _capture_velocity_cadence(actor: OperatorActor, preview: AsterV4LocomotionPreview, camera: Camera2D) -> Dictionary:
    actor.global_position = Vector2(1100.0, 500.0)
    camera.global_position = actor.global_position
    actor.debug_drive(Vector2.RIGHT * 0.5, Vector2.RIGHT)
    await _physics_frames(4)
    await _frames(2)
    var slow_before := float(preview.debug_contract().get("move_phase_advance_total", 0.0))
    await _frames(12)
    var slow_contract := preview.debug_contract()
    var slow_delta := float(slow_contract.get("move_phase_advance_total", 0.0)) - slow_before
    var slow_scale := float(slow_contract.get("move_cadence_scale", 0.0))

    actor.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    await _physics_frames(4)
    await _frames(2)
    var full_before := float(preview.debug_contract().get("move_phase_advance_total", 0.0))
    await _frames(12)
    var full_contract := preview.debug_contract()
    var full_delta := float(full_contract.get("move_phase_advance_total", 0.0)) - full_before
    var full_scale := float(full_contract.get("move_cadence_scale", 0.0))
    var scale_pass := slow_scale > 0.45 and slow_scale < 0.55 and full_scale > 0.95 and full_scale < 1.05
    var phase_pass := slow_delta > 0.0 and full_delta > slow_delta * 1.65
    _require(scale_pass, "half/full movement report approximately 0.5x/1.0x UAL cadence")
    _require(phase_pass, "full-speed UAL phase advances materially faster than half-speed phase")
    return {
        "authority": str(full_contract.get("move_cadence_authority", "")),
        "slow_input_magnitude": 0.5,
        "slow_cadence_scale": slow_scale,
        "slow_phase_advance": slow_delta,
        "full_input_magnitude": 1.0,
        "full_cadence_scale": full_scale,
        "full_phase_advance": full_delta,
        "scale_pass": scale_pass,
        "phase_ratio_full_over_slow": full_delta / slow_delta if slow_delta > 0.0 else 0.0,
        "phase_pass": phase_pass,
    }


func _capture_case(
    actor: OperatorActor,
    preview: AsterV4LocomotionPreview,
    camera: Camera2D,
    case_label: String,
    shot_aim: Vector2,
    retarget_aim: Vector2,
    case_index: int,
    capture_late: bool,
) -> Dictionary:
    _clear_projectiles()
    await process_frame
    actor.global_position = Vector2(1100.0, 500.0)
    actor.debug_drive(Vector2.RIGHT, shot_aim)
    await _physics_frames(4 + posmod(case_index, 3))
    await process_frame
    camera.global_position = actor.global_position
    var shot_sector := _expected_sector(shot_aim)
    var retarget_sector := _expected_sector(retarget_aim)
    var prepared_contract := preview.debug_contract()
    _require(int(prepared_contract.get("sector", -1)) == shot_sector, "%s raster is prepared on the shot sector" % case_label)
    var lower_frame_before := _lower_frame(preview)
    var cursor_before := float(preview.get("_move_cursor"))
    var phase_before := float(prepared_contract.get("move_phase_advance_total", 0.0))
    var moving_advances_before := int(prepared_contract.get("moving_fire_move_advance_count", 0))
    var trigger_count_before := int(prepared_contract.get("muzzle_vfx_trigger_count", 0))

    var stale_sector := posmod(shot_sector + 4, DIRECTIONS.size())
    actor.facing_sector = stale_sector
    actor.aim_world = shot_aim.normalized()
    var fired := actor.debug_fire_once()
    _require(fired, "%s fires while moving" % case_label)
    _require(actor.facing_sector == shot_sector, "%s resolves stale facing on the shot tick" % case_label)

    var immediate_contract := preview.debug_contract()
    var shot_local := preview.get_authored_muzzle_local_position()
    var shot_global := preview.get_authored_muzzle_global_position()
    var flash_global := Vector2(immediate_contract.get("muzzle_vfx_global_position", Vector2.ZERO))
    var flash_local := preview.to_local(flash_global)
    var flash_rotation := float(immediate_contract.get("muzzle_vfx_rotation", 99.0))
    var flash_socket_error := flash_global.distance_to(shot_global)
    var flash_local_error := flash_local.distance_to(shot_local)
    var flash_angle_error := absf(angle_difference(flash_rotation, shot_aim.angle()))
    var fire_frame_immediate := int(floor(float(immediate_contract.get("fire_elapsed", -1.0)) * float(immediate_contract.get("fire_fps", 0.0))))
    _require(bool(immediate_contract.get("muzzle_vfx_visible", false)), "%s flash is visible on the exact trigger tick" % case_label)
    _require(int(immediate_contract.get("muzzle_vfx_trigger_count", 0)) == trigger_count_before + 1, "%s trigger starts exactly one muzzle burst" % case_label)
    _require(int(immediate_contract.get("muzzle_vfx_shot_sector", -1)) == shot_sector, "%s flash snapshots the shot sector" % case_label)
    _require(Vector2(immediate_contract.get("muzzle_vfx_shot_local", Vector2.ZERO)).distance_to(shot_local) <= 0.05, "%s flash snapshots the authored socket" % case_label)
    _require(flash_socket_error <= 0.05 and flash_local_error <= 0.05, "%s flash begins at the authored muzzle" % case_label)
    _require(flash_angle_error <= 0.001, "%s flash follows continuous shot aim" % case_label)
    _require(fire_frame_immediate == int(immediate_contract.get("fire_contact_frame", -1)), "%s fire begins immediately on contact frame 2" % case_label)

    var projectile := _find_actor_projectile(actor)
    _require(projectile != null, "%s spawns a projectile" % case_label)
    var birth_error := INF
    var projectile_angle_error := INF
    if projectile:
        birth_error = projectile.global_position.distance_to(shot_global)
        projectile_angle_error = absf(angle_difference(projectile.direction.angle(), shot_aim.angle()))
    var birth_matches := projectile != null and birth_error <= 0.05 and projectile_angle_error <= 0.001
    _require(birth_matches, "%s projectile is born at the authored socket with continuous aim" % case_label)
    _set_overlay(
        "%s  |  IMMEDIATE SOCKET BIRTH" % case_label,
        "contact F2  |  birth %.4f px  |  flash %.4f px  |  aim %.1f deg" % [birth_error, flash_socket_error, rad_to_deg(shot_aim.angle())],
    )
    camera.global_position = actor.global_position
    var birth_path := await _save("ASTER_UAL_V6_%s_BIRTH.png" % case_label)

    actor.aim_world = retarget_aim.normalized()
    actor.facing_sector = retarget_sector
    actor.debug_drive(Vector2.RIGHT, retarget_aim)
    var retarget_contract := preview.debug_contract()
    var retarget_flash_global := Vector2(retarget_contract.get("muzzle_vfx_global_position", Vector2.ZERO))
    var retarget_flash_rotation := float(retarget_contract.get("muzzle_vfx_rotation", 99.0))
    var immediate_snapshot_position_error := retarget_flash_global.distance_to(flash_global)
    var immediate_snapshot_angle_error := absf(angle_difference(retarget_flash_rotation, flash_rotation))
    var immediate_snapshot_pass := immediate_snapshot_position_error <= 0.05 and immediate_snapshot_angle_error <= 0.001
    _require(immediate_snapshot_pass, "%s flash does not teleport on immediate aim retarget" % case_label)

    actor.aim_world = shot_aim.normalized()
    actor.facing_sector = shot_sector
    actor.debug_drive(Vector2.RIGHT, shot_aim)
    await process_frame
    camera.global_position = actor.global_position
    var shot_contract := preview.debug_contract()
    var rendered_flash_global := Vector2(shot_contract.get("muzzle_vfx_global_position", Vector2.ZERO))
    var rendered_socket_global := preview.to_global(shot_local)
    var rendered_flash_error := rendered_flash_global.distance_to(rendered_socket_global)
    var rendered_fire_frame := int(floor(float(shot_contract.get("fire_elapsed", -1.0)) * float(shot_contract.get("fire_fps", 0.0))))
    var moving_layers_active := (
        bool(shot_contract.get("moving_fire_active", false))
        and bool(shot_contract.get("fire_upper_visible", false))
        and str(shot_contract.get("lower_body_atlas_selected", "")) == "composite_fire_v6/move_lower"
    )
    _require(bool(shot_contract.get("muzzle_vfx_visible", false)), "%s immediate burst survives the first rendered contact frame" % case_label)
    _require(rendered_flash_error <= 0.05, "%s rendered flash remains on the snapshotted shot socket" % case_label)
    _require(rendered_fire_frame >= 2, "%s first rendered fire pose is contact/recoil, never pre-fire" % case_label)
    _require(moving_layers_active, "%s uses moving lower + Fire upper on the first render" % case_label)
    _set_overlay(
        "%s  |  CONTACT F%d + MOVING LOWER" % [case_label, rendered_fire_frame],
        "primary_fired burst  |  flash/socket %.4f px  |  continuous %.1f deg" % [rendered_flash_error, rad_to_deg(shot_aim.angle())],
    )
    var shot_path := await _save("ASTER_UAL_V6_%s_SHOT.png" % case_label)

    var rendered_flash_local := preview.to_local(rendered_flash_global)
    var rendered_flash_rotation := float(shot_contract.get("muzzle_vfx_rotation", 99.0))
    actor.aim_world = retarget_aim.normalized()
    actor.facing_sector = retarget_sector
    actor.debug_drive(Vector2.RIGHT, retarget_aim)
    var visual_snapshot_contract := preview.debug_contract()
    var visual_snapshot_global := Vector2(visual_snapshot_contract.get("muzzle_vfx_global_position", Vector2.ZERO))
    var visual_snapshot_local := preview.to_local(visual_snapshot_global)
    var visual_snapshot_rotation := float(visual_snapshot_contract.get("muzzle_vfx_rotation", 99.0))
    var snapshot_local_error := visual_snapshot_local.distance_to(rendered_flash_local)
    var snapshot_angle_error := absf(angle_difference(visual_snapshot_rotation, rendered_flash_rotation))
    var snapshot_pass := immediate_snapshot_pass and snapshot_local_error <= 0.05 and snapshot_angle_error <= 0.001
    _require(snapshot_pass, "%s visible flash preserves fired socket/angle after retarget" % case_label)
    _set_overlay(
        "%s  |  IMMEDIATE RETARGET SNAPSHOT" % case_label,
        "aim %.1f -> %.1f deg  |  flash delta %.4f px / %.4f rad" % [rad_to_deg(shot_aim.angle()), rad_to_deg(retarget_aim.angle()), snapshot_local_error, snapshot_angle_error],
    )
    var snapshot_path := await _save("ASTER_UAL_V6_%s_SNAPSHOT.png" % case_label)

    actor.aim_world = shot_aim.normalized()
    actor.facing_sector = shot_sector
    actor.debug_drive(Vector2.RIGHT, shot_aim)
    var lower_frame_after := _lower_frame(preview)
    var phase_after := float(shot_contract.get("move_phase_advance_total", phase_before))
    var advance_count_after := int(shot_contract.get("moving_fire_move_advance_count", moving_advances_before))
    for _index in range(8):
        if lower_frame_after != lower_frame_before and phase_after > phase_before + 0.2 and advance_count_after > moving_advances_before:
            break
        await process_frame
        var advancing_contract := preview.debug_contract()
        lower_frame_after = _lower_frame(preview)
        phase_after = float(advancing_contract.get("move_phase_advance_total", phase_before))
        advance_count_after = int(advancing_contract.get("moving_fire_move_advance_count", moving_advances_before))
    var lower_advanced := lower_frame_after != lower_frame_before and phase_after > phase_before + 0.2 and advance_count_after > moving_advances_before
    _require(lower_advanced, "%s UAL lower-body phase advances while firing" % case_label)

    var late_path := ""
    if capture_late:
        camera.global_position = actor.global_position
        var late_contract := preview.debug_contract()
        _set_overlay(
            "%s  |  LATER MOVING-FIRE PHASE" % case_label,
            "lower F%d -> F%d  |  phase +%.3f  |  cadence %.3fx" % [lower_frame_before, lower_frame_after, phase_after - phase_before, float(late_contract.get("move_cadence_scale", 0.0))],
        )
        late_path = await _save("ASTER_UAL_V6_%s_LATE.png" % case_label)

    var result := {
        "case": case_label,
        "shot_sector": shot_sector,
        "shot_sector_name": DIRECTIONS[shot_sector],
        "stale_sector_before_fire": stale_sector,
        "retarget_sector": retarget_sector,
        "shot_aim": [shot_aim.x, shot_aim.y],
        "shot_angle_degrees": rad_to_deg(shot_aim.angle()),
        "retarget_aim": [retarget_aim.x, retarget_aim.y],
        "retarget_angle_degrees": rad_to_deg(retarget_aim.angle()),
        "same_tick_sector_resolved": actor.facing_sector == shot_sector,
        "fire_contact_frame_immediate": fire_frame_immediate,
        "fire_frame_first_render": rendered_fire_frame,
        "muzzle_trigger_count_delta": int(immediate_contract.get("muzzle_vfx_trigger_count", 0)) - trigger_count_before,
        "muzzle_duration_seconds": float(immediate_contract.get("muzzle_vfx_duration", 0.0)),
        "authored_muzzle_local": [shot_local.x, shot_local.y],
        "authored_muzzle_global_at_birth": [shot_global.x, shot_global.y],
        "projectile_birth_error_px": birth_error,
        "projectile_angle_error_radians": projectile_angle_error,
        "projectile_birth_matches_socket": birth_matches,
        "flash_socket_error_px_at_trigger": flash_socket_error,
        "flash_local_error_px_at_trigger": flash_local_error,
        "flash_socket_error_px_first_render": rendered_flash_error,
        "flash_angle_error_radians": flash_angle_error,
        "flash_matches_shot_socket": flash_socket_error <= 0.05 and rendered_flash_error <= 0.05,
        "flash_angle_matches_continuous_aim": flash_angle_error <= 0.001,
        "immediate_retarget_position_error_px": immediate_snapshot_position_error,
        "immediate_retarget_angle_error_radians": immediate_snapshot_angle_error,
        "visual_snapshot_local_error_px": snapshot_local_error,
        "visual_snapshot_angle_error_radians": snapshot_angle_error,
        "snapshot_does_not_teleport": snapshot_pass,
        "moving_fire_layers_active": moving_layers_active,
        "lower_body_advanced_during_fire": lower_advanced,
        "lower_frame_before": lower_frame_before,
        "lower_frame_after": lower_frame_after,
        "move_cursor_before": cursor_before,
        "move_phase_advance_during_fire": phase_after - phase_before,
        "moving_fire_advance_count_delta": advance_count_after - moving_advances_before,
        "move_cadence_scale": float(preview.debug_contract().get("move_cadence_scale", 0.0)),
        "birth_capture": birth_path,
        "shot_capture": shot_path,
        "snapshot_capture": snapshot_path,
        "late_capture": late_path,
    }
    _clear_projectiles()
    for _index in range(48):
        await process_frame
        if str(preview.debug_contract().get("playback_state", "")) == "move":
            break
    return result


func _expected_sector(vec: Vector2) -> int:
    return int(floor(fposmod(vec.angle() + PI / 8.0, TAU) / (PI / 4.0))) % 8


func _lower_frame(preview: AsterV4LocomotionPreview) -> int:
    if preview.primary == null:
        return -1
    return int(round(preview.primary.region_rect.position.y / 384.0))


func _find_actor_projectile(actor: OperatorActor) -> PrototypeProjectile:
    for child in root.get_children():
        if child is PrototypeProjectile and (child as PrototypeProjectile).owner_actor == actor:
            return child as PrototypeProjectile
    return null


func _clear_projectiles() -> void:
    for child in root.get_children():
        if child is PrototypeProjectile:
            child.queue_free()


func _make_overlay() -> void:
    overlay_layer = CanvasLayer.new()
    overlay_layer.name = "AsterUALV6CaptureOverlay"
    overlay_layer.layer = 120
    root.add_child(overlay_layer)
    var background := ColorRect.new()
    background.position = Vector2(160.0, 40.0)
    background.size = Vector2(960.0, 72.0)
    background.color = Color(0.004, 0.018, 0.027, 0.92)
    background.mouse_filter = Control.MOUSE_FILTER_IGNORE
    overlay_layer.add_child(background)
    overlay_title = Label.new()
    overlay_title.position = Vector2(176.0, 46.0)
    overlay_title.add_theme_font_size_override("font_size", 24)
    overlay_title.add_theme_color_override("font_color", Color("7df7ff"))
    overlay_layer.add_child(overlay_title)
    overlay_detail = Label.new()
    overlay_detail.position = Vector2(176.0, 78.0)
    overlay_detail.add_theme_font_size_override("font_size", 16)
    overlay_detail.add_theme_color_override("font_color", Color("e7f4f8"))
    overlay_layer.add_child(overlay_detail)


func _set_overlay(title: String, detail: String) -> void:
    overlay_title.text = title
    overlay_detail.text = detail


func _save(filename: String) -> String:
    # Freeze gameplay/process authority only while the renderer publishes the
    # current evidence frame. This keeps an exact projectile-birth frame exact,
    # prevents PNG encode time from consuming the 0.06 s burst, and lets label
    # changes reach the viewport without advancing any runtime state.
    var was_paused := paused
    paused = true
    await process_frame
    RenderingServer.force_draw()
    var viewport_texture := root.get_texture()
    if viewport_texture == null:
        paused = was_paused
        _fail("capture backend exposed no viewport texture: " + filename)
        return ""
    var image := viewport_texture.get_image()
    if image == null or image.is_empty() or image.get_size() != VIEWPORT_SIZE:
        paused = was_paused
        _fail("invalid runtime capture image: " + filename)
        return ""
    var path := _global_output(filename)
    var error := image.save_png(path)
    paused = was_paused
    if error != OK:
        _fail("capture write failed: %s error=%d" % [path, error])
        return ""
    print("CAPTURED: " + path)
    return path


func _global_output(filename: String) -> String:
    return ProjectSettings.globalize_path(OUT_DIR + "/" + filename)


func _make_required_contact(paths: Array[String], filename: String, columns: int, rows: int, expected_count: int, label: String) -> void:
    if paths.size() != expected_count:
        _fail("%s capture set count is incomplete" % label)
        return
    for path in paths:
        if path.is_empty():
            _fail("%s capture set contains an empty path" % label)
            return
    _make_contact_sheet(paths, filename, columns, rows)


func _make_contact_sheet(paths: Array[String], filename: String, columns: int, rows: int) -> void:
    var grid_size := Vector2i(CONTACT_CELL.x * columns, CONTACT_CELL.y * rows)
    var contact_size := Vector2i(max(CONTACT_MIN_SIZE.x, grid_size.x), max(CONTACT_MIN_SIZE.y, grid_size.y))
    var grid_origin := Vector2i(int((contact_size.x - grid_size.x) / 2), int((contact_size.y - grid_size.y) / 2))
    var contact := Image.create(contact_size.x, contact_size.y, false, Image.FORMAT_RGBA8)
    contact.fill(Color("050b10"))
    for index in range(paths.size()):
        var source := Image.new()
        var error := source.load(paths[index])
        if error != OK or source.get_size() != VIEWPORT_SIZE:
            _fail("contact source invalid: " + paths[index])
            continue
        var crop := source.get_region(CONTACT_CROP)
        crop.resize(CONTACT_CELL.x, CONTACT_CELL.y, Image.INTERPOLATE_LANCZOS)
        var destination := grid_origin + Vector2i(index % columns, index / columns) * CONTACT_CELL
        contact.blit_rect(crop, Rect2i(Vector2i.ZERO, CONTACT_CELL), destination)
    var output_path := _global_output(filename)
    var save_error := contact.save_png(output_path)
    if save_error != OK:
        _fail("contact write failed: %s error=%d" % [output_path, save_error])
    else:
        print("CONTACT: " + output_path)


func _all_case_bool(list_key: String, value_key: String) -> bool:
    var cases: Array = evidence.get(list_key, [])
    if cases.size() != DIRECTIONS.size():
        return false
    for item in cases:
        if not bool((item as Dictionary).get(value_key, false)):
            return false
    return true


func _write_json(filename: String, payload: Dictionary) -> void:
    var path := _global_output(filename)
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        _fail("could not open evidence JSON: " + path)
        return
    file.store_string(JSON.stringify(payload, "  "))
    file.close()
    print("EVIDENCE: " + path)


func _finish(stage: Node, actor: OperatorActor, previous_setting: bool) -> void:
    if actor:
        actor.debug_stop_drive()
    _clear_projectiles()
    if stage:
        stage.queue_free()
    if overlay_layer:
        overlay_layer.queue_free()
    await process_frame
    ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
    if failed:
        print("ASTER_UAL_V6_MOVING_FIRE_CAPTURE: FAIL (%d)" % failures.size())
        for failure in failures:
            print(" - " + failure)
        quit(1)
        return
    print("ASTER_UAL_V6_MOVING_FIRE_CAPTURE: PASS %dx%d %s" % [VIEWPORT_SIZE.x, VIEWPORT_SIZE.y, ProjectSettings.globalize_path(OUT_DIR)])
    quit(0)


func _frames(count: int) -> void:
    for _index in range(count):
        await process_frame


func _physics_frames(count: int) -> void:
    for _index in range(count):
        await physics_frame


func _require(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        _fail(label)


func _fail(label: String) -> void:
    failed = true
    failures.append(label)
    push_error(label)
