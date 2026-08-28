# M10 — Intel Analysis & Operator Loadout

## Goal

M10 closes the GDD P5 loop: **field discovery must feed permanent progression**.

The authoritative loop is:

`Enemy discovery → unsecured intel sample → extraction → Lab analysis → weakness/module unlock → Armory equip → next deployment combat effect`

No part of this loop is presentation-only. Samples, analysis costs, unlocked weaknesses, unlocked modules and equipped loadouts live in `CampaignProgression` and are persisted under the existing campaign save.

## Field intel families

| Family | Stage-01 source | Run farming rule |
| --- | --- | --- |
| SECURITY | first unique Rifle / Shield / Drone identity | one sample per unique enemy ID per run |
| ABERRANT | first unique Aberrant identity | one sample per unique enemy ID per run |
| ANCHOR | Signal Anchor Guardian | one sample per unique enemy ID per run |

A repeated kill of the same identity does not produce another sample in the same run.

Intel is **risk cargo**. Deliberate extraction secures all carried samples. A squad wipe secures zero intel samples. This is intentionally stricter than common research/salvage emergency recovery and matches the high-value discovery fantasy.

## Data-driven analyses

Definitions live in `data/progression/intel_discoveries.json`.

### SECURITY ARC-GAP MAPPING

- Cost: 2 SECURITY samples + 120 Research
- Weakness: `SECURITY_ARC_GAP`
- Module: `MOD_PRISM_FOCUS`
- Operator: ASTER
- Effect: additional +15% ASTER damage against EXPOSED security targets.

### ABERRANT JOINT STRESS MAP

- Cost: 1 ABERRANT sample + 140 Research
- Weakness: `ABERRANT_JOINT_MAP`
- Module: `MOD_BREACH_LINER`
- Operator: ROOK
- Effect: EXPOSED-consuming Breach Slam becomes 52 damage and 3.0 seconds of STAGGER.

### ANCHOR SIGNAL MODEL

- Cost: 1 ANCHOR sample + 180 Research
- Weakness: `ANCHOR_SIGNAL_MODEL`
- Module: `MOD_SENSOR_ARRAY`
- Operator: MICA
- Effect: Pulse Scan radius 420→500 and EXPOSED duration 6→8 seconds; Sensor Bloom EXPOSED duration 10→12 seconds.

## Analysis authority

`CampaignProgression.analyze_intel()` is the only analysis transaction.

It must:

1. Resolve a registry definition.
2. Reject unknown or already-analyzed IDs.
3. Verify actual Research and sample inventory.
4. Deduct both costs exactly once.
5. Unlock both the weakness and associated module.
6. Persist the result.

Analysis cannot produce negative resources and cannot be repeated for duplicate rewards.

## Loadout authority

`CampaignProgression.equip_module()` is the only loadout transaction.

Rules:

- Locked modules cannot be equipped.
- A module can only be equipped by its authored operator.
- Empty/`NONE` removes the current module.
- Equipped module IDs persist in campaign state.
- `StoryStage01.configure_campaign()` injects the saved module ID into each operator at deployment.
- Operator/skill/projectile gameplay code reads the injected module ID to apply the real combat modifier.

## Retained M8 extraction fix

M10 audit found a data drift bug in the earlier extraction-window contract. Code aliases used `R04_JUNCTION` and `R05_CORE_C`, while the authoritative mission JSON uses `R04_CONTAINMENT` and `R05_CORE`.

The runtime checkpoint list is now exactly:

1. `R03_ARCHIVE`
2. `R04_CONTAINMENT`
3. `R05_CORE`

`tools/validate_m10_intel_contract.py` derives the RESEARCH / ELITE / BOSS checkpoint IDs from `MIS_CH01_01.json` and fails CI if the runtime constant drifts again.

## UI contract

### Field HUD

Top-right risk cargo readout includes:

`INTEL  SEC ##   ABR ##   ANC ##`

The count represents unsecured run cargo, not permanent Base inventory.

### Mission Results

Results distinguish:

- secured SECURITY / ABERRANT / ANCHOR samples,
- lost intel samples on wipe,
- permanent Base intel inventory after campaign commit.

### Operations Base

The lower progression panel is:

`FIELD INTEL → LAB ANALYSIS → ARMORY LOADOUT`

It shows actual sample inventory, research/sample costs, analysis completion state and ASTER / ROOK / MICA module equip state.

## Validation gates

M10 adds:

- `tools/validate_m10_intel_contract.py`
- `tests/smoke/m10_intel_loadout_smoke.gd`
- `tests/render/m10_progression_capture.gd`

The M10 visual evidence extends the retained runtime evidence set to 34 real 1280×720 Godot screenshots:

- `32_m10_lab_analysis_ready.png`
- `33_m10_armory_loadout.png`
- `34_m10_field_intel_loadout.png`

Public Pages deployment remains disabled.
