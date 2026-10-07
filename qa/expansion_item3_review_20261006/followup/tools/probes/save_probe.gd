extends SceneTree
## Claude review probe (item 3): read one save file through CampaignProgression, dump the snapshot, save, read again, dump again.
## Works on the old (schema 5) and the new (schema 6) code. Writes only below --out (a res:// folder inside the scratch snapshot).
## usage (after --):  --in=res://<save json>  --out=res://<folder>  --tag=<name>
func _init() -> void:
    var args := {}
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--") and a.find("=") > 0: args[a.get_slice("=", 0).trim_prefix("--")] = a.substr(a.find("=") + 1)
    var src := str(args.get("in", ""))
    var out_dir := str(args.get("out", ""))
    var tag := str(args.get("tag", "probe"))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))
    var work := out_dir.path_join(tag + "_work.json")
    var f := FileAccess.open(work, FileAccess.WRITE); f.store_string(FileAccess.get_file_as_string(src)); f.close()
    var p := CampaignProgression.new(true, work)
    var first := p.snapshot()
    p._save()
    var written1 := FileAccess.get_file_as_string(work)
    var p2 := CampaignProgression.new(true, work)
    var second := p2.snapshot()
    p2._save()
    var written2 := FileAccess.get_file_as_string(work)
    dump(out_dir.path_join(tag + "_snapshot1.json"), first)
    dump(out_dir.path_join(tag + "_snapshot2.json"), second)
    dump(out_dir.path_join(tag + "_written1.json"), JSON.parse_string(written1))
    dump(out_dir.path_join(tag + "_written2.json"), JSON.parse_string(written2))
    print("SAVE_PROBE ", tag, " schema_code=", CampaignProgression.SAVE_SCHEMA_VERSION, " snapshot_equal_after_save=", first == second, " file_stable_after_second_save=", written1 == written2, " keys=", first.size())
    quit(0)
func dump(path: String, value: Variant) -> void:
    var f := FileAccess.open(path, FileAccess.WRITE)
    f.store_string(JSON.stringify(value, "  ", true)); f.close()
