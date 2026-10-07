extends RefCounted
## Loads what a deploy needs while the player is still on the menus, so DEPLOY does not
## stall (qa/spawn_hitch_20260925/). The title and base screens queue the robot art the
## next mission can spawn, which stays cached for the run like EnemyActor's own caches.
## The briefing screen adds that mission's room plates, cover props and the squad's
## animation atlases; plates and atlases are handed over once to the stage that deploys
## and dropped if the player backs out. Native: decoding runs on WorkerThreadPool and robot
## textures load on ResourceLoader's threads; the main thread only turns finished images
## into textures, a few milliseconds per frame. Web builds have no threads, so there each
## frame runs one job itself. GameFlow drives pump(); the stage calls finish() first, and
## the loaders' own synchronous paths stay the fallback for anything not reached.

const MachineSprite := preload("res://scripts/animation/site7_machine_sprite.gd")
const Props := preload("res://scripts/missions/site7_environment_props.gd")
const ROOM_ART := "res://data/visual/site7_battle_art.json"
const MAX_RUNNING := 2
const ADOPT_BUDGET_USEC := 4000

static var _requested: Array[String] = []
static var _texture_paths: Array[String] = []
static var _loading: Array[String] = []
## {"key", "prepare": worker-safe Callable -> Variant, "adopt": main-thread Callable(result),
## "done": main-thread Callable -> bool}
static var _jobs: Array[Dictionary] = []
static var _running: Array[Dictionary] = []

## Robot ids of a mission's rooms: encounters and reinforcement waves, first-seen order.
static func room_enemy_ids(rooms: Array) -> Array[String]:
    var seen: Array[String] = []
    for room in rooms:
        if not (room is Dictionary): continue
        var waves: Array = [room.get("encounter", [])]
        waves.append_array(room.get("reinforcements", []))
        for wave in waves:
            if not (wave is Array): continue
            for row in wave:
                var identity := str((row as Dictionary).get("enemy_id", "")) if row is Dictionary else ""
                if not identity.is_empty() and not identity in seen: seen.append(identity)
    return seen

static func mission_enemy_ids(mission_id: String) -> Array[String]:
    var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission_id))
    if not (parsed is Dictionary): return []
    return room_enemy_ids((parsed.get("main_route", []) as Array) + (parsed.get("optional_rooms", []) as Array))

## Queues the robot art a mission can spawn. Reads the mission and reviewed specs only.
static func request_robots(mission_id: String) -> void:
    var tag := "robots:" + mission_id
    if mission_id.is_empty() or tag in _requested: return
    _requested.append(tag)
    for identity in mission_enemy_ids(mission_id):
        var profile := ArtProfileRegistry.get_profile(identity)
        for path in [str(profile.get("master_asset", "")), str(profile.get("rig_sheet", "")), EnemyDetailOverlayPresentation.detail_asset(identity)]:
            var resource_path: String = path if path.is_empty() or path.begins_with("res://") else "res://" + path
            if not resource_path.is_empty() and ResourceLoader.exists(resource_path) and not resource_path in _texture_paths:
                _texture_paths.append(resource_path)
        if not bool(ProjectSettings.get_setting("sable_visuals/site7_authored_machines", true)): continue
        if (profile.get("machine_asset", {}) as Dictionary).is_empty(): continue
        var spec := EnemyActor.reviewed_machine_spec(identity)
        if spec.is_empty(): continue
        for view in MachineSprite.view_specs(spec):
            _queue(str(view.get("texture", "")), func() -> Variant: return MachineSprite.prepare_view(view),
                func(result: Variant) -> void: MachineSprite.adopt_view(result),
                func() -> bool: return MachineSprite.view_cached(view))

## Everything the deploy of a mission loads: its robots, room plates, cover props and the
## squad's atlases.
static func request_deploy(mission_id: String) -> void:
    request_robots(mission_id)
    var tag := "deploy:" + mission_id
    if mission_id.is_empty() or tag in _requested: return
    _requested.append(tag)
    var art: Variant = JSON.parse_string(FileAccess.get_file_as_string(ROOM_ART))
    var plates: Dictionary = art.get("missions", {}).get(mission_id, {}) if art is Dictionary else {}
    for collection in ["rooms", "connectors"]:
        for row in plates.get(collection, []):
            var path := "res://" + str((row as Dictionary).get("asset", "")) if row is Dictionary else ""
            if path == "res://" or not BattleTextureLibrary.has_texture(path): continue
            _queue(path, func() -> Variant: return BattleTextureLibrary.decode_image(path),
                func(result: Variant) -> void: BattleTextureLibrary.keep_prepared(path, result),
                func() -> bool: return BattleTextureLibrary.has_prepared(path))
    if bool(ProjectSettings.get_setting(MotionLabCharacterRuntime.FEATURE_SETTING, true)):
        var characters: Array[String] = []
        for profile in ArtProfileRegistry.get_all_profiles().values():
            var character := str((profile as Dictionary).get("motion_lab_character_id", "")).strip_edges().to_lower() if profile is Dictionary else ""
            if character in ["aster", "mica", "rook"] and not character in characters: characters.append(character)
        for character in characters:
            for path in MotionLabCharacterRuntime.atlas_paths(character):
                _queue(path, func() -> Variant: return MotionLabCharacterRuntime.decode_atlas(path),
                    func(result: Variant) -> void: MotionLabCharacterRuntime.keep_prepared(path, result),
                    func() -> bool: return MotionLabCharacterRuntime.has_prepared(path))
    var config: Variant = JSON.parse_string(FileAccess.get_file_as_string(Props.CONFIG))
    if config is Dictionary and not (config.get("missions", {}).get(mission_id, {}) as Dictionary).is_empty():
        var spec: Variant = JSON.parse_string(FileAccess.get_file_as_string(str(config.spec)))
        var used: Array[String] = []
        for rows in (config.missions[mission_id] as Dictionary).values():
            for row in rows:
                var id := str(row.get("asset", ""))
                if id in used or not (spec is Dictionary) or not spec.get("props", {}).has(id): continue
                used.append(id)
                var asset: Dictionary = spec.props[id]
                var path := str(asset.texture)
                var sha := str(asset.sha256)
                var key := path + "|" + sha
                _queue(key, func() -> Variant: return Props.prepare_prop(path, sha),
                    func(result: Variant) -> void: Props.adopt_prop(key, result),
                    func() -> bool: return Props.prop_cached(key))

static func _queue(key: String, prepare: Callable, adopt: Callable, done: Callable) -> void:
    if key.is_empty() or done.call(): return
    for job in _jobs + _running:
        if job.key == key: return
    _jobs.append({"key":key, "prepare":prepare, "adopt":adopt, "done":done})

static func busy() -> bool:
    return not (_texture_paths.is_empty() and _loading.is_empty() and _jobs.is_empty() and _running.is_empty())

## One frame of background work.
static func pump() -> void:
    if not busy(): return
    if OS.has_feature("web"):
        _pump_inline()
        return
    while not _texture_paths.is_empty():
        var path: String = _texture_paths.pop_front()
        if EnemyActor.has_cached_texture(path): continue
        if ResourceLoader.load_threaded_request(path, "Texture2D") == OK: _loading.append(path)
    for path in _loading.duplicate():
        if ResourceLoader.load_threaded_get_status(path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS: continue
        _loading.erase(path)
        EnemyActor.keep_texture(path, ResourceLoader.load_threaded_get(path) as Texture2D)
    var started := Time.get_ticks_usec()
    for job in _running.duplicate():
        if Time.get_ticks_usec() - started > ADOPT_BUDGET_USEC: break
        if not WorkerThreadPool.is_task_completed(job.task): continue
        _running.erase(job)
        _adopt(job)
    while _running.size() < MAX_RUNNING and not _jobs.is_empty():
        var job: Dictionary = _jobs.pop_front()
        if job.done.call(): continue
        # The worker touches only these two; the job dictionary stays the main thread's.
        var prepare: Callable = job.prepare
        var holder := [null]
        job["holder"] = holder
        job["task"] = WorkerThreadPool.add_task(func() -> void: holder[0] = prepare.call(), false, "Deploy warm")
        _running.append(job)

static func _adopt(job: Dictionary) -> void:
    WorkerThreadPool.wait_for_task_completion(job.task)
    if not job.done.call(): job.adopt.call(job.holder[0])

static func _pump_inline() -> void:
    while not _texture_paths.is_empty():
        var path: String = _texture_paths.pop_front()
        if EnemyActor.has_cached_texture(path): continue
        EnemyActor.cached_texture(path)
        return
    while not _jobs.is_empty():
        var job: Dictionary = _jobs.pop_front()
        if job.done.call(): continue
        job.adopt.call(job.prepare.call())
        return

## Waits for work already handed to threads and drops the rest of the queue; the caller's
## synchronous loads cover whatever was not reached.
static func finish() -> void:
    for job in _running: _adopt(job)
    _running.clear()
    for path in _loading:
        EnemyActor.keep_texture(path, ResourceLoader.load_threaded_get(path) as Texture2D)
    _loading.clear()
    _texture_paths.clear()
    _jobs.clear()
    # A later request for a dropped mission must queue again; finished work is skipped then.
    _requested.clear()

## The player left the briefing without deploying: stop, and free the plates and atlases
## that were only meant for that deploy. Robot art stays cached.
static func release() -> void:
    finish()
    BattleTextureLibrary.drop_prepared()
    MotionLabCharacterRuntime.drop_prepared()
