extends SceneTree
## Upgrade economy gate. The two base upgrades run to six levels (data/progression/upgrades.json) so
## the rewards of operations 6-10 have somewhere to go. This proves that the first three levels still
## cost what they always did, that every level is bought through the real purchase path with exact
## accounting, that saves keep and clamp levels, that the base lobby prints each price inside its
## button, and that the total sink stays in proportion to what operations 1-10 author. Data and
## wiring only; it is no approval of balance or play.
const TestOutput := preload("res://tests/support/test_output.gd")
const LOBBY_SCENE := preload("res://scenes/base/BaseLobby.tscn")
const ARMORY := "ARMORY_CALIBRATION"
const LAB := "LAB_SIGNAL_ANALYSIS"
const LEVELS := 6
const OPERATIONS := 10
## Levels 1-3 as shipped before the extension, [research, salvage, fragments]. Saves paid these
## prices, so the table never changes them.
const LEGACY := {
    "ARMORY_CALIBRATION": [[140, 1, 0], [240, 2, 0], [340, 3, 0]],
    "LAB_SIGNAL_ANALYSIS": [[100, 0, 1], [220, 0, 1], [340, 0, 1]],
}
const DAMAGE_PER_LEVEL := 0.08
const RESEARCH_PER_LEVEL := 0.12
## The stage and the operators clamp both multipliers to 1..2; the top level stays inside so the
## bonus the base shows is the bonus that is applied.
const MULTIPLIER_CLAMP := 2.0
## The base's whole sink (upgrades and analyses) over what operations 1-10 author in one full-loot
## clear each. Research income also grows with the LAB multiplier, so its band sits above 1.
const RESEARCH_BAND := Vector2(0.9, 1.5)
const PARTS_BAND := Vector2(0.5, 1.5)
## The facility button of BaseLobby (UPGRADE_BUTTON_WIDTH); a long price shrinks the font, but not below this.
const BUTTON_WIDTH := 242.0
const MIN_FONT := 14

var failures: Array[String] = []
var checks := 0
var save_path := TestOutput.path("res://.cache/tests/upgrade_economy/save.json")

func _init() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
    checks += 1
    if not ok: failures.append(label); push_error(label)

func cost_row(cost: Dictionary) -> Array:
    return [int(cost.get("research", 0)), int(cost.get("salvage", 0)), int(cost.get("fragments", 0))]

func table_total(table: Array[Dictionary]) -> Array:
    var sum := [0, 0, 0]
    for row in table:
        var price := cost_row(row)
        for i in range(3): sum[i] += price[i]
    return sum

func set_level(campaign: CampaignProgression, id: String, level: int) -> void:
    if id == ARMORY: campaign.armory_level = level
    else: campaign.lab_level = level

func level_of(campaign: CampaignProgression, id: String) -> int:
    return campaign.armory_level if id == ARMORY else campaign.lab_level

func expected_label(verb: String, price: Array) -> String:
    var parts: Array[String] = ["%dR" % price[0]]
    if int(price[1]) > 0: parts.append("%dS" % price[1])
    if int(price[2]) > 0: parts.append("%dF" % price[2])
    return "%s // %s" % [verb, " + ".join(parts)]

func write_save(data: Dictionary) -> void:
    var file := FileAccess.open(save_path, FileAccess.WRITE)
    file.store_string(JSON.stringify(data))
    file.close()

func run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(save_path.get_base_dir()))
    var probe := CampaignProgression.new(false)
    for id in [ARMORY, LAB]:
        check_table(probe, id)
        walk_purchases(id)
        check_shortfalls(id)
    check_snapshot()
    check_persistence()
    check_weapon_tiers()
    check_income_coverage(probe)
    await check_lobby()
    print("UPGRADE_ECONOMY: %s (%d checks)" % ["PASS" if failures.is_empty() else "FAIL", checks])
    for failure in failures: print("  FAIL ", failure)
    quit(0 if failures.is_empty() else 1)

## The table itself: six levels, levels 1-3 unchanged, every later level costs more research and never less in parts.
func check_table(probe: CampaignProgression, id: String) -> void:
    var table := probe.upgrade_table(id)
    check(probe.max_level(id) == LEVELS and table.size() == LEVELS, "%s has %d levels" % [id, LEVELS])
    var legacy: Array = LEGACY[id]
    for i in range(mini(legacy.size(), table.size())):
        check(cost_row(table[i]) == legacy[i], "%s level %d still costs %s" % [id, i + 1, str(legacy[i])])
    for i in range(1, table.size()):
        var before := cost_row(table[i - 1])
        var after := cost_row(table[i])
        check(after[0] > before[0], "%s research rises at level %d" % [id, i + 1])
        check(after[1] >= before[1] and after[2] >= before[2], "%s parts never get cheaper at level %d" % [id, i + 1])
    check(probe.max_level("NOT_AN_UPGRADE") == 0 and probe.upgrade_table("NOT_AN_UPGRADE").is_empty(), "An unknown upgrade has no table")
    check(cost_row(probe.get_upgrade_cost("NOT_AN_UPGRADE")) == [0, 0, 0], "An unknown upgrade costs nothing and cannot be bought")
    var refused := probe.purchase_upgrade("NOT_AN_UPGRADE")
    check(str(refused.get("reason", "")) == "UNKNOWN_UPGRADE", "An unknown upgrade is refused")

## Every level through the real purchase path, with exactly the total in the wallet.
func walk_purchases(id: String) -> void:
    var campaign := CampaignProgression.new(false)
    var table := campaign.upgrade_table(id)
    var total := table_total(table)
    campaign.research_value = total[0]
    campaign.salvage = total[1]
    campaign.signal_fragments = total[2]
    for level in range(table.size()):
        check(cost_row(campaign.get_upgrade_cost(id)) == cost_row(table[level]), "%s reports the level %d price" % [id, level + 1])
        var result := campaign.purchase_upgrade(id)
        check(bool(result.get("success", false)) and int(result.get("new_level", -1)) == level + 1, "%s level %d purchases" % [id, level + 1])
    check(campaign.research_value == 0 and campaign.salvage == 0 and campaign.signal_fragments == 0, "%s spends the exact wallet to zero" % id)
    check(cost_row(campaign.get_upgrade_cost(id)) == [0, 0, 0], "%s has no next price at the cap" % id)
    campaign.research_value = 99999
    campaign.salvage = 99
    campaign.signal_fragments = 99
    var capped := campaign.purchase_upgrade(id)
    check(not bool(capped.get("success", true)) and str(capped.get("reason", "")) == "MAX_LEVEL", "%s stops at level %d" % [id, LEVELS])
    check(campaign.research_value == 99999 and campaign.salvage == 99 and campaign.signal_fragments == 99 and level_of(campaign, id) == LEVELS, "%s: a purchase refused at the cap takes nothing" % id)

## One short of any single currency at any level buys nothing and takes nothing.
func check_shortfalls(id: String) -> void:
    var table := CampaignProgression.new(false).upgrade_table(id)
    for level in range(table.size()):
        var price := cost_row(table[level])
        for currency in range(3):
            if price[currency] <= 0: continue
            var campaign := CampaignProgression.new(false)
            set_level(campaign, id, level)
            var wallet := price.duplicate()
            wallet[currency] -= 1
            campaign.research_value = wallet[0]
            campaign.salvage = wallet[1]
            campaign.signal_fragments = wallet[2]
            var result := campaign.purchase_upgrade(id)
            var untouched: bool = campaign.research_value == wallet[0] and campaign.salvage == wallet[1] and campaign.signal_fragments == wallet[2] and level_of(campaign, id) == level
            check(str(result.get("reason", "")) == "INSUFFICIENT_RESOURCES" and untouched, "%s level %d is refused one %s short" % [id, level + 1, ["research", "salvage", "fragment"][currency]])

func check_snapshot() -> void:
    var campaign := CampaignProgression.new(false)
    var armory := campaign.upgrade_table(ARMORY)
    var lab := campaign.upgrade_table(LAB)
    for level in range(LEVELS + 1):
        campaign.armory_level = level
        campaign.lab_level = level
        var snapshot := campaign.snapshot()
        check(int(snapshot.get("armory_max_level", 0)) == LEVELS and int(snapshot.get("lab_max_level", 0)) == LEVELS and int(snapshot.get("max_upgrade_level", 0)) == LEVELS, "The snapshot reports the level caps at level %d" % level)
        var damage := float(snapshot.get("damage_multiplier", 0.0))
        var research := float(snapshot.get("research_multiplier", 0.0))
        check(is_equal_approx(damage, 1.0 + DAMAGE_PER_LEVEL * level) and is_equal_approx(research, 1.0 + RESEARCH_PER_LEVEL * level), "Level %d grants +%d%% damage and +%d%% research" % [level, roundi(DAMAGE_PER_LEVEL * 100.0 * level), roundi(RESEARCH_PER_LEVEL * 100.0 * level)])
        check(damage <= MULTIPLIER_CLAMP and research <= MULTIPLIER_CLAMP, "Level %d stays inside the x%.1f multiplier clamp" % [level, MULTIPLIER_CLAMP])
        var next_armory := cost_row(armory[level]) if level < LEVELS else [0, 0, 0]
        var next_lab := cost_row(lab[level]) if level < LEVELS else [0, 0, 0]
        check(cost_row(snapshot.armory_cost) == next_armory and cost_row(snapshot.lab_cost) == next_lab, "The snapshot offers the level %d prices" % (level + 1))

## A save written at the old cap keeps its levels and is offered level 4; a save at the new cap or a damaged one loads cleanly.
func check_persistence() -> void:
    CampaignProgression.new(true, save_path).debug_reset()
    write_save({"schema_version": 4, "research_value": 500, "salvage": 6, "signal_fragments": 2, "armory_level": 3, "lab_level": 3})
    var old := CampaignProgression.new(true, save_path)
    check(old.armory_level == 3 and old.lab_level == 3, "A save at the old three-level cap keeps its levels")
    check(cost_row(old.get_upgrade_cost(ARMORY)) == [440, 5, 1] and cost_row(old.get_upgrade_cost(LAB)) == [460, 2, 2], "That save is offered level 4 next")
    check(bool(old.purchase_upgrade(ARMORY).get("success", false)) and old.research_value == 60 and old.salvage == 1 and old.signal_fragments == 1, "Level 4 is bought from the old save with its exact price")
    var reloaded := CampaignProgression.new(true, save_path)
    check(reloaded.armory_level == 4 and reloaded.lab_level == 3 and reloaded.research_value == 60, "Level 4 survives a reload")
    write_save({"schema_version": 4, "armory_level": LEVELS, "lab_level": LEVELS})
    var maxed := CampaignProgression.new(true, save_path)
    check(maxed.armory_level == LEVELS and maxed.lab_level == LEVELS, "A save at the top level keeps both levels")
    # A table that failed to load must not reset the levels a save holds, and then nothing can be bought.
    write_save({"schema_version": 4, "armory_level": 5, "lab_level": 4})
    var blind := CampaignProgression.new(true, save_path)
    blind._upgrade_cache.clear()
    blind._load()
    check(blind.armory_level == 5 and blind.lab_level == 4, "Saved levels survive a missing upgrade table")
    check(blind.max_level(ARMORY) == 0 and str(blind.purchase_upgrade(ARMORY).get("reason", "")) == "MAX_LEVEL", "Nothing can be bought without an upgrade table")
    write_save({"schema_version": 4, "armory_level": 99, "lab_level": -4})
    var damaged := CampaignProgression.new(true, save_path)
    check(damaged.armory_level == LEVELS and damaged.lab_level == 0, "Out-of-range saved levels clamp to 0..%d" % LEVELS)
    damaged.debug_reset()
    check(not FileAccess.file_exists(save_path), "The fixture save is removed afterwards")

func check_weapon_tiers() -> void:
    var campaign := CampaignProgression.new(false)
    campaign.armory_level = LEVELS
    var unlocked: Array = campaign.snapshot().get("unlocked_weapons", [])
    check(unlocked.has("WPN_AR_BURST_02") and unlocked.has("WPN_LMG_HELIX_01"), "The extended levels keep the ARMORY weapon tiers unlocked")

## What one full-loot clear of a mission pays: [research, salvage, fragments]. Rows without authored
## loot pay the defaults StoryStage01 awards (_award_main_route_reward and the two optional rooms).
func mission_income(id: String) -> Array:
    var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/missions/%s.json" % id))
    var research := 0
    var salvage := 0
    var fragments := 0
    var rows: Array = (mission.get("main_route", []) as Array) + (mission.get("optional_rooms", []) as Array)
    for row: Dictionary in rows:
        if row.has("loot"):
            for loot: Dictionary in row.loot:
                var quantity := maxi(0, int(loot.get("quantity", 0)))
                match str(loot.get("loot_id", "")):
                    "LOT_RESEARCH_COMMON", "LOT_RESEARCH_HIGH_VALUE": research += quantity
                    "LOT_SALVAGE_FIELD": salvage += quantity
                    "LOT_SIGNAL_FRAGMENT": fragments += quantity
        elif str(row.get("id", "")) == "O01_SUPPLY":
            research += 20
            salvage += 2
        elif str(row.get("id", "")) == "O02_RESEARCH":
            research += 40
            fragments += 1
        else:
            research += {"EVENT": 10, "COMBAT": 25, "RESEARCH": 45, "ELITE": 35, "BOSS": 45}.get(str(row.get("type", "EVENT")), 0)
    return [research, salvage, fragments]

func in_band(ratio: float, band: Vector2) -> bool:
    return ratio >= band.x and ratio <= band.y

func check_income_coverage(probe: CampaignProgression) -> void:
    var income := [0, 0, 0]
    var early := [0, 0, 0]
    for number in range(1, OPERATIONS + 1):
        var pay := mission_income("MIS_CH01_%02d" % number)
        for i in range(3):
            income[i] += pay[i]
            if number <= 5: early[i] += pay[i]
    var analyses := 0
    for row: Dictionary in probe.snapshot().get("discoveries", []): analyses += int(row.get("research_cost", 0))
    var sink := [analyses, 0, 0]
    var legacy := [0, 0, 0]
    for id in [ARMORY, LAB]:
        var total := table_total(probe.upgrade_table(id))
        for i in range(3): sink[i] += total[i]
        for row: Array in LEGACY[id]:
            for i in range(3): legacy[i] += row[i]
    print("economy: income research %d salvage %d fragments %d | sink research %d salvage %d fragments %d | operations 1-5 pay %s" % [income[0], income[1], income[2], sink[0], sink[1], sink[2], str(early)])
    check(in_band(float(sink[0]) / float(income[0]), RESEARCH_BAND), "Research sink %d against %d authored is inside %.1f-%.1f" % [sink[0], income[0], RESEARCH_BAND.x, RESEARCH_BAND.y])
    check(in_band(float(sink[1]) / float(income[1]), PARTS_BAND), "Salvage sink %d against %d authored is inside %.1f-%.1f" % [sink[1], income[1], PARTS_BAND.x, PARTS_BAND.y])
    check(in_band(float(sink[2]) / float(income[2]), PARTS_BAND), "Signal fragment sink %d against %d authored is inside %.1f-%.1f" % [sink[2], income[2], PARTS_BAND.x, PARTS_BAND.y])
    check(early[0] >= legacy[0] and early[1] >= legacy[1] and early[2] >= legacy[2], "Operations 1-5 alone still pay for the first three levels of both upgrades")
    # Negative control: the old three-level cap could not absorb the research of ten operations.
    var old_sink := float(legacy[0] + analyses) / float(income[0])
    check(not in_band(old_sink, RESEARCH_BAND), "Negative control: the old three-level cap (%.2f of the research) fails the band" % old_sink)

## The lobby prints the next price inside its 242 px button at every level, and offers nothing at the cap.
func check_lobby() -> void:
    var campaign := CampaignProgression.new(false)
    campaign.research_value = 9999
    campaign.salvage = 99
    campaign.signal_fragments = 99
    var lobby := LOBBY_SCENE.instantiate() as BaseLobby
    lobby.configure_campaign(campaign.snapshot())
    root.add_child(lobby)
    await process_frame
    await process_frame
    var facilities := {ARMORY: ["ARMORY", "CALIBRATE", "CALIBRATION LEVEL"], LAB: ["LAB", "ANALYZE CORE", "SIGNAL ANALYSIS LEVEL"]}
    for id: String in facilities:
        var table := campaign.upgrade_table(id)
        for level in range(LEVELS + 1):
            set_level(campaign, id, level)
            lobby.refresh_campaign(campaign.snapshot())
            lobby._show_facility(str(facilities[id][0]))
            var button: Button = lobby._upgrade_button
            var label := button.text
            var want := expected_label(str(facilities[id][1]), cost_row(table[level])) if level < LEVELS else "%s // MAX LEVEL" % facilities[id][1]
            check(label == want, "%s button at level %d reads '%s' (got '%s')" % [id, level, want, label])
            check(button.disabled == (level >= LEVELS), "%s button is %s at level %d" % [id, "disabled" if level >= LEVELS else "enabled", level])
            var width := button.get_minimum_size().x
            check(width > 40.0 and width <= BUTTON_WIDTH, "%s label '%s' is %.0f px wide inside %.0f" % [id, label, width, BUTTON_WIDTH])
            check(is_equal_approx(button.size.x, BUTTON_WIDTH), "%s button keeps its %.0f px width at level %d" % [id, BUTTON_WIDTH, level])
            var font_size := button.get_theme_font_size("font_size")
            check(font_size >= MIN_FONT, "%s label at level %d stays legible (%d px font)" % [id, level, font_size])
            if level == 0 or level == LEVELS - 1: print("lobby: %s level %d '%s' -> %.0f px at font %d" % [id, level, label, width, font_size])
            check(lobby._facility_body.text.begins_with("%s %d/%d" % [facilities[id][2], level, LEVELS]), "%s panel shows level %d/%d" % [id, level, LEVELS])
        set_level(campaign, id, 0)
    # The two labels players saw before the extension are unchanged.
    campaign.armory_level = 0
    campaign.lab_level = 0
    lobby.refresh_campaign(campaign.snapshot())
    lobby._show_facility("ARMORY")
    check((lobby._upgrade_button as Button).text == "CALIBRATE // 140R + 1S", "The level 1 ARMORY label is unchanged")
    lobby._show_facility("LAB")
    check((lobby._upgrade_button as Button).text == "ANALYZE CORE // 100R + 1F", "The level 1 LAB label is unchanged")
    lobby.queue_free()
    await process_frame
