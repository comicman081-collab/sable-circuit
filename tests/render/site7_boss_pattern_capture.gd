extends SceneTree
## Controlled phase fixtures in each boss's actual room, rendered at native 1080p.
## All ten operations are open, so every boss stands in its own boss room. A boss whose operation had no
## room plates yet was staged in the boss-room shape it was designed for (the mission 3 boss hall): those
## frames are a TEST BED, not the operation's own room, and the report says so. TEST_BED is empty now; move a
## boss's row out of TEST_BED and its id into BOSS_IDS when its operation opens.
## Run windowed (not --headless) for the PNG frames; headless still runs every geometry check.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")
const BOSS_IDS := ["BOSS_SITE7_ANCHOR_01", "BOSS_SITE7_RELAY_01", "BOSS_SITE7_REMNANT_01", "BOSS_SITE7_FORGE_01", "BOSS_SITE7_CARRIER_01", "BOSS_SITE7_AERATOR_01", "BOSS_SITE7_CRYO_01", "BOSS_SITE7_GANTRY_01", "BOSS_SITE7_ARCHIVE_01", "BOSS_SITE7_ORIGIN_01"]
## From this index on, a boss gets both attacks (A, B) of every phase in its own room, like the test bed.
const FIRST_A_B_ROOM := 5
## boss id, the operation whose file holds its boss row (health), host mission and route step to stage it in
const TEST_BED := []
var out := ""
var failures: Array[String] = []
var rows: Array[Dictionary] = []
var native_capture := false

func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    if not ok: failures.append(label); push_error(label)
func settle(frames: int = 3) -> void:
    for _i in range(frames):
        await physics_frame
        await process_frame

func capture(label: String, boss: EnemyActor = null) -> void:
    if not native_capture:
        return
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    var path := out.path_join(label + ".png")
    check(image.get_size() == Vector2i(1920, 1080), "native 1080p " + label)
    check(image.save_png(ProjectSettings.globalize_path(path)) == OK, "save " + label)
    if boss != null:
        var emitter_screen: Vector2 = boss.machine_sprite.sprite.get_global_transform_with_canvas() * boss.machine_sprite.emitter_px
        check(Rect2(Vector2.ZERO, Vector2(1920, 1080)).has_point(emitter_screen), "emitter visible " + label)
        rows.append({"capture": path, "enemy_id": boss.enemy_id, "emitter_screen": emitter_screen,
            "texture_sha256": FileAccess.get_sha256(str(boss.art_profile.machine_asset.spec)),
            "machine": boss.machine_sprite.debug_contract()})

func _safe_floor_gap(stage: StoryStage01, victim: OperatorActor, warnings: Array[Node]) -> bool:
    var width := victim.get_combat_hit_rect().size.x * 1.5
    for radius in [100.0, 160.0, 220.0, 280.0, 300.0]:
        for i in range(72):
            var direction := Vector2.from_angle(float(i) * TAU / 72.0)
            var center: Vector2 = victim.global_position + direction * float(radius)
            var tangent: Vector2 = direction.orthogonal() * width * 0.5
            var points: Array[Vector2] = [center - tangent, center, center + tangent]
            if points.all(func(point: Vector2) -> bool: return stage.battlefield.is_walkable(point) and warnings.all(func(warning: Node) -> bool: return not warning.contains(point))):
                return true
    return false

func run() -> void:
    out = TestOutput.path("res://.cache/site7_boss_pattern_capture")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    native_capture = DisplayServer.get_name() != "headless"
    if native_capture:
        DisplayServer.window_set_size(Vector2i(1920, 1080))
    for index in range(BOSS_IDS.size()):
        await _own_room(index)
    for bed in TEST_BED:
        await _test_bed(bed)
    var file := FileAccess.open(out.path_join("capture_report.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": "PASS_TECHNICAL_ONLY" if failures.is_empty() else "FAIL", "failures": failures,
        "native_resolution": [1920, 1080] if native_capture else [], "controlled_phase_fixture": true,
        "test_bed_note": "Every operation is open: all ten bosses are captured in their own boss rooms and the test bed is empty.",
        "native_capture": native_capture, "visual_approval": false, "rows": rows}, "  "))
    file.close()
    print("SITE7_BOSS_PATTERN_CAPTURE: ", "PASS" if failures.is_empty() else "FAIL", " ", out)
    quit(0 if failures.is_empty() else 1)

## Operations 1-10: the boss in its own boss room, one warning frame per phase (attacks A and B of every
## phase for the bosses from FIRST_A_B_ROOM on).
func _own_room(index: int) -> void:
    var mission_id := "MIS_CH01_%02d" % (index + 1)
    var stage := await _stage(mission_id, 4)
    var boss := _boss_in(stage, BOSS_IDS[index])
    check(boss != null, mission_id + " boss spawned")
    if boss == null:
        stage.free()
        return
    var victim := _freeze(stage)
    stage.camera.global_position = boss.global_position + Vector2(-90.0, -95.0)
    stage.camera.position_smoothing_enabled = false
    stage.camera.force_update_scroll()
    await settle(3)
    await capture("mission%d_boss_room" % (index + 1), boss)
    if index >= FIRST_A_B_ROOM:
        var boss_id: String = BOSS_IDS[index]
        var name := boss_id.trim_prefix("BOSS_SITE7_").trim_suffix("_01").to_lower()
        await _phase_attacks(stage, boss, victim, boss_id, name, "mission%d" % (index + 1), mission_id, false)
        stage.free()
        await settle(3)
        return
    for phase in range(1, 4):
        boss.health = boss.max_health * [0.95, 0.50, 0.25][phase - 1]
        boss.tactics.phase = phase
        boss.tactics.attack_serial = 2 if (index == 0 and phase >= 2) or (index == 2 and phase == 2) else 1
        boss.tactics._shot_ordinal = 0
        var direction := (victim.global_position - boss.global_position).normalized()
        boss.tactics.locked_ground = direction
        boss.tactics.locked_aim = boss.aim_from_emitter(victim.get_combat_aim_point())
        boss.tactics._boss_attack(victim)
        var warnings := get_nodes_in_group("site7_attack_warnings")
        for warning in warnings:
            warning.set_physics_process(false)
            warning.elapsed = warning.windup * 0.52
            warning.queue_redraw()
        check(_safe_floor_gap(stage, victim, warnings), mission_id + " phase " + str(phase) + " safe floor gap")
        await settle(2)
        await capture("mission%d_phase%d_warning" % [index + 1, phase], boss)
        rows.append({"mission": mission_id, "phase": phase, "warnings": warnings.size(),
            "kinds": warnings.map(func(warning: Node) -> String: return warning.kind),
            "safe_floor_gap": _safe_floor_gap(stage, victim, warnings)})
        for warning in warnings: warning.free()
        for node in root.get_children():
            if node is PrototypeProjectile: node.free()
    stage.free()
    await settle(3)

## Test bed (empty while every operation is open): attacks A and B of every phase, in order on one boss
## (ARCHIVE recalls where the target stood), with the target walking a little between attacks so a recalled
## echo is visible.
func _test_bed(bed: Array) -> void:
    var enemy_id: String = bed[0]
    var name := enemy_id.trim_prefix("BOSS_SITE7_").trim_suffix("_01").to_lower()
    var boss_row := _boss_row(str(bed[1]))
    check(str(boss_row.get("enemy_id", "")) == enemy_id, enemy_id + " is the boss row of " + str(bed[1]))
    var stage := await _stage(str(bed[2]), int(bed[3]), boss_row)
    var boss := _boss_in(stage, enemy_id)
    check(boss != null, enemy_id + " spawned in the test bed")
    if boss == null:
        stage.free()
        return
    var victim := _freeze(stage)
    _frame(stage, boss, victim)
    await settle(3)
    await capture("testbed_%s_room" % name, boss)
    await _phase_attacks(stage, boss, victim, enemy_id, name, "testbed", str(bed[2]), true)
    stage.free()
    await settle(3)

## Attacks A and B of every phase, in order on one boss (ARCHIVE recalls where the target stood), with the
## target walking a little between attacks so a recalled echo is visible. `file_prefix` names the frames
## ("testbed" or "mission6"); `host` is the mission whose floor the boss stands on.
func _phase_attacks(stage: StoryStage01, boss: EnemyActor, victim: OperatorActor, enemy_id: String, name: String,
        file_prefix: String, host: String, test_bed: bool) -> void:
    for phase in range(1, 4):
        boss.health = boss.max_health * [0.95, 0.50, 0.25][phase - 1]
        boss.tactics.phase = phase
        for serial in range(1, 3):
            _step_target(stage, boss, victim)
            _frame(stage, boss, victim)
            boss.tactics.attack_serial = serial
            boss.tactics._shot_ordinal = 0
            boss.tactics.locked_ground = (victim.global_position - boss.global_position).normalized()
            boss.tactics.locked_aim = boss.aim_from_emitter(victim.get_combat_aim_point())
            boss.tactics._boss_attack(victim)
            var warnings := get_nodes_in_group("site7_attack_warnings")
            for warning in warnings:
                warning.set_physics_process(false)
                warning.elapsed = warning.windup * 0.52
                warning.queue_redraw()
            var attack := "a" if serial == 1 else "b"
            var label := "%s phase %d%s" % [enemy_id, phase, attack]
            var gap := _safe_floor_gap(stage, victim, warnings)
            var shots := root.get_children().filter(func(node: Node) -> bool: return node is PrototypeProjectile).size()
            check(gap, label + (" safe floor gap on the test-bed floor" if test_bed else " safe floor gap on its own floor"))
            check(warnings.size() <= 7 and warnings.size() + shots >= 1, label + " warns or fires, and warns at most seven times")
            await settle(2)
            await capture("%s_%s_p%d%s_warning" % [file_prefix, name, phase, attack] if test_bed else "%s_phase%d%s_warning" % [file_prefix, phase, attack], boss)
            rows.append({"test_bed": test_bed, "host_mission": host, "boss": enemy_id, "phase": phase, "attack": attack.to_upper(),
                "warnings": warnings.size(), "shots": shots, "kinds": warnings.map(func(warning: Node) -> String: return warning.kind),
                "boss_to_target_px": snappedf(boss.global_position.distance_to(victim.global_position), 0.1), "safe_floor_gap": gap})
            for warning in warnings: warning.free()
            for node in root.get_children():
                if node is PrototypeProjectile: node.free()

## The stage in battle preview at a boss-room step, optionally with that room's boss row swapped in memory.
func _stage(mission_id: String, step: int, swap: Dictionary = {}) -> StoryStage01:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    stage.battle_preview = true
    root.add_child(stage)
    await settle(8)
    if not swap.is_empty():
        var room: Dictionary = stage.main_route[step]
        room["encounter"] = [swap]
        room["reinforcements"] = []
    stage.start_battle_preview(step)
    await settle(4)
    return stage

func _boss_row(mission_id: String) -> Dictionary:
    var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission_id))
    return (((mission.get("main_route", []) as Array)[4] as Dictionary).get("encounter", []) as Array)[0]

func _boss_in(stage: StoryStage01, enemy_id: String) -> EnemyActor:
    var boss: EnemyActor
    for enemy in get_nodes_in_group("m3_enemies"):
        if not stage.is_ancestor_of(enemy): continue
        enemy.set_physics_process(false)
        if enemy.enemy_id == enemy_id: boss = enemy
        else: enemy.hide()
    return boss

func _freeze(stage: StoryStage01) -> OperatorActor:
    stage.set_process(false)
    stage.set_physics_process(false)
    stage.squad.set_process(false)
    stage.squad.set_physics_process(false)
    for operator in stage.squad.operators:
        operator.set_process(false)
        operator.set_physics_process(false)
    return stage.squad.get_active_operator()

## The whole machine (about 260 px tall above its foot point) and the target in frame.
func _frame(stage: StoryStage01, boss: EnemyActor, victim: OperatorActor) -> void:
    var view := Rect2(boss.global_position + Vector2(-140.0, -270.0), Vector2(280.0, 300.0))
    view = view.merge(Rect2(victim.global_position + Vector2(-70.0, -150.0), Vector2(140.0, 190.0)))
    stage.camera.global_position = view.get_center()
    stage.camera.position_smoothing_enabled = false
    stage.camera.force_update_scroll()

## Walks the target a step along painted floor, away from the boss, between two attacks.
func _step_target(stage: StoryStage01, boss: EnemyActor, victim: OperatorActor) -> void:
    var offsets := [Vector2(150.0, 0.0), Vector2(-150.0, 0.0), Vector2(0.0, 110.0), Vector2(0.0, -110.0), Vector2(105.0, 80.0), Vector2(-105.0, -80.0)]
    for offset in offsets:
        var point: Vector2 = victim.global_position + offset
        if stage.battlefield.is_walkable(point) and point.distance_to(boss.global_position) > 170.0:
            victim.global_position = point
            return
