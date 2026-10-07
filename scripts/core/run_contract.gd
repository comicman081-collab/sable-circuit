extends RefCounted
class_name RunContract

const DATA_PATH := "res://data/progression/run_modifiers.json"
const MissionCatalog := preload("res://scripts/core/site7_campaign.gd")
# First setting, set by Claude on the user's delegation (2026-10-04); no human play yet. Order doc 9.11.
const REDLINE_HEALTH := 1.35
const REDLINE_DAMAGE := 1.25
const REDLINE_SPEED := 1.12
const REDLINE_INTERVAL := 0.85
const REDLINE_HAZARD_REWARD := 1.60
const REDLINE_OPPORTUNITY_REWARD := 1.50

## The first offer is the shipped contract, including its original key set.
## Keep one recovery priority across the three risk cards: a higher risk never
## trades away a resource multiplier merely because its opportunity changed.
static func offers(run_id: String, mission_id: String) -> Array[Dictionary]:
    var first := build(run_id)
    var out: Array[Dictionary] = [first]
    var data := _load_data()
    var hazards: Array = data.get("hazards", [])
    var others: Array[Dictionary] = []
    for row: Dictionary in hazards:
        if str(row.get("id", "")) != str(first.hazard_id): others.append(row)
    var offset := _stable_index(run_id + "|" + mission_id + "|OFFERS", others.size())
    for i in range(mini(2, others.size())):
        var hazard: Dictionary = others[(offset + i) % others.size()]
        var offer := first.duplicate(true)
        var old_reward := 1.0
        for row: Dictionary in hazards:
            if str(row.get("id", "")) == str(first.hazard_id): old_reward = clampf(float(row.get("reward_multiplier", 1.0)), 1.0, 2.0)
        var reward := clampf(float(hazard.get("reward_multiplier", 1.0)), 1.0, 2.0)
        offer.hazard_id = str(hazard.id)
        offer.hazard_title = str(hazard.title)
        offer.risk_score = clampi(int(hazard.get("risk_score", 0)), 0, 10)
        for key in ["enemy_health_multiplier", "enemy_damage_multiplier", "enemy_speed_multiplier", "enemy_attack_interval_multiplier"]:
            offer[key] = clampf(float(hazard.get(key, 1.0)), 0.5, 2.0 if key in ["enemy_speed_multiplier", "enemy_attack_interval_multiplier"] else 3.0)
        for key in ["research_reward_multiplier", "salvage_reward_multiplier", "fragment_reward_multiplier"]:
            offer[key] = float(first[key]) / old_reward * reward
        out.append(offer)
    return out

static func redline(run_id: String) -> Dictionary:
    var contract := build(run_id)
    contract.merge({"hazard_id":"REDLINE", "hazard_title":"REDLINE", "opportunity_id":"REDLINE_RECOVERY", "opportunity_title":"MAXIMUM RECOVERY",
        "risk_score":5, "redline":true, "enemy_health_multiplier":REDLINE_HEALTH, "enemy_damage_multiplier":REDLINE_DAMAGE,
        "enemy_speed_multiplier":REDLINE_SPEED, "enemy_attack_interval_multiplier":REDLINE_INTERVAL}, true)
    for key in ["research_reward_multiplier", "salvage_reward_multiplier", "fragment_reward_multiplier"]:
        contract[key] = REDLINE_HAZARD_REWARD * REDLINE_OPPORTUNITY_REWARD
    return contract

static func redline_available(mission_id: String, cleared: Array) -> bool:
    return cleared.has(mission_id) and MissionCatalog.available(mission_id, cleared)

static func is_redline(contract: Dictionary) -> bool:
    return str(contract.get("hazard_id", "")) == "REDLINE" and str(contract.get("opportunity_id", "")) == "REDLINE_RECOVERY"

static func identity(contract: Dictionary) -> String:
    if contract.is_empty(): return "NEUTRAL"
    return str(contract.get("hazard_id", "NEUTRAL")) + "/" + str(contract.get("opportunity_id", "STANDARD_RECOVERY"))

## REDLINE keeps boss recovery/movement timing and every authored warning intact.
## The existing projectile damage multiplier is still applied by EnemyActor.
static func enemy_modifiers(contract: Dictionary, enemy_id: String) -> Dictionary:
    var out := contract.duplicate(true)
    if is_redline(contract) and enemy_id.begins_with("BOSS_"):
        out["enemy_speed_multiplier"] = 1.0
        out["enemy_attack_interval_multiplier"] = 1.0
    return out

static func effect_text(contract: Dictionary) -> String:
    return "HP %+d%%  /  DAMAGE %+d%%  /  SPEED %+d%%  /  ATTACK GAP %+d%%\nREWARDS  RESEARCH ×%.2f  /  SALVAGE ×%.2f  /  SIGNAL ×%.2f" % [
        roundi((float(contract.get("enemy_health_multiplier", 1.0)) - 1.0) * 100),
        roundi((float(contract.get("enemy_damage_multiplier", 1.0)) - 1.0) * 100),
        roundi((float(contract.get("enemy_speed_multiplier", 1.0)) - 1.0) * 100),
        roundi((float(contract.get("enemy_attack_interval_multiplier", 1.0)) - 1.0) * 100),
        float(contract.get("research_reward_multiplier", 1.0)), float(contract.get("salvage_reward_multiplier", 1.0)), float(contract.get("fragment_reward_multiplier", 1.0))]

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
