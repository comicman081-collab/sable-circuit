"""Historical downloader, disabled after the commercial/AI-use license audit."""
raise SystemExit("Non-3D downloads are disabled: commercial and AI-use rights are unverified.")
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import hashlib
import json
import shutil
import time

ROOT = Path(__file__).resolve().parent
LIBRARY = Path("C:/ai_asset/karchive/2026-09-23")
STAGE = ROOT / "tmp" / "downloads"
LIBRARY.mkdir(parents=True, exist_ok=True)
STAGE.mkdir(parents=True, exist_ok=True)
rows = json.loads((ROOT / "downloads_catalog.json").read_text(encoding="utf-8"))
assert len({r["source_url"] for r in rows}) == len(rows)


def hash_file(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def fetch(row):
    stem = row["page_path"].strip("/").replace("/", "__")
    assert stem and all(c.isalnum() or c in "-_" for c in stem)
    relative = Path(row["category"]) / (stem + row["extension"])
    final = (LIBRARY / relative).resolve()
    assert final.is_relative_to(LIBRARY.resolve())
    stage = STAGE / (row["category"] + "__" + stem + row["extension"] + ".part")
    if final.exists() or stage.exists():
        raise RuntimeError("Refusing to overwrite pre-existing file")
    for attempt in range(3):
        try:
            req = Request(row["download_url"], headers={"Referer": row["page_url"]})
            with urlopen(req, timeout=90) as response, stage.open("xb") as output:
                content_type = response.headers.get("Content-Type", "")
                expected = int(response.headers.get("Content-Length", "0"))
                if expected > 6_000_000_000:
                    raise RuntimeError("File exceeds 6 GB safety bound")
                digest = hashlib.sha256()
                total = 0
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    total += len(block)
                    if total > 6_000_000_000:
                        raise RuntimeError("File exceeds 6 GB safety bound")
                    digest.update(block)
                    output.write(block)
            if not total or expected and total != expected:
                raise RuntimeError(f"Incomplete response {total}/{expected}")
            prefix = stage.open("rb").read(16)
            suffix = row["extension"]
            signatures = {".png": prefix.startswith(b"\x89PNG\r\n\x1a\n"),
                          ".jpg": prefix.startswith(b"\xff\xd8"), ".jpeg": prefix.startswith(b"\xff\xd8"),
                          ".webp": prefix.startswith(b"RIFF") and prefix[8:12] == b"WEBP",
                          ".mp4": prefix[4:8] == b"ftyp", ".mp3": prefix.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")),
                          ".wav": prefix.startswith(b"RIFF") and prefix[8:12] == b"WAVE",
                          ".zip": prefix.startswith(b"PK\x03\x04"), ".pdf": prefix.startswith(b"%PDF-")}
            if not signatures[suffix]:
                raise RuntimeError(f"Signature mismatch: {suffix}, {prefix.hex()}")
            final.parent.mkdir(parents=True, exist_ok=True)
            with stage.open("rb") as source, final.open("xb") as output:
                shutil.copyfileobj(source, output, 1024 * 1024)
            if hash_file(final) != digest.hexdigest():
                raise RuntimeError("Destination hash differs from downloaded bytes")
            stage.unlink()  # Verified staging copy; the source is preserved at final.
            return {**row, "local_path": str(final), "bytes": total, "sha256": digest.hexdigest(),
                    "content_type": content_type, "status": "PASS_DOWNLOADED_SIGNATURE_AND_SHA256"}
        except (HTTPError, TimeoutError, OSError) as exc:
            if stage.exists():
                stage.rename(stage.with_name(stage.name + f".failed_attempt_{attempt + 1}"))
            if attempt == 2:
                raise
            time.sleep(1 + 2 * attempt)


done = []
failed = []
with ThreadPoolExecutor(max_workers=4) as pool:
    futures = {pool.submit(fetch, row): row for row in rows}
    for index, future in enumerate(as_completed(futures), 1):
        try:
            done.append(future.result())
        except Exception as exc:
            failed.append({"source_url": futures[future]["source_url"], "page_url": futures[future]["page_url"], "error": repr(exc)})
        if index % 100 == 0 or index == len(rows):
            print(f"Downloaded {index}/{len(rows)}; successes={len(done)} failures={len(failed)}", flush=True)
            (ROOT / "download_receipt.partial.json").write_text(json.dumps({"done": done, "failed": failed}, ensure_ascii=False), encoding="utf-8")

done.sort(key=lambda r: r["local_path"])
summary = {"status": "COMPLETE" if not failed and len(done) == len(rows) else "INCOMPLETE",
           "source": "https://karchive.vibeline.co.kr/", "source_kind": "public per-item download buttons; 3D prior archive excluded",
           "library": str(LIBRARY), "downloaded_count": len(done), "downloaded_bytes": sum(r["bytes"] for r in done),
           "by_category": dict(Counter(r["category"] for r in done)), "failures": failed,
           "integrated_into_sable": False, "license_scope": "Non-3D use rights unverified; stored for review only."}
(ROOT / "download_receipt.json").write_text(json.dumps({"summary": summary, "files": done}, ensure_ascii=False, indent=2), encoding="utf-8")
(LIBRARY / "download_receipt.json").write_text(json.dumps({"summary": summary, "files": done}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
