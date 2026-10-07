extends SceneTree

## Native app evidence. Uses the real StoryStage squad and real Godot input;
## no debug-drive sprites, substituted portrait, or separate HTML controller.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const LOBBY := preload("res://scenes/base/BaseLobby.tscn")
const OUT := "res://qa/rook_app_integration_20260913/final_capture"
var failures: Array[String] = []
var observations: Array[Dictionary] = []

func _init() -> void:
    call_deferred("run")

func check(condition: bool, label: String) -> void:
    if not condition:
        failures.append(label)
        push_error(label)

func settle(frames: int) -> void:
    for i in range(frames):
        await physics_frame
        await process_frame

func key(code: Key, pressed: bool) -> void:
    var event := InputEventKey.new()
    event.keycode = code
    event.physical_keycode = code
    event.pressed = pressed
    Input.parse_input_event(event)

func point_at(stage: StoryStage01, target: Vector2) -> void:
    var screen_point := root.get_final_transform() * (stage.get_canvas_transform() * target)
    Input.warp_mouse(screen_point)
    var event := InputEventMouseMotion.new()
    event.position = screen_point
    event.global_position = screen_point
    Input.parse_input_event(event)

func fire(pressed: bool) -> void:
    var event := InputEventMouseButton.new()
    event.button_index = MOUSE_BUTTON_LEFT
    event.pressed = pressed
    event.position = root.get_mouse_position()
    Input.parse_input_event(event)

func snapshot(name: String) -> void:
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    check(image.get_size() == Vector2i(1920,1080), "Native 1080p viewport")
    check(image.save_png(OUT + "/" + name + ".png") == OK, "Save " + name)

func run() -> void:
    root.size = Vector2i(1920,1080)
    root.content_scale_size = Vector2i(1280,720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
    for number in range(1,4):
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        stage.battle_preview = true
        root.add_child(stage)
        await settle(8)
        stage.start_battle_preview(1)
        await settle(5)
        key(KEY_2,true)
        await settle(2)
        key(KEY_2,false)
        var player := stage.squad.get_active_operator()
        check(player.operator_id == "CHR_PROTO_02", "Key 2 selects actual ROOK")
        var runtime := player.get_node("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
        check(runtime.is_runtime_active(), "Current ROOK is active in stage %d" % number)
        var initial := player.global_position
        var frames_seen: Dictionary = {}
        point_at(stage, player.global_position + Vector2(500,0))
        key(KEY_D,true)
        key(KEY_S,true)
        for i in range(28):
            await settle(1)
            frames_seen[runtime.debug_contract().frame] = true
        key(KEY_D,false)
        key(KEY_S,false)
        var diagonal := player.global_position - initial
        check(diagonal.x > 1 and diagonal.y > 1, "Real diagonal chord moves ROOK")
        check(frames_seen.size() > 1, "Displayed gait changes while moving")
        point_at(stage, player.global_position + Vector2(400,-100))
        var ammo_before := player.ammo
        fire(true)
        await settle(7)
        check(player.ammo < ammo_before, "Real held fire consumes ROOK ammunition")
        await snapshot("battle_stage_%02d_rook_1920x1080" % number)
        point_at(stage, player.global_position + Vector2(-450,-60))
        check(runtime.debug_contract().sector == player.facing_sector, "Rapid pointer event updates displayed direction immediately")
        await settle(27)
        fire(false)
        key(KEY_R,true)
        await settle(2)
        key(KEY_R,false)
        check(player.is_reloading(), "Real R starts reload")
        observations.append({"stage":number,"runtime":runtime.debug_contract(),"diagonal_delta":[diagonal.x,diagonal.y],"walk_frames":frames_seen.keys(),"ammo_before":ammo_before,"ammo_after":player.ammo,"reloading":player.is_reloading()})
        if number == 1:
            await settle(90)
            point_at(stage,player.global_position + Vector2(500,0))
            key(KEY_SHIFT,true)
            key(KEY_D,true)
            for sample in range(6):
                await settle(8)
                await snapshot("rook_run_%02d_1920x1080" % sample)
            key(KEY_D,false)
            key(KEY_SHIFT,false)
            await settle(2)
        stage.queue_free()
        for node in root.get_children():
            if node is PrototypeProjectile:
                node.queue_free()
        await settle(3)
    # Combat feedback is parented to SceneTree.root. Let its normal lifetime
    # finish before the lobby evidence; do not erase it from a screenshot.
    await settle(180)
    var lobby := LOBBY.instantiate()
    root.add_child(lobby)
    await settle(4)
    await snapshot("lobby_rook_portrait_1920x1080")
    lobby.queue_free()
    await settle(2)
    var report := FileAccess.open(OUT + "/capture_report.json",FileAccess.WRITE)
    report.store_string(JSON.stringify({"status":"PASS_INPUT_AND_CAPTURE_ONLY" if failures.is_empty() else "FAIL","native_resolution":[1920,1080],"input":"Input.parse_input_event and live regular Godot renderer; not physical keyboard testing","stages":observations,"failures":failures},"  "))
    report.close()
    print("ROOK_MOTION_LAB_APP_CAPTURE: " + ("PASS" if failures.is_empty() else "FAIL"))
    quit(0 if failures.is_empty() else 1)
