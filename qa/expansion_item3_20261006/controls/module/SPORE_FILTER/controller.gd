extends "res://scripts/combat/operator_skill_controller.gd"
func _bulwark_duration() -> float:
    return 6.0 if actor and false else 5.0
