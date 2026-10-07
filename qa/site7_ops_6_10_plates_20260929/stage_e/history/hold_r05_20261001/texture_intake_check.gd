extends SceneTree

func _initialize() -> void:
	var rows: Array = []
	var passed := true
	for i in range(1, 5):
		var plate := "S10_R%02d" % i
		var path := "res://assets/environments/site7_v2/stage10/%s/%s_GAME.png" % [plate, plate]
		var expected := Vector2i(1774, 887) if i == 4 else Vector2i(1672, 941)
		var source := Image.load_from_file(path)
		var texture := load(path) as Texture2D
		var valid := source != null and texture != null
		var identical := false
		if valid:
			var imported := texture.get_image()
			valid = imported != null and source.get_size() == expected and Vector2i(texture.get_size()) == expected
			if valid:
				source.convert(Image.FORMAT_RGB8)
				imported.convert(Image.FORMAT_RGB8)
				identical = source.get_data() == imported.get_data()
		valid = valid and identical
		passed = passed and valid
		rows.append({"plate": plate, "expected_native_size": [expected.x, expected.y], "resource_loaded": texture != null, "imported_pixels_identical_to_GAME": identical, "pass": valid})
	var output := FileAccess.open("res://.cache/diag/site7_ops_e/hold_r05_20261001/texture_intake_check.json", FileAccess.WRITE)
	output.store_string(JSON.stringify({"status": "PASS" if passed else "FAIL", "scope": "four imported GAME textures only; no gameplay claim", "rows": rows}, "  "))
	print("S10_GAME_INTAKE_CHECK ", "PASS" if passed else "FAIL", " 4 textures")
	quit(0 if passed else 1)
