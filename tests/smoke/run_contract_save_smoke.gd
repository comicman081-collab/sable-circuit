extends SceneTree
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
const Output := preload("res://tests/support/test_output.gd")
const Fixture := preload("res://tests/support/contract_fixture.gd")
var checks := 0
var failures: Array[String] = []
var path := Output.path("res://.cache/tests/run_contract/save.json")
func _init() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(path.get_base_dir()))
    check(CampaignProgression.SAVE_SCHEMA_VERSION == 6, "save schema 6")
    for version in [3,4,5]:
        var fixture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/run_contract/save_v%d.json" % version))
        write(fixture)
        var p := CampaignProgression.new(true, path)
        var before := p.snapshot()
        for key in fixture:
            if key in ["schema_version", "run_serial", "committed_run_ids"]: continue
            if key == "intel_samples":
                check(before[key].size() == 8, "v%d has all eight intel keys" % version)
                for sample in fixture[key]:
                    check(Fixture.equal(before[key][sample], fixture[key][sample]), "v%d preserves sample %s" % [version, sample])
                for sample in ["AERATOR", "CRYO", "GANTRY", "ARCHIVE", "ORIGIN"]:
                    check(before[key][sample] == 0, "v%d initializes %s to zero" % [version, sample])
            elif key in ["discoveries", "weapon_catalog"]:
                preserve_rows(fixture[key], before[key], key, version)
            else:
                check(Fixture.equal(before.get(key), fixture[key]), "v%d preserves %s" % [version, key])
        check(p.run_serial == int(fixture.run_serial) and p._committed_run_ids == fixture.committed_run_ids, "old transaction dedupe and run serial preserved")
        check(before.redline_cleared.is_empty(), "old saves never infer REDLINE clears")
        p._save()
        var after := CampaignProgression.new(true, path)
        check(after.snapshot() == before and after.run_serial == p.run_serial and after._committed_run_ids == p._committed_run_ids, "v%d schema6 write/read equality" % version)
        check(not before.has("run_contract") and not before.has("active_run_boosts"), "deployment modifiers never persisted")
    var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/run_contract/save_v4.json"))
    data.schema_version = 99
    data["unknown_future_field"] = {"anything":123}
    data["run_contract"] = RunContract.redline("NEVER-SAVED")
    data["redline_cleared"] = ["MIS_CH01_01", "MIS_CH01_01", "MIS_CH01_02", "MIS_CH01_99", 17]
    write(data)
    var p := CampaignProgression.new(true, path)
    check(p.redline_cleared == ["MIS_CH01_01"], "sanitize unknown, uncleared and duplicate REDLINE IDs")
    check(not p.snapshot().has("unknown_future_field") and not p.snapshot().has("run_contract"), "ignore unknown future fields")
    p._save()
    var again := CampaignProgression.new(true, path)
    check(again.snapshot() == p.snapshot() and again.redline_cleared == p.redline_cleared, "REDLINE clear persists")
    for malformed in [null, "MIS_CH01_01", {}, 9]:
        data.redline_cleared = malformed
        write(data)
        check(CampaignProgression.new(true, path).redline_cleared.is_empty(), "ignore malformed REDLINE list")
    print("RUN_CONTRACT_SAVE_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks)")
    quit(0 if failures.is_empty() else 1)
func write(value: Dictionary) -> void:
    var f := FileAccess.open(path, FileAccess.WRITE)
    f.store_string(JSON.stringify(value)); f.close()
func preserve_rows(old: Array, current: Array, kind: String, version: int) -> void:
    var id := "analysis_id" if kind == "discoveries" else "weapon_id"
    check(current.size() == 8, "v%d expanded %s count" % [version, kind])
    for row: Dictionary in old:
        var matches := current.filter(func(r: Dictionary) -> bool: return r.get(id) == row[id])
        check(matches.size() == 1 and Fixture.equal(matches[0], row), "v%d preserves complete old %s row %s" % [version, kind, row[id]])
    for row: Dictionary in current:
        if old.any(func(r: Dictionary) -> bool: return r[id] == row[id]): continue
        if kind == "discoveries":
            check(not row.analyzed and not row.module_unlocked and not row.can_analyze, "v%d new analysis locked %s" % [version, row[id]])
        else:
            check(not row.unlocked, "v%d new weapon locked %s" % [version, row[id]])
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
