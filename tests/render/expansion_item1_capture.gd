extends SceneTree
## Controlled runtime fixtures in the real operation 6-9 rooms, with their existing
## plates, props, mood and abyss. These are not human play or balance evidence.
## Run windowed for native 1920x1080 PNGs; headless checks fixture geometry only:
## Godot --path . -s res://tests/render/expansion_item1_capture.gd -- --out=res://.cache/<folder>
## Subjects/actors are held still and hazard phases are advanced by the real controller.
## BROODING is triggered through real damage, then hatch timers are held for inspection.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")
const CoverNavigation := preload("res://scripts/combat/cover_navigation.gd")

var out_dir := TestOutput.path("res://.cache/diag/expansion_item1_20261003/capture")
var native_capture := false
var checks := 0
var failures: Array[String] = []
var rows: Array[Dictionary] = []
var events: Array[Dictionary] = []
# Root effects are produced by CombatFeedback, outside the stage subtree.
# Keep only newly-created visual fixture nodes; never free pre-existing roots,
# audio services, autoloaders or unrelated runtime nodes.
var _fixture_scope_active := false
var _fixture_root_baseline: Dictionary = {}
var _fixture_effects: Array[WeakRef] = []

func _begin_fixture_scope() -> void:
    _fixture_root_baseline.clear()
    _fixture_effects.clear()
    for node in root.get_children():
        _fixture_root_baseline[node.get_instance_id()] = true
    _fixture_scope_active = true

func _remember_fixture_effects() -> void:
    if not _fixture_scope_active:
        return
    for node in root.get_children():
        if _fixture_root_baseline.has(node.get_instance_id()):
            continue
        if not (node is PrototypeProjectile or node is CombatExplosionVFX or node is CombatHitVFX or node.is_in_group("vfx_ground_marks")):
            continue
        var remembered := false
        for reference in _fixture_effects:
            if reference.get_ref() == node:
                remembered = true
                break
        if not remembered:
            _fixture_effects.append(weakref(node))

func _init() -> void:
    call_deferred("_run")

func _check(ok: bool, message: String) -> void:
    checks += 1
    if not ok:
        failures.append(message)
        push_error(message)

func _run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    native_capture = DisplayServer.get_name() != "headless"
    if native_capture:
        DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))
    GameSettings.load_once()
    var prior_shake := GameSettings.screen_shake
    GameSettings.screen_shake = false # memory only; never save the player's setting
    await _brooding()
    await _beacon()
    await _hazard("MIS_CH01_06", "SPORE_CLOUD")
    await _hazard("MIS_CH01_07", "FROST_PLATE")
    await _hazard("MIS_CH01_08", "RAIL_LANE")
    GameSettings.screen_shake = prior_shake
    var report := {
        "status": "PASS_TECHNICAL_ONLY" if failures.is_empty() else "FAIL",
        "checks": checks, "failures": failures, "native_capture": native_capture,
        "native_resolution": [1920, 1080] if native_capture else [],
        "controlled_runtime_fixture": true, "human_play": false, "visual_approval": false,
        "balance_approval": false, "rows": rows, "events": events,
        "skipped_fixtures": events.filter(func(event: Dictionary) -> bool: return event.get("status", "") == "SKIP_NO_PLACEMENT"),
        "staging_note": "Real mission rooms and runtime controllers. Actors are frozen; hazard phases and hatch timers are held for inspection. BROODING parent damage is a capture fixture, not player damage. No art or mission data is changed.",
        "headless_note": "Headless checks fixture geometry only and emits no image evidence.",
        "art_note": "Existing common weathering is retained. Affixes add no sprite material or tint."
    }
    var file := FileAccess.open(out_dir.path_join("capture_report.json"), FileAccess.WRITE)
    _check(file != null, "capture report can be opened")
    if file != null:
        report["checks"] = checks
        report["failures"] = failures
        file.store_string(JSON.stringify(report, "  "))
        file.close()
    print("EXPANSION_ITEM1_CAPTURE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks) ", out_dir)
    quit(0 if failures.is_empty() else 1)

func _open(mission: String, step: int) -> StoryStage01:
    _begin_fixture_scope()
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    stage.battle_preview = true
    root.add_child(stage)
    _freeze(stage)
    await _settle(6)
    stage.start_battle_preview(step)
    _freeze(stage)
    for node in get_nodes_in_group("zone_hazards"):
        if stage.is_ancestor_of(node):
            node.set_physics_process(false)
    await _settle(4)
    _check(stage.has_battle_floor(), mission + " fixture uses its actual painted floor")
    _check(stage.current_step == step, mission + " fixture opened requested room")
    return stage

func _freeze(stage: StoryStage01) -> void:
    stage.set_process(false)
    stage.set_physics_process(false)
    stage.squad.set_process(false)
    stage.squad.set_physics_process(false)
    for actor in stage.squad.operators:
        actor.set_process(false)
        actor.set_physics_process(false)
    var presentation := stage.get_node_or_null("SquadCameraPresentation")
    if presentation != null:
        presentation.set_process(false)
    for enemy in _enemies(stage):
        enemy.set_physics_process(false)

func _enemies(stage: StoryStage01) -> Array[EnemyActor]:
    var result: Array[EnemyActor] = []
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and stage.is_ancestor_of(node) and node.health > 0.0:
            result.append(node as EnemyActor)
    return result

func _with_affix(stage: StoryStage01, id: String) -> EnemyActor:
    for enemy in _enemies(stage):
        var affix := enemy.get_node_or_null("EliteAffix") as EliteAffix
        if affix != null and affix.affix_id == id:
            return enemy
    return null

func _has_declared_affix(value: Variant, id: String) -> bool:
    if value is Dictionary:
        if str(value.get("affix", "")).strip_edges().to_upper() == id:
            return true
        for child in value.values():
            if _has_declared_affix(child, id):
                return true
    elif value is Array:
        for child in value:
            if _has_declared_affix(child, id):
                return true
    return false

func _has_declared_hazard(stage: StoryStage01, id: String) -> bool:
    var room: Dictionary = stage.main_route[stage.current_step]
    for value in room.get("hazards", []):
        if value is Dictionary and str(value.get("type", "")).strip_edges().to_upper() == id:
            return true
    return false

func _skip_no_placement(stage: StoryStage01, id: String) -> void:
    var room: Dictionary = stage.main_route[stage.current_step]
    var reason := "Actual mission JSON has no %s declaration in %s; capture fixture skipped. Separate feature-mechanics tests still run." % [id, str(room.id)]
    events.append({"status": "SKIP_NO_PLACEMENT", "fixture": id, "mission": stage.mission_id,
        "room": str(room.id), "reason": reason, "capture": "", "image_evidence": false})
    print("EXPANSION_ITEM1_CAPTURE: SKIP_NO_PLACEMENT ", stage.mission_id, " ", str(room.id), " ", id, " // ", reason)

func _frame(stage: StoryStage01, subjects: Array[EnemyActor], floor_point := Vector2.INF) -> void:
    var bounds := Rect2()
    var initialized := false
    for subject in subjects:
        var rect := subject.get_combat_hit_rect().grow(28.0)
        if not initialized:
            bounds = rect
            initialized = true
        else:
            bounds = bounds.merge(rect)
    if floor_point.is_finite():
        var floor_bounds := Rect2(floor_point - Vector2(190, 115), Vector2(380, 230))
        bounds = bounds.merge(floor_bounds) if initialized else floor_bounds
        initialized = true
    if initialized:
        stage.camera.global_position = bounds.get_center() + Vector2(0, 18)
    # The normal production camera zoom is retained. This is a camera placement,
    # not a sprite or source-art resize.
    stage.camera.zoom = Vector2.ONE * SquadCameraPresentation.NORMAL_ZOOM
    stage.camera.offset = Vector2.ZERO
    stage.camera.position_smoothing_enabled = false
    stage.camera.force_update_scroll()

func _label(stage: StoryStage01, title: String, tip: String) -> void:
    stage.hud.show_transmission("CONTROLLED RUNTIME FIXTURE // NOT HUMAN PLAY\n" + title, 3600.0)
    stage.hud.set_story(tip)

func _brooding() -> void:
    var stage := await _open("MIS_CH01_06", 3)
    if not _has_declared_affix(stage.main_route[stage.current_step], "BROODING"):
        _skip_no_placement(stage, "BROODING")
        await _close(stage)
        return
    var parent := _with_affix(stage, "BROODING")
    _check(parent != null, "operation 6 R04 contains its declared BROODING parent")
    if parent == null:
        await _close(stage)
        return
    var affix := parent.get_node("EliteAffix") as EliteAffix
    _check(stage.battlefield.is_walkable(parent.global_position), "BROODING parent is on walkable painted floor")
    var before := stage.enemies_alive
    var parent_at := parent.global_position
    _frame(stage, [parent])
    _label(stage, "OP6 R04 // BROODING PARENT", EliteAffix.tip("BROODING"))
    await _capture(stage, "01_op6_brooding_parent", "BROODING_PARENT", [parent])
    parent.apply_damage(99999.0)
    parent.hide()
    var hatchlings: Array[EnemyActor] = []
    for enemy in _enemies(stage):
        if enemy.brood_generation == 1 and int(enemy.get_meta("brood_parent_id", 0)) == parent.get_instance_id():
            enemy.set_physics_process(false)
            enemy.brood_hatch_left = enemy.brood_hatch_duration * 0.5
            enemy.queue_redraw()
            hatchlings.append(enemy)
    _check(hatchlings.size() == 2, "real BROODING parent damage spawned exactly two hatchlings")
    _check(stage.enemies_alive == before + 1, "BROODING count reflects children +2 and parent -1")
    for child in hatchlings:
        _check(child.get_node_or_null("EliteAffix") == null and child.brood_hatch_left >= 0.3, "hatchling is plain and held in its hatch warning")
        _check(stage.battlefield.is_walkable(child.global_position), "hatchling remains on actual room floor")
    _remember_fixture_effects()
    # Robot destruction lasts at most 1.45 s. Let the actual effect expire while
    # the hatch timers remain held, so fire/smoke cannot obscure the two rings.
    await create_timer(1.5).timeout
    await _settle(2)
    for reference in _fixture_effects:
        var effect = reference.get_ref()
        _check(not is_instance_valid(effect) or not effect is CombatExplosionVFX, "BROODING destruction effect naturally expired before the hatch-ring frame")
    events.append({"fixture": "BROODING", "mission": stage.mission_id,
        "parent_position": _xy(parent_at), "parent_capture_damage": 99999.0,
        "parent_health_before": parent.max_health, "enemy_count_before": before,
        "enemy_count_after": stage.enemies_alive, "hatchlings": hatchlings.size(),
        "hatch_duration": float(affix.spec.get("brood_hatch_windup", 0.0)),
        "destruction_settle_seconds": 1.5,
        "order": "Real apply_damage reserves both hatchlings before the parent defeated signal; hatch timers then held, actual destruction effect allowed to expire for 1.5 s, stage and owned fixture effects freed after capture."})
    _frame(stage, hatchlings, parent_at)
    _label(stage, "OP6 R04 // TWO PLAIN DRONES HATCHING", "CAPTURE FIXTURE: hatch timers held at halfway through the real warning; actors do not attack.")
    await _capture(stage, "02_op6_brooding_hatching", "BROODING_HATCHING", hatchlings)
    for child in hatchlings:
        child.brood_hatch_left = 0.0
        child.queue_redraw()
    _label(stage, "OP6 R04 // TWO PLAIN DRONES HATCHED", "CAPTURE FIXTURE: hatch timers completed; plain drone art and existing common weathering are unchanged.")
    await _capture(stage, "03_op6_brooding_hatched", "BROODING_HATCHED", hatchlings)
    await _close(stage)

func _beacon() -> void:
    var stage := await _open("MIS_CH01_09", 3)
    if not _has_declared_affix(stage.main_route[stage.current_step], "BEACON"):
        _skip_no_placement(stage, "BEACON")
        await _close(stage)
        return
    var source := _with_affix(stage, "BEACON")
    _check(source != null, "operation 9 R04 contains its declared BEACON robot")
    if source == null:
        await _close(stage)
        return
    var affix := source.get_node("EliteAffix") as EliteAffix
    var peers := affix.linked_enemies()
    _check(peers.size() >= 1 and peers.size() <= 6, "BEACON fixture displays between one and six real protection links")
    var subjects: Array[EnemyActor] = [source]
    subjects.append_array(peers)
    _frame(stage, subjects)
    _label(stage, "OP9 R04 // BEACON PROTECTION LINKS", EliteAffix.tip("BEACON"))
    await _capture(stage, "04_op9_beacon_links", "BEACON_LINKED", subjects)
    var peer_positions := peers.map(func(peer: EnemyActor) -> Array: return _xy(peer.global_position))
    events.append({"fixture": "BEACON", "mission": stage.mission_id, "links_before": peers.size(),
        "reduction": affix.spec.get("beacon_reduction", 0.0), "peer_positions": peer_positions})
    source.apply_damage(99999.0)
    source.hide()
    for peer in peers:
        _check(EliteAffix.beacon_for(peer) == null, "BEACON death immediately releases each protected peer")
    _label(stage, "OP9 R04 // BEACON DESTROYED, LINKS RELEASED", "CAPTURE FIXTURE: source destroyed through real damage; the existing robot art keeps its common weathering and no variant tint.")
    await _capture(stage, "05_op9_beacon_released", "BEACON_RELEASED", peers)
    await _close(stage)

func _hazard(mission: String, id: String) -> void:
    var stage := await _open(mission, 1)
    if not _has_declared_hazard(stage, id):
        _skip_no_placement(stage, id)
        await _close(stage)
        return
    var hazard: ZoneHazard = null
    for node in get_nodes_in_group("zone_hazards"):
        if stage.is_ancestor_of(node) and node is ZoneHazard and node.hazard_id == id:
            hazard = node as ZoneHazard
            break
    _check(hazard != null, mission + " R02 contains its declared " + id)
    if hazard == null:
        await _close(stage)
        return
    var subjects: Array[EnemyActor] = []
    for enemy in _enemies(stage):
        if enemy.get_node_or_null("EliteAffix") == null:
            subjects.append(enemy)
    # Use the smallest existing plain robot in this real encounter, keeping its
    # actual art/scale. A pylon's large body otherwise hid most of the cloud.
    subjects.sort_custom(func(a: EnemyActor, b: EnemyActor) -> bool:
        return a.get_combat_hit_rect().get_area() < b.get_combat_hit_rect().get_area())
    if subjects.size() > 1:
        subjects.resize(1)
    var victim := stage.squad.get_active_operator()
    var victim_before := victim.health
    var robot_before := subjects[0].health if not subjects.is_empty() else 0.0
    # Show the actual hazard unobscured through idle and telegraph. The staged
    # targets remain on painted floor outside it until the active frame only.
    victim.global_position = _outside_hazard_point(stage, hazard, victim, -1.0)
    if not subjects.is_empty():
        subjects[0].global_position = _outside_hazard_point(stage, hazard, subjects[0], 1.0)
    # Keep one unchanged camera for the three phases; the normal game zoom stays
    # 1.22, and the hazard's real runtime placement is never changed.
    _frame(stage, [], hazard.global_position)
    var prefix := "%s_%s" % [mission.trim_prefix("MIS_CH01_"), id.to_lower()]
    _label(stage, mission + " R02 // " + id + " FIRST DELAY", ZoneHazard.tip(id))
    await _capture(stage, prefix + "_idle", id + "_IDLE", subjects, hazard)
    # The actual first-delay/telegraph transition is exercised through the hazard
    # controller; the warning is then held for a readable native frame.
    hazard._physics_process(hazard.phase_left + 0.001)
    if id != "FROST_PLATE":
        _check(hazard.phase == ZoneHazard.Phase.TELEGRAPH, id + " enters its real telegraph")
        hazard.phase_left = float(hazard.spec.get("telegraph", 1.0)) * 0.45
        hazard.queue_redraw()
        _label(stage, mission + " R02 // " + id + " TELEGRAPH", "CAPTURE FIXTURE: real warning phase held for inspection; no damage has landed.")
        await _capture(stage, prefix + "_telegraph", id + "_TELEGRAPH", subjects, hazard)
        _check(is_equal_approx(victim.health, victim_before), id + " operator has no warning-phase damage")
        if not subjects.is_empty():
            _check(is_equal_approx(subjects[0].health, robot_before), id + " robot has no warning-phase damage")
        _place_hazard_active_targets(hazard, victim, subjects)
        hazard._physics_process(hazard.phase_left + 0.001)
    else:
        _check(hazard.phase == ZoneHazard.Phase.DISCHARGE, "FROST_PLATE becomes active after its first delay")
        _place_hazard_active_targets(hazard, victim, subjects)
    # One short real-controller tick updates persistent damage or frost tokens.
    hazard._physics_process(0.05)
    hazard.queue_redraw()
    _check(hazard.phase == ZoneHazard.Phase.DISCHARGE, id + " active/discharge phase is held for capture")
    _label(stage, mission + " R02 // " + id + " ACTIVE", "CAPTURE FIXTURE: operator and plain robot deliberately placed on the hazard; real controller advanced, then held.")
    await _capture(stage, prefix + "_active", id + "_ACTIVE", subjects, hazard)
    events.append({"fixture": id, "mission": mission, "position": _xy(hazard.global_position),
        "operator_damage_observed": victim_before - victim.health,
        "robot_damage_observed": robot_before - subjects[0].health if not subjects.is_empty() else 0.0,
        "hazard_contract": hazard.debug_contract(),
        "staging": "Idle/telegraph targets on real painted floor outside the unchanged hazard. Active targets moved to opposite inside ends only, before the real damage/slow controller tick. Smallest existing plain robot chosen; native art and game camera zoom unchanged.",
        "note": "Damage/timing numbers describe a staged frame, not a balance or avoidance test."})
    if id == "FROST_PLATE":
        _check(is_equal_approx(victim.hazard_speed_factor(), float(hazard.spec.get("slow_multiplier", 0.7))), "FROST_PLATE active frame has the actual operator speed token")
        if not subjects.is_empty():
            _check(is_equal_approx(subjects[0].hazard_speed_factor(), float(hazard.spec.get("slow_multiplier", 0.7))), "FROST_PLATE active frame has the actual robot speed token")
        stage._clear_hazards()
        await _settle(3)
        _check(get_nodes_in_group("zone_hazards").filter(func(node: Node) -> bool: return stage.is_ancestor_of(node)).is_empty(), "FROST_PLATE clear removes the room's hazard nodes")
        _check(victim.hazard_speed_factor() == 1.0, "FROST_PLATE clear restores the operator hazard speed factor exactly to 1.0")
        if not subjects.is_empty():
            _check(subjects[0].hazard_speed_factor() == 1.0, "FROST_PLATE clear restores the robot hazard speed factor exactly to 1.0")
        _label(stage, mission + " R02 // FROST PLATE CLEARED", "CAPTURE FIXTURE: normal room hazard clear removed the frost and its speed tokens.")
        await _capture(stage, prefix + "_cleared", "FROST_PLATE_CLEARED", subjects)
    await _close(stage)

func _outside_hazard_point(stage: StoryStage01, hazard: ZoneHazard, actor: Node2D, side: float) -> Vector2:
    var obstacles := CoverNavigation.ground_obstacles(actor, hazard.global_position)
    for extra: float in [110.0, 140.0, 180.0, 220.0]:
        for angle: float in [0.0, -0.25, 0.25, -0.55, 0.55, -1.0, 1.0, -PI * 0.5, PI * 0.5, PI]:
            var point := hazard.global_position + Vector2(side, 0).rotated(angle) * (hazard.radius + extra)
            if hazard.contains(point, 64.0) or not stage.battlefield.is_walkable(point):
                continue
            if obstacles.any(func(rect: Rect2) -> bool: return rect.has_point(point)):
                continue
            return point
    # Authored initial spawns are already clear of hazards and painted walls.
    # Retain that real spawn if no nearer inspection position fits.
    return actor.global_position

func _place_hazard_active_targets(hazard: ZoneHazard, victim: OperatorActor, subjects: Array[EnemyActor]) -> void:
    var left: Vector2
    var right: Vector2
    if hazard.is_band():
        var angle := deg_to_rad(float(hazard.spec.get("angle_degrees", -26.565051177)))
        var x := float(hazard.spec.get("half_length", 90.0)) * 0.85
        var y := -float(hazard.spec.get("half_width", 24.0)) * 0.65
        left = Vector2(-x, y).rotated(angle)
        right = Vector2(x, y).rotated(angle)
    else:
        # Opposite back-rim points are genuinely inside the ellipse:
        # 0.9² + 0.35² = 0.9325. Bodies rise above those feet, leaving its
        # centre and front portion more readable at the unchanged game scale.
        left = Vector2(-hazard.radius * 0.9, -hazard.radius * ZoneHazard.FLOOR_RATIO * 0.35)
        right = Vector2(hazard.radius * 0.9, -hazard.radius * ZoneHazard.FLOOR_RATIO * 0.35)
    victim.global_position = hazard.global_position + left
    if not subjects.is_empty():
        subjects[0].global_position = hazard.global_position + right

func _screen(node: Node2D) -> Vector2:
    return root.get_final_transform() * node.get_global_transform_with_canvas() * Vector2.ZERO

func _xy(point: Vector2) -> Array:
    return [snappedf(point.x, 0.01), snappedf(point.y, 0.01)]

func _actor_row(actor: EnemyActor) -> Dictionary:
    var at := _screen(actor)
    var affix := actor.get_node_or_null("EliteAffix") as EliteAffix
    var art := []
    for node in actor.find_children("*", "Sprite2D", true, false):
        var sprite := node as Sprite2D
        art.append({"node": str(actor.get_path_to(sprite)), "modulate": sprite.modulate.to_html(true),
            "self_modulate": sprite.self_modulate.to_html(true), "material_present": sprite.material != null,
            "material_path": sprite.material.resource_path if sprite.material != null else "",
            "note": "Common weathering is retained; compare with the same plain robot."})
    return {"enemy_id": actor.enemy_id, "position": _xy(actor.global_position), "screen": _xy(at),
        "on_screen": Rect2(Vector2.ZERO, Vector2(1920, 1080)).has_point(at),
        "health": actor.health, "max_health": actor.max_health,
        "affix": affix.affix_id if affix != null else "", "brood_generation": actor.brood_generation,
        "brood_hatch_left": actor.brood_hatch_left, "sprites": art,
        "run_modifiers": actor.debug_run_modifier_contract(), "hazard_speed_factor": actor.hazard_speed_factor()}

func _capture(stage: StoryStage01, label: String, phase_label: String, subjects: Array[EnemyActor], hazard: ZoneHazard = null) -> void:
    for actor in subjects:
        actor.queue_redraw()
    if hazard != null:
        hazard.queue_redraw()
    await _settle(2)
    var actors := []
    for actor in subjects:
        var actor_row := _actor_row(actor)
        _check(bool(actor_row["on_screen"]), label + " subject " + actor.enemy_id + " is visible in native viewport geometry")
        actors.append(actor_row)
    var row := {"fixture": phase_label, "mission": stage.mission_id, "room": str(stage.main_route[stage.current_step].id),
        "capture": "", "sha256": "", "actual_size": [], "native_capture": native_capture,
        "actors": actors, "controlled_runtime_fixture": true,
        "camera_position": _xy(stage.camera.global_position), "camera_zoom": _xy(stage.camera.zoom)}
    var operator_rows := []
    for operator in stage.squad.operators:
        var screen := _screen(operator)
        operator_rows.append({"operator_id": operator.operator_id, "position": _xy(operator.global_position),
            "screen": _xy(screen), "on_screen": Rect2(Vector2.ZERO, Vector2(1920, 1080)).has_point(screen),
            "health": operator.health, "run_modifiers": operator.debug_run_boost_contract(),
            "hazard_speed_factor": operator.hazard_speed_factor()})
    row["operators"] = operator_rows
    if hazard != null:
        var at := _screen(hazard)
        var on_screen := Rect2(Vector2.ZERO, Vector2(1920, 1080)).has_point(at)
        _check(on_screen, label + " hazard is visible in native viewport geometry")
        row["hazard"] = hazard.debug_contract()
        row["hazard_screen"] = _xy(at)
        row["hazard_on_screen"] = on_screen
        _check(Rect2(Vector2.ZERO, Vector2(1920, 1080)).has_point(_screen(stage.squad.get_active_operator())), label + " staged operator is visible in native viewport geometry")
    if native_capture:
        await RenderingServer.frame_post_draw
        var image := root.get_texture().get_image()
        var path := out_dir.path_join(label + ".png")
        _check(image.get_size() == Vector2i(1920, 1080), label + " native screenshot is exactly 1920x1080")
        _check(image.save_png(ProjectSettings.globalize_path(path)) == OK, label + " native screenshot saved")
        row["capture"] = path
        row["actual_size"] = [image.get_width(), image.get_height()]
        row["sha256"] = FileAccess.get_sha256(path)
    rows.append(row)

func _settle(frames: int) -> void:
    for _i in range(frames):
        await physics_frame
        await process_frame
        _remember_fixture_effects()

func _close(stage: StoryStage01) -> void:
    var mission := stage.mission_id
    _remember_fixture_effects()
    _fixture_scope_active = false
    stage.free()
    var removed_effects := 0
    for reference in _fixture_effects:
        var effect = reference.get_ref()
        if is_instance_valid(effect) and effect.get_parent() == root:
            effect.free()
            removed_effects += 1
    _fixture_effects.clear()
    _fixture_root_baseline.clear()
    await _settle(3)
    _check(get_nodes_in_group("m3_enemies").is_empty(), mission + " stage removal leaves no robot orphan")
    _check(get_nodes_in_group("zone_hazards").is_empty(), mission + " stage removal leaves no hazard orphan")
    _check(get_nodes_in_group("elite_beacons").is_empty(), mission + " stage removal leaves no beacon orphan")
    events.append({"mission": mission, "cleanup": "Stage freed with all room actors/hazards; only visual root nodes newly created within this fixture scope were removed. Existing roots/autoloaders and unrelated nodes were untouched.",
        "owned_fixture_root_effects_removed": removed_effects, "orphan_groups_empty": true})
