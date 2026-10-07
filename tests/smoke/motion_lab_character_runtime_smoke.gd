extends SceneTree

## App-level contract for all three current Motion Studio character packages.
## This deliberately instantiates the real StoryStage squad rather than a
## synthetic sprite fixture so map scale, actor input, collision displacement,
## muzzle birth, and older-presentation suppression are exercised together.

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const FEATURE_SETTING := "sable_visuals/motion_lab_character_runtime"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
var sector_vectors: Array[Vector2] = [
    Vector2.RIGHT,
    Vector2(1.0, 1.0).normalized(),
    Vector2.DOWN,
    Vector2(-1.0, 1.0).normalized(),
    Vector2.LEFT,
    Vector2(-1.0, -1.0).normalized(),
    Vector2.UP,
    Vector2(1.0, -1.0).normalized(),
]
const CASES: Array[Dictionary] = [
    {"actor_id": "CHR_PROTO_01", "name": "ASTER", "package": "aster"},
    {"actor_id": "CHR_PROTO_02", "name": "ROOK", "package": "rook"},
    {"actor_id": "CHR_PROTO_03", "name": "MICA", "package": "mica"},
]

var failures: Array[String] = []
var _last_projectile_origin := Vector2.INF


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    var feature_before: bool = bool(ProjectSettings.get_setting(FEATURE_SETTING, true))
    ProjectSettings.set_setting(FEATURE_SETTING, true)

    var stage := STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(12)

    for test_case in CASES:
        var actor := _find_operator(stage, str(test_case["actor_id"]))
        _check(actor != null, "%s exists in the real StoryStage squad" % str(test_case["name"]))
        if actor != null:
            await _check_operator(actor, test_case)

    stage.queue_free()
    await process_frame
    ProjectSettings.set_setting(FEATURE_SETTING, feature_before)

    if failures.is_empty():
        print("MOTION_LAB_CHARACTER_RUNTIME_SMOKE: PASS")
        quit(0)
        return
    print("MOTION_LAB_CHARACTER_RUNTIME_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)


func _find_operator(stage: StoryStage01, actor_id: String) -> OperatorActor:
    for actor in stage.squad.operators:
        if actor.operator_id == actor_id:
            return actor
    return null


func _check_operator(actor: OperatorActor, test_case: Dictionary) -> void:
    var name := str(test_case["name"])
    var package_id := str(test_case["package"])
    var runtime := actor.get_node_or_null("MotionLabCharacterRuntime") as MotionLabCharacterRuntime
    _check(runtime != null, "%s owns the shared Motion Studio runtime bridge" % name)
    if runtime == null:
        return
    await _frames(3)

    var contract := runtime.debug_contract()
    print("MOTION_LAB_RUNTIME_CONTRACT %s: %s" % [name, contract])
    _check(runtime.is_runtime_active(), "%s current Motion Studio package activates" % name)
    _check(str(contract.get("character_id", "")) == package_id, "%s reads its exact current package profile" % name)
    _check(str(contract.get("profile_path", "")).ends_with("/%s/profile.json" % package_id), "%s profile resolves inside the project Motion Studio package" % name)
    _check(int(contract.get("directions", 0)) == 8, "%s loads every authored direction" % name)
    _check(is_equal_approx(float(contract.get("display_height_px", 0.0)), 129.6), "%s uses the user-requested 129.6px map-operator height" % name)
    var studio_stride := float((runtime._profile.get("locomotion", {}) as Dictionary).get("walkStride", 1.6))
    _check(absf(float(contract.get("walk_cycle_distance", 0.0)) - studio_stride * 100.0) < 0.01, "%s walks one gait cycle per Studio stride x 100 map px, like every operator" % name)
    var registered: Array = contract.get("walk_registration_directions", [])
    if package_id == "aster":
        _check(registered.size() == 8, "ASTER keeps her torso steady through all eight walk cycles (%d registered)" % registered.size())
    else:
        _check(registered.is_empty(), "%s keeps its accepted hip placement" % name)
    var ground_anchor: Vector2 = contract.get("ground_anchor_local", Vector2.INF)
    _check(ground_anchor.length() <= 0.01, "%s source root is grounded on the actor map position" % name)
    _check(runtime.sprite != null and runtime.sprite.visible and runtime.sprite.texture != null, "%s displays authored Motion Studio raster pixels" % name)

    var visual := actor.get_node_or_null("VisualRoot") as OperatorVisual
    _check(visual != null and visual.modulate.a <= 0.01, "%s suppresses the old vector body without changing gameplay sockets" % name)
    var fast := actor.get_node_or_null("FastCharacterRuntime") as FastCharacterRuntime
    _check(fast == null or not fast.is_runtime_active(), "%s has no competing legacy fast-raster body" % name)
    if actor.operator_id == "CHR_PROTO_01":
        var legacy_aster := actor.get_node_or_null("AsterV4LocomotionPreview") as AsterV4LocomotionPreview
        _check(legacy_aster == null or not legacy_aster.is_runtime_active(), "ASTER Motion Studio body suppresses the retired V4 preview")

    for sector in range(DIRECTIONS.size()):
        actor.debug_drive(Vector2.ZERO, sector_vectors[sector])
        await _frames(2)
        contract = runtime.debug_contract()
        _check(int(contract.get("sector", -1)) == sector and str(contract.get("direction", "")) == DIRECTIONS[sector], "%s direction %s selects its matching authored atlas" % [name, DIRECTIONS[sector]])
        _check(runtime.sprite.texture != null, "%s direction %s keeps a drawable atlas" % [name, DIRECTIONS[sector]])

    actor.set_movement_bounds(Rect2(-10000.0, -10000.0, 20000.0, 20000.0))
    var stage := actor.get_parent().get_parent() as StoryStage01
    var entry: Dictionary = stage.main_route[0]
    actor.global_position = Vector2(float(entry.x), float(entry.y) - 120.0)
    var start := actor.global_position
    var frames_seen: Dictionary = {}
    var shift_seen := 0.0
    actor.debug_drive(Vector2.RIGHT, Vector2.RIGHT)
    for _sample in range(132):
        await physics_frame
        await process_frame
        contract = runtime.debug_contract()
        frames_seen[int(contract.get("frame", -1))] = true
        shift_seen = maxf(shift_seen, absf(float(contract.get("registration_x", 0.0))))
    _check((shift_seen > 1.0) == (package_id == "aster"), "%s walk registration shift %.1f cell px" % [name, shift_seen])
    _check(actor.global_position.x - start.x > 220.0, "%s advances across the actual map while walking" % name)
    _check(frames_seen.size() == 6 and not frames_seen.has(-1), "%s distance-driven walk visits all six approved gait frames" % name)

    actor.debug_drive(Vector2.ZERO, Vector2.UP)
    await _frames(2)
    var muzzle_before := runtime.get_authored_muzzle_global_position()
    var origin_before: Vector2 = actor.call("_get_projectile_spawn_origin")
    _check(origin_before.distance_to(muzzle_before) <= 0.01, "%s projectile source follows the visible authored muzzle" % name)
    _last_projectile_origin = Vector2.INF
    if not actor.projectile_spawned.is_connected(_capture_projectile_origin):
        actor.projectile_spawned.connect(_capture_projectile_origin)
    var fired := actor.debug_fire_once()
    var muzzle_after := runtime.get_authored_muzzle_global_position()
    _check(fired, "%s accepts a gameplay fire request" % name)
    _check(_last_projectile_origin.distance_to(muzzle_after) <= 0.01, "%s spawned projectile uses the same current whole-body frame muzzle" % name)
    actor.debug_stop_drive()


func _capture_projectile_origin(projectile: Node2D) -> void:
    _last_projectile_origin = projectile.global_position
    projectile.queue_free()


func _frames(count: int) -> void:
    for _frame in range(count):
        await process_frame


func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
