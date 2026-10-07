extends CanvasLayer

var _label: Label
var _squad: SquadController

func _ready() -> void:
    _label = Label.new()
    _label.position = Vector2(24, 20)
    _label.add_theme_font_size_override("font_size", 18)
    _label.add_theme_color_override("font_color", Color("eaf5ff"))
    add_child(_label)
    _squad = get_tree().get_first_node_in_group("squad_controller") as SquadController

func _process(_delta: float) -> void:
    if _squad == null:
        _squad = get_tree().get_first_node_in_group("squad_controller") as SquadController
        return
    var active := _squad.get_active_operator()
    if active == null:
        return
    _label.text = "SABLE CIRCUIT // PLAYABLE SQUAD PROTOTYPE\n" + \
        "WASD Move  SHIFT Run  LMB Fire  R Reload  SPACE Evade  1/2/3 Swap\n" + \
        "ACTIVE: %s   AMMO: %02d/%02d   FACING SECTOR: %d   AI WINGMEN: LIVE" % [active.display_name, active.ammo, active.magazine_size, active.facing_sector]
