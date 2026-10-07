extends SceneTree
const Output := preload("res://tests/support/test_output.gd")
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
const CASES := [
    ["MOD_SPORE_FILTER", "CHR_PROTO_02", "E", "rook_bulwark_duration", 5.0, 6.0],
    ["MOD_FROST_LENS", "CHR_PROTO_01", "Q", "aster_prism_cooldown", 4.0, 3.2],
    ["MOD_RAIL_SPOOL", "CHR_PROTO_01", "E", "aster_dash_distance", 150.0, 200.0],
    ["MOD_ECHO_RELAY", "CHR_PROTO_03", "E", "mica_relay_guard_duration", 4.0, 6.0],
    ["MOD_NULL_ANCHOR", "CHR_PROTO_02", "X", "rook_scatter_duration", 5.0, 6.5]
]
var checks := 0
var failures: Array[String] = []
var measurements: Array = []
var squad: SquadController
var target: EnemyActor
func _init() -> void: call_deferred("run")
func run() -> void:
    var p := CampaignProgression.new(false)
    for row: Array in CASES:
        check(p.equip_module(row[1], row[0]).reason == "MODULE_LOCKED", row[0] + " locked before analysis")
    p.research_value = 10000
    p.intel_samples = IntelSamples.sanitize({"SECURITY":2,"ABERRANT":1,"ANCHOR":1,"AERATOR":1,"CRYO":1,"GANTRY":1,"ARCHIVE":1,"ORIGIN":1})
    for row: Dictionary in p.snapshot().discoveries: check(p.analyze_intel(row.analysis_id).success, row.analysis_id + " unlock")
    squad = SquadController.new(); root.add_child(squad)
    await process_frame
    squad.set_process(false)
    for actor: OperatorActor in squad.operators:
        actor.set_physics_process(false)
        actor.movement_bounds = Rect2(-5000,-5000,10000,10000)
        actor.get_node("SkillController").set_process(false)
    target = preload("res://scenes/actors/enemy/EnemyActor.tscn").instantiate()
    check(target.configure("ENM_SITE7_DRONE_01",10000), "live target uses registered robot")
    root.add_child(target); target.set_physics_process(false)
    for row: Array in CASES:
        var actor := operator(row[1])
        var skills := actor.get_node("SkillController")
        var wrong := "CHR_PROTO_01" if row[1] != "CHR_PROTO_01" else "CHR_PROTO_02"
        check(p.equip_module(wrong,row[0]).reason == "MODULE_INCOMPATIBLE", row[0] + " wrong operator rejected")
        actor.apply_campaign_modifiers({"module_id":""})
        var vanilla := measure(actor, row[2])
        check(close(vanilla.value,row[4]), row[0] + " actual baseline")
        check(p.equip_module(row[1],row[0]).success, row[0] + " single slot equipped")
        actor.apply_campaign_modifiers({"module_id":p.equipped_modules[row[1]]})
        actor.apply_campaign_modifiers({"module_id":p.equipped_modules[row[1]]})
        var active := measure(actor,row[2])
        var contract: Dictionary = skills.debug_contract()
        check(close(active.value,row[5]) and close(contract[row[3]],row[5]), row[0] + " actual effect and debug authority agree exactly once")
        check(close(actor.debug_campaign_damage_multiplier(),1.0), row[0] + " time effect adds no damage multiplier")
        if row[0] == "MOD_RAIL_SPOOL":
            check(close(active.cooldown,4.0) and close(vanilla.cooldown,5.0), "RAIL SPOOL actual E cooldown")
            check(close(contract.aster_prism_cooldown,4.0), "switch FROST to RAIL removes Q cooldown bonus")
            check(active.value - vanilla.value <= 50.0, "dash extension at most 50px")
        elif row[0] == "MOD_FROST_LENS":
            check(1.0 - active.value / vanilla.value <= 0.25, "cooldown reduction at most 25 percent")
            check(close(active.damage,vanilla.damage), "FROST changes no damage")
        else:
            check(active.value - vanilla.value <= 2.0, row[0] + " duration extension at most 2 seconds")
        check(p.equipped_modules.size() == 3 and p.equipped_modules[row[1]] is String, "save retains one string slot per operator")
        actor.apply_campaign_modifiers({"module_id":""})
        var removed := measure(actor,row[2])
        check(removed == vanilla, row[0] + " removal restores exact actual baseline")
        # Switch from A to B in the same actor. A's authority must vanish.
        var other := "MOD_PRISM_FOCUS" if row[1] == "CHR_PROTO_01" else ("MOD_BREACH_LINER" if row[1] == "CHR_PROTO_02" else "MOD_SENSOR_ARRAY")
        actor.apply_campaign_modifiers({"module_id":row[0]})
        actor.apply_campaign_modifiers({"module_id":other})
        var switched: Dictionary = skills.debug_contract()
        check(close(switched[row[3]],row[4]), row[0] + " A to legacy B leaves only B authority")
        measurements.append({"module":row[0],"before":vanilla,"after":active,"removed":removed})
    var out := Output.path("res://.cache/tests/module_expansion.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f := FileAccess.open(out,FileAccess.WRITE)
    f.store_string(JSON.stringify({"checks":checks,"measurements":measurements,"failures":failures},"  ")); f.close()
    squad.queue_free(); target.queue_free(); await process_frame
    for node in root.get_children():
        if node is OperatorSkillVFX: node.queue_free()
    await process_frame
    print("MODULE_EXPANSION_SMOKE: ", "PASS" if failures.is_empty() else "FAIL", " (", checks, " checks)")
    quit(0 if failures.is_empty() else 1)
func operator(id: String) -> OperatorActor:
    for actor in squad.operators:
        if actor.operator_id == id: return actor
    return null
func measure(actor: OperatorActor, slot: String) -> Dictionary:
    # Independent fresh activations, with physics paused. Existing active skills
    # normally expire on their timer; loadout replacement is a base action.
    for i in range(squad.operators.size()):
        var other := squad.operators[i]
        other.reset_for_battle_preview()
        other.global_position = Vector2(2500+i*200,2000)
    actor.global_position = Vector2(500,1000); actor.aim_world = Vector2.RIGHT
    target.global_position = Vector2(800,1000); target.health = 10000
    var start := actor.global_position
    var skills := actor.get_node("SkillController")
    squad.debug_set_energy(100)
    check(skills.debug_force_cast(slot), actor.operator_id + " actual " + slot + " cast")
    var buffs := actor.debug_runtime_skill_buffs()
    match [actor.operator_id,slot]:
        ["CHR_PROTO_01","Q"]: return {"value":skills.q_left,"damage":10000-target.health}
        ["CHR_PROTO_01","E"]: return {"value":actor.global_position.distance_to(start),"cooldown":skills.e_left}
        ["CHR_PROTO_02","E"]: return {"value":buffs.guard_left,"reduction":buffs.guard_reduction}
        ["CHR_PROTO_03","E"]:
            for other in squad.operators: check(close(other.debug_runtime_skill_buffs().guard_left,buffs.guard_left),"ECHO relay guards every operator equally")
            return {"value":buffs.guard_left,"reduction":buffs.guard_reduction}
        ["CHR_PROTO_02","X"]: return {"value":buffs.scatter_cycle_left,"guard":buffs.guard_left,"reduction":buffs.guard_reduction}
    return {}
func close(a: float,b: float) -> bool: return absf(a-b) < 0.001
func check(ok: bool,label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)
