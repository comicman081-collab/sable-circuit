extends Node2D
class_name EliteAffix
## Elite variant of an existing robot (data/progression/elite_affixes.json).
## SHIELDED soaks damage with a recharging barrier, OVERCHARGED hits harder and
## sooner, VOLATILE bursts on death after a warning circle. The variant is shown
## with a code-drawn ring and the overhead label; robot art is never tinted.

const DATA_PATH := "res://data/progression/elite_affixes.json"
const BLAST := preload("res://scripts/combat/elite_volatile_blast.gd")
const Painter := preload("res://scripts/vfx/vfx_painter.gd")

static var _table: Dictionary = {}

var affix_id := ""
var spec: Dictionary = {}
var color := Color.WHITE
var barrier := 0.0
var barrier_max := 0.0
var _since_damage := 0.0
var _phase := 0.0
var _defeat_handled := false
var _paint := Painter.new()

static func table() -> Dictionary:
    if _table.is_empty():
        var parsed = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
        _table = (parsed.get("affixes", {}) as Dictionary) if parsed is Dictionary else {}
    return _table

## Adds the affix to an enemy that has its encounter health set. Unknown or empty ids do nothing.
static func apply(enemy: EnemyActor, id_value: String) -> EliteAffix:
    var key := id_value.strip_edges().to_upper()
    if enemy.enemy_id.begins_with("BOSS_") or enemy.brood_generation > 0:
        return null
    if key.is_empty() or not table().has(key) or enemy.get_node_or_null("EliteAffix") != null:
        return null
    var affix := EliteAffix.new()
    affix.name = "EliteAffix"
    affix.affix_id = key
    affix.spec = (table()[key] as Dictionary).duplicate(true)
    affix.color = Color(str(affix.spec.get("color", "ffffff")))
    enemy.run_damage_multiplier *= float(affix.spec.get("damage_multiplier", 1.0))
    enemy.run_attack_interval_multiplier *= float(affix.spec.get("attack_interval_multiplier", 1.0))
    enemy.run_speed_multiplier *= float(affix.spec.get("speed_multiplier", 1.0))
    affix.barrier_max = enemy.max_health * float(affix.spec.get("barrier_ratio", 0.0))
    affix.barrier = affix.barrier_max
    enemy.add_child(affix)
    return affix

static func tip(id_value: String) -> String:
    return str(table().get(id_value.strip_edges().to_upper(), {}).get("tip", ""))

func _ready() -> void:
    z_index = -1
    show_behind_parent = true
    if affix_id == "BEACON": add_to_group("elite_beacons")

func title() -> String:
    return str(spec.get("title", affix_id))

## Returns the damage left after the barrier. The regen timer restarts on every hit.
func absorb(amount: float) -> float:
    _since_damage = 0.0
    if barrier <= 0.0: return amount
    var soaked := minf(barrier, amount)
    barrier -= soaked
    var owner_enemy := get_parent() as EnemyActor
    if owner_enemy != null and owner_enemy.is_inside_tree():
        var sfx := preload("res://scripts/audio/combat_sfx_bank.gd")
        sfx.play(get_tree(), "shield_break" if barrier <= 0.0 else "shield_hit", owner_enemy)
    return amount - soaked

## Called once when the robot is destroyed.
func on_defeated() -> void:
    if _defeat_handled: return
    _defeat_handled = true
    var enemy := get_parent() as EnemyActor
    if enemy == null or enemy.get_parent() == null: return
    if affix_id == "BEACON":
        remove_from_group("elite_beacons")
        return
    if affix_id == "BROODING":
        var stage := enemy.get_parent()
        if stage.has_method("spawn_elite_brood"):
            stage.call("spawn_elite_brood", enemy, spec)
        return
    if affix_id != "VOLATILE": return
    var blast := BLAST.new()
    blast.setup(enemy.global_position, enemy.enemy_id, color,
        float(spec.get("death_blast_radius", 150.0)), float(spec.get("death_blast_damage", 22.0)) * enemy.run_damage_multiplier,
        float(spec.get("death_blast_windup", 0.9)))
    enemy.get_parent().add_child(blast)

## Fresh health/position checks on each hit avoid a cached aura outliving its source.
## A robot receives the strongest eligible beacon once, before its own barrier.
static func beacon_for(enemy: EnemyActor) -> EliteAffix:
    if enemy == null or not enemy.is_inside_tree() or enemy.health <= 0.0: return null
    var best: EliteAffix = null
    var reduction := 0.0
    for node in enemy.get_tree().get_nodes_in_group("elite_beacons"):
        var beacon := node as EliteAffix
        if beacon == null or beacon.is_queued_for_deletion(): continue
        var source := beacon.get_parent() as EnemyActor
        if source == null or source == enemy or source.health <= 0.0 or source.is_queued_for_deletion(): continue
        if source.get_parent() != enemy.get_parent(): continue
        var radius := float(beacon.spec.get("beacon_radius", 360.0))
        if source.global_position.distance_squared_to(enemy.global_position) > radius * radius: continue
        var value := clampf(float(beacon.spec.get("beacon_reduction", 0.0)), 0.0, 0.35)
        if value > reduction or (is_equal_approx(value, reduction) and best != null and beacon.get_instance_id() < best.get_instance_id()):
            best = beacon
            reduction = value
    return best

static func protected_damage(enemy: EnemyActor, amount: float) -> float:
    var beacon := beacon_for(enemy)
    return amount * (1.0 - clampf(float(beacon.spec.get("beacon_reduction", 0.0)), 0.0, 0.35)) if beacon != null else amount

## Every living peer inside the radius receives the aura. Only the drawn
## links, not damage protection, have a six-peer display budget.
func protected_enemies() -> Array[EnemyActor]:
    var result: Array[EnemyActor] = []
    var source := get_parent() as EnemyActor
    if affix_id != "BEACON" or source == null or source.health <= 0.0 or not source.is_inside_tree(): return result
    var radius := float(spec.get("beacon_radius", 360.0))
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        var peer := node as EnemyActor
        if peer == null or peer == source or peer.health <= 0.0 or peer.is_queued_for_deletion(): continue
        if peer.get_parent() != source.get_parent(): continue
        if source.global_position.distance_to(peer.global_position) <= radius: result.append(peer)
    result.sort_custom(func(a: EnemyActor, b: EnemyActor) -> bool:
        var da := source.global_position.distance_squared_to(a.global_position)
        var db := source.global_position.distance_squared_to(b.global_position)
        return a.get_instance_id() < b.get_instance_id() if is_equal_approx(da, db) else da < db)
    return result

func linked_enemies() -> Array[EnemyActor]:
    var result: Array[EnemyActor] = []
    for peer in protected_enemies():
        if beacon_for(peer) == self: result.append(peer)
    result.resize(mini(result.size(), mini(6, maxi(0, int(spec.get("beacon_max_links", 6))))))
    return result

func _process(delta: float) -> void:
    _phase += delta
    _since_damage += delta
    if barrier_max > 0.0 and barrier < barrier_max and _since_damage >= float(spec.get("barrier_regen_delay", 4.0)):
        barrier = minf(barrier_max, barrier + barrier_max * float(spec.get("barrier_regen_per_second", 0.25)) * delta)
    queue_redraw()

func _draw() -> void:
    var enemy := get_parent() as EnemyActor
    if enemy == null or enemy.health <= 0.0 or not enemy.is_inside_tree(): return
    # A rotating broken floor ring (outside the exposed/stagger arcs) marks the variant;
    # the barrier itself is shown on the overhead bar.
    var radius := clampf(enemy.get_combat_hit_rect().size.x * 0.42, 46.0, 96.0)
    draw_set_transform(Vector2(0, 6), 0.0, Vector2(1.0, 0.46))
    for i in range(3):
        var start := _phase * 1.4 + float(i) * TAU / 3.0
        draw_arc(Vector2.ZERO, radius, start, start + 1.55, 20, Color(color, 0.78), 3.4)
    draw_arc(Vector2.ZERO, radius + 7.0, 0.0, TAU, 48, Color(color, 0.2), 1.6)
    draw_set_transform(Vector2.ZERO)
    if affix_id == "BEACON":
        _paint.clear()
        for peer in linked_enemies():
            _paint.beam(Vector2(0, 6), to_local(peer.global_position) + Vector2(0, 6), 2.0, Color(color, 0.48))
        _paint.flush(get_canvas_item())

func barrier_share() -> float:
    return barrier / barrier_max if barrier_max > 0.0 else 0.0

func debug_contract() -> Dictionary:
    var enemy := get_parent() as EnemyActor
    return {"affix": affix_id, "barrier": barrier, "barrier_max": barrier_max,
        "links": linked_enemies().size() if affix_id == "BEACON" else 0,
        "damage_multiplier": enemy.run_damage_multiplier if enemy else 0.0,
        "attack_interval_multiplier": enemy.run_attack_interval_multiplier if enemy else 0.0}
