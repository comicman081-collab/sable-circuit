extends SceneTree
## Controlled boss phase/telegraph cases in the real scene, not a playthrough.
## Health and attack serial select the tested phase; no game values are changed.
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
# Default candidate input is the reviewed runtime spec (the 2026-09-13 QA candidate was retired); pass --candidate-spec for a new candidate.
const SPEC := "res://assets/enemies/signal_anchor_guardian/authored_core_v1/spec.json"
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
