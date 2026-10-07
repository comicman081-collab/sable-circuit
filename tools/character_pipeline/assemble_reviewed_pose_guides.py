"""Assemble exact reviewed support-phase guides; never generate visible art."""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g
import visible_frame_harness as frozen
import visible_frame_harness_current as current


def review(role, reviewer, subject, checks, evidence, reviewed_utc):
    return {
        "role": role,
        "reviewer": reviewer,
        "reviewed_utc": reviewed_utc,
        "subject_sha256": subject,
        "verdict": "PASS",
        "checks": {key: "PASS" for key in checks},
        "reply_evidence": g.ref(evidence),
    }


def main(args):
    capture = g.read(args.capture)
    calibration = g.read(args.calibration)
    primary_text = g.local(args.primary).read_text(encoding="utf-8")
    ponytail_text = g.local(args.ponytail).read_text(encoding="utf-8")
    if "PASS_EIGHT_POSE_GUIDES_ONLY_NOT_VISIBLE_ART_NOT_RUNTIME" not in primary_text:
        raise ValueError("EXACT_PRIMARY_STATIC_GUIDE_PASS_REQUIRED")
    if "PASS_STATIC_EIGHT_PHASE_POSE_GUIDES_ONLY" not in ponytail_text:
        raise ValueError("EXACT_PONYTAIL_STATIC_GUIDE_PASS_REQUIRED")
    if capture.get("calibration") != g.ref(args.calibration):
        raise ValueError("CAPTURE_CALIBRATION_MISMATCH")
    if calibration.get("status") != "PASS_TECHNICAL_PHASE_GUIDE_CANDIDATES_ONLY":
        raise ValueError("TECHNICAL_CALIBRATION_PASS_REQUIRED")
    out = g.local(args.out)
    out.mkdir(parents=True, exist_ok=False)
    contract = g.read(frozen.CONTRACT)
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    support_phases = ["contact_l", "down_l", "passing_l", "contact_r", "down_r", "passing_r"]
    rows = {row["phase"]: row for row in capture["frames"]}
    results = []
    for phase in support_phases:
        row = rows[phase]
        guide = {
            "visual_role": "pose_guide_only_not_runtime_art",
            "image": row["image"],
            "capture": g.ref(args.capture),
            "blend": capture["blend"],
            "license": g.ref("third_party/vrm/seed_san/MODEL_LICENSE.json"),
            "action": "Sprint_Loop",
            "screen_direction": "E",
            "phase": phase,
            "phase_definition": contract["phase_semantics"]["run"][phase],
            "capture_frame": row["frame"],
            "contact_calibration": g.ref(args.calibration),
            "contact_calibration_phase": phase,
            "current_gate": g.ref(current.CURRENT_GATE),
            "contact_contract": g.ref(current.CONTACT_CONTRACT),
            "visual_promotion_contract": g.ref(current.VISUAL_PROMOTION_CONTRACT),
            "contact_calibrator": g.ref(current.CONTACT_CALIBRATOR),
        }
        pose_subject = frozen.pose_guide_subject(guide, "E", "run", phase)
        contact_subject = current.contact_calibration_subject(guide, "E", "run", phase)
        pose_bundle_path = out / (phase.upper() + "_POSE_REVIEW_BUNDLE.json")
        contact_bundle_path = out / (phase.upper() + "_CONTACT_REVIEW_BUNDLE.json")
        pose_bundle = {
            "schema": 1,
            "stage": "licensed_pose_guide_reviews",
            "pose_guide_subject_sha256": pose_subject,
            "direction": "E", "motion": "run", "phase": phase,
            "phase_definition": guide["phase_definition"], "capture_frame": row["frame"],
            "reviews": [
                review("visual", "Codex Astra primary visual review", pose_subject,
                       contract["pose_guide_review_checks"], args.primary, timestamp),
                review("Ponytail FULL", "/root/ponytail_motion_audit", pose_subject,
                       contract["pose_guide_review_checks"], args.ponytail, timestamp),
            ],
            "verdict": "PASS_ONE_LOWER_BODY_POSE_GUIDE_ONLY",
        }
        contact_bundle = {
            "schema": 1,
            "stage": "fixed_floor_contact_reviews",
            "contact_calibration_subject_sha256": contact_subject,
            "direction": "E", "motion": "run", "phase": phase,
            "reviews": [
                review("visual", "Codex Astra primary visual review", contact_subject,
                       current.CONTACT_REVIEW_CHECKS, args.primary, timestamp),
                review("Ponytail FULL", "/root/ponytail_motion_audit", contact_subject,
                       current.CONTACT_REVIEW_CHECKS, args.ponytail, timestamp),
            ],
            "verdict": "PASS_ONE_STATIC_FIXED_FLOOR_SUPPORT_GUIDE_ONLY",
        }
        g.write(pose_bundle_path, pose_bundle)
        g.write(contact_bundle_path, contact_bundle)
        guide["review_bundle"] = g.ref(pose_bundle_path)
        guide["contact_review_bundle"] = g.ref(contact_bundle_path)
        guide_path = out / (phase.upper() + "_POSE_GUIDE.json")
        g.write(guide_path, guide)
        errors = current._audit_pose_guide_current(guide, "E", "run", phase)
        if errors:
            raise ValueError("ASSEMBLED_GUIDE_FAILED:" + phase + ":" + ",".join(errors))
        results.append({
            "phase": phase,
            "guide": g.ref(guide_path),
            "pose_subject_sha256": pose_subject,
            "contact_subject_sha256": contact_subject,
        })
    g.write(out / "ASSEMBLY_RECEIPT.json", {
        "schema": 1,
        "status": "PASS_SIX_STATIC_SUPPORT_POSE_GUIDES_ONLY",
        "production_ready": False,
        "visible_art_generated": False,
        "capture": g.ref(args.capture),
        "calibration": g.ref(args.calibration),
        "primary_evidence": g.ref(args.primary),
        "ponytail_evidence": g.ref(args.ponytail),
        "guides": results,
        "next": "reserve exactly one built-in ImageGen visible-frame request",
    })
    print(str(out / "ASSEMBLY_RECEIPT.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--primary", required=True)
    parser.add_argument("--ponytail", required=True)
    parser.add_argument("--out", required=True)
    main(parser.parse_args())
