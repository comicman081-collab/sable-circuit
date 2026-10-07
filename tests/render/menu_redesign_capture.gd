extends SceneTree
## Native 1920x1080 review captures of the redesigned menu flow plus a few
## structural checks. Captures are presentation evidence only, not a human
## playtest or art approval. Run windowed (not --headless) to write PNGs.
const FLOW := preload("res://scenes/bootstrap/GameFlow.tscn")
var out := "res://qa/menu_redesign_20260924"
var failures: Array[String] = []
var checks := 0
var shots: Array[String] = []

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)

func wait(seconds: float) -> void:
    await create_timer(seconds).timeout

func shot(name: String) -> void:
    if DisplayServer.get_name() == "headless": return
    await RenderingServer.frame_post_draw
    var img := root.get_texture().get_image()
    check(img.get_size() == Vector2i(1920, 1080), "Native capture size " + name)
    img.save_png(out + "/" + name + ".png")
    shots.append(name + ".png")

func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    var flow := FLOW.instantiate() as GameFlow
    flow.persist_campaign = false
    root.add_child(flow)
    await wait(2.8)
    var title := flow.current_view as TitleScreen
    check(title != null, "Title is the boot view")
    check(title.find_child("StartDemo", true, false) != null, "Start entry keeps its StartDemo node name")
    check(title.lineup.debug_member_count() == 3, "Title lineup shows all three current operators")
    await shot("01_title")
    (title.find_child("TrainingSimulator", true, false) as Button).pressed.emit()
    await wait(0.6)
    check(title.training_panel.visible, "Training simulator panel opens")
    await shot("02_title_training")
    flow.campaign.research_value = 640; flow.campaign.salvage = 6; flow.campaign.signal_fragments = 3
    flow.enter_base()
    await wait(1.6)
    check(flow.current_view is BaseLobby, "Operations base opens")
    await shot("03_operations_base")
    flow.open_mission_briefing("MIS_CH01_01")
    await wait(1.8)
    await shot("04_briefing_comms")
    var briefing := flow.current_view as BriefingScreen
    briefing.debug_complete_briefing()
    await wait(1.4)
    check(briefing.find_child("DeployButton", true, false).visible, "Deploy appears after comms")
    await shot("05_briefing_deploy")
    flow.debug_show_results()
    await wait(1.8)
    check(flow.current_view is MissionResults, "Debrief opens")
    await shot("06_debrief")
    flow.open_battle_preview(2)
    await wait(2.0)
    var controls: CanvasLayer = (flow.current_view as StoryStage01).get_node("DemoControls")
    controls._toggle_help()
    await wait(0.4)
    await shot("07_pause_manual")
    controls._toggle_help()
    var report := {"checks": checks, "failures": failures, "captures": shots, "resolution": [1920, 1080],
        "viewport": [1280, 720], "stretch": "canvas_items", "human_playtest": false, "art_approval": false}
    var file := FileAccess.open(out + "/capture_report.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  ")); file.close()
    flow.queue_free()
    await wait(0.2)
    print("MENU_REDESIGN_CAPTURE %s / %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
    quit(0 if failures.is_empty() else 1)
