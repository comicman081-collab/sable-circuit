extends SceneTree
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
var checks := 0
var failures: Array[String] = []
func _init() -> void:call_deferred("run")
func check(value: bool, label: String) -> void:
    checks += 1
    if not value:failures.append(label);push_error(label)
func run() -> void:
    var parent := Node2D.new();root.add_child(parent)
    parent.transform = Transform2D(0.7,Vector2(170,-230)).scaled_local(Vector2(1.8,0.7))
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_ABERRANT_01",100)
    parent.add_child(actor);actor.set_physics_process(false)
    actor.global_position=Vector2(150,200)
    var victim := OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    victim.global_position=actor.global_position+Vector2(140,0)
    actor.tactics.state_left=0
    actor.tactics.step(victim,1.0/60)
    check(actor.tactics.state=="WINDUP","Actual lunge windup")
    for x in range(-70,230,10):
        for y in [-59.0,-58.0,-40.0,0.0,40.0,58.0,59.0]:
            var point := actor.global_position+Vector2(x,y)
            var axis_x := clampf(float(x),0.0,151.2)
            var expected := Vector2(x-axis_x,y).length() <= 58.0
            check(actor.tactics.lunge_contains(point)==expected,"Warning capsule equals swept damage envelope")
    actor.tactics._warning("lane",Vector2(440,330),Vector2.RIGHT)
    var warning: Node2D = parent.get_child(parent.get_child_count()-1)
    check(warning.global_position.distance_to(Vector2(440,330))<.001,"World warning position under transformed parent")
    check(warning.contains(Vector2(650,340)),"Visible lane interior receives hit")
    check(not warning.contains(Vector2(650,347)),"Visible lane exterior evades")
    parent.rotation += 0.5
    parent.scale *= 1.4
    check(warning.global_position.distance_to(Vector2(440,330))<.001,"Frozen warning survives parent transform")
    check(warning.contains(Vector2(650,340)),"Frozen world geometry preserved")
    actor.enemy_id="QUADRUPED_01"
    actor.tactics.step(victim,1.0)
    check(actor.tactics.state=="UNSUPPORTED_ROLE" and actor.velocity==Vector2.ZERO,"Unknown role cannot become a rifle fallback")
    victim.free();parent.free()
    print("SITE7_ATTACK_GEOMETRY_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)
