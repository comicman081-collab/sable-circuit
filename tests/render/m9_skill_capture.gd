extends SceneTree

const STAGE_SCENE := preload("res://scenes/mission/StoryStage01.tscn")
const ENEMY_SCENE := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OUT_DIR := "res://artifacts/runtime_capture"

var stage: StoryStage01
var camera: Camera2D
var target: EnemyActor
var capture_failed := false

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    DisplayServer.window_set_size(Vector2i(1280,720))
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
    stage = STAGE_SCENE.instantiate() as StoryStage01
    root.add_child(stage)
    current_scene = stage
    await _frames(10)
    stage.set_process(false)
    var camera_presentation := stage.get_node_or_null("SquadCameraPresentation") as SquadCameraPresentation
    if camera_presentation != null:
        camera_presentation.set_process(false)
    camera = stage.get_node("Camera2D") as Camera2D
    camera.enabled = true
    camera.position_smoothing_enabled = false
    camera.global_position = Vector2(1030,490)
    camera.zoom = Vector2.ONE * 1.30

    stage.configure_campaign({"damage_multiplier":1.08,"research_multiplier":1.12},"M9-CAPTURE")
    stage.current_step = 2
    stage.call("_activate_step")
    stage.hud.set_objective("MICA SCAN → ASTER EXPLOIT → ROOK BREACH",false)
    stage.hud.set_story("M9 SYNERGY // Build EXPOSED, exploit it, then consume it into STAGGER.")
    stage.hud.set_combat_status(1)

    _place_squad()
    target = ENEMY_SCENE.instantiate() as EnemyActor
    target.configure("ENM_SITE7_SHIELD_01",400.0)
    target.global_position = Vector2(1120,490)
    stage.add_child(target)
    await _frames(3)
    target.set_physics_process(false)
    target.health = 400.0
    target.max_health = 400.0
    stage.squad.debug_set_energy(0.0)

    await _capture_mica_exposed()
    await _capture_aster_exploit()
    await _capture_rook_stagger()
    await _capture_ultimate_ready()

    if capture_failed or not _verify():
        quit(1)
        return
    print("M9_SKILL_CAPTURE: PASS")
    quit(0)

func _place_squad() -> void:
    var positions: Array[Vector2] = [Vector2(900,500),Vector2(930,555),Vector2(900,435)]
    for i in range(stage.squad.operators.size()):
        var actor := stage.squad.operators[i]
        actor.global_position = positions[i]
        actor.aim_world = Vector2.RIGHT
        actor.facing_sector = 0
        actor.debug_drive(Vector2.ZERO,Vector2.RIGHT)

func _capture_mica_exposed() -> void:
    stage.squad.request_control(2)
    var mica := stage.squad.operators[2]
    mica.global_position = Vector2(900,435)
    mica.aim_world = (target.global_position-mica.global_position).normalized()
    var skills := mica.get_node_or_null("SkillController") as OperatorSkillController
    if skills == null or not skills.debug_force_cast("Q") or not target.is_exposed():
        push_error("M9 capture failed to establish MICA EXPOSED state")
        capture_failed = true
        return
    stage.hud.set_story("MICA // PULSE SCAN   →   EXPOSED established on the Shield Breacher.")
    await _frames(2)
    camera.global_position = Vector2(1030,490)
    await _save("28_m9_mica_exposed.png")
    await _clear_skill_vfx()

func _capture_aster_exploit() -> void:
    stage.squad.request_control(0)
    var aster := stage.squad.operators[0]
    aster.global_position = Vector2(900,500)
    aster.aim_world = (target.global_position-aster.global_position).normalized()
    var skills := aster.get_node_or_null("SkillController") as OperatorSkillController
    var before := target.health
    if skills == null or not skills.debug_force_cast("Q"):
        push_error("M9 capture failed to cast ASTER Prism")
        capture_failed = true
        return
    var contract := skills.debug_contract()
    if str(contract.get("last_synergy","")) != "EXPOSED_EXPLOIT" or not target.is_exposed() or target.health >= before-40.0:
        push_error("M9 capture ASTER exploit contract failed")
        capture_failed = true
        return
    stage.hud.set_story("ASTER // PRISM   →   EXPOSED exploit amplified; mark remains for BREACH.")
    await _frames(2)
    camera.global_position = Vector2(1030,490)
    await _save("29_m9_aster_exploit.png")
    await _clear_skill_vfx()

func _capture_rook_stagger() -> void:
    stage.squad.request_control(1)
    var rook := stage.squad.operators[1]
    rook.global_position = Vector2(940,500)
    rook.aim_world = (target.global_position-rook.global_position).normalized()
    var skills := rook.get_node_or_null("SkillController") as OperatorSkillController
    var energy_before := float(stage.squad.debug_energy_contract().get("current",0.0))
    if skills == null or not skills.debug_force_cast("Q"):
        push_error("M9 capture failed to cast ROOK Breach Slam")
        capture_failed = true
        return
    if target.is_exposed() or not target.is_staggered():
        push_error("M9 capture ROOK failed to consume EXPOSED into STAGGER")
        capture_failed = true
        return
    if float(stage.squad.debug_energy_contract().get("current",0.0)) < energy_before+27.9:
        push_error("M9 capture ROOK stagger did not reward squad energy")
        capture_failed = true
        return
    stage.hud.set_story("ROOK // BREACH SLAM   →   EXPOSED consumed; armor STAGGERED; squad ENERGY surged.")
    await _frames(2)
    camera.global_position = Vector2(1030,490)
    await _save("30_m9_rook_stagger.png")
    await _clear_skill_vfx()

func _capture_ultimate_ready() -> void:
    stage.squad.request_control(0)
    var aster := stage.squad.operators[0]
    aster.global_position = Vector2(900,500)
    aster.aim_world = Vector2.RIGHT
    stage.squad.debug_set_energy(100.0)
    stage.hud.set_story("SQUAD ENERGY 100/100 // ULTIMATE READY   [X] ASTER OVERCLOCK")
    await _frames(3)
    var hud_contract := stage.hud.debug_skill_hud_contract()
    var labels: Array = hud_contract.get("skill_labels",[])
    if str(hud_contract.get("energy_text","")) != "100/100" or labels.size()!=3 or "X READY" not in str(labels[2]):
        push_error("M9 capture HUD did not expose authoritative ultimate-ready state")
        capture_failed = true
        return
    camera.global_position = Vector2(1030,490)
    await _save("31_m9_ultimate_ready.png")

func _clear_skill_vfx() -> void:
    for node in root.get_children():
        if node is OperatorSkillVFX and is_instance_valid(node):
            node.queue_free()
    await process_frame

func _frames(count: int) -> void:
    for _i in range(count):
        await process_frame

func _save(filename: String) -> void:
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    var bright_samples := 0
    for y in range(110,620,4):
        for x in range(330,1030,4):
            var pixel := image.get_pixel(x,y)
            if maxf(pixel.r,maxf(pixel.g,pixel.b))>0.24:
                bright_samples += 1
    if bright_samples < 100:
        push_error("M9 evidence is visually empty/off-canvas: %s samples=%d" % [filename,bright_samples])
        capture_failed = true
    var path := ProjectSettings.globalize_path(OUT_DIR+"/"+filename)
    var err := image.save_png(path)
    if err != OK:
        push_error("M9 capture failed: %s err=%d" % [path,err])
        capture_failed = true
        return
    print("M9_CAPTURED: %s samples=%d" % [path,bright_samples])

func _verify() -> bool:
    for filename in ["28_m9_mica_exposed.png","29_m9_aster_exploit.png","30_m9_rook_stagger.png","31_m9_ultimate_ready.png"]:
        if not FileAccess.file_exists(ProjectSettings.globalize_path(OUT_DIR+"/"+filename)):
            push_error("missing M9 runtime evidence: "+filename)
            return false
    return true
