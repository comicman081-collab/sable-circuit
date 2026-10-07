extends SceneTree
## Actual projectile boundary observation, not a declared-count-only test.
## Active robot roster only: retired humanoid keys (rifle/shield/aberrant) are
## refused by EnemyActor._runtime_enemy_allowed() and must not be exercised.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
# Independent of Site7EnemyTactics.ROLES; a remapped role must fail here.
const ROLE_BY_ID := {"ENM_SITE7_DRONE_01":"drone","ENM_SITE7_BULWARK_01":"shield",
    "ENM_SITE7_RAM_01":"melee","ENM_SITE7_PRISM_01":"skimmer","ENM_SITE7_MORTAR_01":"mortar",
    "ENM_SITE7_NULL_PYLON_01":"mortar","BOSS_SITE7_ANCHOR_01":"boss","BOSS_SITE7_FORGE_01":"boss",
    "BOSS_SITE7_CARRIER_01":"boss","BOSS_SITE7_RELAY_01":"boss","BOSS_SITE7_REMNANT_01":"boss",
    "BOSS_SITE7_AERATOR_01":"boss","BOSS_SITE7_CRYO_01":"boss","BOSS_SITE7_GANTRY_01":"boss",
    "BOSS_SITE7_ARCHIVE_01":"boss","BOSS_SITE7_ORIGIN_01":"boss"}
const TestOutput := preload("res://tests/support/test_output.gd")
var failures: Array[String] = []
var checks := 0
var finished := false
var events: Array[Dictionary] = []
var attacks: Array[Dictionary] = []
var shells: Array[Dictionary] = []
var cases: Array[Dictionary] = []
func _init() -> void:
    call_deferred("run")
    # A script error aborts only run(); never leave the SceneTree idling forever.
    call_deferred("_ensure_finished")
func check(value: bool, label: String) -> void:
    checks += 1
    if not value:failures.append(label);push_error(label)
func abort(label: String) -> void:
    check(false,label)
    finished = true
    print("SITE7_EMISSION_OWNER_SMOKE: FAIL (",checks," checks) ",label)
    quit(1)
func _ensure_finished() -> void:
    if not finished:abort("Smoke run ended without a verdict")
## Projectiles per completed attack. Burst roles fire once, the melee ram only
## lunges, mortars launch a shell instead of a projectile, bosses fan or warn.
func expected_count(role: String, phase: int, serial: int, enemy_id: String) -> int:
    if role == "boss":
        match enemy_id:
            "BOSS_SITE7_RELAY_01": return 2 if serial % 2 == 0 and phase >= 2 else 0
            "BOSS_SITE7_FORGE_01": return 2 if serial % 2 == 0 else 0
            "BOSS_SITE7_REMNANT_01": return 0
            "BOSS_SITE7_CARRIER_01": return 2 if phase == 1 else 0
            "BOSS_SITE7_AERATOR_01": return 3 if phase == 2 and serial % 2 == 0 else 0
            "BOSS_SITE7_CRYO_01": return 2 if phase == 1 and serial % 2 == 0 else 0
            "BOSS_SITE7_ORIGIN_01": return 2 if phase <= 2 and serial % 2 == 0 else 0
            "BOSS_SITE7_GANTRY_01", "BOSS_SITE7_ARCHIVE_01": return 0
            _: return 0 if phase >= 2 and serial % 2 == 0 else (3 if phase == 1 else 5)
    if role in ["melee","mortar"]:return 0
    return 1
func run() -> void:
    var victim := OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    for hz in [30,60,120]:
        for id in ROLE_BY_ID:
            var role: String = ROLE_BY_ID[id]
            for phase in ([1,2,3] if role == "boss" else [1]):
                var context := "%s hz=%d phase=%d" % [id,hz,phase]
                var arena := Node2D.new();root.add_child(arena)
                var actor := ENEMY.instantiate() as EnemyActor
                # A refused profile queue_frees itself in _ready and never owns tactics.
                if not actor.configure(id,100):
                    actor.free();arena.free();victim.free()
                    abort("Active robot refused by runtime gate: "+context);return
                arena.add_child(actor);actor.set_physics_process(false)
                if actor.tactics == null or actor.is_queued_for_deletion():
                    arena.free();victim.free()
                    abort("Robot actor has no tactics controller: "+context);return
                check(str(actor.tactics.ROLES.get(id,"")) == role,"Tactics assigns the expected robot role: "+context)
                actor.health = [90.0,50.0,20.0][phase-1]
                actor.global_position=Vector2(100,100);victim.global_position=Vector2(240,100)
                events.clear();attacks.clear();shells.clear()
                actor.projectile_emitted.connect(func(row: Dictionary) -> void:events.append(row))
                actor.tactics.attack_started.connect(func(row: Dictionary) -> void:attacks.append(row))
                actor.tactics.mortar_launched.connect(func(row: Dictionary) -> void:shells.append(row))
                # Run exactly two complete attacks through the real controller.
                for tick in range(hz*20):
                    actor.tactics.step(victim,1.0/float(hz))
                    if actor.tactics.attack_serial==2 and actor.tactics.state=="RECOVER":break
                check(attacks.size()==2,"Two completed attacks: "+context)
                for attack in attacks:
                    var serial: int = attack.attack_serial
                    var attack_context := "%s serial=%d" % [context,serial]
                    var selected := events.filter(func(row: Dictionary) -> bool:return row.attack_serial==serial)
                    check(selected.size()==expected_count(role,phase,serial,id),"Actual emission count matches independent role expectation: "+attack_context)
                    for i in range(selected.size()):
                        var row: Dictionary=selected[i]
                        check(row.actor_id==actor.get_instance_id() and row.owner_id==actor.tactics.get_instance_id(),"One actual owning actor/controller: "+attack_context)
                        check(row.ordinal==i,"No duplicate/missing projectile ordinal: "+attack_context)
                        check(is_instance_valid(instance_from_id(row.projectile_id)),"Observed projectile was actually created: "+attack_context)
                    var launched := shells.filter(func(row: Dictionary) -> bool:return row.attack_serial==serial)
                    check(launched.size()==(1 if role == "mortar" else 0),"Actual mortar shell count matches role: "+attack_context)
                    for row in launched:
                        check(row.actor_id==actor.get_instance_id(),"Mortar shell launched by the owning actor: "+attack_context)
                        check(is_instance_valid(instance_from_id(row.shell_id)),"Observed mortar shell was actually created: "+attack_context)
                # The old presentation cannot emit an additional untelegraphed fan.
                var before := events.size()
                var old := actor.get_node_or_null("PremiumPresentation")
                check(old != null and old.has_method("_fire_phase_pattern"),"Actual legacy presentation path is exercised: "+context)
                if old and old.has_method("_fire_phase_pattern"):
                    old.set("_phase_index",3)
                    old.call("_fire_phase_pattern")
                check(events.size()==before,"Legacy presentation adds no projectile: "+context)
                cases.append({"hz":hz,"enemy_id":id,"role":role,"phase":phase,"attacks":attacks.duplicate(true),
                    "emissions":events.duplicate(true),"mortar_shells":shells.duplicate(true)})
                for row in events:
                    var bullet=instance_from_id(row.projectile_id)
                    if is_instance_valid(bullet):bullet.free()
                arena.free()
    victim.free()
    var evidence := {"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,
        "recorded_utc":Time.get_datetime_string_from_system(true),"cases":cases,"visual_approval":false,"code_sha256":{}}
    for path in ["res://scripts/actors/enemy_actor.gd","res://scripts/combat/site7_enemy_tactics.gd","res://scripts/combat/site7_mortar_shell.gd","res://scripts/animation/premium_enemy_presentation.gd","res://tests/smoke/site7_emission_owner_smoke.gd"]:
        evidence.code_sha256[path]=FileAccess.get_sha256(path)
    var directory := TestOutput.path("res://qa/stage1_implementation_20260913/emissions/"+str(Time.get_unix_time_from_system()).replace(".","_"))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
    var file := FileAccess.open(directory+"/actual_projectile_trace.json",FileAccess.WRITE)
    file.store_string(JSON.stringify(evidence,"  "));file.close()
    finished = true
    print("SITE7_EMISSION_OWNER_SMOKE: ",evidence.status," (",checks," checks) ",directory)
    quit(0 if failures.is_empty() else 1)
