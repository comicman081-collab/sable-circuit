# Independent current phase-validator implementation review

Reviewer: `/root/tripo_intake_review`, Ponytail FULL. **PASS for the inspected implementation delta**, with corrected mixed-schema dispatch. This is not visible-frame generation, motion or runtime approval. The new per-frame route has been exercised with isolated fixtures; no claim is made that a new complete eight-phase ImageGen production set already exists.

I traced the current request/reserve/frame/seal/verify/sequence path, the new `phase_aware_visible_frame.py` and `visible_frame_phase_contract.json`, the existing normalizer/base matte/protected derivative and the R6 existing-frame admission. I compared the old and new `audit_frame` functions after AST normalization. The diff retains the original request errors, exact permit, identity/scope, source author, output-root boundary, exact raw path, normalization, RGB preservation, derivative reproduction, native resolution, measured bounds, annotation source/laterality, muzzle and QA checks. It adds the explicit pre-generation phase contract, optional protected matte, phase-dependent stride application and current consumed-code bindings. It does not remove error strings from an old failed audit.

Run contact/flight and walk contact retain the exact existing E/W stride floor values. Down/passing/up are no longer forced into that wide silhouette. Their source-bound pose/contact and independent anatomy/support reviews remain required. That matches the actual reviewed geometry: passing legs cross with narrow foot spacing, while contact and flight have spread limbs. This implementation does not infer a full temporal gait solely from scalar stride.

The protected matte is explicit and source-sized, binary and nonempty. It may select only pixels the base classifier removes, excludes edge-connected source background, preserves normalized/original RGB and reproduces every output pixel. The mask path/hash is included in the exact frame subject. Its semantic correctness remains a required fresh independent frame check; mathematical membership alone is not treated as proof of opaque subject. No painting or ImageGen hard-mask claim is introduced.

For new phase-aware requests, the exact phase contract and consumed verifier/helper bytes are bound before reservation. The frame must carry that same contract, and the original single-attempt permit is compared against the recomputed request subject. Contract/code changes invalidate stale permits/reviews. The shared current seal adds both `phase_specific_stride_and_support` and `explicit_alpha_mask_preserves_source_subject`, and recursive receipt/sequence verification recomputes that seal.

I found a dispatch mismatch in the initial implementation: audit prioritized existing-frame admission, whereas seal prioritized a phase-contract field. The parent fixed it before my diagnostic ran. The final current audit explicitly rejects an admission carrying the phase-contract field, and seal prioritizes the admission branch. `DISPATCH_PROBE_R1.json` therefore records the corrected behavior (all five admission checks retained), not a successful pre-fix exploit. The probe intentionally stops before a review or receipt is produced. The new mixed-schema unit test also passes.

Executed verification:

- Phase-aware frame tests: 5 passed.
- Frozen visible-frame tests: 11 passed.
- Existing-frame admission tests including mixed-schema rejection: 13 passed.
- Contact harness tests: 5 passed.

All 34 passed. The associated logs are retained in this directory. The frozen verifier file stays at SHA `a24dbf646b4906645912639cc99397240e454c2d8fe7ec0d07b41149f118658a`. Current gate inspected after the fix: `d72c284d9ec863471c910703042befd1f0702aef5dd0111c361eb5c9f4676384`.

No further material blocker was found in this bounded implementation delta. Fresh code-bound guide subjects and the R6 admission subject must be used for final reviews; the obsolete r03/r04 guide subjects and R6 earlier reviews remain historical. No source art, masks, production code or parent artifact was modified by this reviewer. A direct current module and small explicit contract avoid changing the frozen historical verifier or constructing an arbitrary compatibility framework.
