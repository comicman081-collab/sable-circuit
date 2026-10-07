"""Scope guard, not a visual-quality classifier or a new character generator.

Production adapters are opt-in only after actual source-preservation review.
Known retired source-reconstruction code cannot regain approval by renaming.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / 'tools/character_pipeline/art_authority_policy.json'


def executable_refs(plan):
    return [plan[k] for k in ('builder', 'runner') if k in plan] + plan.get('dependencies', [])


def retirement_errors(plan):
    import generation_harness as g
    policy = g.read(POLICY)
    retired_paths = {str(g.local(p)).casefold() for p in policy['retired_paths']}
    retired_hashes = set(policy['retired_content_sha256'])
    errors = []
    refs = executable_refs(plan)
    for item in refs:
        path = g.local(item['path'])
        # Known path and historical content denial take precedence over a stale
        # receipt. This is a scope failure, not permission to regenerate art.
        if str(path).casefold() in retired_paths or item.get('sha256') in retired_hashes:
            errors.append('RETIRED_ART_REAUTHORING_ROUTE:' + item['path'])
    if errors:
        return sorted(set(errors))
    for item in refs:
        path = g.local(item['path'])
        g.resolve(item)
        if g.sha(path) in retired_hashes:
            errors.append('RETIRED_ART_REAUTHORING_CONTENT:' + item['path'])
    return sorted(set(errors))


def assert_executable_not_retired(path):
    import generation_harness as g
    errors = retirement_errors({'builder': g.ref(path)})
    if errors:
        raise ValueError(','.join(errors))


def isolated_fixture(plan, authority):
    """Synthetic source receipts alone never grant production execution."""
    import generation_harness as g
    root = ROOT / 'artifacts/generation_harness_audit/unit_fixtures'
    sources = authority['sources']
    # Existing ImageGen intake intentionally has no generation request.  It must
    # remain a non-fixture source instead of receiving a fabricated permit.
    if (not sources or any('request' not in s for s in sources)
            or not all(g.read(g.resolve(s['request'])).get('qa_fixture_only') is True for s in sources)):
        return False
    refs = [plan['builder'], plan['runner'], plan['scope'], plan['source_receipt']]
    refs += plan['source_images']
    refs += [i[k] for i in plan['readonly_inputs'] for k in ('asset', 'license')]
    refs += [s['request'] for s in sources]
    return (g.local(plan['output_root']).is_relative_to(root)
            and all(g.resolve(r).is_relative_to(root) for r in refs))


def adapter_review_subject(plan, authority, entry):
    """Bind review to the exact code, source, operation set, and neutral evidence."""
    import generation_harness as g
    subject = {
        'schema': 1,
        'actor_id': plan.get('actor_id'),
        'costume_id': plan.get('costume_id'),
        'direction': plan.get('direction'),
        'art_authority': plan.get('art_authority'),
        'local_operations': plan.get('local_operations'),
        'source_receipt': plan.get('source_receipt'),
        'source_images': plan.get('source_images'),
        'plan_neutral_admission': plan.get('neutral_admission'),
        'source_bindings': authority.get('bindings'),
        'executable_closure': entry.get('executable_closure'),
        'neutral_evidence': entry.get('neutral_evidence'),
    }
    if plan.get('calf_width_witness') is not None:
        subject['calf_width_witness'] = plan['calf_width_witness']
    return g.canonical(subject)


def production_errors(plan, authority):
    import generation_harness as g
    errors = retirement_errors(plan)
    if errors or isolated_fixture(plan, authority):
        return errors
    policy = g.read(POLICY)
    if plan.get('art_authority') != 'imagegen_visuals_blender_motion_only':
        errors.append('IMAGEGEN_VISUAL_AUTHORITY_REQUIRED')
    operations = plan.get('local_operations')
    if (not isinstance(operations, list) or not operations
            or any(op not in policy['allowed_local_operations'] for op in operations)):
        errors.append('LOCAL_VISUAL_REAUTHORING_OR_UNSPECIFIED_OPERATION')
    # A declaration or extra PASS checkbox is not an implementation. Match the
    # complete reviewed executable closure in the checked-in policy, not names.
    closure = {r['path']: r['sha256'] for r in executable_refs(plan)}
    matches = [entry for entry in policy['approved_motion_adapters']
               if entry.get('executable_closure') == closure]
    if len(matches) != 1:
        errors.append('SOURCE_PRESERVING_MOTION_ADAPTER_NOT_IMPLEMENTED_OR_REVIEWED')
    else:
        entry = matches[0]
        checks = ['no_visual_reauthoring', 'neutral_source_preservation', 'motion_only_operations']
        subject = adapter_review_subject(plan, authority, entry)
        if entry.get('review_subject_sha256') != subject:
            errors.append('ADAPTER_REVIEW_SUBJECT_DOES_NOT_BIND_SOURCE_AND_EVIDENCE')
        if plan.get('neutral_admission') != entry.get('neutral_evidence'):
            errors.append('PLAN_NEUTRAL_ADMISSION_MUST_MATCH_REVIEWED_ADAPTER_EVIDENCE')
        review = g.read(g.resolve(entry['review_bundle']))
        errors += g.verify_reviews(review.get('reviews', []), subject, checks,
                                   ['implementation', 'Ponytail FULL'])
        if not entry.get('neutral_evidence'):
            errors.append('ACTUAL_NEUTRAL_SOURCE_PRESERVATION_EVIDENCE_REQUIRED')
        else:
            g.resolve(entry['neutral_evidence'])
    return sorted(set(errors))
