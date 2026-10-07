"""Seal reviewed repair scope and a real masked-edit boundary before reserve.

Reference images and natural-language preserve lists do not constrain the
built-in ImageGen editor to a local region.  A repair reservation therefore
requires an independently reviewed execution boundary which proves that the
selected generator can consume the exact binary change mask.  This prevents a
second whole-frame resynthesis from being authorized as a precise repair.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import generation_harness as g
import visible_frame_harness as frozen
import visible_frame_harness_current as current
import imagegen_repair_execution_boundary as repair_boundary


def main(args):
    draft = g.read(args.draft)
    boundary_ref = g.ref(args.execution_boundary)
    boundary_errors, _ = repair_boundary.audit_boundary(draft, boundary_ref)
    if boundary_errors:
        raise ValueError("REPAIR_EXECUTION_BOUNDARY_FAILED:" + ",".join(boundary_errors))
    execution = g.read(args.execution_boundary)
    subject = frozen.repair_target_subject(draft)
    checks = g.read(frozen.CONTRACT)["repair_target_review_checks"]
    out = g.local(args.out)
    bundle_path = g.resolve(g.ref(args.scope_review_bundle))
    bundle = g.read(bundle_path)
    bundle_errors = g.verify_reviews(
        bundle.get("reviews", []), subject, checks,
        g.read(frozen.CONTRACT)["repair_target_review_roles"]
    )
    if (bundle.get("schema") != 1 or bundle.get("stage") != "repair_target_scope_reviews" or
            bundle.get("repair_target_subject_sha256") != subject or
            bundle.get("verdict") != "PASS_REPAIR_TARGET_SCOPE_ONLY" or bundle_errors):
        raise ValueError("INDEPENDENT_STRUCTURED_REPAIR_SCOPE_REVIEWS_REQUIRED:" + ",".join(bundle_errors))
    final = dict(draft)
    final["repair_target_review_bundle"] = g.ref(bundle_path)
    final["repair_execution_boundary"] = g.ref(args.execution_boundary)
    final["repair_change_mask"] = execution["change_mask"]
    request_path = out / "REQUEST.json"
    g.write(request_path, final)
    current.install_current_patches()
    audit = current._audit_request_current(request_path)
    if audit["errors"]:
        raise ValueError("FINAL_REPAIR_REQUEST_FAILED:" + ",".join(audit["errors"]))
    g.write(out / "REQUEST_AUDIT.json", audit)
    result = frozen.reserve(request_path)
    g.write(out / "RESERVE_RESULT.json", result)
    print(str(out / "RESERVE_RESULT.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", required=True)
    parser.add_argument("--scope-review-bundle", required=True)
    parser.add_argument("--execution-boundary", required=True)
    parser.add_argument("--out", required=True)
    main(parser.parse_args())
