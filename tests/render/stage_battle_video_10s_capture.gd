extends SceneTree

## Capture-only: an unmodified app encounter, selected with SABLE_CAPTURE_MISSION.
## It drives the regular input route and streams native 1920x1080 RGBA frames.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const SIZE := Vector2i(1920, 1080)
const FPS := 60
const FRAME_COUNT := 600
const ALLOWED_MISSIONS := ["MIS_CH01_01", "MIS_CH01_02", "MIS_CH01_03", "MIS_CH01_04", "MIS_CH01_05", "MIS_CH01_06", "MIS_CH01_07", "MIS_CH01_08", "MIS_CH01_09", "MIS_CH01_10"]

var held_keys: Array[int] = []
var fire_held := false
var shots := 0
var movie_capture := false
var boss_capture := false

func _init() -> void:
    call_deferred("run")

func _key(code: int, pressed: bool) -> void:
    var event := InputEventKey.new()
    event.keycode = code
    event.physical_keycode = code
    event.pressed = pressed
    Input.parse_input_event(event)

func _set_keys(codes: Array[int]) -> void:
    for code in held_keys:
        if not codes.has(code): _key(code, false)
    for code in codes:
        if not held_keys.has(code): _key(code, true)
    held_keys = codes

func _set_fire(pressed: bool) -> void:
    if fire_held == pressed: return
    var event := InputEventMouseButton.new()
    event.button_index = MOUSE_BUTTON_LEFT
    event.pressed = pressed
    event.position = root.get_mouse_position()
    Input.parse_input_event(event)
    fire_held = pressed

func _aim_at_enemy(stage: StoryStage01) -> void:
    var actor := stage.squad.get_active_operator()
    var target := actor.global_position + Vector2(350, -50)
    var nearest := INF
    for enemy in get_nodes_in_group("prototype_targets"):
        if enemy is Node2D and not enemy.is_queued_for_deletion():
            if boss_capture and enemy is EnemyActor and enemy.enemy_id.begins_with("BOSS_"):
                target = enemy.get_combat_aim_point()
                break
            var distance: float = actor.global_position.distance_squared_to(enemy.global_position)
            if distance < nearest:
                nearest = distance
                target = enemy.call("get_combat_aim_point") if enemy.has_method("get_combat_aim_point") else enemy.global_position
    var screen_point := root.get_final_transform() * (stage.get_canvas_transform() * target)
    Input.warp_mouse(screen_point)
    var event := InputEventMouseMotion.new()
    event.position = screen_point
    event.global_position = screen_point
    Input.parse_input_event(event)

func _record_shot(_projectile: Node2D) -> void:
    shots += 1

func _visible_enemy_ids() -> Array[String]:
    var ids: Array[String] = []
    for enemy in get_nodes_in_group("prototype_targets"):
        if enemy.is_queued_for_deletion(): continue
        var enemy_id := str(enemy.get("enemy_id"))
        if not enemy_id.is_empty() and not ids.has(enemy_id): ids.append(enemy_id)
    ids.sort()
    return ids

func _send_frame(peer: StreamPeerTCP) -> void:
    await RenderingServer.frame_post_draw
    var picture := root.get_texture().get_image()
    assert(picture.get_size() == SIZE)
    picture.convert(Image.FORMAT_RGBA8)
    var pixels := picture.get_data()
    peer.put_u32(pixels.size())
    assert(peer.put_data(pixels) == OK)

func run() -> void:
    var output := OS.get_environment("SABLE_CAPTURE_OUTPUT")
    var mission_id := OS.get_environment("SABLE_CAPTURE_MISSION")
    assert(not output.is_empty())
    assert(mission_id in ALLOWED_MISSIONS)
    movie_capture=OS.get_environment("SABLE_CAPTURE_MOVIE")=="1"
    boss_capture=OS.get_environment("SABLE_CAPTURE_BOSS")=="1"
    root.size = SIZE
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(SIZE)
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    Engine.physics_ticks_per_second = FPS
    Input.use_accumulated_input = false
    var peer := StreamPeerTCP.new()
    peer.big_endian = true
    assert(peer.connect_to_host("127.0.0.1", int(OS.get_environment("SABLE_CAPTURE_PORT"))) == OK)
    while peer.get_status() == StreamPeerTCP.STATUS_CONNECTING:
        peer.poll()
        await process_frame
    assert(peer.get_status() == StreamPeerTCP.STATUS_CONNECTED)
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    current_scene = stage
    for i in range(8): await process_frame
    # Boss review starts in the authored boss room; the regular capture keeps
    # its original mixed-encounter default.
    var capture_step := 4 if boss_capture else 1
    stage.start_battle_preview(capture_step)
    if OS.get_environment("SABLE_CAPTURE_FULL_WAVES") == "1":
        # Density evidence: attach the room's authored reinforcement waves as
        # a campaign deployment does (the preview omits them by default).
        var room: Dictionary = stage.main_route[stage.current_step]
        stage._encounter_waves.append_array(room.get("reinforcements", []))
        stage._reinforce_at = int(room.get("reinforce_at", 0))
    for actor in stage.squad.operators:
        actor.projectile_spawned.connect(_record_shot)
    var observations: Array[Dictionary] = []
    var next_encounter_frame := -120
    var seen_enemy_ids: Array[String] = []
    var capture_start_render_frame := Engine.get_frames_drawn()
    var sfx: Node=preload("res://scripts/audio/combat_sfx_bank.gd").manager(self)
    sfx.debug_trace=true
    var enemy_observations: Array[Dictionary]=[]
    for frame in range(FRAME_COUNT):
        var keys: Array[int] = []
        if frame < 90: keys = [KEY_D]
        elif frame < 150: keys = [KEY_S]
        elif frame < 210: keys = [KEY_A]
        elif frame == 210: keys = [KEY_R]
        elif frame >= 300 and frame < 390: keys = [KEY_D]
        elif frame >= 390 and frame < 450: keys = [KEY_W, KEY_SHIFT]
        if stage._preview_cleared and frame - next_encounter_frame > 60:
            keys.append(KEY_F)
            next_encounter_frame = frame
        _set_keys(keys)
        _aim_at_enemy(stage)
        _set_fire(frame < 210 or frame >= 300)
        await process_frame
        var visible := _visible_enemy_ids()
        for enemy_id in visible:
            if not seen_enemy_ids.has(enemy_id): seen_enemy_ids.append(enemy_id)
        await _send_frame(peer)
        if frame in [30, 300, 540]:
            root.get_texture().get_image().save_png(output.path_join("frame_%04d.png" % frame))
        if frame % FPS == 0 or frame == FRAME_COUNT - 1:
            var actor := stage.squad.get_active_operator()
            observations.append({"frame": frame, "encounter_step": stage.current_step, "position": [actor.position.x, actor.position.y], "ammo": actor.ammo, "health": actor.health, "hostiles": stage.enemies_alive, "visible_enemy_ids": visible, "squad_projectiles": shots})
            for enemy in get_nodes_in_group("m3_enemies"):
                if enemy is EnemyActor and not enemy.is_queued_for_deletion():
                    enemy_observations.append({"frame":frame,"instance":enemy.get_instance_id(),"enemy":enemy.enemy_id,"position":[enemy.global_position.x,enemy.global_position.y],"state":enemy.tactics.state,"shots":enemy.tactics.shots_fired,"lunges":enemy.tactics.lunges})
        if frame % 120 == 0: print("STAGE_CAPTURE_FRAME ", mission_id, " ", frame, "/", FRAME_COUNT)
    _set_keys([])
    _set_fire(false)
    peer.put_u32(0)
    var report := {"native_resolution": [1920,1080], "render_content_scale": [1280,720], "frames": FRAME_COUNT, "fps": FPS, "duration_seconds": 10,
        "scene": "res://scenes/mission/StoryStage01.tscn", "mission": mission_id, "initial_encounter_step": capture_step,
        "clock": "Godot --fixed-fps 60; native rendered viewport readback, not a wall-clock performance measurement",
        "normal_ai_and_damage": true, "input": "WASD / Shift / mouse aim / LMB / reload / F next encounter via Input.parse_input_event",
        "app_registry_unchanged": true, "audio": movie_capture, "capture_start_render_frame":capture_start_render_frame,
        "capture_end_render_frame":Engine.get_frames_drawn(),"audio_events":sfx.debug_snapshot(),"enemy_observations":enemy_observations,
        "art_approval": false, "seen_enemy_ids": seen_enemy_ids, "observations": observations}
    var file := FileAccess.open(output.path_join("capture.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("STAGE_BATTLE_VIDEO_CAPTURE_COMPLETE mission=", mission_id, " shots=", shots, " seen=", seen_enemy_ids)
    quit()
