# QWEN_IMAGE_EDIT_2511_LOCAL_INSTALL_REPORT

## COMFYUI

- Path: `C:\AI_ENVS\ComfyUI_windows_portable\SableQwen2511\ComfyUI` (existing local, read-only runtime)
- Portable Python: `C:\AI_ENVS\ComfyUI_windows_portable\python_embeded\python.exe` (existing local, read-only executable shared by the portable installation)
- Version/commit: ComfyUI `0.33.1`, source checkout
  `72865f4f27eaf5396f8f36370e0a2be3a9a090ee`
- Python: `3.13.14`
- PyTorch: `2.13.0+cu130`
- CUDA: `13.0`
- GPU: NVIDIA GeForce RTX 4070 SUPER
- VRAM: `12,878,086,144` bytes / `12,282 MiB`

The verified runtime and weight store remain at
`C:\AI_ENVS\ComfyUI_windows_portable\SableQwen2511`. It is used read-only:
the SABLE launcher must pin all Comfy input, output, temp, and user directories
beneath this project. Its runtime contains no active `extra_model_paths.yaml`,
so it has no Krea model-resolution path.

## LICENSE GATE

| Component | Official source and immutable revision | License | Commercial local use |
| --- | --- | --- | --- |
| Qwen Image Edit 2511 diffusion | `Comfy-Org/Qwen-Image-Edit_ComfyUI` @ `984166f60a9b1fcede5e9b9287b7a7aebc050010` | Apache-2.0 | allowed |
| Qwen 2.5 VL text encoder | `Comfy-Org/Qwen-Image_ComfyUI` @ `7beb7b647f04469fbe64ba8adc2bb0d7e5e9f73f` | Apache-2.0 | allowed |
| Qwen Image VAE | `Comfy-Org/Qwen-Image_ComfyUI` @ `7beb7b647f04469fbe64ba8adc2bb0d7e5e9f73f` | Apache-2.0 | allowed |

- Upstream model authority: `Qwen/Qwen-Image-Edit-2511` @
  `6f3ccc0b56e431dc6a0c2b2039706d7d26f22cb9`, Apache-2.0.
- Local license inventory: `tools/licenses/qwen_image_edit_2511/`.
- Krea2 used: **NO**
- Paid/non-commercial/research-only models used: **NO**
- Model weights are production-tool dependencies, not game-distribution files.
  Output distribution still requires SABLE to hold rights to all supplied input
  art and other non-model content.

## APPROVED WEIGHT SPECIFICATION

| Role | File | Size | SHA-256 | Destination |
| --- | --- | ---: | --- | --- |
| diffusion | `qwen_image_edit_2511_int8_convrot.safetensors` | 20,499,083,824 | `11b5af5ac601821d73930c84846c9a158e67177356daf927ce1c8d10f3963829` | `runtime/models/diffusion_models/` |
| text encoder | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | 9,384,670,680 | `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4` | `runtime/models/text_encoders/` |
| VAE | `qwen_image_vae.safetensors` | 253,806,246 | `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f` | `runtime/models/vae/` |

These are the only approved SABLE Qwen weights. They are present in the
verified read-only runtime above. BF16, FP8mixed alternative diffusion,
Lightning LoRA, Krea2, Universal Base Characters, and any other unapproved
weight cannot be used as a fallback.

## HISTORICAL COMFYUI LOAD VALIDATION

- diffusion recognized: **YES**
- text encoder recognized: **YES**
- VAE recognized: **YES**
- missing models: **none**
- missing nodes: **none**
- errors: no loader/dtype/shape error. Current local log evidence also shows
  `QwenImageTEModel_` and `QwenImage` loaded for a completed 40-step run.

## HISTORICAL TECHNICAL EDIT TEST

- input: `art_src/pilot_v2/aster_v2/qwen_edits/technical_smoke/sable_qwen_2511_smoke_input.png`
- output: generated during validation; no raw output is retained
- resolution: `512×512` input → `1024×1024` output
- elapsed: `1044.819` seconds
- peak VRAM: `11900 MiB`
- actual edit delta: `17.8104` mean absolute RGB delta after resize (minimum `10.0`)
- cloud calls: `0`
- Krea2 calls: `0`
- result: **PASS (technical only)**

The first two smoke attempts produced output files but failed the actual-edit
delta gate; neither was counted as a success. The passing run changed the
requested test colour materially. All smoke outputs were then purged because
they are reproducible technical fixtures, not production art.

## ASTER EDIT PILOT

- Earlier stick-guide attempts: visual **FAIL** and purged. They were not
  retained or promoted.
- Current input authority: repo ASTER identity/property lock, Image A render
  authority, UAL-derived locked camera anchors, and the Blender full-mass
  spatial guide.
- Current candidate: `art_src/pilot_v2/aster_v2/qwen_edits/qwen_static_master_fullmass_v3_seed251114/`
- result: one exact-green 1024×1024 source and binary mask exist for human
  inspection only. No runtime export or animation was made.
- visual gate: **USER REVIEW REQUIRED**

## CURRENT WEIGHT REVALIDATION — 2026-08-29

The installed files below were read from the immutable local runtime at
`C:\AI_ENVS\ComfyUI_windows_portable\SableQwen2511\models`. No write,
download, move, rename, or deletion occurred in `C:\AI_ENVS` or
`C:\AI_MODELS`.

| File | Bytes | Actual SHA-256 | Expected SHA-256 | Match |
| --- | ---: | --- | --- | --- |
| `qwen_image_edit_2511_int8_convrot.safetensors` | 20,499,083,824 | `11b5af5ac601821d73930c84846c9a158e67177356daf927ce1c8d10f3963829` | same | YES |
| `qwen_2.5_vl_7b_fp8_scaled.safetensors` | 9,384,670,680 | `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4` | same | YES |
| `qwen_image_vae.safetensors` | 253,806,246 | `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f` | same | YES |

The local ComfyUI server was configured with that read-only model directory;
its input, output, temporary, user, and log directories were all beneath the
SABLE project. Its loader API recognized exactly these three Qwen files. The
single ASTER candidate took 171.324 seconds with seed `251114`, 32 steps,
cloud calls `0`, and Krea2 calls `0`.

## CURRENT PRE-GATE PIPELINE VALIDATION — 2026-08-29

`tools/art_pipeline/Invoke-AsterStaticMasterPipeline.ps1 -Mode Validate`
passed against the retained ASTER source candidate. It checked the approved
Apache-2.0/commercial-use inventory, exact pinned file sizes, absence of a
Qwen `extra_model_paths.yaml`, C: paths as read-only dependencies, source and
mask SHA-256 values, exact `#00FF00` exterior, and the required Image A/game
scale review evidence. It did not launch Blender or ComfyUI and did not modify
anything under `C:\AI_ENVS` or `C:\AI_MODELS`.

## FINAL (corrected local installation state)

- QWEN_2511_LICENSE_GATE: **PASS**
- QWEN_2511_RUNTIME_GATE: **PASS — local weights and completed local execution verified; SABLE writes must remain project-local**
- ASTER_STATIC_EDIT_GATE: **USER REVIEW REQUIRED (one current source candidate; no promotion)**
- PRODUCTION_EXPANSION: **HOLD**
