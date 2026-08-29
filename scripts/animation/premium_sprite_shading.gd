extends Node
class_name PremiumSpriteShading

const SHADER := preload("res://assets/shaders/premium_2p5d_sprite.gdshader")

var _bound := false
var _material: ShaderMaterial

func _ready() -> void:
    call_deferred("_bind")

func _bind() -> void:
    if _bound:
        return
    var owner_actor := get_parent()
    var accent := _resolve_accent(owner_actor)
    _material = ShaderMaterial.new()
    _material.shader = SHADER
    _material.set_shader_parameter("accent_color", accent)
    _material.set_shader_parameter("top_light", 0.20)
    _material.set_shader_parameter("lower_shadow", 0.26)
    _material.set_shader_parameter("rim_strength", 0.08)
    _material.set_shader_parameter("contrast", 1.12)
    _material.set_shader_parameter("saturation", 0.96)
    _material.set_shader_parameter("bounce_strength", 0.08)
    _material.set_shader_parameter("sheen_strength", 0.12)
    _material.set_shader_parameter("edge_ao_strength", 0.07)
    _material.set_shader_parameter("ink_softening", 0.24)

    var sprites: Array[Sprite2D] = []
    _collect_sprites(owner_actor, sprites)
    for sprite in sprites:
        if sprite.name == "UniqueMasterSprite":
            continue
        sprite.material = _material
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
        if "RIFLE" in id: return Color("ef7d72")
        if "SHIELD" in id: return Color("f0ad55")
        if "DRONE" in id: return Color("e667a0")
        if "ABERRANT" in id: return Color("c566d9")
        if "BOSS" in id or "ANCHOR" in id: return Color("a78cff")
    return Color("72dbe8")

func debug_bound() -> bool:
    return _bound

func debug_premium_volume_contract() -> bool:
    if not _bound or _material == null:
        return false
    return (
        float(_material.get_shader_parameter("lower_shadow")) >= 0.25
        and float(_material.get_shader_parameter("bounce_strength")) > 0.0
        and float(_material.get_shader_parameter("sheen_strength")) > 0.0
        and float(_material.get_shader_parameter("saturation")) <= 0.98
        and float(_material.get_shader_parameter("ink_softening")) >= 0.20
    )
