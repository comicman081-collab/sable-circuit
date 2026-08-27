extends Node
class_name SquadCameraPresentation

const AIM_LOOK_AHEAD_X := 92.0
const AIM_LOOK_AHEAD_Y := 62.0
const VERTICAL_SAFE_BIAS := 22.0
const SQUAD_WEIGHT := 0.22
const FOLLOW_RATE := 8.2

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
    var blend := 1.0 - pow(0.00035, delta * FOLLOW_RATE / 8.2)
    camera.global_position = camera.global_position.lerp(target, blend)

func _target_for_active(active: OperatorActor) -> Vector2:
    var centroid := active.global_position
    var count := 1.0
    if stage and stage.squad:
        centroid = Vector2.ZERO
        count = 0.0
        for actor in stage.squad.operators:
            if actor != null and not actor.is_downed():
                centroid += actor.global_position
                count += 1.0
        if count > 0.0:
            centroid /= count
        else:
            centroid = active.global_position
    var anchor := active.global_position.lerp(centroid, SQUAD_WEIGHT)
    var aim := active.aim_world.normalized() if active.aim_world.length_squared() > 0.001 else Vector2.RIGHT
    var look_ahead := Vector2(aim.x * AIM_LOOK_AHEAD_X, aim.y * AIM_LOOK_AHEAD_Y)
    return anchor + look_ahead + Vector2(0.0, VERTICAL_SAFE_BIAS)

func debug_camera_contract() -> Dictionary:
    return {
        "aim_look_ahead_x": AIM_LOOK_AHEAD_X,
        "aim_look_ahead_y": AIM_LOOK_AHEAD_Y,
        "vertical_safe_bias": VERTICAL_SAFE_BIAS,
        "squad_weight": SQUAD_WEIGHT,
        "player_left_of_aim": true,
        "compact_squad_safe": true
    }

func debug_target_for_active() -> Vector2:
    if stage == null or stage.squad == null:
        return Vector2.ZERO
    var active := stage.squad.get_active_operator()
    if active == null:
        return Vector2.ZERO
    return _target_for_active(active)
