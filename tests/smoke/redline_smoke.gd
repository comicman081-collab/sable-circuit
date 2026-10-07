extends SceneTree
const Stage := preload("res://scenes/mission/StoryStage01.tscn")
const Output := preload("res://tests/support/test_output.gd")
var checks := 0
var failures: Array[String] = []
var rows := []
func _init() -> void: call_deferred("run")
func run() -> void:
    var contract := RunContract.redline("REDLINE-ACTORS")
    # The shipped first setting (order doc 9.11): a later change is one deliberate edit here and in run_contract.gd.
    check(is_equal_approx(RunContract.REDLINE_HEALTH, 1.35) and is_equal_approx(RunContract.REDLINE_DAMAGE, 1.25) and is_equal_approx(RunContract.REDLINE_SPEED, 1.12) and is_equal_approx(RunContract.REDLINE_INTERVAL, 0.85), "REDLINE enemy multipliers are the order 9.11 first setting")
    var stage := Stage.instantiate() as StoryStage01
    root.add_child(stage)
    await frames(3)
    stage.configure_campaign({}, "REDLINE-ACTORS", contract)
    for step in [1,4]:
        stage.debug_spawn_encounter_for_step(step)
        await frames(2)
        var source_index := 0
        for node in get_nodes_in_group("m3_enemies"):
            if not (node is EnemyActor): continue
            var enemy := node as EnemyActor
            enemy.set_physics_process(false)
            var room: Dictionary = stage.main_route[step]
            var row: Dictionary = (room.encounter as Array)[source_index]
            source_index += 1
            check(str(row.enemy_id) == enemy.enemy_id, "spawn order matches the authored encounter row")
            var authored := float(row.health)
            check(authored > 0 and is_equal_approx(enemy.max_health, authored * RunContract.REDLINE_HEALTH), enemy.enemy_id + " actual authored HP multiplied exactly once")
            check(is_equal_approx(enemy.run_damage_multiplier, RunContract.REDLINE_DAMAGE), enemy.enemy_id + " actual damage multiplier")
            var boss := enemy.enemy_id.begins_with("BOSS_")
            check(is_equal_approx(enemy.run_speed_multiplier, 1.0 if boss else RunContract.REDLINE_SPEED), enemy.enemy_id + " actual movement factor")
            check(is_equal_approx(enemy.run_attack_interval_multiplier, 1.0 if boss else RunContract.REDLINE_INTERVAL), enemy.enemy_id + " actual interval factor")
            var fired := []
            enemy.projectile_emitted.connect(func(event: Dictionary) -> void: fired.append(event))
            enemy._spawn_projectile(Vector2.RIGHT)
            check(fired.size() == 1, enemy.enemy_id + " real projectile emitted")
            if fired.size() == 1:
                var shot := instance_from_id(int(fired[0].projectile_id)) as PrototypeProjectile
                var normal := PrototypeProjectile.new()
                root.add_child(normal)
                normal.setup(Vector2.ZERO, Vector2.RIGHT, enemy, Color.WHITE, enemy.art_profile, "operators")
                check(is_equal_approx(shot.damage, normal.damage * RunContract.REDLINE_DAMAGE), enemy.enemy_id + " real projectile damage multiplied once")
                normal.free(); shot.free()
            rows.append({"enemy":enemy.enemy_id, "authored_hp":authored, "actual_hp":enemy.max_health, "speed":enemy.run_speed_multiplier, "interval":enemy.run_attack_interval_multiplier})
            enemy.queue_free()
        await frames(2)
    stage.debug_seed_cargo(100,40,10,10,true,6)
    var summary := stage.debug_extraction_summary("R06_EXTRACT")
    check(int(summary.secured_research) == 336 and int(summary.secured_salvage) == 24 and int(summary.secured_fragments) == 24, "actual extraction reward multiplied exactly once by 2.4")
    check(summary.run_contract == contract, "actual summary retains chosen contract")
    var extreme := contract.duplicate(true)
    for key in ["enemy_health_multiplier", "enemy_damage_multiplier", "enemy_speed_multiplier", "enemy_attack_interval_multiplier", "research_reward_multiplier", "salvage_reward_multiplier", "fragment_reward_multiplier"]: extreme[key] = 99.0
    stage.configure_campaign({}, "CLAMP-TEST", extreme)
    stage.debug_seed_cargo(100,0,10,10,true,6)
    var capped := stage.debug_extraction_summary("R06_EXTRACT")
    check(int(capped.secured_research) == 400 and int(capped.secured_salvage) == 40 and int(capped.secured_fragments) == 40, "actual stage keeps 4× reward clamp")
    stage.debug_spawn_encounter_for_step(1)
    await frames(2)
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor:
            check(is_equal_approx(node.run_health_multiplier,3.0) and is_equal_approx(node.run_damage_multiplier,3.0) and is_equal_approx(node.run_speed_multiplier,2.0) and is_equal_approx(node.run_attack_interval_multiplier,2.0), "actual actor retains existing clamps on oversized input")
    stage.queue_free(); await frames(2)
    var catalog := preload("res://scripts/core/site7_campaign.gd")
    check(not RunContract.redline_available("MIS_CH01_01", []), "uncleared operation has no REDLINE")
    check(not RunContract.redline_available("MIS_CH01_02", []), "locked operation has no REDLINE")
    check(not RunContract.redline_available("MIS_CH01_99", ["MIS_CH01_99"]), "unknown operation has no REDLINE")
    for fault in ["WIPED", "EARLY", "PREVIEW", "LOCKED", "DUPLICATE", "UNCLEARED", "VALID"]:
        var p := CampaignProgression.new(false)
        if fault != "UNCLEARED": p.commit_mission({"transaction_id":"BASE", "mission_id":"MIS_CH01_01", "outcome":"EXTRACTED", "full_route_cleared":true})
        var old_clears := p.cleared_missions.duplicate()
        var before_ids := catalog.ui_rows(old_clears)
        var data := {"transaction_id":"BASE" if fault == "DUPLICATE" else "NEW", "mission_id":"MIS_CH01_03" if fault == "LOCKED" else "MIS_CH01_01", "outcome":"WIPED" if fault == "WIPED" else "EXTRACTED", "full_route_cleared":fault != "EARLY", "battle_preview":fault == "PREVIEW", "run_contract":contract}
        var transaction := p.commit_mission(data)
        check(p.redline_cleared == (["MIS_CH01_01"] if fault == "VALID" else []), fault + " REDLINE record gate")
        check(p.cleared_missions == old_clears and catalog.ui_rows(p.cleared_missions) == before_ids, fault + " never changes ordinary mission locks/clears")
        if fault in ["PREVIEW", "LOCKED", "DUPLICATE", "UNCLEARED"]: check(not bool(transaction.get("committed", true)), fault + " transaction rejection retained")
    var out := Output.path("res://.cache/tests/run_contract/redline.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out, FileAccess.WRITE)
    f.store_string(JSON.stringify({"checks":checks,"failures":failures,"actors":rows,"proposal":contract,"human_play":false,"balance_approval":false}, "  ")); f.close()
    print("REDLINE_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks)")
    quit(0 if failures.is_empty() else 1)
func frames(n: int) -> void:
    for _i in range(n): await process_frame
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
