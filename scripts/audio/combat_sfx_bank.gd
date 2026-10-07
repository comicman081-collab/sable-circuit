extends Node
## Scene-owned combat SFX playback. No synthesis and no gameplay timing changes.
## R05: world-position panning/attenuation for spatial cues, per-play pitch and
## gain variation from the cue map, per-emitter cooldown for impacts/hurts, a
## per-cue voice cap, and a combat bus with weight EQ, glue compression and a
## short room reverb before the limiter.
const Bank = preload("res://assets/audio/combat_r04/bank.gd")
const MAX_VOICES := 32
const NORMAL_VOICES := 24
const MAX_VOICES_PER_CUE := 5
const BUS := "SableCombatR04"
const SPATIAL_MAX_DISTANCE := 2600.0
const SPATIAL_ATTENUATION := 1.35
# Firing is already limited by weapon cadence and must sound on every trigger;
# only these secondary layers use the cue map's per-emitter cooldown.
const COOLDOWN_CUES := ["impact_steel_light", "impact_steel_heavy", "robot_hit", "impact_concrete", "ricochet",
    "shield_hit", "impact_body", "aster_hurt", "rook_hurt", "mica_hurt", "boss_core_hit", "boss_charge",
    "aster_reload", "rook_reload", "mica_reload", "armor_break", "shield_break"]
const PROFILE_CUES := {
    "SFX_FIRE_ASTER_COIL_01": "aster_fire", "SFX_FIRE_ROOK_BREACH_01": "rook_fire",
    "SFX_FIRE_MICA_PULSE_01": "mica_fire", "SFX_FIRE_ENM_RIFLE_01": "enemy_fire",
    "SFX_FIRE_ENM_SHIELD_01": "turret_fire", "SFX_FIRE_ENM_DRONE_01": "enemy_fire",
    "SFX_FIRE_ENM_ABERRANT_01": "turret_fire", "SFX_FIRE_BOSS_ANCHOR_01": "turret_fire",
    "SFX_HIT_ASTER_PRISM_01": "impact_steel_light", "SFX_HIT_ROOK_CRUSH_01": "impact_steel_heavy",
    "SFX_HIT_MICA_SCAN_01": "robot_hit", "SFX_HIT_ENM_RIFLE_01": "impact_steel_light",
    "SFX_HIT_ENM_SHIELD_01": "impact_steel_heavy", "SFX_HIT_ENM_DRONE_01": "robot_hit",
    "SFX_HIT_ENM_ABERRANT_01": "impact_steel_heavy", "SFX_HIT_BOSS_ANCHOR_01": "boss_core_hit",
}
var _voices: Array[Dictionary] = []
var _next: Dictionary = {}
var _last_frame: Dictionary = {}
var _cooldown_until: Dictionary = {}
var _dedup_frame := -1
var _duck_left := 0.0
var _rng := RandomNumberGenerator.new()
var played_count := 0
var suppressed_count := 0
var peak_voices := 0
var debug_trace := false
var events: Array[Dictionary] = []

static func manager(tree: SceneTree) -> Node:
    if tree == null: return null
    var host: Node = tree.current_scene if is_instance_valid(tree.current_scene) else tree.root
    # GameFlow swaps child views without replacing SceneTree.current_scene.
    # Own the voices under the actual battle view, never the persistent bootstrap.
    for candidate in tree.get_nodes_in_group("sable_combat_audio_host"):
        if not candidate.is_queued_for_deletion():
            host = candidate
            break
    var existing := host.get_node_or_null("CombatSfxR04")
    if existing != null: return existing
    var node := load("res://scripts/audio/combat_sfx_bank.gd").new() as Node
    node.name = "CombatSfxR04"
    host.add_child(node)
    return node

static func play(tree: SceneTree, cue_or_profile: String, emitter: Node = null, at: Vector2 = Vector2.INF) -> void:
    if tree == null: return
    var cue: String = PROFILE_CUES.get(cue_or_profile, cue_or_profile)
    if not Bank.CUES.has(cue): return
    manager(tree).call("emit_cue", cue, emitter, at)

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_PAUSABLE
    _rng.randomize()
    if AudioServer.get_bus_index(BUS) < 0:
        AudioServer.add_bus()
        var index := AudioServer.bus_count - 1
        AudioServer.set_bus_name(index, BUS)
        AudioServer.set_bus_send(index, "Master")
        # Keep combat cues audible beside the stage score. This is applied at
        # the dedicated bus, never by muting/replacing any user music choice.
        AudioServer.set_bus_volume_db(index, 1.0)
        # Weight: gentle sub/low lift so shots and impacts land with body.
        var eq := AudioEffectEQ6.new()
        eq.set_band_gain_db(0, 2.5)
        eq.set_band_gain_db(1, 1.5)
        eq.set_band_gain_db(5, -1.0)
        AudioServer.add_bus_effect(index, eq)
        # Glue: many weapons at once read as one fight instead of clicks.
        var glue := AudioEffectCompressor.new()
        glue.threshold = -16.0
        glue.ratio = 3.0
        glue.attack_us = 6000.0
        glue.release_ms = 140.0
        glue.gain = 2.0
        AudioServer.add_bus_effect(index, glue)
        # Space: a short industrial-hall reverb gives shots a tail and scale.
        var hall := AudioEffectReverb.new()
        hall.room_size = 0.58
        hall.damping = 0.45
        hall.spread = 0.8
        hall.hipass = 0.22
        hall.predelay_msec = 18.0
        hall.dry = 1.0
        hall.wet = 0.14
        AudioServer.add_bus_effect(index, hall)
        var limiter := AudioEffectLimiter.new()
        limiter.ceiling_db = -1.5
        limiter.threshold_db = -3.0
        AudioServer.add_bus_effect(index, limiter)

func _process(delta: float) -> void:
    _duck_left = maxf(0.0, _duck_left - delta)
    for voice in _voices:
        if is_instance_valid(voice.player):
            voice.player.volume_db = voice.gain_db - (5.0 if _duck_left > 0.0 and voice.priority < 80 else 0.0)

func emit_cue(cue: String, emitter: Node = null, at: Vector2 = Vector2.INF) -> void:
    if not Bank.CUES.has(cue): return
    var frame := Engine.get_physics_frames()
    if frame != _dedup_frame:
        _last_frame.clear()
        _dedup_frame = frame
    # Coalesce fan/pellet events from ONE source only, never distinct actors.
    var emitter_id := emitter.get_instance_id() if is_instance_valid(emitter) else 0
    var key := "%s:%s" % [emitter_id, cue]
    if _last_frame.has(key):
        suppressed_count += 1
        return
    var data: Dictionary = Bank.CUES[cue]
    var now := Time.get_ticks_msec()
    if emitter_id != 0 and cue in COOLDOWN_CUES and now < int(_cooldown_until.get(key, 0)):
        suppressed_count += 1
        return
    _last_frame[key] = true
    _cooldown_until[key] = now + int(data.get("cooldown_ms", 0))
    var priority := int(data.priority)
    # Per-cue cap: a sixth identical impact adds mush, not weight. Steal oldest.
    var same: Array[int] = []
    for i in range(_voices.size()):
        if _voices[i].cue == cue: same.append(i)
    if same.size() >= MAX_VOICES_PER_CUE:
        if priority >= 80:
            _drop_voice(same[0])
        else:
            suppressed_count += 1
            return
    if _voices.size() >= (NORMAL_VOICES if priority < 80 else MAX_VOICES):
        var victim := -1
        for i in range(_voices.size()):
            if int(_voices[i].priority) < 80 and int(_voices[i].priority) <= priority:
                if victim < 0 or int(_voices[i].priority) < int(_voices[victim].priority): victim = i
        if victim < 0:
            suppressed_count += 1
            return
        _drop_voice(victim)
    var streams: Array = data.streams
    # Shuffle-bag order: never the same WAV twice in a row.
    var index := int(_next.get(cue, 0)) % streams.size()
    if streams.size() > 2:
        var previous := int(_next.get(cue + "#last", -1))
        index = _rng.randi_range(0, streams.size() - 1)
        if index == previous: index = (index + 1 + _rng.randi_range(0, streams.size() - 2)) % streams.size()
        _next[cue + "#last"] = index
    else:
        _next[cue] = index + 1
    var position := at
    if not position.is_finite() and emitter is Node2D and is_instance_valid(emitter): position = (emitter as Node2D).global_position
    var spatial := bool(data.get("spatial", false)) and position.is_finite()
    var player: Node
    if spatial:
        var positional := AudioStreamPlayer2D.new()
        positional.max_distance = SPATIAL_MAX_DISTANCE
        positional.attenuation = SPATIAL_ATTENUATION
        positional.panning_strength = 0.65
        positional.global_position = position
        positional.playback_type = AudioServer.PLAYBACK_TYPE_STREAM
        player = positional
    else:
        var flat := AudioStreamPlayer.new()
        # Web exports need streaming playback explicitly, matching the music
        # manager. Without it some browsers prepare the WAV but never advance its
        # voice after the user-triggered combat input.
        flat.playback_type = AudioServer.PLAYBACK_TYPE_STREAM
        player = flat
    player.name = "SFX_" + cue
    player.set("stream", streams[index])
    player.set("bus", BUS)
    var pitch_range: Array = data.get("pitch", [1.0, 1.0])
    player.set("pitch_scale", _rng.randf_range(float(pitch_range[0]), float(pitch_range[1])))
    var gain := float(data.gain_db) + (_rng.randf_range(-1.0, 1.0) if priority < 90 else 0.0)
    player.set("volume_db", gain)
    add_child(player)
    _voices.append({"player":player, "cue":cue, "priority":priority, "gain_db":gain})
    player.connect("finished", _finish.bind(player))
    if cue.begins_with("boss_") and priority >= 85: _duck_left = maxf(_duck_left, 0.8)
    _process(0.0)
    player.call("play")
    played_count += 1
    peak_voices = maxi(peak_voices, _voices.size())
    if debug_trace:
        events.append({"cue":cue, "variant":index, "frame":frame, "emitter":emitter_id,
            "stream":(streams[index] as Resource).resource_path, "gain_db":gain, "spatial":spatial,
            "pitch":float(player.get("pitch_scale"))})
        if events.size() > 4096: events.pop_front()

func _drop_voice(index: int) -> void:
    var voice: Dictionary = _voices[index]
    if is_instance_valid(voice.player):
        voice.player.call("stop")
        voice.player.queue_free()
    _voices.remove_at(index)

func _finish(player: Node) -> void:
    for i in range(_voices.size()-1, -1, -1):
        if _voices[i].player == player: _voices.remove_at(i)
    player.queue_free()

func debug_snapshot() -> Dictionary:
    return {"played":played_count, "suppressed":suppressed_count, "voices":_voices.size(),
        "peak_voices":peak_voices, "duck_left":_duck_left, "events":events.duplicate(true)}
