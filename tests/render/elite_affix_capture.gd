extends SceneTree
## Native 1920x1080 frames of the elite variants in their mission rooms: 01 operation 3
## elite room with a half-spent SHIELDED barrier and a VOLATILE drone, 02 the same room
## during the VOLATILE warning circle, 03 operation 5 elite room with SHIELDED and
## OVERCHARGED. The VOLATILE drone and the OVERCHARGED ram are moved beside the squad so
## the HUD does not cover them. Run windowed (not --headless):
##   Godot --path . -s res://tests/render/elite_affix_capture.gd -- --out=res://<folder>

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")

var out_dir := TestOutput.path("res://.cache/tests/elite_affix_capture")
var failed := false
var report := {}
# Robots kept at full health while the room settles, so companion fire cannot remove the subject.
var keep: Array[EnemyActor] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))

    var stage := await _open("MIS_CH01_03")
    var shielded := _with_affix("SHIELDED")
    var volatile := _with_affix("VOLATILE")
    _check(shielded != null and volatile != null, "operation 3 elite room has SHIELDED and VOLATILE robots")
    if shielded != null:
        var affix := shielded.get_node("EliteAffix") as EliteAffix
        affix.barrier = affix.barrier_max
        shielded.apply_damage(affix.barrier_max * 0.5)
    await _capture(stage, "01_op3_shielded_and_volatile.png")
    paused = false
    if volatile != null:
        # Staged into open floor beside the squad so the warning circle is not under the HUD.
        volatile.global_position = stage.squad.get_active_operator().global_position + Vector2(240, 80)
        keep.erase(volatile)
        volatile.apply_damage(99999.0)
        await _settle(30)
    await _capture(stage, "02_op3_volatile_warning.png")
    paused = false
    stage.queue_free()
    await _settle(4)

    stage = await _open("MIS_CH01_05")
    var overcharged := _with_affix("OVERCHARGED")
    _check(_with_affix("SHIELDED") != null and overcharged != null, "operation 5 elite room has SHIELDED and OVERCHARGED robots")
    if overcharged != null:
        # Staged beside the squad; it otherwise idles under the top-right HUD.
        overcharged.global_position = stage.squad.get_active_operator().global_position + Vector2(280, -30)
        await _settle(2)
    await _capture(stage, "03_op5_shielded_and_overcharged.png")

    var file := FileAccess.open(out_dir.path_join("elite_affix_layout.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    if failed:
        quit(1)
    else:
        print("ELITE_AFFIX_CAPTURE: PASS ", ProjectSettings.globalize_path(out_dir))
        quit(0)

func _open(mission: String) -> StoryStage01:
    var stage := STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    stage.mission_id = mission
    root.add_child(stage)
    await _settle(6)
    stage.start_battle_preview(3)
    keep.clear()
    for node in get_nodes_in_group("m3_enemies"):
        if (node as Node).get_node_or_null("EliteAffix") != null: keep.append(node as EnemyActor)
    await _settle(45)
    return stage

func _with_affix(id: String) -> EnemyActor:
    for node in get_nodes_in_group("m3_enemies"):
        var affix := (node as Node).get_node_or_null("EliteAffix") as EliteAffix
        if affix != null and affix.affix_id == id and (node as EnemyActor).health > 0.0: return node as EnemyActor
    return null

func _capture(stage: StoryStage01, file_name: String) -> void:
    paused = true
    await process_frame
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    _check(image.get_size() == Vector2i(1920, 1080), file_name + " is native 1920x1080, got " + str(image.get_size()))
    _check(image.save_png(ProjectSettings.globalize_path(out_dir.path_join(file_name))) == OK, file_name + " saved")
    # Where each variant sits on screen (1080p pixels), so the frame can be checked for it.
    var rows := []
    var to_screen := stage.get_canvas_transform()
    for node in get_nodes_in_group("m3_enemies"):
        var affix := (node as Node).get_node_or_null("EliteAffix") as EliteAffix
        if affix == null or (node as EnemyActor).health <= 0.0: continue
        var at: Vector2 = to_screen * (node as EnemyActor).global_position * 1.5
        rows.append({"affix": affix.affix_id, "enemy_id": (node as EnemyActor).enemy_id, "screen": [roundi(at.x), roundi(at.y)],
            "barrier_share": snappedf(affix.barrier_share(), 0.01), "on_screen": Rect2(0, 0, 1920, 1080).has_point(at)})
    report[file_name] = rows

func _settle(frames: int) -> void:
    for i in range(frames):
        await physics_frame
        await process_frame
        for enemy in keep:
            if is_instance_valid(enemy) and enemy.health > 0.0: enemy.health = enemy.max_health

func _check(condition: bool, message: String) -> void:
    if not condition:
        failed = true
        push_error(message)
