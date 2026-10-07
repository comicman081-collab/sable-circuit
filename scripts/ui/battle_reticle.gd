extends Control

## Display-only confirmation. Hitboxes, aim and damage remain actor authority.
var _stage: StoryStage01
var _hit_left := 0.0
var _damage_left := 0.0
var _known_health: Dictionary = {}
var _cover_blocked := false
var _cover_clock := 0.0
const CoverNavigation := preload("res://scripts/combat/cover_navigation.gd")
const DemoInput := preload("res://scripts/ui/demo_input.gd")

func _aim_point(actor: OperatorActor) -> Vector2:
    return actor._get_projectile_spawn_origin() + actor.aim_world * 260.0 if DemoInput.touch_mode else actor.get_global_mouse_position()

func _ready() -> void:
    call_deferred("_bind")

func _bind() -> void:
    _stage = get_parent().get_parent() as StoryStage01
    if not _stage: return
    for actor in _stage.squad.operators:
        _known_health[actor.get_instance_id()] = actor.health
        actor.primary_hit.connect(_on_hit)
        actor.health_changed.connect(_on_health)

func _on_hit(actor: OperatorActor, amount: float) -> void:
    if actor.controlled and amount > 0.0: _hit_left = 0.13

func _on_health(actor: OperatorActor, health: float, _maximum: float) -> void:
    var id := actor.get_instance_id()
    if actor.controlled and health < float(_known_health.get(id, health)):
        _damage_left = 0.22
    _known_health[id] = health

func _process(delta: float) -> void:
    _hit_left = maxf(0.0, _hit_left - delta)
    _damage_left = maxf(0.0, _damage_left - delta)
    _cover_clock -= delta
    if _cover_clock <= 0.0:
        _cover_clock = 0.1
        _cover_blocked = false
        if is_instance_valid(_stage):
            var actor := _stage.squad.get_active_operator()
            if actor and not actor.is_downed():
                var origin := actor._get_projectile_spawn_origin()
                var point := _aim_point(actor)
                if point.distance_to(origin)>1.0:
                    _cover_blocked = CoverNavigation.reticle_blocked(get_tree(),origin,point)
    queue_redraw()

func _draw() -> void:
    if not _stage: return
    var actor := _stage.squad.get_active_operator()
    if not actor: return
    var color := Color("a6d8d1")
    var world := _aim_point(actor)
    var point := actor.get_canvas_transform() * world if DemoInput.touch_mode else get_viewport().get_mouse_position()
    for enemy in get_tree().get_nodes_in_group("prototype_targets"):
        if enemy is EnemyActor and enemy.get_combat_hit_rect().has_point(world):
            color = Color("f2767e")
            break
    if _cover_blocked: color = Color("efbc68")
    for axis in [Vector2.RIGHT,Vector2.DOWN,Vector2.LEFT,Vector2.UP]:
        draw_line(point + axis * 5.0, point + axis * 10.0, Color(0,0,0,0.8), 3.0, true)
        draw_line(point + axis * 5.0, point + axis * 10.0, color, 1.0, true)
    draw_circle(point,1.0,color)
    if _cover_blocked:
        draw_line(point+Vector2(-3,-3),point+Vector2(3,3),color,1.4,true)
        draw_string(ThemeDB.fallback_font,point+Vector2(15,4),"BLOCKED",HORIZONTAL_ALIGNMENT_LEFT,-1,12,color)
    if actor.is_reloading():
        draw_arc(point,14.0,-PI/2.0,-PI/2.0+TAU*actor.get_reload_progress(),28,Color("ebbb71"),1.5,true)
    if _hit_left > 0.0:
        for index in range(4):
            var ray := Vector2.RIGHT.rotated(PI/4.0+float(index)*PI/2.0)
            draw_line(point+ray*5.0, point+ray*11.0, Color(1,0.96,0.83,_hit_left/0.13),1.8,true)
    if _damage_left > 0.0:
        var viewport := get_viewport_rect().size
        var red := Color(0.9,0.17,0.24,0.30*_damage_left/0.22)
        draw_rect(Rect2(Vector2.ZERO,Vector2(viewport.x,3)),red)
        draw_rect(Rect2(Vector2(0,viewport.y-3),Vector2(viewport.x,3)),red)
