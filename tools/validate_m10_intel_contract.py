#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

def need(rel: str, tokens: list[str]) -> str:
    path = ROOT / rel
    if not path.is_file():
        ERRORS.append(f"missing M10 contract file: {rel}")
        return ""
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            ERRORS.append(f"{rel} missing M10 token: {token}")
    return text

discovery_path = ROOT / "data" / "progression" / "intel_discoveries.json"
if not discovery_path.is_file():
    ERRORS.append("missing M10 intel discovery registry")
else:
    try:
        payload = json.loads(discovery_path.read_text(encoding="utf-8")); rows = payload.get("discoveries", [])
        if len(rows) != 3: ERRORS.append(f"M10 requires exactly three discoveries, got {len(rows)}")
        analyses:set[str]=set(); modules:set[str]=set(); weaknesses:set[str]=set(); operators:set[str]=set(); samples:set[str]=set()
        expected={"ANL_SECURITY_ARC_GAP":("SECURITY","MOD_PRISM_FOCUS","CHR_PROTO_01"),"ANL_ABERRANT_JOINT_MAP":("ABERRANT","MOD_BREACH_LINER","CHR_PROTO_02"),"ANL_ANCHOR_SIGNAL_MODEL":("ANCHOR","MOD_SENSOR_ARRAY","CHR_PROTO_03")}
        for row in rows:
            aid=str(row.get("analysis_id","")); sample=str(row.get("sample_key","")); module=str(row.get("module_id","")); weakness=str(row.get("weakness_id","")); operator=str(row.get("operator_id",""))
            if aid in analyses: ERRORS.append(f"duplicate analysis id: {aid}")
            if module in modules: ERRORS.append(f"duplicate module id: {module}")
            if weakness in weaknesses: ERRORS.append(f"duplicate weakness id: {weakness}")
            analyses.add(aid); modules.add(module); weaknesses.add(weakness); operators.add(operator); samples.add(sample)
            if expected.get(aid)!=(sample,module,operator): ERRORS.append(f"M10 discovery ownership mismatch for {aid}: {(sample,module,operator)}")
            if int(row.get("sample_cost",0))<=0 or int(row.get("research_cost",0))<=0: ERRORS.append(f"M10 analysis costs must be positive: {aid}")
        if operators!={"CHR_PROTO_01","CHR_PROTO_02","CHR_PROTO_03"}: ERRORS.append(f"M10 discoveries must cover all three operators: {operators}")
        if samples!={"SECURITY","ABERRANT","ANCHOR"}: ERRORS.append(f"M10 discoveries must cover all intel families: {samples}")
    except Exception as exc: ERRORS.append(f"could not parse M10 intel discovery registry: {exc}")

campaign_text=need("scripts/core/campaign_progression.gd",["func analyze_intel","func equip_module",'"secured_intel"','"equipped_modules"','"unlocked_modules"','"unlocked_weaknesses"',"_sanitize_intel"])
stage_text=need("scripts/missions/story_stage_01.gd",['"SECURITY":0','"ABERRANT":0','"ANCHOR":0',"_award_enemy_intel",'"secured_intel"','"lost_intel_samples"','"intel_samples_lost_on_wipe"'])
need("scripts/actors/operator_actor.gd",["equipped_module_id","func has_module",'"module_id"'])
need("scripts/combat/operator_skill_controller.gd",['"MOD_PRISM_FOCUS"','"MOD_BREACH_LINER"','"MOD_SENSOR_ARRAY"','"mica_scan_radius":500.0','"rook_breach_damage":52.0','"aster_prism_focus_multiplier":1.15'])
need("scripts/combat/prototype_projectile.gd",["MOD_PRISM_FOCUS","_is_security_target"])
need("scripts/ui/story_stage_hud.gd",["set_intel_status","INTEL  SEC","debug_intel_text"])
# Semantic M10 Base contract: keep analysis/module actions and discovery panel;
# later milestones may rename visual headings or add sibling loadout controls.
need("scripts/ui/base_lobby.gd",["signal analysis_requested","signal module_equip_requested","_build_m10_progression_panel","DISCOVERY PIPELINE","debug_m10_contract"])
need("scripts/core/game_flow.gd",["_on_analysis_requested","_on_module_equip_requested","campaign.analyze_intel","campaign.equip_module"])
need("scripts/ui/mission_results.gd",["SECURED  INTEL","LOST INTEL SAMPLES"])
need("tests/smoke/m10_intel_loadout_smoke.gd",["M10_INTEL_LOADOUT_SMOKE: PASS","Core C actual node opens extraction window"])

mission_path=ROOT/"data"/"missions"/"MIS_CH01_01.json"
if mission_path.is_file() and stage_text:
    mission=json.loads(mission_path.read_text(encoding="utf-8")); authored=[str(row.get("id","")) for row in mission.get("main_route",[]) if str(row.get("type","")) in {"RESEARCH","ELITE","BOSS"}]
    match=re.search(r"const\s+EXTRACTION_OFFER_IDS\s*:=\s*\[(.*?)\]",stage_text)
    if not match: ERRORS.append("StoryStage01 missing parseable EXTRACTION_OFFER_IDS")
    else:
        code_ids=re.findall(r'"([^"]+)"',match.group(1))
        if code_ids!=authored: ERRORS.append(f"extraction window IDs drift from mission data: code={code_ids} mission={authored}")

if ERRORS:
    print("M10_INTEL_CONTRACT_VALIDATION: FAIL")
    for error in ERRORS: print(" -",error)
    sys.exit(1)
print("M10_INTEL_CONTRACT_VALIDATION: PASS")
print("checked intel families, analysis/module ownership, field risk, loadout authority, and mission-driven extraction IDs")
