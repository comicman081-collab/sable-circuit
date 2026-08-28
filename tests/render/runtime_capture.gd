extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const RESULTS_SCENE := preload("res://scenes/ui/MissionResults.tscn")
const LOBBY_SCENE := preload("res://scenes/base/BaseLobby.tscn")
const OUT_DIR := "res://artifacts/runtime_capture"
const CORE_CENTER := Vector2(1920.0, 490.0)
const REQUIRED_EVIDENCE: Array[String] = [
    "01_map_movement.png","02_combat_decon.png","03_boss_phase3.png",
    "19_direction_sector_7.png","24_death_boss.png",
    "25_m8_extraction_window.png","26_m8_wipe_results.png","27_m8_base_armory.png"
]

var stage: StoryStage01
var camera: Camera2D
var camera_presentation: SquadCameraPresentation
var capture_failed := false

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    DisplayServer.window_set_size(Vector2i(1280, 720))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    stage = STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _settle(10)
    camera = stage.get_node("Camera2D") as Camera2D
    camera_presentation = stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    camera.enabled = true
    camera.position_smoothing_enabled = false
    stage.set_process(false)
    await _capture_movement()
    await _capture_combat()
    await _capture_boss_phase3()
    await _capture_all_rooms()
    await _capture_eight_directions()
    await _capture_unique_deaths()
    await _capture_m8_extraction_window()
    await _capture_m8_wipe_results()
    await _capture_m8_base_armory()
    if capture_failed or not _verify_required_evidence():
        quit(1)
        return
    print("RUNTIME_CAPTURE: PASS")
    quit(0)

func _capture_movement() -> void:
    await _clear_enemies()
    stage.current_step = 0
    stage.call("_activate_step")
    _place_squad(Vector2(320,515), Vector2(0.98,-0.18))
    var active := stage.squad.get_active_operator()
    if active:
        active.debug_drive(Vector2(1.0,-1.0).normalized(), Vector2(0.98,-0.18))
    await _settle(11)
    _focus_live_camera()
    await _settle(1)
    await _save("01_map_movement.png")
    if active:
        active.debug_stop_drive()
    await _settle(2)

func _capture_combat() -> void:
    await _clear_enemies()
    stage.current_step = 1
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(1)
    _place_squad(Vector2(548,432), Vector2(0.98,-0.14))
    await _settle(22)
    var active := stage.squad.get_active_operator()
    if active:
        active.aim_world = Vector2(0.98,-0.14).normalized()
        active.debug_fire_once()
    _focus_live_camera()
    await _settle(1)
    await _save("02_combat_decon.png")

func _capture_boss_phase3() -> void:
    await _clear_enemies()
    stage.current_step = 4
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(4)
    _place_squad(Vector2(1695,615), Vector2(0.96,-0.28))
    await _settle(8)
    var boss: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
            boss = node
            break
    var boss_arena := stage.get_node_or_null("BossArenaPresentation") as BossArenaPresentation
    if boss == null or boss_arena == null or camera_presentation == null:
        push_error("boss capture missing boss, arena or camera presentation")
        capture_failed = true
        return
    if boss.global_position.distance_to(CORE_CENTER) >= 12.0:
        push_error("boss capture body escaped the Core C anchor zone")
        capture_failed = true
        return
    boss.health = boss.max_health * 0.24
    await _settle(18)
    if boss_arena.debug_phase() != 3 or boss_arena.debug_active_pylon_count() != 4 or not boss_arena.debug_weakpoint_exposed():
        push_error("boss capture Phase 3 arena contract failed")
        capture_failed = true
        return
    var camera_context := camera_presentation.debug_focus_context()
    if not bool(camera_context.get("boss_focus",false)):
        push_error("boss capture camera lost Phase 3 boss while targetability guard was active")
        capture_failed = true
        return
    var boss_zoom := float(camera_context.get("zoom",99.0))
    if boss_zoom > 1.05:
        push_error("boss capture camera failed giant-boss zoom-out: %.3f" % boss_zoom)
        capture_failed = true
        return
    print("BOSS_CAMERA_EVIDENCE guard_targetable=%s boss_focus=%s zoom=%.3f target=%s" % [
        str(boss.is_in_group("prototype_targets")),
        str(bool(camera_context.get("boss_focus",false))),
        boss_zoom,
        str(camera_context.get("target",Vector2.ZERO))
    ])
    _focus_live_camera()
    await _settle(2)
    await _save("03_boss_phase3.png")

func _capture_all_rooms() -> void:
    await _clear_enemies()
    var rooms: Array = [
        ["04_room_outer_gate.png", Vector2(280,470),0],
        ["05_room_decon_corridor.png", Vector2(690,350),1],
        ["06_room_archive_annex.png", Vector2(1100,490),2],
        ["07_room_containment_junction.png", Vector2(1510,350),3],
        ["08_room_core_c.png", Vector2(1920,490),4],
        ["09_room_emergency_lift.png", Vector2(2330,350),5],
        ["10_room_emergency_stores.png", Vector2(1100,705),2],
        ["11_room_signal_lab.png", Vector2(1510,705),3]
    ]
    for row in rooms:
        var filename: String = str(row[0])
        var pos: Vector2 = row[1]
        stage.current_step = int(row[2])
        stage.call("_activate_step")
        _place_squad(pos + Vector2(-118,82), Vector2(0.98,-0.10))
        camera.global_position = pos
        camera.zoom = Vector2.ONE * 1.46
        await _settle(8)
        camera.global_position = pos
        await _settle(1)
        await _save(filename)

func _capture_eight_directions() -> void:
    await _clear_enemies()
    stage.current_step = 2
    stage.call("_activate_step")
    camera.global_position = Vector2(1100,490)
    camera.zoom = Vector2.ONE * 1.46
    stage.squad.request_control(0)
    var direction_positions: Array[Vector2] = [Vector2(1030,515), Vector2(1100,515), Vector2(1170,515)]
    for i in range(stage.squad.operators.size()):
        var actor := stage.squad.operators[i]
        actor.visible = true
        actor.global_position = direction_positions[i]
        actor.velocity = Vector2.ZERO
    var vectors: Array[Vector2] = [
        Vector2.RIGHT,Vector2(1,1).normalized(),Vector2.DOWN,Vector2(-1,1).normalized(),
        Vector2.LEFT,Vector2(-1,-1).normalized(),Vector2.UP,Vector2(1,-1).normalized()
    ]
    for sector in range(8):
        for actor in stage.squad.operators:
            actor.global_position = direction_positions[stage.squad.operators.find(actor)]
            actor.debug_drive(Vector2.ZERO, vectors[sector])
            actor.velocity = Vector2.ZERO
        await physics_frame
        await physics_frame
        await _settle(1)
        for actor in stage.squad.operators:
            if actor.facing_sector != sector:
                push_error("direction evidence sector drift: %s expected=%d actual=%d" % [actor.display_name, sector, actor.facing_sector])
                capture_failed = true
                break
        if capture_failed:
            break
        camera.global_position = Vector2(1100,490)
        camera.zoom = Vector2.ONE * 1.46
        await _save("%02d_direction_sector_%d.png" % [12+sector,sector])
    for actor in stage.squad.operators:
        actor.debug_stop_drive()

func _capture_unique_deaths() -> void:
    await _clear_enemies()
    stage.current_step = 3
    stage.call("_activate_step")
    var ids: Array[String] = ["ENM_SITE7_RIFLE_01","ENM_SITE7_SHIELD_01","ENM_SITE7_DRONE_01","ENM_SITE7_ABERRANT_01","BOSS_SITE7_ANCHOR_01"]
    var names: Array[String] = ["rifle","shield","drone","aberrant","boss"]
    var camera_was_processing := false
    if camera_presentation != null:
        camera_was_processing = camera_presentation.is_processing()
        camera_presentation.set_process(false)
    camera.zoom = Vector2.ONE * 1.46
    for i in range(ids.size()):
        await _clear_enemies()
        var center := Vector2(1510,350)
        var death_origin := center + Vector2(72,0)
        camera.global_position = death_origin
        _place_squad(center+Vector2(-190,118),Vector2.RIGHT)
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(ids[i],300.0 if i==4 else 90.0)
        enemy.global_position = death_origin
        stage.add_child(enemy)
        await _settle(4)
        enemy.apply_damage(9999.0)
        var sequence := await _await_death_sequence(ids[i])
        if sequence == null:
            push_error("death evidence missing sequence for " + ids[i])
            capture_failed = true
            break
        if sequence.debug_piece_count() <= 0:
            push_error("death evidence has zero authored fragments for " + ids[i])
            capture_failed = true
            break
        var target_progress := 0.30 if i < 4 else 0.24
        var guard := 0
        while is_instance_valid(sequence) and sequence.debug_progress() < target_progress and guard < 60:
            camera.global_position = death_origin
            await process_frame
            guard += 1
        if not is_instance_valid(sequence) or sequence.debug_piece_count() <= 0:
            push_error("death evidence expired before capture for " + ids[i])
            capture_failed = true
            break
        camera.global_position = death_origin
        await _settle(1)
        camera.global_position = death_origin
        print("DEATH_EVIDENCE: %s mode=%s pieces=%d progress=%.3f" % [ids[i], sequence.debug_mode(), sequence.debug_piece_count(), sequence.debug_progress()])
        await _save("%02d_death_%s.png" % [20+i,names[i]])
    if camera_presentation != null:
        camera_presentation.set_process(camera_was_processing)

func _capture_m8_extraction_window() -> void:
    await _clear_enemies()
    stage.visible = true
    stage.hud.visible = true
    stage.current_step = 4
    stage.call("_activate_step")
    stage.debug_seed_cargo(115,85,2,1,true,5)
    stage.debug_offer_extraction("R05_CORE_C")
    _place_squad(Vector2(1695,615),Vector2(0.96,-0.28))
    camera.global_position = CORE_CENTER
    camera.zoom = Vector2.ONE * 1.28
    await _settle(4)
    if not stage.hud.debug_extraction_visible():
        push_error("M8 extraction capture missing visible extraction decision panel")
        capture_failed = true
        return
    var cargo_text := stage.hud.debug_cargo_text()
    if not ("R 115" in cargo_text and "+HV 085" in cargo_text and "S 02" in cargo_text and "F 01" in cargo_text):
        push_error("M8 extraction capture cargo HUD is not authoritative: " + cargo_text)
        capture_failed = true
        return
    await _save("25_m8_extraction_window.png")

func _capture_m8_wipe_results() -> void:
    stage.hud.visible = false
    stage.visible = false
    var wipe_summary := stage.debug_wipe_summary()
    wipe_summary["campaign"] = {
        "research_value":364,"salvage":3,"signal_fragments":1,"armory_level":1,"lab_level":1
    }
    var results := RESULTS_SCENE.instantiate() as MissionResults
    results.configure(wipe_summary)
    root.add_child(results)
    await _settle(4)
    var shown := results.debug_summary()
    if str(shown.get("outcome","")) != "WIPED" or bool(shown.get("carrier_fragment_secured",true)):
        push_error("M8 wipe result capture does not distinguish found vs secured high-value cargo")
        capture_failed = true
    await _save("26_m8_wipe_results.png")
    results.queue_free()
    await process_frame

func _capture_m8_base_armory() -> void:
    var lobby := LOBBY_SCENE.instantiate() as BaseLobby
    lobby.configure_campaign({
        "research_value":620,"salvage":5,"signal_fragments":3,
        "armory_level":1,"lab_level":1,"completed_runs":3,"extracted_runs":2,"wiped_runs":1,
        "damage_multiplier":1.08,"research_multiplier":1.12,"max_upgrade_level":3,
        "armory_cost":{"research":240,"salvage":2,"fragments":0},
        "lab_cost":{"research":220,"salvage":0,"fragments":1}
    })
    root.add_child(lobby)
    await _settle(3)
    lobby.call("_show_facility","ARMORY")
    await _settle(2)
    var snapshot := lobby.debug_campaign_snapshot()
    if int(snapshot.get("research_value",0)) != 620 or int(snapshot.get("armory_level",0)) != 1:
        push_error("M8 base capture campaign snapshot mismatch")
        capture_failed = true
    await _save("27_m8_base_armory.png")
    lobby.queue_free()
    await process_frame

func _await_death_sequence(expected_id: String) -> EnemyDeathSequence:
    for _frame in range(18):
        for node in get_nodes_in_group("enemy_death_sequences"):
            if node is EnemyDeathSequence and node.enemy_id == expected_id:
                return node as EnemyDeathSequence
        await process_frame
    return null

func _place_squad(center: Vector2, aim: Vector2) -> void:
    var aim_dir := aim.normalized() if aim.length_squared() > 0.001 else Vector2.RIGHT
    var side := Vector2(-aim_dir.y,aim_dir.x)
    var rear := -aim_dir
    var positions: Array[Vector2] = [center,center+rear*82.0+side*72.0,center+rear*118.0-side*48.0]
    for i in range(stage.squad.operators.size()):
        var actor := stage.squad.operators[i]
        actor.global_position = positions[i]
        actor.aim_world = aim_dir
        actor.facing_sector = actor.call("_sector_from_vector", aim_dir)
        actor.velocity = Vector2.ZERO

func _focus_live_camera() -> void:
    if camera_presentation != null:
        var context := camera_presentation.debug_focus_context()
        camera.global_position = context.get("target", camera_presentation.debug_target_for_active())
        camera.zoom = Vector2.ONE * float(context.get("zoom",1.46))
    elif stage.squad.get_active_operator() != null:
        camera.global_position = stage.squad.get_active_operator().global_position
        camera.zoom = Vector2.ONE * 1.46

func _clear_enemies() -> void:
    for node in get_nodes_in_group("m3_enemies"):
        if is_instance_valid(node): node.queue_free()
    for node in get_nodes_in_group("enemy_death_sequences"):
        if is_instance_valid(node): node.queue_free()
    await process_frame
    await process_frame

func _settle(frames: int) -> void:
    for _i in range(frames): await process_frame

func _save(filename: String) -> void:
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    var path := ProjectSettings.globalize_path(OUT_DIR + "/" + filename)
    var err := image.save_png(path)
    if err != OK:
        push_error("capture failed: " + path + " err=" + str(err))
        capture_failed = true
        return
    print("CAPTURED: " + path)

func _verify_required_evidence() -> bool:
    for filename in REQUIRED_EVIDENCE:
        var path := ProjectSettings.globalize_path(OUT_DIR + "/" + filename)
        if not FileAccess.file_exists(path):
            push_error("missing required runtime evidence: " + filename)
            return false
    return true
