extends SceneTree
## Cover sliding under four body setups, same operator, same props, same inputs:
## grounded as shipped, grounded with platform_floor_layers 0 / on-leave DO_NOTHING,
## the same with floor_snap_length 0, and floating. The operator walks at each active
## cover prop of a room from 16 sides, each straight on and 20 and 40 degrees off, for
## 75 ticks; end points are compared.
## Run with --fixed-fps 60 so every frame is one physics tick.
## qa/ is .gdignore'd: copy this file to .cache/probe/ and run
## godot --headless --fixed-fps 60 --path . -s res://.cache/probe/cover_slide_probe.gd -- --mission=MIS_CH01_02 --out=res://.cache/cover_slide_02.json
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
## The shipped setup runs twice, first and last, to show the run-to-run noise floor.
const MODES := ["grounded_shipped", "grounded_no_platform", "grounded_no_platform_no_snap", "floating", "grounded_shipped_repeat"]
var stage: StoryStage01
var lead: OperatorActor
var rows: Array[Dictionary] = []

func _init() -> void: call_deferred("run")

func settle(count: int) -> void:
    for _i in range(count):
        await physics_frame
        await process_frame

func configure(mode: String) -> void:
    lead.motion_mode = CharacterBody2D.MOTION_MODE_FLOATING if mode == "floating" else CharacterBody2D.MOTION_MODE_GROUNDED
    var shipped := mode.begins_with("grounded_shipped")
    lead.platform_floor_layers = 0xFFFFFFFF if shipped else 0
    lead.platform_on_leave = CharacterBody2D.PLATFORM_ON_LEAVE_ADD_VELOCITY if shipped else CharacterBody2D.PLATFORM_ON_LEAVE_DO_NOTHING
    lead.floor_snap_length = 0.0 if mode.ends_with("no_snap") else 1.0

func run() -> void:
    var mission := "MIS_CH01_02"
    var out := "res://.cache/cover_slide.json"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--mission="): mission = arg.get_slice("=", 1)
        if arg.begins_with("--out="): out = arg.get_slice("=", 1)
    stage = STAGE.instantiate() as StoryStage01
    stage.mission_id = mission
    stage.battle_preview = true
    root.add_child(stage)
    await settle(10)
    var summary := {}
    for step in [1, 3, 4]:
        stage.start_battle_preview(step)
        await settle(4)
        stage.set_process(false); stage.set_physics_process(false)
        stage.squad.set_process(false); stage.squad.set_physics_process(false)
        stage._clear_hazards()
        for node in get_nodes_in_group("m3_enemies"): node.queue_free()
        lead = stage.squad.get_active_operator()
        for member in stage.squad.operators:
            if member != lead: member.set_physics_process(false); member.collision_layer = 0
        await settle(2)
        var room_center := Vector2(float(stage.main_route[stage.current_step].x), float(stage.main_route[stage.current_step].y))
        for cover in get_nodes_in_group("sable_environment_cover"):
            if not cover.active or not cover.is_visible_in_tree() or cover.global_position.distance_to(room_center) > 900.0: continue
            var box := Rect2(cover.to_global(cover.ground[0]), Vector2.ZERO)
            for point in cover.ground: box = box.expand(cover.to_global(point))
            var radius := box.size.length() * 0.5 + 40.0
            for side in range(16):
                var out_dir := Vector2.from_angle(side * TAU / 16.0)
                var start := box.get_center() + out_dir * radius + Vector2(0, 18)
                for skew in [0.0, 20.0, 40.0]:
                    var heading := (-out_dir).rotated(deg_to_rad(skew))
                    if not stage.battlefield.segment_walkable(start, start + heading * 200.0): continue
                    var ends := {}
                    for mode in MODES:
                        configure(mode)
                        lead.global_position = start
                        lead.velocity = Vector2.ZERO
                        lead.debug_drive(Vector2.ZERO, heading)
                        await settle(3)
                        lead.debug_drive(heading, heading)
                        var path := 0.0
                        var last := lead.global_position
                        for _tick in range(75):
                            await physics_frame
                            path += lead.global_position.distance_to(last)
                            last = lead.global_position
                        lead.debug_drive(Vector2.ZERO, heading)
                        ends[mode] = {"end": lead.global_position, "path": path}
                    var base: Vector2 = ends.grounded_shipped.end
                    rows.append({"step": step, "cover": str(cover.name), "side": side, "skew": skew,
                        "path_px": {"grounded_shipped": snappedf(ends.grounded_shipped.path, 0.01), "grounded_no_platform": snappedf(ends.grounded_no_platform.path, 0.01), "floating": snappedf(ends.floating.path, 0.01)},
                        "repeat_vs_shipped_px": snappedf(base.distance_to(ends.grounded_shipped_repeat.end), 0.001),
                        "no_platform_vs_shipped_px": snappedf(base.distance_to(ends.grounded_no_platform.end), 0.001),
                        "no_snap_vs_shipped_px": snappedf(base.distance_to(ends.grounded_no_platform_no_snap.end), 0.001),
                        "floating_vs_shipped_px": snappedf(base.distance_to(ends.floating.end), 0.01)})
    var identical := 0
    var repeat_identical := 0
    var no_snap_diff := 0
    var no_snap_max := 0.0
    var floating_diff := 0
    var floating_max := 0.0
    var path_ratio := []
    for row in rows:
        if row.no_platform_vs_shipped_px == 0.0: identical += 1
        if row.repeat_vs_shipped_px == 0.0: repeat_identical += 1
        if row.no_snap_vs_shipped_px > 0.01: no_snap_diff += 1
        no_snap_max = maxf(no_snap_max, row.no_snap_vs_shipped_px)
        if row.floating_vs_shipped_px > 1.0: floating_diff += 1
        floating_max = maxf(floating_max, row.floating_vs_shipped_px)
        if row.path_px.grounded_shipped > 1.0: path_ratio.append(row.path_px.floating / row.path_px.grounded_shipped)
    path_ratio.sort()
    summary = {"mission": mission, "approaches": rows.size(), "shipped_repeat_identical": repeat_identical, "no_platform_identical_to_shipped": identical,
        "no_snap_differs": no_snap_diff, "no_snap_max_end_difference_px": no_snap_max,
        "floating_differs_over_1px": floating_diff, "floating_max_end_difference_px": floating_max,
        "floating_path_ratio_min_median_max": [path_ratio[0], path_ratio[path_ratio.size() / 2], path_ratio[-1]] if not path_ratio.is_empty() else []}
    var file := FileAccess.open(out, FileAccess.WRITE)
    file.store_string(JSON.stringify({"summary": summary, "rows": rows}, "  "))
    file.close()
    print("COVER_SLIDE " + JSON.stringify(summary))
    quit(0)
