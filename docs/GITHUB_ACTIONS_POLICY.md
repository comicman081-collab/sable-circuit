# GitHub Actions & External Asset Policy v0.2

## Current repository phase
Validation only. No deployment workflow and no GitHub Pages workflow is present.

The baseline CI has two gates:
1. repository/data contract validation;
2. a real Godot 4.7.2 headless import + bootstrap smoke run.

## Artifact storage

Validation, smoke-test, debug, coverage, and runtime-capture output is
ephemeral runner data. `validate.yml` must not upload those files as GitHub
Actions artifacts. The runtime-capture job may create images for assertions
inside its runner, but the runner is discarded after the job and no upload step
may preserve those images.

If a future production deployment requires an artifact, it may upload only the
provider-required deployment artifact. GitHub Pages must use the shortest
supported retention (prefer one day) and must not include separate preview,
test, or duplicate bundle artifacts. Storage cleanup must never alter a live
deployment.

## Godot toolchain rule
CI downloads the official Linux x86_64 Godot 4.7.2 stable editor archive from the matching GitHub release and verifies the archive against the frozen SHA-256 before execution.

Baseline archive SHA-256:
`cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4`

Changing the engine version or digest is an explicit architecture change and must be reviewed in the same commit.

## What Actions may fetch

### Toolchain
Pinned Godot stable binaries/export templates, test utilities and official GitHub actions.

### External content
Only resources listed in `assets/external/manifest.json` may be fetched automatically. Every entry must include:
- stable id
- human-readable name
- origin
- exact version/revision
- license id/name
- license evidence/note
- destination path
- SHA-256 of expected bytes
- whether redistribution inside this repository is permitted

## What Actions must not do
- scrape arbitrary web pages for assets
- fetch a mutable `latest` asset without an expected digest
- download material with unclear commercial-use rights
- inject secrets into logs or cache
- enable Pages or publish a release without an explicit production decision
- execute downloaded binaries before integrity verification

## Reproducibility
Actions cache is only a speed optimization. A cache hit must never change the logical build result. Toolchain and external file integrity remain independently versioned and hashed.

Official GitHub actions use reviewed major-version tags during pre-production. Before release hardening, workflow actions are frozen to audited commit SHAs.

## Future workflows
1. `validate.yml` — structure/data + pinned Godot headless validation.
2. `web-build.yml` — intentionally absent until an explicit deployment decision.
3. `pages.yml` — intentionally absent until explicitly approved.

## Cleanup record — 2026-09-10

- Queried `comicman081-collab/sable-circuit` through the GitHub API before
  cleanup: 0 Actions artifacts and no GitHub Pages deployment were present.
- No artifact or workflow run was deleted because there was nothing stored.
- Repository Actions artifact-and-log default retention was changed from 90 days
  to 1 day to bound any future accidental upload.
- Removed the `sable-circuit-runtime-captures` upload from `validate.yml`; its
  rendered screenshots remain runner-local only.
- No production URL exists for this repository, so there was no deployment to
  preserve or re-verify. This records current storage, not previously accrued
  billing usage.
