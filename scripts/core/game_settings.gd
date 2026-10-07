extends RefCounted
class_name GameSettings
## Player preferences that outlive a run, stored apart from campaign saves in
## user://settings.cfg (IndexedDB on the web build).

const PATH := "user://settings.cfg"

static var screen_shake := true
static var _loaded := false

static func load_once() -> void:
    if _loaded: return
    _loaded = true
    var config := ConfigFile.new()
    if config.load(PATH) == OK:
        screen_shake = bool(config.get_value("display", "screen_shake", true))

static func set_screen_shake(enabled: bool) -> void:
    load_once()
    screen_shake = enabled
    var config := ConfigFile.new()
    config.load(PATH)
    config.set_value("display", "screen_shake", enabled)
    if config.save(PATH) != OK:
        push_warning("GameSettings could not save " + PATH)
