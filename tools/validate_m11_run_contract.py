#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def need(rel: str, tokens: list[str]) -> str:
    path = ROOT / rel
    if not path.is_file():
        ERRORS.append(f"missing M11 contract file: {rel}")
        return ""
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            ERRORS.append(f"{rel} missing M11 token: {token}")
    return text


registry = ROOT / "data" / "progression" / "run_modifiers.json"
if not registry.is_file():
    ERRORS.append("missing M11 run modifier registry")
else:
    try:
        data = json.loads(registry.read_text(encoding="utf-8"))
        hazards = data.get("hazards", [])
        opportunities = data.get("opportunities", [])
        boosts = data.get("run_only_boosts", [])
        if len(hazards) != 4:
            ERRORS.append(f"M11 requires exactly four hazards, got {len(hazards)}")
        if len(opportunities) != 4:
            ERRORS.append(f"M11 requires exactly four opportunities, got {len(opportunities)}")
        if len(boosts) != 2:
            ERRORS.append(f"M11 requires exactly two run-only boosts, got {len(boosts)}")

        ids: set[str] = set()
        for row in hazards + opportunities + boosts:
            rid = str(row.get("id", ""))
            if not rid:
                ERRORS.append("M11 modifier row missing id")
            elif rid in ids:
                ERRORS.append(f"duplicate M11 modifier id: {rid}")
            ids.add(rid)

        for row in hazards:
            if float(row.get("reward_multiplier", 0.0)) < 1.0:
                ERRORS.append(f"hazard reward multiplier must be >= 1: {row.get('id')}")
            difficulty = [
                float(row.get("enemy_health_multiplier", 1.0)),
                float(row.get("enemy_damage_multiplier", 1.0)),
                float(row.get("enemy_speed_multiplier", 1.0)),
                float(row.get("enemy_attack_interval_multiplier", 1.0)),
            ]
            if all(abs(v - 1.0) < 1e-9 for v in difficulty):
                ERRORS.append(f"hazard must change gameplay difficulty: {row.get('id')}")

        sources = {str(row.get("source_room", "")) for row in boosts}
        if sources != {"O01_SUPPLY", "O02_RESEARCH"}:
            ERRORS.append(f"run-only boost sources drift from optional rooms: {sources}")
    except Exception as exc:
        ERRORS.append(f"could not parse M11 run modifier registry: {exc}")

need("scripts/core/run_contract.gd", [
    "class_name RunContract", "func build", "_stable_hash", "enemy_health_multiplier",
    "research_reward_multiplier", "run_only_boosts",
])
need("scripts/missions/story_stage_01.gd", [
    "_configure_run_contract", "enemy.apply_run_modifiers", "_activate_run_boost_for_room",
    "_apply_active_run_boosts", "run_only_boosts_expire_on_return", "active_run_boosts",
])
need("scripts/actors/enemy_actor.gd", [
    "apply_run_modifiers", "run_health_multiplier", "run_damage_multiplier",
    "run_speed_multiplier", "run_attack_interval_multiplier", "debug_run_modifier_contract",
])
need("scripts/actors/operator_actor.gd", [
    "apply_run_boosts", "run_primary_damage_multiplier", "run_incoming_damage_multiplier",
    "run_speed_multiplier", "debug_run_boost_contract",
])
need("scripts/actors/squad_controller.gd", [
    "run_energy_gain_multiplier", "configure_run_energy_multiplier", "apply_run_multiplier",
])
need("scripts/core/game_flow.gd", ["RunContract.build", "last_run_contract"])
need("scripts/combat/operator_skill_controller.gd", [
    'add_energy(100.0,"ultimate_refund",false)',
])
need("tests/smoke/m11_run_contract_smoke.gd", ["M11_RUN_CONTRACT_SMOKE: PASS"])

campaign_text = need("scripts/core/campaign_progression.gd", ["SAVE_SCHEMA_VERSION"])
for forbidden in ["run_contract", "active_run_boosts", "run_energy_gain_multiplier", "run_primary_damage_multiplier"]:
    if forbidden in campaign_text:
        ERRORS.append(f"run-only M11 state leaked into CampaignProgression persistence: {forbidden}")

if ERRORS:
    print("M11_RUN_CONTRACT_VALIDATION: FAIL")
    for error in ERRORS:
        print(" -", error)
    sys.exit(1)

print("M11_RUN_CONTRACT_VALIDATION: PASS")
print("checked deterministic run data, gameplay authority, optional boosts, and non-persistence")
