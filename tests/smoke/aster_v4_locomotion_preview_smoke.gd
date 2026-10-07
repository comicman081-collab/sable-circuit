extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const FEATURE_SETTING := "sable_visuals/aster_v4_locomotion_preview"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const UPPER_DIRECTIONS_16: Array[String] = [
    "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW", "N", "NNE", "NE", "ENE",
]
const COMPOSITE_V6_MANIFEST := "res://assets/units/operators/aster/composite_fire_v6/ASTER_COMPOSITE_FIRE_V6_MANIFEST.json"
const TORSO_SOCKET_V1 := "res://assets/units/operators/aster/ASTER_TORSO_SOCKET_V1.json"
const TORSO_BRIDGE_V1 := "res://assets/units/operators/aster/torso_bridge_v1/ASTER_TORSO_BRIDGE_V1_MANIFEST.json"
const UPPER_16_MANIFEST := "res://assets/units/operators/aster/fire_upper_16_no_shoulder_v2/ASTER_FIRE_UPPER_16_NO_SHOULDER_V2_MANIFEST.json"
const UPPER_16_MUZZLE_ALIGNMENT := "res://assets/units/operators/aster/fire_upper_16_no_shoulder_v2/ASTER_MUZZLE_ALIGNMENT_16_NO_SHOULDER_V2.json"
const TORSO_SOCKET_16_V2 := "res://assets/units/operators/aster/ASTER_TORSO_SOCKET_16_NO_SHOULDER_V4.json"

var failures: Array[String] = []


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    var previous_setting := bool(ProjectSettings.get_setting(FEATURE_SETTING, false))
    ProjectSettings.set_setting(FEATURE_SETTING, true)
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(12)

    var actor := stage.squad.get_active_operator() as OperatorActor
    _check(actor != null and actor.operator_id == "CHR_PROTO_01", "active operator is ASTER")
    if actor == null:
        ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
        quit(1)
        return

    var preview := actor.get_node_or_null("AsterV4LocomotionPreview") as AsterV4LocomotionPreview
    _check(preview != null, "ASTER owns the locomotion preview layer")
    if preview == null:
        ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
        quit(1)
        return

    var collision := actor.get_node("CollisionShape2D") as CollisionShape2D
    var collision_position := collision.position
    var collision_shape := collision.shape
    var speed_before := actor.walk_speed
    var fire_interval_before := actor.fire_interval
    var contract := preview.debug_contract()
    _check(bool(contract.get("active", false)), "V6 locomotion preview activates behind feature flag")
    _check(str(contract.get("status", "")) == "preview_loaded", "V6 locomotion bundle passes runtime dimension validation")
    _check(int(contract.get("idle_texture_count", 0)) == 8, "all eight authored Idle atlases load")
    _check(int(contract.get("move_texture_count", 0)) == 8, "all eight move atlases load from one coherent family")
    _check(int(contract.get("fire_texture_count", 0)) == 8, "all eight clean Fire V4 atlases load")
    _check(int(contract.get("idle_frame_count", 0)) == 4, "authored Idle exposes four frames")
    _check(str(contract.get("idle_runtime_asset_family", "")) == "idle_360_clean_v5", "Idle uses the clean V5 atlas family without matte bands")
    var move_family := str(contract.get("move_runtime_asset_family", ""))
    _check(move_family == "move_360_ual_v6", "promotion gate requires the complete articulated Move V6 family")
    _check(str(contract.get("composite_runtime_asset_family", "")) == "composite_fire_v6", "Move V6 and Composite Fire V6 promote as one atomic bundle")
    _check(int(contract.get("move_frame_count", 0)) == 24, "UAL-derived Move V6 exposes twenty-four frames")
    _check(is_equal_approx(float(contract.get("move_fps", 0.0)), 24.0), "Move V6 owns the authored 24 fps reference cadence")
    _check(bool(contract.get("move_v6_selected", false)), "the complete V6 bundle is selected atomically")
    _check(not bool(contract.get("move_v5_selected", true)), "V5 remains rollback-only after V6 promotion")
    _check(str(contract.get("move_cadence_authority", "")) == "velocity_scaled_from_walk_speed", "runtime scales UAL gait cadence from actual ground speed")
    _check(not bool(contract.get("continuous_render_blend", true)), "dense V6 playback does not alpha-crossfade adjacent frames")
    _check(not bool(contract.get("adjacent_frame_crossfade", true)), "single-sprite playback prevents double silhouettes")
    _check(bool(contract.get("stationary_uses_idle_atlas", false)), "stationary ASTER uses authored Idle atlases")
    _check(move_family == "move_360_ual_v6", "runtime resolves the promoted coherent V6 move family")
    var split_fire_valid := bool(contract.get("split_fire_set_valid", false))
    var upper16_promoted := bool(contract.get("upper16_promoted", false))
    var active_upper_count := int(contract.get("upper_direction_count", 0))
    var active_upper_directions := UPPER_DIRECTIONS_16 if upper16_promoted else DIRECTIONS
    _check(split_fire_valid, "promotion gate requires the complete moving-fire split family")
    if split_fire_valid:
        _check(int(contract.get("idle_lower_texture_count", 0)) == 8, "all eight split Idle lower atlases load")
        _check(int(contract.get("move_lower_texture_count", 0)) == 8, "all eight split Move lower atlases load")
        _check(int(contract.get("fire_upper_texture_count", 0)) == active_upper_count, "the active Fire upper atlas family loads as one complete set")
        _check(bool(contract.get("moving_fire_split_fix_claimed", false)), "complete split set enables the moving-fire fix")
    else:
        _check(not bool(contract.get("moving_fire_split_fix_claimed", true)), "an incomplete split set does not claim the moving-fire fix")
        _check(not str(contract.get("split_fire_failure_reason", "")).is_empty(), "an incomplete split set reports its blocker")

    var independent_aim_valid := bool(contract.get("independent_aim_composite_valid", false))
    _check(independent_aim_valid, "64-pair socket-aligned velocity-lower/aim-upper bundle promotes atomically")
    _check(bool(contract.get("torso_socket_loaded", false)), "torso socket V1 authority loads")
    _check(str(contract.get("torso_socket_path", "")) == (TORSO_SOCKET_16_V2 if upper16_promoted else TORSO_SOCKET_V1), "runtime pins the active torso socket authority path")
    _check(bool(contract.get("torso_bridge_loaded", false)), "all lower-phase torso bridge atlases load")
    _check(str(contract.get("torso_bridge_manifest_path", "")) == TORSO_BRIDGE_V1, "runtime pins the torso bridge V1 manifest")
    _check(int(contract.get("torso_bridge_texture_count", 0)) == 8, "all eight velocity-direction torso bridge atlases load")
    _check(str(contract.get("independent_aim_pair_qa", "")) == ("128_of_128_connected_all_24_lower_phases" if upper16_promoted else "64_of_64_connected"), "runtime exposes the complete active waist-connectivity QA result")
    _check(not bool(contract.get("raw_cross_direction_splice_used", true)), "runtime never uses an unaligned cross-direction splice")
    _check(bool(contract.get("true_strafe_backpedal_presentation", false)), "validated independent sectors enable true strafe/backpedal presentation")
    _check(active_upper_count == (16 if upper16_promoted else 8), "upper-body selector count matches the atomically promoted asset family")
    _check(int(contract.get("lower_direction_count", 0)) == 8, "lower-body selector owns its independent eight-direction schema")
    _check(str(contract.get("upper_direction_api", "")) == "count_driven_continuous_aim", "upper selector API is direction-count driven for a future sixteen-way set")
    _check(str(contract.get("upper_runtime_asset_family", "")) == ("fire_upper_16_no_shoulder_v2" if upper16_promoted else "composite_fire_v6/fire_upper"), "acceptance capture identifies the active upper runtime family")
    _check(str(contract.get("upper_alignment_path", "")) == (TORSO_SOCKET_16_V2 if upper16_promoted else TORSO_SOCKET_V1), "acceptance capture identifies the torso alignment authority")
    _check(str(contract.get("upper_contact_frame_alignment_path", "")) == (UPPER_16_MUZZLE_ALIGNMENT if upper16_promoted else "res://assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json"), "acceptance capture identifies the muzzle contact-frame alignment authority")
    _check(bool(contract.get("upper_alignment_promoted", false)), "upper alignment promotes only with the complete validated bundle")
    _check(str(contract.get("upper_alignment_status", "")) == "validated_%d_way" % active_upper_count, "current upper alignment identifies its active direction count")
    _check(str(contract.get("upper_runtime_promotion_contract", "")) == "upper_atlases_plus_torso_socket_plus_muzzle_alignment_atomic", "future sixteen-way upper remains behind an atomic asset-and-alignment contract")
    _check(str(contract.get("upper_direction_authority", "")) == "continuous_aim_with_facing_fallback", "upper body follows continuous aim")
    _check(str(contract.get("lower_direction_authority", "")) == "actual_velocity", "lower body follows actual velocity")
    _check(is_equal_approx(float(contract.get("direction_hysteresis_degrees", 0.0)), 4.0), "upper and lower selectors use four-degree hysteresis")
    _check(bool(contract.get("move_cursor_preserved_on_sector_change", false)), "sector changes explicitly preserve locomotion phase")

    # The current 16-way candidate is deliberately HOLD.  It must be detected
    # but must not replace even one fallback texture, socket or muzzle record.
    # These assertions become the promotion branch automatically once all
    # three authorities pass together.
    _check(bool(contract.get("upper16_candidate_detected", false)), "runtime detects the staged sixteen-way upper candidate")
    _check(bool(contract.get("upper16_atomic_no_partial_mix", false)), "runtime declares atomic no-partial-mix promotion")
    if upper16_promoted:
        _check(active_upper_count == 16, "eligible sixteen-way bundle promotes all selectors together")
        _check(not bool(contract.get("upper16_safe_fallback_active", true)), "promoted sixteen-way bundle leaves fallback mode")
        _check(str(contract.get("upper16_failure_reason", "sentinel")).is_empty(), "promoted sixteen-way bundle has no gate failure")
        _check(bool(contract.get("upper_socket_offsets_per_fire_frame", false)), "promoted 8x16 socket selects a distinct offset for every fire phase")
        _check(int(contract.get("muzzle_alignment_record_count", 0)) == 16, "promoted muzzle alignment swaps all sixteen records together")
    else:
        _check(active_upper_count == 8, "HOLD sixteen-way candidate keeps the safe eight-way selector")
        _check(bool(contract.get("upper16_safe_fallback_active", false)), "HOLD candidate keeps the coherent eight-way fallback active")
        _check(not str(contract.get("upper16_failure_reason", "")).is_empty(), "HOLD candidate records the exact promotion blocker")
        _check(int(contract.get("fire_upper_texture_count", 0)) == 8, "failed partial promotion cannot mix sixteen upper atlases into eight-way runtime")
        _check(not bool(contract.get("upper_socket_offsets_per_fire_frame", true)), "failed partial promotion cannot mix per-frame 8x16 offsets into fallback")
        _check(int(contract.get("muzzle_alignment_record_count", 0)) == 8, "failed partial promotion cannot mix sixteen muzzle records into fallback")
        _check(str(contract.get("torso_socket_path", "")) == TORSO_SOCKET_V1, "failed partial promotion cannot mix the 8x16 socket into fallback")
        _check(str(contract.get("muzzle_alignment_path", "")) == "res://assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json", "failed partial promotion cannot mix sixteen-way muzzle records into fallback")

    # Pure status-gate probes cover every partial-pass permutation without
    # mutating or temporarily rewriting production manifests.
    _check(not bool(preview.call("_upper16_manifest_status_gate", {"candidate_status": "PASS", "promotion_ready": true, "visual_gate": "HOLD", "qa": {"technical_result": "PASS"}, "runtime_eligible": true})), "visual HOLD blocks a technically complete sixteen-way manifest")
    _check(not bool(preview.call("_upper16_manifest_status_gate", {"candidate_status": "PASS", "promotion_ready": true, "visual_gate": "PASS", "qa": {"technical_result": "FAIL"}, "runtime_eligible": true})), "technical FAIL blocks a visually approved sixteen-way manifest")
    _check(not bool(preview.call("_upper16_manifest_status_gate", {"candidate_status": "HOLD", "promotion_ready": true, "visual_gate": "PASS", "qa": {"technical_result": "PASS"}, "runtime_eligible": true})), "candidate HOLD blocks otherwise complete sixteen-way assets")
    _check(not bool(preview.call("_upper16_manifest_status_gate", {"candidate_status": "PASS", "promotion_ready": false, "visual_gate": "PASS", "qa": {"technical_result": "PASS"}, "runtime_eligible": true})), "candidate PASS without explicit promotion readiness cannot authorize the manifest")
    _check(not bool(preview.call("_upper16_manifest_status_gate", {"candidate_status": "PASS", "promotion_ready": true, "visual_gate": "PASS", "qa": {"technical_result": "PASS"}, "runtime_eligible": false})), "manifest runtime eligibility is mandatory for sixteen-way promotion")
    _check(not bool(preview.call("_upper16_manifest_status_gate", {"promotion_ready": true, "visual_gate": "PASS", "qa": {"technical_result": "PASS"}, "runtime_eligible": true})), "promotion readiness cannot replace reviewed candidate PASS")
    _check(not bool(preview.call("_upper16_manifest_status_gate", {"candidate_status": "PASS", "promotion_ready": true, "visual_gate": "PASS", "technical_result": "PASS", "runtime_eligible": true})), "top-level technical PASS cannot replace qa.technical_result PASS")
    _check(bool(preview.call("_upper16_manifest_status_gate", {"candidate_status": "PASS", "promotion_ready": true, "visual_gate": "PASS", "qa": {"technical_result": "PASS"}, "runtime_eligible": true})), "manifest promotes only when candidate, promotion, visual, technical, and runtime gates all PASS")
    _check(not bool(preview.call("_upper16_alignment_status_gate", {"candidate_status": "HOLD"})), "HOLD muzzle alignment cannot enter an otherwise promoted bundle")
    _check(not bool(preview.call("_upper16_alignment_status_gate", {"promotion_ready": true})), "muzzle promotion marker cannot replace alignment candidate PASS")
    _check(not bool(preview.call("_upper16_socket_status_gate", {"candidate_status": "PASS", "visual_gate": "PASS", "runtime_eligible": false})), "non-runtime-eligible 8x16 socket blocks atomic promotion")
    var valid_socket_status := {
        "candidate_status": "PASS",
        "visual_gate": "PASS",
        "runtime_eligible": true,
        "dependency": {
            "candidate_status": "PASS",
            "promotion_ready": true,
            "visual_gate": "PASS",
            "technical_result": "PASS",
            "gate": "PASS",
            "candidate_or_promotion_pass": true,
            "visual_pass": true,
            "technical_pass": true,
        },
        "qa": {"technical_gate": "PASS", "dependency_gate": "PASS", "promotion_gate": "PASS"},
    }
    _check(bool(preview.call("_upper16_socket_status_gate", valid_socket_status)), "fully reviewed 8x16 socket status passes")
    var socket_without_candidate := valid_socket_status.duplicate(true)
    socket_without_candidate.erase("candidate_status")
    socket_without_candidate["promotion_ready"] = true
    _check(not bool(preview.call("_upper16_socket_status_gate", socket_without_candidate)), "socket promotion marker cannot replace socket candidate PASS")
    var socket_without_dependency_promotion := valid_socket_status.duplicate(true)
    (socket_without_dependency_promotion["dependency"] as Dictionary)["promotion_ready"] = false
    _check(not bool(preview.call("_upper16_socket_status_gate", socket_without_dependency_promotion)), "dependency promotion readiness is mandatory for the 8x16 socket")

    var torso_socket_manifest := _read_json_dictionary(str(contract.get("torso_socket_path", TORSO_SOCKET_V1)))
    var torso_socket_qa: Dictionary = torso_socket_manifest.get("qa", {})
    var torso_bridge_manifest := _read_json_dictionary(TORSO_BRIDGE_V1)
    if upper16_promoted:
        _check(str(torso_socket_qa.get("promotion_gate", "")) == "PASS", "8x16 torso socket promotion gate passes")
        _check(int(torso_socket_qa.get("pair_count", 0)) == 128 and int(torso_socket_qa.get("passed_pairs", 0)) == 128, "8x16 torso socket authority covers every lower/upper direction pair")
        _check(bool(torso_socket_qa.get("cardinal_same_direction_offsets_zero", false)), "cardinal same-direction 8x16 torso offsets remain exactly zero")
    else:
        _check(str(torso_socket_qa.get("gate", "")) == "PASS", "torso socket V1 visual connectivity gate passes")
        _check(int(torso_socket_qa.get("pairs_scanned", 0)) == 64 and int(torso_socket_qa.get("passed_pairs", 0)) == 64, "torso socket authority covers every lower/upper direction pair")
        _check(bool(torso_socket_qa.get("same_direction_zero", false)), "same-direction torso offsets remain exactly zero")
    _check(int(torso_bridge_manifest.get("frame_count", 0)) == 24, "torso bridge follows all twenty-four lower locomotion phases")
    _check(not bool(torso_bridge_manifest.get("baked_muzzle_vfx", true)), "torso bridge contains no baked muzzle effect")
    for direction in DIRECTIONS:
        var move_manifest_path := "res://assets/units/operators/aster/move_360_ual_v6/%s/ASTER_MOVE_%s_360_UAL_V6_MANIFEST.json" % [direction, direction]
        var move_manifest := _read_json_dictionary(move_manifest_path)
        var move_qa: Dictionary = move_manifest.get("qa", {})
        var gait_qa: Dictionary = move_qa.get("gait_display_metrics", {})
        _check(not move_manifest.is_empty(), "V6 %s move manifest parses" % direction)
        _check(str(gait_qa.get("gate", "")) == "PASS", "V6 %s manifest records visible gait PASS" % direction)
        _check(int(move_qa.get("unique_decoded_frames", 0)) == 24, "V6 %s atlas contains 24 unique decoded frames" % direction)
        _check(bool(move_qa.get("weapon_corridor_pixel_stable", false)), "V6 %s keeps the authored weapon corridor stable" % direction)
        _check(int(move_qa.get("visible_green_residual_pixels", -1)) == 0, "V6 %s runtime atlas contains no green matte pixels" % direction)
    var composite_manifest := _read_json_dictionary(COMPOSITE_V6_MANIFEST)
    var composite_qa: Dictionary = composite_manifest.get("qa", {})
    _check(not composite_manifest.is_empty(), "Composite Fire V6 manifest parses")
    _check(int(composite_qa.get("frame_pairs_scanned", 0)) == 1344, "Composite Fire V6 validates all 1,344 lower/fire frame pairs")
    _check(str(composite_qa.get("costume_continuity", "")) == "COSTUME_CONTINUITY_PASS", "Composite Fire V6 locks ASTER costume continuity")
    _check(int(composite_qa.get("lower_costume_mismatch_pixels", -1)) == 0, "Composite Fire V6 preserves every lower costume authority pixel")
    _check(int(composite_qa.get("lower_costume_missing_hole_pixels", -1)) == 0, "Composite Fire V6 contains no missing lower-body holes")
    _check(int(composite_qa.get("white_cyan_costume_mismatch_pixels", -1)) == 0, "Composite Fire V6 preserves the white/cyan thigh panel")
    _check(bool(contract.get("muzzle_texture_loaded", false)), "separate runtime muzzle VFX loads")
    _check(bool(contract.get("muzzle_alignment_loaded", false)), "Fire contact-frame V7 muzzle alignment contract loads atomically")
    _check(str(contract.get("muzzle_alignment_path", "")) == (UPPER_16_MUZZLE_ALIGNMENT if upper16_promoted else "res://assets/units/operators/aster/ASTER_MUZZLE_ALIGNMENT_V7.json"), "Godot consumes the active shared muzzle JSON authority")
    _check(int(contract.get("muzzle_alignment_source_frame", -1)) == 2, "muzzle alignment is measured from the recoil-contact frame")
    _check(not bool(contract.get("character_raster_rotated", true)), "muzzle correction never rotates ASTER's body or hair raster")
    _check(bool(contract.get("gameplay_aim_direction_unchanged", false)), "muzzle correction leaves gameplay aim authority unchanged")
    _check(not bool(contract.get("muzzle_vfx_embedded_in_character_frames", true)), "character frames contain no baked muzzle VFX")
    _check(bool(contract.get("muzzle_vfx_runtime_only", false)), "muzzle flash is runtime-only")
    _check(str(contract.get("muzzle_vfx_timing_authority", "")) == "primary_fired_immediate_burst", "muzzle flash timing is driven directly by the shot event")
    _check(int(contract.get("fire_contact_frame", -1)) == 2, "fire presentation begins on the authored shot-contact pose")
    _check(bool(contract.get("rendering_only", false)), "V6 layer declares presentation-only authority")
    _check(not bool(contract.get("gameplay_timing_coupled", true)), "V6 layer does not own gameplay timing")
    _check(not bool(contract.get("collision_coupled", true)), "V6 layer does not own collision")
    _check(bool(contract.get("atlas_region_filter_clipped", false)), "atlas filtering clips each active cell")
    var authored_muzzle_local := preview.get_authored_muzzle_local_position()
    var authored_muzzle_global := preview.get_authored_muzzle_global_position()
    _check(authored_muzzle_global.is_equal_approx(preview.to_global(authored_muzzle_local)), "authored muzzle global position comes from the visible per-sector socket")

    actor.set_movement_bounds(Rect2(-10000.0, -10000.0, 20000.0, 20000.0))
    var vectors: Array[Vector2] = [
        Vector2.RIGHT, Vector2(1, 1).normalized(), Vector2.DOWN, Vector2(-1, 1).normalized(),
        Vector2.LEFT, Vector2(-1, -1).normalized(), Vector2.UP, Vector2(1, -1).normalized(),
    ]
    var active_muzzle_alignment := _read_json_dictionary(str(contract.get("muzzle_alignment_path", "")))
    var expected_muzzle_source_points: Array[Vector2] = []
    var expected_barrel_tangent_degrees: Array[float] = []
    var active_calibration: Dictionary = active_muzzle_alignment.get("calibration", {})
    for upper_direction in active_upper_directions:
        var calibration_entry: Dictionary = active_calibration.get(upper_direction, {})
        var muzzle_xy: Array = calibration_entry.get("muzzle_xy", [])
        expected_muzzle_source_points.append(Vector2(float(muzzle_xy[0]), float(muzzle_xy[1])) if muzzle_xy.size() == 2 else Vector2.INF)
        expected_barrel_tangent_degrees.append(float(calibration_entry.get("barrel_tangent_degrees", 9999.0)))
    _check(expected_muzzle_source_points.size() == active_upper_count, "active muzzle authority exposes one record per upper direction")

    # Sector helpers keep a four-degree dead band beyond each nominal sector
    # edge.  Exercise both today's eight-way sets and the future sixteen-way
    # upper API without coupling either selector to gameplay facing writes.
    _check(int(preview.call("_resolve_direction_sector", Vector2.from_angle(deg_to_rad(25.0)), 0, 8, false)) == 0, "eight-way selector holds E through the four-degree hysteresis band")
    _check(int(preview.call("_resolve_direction_sector", Vector2.from_angle(deg_to_rad(27.0)), 0, 8, false)) == 1, "eight-way selector changes to SE beyond the hysteresis band")
    _check(int(preview.call("_resolve_direction_sector", Vector2.from_angle(deg_to_rad(15.0)), 0, 16, false)) == 0, "future sixteen-way upper selector holds its four-degree hysteresis band")
    _check(int(preview.call("_resolve_direction_sector", Vector2.from_angle(deg_to_rad(16.0)), 0, 16, false)) == 1, "future sixteen-way upper selector advances beyond its hysteresis band")
    _check(int(contract.get("full_body_idle_fire_direction_count", 0)) == 8, "Idle and fallback full-body Fire retain their authored eight-way authority")
    _check(bool(contract.get("full_body_upper_sector_remap_active", false)) == upper16_promoted, "full-body remapping activates exactly when the upper selector promotes to sixteen directions")
    for future_upper_sector in range(16):
        var full_body_sector := int(preview.call("_remap_sector", future_upper_sector, 16, 8))
        _check(full_body_sector >= 0 and full_body_sector < 8, "future upper sector %d remaps safely into an eight-way full-body atlas" % future_upper_sector)

    if upper16_promoted:
        var phase_before_sixteen_sweep := float(preview.get("_move_cursor"))
        for upper_sector in range(UPPER_DIRECTIONS_16.size()):
            actor.velocity = Vector2.RIGHT * speed_before
            actor.aim_world = Vector2.from_angle(float(upper_sector) * TAU / float(UPPER_DIRECTIONS_16.size()))
            preview.call("_sync_sector", true)
            _check(int(preview.get("_upper_sector")) == upper_sector, "promoted selector resolves exact sixteen-way centre %s" % UPPER_DIRECTIONS_16[upper_sector])
            _check(int(preview.get("_lower_sector")) == 0, "sixteen-way aim sweep keeps the eastward velocity lower")
            _check(is_equal_approx(float(preview.get("_move_cursor")), phase_before_sixteen_sweep), "sixteen-way aim sector %s preserves gait phase" % UPPER_DIRECTIONS_16[upper_sector])

    # A forced sector resync is allowed to change both selected atlases, but it
    # must never rewind the UAL gait.  No frame is processed between the write
    # and assertion, so any delta here can only come from `_sync_sector`.
    actor.velocity = Vector2.RIGHT * speed_before
    actor.aim_world = Vector2.RIGHT
    preview.call("_sync_sector", true)
    preview.set("_move_cursor", 7.25)
    actor.velocity = Vector2.DOWN * speed_before
    actor.aim_world = Vector2.UP
    preview.call("_sync_sector", true)
    _check(is_equal_approx(float(preview.get("_move_cursor")), 7.25), "upper/lower sector changes never reset the locomotion cursor")

    for sector in range(vectors.size()):
        var expected_upper_sector := int(sector * active_upper_count / DIRECTIONS.size())
        var expected_upper_direction := active_upper_directions[expected_upper_sector]
        var loops_before := int(preview.debug_contract().get("completed_move_loops", 0))
        actor.debug_drive(Vector2.RIGHT, vectors[sector])
        await _physics_frames(70)
        contract = preview.debug_contract()
        _check(int(contract.get("sector", -1)) == expected_upper_sector, "move playback resolves active upper sector %d" % expected_upper_sector)
        _check(int(contract.get("upper_sector", -1)) == expected_upper_sector, "move upper follows aim sector %d" % expected_upper_sector)
        _check(int(contract.get("lower_sector", -1)) == 0, "move lower remains on actual eastward velocity while aiming sector %d" % sector)
        _check(str(contract.get("playback_state", "")) == "move", "move playback enters its active state in sector %d" % sector)
        _check(not bool(contract.get("blend_sprite_visible", true)), "move playback keeps the adjacent blend sprite hidden in sector %d" % sector)
        _check(bool(contract.get("fire_upper_visible", false)), "move playback displays the aim-ready upper for sector %d" % sector)
        _check(bool(contract.get("torso_bridge_visible", false)), "move playback displays the velocity-phase torso bridge for sector %d" % sector)
        _check(bool(contract.get("move_aim_ready_upper_active", false)), "non-firing move uses aim-ready upper composition in sector %d" % sector)
        _check(str(contract.get("lower_body_atlas_selected", "")) == "composite_fire_v6/move_lower", "move playback selects eastward articulated lower while aiming sector %d" % sector)
        var expected_upper_offset := _torso_runtime_offset(torso_socket_manifest, "E", expected_upper_direction, "aim")
        _check(Vector2(contract.get("upper_presentation_offset_runtime", Vector2.INF)).distance_to(expected_upper_offset) <= 0.001, "move sector %d applies the socket-authorized upper translation" % sector)
        _check(int(contract.get("completed_move_loops", 0)) > loops_before, "move playback completes a loop in sector %d" % sector)

    # Invert the authority check: fixed east aim with each movement direction
    # must choose all eight lower atlases without disturbing the upper sector.
    for lower_sector in range(vectors.size()):
        actor.debug_drive(vectors[lower_sector], Vector2.RIGHT)
        await _physics_frames(3)
        contract = preview.debug_contract()
        _check(int(contract.get("upper_sector", -1)) == 0, "fixed east aim keeps upper sector while lower selects %s" % DIRECTIONS[lower_sector])
        _check(int(contract.get("lower_sector", -1)) == lower_sector, "actual velocity selects lower sector %s" % DIRECTIONS[lower_sector])
        _check(Vector2(contract.get("upper_presentation_offset_runtime", Vector2.INF)).distance_to(_torso_runtime_offset(torso_socket_manifest, DIRECTIONS[lower_sector], "E", "aim")) <= 0.001, "lower %s / upper E uses its validated torso offset" % DIRECTIONS[lower_sector])

    # Moving right while aiming forward, sideways, or backward must all advance
    # the leg cycle.  The authored upper body follows aim; locomotion may never
    # collapse to a frozen fire stance for twin-stick relative angles.
    for relative_aim in [Vector2.RIGHT, Vector2.UP, Vector2.LEFT, Vector2.DOWN]:
        actor.debug_drive(Vector2.RIGHT, relative_aim)
        await _physics_frames(2)
        var phase_before := float(preview.debug_contract().get("move_phase_advance_total", 0.0))
        await _physics_frames(10)
        contract = preview.debug_contract()
        _check(float(contract.get("move_phase_advance_total", 0.0)) > phase_before + 2.0, "leg cycle advances while moving right and aiming at %.1f degrees" % rad_to_deg(relative_aim.angle()))

    # Cadence must follow ground speed so half-speed analog movement cannot use
    # the same planted-foot timing as a full-speed walk.
    actor.debug_drive(Vector2(0.5, 0.0), Vector2.UP)
    await _physics_frames(2)
    var slow_phase_before := float(preview.debug_contract().get("move_phase_advance_total", 0.0))
    await _physics_frames(12)
    contract = preview.debug_contract()
    var slow_phase_delta := float(contract.get("move_phase_advance_total", 0.0)) - slow_phase_before
    var slow_cadence := float(contract.get("move_cadence_scale", 0.0))
    actor.debug_drive(Vector2.RIGHT, Vector2.UP)
    await _physics_frames(2)
    var full_phase_before := float(preview.debug_contract().get("move_phase_advance_total", 0.0))
    await _physics_frames(12)
    contract = preview.debug_contract()
    var full_phase_delta := float(contract.get("move_phase_advance_total", 0.0)) - full_phase_before
    var full_cadence := float(contract.get("move_cadence_scale", 0.0))
    _check(slow_cadence > 0.45 and slow_cadence < 0.55, "half-speed movement uses approximately half UAL cadence")
    _check(full_cadence > 0.95 and full_cadence < 1.05, "walk speed uses the authored UAL cadence")
    _check(full_phase_delta > slow_phase_delta * 1.8, "ground-speed scaling materially separates slow and full gait timing")

    # The projectile must be born at the exact socket that drives the visible
    # muzzle flash.  Exercise all authored directions while locomotion remains
    # active; this guards the diagonal/back-facing disconnect reported in the
    # interactive review.
    for sector in range(vectors.size()):
        var expected_upper_sector := int(sector * active_upper_count / DIRECTIONS.size())
        var expected_upper_direction := active_upper_directions[expected_upper_sector]
        actor.debug_drive(Vector2.RIGHT, vectors[sector])
        await _physics_frames(2)
        # Recreate a click-to-fire tick where aim has changed but presentation
        # still holds the previous direction.  Fire must synchronize the
        # sector before either the visible socket or projectile is resolved.
        actor.facing_sector = posmod(sector + 4, vectors.size())
        actor.aim_world = vectors[sector]
        var fired := actor.debug_fire_once()
        _check(fired, "moving ASTER fires for muzzle socket sector %d" % sector)
        _check(actor.facing_sector == sector, "same-tick aim and fire synchronizes authored sector %d" % sector)
        contract = preview.debug_contract()
        _check(int(contract.get("lower_sector", -1)) == 0, "moving shot sector %d retains eastward velocity lower" % sector)
        var expected_upper_offset := _torso_runtime_offset(torso_socket_manifest, "E", expected_upper_direction, "aim")
        var expected_contact_offset := _torso_runtime_offset(torso_socket_manifest, "E", expected_upper_direction, "recoil_contact_clean")
        var expected_local := (
            Vector2(contract.get("fixed_visual_origin", Vector2.ZERO))
            + (expected_muzzle_source_points[expected_upper_sector] - Vector2.ONE * float(contract.get("cell_size", 0.0)) * 0.5) * float(contract.get("display_scale", 0.0))
            + expected_contact_offset
        )
        _check(Vector2(contract.get("upper_presentation_offset_runtime", Vector2.INF)).distance_to(expected_upper_offset) <= 0.001, "moving shot sector %d exposes the translated upper offset" % sector)
        _check(preview.get_authored_muzzle_local_position().distance_to(expected_local) <= 0.05, "sector %d uses the translated visible Fire contact-frame muzzle endpoint" % sector)
        _check(absf(angle_difference(preview.get_authored_barrel_tangent(expected_upper_sector).angle(), deg_to_rad(expected_barrel_tangent_degrees[expected_upper_sector]))) <= deg_to_rad(0.06), "sector %d exposes the measured visible barrel tangent" % sector)
        var expected_origin := preview.get_authored_muzzle_global_position()
        contract = preview.debug_contract()
        _check(bool(contract.get("muzzle_vfx_visible", false)), "muzzle flash starts synchronously with projectile birth in sector %d" % sector)
        _check(Vector2(contract.get("muzzle_vfx_global_position", Vector2.ZERO)).distance_to(expected_origin) <= 0.05, "visible muzzle flash shares projectile socket in sector %d" % sector)
        _check(absf(angle_difference(float(contract.get("muzzle_vfx_rotation", 99.0)), vectors[sector].angle())) <= 0.001, "muzzle flash follows shot direction in sector %d" % sector)
        var expected_barrel_residual := absf(angle_difference(vectors[sector].angle(), deg_to_rad(expected_barrel_tangent_degrees[expected_upper_sector])))
        _check(absf(float(contract.get("muzzle_vfx_barrel_residual_radians", -1.0)) - expected_barrel_residual) <= deg_to_rad(0.06), "sector %d reports the authored barrel residual without changing aim" % sector)
        _check(int(contract.get("muzzle_vfx_shot_sector", -1)) == expected_upper_sector, "muzzle flash snapshots active upper sector %d" % expected_upper_sector)
        var spawned: PrototypeProjectile = null
        for child in root.get_children():
            if child is PrototypeProjectile and (child as PrototypeProjectile).owner_actor == actor:
                spawned = child as PrototypeProjectile
                break
        _check(spawned != null, "projectile spawns for authored muzzle sector %d" % sector)
        if spawned != null:
            _check(spawned.global_position.distance_to(expected_origin) <= 0.05, "projectile origin equals visible authored muzzle socket in sector %d" % sector)
            _check(absf(angle_difference(spawned.direction.angle(), float(contract.get("muzzle_vfx_rotation", 99.0)))) <= deg_to_rad(1.0), "projectile and muzzle flash remain collinear within one degree in sector %d" % sector)
            spawned.queue_free()
        await process_frame

    # Gameplay aim is continuous even though the authored character raster uses
    # eight sectors.  Exercise angles between sector centres so a quantized
    # flash or stale socket cannot hide behind the cardinal-only capture.
    var off_axis_degrees: Array[float] = [11.25, 22.0, 33.75, 67.5, 101.25, 157.5, -146.25, -78.75]
    for angle_degrees in off_axis_degrees:
        var off_axis := Vector2.from_angle(deg_to_rad(angle_degrees))
        actor.debug_drive(Vector2.RIGHT, off_axis)
        await _physics_frames(2)
        actor.facing_sector = posmod(actor.facing_sector + 4, vectors.size())
        actor.aim_world = off_axis
        var fired := actor.debug_fire_once()
        _check(fired, "off-axis shot fires at %.2f degrees" % angle_degrees)
        var expected_origin := preview.get_authored_muzzle_global_position()
        contract = preview.debug_contract()
        _check(bool(contract.get("muzzle_vfx_visible", false)), "off-axis flash starts immediately at %.2f degrees" % angle_degrees)
        _check(Vector2(contract.get("muzzle_vfx_global_position", Vector2.ZERO)).distance_to(expected_origin) <= 0.05, "off-axis flash remains on the authored muzzle at %.2f degrees" % angle_degrees)
        _check(absf(angle_difference(float(contract.get("muzzle_vfx_rotation", 99.0)), off_axis.angle())) <= 0.001, "off-axis flash follows continuous aim at %.2f degrees" % angle_degrees)
        var shot_flash_position := Vector2(contract.get("muzzle_vfx_global_position", Vector2.ZERO))
        var shot_flash_rotation := float(contract.get("muzzle_vfx_rotation", 99.0))
        actor.aim_world = -off_axis
        actor.facing_sector = posmod(actor.facing_sector + 4, vectors.size())
        contract = preview.debug_contract()
        _check(Vector2(contract.get("muzzle_vfx_global_position", Vector2.ZERO)).distance_to(shot_flash_position) <= 0.05, "off-axis flash socket does not teleport after aim changes at %.2f degrees" % angle_degrees)
        _check(absf(angle_difference(float(contract.get("muzzle_vfx_rotation", 99.0)), shot_flash_rotation)) <= 0.001, "off-axis flash direction remains the fired-shot snapshot at %.2f degrees" % angle_degrees)
        actor.aim_world = off_axis
        var spawned: PrototypeProjectile = null
        for child in root.get_children():
            if child is PrototypeProjectile and (child as PrototypeProjectile).owner_actor == actor:
                spawned = child as PrototypeProjectile
                break
        _check(spawned != null, "off-axis projectile spawns at %.2f degrees" % angle_degrees)
        if spawned != null:
            _check(spawned.global_position.distance_to(expected_origin) <= 0.05, "off-axis projectile shares the authored muzzle at %.2f degrees" % angle_degrees)
            _check(absf(angle_difference(spawned.direction.angle(), off_axis.angle())) <= 0.001, "off-axis projectile preserves continuous gameplay aim at %.2f degrees" % angle_degrees)
            _check(absf(angle_difference(spawned.direction.angle(), shot_flash_rotation)) <= deg_to_rad(1.0), "off-axis projectile and flash remain collinear within one degree at %.2f degrees" % angle_degrees)
            spawned.queue_free()
        await process_frame

    actor.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    await _physics_frames(3)
    var moving_fire_advances_before := int(preview.debug_contract().get("moving_fire_move_advance_count", 0))
    var saw_moving_fire := false
    var saw_split_upper := false
    var saw_split_lower := false
    var saw_torso_bridge := false
    var saw_runtime_flash := false
    var immediate_flash_trigger_before := int(preview.debug_contract().get("muzzle_vfx_trigger_count", 0))
    if actor.debug_fire_once():
        contract = preview.debug_contract()
        _check(bool(contract.get("muzzle_vfx_visible", false)), "runtime muzzle VFX is visible on the exact shot tick")
        _check(int(contract.get("muzzle_vfx_trigger_count", 0)) == immediate_flash_trigger_before + 1, "shot event starts exactly one muzzle burst")
        _check(int(floor(float(contract.get("fire_elapsed", 0.0)) * float(contract.get("fire_fps", 0.0)))) >= int(contract.get("fire_contact_frame", 99)), "fire pose starts at contact rather than delayed pre-fire")
        for _frame in range(36):
            await physics_frame
            contract = preview.debug_contract()
            if bool(contract.get("moving_fire_active", false)):
                saw_moving_fire = true
            if bool(contract.get("fire_upper_visible", false)):
                saw_split_upper = true
            if str(contract.get("lower_body_atlas_selected", "")) == "composite_fire_v6/move_lower":
                saw_split_lower = true
            if bool(contract.get("torso_bridge_visible", false)):
                saw_torso_bridge = true
            if bool(contract.get("muzzle_vfx_visible", false)) and not saw_runtime_flash:
                saw_runtime_flash = true
    contract = preview.debug_contract()
    _check(saw_moving_fire, "an actual moving shot enters moving-fire playback")
    _check(int(contract.get("moving_fire_move_advance_count", 0)) > moving_fire_advances_before, "moving fire continues advancing locomotion frames")
    if independent_aim_valid:
        _check(saw_split_upper, "moving fire displays only the authored Fire upper overlay")
        _check(saw_split_lower, "moving fire selects the articulated V6 locomotion lower atlas")
        _check(saw_torso_bridge, "moving fire advances the velocity-phase torso bridge")
    else:
        _check(not saw_split_upper, "incomplete split assets never display an unvalidated upper overlay")
    _check(saw_runtime_flash, "actual fire trigger displays separate runtime muzzle VFX")

    # ASTER's 0.105 s cadence is faster than the former frame-2 delay.  Every
    # rapid shot must independently restart the short flash burst instead of
    # resetting an animation cursor that can never reach its flash frame.
    var rapid_trigger_count := int(preview.debug_contract().get("muzzle_vfx_trigger_count", 0))
    for shot_index in range(4):
        if shot_index > 0:
            await _physics_frames(6)
        _check(actor.debug_fire_once(), "rapid-fire shot %d is accepted" % (shot_index + 1))
        contract = preview.debug_contract()
        _check(bool(contract.get("muzzle_vfx_visible", false)), "rapid-fire shot %d starts an immediate muzzle burst" % (shot_index + 1))
        _check(int(contract.get("muzzle_vfx_trigger_count", 0)) == rapid_trigger_count + shot_index + 1, "rapid-fire shot %d owns one distinct muzzle burst" % (shot_index + 1))

    actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
    await _physics_frames(3)
    contract = preview.debug_contract()
    _check(str(contract.get("playback_state", "")) in ["stationary_fire", "idle"], "stopping leaves moving-fire locomotion immediately")
    _check(not bool(contract.get("moving_fire_active", true)), "stopped firing never freezes a moving lower-body pose")
    await _physics_frames(24)
    contract = preview.debug_contract()
    _check(str(contract.get("playback_state", "")) == "idle", "fire recovery returns to authored Idle instead of move contact-A")
    _check(not bool(contract.get("blend_sprite_visible", true)), "Idle keeps the adjacent blend sprite hidden")

    _check(actor.walk_speed == speed_before, "preview does not alter movement speed")
    _check(actor.fire_interval == fire_interval_before, "preview does not alter fire cadence")
    _check(collision.position == collision_position and collision.shape == collision_shape, "preview does not alter collision authority")

    ProjectSettings.set_setting(FEATURE_SETTING, false)
    await _frames(3)
    contract = preview.debug_contract()
    _check(not bool(contract.get("active", true)), "feature flag disables the preview immediately")
    _check(is_equal_approx((actor.get_node("VisualRoot") as CanvasItem).modulate.a, 1.0), "fallback restores legacy visual alpha")

    actor.debug_stop_drive()
    for child in root.get_children():
        if child is PrototypeProjectile and (child as PrototypeProjectile).owner_actor == actor:
            child.queue_free()
    stage.queue_free()
    await process_frame
    ProjectSettings.set_setting(FEATURE_SETTING, previous_setting)
    if failures.is_empty():
        print("ASTER_UAL_V6_LOCOMOTION_PREVIEW_SMOKE: PASS")
        quit(0)
        return
    print("ASTER_UAL_V6_LOCOMOTION_PREVIEW_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)


func _frames(count: int) -> void:
    for _index in range(count):
        await process_frame


func _physics_frames(count: int) -> void:
    for _index in range(count):
        await physics_frame


func _read_json_dictionary(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var parsed = JSON.parse_string(file.get_as_text())
    return parsed as Dictionary if parsed is Dictionary else {}


func _torso_runtime_offset(manifest: Dictionary, lower_direction: String, upper_direction: String, frame_label: String = "aim") -> Vector2:
    var offsets: Dictionary = manifest.get("offsets_source_px_by_frame", manifest.get("offsets_source_px", {}))
    var row = offsets.get(lower_direction, {})
    if not row is Dictionary:
        return Vector2.INF
    var raw_offset = (row as Dictionary).get(upper_direction, [])
    if raw_offset is Dictionary:
        raw_offset = (raw_offset as Dictionary).get(frame_label, [])
    if not raw_offset is Array:
        return Vector2.INF
    var xy := raw_offset as Array
    if xy.size() != 2:
        return Vector2.INF
    return Vector2(float(xy[0]), float(xy[1])) * float(manifest.get("display_scale", 0.0))


func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
