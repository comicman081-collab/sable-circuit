extends SceneTree

func _init() -> void:
    var args := OS.get_cmdline_user_args()
    if args.size() != 2:
        push_error("usage: -- <input.svg> <output.png>")
        quit(2)
        return
    var input_path := ProjectSettings.globalize_path(args[0]) if args[0].begins_with("res://") else args[0]
    var output_path := ProjectSettings.globalize_path(args[1]) if args[1].begins_with("res://") else args[1]
    var svg := FileAccess.get_file_as_string(input_path)
    if svg.is_empty():
        push_error("empty SVG authority: " + input_path)
        quit(3)
        return
    var image := Image.new()
    var load_error := image.load_svg_from_string(svg, 1.0)
    if load_error != OK:
        push_error("SVG load failed: %s (%d)" % [input_path, load_error])
        quit(4)
        return
    var save_error := image.save_png(output_path)
    if save_error != OK:
        push_error("PNG save failed: %s (%d)" % [output_path, save_error])
        quit(5)
        return
    print("SVG_AUTHORITY_RENDERED: %s %dx%d" % [output_path, image.get_width(), image.get_height()])
    quit()
