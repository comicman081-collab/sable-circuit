extends SceneTree
## Claude review helper (item 2): dump RunContract.build() for a list of run ids as canonical JSON.
## usage (from a snapshot): golden_dump.gd -- --ids=res://.cache/ids.json --out=res://.cache/out/build_<name>.json
func _init() -> void:
    var ids_path := "res://.cache/ids.json"
    var out := "res://.cache/out/build_dump.json"
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--ids="): ids_path = a.trim_prefix("--ids=")
        if a.begins_with("--out="): out = a.trim_prefix("--out=")
    var ids: Array = JSON.parse_string(FileAccess.get_file_as_string(ids_path))
    var rows := {}
    for id in ids:
        rows[str(id)] = JSON.stringify(RunContract.build(str(id)), "", true)
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out, FileAccess.WRITE)
    f.store_string(JSON.stringify(rows, "", true)); f.close()
    print("GOLDEN_DUMP: ", ids.size(), " ids -> ", out)
    quit(0)
