extends "res://scripts/missions/story_stage_01.gd"
const MutantIntel := preload("res://.cache/diag/expansion_item3_20261006/intel_controls/generic_boss_first/intel.gd")
func _award_enemy_intel(enemy_id: String) -> void:
    var id := enemy_id.to_upper()
    if _intel_seen_enemy_ids.has(id): return
    _intel_seen_enemy_ids.append(id)
    var key := MutantIntel.enemy_key(id)
    if key.is_empty(): return
    _cargo_intel[key] = int(_cargo_intel.get(key,0)) + 1
    hud.set_intel_status(_cargo_intel)

