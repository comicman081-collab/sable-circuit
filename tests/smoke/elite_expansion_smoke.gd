extends SceneTree
## Real actor coverage of BROODING and BEACON, including room accounting.
## The 2026-10-03 user decision preserves common machine weathering/hit flash;
## an affix must add no sprite material, shader parameter or modulation.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const NAV := preload("res://scripts/combat/cover_navigation.gd")
var checks := 0
var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    _table_contract()
    await _sprite_contract()
    await _ancestry_controls()
    await _beacon_contract()
    await _brood_contract()
    if failures.is_empty():
        print("ELITE_EXPANSION_SMOKE: PASS (%d checks)" % checks)
        quit(0)
    else:
        for failure in failures: printerr("FAIL: ", failure)
        print("ELITE_EXPANSION_SMOKE: FAIL (%d checks, %d failures)" % [checks, failures.size()])
        quit(1)

func _table_contract() -> void:
    var table := EliteAffix.table()
    _check(table.size() == 5, "five distinct affixes")
    var seen: Array[String] = []
    var hex := RegEx.new()
    hex.compile("^[0-9a-fA-F]{6}$")
    for id: String in table:
        var color := str(table[id].get("color", "")).to_lower()
        _check(hex.search(color) != null and not seen.has(color), id + " uses a distinct six-digit colour")
        _check(EliteAffix.tip(id).begins_with(id + ":"), id + " has an id-prefixed tip")
        seen.append(color)
    var brood: Dictionary = table.BROODING
    _check(int(brood.brood_count) == 2 and float(brood.brood_hatch_windup) >= 0.6 and float(brood.brood_health_ratio) > 0.0, "brood count, hatch warning and health ratio are defined")
    var beacon: Dictionary = table.BEACON
    _check(float(beacon.beacon_reduction) > 0.0 and float(beacon.beacon_reduction) <= 0.35 and int(beacon.beacon_max_links) <= 6, "beacon data stays inside reduction and link limits")
    var boss := ENEMY.instantiate() as EnemyActor
    boss.configure("BOSS_SITE7_ORIGIN_01", 1000.0)
    for id: String in table:
        _check(EliteAffix.apply(boss, id) == null, "boss refuses " + id + " at application boundary")
    boss.free()

func _actor(parent: Node, identity: String, hp: float, point: Vector2) -> EnemyActor:
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure(identity, hp)
    actor.position = point
    parent.add_child(actor)
    actor.set_physics_process(false)
    return actor

func _sprite_contract() -> void:
    var holder := Node2D.new()
    root.add_child(holder)
    for id: String in EliteAffix.table():
        var plain := _actor(holder, "ENM_SITE7_DRONE_01", 1000.0, Vector2(700, 0))
        var elite := _actor(holder, "ENM_SITE7_DRONE_01", 1000.0, Vector2.ZERO)
        var affix := EliteAffix.apply(elite, " " + id.to_lower() + " ")
        await _frames(3)
        _check(affix != null and affix.affix_id == id and EliteAffix.apply(elite, "SHIELDED") == null, id + " normalizes its id and rejects a second affix")
        var plain_sprites := _sprites(plain)
        var elite_sprites := _sprites(elite)
        _check(not plain_sprites.is_empty() and plain_sprites.size() == elite_sprites.size(), id + " keeps the same sprite nodes")
        for path: String in plain_sprites:
            _check(elite_sprites.has(path) and _sprite_equal(plain_sprites[path], elite_sprites.get(path)), id + " keeps common sprite material/modulation at " + path)
            _check(elite_sprites.has(path) and _sprite_ancestry_equal(plain_sprites[path], elite_sprites.get(path), plain, elite), id + " keeps the entire sprite-to-actor CanvasItem chain at " + path)
        # Compare the common hit response too. The affix adds no flash of its own.
        plain._hit_flash = 0.7
        elite._hit_flash = 0.7
        if is_instance_valid(plain.machine_sprite): plain.machine_sprite.sync_pose()
        if is_instance_valid(elite.machine_sprite): elite.machine_sprite.sync_pose()
        for path: String in plain_sprites:
            _check(elite_sprites.has(path) and _sprite_equal(plain_sprites[path], elite_sprites.get(path)), id + " keeps the common hit response at " + path)
            _check(elite_sprites.has(path) and _sprite_ancestry_equal(plain_sprites[path], elite_sprites.get(path), plain, elite), id + " keeps the common hit response through every ancestor at " + path)
        plain.free()
        elite.free()
    holder.free()
    await _frames(1)

func _sprites(actor: Node) -> Dictionary:
    var result := {}
    for node in actor.find_children("*", "Sprite2D", true, false):
        result[str(actor.get_path_to(node))] = node
    return result

func _sprite_equal(a: Sprite2D, b: Sprite2D) -> bool:
    if b == null or a.modulate != b.modulate or a.self_modulate != b.self_modulate: return false
    if (a.material == null) != (b.material == null): return false
    if a.material == null: return true
    if a.material.get_class() != b.material.get_class(): return false
    if a.material is ShaderMaterial:
        var left := a.material as ShaderMaterial
        var right := b.material as ShaderMaterial
        if left.shader.resource_path != right.shader.resource_path: return false
        for uniform: Dictionary in left.shader.get_shader_uniform_list():
            if left.get_shader_parameter(str(uniform.name)) != right.get_shader_parameter(str(uniform.name)): return false
        return true
    return a.material.resource_path == b.material.resource_path

func _sprite_ancestry_equal(a: Sprite2D, b: Sprite2D, plain_root: Node, elite_root: Node) -> bool:
    if a == null or b == null: return false
    var left: Node = a
    var right: Node = b
    while left != null and right != null:
        if left.get_class() != right.get_class(): return false
        if left is CanvasItem and not _canvas_equal(left as CanvasItem, right as CanvasItem): return false
        if left == plain_root or right == elite_root:
            return left == plain_root and right == elite_root
        left = left.get_parent()
        right = right.get_parent()
    return false

func _canvas_equal(a: CanvasItem, b: CanvasItem) -> bool:
    # Keep the original Sprite2D checks, including common weathering parameters.
    if a is Sprite2D and b is Sprite2D: return _sprite_equal(a as Sprite2D, b as Sprite2D)
    if a.modulate != b.modulate or a.self_modulate != b.self_modulate: return false
    if (a.material == null) != (b.material == null): return false
    if a.material == null: return true
    if a.material.get_class() != b.material.get_class(): return false
    if a.material is ShaderMaterial:
        var left := a.material as ShaderMaterial
        var right := b.material as ShaderMaterial
        if (left.shader == null) != (right.shader == null): return false
        if left.shader == null: return true
        if left.shader.resource_path != right.shader.resource_path or left.shader.code != right.shader.code: return false
        for uniform: Dictionary in left.shader.get_shader_uniform_list():
            if left.get_shader_parameter(str(uniform.name)) != right.get_shader_parameter(str(uniform.name)): return false
        return true
    return a.material.resource_path == b.material.resource_path

func _ancestry_controls() -> void:
    var holder := Node2D.new()
    root.add_child(holder)
    var plain := _actor(holder, "ENM_SITE7_DRONE_01", 1000.0, Vector2(700, 0))
    var changed := _actor(holder, "ENM_SITE7_DRONE_01", 1000.0, Vector2.ZERO)
    await _frames(3)
    var plain_sprites := _sprites(plain)
    var changed_sprites := _sprites(changed)
    var visual := changed.get_node_or_null("HighResVisualRoot") as CanvasItem
    _check(visual != null and not plain_sprites.is_empty(), "ancestor controls have real robot sprites and HighResVisualRoot")
    if visual != null and not plain_sprites.is_empty():
        var controls := [{"node": changed, "property": "modulate", "label": "actor root modulate"},
            {"node": changed, "property": "self_modulate", "label": "actor root self_modulate"},
            {"node": visual, "property": "modulate", "label": "HighResVisualRoot modulate"}]
        for control: Dictionary in controls:
            var node := control.node as CanvasItem
            var property := str(control.property)
            var original: Color = node.get(property)
            node.set(property, Color(0.7, 1.0, 0.7))
            var local_equal := true
            var chain_equal := true
            for path: String in plain_sprites:
                local_equal = local_equal and _sprite_equal(plain_sprites[path], changed_sprites.get(path))
                chain_equal = chain_equal and _sprite_ancestry_equal(plain_sprites[path], changed_sprites.get(path), plain, changed)
            _check(local_equal, str(control.label) + " control leaves local Sprite2D values unchanged")
            _check(not chain_equal, str(control.label) + " control is rejected by the ancestor comparison")
            node.set(property, original)
            var restored := true
            for path: String in plain_sprites:
                restored = restored and _sprite_ancestry_equal(plain_sprites[path], changed_sprites.get(path), plain, changed)
            _check(restored, str(control.label) + " control restores the common robot state")
    holder.free()
    await _frames(1)

func _beacon_contract() -> void:
    var holder := Node2D.new()
    root.add_child(holder)
    var source := _actor(holder, "ENM_SITE7_NULL_PYLON_01", 1000.0, Vector2.ZERO)
    var affix := EliteAffix.apply(source, "BEACON")
    var peer := _actor(holder, "ENM_SITE7_DRONE_01", 1000.0, Vector2(100, 0))
    var outside := _actor(holder, "ENM_SITE7_DRONE_01", 1000.0, Vector2(500, 0))
    source.apply_damage(100.0)
    _check(is_equal_approx(source.health, 900.0), "a beacon does not protect itself")
    peer.apply_damage(100.0)
    _check(is_equal_approx(peer.health, 925.0), "beacon reduces actual peer damage by its 25 percent")
    outside.apply_damage(100.0)
    _check(is_equal_approx(outside.health, 900.0), "outside radius damage stays full")
    _check(affix.linked_enemies().size() == 1 and affix.linked_enemies()[0] == peer, "one actual protected peer gets one link")
    source.apply_damage(99999.0)
    var before := peer.health
    peer.apply_damage(100.0)
    _check(is_equal_approx(before - peer.health, 100.0) and EliteAffix.beacon_for(peer) == null, "beacon death releases protection in the same call stack")
    source.free()
    var weak := _actor(holder, "ENM_SITE7_NULL_PYLON_01", 1000.0, Vector2.ZERO)
    var strong := _actor(holder, "ENM_SITE7_NULL_PYLON_01", 1000.0, Vector2(-40, 0))
    var weak_affix := EliteAffix.apply(weak, "BEACON")
    var strong_affix := EliteAffix.apply(strong, "BEACON")
    weak_affix.spec.beacon_reduction = 0.2
    strong_affix.spec.beacon_reduction = 0.35
    before = peer.health
    peer.apply_damage(100.0)
    _check(is_equal_approx(before - peer.health, 65.0), "overlapping beacons use the strongest once, not multiplied")
    _check(int(weak_affix.linked_enemies().has(peer)) + int(strong_affix.linked_enemies().has(peer)) == 1, "overlap draws at most one link to a peer")
    strong.apply_damage(99999.0)
    before = peer.health
    peer.apply_damage(100.0)
    _check(is_equal_approx(before - peer.health, 80.0), "the remaining weaker source takes over immediately")
    strong.free()
    weak.free()
    peer.free()
    outside.free()

    source = _actor(holder, "ENM_SITE7_NULL_PYLON_01", 1000.0, Vector2.ZERO)
    affix = EliteAffix.apply(source, "BEACON")
    var shielded := _actor(holder, "ENM_SITE7_DRONE_01", 100.0, Vector2(100, 0))
    var shield := EliteAffix.apply(shielded, "SHIELDED")
    shielded.apply_damage(40.0)
    _check(is_equal_approx(shielded.health, 100.0) and is_zero_approx(shield.barrier), "reduction happens before shield absorption: 40 becomes 30, exactly the barrier")
    shielded.apply_damage(40.0)
    _check(is_equal_approx(shielded.health, 70.0), "after the barrier breaks the reduced damage reaches health")
    holder.free()
    await _frames(1)

    holder = Node2D.new()
    root.add_child(holder)
    source = _actor(holder, "ENM_SITE7_NULL_PYLON_01", 1000.0, Vector2.ZERO)
    affix = EliteAffix.apply(source, "BEACON")
    var peers: Array[EnemyActor] = []
    for index in range(7): peers.append(_actor(holder, "ENM_SITE7_DRONE_01", 1000.0, Vector2(40 + index * 30, 0)))
    _check(affix.protected_enemies().size() == 7 and affix.linked_enemies().size() == 6, "seven peers receive the aura but only six links are drawn")
    before = peers[6].health
    peers[6].apply_damage(100.0)
    _check(is_equal_approx(before - peers[6].health, 75.0), "the line display budget does not remove the seventh peer's protection")
    holder.free()
    await _frames(1)
    _check(get_nodes_in_group("elite_beacons").is_empty(), "beacon fixture leaves no source nodes")

func _brood_contract() -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_06"
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.set_process(false)
    stage.configure_campaign({}, "ELITE-EXPANSION-FIXTURE", {"enemy_health_multiplier": 1.3})
    stage.current_step = 3
    var room: Dictionary = stage.main_route[3].duplicate(true)
    room.encounter = [{"enemy_id": "ENM_SITE7_MORTAR_01", "health": 400.0, "affix": "BROODING"}]
    room.reinforcements = []
    room.reinforce_at = 0
    room.hazards = []
    stage.main_route[3] = room
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(3)
    var parent: EnemyActor = null
    for node in get_nodes_in_group("m3_enemies"):
        if node.get_parent() == stage:
            parent = node as EnemyActor
            parent.set_physics_process(false)
    _check(parent != null and stage.enemies_alive == 1, "last-robot fixture starts with one BROODING parent")
    if parent == null:
        stage.free()
        return
    var count := {"completed": 0, "reserved_before_decrement": -1}
    stage.room_completed.connect(func(_row: Dictionary, step: int) -> void:
        if step == 3: count.completed += 1)
    stage.hostile_defeated.connect(func(id: String) -> void:
        if id == "ENM_SITE7_MORTAR_01": count.reserved_before_decrement = stage.enemies_alive)
    var at := parent.global_position
    var affix := parent.get_node("EliteAffix") as EliteAffix
    parent.apply_damage(99999.0)
    var babies: Array[EnemyActor] = []
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and node.get_parent() == stage and node.has_meta("brood_parent_id"):
            node.set_physics_process(false)
            babies.append(node)
    _check(count.reserved_before_decrement == 3 and stage.enemies_alive == 2, "both hatchlings are counted before the parent decrements")
    _check(babies.size() == 2 and count.completed == 0 and stage._combat_started, "two live hatchlings keep the last parent's room locked")
    affix.on_defeated()
    _check(stage.enemies_alive == 2 and babies.size() == 2, "a repeated defeat hook cannot hatch twice")
    var ids: Array[int] = []
    for baby in babies:
        ids.append(baby.get_instance_id())
        _check(baby.enemy_id == "ENM_SITE7_DRONE_01" and baby.brood_generation == 1 and baby.get_node_or_null("EliteAffix") == null and EliteAffix.apply(baby, "BROODING") == null, "hatchling is a plain one-generation drone")
        _check(is_equal_approx(baby.max_health, 400.0 * 0.25 * 1.3) and is_equal_approx(baby.run_health_multiplier, 1.3), "hatchling authored health gets the contract exactly once")
        _check(at.distance_to(baby.global_position) <= 320.0 and stage._brood_spawn_fits(parent, baby.global_position, NAV.ground_obstacles(parent)), "hatchling's collider is on nearby painted floor outside cover")
        var shots: Array = []
        baby.projectile_emitted.connect(func(event: Dictionary) -> void: shots.append(event))
        _check(baby.brood_hatch_duration >= 0.6 and baby.brood_hatch_left >= 0.6, "hatch warning lasts at least 0.6 s")
        baby._spawn_projectile(Vector2.RIGHT)
        baby._try_attack(Vector2.RIGHT, 1.0)
        baby._physics_process(0.59)
        baby._spawn_projectile(Vector2.RIGHT)
        _check(shots.is_empty() and baby.brood_hatch_left > 0.0, "no projectile, legacy attack or normal controller attack during hatch")
        baby._physics_process(0.011)
        _check(is_zero_approx(baby.brood_hatch_left), "hatch completes after the marked warning")
        baby._spawn_projectile(Vector2.RIGHT)
        _check(shots.size() == 1, "hatchling can fire after the warning")
    var story := str(stage.call("_combat_story", "ELITE"))
    _check(story.contains("BROODING:") and not story.contains("BEACON:"), "combat story explains only its present affix")
    if babies.size() == 2:
        babies[0].apply_damage(99999.0)
        _check(stage.enemies_alive == 1 and count.completed == 0, "first hatchling death keeps the room locked")
        babies[1].apply_damage(99999.0)
        _check(stage.enemies_alive == 0 and count.completed == 1, "final hatchling death opens the room exactly once")
        var offspring: Array[EnemyActor] = []
        for node in stage.get_children():
            if node is EnemyActor and node.has_meta("brood_parent_id"): offspring.append(node)
        _check(offspring.size() == 2 and offspring[0].brood_generation == 1 and offspring[1].brood_generation == 1 and offspring[0].health == 0.0 and offspring[1].health == 0.0,
            "both first-generation deaths leave exactly the original two offspring, no grandchildren")
        # debug_spawn_encounter_for_step queues any preceding room's actors for
        # deletion. Flush that queue before asserting the global hostile group.
        await _frames(1)
        var remaining: PackedStringArray = []
        for node in get_nodes_in_group("m3_enemies"):
            remaining.append("%s hp=%s generation=%s queued=%s" % [node.get_path(), node.health, node.brood_generation, node.is_queued_for_deletion()])
        _check(get_nodes_in_group("m3_enemies").is_empty(), "plain children do not breed another generation; remaining=" + "; ".join(remaining))
    stage.free()
    current_scene = null
    await _frames(2)
    for id in ids: _check(instance_from_id(id) == null, "stage deletion frees its hatchlings without orphans")
    _check(root.get_children().filter(func(node: Node) -> bool: return node is PrototypeProjectile and not is_instance_valid((node as PrototypeProjectile).owner_actor)).is_empty(), "hatchling projectiles also clear after their owner stage is deleted")

    # Preserve the old reinforcement transition in a plain room.
    stage = STAGE.instantiate() as StoryStage01
    stage.mission_id = "MIS_CH01_06"
    root.add_child(stage)
    current_scene = stage
    await _frames(4)
    stage.set_process(false)
    stage.current_step = 3
    room = stage.main_route[3].duplicate(true)
    room.encounter = [{"enemy_id": "ENM_SITE7_DRONE_01", "health": 100.0}]
    room.reinforcements = [[{"enemy_id": "ENM_SITE7_DRONE_01", "health": 100.0}]]
    room.reinforce_at = 0
    room.hazards = []
    stage.main_route[3] = room
    stage.call("_activate_step")
    stage.debug_spawn_encounter_for_step(3)
    for node in get_nodes_in_group("m3_enemies"):
        if node.get_parent() == stage: node.apply_damage(99999.0)
    _check(stage._wave_index == 1 and is_equal_approx(stage._wave_wait, 2.2) and stage._combat_started, "plain last-robot reinforcement still waits the HEAD 2.2 s")
    stage.free()
    current_scene = null
    await _frames(2)

func _frames(count: int) -> void:
    for index in range(count):
        await physics_frame
        await process_frame

func _check(condition: bool, message: String) -> void:
    checks += 1
    if not condition: failures.append(message)
