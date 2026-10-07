extends RefCounted
class_name CombatFeedback

const HIT_VFX := preload("res://scripts/vfx/combat_hit_vfx.gd")
const EXPLOSION_VFX := preload("res://scripts/vfx/combat_explosion_vfx.gd")
const SFX := preload("res://scripts/audio/combat_sfx_bank.gd")
## Blasts that happen on the floor and leave scorch under the bodies.
const SCORCHING := ["ROBOT_HEAVY", "BOSS", "MORTAR", "VOLATILE", "SLAM"]

static func play_fire(tree: SceneTree, art_profile: Dictionary, emitter: Node = null) -> void:
    var id_value := str(art_profile.get("fire_sfx_profile", ""))
    if not id_value.is_empty():
        SFX.play(tree, id_value, emitter)

## incoming is the round's travel direction; impact sparks spray back off the struck face.
## `visual_profile` replaces the weapon's impact look (an armour deflect, a boss guard)
## while its impact sound still plays: one effect per hit, not two stacked.
static func spawn_hit(tree: SceneTree, world_pos: Vector2, art_profile: Dictionary, tint: Color, emitter: Node = null, incoming: Vector2 = Vector2.ZERO, visual_profile := "") -> void:
    if tree == null:
        return
    var vfx := HIT_VFX.new() as CombatHitVFX
    tree.root.add_child(vfx)
    vfx.global_position = world_pos
    vfx.setup(visual_profile if not visual_profile.is_empty() else str(art_profile.get("hit_vfx_profile", "HIT_GENERIC")), tint, -incoming)
    var sfx_id := str(art_profile.get("impact_sfx_profile", ""))
    if not sfx_id.is_empty():
        SFX.play(tree, sfx_id, emitter, world_pos)

## An impact visual alone, with no sound (showcases and tests).
static func spawn_hit_visual(tree: SceneTree, world_pos: Vector2, profile_id: String, tint: Color, incoming: Vector2 = Vector2.ZERO) -> void:
    if tree == null:
        return
    var vfx := HIT_VFX.new() as CombatHitVFX
    tree.root.add_child(vfx)
    vfx.global_position = world_pos
    vfx.setup(profile_id, tint, -incoming)

## Rounds absorbed by cover: the visual hit with concrete dust and chips, plus concrete
## thud and, now and then, a glancing ricochet instead of the weapon's flesh/armour impact.
static func spawn_cover_hit(tree: SceneTree, world_pos: Vector2, art_profile: Dictionary, tint: Color, emitter: Node = null, incoming: Vector2 = Vector2.ZERO) -> void:
    if tree == null:
        return
    var vfx := HIT_VFX.new() as CombatHitVFX
    tree.root.add_child(vfx)
    vfx.global_position = world_pos
    vfx.setup(str(art_profile.get("hit_vfx_profile", "HIT_GENERIC")), tint, -incoming)
    vfx.mark_cover_surface()
    SFX.play(tree, "ricochet" if randf() < 0.3 else "impact_concrete", emitter, world_pos)

## The damaged target's own reaction, scaled by how much of its health the hit took:
## FLINCH under 4%, LIGHT from 4%, HEAVY from 14%, DOWNED when it drops to zero.
static func spawn_hurt(tree: SceneTree, world_pos: Vector2, target_kind: String, target_id: String, reaction: String, tint: Color, critical: bool = false) -> void:
    if tree == null:
        return
    var vfx := HIT_VFX.new() as CombatHitVFX
    tree.root.add_child(vfx)
    vfx.global_position = world_pos
    vfx.setup_hurt(target_kind, target_id, reaction, tint, critical)

static func hurt_reaction(applied: float, health_after: float, max_health: float) -> String:
    if health_after <= 0.0: return "DOWNED"
    var ratio := applied / maxf(1.0, max_health)
    if ratio >= 0.14: return "HEAVY"
    if ratio >= 0.04: return "LIGHT"
    return "FLINCH"

## A blast drawn at the radius the caller's damage uses (see CombatExplosionVFX.KINDS).
## Floor-level kinds also leave scorch at `ground` (the blast point when not given).
static func spawn_explosion(tree: SceneTree, world_pos: Vector2, kind: String, tint: Color, radius: float, direction := Vector2.RIGHT, reach := 0.0, ground := Vector2.INF) -> CombatExplosionVFX:
    if tree == null or tree.root == null:
        return null
    var fx := EXPLOSION_VFX.new() as CombatExplosionVFX
    tree.root.add_child(fx)
    fx.global_position = world_pos
    fx.setup(kind, tint, radius, direction, reach)
    if kind.to_upper() in SCORCHING:
        var mark := EXPLOSION_VFX.GroundMark.new()
        tree.root.add_child(mark)
        mark.global_position = ground if ground.is_finite() else world_pos
        mark.setup(radius * (0.55 if kind.to_upper() == "BOSS" else 0.75), tint if kind.to_upper() in EXPLOSION_VFX.ENERGY_KINDS else Color("ff7a2a"))
    return fx

## A robot's destruction, sized and styled by its body: flyers burst in the air and rain
## parts, ground machines blow apart on the floor, bosses go in a chain of blasts.
static func spawn_destruction(tree: SceneTree, enemy: Node2D, rect: Rect2, enemy_id: String, tint: Color) -> CombatExplosionVFX:
    var id := enemy_id.to_upper()
    if id.begins_with("BOSS_"):
        return spawn_explosion(tree, rect.get_center(), "BOSS", tint, maxf(rect.size.x, rect.size.y) * 0.62, Vector2.RIGHT, 0.0, enemy.global_position)
    if "DRONE" in id or "PRISM" in id:
        return spawn_explosion(tree, rect.get_center(), "ROBOT_SMALL", tint, 62.0)
    return spawn_explosion(tree, rect.get_center(), "ROBOT_HEAVY", tint, 82.0, Vector2.RIGHT, 0.0, enemy.global_position)

## Extra one-shot layer (armour deflect, guard block) at a world position.
static func play_layer(tree: SceneTree, cue: String, emitter: Node, world_pos: Vector2) -> void:
    SFX.play(tree, cue, emitter, world_pos)
