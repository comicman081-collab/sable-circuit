extends SceneTree
## Native 1920x1080 frames of the volumetric impact and hurt VFX in an operation room:
## 01 live hits on the room's robots and one operator, 02 every impact profile and
## hurt reaction side by side at the same age. Run windowed (not --headless):
##   Godot --path . -s res://tests/render/combat_hit_hurt_vfx_capture.gd -- --out=res://<folder>

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")
const FREEZE_AGE := 0.085
const IMPACTS := [["HIT_ASTER_PRISM_01", "69d2ff"], ["HIT_ROOK_CRUSH_01", "ffb45c"], ["HIT_MICA_SCANBURST_01", "62d8c8"],
    ["HIT_ENM_DRONE_ARC_01", "65e1e8"], ["HIT_BOSS_ANCHOR_RIFT_01", "9179ff"], ["HIT_GENERIC", "f0f5f7"]]
const REACTIONS := ["FLINCH", "LIGHT", "HEAVY", "DOWNED"]

var out_dir := TestOutput.path("res://.cache/tests/hit_hurt_vfx_capture")
var failed := false
var stage: StoryStage01

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))
    stage = STAGE.instantiate() as StoryStage01
    stage.battle_preview = true
    root.add_child(stage)
    await _settle(6)
    stage.start_battle_preview(1)
    await _settle(20)

    var enemies := get_nodes_in_group("m3_enemies")
    _check(enemies.size() >= 2, "combat room has robots to hit")
    var shooter := stage.squad.get_active_operator()
    for enemy_node in enemies.slice(0, 3):
        var enemy := enemy_node as EnemyActor
        var centre := enemy.get_combat_hit_rect().get_center()
        CombatFeedback.spawn_hit(self, centre, shooter.art_profile, shooter.accent_color.lightened(0.35), null, (centre - shooter.global_position).normalized())
        enemy.apply_damage(enemy.max_health * 0.2)
    var hurt_operator := stage.squad.operators[1]
    hurt_operator.apply_damage(hurt_operator.max_health * 0.2)
    await _freeze_and_capture("01_room_hits_and_hurt.png")

    paused = false
    _clear_vfx()
    # Lay the matrix out in screen space (1280x720 content) so it reads at any camera zoom.
    var to_world := stage.get_canvas_transform().affine_inverse()
    for index in range(IMPACTS.size()):
        var row: Array = IMPACTS[index]
        var at := to_world * Vector2(330 + index * 150, 250)
        CombatFeedback.spawn_hit(self, at, {"hit_vfx_profile": row[0]}, Color(str(row[1])), null, Vector2.RIGHT)
    for index in range(REACTIONS.size()):
        CombatFeedback.spawn_hurt(self, to_world * Vector2(330 + index * 150, 470), "ENEMY", "ENM_SITE7_BULWARK_01", REACTIONS[index], Color("e2a94e"))
    CombatFeedback.spawn_hurt(self, to_world * Vector2(930, 470), "OPERATOR", "CHR_PROTO_02", "HEAVY", Color("ffb45c"))
    CombatFeedback.spawn_hurt(self, to_world * Vector2(1080, 470), "BOSS", "BOSS_SITE7_ANCHOR_01", "HEAVY", Color("9179ff"))
    await _freeze_and_capture("02_profile_and_reaction_matrix.png")

    if failed:
        quit(1)
    else:
        print("COMBAT_HIT_HURT_VFX_CAPTURE: PASS ", ProjectSettings.globalize_path(out_dir))
        quit(0)

func _freeze_and_capture(file_name: String) -> void:
    # Hold every effect at the same early age so the frame shows its readable peak.
    for node in root.get_children():
        if node is CombatHitVFX:
            var vfx := node as CombatHitVFX
            vfx.age = FREEZE_AGE
            vfx.call("_sync_visual_layers", FREEZE_AGE / vfx.lifetime)
            vfx.queue_redraw()
    paused = true
    await process_frame
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    _check(image.get_size() == Vector2i(1920, 1080), file_name + " is native 1920x1080, got " + str(image.get_size()))
    _check(image.save_png(ProjectSettings.globalize_path(out_dir.path_join(file_name))) == OK, file_name + " saved")

func _clear_vfx() -> void:
    for node in root.get_children():
        if node is CombatHitVFX: node.free()

func _settle(frames: int) -> void:
    for i in range(frames):
        await physics_frame
        await process_frame

func _check(condition: bool, message: String) -> void:
    if not condition:
        failed = true
        push_error(message)
