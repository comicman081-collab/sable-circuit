extends SceneTree

const LIBRARIES := {
    "UAL1": "res://assets/external/quaternius/ual1/UAL1_Standard.glb",
    "UAL1_RM": "res://assets/external/quaternius/ual1/UAL1_Standard_RM.glb",
    "UAL2": "res://assets/external/quaternius/ual2/UAL2_Standard.glb",
    "UAL2_RM": "res://assets/external/quaternius/ual2/UAL2_Standard_RM.glb",
}


func _init() -> void:
    var failures: Array[String] = []
    for label in LIBRARIES:
        var path: String = LIBRARIES[label]
        var packed := ResourceLoader.load(path) as PackedScene
        if packed == null:
            failures.append("%s PackedScene load failed" % label)
            continue
        var instance := packed.instantiate()
        var animation_players: Array[AnimationPlayer] = []
        var skeletons: Array[Skeleton3D] = []
        _collect_nodes(instance, animation_players, skeletons)
        if animation_players.is_empty():
            failures.append("%s AnimationPlayer missing" % label)
            instance.free()
            continue
        var names := _animation_names(animation_players[0])
        if names.size() != 43 or names.has(""):
            failures.append("%s animation count/name check failed: %d" % [label, names.size()])
        print("QUATERNIUS_GODOT_IMPORT: PASS %s animations=%d skeleton_nodes=%d" % [label, names.size(), skeletons.size()])
        print("QUATERNIUS_GODOT_NAMES %s: %s" % [label, ", ".join(names)])
        instance.free()
    if failures.is_empty():
        print("QUATERNIUS_GODOT_IMPORT_SMOKE: PASS")
    else:
        for failure in failures:
            push_error(failure)
        print("QUATERNIUS_GODOT_IMPORT_SMOKE: FAIL")
        quit(1)
        return
    quit(0)


func _collect_nodes(node: Node, animation_players: Array[AnimationPlayer], skeletons: Array[Skeleton3D]) -> void:
    if node is AnimationPlayer:
        animation_players.append(node as AnimationPlayer)
    if node is Skeleton3D:
        skeletons.append(node as Skeleton3D)
    for child in node.get_children():
        _collect_nodes(child, animation_players, skeletons)


func _animation_names(player: AnimationPlayer) -> Array[String]:
    var names: Array[String] = []
    for name in player.get_animation_list():
        names.append(str(name))
    names.sort()
    return names
