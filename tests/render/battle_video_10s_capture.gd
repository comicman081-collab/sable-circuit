extends SceneTree

## Capture-only: normal app scene, app assets, AI and damage; physical input path.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const SIZE := Vector2i(1920, 1080)
const FPS := 60
const FRAME_COUNT := 600
var shots := 0
var held_keys: Array[int] = []
var fire_held := false

func _init() -> void:
    call_deferred("run")

func key(code: int, pressed: bool) -> void:
    var event := InputEventKey.new()
    event.keycode = code
    event.physical_keycode = code
    event.pressed = pressed
    Input.parse_input_event(event)

func set_keys(codes: Array[int]) -> void:
    for code in held_keys:
        if not codes.has(code): key(code, false)
    for code in codes:
        if not held_keys.has(code): key(code, true)
    held_keys = codes

func set_fire(pressed: bool) -> void:
    if fire_held == pressed: return
    var event := InputEventMouseButton.new()
    event.button_index = MOUSE_BUTTON_LEFT
    event.pressed = pressed
    event.position = root.get_mouse_position()
    Input.parse_input_event(event)
    fire_held = pressed

func aim_at_enemy(stage: StoryStage01) -> void:
    var actor := stage.squad.get_active_operator()
    var target := actor.global_position + Vector2(350, -50)
    var nearest := INF
    for enemy in get_nodes_in_group("prototype_targets"):
        if enemy is Node2D and not enemy.is_queued_for_deletion():
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

func record_shot(_projectile: Node2D) -> void:
    shots += 1

func run() -> void:
    var output := OS.get_environment("SABLE_CAPTURE_OUTPUT")
    assert(not output.is_empty())
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
    stage.mission_id = "MIS_CH01_01"
    stage.battle_preview = true
    root.add_child(stage)
    current_scene = stage
    for i in range(8): await process_frame
    stage.start_battle_preview(1)
    for actor in stage.squad.operators:
        actor.projectile_spawned.connect(record_shot)
    var observations: Array[Dictionary] = []
    var next_encounter_frame := -120
    for frame in range(FRAME_COUNT):
        var keys: Array[int] = []
        if frame < 90: keys = [KEY_D]
        elif frame < 150: keys = [KEY_S]
        elif frame < 210: keys = [KEY_A]
        elif frame == 210: keys = [KEY_R]
        elif frame >= 300 and frame < 390: keys = [KEY_D]
        elif frame >= 390 and frame < 450: keys = [KEY_W, KEY_SHIFT]
        # Use the app's ordinary Next Encounter control after a cleared room.
        # Do not prolong a fight by changing enemy health or disabling squad AI.
        if stage._preview_cleared and frame - next_encounter_frame > 60:
            keys.append(KEY_F)
            next_encounter_frame = frame
        set_keys(keys)
        aim_at_enemy(stage)
        set_fire(frame < 210 or frame >= 300)
        await process_frame
        await RenderingServer.frame_post_draw
        var picture := root.get_texture().get_image()
        assert(picture.get_size() == SIZE)
        picture.convert(Image.FORMAT_RGBA8)
        var pixels := picture.get_data()
        peer.put_u32(pixels.size())
        assert(peer.put_data(pixels) == OK)
        if frame in [30, 240, 540]:
            picture.save_png(output.path_join("frame_%04d.png" % frame))
        if frame % FPS == 0 or frame == FRAME_COUNT - 1:
            var actor := stage.squad.get_active_operator()
            observations.append({"frame": frame, "encounter_step": stage.current_step, "position": [actor.position.x, actor.position.y], "ammo": actor.ammo, "health": actor.health, "hostiles": stage.enemies_alive, "squad_projectiles": shots})
        if frame % 120 == 0: print("CAPTURE_FRAME ", frame, "/", FRAME_COUNT)
    set_keys([])
    set_fire(false)
    peer.put_u32(0)
    var report := {"native_resolution": [1920, 1080], "render_content_scale": [1280, 720], "frames": FRAME_COUNT, "fps": FPS, "duration_seconds": 10, "scene": "res://scenes/mission/StoryStage01.tscn", "mission": stage.mission_id, "initial_encounter_step": 1, "clock": "Godot --fixed-fps 60; native rendered viewport readback, not performance footage", "normal_ai_and_damage": true, "input": "WASD / Shift / mouse aim / LMB / reload / F next encounter via Input.parse_input_event", "app_registry_unchanged": true, "art_approval": false, "observations": observations}
    var file := FileAccess.open(output.path_join("capture.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("BATTLE_VIDEO_CAPTURE_COMPLETE shots=", shots)
    quit()
