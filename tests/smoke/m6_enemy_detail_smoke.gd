extends SceneTree

const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const IDS: Array[String] = [
    "ENM_SITE7_RIFLE_01",
    "ENM_SITE7_SHIELD_01",
    "ENM_SITE7_DRONE_01",
    "ENM_SITE7_ABERRANT_01",
    "BOSS_SITE7_ANCHOR_01"
]

var failures: Array[String] = []

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var paths: Dictionary = {}
    var loaded_count := 0
    for i in range(IDS.size()):
        var enemy := ENEMY_SCENE.instantiate() as EnemyActor
        enemy.configure(IDS[i], 180.0 if i < 4 else 620.0)
        enemy.global_position = Vector2(220.0 + float(i) * 150.0, 340.0)
        root.add_child(enemy)
        await _frames(4)
        var detail := enemy.get_node_or_null("DetailOverlayPresentation") as EnemyDetailOverlayPresentation
        _check(detail != null, IDS[i] + " detail presentation exists")
        if detail:
            _check(detail.debug_loaded(), IDS[i] + " detail SVG loads on articulated rig")
            _check(detail.debug_overlay_count() >= 6, IDS[i] + " has 6+ detail overlay layers")
            var path := detail.debug_source_path()
            _check(not path.is_empty(), IDS[i] + " detail path exists")
            _check(not paths.has(path), IDS[i] + " detail path is unique")
            paths[path] = true
            if detail.debug_loaded():
                loaded_count += 1
        enemy.queue_free()
        await _frames(2)

    _check(paths.size() == 5, "five enemy detail paths are unique")
    _check(loaded_count == 5, "all five enemy identity detail atlases load at runtime")

    if failures.is_empty():
        print("M6_ENEMY_DETAIL_SMOKE: PASS")
        quit(0)
        return
    print("M6_ENEMY_DETAIL_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)

func _frames(count: int) -> void:
    for _i in range(count):
        await process_frame

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
