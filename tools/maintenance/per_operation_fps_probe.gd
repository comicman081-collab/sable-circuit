extends SceneTree
## Per-operation native render survey: an instrument, not a test, and no approval of performance.
## One stage per operation, battle-preview rooms R02 / R04 / R05 (preview steps 1 / 3 / 4). Fixed actors,
## frozen enemy AI with replenished HP, real operator cooldown and reload autofire, normal hazard cycles:
## the fixture of qa/expansion_item1_review_20261003/evidence/tools/item1_perf_probe_fixed.gd without its
## item-1 only parts. The preview omits reinforcement waves, and the stage's and squad's own _process (HUD
## refresh) is off, so the numbers rank operations against each other; they are not an in-play frame rate.
## Native renderer only. Driver: tools/maintenance/per_operation_fps.py (rotates the operation order per round).
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const PREVIEW_STEPS := [1, 3, 4]
var out := "res://.cache/fps_survey/probe.json"
var tag := "survey"
var round_index := 1
var sample_seconds := 6.0
var warmup_seconds := 2.0
var max_runtime_seconds := 600.0
var screen_choice := "auto"
var shot_dir := ""
var mission_numbers: Array[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
var step_list: Array[int] = [1, 3, 4]
var stage: StoryStage01
var _fixed_enemies: Array[EnemyActor] = []
var _enemy_points: Array[Vector2] = []
var _operator_points: Array[Vector2] = []
var _drive_enabled := false
var _elapsed_start := 0
var _autofire_count := 0
var _screen_index := 0

func _init() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.substr(6)
        if arg.begins_with("--tag="): tag = arg.substr(6)
        if arg.begins_with("--round="): round_index = int(arg.substr(8))
        if arg.begins_with("--sample-seconds="): sample_seconds = float(arg.substr(17))
        if arg.begins_with("--warmup-seconds="): warmup_seconds = float(arg.substr(17))
        if arg.begins_with("--max-runtime="): max_runtime_seconds = float(arg.substr(14))
        if arg.begins_with("--screen="): screen_choice = arg.substr(9)
        if arg.begins_with("--shot-dir="): shot_dir = arg.substr(11)
        if arg.begins_with("--order="):
            mission_numbers.clear()
            for part in arg.substr(8).split(","):
                if part.is_valid_int() and int(part) >= 1 and int(part) <= 10: mission_numbers.append(int(part))
        if arg.begins_with("--steps="):
            step_list.clear()
            for part in arg.substr(8).split(","):
                if part.is_valid_int() and int(part) in PREVIEW_STEPS: step_list.append(int(part))
    call_deferred("_run")

func _run() -> void:
    if DisplayServer.get_name() == "headless":
        printerr("FPS_SURVEY requires the native renderer, not --headless")
        quit(2)
        return
    if mission_numbers.is_empty() or step_list.is_empty():
        printerr("FPS_SURVEY needs at least one operation (1-10) and one preview step (1, 3, 4)")
        quit(1)
        return
    _elapsed_start = Time.get_ticks_usec()
    create_timer(max_runtime_seconds).timeout.connect(func() -> void:
        printerr("FPS_SURVEY exceeded its own runtime bound")
        quit(3))
    _place_window()
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    Engine.max_fps = 0
    var viewport := root.get_viewport_rid()
    RenderingServer.viewport_set_measure_render_time(viewport, true)
    physics_frame.connect(_physics_tick)
    var runs: Array[Dictionary] = []
    var order_position := 0
    for number in mission_numbers:
        order_position += 1
        var load_start := Time.get_ticks_usec()
        stage = STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        stage.battle_preview = true
        root.add_child(stage)
        current_scene = stage
        await _settle_frames(6)
        var load_ms := float(Time.get_ticks_usec() - load_start) / 1000.0
        if stage.main_route.size() < 5 or stage.squad == null:
            printerr("FPS_SURVEY mission ", stage.mission_id, " did not load a five-room route and a squad")
            quit(5)
            return
        stage.set_process(false)
        stage.squad.set_process(false)
        var room_position := 0
        for step in step_list:
            room_position += 1
            _drive_enabled = false
            _cleanup_root_effects()
            var start_at := Time.get_ticks_usec()
            stage.start_battle_preview(step)
            var start_ms := float(Time.get_ticks_usec() - start_at) / 1000.0
            await _settle_frames(2)
            _prepare_fixed_fixture(step)
            _autofire_count = 0
            _drive_enabled = true
            await _wait_seconds(warmup_seconds)
            _autofire_count = 0
            var sample := await _measure(viewport)
            var room: Dictionary = stage.main_route[step]
            var shot_file := _save_shot(number, str(room.id))
            var hazard_types: PackedStringArray = []
            for node in get_nodes_in_group("zone_hazards"):
                if stage.is_ancestor_of(node): hazard_types.append(str(node.get("hazard_id")))
            sample.merge({"tag": tag, "round": round_index, "mission": stage.mission_id, "operation": number,
                "order_position": order_position, "room_position": room_position, "room": str(room.id), "step": step,
                "camera": [stage.camera.global_position.x, stage.camera.global_position.y],
                "fixed_enemy_count": _fixed_enemies.size(), "enemy_ids": _enemy_id_counts(), "hazard_types": hazard_types,
                "successful_autofire_triggers": _autofire_count, "stage_load_ms": snappedf(load_ms, 0.1),
                "start_preview_ms": snappedf(start_ms, 0.1), "shot": shot_file})
            runs.append(sample)
            print("FPS_SURVEY ", JSON.stringify({"round": round_index, "operation": number, "room": str(room.id),
                "fps": sample.fps, "p99_ms": sample.p99_ms, "max_ms": sample.max_ms, "gpu_ms": sample.gpu_ms}))
            _drive_enabled = false
        _fixed_enemies.clear()
        _enemy_points.clear()
        _operator_points.clear()
        stage.free()
        stage = null
        current_scene = null
        _cleanup_root_effects()
        await _settle_frames(2)
    var report := {"instrument": "per_operation_fps_probe", "diagnostic_only": true, "tag": tag, "round": round_index,
        "order": mission_numbers, "steps": step_list, "native_resolution": [1920, 1080], "content_scale": [1280, 720],
        "vsync": false, "screen": _screen_index, "screen_count": DisplayServer.get_screen_count(),
        "sample_seconds": sample_seconds, "warmup_seconds": warmup_seconds,
        "adapter": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(),
        "godot": str(Engine.get_version_info().get("string", "")), "template_build": OS.has_feature("template"),
        "elapsed_seconds": float(Time.get_ticks_usec() - _elapsed_start) / 1000000.0,
        "fixture": "Actual preview rows R02 / R04 / R05; actor roots fixed, enemy AI frozen and HP replenished, real operator cooldown and reload autofire, normal hazard cycles. Preview omits reinforcement waves; stage and squad _process (HUD refresh) off. Ranks operations against each other, not an in-play frame rate.",
        "runs": runs}
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var file := FileAccess.open(out, FileAccess.WRITE)
    if file == null:
        printerr("FPS_SURVEY cannot write --out: ", out)
        quit(4)
        return
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("FPS_SURVEY_COMPLETE ", tag, " round=", round_index, " samples=", runs.size())
    quit(0)

## One native frame per sampled room when "--shot-dir=<absolute folder>" is given (the export trial reads them to see
## that robots, plates and cover were drawn in a packaged build). Returns the file written, or "" when off or failed.
func _save_shot(number: int, room_id: String) -> String:
    if shot_dir.is_empty(): return ""
    DirAccess.make_dir_recursive_absolute(shot_dir)
    var path := "%s/op%02d_%s.png" % [shot_dir, number, room_id]
    var image := root.get_viewport().get_texture().get_image()
    if image == null or image.save_png(path) != OK:
        printerr("FPS_SURVEY cannot write a frame to ", path)
        return ""
    return path

## A borderless 1080p window on the second monitor when there is one ("--screen=auto"), so a long survey does
## not cover the monitor the person is working on; "--screen=primary" or an index overrides it.
func _place_window() -> void:
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    var primary := DisplayServer.get_primary_screen()
    _screen_index = primary
    if screen_choice == "auto":
        for index in range(DisplayServer.get_screen_count()):
            if index != primary:
                _screen_index = index
                break
    elif screen_choice.is_valid_int():
        _screen_index = clampi(int(screen_choice), 0, DisplayServer.get_screen_count() - 1)
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DisplayServer.window_set_position(DisplayServer.screen_get_position(_screen_index))
    root.size = Vector2i(1920, 1080)

func _prepare_fixed_fixture(step: int) -> void:
    _fixed_enemies.clear()
    _enemy_points.clear()
    _operator_points.clear()
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and stage.is_ancestor_of(node) and not node.is_queued_for_deletion():
            node.set_physics_process(false)
            node.health = node.max_health * 100.0
            _fixed_enemies.append(node)
            _enemy_points.append(node.global_position)
    for actor in stage.squad.operators:
        actor.reset_for_battle_preview()
        actor.debug_drive(Vector2.ZERO, Vector2.RIGHT)
        _operator_points.append(actor.global_position)
    var room: Dictionary = stage.main_route[step]
    stage.camera.global_position = Vector2(float(room.x), float(room.y)) + Vector2(70, -10)
    stage.camera.zoom = Vector2(1.22, 1.22)
    stage.camera.offset = Vector2.ZERO
    stage.camera.reset_smoothing()

func _enemy_id_counts() -> Dictionary:
    var counts := {}
    for enemy in _fixed_enemies:
        if is_instance_valid(enemy): counts[str(enemy.enemy_id)] = int(counts.get(str(enemy.enemy_id), 0)) + 1
    return counts

func _physics_tick() -> void:
    if not _drive_enabled or not is_instance_valid(stage): return
    for index in range(_fixed_enemies.size()):
        var enemy := _fixed_enemies[index]
        if not is_instance_valid(enemy): continue
        enemy.global_position = _enemy_points[index]
        enemy.velocity = Vector2.ZERO
        enemy.health = enemy.max_health * 100.0
        # Match the normal 60 Hz redraw cadence, including the hatch ring.
        enemy.queue_redraw()
    for index in range(stage.squad.operators.size()):
        var actor := stage.squad.operators[index]
        actor.global_position = _operator_points[index]
        actor.velocity = Vector2.ZERO
        if actor.health < actor.max_health * 0.5: actor.heal(actor.max_health)
        var target: EnemyActor = null
        var distance := INF
        for enemy in _fixed_enemies:
            if not is_instance_valid(enemy): continue
            var d := actor.global_position.distance_squared_to(enemy.global_position)
            if d < distance: target = enemy; distance = d
        var aim := (target.get_combat_aim_point() - actor.global_position).normalized() if target != null else Vector2.RIGHT
        actor.debug_drive(Vector2.ZERO, aim)
        if actor._try_fire(false): _autofire_count += 1

func _settle_frames(count: int) -> void:
    for index in range(count): await process_frame

func _wait_seconds(seconds: float) -> void:
    var start := Time.get_ticks_usec()
    while Time.get_ticks_usec() - start < int(seconds * 1000000.0): await process_frame

func _percentile(sorted_values: PackedFloat32Array, fraction: float) -> float:
    if sorted_values.is_empty(): return 0.0
    var index := clampi(int(ceil(fraction * sorted_values.size())) - 1, 0, sorted_values.size() - 1)
    return sorted_values[index]

func _measure(viewport: RID) -> Dictionary:
    var frames := 0
    var draws := 0.0
    var primitives := 0.0
    var render_cpu := 0.0
    var gpu := 0.0
    var process := 0.0
    var physics := 0.0
    var live_vfx := 0.0
    var live_projectiles := 0.0
    var peak_vfx := 0
    var frame_ms := PackedFloat32Array()
    var start := Time.get_ticks_usec()
    var last := start
    while Time.get_ticks_usec() - start < int(sample_seconds * 1000000.0):
        await process_frame
        var now := Time.get_ticks_usec()
        frame_ms.append(float(now - last) / 1000.0)
        last = now
        frames += 1
        draws += Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
        primitives += Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
        render_cpu += RenderingServer.viewport_get_measured_render_time_cpu(viewport)
        gpu += RenderingServer.viewport_get_measured_render_time_gpu(viewport)
        process += Performance.get_monitor(Performance.TIME_PROCESS)
        physics += Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)
        var vfx := 0
        var projectiles := 0
        for node in root.get_children():
            if node is PrototypeProjectile: projectiles += 1
            var script := node.get_script() as Script
            if script != null and script.resource_path.begins_with("res://scripts/vfx/"): vfx += 1
        live_vfx += vfx
        live_projectiles += projectiles
        peak_vfx = maxi(peak_vfx, vfx)
    var elapsed := float(Time.get_ticks_usec() - start) / 1000000.0
    var sorted := frame_ms.duplicate()
    sorted.sort()
    return {"frames": frames, "elapsed_seconds": elapsed, "fps": snappedf(frames / elapsed, 0.01),
        "frame_ms": snappedf(elapsed * 1000.0 / frames, 0.001), "p50_ms": snappedf(_percentile(sorted, 0.5), 0.001),
        "p95_ms": snappedf(_percentile(sorted, 0.95), 0.001), "p99_ms": snappedf(_percentile(sorted, 0.99), 0.001),
        "max_ms": snappedf(sorted[sorted.size() - 1] if not sorted.is_empty() else 0.0, 0.001),
        "draw_calls": snappedf(draws / frames, 0.1), "primitives": snappedf(primitives / frames, 0.1),
        "render_cpu_ms": snappedf(render_cpu / frames, 0.001), "gpu_ms": snappedf(gpu / frames, 0.001),
        "process_ms": snappedf(process * 1000.0 / frames, 0.001), "physics_ms": snappedf(physics * 1000.0 / frames, 0.001),
        "live_vfx_mean": snappedf(live_vfx / frames, 0.1), "live_vfx_peak": peak_vfx,
        "live_projectiles_mean": snappedf(live_projectiles / frames, 0.1),
        "texture_mem_mb": snappedf(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0, 0.1),
        "video_mem_mb": snappedf(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0, 0.1),
        "static_mem_mb": snappedf(Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0, 0.1),
        "node_count": int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT))}

func _cleanup_root_effects() -> void:
    for node in root.get_children():
        if node is PrototypeProjectile:
            node.queue_free()
            continue
        var script := node.get_script() as Script
        if script != null and script.resource_path.begins_with("res://scripts/vfx/"): node.queue_free()
