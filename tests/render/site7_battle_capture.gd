extends SceneTree

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var OUT := ""
var failed := false
var reports: Array[Dictionary] = []

func _init() -> void:
    call_deferred("run")

func check(condition: bool, message: String) -> void:
    if not condition:
        failed = true
        push_error(message)

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

func run() -> void:
    OUT = preload("res://tests/support/test_output.gd").path("res://.cache/diag/site7_battle_capture")
    var only_mission := 0
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): only_mission = int(arg.get_slice("=", 1))
    root.size = Vector2i(1920,1080)
    root.content_scale_size = Vector2i(1280,720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
    for number in range(1,11):
        if only_mission != 0 and number != only_mission: continue
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        stage.battle_preview = true
        root.add_child(stage)
        await settle(6)
        for step in [1,3,4]:
            stage.start_battle_preview(step)
            await settle(2)
            var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
            check(art.debug_all_assets_loaded(), "Incomplete production background set S%d" % number)
            check(stage.squad.operators.size() == 3, "Missing squad slot")
            check(stage.hud.debug_uses_unique_portraits(), "Missing real portrait")
            check(stage.enemies_alive > 0, "Missing live enemy encounter S%d" % number)
            var player := stage.squad.get_active_operator()
            var runtime := player.get_node("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
            check(runtime.is_runtime_active(), "ASTER shared runtime inactive")
            check(is_equal_approx(float(runtime.debug_contract().get("display_height_px", 0.0)), 129.6), "Requested 1.8x character scale not applied")
            check((stage.squad.operators[2].get_node("MotionLabCharacterRuntime") as MotionLabCharacterRuntime).is_runtime_active(), "MICA shared runtime inactive")
            var origin := player.position
            key(KEY_D, true)
            key(KEY_S, true)
            await settle(8)
            key(KEY_D, false)
            key(KEY_S, false)
            var displacement := player.position - origin
            check(displacement.x > 1.0 and displacement.y > 1.0, "Live diagonal input failed")
            # Native input dispatch, not debug_drive: use the same actor/fire path.
            # Input.parse_input_event uses native window pixels; canvas_items
            # applies the 1080p-to-720p stretch on dispatch, just as real input.
            var target_world := player.global_position + Vector2(260,-70)
            var screen_point := root.get_final_transform() * (stage.get_canvas_transform() * target_world)
            Input.warp_mouse(screen_point)
            var mouse := InputEventMouseMotion.new()
            mouse.position = screen_point
            mouse.global_position = screen_point
            Input.parse_input_event(mouse)
            var before := player.ammo
            var press := InputEventMouseButton.new()
            press.button_index = MOUSE_BUTTON_LEFT
            press.position = screen_point
            press.pressed = true
            Input.parse_input_event(press)
            await settle(7)
            var shots := before - player.ammo
            check(shots > 0, "Live firing did not consume ammunition")
            press = InputEventMouseButton.new()
            press.button_index = MOUSE_BUTTON_LEFT
            press.pressed = false
            Input.parse_input_event(press)
            if DisplayServer.get_name() != "headless":
                await RenderingServer.frame_post_draw
                var image := root.get_texture().get_image()
                check(image.get_size() == Vector2i(1920,1080), "Not native 1080p")
                check(image.save_png(ProjectSettings.globalize_path(OUT + ("/stage_%02d%s_1920x1080.png" % [number, "" if step == 1 else ("_elite" if step == 3 else "_boss")]))) == OK, "Capture write failed")
            var streaming := art.debug_streaming_state()
            check(streaming.visible_ids.size() == 15, "Continuous mission lost an authored plate")
            reports.append({"mission":stage.mission_id,"encounter_step":step,"floor":stage.battlefield.call("debug_contract"),"art":art.debug_local_plate_contract(),"streaming":streaming,"diagonal_delta":[displacement.x,displacement.y],"live_shots":shots,"aster_runtime":runtime.debug_contract(),"native_capture":DisplayServer.get_name() != "headless"})
        stage.queue_free()
        # Projectiles live outside the stage; dispose owned test projectiles too.
        for node in root.get_children():
            if node.get_script() == preload("res://scripts/combat/prototype_projectile.gd"):
                node.queue_free()
        await settle(3)
    var file := FileAccess.open(OUT + "/" + ("capture" if DisplayServer.get_name() != "headless" else "smoke") + "_report.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"FAIL" if failed else "PASS_TECHNICAL_ONLY","native_resolution":[1920,1080],"stages":reports},"  "))
    file.close()
    print("SITE7_BATTLE_DESIGN: " + ("FAIL" if failed else "PASS"))
    quit(1 if failed else 0)
