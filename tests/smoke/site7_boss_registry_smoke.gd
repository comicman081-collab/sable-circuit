extends SceneTree
## Every boss after ANCHOR/FORGE/CARRIER must be the exact authored machine its mission names.
## A boss also spawns in a live stage as soon as the campaign marks its mission deployable (missions 2/3
## always are). Operations 6-10 wait for their plates: until the campaign opens one, its boss is checked as
## data and as an actor, and the mission must still carry its staging block, so registering a boss can
## never be what enables an operation or moves a boss room. Opening an operation later needs no edit here.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const BOSSES := {
    "MIS_CH01_02": "BOSS_SITE7_RELAY_01",
    "MIS_CH01_03": "BOSS_SITE7_REMNANT_01",
    "MIS_CH01_06": "BOSS_SITE7_AERATOR_01",
    "MIS_CH01_07": "BOSS_SITE7_CRYO_01",
    "MIS_CH01_08": "BOSS_SITE7_GANTRY_01",
    "MIS_CH01_09": "BOSS_SITE7_ARCHIVE_01",
    "MIS_CH01_10": "BOSS_SITE7_ORIGIN_01"
}
const ALWAYS_DEPLOYABLE := ["MIS_CH01_02", "MIS_CH01_03"]
## Heights are measured on the machine's own mass (`visible_rect_px`), not on the canvas around it.
const VISIBLE_HEIGHT := Vector2(220.0, 270.0)
var failures: Array[String] = []
var checks := 0

func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)

func run() -> void:
    var campaign: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/story/site7_campaign.json"))
    var deployable := {}
    for row in campaign.get("missions", []):
        deployable[str(row.get("mission_id", ""))] = bool(row.get("deployable", true))
    for mission_id in ALWAYS_DEPLOYABLE:
        check(bool(deployable.get(mission_id, false)), mission_id + " deployable")
    for mission_id in BOSSES:
        await _verify_boss(mission_id, BOSSES[mission_id], bool(deployable.get(mission_id, false)))
    print("SITE7_BOSS_REGISTRY_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks)")
    quit(0 if failures.is_empty() else 1)

func _verify_boss(mission_id: String, enemy_id: String, live: bool) -> void:
    var profile := ArtProfileRegistry.get_profile(enemy_id)
    check(not profile.is_empty(), enemy_id + " profile")
    check(str(profile.get("body_plan", "")) == "robot" and bool(profile.get("runtime_enabled", false)), enemy_id + " active robot")
    check(not profile.has("biped_asset"), enemy_id + " no biped art")
    var binding: Dictionary = profile.get("machine_asset", {})
    var spec_path := str(binding.get("spec", ""))
    check(FileAccess.file_exists(spec_path), enemy_id + " spec exists")
    if not FileAccess.file_exists(spec_path): return
    check(FileAccess.get_sha256(spec_path) == str(binding.get("sha256", "")), enemy_id + " spec hash")
    var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(spec_path))
    check(str(spec.get("enemy_id", "")) == enemy_id and str(spec.get("kind", "")) == "anchored_machine", enemy_id + " fixed machine")
    check(FileAccess.get_sha256(str(spec.get("texture", ""))) == str(spec.get("texture_sha256", "")), enemy_id + " authored texture hash")
    var native := _native_size(str(spec.get("texture", "")))
    var art := _art_rect(spec, native)
    check(art.size.x > 0.0 and Rect2(Vector2.ZERO, native).encloses(art), enemy_id + " art bounds inside the picture")
    var visible_height := float(spec.get("display_height", 0.0)) * art.size.y / maxf(1.0, native.y)
    check(visible_height >= VISIBLE_HEIGHT.x and visible_height <= VISIBLE_HEIGHT.y, enemy_id + " display size " + str(snappedf(visible_height, 0.1)))
    var emitter: Array = spec.get("emitter_px", [0, 0])
    check(art.has_point(Vector2(float(emitter[0]), float(emitter[1]))), enemy_id + " emitter on the machine")
    var actor := ENEMY.instantiate() as EnemyActor
    check(actor.configure(enemy_id, 710.0), enemy_id + " configures")
    root.add_child(actor)
    actor.set_physics_process(false)
    check(is_instance_valid(actor.machine_sprite) and actor.machine_sprite.configured, enemy_id + " authored renderer")
    if is_instance_valid(actor.machine_sprite):
        check(actor.machine_sprite.kind == "anchored_machine" and actor.machine_sprite.views.size() == 1, enemy_id + " one fixed view")
        check(actor.machine_sprite.emitter_visible, enemy_id + " visible top emitter")
        _verify_art_geometry(enemy_id, actor, art, native)
    actor.free()
    _verify_mission_rows(mission_id, enemy_id, live)
    if live: await _verify_live_stage(mission_id, enemy_id)

## Damage box, health bar and muzzle must follow the machine, not the transparent canvas around it.
func _verify_art_geometry(enemy_id: String, actor: EnemyActor, art: Rect2, native: Vector2) -> void:
    var machine: Node2D = actor.machine_sprite
    var overhead: EnemyOverheadUI = actor.get_node("OverheadUI")
    var to_texture: Vector2 = machine.image_size / native
    var top := INF
    var world := Rect2(machine.sprite.to_global(art.position * to_texture), Vector2.ZERO)
    for corner in [art.position, art.position + Vector2(art.size.x, 0.0), art.end, art.position + Vector2(0.0, art.size.y)]:
        var local: Vector2 = overhead.to_local(machine.sprite.to_global(corner * to_texture))
        top = minf(top, local.y)
        world = world.expand(machine.sprite.to_global(corner * to_texture))
    check(absf(overhead.bar_y_local() - (top - 12.0)) < 0.01, enemy_id + " health bar sits on the machine top, not the canvas top")
    var hit: Rect2 = machine.hit_rect_world()
    check(world.encloses(hit), enemy_id + " damage box inside the machine")
    check(hit.get_area() >= world.get_area() * 0.45 and hit.get_area() <= world.get_area() * 0.6, enemy_id + " damage box keeps the shipped 76x70 % inset")
    check(world.grow(1.0).has_point(machine.muzzle_world()), enemy_id + " muzzle on the machine")

func _verify_mission_rows(mission_id: String, enemy_id: String, live: bool) -> void:
    var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission_id))
    check(enemy_id in mission.get("new_enemy_ids", []), mission_id + " introduces boss")
    var boss_rows := 0
    for room in mission.get("main_route", []):
        if str(room.get("type", "")) != "BOSS": continue
        for row in room.get("encounter", []):
            if str(row.get("enemy_id", "")) == enemy_id: boss_rows += 1
    check(boss_rows == 1, mission_id + " boss encounter uses its own boss")
    if live:
        check(not mission.has("staging"), mission_id + " is deployable, so its staging block is gone")
        return
    var staging: Dictionary = mission.get("staging", {})
    var staged: Dictionary = staging.get("boss", {})
    check(str(staged.get("id", "")) == enemy_id and not staged.has("placeholder_id"), mission_id + " staging names the registered boss")
    check(str(staging.get("status", "")) == "ART_PENDING", mission_id + " still waits for its plates")

func _verify_live_stage(mission_id: String, enemy_id: String) -> void:
    var stage := STAGE.instantiate() as StoryStage01
    stage.mission_id = mission_id
    root.add_child(stage)
    for _i in range(5): await process_frame
    var spawned: Array[String] = stage.debug_spawn_encounter_for_step(4)
    check(enemy_id in spawned, mission_id + " live boss spawned")
    for node in get_nodes_in_group("m3_enemies"):
        if node is EnemyActor and stage.is_ancestor_of(node) and node.enemy_id == enemy_id:
            check(is_instance_valid(node.machine_sprite) and node.machine_sprite.configured, mission_id + " live authored art")
    stage.queue_free()
    for _i in range(4): await process_frame

func _native_size(path: String) -> Vector2:
    if path.is_empty(): return Vector2.ONE
    var image := Image.load_from_file(path)
    return Vector2(image.get_size()) if image != null and not image.is_empty() else Vector2.ONE

func _art_rect(spec: Dictionary, native: Vector2) -> Rect2:
    var xy: Array = spec.get("visible_rect_px", [])
    if xy.size() != 4: return Rect2(Vector2.ZERO, native)
    var corner := Vector2(float(xy[0]), float(xy[1]))
    return Rect2(corner, Vector2(float(xy[2]), float(xy[3])) - corner)
