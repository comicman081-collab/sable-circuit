extends CanvasLayer
## F9 field readout for tuning: FPS, live hostiles, hostiles currently attacking against the
## concurrent-attack cap, and where the play-session log is written.
const DemoInput := preload("res://scripts/ui/demo_input.gd")
const Tactics := preload("res://scripts/combat/site7_enemy_tactics.gd")
const ATTACK_STATES := ["WINDUP", "BURST", "LUNGE"]

var _label: Label
var _latch := false

func _ready() -> void:
    layer = 90
    _label = Label.new()
    _label.name = "Readout"
    # Top right, under the cargo / intel readout: the top-left corner is the minimap.
    _label.position = Vector2(1280 - 12 - 320, 104)
    _label.size = Vector2(320, 72)
    _label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _label.grow_horizontal = Control.GROW_DIRECTION_BEGIN
    _label.add_theme_font_size_override("font_size", 15)
    _label.add_theme_color_override("font_color", Color("d8f3ff"))
    _label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
    _label.add_theme_constant_override("outline_size", 5)
    _label.visible = false
    add_child(_label)

func _process(_delta: float) -> void:
    var pressed := DemoInput.key(KEY_F9)
    if pressed and not _latch:
        _label.visible = not _label.visible
    _latch = pressed
    if _label.visible:
        _label.text = readout()

func counts() -> Dictionary:
    var live := 0
    var attacking := 0
    for node in get_tree().get_nodes_in_group("m3_enemies"):
        live += 1
        var tactics = node.get("tactics")
        if tactics != null and str(tactics.state) in ATTACK_STATES:
            attacking += 1
    return {"live": live, "attacking": attacking}

func readout() -> String:
    var data := counts()
    var lines := [
        "FPS %d" % Engine.get_frames_per_second(),
        "HOSTILES %d   ATTACKING %d / %d" % [data.live, data.attacking, Tactics.MAX_CONCURRENT_ATTACKERS],
    ]
    var session_log := get_parent().get_node_or_null("PlaySessionLog") as PlaySessionLog
    if session_log == null:
        lines.append("PLAY LOG off")
    else:
        lines.append("PLAY LOG -> " + ProjectSettings.globalize_path(session_log.output_dir))
    return "\n".join(lines)
