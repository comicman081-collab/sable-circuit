extends SceneTree
const STAGE := preload("res://scenes/mission/StoryStage01.tscn")
var failures: Array[String] = []
var checks := 0
var hits := 0
var captures: Array[String] = []
var out := "res://qa/cover_ai_20260919/boss_guard_"+str(Time.get_unix_time_from_system()).replace(".","_")
class Target extends Node2D:
    var damage := 0.0
    func apply_damage(value: float) -> void: damage+=value
    func get_combat_hit_rect() -> Rect2: return Rect2(global_position-Vector2(14,14),Vector2(28,28))
func _init() -> void: call_deferred("run")
func check(ok: bool, note: String) -> void:
    checks+=1
    if not ok: failures.append(note); push_error(note)
func settle(count: int = 3) -> void:
    for tick in range(count): await physics_frame; await process_frame
func advance(shot: PrototypeProjectile, hz: int) -> void:
    shot.set_physics_process(false)
    for tick in range(hz*2):
        if shot.is_queued_for_deletion(): break
        shot._physics_process(1.0/hz)
func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
    root.size=Vector2i(1920,1080)
    root.content_scale_size=Vector2i(1280,720)
    root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
    if DisplayServer.get_name()!="headless": DisplayServer.window_set_size(Vector2i(1920,1080))
    var stage := STAGE.instantiate() as StoryStage01
    root.add_child(stage)
    await settle(8)
    stage.battle_preview=true
    stage.start_battle_preview(4)
    await settle(4)
    stage.set_process(false); stage.set_physics_process(false)
    stage.squad.set_process(false); stage.squad.set_physics_process(false)
    var player := stage.squad.get_active_operator()
    for actor in stage.squad.operators:
        actor.set_physics_process(false); actor.set_process(false)
    var boss: EnemyActor
    for node in get_nodes_in_group("m3_enemies"):
        node.set_physics_process(false)
        if node.enemy_id=="BOSS_SITE7_ANCHOR_01": boss=node
    check(boss!=null,"Actual app boss loaded")
    if boss==null: quit(1); return
    var guard := boss.get_node("BossPhaseTransitionGuard")
    guard.set_physics_process(false)
    var shots: Array[PrototypeProjectile]=[]
    player.projectile_spawned.connect(func(shot: PrototypeProjectile) -> void: shots.append(shot))
    player.primary_hit.connect(func(_actor: OperatorActor,_damage: float) -> void: hits+=1)
    player.global_position=boss.global_position+Vector2(-280,-20)
    stage.camera.global_position=boss.global_position+Vector2(-60,-80)
    stage.camera.zoom=Vector2(1.02,1.02)
    stage.camera.reset_smoothing(); stage.camera.force_update_scroll()
    for node in root.get_children():
        if node is PrototypeProjectile: node.free()
    for hz in [30,60,120]:
        # Threshold fixture, entered through the actual damage + guard code.
        guard._phase3_seen=false; guard._guard_left=0; guard._removed_target_group=false
        boss.health=boss.max_health*.35
        boss.apply_damage(boss.max_health*.04)
        guard._physics_process(1.0/hz)
        check(guard.debug_guard_active() and boss.is_in_group("site7_guarded_targets"),"Phase guard has projectile collider at %dHz"%hz)
        check(not boss.is_in_group("prototype_targets"),"Companion auto-target exclusion preserved at %dHz"%hz)
        var hp := boss.health
        var before_hits := hits
        player._pointer_target=boss.get_combat_aim_point()
        check(player.debug_fire_once(),"Actual controlled weapon emits shield test at %dHz"%hz)
        var shot: PrototypeProjectile = shots.back()
        var sentinel := Target.new()
        root.add_child(sentinel)
        sentinel.add_to_group("prototype_targets")
        sentinel.global_position=shot.global_position+shot.direction*750
        advance(shot,hz)
        check(shot.is_queued_for_deletion(),"Shield absorbs projectile at %dHz"%hz)
        check(boss.health==hp and sentinel.damage==0 and hits==before_hits,"No shield damage, pass-through or hit bonus at %dHz"%hz)
        if hz==60 and DisplayServer.get_name()!="headless":
            await RenderingServer.frame_post_draw
            var picture := root.get_texture().get_image()
            check(picture.get_size()==Vector2i(1920,1080),"Native boss guard capture")
            var path := out+"/core_shielded_1920x1080.png"
            check(picture.save_png(ProjectSettings.globalize_path(path))==OK,"Boss guard image saved")
            captures.append(path)
        sentinel.queue_free()
        guard._physics_process(guard.debug_guard_seconds()+0.01)
        check(not guard.debug_guard_active() and boss.is_in_group("prototype_targets") and not boss.is_in_group("site7_guarded_targets"),"Normal targeting restored after original eight seconds at %dHz"%hz)
        player._pointer_target=boss.get_combat_aim_point()
        check(player.debug_fire_once(),"Post-shield real weapon fires at %dHz"%hz)
        advance(shots.back(),hz)
        check(boss.health<hp and hits==before_hits+1,"Normal damage/hit bonus restored at %dHz"%hz)
        await settle(1)
    stage.queue_free(); await settle(3)
    check(get_nodes_in_group("site7_guarded_targets").is_empty(),"No stale shield targets after scene exit")
    var hashes: Dictionary={}
    for path in ["scripts/animation/boss_phase_transition_guard.gd","scripts/combat/prototype_projectile.gd","scripts/ui/enemy_overhead_ui.gd","tests/render/site7_boss_guard_check.gd"]:
        hashes[path]=FileAccess.get_sha256("res://"+path)
    FileAccess.open(out+"/check.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_TECHNICAL_ONLY" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"captures":captures,"dependency_sha256":hashes,"controlled_threshold_fixture":true,"visual_approval":false},"  "))
    print("SITE7_BOSS_GUARD: %s / %d checks"%["PASS" if failures.is_empty() else "FAIL",checks])
    quit(0 if failures.is_empty() else 1)
