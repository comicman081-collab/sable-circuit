extends SceneTree
# Claude scratch probe (T-5/T-6): how wide is the text really? Reads only; never saves.
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
func _init() -> void: call_deferred("run")
func run() -> void:
    root.size = Vector2i(1280, 720)
    var flow := GameFlow.new(); flow.persist_campaign = false; root.add_child(flow)
    var p := flow.campaign; p.research_value = 10000
    for key in IntelSamples.KEYS: p.intel_samples[key] = 3
    flow.enter_base()
    var lobby := flow.current_view as BaseLobby
    await create_timer(0.7).timeout
    var lbl := lobby._intel_summary_label
    var font: Font = lbl.label_settings.font if lbl.label_settings else lbl.get_theme_font("font")
    print("PROBE lobby samples: rect=", lbl.get_global_rect(), " fontsize=", lbl.get_theme_font_size("font_size"), " text=", lbl.text)
    var names := ["SECURITY", "ABERRANT", "ANCHOR", "AERATOR", "CRYO", "GANTRY", "ARCHIVE", "ORIGIN"]
    var parts := PackedStringArray()
    for n in names: parts.append("%s 03" % n)
    for sep in [" ", "  ", "   "]:
        var full: String = "SAMPLES // " + sep.join(parts)
        for fs in [12, 11, 10]:
            print("PROBE full-name samples sep=%d size=%d width=%.1f chars=%d" % [sep.length(), fs, font.get_string_size(full, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, full.length()])
    for i in range(3):
        var op: String = ["CHR_PROTO_01", "CHR_PROTO_02", "CHR_PROTO_03"][i]
        var ml := lobby.find_child("ModuleLabel_" + op, true, false) as Label
        var mb := lobby.find_child("ModuleCycle_" + op, true, false) as Button
        var f2: Font = ml.label_settings.font if ml.label_settings else ml.get_theme_font("font")
        print("PROBE module label %s rect=%s text=%s fontsize=%d  | button rect=%s" % [op, str(ml.get_global_rect()), ml.text, ml.get_theme_font_size("font_size"), str(mb.get_global_rect())])
        var rows := []
        for r in p.snapshot().discoveries:
            if r.operator_id == op: rows.append(str(r.module_name))
        var line := " / ".join(PackedStringArray(rows))
        for fs in [11, 10]:
            print("PROBE   unlocked-names line %s size=%d width=%.1f text=%s" % [op, fs, f2.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, line])
    print("PROBE panel rect=", lobby._m10_panel.get_global_rect(), " samples label parent=", lbl.get_parent().name)
    # HUD side
    flow.deploy_mission("MIS_CH01_01")
    await process_frame
    var stage := flow.current_view as StoryStage01
    if stage:
        var worst := {}
        for key in IntelSamples.KEYS: worst[key] = 12
        stage.debug_seed_intel(12, 12, 12, {"AERATOR": 12, "CRYO": 12, "GANTRY": 12, "ARCHIVE": 12, "ORIGIN": 12})
        await process_frame
        var il: Label = stage.hud._intel_label
        var hf: Font = il.label_settings.font if il.label_settings else il.get_theme_font("font")
        var fs2 := il.get_theme_font_size("font_size")
        print("PROBE hud intel: rect=%s fontsize=%d width=%.1f text=%s" % [str(il.get_global_rect()), fs2, hf.get_string_size(il.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs2).x, il.text])
        var tp: Control = stage.hud._transmission_panel
        print("PROBE hud transmission panel rect=", tp.get_global_rect(), " visible=", tp.visible)
        for name in ["_cargo_label", "_status_label", "_optional_label"]:
            var c: Control = stage.hud.get(name)
            print("PROBE hud ", name, " rect=", c.get_global_rect(), " visible=", c.visible)
    flow.queue_free(); await process_frame
    print("PROBE_DONE")
    quit(0)
