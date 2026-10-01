extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const Projectile := preload("res://scripts/combat/prototype_projectile.gd")

const FAR_X := 2300.0 # beyond ally auto-fire range (520 px) and every projectile's reach

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    for _i in range(3):
        await process_frame
    var camera := stage.get_node("Camera2D") as Camera2D
    _check(camera != null and camera.offset == Vector2.ZERO, "camera starts without a shake offset")

    var d := ImpactFeel.director(self)
    await process_frame
    _check(d != null and d.is_inside_tree(), "impact director attaches to the scene root")
    if d == null:
        quit(1)
        return

    # --- camera shake (camera-shake card numbers, 720p scaled) ---
    ImpactFeel.shake(self, 0.0)
    _check(d.debug_shake_count() == 0, "strength below the threshold is ignored")

    ImpactFeel.shake(self, 0.5)
    var peak := Vector2.ZERO
    var started := Time.get_ticks_msec()
    while Time.get_ticks_msec() - started < 450:
        await process_frame
        peak.x = maxf(peak.x, absf(camera.offset.x))
        peak.y = maxf(peak.y, absf(camera.offset.y))
    var card_amp := 6.0 * ImpactFeel.REF_SCALE
    _check(d.debug_shake_count() == 1, "strength 0.5 starts exactly one shake")
    _check(peak.x > 0.5, "shake moves the camera")
    _check(peak.x <= card_amp + 0.01, "x amplitude stays within the card default (6 px at 1080p)")
    _check(peak.y <= card_amp * ImpactFeel.SHAKE_Y_RATIO + 0.01, "y amplitude stays at 4/6 of x")
    _check(camera.offset == Vector2.ZERO, "camera returns exactly to rest")
    _check(not d.debug_shake_active(), "shake releases the camera when finished")

    var before := d.debug_shake_count()
    ImpactFeel.shake(self, 0.9)
    ImpactFeel.shake(self, 0.3)
    _check(d.debug_shake_count() == before + 1, "a weaker shake never replaces a stronger live one")
    await _wait_real(0.6)
    _check(camera.offset == Vector2.ZERO, "stacked shakes also end at rest")

    ImpactFeel.shake_scale = 0.0
    before = d.debug_shake_count()
    ImpactFeel.shake(self, 1.0)
    _check(d.debug_shake_count() == before, "shake_scale 0 disables shake")
    ImpactFeel.shake_scale = 1.0

    # --- hit-stop ---
    ImpactFeel.hit_stop(self, 0.05)
    _check(Engine.time_scale < 1.0, "hit-stop slows engine time")
    await _wait_real(0.25)
    _check(is_equal_approx(Engine.time_scale, 1.0), "hit-stop restores engine time")

    ImpactFeel.hit_stop(self, 5.0)
    await _wait_real(0.3)
    _check(is_equal_approx(Engine.time_scale, 1.0), "hit-stop duration is capped at %.2f s" % ImpactFeel.HIT_STOP_MAX_SEC)

    await _wait_real(0.2)
    ImpactFeel.hit_stop(self, 0.03)
    await _wait_real(0.06)
    var stops := d.debug_hit_stop_count()
    ImpactFeel.hit_stop(self, 0.03)
    _check(d.debug_hit_stop_count() == stops and is_equal_approx(Engine.time_scale, 1.0), "cooldown blocks back-to-back freezes")
    await _wait_real(0.3)

    ImpactFeel.hit_stop_enabled = false
    ImpactFeel.hit_stop(self, 0.05)
    _check(is_equal_approx(Engine.time_scale, 1.0), "hit_stop_enabled false disables freezes")
    ImpactFeel.hit_stop_enabled = true

    # --- gameplay hooks ---
    _check(is_equal_approx(ImpactFeel.stop_for_weight(0.2), 0.0), "light projectiles never freeze")
    _check(ImpactFeel.stop_for_weight(0.65) <= ImpactFeel.HIT_STOP_MAX_SEC, "heavy projectile stop is within the cap")

    var shield := ENEMY_SCENE.instantiate() as EnemyActor
    shield.configure("ENM_SITE7_SHIELD_01", 9999.0)
    shield.position = Vector2(FAR_X, 400)
    stage.add_child(shield)
    shield.set_physics_process(false)
    await process_frame
    before = d.debug_shake_count()
    stops = d.debug_hit_stop_count()
    var projectile := Projectile.new()
    root.add_child(projectile)
    projectile.setup(shield.global_position + Vector2(-20, 0), Vector2.RIGHT, null, Color.WHITE, ArtProfileRegistry.get_profile("ENM_SITE7_SHIELD_01"), "prototype_targets")
    _check(projectile.impact_weight > 0.0, "shield projectile carries an impact weight")
    started = Time.get_ticks_msec()
    while d.debug_shake_count() == before and Time.get_ticks_msec() - started < 1500:
        await process_frame
    _check(d.debug_shake_count() == before + 1, "a heavy projectile hit shakes the camera")
    _check(d.debug_hit_stop_count() == stops + 1, "a heavy projectile hit triggers a hit-stop")
    await _wait_real(0.6)

    before = d.debug_shake_count()
    stops = d.debug_hit_stop_count()
    var drone := ENEMY_SCENE.instantiate() as EnemyActor
    drone.configure("ENM_SITE7_DRONE_01", 50.0)
    drone.position = Vector2(FAR_X + 100.0, 400)
    stage.add_child(drone)
    drone.set_physics_process(false)
    await process_frame
    drone.apply_damage(9999.0)
    await process_frame
    _check(d.debug_shake_count() == before + 1, "enemy defeat shakes the camera")
    _check(d.debug_hit_stop_count() == stops + 1, "enemy defeat triggers a hit-stop")
    await _wait_real(0.6)

    before = d.debug_shake_count()
    var boss := ENEMY_SCENE.instantiate() as EnemyActor
    boss.configure("BOSS_SITE7_ANCHOR_01", 300.0)
    boss.position = Vector2(FAR_X + 200.0, 400)
    stage.add_child(boss)
    boss.set_physics_process(false)
    await process_frame
    await process_frame
    _check(d.debug_shake_count() == before, "boss spawn at full health causes no shake")
    boss.health = 80.0
    await process_frame
    await process_frame
    var boss_premium := boss.get_node_or_null("PremiumPresentation") as PremiumEnemyPresentation
    _check(boss_premium != null and boss_premium.debug_phase() == 3, "boss reaches phase 3")
    _check(d.debug_shake_count() == before + 1, "boss phase change shakes the camera")
    boss.queue_free()
    shield.queue_free()
    await _wait_real(0.6)

    before = d.debug_shake_count()
    stage.squad.operators[2].apply_damage(9999.0)
    await process_frame
    _check(stage.squad.operators[2].is_downed(), "operator is downed")
    _check(d.debug_shake_count() == before + 1, "operator down shakes the camera")
    await _wait_real(0.6)

    # --- everything restored ---
    _check(is_equal_approx(Engine.time_scale, 1.0), "engine time ends at 1.0")
    _check(camera.offset == Vector2.ZERO, "camera ends at rest after every event")

    stage.queue_free()
    await process_frame

    if failures.is_empty():
        print("M6_IMPACT_FEEL_SMOKE: PASS")
        quit(0)
        return
    print("M6_IMPACT_FEEL_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _wait_real(seconds: float) -> void:
    await create_timer(seconds, true, false, true).timeout

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        print("FAIL: " + label)
