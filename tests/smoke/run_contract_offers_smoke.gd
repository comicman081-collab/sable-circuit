extends SceneTree
const Fixture := preload("res://tests/support/contract_fixture.gd")
var checks := 0
var failures: Array[String] = []
func _init() -> void:
    var golden: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/run_contract/head_7b26a152_golden.json"))
    check((golden.contracts as Array).size() == 64, "64 HEAD contracts frozen before implementation")
    for row: Dictionary in golden.contracts:
        var run_id := str(row.run_id)
        # JSON decodes whole numbers as floats; compare the entire canonical
        # payload rather than treating a Dictionary's numeric storage type as drift.
        check(Fixture.equal(RunContract.build(run_id), row), run_id + " complete HEAD return shape/values unchanged")
        for n in range(1, 11):
            var id := "MIS_CH01_%02d" % n
            var offers := RunContract.offers(run_id, id)
            check(offers.size() == 3 and Fixture.equal(offers[0], row), id + " default is HEAD")
            check(offers == RunContract.offers(run_id, id), id + " offers deterministic")
            var pairs := {}
            for offer in offers:
                pairs[RunContract.identity(offer)] = true
                for key in ["enemy_health_multiplier", "enemy_damage_multiplier"]: check(float(offer[key]) >= 0.5 and float(offer[key]) <= 3.0, key + " clamp")
                for key in ["enemy_speed_multiplier", "enemy_attack_interval_multiplier"]: check(float(offer[key]) >= 0.5 and float(offer[key]) <= 2.0, key + " clamp")
                for key in ["research_reward_multiplier", "salvage_reward_multiplier", "fragment_reward_multiplier"]: check(float(offer[key]) >= 0.5 and float(offer[key]) <= 4.0, key + " stage clamp")
                for other in offers:
                    if int(offer.risk_score) > int(other.risk_score):
                        for key in ["research_reward_multiplier", "salvage_reward_multiplier", "fragment_reward_multiplier"]: check(float(offer[key]) >= float(other[key]), "higher risk preserves each resource reward")
            check(pairs.size() == 3, id + " three distinct hazard/opportunity pairs")
            var redline := RunContract.redline(run_id)
            for offer in offers:
                check(int(redline.risk_score) > int(offer.risk_score), "REDLINE risk exceeds offers")
                for key in ["research_reward_multiplier", "salvage_reward_multiplier", "fragment_reward_multiplier"]: check(float(redline[key]) > float(offer[key]), "REDLINE reward exceeds all offers")
    var r := RunContract.redline("BOUNDARY")
    check(float(r.enemy_health_multiplier) > 1.25 and float(r.enemy_health_multiplier) <= 1.5, "REDLINE HP proposal")
    check(float(r.enemy_damage_multiplier) > 1.20 and float(r.enemy_damage_multiplier) <= 1.35, "REDLINE damage proposal")
    check(float(r.enemy_speed_multiplier) > 1.10 and float(r.enemy_speed_multiplier) <= 1.15, "REDLINE speed proposal")
    check(float(r.enemy_attack_interval_multiplier) < 0.88 and float(r.enemy_attack_interval_multiplier) >= 0.80, "REDLINE interval proposal")
    check(RunContract.REDLINE_HAZARD_REWARD <= 1.6 and RunContract.REDLINE_OPPORTUNITY_REWARD <= 3.0, "REDLINE recovery uses unchanged clamps")
    print("RUN_CONTRACT_OFFERS_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks)")
    quit(0 if failures.is_empty() else 1)
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
