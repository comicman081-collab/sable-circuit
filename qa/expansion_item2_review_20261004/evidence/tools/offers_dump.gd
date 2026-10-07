extends SceneTree
## Claude review helper (item 2): dump offers() for run ids x missions, plus redline(), as canonical JSON.
## usage: offers_dump.gd -- --ids=res://.cache/ids.json --out=res://.cache/out/offers_<tag>.json
func _init() -> void:
    var ids_path := "res://.cache/ids.json"
    var out := "res://.cache/out/offers_dump.json"
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--ids="): ids_path = a.trim_prefix("--ids=")
        if a.begins_with("--out="): out = a.trim_prefix("--out=")
    var ids: Array = JSON.parse_string(FileAccess.get_file_as_string(ids_path))
    var rows := {}
    for id in ids:
        var per := {}
        for n in range(1, 11):
            var m := "MIS_CH01_%02d" % n
            per[m] = RunContract.offers(str(id), m)
        per["REDLINE"] = RunContract.redline(str(id))
        rows[str(id)] = per
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out, FileAccess.WRITE)
    f.store_string(JSON.stringify(rows, "", true)); f.close()
    print("OFFERS_DUMP: ", ids.size(), " ids -> ", out)
    quit(0)
