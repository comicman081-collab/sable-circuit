"""Prepare one exact MICA E-run ImageGen request from a reviewed pose guide."""
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

PHASE_INSTRUCTIONS = {
    "contact_l": "The plate-free anatomical LEFT leg leads toward screen-right and begins support in a natural near-straight heel/sole arrival. The beige-plate RIGHT leg trails behind. Do not turn heel strike into a high kick.",
    "down_l": "The plate-free anatomical LEFT leg is planted under load with a visibly flexed knee and lower pelvis. The beige-plate RIGHT leg swings forward. Keep the planted sole near the fixed floor.",
    "passing_l": "The plate-free anatomical LEFT leg supports naturally while the beige-plate RIGHT swing leg passes it toward screen-right. Overlap may occur in profile, but do not cross or tangle the anatomical leg chains.",
    "contact_r": "The beige-plate anatomical RIGHT leg leads toward screen-right and begins support in a natural near-straight heel/sole arrival. The plate-free LEFT leg trails behind. Do not turn heel strike into a high kick.",
    "down_r": "The beige-plate anatomical RIGHT leg is planted under load with a visibly flexed knee and lower pelvis. The plate-free LEFT leg swings forward. Keep the planted sole near the fixed floor.",
    "passing_r": "The beige-plate anatomical RIGHT leg supports naturally while the plate-free LEFT swing leg passes it toward screen-right. Overlap may occur in profile, but do not cross or tangle the anatomical leg chains.",
}


def prompt_for(phase, definition):
    return f"""Author exactly one new production-candidate raster frame using the supplied references in exact order. The FIRST image is the approved MICA identity/costume authority. The SECOND image is the approved true E/right-facing profile authority. The THIRD image is a licensed Blender+UAL motion-geometry guide only. Never copy the third image's visible person, mechanical arms, hair, face, clothing, materials, bare feet, props, backpack, or surface appearance. Blender and UAL communicate lower-body geometry only; every visible pixel of MICA must be authored by built-in ImageGen from the first two approved MICA artworks.

Create one east-facing RUN {phase} frame on a perfectly flat, uniform chroma-key green background. Exact phase: {definition}.

Preserve these anatomical markers literally:
- {ANCHORS['left']}
- {ANCHORS['right']}

{PHASE_INSTRUCTIONS[phase]}

For contact phases specifically, the support boot must visibly meet one fixed
horizontal ground baseline even though that baseline is not drawn: place the
lowest support-sole pixels at the character's lowest body point. The support
boot is planted; the frame is not airborne. Do not show a floor or shadow.

Use a broad athletic running stride appropriate to this phase, coherent hip-knee-ankle chains, and natural sagittal ankle pitch. It must read as forward running, not tap dance, marching, skating, a split jump, tiny stepping, or tangled legs. Do not inflate calves, narrow the stride, lift either knee grotesquely, rotate either ankle sideways by 90 degrees, or let both feet face front.

Align the entire body as one strict right-facing E side profile: head, shoulders, ribcage, waist, pelvis, knees, boots, rifle and main barrel agree. No frontal torso/pelvis, 90-degree waist kink, counter-twist, body wobble, detached coat panels, duplicated limbs, or crossed shins.

Keep the approved MICA face, brown braid, navy patterned long coat, pale beige trim, teal lining, asymmetric thigh equipment, guards, boots, cyan devices, and established rifle. Keep one coherent two-hand rifle grip and a clearly visible main barrel tip pointing screen-right, distinct from lower auxiliary parts. Maintain empty margin beyond the muzzle and around both boots. Keep scale consistent with the approved source.

Background: flat uniform chroma green only. No scenery, floor, shadow, gradient, vignette, text, border, green glow, or reflected green spill. Produce one full-body character image, not a sheet, collage, diagram, or variants.
"""


def main(args):
    guide = g.read(args.guide)
    phase = guide.get("phase")
    if phase not in PHASE_INSTRUCTIONS or guide.get("screen_direction") != "E":
        raise ValueError("REVIEWED_E_SUPPORT_GUIDE_REQUIRED")
    errors = current._audit_pose_guide_current(guide, "E", "run", phase)
    if errors:
        raise ValueError("POSE_GUIDE_NOT_CURRENTLY_APPROVED:" + ",".join(errors))
    out = g.local(args.out)
    out.mkdir(parents=True, exist_ok=False)
    prompt_path = out / "PROMPT.txt"
    prompt_path.write_text(prompt_for(phase, guide["phase_definition"]), encoding="utf-8")
    stem = "MICA_C03_E_RUN_" + phase.upper() + "_ASTRA_R1"
    source_receipt = g.ref("art_src/characters/mica/rigged_v2/source_front_r1/SOURCE_RECEIPT_R7.json")
    identity = g.ref("art_src/characters/mica/rigged_v2/source_front_r1/MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png")
    direction = g.ref("art_src/characters/mica/rigged_v1/source/MICA_C03_E_TRUE_PROFILE_GREEN_V1.png")
    request = {
        "schema": 1, "stage": "visible_frame_request", "operation": "author_new_frame",
        "qa_fixture_only": False, "generator": "built_in_ImageGen",
        "actor_id": "CHR_PROTO_03", "costume_id": "MICA_RECON_C03",
        "direction": "E", "motion": "run", "phase": phase,
        "phase_definition": guide["phase_definition"],
        "anatomical_laterality_anchors": ANCHORS,
        "attempt_revision": args.attempt_revision, "max_unreviewed_outputs": 1,
        "source_receipt": source_receipt,
        "pose_guide": guide,
        "supporting_references": [{"role": "direction_reference", **direction}],
        "imagegen_input_order": [
            {"role": "approved_source_identity", **identity},
            {"role": "direction_reference", **direction},
            {"role": "licensed_pose_guide", **guide["image"]},
        ],
        "mechanism_changes": [
            "use exact R12 independently measured support phase rather than segmented legacy frames",
            "bind fixed-floor sole vertices and distinct contact/down metrics before ImageGen",
            "keep Blender UAL VRM appearance excluded and author every visible MICA pixel with built-in ImageGen",
        ],
        "prompt": g.ref(prompt_path),
        "background": "uniform_chroma_green",
        "output_root": out.relative_to(ROOT).as_posix(),
        "expected_raw_path": (out / (stem + "_IMAGEGEN_RAW.png")).relative_to(ROOT).as_posix(),
    }
    if args.attempt_revision > 1:
        if not args.previous_failure:
            raise ValueError("RETRY_PREVIOUS_FAILURE_REQUIRED")
        request["previous_failure"] = g.ref(args.previous_failure)
        request["mechanism_changes"].extend([
            "state that the planted support sole is the lowest body point on an invisible fixed baseline",
            "explicitly prohibit an airborne contact result while retaining no visible floor or shadow",
        ])
    request_path = out / "REQUEST.json"
    g.write(request_path, request)
    # Match CLI behavior: patch the frozen audit for the current process.
    frozen._audit_pose_guide = current._audit_pose_guide_current
    audit = frozen.audit_request(request_path)
    if audit["errors"]:
        raise ValueError("REQUEST_FAILED:" + ",".join(audit["errors"]))
    g.write(out / "REQUEST_AUDIT.json", audit)
    permit = frozen.reserve(request_path)
    g.write(out / "RESERVE_RESULT.json", permit)
    print(str(out / "RESERVE_RESULT.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--attempt-revision", type=int, default=1)
    parser.add_argument("--previous-failure")
    main(parser.parse_args())
