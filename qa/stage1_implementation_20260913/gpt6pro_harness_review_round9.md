# SABLE CIRCUIT Round 9 — narrow re-review of actual R8 fixes

Please verify the attached current code for R8-01/02/03 and the additional real resume-routing regression below. Do not repeat a general architecture audit or infer art/MVP completion. Reply with defect IDs, exact evidence, small actionable fixes, and separate code review from supplied runtime evidence. The intentionally malformed JSON and no-warning tactics subclass are test-only negative fixtures, never runtime registry inputs.

R8-01: Capture now checks actual source-owned warning nodes: phase 2 one circle; phase 3 one circle plus four lanes. It checks visible/fired/elapsed/windup state and bounds polling to the actual fired window; captures include real HP before/after. The new real Godot test forces a no-warning attack that still enters RECOVER with zero projectiles; the new predicate rejects it. Tests run warning clocks at 30/60/120 Hz.

R8-02: Actual machine Sprite2D.is_visible_in_tree plus global_transform_with_canvas emitter-in-viewport checks. Test hides the sprite, hides an ancestor, and moves it offscreen; restores a real visible baseline. No mock predicate bypass.

R8-03: Normal --app-registry capture does not read candidate JSON at all, even if an explicit --candidate-spec path is missing or malformed. Candidate mode requires existing parseable Dictionary JSON. Captured spec hashes are taken from the actually selected actor profile. Full normal-app capture succeeded with an intentionally missing candidate argument, candidate_input_read=false.

Actual validation: Godot capture-edge smoke PASS 52 checks; native normal-app capture PASS_CAPTURE_ONLY, 22 WebP images at 1920x1080; native validator 24 containers passed (including hidden/visible negative-test PNG evidence). Main agent viewed phase 2 warning, phase 2 impact, phase 3 impact. Phase2 HP96->76, phase3 HP96->56, with actual fired warnings. A first fixture run failed two onscreen positives because a fixture position was assigned after _ready; this fixture was corrected to spawn at its real home BEFORE insertion, and the failed evidence is retained. No combat gameplay speeds, damage, player art, or registry pointers changed in this fix batch.

Additional actual harness defect: after a non-E whole-cycle source rejection, old handoff requested a missing unrelated direction, ignoring SE/walk/3..5 that were still rejected by cycle evidence although isolated source reviews were approved. cycle_followup now selects those exact failed slots first and queues completed but unreviewed cycles before new directions. Non-art rejection requests review/repair of that mechanism, not new artwork. Explicit source rejection and incomplete/unreviewed E pilot retain priority. The full initial run caught a pilot priority regression; it was fixed without weakening the existing test. Current complete re-run is 101 tests OK. This is technical fixture evidence, not a Luna character-generation run.

SE 3/4/5 whole-cycle weapon/torso projection repair is ongoing, not approved. The prior two-leg isolated source fix is not being called a whole-cycle PASS. Other enemy assets remain incomplete. No delivery, deployment, blanket quality approval, or claimed Luna end-to-end success is requested.

## FILE: tests/render/site7_anchor_candidate_capture.gd
SHA256: 76cea8625513abd8ecfa551831854256888042fbe6e36af76aa5109688a25095
```text
extends SceneTree
## Controlled boss phase/telegraph cases in the real scene, not a playthrough.
## Health and attack serial select the tested phase; no game values are changed.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
const SPEC := "res://motion_lab_v1/qa/stage1_enemies_20260913/anchor/candidate_spec_v1.json"
var out := "res://qa/stage1_implementation_20260913/anchor_native_"+str(Time.get_unix_time_from_system()).replace(".","_")
var failures: Array[String] = []
var rows: Array[Dictionary] = []
var emissions: Array[Dictionary] = []
var use_app := "--app-registry" in OS.get_cmdline_user_args()
var used_specs: Dictionary = {}
var warning_evidence: Array[Dictionary] = []

static func candidate_input(app_mode: bool, path: String) -> Dictionary:
    # App capture must not even open an unrelated candidate-only input.
    if app_mode: return {"ok":true,"spec":{},"path":""}
    if not FileAccess.file_exists(path): return {"ok":false,"error":"Candidate spec missing: "+path}
    var parser := JSON.new()
    if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:
        return {"ok":false,"error":"Candidate spec is not a JSON object: "+path}
    return {"ok":true,"spec":parser.data,"path":path}

static func visibility_issues(actor: EnemyActor) -> Array[String]:
    var issues: Array[String] = []
    if not is_instance_valid(actor) or not is_instance_valid(actor.machine_sprite) or not is_instance_valid(actor.machine_sprite.sprite):
        issues.append("Boss artwork unavailable")
        return issues
    var picture: Sprite2D=actor.machine_sprite.sprite
    if not picture.is_visible_in_tree(): issues.append("Boss artwork is hidden")
    var iris_screen: Vector2=picture.get_global_transform_with_canvas()*actor.machine_sprite.emitter_px
    if not picture.get_viewport_rect().has_point(iris_screen): issues.append("Boss iris is outside the captured viewport")
    return issues

static func own_warning_rows(actor: EnemyActor) -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    for warning in actor.get_tree().get_nodes_in_group("site7_attack_warnings"):
        if warning.source!=actor or warning.is_queued_for_deletion(): continue
        result.append({"id":warning.get_instance_id(),"kind":warning.kind,"elapsed":warning.elapsed,
            "windup":warning.windup,"fired":warning.fired,"position":warning.global_position,
            "ray":warning.ray,"visible":warning.is_visible_in_tree()})
    return result

static func warning_issues(observed: Array[Dictionary], phase: int, expect_fired: bool) -> Array[String]:
    var issues: Array[String] = []
    var counts := {"circle":0,"lane":0}
    for row in observed:
        if not counts.has(row.kind): issues.append("Unexpected warning kind");continue
        counts[row.kind]+=1
        if not row.visible: issues.append("Warning hidden")
        if row.fired!=expect_fired: issues.append("Warning firing state mismatch")
        if not is_finite(row.elapsed) or not is_finite(row.windup) or row.windup<=0.0:
            issues.append("Warning clock invalid")
        elif (row.elapsed>=row.windup)!=expect_fired or row.elapsed>row.windup+0.26:
            issues.append("Warning clock does not show requested visible phase")
    if counts.circle!=1 or counts.lane!=(4 if phase==3 else 0): issues.append("Missing/extra boss warning geometry")
    return issues

func _init() -> void: call_deferred("run")

func settle(count: int = 1) -> void:
    for i in range(count):
        await physics_frame
        await process_frame

func capture(actor: EnemyActor, label: String) -> void:
    await RenderingServer.frame_post_draw
    var im := root.get_texture().get_image()
    var path := out+"/"+label+".webp"
    var iris_screen: Vector2=actor.machine_sprite.sprite.get_global_transform_with_canvas()*actor.machine_sprite.emitter_px
    for issue in visibility_issues(actor): failures.append(issue+": "+label)
    if im.get_size()!=Vector2i(1920,1080) or im.save_webp(path,true,0.94)!=OK:
        failures.append("Capture failed: "+label)
    rows.append({"path":path,"sha256":FileAccess.get_sha256(path),"label":label,
        "native":[1920,1080],"iris_canvas":iris_screen,"wall_ms":Time.get_ticks_msec(),"physics_tick":Engine.get_physics_frames(),
        "health_fixture":actor.health,"tactics":actor.tactics.contract(),
        "machine":actor.machine_sprite.debug_contract(),"emissions":emissions.duplicate(true),
        "warnings":own_warning_rows(actor)})

func run() -> void:
    ProjectSettings.set_setting("sable_visuals/site7_authored_machines",use_app)
    root.size=Vector2i(1920,1080)
    root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    DisplayServer.window_set_size(Vector2i(1920,1080))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    var candidate_path: String=SPEC
    var arguments:=OS.get_cmdline_user_args()
    var path_option:=arguments.find("--candidate-spec")
    if path_option>=0 and path_option+1<arguments.size(): candidate_path=arguments[path_option+1]
    var intake:=candidate_input(use_app,candidate_path)
    if not intake.ok:
        push_error(intake.error);quit(1);return
    var spec: Dictionary=intake.spec
    for phase in [1,2,3]:
        for serial in [0,1]:
            var label: String="phase%d_attack%d" % [phase,serial+1]
            var stage:=STAGE.instantiate() as StoryStage01
            stage.battle_preview=true;root.add_child(stage)
            await settle(4)
            stage.start_battle_preview(4)
            await settle(2)
            stage.set_process(false);stage.set_physics_process(false)
            stage.squad.set_process(false);stage.squad.set_physics_process(false)
            var actor: EnemyActor
            for enemy in get_nodes_in_group("m3_enemies"):
                enemy.set_physics_process(false)
                if enemy.enemy_id=="BOSS_SITE7_ANCHOR_01":actor=enemy
                else:enemy.hide()
            if actor==null or (not is_instance_valid(actor.machine_sprite) if use_app else not actor.preview_machine_source(spec)):
                failures.append("Boss source unavailable");stage.queue_free();await settle(2);continue
            var actual_spec: String=actor.art_profile.machine_asset.spec if use_app else candidate_path
            used_specs[actual_spec]=FileAccess.get_sha256(actual_spec)
            # Keep the encounter's actual anchored position. The existing
            # BossAnchorLockPresentation restores it each frame; arbitrary
            # relocation makes a numeric test pass while the art is offscreen.
            actor.health=actor.max_health*([0.95,0.5,0.25][phase-1])
            actor.velocity=Vector2.ZERO
            var victim: OperatorActor
            for operator in get_nodes_in_group("operators"):
                operator.debug_drive(Vector2.ZERO,Vector2.RIGHT)
                operator.set_physics_process(false)
                if operator.operator_id=="CHR_PROTO_01":victim=operator
                else:operator.hide()
            victim.global_position=actor.global_position+Vector2(-310,-30)
            stage.camera.global_position=actor.global_position+Vector2(-110,-150)
            stage.camera.position_smoothing_enabled=false
            emissions.clear()
            actor.projectile_emitted.connect(func(row: Dictionary) -> void:emissions.append(row))
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.attack_serial=serial
            actor.tactics.step(victim,1.0/60.0)
            await settle(2)
            await capture(actor,label+"_windup_start")
            var fixed_position:=actor.global_position
            var fixed_muzzle: Vector2=actor.machine_sprite.muzzle_world()
            for tick in range(65):
                actor.tactics.step(victim,1.0/60.0)
                await settle()
                if tick==28:await capture(actor,label+"_windup_mid")
                if actor.tactics.state=="RECOVER":break
            await capture(actor,label+"_attack")
            if actor.tactics.state!="RECOVER":failures.append(label+" never attacked")
            if actor.global_position!=fixed_position or actor.machine_sprite.muzzle_world().distance_to(fixed_muzzle)>0.001:
                failures.append(label+" anchored geometry drifted")
            var expected_shots:=0 if phase>=2 and serial==1 else (3 if phase==1 else 5)
            if emissions.size()!=expected_shots:failures.append(label+" projectile count mismatch")
            for shot in emissions:
                if Vector2(shot.origin[0],shot.origin[1]).distance_to(fixed_muzzle)>0.001:
                    failures.append(label+" projectile did not originate at iris")
            if phase>=2 and serial==1:
                var before:=own_warning_rows(actor)
                for issue in warning_issues(before,phase,false): failures.append(label+": "+issue)
                var victim_health_before:=victim.health
                await capture(actor,label+"_ground_warning")
                # Observe the actual firing window. A fixed 90-tick delay can
                # photograph an already deleted impact and falsely label it.
                var impact: Array[Dictionary] = []
                for tick in range(180):
                    await settle()
                    impact=own_warning_rows(actor)
                    if warning_issues(impact,phase,true).is_empty(): break
                    if impact.is_empty(): break
                for issue in warning_issues(impact,phase,true): failures.append(label+": "+issue)
                if victim.health>=victim_health_before: failures.append(label+": ground attack did not damage the stationary in-zone victim")
                await capture(actor,label+"_ground_impact")
                warning_evidence.append({"case":label,"before":before,"impact":impact,
                    "health_before":victim_health_before,"health_after":victim.health})
            stage.queue_free()
            for node in root.get_children():
                if node is PrototypeProjectile:node.queue_free()
            await settle(3)
    var hashes: Dictionary={}
    hashes.merge(used_specs)
    for path in ["res://scripts/animation/site7_machine_sprite.gd","res://scripts/actors/enemy_actor.gd","res://scripts/combat/site7_enemy_tactics.gd","res://scripts/combat/site7_attack_warning.gd","res://scripts/ui/enemy_overhead_ui.gd","res://tests/render/site7_anchor_candidate_capture.gd","res://data/art_profiles/enemy_profiles.json"]:
        hashes[path]=FileAccess.get_sha256(path)
    var file:=FileAccess.open(out+"/capture_report.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"status":"CAPTURED_CONTROLLED_PHASES_NOT_VISUAL_APPROVAL","app_registry":use_app,
        "failures":failures,"rows":rows,"hashes":hashes,"warning_evidence":warning_evidence,
        "candidate_path_argument":candidate_path,"candidate_input_read":not use_app,
        "phase_health_and_serial_fixtures":true},"  "));file.close()
    print("SITE7_ANCHOR_CAPTURE: ","PASS_CAPTURE_ONLY" if failures.is_empty() else "FAIL"," ",out)
    quit(0 if failures.is_empty() else 1)

```

## FILE: tests/render/site7_anchor_capture_smoke.gd
SHA256: 7ba9b8a3c42fc7b83ac199e73075425ddb8e82b77d5a77ec53bd5d69f7ab8b5d
```text
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

```

## FILE: qa/stage1_implementation_20260913/r8_fixtures/no_warning_tactics.gd
SHA256: 68a6711fd27459998a19e72b80552ffe1d5485136b83fbb8927067f7e75ac96b
```text
extends "res://scripts/combat/site7_enemy_tactics.gd"
## Test-only R8-01 mutation. Never used by an app actor or registry.
func _warning(_kind: String, _location: Vector2, _direction: Vector2) -> void:
    pass

```

## FILE: qa/stage1_implementation_20260913/r8_fixtures/malformed_spec.json
SHA256: b8694d125b7538e56df8a71d0c37e9288493a73c6ae6fa8cb0d80ed6b5216ff2
```text
{ malformed test-only candidate JSON

```

## FILE: scripts/combat/site7_enemy_tactics.gd
SHA256: efacd6facda231852c947cb26572cc873ed022d62bb5ddf1ef55b2c8b260bd02
```text
extends Node2D
## Enemy attack controller. Authored art reads these states; it never supplies AI.
const Warning := preload("res://scripts/combat/site7_attack_warning.gd")
const ROLES := {"ENM_SITE7_RIFLE_01":"rifle", "ENM_SITE7_SHIELD_01":"shield",
    "ENM_SITE7_DRONE_01":"drone", "ENM_SITE7_ABERRANT_01":"melee", "BOSS_SITE7_ANCHOR_01":"boss"}
const LUNGE_SPEED := 360.0
const LUNGE_DURATION := 0.42
const LUNGE_RADIUS := 58.0
signal attack_started(event: Dictionary)

var actor: EnemyActor
var state := "REPOSITION"
var state_left := 0.7
var state_duration := 0.7
var locked_aim := Vector2.LEFT
var locked_ground := Vector2.LEFT
var burst_left := 0
var burst_clock := 0.0
var phase := 1
var attack_serial := 0
var shots_fired := 0
var lunges := 0
var _struck: Array[int] = []
var _age := 0.0
var _lunge_origin := Vector2.ZERO
var _lunge_reach := 0.0
var _shot_ordinal := 0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    top_level = true
    z_index = 1

func _enter(next_state: String, duration: float) -> void:
    state = next_state
    state_left = duration
    state_duration = maxf(duration, 0.001)
    # Stagger skips step(). Invalidate THIS CanvasItem's cached warning now.
    queue_redraw()

func interrupt() -> void:
    burst_left = 0
    _struck.clear()
    _enter("RECOVER", 0.55)

func step(target: OperatorActor, delta: float) -> void:
    global_transform = Transform2D(0.0, actor.global_position)
    var role := str(ROLES.get(actor.enemy_id,""))
    if role.is_empty():
        actor.velocity = Vector2.ZERO
        _enter("UNSUPPORTED_ROLE",1.0)
        return
    _age += delta
    state_left -= delta
    var offset := target.global_position - actor.global_position
    var dist := offset.length()
    var toward := offset.normalized() if dist > 0.01 else Vector2.LEFT
    # Do not even resolve a new visual yaw while an announced attack is locked.
    # Its body, muzzle and shot must retain the same warning direction.
    var aim := locked_aim
    if state not in ["WINDUP", "BURST", "LUNGE"]:
        aim = actor.aim_from_emitter(target.get_combat_aim_point())
        if not _valid_aim(aim): aim = actor._aim_dir
    var boss := role == "boss"
    var rifle := role == "rifle"
    var shield := role == "shield"
    var drone := role == "drone"
    var melee := role == "melee"
    phase = 1 if actor.health > actor.max_health * 0.66 else (2 if actor.health > actor.max_health * 0.33 else 3)
    actor.velocity = Vector2.ZERO
    actor._aim_dir = locked_aim if state in ["WINDUP", "BURST", "LUNGE"] else aim
    if state == "REPOSITION":
        if drone:
            var tangent := toward.orthogonal() * actor._orbit_sign
            actor.velocity = (tangent * 0.72 + toward * clampf((dist - 280.0) / 160.0, -0.7, 0.7)).limit_length(1.0) * 118.0
        elif melee:
            actor.velocity = toward * 112.0 if dist > 85.0 else Vector2.ZERO
        elif shield:
            actor.velocity = toward * 62.0 if dist > 190.0 else Vector2.ZERO
        elif rifle:
            var radial := 1.0 if dist > 360.0 else (-0.7 if dist < 220.0 else 0.0)
            actor.velocity = (toward * radial + toward.orthogonal() * actor._orbit_sign * 0.38).limit_length(1.0) * 86.0
        if state_left <= 0.0 and (not melee or dist < 250.0):
            var reposition_velocity := actor.velocity
            actor.velocity = Vector2.ZERO
            # Stop/bank first, then freeze the actual emitter ray. Never home
            # a telegraphed shot onto the player's later position.
            var candidate_aim := actor.aim_from_emitter(target.get_combat_aim_point())
            if not _valid_aim(candidate_aim):
                # The target may be inside every authored emitter offset.
                # Keep moving normally; do not advertise or emit a reverse ray.
                actor.velocity = reposition_velocity
                queue_redraw()
                return
            locked_aim = candidate_aim
            locked_ground = toward
            _lunge_origin = actor.global_position
            _lunge_reach = LUNGE_SPEED * LUNGE_DURATION * actor.run_speed_multiplier
            actor._aim_dir = locked_aim
            actor.velocity = Vector2.ZERO
            _enter("WINDUP", 0.95 if boss else (0.7 if shield else (0.6 if melee else 0.48)))
    elif state == "WINDUP":
        if state_left <= 0.0:
            attack_serial += 1
            _shot_ordinal = 0
            attack_started.emit({"actor_id":actor.get_instance_id(),"enemy_id":actor.enemy_id,
                "attack_serial":attack_serial,"phase":phase,"owner_id":get_instance_id()})
            if melee:
                lunges += 1
                _struck.clear()
                _enter("LUNGE", LUNGE_DURATION)
            elif boss:
                _boss_attack(target)
                _enter("RECOVER", (1.8 - float(phase) * 0.20) * actor.run_attack_interval_multiplier)
            else:
                burst_left = 3 if rifle else 1
                burst_clock = 0.0
                _enter("BURST", 0.5)
    elif state == "BURST":
        burst_clock -= delta
        if burst_left > 0 and burst_clock <= 0.0:
            _fire(locked_aim)
            burst_left -= 1
            burst_clock += 0.14
        if burst_left <= 0:
            _enter("RECOVER", (1.4 if shield else 0.85) * actor.run_attack_interval_multiplier)
    elif state == "LUNGE":
        actor.velocity = locked_ground * LUNGE_SPEED
        for victim in get_tree().get_nodes_in_group("operators"):
            if not victim is OperatorActor or victim.is_downed() or _struck.has(victim.get_instance_id()):
                continue
            if lunge_contains(victim.global_position) and actor.global_position.distance_to(victim.global_position) < LUNGE_RADIUS:
                victim.apply_damage(18.0 * actor.run_damage_multiplier)
                _struck.append(victim.get_instance_id())
        if state_left <= 0.0:
            actor.velocity = Vector2.ZERO
            _enter("RECOVER", 1.1 * actor.run_attack_interval_multiplier)
    elif state == "RECOVER":
        if drone:
            actor.velocity = toward.orthogonal() * actor._orbit_sign * 62.0
        if state_left <= 0.0:
            _enter("REPOSITION", 0.9 if not boss else 0.45)
    queue_redraw()

func _valid_aim(direction: Vector2) -> bool:
    return direction.is_finite() and direction.length_squared() > 0.000001

func _fire(direction: Vector2) -> void:
    if not _valid_aim(direction): return
    shots_fired += 1
    CombatFeedback.play_fire(get_tree(), actor.art_profile)
    actor._spawn_projectile(direction, self, attack_serial, _shot_ordinal)
    _shot_ordinal += 1

func _boss_attack(target: OperatorActor) -> void:
    # Slow readable fan in phase one; frozen impact zones in two; cross lanes
    # in three. Large gaps are intentional. These are damaging, not fake decals.
    if phase >= 2 and attack_serial % 2 == 0:
        _warning("circle", target.global_position, Vector2.RIGHT)
        if phase == 3:
            var origin := actor.global_position
            for i in range(4):
                var ray := locked_ground.rotated(float(i) * PI * 0.5)
                _warning("lane", origin + ray * 100.0, ray)
    else:
        var count := 3 if phase == 1 else 5
        for i in range(count):
            _fire(locked_aim.rotated((float(i) - float(count - 1) * 0.5) * 0.22))

func _warning(kind: String, location: Vector2, direction: Vector2) -> void:
    var warning := Warning.new()
    warning.source = actor
    warning.kind = kind
    warning.top_level = true
    warning.ray = direction
    warning.windup = 1.15 if kind == "circle" else 1.35
    warning.damage = 20.0
    actor.get_parent().add_child(warning)
    warning.global_transform = Transform2D(0.0,location)

func lunge_contains(point: Vector2) -> bool:
    var offset := point - _lunge_origin
    var nearest := _lunge_origin + locked_ground * clampf(offset.dot(locked_ground),0.0,_lunge_reach)
    return point.distance_to(nearest) <= LUNGE_RADIUS

func _draw() -> void:
    if not is_instance_valid(actor) or actor.health <= 0.0 or state != "WINDUP":
        return
    var progress := 1.0 - clampf(state_left / state_duration, 0.0, 1.0)
    var color := Color("ef907e", 0.30 + progress * 0.42)
    if "ABERRANT" in actor.enemy_id:
        var base := to_local(_lunge_origin)
        var side := locked_ground.orthogonal() * LUNGE_RADIUS
        var tip := base + locked_ground * _lunge_reach
        draw_colored_polygon(PackedVector2Array([base-side,base+side,tip+side,tip-side]),Color(color,0.12))
        draw_circle(base,LUNGE_RADIUS,Color(color,0.12))
        draw_circle(tip,LUNGE_RADIUS,Color(color,0.12))
        draw_line(base-side,tip-side,color,1.8)
        draw_line(base+side,tip+side,color,1.8)
        var angle := locked_ground.angle()
        draw_arc(base,LUNGE_RADIUS,angle+PI/2,angle+3*PI/2,32,color,1.8)
        draw_arc(tip,LUNGE_RADIUS,angle-PI/2,angle+PI/2,32,color,1.8)
    else:
        var origin := to_local(actor.projectile_origin(locked_aim))
        draw_line(origin, origin + locked_aim * 300.0, color, 1.1)
    draw_arc(Vector2(0,6), 23.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 32, color, 2.0)

func contract() -> Dictionary:
    return {"state": state, "state_left": state_left, "locked_aim": locked_aim,
        "phase": phase, "attacks": attack_serial, "shots": shots_fired, "lunges": lunges,
        "contract_is_intent_not_validation":true,
        "role":ROLES.get(actor.enemy_id,"unsupported"),"lunge_radius":LUNGE_RADIUS,"lunge_reach":_lunge_reach}

```

## FILE: scripts/combat/site7_attack_warning.gd
SHA256: a2b237db6016c2dd85ed0c346784723ae53a0bbd1cd81a463291df267a3b4f39
```text
extends Node2D
## A floor warning and its damage share the same frozen geometry and clock.
## No invisible homing: moving out of the marked region always evades the hit.

var source: EnemyActor
var kind := "circle"
var radius := 58.0
var ray := Vector2.RIGHT
var reach := 430.0
var half_width := 16.0
var windup := 1.05
var damage := 16.0
var elapsed := 0.0
var fired := false

func _ready() -> void:
    z_index = -2
    add_to_group("site7_attack_warnings")

func _physics_process(delta: float) -> void:
    if not is_instance_valid(source) or source.health <= 0.0:
        queue_free()
        return
    elapsed += delta
    if elapsed >= windup and not fired:
        fired = true
        for actor in get_tree().get_nodes_in_group("operators"):
            if actor is OperatorActor and not actor.is_downed() and contains(actor.global_position):
                actor.apply_damage(damage * source.run_damage_multiplier)
    if elapsed > windup + 0.26:
        queue_free()
    queue_redraw()

func contains(point: Vector2) -> bool:
    var offset := to_local(point)
    if kind == "circle":
        return offset.length() <= radius
    var forward := offset.dot(ray)
    return forward >= 0.0 and forward <= reach and absf(offset.dot(ray.orthogonal())) <= half_width

func _draw() -> void:
    var progress := clampf(elapsed / windup, 0.0, 1.0)
    var color := Color("f48caa")
    if fired:
        color = Color("eee2ff")
    var fill := Color(color, 0.12 if not fired else 0.36)
    if kind == "circle":
        draw_circle(Vector2.ZERO, radius, fill)
        draw_arc(Vector2.ZERO, radius, 0.0, TAU, 64, Color(color, 0.75), 1.8)
        draw_arc(Vector2.ZERO, radius - 5.0, -PI * 0.5, -PI * 0.5 + TAU * progress, 64, color, 2.4)
        draw_line(Vector2(-7,0), Vector2(7,0), color, 1.3)
        draw_line(Vector2(0,-7), Vector2(0,7), color, 1.3)
    else:
        var side := ray.orthogonal() * half_width
        draw_colored_polygon(PackedVector2Array([-side, side, ray * reach + side, ray * reach - side]), fill)
        draw_line(-side, ray * reach - side, Color(color, 0.8), 1.5)
        draw_line(side, ray * reach + side, Color(color, 0.8), 1.5)
        draw_line(Vector2.ZERO, ray * reach * progress, color, 2.2 if not fired else 6.0)

```

## FILE: scripts/animation/site7_machine_sprite.gd
SHA256: 986d9b4f34c33ee9c07d4737c286bad32c0acd84b78361e4b7f7a7fbcdc338c8
```text
extends Node2D
## Source-preserving preview/runtime for non-walking machines only.
## A drone banks as one rigid object; an anchor stays anchored. Neither is a
## humanoid gait and neither may use a six-frame foot-cycle approval as proof.

var actor: EnemyActor
var sprite: Sprite2D
var kind := ""
var emitter_px := Vector2.ZERO
var image_size := Vector2.ZERO
var age := 0.0
var flash := 0.0
var render_scale := 1.0
var body_origin := Vector2.ZERO
var configured := false
const DIRECTIONS := ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
var views: Dictionary = {}
var facing := ""
var emitter_visible := true
const MAX_TARGET_ERROR := PI / 8.0 + 0.02
static var _pixel_hash_cache: Dictionary = {}

func _visible_pixel_hash(image: Image, file_hash: String) -> String:
    if _pixel_hash_cache.has(file_hash): return _pixel_hash_cache[file_hash]
    var canonical := image.duplicate() as Image
    canonical.convert(Image.FORMAT_RGBA8)
    var bytes := canonical.get_data()
    # Invisible RGB is not another direction. Do not change the source or the
    # displayed texture; canonicalize only the comparison buffer.
    for alpha in range(3,bytes.size(),4):
        if bytes[alpha]==0:
            bytes[alpha-3]=0; bytes[alpha-2]=0; bytes[alpha-1]=0
    var hash := HashingContext.new()
    hash.start(HashingContext.HASH_SHA256)
    hash.update((str(image.get_width())+"x"+str(image.get_height())+":RGBA8:").to_utf8_buffer())
    hash.update(bytes)
    var result := hash.finish().hex_encode()
    _pixel_hash_cache[file_hash]=result
    return result

func _read_view(spec: Dictionary) -> Dictionary:
    var path := str(spec.get("texture", ""))
    if FileAccess.get_sha256(path) != str(spec.get("texture_sha256", "")): return {}
    var image := Image.load_from_file(path)
    if image == null or image.is_empty(): return {}
    var root_xy: Array = spec.get("root_px", [])
    var emitter_xy: Array = spec.get("emitter_px", [])
    if root_xy.size() != 2 or emitter_xy.size() != 2: return {}
    var size := Vector2(image.get_size())
    var origin := Vector2(float(root_xy[0]),float(root_xy[1]))
    var emitter := Vector2(float(emitter_xy[0]),float(emitter_xy[1]))
    var ratio := float(spec.get("display_height",110.0)) / size.y
    if not origin.is_finite() or not emitter.is_finite() or not is_finite(ratio): return {}
    if ratio <= 0.0 or ratio > 1.0 or not Rect2(Vector2.ZERO,size).has_point(emitter): return {}
    return {"texture":ImageTexture.create_from_image(image),"size":size,"root":origin,
        "emitter":emitter,"scale":ratio,"emitter_visible":bool(spec.get("emitter_visible",true)),
        "texture_sha256":str(spec.texture_sha256),
        "pixel_sha256":_visible_pixel_hash(image,str(spec.texture_sha256))}

func configure(owner_actor: EnemyActor, spec: Dictionary) -> bool:
    if configured or not is_instance_valid(owner_actor): return false
    var staged_kind := str(spec.get("kind", ""))
    var expected_kind := {"ENM_SITE7_DRONE_01":"hover_machine", "BOSS_SITE7_ANCHOR_01":"anchored_machine"}
    if expected_kind.get(owner_actor.enemy_id,"") != staged_kind or staged_kind.is_empty(): return false
    # Load the complete set before publishing any node/state. A single front
    # illustration is NOT an omnidirectional drone, even with an omni emitter.
    var staged: Dictionary = {}
    if staged_kind == "hover_machine":
        if str(spec.get("facing_mode","")) != "authored_yaw8": return false
        var authored: Dictionary = spec.get("views",{})
        if authored.size() != 8: return false
        var hashes: Array[String] = []
        var pixel_hashes: Array[String] = []
        for direction in DIRECTIONS:
            if not authored.has(direction): return false
            var view := _read_view(authored[direction])
            if view.is_empty() or hashes.has(view.texture_sha256) or pixel_hashes.has(view.pixel_sha256): return false
            hashes.append(view.texture_sha256)
            pixel_hashes.append(view.pixel_sha256)
            staged[direction] = view
    else:
        var fixed := _read_view(spec)
        if fixed.is_empty(): return false
        staged["ANCHORED"] = fixed
    actor = owner_actor
    kind = staged_kind
    sprite = Sprite2D.new()
    sprite.name = "AuthoredMachinePixels"
    sprite.set_meta("preserve_authored_material", true)
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.centered = false
    add_child(sprite)
    views = staged
    _apply_view("E" if kind == "hover_machine" else "ANCHORED")
    configured = true
    face_direction(actor._aim_dir)
    return true

func _apply_view(direction: String) -> void:
    if facing == direction: return
    var view: Dictionary = views[direction]
    facing = direction
    image_size = view.size
    emitter_px = view.emitter
    emitter_visible = view.emitter_visible
    render_scale = float(view.scale)
    sprite.texture = view.texture
    sprite.scale = Vector2.ONE * render_scale
    body_origin = -view.root * render_scale
    sprite.position = body_origin

func face_direction(direction: Vector2) -> void:
    if not configured or kind != "hover_machine" or direction.length_squared() < 0.000001: return
    var local_dir := actor.global_transform.affine_inverse().basis_xform(direction)
    var sector := int(floor(fposmod(local_dir.angle()+PI/8.0,TAU)/(PI/4.0)))%8
    _apply_view(DIRECTIONS[sector])

func visible_heading_world() -> Vector2:
    if kind != "hover_machine": return Vector2.ZERO
    var index := DIRECTIONS.find(facing)
    return global_transform.basis_xform(Vector2.from_angle(index*PI/4.0)).normalized()

func resolve_target(target: Vector2) -> Vector2:
    if not configured or not target.is_finite(): return Vector2.INF
    if kind != "hover_machine": return (target-muzzle_world()).normalized()
    # Each authored yaw has a different physical emitter offset. Evaluate its
    # own ray, then keep the pose whose front actually agrees with that ray.
    # No interpolation, horizontal mirroring, or whole-bitmap screen rotation.
    var best := facing
    var error := INF
    sync_pose()
    for i in range(DIRECTIONS.size()):
        var direction: String = DIRECTIONS[i]
        var view: Dictionary = views[direction]
        var local_emitter: Vector2 = (view.emitter-view.root)*float(view.scale)
        var ray := (target-to_global(local_emitter)).normalized()
        var heading := global_transform.basis_xform(Vector2.from_angle(i*PI/4.0)).normalized()
        var candidate_error := absf(heading.angle_to(ray))
        if candidate_error < error:
            best = direction
            error = candidate_error
    # "Least wrong" is not necessarily forward. Inside the illustrated gun's
    # reach there may be no legal view. Retain the pose and explicitly reject
    # this target; the tactics controller must reposition without winding up.
    if error > MAX_TARGET_ERROR: return Vector2.INF
    _apply_view(best)
    return (target-muzzle_world()).normalized()

func _process(delta: float) -> void:
    if not configured: return
    age += delta
    flash = move_toward(flash, 0.0, delta * 7.0)
    sync_pose()
    queue_redraw()

func sync_pose() -> void:
    if not configured: return
    # Use bounded rigid-body motion only. No image stretching or cut-up limbs.
    if kind == "hover_machine":
        rotation = clampf(actor.velocity.x / 118.0, -1.0, 1.0) * 0.045
        position.y = sin(age * 2.8) * 3.0
        if actor.health <= 0.0:
            rotation += (0.55 - actor._death_left) * 1.2
            position.y += (0.55 - actor._death_left) * 65.0
    else:
        rotation = 0.0
        position = Vector2.ZERO
    sprite.modulate = Color.WHITE.lerp(Color(1.3,1.15,1.25),actor._hit_flash * 0.4)

func muzzle_world() -> Vector2:
    sync_pose()
    return sprite.to_global(emitter_px)

func fired() -> void:
    flash = 1.0
    queue_redraw()

func hit_rect_world() -> Rect2:
    var shape := Rect2(image_size * Vector2(0.12,0.15), image_size * Vector2(0.76,0.70))
    var bounds := Rect2(sprite.to_global(shape.position),Vector2.ZERO)
    for corner in [shape.position + Vector2(shape.size.x,0), shape.end, shape.position + Vector2(0,shape.size.y)]:
        bounds = bounds.expand(sprite.to_global(corner))
    return bounds

func _draw() -> void:
    if not configured or actor.health <= 0.0: return
    var center := to_local(sprite.to_global(emitter_px))
    var charge := 0.0
    if actor.tactics and actor.tactics.state == "WINDUP":
        charge = clampf(1.0 - actor.tactics.state_left / actor.tactics.state_duration, 0.0, 1.0)
    var radius := 8.0 if kind == "hover_machine" else 26.0
    var power := maxf(flash, charge * 0.5)
    if power > 0.0 and emitter_visible:
        draw_circle(center, radius * (1.0 + power), Color(0.94,0.25,0.75,power * 0.22))
        draw_arc(center, radius * 1.4, -age, TAU-age, 32, Color(0.8,0.45,1.0,power * 0.75),1.5)

func debug_contract() -> Dictionary:
    return {"kind":kind,"configured":configured,"art_warp":false,
        "gait_claim":false,"emitter_px":emitter_px,"emitter_world":muzzle_world(),
        "native_size":image_size,"display_height":image_size.y * render_scale,
        "facing":facing,"view_count":views.size(),"heading_world":visible_heading_world(),
        "emitter_visible":emitter_visible,"texture_sha256":views[facing].texture_sha256,
        "mirrored":false}

```

## FILE: motion_lab_v1/character_workflow.py
SHA256: 06005b2cbba079e832663d1cbb17d9e35b4dd0cad063b35f24f9a7dcaf43cec0
```text
"""Small, local-only handoff workflow for the implemented Motion Studio route.

It inventories exact source slots, binds human/model visual observations to
their files, runs the real tests, and refuses stale or incomplete delivery.
It never calls an image API, fabricates reviews, or publishes a deployment.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parent
DIRECTIONS=['E','SE','S','SW','W','NW','N','NE']
PILOT=['E/idle/0','E/walk/0','E/walk/3','E/walk/1','E/walk/4','E/walk/2','E/walk/5']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ident(value):
    if not re.fullmatch(r'[a-z0-9_-]+',value):raise ValueError('Use an ASCII character id, not a path')
    return value
def local(value):
    path=(ROOT/value).resolve()
    if path==ROOT or not path.is_relative_to(ROOT):raise ValueError('Path must stay below motion_lab_v1')
    return path
def recipe(character):
    c=read(ROOT/'characters'/f'{ident(character)}.json')
    if c['id']!=character or local(c['source'])!=ROOT/'art'/character:raise ValueError('Recipe identity/source mismatch')
    if not {'walk','idle'}<=set(c['clips']) or set(c['clips'])-{'walk','idle','run'}:raise ValueError('Use explicit walk/idle and optional authored run clips')
    for clip in c['clips'].values():
        if type(clip.get('frames')) is not int or not 1<=clip['frames']<=24:raise ValueError('Invalid authored frame count')
        starts=clip.get('phaseStarts')
        if starts is not None and (not isinstance(starts,list) or len(starts)!=clip['frames'] or starts[0]!=0 or any(not isinstance(value,(int,float)) or isinstance(value,bool) or not 0<=value<1 for value in starts) or any(current<=previous for previous,current in zip(starts,starts[1:]))):raise ValueError('phaseStarts must begin at 0 and contain one increasing phase start per frame')
    if any(c['clips'][action]['frames']!=(1 if action=='idle' else 6) for action in c['clips']):raise ValueError('This six-phase workflow requires 6 walk/run frames and 1 idle frame per direction')
    return c
def slots(c):
    for direction in DIRECTIONS:
        for action,spec in c['clips'].items():
            for frame in range(spec['frames']):
                base=local(c['source'])/f'{direction}_{action}_{frame}'
                override=base.with_name(base.name+'_override.png')
                yield f'{direction}/{action}/{frame}',override if override.exists() else base.with_name(base.name+'_master.png')
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
def binding_valid(value):
    try:return sha(local(value['path']))==value['sha256']
    except (KeyError,ValueError,OSError,TypeError):return False

def invalidate_delivery(character,reason):
    """Keep prior evidence, but do not leave a rejected delivery as current."""
    path=ROOT/'dist'/f'{ident(character)}.delivery.json'
    if path.exists():
        previous=ROOT/'qa'/character/'delivery_history'/f'{sha(path)}.json'
        previous.parent.mkdir(parents=True,exist_ok=True)
        if not previous.exists():shutil.copy2(path,previous)
    package=ROOT/'dist'/f'{character}.package.json'
    write(path,{'recordedAt':stamp(),'character':character,'status':'HOLD_VISUAL_REPAIR','reason':reason,'package':binding(package) if package.exists() else None,'reviewedDelivery':False})

def source_status(character):
    c=recipe(character)
    if c.get('workflowVersion')!=1:
        return {'character':character,'ready':False,'mode':'existing-runtime','next':'Use verify-runtime for the accepted existing package. Start an explicit source migration before new art; do not invent historical source reviews.','slots':[],'errors':['Existing paired-source package has no new-workflow review ledger']}
    reference=local(c['identityReference']);errors=[]
    if not reference.exists() or sha(reference)!=c['referenceSHA256']:errors.append('Identity reference missing or changed')
    ledger=ROOT/'qa'/character/'source_reviews.json'
    reviews=read(ledger) if ledger.exists() else []
    rows=[];seen={}
    for name,path in slots(c):
        row={'slot':name,'path':path.relative_to(ROOT).as_posix(),'state':'missing'}
        if path.exists():
            digest=sha(path);row.update(sha256=digest,state='needs_review')
            receipt=path.with_suffix('.source.json')
            if not receipt.exists():row['state']='missing_provenance'
            else:
                r=read(receipt)
                try:
                    from source_provenance import validate_slot
                    validate_slot(ROOT,path,r)
                except (ValueError,KeyError,TypeError,OSError) as error:
                    row['state']='stale_provenance';row['provenanceError']=str(error)
            if digest in seen:row['state']='duplicate_source';errors.append(f'{name}: same source as {seen[digest]}')
            seen[digest]=name
            current=[r for r in reviews if r['slot']==name]
            if row['state']=='needs_review' and current:
                review=current[-1]
                if review.get('sourceSHA256')==digest and review.get('sourceReceiptSHA256')==sha(receipt) and review.get('referenceSHA256')==c['referenceSHA256'] and binding_valid(review.get('evidence')):
                    row['state']='approved' if review['decision']=='approved' else 'repair'
        rows.append(row)
    pending=[r for r in rows if r['state']!='approved']
    pilots=[r for slot in PILOT for r in pending if r['slot']==slot]
    repairs=[r for r in pending if r['state']=='repair']
    next_row=(repairs or pilots or pending or [None])[0]
    return {'character':character,'mode':'source-authoring','ready':not errors and not pending,'requiredFrames':len(rows),'approvedFrames':len(rows)-len(pending),'next':next_row or 'build','errors':errors,'slots':rows}

def review_source(character,slot,decision,evidence,notes,reviewer):
    if decision not in ('approved','repair'):raise ValueError('Use approved or repair')
    c=recipe(character);path=dict(slots(c)).get(slot)
    if path is None or not path.exists():raise ValueError('Cannot review a missing source slot')
    if decision=='approved':
        from cycle_review import require_pilot
        direction,action,_=slot.split('/')
        require_pilot(character,direction,action)
    if not notes.strip() or not reviewer.strip():raise ValueError('Record the actual observation and reviewer')
    proof=local(evidence)
    if not proof.is_file():raise ValueError('Review evidence is missing')
    ledger=ROOT/'qa'/character/'source_reviews.json';reviews=read(ledger) if ledger.exists() else []
    if decision=='approved':
        from source_provenance import pixels
        pixel_hash=pixels(path)
        if any(r.get('decision')=='repair' and (r.get('sourceSHA256')==sha(path) or r.get('sourcePixelSHA256')==pixel_hash) for r in reviews):
            raise ValueError('Rejected source bytes are unchanged; notes cannot repair source art')
        state=next(r['state'] for r in source_status(character)['slots'] if r['slot']==slot)
        if state not in ('needs_review','approved'):
            raise ValueError('Source provenance/readiness must pass before approval: '+state)
    from source_provenance import pixels
    row={'recordedAt':stamp(),'slot':slot,'decision':decision,'reviewer':reviewer,'notes':notes,'sourceSHA256':sha(path),'sourcePixelSHA256':pixels(path),'sourceReceiptSHA256':sha(path.with_suffix('.source.json')) if path.with_suffix('.source.json').exists() else None,'referenceSHA256':c['referenceSHA256'],'evidence':binding(proof)}
    reviews.append(row);write(ledger,reviews)
    if decision=='repair':
        quarantine=ROOT/'qa'/character/'quarantine'/sha(path);quarantine.mkdir(parents=True,exist_ok=True)
        for src in [path,path.with_suffix('.source.json'),proof]:
            if src.exists() and not (quarantine/src.name).exists():shutil.copy2(src,quarantine/src.name)
        write(quarantine/'review.json',row)
        invalidate_delivery(character,'Source rejected: '+slot+'; '+notes)
    return row

def cycle_followup(character, source, cycles):
    """Keep a rejected/complete non-E cycle ahead of unrelated missing views."""
    from cycle_review import ledger
    from source_provenance import pixels
    rows={r['slot']:r for r in source['slots']}
    for cycle in cycles['cycles']:
        if cycle['state']!='repair':continue
        rejection=next((r for r in reversed(ledger(character)) if r['direction']==cycle['direction'] and
                        r['action']==cycle['action'] and r['decision']=='repair'),None)
        if rejection and rejection.get('rejectionScope','source-art')=='source-art':
            old={r['slot']:r for r in rejection['inputs']['sources']}
            for slot in rejection.get('failedSlots',list(old)):
                current=rows.get(slot)
                if not current:continue
                unchanged=current.get('sha256')==old[slot]['sha256']
                if not unchanged and current['state']=='approved' and old[slot].get('pixelSHA256'):
                    unchanged=pixels(local(current['path']))==old[slot]['pixelSHA256']
                if unchanged or current['state']!='approved':
                    return {**current,'kind':'cycle-source-repair','direction':cycle['direction'],
                            'action':cycle['action'],'cycleState':'repair',
                            'reason':rejection.get('notes','Rejected cycle source must be repaired')}
        # Timing/preview/annotation/runtime rejection must not request new art.
        return {'kind':'cycle-review',**cycle,'rejectionScope':rejection.get('rejectionScope') if rejection else None,
                'command':f'character_workflow.py prepare-cycle --character {character} --direction {cycle["direction"]} --action {cycle["action"]}'}
    for cycle in cycles['cycles']:
        if cycle['state'] in ('approved','missing_sources'):continue
        names=[f'{cycle["direction"]}/{cycle["action"]}/{i}' for i in range(6)]
        if cycle['direction']=='E' and cycle['action']=='walk':names+=['E/idle/0']
        if all(name in rows and rows[name]['state']=='approved' for name in names):
            return {'kind':'cycle-review',**cycle,
                    'command':f'character_workflow.py prepare-cycle --character {character} --direction {cycle["direction"]} --action {cycle["action"]}'}
    return None

def workflow_status(character):
    """Source completeness is not cycle readiness or a runtime approval."""
    source=source_status(character)
    if source['mode']=='existing-runtime':return source
    from cycle_review import status as cycle_status
    cycles=cycle_status(character)
    runtime_path=ROOT/'qa'/character/'runtime_reviews.json'
    runtime=read(runtime_path)[-1] if runtime_path.exists() and read(runtime_path) else None
    rejected=runtime is not None and runtime.get('decision')=='repair'
    result=dict(source,sourcesReady=source['ready'],cycleStatus=cycles,runtimeRepairRequired=rejected,
                ready=source['ready'] and cycles['ready'] and not rejected,
                activeBuildReady=source['ready'] and cycles['ready'])
    followup=cycle_followup(character,source,cycles)
    if any(r['state']=='repair' for r in source['slots']):
        pass  # Preserve source_status's explicit failed-slot priority.
    elif isinstance(source['next'],dict) and source['next'].get('slot') in PILOT:
        pass  # An incomplete/unreviewed pilot cannot be skipped for another cycle.
    elif followup:
        result['next']=followup
    elif source['ready'] and not cycles['ready']:
        pending=next(r for r in cycles['cycles'] if r['state']!='approved')
        result['next']={'kind':'cycle-review',**pending,'command':f'character_workflow.py prepare-cycle --character {character} --direction {pending["direction"]} --action {pending["action"]}'}
    elif source['ready'] and cycles['ready']:
        result['next']='repair-runtime-and-recapture' if rejected else 'build-reviewed-cycles'
    if rejected:result['runtimeRejection']=runtime
    return result

def check_package(character):
    from package_standalone import bundle_inputs
    report=read(ROOT/'dist'/f'{ident(character)}.package.json')
    current=bundle_inputs(character)
    if report['character']!=character or report['inputs']!=current:raise ValueError('Stale package: run package_standalone.py for this character')
    if report['inputSHA256']!=hashlib.sha256(json.dumps(current,sort_keys=True).encode()).hexdigest():raise ValueError('Package input digest mismatch')
    destination=local(report['path'])
    if sha(destination)!=report['sha256'] or destination.stat().st_size!=report['bytes']:raise ValueError('Packaged HTML was changed')
    return report

def check_browser(character,path,package):
    report=read(local(path))
    expected={f'{mode}_{d}' for mode in ['mouse','keyboard'] for d in DIRECTIONS}|{'repeat_preserves_mouse'}
    rows=report.get('results',[])
    if report.get('kind')!='motion-studio-combat-browser' or report.get('character')!=character:raise ValueError('Wrong browser report')
    if report.get('build',{}).get('inputSHA256')!=package['inputSHA256']:raise ValueError('Browser report belongs to different source/runtime bytes')
    if report.get('testScriptSHA256')!=sha(ROOT/'public/qa/combat-checks.js'):raise ValueError('Browser test script changed; rerun it')
    if len(rows)!=17 or {r['name'] for r in rows}!=expected or report.get('pass') is not True:raise ValueError('Incomplete browser input matrix')
    for r in rows:
        facing='E' if r['name']=='repeat_preserves_mouse' else r['name'].split('_',1)[1]
        if r.get('pass') is not True or r.get('heldMouse') is not True or r.get('spriteDirection')!=facing or r.get('direction')!=facing or r.get('shotCount',0)<1 or r.get('observedShots')!=r.get('shotCount') or not r.get('travel',0)>.01 or not 0<=r.get('maxFacingErrorDegrees',999)<=24.51:
            raise ValueError('Browser case failed: '+r['name'])
        if r['name'] in ['mouse_E','mouse_S','mouse_W','mouse_N','repeat_preserves_mouse'] and (r.get('convergedShots',0)<1 or not 0<=r.get('maxCursorError',999)<1e-5):raise ValueError('Cursor convergence failed: '+r['name'])
    if report.get('externalResources')!=[]:raise ValueError('Standalone page used external resources or did not record them')
    if len(report.get('viewport',[]))!=2 or report['viewport'][0]<1920 or report['viewport'][1]<1080:raise ValueError('Use a native 1920x1080 or larger QA viewport')
    rapid=report.get('rapidAim',[])
    if len(rapid)!=16 or {r.get('name') for r in rapid}!={f'{mode}_{d}' for mode in ['stationary','moving'] for d in DIRECTIONS}:
        raise ValueError('Missing rapid aim latency matrix; eventual convergence is insufficient')
    import math
    weapon=recipe(character)['weapon']
    for key in ('fireInterval','reloadSeconds'):
        if type(weapon.get(key)) not in (int,float) or not math.isfinite(weapon[key]) or weapon[key]<=0:raise ValueError('Invalid authoritative weapon timing')
    for row in rapid:
        def finite(key):
            value=row.get(key)
            return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0
        if any(row.get(k) is not True for k in ['pass','heldMouse','locomotionUnchanged','oldProjectileVelocityUnchanged']):raise ValueError('Rapid aim state failed: '+row['name'])
        if any(not finite(k) or row[k]>=1e-5 for k in ['immediateErrorDegrees','firstFrameErrorDegrees','shotErrorDegrees']):raise ValueError('Rapid aim used a stale input: '+row['name'])
        if any(not finite(k) for k in ['immediateMs','firstFrameMs','shotWaitSeconds','eligibleBudgetSeconds']):raise ValueError('Invalid aim timing')
        if row['immediateMs']>1000/120 or row['firstFrameMs']>50:raise ValueError('Aim response exceeds latency budget')
        if any(not finite(k) for k in ['initialCooldownSeconds','initialReloadSeconds']):raise ValueError('Missing initial weapon timing')
        cooldown,reload=row['initialCooldownSeconds'],row['initialReloadSeconds']
        ammo=row.get('initialAmmo')
        if (cooldown>weapon['fireInterval']+1e-8 or reload>weapon['reloadSeconds']+1e-8 or
                type(ammo) is not int or not 0<=ammo<=weapon['magazine']):raise ValueError('Initial weapon state exceeds current recipe')
        expected_budget=(max(reload,cooldown) if reload>0 else cooldown+weapon['reloadSeconds'] if ammo==0 else cooldown)+1/120
        if abs(row['eligibleBudgetSeconds']-expected_budget)>1e-8:raise ValueError('Self-declared eligibility budget differs from weapon state')
        samples=row.get('inputSamples',[]);sector=DIRECTIONS.index(row['name'].split('_',1)[1])
        if len(samples)!=3 or [s.get('sector') for s in samples]!=[(sector+4)%8,(sector+2)%8,sector]:raise ValueError('Missing actual reversal sample sequence')
        previous_ms=-1.0
        def vector2(value):return isinstance(value,list) and len(value)==2 and all(type(v) in (int,float) and math.isfinite(v) for v in value)
        for sample in samples:
            ms=sample.get('offsetMs');angle=sample.get('aim')
            if type(ms) not in (int,float) or not math.isfinite(ms) or not previous_ms<=ms<=row['immediateMs']:raise ValueError('Invalid reversal sample time')
            previous_ms=ms
            muzzle=sample.get('muzzle')
            if (not isinstance(muzzle,list) or len(muzzle)!=3 or not vector2(muzzle[:2]) or
                type(muzzle[2]) not in (int,float) or not math.isfinite(muzzle[2]) or
                abs(muzzle[2]-weapon['height'])>1e-8 or not vector2(sample.get('target')) or
                type(angle) not in (int,float) or not math.isfinite(angle)):
                raise ValueError('Missing sampled muzzle ray at actual weapon height')
            if not vector2(sample.get('requestedTarget')) or not vector2(sample.get('actorPosition')):raise ValueError('Missing independently requested target')
            origin,requested=sample['actorPosition'],sample['requestedTarget']
            requested_angle=sample['sector']*math.pi/4
            if (math.hypot(*(requested[i]-origin[i]-4*f(requested_angle) for i,f in enumerate((math.cos,math.sin))))>1e-6 or
                math.hypot(*(sample['target'][i]-requested[i] for i in (0,1)))>1e-6):raise ValueError('Reversal labels do not match actual requested target')
            if origin!=row.get('locomotionBefore',[])[3:5] or sample.get('actorTime')!=row.get('locomotionBefore',[None])[0]:raise ValueError('Reversal actor basis differs from observed state')
            x,y=(sample['target'][i]-sample['muzzle'][i] for i in (0,1))
            difference=math.atan2(y,x)-angle
            if math.hypot(x,y)<1e-8 or abs(math.atan2(math.sin(difference),math.cos(difference)))>math.radians(1e-5):raise ValueError('A reversal sample used stale aim')
        before,after=row.get('locomotionBefore'),row.get('locomotionAfterInput')
        if (not isinstance(before,list) or len(before)!=9 or before!=after or
                any(type(v) not in (int,float) or not math.isfinite(v) for v in before)):
            raise ValueError('Immediate input changed locomotion or weapon state')
        if before[5]!=ammo or max(0,before[6])!=cooldown or before[8]!=reload:raise ValueError('Initial weapon state differs from sampled actor')
        old=row.get('oldProjectileSamples')
        if not isinstance(old,list):raise ValueError('Missing old projectile velocity samples')
        for i,bullet in enumerate(old):
            if bullet.get('index')!=i or not vector2(bullet.get('before')) or not vector2(bullet.get('after')) or bullet['before']!=bullet['after']:raise ValueError('Old projectile changed velocity')
        if row['shotWaitSeconds']>row['eligibleBudgetSeconds']+1/120+1e-8 or row.get('shotCount',0)<1:raise ValueError('Projectile missed first eligible step')
        if not finite('travel') or (row['travel']<=.01 if row['name'].startswith('moving_') else row['travel']>=.01):raise ValueError('Rapid aim movement coverage missing')
    return binding(local(path))

def verify_runtime(character,browser_report=None,locomotion_report=None):
    package=check_package(character);out=ROOT/'qa'/character
    run=out/'checks'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');run.mkdir(parents=True)
    env=os.environ.copy();env.update(TEMP=str(run),TMP=str(run),PYTHONDONTWRITEBYTECODE='1')
    tests=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('*.test.js'))
    commands=[[sys.executable,'-B','validate_character.py','--character',character],['node','--test',*tests],[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],['node','verify_bundle.mjs',str(local(package['path']))]]
    checks=[]
    for index,command in enumerate(commands):
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        log=run/f'{index}.log';log.write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        checks.append({'command':command,'exitCode':result.returncode,'log':binding(log)})
        if result.returncode:raise ValueError('Validation failed; inspect '+str(log.relative_to(ROOT)))
    browser=check_browser(character,browser_report,package) if browser_report else None
    from locomotion_review import check as check_locomotion
    locomotion=check_locomotion(ROOT,character,locomotion_report,package) if locomotion_report else None
    result={'recordedAt':stamp(),'character':character,'status':'PASS_RUNTIME_CHECKS' if browser and locomotion else 'PASS_INPUT_CHECKS_ONLY' if browser else 'PASS_TECHNICAL_ONLY','package':binding(ROOT/'dist'/f'{character}.package.json'),'inputSHA256':package['inputSHA256'],'checks':checks,'browser':browser,'locomotion':locomotion,'scope':'Input plus temporal selected-renderer checks when supplied; no automatic anatomy, foot-contact, visual approval or Luna generation claim'}
    write(run/'result.json',result);write(out/'latest_runtime_check.json',result)
    return result

def review_runtime(character,evidence,decision,notes,reviewer,locomotion_report=None,motion_evidence=None,observations=None):
    from PIL import Image
    package=check_package(character);path=local(evidence)
    with Image.open(path) as image:
        image.load();width,height=image.size
    if width<1920 or height<1080:raise ValueError('Runtime visual review needs native 1920x1080 evidence')
    if not notes.strip() or not reviewer.strip():raise ValueError('Record actual visual observations and reviewer')
    result={'recordedAt':stamp(),'character':character,'inputSHA256':package['inputSHA256'],'evidence':binding(path),'nativeDimensions':[width,height],'decision':decision,'notes':notes,'reviewer':reviewer}
    if decision=='approved':
        from cycle_review import require_build
        require_build(character)
        if not locomotion_report or not motion_evidence:raise ValueError('A still image cannot approve gait. Supply current --locomotion-report and native --motion-evidence video after watching it')
        from locomotion_review import check as check_locomotion
        result['locomotion']=check_locomotion(ROOT,character,locomotion_report,package)
        import cv2
        video=local(motion_evidence);cap=cv2.VideoCapture(str(video))
        w,h,frames,fps=[cap.get(k) for k in [cv2.CAP_PROP_FRAME_WIDTH,cv2.CAP_PROP_FRAME_HEIGHT,cv2.CAP_PROP_FRAME_COUNT,cv2.CAP_PROP_FPS]]
        ok,_=cap.read();cap.release()
        if not ok or w<1920 or h<1080 or fps<=0 or frames/fps<2:raise ValueError('Motion review requires a decodable native 1080p video spanning at least two seconds')
        result['motionEvidence']=binding(video)
        from motion_evidence import check as check_motion
        result['motionCapture']=check_motion(ROOT,video,package)
        if not observations:raise ValueError('Supply time-specific --observations; generic notes cannot approve gait')
        from runtime_observations import validate
        validate(read(local(observations)),character,package,read(video.with_suffix('.json')),reviewer)
        result['observations']=binding(local(observations))
    path=ROOT/'qa'/character/'runtime_reviews.json';history=read(path) if path.exists() else [];history.append(result);write(path,history)
    if decision!='approved':invalidate_delivery(character,'Runtime visual review requires repair: '+notes)
    return result

def deliver(character,browser_report,locomotion_report):
    from cycle_review import require_build
    cycle_checks=require_build(character)
    # Fail before expensive tests when a visible rejection is still current.
    reviews=read(ROOT/'qa'/character/'runtime_reviews.json')
    if not reviews or reviews[-1].get('decision')!='approved':raise ValueError('Current runtime visual rejection/missing review must be resolved before delivery')
    status=source_status(character)
    if not status['ready']:raise ValueError('Source review is incomplete: '+json.dumps(status['next'],ensure_ascii=False))
    result=verify_runtime(character,browser_report,locomotion_report)
    reviews=read(ROOT/'qa'/character/'runtime_reviews.json');review=reviews[-1]
    if review['decision']!='approved' or review['inputSHA256']!=result['inputSHA256'] or not binding_valid(review['evidence']) or not binding_valid(review.get('motionEvidence')) or not binding_valid(review.get('motionCapture')) or review.get('locomotion')!=result['locomotion']:raise ValueError('Current temporal/visual review is missing, failed, or stale')
    if not binding_valid(review.get('observations')):raise ValueError('Time-specific runtime visual observations are missing/stale')
    from runtime_observations import validate
    validate(read(local(review['observations']['path'])),character,check_package(character),read(local(review['motionCapture']['path'])),review['reviewer'])
    from motion_evidence import check as check_motion
    check_motion(ROOT,local(review['motionEvidence']['path']),check_package(character))
    result.update(status='REVIEWED_DELIVERY',sourceReviews=binding(ROOT/'qa'/character/'source_reviews.json'),runtimeReviews=binding(ROOT/'qa'/character/'runtime_reviews.json'),cycleReviews=binding(ROOT/'qa'/character/'cycle_reviews.json'),cycleChecks=cycle_checks)
    write(ROOT/'dist'/f'{character}.delivery.json',result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ['status','handoff','build','verify-runtime','deliver','review-source','review-runtime']:
        s=sub.add_parser(name);s.add_argument('--character',required=True,type=ident)
        if name in ['verify-runtime','deliver']:s.add_argument('--browser-report',required=name=='deliver')
        if name in ['verify-runtime','deliver','review-runtime']:s.add_argument('--locomotion-report',required=name=='deliver')
        if name=='review-runtime':s.add_argument('--motion-evidence');s.add_argument('--observations')
        if name in ['review-source','review-runtime']:
            s.add_argument('--decision',choices=['approved','repair'],required=True);s.add_argument('--evidence',required=True);s.add_argument('--notes',required=True);s.add_argument('--reviewer',required=True)
        if name=='review-source':s.add_argument('--slot',required=True)
        if name=='handoff':s.add_argument('--output',help='New packet path below motion_lab_v1/qa; never overwritten')
    s=sub.add_parser('verify-handoff');s.add_argument('--packet',required=True)
    s=sub.add_parser('verify-improvements');s.add_argument('--output',help='Optional fresh QA receipt path')
    s=sub.add_parser('prepare-runtime-review');s.add_argument('--character',required=True,type=ident);s.add_argument('--motion-evidence',required=True)
    for name in ['prepare-cycle','review-cycle']:
        s=sub.add_parser(name);s.add_argument('--character',required=True,type=ident);s.add_argument('--direction',required=True,choices=DIRECTIONS);s.add_argument('--action',default='walk',choices=['walk','run'])
        if name=='review-cycle':
            s.add_argument('--decision',required=True,choices=['approved','repair']);s.add_argument('--packet');s.add_argument('--evidence');s.add_argument('--notes');s.add_argument('--reviewer')
            s.add_argument('--rejection-scope',choices=['source-art','timing','preview','annotation','runtime'])
            s.add_argument('--failed-slot',action='append');s.add_argument('--required-change',action='append')
    a=p.parse_args()
    try:
        if a.command=='status':result=workflow_status(a.character)
        elif a.command=='prepare-cycle':
            from cycle_preview import prepare
            result=prepare(a.character,a.direction,a.action)
        elif a.command=='review-cycle':
            from cycle_review import record
            result=record(a.character,a.direction,a.action,a.decision,a.packet,a.evidence,a.notes,a.reviewer,a.rejection_scope,a.failed_slot,a.required_change)
        elif a.command=='prepare-runtime-review':
            from motion_evidence import check as check_motion
            from runtime_observations import template
            package=check_package(a.character);video=local(a.motion_evidence);check_motion(ROOT,video,package)
            path=ROOT/'qa'/a.character/'runtime_observations'/f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.json'
            write(path,template(a.character,package,read(video.with_suffix('.json'))))
            result={'status':'UNREVIEWED_RUNTIME_TEMPLATE','path':str(path)}
        elif a.command=='handoff':
            from character_handoff import make
            packet=make(a.character)
            path=local(a.output or f'qa/{a.character}/handoffs/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.json')
            if not path.is_relative_to(ROOT/'qa') or path.exists():raise ValueError('Use a fresh QA packet path; prior handoffs are preserved')
            write(path,packet)
            result={'status':packet['status'],'packet':str(path),'nextAction':packet['nextAction'],'nextSource':packet['nextSource'],'warnings':packet['warnings'],'reviewedDelivery':False,'lunaGenerationTested':False}
        elif a.command=='verify-handoff':
            from character_handoff import verify
            result=verify(a.packet)
        elif a.command=='verify-improvements':
            from improvement_harness import verify_r3
            result=verify_r3(ROOT.parent)
            if a.output:
                path=local(a.output)
                if not path.is_relative_to(ROOT/'qa') or path.exists():raise ValueError('Use a fresh QA receipt path')
                write(path,result)
            result={k:v for k,v in result.items() if k!='inputs'}
        elif a.command=='build':
            status=source_status(a.character)
            if not status['ready']:raise ValueError('Resolve source status first: '+json.dumps(status['next'],ensure_ascii=False))
            from build_character import compile_character
            result=compile_character(ROOT/'characters'/f'{a.character}.json')
        elif a.command=='verify-runtime':result=verify_runtime(a.character,a.browser_report,a.locomotion_report)
        elif a.command=='deliver':result=deliver(a.character,a.browser_report,a.locomotion_report)
        elif a.command=='review-source':result=review_source(a.character,a.slot,a.decision,a.evidence,a.notes,a.reviewer)
        else:result=review_runtime(a.character,a.evidence,a.decision,a.notes,a.reviewer,a.locomotion_report,a.motion_evidence,a.observations)
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as error:
        print(json.dumps({'status':'NEEDS_FIX','error':str(error)},ensure_ascii=False));return 1

if __name__=='__main__':raise SystemExit(main())

```

## FILE: motion_lab_v1/character_handoff.py
SHA256: a780c28e00bbddc87c6a675557b06f4b8ee183a104431476f868584875c70688
```text
"""Emit exact-byte resume instructions for the existing character workflow.

No provider calls, model switches, generations, reviews, promotion, or scene
changes. A packet is a handoff, never proof of a Luna production run.
"""
from pathlib import Path
import hashlib
import json
import character_workflow as workflow

CORE = ('character_workflow.py', 'character_handoff.py', 'improvement_harness.py', 'compact_atlas.py', 'README_KO.md',
        'gait_contract.py', 'cycle_review.py', 'cycle_preview.py', 'cycle_live_review.js', 'runtime_observations.py', 'source_provenance.py',
        'new_character.py', 'build_character.py', 'build_atlas.py', 'intake_frame.py', 'intake_pair.py', 'preview_gait.py',
        'package_standalone.py', 'validate_character.py', 'intake_derived_frame.py', 'locomotion_review.py', 'motion_evidence.py',
        'public/keyboard-input.js', 'public/combat-aim.js', 'public/simulation.js', 'public/atlas-renderer.js', 'public/studio.js',
        'public/qa/combat-checks.js', 'public/qa/locomotion-checks.js', 'public/qa/capture-motion.js')
REFERENCES = ('SKILL.md', 'references/authoring.md', 'references/gait-repair.md',
              'references/browser-check.md', 'references/reuse-improvements.md', 'references/cycle-review.md',
              'references/aim-response.md', 'references/enemy-facing.md')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fingerprint(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()

def make(character):
    lab = workflow.ROOT.resolve()
    project = lab.parent
    config = workflow.recipe(character)
    status = workflow.workflow_status(character)
    inputs = {}

    def include(path):
        path = path.resolve()
        if path == project or not path.is_relative_to(project):
            raise ValueError('Handoff input must stay in project')
        inputs[path.relative_to(project).as_posix()] = sha(path) if path.is_file() else None

    for name in CORE:
        include(lab / name)
    for name in REFERENCES:
        include(project / '.agents/skills/sable-character-studio' / name)
    include(lab / 'characters' / f'{character}.json')
    include(lab / 'AGENTS.md')
    for path in (lab / 'tests').glob('*'):
        if path.is_file() and (path.suffix == '.py' or path.name.endswith('.test.js')):
            include(path)
    if config.get('identityReference'):
        include(workflow.local(config['identityReference']))
    for row in status['slots']:
        path = workflow.local(row['path'])
        include(path)
        receipt = path.with_suffix('.source.json')
        include(receipt)
        if receipt.is_file():
            source = workflow.read(receipt)
            for key in ('toolResponse', 'sourceMaster'):
                if source.get(key):
                    include(workflow.local(source[key]['path']))
            for key in ('normalization','mask'):
                entry=source.get('derivation',{}).get(key)
                if isinstance(entry,dict) and entry.get('path'):include(workflow.local(entry['path']))
    include(lab / 'art' / character / 'requests.json')
    requests_path=lab / 'art' / character / 'requests.json'
    if requests_path.is_file():
        for request in workflow.read(requests_path):
            if request.get('poseGuide'):include(workflow.local(request['poseGuide']))
    for relative in (f'qa/{character}/source_reviews.json', f'qa/{character}/runtime_reviews.json', f'qa/{character}/cycle_reviews.json',
                     f'dist/{character}.package.json', f'dist/{character}.delivery.json',
                     f'public/assets/atlas/{character}/profile.json'):
        path = workflow.local(relative)
        include(path)
        if path.is_file() and path.name.endswith('_reviews.json'):
            for row in workflow.read(path):
                for key in ('evidence', 'motionEvidence', 'motionCapture', 'locomotion', 'packet','observations'):
                    if isinstance(row.get(key), dict) and row[key].get('path'):
                        bound=workflow.local(row[key]['path']);include(bound)
                        if key=='packet' and bound.is_file():
                            packet=workflow.read(bound)
                            if packet.get('preview'):
                                pp=workflow.local(packet['preview']['path']);include(pp)
                                if pp.is_file():
                                    for evidence_key in ('video','atlas','contact'):
                                        entry=workflow.read(pp).get(evidence_key)
                                        if entry:include(workflow.local(entry['path']))
    profile_path = lab / f'public/assets/atlas/{character}/profile.json'
    if profile_path.is_file():
        profile = workflow.read(profile_path)
        if profile.get('id') != character:
            raise ValueError('Runtime profile identity differs from handoff')
        for view in profile.get('views', {}).values():
            for clip in view.values():
                if isinstance(clip, dict) and clip.get('image'):
                    include(workflow.local('public/' + clip['image']))
                if isinstance(clip, dict):
                    for source in clip.get('sources', []):
                        if source.get('source'):
                            include(workflow.local(source['source']))
        for relative in (f'public/assets/atlas/{character}/portrait.png', 'public/style.css',
                         'public/index.html', 'public/assets/Rajdhani-Medium.ttf'):
            include(workflow.local(relative))
        if profile.get('animation', {}).get('presentation') != 'authored_frames':
            selected = None
            for name in ('coherent', 'fire'):
                possible = workflow.local(f'public/assets/atlas/{character}/{name}/manifest.json')
                include(possible)
                if selected is None and possible.is_file():
                    selected = possible
            if selected:
                for entry in workflow.read(selected).get('directions', {}).values():
                    for key in ('idle','walk','run','move','fire','upper','idleLower','moveLower'):
                        if entry.get(key):
                            include(workflow.local('public/' + entry[key]))
    errors = list(status['errors'])
    if status['mode'] != 'existing-runtime' and status['errors']:
        action = 'REPAIR_SOURCE_STATUS_ERRORS'
    elif status['mode'] == 'existing-runtime':
        action = 'VERIFY_EXISTING_RUNTIME'
    elif status.get('runtimeRepairRequired'):
        action = 'REPAIR_RUNTIME_VISUAL'
    elif any(r['state'] == 'repair' for r in status['slots']):
        action = 'REPAIR_REPORTED_SOURCE'
    elif isinstance(status.get('next'),dict) and status['next'].get('kind')=='cycle-source-repair':
        action = 'REPAIR_REPORTED_CYCLE_SOURCE'
    elif isinstance(status.get('next'),dict) and status['next'].get('kind')=='cycle-review':
        action = 'REVIEW_WHOLE_CYCLE'
    elif status['ready']:
        action = 'BUILD_REVIEWED_SOURCES'
    else:
        action = 'COMPLETE_OR_REVIEW_NEXT_SOURCE'
    candidate = None
    if character == 'rook':
        from improvement_harness import verify_r3
        try:
            candidate = verify_r3(project)
            inputs.update(candidate.pop('inputs'))
        except (ValueError, OSError, KeyError, TypeError) as error:
            candidate = {'status': 'STALE_OR_MISSING_EVIDENCE', 'error': str(error), 'productionPromotion': False}
            errors.append('Frozen R3 reuse evidence is unavailable/stale; do not regenerate retired inputs or claim its old result: ' + str(error))
        weapon_path = project / 'data/progression/weapons.json'
        include(weapon_path)
        if weapon_path.is_file():
            expected = next((row for row in workflow.read(weapon_path)['weapons']
                             if row.get('default_for') == 'CHR_PROTO_02'), None)
            if expected:
                mismatches = {key: {'recipe': config.get('weapon', {}).get(key), 'game': expected[game_key]}
                              for key, game_key in (('magazine','magazine_size'), ('fireInterval','fire_interval'),
                                                    ('reloadSeconds','reload_duration'))
                              if config.get('weapon', {}).get(key) != expected[game_key]}
                if mismatches:
                    errors.append('ROOK art scaffold weapon values differ from the actual game: ' + json.dumps(mismatches))
        errors.append('Before new ROOK HTML gameplay integration, verify movement-unit mapping and scattergun pellet behavior; an art scaffold is not a gameplay parity receipt.')
    ready_core = (all(inputs.get((lab / name).relative_to(project).as_posix()) for name in CORE)
                  and all(inputs.get(('.agents/skills/sable-character-studio/' + name)) for name in REFERENCES))
    if not ready_core:
        errors.append('Required current workflow module missing; repair installation before executing the packet')
    next_source = status.get('next')
    affected_direction = (next_source.get('slot','E/').split('/')[0] if 'slot' in next_source else next_source.get('direction','E')) if isinstance(next_source, dict) else 'E'
    return {'kind': 'sable-character-handoff', 'schema': 1, 'recordedAt': workflow.stamp(),
            'character': character, 'route': 'motion_lab_v1/authored_frames',
            'status': 'READY_TO_RESUME' if ready_core else 'NEEDS_WORKFLOW_FIX',
            'nextAction': action, 'nextSource': status.get('next'), 'sourceStatus': status,
            'candidateEvidence': candidate, 'warnings': errors,
            'reference': config.get('identityReference'), 'recipe': f'characters/{character}.json',
            'commands': {'status': f'character_workflow.py status --character {character}',
                         'previewAffectedCycle': f'preview_gait.py --character {character} --direction {affected_direction}',
                         'prepareCycleReview': f'character_workflow.py prepare-cycle --character {character} --direction {affected_direction}',
                         'buildOnlyWhenReady': f'character_workflow.py build --character {character}',
                         'packageAfterBuild': f'package_standalone.py --character {character}',
                         'regressionPython': '-B -m unittest discover -s tests -p test_*.py',
                         'regressionNode': 'node --test tests/*.test.js'},
            'requiredReading': [str(project / '.agents/skills/sable-character-studio' / n) for n in REFERENCES],
            'boundaries': ['This packet authorizes no generation, model switch, delegation or deployment',
                           'Use actual reference and recipe; no copied character pixels or split-leg fallback',
                           'Repair known failures before expanding views; inspect real E idle/opposite contacts and chronological cycle',
                           'Two same-category source failures require changing the failed approach, not blind retries',
                           'Technical fixtures and pinned R3 evidence are NOT Luna production success',
                           'Actual source and native temporal runtime reviews still required for delivery'],
            'lunaGenerationTested': False, 'reviewedDelivery': False,
            'inputs': inputs, 'inputSHA256': fingerprint(inputs)}

def verify(packet_path):
    packet = workflow.read(workflow.local(packet_path))
    if packet.get('kind') != 'sable-character-handoff' or packet.get('schema') != 1:
        raise ValueError('Not a current character handoff')
    if packet.get('inputSHA256') != fingerprint(packet['inputs']):
        raise ValueError('Handoff fingerprint differs')
    project = workflow.ROOT.resolve().parent
    for name, digest in packet['inputs'].items():
        path = (project / name).resolve()
        if path == project or not path.is_relative_to(project):
            raise ValueError('Handoff input escapes project')
        if (sha(path) if path.is_file() else None) != digest:
            raise ValueError('Stale handoff input: ' + name)
    fresh = make(packet['character'])
    if fresh['inputs'] != packet['inputs'] or fresh['sourceStatus'] != packet['sourceStatus']:
        raise ValueError('Source choice or current dependency set changed; recreate handoff')
    for key in ('route','status','nextAction','nextSource','candidateEvidence','warnings','commands',
                'reference','recipe','requiredReading','boundaries','lunaGenerationTested','reviewedDelivery'):
        if packet.get(key) != fresh[key]:
            raise ValueError('Handoff instructions or conclusions were changed: ' + key)
    return {'status': 'CURRENT_HANDOFF', 'character': packet['character'],
            'inputSHA256': packet['inputSHA256'], 'nextAction': fresh['nextAction'],
            'reviewedDelivery': False, 'lunaGenerationTested': False}

```

## FILE: motion_lab_v1/tests/test_reuse_improvements.py
SHA256: ade13785a340eec41477571f0eb3c437d8b7402f072b5104d8c4d91ca8fe8e55
```text
"""Local technical fixtures only. No game art, providers, or model runs."""
import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import compact_atlas as atlas
import improvement_harness as harness
import character_handoff as handoff
import character_workflow as workflow

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')

def fixture_root(prefix):
    parent = LAB / 'qa/technical_tests'
    parent.mkdir(parents=True, exist_ok=True)
    # Keep owned fixtures and failed evidence; never recursively clean user data.
    return Path(tempfile.mkdtemp(prefix=prefix, dir=parent))

class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.root = fixture_root('lossless_')
        self.desc_path = self.root / 'descriptor.json'
        self.output = self.root / 'motion_lab_v1/qa/candidate'
        desc = {'cell_size': 4, 'display_scale': .5, 'display_offset': [0, -4],
                'states': {'idle': {'frames': 1, 'fps': 1}, 'move': {'frames': 4, 'fps': 24},
                           'fire': {'frames': 2, 'fps': 12}}, 'directions': {}}
        for direction in atlas.DIRECTIONS:
            row = {'muzzle_xy': [3, 1]}
            for state, spec in desc['states'].items():
                path = self.root / direction / (state + '.png')
                path.parent.mkdir(parents=True, exist_ok=True)
                image = Image.new('RGBA', (4, 4 * spec['frames']))
                for index in range(spec['frames']):
                    # Two visually transparent but byte-distinct cells catch
                    # accidental hidden-RGB normalization and false deduplication.
                    cell = Image.new('RGBA', (4, 4), (20 + 20 * (index % 2), 80, 120, 0))
                    image.paste(cell, (0, index * 4))
                image.save(path)
                row[state + '_atlas'] = path.relative_to(self.root).as_posix()
            desc['directions'][direction] = row
        save(self.desc_path, desc)

    def build(self):
        result = atlas.pack(self.root, self.desc_path, self.output)
        return Path(result['manifest'])

    def test_preserves_all_slots_and_hidden_rgba(self):
        path = self.build()
        result = atlas.verify(self.root, path)
        self.assertEqual(result['rgba_exact_timing_cells'], 56)
        self.assertTrue(result['timing_unchanged'])
        self.assertFalse(result['production_approved'])
        manifest = atlas.read(path)
        self.assertEqual(manifest['directions']['E']['unique_cells'], 2)
        frames = manifest['directions']['E']['states']['move']
        self.assertEqual(len(frames), 4)
        self.assertAlmostEqual(sum(f['duration_seconds'] for f in frames), 4 / 24)
        self.assertEqual(frames[0]['x'], frames[2]['x'])

    def test_changed_duration_or_order_or_offset_fails(self):
        path = self.build()
        original = atlas.read(path)
        for mutate in (
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=.5),
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=math.nan),
            lambda m: m['directions']['E']['states']['move'][0].update(source_frame=1),
            lambda m: m['directions']['E']['states']['move'][0].update(x=999),
            lambda m: m['directions']['E']['states']['move'].pop(),
            lambda m: m.update(display_offset=[0, 0]),
        ):
            broken = copy.deepcopy(original)
            mutate(broken)
            save(path, broken)
            with self.assertRaises(ValueError):
                atlas.verify(self.root, path)

    def test_resealed_pixel_corruption_still_fails_against_original(self):
        path = self.build()
        manifest = atlas.read(path)
        page = self.root / manifest['directions']['E']['texture']
        image = atlas.rgba(page)
        image.putpixel((0, 0), (1, 2, 3, 0))
        image.save(page)
        manifest['directions']['E']['sha256'] = atlas.sha(page)
        save(path, manifest)
        with self.assertRaisesRegex(ValueError, 'RGBA differs'):
            atlas.verify(self.root, path)

    def test_source_change_is_not_accepted_from_old_checks(self):
        path = self.build()
        source = self.root / 'E/move.png'
        Image.new('RGBA', (4, 16), (200, 0, 0, 255)).save(source)
        with self.assertRaisesRegex(ValueError, 'Original texture changed'):
            atlas.verify(self.root, path)

    def test_rgb_without_real_alpha_is_not_silently_converted(self):
        source = self.root / 'E/idle.png'
        Image.new('RGB', (4, 4), (0, 255, 0)).save(source)
        with self.assertRaisesRegex(ValueError, 'actual RGBA'):
            self.build()

    def test_no_overwrite_or_output_escape(self):
        path = self.build()
        before = atlas.sha(path)
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(atlas.sha(path), before)
        with self.assertRaises(ValueError):
            atlas.pack(self.root, self.desc_path, self.root / 'production')
        self.assertFalse((self.root / 'production').exists())

class PerformanceTests(unittest.TestCase):
    def rows(self):
        row = {'p95_ms': 6.424, 'p99_ms': 19.714, 'squad_count': 3, 'end_hostiles': 3}
        return [dict(row) for _ in range(3)]

    def test_r3_relative_failure_cannot_be_rounded_to_pass(self):
        baseline, candidate = self.rows(), self.rows()
        for row in candidate:
            row['p95_ms'] = 7.106
        result = harness.evaluate_performance(baseline, candidate)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(result['absolute_budget_met'])
        self.assertFalse(result['relative_budget_met'])

    def test_valid_within_budget_data_can_pass(self):
        self.assertEqual(harness.evaluate_performance(self.rows(), self.rows())['status'], 'PASS')

    def test_missing_repeat_invalid_number_and_population_fail(self):
        for mutate in (lambda r: r.pop(), lambda r: r[0].update(p95_ms=float('nan')),
                       lambda r: r[0].update(p99_ms=float('inf')), lambda r: r[0].update(p95_ms=True),
                       lambda r: r[0].update(end_hostiles=2), lambda r: r[0].update(p99_ms=1)):
            candidate = self.rows()
            mutate(candidate)
            with self.assertRaises(ValueError):
                harness.evaluate_performance(self.rows(), candidate)

    def test_empty_and_stale_input_binding_fails(self):
        root = fixture_root('binding_')
        path = root / 'file.txt'
        path.write_text('fixture', encoding='utf-8')
        values = {'file.txt': atlas.sha(path)}
        harness.check_bindings(root, values)
        path.write_text('changed', encoding='utf-8')
        for value in ({}, values, {'../outside': 'invalid'}):
            with self.assertRaises(ValueError):
                harness.check_bindings(root, value)

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.project = fixture_root('handoff_')
        self.lab = self.project / 'motion_lab_v1'
        self.lab.mkdir()
        self.patch = patch.object(workflow, 'ROOT', self.lab)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for name in handoff.CORE + ('AGENTS.md',):
            path = self.lab / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical file fixture only', encoding='utf-8')
        for name in handoff.REFERENCES:
            path = self.project / '.agents/skills/sable-character-studio' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical instruction fixture only', encoding='utf-8')
        reference = self.lab / 'art/fixture/identity_reference.png'
        reference.parent.mkdir(parents=True)
        reference.write_bytes(b'not image generation: identity hash fixture')
        self.config = {'id': 'fixture', 'name': 'Technical fixture', 'source': 'art/fixture',
                       'heightMetres': 1.72, 'locomotion': {'walkSpeed': 1.35, 'walkStride': 1.6},
                       'workflowVersion': 1, 'identityReference': 'art/fixture/identity_reference.png',
                       'referenceSHA256': atlas.sha(reference), 'clips': {'walk': {'frames': 6}, 'idle': {'frames': 1}}}
        save(self.lab / 'characters/fixture.json', self.config)
        self.packet_path = self.lab / 'qa/handoff.json'

    def packet(self):
        packet = handoff.make('fixture')
        save(self.packet_path, packet)
        return packet

    def test_packet_has_real_next_slot_not_generation_success(self):
        packet = self.packet()
        self.assertEqual(packet['status'], 'READY_TO_RESUME')
        self.assertEqual(packet['nextSource']['slot'], 'E/idle/0')
        self.assertFalse(packet['lunaGenerationTested'])
        self.assertFalse(packet['reviewedDelivery'])
        self.assertEqual(handoff.verify(str(self.packet_path))['status'], 'CURRENT_HANDOFF')

    def test_code_change_invalidates_packet(self):
        self.packet()
        (self.lab / 'public/atlas-renderer.js').write_text('changed fixture', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_new_missing_source_invalidates_packet(self):
        self.packet()
        (self.lab / 'art/fixture/E_walk_0_master.png').write_bytes(b'new test bytes')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_aim_latency_instruction_change_invalidates_packet(self):
        self.packet()
        path=self.project / '.agents/skills/sable-character-studio/references/aim-response.md'
        path.write_text('Changed aim latency constraint fixture',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_runtime_texture_change_invalidates_packet(self):
        texture = self.lab / 'public/assets/atlas/fixture/E_walk.webp'
        texture.parent.mkdir(parents=True)
        texture.write_bytes(b'non-art texture fixture')
        save(texture.parent / 'profile.json', {'id': 'fixture', 'animation': {'presentation': 'authored_frames'},
             'views': {'E': {'walk': {'image': 'assets/atlas/fixture/E_walk.webp', 'sources': []}}}})
        self.packet()
        texture.write_bytes(b'changed texture fixture')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_changed_claim_or_instruction_is_rejected(self):
        original = self.packet()
        for update in ({'reviewedDelivery': True}, {'lunaGenerationTested': True}, {'nextAction': 'DEPLOY_NOW'}):
            packet = copy.deepcopy(original)
            packet.update(update)
            save(self.packet_path, packet)
            with self.assertRaisesRegex(ValueError, 'instructions or conclusions'):
                handoff.verify(str(self.packet_path))

    def test_known_repair_precedes_missing_pilot_slot(self):
        source = self.lab / 'art/fixture/E_walk_0_master.png'
        Image.new('RGBA',(16,24),(90,110,130,255)).save(source)
        master=source.with_name('technical_original.png');master.write_bytes(source.read_bytes())
        proof = self.lab / 'qa/proof.json'
        returned=str(self.lab/'technical_returned.png')
        save(proof, {'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Synthetic test, not a real invocation: '+returned},'projectCopy':str(master.relative_to(self.lab)),'projectCopySHA256':atlas.sha(master)})
        save(source.with_suffix('.source.json'), {'testFixture': True, 'generator': 'Codex built-in ImageGen',
             'sha256': atlas.sha(source), 'toolResponse': workflow.binding(proof),'sourceMaster':workflow.binding(master),'destination':str(source.relative_to(self.lab))})
        workflow.review_source('fixture', 'E/walk/0', 'repair', str(source),
                               'Technical negative fixture, not actual art review', 'unit-test')
        packet = self.packet()
        self.assertEqual(packet['nextAction'], 'REPAIR_REPORTED_SOURCE')
        self.assertEqual(packet['nextSource']['slot'], 'E/walk/0')

    def test_runtime_rejection_is_the_next_action_not_a_rebuild(self):
        save(self.lab/'qa/fixture/runtime_reviews.json',[{'decision':'repair','notes':'Synthetic rejected gait fixture'}])
        packet=self.packet()
        self.assertEqual(packet['nextAction'],'REPAIR_RUNTIME_VISUAL')
        self.assertTrue(packet['sourceStatus']['runtimeRepairRequired'])
        self.assertFalse(packet['sourceStatus']['ready'])

    def pending_cycle_fixture(self, state='repair'):
        rows=[{'slot':f'SE/walk/{i}','path':f'art/fixture/SE_walk_{i}_master.png',
               'state':'approved','sha256':f'old-{i}'} for i in range(6)]
        missing={'slot':'S/walk/0','path':'art/fixture/S_walk_0_master.png','state':'missing'}
        source={'character':'fixture','mode':'source-authoring','ready':False,'next':missing,
                'requiredFrames':56,'approvedFrames':6,'errors':[],'slots':rows+[missing]}
        cycle={'direction':'SE','action':'walk','state':state}
        cycles={'required':True,'ready':False,'cycles':[{'direction':'E','action':'walk','state':'approved'},cycle]}
        rejection={'direction':'SE','action':'walk','decision':'repair','rejectionScope':'source-art',
                   'failedSlots':['SE/walk/3','SE/walk/4'],'inputs':{'sources':rows[:6]},'notes':'Synthetic cycle-only rejection'}
        return source,cycles,rejection

    def test_non_e_cycle_repair_precedes_unrelated_missing_direction(self):
        source,cycles,rejection=self.pending_cycle_fixture()
        with patch.object(workflow,'source_status',return_value=source), \
             patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_CYCLE_SOURCE')
            self.assertEqual(packet['nextSource']['slot'],'SE/walk/3')
            self.assertIn('--direction SE',packet['commands']['prepareCycleReview'])
            self.assertFalse(packet['reviewedDelivery'])

    def test_complete_non_e_cycle_review_precedes_new_direction(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
            self.assertEqual(packet['nextSource']['direction'],'SE')

    def test_unreviewed_pilot_precedes_complete_non_e_cycle(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        pilot={'slot':'E/walk/5','path':'art/fixture/E_walk_5_master.png','state':'needs_review'}
        source['slots'].append(pilot);source['next']=pilot
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextSource']['slot'],'E/walk/5')
            self.assertNotEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')

    def test_non_art_cycle_rejection_does_not_request_new_source(self):
        source,cycles,rejection=self.pending_cycle_fixture()
        rejection['rejectionScope']='timing'
        with patch.object(workflow,'source_status',return_value=source), \
             patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
            self.assertNotIn('slot',packet['nextSource'])
            self.assertEqual(packet['nextSource']['rejectionScope'],'timing')

    def test_direct_source_repair_still_precedes_cycle_review(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        source['slots'][-1]['state']='repair'
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_SOURCE')
            self.assertEqual(packet['nextSource']['slot'],'S/walk/0')

    def test_pose_guide_and_request_change_invalidate_handoff(self):
        guide=self.lab/'reference/guide.png';guide.parent.mkdir(parents=True);guide.write_bytes(b'technical pose guide fixture')
        save(self.lab/'art/fixture/requests.json',[{'poseGuide':'reference/guide.png'}])
        self.packet();guide.write_bytes(b'changed guide fixture')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

if __name__ == '__main__':
    unittest.main()

```

## FILE: .agents/skills/sable-character-studio/references/reuse-improvements.md
SHA256: 0cda9e925a076703caa945dae8cf2e389c89074c244ae84b39414501839a0fa6
```text
# Executable reuse and Luna handoff

Use the current Motion Studio. This procedure incorporates tested ROOK R3
mechanics without treating its failed high-resolution art or performance as an
approved production recipe. It does not start a model, generation or deployment.

## Resume from actual files

Run from `motion_lab_v1`, using the installed Python below as read-only input.
Create a task-local folder below `qa/`, set TEMP/TMP there, and set
`PYTHONDONTWRITEBYTECODE=1`. No source-art API is called by these commands.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py handoff --character rook
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py verify-handoff --packet 'ACTUAL_PRINTED_PACKET_PATH'
```

Replace `rook` with the requested existing character, and the packet argument
with the real first command's output. Do not execute the placeholder literally.
The output names a precise failed/review/missing slot, reference, recipe and
existing commands. A packet with `READY_TO_RESUME` is NOT ready for delivery.
Changed source bytes, a newly supplied missing slot, overrides, review evidence,
runtime code or skill instructions invalidate it. Regenerate it after changes.
The harness prioritizes actual `repair` verdicts before producing other views.
This includes cycle-only source rejections outside E: `REPAIR_REPORTED_CYCLE_SOURCE`
names the failed slot even if its isolated source review was approved. After
replacement, finish/review that complete cycle before filling another direction.
Timing/preview/annotation rejections request cycle work, not new source art.
It now prioritizes a runtime visual rejection even when individual source
slots are approved. Use [the enforced cycle gate](cycle-review.md); exact-byte
handoffs and R3 packing checks never substitute for that cycle approval.

For a genuinely new character, use `new_character.py` with the actual user's
reference first. Its copied camera/gameplay defaults are scaffolding: inspect
the character's real weapon, magazine, cadence and movement units before
integration. In particular ROOK's art scaffold is not its 10-round/.42s/1.38s
game scattergun. The packet flags this known unresolved gap; it does not silently
adjust production Actor values. Never convert another character's pixels into
the new one to make an incomplete source set build.

## Tested mechanics and where they belong

| Mechanic | Reuse location | Boundary |
|---|---|---|
| Shared mouse/key aim and same whole-body movement/fire phase | `public/keyboard-input.js`, `combat-aim.js`, `simulation.js`, `atlas-renderer.js` | Default new-character route; retain existing tests |
| Exact deduplication with explicit cell rectangles and timing aliases | `compact_atlas.py` | Existing vertical RGBA FastRuntime descriptor imports only; not a replacement authored-frame compiler |
| Selected cell committed before synchronous fire; preserved stationary recoil | R3 `pilot_runtime.gd` | Isolated Godot FastRuntime reference; not a browser script or a production-approved replacement |
| Single resident page per direction; candidate chosen before initial load | R3 loader/test scene | Never load old and new textures together in comparison |
| Exclusive bounded batch, code hashes, same scene population | R3 `run_pilot.py` | Capture and benchmark must not overlap; keep all declared repetitions |
| Exact-green normalization with raw-source/tool binding | `normalize_imagegen_chroma.py` + `intake_derived_frame.py` | Deterministic backdrop derivative only; never a new ImageGen claim or anatomy repair |

The frozen R3 runtime uses its original descriptor timing and art. No new
character should copy its ROOK path constants. For a real FastRuntime migration,
make a separate candidate, adapt its exact descriptor/manifest path and rerun
actual runtime/temporal/performance evidence. Do not relabel the old receipt.

Verify the reference before relying on its claims:

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B character_workflow.py verify-improvements
```

This independently compares all 272 stored timing cells with the current
original RGBA, verifies pinned evidence/code hashes, and recalculates the
declared 10/11/12 performance repeats. Expected historical result:
`VERIFIED_LIMITED_REUSE`, controller 216/216, temporal 32/32,
**performance FAIL, sourceVisualStatus HOLD, productionPromotion false**.
That successful verification means the limitations were preserved, not waived.
Missing/stale evidence fails closed; never regenerate retired assets just to
make an old reference path exist.

## Optional lossless atlas import

The new project adapter has no provider dependency and never alters its input.
It preserves decoded RGBA including RGB under alpha=0, frame order, durations,
display offsets/scale and muzzle metadata. Verification reads both original
and packed cells; it does not trust an old `checks: PASS` label.

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B compact_atlas.py pack --descriptor '../data/character_pipeline/rook_runtime.json' --output 'qa/atlas_candidates/ACTUAL_NEW_CANDIDATE_NAME'
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B compact_atlas.py verify --manifest 'ACTUAL_PRINTED_MANIFEST_PATH'
```

Use a fresh named candidate path, not the literal placeholder. No automatic
overwrite, cleanup, production pointer change or deployment occurs. The input
must be an existing regular descriptor-sized vertical sheet, not a failed
generated row that is being disguised by equal slicing. Missing/invalid alpha,
rectangles, original hashes, order and timing are errors. Memory estimates are
not GPU measurements. Packing fewer unique cells does not shorten the loop.

## Art and delivery constraints still apply

- Inspect native alpha channels and light/dark edges; painted checkerboard is
  not transparency. Preserve the failed source, then use a separately keyed
  green fallback when needed. Read ImageGen/identity instructions when doing
  actual art work; these harness utilities do not grant a provider switch.
- Trace each leg from hip to boot with that character's own asymmetric markers.
  Guide colors are not clothing. A neutral guide only avoids color copying;
  it does not prove the opposite support or correct foot contact.
- Inspect the compiled chronological cycle as well as isolated originals.
  Different source framing can change body/weapon proportions after normalizing.
  Keep a valid half of a pair via the existing `intake_pair.py --side` mechanism;
  do not approve the failed half with it.
- Distinguish 8x8 dispatch from authored strafe, speed-up walk from authored
  sprint, and ammo/reload logic from reload-hand art. Stationary recoil should
  preserve verified planted feet; do not discard a valid recoil clip merely
  to force an idle frame.
- Follow `authoring.md` and `browser-check.md` for build and delivery. Full
  strides, native 1080p video, selected-renderer evidence and actual visual
  observations remain mandatory. Static/technical tests cannot approve gait.

## Regression commands

```powershell
& 'C:/AI_ENVS/pair_pipeline_env/Scripts/python.exe' -B -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.js
```

The new tests exercise corrupt pixels, timing/order changes, missing repeats,
non-finite performance values, stale/tampered handoffs and known-repair priority.
They are local technical fixtures, not a Luna character-generation run. Do not
claim Luna end-to-end success without that separately authorized actual run.

```

## FILE: .agents/skills/sable-character-studio/references/enemy-facing.md
SHA256: 0c5107d049e3e243317c086d8e1d8eed59331ddebeaecbef5fc2404a4d7ec480
```text
# SITE-7 enemy facing: visible front, emitter and warning

Use for the current `site7_machine_sprite.gd` and enemy combat integration.
The 2026-09-13 user screenshot exposed a front-facing drone illustration being
reused while firing toward the opposite side. An omni **emitter** does not make
the whole vehicle's visible front omnidirectional. Do not repeat that shortcut.

- Flying drones use eight separately authored yaw views (`authored_yaw8`),
  exact texture hashes and per-view root/emitter coordinates. The runtime
  rejects missing views and repeated file OR visible-RGBA hashes before publishing
  the node. Metadata and RGB hidden under alpha=0 do not create new views.
  Hash uniqueness cannot judge whether the paintings show the correct angles.
- Use the ImageGen appearance authority; do not roll a 2D three-quarter picture
  around the screen or mirror asymmetric sensors to manufacture all views.
  Inspect front versus rear surfaces, appendage count, native alpha and the
  original-scale visible emitter. The separate three-sensor cluster is not the
  lower magenta firing orb. Preserve rejected four-thruster/mirrored-lens art.
- `resolve_target` selects an authored pose and solves that pose's actual
  emitter ray together. It evaluates candidates without committing eight
  texture changes per tick. The initial frame uses the actor's current aim.
  Movement velocity may oppose aim; orbiting does not turn the gun away.
- A nearest-angle result is not automatically valid: targets inside all gun
  offsets can leave every candidate pointing backward. `Vector2.INF` is an
  explicit invalid aim, not a shot direction. Keep the prior pose and reposition;
  do not enter WINDUP, fire a zero/non-finite ray, or invent a forward target.
- At WINDUP entry, stop/bank first and freeze pose plus aim. WINDUP/BURST/LUNGE
  must not resolve a fresh target or home the advertised attack. Recovery may
  respond to the new target immediately. This is intentionally different from
  the player's latest-pointer-input behavior.
- `_enter` invalidates the Tactics CanvasItem's own cached draw commands.
  Stagger skips `step`, so redrawing only EnemyActor leaves the old warning line.
  Check the native before/after warning pixels while stagger is still active.
- Legacy mock rifle/pistol/arm pixels already rotate around their bones to
  world aim. Applying `flip_h` to them again reverses the barrel. Keep those
  pixels unflipped while that mock remains; it is not an eight-view humanoid
  appearance solution and must not replace the pending authored biped cycle.
- Anchored machines retain their own stationary emitter/root contract. Do not
  force humanoid footsteps or a yawing chassis onto the stationary boss.

Current executable checks: `tests/smoke/site7_enemy_facing_smoke.gd` exercises
8 target directions at 30/60/120Hz, opposite movement, first-frame facing,
locked warnings, real projectile creation and opposite-target recovery. It also
rejects incomplete/duplicate views and checks actual mock barrel transforms.
`site7_machine_source_smoke.gd` checks actual image binding, transformed muzzle,
hit bounds, anchor stability and death presentation. Count actual projectile
objects/emission events, not all root children (audio is a separate child).

`tests/render/site7_machine_edge_case_smoke.gd` checks the R6 close-target,
metadata-only/hidden-RGB duplicate and interrupted-warning regressions. Run it
with actual rendering, not headless: the warning check reads native viewport
pixels as well as the Tactics draw signal. Synthetic PNGs are test-only.

Run native 1920x1080 captures in the real game scene and inspect all affected
view transitions. A test PASS or source contact sheet is not runtime visual
approval. `prepare_drone_directions.py` only produces isolated candidates/specs;
the app registry must not point at an unreviewed QA candidate automatically.
Keep player art, gait, 1.8x display scale and weapon timing unchanged.

## Current local app connection

The reviewed drone is now bound by `data/art_profiles/enemy_profiles.json`
to `assets/enemies/recon_drone/authored_yaw8_v1/spec.json`, with byte-identical
copies of the selected images. The app loader validates identity/spec hash and
each texture before hiding the existing visual. A failed candidate does not
erase the current visible node. Repeated configure and wrong-role intake fail.

Run `tests/smoke/site7_drone_app_smoke.gd` without disabling app intake. Unlike
the candidate smokes, it starts the normal registry path and advances actual
WINDUP-to-emission transitions at 30/60/120Hz. Capture the app path using
`tests/render/site7_enemy_facing_capture.gd -- --app-registry`. Retain the
candidate-only tests too; they still cover deliberately invalid input.

GPT 6 Pro round 7 closed the three R6 counterexamples by code/test comparison
and its own synthetic pixel/math checks. It did not run Godot, inspect the
drone art or certify this registry connection. Keep those scopes separate.

The fixed boss is also connected through the registry, at
`assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json`. Its central
iris emits; the four arm housings do not acquire independent yaw. Keep the
body/root stationary. `site7_anchor_app_smoke.gd` exercises normal app loading
and actual locked emissions. `site7_anchor_candidate_capture.gd -- --app-registry`
captures all three phases through real Tactics time advancement, with explicitly
controlled HP/attack serial fixtures; this is not a whole-operation playthrough.

For anchored-boss captures, frame the real `home_position`: the boss anchor
component restores it after an attempted fixture relocation. Require the
visible iris on-screen, not merely a decoded 1080p screenshot. The first
offscreen capture is retained as VISUAL_HOLD. Machine overhead bars use the
full transformed artwork corners, not inset damage bounds; the pylon otherwise
overlaps its health bar. `site7_machine_source_smoke.gd` covers these corners
under scaled/rotated transforms. Do not change damage bounds to fix a UI overlap.

Round8 capture regressions use `tests/render/site7_anchor_capture_smoke.gd`:
reject hidden artwork even with an on-screen iris; collect only this actor's
actual warning objects (phase2: one circle; phase3: one circle and four lanes).
Capture elapsed/windup/fired during the visible warning and impact window and
record real in-zone damage. Zero projectiles plus RECOVER does not prove a
ground attack happened. Do not label fixed-delay after-effects as a visible hit.
App-mode capture must not read a QA candidate spec; bind the normal registry's
actual spec hash. Candidate mode still explicitly rejects missing/malformed
JSON. The test-only no-warning subclass must never enter a runtime registry.
Visibility/geometry/clock checks do not replace observing the native pictures.

```

## FILE: qa/stage1_implementation_20260913/anchor_capture_edges_1789292477_647/report.json
SHA256: 4230c6113af76c227770900a6775fd8c4e2e87605b48754cd99a0ba3724af74c
```text
{
  "checks": 52,
  "failures": [],
  "hashes": {
    "data/art_profiles/enemy_profiles.json": "549ca45d47ec39ea740776c9eccfd52323a00775da0a29b38e969baf4ec951a3",
    "qa/stage1_implementation_20260913/r8_fixtures/malformed_spec.json": "b8694d125b7538e56df8a71d0c37e9288493a73c6ae6fa8cb0d80ed6b5216ff2",
    "qa/stage1_implementation_20260913/r8_fixtures/no_warning_tactics.gd": "68a6711fd27459998a19e72b80552ffe1d5485136b83fbb8927067f7e75ac96b",
    "scripts/combat/site7_attack_warning.gd": "a2b237db6016c2dd85ed0c346784723ae53a0bbd1cd81a463291df267a3b4f39",
    "scripts/combat/site7_enemy_tactics.gd": "efacd6facda231852c947cb26572cc873ed022d62bb5ddf1ef55b2c8b260bd02",
    "tests/render/site7_anchor_candidate_capture.gd": "76cea8625513abd8ecfa551831854256888042fbe6e36af76aa5109688a25095",
    "tests/render/site7_anchor_capture_smoke.gd": "7ba9b8a3c42fc7b83ac199e73075425ddb8e82b77d5a77ec53bd5d69f7ab8b5d"
  },
  "native": [
    1920,
    1080
  ],
  "observed": [
    {
      "before": [
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52546242232,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ],
      "health_after": 76.0,
      "health_before": 96.0,
      "hz": 30,
      "impact": [
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52546242232,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ],
      "phase": 2
    },
    {
      "before": [
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52563019448,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52579796665,
          "kind": "lane",
          "position": "(860.465, 890.3676)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52596573882,
          "kind": "lane",
          "position": "(969.6324, 800.465)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52613351099,
          "kind": "lane",
          "position": "(1059.535, 909.6324)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52630128316,
          "kind": "lane",
          "position": "(950.3676, 999.535)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ],
      "health_after": 56.0,
      "health_before": 96.0,
      "hz": 30,
      "impact": [
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52563019448,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52579796665,
          "kind": "lane",
          "position": "(860.465, 890.3676)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52596573882,
          "kind": "lane",
          "position": "(969.6324, 800.465)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52613351099,
          "kind": "lane",
          "position": "(1059.535, 909.6324)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52630128316,
          "kind": "lane",
          "position": "(950.3676, 999.535)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ],
      "phase": 3
    },
    {
      "before": [
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52646905532,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ],
      "health_after": 76.0,
      "health_before": 96.0,
      "hz": 60,
      "impact": [
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52646905532,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ],
      "phase": 2
    },
    {
      "before": [
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52663682748,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52680459963,
          "kind": "lane",
          "position": "(860.465, 890.3676)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52697237178,
          "kind": "lane",
          "position": "(969.6324, 800.465)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52714014393,
          "kind": "lane",
          "position": "(1059.535, 909.6324)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52730791608,
          "kind": "lane",
          "position": "(950.3676, 999.535)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ],
      "health_after": 56.0,
      "health_before": 96.0,
      "hz": 60,
      "impact": [
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52663682748,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52680459963,
          "kind": "lane",
          "position": "(860.465, 890.3676)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52697237178,
          "kind": "lane",
          "position": "(969.6324, 800.465)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52714014393,
          "kind": "lane",
          "position": "(1059.535, 909.6324)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666667,
          "fired": true,
          "id": 52730791608,
          "kind": "lane",
          "position": "(950.3676, 999.535)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ],
      "phase": 3
    },
    {
      "before": [
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52747568824,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ],
      "health_after": 76.0,
      "health_before": 96.0,
      "hz": 120,
      "impact": [
        {
          "elapsed": 1.36666666666666,
          "fired": true,
          "id": 52747568824,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ],
      "phase": 2
    },
    {
      "before": [
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52764346040,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52781123257,
          "kind": "lane",
          "position": "(860.465, 890.3676)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52797900474,
          "kind": "lane",
          "position": "(969.6324, 800.465)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52814677691,
          "kind": "lane",
          "position": "(1059.535, 909.6324)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0,
          "fired": false,
          "id": 52831454908,
          "kind": "lane",
          "position": "(950.3676, 999.535)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ],
      "health_after": 56.0,
      "health_before": 96.0,
      "hz": 120,
      "impact": [
        {
          "elapsed": 1.36666666666666,
          "fired": true,
          "id": 52764346040,
          "kind": "circle",
          "position": "(650.0, 870.0)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 1.36666666666666,
          "fired": true,
          "id": 52781123257,
          "kind": "lane",
          "position": "(860.465, 890.3676)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666666,
          "fired": true,
          "id": 52797900474,
          "kind": "lane",
          "position": "(969.6324, 800.465)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666666,
          "fired": true,
          "id": 52814677691,
          "kind": "lane",
          "position": "(1059.535, 909.6324)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.36666666666666,
          "fired": true,
          "id": 52831454908,
          "kind": "lane",
          "position": "(950.3676, 999.535)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ],
      "phase": 3
    }
  ],
  "status": "PASS",
  "visual_art_approval": false
}
```

## FILE: qa/stage1_implementation_20260913/anchor_native_1789292550_916/capture_report.json
SHA256: 0a3fddda4677d2cf3e04fd11d1b9dbb649862e8918d4e8aef7c3ed95c6e4d2f5
```text
{
  "app_registry": true,
  "candidate_input_read": false,
  "candidate_path_argument": "res://qa/stage1_implementation_20260913/r8_fixtures/does_not_exist.json",
  "failures": [],
  "hashes": {
    "res://assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json": "c3f98d11fc537fd5e7d542e7114296cdc0c12b7f2f4877e71c1bd6fed194b763",
    "res://data/art_profiles/enemy_profiles.json": "549ca45d47ec39ea740776c9eccfd52323a00775da0a29b38e969baf4ec951a3",
    "res://scripts/actors/enemy_actor.gd": "6960d7b99d0df3098399645cb389e4ed4fee4ae51397af8ebeb81560cf0e7b95",
    "res://scripts/animation/site7_machine_sprite.gd": "986d9b4f34c33ee9c07d4737c286bad32c0acd84b78361e4b7f7a7fbcdc338c8",
    "res://scripts/combat/site7_attack_warning.gd": "a2b237db6016c2dd85ed0c346784723ae53a0bbd1cd81a463291df267a3b4f39",
    "res://scripts/combat/site7_enemy_tactics.gd": "efacd6facda231852c947cb26572cc873ed022d62bb5ddf1ef55b2c8b260bd02",
    "res://scripts/ui/enemy_overhead_ui.gd": "ba2c0d4062fa454663f009f51ed53d5bd3d34239eec83c673d600d94f18d310a",
    "res://tests/render/site7_anchor_candidate_capture.gd": "76cea8625513abd8ecfa551831854256888042fbe6e36af76aa5109688a25095"
  },
  "phase_health_and_serial_fixtures": true,
  "rows": [
    {
      "emissions": [],
      "health_fixture": 589.0,
      "iris_canvas": "(774.1413, 378.5665)",
      "label": "phase1_attack1_windup_start",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase1_attack1_windup_start.webp",
      "physics_tick": 31,
      "sha256": "0e8f73dd13afb309af3ed19e070d916ab5ca49bb2555acdae681119e04f3b58b",
      "tactics": {
        "attacks": 0,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 1,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.95
      },
      "wall_ms": 5337,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 546.0,
      "iris_canvas": "(774.1413, 378.5665)",
      "label": "phase1_attack1_windup_mid",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase1_attack1_windup_mid.webp",
      "physics_tick": 67,
      "sha256": "d04f6bbd03e3c4ac8fe2708091330f375c517de94ad55a883858c74b9493e0ad",
      "tactics": {
        "attacks": 0,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 1,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.466666666666665
      },
      "wall_ms": 6032,
      "warnings": []
    },
    {
      "emissions": [
        {
          "actor_id": 77611403053,
          "attack_serial": 1,
          "direction": [
            -0.935166716575623,
            0.354207783937454
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 0,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 78953580225,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 102,
          "projectile_id": 83684755020
        },
        {
          "actor_id": 77611403053,
          "attack_serial": 1,
          "direction": [
            -0.989925444126129,
            0.141589388251305
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 1,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 78953580225,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 102,
          "projectile_id": 83785418335
        },
        {
          "actor_id": 77611403053,
          "attack_serial": 1,
          "direction": [
            -0.996964693069458,
            -0.077854335308075
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 2,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 78953580225,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 102,
          "projectile_id": 83886081764
        }
      ],
      "health_fixture": 546.0,
      "iris_canvas": "(774.1413, 378.5665)",
      "label": "phase1_attack1_attack",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase1_attack1_attack.webp",
      "physics_tick": 104,
      "sha256": "966c8c342061ba64a1c2c2cd4400dcd2c9531ae24dd44d709a821672726a2e31",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 1,
        "role": "boss",
        "shots": 3,
        "state": "RECOVER",
        "state_left": 1.6
      },
      "wall_ms": 6759,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 589.0,
      "iris_canvas": "(781.7888, 379.625)",
      "label": "phase1_attack2_windup_start",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase1_attack2_windup_start.webp",
      "physics_tick": 139,
      "sha256": "4b169791c55b756d5c7f00c63a9374189970344634783a97a15c0a64644390d6",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 1,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.95
      },
      "wall_ms": 9532,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 546.0,
      "iris_canvas": "(781.7888, 379.625)",
      "label": "phase1_attack2_windup_mid",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase1_attack2_windup_mid.webp",
      "physics_tick": 176,
      "sha256": "b9ed99faef059b51628b71ed2be10b467924cee95a5f3bffa351ee1e1de562c5",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 1,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.466666666666665
      },
      "wall_ms": 10252,
      "warnings": []
    },
    {
      "emissions": [
        {
          "actor_id": 113816634973,
          "attack_serial": 2,
          "direction": [
            -0.935166716575623,
            0.354207783937454
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 0,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 115125258450,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 211,
          "projectile_id": 119856433316
        },
        {
          "actor_id": 113816634973,
          "attack_serial": 2,
          "direction": [
            -0.989925444126129,
            0.141589388251305
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 1,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 115125258450,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 211,
          "projectile_id": 119957095988
        },
        {
          "actor_id": 113816634973,
          "attack_serial": 2,
          "direction": [
            -0.996964693069458,
            -0.077854335308075
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 2,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 115125258450,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 211,
          "projectile_id": 120057759930
        }
      ],
      "health_fixture": 546.0,
      "iris_canvas": "(781.7888, 379.625)",
      "label": "phase1_attack2_attack",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase1_attack2_attack.webp",
      "physics_tick": 212,
      "sha256": "b5cee442c74f2977efcc2a328fff692b0ce9a4d4f76c558c6ea1cd113fc96ae4",
      "tactics": {
        "attacks": 2,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 1,
        "role": "boss",
        "shots": 3,
        "state": "RECOVER",
        "state_left": 1.6
      },
      "wall_ms": 10955,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 310.0,
      "iris_canvas": "(783.9917, 379.9299)",
      "label": "phase2_attack1_windup_start",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack1_windup_start.webp",
      "physics_tick": 242,
      "sha256": "6cad389d30376b9ffaec59ad5dc41d4ca5f97b161789c2dcb61210995958e5fb",
      "tactics": {
        "attacks": 0,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.95
      },
      "wall_ms": 13539,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 267.0,
      "iris_canvas": "(783.9917, 379.9299)",
      "label": "phase2_attack1_windup_mid",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack1_windup_mid.webp",
      "physics_tick": 278,
      "sha256": "c24f7cacbd8188793eec5f09d2589eec54f60bcc6f1d049ee390fc7eb0b8d8fd",
      "tactics": {
        "attacks": 0,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.466666666666665
      },
      "wall_ms": 14227,
      "warnings": []
    },
    {
      "emissions": [
        {
          "actor_id": 149988312627,
          "attack_serial": 1,
          "direction": [
            -0.835328161716461,
            0.54975152015686
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 0,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 151296936078,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 312,
          "projectile_id": 156028110826
        },
        {
          "actor_id": 149988312627,
          "attack_serial": 1,
          "direction": [
            -0.935166716575623,
            0.354207783937454
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 1,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 151296936078,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 312,
          "projectile_id": 156128773664
        },
        {
          "actor_id": 149988312627,
          "attack_serial": 1,
          "direction": [
            -0.989925444126129,
            0.141589388251305
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 2,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 151296936078,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 312,
          "projectile_id": 156229437780
        },
        {
          "actor_id": 149988312627,
          "attack_serial": 1,
          "direction": [
            -0.996964693069458,
            -0.077854335308075
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 3,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 151296936078,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 312,
          "projectile_id": 156330100693
        },
        {
          "actor_id": 149988312627,
          "attack_serial": 1,
          "direction": [
            -0.955945193767548,
            -0.293545097112656
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 4,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 151296936078,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 312,
          "projectile_id": 156430763555
        }
      ],
      "health_fixture": 267.0,
      "iris_canvas": "(783.9917, 379.9299)",
      "label": "phase2_attack1_attack",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack1_attack.webp",
      "physics_tick": 313,
      "sha256": "debff38010a785d6904415f6ceb12a32d3b2cc4026de1074562d39596a3d29ba",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 5,
        "state": "RECOVER",
        "state_left": 1.4
      },
      "wall_ms": 14926,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 310.0,
      "iris_canvas": "(783.3402, 379.8398)",
      "label": "phase2_attack2_windup_start",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack2_windup_start.webp",
      "physics_tick": 342,
      "sha256": "fcdc307fef679fc991212f0a9e8b713addf4848e7528abed742d16f33bfa2ae8",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.95
      },
      "wall_ms": 17462,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 267.0,
      "iris_canvas": "(783.3402, 379.8398)",
      "label": "phase2_attack2_windup_mid",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack2_windup_mid.webp",
      "physics_tick": 378,
      "sha256": "dec77ce092cb185b9fdba61c1cb8ffaa4ebb2c8ba31ceabafc1af09d6a99e87c",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.466666666666665
      },
      "wall_ms": 18156,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 267.0,
      "iris_canvas": "(783.3402, 379.8398)",
      "label": "phase2_attack2_attack",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack2_attack.webp",
      "physics_tick": 413,
      "sha256": "e60b411db8f643bb982adee0f2dd0dc0099ea4deff2c3df1e86d8a5602a0b216",
      "tactics": {
        "attacks": 2,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 0,
        "state": "RECOVER",
        "state_left": 1.4
      },
      "wall_ms": 18842,
      "warnings": [
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 192317228906,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ]
    },
    {
      "emissions": [],
      "health_fixture": 267.0,
      "iris_canvas": "(783.3402, 379.8398)",
      "label": "phase2_attack2_ground_warning",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack2_ground_warning.webp",
      "physics_tick": 421,
      "sha256": "fdab8ec437580fd7da4603e6147567341d166a972b5c217b39270d7d11dac23c",
      "tactics": {
        "attacks": 2,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 0,
        "state": "RECOVER",
        "state_left": 1.4
      },
      "wall_ms": 19095,
      "warnings": [
        {
          "elapsed": 0.15,
          "fired": false,
          "id": 192317228906,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ]
    },
    {
      "emissions": [],
      "health_fixture": 267.0,
      "iris_canvas": "(783.3402, 379.8398)",
      "label": "phase2_attack2_ground_impact",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase2_attack2_ground_impact.webp",
      "physics_tick": 481,
      "sha256": "0d2101c5968f1a3082df38508a71070e404b56c2b70008d6cb9f83cc950e9c1e",
      "tactics": {
        "attacks": 2,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 2,
        "role": "boss",
        "shots": 0,
        "state": "RECOVER",
        "state_left": 1.4
      },
      "wall_ms": 20187,
      "warnings": [
        {
          "elapsed": 1.15,
          "fired": true,
          "id": 192317228906,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ]
    },
    {
      "emissions": [],
      "health_fixture": 155.0,
      "iris_canvas": "(785.6941, 380.1656)",
      "label": "phase3_attack1_windup_start",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack1_windup_start.webp",
      "physics_tick": 509,
      "sha256": "b501acb9d4fa6c5be10634297bca03f32a93c8a04f678c4200892c703c35087e",
      "tactics": {
        "attacks": 0,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.95
      },
      "wall_ms": 22766,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 155.0,
      "iris_canvas": "(785.6941, 380.1656)",
      "label": "phase3_attack1_windup_mid",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack1_windup_mid.webp",
      "physics_tick": 546,
      "sha256": "e2fd7d3b4029898c5ba22e412596e466ccc2ecc34ff9212588f45c471be48ffa",
      "tactics": {
        "attacks": 0,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.466666666666665
      },
      "wall_ms": 23484,
      "warnings": []
    },
    {
      "emissions": [
        {
          "actor_id": 225150240971,
          "attack_serial": 1,
          "direction": [
            -0.835328161716461,
            0.54975152015686
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 0,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 226458863311,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 581,
          "projectile_id": 230586058513
        },
        {
          "actor_id": 225150240971,
          "attack_serial": 1,
          "direction": [
            -0.935166716575623,
            0.354207783937454
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 1,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 226458863311,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 581,
          "projectile_id": 230686721682
        },
        {
          "actor_id": 225150240971,
          "attack_serial": 1,
          "direction": [
            -0.989925444126129,
            0.141589388251305
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 2,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 226458863311,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 581,
          "projectile_id": 230787385645
        },
        {
          "actor_id": 225150240971,
          "attack_serial": 1,
          "direction": [
            -0.996964693069458,
            -0.077854335308075
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 3,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 226458863311,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 581,
          "projectile_id": 230888048328
        },
        {
          "actor_id": 225150240971,
          "attack_serial": 1,
          "direction": [
            -0.955945193767548,
            -0.293545097112656
          ],
          "enemy_id": "BOSS_SITE7_ANCHOR_01",
          "ordinal": 4,
          "origin": [
            2128.13305664063,
            334.254333496094
          ],
          "owner_id": 226458863311,
          "owner_path": "/root/StoryStage01/EnemyActor/Tactics",
          "physics_tick": 581,
          "projectile_id": 230988711967
        }
      ],
      "health_fixture": 155.0,
      "iris_canvas": "(785.6941, 380.1656)",
      "label": "phase3_attack1_attack",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack1_attack.webp",
      "physics_tick": 583,
      "sha256": "2d8aad652236bd4edd6ab093e33d3d0f6a08d00bd20e7e8bd762aadc8dd281a0",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 5,
        "state": "RECOVER",
        "state_left": 1.2
      },
      "wall_ms": 24199,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 155.0,
      "iris_canvas": "(784.3153, 379.9747)",
      "label": "phase3_attack2_windup_start",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack2_windup_start.webp",
      "physics_tick": 616,
      "sha256": "60459c98497129d18d773b882a7186d6d7d47fc2c0776e43fd2d59b7772d05bb",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.95
      },
      "wall_ms": 26723,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 155.0,
      "iris_canvas": "(784.3153, 379.9747)",
      "label": "phase3_attack2_windup_mid",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack2_windup_mid.webp",
      "physics_tick": 652,
      "sha256": "7648349cbc6a72893f09856b97be5c64ab5eb7dfbbcd9badb682ad5813b13f53",
      "tactics": {
        "attacks": 1,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 0,
        "state": "WINDUP",
        "state_left": 0.466666666666665
      },
      "wall_ms": 27406,
      "warnings": []
    },
    {
      "emissions": [],
      "health_fixture": 155.0,
      "iris_canvas": "(784.3153, 379.9747)",
      "label": "phase3_attack2_attack",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack2_attack.webp",
      "physics_tick": 687,
      "sha256": "ef3ae646995f7a5d6d28d043e088c4fbc38fbfea032894e922a240c3edd46569",
      "tactics": {
        "attacks": 2,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 0,
        "state": "RECOVER",
        "state_left": 1.2
      },
      "wall_ms": 28091,
      "warnings": [
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266271196741,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266287974591,
          "kind": "lane",
          "position": "(2023.185, 458.6476)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266304751731,
          "kind": "lane",
          "position": "(2132.352, 368.745)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266321529024,
          "kind": "lane",
          "position": "(2222.255, 477.9124)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266338306122,
          "kind": "lane",
          "position": "(2113.088, 567.815)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ]
    },
    {
      "emissions": [],
      "health_fixture": 155.0,
      "iris_canvas": "(784.3153, 379.9747)",
      "label": "phase3_attack2_ground_warning",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack2_ground_warning.webp",
      "physics_tick": 695,
      "sha256": "cc5ef0793a261f021573d73a72ea7253851c9b385f53ae8a7b5687995a08cf31",
      "tactics": {
        "attacks": 2,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 0,
        "state": "RECOVER",
        "state_left": 1.2
      },
      "wall_ms": 28353,
      "warnings": [
        {
          "elapsed": 0.15,
          "fired": false,
          "id": 266271196741,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 0.15,
          "fired": false,
          "id": 266287974591,
          "kind": "lane",
          "position": "(2023.185, 458.6476)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.15,
          "fired": false,
          "id": 266304751731,
          "kind": "lane",
          "position": "(2132.352, 368.745)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.15,
          "fired": false,
          "id": 266321529024,
          "kind": "lane",
          "position": "(2222.255, 477.9124)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.15,
          "fired": false,
          "id": 266338306122,
          "kind": "lane",
          "position": "(2113.088, 567.815)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ]
    },
    {
      "emissions": [],
      "health_fixture": 155.0,
      "iris_canvas": "(784.3153, 379.9747)",
      "label": "phase3_attack2_ground_impact",
      "machine": {
        "art_warp": false,
        "configured": true,
        "display_height": 270.0,
        "emitter_px": "(638.0, 616.0)",
        "emitter_visible": true,
        "emitter_world": "(2128.133, 334.2543)",
        "facing": "ANCHORED",
        "gait_claim": false,
        "heading_world": "(0.0, 0.0)",
        "kind": "anchored_machine",
        "mirrored": false,
        "native_size": "(1227.0, 1247.0)",
        "texture_sha256": "c47ca7b363a07548e0316b84ce331643f8ff3bd79ce725db74878890ce95b4f4",
        "view_count": 1
      },
      "native": [
        1920,
        1080
      ],
      "path": "res://qa/stage1_implementation_20260913/anchor_native_1789292550_916/phase3_attack2_ground_impact.webp",
      "physics_tick": 767,
      "sha256": "75b72221bd23ab7a25c06d343efa307610b5c0bdbe4a2207174e7957bb0e4e87",
      "tactics": {
        "attacks": 2,
        "contract_is_intent_not_validation": true,
        "locked_aim": "(-0.989925, 0.141589)",
        "lunge_radius": 58.0,
        "lunge_reach": 151.2,
        "lunges": 0,
        "phase": 3,
        "role": "boss",
        "shots": 0,
        "state": "RECOVER",
        "state_left": 1.2
      },
      "wall_ms": 29650,
      "warnings": [
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266271196741,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266287974591,
          "kind": "lane",
          "position": "(2023.185, 458.6476)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266304751731,
          "kind": "lane",
          "position": "(2132.352, 368.745)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266321529024,
          "kind": "lane",
          "position": "(2222.255, 477.9124)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266338306122,
          "kind": "lane",
          "position": "(2113.088, 567.815)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ]
    }
  ],
  "status": "CAPTURED_CONTROLLED_PHASES_NOT_VISUAL_APPROVAL",
  "warning_evidence": [
    {
      "before": [
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 192317228906,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ],
      "case": "phase2_attack2",
      "health_after": 76.0,
      "health_before": 96.0,
      "impact": [
        {
          "elapsed": 1.15,
          "fired": true,
          "id": 192317228906,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        }
      ]
    },
    {
      "before": [
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266271196741,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266287974591,
          "kind": "lane",
          "position": "(2023.185, 458.6476)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266304751731,
          "kind": "lane",
          "position": "(2132.352, 368.745)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266321529024,
          "kind": "lane",
          "position": "(2222.255, 477.9124)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 0.0166666666666667,
          "fired": false,
          "id": 266338306122,
          "kind": "lane",
          "position": "(2113.088, 567.815)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ],
      "case": "phase3_attack2",
      "health_after": 56.0,
      "health_before": 96.0,
      "impact": [
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266271196741,
          "kind": "circle",
          "position": "(1812.72, 438.28)",
          "ray": "(1.0, 0.0)",
          "visible": true,
          "windup": 1.15
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266287974591,
          "kind": "lane",
          "position": "(2023.185, 458.6476)",
          "ray": "(-0.99535, -0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266304751731,
          "kind": "lane",
          "position": "(2132.352, 368.745)",
          "ray": "(0.096324, -0.99535)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266321529024,
          "kind": "lane",
          "position": "(2222.255, 477.9124)",
          "ray": "(0.99535, 0.096324)",
          "visible": true,
          "windup": 1.35
        },
        {
          "elapsed": 1.35,
          "fired": true,
          "id": 266338306122,
          "kind": "lane",
          "position": "(2113.088, 567.815)",
          "ray": "(-0.096324, 0.99535)",
          "visible": true,
          "windup": 1.35
        }
      ]
    }
  ]
}
```

## FILE: qa/stage1_implementation_20260913/r8_captures_native_1080p.json
SHA256: 63d6affd9231c85d23760c926272c384099966f8183acca7e6e928c8db3c8970
```text
{
  "schema": 1,
  "generated_at_utc": "2026-09-13T09:47:19.527438+00:00",
  "gate": "PASS",
  "container_gate": "PASS",
  "dynamic_capture_gate": "PASS",
  "dynamic_capture_required": true,
  "minimum_native_review_resolution": [
    1920,
    1080
  ],
  "scope": "review_container_resolution_and_decode_only",
  "quality_claim": false,
  "anti_upscale_note": "A PASS proves only a native-size review container. Source/master/runtime resolution and any scaling remain mandatory in the producing manifest.",
  "evidence": [
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase1_attack1_attack.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 451770,
      "sha256": "966c8c342061ba64a1c2c2cd4400dcd2c9531ae24dd44d709a821672726a2e31"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase1_attack1_windup_mid.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 454560,
      "sha256": "d04f6bbd03e3c4ac8fe2708091330f375c517de94ad55a883858c74b9493e0ad"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase1_attack1_windup_start.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 453214,
      "sha256": "0e8f73dd13afb309af3ed19e070d916ab5ca49bb2555acdae681119e04f3b58b"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase1_attack2_attack.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 444494,
      "sha256": "b5cee442c74f2977efcc2a328fff692b0ce9a4d4f76c558c6ea1cd113fc96ae4"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase1_attack2_windup_mid.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 448798,
      "sha256": "b9ed99faef059b51628b71ed2be10b467924cee95a5f3bffa351ee1e1de562c5"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase1_attack2_windup_start.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 444862,
      "sha256": "4b169791c55b756d5c7f00c63a9374189970344634783a97a15c0a64644390d6"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack1_attack.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 448386,
      "sha256": "debff38010a785d6904415f6ceb12a32d3b2cc4026de1074562d39596a3d29ba"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack1_windup_mid.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 453260,
      "sha256": "c24f7cacbd8188793eec5f09d2589eec54f60bcc6f1d049ee390fc7eb0b8d8fd"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack1_windup_start.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 450870,
      "sha256": "6cad389d30376b9ffaec59ad5dc41d4ca5f97b161789c2dcb61210995958e5fb"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack2_attack.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 452032,
      "sha256": "e60b411db8f643bb982adee0f2dd0dc0099ea4deff2c3df1e86d8a5602a0b216"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack2_ground_impact.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 454340,
      "sha256": "0d2101c5968f1a3082df38508a71070e404b56c2b70008d6cb9f83cc950e9c1e"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack2_ground_warning.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 452810,
      "sha256": "fdab8ec437580fd7da4603e6147567341d166a972b5c217b39270d7d11dac23c"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack2_windup_mid.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 453062,
      "sha256": "dec77ce092cb185b9fdba61c1cb8ffaa4ebb2c8ba31ceabafc1af09d6a99e87c"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase2_attack2_windup_start.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 450984,
      "sha256": "fcdc307fef679fc991212f0a9e8b713addf4848e7528abed742d16f33bfa2ae8"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack1_attack.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 448994,
      "sha256": "2d8aad652236bd4edd6ab093e33d3d0f6a08d00bd20e7e8bd762aadc8dd281a0"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack1_windup_mid.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 451520,
      "sha256": "e2fd7d3b4029898c5ba22e412596e466ccc2ecc34ff9212588f45c471be48ffa"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack1_windup_start.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 453902,
      "sha256": "b501acb9d4fa6c5be10634297bca03f32a93c8a04f678c4200892c703c35087e"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack2_attack.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 463046,
      "sha256": "ef3ae646995f7a5d6d28d043e088c4fbc38fbfea032894e922a240c3edd46569"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack2_ground_impact.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 462962,
      "sha256": "75b72221bd23ab7a25c06d343efa307610b5c0bdbe4a2207174e7957bb0e4e87"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack2_ground_warning.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 464406,
      "sha256": "cc5ef0793a261f021573d73a72ea7253851c9b385f53ae8a7b5687995a08cf31"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack2_windup_mid.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 448384,
      "sha256": "7648349cbc6a72893f09856b97be5c64ab5eb7dfbbcd9badb682ad5813b13f53"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_native_1789292550_916\\phase3_attack2_windup_start.webp",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGB",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 455018,
      "sha256": "60459c98497129d18d773b882a7186d6d7d47fc2c0776e43fd2d59b7772d05bb"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_capture_edges_1789292477_647\\visible.png",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGBA",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 131711,
      "sha256": "dc1bb2983406d899de8f92be90613d8856214ef56d2b8192355575839ddc42f7"
    },
    {
      "path": "D:\\AI 종합 폴더\\Games\\Sable-circuit\\qa\\stage1_implementation_20260913\\anchor_capture_edges_1789292477_647\\hidden.png",
      "error": null,
      "kind": "image",
      "evidence_class": "dynamic_or_authored_review_frame",
      "resolution": [
        1920,
        1080
      ],
      "mode": "RGBA",
      "decodable": true,
      "native_1080p_container": true,
      "size_bytes": 11343,
      "sha256": "80c6cd2f521a0a36bbdb6cf087888d0f443cd006319619740cec7f29114daef0"
    }
  ]
}

```

## FILE: qa/stage1_implementation_20260913/r9_workflow_regression_v2.stderr.log
SHA256: 9ac9b7fbcdac000a3390e0417c06f803ffe9feddaf8d85ddcfc97bbec5db217c
```text
.....................................................................................................
----------------------------------------------------------------------
Ran 101 tests in 196.763s

OK
OpenCV: FFMPEG: tag 0x30385056/'VP80' is not supported with codec id 139 and format 'webm / WebM'
[mov,mp4,m4a,3gp,3g2,mj2 @ 0000018856129040] moov atom not found

```
