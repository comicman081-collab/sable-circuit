# Ponytail FULL — MICA ratio-chroma matte mechanism R4

- Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
- UTC: **2026-09-07T17:09:13Z** (2026-09-08 02:09:13 KST).
- Applied skill: `sable-motion-production`.
- Verdict: **PASS_LIMITED_MATTING_MECHANISM_CHECKS_FOR_THIS_EXACT_OUTPUT**.
- **Strict-E whole-body direction remains HOLD; this is not a PASS frame receipt or promotion authorization.**

## Actual scope and evidence

I directly opened the preserved exact-green master and new `RUNTIME_RGBA_RATIO_R4.png` at their original 1254×1254 scale. I read the current `derive_chroma_runtime_rgba.py` end to end, its emitted QA, the prior R3 seven-check review, and the earlier connected-matte counterexample report. Read-only independent PIL/NumPy checks decoded the raw/master/old and new RGBA; they did not call the producer's `background_mask`.

Only this report was written. No source/code/candidate mutation, generation, rendering, runtime or Luna execution occurred. No new native 1920×1080 light/dark R4 review package was supplied for this narrow mechanism task, so this report does not approve that presentation gate or the complete frame gate.

## Bounded checks

| Check | Verdict | Actual finding |
| --- | --- | --- |
| Eight previously ambiguous cyan-edge pixels | PASS | All eight are now alpha 255 and RGB-identical to both raw and preserved master; exact values below. |
| Dark chroma-fringe removal retained | PASS, boundary class | In the current native image, the independently selected dark-green class has 208 pixels: 205 transparent, 3 retained inside the subject, **0 retained on the alpha boundary**. Examples at `(502,250)=(10,39,12)`, `(1137,395)=(11,52,4)`, `(1075,407)=(7,40,2)`, `(670,733)=(5,23,4)` remain transparent. Interior pixels are not erased merely to obtain a global zero. |
| Strong-green alpha boundary | PASS, exact predicate | Independently counted **0**, matching QA. There are 30 retained interior matches. This is not a claim that every possible green tint is zero. |
| Reproducibility / retained RGB | PASS | Independent synchronous four-neighbour reconstruction converged in 10 expansion rounds; saved alpha mismatches **0**. Visible RGB differences from master **0**, and from raw **0**. |
| Visible subject / halo inspection | PASS, limited native inspection | The thin cyan back-device strip is present, as are forearm and shin lights, teal coat lining, hair, hands, weapon, coat and boots. No obvious new missing subject chunk or unmistakable dark-green edge halo was established in the directly opened native comparison. This is not a semantic proof for every removed pixel. |

Relative to the prior R3 derivative, **309 pixels become visible and zero previously visible pixels are newly deleted**. Alpha is binary: **1,272,990 transparent and 299,526 opaque**, no intermediate values. The entire outer border is transparent; transparent RGB is zero. Input/output hashes and counts agree with the supplied QA.

### Exact eight-pixel comparison

All entries were `(0,0,0,0)` in the prior R3 derivative. The new alpha is **255** for every entry; raw, master and retained RGB are identical.

| Native coordinate `(x,y)` | Preserved RGB |
| --- | --- |
| `(564,185)` | `(129,239,210)` |
| `(563,192)` | `(133,230,211)` |
| `(562,199)` | `(106,225,204)` |
| `(561,205)` | `(117,231,211)` |
| `(560,211)` | `(117,227,198)` |
| `(560,212)` | `(140,233,217)` |
| `(559,218)` | `(120,228,205)` |
| `(558,222)` | `(39,175,154)` |

## Mechanism and limits

The new green-vs-red and green-vs-blue ratio checks, `4G >= 5R` and `4G >= 5B`, apply to both bright seeds and the connected chroma family. This excludes the eight cyan-family edge values above while retaining the low-luminance green-fringe class. The existing absolute differences, green minimum and four-neighbour connectivity remain in place; exact-green master pixels are not repainted.

The independently evaluated strong-green family is `G>=12`, `G-R>=16`, `G-B>=16`, `4G>=5R`, `4G>=5B`. The separate dark counterexample class additionally uses `G<=64`, `R<=12`, `B<=12`. The alpha boundary is the visible pixel set adjacent to transparency in four directions. Zero boundary matches are partly a consequence of connected growth, not independent visual ground truth; actual native inspection and preservation/removal samples are therefore reported separately. The ratio rule is not universal semantic matting authority for future sources or differently colored costumes.

## Exact hashes

Candidate root: `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r3_e_flight_l_profile_repair/`.

| Artifact | SHA-256 |
| --- | --- |
| `MICA_C03_E_RUN_FLIGHT_L_PROFILE_REPAIR_R3_IMAGEGEN_RAW.png` | `274d14d3e1fc45718b099447d087404063cdbea09eb3d3f4b1fccdb5857ff82c` |
| `...EXACT_GREEN.png` | `0248c794186c4513b3907f3f41d2e8d14703c6a664e921be7dbe0a1deb65978d` |
| Previous `...RUNTIME_RGBA.png` | `647fb840cb287a4705cd8f2c44563b6333cf8e813f0c91241923b7fa58a1516e` |
| Reviewed `...RUNTIME_RGBA_RATIO_R4.png` | `c4d17fdd5e14e88162e36ff8d204e95aa3d4b893f83245eec64b104f3a904ab7` |
| `...RUNTIME_RGBA_RATIO_R4_QA.json` | `4caab9bd190af6ed55f46ece428d1847e4d6df3bf5de65d61c83673a190ea170` |
| Current `tools/character_pipeline/derive_chroma_runtime_rgba.py` | `a72d94d664ccc536d2f84fa1c713c3cd91bc8cbc26e4283fc0450bd2fd74e603` |
| Prior `PONYTAIL_MICA_C03_E_FLIGHT_L_PROFILE_REPAIR_R3_FRAME_REVIEW.md` | `7e6fc0041b09a650f383af7c8d1500e1ed3a16458f9e7915b90eb569f2a7cfff` |

The prior exact frame subject `d2c7a34c8f6e72168ee988647200bb75ef17457d1f8d92d8ad6d73d26dc07e20` binds the old derivative, not this new R4 output. Do not silently reuse that audit as authorization for replacement bytes. Its whole-body E-direction HOLD is unaffected; no temporal gait, grounding, firing, runtime, HTML or Luna approval is given here.

Signed: `/root/ponytail_motion_audit` — Ponytail FULL independent limited matte review.
