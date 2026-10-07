extends SceneTree
## Native same-camera v1/v2 comparison inside StoryStage01. Never changes art on disk.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var out := ""
var mission := ""
var room_id := ""
var v1 := ""
var v1_scale := 1.0
var shots: Array = []
func _init() -> void: call_deferred("run")
func shot(name: String) -> void:
    for i in 4: await process_frame
    await RenderingServer.frame_post_draw
    var im := root.get_texture().get_image()
    assert(im.get_size() == Vector2i(1920,1080))
    assert(im.save_png(out + "/" + name + ".png") == OK)
    shots.append({"file":name + ".png","native_capture":[1920,1080],"camera_zoom":1.0})
    print("STAGE3_COMPARE_CAPTURE ", mission, " ", name)
func run() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out=arg.trim_prefix("--out=")
        if arg.begins_with("--mission="): mission=arg.trim_prefix("--mission=")
        if arg.begins_with("--room="): room_id=arg.trim_prefix("--room=")
        if arg.begins_with("--v1="): v1=arg.trim_prefix("--v1=")
        if arg.begins_with("--v1-scale="): v1_scale=arg.trim_prefix("--v1-scale=").to_float()
    if not out.begins_with("res://.cache/") or not v1.begins_with("res://assets/") or mission.is_empty() or room_id.is_empty():
        quit(2)
        return
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size=Vector2i(1920,1080)
    root.content_scale_size=root.size
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(root.size)
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id=mission
    stage.battle_preview=true
    root.add_child(stage)
    for i in 30: await process_frame
    stage.process_mode=Node.PROCESS_MODE_DISABLED
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    var plate := art.get_room_plate(room_id)
    assert(plate != null)
    var cam := Camera2D.new()
    cam.process_mode=Node.PROCESS_MODE_ALWAYS
    cam.zoom=Vector2.ONE
    root.add_child(cam)
    cam.global_position=plate.global_position
    cam.make_current()
    await shot("v2_game_same_camera")
    for child in stage.get_children():
        if child is CanvasLayer: child.visible=false
    for group in ["m3_enemies","sable_environment_cover"]:
        for n in get_nodes_in_group(group):
            if n is CanvasItem: (n as CanvasItem).visible=false
    var positions := [Vector2(-190,110),Vector2(5,170),Vector2(200,110)]
    for i in range(stage.squad.operators.size()):
        var actor=stage.squad.operators[i]
        actor.global_position=plate.global_position+positions[i]
        actor.velocity=Vector2.ZERO
        actor.z_as_relative=false
        actor.z_index=3000
    for p in art.get("_sprites"):
        p.visible=p==plate
    for seal in get_nodes_in_group("site7_sealed_bulkhead"):
        (seal as CanvasItem).visible=str(seal.get_meta("room_id", ""))==room_id
    await shot("v2_isolated_same_camera")
    for seal in get_nodes_in_group("site7_sealed_bulkhead"):
        (seal as CanvasItem).visible=false
    plate.texture=ImageTexture.create_from_image(Image.load_from_file(v1))
    plate.scale=Vector2.ONE*v1_scale
    plate.material=null
    await shot("v1_isolated_same_camera")
    var f=FileAccess.open(out+"/capture_manifest.json",FileAccess.WRITE)
    f.store_string(JSON.stringify({"scene":"StoryStage01","mission":mission,"room":room_id,"v1_asset":v1,"v1_scale":v1_scale,"v2_scale":1.0,"mode":"native game fixture; same camera and actor positions; no human play approval","shots":shots},"  "))
    f.close()
    quit(0)
