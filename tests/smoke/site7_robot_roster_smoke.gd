extends SceneTree

const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const ALLOWED := ["ENM_SITE7_DRONE_01", "BOSS_SITE7_ANCHOR_01", "ENM_SITE7_BULWARK_01", "ENM_SITE7_RAM_01", "BOSS_SITE7_RELAY_01", "ENM_SITE7_MORTAR_01", "BOSS_SITE7_REMNANT_01"]
const INTRODUCED := ["ENM_SITE7_BULWARK_01", "ENM_SITE7_RAM_01", "ENM_SITE7_MORTAR_01"]
const NEW_IDS := [["ENM_SITE7_BULWARK_01"], ["ENM_SITE7_RAM_01", "BOSS_SITE7_RELAY_01"], ["ENM_SITE7_MORTAR_01", "BOSS_SITE7_REMNANT_01"]]
## Operations 6-10 are held back (no plates, so no stage can load): they introduce only their own boss and
## draw every other robot from the active roster. Checked from their data.
const HELD_BACK_NEW_IDS := {"MIS_CH01_06": "BOSS_SITE7_AERATOR_01", "MIS_CH01_07": "BOSS_SITE7_CRYO_01", "MIS_CH01_08": "BOSS_SITE7_GANTRY_01",
    "MIS_CH01_09": "BOSS_SITE7_ARCHIVE_01", "MIS_CH01_10": "BOSS_SITE7_ORIGIN_01"}
const Warmer := preload("res://scripts/core/deploy_warmer.gd")
var failures: Array[String] = []
var checks := 0

func _init() -> void:
    call_deferred("run")

func check(ok: bool, note: String) -> void:
    checks += 1
    if not ok:
        failures.append(note)
        push_error(note)

func settle() -> void:
    for index in range(5): await process_frame

func run() -> void:
    for id in ["ENM_SITE7_RIFLE_01", "ENM_SITE7_SHIELD_01", "ENM_SITE7_ABERRANT_01"]:
        check(ArtProfileRegistry.get_profile(id).is_empty(), "Retired body not registered: " + id)
        var retired := ENEMY.instantiate() as EnemyActor
        check(not retired.configure(id, 100), "Retired configure rejected: " + id)
        root.add_child(retired)
        await settle()
        check(not is_instance_valid(retired), "Retired enemy removed before display: " + id)
    var default_actor := ENEMY.instantiate() as EnemyActor
    root.add_child(default_actor)
    await settle()
    check(default_actor.enemy_id == ALLOWED[0], "Editor default is a reviewed drone")
    check(is_instance_valid(default_actor.machine_sprite), "Default drone has authored machine art")
    check(not default_actor.preview_biped_source({}), "Biped preview intake disabled")
    default_actor.queue_free()
    await settle()
    for number in range(1, 4):
        var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/MIS_CH01_%02d.json" % number))
        check(mission.new_enemy_ids == NEW_IDS[number-1], "Each stage introduces its own new archetypes")
        var normal_types: Array[String] = []
        for room: Dictionary in mission.main_route:
            for row: Dictionary in room.get("encounter",[]):
                var identity := str(row.enemy_id)
                if identity.begins_with("BOSS_"): continue
                if not identity in normal_types: normal_types.append(identity)
                for later in range(number,3): check(identity != INTRODUCED[later],"No later-stage archetype introduced early")
        check(INTRODUCED[number-1] in normal_types,"New archetype really appears, not metadata only")
        check(normal_types.size() >= mini(number+1,3),"Distinct silhouettes in actual encounter data")
        var stage := STAGE.instantiate() as StoryStage01
        stage.mission_id = "MIS_CH01_%02d" % number
        root.add_child(stage)
        await settle()
        for step in [1, 3, 4]:
            var ids: Array[String] = stage.debug_spawn_encounter_for_step(step)
            await settle()
            check(not ids.is_empty(), "Encounter still populated")
            for id in ids: check(id in ALLOWED, "Only robot roster can spawn")
            for node in get_nodes_in_group("m3_enemies"):
                if not stage.is_ancestor_of(node): continue
                check(node.enemy_id in ALLOWED, "Live actor is robot")
                check(is_instance_valid(node.machine_sprite), "Live actor uses reviewed robot art")
                check(not is_instance_valid(node.biped_sprite), "No biped renderer")
            for actor in stage.squad.operators:
                check(actor.has_node("MotionLabCharacterRuntime"), "Playable character motion retained")
        stage.queue_free()
        await settle()
    for mission_id in HELD_BACK_NEW_IDS:
        var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % mission_id))
        check(data.new_enemy_ids == [HELD_BACK_NEW_IDS[mission_id]], mission_id + " introduces only its own boss")
        var seen := Warmer.mission_enemy_ids(mission_id)
        check(seen.has(HELD_BACK_NEW_IDS[mission_id]), mission_id + " fights its own boss")
        for identity in seen:
            var profile := ArtProfileRegistry.get_profile(identity)
            check(not profile.is_empty() and bool(profile.get("runtime_enabled", false)) and str(profile.get("body_plan", "")) == "robot", mission_id + " robot is active: " + identity)
            check(not identity in ["ENM_SITE7_RIFLE_01", "ENM_SITE7_SHIELD_01", "ENM_SITE7_ABERRANT_01"], mission_id + " no retired body: " + identity)
            if identity.begins_with("BOSS_"): check(identity == HELD_BACK_NEW_IDS[mission_id], mission_id + " holds one boss only: " + identity)
    print("SITE7_ROBOT_ROSTER: %s / %d checks" % ["PASS" if failures.is_empty() else "FAIL", checks])
    quit(0 if failures.is_empty() else 1)
