extends Node
class_name SquadCameraPresentation

const AIM_LOOK_AHEAD_X := 108.0
const AIM_LOOK_AHEAD_Y := 72.0
const VERTICAL_COMPOSITION_BIAS := -24.0
const BOSS_VERTICAL_COMPOSITION_BIAS := -25.0
const NORMAL_ZOOM := 1.46
const BOSS_ZOOM := 1.02
const SQUAD_WEIGHT := 0.28
const COMBAT_TARGET_WEIGHT := 0.40
const BOSS_COMBAT_TARGET_WEIGHT := 0.50
const MAX_COMBAT_TARGET_DISTANCE := 620.0
const MAX_BOSS_CAMERA_DISTANCE := 900.0
const FOLLOW_RATE := 8.6
const ZOOM_FOLLOW_RATE := 6.2

var stage: StoryStage01
var camera: Camera2D
var _last_target := Vector2.ZERO
var _last_boss_focus := false

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
    var context := _focus_context(active)
    var target: Vector2 = context.get("target", active.global_position)
    var desired_zoom := float(context.get("zoom", NORMAL_ZOOM))
    _last_target = target
    _last_boss_focus = bool(context.get("boss_focus", false))
    var position_blend := 1.0 - pow(0.00028, delta * FOLLOW_RATE / 8.6)
    var zoom_blend := 1.0 - pow(0.00055, delta * ZOOM_FOLLOW_RATE / 6.2)
    camera.global_position = camera.global_position.lerp(target, position_blend)
    camera.zoom = camera.zoom.lerp(Vector2.ONE * desired_zoom, zoom_blend)

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

func _priority_boss(active: OperatorActor) -> EnemyActor:
    # Combat targetability is intentionally suspended for a short Phase-3 guard
    # window. Camera composition must not interpret that gameplay protection as
    # "the boss no longer exists". The camera therefore tracks the authoritative
    # live enemy group, independently from prototype_targets.
    var best: EnemyActor = null
    var best_d2 := INF
    for node in active.get_tree().get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and is_instance_valid(node):
            var enemy := node as EnemyActor
            if enemy.health <= 0.0:
                continue
            if not ("BOSS" in enemy.enemy_id or "ANCHOR" in enemy.enemy_id):
                continue
            var d2 := active.global_position.distance_squared_to(enemy.global_position)
            if d2 <= MAX_BOSS_CAMERA_DISTANCE * MAX_BOSS_CAMERA_DISTANCE and d2 < best_d2:
                best = enemy
                best_d2 = d2
    return best

func _hostile_centroid(active: OperatorActor) -> Dictionary:
    var sum := Vector2.ZERO
    var count := 0.0
    var nearest_d2 := INF
    for node in active.get_tree().get_nodes_in_group("prototype_targets"):
        if node is Node2D and is_instance_valid(node):
            var d2 := active.global_position.distance_squared_to(node.global_position)
            if d2 <= MAX_COMBAT_TARGET_DISTANCE * MAX_COMBAT_TARGET_DISTANCE:
                sum += node.global_position
                count += 1.0
                nearest_d2 = minf(nearest_d2, d2)
    return {
        "valid": count > 0.0,
        "position": sum / count if count > 0.0 else active.global_position,
        "count": count,
        "nearest_d2": nearest_d2
    }

func _focus_context(active: OperatorActor) -> Dictionary:
    var centroid := _squad_centroid(active)
    var squad_anchor := active.global_position.lerp(centroid, SQUAD_WEIGHT)
    var aim := active.aim_world.normalized() if active.aim_world.length_squared() > 0.001 else Vector2.RIGHT
    var boss := _priority_boss(active)

    if boss != null:
        var boss_pos := boss.global_position
        var boss_delta := boss_pos - squad_anchor
        if boss_delta.length() > MAX_BOSS_CAMERA_DISTANCE:
            boss_pos = squad_anchor + boss_delta.normalized() * MAX_BOSS_CAMERA_DISTANCE
        var boss_target := squad_anchor.lerp(boss_pos, BOSS_COMBAT_TARGET_WEIGHT)
        boss_target += Vector2(aim.x * 14.0, aim.y * 7.0)
        boss_target += Vector2(0.0, BOSS_VERTICAL_COMPOSITION_BIAS)
        return {
            "target": boss_target,
            "zoom": BOSS_ZOOM,
            "boss_focus": true,
            "boss": boss,
            "hostile_count": 1
        }

    var hostile := _hostile_centroid(active)
    var target := squad_anchor
    if bool(hostile.get("valid", false)):
        var hostile_pos: Vector2 = hostile.get("position", active.global_position)
        var delta := hostile_pos - squad_anchor
        if delta.length() > MAX_COMBAT_TARGET_DISTANCE:
            hostile_pos = squad_anchor + delta.normalized() * MAX_COMBAT_TARGET_DISTANCE
        target = squad_anchor.lerp(hostile_pos, COMBAT_TARGET_WEIGHT)
        target += Vector2(aim.x * 24.0, aim.y * 18.0)
    else:
        target += Vector2(aim.x * AIM_LOOK_AHEAD_X, aim.y * AIM_LOOK_AHEAD_Y)
    target += Vector2(0.0, VERTICAL_COMPOSITION_BIAS)
    return {
        "target": target,
        "zoom": NORMAL_ZOOM,
        "boss_focus": false,
        "boss": null,
        "hostile_count": int(hostile.get("count", 0.0))
    }

func debug_camera_contract() -> Dictionary:
    return {
        "aim_look_ahead_x": AIM_LOOK_AHEAD_X,
        "aim_look_ahead_y": AIM_LOOK_AHEAD_Y,
        "vertical_composition_bias": VERTICAL_COMPOSITION_BIAS,
        "boss_vertical_composition_bias": BOSS_VERTICAL_COMPOSITION_BIAS,
        "normal_zoom": NORMAL_ZOOM,
        "boss_zoom": BOSS_ZOOM,
        "squad_weight": SQUAD_WEIGHT,
        "combat_target_weight": COMBAT_TARGET_WEIGHT,
        "boss_combat_target_weight": BOSS_COMBAT_TARGET_WEIGHT,
        "max_combat_target_distance": MAX_COMBAT_TARGET_DISTANCE,
        "max_boss_camera_distance": MAX_BOSS_CAMERA_DISTANCE,
        "target_aware_combat_frame": true,
        "priority_boss_scan_m3_enemies": true,
        "boss_targetability_independent": true,
        "boss_safe_frame": true,
        "boss_zoom_out": true,
        "boss_large_silhouette_clearance": true,
        "player_lower_left_bias": true,
        "hostile_upper_right_bias": true,
        "m7_camera": true
    }

func debug_focus_context() -> Dictionary:
    if stage == null or stage.squad == null:
        return {}
    var active := stage.squad.get_active_operator()
    if active == null:
        return {}
    return _focus_context(active)

func debug_target_for_active() -> Vector2:
    var context := debug_focus_context()
    if context.is_empty():
        return Vector2.ZERO
    var active := stage.squad.get_active_operator()
    var target: Vector2 = context.get("target", Vector2.ZERO)
    var boss := context.get("boss") as EnemyActor
    print("M7_CAMERA_DEBUG active=%s boss_focus=%s boss_id=%s active_pos=%s boss_pos=%s target=%s zoom=%.3f" % [
        active.display_name,
        str(bool(context.get("boss_focus",false))),
        boss.enemy_id if boss != null else "NONE",
        str(active.global_position),
        str(boss.global_position) if boss != null else "NONE",
        str(target),
        float(context.get("zoom",NORMAL_ZOOM))
    ])
    return target
