extends RefCounted
class_name ProceduralCombatSFX

## M3 runtime proof sounds. These are intentionally unique per identity profile and
## will be replaced by production recordings/synthesis while preserving profile IDs.
static func play(tree: SceneTree, profile_id: String, volume_db: float = -11.0) -> void:
    if tree == null:
        return
    var player := AudioStreamPlayer.new()
    player.name = "SFX_" + profile_id
    player.volume_db = volume_db
    player.stream = _build_stream(profile_id)
    tree.root.add_child(player)
    player.finished.connect(player.queue_free)
    player.play()

static func _build_stream(profile_id: String) -> AudioStreamWAV:
    var spec: Dictionary = _spec(profile_id)
    var rate: int = 22050
    var duration: float = float(spec["duration"])
    var sample_count: int = maxi(64, int(duration * float(rate)))
    var bytes := PackedByteArray()
    bytes.resize(sample_count * 2)
    var rng := RandomNumberGenerator.new()
    rng.seed = abs(profile_id.hash()) + 1

    var attack_time: float = float(spec["attack"])
    var decay_power: float = float(spec["decay"])
    var base_hz: float = float(spec["base_hz"])
    var sweep_hz: float = float(spec["sweep_hz"])
    var harmonic_ratio: float = float(spec["harmonic_ratio"])
    var phase_offset: float = float(spec["phase_offset"])
    var fundamental_mix: float = float(spec["fundamental_mix"])
    var harmonic_mix: float = float(spec["harmonic_mix"])
    var square_mix: float = float(spec["square_mix"])
    var noise_mix: float = float(spec["noise_mix"])
    var pulse_hz: float = float(spec["pulse_hz"])
    var pulse_mix: float = float(spec["pulse_mix"])
    var click_strength: float = float(spec["click_strength"])
    var gain: float = float(spec["gain"])

    for i in range(sample_count):
        var t: float = float(i) / float(sample_count - 1)
        var attack: float = clampf(t / maxf(0.002, attack_time), 0.0, 1.0)
        var env: float = attack * pow(maxf(0.0, 1.0 - t), decay_power)
        var phase: float = TAU * (base_hz * t * duration + 0.5 * sweep_hz * t * t * duration)
        var fundamental: float = sin(phase)
        var harmonic: float = sin(phase * harmonic_ratio + phase_offset)
        var squareish: float = signf(sin(phase * 0.5 + 0.3))
        var noise: float = rng.randf_range(-1.0, 1.0)
        var pulse: float = sin(TAU * pulse_hz * t * duration) if pulse_hz > 0.0 else 0.0
        var value: float = fundamental * fundamental_mix + harmonic * harmonic_mix + squareish * square_mix + noise * noise_mix + pulse * pulse_mix
        if click_strength > 0.0:
            value += exp(-t * 95.0) * click_strength * (1.0 if i % 2 == 0 else -1.0)
        value = clampf(value * env * gain, -1.0, 1.0)
        var sample: int = int(round(value * 32767.0))
        var unsigned: int = sample & 0xffff
        bytes[i * 2] = unsigned & 0xff
        bytes[i * 2 + 1] = (unsigned >> 8) & 0xff

    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = rate
    stream.stereo = false
    stream.data = bytes
    return stream

static func _spec(profile_id: String) -> Dictionary:
    var s := {
        "duration": 0.12, "attack": 0.004, "decay": 2.4,
        "base_hz": 520.0, "sweep_hz": -180.0, "harmonic_ratio": 2.0,
        "phase_offset": 0.0, "fundamental_mix": 0.65, "harmonic_mix": 0.22,
        "square_mix": 0.05, "noise_mix": 0.08, "pulse_hz": 0.0,
        "pulse_mix": 0.0, "click_strength": 0.25, "gain": 0.72
    }
    if "ASTER" in profile_id:
        s.merge({"duration":0.095,"base_hz":780.0,"sweep_hz":-260.0,"harmonic_ratio":2.7,"harmonic_mix":0.34,"noise_mix":0.035,"click_strength":0.42,"decay":3.1}, true)
    elif "ROOK" in profile_id:
        s.merge({"duration":0.19,"base_hz":118.0,"sweep_hz":-42.0,"harmonic_ratio":1.53,"fundamental_mix":0.82,"square_mix":0.18,"noise_mix":0.16,"click_strength":0.30,"decay":1.55,"gain":0.86}, true)
    elif "MICA" in profile_id:
        s.merge({"duration":0.16,"base_hz":620.0,"sweep_hz":-410.0,"harmonic_ratio":1.75,"pulse_hz":64.0,"pulse_mix":0.18,"noise_mix":0.025,"click_strength":0.12,"decay":2.05}, true)
    elif "RIFLE" in profile_id:
        s.merge({"duration":0.09,"base_hz":360.0,"sweep_hz":-90.0,"harmonic_ratio":2.2,"square_mix":0.15,"noise_mix":0.18,"click_strength":0.38,"decay":3.6}, true)
    elif "SHIELD" in profile_id:
        s.merge({"duration":0.23,"base_hz":142.0,"sweep_hz":-65.0,"harmonic_ratio":1.34,"fundamental_mix":0.75,"square_mix":0.20,"noise_mix":0.12,"pulse_hz":41.0,"pulse_mix":0.12,"decay":1.4,"gain":0.9}, true)
    elif "DRONE" in profile_id:
        s.merge({"duration":0.13,"base_hz":1040.0,"sweep_hz":520.0,"harmonic_ratio":1.62,"pulse_hz":92.0,"pulse_mix":0.25,"noise_mix":0.04,"click_strength":0.09,"decay":2.6}, true)
    elif "ABERRANT" in profile_id:
        s.merge({"duration":0.21,"base_hz":174.0,"sweep_hz":90.0,"harmonic_ratio":0.73,"noise_mix":0.24,"pulse_hz":29.0,"pulse_mix":0.19,"click_strength":0.05,"decay":1.7}, true)
    elif "BOSS_ANCHOR" in profile_id or "ANCHOR" in profile_id:
        s.merge({"duration":0.36,"base_hz":78.0,"sweep_hz":420.0,"harmonic_ratio":2.41,"fundamental_mix":0.7,"harmonic_mix":0.42,"square_mix":0.08,"noise_mix":0.10,"pulse_hz":17.0,"pulse_mix":0.23,"click_strength":0.30,"decay":1.25,"gain":0.92}, true)
    return s
