#!/usr/bin/env python3
"""Model of the base upgrade economy over operations 1-10.

After each operation the modelled player spends on the cheapest affordable item (next ARMORY level,
next LAB level or the next intel analysis, by research cost) until nothing is affordable. Prices come
from data/progression/upgrades.json and data/progression/intel_discoveries.json, income from the
authored loot of data/missions/MIS_CH01_01..10.json (counted as tests/smoke/upgrade_economy_smoke.gd
does). The LAB multiplier (+12 % research per level) applies to research earned after it is bought.

This is a design aid for tuning prices, not a balance approval: real players collect less, replay more
and choose differently, and intel samples are assumed to be available.

    python tools/maintenance/upgrade_economy_sim.py [--loot 1.0 0.85 0.7] [--path 1.0]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OPERATIONS = 10
RESEARCH_PER_LAB_LEVEL = 0.12
# What StoryStage01 awards a room that authors no loot (main-route type, then the two optional rooms).
DEFAULT_ROOM_RESEARCH = {"EVENT": 10, "COMBAT": 25, "RESEARCH": 45, "ELITE": 35, "BOSS": 45}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def mission_income(number: int) -> tuple[int, int, int]:
    """Research, salvage and signal fragments one full-loot clear of the operation pays."""
    mission = load(f"data/missions/MIS_CH01_{number:02d}.json")
    research = salvage = fragments = 0
    for row in mission["main_route"] + mission.get("optional_rooms", []):
        if "loot" in row:
            for loot in row["loot"]:
                quantity = max(0, int(loot.get("quantity", 0)))
                kind = loot.get("loot_id")
                if kind in ("LOT_RESEARCH_COMMON", "LOT_RESEARCH_HIGH_VALUE"):
                    research += quantity
                elif kind == "LOT_SALVAGE_FIELD":
                    salvage += quantity
                elif kind == "LOT_SIGNAL_FRAGMENT":
                    fragments += quantity
        elif row.get("id") == "O01_SUPPLY":
            research += 20
            salvage += 2
        elif row.get("id") == "O02_RESEARCH":
            research += 40
            fragments += 1
        else:
            research += DEFAULT_ROOM_RESEARCH.get(row.get("type", "EVENT"), 0)
    return research, salvage, fragments


def price_tables() -> dict[str, list[tuple[int, int, int]]]:
    tables = {}
    for upgrade in load("data/progression/upgrades.json")["upgrades"]:
        tables[upgrade["upgrade_id"]] = [(r["research"], r["salvage"], r["fragments"]) for r in upgrade["levels"]]
    return tables


def simulate(loot: float, verbose: bool) -> tuple[list[int], list[int], list[float]]:
    tables = price_tables()
    armory, lab = tables["ARMORY_CALIBRATION"], tables["LAB_SIGNAL_ANALYSIS"]
    analyses = sorted(int(row["research_cost"]) for row in load("data/progression/intel_discoveries.json")["discoveries"])
    research = salvage = fragments = 0.0
    armory_level = lab_level = bought = 0
    at_five: list[int] = []
    for number in range(1, OPERATIONS + 1):
        income = mission_income(number)
        research += income[0] * loot * (1.0 + RESEARCH_PER_LAB_LEVEL * lab_level)
        salvage += income[1] * loot
        fragments += income[2] * loot
        while True:
            options = []
            if armory_level < len(armory) and research >= armory[armory_level][0] and salvage >= armory[armory_level][1] and fragments >= armory[armory_level][2]:
                options.append((armory[armory_level][0], "armory"))
            if lab_level < len(lab) and research >= lab[lab_level][0] and salvage >= lab[lab_level][1] and fragments >= lab[lab_level][2]:
                options.append((lab[lab_level][0], "lab"))
            if bought < len(analyses) and research >= analyses[bought]:
                options.append((analyses[bought], "analysis"))
            if not options:
                break
            _, kind = min(options)
            if kind == "armory":
                research -= armory[armory_level][0]
                salvage -= armory[armory_level][1]
                fragments -= armory[armory_level][2]
                armory_level += 1
            elif kind == "lab":
                research -= lab[lab_level][0]
                salvage -= lab[lab_level][1]
                fragments -= lab[lab_level][2]
                lab_level += 1
            else:
                research -= analyses[bought]
                bought += 1
        if verbose:
            print(f"  after operation {number:2d}: ARMORY {armory_level}/{len(armory)}  LAB {lab_level}/{len(lab)}  analyses {bought}/{len(analyses)}"
                  f"  | left research {research:6.0f}  salvage {salvage:5.1f}  fragments {fragments:5.1f}")
        if number == 5:
            at_five = [armory_level, lab_level, bought]
    return at_five, [armory_level, lab_level, bought], [research, salvage, fragments]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--loot", type=float, nargs="*", default=[1.0, 0.85, 0.7], help="share of the authored loot the player collects")
    parser.add_argument("--path", type=float, default=None, help="also print the operation-by-operation path for this loot share")
    args = parser.parse_args()
    income = [sum(mission_income(n)[i] for n in range(1, OPERATIONS + 1)) for i in range(3)]
    tables = price_tables()
    sink = [sum(row[i] for table in tables.values() for row in table) for i in range(3)]
    analyses = sum(int(row["research_cost"]) for row in load("data/progression/intel_discoveries.json")["discoveries"])
    print(f"authored income (operations 1-{OPERATIONS}, full loot): research {income[0]}  salvage {income[1]}  fragments {income[2]}")
    print(f"sink: research {sink[0] + analyses} (upgrades {sink[0]} + analyses {analyses})  salvage {sink[1]}  fragments {sink[2]}"
          f"  -> {(sink[0] + analyses) / income[0]:.2f} / {sink[1] / income[1]:.2f} / {sink[2] / income[2]:.2f} of the income")
    for loot in args.loot:
        at_five, at_end, left = simulate(loot, verbose=False)
        print(f"loot {loot:4.0%}: after op 5 ARMORY {at_five[0]} LAB {at_five[1]} analyses {at_five[2]} | after op {OPERATIONS} ARMORY {at_end[0]} LAB {at_end[1]}"
              f" analyses {at_end[2]} | left research {left[0]:.0f} salvage {left[1]:.1f} fragments {left[2]:.1f}")
    if args.path is not None:
        print(f"path at {args.path:.0%} loot:")
        simulate(args.path, verbose=True)


if __name__ == "__main__":
    main()
