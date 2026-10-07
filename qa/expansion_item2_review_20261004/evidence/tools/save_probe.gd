extends SceneTree
## Claude review helper (item 2): load a save file with CampaignProgression, print and write its snapshot.
## usage: save_probe.gd -- --save=res://.cache/in/x.json --out=res://.cache/out/y.json [--resave=1]
## --resave=1 writes the loaded state back through the same code first and dumps the re-read snapshot too.
func _init() -> void:
    var save := ""
    var out := "res://.cache/out/save_probe.json"
    var resave := false
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--save="): save = a.trim_prefix("--save=")
        if a.begins_with("--out="): out = a.trim_prefix("--out=")
        if a == "--resave=1": resave = true
    var p := CampaignProgression.new(true, save)
    var row := {"schema_const": CampaignProgression.SAVE_SCHEMA_VERSION, "snapshot": p.snapshot(), "run_serial": p.run_serial,
        "committed_run_ids": p._committed_run_ids.duplicate(), "redline_cleared": p.get("redline_cleared")}
    if resave:
        p._save()
        var again := CampaignProgression.new(true, save)
        row["reread_snapshot"] = again.snapshot()
        row["reread_run_serial"] = again.run_serial
        row["reread_committed_run_ids"] = again._committed_run_ids.duplicate()
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out, FileAccess.WRITE)
    f.store_string(JSON.stringify(row, "", true)); f.close()
    print("SAVE_PROBE: ", save, " -> ", out)
    quit(0)
