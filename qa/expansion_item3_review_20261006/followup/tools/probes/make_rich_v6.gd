extends SceneTree
## Claude review probe (item 3): build a fully loaded schema-6 save with the real purchase / equip functions (new code only).
## usage (after --):  --out=res://<file>
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
func _init() -> void:
    var out := ""
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--out="): out = a.substr(6)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out, FileAccess.WRITE); f.store_string("{}"); f.close()
    var p := CampaignProgression.new(true, out)
    p.research_value = 10000; p.salvage = 100; p.signal_fragments = 100
    p.intel_samples = IntelSamples.sanitize({"SECURITY": 2, "ABERRANT": 1, "ANCHOR": 1, "AERATOR": 3, "CRYO": 1, "GANTRY": 2, "ARCHIVE": 1, "ORIGIN": 4})
    var analysed := 0
    for row: Dictionary in p.snapshot().discoveries:
        if p.analyze_intel(row.analysis_id).success: analysed += 1
    var results := []
    results.append(p.equip_module("CHR_PROTO_01", "MOD_RAIL_SPOOL").reason)
    results.append(p.equip_module("CHR_PROTO_02", "MOD_NULL_ANCHOR").reason)
    results.append(p.equip_module("CHR_PROTO_03", "MOD_ECHO_RELAY").reason)
    results.append(p.equip_weapon("CHR_PROTO_01", "WPN_DMR_RAIL_01").reason)
    results.append(p.equip_weapon("CHR_PROTO_02", "WPN_SHOTGUN_NULL_01").reason)
    p._save()
    print("MAKE_RICH_V6 analysed=", analysed, " results=", results, " schema=", p.snapshot().schema_version, " samples=", p.intel_samples)
    quit(0)
