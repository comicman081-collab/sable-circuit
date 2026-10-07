extends "res://scripts/combat/operator_skill_controller.gd"
func _q_cooldown() -> float:
    if actor and actor.operator_id == "CHR_PROTO_01" and false: return 3.2
    return float(Q_COOLDOWNS.get(actor.operator_id if actor else "",5.0))
