extends SceneTree
## Run by the editor binary on the exported pack, never from the project folder (the release template ignores -s):
##   Godot_..._console.exe --headless --main-pack SableCircuit.pck -s <this file> -- --list=<json> --out=<json>
## with no --path and a working folder that holds no project.godot, so res:// is the pack and nothing else.
## tools/environment/build_windows_test_build.py writes the list: every file the stage holds, split into what the game
## opens as raw bytes (images, json, mp3, video) and what it loads as a resource (scenes, scripts, shaders, fonts,
## SVG files). This script asks the pack for each one, decodes a spread of the images with Image.load_from_file (the
## way the robots' and plates' art is read), builds every music stream from its raw bytes (the way DemoMusic does) and
## load()s the fonts, SVGs and .res files. It reads the pack and writes only --out. A technical check of the package:
## it approves no art, balance or play.
const SAMPLE_LIMIT := 40

func _initialize() -> void:
    var list_path := ""
    var out_path := ""
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--list="): list_path = arg.substr(7)
        elif arg.begins_with("--out="): out_path = arg.substr(6)
    if list_path.is_empty() or out_path.is_empty():
        printerr("EXPORT_AUDIT needs --list=<json> and --out=<json>")
        quit(2)
        return
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(list_path))
    if not (parsed is Dictionary):
        printerr("EXPORT_AUDIT cannot read the list: ", list_path)
        quit(2)
        return
    var list: Dictionary = parsed
    var raw_missing: Array[String] = []
    var resources_missing: Array[String] = []
    var decode_failed: Array[String] = []
    var load_failed: Array[String] = []
    var raw_paths: Array = list.get("raw", [])
    var resource_paths: Array = list.get("resources", [])
    var decode_paths: Array = list.get("decode_samples", [])
    var load_paths: Array = list.get("load_samples", [])
    var music_paths: Array = list.get("music", [])
    for path in raw_paths:
        if not FileAccess.file_exists(str(path)): raw_missing.append(str(path))
    for path in resource_paths:
        if not ResourceLoader.exists(str(path)): resources_missing.append(str(path))
    var decoded_ok := 0
    for path in decode_paths:
        var image := Image.load_from_file(str(path))
        if image == null or image.is_empty(): decode_failed.append(str(path))
        else: decoded_ok += 1
    var loaded_ok := 0
    for path in load_paths:
        var resource: Resource = load(str(path))
        if resource == null: load_failed.append(str(path))
        else: loaded_ok += 1
    var music_ok := 0
    var music_failed: Array[String] = []
    for path in music_paths:
        var stream := AudioStreamMP3.load_from_buffer(FileAccess.get_file_as_bytes(str(path)))
        if stream == null or stream.get_length() <= 0.0: music_failed.append(str(path))
        else: music_ok += 1
    var result := {
        "template_build": OS.has_feature("template"), "godot": str(Engine.get_version_info().get("string", "")),
        "project_name": str(ProjectSettings.get_setting("application/config/name", "")), "user_data_dir": OS.get_user_data_dir(),
        "raw_checked": raw_paths.size(), "raw_missing_count": raw_missing.size(), "raw_missing": raw_missing.slice(0, SAMPLE_LIMIT),
        "resources_checked": resource_paths.size(), "resources_missing_count": resources_missing.size(), "resources_missing": resources_missing.slice(0, SAMPLE_LIMIT),
        "decoded_checked": decode_paths.size(), "decoded_ok": decoded_ok, "decode_failed": decode_failed.slice(0, SAMPLE_LIMIT),
        "loaded_checked": load_paths.size(), "loaded_ok": loaded_ok, "load_failed": load_failed.slice(0, SAMPLE_LIMIT),
        "music_checked": music_paths.size(), "music_ok": music_ok, "music_failed": music_failed}
    var ok := raw_missing.is_empty() and resources_missing.is_empty() and decode_failed.is_empty() and load_failed.is_empty() and music_failed.is_empty()
    result["pass"] = ok
    DirAccess.make_dir_recursive_absolute(out_path.get_base_dir())
    var file := FileAccess.open(out_path, FileAccess.WRITE)
    if file == null:
        printerr("EXPORT_AUDIT cannot write --out: ", out_path)
        quit(4)
        return
    file.store_string(JSON.stringify(result, "  "))
    file.close()
    print("EXPORT_AUDIT ", "PASS" if ok else "FAIL", " raw ", raw_paths.size() - raw_missing.size(), "/", raw_paths.size(),
        " resources ", resource_paths.size() - resources_missing.size(), "/", resource_paths.size(), " decoded ", decoded_ok, "/", decode_paths.size(),
        " loaded ", loaded_ok, "/", load_paths.size(), " music ", music_ok, "/", music_paths.size())
    quit(0 if ok else 1)
