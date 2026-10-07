extends SceneTree
const IntelSamples := preload("res://.cache/diag/expansion_item3_20261006/intel_controls/missing_origin_key/intel.gd")
const Output := preload("res://tests/support/test_output.gd")
const BOSS_KEYS := ["ANCHOR", "ANCHOR", "ANCHOR", "ANCHOR", "ANCHOR", "AERATOR", "CRYO", "GANTRY", "ARCHIVE", "ORIGIN"]
var checks := 0
var failures: Array[String] = []
var evidence: Array = []

func _init() -> void: call_deferred("run")
func run() -> void:
    var p := CampaignProgression.new(false)
    var stage: StoryStage01 = load("res://.cache/diag/expansion_item3_20261006/intel_controls/missing_origin_key/stage.gd").new()
    stage.hud = StoryStageHUD.new()
    check(IntelSamples.KEYS == ["SECURITY", "ABERRANT", "ANCHOR", "AERATOR", "CRYO", "GANTRY", "ARCHIVE", "ORIGIN"], "exact eight ordered keys")
    check(p.intel_samples == IntelSamples.empty() and stage._cargo_intel == IntelSamples.empty(), "inventory and cargo initialize all eight keys")
    for n in range(1, 11):
        var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/MIS_CH01_%02d.json" % n))
        var bosses: Array = []
        for room: Dictionary in mission.main_route:
            for enemy: Dictionary in room.get("encounter", []):
                if str(enemy.enemy_id).begins_with("BOSS_"): bosses.append(enemy.enemy_id)
        check(bosses.size() == 1, "operation %d exactly one boss" % n)
        if bosses.size() != 1: continue
        var id: String = bosses[0]
        check(IntelSamples.enemy_key(id) == BOSS_KEYS[n-1], id + " exact mapping before generic BOSS")
        var before := stage.debug_intel_cargo()
        stage._award_enemy_intel(id)
        var awarded := stage.debug_intel_cargo()
        check(awarded[BOSS_KEYS[n-1]] == before[BOSS_KEYS[n-1]] + 1, id + " one defeat adds one sample")
        stage._award_enemy_intel(id)
        check(stage.debug_intel_cargo() == awarded, id + " duplicate defeat never awards twice")
        evidence.append({"enemy":id, "key":BOSS_KEYS[n-1]})
    for pair in [["ENM_SITE7_BULWARK_01", "SECURITY"], ["ENM_SITE7_DRONE_01", "SECURITY"], ["ENM_SITE7_MORTAR_01", "SECURITY"], ["ENM_SITE7_RAM_01", "ABERRANT"], ["ENM_SITE7_PRISM_01", ""], ["ENM_SITE7_NULL_PYLON_01", ""]]:
        check(IntelSamples.enemy_key(pair[0]) == pair[1], pair[0] + " retains HEAD mapping")
        var before := IntelSamples.total(stage.debug_intel_cargo())
        stage._award_enemy_intel(pair[0])
        check(IntelSamples.total(stage.debug_intel_cargo()) == before + (0 if pair[1].is_empty() else 1), pair[0] + " actual award")
    # The old SECURITY analysis costs two, paid by three distinct robot types.
    var cargo := stage.debug_intel_cargo()
    for row: Dictionary in p.snapshot().discoveries:
        check(cargo.get(row.sample_key, 0) >= row.sample_cost, str(row.analysis_id) + " affordable from ten boss defeats and legacy robots")
    var contracts := [RunContract.build("INTEL"), RunContract.redline("INTEL")]
    contracts.append_array(RunContract.offers("INTEL", "MIS_CH01_01"))
    for contract: Dictionary in contracts:
        stage._configure_run_contract(contract)
        var extracted := stage.debug_extraction_summary()
        check(extracted.secured_intel == cargo, "contract does not multiply any sample key")
        var wipe := stage.debug_wipe_summary()
        check(wipe.secured_intel == IntelSamples.empty() and wipe.lost_intel_samples == IntelSamples.total(cargo), "wipe loses and counts all eight keys")
    p.commit_mission({"run_id":"SUPPLY", "secured_intel":cargo, "secured_research":10000})
    for row: Dictionary in p.snapshot().discoveries:
        check(p.analyze_intel(row.analysis_id).success, str(row.analysis_id) + " all analyses reachable")
    check(p.snapshot().analyzed_intel.size() == 8, "all eight analyses completed")
    check(p._sanitize_intel({"AERATOR":-1,"CRYO":2,"UNKNOWN":7}) == IntelSamples.sanitize({"CRYO":2}), "all keys sanitized without unknown or negative values")
    stage.debug_seed_intel(2, 1, 1, {"ORIGIN":3})
    check(stage.debug_intel_cargo().ORIGIN == 3 and stage.debug_intel_cargo().SECURITY == 2, "debug seed retains old signature and new keys")
    var out := Output.path("res://.cache/tests/intel_supply.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out, FileAccess.WRITE)
    f.store_string(JSON.stringify({"checks":checks,"mapping":evidence,"cargo":cargo,"failures":failures}, "  ")); f.close()
    stage.hud.free(); stage.free()
    print("INTEL_SUPPLY_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks)")
    quit(0 if failures.is_empty() else 1)
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
