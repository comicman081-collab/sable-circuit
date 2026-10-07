extends SceneTree

## Runtime integration gate for the second authored operator.  This uses the
## actual registry profile and ROOK C02 descriptor—not a synthetic fixture.

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")
const DIRECTIONS: Array[Vector2] = [
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


func _run() -> void:
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview", false)
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime", true)
    var profile := ArtProfileRegistry.get_profile("CHR_PROTO_02")
    _check(str(profile.get("authored_runtime_descriptor", "")) == "data/character_pipeline/rook_runtime.json", "ROOK registry selects the C02 fast descriptor")
    _check(str(profile.get("costume_id", "")) == "ROOK_BREACH_C02", "ROOK registry locks the C02 costume")

    var actor := OPERATOR_SCENE.instantiate() as OperatorActor
    actor.operator_id = "CHR_PROTO_02"
    actor.display_name = "ROOK"
    root.add_child(actor)
    await process_frame
    await process_frame
    var runtime := actor.get_node_or_null("FastCharacterRuntime") as FastCharacterRuntime
    _check(runtime != null and runtime.is_runtime_active(), "ROOK C02 authored runtime activates")
    var contract := runtime.debug_contract() if runtime else {}
    _check(str(contract.get("actor_id", "")) == "CHR_PROTO_02", "runtime descriptor belongs to ROOK")
    _check(int((contract.get("frame_counts", {}) as Dictionary).get("idle", 0)) == 4, "ROOK idle atlas has four frames")
    _check(int((contract.get("frame_counts", {}) as Dictionary).get("move", 0)) == 24, "ROOK move atlas has 24 UAL-timed frames")
    _check(int((contract.get("frame_counts", {}) as Dictionary).get("fire", 0)) == 6, "ROOK fire atlas has six UAL-timed frames")

    for sector in range(DIRECTIONS.size()):
        actor.debug_drive(Vector2.RIGHT, DIRECTIONS[sector])
        actor.velocity = Vector2.RIGHT * 138.0
        await physics_frame
        await process_frame
        _check(actor.facing_sector == sector, "ROOK resolves %d-degree aim sector %d" % [sector * 45, sector])
        _check(runtime != null and runtime.sprite.texture != null and runtime.sprite.visible, "ROOK sector %d selects a visible authored atlas" % sector)
        var authored_muzzle := runtime.get_authored_muzzle_global_position() if runtime else Vector2.ZERO
        var projectile_origin: Vector2 = actor.call("_get_projectile_spawn_origin")
        _check(projectile_origin.distance_to(authored_muzzle) < 0.01, "ROOK sector %d projectile uses authored muzzle socket" % sector)

    actor.debug_drive(Vector2.RIGHT, Vector2(0.70710678, -0.70710678))
    await physics_frame
    var fired := actor.debug_fire_once()
    await process_frame
    _check(fired, "ROOK primary fire begins from the selected NE direction")
    _check(runtime != null and runtime.sprite.texture != null, "ROOK fire keeps the authored raster active")
    for child in root.get_children():
        if child is PrototypeProjectile:
            child.queue_free()
    await process_frame
    await process_frame
    actor.queue_free()
    await process_frame
    await process_frame
    print("ROOK_C02_FAST_RUNTIME_SMOKE: " + ("PASS" if failures == 0 else "FAIL"))
    quit(0 if failures == 0 else 1)
