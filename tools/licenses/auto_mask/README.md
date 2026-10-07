# Local auto-mask model inventory

`C:\AI_MODELS\auto-mask` is read-only. It is used only to derive a binary
subject mask and exact `#00FF00` exterior from one project-local candidate; no
weight is included in the game or its asset distribution.

The local CLIPSeg model card declares Apache-2.0. The official
[SAM 2 repository license](https://github.com/facebookresearch/sam2/blob/main/LICENSE)
and the official [SAM 2.1 Hiera model card](https://huggingface.co/facebook/sam2.1-hiera-small)
declare Apache-2.0. Pinned local revisions, file sizes, and SHA-256 values are
in `MODEL_INVENTORY.json`.

This helper is permitted for SABLE local production only because its recorded
license permits commercial local use. It is not Krea/Krea2, cloud inference, or
a distributable SABLE runtime dependency.
