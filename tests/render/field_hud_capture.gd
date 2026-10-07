extends SceneTree
## Native 1920x1080 captures of the mockup-style field HUD in a real campaign
## deployment (entry corridor and first live encounter). Review evidence only.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var out := "res://qa/field_hud_20260924"
var failures: Array[String] = []
var shots: Array[String] = []

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    if not ok: failures.append(label); push_error(label)

func shot(name: String) -> void:
    if DisplayServer.get_name() == "headless": return
    await RenderingServer.frame_post_draw
    var img := root.get_texture().get_image()
    check(img.get_size() == Vector2i(1920, 1080), "Native capture size " + name)
    img.save_png(out + "/" + name + ".png")
    shots.append(name + ".png")

func run() -> void:
    var mission := "MIS_CH01_01"
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--mission="): mission = a.get_slice("=", 1)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    stage.configure_campaign({}, mission + "-HUD-CAPTURE", {})
    for i in range(40): await physics_frame
    for enemy in get_nodes_in_group("m3_enemies"):
        if enemy is EnemyActor: enemy.set_physics_process(false)
    var hud := stage.hud
    check(hud.debug_hud_art_loaded(), "Weapon and skill art bound")
    check(hud.debug_uses_unique_portraits(), "Three distinct squad portraits")
    check((hud.debug_skill_hud_contract().keys as Array) == ["Q", "E", "X"], "Q/E/X skill keys kept")
    hud.set_cargo_status(1250, 0, 115, 0)
    await create_timer(0.8).timeout
    await shot("%s_entry" % mission.right(2))
    # Walk the squad a little way in, then show the live encounter.
    var actor := stage.squad.get_active_operator()
    var target: Vector2 = stage.constrain_battle_position(Vector2(float(stage.main_route[1].x) - 900.0, float(stage.main_route[1].y)))
    actor.global_position = target
    for member in stage.squad.operators:
        if member != actor: member.global_position = stage.constrain_battle_position(target + Vector2(-90, 60))
    for enemy in get_nodes_in_group("m3_enemies"):
        if enemy is EnemyActor: enemy.set_physics_process(true)
    for i in range(90): await physics_frame
    await shot("%s_encounter" % mission.right(2))
    hud._minimap.zoom_by(1)
    await create_timer(0.6).timeout
    await shot("%s_minimap_zoom" % mission.right(2))
    hud._minimap.zoom_by(-1)
    # Boss framing uses the wider boss zoom-out.
    stage.battle_preview = true
    stage.start_battle_preview(4)
    for i in range(150): await physics_frame
    await shot("%s_boss" % mission.right(2))
    var file := FileAccess.open(out + "/capture_%s.json" % mission.right(2), FileAccess.WRITE)
    file.store_string(JSON.stringify({"failures": failures, "captures": shots, "resolution": [1920, 1080], "human_playtest": false}, "  "))
    file.close()
    print("FIELD_HUD_CAPTURE %s %s" % ["PASS" if failures.is_empty() else "FAIL", failures])
    quit(0 if failures.is_empty() else 1)
