extends SceneTree
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok:
        failures.append(label)
        push_error(label)
func run() -> void:
    var flow := preload("res://scripts/core/game_flow.gd").new()
    flow.persist_campaign = false
    root.add_child(flow)
    await process_frame
    var music: Node = flow.music
    check(music.current_key == "title", "Actual app title selects music")
    check(music.catalog.size() == 9, "Nine assigned non-cinematic cues remain cataloged")
    for key in music.catalog:
        music.play_track(key)
        var player: AudioStreamPlayer = music.voices[music.active]
        check(player.playing, "Player starts " + key)
        check(player.stream.get_length() > 20, "Full music payload " + key)
        check(player.stream.loop, "Loop policy " + key)
    flow.show_intro(false)
    check(music.current_key.is_empty(), "Video uses its embedded original soundtrack without a layered music cue")
    flow.enter_base()
    check(music.current_key == "base", "App lobby selects base")
    check(music.current_key != "intro", "Skipping intro transitions away from its song")
    var pos: int = music.active
    flow.open_mission_briefing("MIS_CH01_01")
    check(music.active == pos, "Briefing preserves current base song")
    for stage in range(1,6):
        flow.open_battle_preview(stage)
        await process_frame
        check(music.current_key == "stage%d" % stage, "App stage selects own cue %d" % stage)
        preload("res://scripts/audio/demo_music.gd").encounter(self, "MIS_CH01_%02d" % stage, true)
        check(music.current_key == "boss", "Boss override %d" % stage)
    for number in range(6, 11):
        var reused := "stage%d" % ((number - 1) % 5 + 1)
        check(music.stage_key("MIS_CH01_%02d" % number) == reused, "Operation %d reuses cue %s until its own track exists" % [number, reused])
    music.toggle_mute()
    check(AudioServer.is_bus_mute(AudioServer.get_bus_index("SableMusic")), "Music mutes")
    check(not AudioServer.is_bus_mute(AudioServer.get_bus_index("Master")), "Master/SFX unaffected")
    music.toggle_mute()
    flow.show_title()
    await create_timer(1.1).timeout
    var playing := 0
    for voice in music.voices:
        if voice.playing: playing += 1
    check(playing == 1, "Rapid transitions settle to exactly one voice")
    paused = true
    await process_frame
    await process_frame
    check(AudioServer.get_bus_volume_db(AudioServer.get_bus_index("SableMusic")) < -7, "Paused music ducks")
    paused = false
    # Real mixer evidence: capture 4 seconds of the selected title on its own bus.
    var record := AudioEffectRecord.new()
    record.format = AudioStreamWAV.FORMAT_16_BITS
    AudioServer.add_bus_effect(AudioServer.get_bus_index("SableMusic"), record)
    record.set_recording_active(true)
    await create_timer(4.0).timeout
    record.set_recording_active(false)
    var capture := record.get_recording()
    if capture != null:
        capture.save_to_wav("res://qa/music_integration_20260920/native_music_mix.wav")
    var report := {"checks":checks,"failures":failures,"pass":failures.is_empty(),"source":"Real GameFlow and AudioStreamPlayer; no player-save writes"}
    var file := FileAccess.open("res://qa/music_integration_20260920/runtime_check.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(report,"  "))
    print("DEMO_MUSIC_CHECK ",JSON.stringify(report))
    flow.queue_free()
    await process_frame
    quit(0 if failures.is_empty() else 1)
