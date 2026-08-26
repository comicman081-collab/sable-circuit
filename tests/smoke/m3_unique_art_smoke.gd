extends SceneTree

const OPERATOR_SCENE := preload("res://scenes/actors/player/OperatorActor.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var playable_ids := ["CHR_PROTO_01", "CHR_PROTO_02", "CHR_PROTO_03"]
    var enemy_ids := ["ENM_SITE7_RIFLE_01", "ENM_SITE7_SHIELD_01", "ENM_SITE7_DRONE_01", "ENM_SITE7_ABERRANT_01", "BOSS_SITE7_ANCHOR_01"]
    var fields := ["visual_profile","motion_profile","projectile_profile","hit_vfx_profile","fire_sfx_profile","impact_sfx_profile","master_asset"]
    var seen: Dictionary = {}

    for identity in playable_ids + enemy_ids:
        var profile := ArtProfileRegistry.get_profile(identity)
        _check(not profile.is_empty(), identity + " profile loads")
        for field in fields:
            var value := str(profile.get(field, ""))
            _check(not value.is_empty(), identity + " has " + field)
            var key := field + "::" + value
            _check(not seen.has(key), identity + " has unique " + field)
            seen[key] = identity
        _check(ResourceLoader.exists("res://" + str(profile.get("master_asset", ""))), identity + " master asset imports")

    for i in range(playable_ids.size()):
        var actor := OPERATOR_SCENE.instantiate() as OperatorActor
        actor.configure(playable_ids[i], ["ASTER","ROOK","MICA"][i], [Color("69d2ff"),Color("ff9d6c"),Color("a8f07a")][i])
        root.add_child(actor)
        await process_frame
        _check(actor.art_profile.get("visual_profile", "") != "", actor.display_name + " runtime profile bound")
        var visual := actor.get_node_or_null("VisualRoot") as OperatorVisual
        _check(visual != null and visual.skeleton != null, actor.display_name + " unique runtime visual has skeleton")
        _check(visual != null and visual.muzzle_socket != null, actor.display_name + " unique runtime visual has muzzle")
        actor.queue_free()
        await process_frame

    for enemy_id in enemy_ids:
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(enemy_id, 100.0)
        root.add_child(enemy)
        await process_frame
        var sprite := enemy.get_node_or_null("HighResVisualRoot/UniqueMasterSprite") as Sprite2D
        _check(sprite != null and sprite.texture != null, enemy_id + " high-res master texture bound")
        _check(enemy.art_profile.get("motion_profile", "") != "", enemy_id + " unique motion profile bound")
        enemy.queue_free()
        await process_frame

    if failures.is_empty():
        print("M3_UNIQUE_ART_SMOKE: PASS")
        quit(0)
        return
    print("M3_UNIQUE_ART_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
