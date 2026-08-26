extends CharacterBody2D
class_name EnemyActor

const Projectile := preload("res://scripts/combat/prototype_projectile.gd")

signal defeated(enemy: EnemyActor)

@export var enemy_id := "ENM_SITE7_RIFLE_01"
@export var max_health := 100.0

var health := 100.0
var art_profile: Dictionary = {}
var home_position := Vector2.ZERO
var _visual_root: Node2D
var _master_sprite: Sprite2D
var _phase := 0.0
var _attack_cd := 0.8
var _hit_flash := 0.0
var _lunge_left := 0.0
var _orbit_sign := 1.0

func _ready() -> void:
    add_to_group("prototype_targets")
    add_to_group("m3_enemies")
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    health = max_health
    home_position = global_position
    _orbit_sign = -1.0 if abs(enemy_id.hash()) % 2 == 0 else 1.0
    _build_high_res_visual()
    queue_redraw()

func configure(id_value: String, hp: float = -1.0) -> void:
    enemy_id = id_value
    art_profile = ArtProfileRegistry.get_profile(enemy_id)
    if hp > 0.0:
        max_health = hp
    health = max_health
    if is_node_ready():
        _rebuild_visual()

func apply_damage(amount: float) -> void:
    health = maxf(0.0, health - amount)
    _hit_flash = 1.0
    if health <= 0.0:
        remove_from_group("prototype_targets")
        defeated.emit(self)
        queue_free()
        return
    queue_redraw()

func _physics_process(delta: float) -> void:
    _phase += delta
    _attack_cd = maxf(0.0, _attack_cd - delta)
    _hit_flash = move_toward(_hit_flash, 0.0, delta * 4.5)
    var target := _nearest_operator()
    if target:
        _update_tactics(target, delta)
    else:
        velocity = velocity.move_toward(Vector2.ZERO, 260.0 * delta)
    move_and_slide()
    _animate_identity()
    queue_redraw()

func _nearest_operator() -> OperatorActor:
    var best: OperatorActor = null
    var best_d2 := INF
    for node in get_tree().get_nodes_in_group("operators"):
        if node is OperatorActor:
            var d2 := global_position.distance_squared_to(node.global_position)
            if d2 < best_d2:
                best_d2 = d2
                best = node
    return best

func _update_tactics(target: OperatorActor, delta: float) -> void:
    var to_target := target.global_position - global_position
    var dist := to_target.length()
    var dir := to_target.normalized() if dist > 0.001 else Vector2.RIGHT
    var motion := str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion:
        var radial := 0.0
        if dist > 350.0: radial = 1.0
        elif dist < 250.0: radial = -0.8
        var side := Vector2(-dir.y, dir.x) * sin(_phase * 2.2) * 0.72
        velocity = (dir * radial + side).limit_length(1.0) * 105.0
        _try_attack(dir, 1.05)
    elif "SHIELD" in motion:
        velocity = dir * (72.0 if dist > 190.0 else 18.0)
        _try_attack(dir, 1.65)
    elif "DRONE" in motion:
        var tangent := Vector2(-dir.y, dir.x) * _orbit_sign
        var radial := clampf((dist - 300.0) / 140.0, -0.7, 0.7)
        velocity = (tangent * 0.9 + dir * radial).normalized() * 138.0
        _try_attack(dir, 0.78)
    elif "ABERRANT" in motion:
        if _lunge_left > 0.0:
            _lunge_left = maxf(0.0, _lunge_left - delta)
            velocity = dir * 330.0
        elif dist > 130.0:
            velocity = dir * 126.0
            if dist < 270.0 and _attack_cd <= 0.0:
                _lunge_left = 0.22
                _attack_cd = 1.35
        else:
            velocity = Vector2.ZERO
            _try_attack(dir, 1.25)
    elif "BOSS" in motion or "ANCHOR" in motion:
        velocity = Vector2(sin(_phase * 0.7), cos(_phase * 0.53)) * 18.0
        _try_attack(dir.rotated(sin(_phase * 0.8) * 0.18), 1.18)
    else:
        velocity = dir * 80.0
        _try_attack(dir, 1.2)

func _try_attack(dir: Vector2, interval: float) -> void:
    if _attack_cd > 0.0:
        return
    _attack_cd = interval
    CombatFeedback.play_fire(get_tree(), art_profile)
    var projectile := Projectile.new()
    get_tree().root.add_child(projectile)
    projectile.setup(global_position + dir * 32.0, dir, self, _projectile_color(), art_profile, "operators")
    if "BOSS" in str(art_profile.get("projectile_profile", "")):
        for angle in [-0.16, 0.16]:
            var extra := Projectile.new()
            get_tree().root.add_child(extra)
            extra.setup(global_position + dir.rotated(angle) * 32.0, dir.rotated(angle), self, _projectile_color(), art_profile, "operators")

func _projectile_color() -> Color:
    var p := str(art_profile.get("projectile_profile", ""))
    if "RIFLE" in p: return Color("d95c65")
    if "SHIELD" in p: return Color("e2a94e")
    if "DRONE" in p: return Color("d9577d")
    if "ABERRANT" in p: return Color("a055c5")
    if "ANCHOR" in p: return Color("9b7cff")
    return Color.WHITE

func _build_high_res_visual() -> void:
    _visual_root = Node2D.new()
    _visual_root.name = "HighResVisualRoot"
    add_child(_visual_root)
    _master_sprite = Sprite2D.new()
    _master_sprite.name = "UniqueMasterSprite"
    var asset_path := str(art_profile.get("master_asset", ""))
    if not asset_path.is_empty() and ResourceLoader.exists("res://" + asset_path):
        _master_sprite.texture = load("res://" + asset_path) as Texture2D
    _visual_root.add_child(_master_sprite)
    _fit_master_sprite()

func _fit_master_sprite() -> void:
    if not is_instance_valid(_master_sprite) or _master_sprite.texture == null:
        return
    var desired_height := 105.0
    if "SHIELD" in enemy_id: desired_height = 132.0
    elif "DRONE" in enemy_id: desired_height = 82.0
    elif "ABERRANT" in enemy_id: desired_height = 118.0
    elif "BOSS" in enemy_id: desired_height = 230.0
    var h := float(_master_sprite.texture.get_height())
    var scale_value := desired_height / maxf(1.0, h)
    _master_sprite.scale = Vector2.ONE * scale_value
    _master_sprite.position.y = -desired_height * 0.48

func _rebuild_visual() -> void:
    if is_instance_valid(_visual_root):
        _visual_root.queue_free()
    _build_high_res_visual()

func _animate_identity() -> void:
    if not is_instance_valid(_visual_root):
        return
    var motion := str(art_profile.get("motion_profile", ""))
    if "RIFLE" in motion:
        _visual_root.position.y = sin(_phase * 7.2) * 1.4 * minf(1.0, velocity.length() / 100.0)
        _visual_root.rotation = sin(_phase * 4.1) * 0.018
    elif "SHIELD" in motion:
        _visual_root.position.y = absf(sin(_phase * 4.1)) * 3.2
        _visual_root.rotation = -0.035 + sin(_phase * 2.0) * 0.012
    elif "DRONE" in motion:
        _visual_root.position.y = sin(_phase * 3.8) * 7.0
        _visual_root.rotation = sin(_phase * 2.6) * 0.11
    elif "ABERRANT" in motion:
        _visual_root.position.y = absf(sin(_phase * 6.6)) * 4.5
        _visual_root.rotation = sin(_phase * 3.3) * 0.08
        _visual_root.scale = Vector2(1.0 + sin(_phase * 6.6) * 0.025, 1.0 - sin(_phase * 6.6) * 0.035)
    elif "BOSS" in motion or "ANCHOR" in motion:
        _visual_root.position.y = sin(_phase * 1.2) * 9.0
        _visual_root.rotation = sin(_phase * 0.72) * 0.045
    if is_instance_valid(_master_sprite):
        _master_sprite.modulate = Color.WHITE.lerp(Color("ff8a8a"), _hit_flash * 0.7)

func _draw() -> void:
    var ratio := clampf(health / maxf(1.0, max_health), 0.0, 1.0)
    var width := 58.0 if "BOSS" not in enemy_id else 130.0
    draw_ellipse_shadow()
    draw_rect(Rect2(-width * 0.5, -82 if "BOSS" not in enemy_id else -150, width, 5), Color("172028"), true)
    draw_rect(Rect2(-width * 0.5 + 1, (-81 if "BOSS" not in enemy_id else -149), (width - 2) * ratio, 3), _projectile_color(), true)

func draw_ellipse_shadow() -> void:
    var radius := 30.0 if "BOSS" not in enemy_id else 82.0
    draw_circle(Vector2(0, 5), radius, Color(0.02,0.03,0.04,0.26), true)
