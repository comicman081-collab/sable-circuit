extends Node

const PROTOTYPE_ARENA := preload("res://scenes/mission/PrototypeArena.tscn")

func _ready() -> void:
    var arena := PROTOTYPE_ARENA.instantiate()
    add_child(arena)
