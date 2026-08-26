extends SceneTree

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var actor := OPERATOR_SCENE.instantiate() as OperatorActor
    actor.configure("CHR_PROTO_01", "ASTER", Color("69d2ff"))
    root.add_child(actor)
    await process_frame
    await process_frame
    var premium := actor.get_node_or_null("PremiumPresentation") as PremiumOperatorPresentation
    _check(premium != null, "operator premium presentation exists")
    _check(premium != null and premium.debug_has_face_rig(), "operator facial micro rig exists")
    if premium:
        var sector_classes: Array[String] = []
        for sector in range(8):
            var c := premium.debug_sector_contract(sector)
            sector_classes.append("%d:%s:%s:%s" % [sector, c.get("front"), c.get("rear"), c.get("left")])
        _check(sector_classes.size() == 8, "eight directional sectors are addressable")
        actor.facing_sector = 6
        await process_frame
        _check(premium.face != null and not premium.face.visible, "rear sector hides facial overlay")
        actor.facing_sector = 2
        await process_frame
        _check(premium.face != null and premium.face.visible, "front sector shows facial overlay")
    actor.queue_free()
    await process_frame

    var enemy := ENEMY_SCENE.instantiate() as EnemyActor
    enemy.configure("ENM_SITE7_DRONE_01", 50.0)
    root.add_child(enemy)
    await process_frame
    var enemy_premium := enemy.get_node_or_null("PremiumPresentation") as PremiumEnemyPresentation
    _check(enemy_premium != null, "enemy premium presentation exists")
    enemy.apply_damage(999.0)
    await process_frame
    _check(get_nodes_in_group("enemy_death_sequences").size() >= 1, "enemy defeat spawns identity death sequence")
    for seq in get_nodes_in_group("enemy_death_sequences"):
        if is_instance_valid(seq): seq.queue_free()
    await process_frame

    var boss := ENEMY_SCENE.instantiate() as EnemyActor
    boss.configure("BOSS_SITE7_ANCHOR_01", 300.0)
    root.add_child(boss)
    await process_frame
    boss.health = 80.0
    await process_frame
    var boss_premium := boss.get_node_or_null("PremiumPresentation") as PremiumEnemyPresentation
    _check(boss_premium != null, "boss premium presentation exists")
    _check(boss_premium != null and boss_premium.debug_phase() == 3, "boss enters phase 3 below 33 percent health")
    boss.queue_free()
    await process_frame

    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    await process_frame
    var env := stage.get_node_or_null("EnvironmentDirector") as Stage01EnvironmentDirector
    _check(env != null, "Stage01 environment director exists")
    if env:
        _check(env.debug_room_style_count() == 8, "Stage01 has eight authored room environment styles")
        var signatures := env.debug_room_signatures()
        var unique: Dictionary = {}
        for sig in signatures:
            unique[str(sig)] = true
        _check(unique.size() == 8, "all Stage01 room visual signatures are unique")
    stage.queue_free()
    await process_frame

    if failures.is_empty():
        print("M4_PREMIUM_MOTION_ENVIRONMENT_SMOKE: PASS")
        quit(0)
        return
    print("M4_PREMIUM_MOTION_ENVIRONMENT_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
