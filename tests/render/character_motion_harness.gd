extends SceneTree

## Production input/physics measurement. No debug_drive, private cursor writes,
## deterministic-capture mode, or velocity-as-displacement assertions.
const ACTOR_SCENE = preload("res://scenes/actors/player/OperatorActor.tscn")
const DIRS = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
const VECTORS = [Vector2.RIGHT, Vector2(0.70710678,0.70710678), Vector2.DOWN,
    Vector2(-0.70710678,0.70710678), Vector2.LEFT, Vector2(-0.70710678,-0.70710678),
    Vector2.UP, Vector2(0.70710678,-0.70710678)]

var actor: OperatorActor
var runtime: Node
var cases: Array = []
var active_case: Dictionary = {}
var hz: int = 60
var expected_aim: Vector2 = Vector2.RIGHT
var wall: StaticBody2D
var test_viewport: SubViewport
var marker_probe := false
var marker_pixels_by_frame: Dictionary = {}
var marker_texture: Texture2D
var marker_image: Image

func _init() -> void:
    hz = int(OS.get_environment("SABLE_HARNESS_HZ"))
    if hz not in [30, 60, 120]:
        quit(2)
        return
    Engine.physics_ticks_per_second = hz
    call_deferred("_run")

func _key(code: Key, pressed: bool) -> void:
    var event = InputEventKey.new()
    event.keycode = code
    event.physical_keycode = code
    event.pressed = pressed
    Input.parse_input_event(event)

func _input(move: Vector2, running: bool, shooting: bool, aim: Vector2) -> void:
    _key(KEY_D, move.x > 0.1)
    _key(KEY_A, move.x < -0.1)
    _key(KEY_S, move.y > 0.1)
    _key(KEY_W, move.y < -0.1)
    _key(KEY_SHIFT, running)
    expected_aim = aim
    var point: Vector2 = actor.get_global_transform_with_canvas() * (aim * 300.0)
    var mouse = InputEventMouseMotion.new()
    mouse.position = point
    mouse.global_position = point
    Input.parse_input_event(mouse)
    # Headless windows do not receive desktop cursor motion. Deliver the same
    # event through Viewport's public input route, not an actor aim/debug setter.
    test_viewport.push_input(mouse, true)
    var button = InputEventMouseButton.new()
    button.button_index = MOUSE_BUTTON_LEFT
    button.pressed = shooting
    button.position = point
    Input.parse_input_event(button)
    test_viewport.push_input(button, true)

func _tick() -> void:
    await physics_frame
    await process_frame

func _run() -> void:
    if not OS.get_environment("SABLE_RUNTIME_CAPTURE_MODE").is_empty():
        push_error("Capture clock override must not be used in production harness")
        quit(2)
        return
    root.size = Vector2i(1920, 1080)
    test_viewport = SubViewport.new()
    test_viewport.size = Vector2i(1920, 1080)
    test_viewport.handle_input_locally = true
    root.add_child(test_viewport)
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime", true)
    ProjectSettings.set_setting("sable_visuals/aster_v4_locomotion_preview", false)
    ProjectSettings.set_setting("sable_visuals/fast_character_runtime_descriptor_override", OS.get_environment("SABLE_HARNESS_DESCRIPTOR"))
    var descriptor = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("SABLE_HARNESS_DESCRIPTOR")))
    if not descriptor is Dictionary:
        quit(2)
        return
    marker_probe = OS.get_environment("SABLE_CHANNEL_MARKER_PROBE") == "1"
    if marker_probe and descriptor.get("qa_fixture_only") != true:
        push_error("Channel marker probe is synthetic regression evidence only")
        quit(2)
        return
    actor = ACTOR_SCENE.instantiate() as OperatorActor
    actor.configure(str(descriptor.get("actor_id", "CHR_PROTO_03")), "HARNESS", Color.WHITE)
    actor.magazine_size = 10000 # Long matrix without unintended empty-magazine gaps; dedicated reload cases below.
    actor.position = Vector2(960,540)
    actor.set_movement_bounds(Rect2(-100000, -100000, 200000, 200000))
    test_viewport.add_child(actor)
    actor.set_controlled(true)
    actor.projectile_spawned.connect(_on_projectile)
    runtime = actor.get_node("FastCharacterRuntime")
    for ignored in range(6):
        await _tick()
    for mode in ["walk", "run"]:
        for direction in range(8):
            await _case("%s/%s/travel" % [mode, DIRS[direction]], direction, direction, mode == "run", "travel")
            for aim in range(8):
                await _case("%s/%s/fire/%s" % [mode, DIRS[direction], DIRS[aim]], direction, aim, mode == "run", "fire")
    for direction in range(8):
        for kind in ["idle_fire", "stop_resume", "turn_adjacent", "turn_opposite", "speed_switch", "reload", "boundary", "collision", "boundary_fire", "collision_fire", "start_turn_fire", "aim_turn_fire"]:
            await _case("%s/%s" % [kind, DIRS[direction]], direction, direction, false, kind)
    _input(Vector2.ZERO, false, false, Vector2.RIGHT)
    _key(KEY_R, false)
    var path = OS.get_environment("SABLE_HARNESS_OUTPUT")
    var output = FileAccess.open(path, FileAccess.WRITE)
    if output == null:
        quit(2)
        return
    output.store_string(JSON.stringify({"schema": 1, "subject_sha256": OS.get_environment("SABLE_HARNESS_SUBJECT"),
        "input_method": "Input.parse_input_event", "clock": "production_physics_delta",
        "physics_hz": hz, "actor_id": actor.operator_id, "viewport_input_method": "Viewport.push_input",
        "descriptor": OS.get_environment("SABLE_HARNESS_DESCRIPTOR"),
        "representation_kind": descriptor.get("representation", {}).get("kind", ""),
        "sprite_pixel_probe": marker_probe,
        "headless": true, "visual_gate": "NOT_EVALUATED", "cases": cases}))
    output.close()
    print("MOTION_HARNESS_CAPTURE_COMPLETE cases=%d hz=%d" % [cases.size(), hz])
    quit(0)

func _case(id: String, direction: int, aim_direction: int, running: bool, kind: String) -> void:
    active_case = {}
    _input(Vector2.ZERO, false, false, VECTORS[aim_direction])
    _key(KEY_R, false)
    # Settle real fire/reload timers through normal processing; never reset cursor.
    for ignored in range(int(hz * 0.6)):
        await _tick()
    actor.position = Vector2(960,540)
    actor.set_movement_bounds(Rect2(-100000, -100000, 200000, 200000))
    actor.ammo = 10000
    var blocked = kind in ["boundary", "collision", "boundary_fire", "collision_fire"]
    if kind in ["boundary", "boundary_fire"]:
        actor.set_movement_bounds(Rect2(actor.position - Vector2(3,3), Vector2(6,6)))
    if kind in ["collision", "collision_fire"]:
        wall = StaticBody2D.new()
        wall.collision_layer = 1
        var shape = CollisionShape2D.new()
        var rectangle = RectangleShape2D.new()
        rectangle.size = Vector2(8, 1000)
        shape.shape = rectangle
        wall.add_child(shape)
        wall.position = actor.position + Vector2(0,-18) + VECTORS[direction] * 20.0
        wall.rotation = VECTORS[direction].angle()
        test_viewport.add_child(wall)
    active_case = {"id": id, "blocked": blocked, "block_observed": false,
        "start_position": [actor.global_position.x,actor.global_position.y],
        "start_locomotion_phase": runtime.call("debug_contract").get("locomotion_phase", 0),
        "requires_fire": kind in ["fire", "idle_fire", "reload", "boundary_fire", "collision_fire", "start_turn_fire", "aim_turn_fire"], "samples": [], "shots": [], "reload_observed": false}
    var ticks = int(hz * 2.1)
    for index in range(ticks):
        var move: Vector2 = VECTORS[direction]
        var run_now: bool = running
        var shooting: bool = kind in ["fire", "idle_fire", "reload", "boundary_fire", "collision_fire", "aim_turn_fire"] or (kind == "start_turn_fire" and index >= ticks / 2.0)
        var aim_now: Vector2 = VECTORS[aim_direction]
        if kind == "idle_fire" or (kind == "stop_resume" and index >= ticks / 3.0 and index < ticks * 2.0 / 3.0):
            move = Vector2.ZERO
        if kind == "start_turn_fire" and index < ticks / 2.0:
            move = Vector2.ZERO
        if index >= ticks / 2.0:
            if kind == "turn_adjacent": move = VECTORS[(direction + 1) % 8]
            if kind == "turn_opposite": move = VECTORS[(direction + 4) % 8]
            if kind == "speed_switch": run_now = true
            if kind in ["start_turn_fire", "aim_turn_fire"]: aim_now = VECTORS[(aim_direction + 4) % 8]
        _input(move, run_now, shooting, aim_now)
        if kind == "reload" and index == int(hz * 0.25):
            _key(KEY_R, true)
        elif kind == "reload":
            _key(KEY_R, false)
        var before: Vector2 = actor.global_position
        active_case["physics_sample_index"] = index
        await _tick()
        var displacement: Vector2 = actor.global_position - before
        var state: Dictionary = runtime.call("debug_contract")
        var wanted: float = (actor.run_speed if run_now else actor.walk_speed) * move.length()
        if blocked and index > hz / 2 and displacement.length() < 0.01:
            if kind in ["boundary", "boundary_fire"] or actor.get_slide_collision_count() > 0:
                active_case["block_observed"] = true
        if actor.is_reloading(): active_case["reload_observed"] = true
        active_case["samples"].append({"dt": 1.0 / hz, "delta": [displacement.x, displacement.y],
            "world_position": [actor.global_position.x, actor.global_position.y],
            "requested_speed": wanted, "reported_velocity": [actor.velocity.x, actor.velocity.y],
            "move_vector": [move.x,move.y], "aim_vector": [actor.aim_world.x,actor.aim_world.y],
            "requested_aim": [expected_aim.x,expected_aim.y],
            "active_descriptor": state.get("descriptor", ""),
            "slide_collisions": actor.get_slide_collision_count(), "reloading": actor.is_reloading(),
            "runtime_active": state.get("active", false), "state": state.get("active_state", ""),
            "sector": state.get("active_sector", -1), "frame": state.get("active_frame", -1)})
        active_case["samples"][-1].merge({
            "representation_channel": state.get("representation_channel", ""),
            "representation_atlas": state.get("representation_atlas", ""),
            "movement_sector": state.get("movement_sector", -1),
            "locomotion_phase": state.get("locomotion_phase", -1)})
        if marker_probe:
            active_case["samples"][-1].merge(_actual_sprite_pixels())
    cases.append(active_case)
    active_case = {}
    if wall != null:
        wall.queue_free()
        wall = null

func _on_projectile(projectile: Node2D) -> void:
    if active_case.is_empty(): return
    var state: Dictionary = runtime.call("debug_contract")
    var socket: Vector2 = runtime.call("get_authored_muzzle_global_position")
    var actual_direction: Vector2 = projectile.get("direction")
    var sector: int = posmod(int(floor((expected_aim.angle() + PI / 8.0) / (PI / 4.0))), 8)
    active_case["shots"].append({"origin": [projectile.global_position.x, projectile.global_position.y],
        "socket": [socket.x,socket.y], "reloading": actor.is_reloading(),
        "direction": [actual_direction.x,actual_direction.y], "socket_error": projectile.global_position.distance_to(socket),
        "aim_error_degrees": abs(rad_to_deg(actual_direction.angle_to(expected_aim))),
        "shown_sector": state.get("active_sector", -1), "aim_sector": sector,
        "representation_channel": state.get("representation_channel", ""),
        "representation_atlas": state.get("representation_atlas", ""),
        "physics_sample_index": active_case.get("physics_sample_index", -1),
        "locomotion_phase": state.get("locomotion_phase", -1),
        "state": state.get("active_state", ""), "frame": state.get("active_frame", -1)})
    if marker_probe:
        active_case["shots"][-1].merge(_actual_sprite_pixels())

func _actual_sprite_pixels() -> Dictionary:
    var actual_sprite: Sprite2D = runtime.get("sprite")
    if actual_sprite.texture != marker_texture:
        marker_texture = actual_sprite.texture
        marker_image = marker_texture.get_image()
        marker_pixels_by_frame.clear()
    var region := Rect2i(actual_sprite.region_rect)
    var frame_image := marker_image.get_region(region)
    if not marker_pixels_by_frame.has(region.position.y):
        var hits: Array = []
        for y in range(frame_image.get_height()):
            for x in range(frame_image.get_width()):
                if frame_image.get_pixel(x,y) == Color.RED:
                    hits.append(Vector2(x,y))
        marker_pixels_by_frame[region.position.y] = hits
    var pixels: Array = marker_pixels_by_frame[region.position.y]
    var point := Vector2.ZERO
    if pixels.size() == 1:
        point = pixels[0]
        if actual_sprite.flip_h: point.x = region.size.x - 1 - point.x
        if actual_sprite.flip_v: point.y = region.size.y - 1 - point.y
        point = actual_sprite.to_global(actual_sprite.get_rect().position + point)
    var hasher := HashingContext.new()
    hasher.start(HashingContext.HASH_SHA256)
    hasher.update(frame_image.get_data())
    return {"sprite_region": [region.position.x, region.position.y, region.size.x, region.size.y],
        "visible_marker_count": pixels.size(), "actual_marker_world": [point.x,point.y],
        "sprite_visible": actual_sprite.is_visible_in_tree(),
        "sprite_alpha": actual_sprite.modulate.a * actual_sprite.self_modulate.a,
        "sprite_centered": actual_sprite.centered,
        "sprite_flip": [actual_sprite.flip_h,actual_sprite.flip_v],
        "shown_frame_rgba_sha256": hasher.finish().hex_encode()}
