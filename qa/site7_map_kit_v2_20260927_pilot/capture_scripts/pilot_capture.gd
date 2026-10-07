extends SceneTree
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var out := ""
var shots: Array = []
func _init(): call_deferred("run")
func shot(name: String):
    for i in 4: await process_frame
    await RenderingServer.frame_post_draw
    var im := root.get_texture().get_image()
    assert(im.get_size() == Vector2i(1920,1080))
    assert(im.save_png(out + "/" + name + ".png") == OK)
    shots.append({"file":name + ".png","native_capture":[1920,1080],"world_px_per_screen_px":1.0})
    print("PILOT_CAPTURE ", name)
func run():
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out=arg.trim_prefix("--out=")
    if not out.begins_with("res://.cache/"): quit(2);return
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size=Vector2i(1920,1080)
    root.content_scale_size=root.size
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(root.size)
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id="MIS_CH01_01"
    stage.battle_preview=true
    root.add_child(stage)
    for i in 30: await process_frame
    stage.start_battle_preview(1)
    for i in 12: await process_frame
    stage.process_mode=Node.PROCESS_MODE_DISABLED
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    var plate := art.get_room_plate("R02_CORRIDOR")
    var cam := Camera2D.new()
    cam.process_mode=Node.PROCESS_MODE_ALWAYS
    cam.zoom=Vector2.ONE
    root.add_child(cam)
    cam.global_position=plate.global_position
    cam.make_current()
    await shot("R02_game_1to1")
    for child in stage.get_children():
        if child is CanvasLayer: child.visible=false
    for n in get_nodes_in_group("m3_enemies"):
        if n is CanvasItem:n.visible=false
    for n in get_nodes_in_group("sable_environment_cover"):
        if n is CanvasItem:n.visible=false
    var positions := [Vector2(-190,110),Vector2(5,170),Vector2(200,110)]
    for i in range(stage.squad.operators.size()):
        var actor=stage.squad.operators[i]
        actor.global_position=plate.global_position+positions[i]
        actor.velocity=Vector2.ZERO
        actor.z_as_relative=false
        actor.z_index=3000
    await shot("R02_v2_same_camera")
    for p in art.get("_sprites"):p.visible=p==plate
    await shot("R02_v2_isolated_1to1")
    plate.texture=ImageTexture.create_from_image(Image.load_from_file("res://assets/environments/site7/decon_corridor/02_DECON_CORRIDOR_CONTINUITY.png"))
    plate.scale=Vector2.ONE*.88
    plate.material=null
    await shot("R02_v1_isolated_same_camera")
    var f=FileAccess.open(out+"/capture_manifest.json",FileAccess.WRITE)
    f.store_string(JSON.stringify({"scene":"StoryStage01","mission":"MIS_CH01_01","mode":"native game battle-preview fixture, paused after 12 frames; no human play approval","shots":shots},"  "))
    f.close()
    quit(0)
