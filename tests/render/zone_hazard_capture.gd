extends SceneTree
## Native 1920x1080 frames of the ARC VENT room hazard in operation 4's elite room:
## 01 idle grates, 02 mid-telegraph, 03 the discharge with an operator and a robot on
## the vent. Run windowed (not --headless):
##   Godot --path . -s res://tests/render/zone_hazard_capture.gd -- --out=res://<folder>

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")

var out_dir := TestOutput.path("res://.cache/tests/zone_hazard_capture")
var failed := false
var report := {}

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    stage.mission_id = "MIS_CH01_04"
    root.add_child(stage)
    await _settle(6)
    stage.start_battle_preview(3)
    await _settle(8)
    var vents := get_nodes_in_group("zone_hazards")
    _check(vents.size() >= 1, "operation 4 elite room has vents")
    if vents.is_empty():
        quit(1)
        return
    var vent := vents[0] as ZoneHazard
    # Hold every vent idle while the room settles; the frames step one vent through its cycle.
    for node in vents: (node as ZoneHazard).phase_left = 60.0
    await _settle(20)
    await _capture(stage, vents, "01_arc_vents_idle.png")
    paused = false
    vent._physics_process(vent.phase_left + 0.01)
    vent._physics_process(float(vent.spec.telegraph) * 0.6)
    await _capture(stage, vents, "02_arc_vent_telegraph.png")
    paused = false
    # Staged: the controlled operator and one robot stand on the vent for the discharge.
    stage.squad.get_active_operator().global_position = vent.global_position + Vector2(-22, 6)
    for node in get_nodes_in_group("m3_enemies"):
        var enemy := node as EnemyActor
        if enemy.get_node_or_null("EliteAffix") == null:
            enemy.global_position = vent.global_position + Vector2(30, -4)
            break
    vent._physics_process(float(vent.spec.telegraph) * 0.4 + 0.01)
    report["discharge_hits"] = vent.last_hits.duplicate()
    _check(vent.phase == ZoneHazard.Phase.DISCHARGE and vent.last_hits.size() >= 1, "the staged discharge hits someone")
    # Let the burst render a few frames without the vent moving on.
    vent.phase_left = 10.0
    for i in range(3):
        await process_frame
    vent.phase_left = float(vent.spec.discharge) * 0.6
    await _capture(stage, vents, "03_arc_vent_discharge.png")

    var file := FileAccess.open(out_dir.path_join("zone_hazard_layout.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    if failed:
        quit(1)
    else:
        print("ZONE_HAZARD_CAPTURE: PASS ", ProjectSettings.globalize_path(out_dir))
        quit(0)

func _capture(stage: StoryStage01, vents: Array, file_name: String) -> void:
    paused = true
    for node in vents: (node as ZoneHazard).queue_redraw()
    await process_frame
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    _check(image.get_size() == Vector2i(1920, 1080), file_name + " is native 1920x1080, got " + str(image.get_size()))
    _check(image.save_png(ProjectSettings.globalize_path(out_dir.path_join(file_name))) == OK, file_name + " saved")
    var rows := []
    var to_screen := stage.get_canvas_transform()
    for node in vents:
        var vent := node as ZoneHazard
        var at: Vector2 = to_screen * vent.global_position * 1.5
        rows.append({"phase": ZoneHazard.Phase.keys()[vent.phase], "screen": [roundi(at.x), roundi(at.y)], "on_screen": Rect2(0, 0, 1920, 1080).has_point(at)})
    report[file_name] = rows

func _settle(frames: int) -> void:
    for i in range(frames):
        await physics_frame
        await process_frame

func _check(condition: bool, message: String) -> void:
    if not condition:
        failed = true
        push_error(message)
