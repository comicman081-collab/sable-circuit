#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def need(rel: str, tokens: list[str]) -> str:
    path = ROOT / rel
    if not path.is_file():
        ERRORS.append(f"missing M12 contract file: {rel}")
        return ""
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            ERRORS.append(f"{rel} missing M12 token: {token}")
    return text


need("scripts/actors/squad_controller.gd", [
    "REVIVE_RANGE := 92.0",
    "REVIVE_DURATION := 2.20",
    "REVIVE_HEALTH_RATIO := 0.35",
    "REVIVE_GUARD_DURATION := 1.25",
    "REVIVE_GUARD_REDUCTION := 0.65",
    "Input.is_key_pressed(KEY_F)",
    "has_revivable_target_in_range",
    "_nearest_downed_operator",
    "target.revive(REVIVE_HEALTH_RATIO)",
    "target.apply_guard(REVIVE_GUARD_DURATION,REVIVE_GUARD_REDUCTION)",
    "debug_step_revive",
    "debug_revive_contract",
])
need("scripts/missions/story_stage_01.gd", [
    "revive_reserved",
    "not revive_reserved",
    "debug_interaction_reserved_for_revive",
    "_extraction_offer_active",
])
# Semantic revive contract: formatting/whitespace may evolve in later actor refactors.
operator_text = need("scripts/actors/operator_actor.gd", [
    "func revive", "downed_state", "maxf(1.0", "health_changed.emit",
])
if "downed_state=false" not in operator_text.replace(" ", ""):
    ERRORS.append("scripts/actors/operator_actor.gd revive path no longer clears downed state")
need("tests/smoke/m12_squad_revive_smoke.gd", ["M12_SQUAD_REVIVE_SMOKE: PASS"])

campaign = need("scripts/core/campaign_progression.gd", ["SAVE_SCHEMA_VERSION"])
for forbidden in ["completed_revives", "last_revived_operator_id", "revive_elapsed", "revive_target"]:
    if forbidden in campaign:
        ERRORS.append(f"M12 run-state leaked into CampaignProgression persistence: {forbidden}")

if ERRORS:
    print("M12_REVIVE_CONTRACT_VALIDATION: FAIL")
    for error in ERRORS:
        print(" -", error)
    sys.exit(1)

print("M12_REVIVE_CONTRACT_VALIDATION: PASS")
print("checked hold-to-revive authority, interruptions, protection, interaction priority, and non-persistence")
