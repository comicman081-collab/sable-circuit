extends SceneTree
## Diagnostic: each mission's whole map in the game renderer (native 1920x1080), with
## the route drawn over it: main rooms numbered in walking order, branches dashed
## from their parent room. Actors, cover and HUD hidden. -- --out=res://.cache/...
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")

class RouteOverlay extends Node2D:
    var stage: StoryStage01
    var zoom := 0.2
    func _draw() -> void:
        var font := ThemeDB.fallback_font
        var w := 3.0 / zoom
        var main := stage.main_route
        for i in range(main.size() - 1):
            var a := Vector2(float(main[i].x), float(main[i].y))
            var b := Vector2(float(main[i + 1].x), float(main[i + 1].y))
            draw_line(a, b, Color(1.0, 0.85, 0.2, 0.9), w)
            var mid := a.lerp(b, 0.6)
            var dir := (b - a).normalized()
            draw_colored_polygon(PackedVector2Array([mid + dir * 14.0 / zoom, mid - dir * 8.0 / zoom + dir.orthogonal() * 9.0 / zoom, mid - dir * 8.0 / zoom - dir.orthogonal() * 9.0 / zoom]), Color(1.0, 0.85, 0.2, 0.95))
        for j in range(stage.optional_rooms.size()):
            var p := stage.branch_parent(j)
            var a := Vector2(float(p.x), float(p.y))
            var b := Vector2(float(stage.optional_rooms[j].x), float(stage.optional_rooms[j].y))
            draw_dashed_line(a, b, Color(0.4, 0.9, 1.0, 0.9), w, 14.0 / zoom)
            draw_circle(b, 10.0 / zoom, Color(0.4, 0.9, 1.0, 0.95))
        for i in range(main.size()):
            var c := Vector2(float(main[i].x), float(main[i].y))
            var kind := str(main[i].type)
            var color := Color(1.0, 0.3, 0.25) if kind in ["COMBAT", "ELITE", "BOSS"] else Color(1.0, 0.85, 0.2)
            draw_circle(c, 18.0 / zoom, Color(0, 0, 0, 0.8))
            draw_circle(c, 14.0 / zoom, color)
            draw_string(font, c + Vector2(22, 8) / zoom, "%d %s" % [i + 1, kind], HORIZONTAL_ALIGNMENT_LEFT, -1, int(22.0 / zoom), Color.WHITE)

func _init() -> void: call_deferred("run")

func run() -> void:
    var out := "res://.cache/structure/overview"
    var only := ""
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.trim_prefix("--out=")
        if arg.begins_with("--mission="): only = arg.trim_prefix("--mission=")
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    for number in range(1, 6):
        var mission := "MIS_CH01_%02d" % number
        if not only.is_empty() and only != mission: continue
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = mission
        stage.battle_preview = true
        root.add_child(stage)
        for i in 30: await process_frame
        var art: Site7RoomArtLayer = null
        for n in stage.get_children():
            if n is Site7RoomArtLayer: art = n
            if n is CanvasLayer: n.visible = false
        for group in ["operators", "m3_enemies", "sable_environment_cover"]:
            for n in get_nodes_in_group(group):
                if n is CanvasItem: (n as CanvasItem).visible = false
        stage.process_mode = Node.PROCESS_MODE_DISABLED
        var bounds := Rect2()
        for room: Dictionary in stage.main_route + stage.optional_rooms:
            var plate := art.get_room_plate(str(room.id))
            var half := plate.texture.get_size() * plate.scale.abs() * 0.5
            var box := Rect2(plate.global_position - half, half * 2.0)
            bounds = box if bounds.size == Vector2.ZERO else bounds.merge(box)
        var cam := Camera2D.new()
        cam.process_mode = Node.PROCESS_MODE_ALWAYS
        root.add_child(cam)
        cam.make_current()
        var zoom := minf(1280.0 / bounds.size.x, 720.0 / bounds.size.y) * 0.98
        cam.zoom = Vector2.ONE * zoom
        cam.global_position = bounds.get_center()
        for i in 6: await process_frame
        await RenderingServer.frame_post_draw
        root.get_texture().get_image().save_png(ProjectSettings.globalize_path("%s/%s_map.png" % [out, mission]))
        var overlay := RouteOverlay.new()
        overlay.stage = stage
        overlay.zoom = zoom
        overlay.z_index = 100
        stage.add_child(overlay)
        overlay.queue_redraw()
        for i in 4: await process_frame
        await RenderingServer.frame_post_draw
        root.get_texture().get_image().save_png(ProjectSettings.globalize_path("%s/%s_route.png" % [out, mission]))
        print("STRUCTURE_CAPTURE ", mission, " zoom=", zoom, " bounds=", bounds)
        cam.queue_free()
        stage.queue_free()
        for i in 4: await process_frame
    quit()
