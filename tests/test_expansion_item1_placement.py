"""Freeze the reversible placement commit, not every future mission/art edit.

Both the original deployment and the recommended replacements are valid; a
single revert of the mission-only commit must not require reverting feature code.
"""
from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEMENT_COMMIT = "5cb3e012"
PLACEMENT_PATHS = {f"data/missions/MIS_CH01_{n:02d}.json" for n in (6, 7, 8, 9)}
PROTECTED_PATHS = ("assets/", "art_src/", "motion_lab_v1/", "data/visual/")
NEW_HAZARDS = {6: "SPORE_CLOUD", 7: "FROST_PLATE", 8: "RAIL_LANE"}
NEW_AFFIXES = {6: "BROODING", 9: "BEACON"}


def committed_bytes(revision: str, number: int) -> bytes:
    path = f"data/missions/MIS_CH01_{number:02d}.json"
    result = subprocess.run(["git", "show", f"{revision}:{path}"], cwd=ROOT,
                            check=True, capture_output=True)
    return result.stdout


def placement_commit_errors(paths: list[str]) -> list[str]:
    errors = []
    if set(paths) != PLACEMENT_PATHS:
        errors.append("placement commit does not touch exactly missions 06-09")
    if any(path.startswith(PROTECTED_PATHS) for path in paths):
        errors.append("placement commit touches protected art/visual paths")
    return errors


def projection(value):
    if isinstance(value, dict):
        return {k: projection(v) for k, v in value.items() if k not in ("hazards", "affix")}
    if isinstance(value, list):
        return [projection(v) for v in value]
    return value


def affix_rows(value):
    result = []
    if isinstance(value, dict):
        if "enemy_id" in value and "affix" in value:
            result.append(value)
        for child in value.values():
            result.extend(affix_rows(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(affix_rows(child))
    return result


def placement_errors(number: int, before: dict, after: dict) -> list[str]:
    """Historical one-for-one placement rules; never apply to today's tree."""
    errors = []
    if number in (1, 2, 3, 4, 5, 10) and before != after:
        errors.append("protected operation changed")
    if projection(before) != projection(after):
        errors.append("fields outside hazards/affix changed")
    if len(affix_rows(before)) != len(affix_rows(after)):
        errors.append("elite row count changed")
    new_affixes = [r for r in affix_rows(after) if r["affix"] in ("BROODING", "BEACON")]
    if len(new_affixes) > 1 or any(r["affix"] != NEW_AFFIXES.get(number) for r in new_affixes):
        errors.append("new elite outside its operation or more than one")
    if any(r["enemy_id"].startswith("BOSS_") for r in affix_rows(after)):
        errors.append("boss has an affix")
    for index, room in enumerate(after.get("main_route", [])):
        previous = before["main_route"][index]
        old_count = sum(r.get("count", 1) for r in previous.get("hazards", []))
        rows = room.get("hazards", [])
        count = sum(r.get("count", 1) for r in rows)
        if count > old_count or any(r.get("count", 1) < 1 for r in rows):
            errors.append("hazard count increased or invalid")
        if rows and room.get("type") == "BOSS":
            errors.append("boss room has hazards")
        for row in rows:
            if row["type"] != "ARC_VENT" and row["type"] != NEW_HAZARDS.get(number):
                errors.append("hazard outside its operation")
        # A new type replaces exactly one original vent, rather than adding one.
        new_count = sum(r.get("count", 1) for r in rows if r["type"] != "ARC_VENT")
        if new_count and (new_count != 1 or count != old_count):
            errors.append("new hazard is not one-for-one")
        if new_count and not str(room.get("id", "")).startswith(("R02", "R04")):
            errors.append("new hazard outside R02/R04")
    return errors


def current_mission_errors(mission: dict, hazards: set[str], affixes: set[str]) -> list[str]:
    """Only invariant runtime validity, allowing later balance and art changes."""
    errors = []
    for row in affix_rows(mission):
        if str(row["enemy_id"]).startswith("BOSS_"):
            errors.append("boss has an affix")
        if str(row["affix"]).strip().upper() not in affixes:
            errors.append("unknown affix id")
    for room in mission.get("main_route", []) + mission.get("optional_rooms", []):
        rows = room.get("hazards", [])
        if rows and room.get("type") == "BOSS":
            errors.append("boss room has hazards")
        for row in rows:
            if str(row.get("type", "")).strip().upper() not in hazards:
                errors.append("unknown hazard id")
            count = row.get("count", 1)
            if isinstance(count, bool) or not isinstance(count, (int, float)) or not count >= 1:
                errors.append("invalid hazard count")
    return errors


class PlacementContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        revisions = (f"{PLACEMENT_COMMIT}^", PLACEMENT_COMMIT)
        for revision in revisions:
            try:
                result = subprocess.run(["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
                                        cwd=ROOT, capture_output=True)
            except OSError as exc:
                raise unittest.SkipTest(f"placement commit pair unavailable: {exc}") from exc
            if result.returncode:
                raise unittest.SkipTest(f"placement commit pair unavailable: {revision}; current mission checks still run")
        cls.before_bytes = {n: committed_bytes(revisions[0], n) for n in range(1, 11)}
        cls.after_bytes = {n: committed_bytes(revisions[1], n) for n in range(1, 11)}
        cls.before = {n: json.loads(raw.decode("utf-8-sig")) for n, raw in cls.before_bytes.items()}
        cls.after = {n: json.loads(raw.decode("utf-8-sig")) for n, raw in cls.after_bytes.items()}

    def test_deployed_missions_preserve_authored_combat_and_rewards(self):
        for number in range(1, 11):
            with self.subTest(operation=number):
                self.assertEqual([], placement_errors(number, self.before[number], self.after[number]))
                if number in (1, 2, 3, 4, 5, 10):
                    self.assertEqual(self.before_bytes[number], self.after_bytes[number])

    def test_fixed_commit_has_the_recommended_replacements(self):
        for number, expected in NEW_AFFIXES.items():
            rows = [row for row in affix_rows(self.after[number]) if row["affix"] in NEW_AFFIXES.values()]
            self.assertEqual([expected], [row["affix"] for row in rows])
            room = next(room for room in self.after[number]["main_route"] if room["id"].startswith("R04"))
            self.assertIn(rows[0], affix_rows(room))
        for number, expected in NEW_HAZARDS.items():
            for room in self.after[number]["main_route"]:
                with self.subTest(operation=number, room=room["id"]):
                    count = sum(row.get("count", 1) for row in room.get("hazards", []) if row["type"] == expected)
                    self.assertEqual(1 if room["id"].startswith(("R02", "R04")) else 0, count)

    def test_original_deployment_is_valid_for_single_commit_revert(self):
        for number in range(1, 11):
            self.assertEqual([], placement_errors(number, self.before[number], self.before[number]))

    def test_changed_health_reward_offset_and_robot_count_are_rejected(self):
        before = self.before[6]
        row = before["main_route"][1]["encounter"][0]
        for field in ("health", "offset_x", "offset_y"):
            after = copy.deepcopy(before)
            after["main_route"][1]["encounter"][0][field] = row.get(field, 0) + 1
            self.assertIn("fields outside hazards/affix changed", placement_errors(6, before, after))
        after = copy.deepcopy(before)
        after["main_route"][1]["encounter"].append(copy.deepcopy(row))
        self.assertIn("fields outside hazards/affix changed", placement_errors(6, before, after))
        after = copy.deepcopy(before)
        after["optional_rooms"][1]["loot"][0]["quantity"] += 1
        self.assertIn("fields outside hazards/affix changed", placement_errors(6, before, after))

    def test_extra_hazard_wrong_operation_and_boss_affix_are_rejected(self):
        before = self.before[6]
        after = copy.deepcopy(before)
        after["main_route"][1]["hazards"][0]["count"] += 1
        self.assertIn("hazard count increased or invalid", placement_errors(6, before, after))
        after = copy.deepcopy(before)
        after["main_route"][1]["hazards"][0]["type"] = "FROST_PLATE"
        self.assertIn("hazard outside its operation", placement_errors(6, before, after))
        after = copy.deepcopy(before)
        boss_room = next(r for r in after["main_route"] if r["type"] == "BOSS")
        boss_row = next(r for r in boss_room["encounter"] if r["enemy_id"].startswith("BOSS_"))
        boss_row["affix"] = "BEACON"
        self.assertIn("boss has an affix", placement_errors(6, before, after))

    def test_protected_asset_and_visual_paths_are_unchanged(self):
        # diff-tree returns repository-root paths even from a scratch subfolder.
        paths = subprocess.run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r",
                                f"{PLACEMENT_COMMIT}^", PLACEMENT_COMMIT],
                               cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
        self.assertEqual([], placement_commit_errors(paths))


class CurrentMissionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hazards = set(json.loads((ROOT / "data/progression/zone_hazards.json").read_text(encoding="utf-8-sig"))["hazards"])
        cls.affixes = set(json.loads((ROOT / "data/progression/elite_affixes.json").read_text(encoding="utf-8-sig"))["affixes"])
        cls.missions = {n: json.loads((ROOT / f"data/missions/MIS_CH01_{n:02d}.json").read_text(encoding="utf-8-sig")) for n in range(1, 11)}

    def test_current_missions_obey_runtime_invariants(self):
        for number, mission in self.missions.items():
            with self.subTest(operation=number):
                self.assertEqual([], current_mission_errors(mission, self.hazards, self.affixes))

    def test_later_health_or_themed_placement_changes_are_allowed(self):
        changed = copy.deepcopy(self.missions[3])
        affix_rows(changed)[0]["health"] += 1
        self.assertEqual([], current_mission_errors(changed, self.hazards, self.affixes))
        changed = copy.deepcopy(self.missions[10])
        room = next(room for room in changed["main_route"] if room["type"] != "BOSS" and room.get("hazards"))
        room["hazards"][0] = {"type": "SPORE_CLOUD", "count": 3}
        self.assertEqual([], current_mission_errors(changed, self.hazards, self.affixes))

    def test_current_boss_ids_and_counts_have_negative_controls(self):
        before = self.missions[6]
        for kind in ("boss_hazard", "boss_affix", "unknown_hazard", "unknown_affix", "zero_count"):
            changed = copy.deepcopy(before)
            room = next(room for room in changed["main_route"] if room.get("hazards"))
            boss = next(room for room in changed["main_route"] if room["type"] == "BOSS")
            expected = ""
            if kind == "boss_hazard":
                boss["hazards"] = [{"type": "ARC_VENT", "count": 1}]
                expected = "boss room has hazards"
            elif kind == "boss_affix":
                next(row for row in boss["encounter"] if row["enemy_id"].startswith("BOSS_"))["affix"] = "BEACON"
                expected = "boss has an affix"
            elif kind == "unknown_hazard":
                room["hazards"][0]["type"] = "MISSING_HAZARD"
                expected = "unknown hazard id"
            elif kind == "unknown_affix":
                affix_rows(changed)[0]["affix"] = "MISSING_AFFIX"
                expected = "unknown affix id"
            else:
                room["hazards"][0]["count"] = 0
                expected = "invalid hazard count"
            with self.subTest(control=kind):
                self.assertIn(expected, current_mission_errors(changed, self.hazards, self.affixes))

    def test_placement_commit_paths_have_synthetic_negative_controls(self):
        paths = sorted(PLACEMENT_PATHS)
        self.assertEqual([], placement_commit_errors(paths))
        for prefix in PROTECTED_PATHS:
            self.assertIn("placement commit touches protected art/visual paths",
                          placement_commit_errors(paths + [prefix + "synthetic_control.txt"]))
        self.assertIn("placement commit does not touch exactly missions 06-09",
                      placement_commit_errors(paths + ["data/missions/MIS_CH01_03.json"]))
        self.assertIn("placement commit does not touch exactly missions 06-09", placement_commit_errors(paths[:-1]))


if __name__ == "__main__":
    unittest.main()
