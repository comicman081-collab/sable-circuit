extends SceneTree

var failures: Array[String] = []


func _init() -> void:
    call_deferred("_run")


func _run() -> void:
    var projectile := PrototypeProjectile.new()
    root.add_child(projectile)
    projectile.setup(
        Vector2(320.0, 240.0),
        Vector2.RIGHT,
        null,
        Color("fff0a8"),
        {"projectile_profile": "PRJ_ASTER_NEEDLE_01"},
        "no_targets_in_smoke",
    )
    await process_frame
    var contract := projectile.debug_visual_contract()
    _check(bool(contract.get("aster_v6_requested", false)), "ASTER profile selects authored projectile V6")
    _check(bool(contract.get("aster_v6_loaded", false)), "projectile V6 lossless WebP loads at runtime")
    _check(bool(contract.get("aster_v6_sprite_active", false)), "projectile V6 owns the ASTER visible body")
    _check(int(contract.get("aster_v6_afterimage_count", 0)) == 2, "projectile V6 owns two restrained runtime afterimages")
    _check(bool(contract.get("aster_v6_local_light_active", false)), "projectile V6 owns restrained local lighting")
    _check(contract.get("aster_v6_resolution", Vector2.ZERO) == Vector2(768.0, 192.0), "projectile V6 runtime resolution is locked")
    _check(is_equal_approx(float(contract.get("aster_v6_tip_anchor", 0.0)), 0.862), "projectile V6 uses measured visible-alpha tip anchor")
    _check(projectile.speed == 1040.0, "authored visual does not change ASTER projectile speed")
    _check(projectile.damage == 10.0, "authored visual does not change ASTER projectile damage")
    _check(not bool(contract.get("hurt_feedback_called_by_projectile", true)), "projectile does not duplicate actor-owned hurt feedback")
    _check(str(contract.get("hit_feedback_authority", "")) == "CombatFeedback.spawn_hit", "existing contact hit feedback authority is preserved")
    projectile.queue_free()
    await process_frame

    if failures.is_empty():
        print("ASTER_PROJECTILE_V6_SMOKE: PASS")
        quit(0)
        return
    print("ASTER_PROJECTILE_V6_SMOKE: FAIL (%d)" % failures.size())
    for failure in failures:
        print(" - " + failure)
    quit(1)


func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: " + label)
    else:
        failures.append(label)
        push_error("FAIL: " + label)
