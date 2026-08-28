extends Node
class_name SquadCameraPresentation

const AIM_LOOK_AHEAD_X := 108.0
const AIM_LOOK_AHEAD_Y := 72.0
const VERTICAL_COMPOSITION_BIAS := -24.0
const BOSS_VERTICAL_COMPOSITION_BIAS := -150.0
const SQUAD_WEIGHT := 0.28
const COMBAT_TARGET_WEIGHT := 0.40
const BOSS_COMBAT_TARGET_WEIGHT := 0.50
const MAX_COMBAT_TARGET_DISTANCE := 620.0
const FOLLOW_RATE := 8.6

var stage: StoryStage01
var camera: Camera2D
var _last_target := Vector2.ZERO

func _ready() -> void:
    process_priority = 140
    stage = get_parent() as StoryStage01
    if stage:
        camera = stage.get_node_or_null("Camera2D") as Camera2D

func _process(delta: float) -> void:
    if stage == null or camera == null or not stage.is_processing():
        return
    var active := stage.squad.get_active_operator() if stage.squad else null
    if active == null:
        return
    var target := _target_for_active(active)
    _last_target = target
    var blend := 1.0 - pow(0.00028, delta * FOLLOW_RATE / 8.6)
    camera.global_position = camera.global_position.lerp(target, blend)

func _squad_centroid(active: OperatorActor) -> Vector2:
    if stage == null or stage.squad == null:
        return active.global_position
    var centroid := Vector2.ZERO
    var count := 0.0
    for actor in stage.squad.operators:
        if actor != null and not actor.is_downed():
            centroid += actor.global_position
            count += 1.0
    return centroid / count if count > 0.0 else active.global_position

func _hostile_centroid(active: OperatorActor) -> Dictionary:
    var sum := Vector2.ZERO
    var count := 0.0
    var nearest_d2 := INF
    var has_boss := false
    for node in active.get_tree().get_nodes_in_group("prototype_targets"):
        if node is Node2D and is_instance_valid(node):
            var d2 := active.global_position.distance_squared_to(node.global_position)
            if d2 <= MAX_COMBAT_TARGET_DISTANCE * MAX_COMBAT_TARGET_DISTANCE:
                sum += node.global_position
                count += 1.0
                nearest_d2 = minf(nearest_d2, d2)
                if node is EnemyActor and ("BOSS" in node.enemy_id or "ANCHOR" in node.enemy_id):
                    has_boss = true
    return {
        "valid": count > 0.0,
        "position": sum / count if count > 0.0 else active.global_position,
        "count": count,
        "nearest_d2": nearest_d2,
        "has_boss": has_boss
    }

func _target_for_active(active: OperatorActor) -> Vector2:
    var centroid := _squad_centroid(active)
    var squad_anchor := active.global_position.lerp(centroid, SQUAD_WEIGHT)
    var aim := active.aim_world.normalized() if active.aim_world.length_squared() > 0.001 else Vector2.RIGHT
    var hostile := _hostile_centroid(active)
    var target := squad_anchor
    var vertical_bias := VERTICAL_COMPOSITION_BIAS
    if bool(hostile.get("valid", false)):
        var hostile_pos: Vector2 = hostile.get("position", active.global_position)
        var delta := hostile_pos - squad_anchor
        if delta.length() > MAX_COMBAT_TARGET_DISTANCE:
            hostile_pos = squad_anchor + delta.normalized() * MAX_COMBAT_TARGET_DISTANCE
        var has_boss := bool(hostile.get("has_boss", false))
        var target_weight := BOSS_COMBAT_TARGET_WEIGHT if has_boss else COMBAT_TARGET_WEIGHT
        # Blend toward the actual hostile group instead of simply panning in aim
        # direction. Signal Anchor occupies substantially more vertical space than a
        # normal enemy: the earlier -78 bias still left its upper ring touching the
        # 1280x720 top edge. The dedicated -150 anchor moves the camera farther into
        # upper-world space, lowering the full boss/ring composition on screen while
        # retaining the squad above the bottom combat HUD.
        target = squad_anchor.lerp(hostile_pos, target_weight)
        target += Vector2(aim.x * (18.0 if has_boss else 24.0), aim.y * (10.0 if has_boss else 18.0))
        if has_boss:
            vertical_bias = BOSS_VERTICAL_COMPOSITION_BIAS
    else:
        target += Vector2(aim.x * AIM_LOOK_AHEAD_X, aim.y * AIM_LOOK_AHEAD_Y)
    target += Vector2(0.0, vertical_bias)
    return target

func debug_camera_contract() -> Dictionary:
    return {
        "aim_look_ahead_x": AIM_LOOK_AHEAD_X,
        "aim_look_ahead_y": AIM_LOOK_AHEAD_Y,
        "vertical_composition_bias": VERTICAL_COMPOSITION_BIAS,
        "boss_vertical_composition_bias": BOSS_VERTICAL_COMPOSITION_BIAS,
        "squad_weight": SQUAD_WEIGHT,
        "combat_target_weight": COMBAT_TARGET_WEIGHT,
        "boss_combat_target_weight": BOSS_COMBAT_TARGET_WEIGHT,
        "max_combat_target_distance": MAX_COMBAT_TARGET_DISTANCE,
        "target_aware_combat_frame": true,
        "boss_safe_frame": true,
        "boss_large_silhouette_clearance": true,
        "player_lower_left_bias": true,
        "hostile_upper_right_bias": true,
        "m7_camera": true
    }

func debug_target_for_active() -> Vector2:
    if stage == null or stage.squad == null:
        return Vector2.ZERO
    var active := stage.squad.get_active_operator()
    if active == null:
        return Vector2.ZERO
    return _target_for_active(active)
