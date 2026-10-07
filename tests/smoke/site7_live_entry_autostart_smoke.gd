extends SceneTree

# Normal campaign entry, not a battle-preview or debug-spawn shortcut.  This
# protects the public demo against an empty first room waiting for an F tap.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var failures: Array[String] = []

func _initialize() -> void:
    call_deferred("run")

func check(value: bool, label: String) -> void:
    if not value:
        failures.append(label)
        push_error(label)

func run() -> void:
    for number in range(1, 11):
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        root.add_child(stage)
        for tick in range(12):
            await process_frame
            await physics_frame
        var expected := (stage.main_route[1].get("encounter", []) as Array).size()
        check(stage.battlefield.world_ready, "Stage %d connected floor failed" % number)
        check(stage.current_step == 1, "Stage %d stayed at the empty access gate" % number)
        check(stage._combat_started, "Stage %d did not start opening combat" % number)
        check(stage.enemies_alive == expected and expected > 0, "Stage %d opening robots missing" % number)
        var actual := 0
        var nearby := 0
        var leader := stage.squad.get_active_operator()
        for enemy in get_nodes_in_group("m3_enemies"):
            if enemy is EnemyActor and stage.is_ancestor_of(enemy):
                actual += 1
                if leader.global_position.distance_to(enemy.global_position) < 600.0:
                    nearby += 1
        check(actual == expected, "Stage %d HUD count is not backed by live enemies" % number)
        if number == 1:
            check(nearby >= 2, "Stage 1 opening scouts are not visible near the player")
        stage.queue_free()
        for tick in range(3):
            await process_frame
            await physics_frame
    print("SITE7_LIVE_ENTRY_AUTOSTART: %s" % ("PASS" if failures.is_empty() else "FAIL"))
    quit(0 if failures.is_empty() else 1)
