extends SceneTree

## Stage 4/5 registry and live-spawn smoke.
## This proves mission data, robot-only profiles, authored machine intake and
## boss/normal encounter wiring; it is not a visual or alpha-quality approval.

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")

const STAGES := ["MIS_CH01_04", "MIS_CH01_05"]
const NEW_IDS := {
    "MIS_CH01_04": ["ENM_SITE7_PRISM_01", "BOSS_SITE7_FORGE_01"],
    "MIS_CH01_05": ["ENM_SITE7_NULL_PYLON_01", "BOSS_SITE7_CARRIER_01"]
}
const ROBOT_IDS := [
    "ENM_SITE7_DRONE_01", "BOSS_SITE7_ANCHOR_01", "ENM_SITE7_BULWARK_01",
    "ENM_SITE7_RAM_01", "ENM_SITE7_MORTAR_01", "ENM_SITE7_PRISM_01",
    "ENM_SITE7_NULL_PYLON_01", "BOSS_SITE7_FORGE_01", "BOSS_SITE7_CARRIER_01"
]

var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("run")

func check(ok: bool, note: String) -> void:
    checks += 1
    if not ok:
        failures.append(note)
        push_error(note)

func settle(frames: int = 4) -> void:
    for _i in range(frames):
        await process_frame

func read_json(path: String) -> Dictionary:
    var value = JSON.parse_string(FileAccess.get_file_as_string(path))
    return value if value is Dictionary else {}

func check_profile_and_runtime(enemy_id: String) -> void:
    var profile := ArtProfileRegistry.get_profile(enemy_id)
    check(not profile.is_empty(), enemy_id + " profile registered")
    check(str(profile.get("body_plan", "")) == "robot", enemy_id + " is robot-only")
    check(bool(profile.get("runtime_enabled", false)), enemy_id + " runtime enabled")
    check(not profile.has("biped_asset"), enemy_id + " has no biped fallback")

    var binding: Dictionary = profile.get("machine_asset", {})
    var asset_path := str(binding.get("spec", ""))
    check(not asset_path.is_empty() and FileAccess.file_exists(asset_path), enemy_id + " machine spec exists")
    if asset_path.is_empty() or not FileAccess.file_exists(asset_path):
        return
    var spec := read_json(asset_path)
    check(str(spec.get("enemy_id", "")) == enemy_id, enemy_id + " spec identity bound")
    check(str(spec.get("kind", "")) in ["hover_machine", "anchored_machine", "tracked_machine"], enemy_id + " authored machine kind")

    var actor := ENEMY.instantiate() as EnemyActor
    root.add_child(actor)
    await settle(2)
    check(actor.configure(enemy_id, 200.0), enemy_id + " configure accepted")
    await settle(3)
    check(is_instance_valid(actor.machine_sprite), enemy_id + " authored machine renderer")
    if is_instance_valid(actor.machine_sprite):
        check(bool(actor.machine_sprite.configured), enemy_id + " machine source configured")
        var contract: Dictionary = actor.machine_sprite.debug_contract()
        var expected_views := 8 if str(spec.get("facing_mode", "")) == "authored_yaw8" else 1
        check(int(contract.get("view_count", 0)) == expected_views, enemy_id + " authored view count")
        check(not bool(contract.get("mirrored", true)), enemy_id + " not mirrored")
    actor.queue_free()
    await settle(2)

func run() -> void:
    for enemy_id in ROBOT_IDS:
        await check_profile_and_runtime(enemy_id)

    for mission_id in STAGES:
        var mission := read_json("res://data/missions/%s.json" % mission_id)
        check(str(mission.get("mission_id", "")) == mission_id, mission_id + " mission identity")
        check((mission.get("main_route", []) as Array).size() >= 6, mission_id + " full six-room route")
        var declared: Array = mission.get("new_enemy_ids", [])
        for enemy_id in NEW_IDS[mission_id]:
            check(enemy_id in declared, mission_id + " declares " + enemy_id)
        var encounter_ids: Array[String] = []
        for room_variant in mission.get("main_route", []):
            if not (room_variant is Dictionary):
                continue
            for row_variant in (room_variant as Dictionary).get("encounter", []):
                if row_variant is Dictionary:
                    var identity := str((row_variant as Dictionary).get("enemy_id", ""))
                    if not identity.is_empty() and not identity in encounter_ids:
                        encounter_ids.append(identity)
        for enemy_id in NEW_IDS[mission_id]:
            check(enemy_id in encounter_ids, mission_id + " encounter uses " + enemy_id)

        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = mission_id
        root.add_child(stage)
        await settle(5)
        check(stage.debug_route_count() == 6, mission_id + " runtime route loaded")
        for step in [1, 3, 4]:
            var spawned: Array[String] = stage.debug_spawn_encounter_for_step(step)
            await settle(5)
            check(not spawned.is_empty(), mission_id + " encounter step " + str(step) + " spawned")
            for enemy_id in spawned:
                check(enemy_id in ROBOT_IDS, mission_id + " live roster remains robot-only")
            for node in get_nodes_in_group("m3_enemies"):
                if not is_instance_valid(node) or not stage.is_ancestor_of(node):
                    continue
                check(node.enemy_id in ROBOT_IDS, mission_id + " live enemy id allowed")
                check(is_instance_valid(node.machine_sprite) and node.machine_sprite.configured, mission_id + " live machine source")
        stage.queue_free()
        await settle(4)

    print("SITE7_STAGE45_REGISTRY: %s / %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
    quit(0 if failures.is_empty() else 1)
