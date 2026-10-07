extends SceneTree
## Exercise the actual capture predicates with normal app actors and mutations.
const Capture := preload("res://tests/render/site7_anchor_candidate_capture.gd")
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const NoWarnings := preload("res://qa/stage1_implementation_20260913/r8_fixtures/no_warning_tactics.gd")
var failures: Array[String] = []
var checks := 0
var out := "res://qa/stage1_implementation_20260913/anchor_capture_edges_"+str(Time.get_unix_time_from_system()).replace(".","_")
var observed: Array[Dictionary] = []

func _init() -> void: call_deferred("run")
func check(ok: bool, note: String) -> void:
    checks+=1
    if not ok: failures.append(note);push_error(note)
func clear_warnings() -> void:
    for warning in get_nodes_in_group("site7_attack_warnings"): warning.free()
func attack(actor: EnemyActor, victim: OperatorActor, phase: int, hz: int) -> void:
    actor.health=actor.max_health*(0.5 if phase==2 else 0.25)
    actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0;actor.tactics.attack_serial=1
    actor.tactics.step(victim,1.0/hz)
    for tick in range(hz*2):
        actor.tactics.step(victim,1.0/hz)
        if actor.tactics.state=="RECOVER": break

func run() -> void:
    root.size=Vector2i(1920,1080);root.content_scale_size=Vector2i(1920,1080)
    DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var missing:="res://qa/stage1_implementation_20260913/r8_fixtures/does_not_exist.json"
    var malformed:="res://qa/stage1_implementation_20260913/r8_fixtures/malformed_spec.json"
    check(not FileAccess.file_exists(missing),"Missing spec fixture really absent")
    for path in [missing,malformed]:
        var app: Dictionary=Capture.candidate_input(true,path)
        check(app.ok and app.spec.is_empty() and app.path.is_empty(),"App never requires QA candidate: "+path)
        var candidate: Dictionary=Capture.candidate_input(false,path)
        check(not candidate.ok and not candidate.error.is_empty(),"Candidate rejects missing/malformed input: "+path)
    check(Capture.candidate_input(false,Capture.SPEC).ok,"Valid candidate positive control")
    var actor:=ENEMY.instantiate() as EnemyActor
    actor.configure("BOSS_SITE7_ANCHOR_01",620.0)
    actor.position=Vector2(960,900)
    root.add_child(actor);actor.set_physics_process(false)
    check(is_instance_valid(actor.machine_sprite),"Normal app registry source loaded")
    if not is_instance_valid(actor.machine_sprite): quit(1);return
    actor.machine_sprite.set_process(false)
    await process_frame;await RenderingServer.frame_post_draw
    check(Capture.visibility_issues(actor).is_empty(),"Visible on-screen artwork accepted")
    root.get_texture().get_image().save_png(out+"/visible.png")
    actor.machine_sprite.sprite.hide()
    await process_frame;await RenderingServer.frame_post_draw
    check("Boss artwork is hidden" in Capture.visibility_issues(actor),"Hidden sprite rejected with same on-screen iris")
    root.get_texture().get_image().save_png(out+"/hidden.png")
    actor.machine_sprite.sprite.show()
    actor.hide()
    check("Boss artwork is hidden" in Capture.visibility_issues(actor),"Hidden ancestor rejected")
    actor.show()
    actor.global_position.x=-10000
    check("Boss iris is outside the captured viewport" in Capture.visibility_issues(actor),"Offscreen iris rejected")
    actor.global_position.x=960
    check(Capture.visibility_issues(actor).is_empty(),"Visibility restored after negatives")
    var victim:=OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    victim.global_position=actor.global_position+Vector2(-310,-30)
    for hz in [30,60,120]:
        for phase in [2,3]:
            victim.reset_for_battle_preview()
            attack(actor,victim,phase,hz)
            for warning in get_nodes_in_group("site7_attack_warnings"): warning.set_physics_process(false)
            var before: Array[Dictionary]=Capture.own_warning_rows(actor)
            check(actor.tactics.state=="RECOVER","Real ground attack transition completed")
            check(Capture.warning_issues(before,phase,false).is_empty(),"Actual own warning shape/count before fire "+str([hz,phase]))
            check(not Capture.warning_issues(before,phase,true).is_empty(),"Pre-fire warnings cannot count as impact")
            var hp_before:=victim.health
            # Step the actual damage code, not forged elapsed/fired observations.
            for tick in range(int(1.36*hz)+1):
                for warning in get_nodes_in_group("site7_attack_warnings"): warning._physics_process(1.0/hz)
            var impact: Array[Dictionary]=Capture.own_warning_rows(actor)
            check(Capture.warning_issues(impact,phase,true).is_empty(),"Actual warnings fired within visible window "+str([hz,phase]))
            check(victim.health<hp_before,"Actual in-zone victim damaged")
            check(not Capture.warning_issues(impact,phase,false).is_empty(),"Impact cannot count as windup")
            observed.append({"hz":hz,"phase":phase,"before":before,"impact":impact,"health_before":hp_before,"health_after":victim.health})
            clear_warnings()
    actor.tactics.free();actor.tactics=NoWarnings.new();actor.add_child(actor.tactics)
    for phase in [2,3]:
        attack(actor,victim,phase,60)
        check(actor.tactics.state=="RECOVER" and actor.tactics.shots_fired==0,"Mutation still meets old RECOVER/zero-projectile condition")
        var absent: Array[Dictionary]=Capture.own_warning_rows(actor)
        check(absent.is_empty() and not Capture.warning_issues(absent,phase,false).is_empty(),"Skipped warning creation explicitly fails new capture predicate")
    actor.free();victim.free()
    await process_frame
    var hashes: Dictionary={}
    for path in ["tests/render/site7_anchor_candidate_capture.gd","tests/render/site7_anchor_capture_smoke.gd","scripts/combat/site7_enemy_tactics.gd","scripts/combat/site7_attack_warning.gd","qa/stage1_implementation_20260913/r8_fixtures/no_warning_tactics.gd","qa/stage1_implementation_20260913/r8_fixtures/malformed_spec.json","data/art_profiles/enemy_profiles.json"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    var f:=FileAccess.open(out+"/report.json",FileAccess.WRITE)
    f.store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,
        "native":[1920,1080],"observed":observed,"hashes":hashes,"visual_art_approval":false},"  "));f.close()
    print("SITE7_ANCHOR_CAPTURE_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks) ",out)
    quit(0 if failures.is_empty() else 1)
