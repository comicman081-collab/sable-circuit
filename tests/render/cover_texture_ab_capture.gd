extends SceneTree
## A/B frame for the reduced cover textures: each kArchive prop drawn with the full
## 1920x1080 texture (top row) and with the cropped half-size GPU copy (bottom row) at
## the in-game display width and camera zoom, in one native 1920x1080 frame. Run windowed:
##   Godot --path . -s res://tests/render/cover_texture_ab_capture.gd -- --out=res://<folder>

const PROP := preload("res://scripts/missions/site7_environment_prop.gd")
const PROPS := preload("res://scripts/missions/site7_environment_props.gd")
const CONFIG := "res://data/visual/site7_environment_props.json"
const TestOutput := preload("res://tests/support/test_output.gd")
const WIDTHS := {"barrier": 216.0, "cabinet": 130.0, "crate": 110.0, "generator": 124.0}
# The normal squad camera zoom; the project's 1280x720 canvas scaling adds the 1.5x to 1080p.
const ZOOM := 1.22

var out_dir := TestOutput.path("res://.cache/tests/cover_texture_ab")

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    root.size = Vector2i(1920, 1080)
    if DisplayServer.get_name() != "headless":
        DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))
    var backdrop := ColorRect.new()
    backdrop.color = Color("1a2630")
    backdrop.size = Vector2(4000, 3000)
    backdrop.position = Vector2(-2000, -1500)
    root.add_child(backdrop)
    var camera := Camera2D.new()
    camera.zoom = Vector2.ONE * ZOOM
    root.add_child(camera)
    camera.make_current()
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
    var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(config.spec)))
    var column := 0
    var report := {}
    for id in ["barrier", "cabinet", "crate", "generator"]:
        var asset: Dictionary = spec.props[id]
        var image := Image.new()
        image.load_png_from_buffer(FileAccess.get_file_as_bytes(str(asset.texture)))
        var full := image.duplicate() as Image
        full.generate_mipmaps()
        var reduced := PROPS.reduced_prop_texture(image)
        var x := -390.0 + column * 250.0
        _prop(ImageTexture.create_from_image(full), image, asset, WIDTHS[id], Rect2i(), Vector2i(), Vector2(x, -40))
        _prop(reduced.texture, reduced.alpha, asset, WIDTHS[id], reduced.region, reduced.source_size, Vector2(x, 230))
        report[id] = {"full_texture": [image.get_width(), image.get_height()], "reduced_texture": [reduced.texture.get_width(), reduced.texture.get_height()], "region": [reduced.region.position.x, reduced.region.position.y, reduced.region.size.x, reduced.region.size.y]}
        column += 1
    for i in range(4): await process_frame
    await RenderingServer.frame_post_draw
    var frame := root.get_texture().get_image()
    frame.save_png(ProjectSettings.globalize_path(out_dir.path_join("cover_full_vs_reduced_1080p.png")))
    var file := FileAccess.open(out_dir.path_join("cover_ab_layout.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify({"frame": [frame.get_width(), frame.get_height()], "zoom": ZOOM, "screen_px_per_world": ZOOM * 1.5, "row_offset_world": 270.0, "props": report}, "  "))
    file.close()
    print("COVER_TEXTURE_AB_CAPTURE: PASS ", frame.get_size())
    quit(0 if frame.get_size() == Vector2i(1920, 1080) else 1)

func _prop(texture: Texture2D, alpha: Image, asset: Dictionary, width: float, region: Rect2i, source_size: Vector2i, at: Vector2) -> void:
    var prop := PROP.new() as StaticBody2D
    root.add_child(prop)
    prop.global_position = at
    prop.configure(texture, alpha, asset, width, region, source_size)
    prop.set_active(true)
