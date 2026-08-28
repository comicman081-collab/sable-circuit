#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ERRORS=[]

def need(rel,tokens):
    p=ROOT/rel
    if not p.is_file(): ERRORS.append(f"missing M13 file: {rel}"); return ""
    text=p.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text: ERRORS.append(f"{rel} missing M13 token: {token}")
    return text

path=ROOT/"data/progression/weapons.json"
if not path.is_file(): ERRORS.append("missing M13 weapon registry")
else:
    try:
        data=json.loads(path.read_text(encoding="utf-8")); rows=data.get("weapons",[])
        if len(rows)!=6: ERRORS.append(f"MVP requires exactly 6 weapon specs, got {len(rows)}")
        ids=set(); classes=[]; defaults={}
        for row in rows:
            wid=str(row.get("weapon_id","")); cls=str(row.get("class","")); classes.append(cls)
            if not wid or wid in ids: ERRORS.append(f"invalid/duplicate weapon id: {wid}")
            ids.add(wid)
            if row.get("default_for"): defaults[str(row["default_for"])]=wid
            for key in ["damage","projectile_speed","projectile_lifetime","fire_interval","magazine_size","reload_duration","pellet_count","ammo_per_trigger","engagement_range"]:
                if float(row.get(key,0))<=0: ERRORS.append(f"{wid} invalid positive field: {key}")
            if not row.get("compatible_operators"): ERRORS.append(f"{wid} has no compatible operators")
        if sorted(classes)!=sorted(["AR","AR","SMG","SHOTGUN","LMG","SPECIAL"]): ERRORS.append(f"weapon class coverage mismatch: {classes}")
        if defaults!={"CHR_PROTO_01":"WPN_AR_COIL_01","CHR_PROTO_02":"WPN_SHOTGUN_MAG_01","CHR_PROTO_03":"WPN_SMG_SENSOR_01"}: ERRORS.append(f"default weapon ownership mismatch: {defaults}")
        burst=next((r for r in rows if r.get("weapon_id")=="WPN_AR_BURST_02"),{}); shotgun=next((r for r in rows if r.get("weapon_id")=="WPN_SHOTGUN_MAG_01"),{})
        if int(burst.get("pellet_count",0))!=3 or int(burst.get("ammo_per_trigger",0))!=3: ERRORS.append("burst rifle must emit and consume three rounds per trigger")
        if int(shotgun.get("pellet_count",0))!=5 or int(shotgun.get("ammo_per_trigger",0))!=1: ERRORS.append("shotgun must emit five pellets for one shell")
    except Exception as exc: ERRORS.append(f"weapon registry parse failed: {exc}")

need("scripts/data/weapon_registry.gd",["class_name WeaponRegistry","get_default_weapon","compatible_weapons","is_compatible"])
need("scripts/core/campaign_progression.gd",["SAVE_SCHEMA_VERSION := 3","unlocked_weapons","equipped_weapons","equip_weapon","cycle_weapon","armory_level>=1","armory_level>=2","WPN_LMG_HELIX_01","ANL_ANCHOR_SIGNAL_MODEL"])
need("scripts/actors/operator_actor.gd",["equipped_weapon_id","weapon_spec","_apply_weapon_loadout","ammo_per_trigger","pellet_count","projectile_speed","debug_weapon_contract"])
need("scripts/core/game_flow.gd",["weapon_cycle_requested","_inject_weapon_loadouts","weapon_id","debug_cycle_weapon"])
need("scripts/ui/base_lobby.gd",["signal weapon_cycle_requested","WeaponCycle_","NEXT WPN","debug_m13_weapon_contract"])
need("tests/smoke/m13_weapon_loadout_smoke.gd",["M13_WEAPON_LOADOUT_SMOKE: PASS"])

if ERRORS:
    print("M13_WEAPON_CONTRACT_VALIDATION: FAIL")
    for e in ERRORS: print(" -",e)
    sys.exit(1)
print("M13_WEAPON_CONTRACT_VALIDATION: PASS")
print("checked six MVP weapon specs, unlock/loadout authority, ammo semantics, deployment injection, and Base controls")
