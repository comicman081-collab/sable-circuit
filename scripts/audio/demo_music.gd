extends Node
signal mute_changed
## Persistent scene soundtrack. Exactly two voices; no effect on SFX or saves.
const CATALOG := "res://sound/music/catalog.json"
var catalog: Dictionary = {}
var voices: Array[AudioStreamPlayer] = []
var current_key := ""
var active := 0
var muted := false
var transition: Tween

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS
    add_to_group("sable_music")
    catalog = JSON.parse_string(FileAccess.get_file_as_string(CATALOG))
    if AudioServer.get_bus_index("SableMusic") < 0:
        AudioServer.add_bus()
        AudioServer.set_bus_name(AudioServer.bus_count - 1, "SableMusic")
        AudioServer.set_bus_send(AudioServer.bus_count - 1, "Master")
    for i in range(2):
        var voice := AudioStreamPlayer.new()
        voice.bus = "SableMusic"
        # Stream playback preserves the standard mixer on web as well as native.
        voice.playback_type = AudioServer.PLAYBACK_TYPE_STREAM
        add_child(voice)
        voices.append(voice)

func _process(_delta: float) -> void:
    AudioServer.set_bus_volume_db(AudioServer.get_bus_index("SableMusic"), -8.0 if get_tree().paused else 0.0)

func _unhandled_key_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_M:
        toggle_mute()
        get_viewport().set_input_as_handled()

func toggle_mute() -> void:
    muted = not muted
    AudioServer.set_bus_mute(AudioServer.get_bus_index("SableMusic"), muted)
    mute_changed.emit()

func select_state(state: String, mission_id: String = "") -> void:
    if state == "INTRO":
        # The cinematic carries its own authored six-clip soundtrack.
        # Never layer a separately selected music cue over it.
        silence()
    elif state == "TITLE": play_track("title")
    elif state in ["BASE", "BRIEFING"]: play_track("base")
    elif state == "RESULTS": play_track("results")
    elif state.begins_with("STAGE_") or state == "BATTLE_PREVIEW":
        play_track(stage_key(mission_id))
    else: silence()

## Operations 1-5 have their own cue. A later operation reuses the cues in order
## until its own track is added to catalog.json as "stage<N>"; nothing else changes.
func stage_key(mission_id: String) -> String:
    var number := maxi(1, int(mission_id.right(2)))
    var key := "stage%d" % number
    if catalog.has(key): return key
    var own := 1
    while catalog.has("stage%d" % (own + 1)): own += 1
    return "stage%d" % ((number - 1) % own + 1)

func play_track(key: String) -> void:
    if key == current_key: return
    if not catalog.has(key):
        push_error("Missing soundtrack cue: " + key)
        return
    var entry: Dictionary = catalog[key]
    var stream := AudioStreamMP3.load_from_buffer(FileAccess.get_file_as_bytes(str(entry.path)))
    if stream == null or stream.get_length() < 1.0:
        push_error("Invalid soundtrack: " + str(entry.path))
        return
    stream.loop = true
    if transition != null and transition.is_valid(): transition.kill()
    var previous := voices[active]
    active = 1 - active
    var next := voices[active]
    next.stop()
    next.stream = stream
    next.volume_db = -60.0
    next.play()
    current_key = key
    transition = create_tween().set_parallel(true)
    transition.tween_property(next, "volume_db", float(entry.gain_db), 0.85)
    transition.tween_property(previous, "volume_db", -60.0, 0.85)
    transition.chain().tween_callback(previous.stop)

func silence() -> void:
    if transition != null and transition.is_valid(): transition.kill()
    for voice in voices: voice.stop()
    current_key = ""

static func encounter(tree: SceneTree, mission_id: String, boss: bool) -> void:
    for music in tree.get_nodes_in_group("sable_music"):
        music.play_track("boss" if boss else music.stage_key(mission_id))
