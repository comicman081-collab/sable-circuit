# GitHub Actions & External Asset Policy v0.1

## Current repository phase
Validation only. No deployment workflow and no GitHub Pages workflow is present.

The baseline CI has two gates:
1. repository/data contract validation;
2. a real Godot 4.7.2 headless import + bootstrap smoke run.

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
2. `web-build.yml` — Web export artifact only.
3. `pages.yml` — intentionally absent until explicitly approved.
