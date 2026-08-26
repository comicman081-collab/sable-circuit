extends Node2D
class_name PrototypeProjectile

var direction := Vector2.RIGHT
var speed := 720.0
var damage := 10.0
var lifetime := 1.1
var owner_actor: Node = null
var tint := Color("fff0a8")
var art_profile: Dictionary = {}
var projectile_profile := "PRJ_GENERIC"
var target_group := "prototype_targets"

func setup(origin: Vector2, dir: Vector2, source: Node, color: Color, profile: Dictionary = {}, hit_group: String = "prototype_targets") -> void:
    global_position = origin
    direction = dir.normalized() if dir.length_squared() > 0.0 else Vector2.RIGHT
    owner_actor = source
    tint = color
    art_profile = profile.duplicate(true)
    projectile_profile = str(art_profile.get("projectile_profile", "PRJ_GENERIC"))
    target_group = hit_group
    rotation = direction.angle()
    _apply_profile_tuning()
    queue_redraw()

func _apply_profile_tuning() -> void:
    if "ASTER" in projectile_profile:
        speed = 1040.0; damage = 10.0; lifetime = 0.9
    elif "ROOK" in projectile_profile:
        speed = 760.0; damage = 7.0; lifetime = 0.58
    elif "MICA" in projectile_profile:
        speed = 640.0; damage = 8.0; lifetime = 1.22
    elif "RIFLE" in projectile_profile:
        speed = 900.0; damage = 8.0
    elif "SHIELD" in projectile_profile:
        speed = 620.0; damage = 16.0
    elif "DRONE" in projectile_profile:
        speed = 780.0; damage = 7.0
    elif "ABERRANT" in projectile_profile:
        speed = 440.0; damage = 12.0; lifetime = 1.5
    elif "ANCHOR" in projectile_profile:
        speed = 560.0; damage = 24.0; lifetime = 1.6

func _physics_process(delta: float) -> void:
    global_position += direction * speed * delta
    lifetime -= delta
    for target in get_tree().get_nodes_in_group(target_group):
        if not is_instance_valid(target) or target == owner_actor:
            continue
        if target is Node2D and global_position.distance_squared_to(target.global_position) <= 24.0 * 24.0:
            if target.has_method("apply_damage"):
                target.apply_damage(damage)
            CombatFeedback.spawn_hit(get_tree(), global_position, art_profile, tint)
            queue_free()
            return
    if lifetime <= 0.0:
        queue_free()

func _draw() -> void:
    if "ASTER" in projectile_profile: _draw_aster()
    elif "ROOK" in projectile_profile: _draw_rook()
    elif "MICA" in projectile_profile: _draw_mica()
    elif "RIFLE" in projectile_profile: _draw_rifle()
    elif "SHIELD" in projectile_profile: _draw_shield()
    elif "DRONE" in projectile_profile: _draw_drone()
    elif "ABERRANT" in projectile_profile: _draw_aberrant()
    elif "ANCHOR" in projectile_profile: _draw_anchor()
    else:
        draw_line(Vector2(-10, 0), Vector2(5, 0), Color(tint, 0.55), 3.0)
        draw_circle(Vector2(5, 0), 3.0, tint)

func _draw_aster() -> void:
    for x in [-22.0, -12.0, -2.0]: draw_line(Vector2(x,0),Vector2(x+7.0,0),Color(tint,0.5),2.0)
    draw_line(Vector2(-3,0),Vector2(13,0),tint,2.5); draw_circle(Vector2(15,0),2.8,Color("ffcf70"))
func _draw_rook() -> void:
    draw_polygon(PackedVector2Array([Vector2(-12,-4),Vector2(8,-6),Vector2(15,0),Vector2(7,6),Vector2(-12,4)]),PackedColorArray([tint.darkened(0.2)])); draw_line(Vector2(-22,0),Vector2(-8,0),Color(tint,0.42),6.0)
func _draw_mica() -> void:
    draw_circle(Vector2.ZERO,7.0,Color(tint,0.18),true); draw_circle(Vector2.ZERO,6.0,tint,false,2.5); draw_circle(Vector2.ZERO,2.0,Color("e9ffe0"),true)
    for x in [-20.0,-12.0,-5.0]: draw_circle(Vector2(x,0),1.5,Color(tint,0.45),true)
func _draw_rifle() -> void:
    draw_line(Vector2(-20,0),Vector2(13,0),Color("eef5f7"),2.0)
    for x in [-17.0,-7.0,3.0]: draw_line(Vector2(x,0),Vector2(x+5,0),Color("b83b45"),3.0)
func _draw_shield() -> void:
    draw_rect(Rect2(-13,-5,27,10),Color("e2a94e"),true); draw_rect(Rect2(-24,-7,10,14),Color("7d342e",0.42),true)
func _draw_drone() -> void:
    for x in [-19.0,-10.0,-1.0,8.0]: draw_circle(Vector2(x,sin(x)*2.0),2.5,Color("d9577d"),true)
    draw_circle(Vector2(13,0),3.2,Color("65e1e8"),true)
func _draw_aberrant() -> void:
    draw_polygon(PackedVector2Array([Vector2(-10,-6),Vector2(5,-8),Vector2(13,-2),Vector2(9,7),Vector2(-5,9),Vector2(-13,3)]),PackedColorArray([Color("7f3fa4")])); draw_line(Vector2(-22,4),Vector2(-8,1),Color("da6b83",0.6),3.0)
func _draw_anchor() -> void:
    draw_rect(Rect2(-22,-7,38,14),Color("8572ff"),true); draw_rect(Rect2(-10,-4,28,8),Color("f0529d"),true)
    for x in [-30.0,-20.0]: draw_line(Vector2(x,-8),Vector2(x,8),Color("0b0b12",0.75),3.0)
