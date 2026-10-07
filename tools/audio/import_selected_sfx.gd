extends SceneTree
## Scoped engine serialization avoids importing the project's historical art/QA tree.
func _init() -> void:
    var directory := "res://qa/sfx_integration_20260919/selected_pcm16/"
    var count := 0
    for filename in DirAccess.get_files_at(directory):
        if not filename.ends_with(".wav"): continue
        var audio := AudioStreamWAV.load_from_file(directory + filename)
        assert(audio != null and audio.mix_rate == 48000)
        var destination := "res://assets/audio/combat_r04/" + filename.get_basename() + ".res"
        assert(ResourceSaver.save(audio, destination) == OK)
        count += 1
    print("SELECTED_SFX_SERIALIZED: ", count)
    quit()
