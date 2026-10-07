extends SceneTree
## Native 1920x1080 frames of the code-drawn combat VFX in an operation room: live
## combat, every projectile with its muzzle flash and wind-up charge, every impact and
## hurt reaction, the explosion kinds at three ages, boss destruction, and each operator's
## Q / E / X skills and buff auras cast from the real operator bodies. Effects are laid
## out in screen space and frozen at set ages so each frame reads the same every run.
## Run windowed (not --headless):
##   Godot --path . -s res://tests/render/combat_vfx_showcase_capture.gd -- --out=res://<folder>

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const TestOutput := preload("res://tests/support/test_output.gd")
const Projectile := preload("res://scripts/combat/prototype_projectile.gd")
const SkillVFX := preload("res://scripts/vfx/operator_skill_vfx.gd")
const HIT_EARLY := 0.07
## The ten bosses, the five of operations 6-10 first. Projectile, impact and colour come from each profile.
const BOSSES := ["BOSS_SITE7_AERATOR_01", "BOSS_SITE7_CRYO_01", "BOSS_SITE7_GANTRY_01", "BOSS_SITE7_ARCHIVE_01", "BOSS_SITE7_ORIGIN_01",
    "BOSS_SITE7_ANCHOR_01", "BOSS_SITE7_RELAY_01", "BOSS_SITE7_REMNANT_01", "BOSS_SITE7_FORGE_01", "BOSS_SITE7_CARRIER_01"]

const OPERATOR_COLORS := {"ASTER": "69d2ff", "ROOK": "ffb45c", "MICA": "62d8c8"}
const PROJECTILES := [
    ["ASTER", "PRJ_ASTER_NEEDLE_01", "69d2ff"], ["ROOK", "PRJ_ROOK_SCATTER_01", "ffb45c"],
    ["MICA", "PRJ_MICA_PULSE_01", "62d8c8"], ["DRONE", "PRJ_ENM_DRONE_BEAMLET_01", "d9577d"],
    ["BULWARK", "PRJ_ENM_SHIELD_01", "e5b860"], ["PRISM", "PRJ_ENM_PRISM_BEAM_01", "8a7bff"],
    ["ANCHOR", "PRJ_BOSS_ANCHOR_LANCE_01", "9b7cff"], ["FORGE", "PRJ_BOSS_FORGE_LANCE_01", "56e3e8"],
    ["CARRIER", "PRJ_BOSS_CARRIER_LANCE_01", "a27aff"]]
const IMPACTS := [
    ["ASTER", "HIT_ASTER_PRISM_01", "69d2ff"], ["ROOK", "HIT_ROOK_CRUSH_01", "ffb45c"],
    ["MICA", "HIT_MICA_SCANBURST_01", "62d8c8"], ["DRONE", "HIT_ENM_DRONE_ARC_01", "d9577d"],
    ["BULWARK", "HIT_ENM_BULWARK_SLUG_01", "e5b860"], ["PRISM", "HIT_ENM_PRISM_REFRACT_01", "8a7bff"],
    ["RAM", "HIT_ENM_RAM_SLAM_01", "ef9251"], ["ANCHOR", "HIT_BOSS_ANCHOR_RIFT_01", "9b7cff"],
    ["FORGE", "HIT_BOSS_FORGE_MELT_01", "56e3e8"], ["CARRIER", "HIT_BOSS_CARRIER_NULL_01", "a27aff"],
    ["ARMOR DEFLECT", "HIT_ARMOR_DEFLECT_01", "ffe09a"], ["BOSS GUARD", "HIT_BARRIER_GUARD_01", "a5e8fa"],
    ["GENERIC", "HIT_GENERIC", "f0f5f7"], ["COVER (ROOK)", "COVER", "ffb45c"]]
const HURTS := [
    ["ROBOT FLINCH", "ENEMY", "ENM_SITE7_BULWARK_01", "FLINCH", "e5b860", false],
    ["ROBOT LIGHT", "ENEMY", "ENM_SITE7_BULWARK_01", "LIGHT", "e5b860", false],
    ["ROBOT HEAVY", "ENEMY", "ENM_SITE7_BULWARK_01", "HEAVY", "e5b860", false],
    ["ROBOT DOWN", "ENEMY", "ENM_SITE7_BULWARK_01", "DOWNED", "e5b860", false],
    ["CRITICAL", "ENEMY", "ENM_SITE7_DRONE_01", "HEAVY", "d9577d", true],
    ["OPERATOR LIGHT", "OPERATOR", "CHR_PROTO_01", "LIGHT", "69d2ff", false],
    ["OPERATOR HEAVY", "OPERATOR", "CHR_PROTO_02", "HEAVY", "ffb45c", false],
    ["OPERATOR DOWN", "OPERATOR", "CHR_PROTO_03", "DOWNED", "62d8c8", false],
    ["BOSS HEAVY", "BOSS", "BOSS_SITE7_ANCHOR_01", "HEAVY", "9b7cff", false]]
## label, kind, colour, radius (world px, as the gameplay callers pass it)
const EXPLOSIONS := [
    ["DRONE DESTROYED", "ROBOT_SMALL", "d9577d", 62.0], ["ROBOT DESTROYED", "ROBOT_HEAVY", "e5b860", 82.0],
    ["MORTAR LANDING", "MORTAR", "c097fa", 64.0], ["ELITE VOLATILE", "VOLATILE", "ff8a4a", 150.0],
    ["BOSS SLAM", "SLAM", "9b7cff", 58.0], ["BOSS LANE", "LANE", "56e3e8", 16.0],
    ["DAMAGED SMOULDER", "SMOLDER", "e5b860", 18.0], ["CINDER RAM TRAIL", "TRAIL", "ef9251", 20.0]]

var out_dir := TestOutput.path("res://.cache/tests/combat_vfx_showcase")
var failed := false
var stage: StoryStage01
var labels: CanvasLayer
var to_world := Transform2D.IDENTITY
var zoom := 1.0
var frame_count := 0

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
    labels = CanvasLayer.new()
    labels.layer = 50
    root.add_child(labels)

    await _live_combat()
    # The showcase frames lay effects out across the screen; the HUD would cover them.
    var hud := stage.get_node_or_null("StoryStageHUD") as CanvasLayer
    if hud != null:
        hud.visible = false
    to_world = stage.get_canvas_transform().affine_inverse()
    zoom = stage.get_canvas_transform().get_scale().x
    print("COMBAT_VFX_SHOWCASE camera zoom ", zoom)
    _hold_actors()
    # Cover props would hide parts of the laid-out effects (and every skill's floor half).
    for prop in get_nodes_in_group("sable_environment_cover"):
        prop.visible = false
    await _projectiles()
    await _impacts()
    await _hurts()
    await _explosions()
    await _boss_families()
    await _boss()
    await _skills()

    if failed:
        quit(1)
    else:
        print("COMBAT_VFX_SHOWCASE_CAPTURE: PASS ", frame_count, " frames ", ProjectSettings.globalize_path(out_dir))
        quit(0)

# --- frames ----------------------------------------------------------------------------

## Real combat: robots fire and wind up on the squad, the squad answers, one robot is
## destroyed and one hurt below the smoulder threshold. Nothing is frozen.
func _live_combat() -> void:
    var enemies := get_nodes_in_group("m3_enemies")
    _check(enemies.size() >= 2, "combat room has robots")
    var active := stage.squad.get_active_operator()
    for step in range(90):
        if step % 9 == 0 and is_instance_valid(active):
            var target := _nearest_enemy(active.global_position)
            if target != null:
                active.aim_world = (target.get_combat_aim_point() - active.global_position).normalized()
                if active.has_method("_try_fire"):
                    active.call("_try_fire", false)
        if step == 30 and enemies.size() >= 2 and is_instance_valid(enemies[1]):
            var hurt := enemies[1] as EnemyActor
            hurt.apply_damage(hurt.max_health * 0.7)
        if step == 70 and is_instance_valid(enemies[0]):
            var doomed := enemies[0] as EnemyActor
            doomed.apply_damage(doomed.max_health * 5.0)
        await physics_frame
        await process_frame
    await _capture("01_live_combat.png")
    for i in range(10):
        await physics_frame
        await process_frame
    await _capture("02_live_combat_destruction.png")
    _clear_vfx()

func _projectiles(rows: Array = PROJECTILES, file_name: String = "03_projectiles_muzzle_charge.png", spacing: float = 72.0) -> void:
    for index in range(rows.size()):
        var row: Array = rows[index]
        var y := 62.0 + float(index) * spacing
        var color := Color(str(row[2]))
        var shot_color := color.lightened(0.35) if OPERATOR_COLORS.has(row[0]) else color
        _label(Vector2(24, y - 30), str(row[0]))
        # Column 1: fired to the right with its muzzle flash at the origin.
        var pellets := 5 if row[0] == "ROOK" else 1
        for p in range(pellets):
            var angle := (float(p) - float(pellets - 1) * 0.5) * 0.09
            _projectile(_w(Vector2(120, y)), Vector2.RIGHT.rotated(angle), shot_color, str(row[1]), 150.0, p == 0)
        # Column 2: mid flight on a diagonal, trail full.
        _projectile(_w(Vector2(560, y + 12)), Vector2.RIGHT.rotated(-0.42), shot_color, str(row[1]), 0.0, false)
        # Column 3: robots' wind-up charge on their emitter.
        if not OPERATOR_COLORS.has(row[0]):
            var charge := CombatMuzzleVFX.new()
            root.add_child(charge)
            charge.global_position = _w(Vector2(820, y))
            charge.mode = CombatMuzzleVFX.MODE_CHARGE
            charge.family = CombatMuzzleVFX.family_for(str(row[1]))
            charge.color = color
            charge.axis = Vector2.RIGHT
            charge.life = 0.9
            charge.age = 0.72
            charge.z_index = 3050
            charge.queue_redraw()
            # Column 4: the same flash on its own, a little later in its life.
            var flash := CombatMuzzleVFX.spawn(self, _w(Vector2(1060, y)), Vector2.RIGHT, str(row[1]), color)
            flash.set_meta("freeze_ratio", 0.55)
    _label(Vector2(120, 8), "FIRED + MUZZLE FLASH")
    _label(Vector2(520, 8), "IN FLIGHT")
    _label(Vector2(780, 8), "ROBOT WIND-UP CHARGE")
    _label(Vector2(1010, 8), "MUZZLE FLASH (LATE)")
    for node in root.get_children():
        if node is CombatMuzzleVFX and not node.has_meta("freeze_ratio") and node.mode == CombatMuzzleVFX.MODE_FLASH:
            node.set_meta("freeze_ratio", 0.3)
    await _capture(file_name)
    _clear_vfx()

func _impacts() -> void:
    for index in range(IMPACTS.size()):
        var row: Array = IMPACTS[index]
        var cell := Vector2(110 + (index % 7) * 177, 150 + (index / 7) * 210)
        _label(cell + Vector2(-60, -110), str(row[0]))
        _impact(row, cell, HIT_EARLY)
    for index in range(7):
        var cell := Vector2(110 + index * 177, 600)
        _impact(IMPACTS[index], cell, 0.0)
    for node in root.get_children():
        if node is CombatHitVFX and _screen(node.global_position).y > 520.0:
            node.set_meta("freeze_ratio", 0.55)
    _label(Vector2(24, 505), "SAME IMPACTS LATER (SPARKS, DEBRIS, SMOKE)")
    await _capture("04_impact_matrix.png")
    _clear_vfx()

func _hurts() -> void:
    for index in range(HURTS.size()):
        var row: Array = HURTS[index]
        for late in range(2):
            var cell := Vector2(80 + index * 140, 210 + late * 300)
            if late == 0:
                _label(cell + Vector2(-60, -150), str(row[0]))
            CombatFeedback.spawn_hurt(self, _w(cell), str(row[1]), str(row[2]), str(row[3]), Color(str(row[4])), bool(row[5]))
            if late == 1:
                for node in root.get_children():
                    if node is CombatHitVFX and not node.has_meta("freeze_ratio") and _screen(node.global_position).y > 400.0:
                        node.set_meta("freeze_ratio", 0.5)
    _label(Vector2(24, 390), "SAME REACTIONS LATER")
    for node in root.get_children():
        if node is CombatHitVFX and not node.has_meta("freeze_ratio"):
            node.set_meta("freeze_age", 0.08)
    await _capture("05_hurt_reactions.png")
    _clear_vfx()

func _explosions() -> void:
    var ratios := [0.08, 0.3, 0.7]
    var names := ["06_explosions_early.png", "07_explosions_mid.png", "08_explosions_late.png"]
    for pass_index in range(3):
        for index in range(EXPLOSIONS.size()):
            var row: Array = EXPLOSIONS[index]
            var cell := Vector2(160 + (index % 4) * 320, 200 + (index / 4) * 330)
            _label(cell + Vector2(-140, -170), "%s  t=%d%%" % [row[0], int(ratios[pass_index] * 100.0)])
            var kind := str(row[1])
            var direction := Vector2.RIGHT
            var reach := 0.0
            var at := _w(cell)
            if kind == "LANE":
                at = _w(cell + Vector2(-130, 0))
                reach = 260.0 / zoom
            var fx := CombatFeedback.spawn_explosion(self, at, kind, Color(str(row[2])), float(row[3]), direction, reach)
            if kind == "TRAIL":
                var path := PackedVector2Array()
                for p in range(14):
                    path.append(_w(cell + Vector2(-130.0 + p * 18.0, 40.0 * sin(float(p) * 0.45))))
                fx.set("_trail", path)
            fx.set_meta("freeze_ratio", ratios[pass_index])
        await _capture(names[pass_index])
        _clear_vfx()

## Every boss family side by side: shots, wind-up charges, impacts (early and late) and heavy hurt reactions.
func _boss_families() -> void:
    var rows: Array = []
    for enemy_id in BOSSES:
        var profile := ArtProfileRegistry.get_profile(enemy_id)
        var palette: Array = profile.get("palette", [])
        rows.append([enemy_id.trim_prefix("BOSS_SITE7_").trim_suffix("_01"), str(profile.get("projectile_profile", "")), str(profile.get("arena_accent", palette[1] if palette.size() > 1 else "#ffffff")).trim_prefix("#"),
            str(profile.get("hit_vfx_profile", "")), enemy_id])
    await _projectiles(rows, "03b_boss_projectiles_muzzle_charge.png", 64.0)
    for pass_index in range(2):
        for index in range(rows.size()):
            var row: Array = rows[index]
            var cell := Vector2(150 + (index % 5) * 250, 200 + (index / 5) * 310)
            _label(cell + Vector2(-100, -150), str(row[0]))
            _impact([row[0], row[3], row[2]], cell, HIT_EARLY)
        if pass_index == 1:
            for node in root.get_children():
                if node is CombatHitVFX: node.set_meta("freeze_ratio", 0.55)
        await _capture(["04b_boss_impact_matrix_early.png", "04c_boss_impact_matrix_late.png"][pass_index])
        _clear_vfx()
    for index in range(rows.size()):
        var row: Array = rows[index]
        var cell := Vector2(150 + (index % 5) * 250, 220 + (index / 5) * 310)
        _label(cell + Vector2(-100, -170), str(row[0]) + " HEAVY HIT")
        CombatFeedback.spawn_hurt(self, _w(cell), "BOSS", str(row[4]), "HEAVY", Color(str(row[2])), false)
    for node in root.get_children():
        if node is CombatHitVFX and not node.has_meta("freeze_ratio"):
            node.set_meta("freeze_age", 0.08)
    await _capture("05b_boss_hurt_reactions.png")
    _clear_vfx()

func _boss() -> void:
    var ages := [0.22, 0.62, 1.12, 1.7]
    for index in range(ages.size()):
        var cell := Vector2(170 + index * 313, 360)
        _label(cell + Vector2(-140, -250), "BOSS DESTROYED  %.2fs" % ages[index])
        var fx := CombatFeedback.spawn_explosion(self, _w(cell), "BOSS", Color("9b7cff"), 130.0, Vector2.RIGHT, 0.0, _w(cell + Vector2(0, 70)))
        fx.set_meta("freeze_age", ages[index])
    await _capture("09_boss_destruction.png")
    _clear_vfx()

## Each slot cast from the three real operators, with real robots as targets.
func _skills() -> void:
    var operators: Array = stage.squad.operators
    var enemies := get_nodes_in_group("m3_enemies").filter(func(e): return is_instance_valid(e) and e.health > 0.0)
    var columns := [Vector2(230, 470), Vector2(640, 470), Vector2(1050, 470)]
    var first: EnemyActor = enemies[0] if not enemies.is_empty() else null
    var second: EnemyActor = enemies[1 % enemies.size()] if not enemies.is_empty() else null
    var slots := [
        ["10_skills_q.png", [["ASTER Q  PRISM LANCE", "ASTER_PRISM", 0.62, 0.22], ["ROOK Q  BREACH SLAM", "ROOK_BREACH_SLAM", 0.62, 0.2], ["MICA Q  PULSE SCAN", "MICA_PULSE_SCAN", 0.82, 0.3]]],
        ["11_skills_e.png", [["ASTER E  VECTOR DASH", "VECTOR_DASH", 0.62, 0.2], ["ROOK E  BULWARK", "BULWARK", 0.62, 0.3], ["MICA E  RELAY STEP", "RELAY_STEP", 0.62, 0.25]]],
        ["12_skills_x.png", [["ASTER X  OVERCLOCK", "OVERCLOCK", 0.85, 0.25], ["ROOK X  SCATTER CYCLE", "SCATTER_CYCLE", 0.85, 0.25], ["MICA X  SENSOR BLOOM", "SENSOR_BLOOM", 1.0, 0.3]]],
        ["13_buff_auras.png", [["ASTER OVERCLOCK AURA", "OVERCLOCK_AURA", 5.0, 0.2], ["ROOK GUARD + SCATTER AURAS", "GUARD_AURA+SCATTER_AURA", 5.0, 0.2]]]]
    for slot in slots:
        var casts: Array = slot[1]
        for column in range(casts.size()):
            var cast: Array = casts[column]
            var body: OperatorActor = operators[column] as OperatorActor
            var at := _w(columns[column])
            body.global_position = at
            body.velocity = Vector2.ZERO
            _label(columns[column] + Vector2(-150, -300), str(cast[0]))
            var aim := Vector2.RIGHT
            var radius := 40.0
            var targets: Array = []
            var enemy: EnemyActor = first if column == 0 else second
            match str(cast[1]):
                "ASTER_PRISM":
                    radius = 150.0 / zoom
                    aim = Vector2(1, -0.35).normalized()
                    if enemy != null:
                        enemy.global_position = at + aim * radius + Vector2(0, 30)
                        targets = [enemy]
                "ROOK_BREACH_SLAM": radius = 150.0
                "MICA_PULSE_SCAN":
                    radius = 300.0
                    if enemy != null:
                        enemy.global_position = at + Vector2(120, -60) / zoom
                        targets = [enemy]
                "VECTOR_DASH": radius = 150.0
                "BULWARK": radius = 70.0
                "RELAY_STEP":
                    radius = 120.0
                    aim = Vector2.LEFT
                    targets = [operators[0], operators[1]]
                "OVERCLOCK": radius = 105.0
                "SCATTER_CYCLE": radius = 160.0
                "SENSOR_BLOOM":
                    radius = 360.0
                    if second != null and first != null:
                        second.global_position = at + Vector2(-150, -110) / zoom
                        first.global_position = at + Vector2(120, -40) / zoom
                        targets = [second, first] if second != first else [second]
            for skill_id in str(cast[1]).split("+"):
                var fx := SkillVFX.new() as OperatorSkillVFX
                root.add_child(fx)
                fx.global_position = at + Vector2(0, -18)
                fx.setup(skill_id, body.accent_color.lightened(0.12), radius, aim, float(cast[2]))
                if not targets.is_empty():
                    fx.mark_targets(targets)
                fx.set_meta("freeze_ratio", float(cast[3]))
        await _capture(str(slot[0]))
        _clear_vfx()

# --- helpers ---------------------------------------------------------------------------

func _projectile(at: Vector2, direction: Vector2, color: Color, profile: String, ahead: float, with_flash: bool) -> void:
    var shot := Projectile.new() as PrototypeProjectile
    if with_flash:
        root.add_child(shot)
        shot.setup(at, direction, null, color, {"projectile_profile": profile}, "none")
    else:
        shot.setup(at, direction, null, color, {"projectile_profile": profile}, "none")
        root.add_child(shot)
    shot.set_physics_process(false)
    shot.global_position = at + direction * ahead / zoom
    shot.set("_travelled", 400.0)
    shot.set("_age", 0.12)
    shot.queue_redraw()

func _impact(row: Array, cell: Vector2, _age: float) -> void:
    var color := Color(str(row[2]))
    if row[1] == "COVER":
        CombatFeedback.spawn_cover_hit(self, _w(cell), {"hit_vfx_profile": "HIT_ROOK_CRUSH_01"}, color, null, Vector2.RIGHT)
    else:
        CombatFeedback.spawn_hit_visual(self, _w(cell), str(row[1]), color, Vector2.RIGHT)

func _nearest_enemy(from: Vector2) -> EnemyActor:
    var best: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        var enemy := node as EnemyActor
        if enemy != null and enemy.health > 0.0 and (best == null or from.distance_to(enemy.global_position) < from.distance_to(best.global_position)):
            best = enemy
    return best

## Robots and followers stop thinking so bodies stay where the frames put them.
func _hold_actors() -> void:
    for node in get_nodes_in_group("m3_enemies"):
        node.process_mode = Node.PROCESS_MODE_DISABLED
    for node in get_nodes_in_group("operators"):
        node.process_mode = Node.PROCESS_MODE_DISABLED
    for group in ["site7_attack_warnings", "site7_mortar_shells"]:
        for node in get_nodes_in_group(group):
            node.queue_free()

func _w(screen_point: Vector2) -> Vector2:
    return to_world * screen_point

func _screen(world_point: Vector2) -> Vector2:
    return to_world.affine_inverse() * world_point

func _label(at: Vector2, text: String) -> void:
    var label := Label.new()
    label.text = text
    label.position = at
    label.add_theme_font_size_override("font_size", 13)
    label.add_theme_color_override("font_color", Color(0.92, 0.95, 1.0))
    label.add_theme_color_override("font_outline_color", Color(0, 0, 0))
    label.add_theme_constant_override("outline_size", 4)
    labels.add_child(label)

## Freezes every effect at its requested age (meta "freeze_age" in seconds or
## "freeze_ratio" of its life), pauses the tree and saves the native frame.
func _capture(file_name: String) -> void:
    for node in root.get_children():
        if node is CombatHitVFX:
            var hit := node as CombatHitVFX
            hit.age = _freeze_time(node, hit.lifetime, HIT_EARLY)
            hit.call("_sync_visual_layers", clampf(hit.age / hit.lifetime, 0.0, 1.0))
            hit.queue_redraw()
        elif node is CombatExplosionVFX:
            var blast := node as CombatExplosionVFX
            if node.has_meta("freeze_ratio") or node.has_meta("freeze_age"):
                blast.age = _freeze_time(node, blast.duration, 0.1)
                blast.call("_process", 0.0)
        elif node is CombatMuzzleVFX:
            var muzzle := node as CombatMuzzleVFX
            if node.has_meta("freeze_ratio"):
                muzzle.age = muzzle.life * float(node.get_meta("freeze_ratio"))
            muzzle.queue_redraw()
        elif node is OperatorSkillVFX:
            var skill := node as OperatorSkillVFX
            if node.has_meta("freeze_ratio"):
                var t := float(node.get_meta("freeze_ratio"))
                skill.life = skill.max_life * (1.0 - t)
                skill.set("_age", skill.max_life * t)
            skill.queue_redraw()
        elif node.is_in_group("vfx_ground_marks") and node.has_meta("freeze_age"):
            node.set("age", float(node.get_meta("freeze_age")))
            node.queue_redraw()
    # Ground marks spawned with a frozen explosion age with it.
    for mark in get_nodes_in_group("vfx_ground_marks"):
        mark.queue_redraw()
    paused = true
    await process_frame
    await process_frame
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    _check(image.get_size() == Vector2i(1920, 1080), file_name + " is native 1920x1080, got " + str(image.get_size()))
    _check(image.save_png(ProjectSettings.globalize_path(out_dir.path_join(file_name))) == OK, file_name + " saved")
    frame_count += 1
    paused = false

func _freeze_time(node: Node, life: float, fallback: float) -> float:
    if node.has_meta("freeze_age"):
        return float(node.get_meta("freeze_age"))
    if node.has_meta("freeze_ratio"):
        return life * float(node.get_meta("freeze_ratio"))
    return fallback

func _clear_vfx() -> void:
    for node in root.get_children():
        if node is CombatHitVFX or node is CombatExplosionVFX or node is CombatMuzzleVFX or node is OperatorSkillVFX or node is PrototypeProjectile:
            node.free()
    for mark in get_nodes_in_group("vfx_ground_marks"):
        mark.free()
    for label in labels.get_children():
        label.free()

func _settle(frames: int) -> void:
    for i in range(frames):
        await physics_frame
        await process_frame

func _check(condition: bool, message: String) -> void:
    if not condition:
        failed = true
        push_error(message)
