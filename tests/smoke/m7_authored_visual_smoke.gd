extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(8)

    var room_art := stage.get_node_or_null("RoomArtLayer") as Site7RoomArtLayer
    _check(room_art != null and room_art.debug_asset_count() == 8 and room_art.debug_all_assets_loaded(), "M7 loads eight expanded room art plates")

    var formation := stage.squad.debug_formation_contract()
    _check(bool(formation.get("m7_echelon", false)), "M7 widened triangular echelon is authoritative")
    _check(bool(formation.get("open_aim_lane", false)), "M7 echelon reserves the firing lane")
    _check(float(formation.get("rear_b", 0.0)) >= 110.0, "M7 rear operator separation is expanded")

    # Authored raster is allowed to stage incrementally, but a partial upload must
    # never reach Godot's WebP decoder or hide the validated directional SVG/vector
    # presentation. Complete payloads promote automatically after decode validation.
    for operator in stage.squad.operators:
        var raster := operator.get_node_or_null("AuthoredRasterPresentation") as OperatorAuthoredRasterPresentation
        var aster_v4 := operator.get_node_or_null("AsterV4LocomotionPreview") as AsterV4LocomotionPreview
        var aster_v4_active := aster_v4 != null and bool(aster_v4.debug_contract().get("active", false))
        var motion_lab := operator.get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
        var motion_lab_active := motion_lab != null and motion_lab.is_runtime_active()
        if operator.operator_id in ["CHR_PROTO_01", "CHR_PROTO_03"]:
            _check(motion_lab_active, "%s current Motion Studio package activates in the game scene" % operator.display_name)
            if motion_lab_active:
                var motion_contract := motion_lab.debug_contract()
                _check(int(motion_contract.get("directions", 0)) == 8, "%s Motion Studio runtime loads all eight directions" % operator.display_name)
                _check(is_equal_approx(float(motion_contract.get("display_height_px", 0.0)), 129.6), "%s Motion Studio source is map-scaled to the 129.6px operator height" % operator.display_name)
        _check(raster != null, "%s owns authored raster staging layer" % operator.display_name)
        if raster:
            var raster_contract := raster.debug_contract()
            var raster_status := str(raster_contract.get("status","unknown"))
            _check(raster_status not in ["decode_error","invalid_dimensions","length_mismatch","invalid_header"], "%s raster staging has no malformed/decode-error state" % operator.display_name)
            if raster_status == "partial":
                _check(bool(raster_contract.get("partial_payload_quarantined",false)), "%s partial raster is quarantined before image decode" % operator.display_name)
                _check(int(raster_contract.get("declared_bytes",0)) > int(raster_contract.get("decoded_bytes",0)) and int(raster_contract.get("decoded_bytes",0)) > 0, "%s partial raster exposes RIFF declared/present byte gap" % operator.display_name)
                _check(not bool(raster_contract.get("authored_raster",true)), "%s partial raster never activates" % operator.display_name)
                if motion_lab_active:
                    _check(bool(raster_contract.get("svg_render_hidden",false)), "%s Motion Studio runtime exclusively replaces the visible vector layer" % operator.display_name)
                elif aster_v4_active:
                    _check(bool(raster_contract.get("svg_render_hidden",false)), "%s V4 preview exclusively replaces the visible vector layer" % operator.display_name)
                else:
                    _check(not bool(raster_contract.get("svg_render_hidden",true)), "%s partial raster preserves validated vector rendering" % operator.display_name)
            elif raster_status == "missing":
                _check(not bool(raster_contract.get("authored_raster",true)), "%s missing raster remains on validated vector rendering" % operator.display_name)
                if motion_lab_active:
                    _check(bool(raster_contract.get("svg_render_hidden",false)), "%s Motion Studio runtime replaces the missing-raster fallback layer" % operator.display_name)
                elif aster_v4_active:
                    _check(bool(raster_contract.get("svg_render_hidden",false)), "%s V4 preview replaces the missing-raster fallback layer" % operator.display_name)
                else:
                    _check(not bool(raster_contract.get("svg_render_hidden",true)), "%s missing raster never hides vector rendering" % operator.display_name)
            elif raster_status == "loaded":
                _check(bool(raster_contract.get("payload_complete",false)), "%s loaded raster owns a complete RIFF payload" % operator.display_name)
                _check(bool(raster_contract.get("authored_raster",false)), "%s validated raster activates" % operator.display_name)
                _check(bool(raster_contract.get("svg_render_hidden",false)), "%s validated raster replaces only visible vector rendering" % operator.display_name)
            elif raster_status == "superseded_by_fast_runtime":
                # A complete FastCharacterRuntime atlas is the sole body
                # renderer for this operator.  The legacy raster staging layer
                # must remain present for provenance but must not draw a second
                # independently bobbing body beside it.
                _check(not bool(raster_contract.get("authored_raster",true)), "%s legacy raster stays inactive beside FastCharacterRuntime" % operator.display_name)
                _check(not bool(raster_contract.get("partial_payload_quarantined",false)), "%s FastCharacterRuntime supersession is not a malformed payload" % operator.display_name)
            elif raster_status == "superseded_by_motion_lab":
                _check(motion_lab_active, "%s only retires the staged raster after the current Motion Studio runtime is active" % operator.display_name)
                _check(not bool(raster_contract.get("authored_raster",true)), "%s staged raster cannot draw a second body beside Motion Studio" % operator.display_name)
                _check(not bool(raster_contract.get("partial_payload_quarantined",false)), "%s Motion Studio supersession is not a malformed payload" % operator.display_name)
            else:
                _check(false, "%s raster staging status is recognized" % operator.display_name)

    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    _check(camera_presentation != null, "M7 target-aware camera exists")
    if camera_presentation:
        var camera_contract := camera_presentation.debug_camera_contract()
        _check(bool(camera_contract.get("m7_camera", false)), "M7 camera contract is active")
        _check(bool(camera_contract.get("target_aware_combat_frame", false)), "camera frames actual hostile group")
        _check(float(camera_contract.get("combat_target_weight", 0.0)) >= 0.35, "camera reserves enemy-side screen space")
        _check(bool(camera_contract.get("boss_safe_frame", false)), "camera owns dedicated boss safe framing")
        _check(bool(camera_contract.get("priority_boss_scan_m3_enemies", false)), "boss framing uses authoritative live-enemy scan")
        _check(bool(camera_contract.get("boss_targetability_independent", false)), "boss framing is independent from combat targetability")
        _check(bool(camera_contract.get("boss_zoom_out", false)), "boss framing owns a dedicated zoom-out")
        _check(float(camera_contract.get("boss_combat_target_weight", 0.0)) >= 0.48, "boss framing reserves additional target space")
        _check(float(camera_contract.get("boss_zoom", 99.0)) <= 1.05, "boss framing zooms out enough for giant silhouette clearance")
        _check(float(camera_contract.get("normal_zoom", 0.0)) - float(camera_contract.get("boss_zoom", 99.0)) >= 0.35, "boss zoom materially differs from normal traversal zoom")

    var boss_arena := stage.get_node_or_null("BossArenaPresentation") as BossArenaPresentation
    _check(boss_arena != null, "Core C has dedicated boss arena presentation")
    if boss_arena:
        var arena_contract := boss_arena.debug_contract()
        _check(int(arena_contract.get("pylon_count",0)) == 4, "Core C owns four authored pylon anchors")
        _check(int(arena_contract.get("phase1_active_pylons",-1)) == 0, "Phase 1 pylons stay dormant")
        _check(int(arena_contract.get("phase2_active_pylons",0)) == 2, "Phase 2 activates two opposing pylons")
        _check(int(arena_contract.get("phase3_active_pylons",0)) == 4, "Phase 3 activates all four pylons")
        _check(int(arena_contract.get("phase3_wedges",0)) == 4, "Phase 3 uses four readable arena wedges")
        _check(bool(arena_contract.get("weakpoint_exposed_phase3",false)), "Phase 3 exposes the authored weakpoint core")
        _check(bool(arena_contract.get("phase3_body_clear",false)), "Phase 3 keeps the boss body readable")
        _check(bool(arena_contract.get("clear_movement_gaps",false)), "Phase 3 preserves movement gaps")
        _check(bool(arena_contract.get("floor_only_telegraphs",false)), "Phase 3 telegraphs remain on the floor plane")
        _check(int(arena_contract.get("arena_z",99)) <= -1, "boss arena renders behind combatants")

    stage.current_step = 4
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(4)
    await _frames(6)
    var boss: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            boss = node
            break
    _check(boss != null, "M7 boss spawns in Core C")
    if boss:
        _check(stage.battlefield.call("contains", boss.global_position), "boss body is grounded inside the actual Core C plate")
        _check(boss.global_position.distance_to(boss_arena.debug_contract().arena_center) < 2.0, "boss telegraphs follow the actual encounter anchor")
        var boss_focus_operator := stage.squad.get_active_operator()
        if boss_focus_operator:
            # Stand where the live boss encounter places the squad (continuous
            # map world coordinates), not a pre-streaming fixed screen point.
            boss_focus_operator.global_position = stage.battlefield.call("squad_spawn", 0)
            boss_focus_operator.aim_world = (boss.global_position-boss_focus_operator.global_position).normalized()
        boss.health = boss.max_health * 0.24
        await _frames(6)
        var premium := boss.get_node_or_null("PremiumPresentation") as PremiumEnemyPresentation
        _check(premium != null and premium.debug_phase() == 3, "M7 boss reaches Phase 3")
        if premium:
            var phase_contract := premium.debug_m7_phase_contract()
            _check(int(phase_contract.get("phase3_burst",0)) == 5, "Phase 3 keeps five separated lanes")
            _check(bool(phase_contract.get("body_clear",false)), "Phase 3 body remains visually readable")
        _check(boss_arena != null and boss_arena.debug_phase() == 3, "boss arena follows boss into Phase 3")
        _check(boss_arena != null and boss_arena.debug_active_pylon_count() == 4, "Phase 3 runtime has four active pylons")
        _check(boss_arena != null and boss_arena.debug_weakpoint_exposed(), "Phase 3 runtime exposes the weakpoint")
        _check(not boss.is_in_group("prototype_targets"), "Phase 3 targetability guard temporarily removes boss from combat target group")
        if camera_presentation:
            var phase3_camera := camera_presentation.debug_focus_context()
            _check(bool(phase3_camera.get("boss_focus",false)), "camera retains boss focus while Phase 3 targetability guard is active")
            _check(float(phase3_camera.get("zoom",99.0)) <= 1.05, "Phase 3 runtime activates giant-boss zoom-out")
            var camera_boss := phase3_camera.get("boss") as EnemyActor
            _check(camera_boss == boss, "camera priority scan resolves the authoritative live boss")

    var active := stage.squad.get_active_operator()
    if active:
        active.set_movement_bounds(Rect2(100,100,2500,1000))
        # The test must begin inside the current combat floor, not teleport
        # back to the first room while the Core C floor remains active.
        active.global_position = stage.battlefield.call("squad_spawn", 0)
        var start := active.global_position
        active.debug_drive(Vector2(1,-1).normalized(), Vector2.RIGHT)
        await _physics_frames(10)
        var travel := active.global_position-start
        _check(travel.x > 5.0 and travel.y < -5.0, "M7 preserves true diagonal movement")
        _check(active.aim_world.dot(Vector2.RIGHT) > 0.98, "M7 preserves independent aim")

        var sector_visual := active.get_node_or_null("SectorSilhouettePresentation") as OperatorSectorSilhouettePresentation
        var scale_guard := active.get_node_or_null("DirectionalScaleGuard") as OperatorDirectionalScaleGuard
        _check(sector_visual != null, "M7 attaches eight-sector silhouette presentation")
        _check(scale_guard != null, "M7 attaches directional scale normalization")
        if scale_guard:
            var scale_contract := scale_guard.debug_contract()
            _check(bool(scale_contract.get("prevents_direction_size_pumping",false)), "direction scale guard forbids head-size pumping")
            _check(float(scale_contract.get("profile_head_scale",99.0)) <= 0.85, "profile replacement head is normalized to frontal gameplay scale")
            _check(float(scale_contract.get("rear_head_scale",99.0)) <= 0.87, "rear replacement head is normalized to frontal gameplay scale")
        if sector_visual:
            # Keep debug drive active while sampling. A controlled operator otherwise
            # refreshes aim from the mouse every physics frame, which made the old
            # runtime direction evidence collapse back to one facing.
            active.debug_drive(Vector2.ZERO, Vector2.RIGHT)
            await _physics_frames(2)
            sector_visual.sync_now()
            if scale_guard: scale_guard.sync_now()
            var side_contract := sector_visual.debug_current_contract()
            active.debug_drive(Vector2.ZERO, Vector2.DOWN)
            await _physics_frames(2)
            sector_visual.sync_now()
            if scale_guard: scale_guard.sync_now()
            var front_contract := sector_visual.debug_current_contract()
            active.debug_drive(Vector2.ZERO, Vector2.UP)
            await _physics_frames(2)
            sector_visual.sync_now()
            if scale_guard: scale_guard.sync_now()
            var rear_contract := sector_visual.debug_current_contract()

            _check(int(side_contract.get("sector",-1)) == 0 and bool(side_contract.get("profile",false)), "sector 0 resolves as a true profile silhouette")
            _check(float(side_contract.get("body_width",1.0)) <= 0.74, "profile body width is visibly compressed")
            _check(float(side_contract.get("shoulder_width",1.0)) <= 0.60, "profile shoulders collapse into side depth")
            _check(float(side_contract.get("face_width",1.0)) <= 0.50, "profile face is narrowed instead of front-facing")
            _check(bool(side_contract.get("profile_replacement_active",false)), "profile sector uses authored directional identity plates")
            _check(int(side_contract.get("directional_profile_plate_count",0)) >= 10, "profile replacement owns layered head torso and identity detail")
            _check(not bool(side_contract.get("baked_head_visible",true)), "profile sector suppresses the baked frontal head")
            _check(bool(side_contract.get("baked_front_core_suppressed",false)), "profile sector cannot leak frontal core art")
            _check(str(side_contract.get("identity","GENERIC")) != "GENERIC", "directional plates preserve operator identity")

            _check(int(front_contract.get("sector",-1)) == 2 and float(front_contract.get("body_width",0.0)) >= 0.98, "front sector restores full body width")
            _check(bool(front_contract.get("baked_head_visible",false)), "front sector restores authored frontal head")

            _check(int(rear_contract.get("sector",-1)) == 6 and bool(rear_contract.get("rear",false)), "sector 6 resolves as rear presentation")
            _check(float(rear_contract.get("body_width",0.0)) >= 0.98, "rear sector keeps full rear silhouette width")
            _check(bool(rear_contract.get("rear_replacement_active",false)), "rear sector uses authored rear identity plates")
            _check(int(rear_contract.get("directional_rear_plate_count",0)) >= 8, "rear replacement owns layered hair backplate and rear armor")
            _check(not bool(rear_contract.get("baked_head_visible",true)), "rear sector removes baked facial art")
            _check(bool(rear_contract.get("baked_front_core_suppressed",false)), "rear sector cannot leak frontal core art")
            _check(absf(float(front_contract.get("body_width",0.0))-float(side_contract.get("body_width",0.0))) >= 0.24, "front/profile silhouettes differ materially")
        active.debug_stop_drive()

    stage.queue_free()
    await process_frame
    if failures.is_empty():
        print("M7_AUTHORED_VISUAL_SMOKE: PASS")
        quit(0)
        return
    print("M7_AUTHORED_VISUAL_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - "+failure)
    quit(1)

func _frames(count:int) -> void:
    for _i in range(count): await process_frame

func _physics_frames(count:int) -> void:
    for _i in range(count): await physics_frame

func _check(condition:bool,label:String) -> void:
    if condition:
        print("PASS: "+label)
    else:
        failures.append(label)
        push_error("FAIL: "+label)
