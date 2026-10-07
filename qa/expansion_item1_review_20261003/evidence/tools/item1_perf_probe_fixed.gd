extends SceneTree
## Cache-only native render diagnostic. The identical probe runs in each project
## without swapping their runtime bytes. Fixed actors, real weapon cooldown and
## animated room hazards; this is not a playthrough or a balance measurement.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var out := "res://.cache/diag/expansion_item1_20261003/perf/probe.json"
var tag := "unlabelled"
var round_index := 1
var sample_seconds := 7.0
var warmup_seconds := 2.0
var max_runtime_seconds := 150.0
var mission_numbers: Array[int] = [6, 7, 8, 9, 10]
var stage: StoryStage01
var _fixed_enemies: Array[EnemyActor] = []
var _enemy_points: Array[Vector2] = []
var _operator_points: Array[Vector2] = []
var _drive_enabled := false
var _elapsed_start := 0
var _autofire_count := 0

func _init() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): out = arg.substr(6)
        if arg.begins_with("--tag="): tag = arg.substr(6)
        if arg.begins_with("--round="): round_index = int(arg.substr(8))
        if arg.begins_with("--sample-seconds="): sample_seconds = float(arg.substr(17))
        if arg.begins_with("--warmup-seconds="): warmup_seconds = float(arg.substr(17))
        if arg.begins_with("--max-runtime="): max_runtime_seconds = float(arg.substr(14))
    call_deferred("_run")

func _run() -> void:
    if DisplayServer.get_name() == "headless":
        printerr("PERF_PROBE requires the native renderer, not --headless")
        quit(2)
        return
    _elapsed_start = Time.get_ticks_usec()
    create_timer(max_runtime_seconds).timeout.connect(func() -> void:
        printerr("PERF_PROBE exceeded its own runtime bound")
        quit(3))
    root.size = Vector2i(1920, 1080)
    root.content_scale_size = Vector2i(1280, 720)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920, 1080))
    DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    Engine.max_fps = 0
    var viewport := root.get_viewport_rid()
    RenderingServer.viewport_set_measure_render_time(viewport, true)
    physics_frame.connect(_physics_tick)
    var runs: Array[Dictionary] = []
    for number in mission_numbers:
        stage = STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        stage.battle_preview = true
        root.add_child(stage)
        current_scene = stage
        await _settle_frames(6)
        stage.set_process(false)
        stage.squad.set_process(false)
        # Room order also rotates to spread scene-loading drift across R02/R04.
        var steps: Array[int] = []
        steps.assign([1, 3] if round_index % 2 == 1 else [3, 1])
        for step in steps:
            _drive_enabled = false
            _cleanup_root_effects()
            stage.start_battle_preview(step)
            await _settle_frames(2)
            _prepare_fixed_fixture(number, step)
            _autofire_count = 0
            _drive_enabled = true
            await _wait_seconds(warmup_seconds)
            _autofire_count = 0
            var sample := await _measure(viewport)
            var room: Dictionary = stage.main_route[step]
            var hazard_types: PackedStringArray = []
            for node in get_nodes_in_group("zone_hazards"):
                if stage.is_ancestor_of(node): hazard_types.append(str(node.get("hazard_id")))
            sample.merge({"version": tag, "round": round_index, "mission": stage.mission_id,
                "room": str(room.id), "step": step, "camera": [stage.camera.global_position.x, stage.camera.global_position.y],
                "fixed_enemy_count": _fixed_enemies.size(), "hazard_types": hazard_types,
                "successful_autofire_triggers": _autofire_count, "brood_parent_destroyed_fixture": number == 6 and step == 3})
            runs.append(sample)
            print("ITEM1_PERF ", JSON.stringify(sample))
            _drive_enabled = false
        _fixed_enemies.clear()
        _enemy_points.clear()
        _operator_points.clear()
        stage.free()
        stage = null
        current_scene = null
        _cleanup_root_effects()
        await _settle_frames(2)
    var report := {"diagnostic_only": true, "version": tag, "round": round_index,
        "native_resolution": [1920, 1080], "content_scale": [1280, 720], "vsync": false,
        "sample_seconds": sample_seconds, "warmup_seconds": warmup_seconds,
        "adapter": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(),
        "elapsed_seconds": float(Time.get_ticks_usec() - _elapsed_start) / 1000000.0,
        "fixture": "Actual R02/R04 preview rows; actor roots fixed, enemy AI frozen and HP replenished, real operator cooldown/reload autofire, normal hazard cycles. Op6 R04 destroys MORTAR in both arms before warmup: the new arm keeps its first-generation hatchling draw state frozen. Preview omits reinforcement waves.",
        "runs": runs}
    var file := FileAccess.open(out, FileAccess.WRITE)
    if file == null:
        printerr("PERF_PROBE cannot write --out: ", out)
        quit(4)
        return
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("ITEM1_PERF_COMPLETE ", tag, " round=", round_index, " samples=", runs.size())
    quit(0)

func _prepare_fixed_fixture(number: int, step: int) -> void:
    # A public damage call triggers each project's own existing defeat logic.
    # No new-class field or affix implementation is referenced by this probe.
    if number == 6 and step == 3:
        for node in get_nodes_in_group("m3_enemies"):
            if node is EnemyActor and node.get_parent() == stage and node.enemy_id == "ENM_SITE7_MORTAR_01":
                node.apply_damage(99999.0)
    _fixed_enemies.clear()
    _enemy_points.clear()
    _operator_points.clear()
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and node.get_parent() == stage and not node.is_queued_for_deletion():
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
    var start := Time.get_ticks_usec()
    while Time.get_ticks_usec() - start < int(sample_seconds * 1000000.0):
        await process_frame
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
    return {"frames": frames, "elapsed_seconds": elapsed, "fps": snappedf(frames / elapsed, 0.01),
        "frame_ms": snappedf(elapsed * 1000.0 / frames, 0.001), "draw_calls": snappedf(draws / frames, 0.1),
        "primitives": snappedf(primitives / frames, 0.1), "render_cpu_ms": snappedf(render_cpu / frames, 0.001),
        "gpu_ms": snappedf(gpu / frames, 0.001), "process_ms": snappedf(process * 1000.0 / frames, 0.001),
        "physics_ms": snappedf(physics * 1000.0 / frames, 0.001), "live_vfx_mean": snappedf(live_vfx / frames, 0.1),
        "live_vfx_peak": peak_vfx, "live_projectiles_mean": snappedf(live_projectiles / frames, 0.1)}

func _cleanup_root_effects() -> void:
    for node in root.get_children():
        if node is PrototypeProjectile:
            node.queue_free()
            continue
        var script := node.get_script() as Script
        if script != null and script.resource_path.begins_with("res://scripts/vfx/"): node.queue_free()
