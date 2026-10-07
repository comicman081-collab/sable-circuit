extends Node
class_name EnemyFieldScalePresentation

var actor: EnemyActor
var _applied_scale: float = 1.0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    call_deferred("_apply")

func _apply() -> void:
    if not is_instance_valid(actor) or actor.is_queued_for_deletion():
        return
    var visual_root := actor.get("_visual_root") as Node2D
    if visual_root == null:
        return
    var factor := 1.14
    if "DRONE" in actor.enemy_id:
        factor = 0.95
    elif "SHIELD" in actor.enemy_id:
        factor = 1.18
    elif "ABERRANT" in actor.enemy_id:
        factor = 1.10
    elif "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id:
        factor = 0.84
    _applied_scale = factor
    visual_root.scale = Vector2.ONE * factor
    var shadow := actor.get_node_or_null("GroundShadow") as Node2D
    if shadow:
        shadow.scale = Vector2.ONE * (0.82 if factor < 0.82 else 0.92)
    var overhead := actor.get_node_or_null("OverheadUI") as Node2D
    if overhead and factor < 0.82:
        overhead.scale = Vector2.ONE * 0.88

func debug_scale() -> float:
    return _applied_scale

func debug_scaled_for_field() -> bool:
    return _applied_scale <= 1.18
