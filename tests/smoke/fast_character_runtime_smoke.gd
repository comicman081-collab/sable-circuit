extends SceneTree

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")
const ROOT_DIR := "res://artifacts/fast_character_runtime_smoke"
const DIRECTIONS: Array[String] = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const STATES: Dictionary = {
    "idle": {"frames": 2, "fps": 4.0},
    "move": {"frames": 3, "fps": 12.0},
    "fire": {"frames": 2, "fps": 12.0},
}

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
    _make_fixture()

    var actor := OPERATOR_SCENE.instantiate() as OperatorActor
    actor.operator_id = "CHR_FAST_SMOKE"
    actor.display_name = "FAST SMOKE"
    actor.art_profile = {
        "actor_id": "CHR_FAST_SMOKE",
        "name": "FAST SMOKE",
        "authored_runtime_descriptor": "artifacts/fast_character_runtime_smoke/runtime_descriptor.json",
    }
    get_root().add_child(actor)
    await process_frame
    await process_frame

    var runtime := actor.get_node_or_null("FastCharacterRuntime") as FastCharacterRuntime
    _check(runtime != null, "operator scene owns the shared fast runtime")
    _check(runtime != null and runtime.is_runtime_active(), "descriptor activates the shared runtime")
    var contract := runtime.debug_contract() if runtime else {}
    _check(int(contract.get("directions", 0)) == 8, "runtime loads all eight directions")
    _check(int((contract.get("frame_counts", {}) as Dictionary).get("move", 0)) == 3, "runtime consumes descriptor frame counts")
    _check(runtime.sprite != null and runtime.sprite.visible, "authored raster replaces the procedural visual")

    actor.facing_sector = 3
    actor.velocity = Vector2(100.0, 0.0)
    await process_frame
    _check(runtime.sprite.texture != null, "movement selects a runtime atlas")
    var muzzle := runtime.get_authored_muzzle_global_position()
    var projectile_origin: Vector2 = actor.call("_get_projectile_spawn_origin")
    _check(projectile_origin.distance_to(muzzle) < 0.01, "projectile birth uses the visible authored muzzle socket")

    actor.queue_free()
    await process_frame
    _remove_fixture()
    print("FAST_CHARACTER_RUNTIME_SMOKE: " + ("PASS" if failures == 0 else "FAIL"))
    quit(0 if failures == 0 else 1)


func _make_fixture() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(ROOT_DIR))
    var direction_payload := {}
    for direction in DIRECTIONS:
        var row := {"muzzle_xy": [230.0, 128.0]}
        for state in STATES:
            var frames := int((STATES[state] as Dictionary)["frames"])
            var image := Image.create(256, 256 * frames, false, Image.FORMAT_RGBA8)
            image.fill(Color(0.08, 0.18, 0.28, 1.0))
            var path := ROOT_DIR + "/%s_%s.png" % [direction, state]
            image.save_png(ProjectSettings.globalize_path(path))
            row[state + "_atlas"] = path.trim_prefix("res://")
        direction_payload[direction] = row
    var descriptor := {
        "schema": 1,
        "actor_id": "CHR_FAST_SMOKE",
        "display_name": "FAST SMOKE",
        "costume_id": "FAST_SMOKE_C01",
        "cell_size": 256,
        "display_scale": 0.4,
        "display_offset": [0.0, -30.0],
        "states": STATES,
        "directions": direction_payload,
    }
    var file := FileAccess.open(ROOT_DIR + "/runtime_descriptor.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(descriptor, "  ") + "\n")
    file.close()


func _remove_fixture() -> void:
    var absolute := ProjectSettings.globalize_path(ROOT_DIR)
    var directory := DirAccess.open(absolute)
    if directory == null:
        return
    directory.list_dir_begin()
    var name := directory.get_next()
    while not name.is_empty():
        if not directory.current_is_dir():
            DirAccess.remove_absolute(absolute.path_join(name))
        name = directory.get_next()
    directory.list_dir_end()
    DirAccess.remove_absolute(absolute)
