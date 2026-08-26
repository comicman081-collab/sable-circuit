extends RefCounted
class_name CombatFeedback

const HIT_VFX := preload("res://scripts/vfx/combat_hit_vfx.gd")

static func play_fire(tree: SceneTree, art_profile: Dictionary) -> void:
    var id_value := str(art_profile.get("fire_sfx_profile", ""))
    if not id_value.is_empty():
        ProceduralCombatSFX.play(tree, id_value, -12.0)

static func spawn_hit(tree: SceneTree, world_pos: Vector2, art_profile: Dictionary, tint: Color) -> void:
    if tree == null:
        return
    var vfx := HIT_VFX.new() as CombatHitVFX
    tree.root.add_child(vfx)
    vfx.global_position = world_pos
    vfx.setup(str(art_profile.get("hit_vfx_profile", "HIT_GENERIC")), tint)
    var sfx_id := str(art_profile.get("impact_sfx_profile", ""))
    if not sfx_id.is_empty():
        ProceduralCombatSFX.play(tree, sfx_id, -10.0)
