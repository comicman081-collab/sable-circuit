extends Node
class_name BossPhaseTransitionGuard

const PHASE3_THRESHOLD := 0.33
const PHASE3_GUARD_SECONDS := 8.0

var actor: EnemyActor
var _phase3_seen := false
var _guard_left := 0.0
var _removed_target_group := false

func _ready() -> void:
    process_physics_priority = -1000
    actor = get_parent() as EnemyActor

func _physics_process(delta: float) -> void:
    if actor == null or not is_instance_valid(actor):
        return
    if not ("BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id):
        return

    var ratio := actor.health / maxf(1.0, actor.max_health)
    if not _phase3_seen and ratio <= PHASE3_THRESHOLD and actor.health > 0.0:
        _phase3_seen = true
        _guard_left = PHASE3_GUARD_SECONDS
        if actor.is_in_group("prototype_targets"):
            actor.remove_from_group("prototype_targets")
            actor.add_to_group("site7_guarded_targets")
            _removed_target_group = true

    if _guard_left > 0.0:
        _guard_left = maxf(0.0, _guard_left - delta)
        if _guard_left <= 0.0 and _removed_target_group and is_instance_valid(actor) and actor.health > 0.0:
            actor.add_to_group("prototype_targets")
            actor.remove_from_group("site7_guarded_targets")
            _removed_target_group = false

func debug_guard_active() -> bool:
    return _guard_left > 0.0 and _removed_target_group

func debug_guard_seconds() -> float:
    return PHASE3_GUARD_SECONDS
