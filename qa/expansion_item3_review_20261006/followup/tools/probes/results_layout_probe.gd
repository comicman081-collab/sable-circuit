extends SceneTree
## Scratch probe (not committed, writes nothing): real label heights of the results screen
## for all ten operations, both outcomes. Positions are panel-local, so the entrance tween does not matter.
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
func _init() -> void: call_deferred("run")
func run() -> void:
    root.size = Vector2i(1280, 720)
    var intel := {}
    for k in IntelSamples.KEYS: intel[k] = 3
    var worst_epilogue_bottom := 0.0
    for i in range(1, 11):
        var mission_id := "MIS_CH01_%02d" % i
        for outcome in ["EXTRACTED", "WIPED"]:
            var results := MissionResults.new()
            root.add_child(results)
            results.configure({"mission_id": mission_id, "outcome": outcome, "extraction_depth": 6 if outcome == "EXTRACTED" else 2,
                "secured_research": 12, "secured_salvage": 3, "secured_fragments": 1, "lost_unsecured": 4, "lost_intel_samples": 2, "secured_intel": intel,
                "campaign": {"research_value": 1234, "salvage": 5, "signal_fragments": 2, "armory_level": 3, "lab_level": 3, "intel_samples": intel},
                "campaign_transaction": {"next_mission_id": "MIS_CH01_%02d" % mini(i + 1, 10) if i < 10 else ""}})
            await process_frame
            await process_frame
            var panel: Panel = results._panel
            var stock: Label = results._campaign_line
            var epi: Label = results._epilogue
            var bar := results.find_child("CommandBar", true, false) as ColorRect
            var back := results.find_child("ReturnToBase", true, false) as Button
            var stock_h := maxf(stock.size.y, stock.get_minimum_size().y)
            var epi_h := maxf(epi.size.y, epi.get_minimum_size().y)
            var epi_bottom := epi.position.y + epi_h
            worst_epilogue_bottom = maxf(worst_epilogue_bottom, epi_bottom)
            print("%s %-9s stock y %.0f..%.0f (min %.1f box %.1f)  bar %.0f..%.0f  epilogue y %.0f..%.0f (lines %d, min %.1f box %.1f)  button top %.0f  font stock %d epi %d" % [
                mission_id, outcome, stock.position.y, stock.position.y + stock_h, stock.get_minimum_size().y, stock.size.y,
                bar.position.y if bar else -1.0, (bar.position.y + bar.size.y) if bar else -1.0,
                epi.position.y, epi_bottom, epi.get_line_count(), epi.get_minimum_size().y, epi.size.y, back.position.y if back else -1.0,
                stock.get_theme_font_size("font_size"), epi.get_theme_font_size("font_size")])
            results.queue_free()
            await process_frame
    print("worst epilogue bottom (panel-local): %.1f ; return button top 516" % worst_epilogue_bottom)
    quit(0)
