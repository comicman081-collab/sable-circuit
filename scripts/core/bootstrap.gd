extends Node

const GAME_FLOW := preload("res://scenes/bootstrap/GameFlow.tscn")

func _ready() -> void:
    var flow := GAME_FLOW.instantiate()
    add_child(flow)
