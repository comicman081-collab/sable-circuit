extends SceneTree
## Read-only art/scale diagnostic, never a navigation or integration test.
## All writes require --out inside the project .cache tree.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const CANDIDATE := "res://art_src/environments/site7_v2/_quarantine/S1_R02/attempt03/S1_R02_RAW_NATIVE.png"
var out := ""
var shots: Array[Dictionary] = []

class DoorOverlay extends Node2D:
    var origin := Vector2.ZERO
    var half := Vector2(836, 470.5)
    func _draw():
        var floor_points := PackedVector2Array()
        for p in [Vector2(169,493),Vector2(837,197),Vector2(1494,491),Vector2(836,812),Vector2(169,493)]:
            floor_points.append(origin + p - half)
        draw_polyline(floor_points, Color(0.4,0.9,0.5,0.8), 2.0)
        var a := origin + Vector2(370,636) - half
        var b := origin + Vector2(520,708) - half
        draw_line(a, b, Color(1,0.3,0.25), 4.0)
        draw_string(ThemeDB.fallback_font, a + Vector2(-60,-22), "SW clear opening ~166 px / target ~300 px", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(1,0.6,0.5))
        var expected := (b-a).normalized() * 300.0
        draw_line(a + Vector2(0,110), a + Vector2(0,110) + expected, Color(1,0.8,0.2), 3.0)
        draw_string(ThemeDB.fallback_font, a + Vector2(-15,160), "300 px reference", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(1,0.8,0.2))

func _init(): call_deferred("run")

func capture(name: String, caption: Label):
    for i in 4: await process_frame
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    assert(image.get_size() == Vector2i(1920,1080))
    var path := out + "/" + name + ".png"
    assert(image.save_png(path) == OK)
    shots.append({"path":path,"native_capture":[1920,1080],"caption":caption.text,"camera_zoom":1.0,"content_scale_size":[1920,1080]})
    print("PILOT_HOLD_CAPTURE ", path)

func run():
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
    if not out.begins_with("res://.cache/"):
        push_error("Required --out=res://.cache/... is missing")
        quit(2)
        return
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size = Vector2i(1920,1080)
    root.content_scale_size = Vector2i(1920,1080)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920,1080))
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_01"
    stage.battle_preview = true
    root.add_child(stage)
    for i in 30: await process_frame
    stage.process_mode = Node.PROCESS_MODE_DISABLED
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    var plate := art.get_room_plate("R02_CORRIDOR")
    assert(plate != null)
    for child in stage.get_children():
        if child is CanvasLayer: child.visible = false
    for group in ["m3_enemies","sable_environment_cover"]:
        for n in get_nodes_in_group(group):
            if n is CanvasItem: n.visible = false
    for p in art.get("_sprites"): p.visible = p == plate
    var cam := Camera2D.new()
    cam.zoom = Vector2.ONE
    cam.process_mode = Node.PROCESS_MODE_ALWAYS
    root.add_child(cam)
    cam.global_position = plate.global_position
    cam.make_current()
    var positions := [Vector2(-190,110),Vector2(5,170),Vector2(200,110)]
    var index := 0
    for actor in stage.squad.operators:
        actor.global_position = plate.global_position + positions[index]
        actor.velocity = Vector2.ZERO
        actor.z_as_relative = false
        actor.z_index = 3000
        index += 1
    var label_layer := CanvasLayer.new()
    root.add_child(label_layer)
    var caption := Label.new()
    caption.position = Vector2(32,20)
    caption.add_theme_font_size_override("font_size",22)
    label_layer.add_child(caption)
    caption.text = "V1 BASELINE | StoryStage01 | R02 | native 1920x1080 | 1 screen px = 1 world px"
    await capture("v1_R02_same_camera", caption)
    var source := Image.load_from_file(CANDIDATE)
    assert(source != null)
    plate.texture = ImageTexture.create_from_image(source)
    plate.scale = Vector2.ONE
    plate.material = null
    caption.text = "V2 ATTEMPT 03 - HOLD | same game scene/camera | source 1672x941 at 1:1 | isolated art preview"
    await capture("v2_R02_hold_same_camera",caption)
    var overlay := DoorOverlay.new()
    overlay.origin = plate.global_position
    overlay.z_index = 4000
    root.add_child(overlay)
    caption.text = "V2 HOLD: doorway width | manually traced clear opening | collision / joins NOT replaced"
    await capture("v2_R02_hold_door_measurement",caption)
    var file := FileAccess.open(out + "/capture_manifest.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"HOLD_DIAGNOSTIC_ONLY","source":CANDIDATE,"source_native":source.get_size(),"production_files_modified":false,"runtime_collision_replaced":false,"seam_shader_for_candidate":"disabled for original-pixel source inspection","shots":shots},"  ") + "\n")
    file.close()
    quit(0)
