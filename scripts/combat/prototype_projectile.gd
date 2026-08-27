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
    z_index = 45
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
        draw_line(Vector2(-42, 0), Vector2(6, 0), Color(tint, 0.18), 7.0)
        draw_line(Vector2(-28, 0), Vector2(8, 0), Color(tint, 0.70), 2.5)
        draw_circle(Vector2(9, 0), 3.2, tint)

func _draw_aster() -> void:
    # Precision coil dart: long cool sheath + segmented white core + warm needle tip.
    draw_line(Vector2(-76,0),Vector2(9,0),Color(0.33,0.86,1.0,0.11),8.0)
    draw_line(Vector2(-56,0),Vector2(12,0),Color(tint,0.42),3.2)
    for x in [-52.0,-35.0,-18.0]:
        draw_line(Vector2(x,0),Vector2(x+10.0,0),Color("eaf9ff",0.76),1.8)
    draw_line(Vector2(-7,0),Vector2(15,0),Color("f4fbff"),2.4)
    draw_circle(Vector2(17,0),4.0,Color("ffcf70"))
    draw_circle(Vector2(17,0),8.0,Color(1.0,0.76,0.30,0.10))

func _draw_rook() -> void:
    # Heavy magnetic pellet: broad pressure wake instead of a thin tracer.
    draw_line(Vector2(-50,0),Vector2(-8,0),Color("d39a58",0.13),13.0)
    draw_line(Vector2(-38,0),Vector2(-7,0),Color("ffe0ad",0.34),6.0)
    draw_polygon(PackedVector2Array([Vector2(-12,-5),Vector2(8,-7),Vector2(17,0),Vector2(8,7),Vector2(-12,5)]),PackedColorArray([Color("d6a15f")]))
    draw_line(Vector2(-2,0),Vector2(12,0),Color("fff0c8"),2.0)

func _draw_mica() -> void:
    # Sensor pulse: a hollow teal packet with telemetry beads trailing behind it.
    draw_line(Vector2(-62,0),Vector2(-12,0),Color("62d8c8",0.10),8.0)
    draw_circle(Vector2.ZERO,8.0,Color("62d8c8",0.13),true)
    draw_circle(Vector2.ZERO,7.0,Color("7cf4e7"),false,2.5)
    draw_circle(Vector2.ZERO,2.5,Color("e9fff9"),true)
    for x in [-48.0,-34.0,-21.0,-11.0]:
        draw_circle(Vector2(x,0),1.8,Color("62d8c8",0.52),true)

func _draw_rifle() -> void:
    draw_line(Vector2(-64,0),Vector2(10,0),Color("c93643",0.12),8.0)
    draw_line(Vector2(-48,0),Vector2(13,0),Color("eef5f7",0.80),2.0)
    for x in [-43.0,-27.0,-11.0,4.0]:
        draw_line(Vector2(x,0),Vector2(x+7,0),Color("d84d59"),3.0)
    draw_circle(Vector2(14,0),2.6,Color("fff0ee"))

func _draw_shield() -> void:
    draw_line(Vector2(-48,0),Vector2(-13,0),Color("e2a94e",0.16),14.0)
    draw_rect(Rect2(-15,-6,31,12),Color("e2a94e"),true)
    draw_rect(Rect2(-7,-3,24,6),Color("fff0b2"),true)
    draw_rect(Rect2(-28,-8,11,16),Color("7d342e",0.45),true)

func _draw_drone() -> void:
    draw_line(Vector2(-66,0),Vector2(11,0),Color("e45a91",0.12),7.0)
    draw_line(Vector2(-48,0),Vector2(13,0),Color("e45a91",0.52),2.0)
    for x in [-36.0,-23.0,-10.0,3.0]:
        draw_circle(Vector2(x,sin(x*0.18)*2.2),2.6,Color("e45a91"),true)
    draw_circle(Vector2(14,0),4.0,Color("65e1e8"),true)

func _draw_aberrant() -> void:
    draw_line(Vector2(-50,4),Vector2(-8,1),Color("da6b83",0.18),9.0)
    draw_polygon(PackedVector2Array([Vector2(-12,-7),Vector2(5,-9),Vector2(15,-2),Vector2(10,8),Vector2(-5,10),Vector2(-15,3)]),PackedColorArray([Color("934eb4")]))
    draw_line(Vector2(-9,-2),Vector2(10,1),Color("ef9ab0"),2.2)

func _draw_anchor() -> void:
    # Phase lance: long violet/magenta energy rail with a bright core.
    draw_line(Vector2(-88,0),Vector2(18,0),Color("9179ff",0.11),16.0)
    draw_line(Vector2(-72,0),Vector2(19,0),Color("f0529d",0.34),7.0)
    draw_rect(Rect2(-24,-8,43,16),Color("8572ff"),true)
    draw_rect(Rect2(-10,-4,31,8),Color("f5dcff"),true)
    for x in [-60.0,-45.0,-31.0]:
        draw_line(Vector2(x,-9),Vector2(x,9),Color("0b0b12",0.72),3.0)
