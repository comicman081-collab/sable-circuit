extends SceneTree
## Scratch micro-benchmark (not committed, writes nothing): cost of one OperatorActor._weapon_art_profile() call,
## the old per-shot deep copy against the cached one, alternating rounds in one process. Function cost only, not FPS.
func _init() -> void: call_deferred("run")
func old_profile(actor: OperatorActor) -> Dictionary:
    var profile := actor.art_profile.duplicate(true)
    for key in ["projectile_profile", "hit_vfx_profile"]:
        var requested := str(actor.weapon_spec.get(key, ""))
        if not requested.is_empty(): profile[key] = requested
    return profile
func run() -> void:
    var squad := SquadController.new(); root.add_child(squad); await process_frame
    squad.set_process(false)
    for actor: OperatorActor in squad.operators:
        actor.set_physics_process(false); actor.get_node("SkillController").set_process(false)
    var rows := []
    for pair in [["CHR_PROTO_01", "WPN_DMR_RAIL_01"], ["CHR_PROTO_02", "WPN_SHOTGUN_NULL_01"], ["CHR_PROTO_02", ""]]:
        var actor: OperatorActor
        for candidate: OperatorActor in squad.operators:
            if candidate.operator_id == pair[0]: actor = candidate
        if actor == null: print("operator not found ", pair[0]); continue
        if not str(pair[1]).is_empty(): actor.apply_campaign_modifiers({"weapon_id": pair[1], "module_id": ""})
        var same := old_profile(actor) == actor._weapon_art_profile()
        var n := 20000
        var old_us := 0
        var new_us := 0
        for round in range(5):
            var t := Time.get_ticks_usec()
            for i in range(n): old_profile(actor)
            old_us += Time.get_ticks_usec() - t
            t = Time.get_ticks_usec()
            for i in range(n): actor._weapon_art_profile()
            new_us += Time.get_ticks_usec() - t
        var calls := float(n * 5)
        print("%s %-22s same_value=%s  old %.3f us/call  cached %.3f us/call  keys=%d" % [pair[0], str(actor.equipped_weapon_id), str(same), float(old_us) / calls, float(new_us) / calls, actor.art_profile.size()])
    squad.queue_free(); await process_frame
    quit(0)
