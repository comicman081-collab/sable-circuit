#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ERRORS: list[str] = []


def require_file(rel: str, needles: list[str]) -> None:
    path = ROOT / rel
    if not path.is_file():
        ERRORS.append(f"missing M9 contract file: {rel}")
        return
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            ERRORS.append(f"{rel} missing M9 contract token: {needle}")


require_file(
    "scripts/combat/operator_skill_controller.gd",
    [
        "class_name OperatorSkillController",
        '"ultimate_key":"X"',
        '"reload_key":"R"',
        '"ASTER_PRISM_LOCK"',
        '"ROOK_BREACH_MOMENTUM"',
        '"MICA_SENSOR_FEEDBACK"',
        '"EXPOSED_EXPLOIT"',
        '"EXPOSED_CONSUMED_STAGGER"',
        '"MICA_PULSE_SCAN"',
        '"ASTER_PRISM"',
        '"ROOK_BREACH_SLAM"',
        '"MICA_SENSOR_BLOOM"',
    ],
)
require_file(
    "scripts/actors/enemy_actor.gd",
    [
        "func apply_exposed",
        "func is_exposed",
        "func apply_stagger",
        "func is_staggered",
        "func consume_exposed_for_stagger",
    ],
)
require_file(
    "scripts/actors/squad_controller.gd",
    [
        "const MAX_ENERGY := 100.0",
        "func add_energy",
        "func spend_energy",
    ],
)
require_file(
    "scripts/ui/story_stage_hud.gd",
    [
        'var keys: Array[String] = ["Q","E","X"]',
        '"reload_key":"R"',
        '"X READY"',
    ],
)
require_file(
    "tests/smoke/m9_operator_skill_synergy_smoke.gd",
    [
        "M9_OPERATOR_SKILL_SYNERGY_SMOKE: PASS",
        "MICA SENSOR FEEDBACK",
        "ASTER PRISM LOCK",
        "ROOK BREACH MOMENTUM",
    ],
)
require_file(
    "tests/render/m9_skill_capture.gd",
    [
        "28_m9_mica_exposed.png",
        "29_m9_aster_exploit.png",
        "30_m9_rook_stagger.png",
        "31_m9_ultimate_ready.png",
        "M9_SKILL_CAPTURE: PASS",
    ],
)

profile_path = ROOT / "data" / "art_profiles" / "playable_profiles.json"
if not profile_path.is_file():
    ERRORS.append("missing playable art profile registry")
else:
    try:
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        profiles = payload.get("profiles", [])
        if len(profiles) != 3:
            ERRORS.append(f"M9 requires exactly 3 playable profiles, got {len(profiles)}")
        seen: set[str] = set()
        expected = {
            "CHR_PROTO_01": ["aster_prism.svg", "aster_vector_dash.svg", "aster_overclock.svg"],
            "CHR_PROTO_02": ["rook_breach_slam.svg", "rook_bulwark.svg", "rook_scatter_cycle.svg"],
            "CHR_PROTO_03": ["mica_pulse_scan.svg", "mica_relay_step.svg", "mica_sensor_bloom.svg"],
        }
        for profile in profiles:
            actor_id = str(profile.get("actor_id", ""))
            icons = [Path(str(v)).name for v in profile.get("hud_action_icon_assets", [])]
            if icons != expected.get(actor_id, []):
                ERRORS.append(f"{actor_id} M9 skill icon order mismatch: {icons}")
            for raw_path in profile.get("hud_action_icon_assets", []):
                rel = str(raw_path)
                if rel in seen:
                    ERRORS.append(f"reused playable skill icon path: {rel}")
                seen.add(rel)
                if not (ROOT / rel).is_file():
                    ERRORS.append(f"missing playable skill icon asset: {rel}")
        if len(seen) != 9:
            ERRORS.append(f"M9 requires 9 unique skill icon paths, got {len(seen)}")
    except Exception as exc:
        ERRORS.append(f"could not parse playable profiles: {exc}")

if ERRORS:
    print("M9_SKILL_CONTRACT_VALIDATION: FAIL")
    for error in ERRORS:
        print(" -", error)
    sys.exit(1)

print("M9_SKILL_CONTRACT_VALIDATION: PASS")
print("checked 3 passives, Q/E/X contracts, EXPOSED/STAGGER synergy, shared energy, and 9 unique skill icons")
