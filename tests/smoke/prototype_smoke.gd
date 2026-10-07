extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
    var arena_scene := load("res://scenes/mission/PrototypeArena.tscn") as PackedScene
    _check(arena_scene != null, "PrototypeArena scene loads")
    if arena_scene == null:
        _finish()
        return
    var arena := arena_scene.instantiate()
    root.add_child(arena)
    call_deferred("_run_after_ready")

func _run_after_ready() -> void:
    await process_frame
    await physics_frame

    var operators := get_nodes_in_group("operators")
    _check(operators.size() == 3, "exactly three operator actors spawn")

    var squad := get_first_node_in_group("squad_controller") as SquadController
    _check(squad != null, "SquadController registers")
    if squad:
        _check(squad.get_active_operator() != null, "active operator exists")
        squad.request_control(2)
        _check(squad.active_index == 2, "control swaps to operator 3")
        squad.request_control(0)

    for node in operators:
        var actor := node as OperatorActor
        _check(actor != null, "operator type contract")
        if actor == null:
            continue
        var visual := actor.get_node("VisualRoot") as OperatorVisual
        _check(visual != null, "%s has OperatorVisual" % actor.display_name)
        if visual:
            _check(visual.skeleton != null and visual.skeleton.get_bone_count() >= 12, "%s has 2D skeletal rig" % actor.display_name)
            _check(visual.animation_player != null, "%s has AnimationPlayer" % actor.display_name)
            _check(visual.animation_tree != null and visual.animation_tree.active, "%s has active AnimationTree" % actor.display_name)
            _check(visual.muzzle_socket != null, "%s has muzzle socket" % actor.display_name)
        actor.debug_drive(Vector2.RIGHT, Vector2.UP)

    await physics_frame
    if not operators.is_empty():
        var first := operators[0] as OperatorActor
        var before_ammo := first.ammo
        var fired := first.debug_fire_once()
        _check(fired, "debug fire transaction succeeds")
        _check(first.ammo == before_ammo - 1, "fire consumes exactly one round")
        first.debug_begin_reload()
        _check(first.is_reloading(), "reload state begins")

    _check(get_nodes_in_group("prototype_targets").size() == 3, "three target dummies spawn")
    _finish()

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: ", label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)

func _finish() -> void:
    if failures.is_empty():
        print("PROTOTYPE_SMOKE: PASS")
        quit(0)
    else:
        print("PROTOTYPE_SMOKE: FAIL (%d)" % failures.size())
        for failure in failures:
            print(" - ", failure)
        quit(1)
