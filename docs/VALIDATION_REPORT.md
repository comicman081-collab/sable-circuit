# Architecture Validation Report v0.1

## Result: PASS for local/static pre-production baseline

The repository also contains a remote CI gate that downloads the exact Godot 4.7.2 stable Linux editor, verifies its SHA-256, performs a headless editor import/parse, and launches the minimal bootstrap scene headlessly. The first PR check is the authoritative remote runtime confirmation.

### 1. Engine baseline — PASS
Godot 4.7.2 stable is frozen for the baseline. GDScript is selected for the browser-first target. Compatibility rendering is selected for the Web target.

### 2. 3–4-head character animation architecture — PASS
Godot 4.7 supports Skeleton2D and AnimationTree. The architecture uses locomotion plus filtered action layers so aiming/firing can be independent from movement while the torso, arms, hands and weapon remain a coherent rig rather than rotating the gun alone.

### 3. AI/navigation — PASS
NavigationAgent2D is a helper for pathfinding/path-following/avoidance. Gameplay authority remains in explicit companion/enemy state machines, so navigation does not own combat decisions.

### 4. Web target — PASS WITH CONSTRAINTS
The design avoids C#, Forward+/Mobile-only assumptions and required native extensions. Browser memory and texture budgets must be measured with production character art.

### 5. Repository layout — PASS
`project.godot` is at repository root. Runtime assets, authoritative data, scenes, scripts, tests, tools and docs have separate ownership. The earlier nested `game/` wrapper is forbidden by validation.

### 6. External assets via Actions — PASS WITH POLICY
Automatic retrieval is allowed only with fixed origin/version, license metadata and SHA-256 verification. Mutable or unlicensed asset downloads are prohibited.

### 7. Deployment boundary — PASS
No Pages workflow is included. Future Web builds may produce artifacts without public deployment until deployment is explicitly approved.

## Local validation performed
- machine-readable frozen repository layout contract: PASS
- required baseline files: PASS
- external asset manifest parse/policy: PASS
- forbidden nested `game/` wrapper guard: PASS
- accidental Pages deployment guard: PASS
- workflow YAML parse: PASS
- bootstrap main-scene contract: PASS

## Risks still open for the vertical slice
- Measure the actual cost of 8-sector art on the first operator before scaling the roster.
- Test sector-switch popping with asymmetric costumes and weapons.
- Validate companion formation/collision in narrow rooms.
- Profile browser memory once real character atlases, VFX and audio are present.
- Set measurable muzzle/projectile angular and positional tolerances during the combat prototype.

## Frozen decisions for v0.1
- engine: Godot 4.7.2 stable
- language: GDScript
- renderer: Compatibility
- repository project root: root-level `project.godot`
- runtime: same operator actor for traversal and combat
- squad: 3 deployed operators, 1 directly controlled
- animation: 8-sector presentation + independent aim/movement + layered Skeleton2D/AnimationTree
- data: reviewable JSON authority
- CI: static validation + pinned Godot headless validation, no deployment
