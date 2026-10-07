"""Draft, but do not reserve, the exact R1 contact_l ImageGen repair scope."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g
import visible_frame_harness as frozen
import visible_frame_harness_current as current

ANCHORS = {
    "left": "anatomical LEFT leg: dark thigh equipment with NO beige vertical plate",
    "right": "anatomical RIGHT leg: thigh pouch with the beige vertical plate",
}


def main(args):
    guide = g.read(args.guide)
    errors = current._audit_pose_guide_current(guide, "E", "run", "contact_l")
    if errors:
        raise ValueError("POSE_GUIDE_NOT_CURRENTLY_APPROVED:" + ",".join(errors))
    out = g.local(args.out)
    out.mkdir(parents=True, exist_ok=False)
    preserve = [
        "R1 face, skin, brown braid, body proportions, E-facing head/torso/pelvis alignment",
        "R1 navy patterned long coat, pale beige trim, teal lining, guards, boots and cyan devices",
        "R1 rifle design, two-hand grip, right-facing main barrel axis and visible muzzle",
        "R1 anatomical laterality: plate-free LEFT leg leads and beige-plate RIGHT leg trails",
        "R1 1024x1536 canvas, pelvis/waist and LEFT hip/upper-thigh region, broad stride, raised trailing RIGHT boot and uniform chroma background",
    ]
    change = [
        "only the leading anatomical LEFT knee-to-boot contact chain below the preserved upper thigh: rotate the foot about its ankle and, only if needed, coherently adjust the connected shin without stretching or detaching; make at least 50 horizontal sole pixels meet y=1250 plus or minus 2 on the 1024x1536 target while nothing extends below y=1252; keep the trailing RIGHT boot bottom at least 80 pixels above that baseline",
        "only the missing approved pair of vertical cyan-lit back devices: restore exactly two from the true-E authority behind the upper torso",
    ]
    prompt = f"""Edit the FIRST supplied image as the immutable primary target. Do not redraw or replace the whole character. Every resulting visible pixel remains built-in ImageGen work; the fourth Blender+UAL image is lower-body geometry guidance only and its person, mechanical arms, hair, clothes, bare feet, props, backpack and materials must never appear.

Requested phase remains east-facing run contact_l: left foot initial contact; right leg trailing; left begins support.

Preserve exactly:
- {preserve[0]}
- {preserve[1]}
- {preserve[2]}
- {preserve[3]}
- {preserve[4]}
- {ANCHORS['left']}
- {ANCHORS['right']}

Change exactly two localized regions and nothing else:
1. {change[0]}. The independently measured target baseline is the exact R1 non-green subject minimum y=1250. Preserve the pelvis/waist and LEFT hip/upper-thigh region; do not translate the whole leg from the hip. Match the fourth reference's contact_l support relation with a natural sagittal heel/sole angle. This is not flight, marching, skating, or a high kick.
2. {change[1]}. Match their count, placement, dark material and cyan strips to the SECOND/THIRD approved MICA references. Do not create extra rods, wings, shoulder armor or a backpack.

Do not swap the thigh markers, legs, or coat sides. Do not change the face, braid, torso, hands, rifle, muzzle, coat design, colors, body scale or strict E profile. No crossed shins, calf inflation, 90-degree ankle/waist twist, extra limbs, detached panels, floor, shadow, scenery, text, gradient, border, green spill, or multiple variants. Keep one full-body subject on perfectly uniform chroma green.
"""
    prompt_path = out / "PROMPT.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    target = g.ref(args.repair_target)
    identity = g.ref("art_src/characters/mica/rigged_v2/source_front_r1/MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png")
    direction = g.ref("art_src/characters/mica/rigged_v1/source/MICA_C03_E_TRUE_PROFILE_GREEN_V1.png")
    request = {
        "schema": 1, "stage": "visible_frame_request", "operation": "repair_failed_frame",
        "qa_fixture_only": False, "generator": "built_in_ImageGen",
        "actor_id": "CHR_PROTO_03", "costume_id": "MICA_RECON_C03",
        "direction": "E", "motion": "run", "phase": "contact_l",
        "phase_definition": guide["phase_definition"],
        "anatomical_laterality_anchors": ANCHORS,
        "attempt_revision": 3, "max_unreviewed_outputs": 1,
        "source_receipt": g.ref("art_src/characters/mica/rigged_v2/source_front_r1/SOURCE_RECEIPT_R7.json"),
        "pose_guide": guide,
        "repair_target": target,
        "repair_target_quarantine_manifest": g.ref(args.quarantine_manifest),
        "repair_preserve_exact": preserve,
        "repair_change_only": change,
        "supporting_references": [{"role": "direction_reference", **direction}],
        "previous_failure": g.ref(args.previous_failure),
        "imagegen_input_order": [
            {"role": "repair_target_primary", **target},
            {"role": "approved_source_identity", **identity},
            {"role": "direction_reference", **direction},
            {"role": "licensed_pose_guide", **guide["image"]},
        ],
        "mechanism_changes": [
            "stop whole-frame new-author retries after independent review of two failures",
            "use correct-laterality R1 as immutable primary edit target and exclude reversed-laterality R2",
            "limit edits to planted LEFT ankle/boot geometry and restoration of the exact two approved back devices",
            "bind the R12 actual fixed-floor contact guide and preserve every unlisted R1 region",
        ],
        "prompt": g.ref(prompt_path),
        "background": "uniform_chroma_green",
        "output_root": out.relative_to(ROOT).as_posix(),
        "expected_raw_path": (out / "MICA_C03_E_RUN_CONTACT_L_ASTRA_R3_REPAIR_IMAGEGEN_RAW.png").relative_to(ROOT).as_posix(),
    }
    draft = out / "DRAFT_REQUEST_REQUIRES_REPAIR_SCOPE_REVIEWS.json"
    g.write(draft, request)
    subject = frozen.repair_target_subject(request)
    g.write(out / "REPAIR_TARGET_SUBJECT.json", {
        "schema": 1,
        "status": "HOLD_REQUIRES_VISUAL_AND_PONYTAIL_FULL_REVIEWS",
        "repair_target_subject_sha256": subject,
        "draft_request": g.ref(draft),
        "visible_art_generated": False,
    })
    print(subject)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide", required=True)
    parser.add_argument("--repair-target", required=True)
    parser.add_argument("--quarantine-manifest", required=True)
    parser.add_argument("--previous-failure", required=True)
    parser.add_argument("--out", required=True)
    main(parser.parse_args())
