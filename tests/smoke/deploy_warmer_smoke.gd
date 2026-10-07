extends SceneTree
## DEPLOY does not stall on loading (DeployWarmer). The title screen queues the next
## mission's robot art; the briefing screen adds its room plates, cover props and the
## squad's atlases; GameFlow pumps the queue on worker threads. Checks that the threaded
## robot views equal a main-thread decode, that the stage's warm is then only cache hits,
## that the deploy takes every prepared plate and atlas (nothing left behind), that backing
## out of a briefing frees them, the web one-job-per-frame path, and finish() mid-flight.
## Campaign persistence off: the player's save is never read or written. Writes no files.

const FLOW := preload("res://scenes/bootstrap/GameFlow.tscn")
const Warmer := preload("res://scripts/core/deploy_warmer.gd")
const MachineSprite := preload("res://scripts/animation/site7_machine_sprite.gd")
const Props := preload("res://scripts/missions/site7_environment_props.gd")

var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    for mission in ["MIS_CH01_01", "MIS_CH01_02", "MIS_CH01_03"]:
        _check(not Warmer.mission_enemy_ids(mission).is_empty(), mission + " lists its robots")
    var first := Warmer.mission_enemy_ids("MIS_CH01_01")
    _check(first.has("ENM_SITE7_DRONE_01") and first.has("BOSS_SITE7_ANCHOR_01"), "operation 1 lists drone and anchor")
    _check(Warmer.mission_enemy_ids("MIS_CH01_02").has("BOSS_SITE7_RELAY_01"), "operation 2 queues relay boss art")
    _check(Warmer.mission_enemy_ids("MIS_CH01_03").has("BOSS_SITE7_REMNANT_01"), "operation 3 queues remnant boss art")
    # Held-back operations: their registered boss is already in the queue list the day they open.
    for pair in [["MIS_CH01_06", "BOSS_SITE7_AERATOR_01"], ["MIS_CH01_07", "BOSS_SITE7_CRYO_01"], ["MIS_CH01_08", "BOSS_SITE7_GANTRY_01"],
            ["MIS_CH01_09", "BOSS_SITE7_ARCHIVE_01"], ["MIS_CH01_10", "BOSS_SITE7_ORIGIN_01"]]:
        var held_back := Warmer.mission_enemy_ids(pair[0])
        _check(held_back.has(pair[1]) and not held_back.has("BOSS_SITE7_CARRIER_01"), "%s lists its own registered boss, not a placeholder" % pair[0])
    var first_views := _views_of(first)
    _check(first_views.size() >= 9, "operation 1 has authored views to warm")
    _check(first_views.all(func(view: Dictionary) -> bool: return not MachineSprite.view_cached(view)), "nothing cached before the title")

    var flow = FLOW.instantiate()
    flow.persist_campaign = false
    root.add_child(flow)
    await process_frame
    _check(Warmer.busy(), "the title screen queues the recommended operation")
    await _until_idle("title robots")
    _check(first_views.all(func(view: Dictionary) -> bool: return MachineSprite.view_cached(view)), "every operation 1 view cached")
    for path in _robot_texture_paths(first):
        _check(EnemyActor.has_cached_texture(path), "texture kept: " + path)
    for view in first_views:
        var threaded: Dictionary = MachineSprite._read_view(view)
        var path := str(view.texture)
        var image := Image.load_from_file(path)
        _check(not threaded.is_empty() and threaded.size == Vector2(image.get_size()), "threaded view has the decoded size: " + path)
        _check(not threaded.is_empty() and threaded.pixel_sha256 == MachineSprite._pixel_hash_of(image), "threaded pixel hash equals main-thread decode: " + path)
    var warm_started := Time.get_ticks_usec()
    for identity in first: EnemyActor.warm_art(identity)
    var warm_ms := (Time.get_ticks_usec() - warm_started) / 1000.0
    print("stage_robot_warm_after_background_ms=%.1f" % warm_ms)
    _check(warm_ms < 60.0, "stage robot warm after the background warm is cache hits (%.1f ms)" % warm_ms)

    # Briefing: plates, props and atlases for this deploy.
    flow.open_mission_briefing("MIS_CH01_01")
    _check(Warmer.busy(), "the briefing queues the deploy")
    await _until_idle("briefing deploy")
    var plates := _plate_paths("MIS_CH01_01")
    var atlases := _atlas_paths()
    var props := _prop_keys("MIS_CH01_01")
    _check(plates.size() >= 10 and atlases.size() == 48 and props.size() >= 2, "deploy has plates, 48 atlases and props (%d/%d/%d)" % [plates.size(), atlases.size(), props.size()])
    _check(plates.all(func(path: String) -> bool: return BattleTextureLibrary.has_prepared(path)), "every room plate prepared")
    _check(atlases.all(func(path: String) -> bool: return MotionLabCharacterRuntime.has_prepared(path)), "every squad atlas prepared")
    _check(props.all(func(key: String) -> bool: return Props.prop_cached(key)), "every cover prop prepared")
    var sample := MotionLabCharacterRuntime.decode_atlas(atlases[0])
    var prepared_atlas: Texture2D = MotionLabCharacterRuntime._prepared.get(atlases[0])
    _check(sample != null and prepared_atlas != null and prepared_atlas.get_size() == Vector2(sample.get_size()), "prepared atlas has the decoded size")

    flow.deploy_mission("MIS_CH01_01")
    for i in range(4): await process_frame
    var stage: StoryStage01 = flow.current_view
    _check(plates.all(func(path: String) -> bool: return not BattleTextureLibrary.has_prepared(path)), "the deploy took every prepared plate")
    _check(atlases.all(func(path: String) -> bool: return not MotionLabCharacterRuntime.has_prepared(path)), "the deploy took every prepared atlas")
    var art := stage.get_node("RoomArtLayer") as Site7RoomArtLayer
    _check(art.get_room_plate(str(stage.main_route[0].id)) != null, "the stage shows its first room plate")
    for operator in stage.squad.operators:
        var runtime := operator.get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
        _check(runtime != null and runtime.debug_contract().active, "operator runtime active on prepared atlases: " + str(operator.name))
    var cover := stage.get_node_or_null("EnvironmentProps")
    _check(cover != null and int(cover.debug_contract().count) > 0, "cover props placed from the prepared art")

    # Backing out of a briefing frees what was prepared for it.
    flow.enter_base()
    await process_frame
    flow.open_mission_briefing("MIS_CH01_01")
    for i in range(3): await process_frame
    flow.enter_base()
    _check(plates.all(func(path: String) -> bool: return not BattleTextureLibrary.has_prepared(path)), "backing out drops prepared plates")
    _check(atlases.all(func(path: String) -> bool: return not MotionLabCharacterRuntime.has_prepared(path)), "backing out drops prepared atlases")
    await process_frame
    root.remove_child(flow)
    flow.free()
    _check(not Warmer.busy(), "leaving the game flow stops the warm")

    # Web builds: one job per frame on the main thread.
    var second := Warmer.mission_enemy_ids("MIS_CH01_02")
    Warmer.request_deploy("MIS_CH01_02")
    var jobs := Warmer._jobs.size() + Warmer._texture_paths.filter(func(path: String) -> bool: return not EnemyActor.has_cached_texture(path)).size()
    _check(jobs > 0, "operation 2 queues uncached work")
    var calls := 0
    while Warmer.busy() and calls < 400:
        Warmer._pump_inline()
        calls += 1
    _check(not Warmer.busy() and calls == jobs, "inline pump does one job per frame (%d jobs, %d calls)" % [jobs, calls])
    _check(_views_of(second).all(func(view: Dictionary) -> bool: return MachineSprite.view_cached(view)), "every operation 2 view cached inline")
    _check(_plate_paths("MIS_CH01_02").all(func(path: String) -> bool: return BattleTextureLibrary.has_prepared(path)), "operation 2 plates prepared inline")
    Warmer.release()
    _check(_plate_paths("MIS_CH01_02").all(func(path: String) -> bool: return not BattleTextureLibrary.has_prepared(path)), "release drops them")

    # The stage deploys while threads are mid-flight.
    var third := Warmer.mission_enemy_ids("MIS_CH01_03")
    Warmer.request_robots("MIS_CH01_03")
    Warmer.pump()
    _check(Warmer.busy(), "operation 3 work in flight")
    Warmer.finish()
    _check(not Warmer.busy(), "finish leaves nothing queued or running")
    for identity in third: EnemyActor.warm_art(identity)
    _check(_views_of(third).all(func(view: Dictionary) -> bool: return MachineSprite.view_cached(view)), "synchronous fallback completes operation 3")
    Warmer.request_robots("MIS_CH01_03")
    Warmer.pump()
    _check(not Warmer.busy(), "a repeated request after finish finds everything cached")
    _finish()

func _until_idle(label: String) -> void:
    var started := Time.get_ticks_msec()
    var slowest := 0
    var last := Time.get_ticks_usec()
    while Warmer.busy() and Time.get_ticks_msec() - started < 90000:
        await process_frame
        var now := Time.get_ticks_usec()
        slowest = maxi(slowest, now - last)
        last = now
    _check(not Warmer.busy(), label + " completes")
    print("%s: done_ms=%d slowest_frame_ms=%.1f" % [label, Time.get_ticks_msec() - started, slowest / 1000.0])

func _views_of(identities: Array[String]) -> Array[Dictionary]:
    var views: Array[Dictionary] = []
    for identity in identities:
        var spec := EnemyActor.reviewed_machine_spec(identity)
        if not spec.is_empty(): views.append_array(MachineSprite.view_specs(spec))
    return views

func _robot_texture_paths(identities: Array[String]) -> Array[String]:
    var paths: Array[String] = []
    for identity in identities:
        var profile := ArtProfileRegistry.get_profile(identity)
        for path in [str(profile.get("master_asset", "")), str(profile.get("rig_sheet", "")), EnemyDetailOverlayPresentation.detail_asset(identity)]:
            var resource_path: String = path if path.is_empty() or path.begins_with("res://") else "res://" + path
            if not resource_path.is_empty() and ResourceLoader.exists(resource_path) and not resource_path in paths: paths.append(resource_path)
    return paths

func _plate_paths(mission_id: String) -> Array[String]:
    var paths: Array[String] = []
    var art: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Warmer.ROOM_ART))
    for collection in ["rooms", "connectors"]:
        for row in art.missions[mission_id][collection]: paths.append("res://" + str(row.asset))
    return paths

func _atlas_paths() -> Array[String]:
    var paths: Array[String] = []
    for character in ["aster", "mica", "rook"]: paths.append_array(MotionLabCharacterRuntime.atlas_paths(character))
    return paths

func _prop_keys(mission_id: String) -> Array[String]:
    var keys: Array[String] = []
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Props.CONFIG))
    var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(config.spec)))
    for rows in (config.missions[mission_id] as Dictionary).values():
        for row in rows:
            var asset: Dictionary = spec.props[str(row.asset)]
            var key := str(asset.texture) + "|" + str(asset.sha256)
            if not key in keys: keys.append(key)
    return keys

func _finish() -> void:
    if failures.is_empty():
        print("DEPLOY_WARMER_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        quit(1)

func _check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label)
