# SABLE CIRCUIT pilot art pipeline

This directory contains the reproducible, local-only generation and cleanup
pipeline for the combat-asset pilot. It reads project-local SDXL weights from
`tools/models/` by default and writes only into the repository's
`art_src/pilot_v2` tree. Network fallback is disabled. `SABLE_CIRCUIT_MODEL_ROOT`
may point to an existing local read-only model source outside the project;
generation output remains project-local.

The pipeline must never use a Universal Base Character or any preview mesh.
Quaternius UAL1/UAL2 Standard remain animation-reference sources only.

The local SDXL distribution includes `LICENSE.md`. Its restrictions still need
to be reviewed against the intended release and use case before shipping.

Generation candidates are source-only and must have an exact `#00FF00` matte.
`apply_green_matte.py` proves that constraint before it writes a candidate.
Only a visually approved candidate may be passed to `promote_green_asset.py`;
that converter turns exact green into binary alpha and produces light/dark
alpha previews plus a QA record.  Do not promote rejected candidates.
