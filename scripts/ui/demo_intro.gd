extends Control
signal completed
const MOVIE := "res://assets/cinematics/sable_intro_original_bgm.ogv"
var player: VideoStreamPlayer
var _done := false

func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    theme = preload("res://scripts/ui/demo_theme.gd").build()
    var black := ColorRect.new()
    black.color = Color.BLACK
    black.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(black)
    player = VideoStreamPlayer.new()
    player.name = "IntroMovie"
    player.expand = true
    player.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    player.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(player)
    var caption := Label.new()
    caption.text = "SABLE CIRCUIT  /  CHAPTER 01     •     ORIGINAL CINEMATIC SOUNDTRACK"
    caption.position = Vector2(32,28)
    add_child(caption)
    var skip := Button.new()
    skip.name = "SkipIntro"
    skip.text = "SKIP INTRO  /  ENTER"
    skip.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
    skip.position = Vector2(-262,-72)
    skip.size = Vector2(230,48)
    skip.pressed.connect(finish)
    add_child(skip)
    skip.grab_focus()
    if FileAccess.file_exists(MOVIE):
        var stream := VideoStreamTheora.new()
        stream.file = MOVIE
        player.stream = stream
        player.finished.connect(finish)
        player.play()
    else:
        caption.text = "INTRO UNAVAILABLE / CONTINUE WITH SKIP"

func _unhandled_key_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo and event.keycode in [KEY_ESCAPE, KEY_ENTER, KEY_SPACE]:
        get_viewport().set_input_as_handled()
        finish()

func finish() -> void:
    if _done: return
    _done = true
    player.stop()
    completed.emit()
