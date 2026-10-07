extends SceneTree
# Claude scratch probe (T-6): where do the two module lines really land?
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
    for page in range(3):
        for button in lobby._analysis_box.get_children().filter(func(n: Node) -> bool: return n is Button):
            (button as Button).pressed.emit()
        if page < 2: lobby._analysis_next.pressed.emit()
    await process_frame
    for op in CampaignProgression.OPERATOR_IDS:
        var ml := lobby.find_child("ModuleLabel_" + op, true, false) as Label
        var ch := lobby.find_child("ModuleChoices_" + op, true, false) as Label
        var mb := lobby.find_child("ModuleCycle_" + op, true, false) as Button
        print("PROBE %s label  rect=%s font=%d text=%s minsize=%s" % [op, str(ml.get_global_rect()), ml.get_theme_font_size("font_size"), ml.text, str(ml.get_combined_minimum_size())])
        if ch: print("PROBE %s listing rect=%s font=%d text=%s minsize=%s autowrap=%d" % [op, str(ch.get_global_rect()), ch.get_theme_font_size("font_size"), ch.text, str(ch.get_combined_minimum_size()), ch.autowrap_mode])
        print("PROBE %s button rect=%s" % [op, str(mb.get_global_rect())])
    flow.queue_free(); await process_frame
    print("PROBE_DONE")
    quit(0)
