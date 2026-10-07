extends SceneTree
## Native 1920x1080 walk-graph review: every room/connector plate of a mission
## with the live floor polygons, route bridges, cover footprints, objective
## radii and spawns drawn over the painted art. Review evidence only.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var out := "res://.cache/site7_v2_pilot/walk_graph"
var stage: StoryStage01

class Overlay extends Node2D:
    var bf: Node
    var stage: Node
    var spawns: Array = []
    func _draw() -> void:
        var polys: Array = bf.get("_world_polygons")
        for poly: PackedVector2Array in polys:
            draw_colored_polygon(poly, Color(0.1, 1.0, 0.3, 0.16))
            var closed := poly.duplicate(); closed.append(poly[0])
            draw_polyline(closed, Color(0.2, 1.0, 0.35, 0.95), 4.0)
        var segs: Array = bf.get("_route_segments")
        var widths: PackedFloat32Array = bf.get("_route_half_widths")
        for i in range(segs.size()):
            var seg: PackedVector2Array = segs[i]
            var w := widths[i]
            draw_line(seg[0], seg[1], Color(0.3, 0.6, 1.0, 0.25), w * 2.0); draw_circle(seg[0], w, Color(0.3, 0.6, 1.0, 0.25)); draw_circle(seg[1], w, Color(0.3, 0.6, 1.0, 0.25))
            draw_line(seg[0], seg[1], Color(0.3, 0.7, 1.0, 0.9), 3.0)
        for cover in stage.get_tree().get_nodes_in_group("sable_environment_cover"):
            var g: PackedVector2Array = cover.ground
            var w := PackedVector2Array()
            for p in g: w.append(cover.to_global(p))
            draw_colored_polygon(w, Color(1, 0.2, 0.2, 0.45))
        for room: Dictionary in stage.main_route + stage.optional_rooms:
            var c := Vector2(float(room.x), float(room.y))
            draw_circle(c, 18, Color(1, 1, 0, 0.9))
            draw_arc(c, 175, 0, TAU, 64, Color(1, 1, 0, 0.5), 3.0)
            draw_string(ThemeDB.fallback_font, c + Vector2(24, -24), str(room.id), HORIZONTAL_ALIGNMENT_LEFT, -1, 48, Color(1, 1, 0))
        for s in spawns:
            draw_circle(s.p, 22, s.c)

func _init() -> void: call_deferred("run")

func run() -> void:
    var mission := "MIS_CH01_01"
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--mission="): mission = a.get_slice("=", 1)
        if a.begins_with("--out="): out = a.trim_prefix("--out=")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    stage = STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    root.add_child(stage)
    for i in range(20): await process_frame
    var bf: Node = stage.battlefield
    print("JOIN_GAPS ", JSON.stringify(bf.join_gaps))
    for layer_name in ["HUD", "DemoControls"]:
        var layer := stage.get_node_or_null(layer_name)
        if layer is CanvasLayer: (layer as CanvasLayer).visible = false
    for child in stage.get_children():
        if child is CanvasLayer: (child as CanvasLayer).visible = false
    for actor in stage.squad.operators: actor.visible = false
    var overlay := Overlay.new()
    overlay.bf = bf
    overlay.stage = stage
    overlay.z_as_relative = false
    overlay.z_index = 4000
    # Enemy spawn preview for every combat room (walkable = cyan, not = red).
    for room: Dictionary in stage.main_route:
        var enc: Array = room.get("encounter", [])
        if enc.is_empty(): continue
        bf.call("begin_encounter", room)
        var count := enc.size()
        for wave in room.get("reinforcements", []): count = maxi(count, (wave as Array).size())
        for i in range(count):
            var p: Vector2 = bf.call("enemy_spawn", i)
            overlay.spawns.append({"p": p, "c": Color(0, 1, 1, 0.9) if bf.is_walkable(p) else Color(1, 0, 0, 1)})
        for i in range(3):
            var s: Vector2 = bf.call("squad_spawn", i)
            overlay.spawns.append({"p": s, "c": Color(1, 0.5, 0, 0.9)})
        bf.call("release")
    stage.add_child(overlay)
    var cam := Camera2D.new()
    stage.add_child(cam)
    cam.make_current()
    var art := stage.get_node("RoomArtLayer")
    var targets: Array = []
    for sprite in art.get("_sprites"):
        targets.append(sprite)
    var index := 0
    for sprite: Sprite2D in targets:
        var half := sprite.texture.get_size() * sprite.scale.abs() * 0.5
        var extent := Vector2(absf(half.x), absf(half.y))
        if absf(sprite.rotation) > 0.1: extent = Vector2(extent.y, extent.x)
        cam.global_position = sprite.global_position
        var zoom := minf(1280.0 / (extent.x * 2.0 + 120.0), 720.0 / (extent.y * 2.0 + 120.0))
        cam.zoom = Vector2.ONE * zoom
        overlay.queue_redraw()
        for f in range(3): await process_frame
        await RenderingServer.frame_post_draw
        var img := root.get_texture().get_image()
        var name := "%s_%02d_%s" % [mission.right(2), index, str(sprite.name)]
        img.save_png(out + "/" + name + ".png")
        print("WALK_SHOT ", name, " room=", sprite.get_meta("room_id", ""), " pos=", sprite.global_position)
        index += 1
    # Whole-mission overview.
    var bounds: Rect2 = art.get("_world_bounds")
    cam.global_position = bounds.get_center()
    cam.zoom = Vector2.ONE * minf(1280.0 / bounds.size.x, 720.0 / bounds.size.y)
    for f in range(3): await process_frame
    await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png(out + "/%s_overview.png" % mission.right(2))
    quit(0)
