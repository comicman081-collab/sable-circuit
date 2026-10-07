extends SceneTree
const Writer := preload("res://scripts/core/campaign_progression.gd")
const Fixture := preload("res://tests/support/contract_fixture.gd")
func _init() -> void:
    var p := Writer.new(true, "res://tests/fixtures/run_contract/save_v4.json")
    var old := p.snapshot()
    assert(Writer.SAVE_SCHEMA_VERSION == 5)
    assert(p.intel_samples.size() == 3 and p._analyzed_intel.size() == 1)
    assert(p.armory_level == 1 and p.equipped_modules.CHR_PROTO_01 == "MOD_PRISM_FOCUS")
    p._save_path = "res://tests/fixtures/run_contract/save_v5.json"
    p._save()
    var read := Writer.new(true, p._save_path)
    assert(Fixture.equal(read.snapshot(), old))
    assert(read.run_serial == p.run_serial and read._committed_run_ids == p._committed_run_ids)
    var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(p._save_path))
    assert(raw.schema_version == 5 and raw.intel_samples.size() == 3)
    print("V5_BASELINE_WRITER: PASS (schema5, 3 keys, 1 analysis, 1 module, armory1, lossless readback)")
    quit()
