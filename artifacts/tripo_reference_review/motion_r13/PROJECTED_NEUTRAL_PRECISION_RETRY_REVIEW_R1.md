# Independent Ponytail FULL: one neutral precision retry

Verdict: **PASS_FOR_ONE_NEUTRAL_PRECISION_RETRY_ONLY**. Exact bindings and the proposed fresh `mica_E_projected_neutral_r02` attempt are in the adjacent JSON. This review produces no Blender asset and approves no pose, motion, contact, other view, runtime, HTML or production output.

The failed R1 stopped before render/save. I compared the preserved builder to current code and verified that the entire delta is the split REST comparison and actual REST export/report. All prior bound dependencies except this reviewed builder delta remain exact. The owned Python audit also independently recalculated all 22 native versus proposed matrices from both in-memory setter diagnostics.

The retained matrix setter has maximum head distance **1.5137835e-7 m** and maximum basis component error **8.3046692e-6**, at `foot_r`. The alternative head/tail/roll setter is worse: basis error **1.8199040e-5** and does not pass the proposed split guard. Thus a head-distance limit of 1e-6 m and dimensionless basis-component limit of 1e-5 is appropriate for this neutral representation test. The evaluated neutral vertex and actual bound sole-floor checks remain at 1e-6 m, and source UV, weights, face topology and material assignments remain exactly compared.

The native basis is also slightly nonorthogonal (maximum Gram-matrix component error 1.7110391e-5). Therefore the actual native REST export must remain the authoritative bind pose. A later caller must resolve its hash, consume that matrix rather than silently orthogonalizing or substituting the mathematical proposal, and compare actual native evaluated deformation. The report's prose does not enforce future consumers; they require their own implementation review. No dynamic tolerance is relaxed here.

The permitted retry is one fresh owned child, 180 seconds, one native 1920×1920 image at 64 samples and one native neutral blend. Actual source-preservation visual review remains pending after that output. The dynamic sole-anchor review remains separate.

Evidence: `review_native_rest_precision_r01.py`, `PROJECTED_NEUTRAL_PRECISION_EXACT_DIFF_R1.patch`, both exact retained `DIAGNOSTIC.json` files and logs, the failed `FAILURE.json`/builder/inputs/log, and the adjacent 69-binding review JSON. No production files were edited by this reviewer.
