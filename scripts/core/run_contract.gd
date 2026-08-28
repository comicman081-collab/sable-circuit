extends RefCounted
class_name RunContract

const DATA_PATH := "res://data/progression/run_modifiers.json"

static func build(run_id: String) -> Dictionary:
    var data := _load_data()
    var hazards: Array = data.get("hazards", [])
    var opportunities: Array = data.get("opportunities", [])
    var boosts: Array = data.get("run_only_boosts", [])
    if hazards.is_empty() or opportunities.is_empty():
        return _neutral(run_id, boosts)

    var hazard: Dictionary = hazards[_stable_index(run_id + "|HAZARD", hazards.size())].duplicate(true)
    var opportunity: Dictionary = opportunities[_stable_index(run_id + "|OPPORTUNITY", opportunities.size())].duplicate(true)
    var hazard_reward := clampf(float(hazard.get("reward_multiplier", 1.0)), 1.0, 2.0)

    return {
        "schema_version": 1,
        "run_id": run_id,
        "seed_signature": _stable_hash(run_id),
        "hazard_id": str(hazard.get("id", "NEUTRAL")),
        "hazard_title": str(hazard.get("title", "NEUTRAL")),
        "opportunity_id": str(opportunity.get("id", "STANDARD_RECOVERY")),
        "opportunity_title": str(opportunity.get("title", "STANDARD RECOVERY")),
        "risk_score": clampi(int(hazard.get("risk_score", 0)), 0, 10),
        "enemy_health_multiplier": clampf(float(hazard.get("enemy_health_multiplier", 1.0)), 0.5, 3.0),
        "enemy_damage_multiplier": clampf(float(hazard.get("enemy_damage_multiplier", 1.0)), 0.5, 3.0),
        "enemy_speed_multiplier": clampf(float(hazard.get("enemy_speed_multiplier", 1.0)), 0.5, 2.0),
        "enemy_attack_interval_multiplier": clampf(float(hazard.get("enemy_attack_interval_multiplier", 1.0)), 0.5, 2.0),
        "research_reward_multiplier": hazard_reward * clampf(float(opportunity.get("research_reward_multiplier", 1.0)), 0.5, 3.0),
        "salvage_reward_multiplier": hazard_reward * clampf(float(opportunity.get("salvage_reward_multiplier", 1.0)), 0.5, 3.0),
        "fragment_reward_multiplier": hazard_reward * clampf(float(opportunity.get("fragment_reward_multiplier", 1.0)), 0.5, 3.0),
        "run_only_boosts": boosts.duplicate(true)
    }

static func _neutral(run_id: String, boosts: Array = []) -> Dictionary:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "seed_signature": _stable_hash(run_id),
        "hazard_id": "NEUTRAL",
        "hazard_title": "NEUTRAL",
        "opportunity_id": "STANDARD_RECOVERY",
        "opportunity_title": "STANDARD RECOVERY",
        "risk_score": 0,
        "enemy_health_multiplier": 1.0,
        "enemy_damage_multiplier": 1.0,
        "enemy_speed_multiplier": 1.0,
        "enemy_attack_interval_multiplier": 1.0,
        "research_reward_multiplier": 1.0,
        "salvage_reward_multiplier": 1.0,
        "fragment_reward_multiplier": 1.0,
        "run_only_boosts": boosts.duplicate(true)
    }

static func _load_data() -> Dictionary:
    if not FileAccess.file_exists(DATA_PATH):
        push_warning("RunContract missing run modifier registry")
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
    if parsed is Dictionary:
        return parsed
    push_warning("RunContract ignored malformed run modifier registry")
    return {}

static func _stable_index(text: String, count: int) -> int:
    if count <= 0:
        return 0
    return _stable_hash(text) % count

static func _stable_hash(text: String) -> int:
    # Small deterministic hash that does not touch Godot's global RNG state.
    var value: int = 146959810
    for i in range(text.length()):
        value = int(((value ^ text.unicode_at(i)) * 16777619) % 2147483647)
    return maxi(0, value)
