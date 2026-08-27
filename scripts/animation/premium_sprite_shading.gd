extends Node
class_name PremiumSpriteShading

const SHADER := preload("res://assets/shaders/premium_2p5d_sprite.gdshader")

var _bound := false

func _ready() -> void:
    call_deferred("_bind")

func _bind() -> void:
    if _bound:
        return
    var owner_actor := get_parent()
    var accent := _resolve_accent(owner_actor)
    var material := ShaderMaterial.new()
    material.shader = SHADER
    material.set_shader_parameter("accent_color", accent)
    material.set_shader_parameter("top_light", 0.24)
    material.set_shader_parameter("lower_shadow", 0.22)
    material.set_shader_parameter("rim_strength", 0.14)
    material.set_shader_parameter("contrast", 1.10)
    material.set_shader_parameter("saturation", 1.06)

    var sprites: Array[Sprite2D] = []
    _collect_sprites(owner_actor, sprites)
    for sprite in sprites:
        if sprite.name == "UniqueMasterSprite":
            continue
        sprite.material = material
    _bound = true

func _collect_sprites(node: Node, out: Array[Sprite2D]) -> void:
    for child in node.get_children():
        if child is Sprite2D:
            out.append(child as Sprite2D)
        _collect_sprites(child, out)

func _resolve_accent(owner_actor: Node) -> Color:
    if owner_actor is OperatorActor:
        return (owner_actor as OperatorActor).accent_color
    if owner_actor is EnemyActor:
        var id := (owner_actor as EnemyActor).enemy_id
        if "RIFLE" in id:
            return Color("ef7d72")
        if "SHIELD" in id:
            return Color("f0ad55")
        if "DRONE" in id:
            return Color("e667a0")
        if "ABERRANT" in id:
            return Color("c566d9")
        if "BOSS" in id or "ANCHOR" in id:
            return Color("a78cff")
    return Color("72dbe8")

func debug_bound() -> bool:
    return _bound
