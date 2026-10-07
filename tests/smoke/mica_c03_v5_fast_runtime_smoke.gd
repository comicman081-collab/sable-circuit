extends SceneTree

## Runtime regression gate for MICA C03 V5.  This deliberately uses the
## registry profile and production descriptor: a fixture could not reveal a
## missing profile link, a schema mismatch, or an out-of-date frame socket.

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")
const DIRECTION_NAMES: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const DIRECTION_VECTORS: Array[Vector2] = [
    Vector2.RIGHT,
    Vector2(0.70710678, 0.70710678),
    Vector2.DOWN,
    Vector2(-0.70710678, 0.70710678),
    Vector2.LEFT,
    Vector2(-0.70710678, -0.70710678),
    Vector2.UP,
    Vector2(0.70710678, -0.70710678),
]

var failures := 0


func _init() -> void:
    call_deferred("_run")


func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures += 1
        push_error("FAIL: " + label)


func _point_from_json(value: Variant) -> Vector2:
    var point := value as Array
    return Vector2(float(point[0]), float(point[1]))


func _expected_global(runtime: FastCharacterRuntime, source_point: Vector2) -> Vector2:
    var local_point := runtime._display_offset + (source_point - Vector2.ONE * (runtime._cell_size * 0.5)) * runtime._display_scale
    return runtime.to_global(local_point)


func _run() -> void:
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview", false)
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime", true)
    var profile := ArtProfileRegistry.get_profile("CHR_PROTO_03")
    _check(str(profile.get("authored_runtime_descriptor", "")) == "data/character_pipeline/mica_runtime.json", "MICA registry selects the C03 V5 descriptor")
    _check(str(profile.get("costume_id", "")) == "MICA_RECON_C03", "MICA registry locks the C03 costume")

    var descriptor_variant: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/character_pipeline/mica_runtime.json"))
    _check(descriptor_variant is Dictionary, "MICA production descriptor parses")
    var descriptor: Dictionary = descriptor_variant as Dictionary
    _check(int(descriptor.get("schema", 0)) == 2, "MICA descriptor declares frame-indexed muzzle schema 2")

    var actor := OPERATOR_SCENE.instantiate() as OperatorActor
    actor.operator_id = "CHR_PROTO_03"
    actor.display_name = "MICA"
    root.add_child(actor)
    await process_frame
    await process_frame
    var runtime := actor.get_node_or_null("FastCharacterRuntime") as FastCharacterRuntime
    _check(runtime != null and runtime.is_runtime_active(), "MICA C03 V5 authored runtime activates")
    var contract: Dictionary = runtime.debug_contract() if runtime else {}
    _check(int(contract.get("descriptor_schema", 0)) == 2, "shared runtime accepts schema 2")
    _check(bool(contract.get("frame_muzzle_tracking", false)), "shared runtime enables per-frame muzzle tracking")
    _check(int((contract.get("frame_counts", {}) as Dictionary).get("move", 0)) == 24, "MICA move atlas has 24 UAL-timed frames")
    _check(bool(contract.get("move_root_sync_enabled", false)), "MICA enables duplicate-pose root synchronization")
    _check(int(contract.get("move_root_samples_per_pose", 0)) == 2, "MICA root synchronization declares two samples per authored pose")

    # Verify the cadence contract directly before exercising direction/socket
    # coverage: the advance sample preserves average travel and the duplicate
    # hold sample keeps the root planted.
    runtime._show("move", 0, 0)
    _check(is_equal_approx(runtime.get_root_motion_scale(), 2.0), "MICA move pose advance sample uses 2x root displacement")
    runtime._show("move", 0, 1)
    _check(is_equal_approx(runtime.get_root_motion_scale(), 0.0), "MICA duplicate move pose sample holds the root")
    runtime._show("idle", 0, 0)
    _check(is_equal_approx(runtime.get_root_motion_scale(), 1.0), "MICA idle restores normal root displacement")

    var directions: Dictionary = descriptor.get("directions", {}) as Dictionary
    for sector in range(DIRECTION_NAMES.size()):
        actor.debug_drive(Vector2.RIGHT, DIRECTION_VECTORS[sector])
        actor.velocity = Vector2.RIGHT * 138.0
        await physics_frame
        await process_frame
        contract = runtime.debug_contract() if runtime else {}
        var direction_name: String = DIRECTION_NAMES[sector]
        _check(actor.facing_sector == sector, "MICA resolves %d-degree aim sector %d" % [sector * 45, sector])
        _check(str(contract.get("active_state", "")) == "move", "MICA sector %s selects the move atlas" % direction_name)
        _check(runtime != null and runtime.sprite.texture != null and runtime.sprite.visible, "MICA sector %s has a visible authored cell" % direction_name)
        var active_frame := int(contract.get("active_frame", -1))
        var direction_spec: Dictionary = directions.get(direction_name, {}) as Dictionary
        var move_points: Array = direction_spec.get("move_muzzle_xy", []) as Array
        _check(active_frame >= 0 and active_frame < move_points.size(), "MICA sector %s exposes a valid tracked move frame" % direction_name)
        if active_frame >= 0 and active_frame < move_points.size() and runtime != null:
            var expected := _expected_global(runtime, _point_from_json(move_points[active_frame]))
            var actual := runtime.get_authored_muzzle_global_position()
            var projectile_origin: Vector2 = actor.call("_get_projectile_spawn_origin")
            _check(actual.distance_to(expected) < 0.01, "MICA sector %s uses its current move-frame muzzle socket" % direction_name)
            _check(projectile_origin.distance_to(actual) < 0.01, "MICA sector %s projectile origin equals its visible socket" % direction_name)

    actor.debug_drive(Vector2.ZERO, DIRECTION_VECTORS[7])
    await physics_frame
    var fired := actor.debug_fire_once()
    var fire_contract: Dictionary = runtime.debug_contract() if runtime else {}
    var fire_points: Array = ((directions.get("NE", {}) as Dictionary).get("fire_muzzle_xy", []) as Array)
    _check(fired, "MICA fires from the selected NE direction")
    _check(str(fire_contract.get("active_state", "")) == "fire" and int(fire_contract.get("active_frame", -1)) == 0, "MICA selects fire cell 0 before spawning its projectile")
    if runtime != null and fire_points.size() > 0:
        var expected_fire := _expected_global(runtime, _point_from_json(fire_points[0]))
        var actual_fire := runtime.get_authored_muzzle_global_position()
        var fire_origin: Vector2 = actor.call("_get_projectile_spawn_origin")
        _check(actual_fire.distance_to(expected_fire) < 0.01, "MICA fire frame 0 socket is authored and current")
        _check(fire_origin.distance_to(actual_fire) < 0.01, "MICA fired projectile starts from the displayed fire-frame socket")

    for child in root.get_children():
        if child is PrototypeProjectile:
            child.queue_free()
    actor.queue_free()
    await process_frame
    await process_frame
    print("MICA_C03_V5_FAST_RUNTIME_SMOKE: " + ("PASS" if failures == 0 else "FAIL"))
    quit(0 if failures == 0 else 1)
