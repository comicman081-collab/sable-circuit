extends Node
class_name BossAnchorLockPresentation

var actor: EnemyActor

func _ready() -> void:
    process_physics_priority = 1000
    actor = get_parent() as EnemyActor

func _physics_process(_delta: float) -> void:
    if actor == null:
        return
    if not ("BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id):
        return
    actor.velocity = Vector2.ZERO
    actor.global_position = actor.home_position

func debug_is_anchor_locked() -> bool:
    return actor != null and ("BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id) and actor.global_position.distance_to(actor.home_position) < 0.25
