extends SceneTree
const Output := preload("res://tests/support/test_output.gd")
const Envelope := preload("res://tests/support/weapon_envelope.gd")
const Painter := preload("res://scripts/vfx/vfx_painter.gd")
const TOKENS := ["ASTER","ROOK","MICA","DRONE","SHIELD","BULWARK","PRISM","FORGE","CARRIER","PYLON","RELAY","REMNANT","AERATOR","CRYO","GANTRY","ARCHIVE","ORIGIN","ANCHOR","MORTAR","RIFLE","ABERRANT","_RAM_","DEFLECT","BARRIER","GUARD"]
var checks := 0
var failures: Array[String] = []
var rows: Array = []
func _init() -> void: call_deferred("run")
func run() -> void:
    var p := CampaignProgression.new(false)
    for id: String in Envelope.NEW_IDS:
        var spec := WeaponRegistry.get_weapon(id)
        check(p.equip_weapon(spec.compatible_operators[0],id).reason == "WEAPON_LOCKED",id+" locked before analysis")
    p.research_value=1000; p.intel_samples.GANTRY=1; p.intel_samples.ORIGIN=1
    var squad := SquadController.new(); root.add_child(squad); await process_frame
    squad.set_process(false)
    for actor: OperatorActor in squad.operators:
        var identity := [actor.operator_id, actor.display_name, actor.accent_color]
        actor.set_script(load("res://.cache/diag/expansion_item3_20261006/weapon_controls/WPN_DMR_RAIL_01/actor.gd"))
        actor._visual = actor.get_node("VisualRoot")
        actor.configure(identity[0], identity[1], identity[2])
        actor.set_physics_process(false); actor.get_node("SkillController").set_process(false)
    check(Painter.new().triangle_count()==0,"empty painter has no triangles")
    var painter_source := FileAccess.get_file_as_string("res://scripts/vfx/vfx_painter.gd")
    check(painter_source.count("RenderingServer.canvas_item_add_triangle_array(")==2,"unchanged painter sends at most two arrays per layer per frame")
    for id: String in Envelope.NEW_IDS:
        var spec := WeaponRegistry.get_weapon(id)
        var rate := Envelope.dps(spec)
        check(rate.burst<=100 and rate.sustained<=78,id+" absolute DPS limits")
        for token: String in TOKENS:
            check(not token in id and not token in spec.projectile_profile and not token in spec.hit_vfx_profile,id+" avoids legacy token "+token)
        check(p.analyze_intel(spec.unlock).success,id+" unlock names actual analysis rule")
        check(p.snapshot().unlocked_weapons.has(id),id+" exact added unlock rule")
        for actor: OperatorActor in squad.operators:
            var compatible := WeaponRegistry.is_compatible(actor.operator_id,id)
            var equipped := p.equip_weapon(actor.operator_id,id)
            check(equipped.success == compatible,id+" compatibility enforced for "+actor.operator_id)
            if not compatible: continue
            check(rate.sustained<=Envelope.legacy_best(actor.operator_id),id+" below legacy sustained DPS for "+actor.operator_id)
            actor.reset_for_battle_preview()
            actor.apply_campaign_modifiers({"weapon_id":id,"module_id":"","damage_multiplier":1.0})
            var original := actor.art_profile.duplicate(true)
            var shot_profile := actor._weapon_art_profile()
            var remaining := shot_profile.duplicate(true)
            for key in ["projectile_profile","hit_vfx_profile"]: remaining[key]=original[key]
            check(remaining==original and actor.art_profile==original,id+" copied profile changes only two VFX fields")
            check(shot_profile.fire_sfx_profile==original.fire_sfx_profile and shot_profile.impact_sfx_profile==original.impact_sfx_profile,id+" preserves both existing sound profiles")
            var shots: Array[PrototypeProjectile] = []
            var observer := func(shot: PrototypeProjectile) -> void: shots.append(shot)
            actor.projectile_spawned.connect(observer)
            var ammo := actor.ammo
            await physics_frame
            check(actor.debug_fire_once(),id+" real trigger fires")
            actor.projectile_spawned.disconnect(observer)
            check(shots.size()==int(spec.pellet_count) and actor.ammo==ammo-int(spec.ammo_per_trigger),id+" real pellet/ammo transaction")
            var family := "WEAPON_RAIL" if id==Envelope.NEW_IDS[0] else "WEAPON_NULL"
            var muzzle: CombatMuzzleVFX
            var flash_count := 0
            for node in root.get_children():
                if node is CombatMuzzleVFX and not node.is_queued_for_deletion() and node.shooter==actor:
                    muzzle=node; flash_count+=1
            check(flash_count==1 and muzzle.family==family,id+" volley dedupes to its own one muzzle flash")
            if muzzle:
                muzzle.age=muzzle.life*0.2; muzzle._draw()
                check(muzzle._paint.triangle_count()>0 and muzzle._paint.triangle_count()<400,id+" bounded muzzle triangles")
            for shot: PrototypeProjectile in shots:
                shot.set_physics_process(false)
                check(shot._family==family and shot.projectile_profile==spec.projectile_profile,id+" own projectile family")
                check(is_equal_approx(shot.damage,spec.damage) and is_equal_approx(shot.speed,spec.projectile_speed) and is_equal_approx(shot.lifetime,spec.projectile_lifetime),id+" exact live weapon numbers")
                check(not shot.debug_visual_contract().aster_v6_requested and not shot.debug_visual_contract().aster_v6_sprite_active,id+" code body never requests ASTER raster")
                shot._travelled=400; shot._draw()
                check(shot._paint.triangle_count()>0 and shot._paint.triangle_count()<400,id+" bounded projectile triangles")
            if not shots.is_empty():
                var target: EnemyActor = preload("res://scenes/actors/enemy/EnemyActor.tscn").instantiate()
                target.configure("ENM_SITE7_DRONE_01",1000); root.add_child(target); target.set_physics_process(false)
                var shot := shots[0]
                target.global_position = shot.global_position+shot.direction*80-(target.get_combat_hit_rect().get_center()-target.global_position)
                var hp := target.health
                shot._physics_process(0.15)
                check(is_equal_approx(hp-target.health,spec.damage),id+" actual impact applies exact weapon damage")
                var impacts := 0
                for node in root.get_children():
                    if node is CombatHitVFX and node.effect_kind==CombatHitVFX.EFFECT_IMPACT and not node.is_queued_for_deletion():
                        impacts+=1
                        check(node.family==family,id+" actual hit uses weapon profile")
                        node.age=node.lifetime*0.2; node._draw()
                        check(node.debug_triangle_count()>0 and node.debug_triangle_count()<1500,id+" bounded hit triangles")
                check(impacts==1,id+" one hit does not stack an operator-family impact")
                target.queue_free()
            actor.apply_campaign_modifiers({"weapon_id":CampaignProgression.DEFAULT_WEAPONS[actor.operator_id]})
            check(actor._weapon_art_profile()==original,id+" switching to default restores entire original profile")
            for node in root.get_children():
                if node is PrototypeProjectile or node is CombatMuzzleVFX or node is CombatHitVFX: node.queue_free()
            await process_frame
        rows.append({"weapon":id,"burst_dps":rate.burst,"sustained_dps":rate.sustained,"flight_px":spec.projectile_speed*spec.projectile_lifetime,"role":spec.role})
    var out := Output.path("res://.cache/tests/weapon_expansion.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out,FileAccess.WRITE); f.store_string(JSON.stringify({"checks":checks,"weapons":rows,"failures":failures},"  ")); f.close()
    squad.queue_free(); await process_frame
    print("WEAPON_EXPANSION_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)
func check(ok: bool,label: String) -> void:
    checks+=1
    if not ok: failures.append(label); push_error(label)
