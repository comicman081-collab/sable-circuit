extends SceneTree
const SFX = preload("res://scripts/audio/combat_sfx_bank.gd")
const OPERATOR = preload("res://scenes/actors/player/OperatorActor.tscn")
const ENEMY = preload("res://scenes/actors/enemy/EnemyActor.tscn")
const WARNING = preload("res://scripts/combat/site7_attack_warning.gd")
var checks := 0
var failures: Array[String] = []
var shots := 0
func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
func run() -> void:
    var arena := Node2D.new()
    root.add_child(arena)
    current_scene = arena
    var audio: Node = SFX.manager(self)
    audio.debug_trace = true
    for cue in SFX.Bank.CUES:
        var streams: Array = SFX.Bank.CUES[cue].streams
        check(streams.size() >= 2 and streams.size() <= 4, "Two to four selected variants: " + cue)
        for stream in streams:
            check(stream is AudioStreamWAV and stream.mix_rate == 48000, "Decoded 48 kHz WAV")
            check(stream.format == AudioStreamWAV.FORMAT_16_BITS, "PCM16 export")
            check(stream.loop_mode == AudioStreamWAV.LOOP_DISABLED, "No looping tail")
            var intermediate: String = "res://qa/sfx_integration_20260919/selected_pcm16/" + stream.resource_path.get_file().get_basename() + ".wav"
            var original := AudioStreamWAV.load_from_file(intermediate)
            check(original != null and original.data == stream.data, "Serialized resource PCM matches selected WAV bytes")
            check(original.stereo == stream.stereo, "Channel layout preserved")
    for path in ["res://data/art_profiles/playable_profiles.json", "res://data/art_profiles/enemy_profiles.json"]:
        var profiles: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
        for profile in profiles.profiles:
            for field in ["fire_sfx_profile", "impact_sfx_profile"]:
                check(SFX.PROFILE_CUES.has(profile[field]), "Mapped existing profile: " + profile[field])
    for id in ["CHR_PROTO_01", "CHR_PROTO_02", "CHR_PROTO_03"]:
        var actor := OPERATOR.instantiate() as OperatorActor
        actor.configure(id, id, Color.WHITE)
        arena.add_child(actor)
        actor.set_physics_process(false)
        actor.projectile_spawned.connect(func(_p: Node2D) -> void: shots += 1)
        var before: int = audio.played_count
        var old_shots := shots
        check(actor.debug_fire_once(), "Real trigger fired: " + id)
        check(audio.played_count == before + 1, "One sound per real trigger including ROOK pellets")
        check(shots > old_shots, "Projectile still emitted")
        var last: Dictionary = audio.events.back()
        await physics_frame
        check(actor.debug_fire_once(), "Second real trigger")
        check(audio.events.back().variant != last.variant, "No immediate repeated WAV")
        actor._reload_left = 1.0
        before = audio.played_count
        check(not actor.debug_fire_once() and audio.played_count == before, "Blocked trigger is silent")
        actor.free()
    for p in get_nodes_in_group("projectiles"): p.queue_free()
    var boss := ENEMY.instantiate() as EnemyActor
    boss.configure("BOSS_SITE7_ANCHOR_01", 100.0)
    arena.add_child(boss)
    boss.set_physics_process(false)
    await physics_frame
    var before: int = audio.played_count
    for i in range(5): boss.tactics._fire(Vector2.RIGHT.rotated(float(i) * 0.2))
    check(audio.played_count == before + 1, "Five actual fan projectiles coalesce to one firing sound")
    var other := Node.new()
    arena.add_child(other)
    SFX.play(self, "turret_fire", other)
    check(audio.played_count == before + 2, "Independent emitter remains audible in same frame")
    for kind in ["circle", "lane"]:
        await physics_frame
        var warning := WARNING.new()
        warning.source = boss
        warning.kind = kind
        arena.add_child(warning)
        warning.set_physics_process(false)
        before = audio.played_count
        warning._physics_process(warning.windup - 0.02)
        check(audio.played_count == before, "Warning is silent until damage boundary")
        warning._physics_process(0.03)
        check(audio.played_count == before + 1, "One detonation at real damage boundary")
        warning._physics_process(0.01)
        check(audio.played_count == before + 1, "No retrigger after detonation")
        check(audio.events.back().cue == ("boss_stomp" if kind == "circle" else "boss_cross_beam"), "Correct warning cue")
        warning.free()
    await physics_frame
    before = audio.played_count
    boss.apply_damage(1000)
    boss.apply_damage(1000)
    check(audio.played_count == before + 1 and audio.events.back().cue == "boss_destroy", "Boss death sound exactly once")
    var canceled := WARNING.new()
    canceled.source = boss
    arena.add_child(canceled)
    canceled.set_physics_process(false)
    canceled._physics_process(2.0)
    check(audio.played_count == before + 1, "Dead source cancels warning without sound")
    boss.free()
    check(audio.get_child_count() > 0, "Audio survives emitter deletion")
    check(SFX.Bank.CUES.boss_destroy.streams[0].get_length() >= 6.99, "Complete destruction tail")
    for i in range(70):
        var source := Node.new()
        arena.add_child(source)
        SFX.play(self, "impact_steel_light", source)
    check(audio.peak_voices <= SFX.MAX_VOICES, "Bounded peak polyphony")
    check(audio.suppressed_count > 0, "Duplicate/over-budget suppression exercised")
    check(AudioServer.get_bus_effect_count(AudioServer.get_bus_index(SFX.BUS)) >= 1, "Mix limiter installed")
    var snapshot: Dictionary = audio.debug_snapshot()
    arena.free()
    check(not is_instance_valid(audio), "All playback destroyed on scene exit")
    current_scene = null
    # Exercise actual GameFlow child-view swaps under a persistent bootstrap.
    var flow := GameFlow.new()
    root.add_child(flow)
    current_scene = flow
    flow.open_battle_preview(1)
    for i in range(6): await process_frame
    var stage := flow.current_view as StoryStage01
    var live_audio: Node = SFX.manager(self)
    check(live_audio.get_parent() == stage, "Actual child battle view owns audio, not bootstrap")
    SFX.play(self, "boss_destroy", stage)
    flow.show_title()
    for i in range(3): await process_frame
    check(not is_instance_valid(live_audio), "Actual title transition stops old battle audio")
    var credits_found := false
    for child in flow.current_view.get_children():
        if child is AcceptDialog and "Michel Baradari" in child.dialog_text: credits_found = true
    check(credits_found, "Required attribution is accessible from actual title UI")
    flow.free()
    current_scene = null
    var report := {"status":"PASS" if failures.is_empty() else "FAIL", "checks":checks,
        "failures":failures, "snapshot":snapshot, "auditory_approval":false}
    var report_path := "res://qa/sfx_integration_20260919/runtime_smoke.json"
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="): report_path = arg.trim_prefix("--out=")
    var file := FileAccess.open(report_path, FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  ")); file.close()
    print("COMBAT_SFX_R04: ", report.status, " / ", checks, " checks")
    quit(0 if failures.is_empty() else 1)
