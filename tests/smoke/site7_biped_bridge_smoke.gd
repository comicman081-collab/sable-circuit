extends SceneTree
## Test-only coloured cells, NEVER character artwork or visual approval.
## No production registry is changed; incomplete rifle art stays quarantined.
const ENEMY := preload("res://scenes/actors/enemy/EnemyActor.tscn")
const OPERATOR := preload("res://scenes/actors/player/OperatorActor.tscn")
const BRIDGE := preload("res://scripts/animation/site7_biped_sprite.gd")
const NAMES := ["E","SE","S","SW","W","NW","N","NE"]
var checks := 0
var failures: Array[String] = []
var emissions: Array[Dictionary] = []
var output := ""
var fixture_profile: Dictionary = {}
var fixture_spec: Dictionary = {}
var fixture_number := 0

class BoundsFixture extends Node2D:
    var locked_position := Vector2.ZERO
    func constrain_battle_position(_value: Vector2) -> Vector2: return locked_position

func _init() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
    checks+=1
    if not ok: failures.append(label);push_error(label)

func write_json(path: String, value: Variant) -> void:
    var file := FileAccess.open(path,FileAccess.WRITE)
    file.store_string(JSON.stringify(value,"  "));file.close()

func save_spec(profile: Dictionary) -> Dictionary:
    fixture_number+=1
    var path := output+"/profile_"+str(fixture_number)+".json"
    write_json(path,profile)
    var spec := fixture_spec.duplicate(true)
    spec.profile=path
    spec.profile_sha256=FileAccess.get_sha256(path)
    return spec

func make_fixture() -> void:
    fixture_profile={"id":"site7_rifle","heightMetres":1.72,"animation":{"presentation":"authored_frames"},"locomotion":{"walkStride":1.33},"views":{}}
    fixture_spec={"kind":"authored_biped8","enemy_id":"ENM_SITE7_RIFLE_01","character_id":"site7_rifle","asset_root":output+"/","display_height":129.6,"atlas_files":{}}
    for sector in range(8):
        var view: Dictionary={}
        for act in ["idle","walk"]:
            var count := 1 if act == "idle" else 6
            var columns := 1 if act == "idle" else 3
            var image := Image.create(64*columns,64*(1 if act == "idle" else 2),false,Image.FORMAT_RGBA8)
            image.fill(Color.TRANSPARENT)
            var muzzles: Array=[]
            for index in range(count):
                var base := Vector2i((index%columns)*64,int(index/columns)*64)
                image.fill_rect(Rect2i(base+Vector2i(16,8),Vector2i(32,48)),Color.from_hsv(float(sector)/8,0.5+index*0.04,0.7))
                var tip := Vector2(32,32)+Vector2.from_angle(sector*PI/4.0)*(8.0+index)
                muzzles.append([tip.x,tip.y])
            var filename: String=NAMES[sector]+"_"+act+".png"
            var path:=output+"/"+filename
            check(image.save_png(path)==OK,"Write test-only synthetic cell "+filename)
            fixture_spec.atlas_files[path]=FileAccess.get_sha256(path)
            view[act]={"cell":[64,64],"root":[32,56],"height":48,"columns":columns,"frames":count,"image":filename,"muzzles":muzzles}
            if act == "walk":view[act].phaseStarts=[0.0,0.2,0.33,0.5,0.7,0.83]
        fixture_profile.views[NAMES[sector]]=view

func refuses(actor: EnemyActor, spec: Dictionary, label: String) -> void:
    var candidate := BRIDGE.new()
    actor.add_child(candidate)
    check(not candidate.configure(actor,spec),label)
    check(not candidate.configured and candidate.sprite==null,"Atomic rejection: "+label)
    candidate.free()

func test_atlas(profile: Dictionary, direction: String, act: String, filename: String, image: Image, columns: int) -> void:
    var path := output+"/"+filename
    check(image.save_png(path)==OK,"Write counterexample atlas "+filename)
    fixture_spec.atlas_files[path]=FileAccess.get_sha256(path)
    profile.views[direction][act].image=filename
    profile.views[direction][act].columns=columns

func repack_walk(columns: int, direction: String = "E") -> Image:
    var source := Image.load_from_file(output+"/"+direction+"_walk.png")
    var result := Image.create(columns*64,int(ceil(6.0/columns))*64,false,Image.FORMAT_RGBA8)
    result.fill(Color.TRANSPARENT)
    for index in range(6):
        result.blit_rect(source,Rect2i((index%3)*64,int(index/3)*64,64,64),Vector2i((index%columns)*64,int(index/columns)*64))
    return result

func review_input_counterexamples(actor: EnemyActor) -> void:
    var bad := fixture_profile.duplicate(true)
    var empty := Image.create(64,64,false,Image.FORMAT_RGBA8);empty.fill(Color.TRANSPARENT)
    test_atlas(bad,"NW","idle","empty_idle.png",empty,1)
    refuses(actor,save_spec(bad),"R11-01 empty idle cell rejected")
    bad=fixture_profile.duplicate(true)
    var partial := Image.load_from_file(output+"/SE_walk.png")
    partial.fill_rect(Rect2i(0,64,64,64),Color.TRANSPARENT)
    test_atlas(bad,"SE","walk","empty_walk_cell.png",partial,3)
    refuses(actor,save_spec(bad),"R11-01 empty used walk cell rejected")
    bad=fixture_profile.duplicate(true)
    test_atlas(bad,"SE","walk","repacked_columns2.png",repack_walk(2),2)
    refuses(actor,save_spec(bad),"R11-02 identical used cells repacked to two columns rejected")
    bad=fixture_profile.duplicate(true)
    var padded := repack_walk(4)
    test_atlas(bad,"E","walk","padded_e.png",padded,4)
    padded.set_pixel(140,90,Color.RED)
    test_atlas(bad,"SE","walk","padded_se.png",padded,4)
    refuses(actor,save_spec(bad),"R11-02 unused padding cannot disguise duplicate used sequence")
    bad=fixture_profile.duplicate(true);bad.locomotion.walkStride=1.0e308
    refuses(actor,save_spec(bad),"R11-03 derived cycle distance overflow rejected")
    bad=fixture_profile.duplicate(true);bad.locomotion.walkStride=1.0e-308;bad.heightMetres=1.0e308
    refuses(actor,save_spec(bad),"R11-03 derived cycle distance underflow rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.height=1.0e-308
    refuses(actor,save_spec(bad),"R11-03 invalid derived render scale rejected")
    # Real distinct sequences remain accepted with a different valid layout;
    # unused padding is ignored for identity, not forbidden unconditionally.
    var good := fixture_profile.duplicate(true)
    var unique := repack_walk(4,"SE");unique.set_pixel(140,90,Color.RED)
    test_atlas(good,"SE","walk","valid_unique_padded.png",unique,4)
    test_atlas(good,"NW","walk","valid_unique_columns2.png",repack_walk(2,"NW"),2)
    var candidate := BRIDGE.new();actor.add_child(candidate)
    check(candidate.configure(actor,save_spec(good)),"R11-02 distinct used sequences survive alternate layouts and padding")
    candidate.free()

func run() -> void:
    output="res://qa/stage1_implementation_20260913/biped_bridge_"+str(Time.get_unix_time_from_system()).replace(".","_")
    DirAccess.make_dir_recursive_absolute(output)
    var registry_hash := FileAccess.get_sha256("res://data/art_profiles/enemy_profiles.json")
    make_fixture()
    var spec:=save_spec(fixture_profile)
    var actor := ENEMY.instantiate() as EnemyActor
    actor.configure("ENM_SITE7_RIFLE_01",100.0)
    root.add_child(actor);actor.set_physics_process(false)
    check(not is_instance_valid(actor.biped_sprite),"Unfinished rifle has no production binding")
    review_input_counterexamples(actor)
    var bad := fixture_profile.duplicate(true)
    bad.views.erase("NE");refuses(actor,save_spec(bad),"Partial direction set rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.phaseStarts=[0,0.2,0.2,0.5,0.7,0.83]
    refuses(actor,save_spec(bad),"Duplicate phase start rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.muzzles[3]=[90,20]
    refuses(actor,save_spec(bad),"Out-of-cell muzzle rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.muzzles[3]=["NaN",20]
    refuses(actor,save_spec(bad),"Nonnumeric muzzle rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.image="../outside.png"
    refuses(actor,save_spec(bad),"Traversal path rejected")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.image=bad.views.E.walk.image
    refuses(actor,save_spec(bad),"One file reused for two directions rejected")
    var duplicate := Image.load_from_file(output+"/E_walk.png")
    duplicate.set_pixel(0,0,Color(1,0,0,0))
    duplicate.save_png(output+"/hidden_rgb_duplicate.png")
    fixture_spec.atlas_files[output+"/hidden_rgb_duplicate.png"]=FileAccess.get_sha256(output+"/hidden_rgb_duplicate.png")
    bad=fixture_profile.duplicate(true);bad.views.SE.walk.image="hidden_rgb_duplicate.png"
    check(fixture_spec.atlas_files[output+"/hidden_rgb_duplicate.png"]!=fixture_spec.atlas_files[output+"/E_walk.png"],"Hidden-RGB fixture changes file bytes")
    refuses(actor,save_spec(bad),"Different file hash cannot disguise duplicate visible direction")
    var broken := spec.duplicate(true);broken.profile_sha256="invalid"
    refuses(actor,broken,"Changed profile rejected")
    broken=spec.duplicate(true);broken.atlas_files[output+"/SE_walk.png"]="invalid"
    refuses(actor,broken,"Changed atlas rejected")
    broken=spec.duplicate(true);broken.enemy_id="ENM_SITE7_SHIELD_01"
    refuses(actor,broken,"Wrong enemy role rejected")
    # Matching all shield identity fields must still fail: the latest roster
    # retires this biped role, rather than merely rejecting mismatched IDs.
    bad=fixture_profile.duplicate(true);bad.id="site7_shield"
    broken=save_spec(bad);broken.enemy_id="ENM_SITE7_SHIELD_01";broken.character_id="site7_shield"
    actor.enemy_id="ENM_SITE7_SHIELD_01"
    refuses(actor,broken,"Retired humanoid shield rejected even with matching profile/spec/actor identity")
    actor.enemy_id="ENM_SITE7_RIFLE_01"
    check(BRIDGE.IDENTITIES.size()==1 and BRIDGE.IDENTITIES.has(actor.enemy_id),"Only one reusable humanoid enemy role is admitted")
    actor._aim_dir=Vector2.UP
    check(actor.preview_biped_source(spec),"Complete candidate intake")
    if not is_instance_valid(actor.biped_sprite):actor.free();quit(1);return
    var bridge: Node2D=actor.biped_sprite
    check(bridge.facing==6,"Initial view respects actor aim before first tactics step")
    check(not actor._visual_root.visible and bridge.sprite.visible,"Candidate replaces only its own mock")
    check(is_equal_approx(bridge.cycle_distance,1.33*129.6/1.72),"NPC metre conversion uses own source height")
    check(actor.max_health==100.0 and actor.run_speed_multiplier==1.0,"No AI health/speed overwritten from Studio")
    for hz in [30,60,120]:
        for move_sector in range(8):
            for aim_sector in range(8):
                bridge.phase=0.0
                bridge.facing=aim_sector
                var movement: Vector2=Vector2.from_angle(move_sector*PI/4.0)*86.0/float(hz)
                for tick in range(hz):bridge.commit_displacement(movement)
                check(absf(bridge.phase-fposmod(86.0/bridge.cycle_distance,1.0))<0.00001,"Distance phase independent of Hz/movement/aim")
                check(bridge.action=="walk" and bridge.facing==aim_sector,"Whole-body movement retains aim sector")
                var saved: float=bridge.phase
                bridge.commit_displacement(Vector2.ZERO)
                for tick in range(5):bridge.sync_pose()
                check(bridge.action=="idle" and bridge.frame==0 and bridge.phase==saved,"Zero measured displacement has no time-driven legs")
    bridge.phase=0.23;bridge.move_direction=Vector2.LEFT;bridge.moving=true;bridge.facing=0;bridge.sync_pose()
    check(bridge.frame==4,"Reverse travel selects reversed authored phase, not warped limbs")
    bridge.move_direction=Vector2.RIGHT;bridge.sync_pose()
    check(bridge.frame==1,"Forward travel retains ordinary phase")
    var victim:=OPERATOR.instantiate() as OperatorActor
    victim.configure("CHR_PROTO_01","ASTER",Color.WHITE)
    root.add_child(victim);victim.set_physics_process(false)
    actor.projectile_emitted.connect(func(event: Dictionary) -> void:emissions.append(event))
    for hz in [30,60,120]:
        for sector in range(8):
            emissions.clear()
            var direction:=Vector2.from_angle(sector*PI/4.0)
            victim.global_position=direction*500.0
            actor.velocity=-direction*86.0
            bridge.commit_displacement(-direction*3.0)
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor.tactics.step(victim,1.0/hz)
            var frozen_muzzle: Vector2=bridge.muzzle_world()
            var frozen_facing: int=bridge.facing
            var frozen_phase: float=bridge.phase
            var locked: Vector2=actor.tactics.locked_aim
            check(actor.tactics.state=="WINDUP" and bridge.action=="idle","Stop before acquiring announced idle emitter")
            check(bridge.visible_heading_world().dot(locked)>cos(PI/8.0+0.02),"Visible front agrees with warning ray")
            victim.global_position=-direction*500.0
            for tick in range(hz*2):
                actor.tactics.step(victim,1.0/hz)
                bridge.commit_displacement(Vector2.ZERO)
                if emissions.size()==3:break
            check(emissions.size()==3,"Real tactics emits exactly three rifle rounds")
            check(bridge.facing==frozen_facing and bridge.phase==frozen_phase and bridge.action=="idle","Target reversal during attack cannot turn body or cycle feet")
            for event in emissions:
                var origin:=Vector2(event.origin[0],event.origin[1])
                var shot_direction:=Vector2(event.direction[0],event.direction[1])
                check(origin.distance_to(frozen_muzzle)<0.001 and shot_direction.distance_to(locked)<0.001,"Actual creation boundary matches frozen visible muzzle/ray")
                var shot:=instance_from_id(event.projectile_id)
                if is_instance_valid(shot):shot.free()
            actor.tactics.state="REPOSITION";actor.tactics.state_left=1.0
            actor.tactics.step(victim,1.0/hz)
            check(bridge.visible_heading_world().dot(locked)<-0.8,"Next movement follows opposite target without smoothing lag")
    actor.velocity=Vector2.ZERO
    bridge.commit_displacement(Vector2.ZERO)
    check(not actor.aim_from_emitter(actor.global_position+Vector2(0,-64.8)).is_finite(),"Inside all emitter offsets rejects reverse shot")
    var previous_facing: int=bridge.facing
    check(not bridge.resolve_target(Vector2.INF).is_finite() and bridge.facing==previous_facing,"Invalid target preserves view")
    var old_texture: Texture2D=bridge.sprite.texture
    check(not bridge.configure(actor,spec) and bridge.sprite.texture==old_texture,"Repeated configure cannot replace active pixels")
    check(actor.get_node("OverheadUI").bar_y_local()<bridge.visual_rect_world().position.y-actor.global_position.y,"HUD stays above entire cell")
    var arena := BoundsFixture.new()
    root.add_child(arena)
    root.remove_child(actor);arena.add_child(actor)
    victim.global_position=Vector2(5000,0)
    actor.tactics.state="REPOSITION";actor.tactics.state_left=10.0
    var phase_before_bounds: float=bridge.phase
    actor._physics_process(1.0/60.0)
    check(actor.velocity.length()>0.0 and actor.global_position==Vector2.ZERO,"Actual enemy movement is clamped by stage boundary")
    check(bridge.phase==phase_before_bounds and bridge.action=="idle","Post-boundary actual displacement, not intended velocity, drives phase")
    for hz in [30,60,120]:
        for lock_state in ["WINDUP","BURST"]:
            arena.locked_position=Vector2.ZERO;actor.global_position=Vector2.ZERO
            victim.global_position=Vector2(500,0)
            bridge.phase=0.23;bridge.facing=0
            actor.tactics.state="REPOSITION";actor.tactics.state_left=0.0
            actor._physics_process(1.0/float(hz))
            check(actor.tactics.state=="WINDUP" and bridge.action=="idle","R11-04 acquire normal announced idle")
            if lock_state=="BURST":actor.tactics.state_left=0.000001
            arena.locked_position=Vector2(1,0)
            emissions.clear()
            actor._physics_process(1.0/float(hz))
            check(actor.global_position==Vector2(1,0),"R11-04 retain actual physical correction")
            check(actor.tactics.state=="RECOVER","R11-04 moved warning/burst is interrupted")
            check(absf(bridge.phase-fposmod(0.23+1.0/bridge.cycle_distance,1.0))<0.00001,"R11-04 do not falsify corrected displacement phase")
            for tick in range(4):actor._physics_process(1.0/float(hz))
            check(emissions.is_empty(),"R11-04 no continuation fire from unannounced corrected origin")
            for event in emissions:
                var shot:=instance_from_id(event.projectile_id)
                if is_instance_valid(shot):shot.free()
    arena.locked_position=Vector2.ZERO;actor.global_position=Vector2.ZERO
    arena.remove_child(actor);root.add_child(actor);arena.free()
    var wall := StaticBody2D.new()
    wall.collision_layer=1;wall.collision_mask=2
    var wall_shape := CollisionShape2D.new()
    var rectangle := RectangleShape2D.new();rectangle.size=Vector2(20,200)
    wall_shape.shape=rectangle;wall.add_child(wall_shape)
    wall.position=Vector2(45,-18);root.add_child(wall)
    actor.global_position=Vector2.ZERO
    actor._orbit_sign=0.0
    bridge.phase=0.0
    actor.tactics.state="REPOSITION";actor.tactics.state_left=10.0
    actor.set_physics_process(true)
    var travel := 0.0
    var before := actor.global_position
    for tick in range(60):
        await physics_frame
        travel+=actor.global_position.distance_to(before)
        before=actor.global_position
    actor.set_physics_process(false)
    check(travel>5.0 and travel<18.0 and actor.get_slide_collision_count()>0,"Real move_and_slide stops on collision wall")
    check(absf(bridge.phase-fposmod(travel/bridge.cycle_distance,1.0))<0.001 and bridge.action=="idle","Actual collision distance agrees with phase and stops walking")
    wall.free()
    actor.configure("ENM_SITE7_SHIELD_01",155.0)
    check(not is_instance_valid(actor.biped_sprite) and not bridge.visible and actor._visual_root.visible,"Role replacement retires old candidate safely")
    check(not actor.preview_biped_source(spec),"Rifle cannot attach to shield")
    actor.free();victim.free()
    # Dispose only this isolated process's transient sound nodes and release
    # their streams before shutdown; production sound generation is unchanged.
    for node in root.get_children():
        if node is AudioStreamPlayer:
            node.stop();node.stream=null;node.queue_free()
    await process_frame
    check(FileAccess.get_sha256("res://data/art_profiles/enemy_profiles.json")==registry_hash,"Production registry is byte-unchanged")
    var hashes: Dictionary={}
    for path in ["scripts/animation/site7_biped_sprite.gd","scripts/actors/enemy_actor.gd","scripts/ui/enemy_overhead_ui.gd","scripts/combat/site7_enemy_tactics.gd","tests/smoke/site7_biped_bridge_smoke.gd"]: hashes[path]=FileAccess.get_sha256("res://"+path)
    write_json(output+"/report.json",{"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"sha256":hashes,"synthetic_fixtures_only":true,"visual_approval":false,"production_registry_changed":false})
    print("SITE7_BIPED_BRIDGE: ","PASS" if failures.is_empty() else "FAIL"," (",checks,") ",output)
    quit(0 if failures.is_empty() else 1)
