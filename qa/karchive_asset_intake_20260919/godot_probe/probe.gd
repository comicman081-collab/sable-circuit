extends SceneTree

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var rows: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var results: Array = []
	var failed := false
	for row: Dictionary in rows:
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		var code := document.append_from_file(row.local_path, state)
		var result := {"id": row.id, "source_sha256": row.sha256, "append_error": code, "native_version": Engine.get_version_info().string}
		if code == OK:
			var node := document.generate_scene(state)
			result["scene_generated"] = node != null
			result["meshes"] = state.get_meshes().size()
			result["materials"] = state.get_materials().size()
			result["animations"] = state.get_animations().size()
			if node != null:
				node.free()
			else:
				failed = true
		else:
			failed = true
		results.append(result)
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	output.store_string(JSON.stringify({"scope": "12 selected GLBs, importer and scene construction only; no gameplay/art/performance approval", "status": "FAIL" if failed else "PASS_IMPORT_ONLY", "results": results}, "\t"))
	output.close()
	print("KARCHIVE_GODOT_IMPORT_RESULT ", "FAIL" if failed else "PASS_IMPORT_ONLY", " count=", results.size())
	quit(1 if failed else 0)
