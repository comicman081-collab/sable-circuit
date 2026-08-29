# Repository automation policy

These rules apply to ChatGPT, Codex, and other coding agents working in this repository.

## GitHub Actions safety
- Normal code edits, commits, pushes, branch work, and pull requests MUST NOT intentionally trigger GitHub Actions.
- The repository workflows are intentionally manual-only. Do not restore broad `push`, `pull_request`, `schedule`, `workflow_run`, or recursive dispatch triggers without explicit user approval.
- Do not run, re-run, or dispatch GitHub Actions unless the user explicitly asks to run CI/verification.
- Normal coding must not consume GitHub Actions minutes.

## Cost and loop guardrails
- Prefer local/static verification during normal development.
- Never add self-triggering commit/push loops, recursive workflow chains, unbounded polling/retry loops, or auto-commit workflows without explicit user approval.
- Keep `concurrency`/`cancel-in-progress` and finite timeouts on runner jobs.
- If a CI run fails, inspect the existing failed run first. Do not retry automatically.
