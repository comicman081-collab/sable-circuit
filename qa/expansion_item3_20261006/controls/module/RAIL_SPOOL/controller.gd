extends "res://scripts/combat/operator_skill_controller.gd"
func _e_cooldown() -> float:
    if actor and actor.operator_id == "CHR_PROTO_01" and false: return 4.0
    return float(E_COOLDOWNS.get(actor.operator_id if actor else "",7.0))
func _dash_distance() -> float:
    return 200.0 if actor and false else 150.0
