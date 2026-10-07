"""Inventory kArchive's public non-3D download entries without downloading assets."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time

ROOT = Path(__file__).resolve().parent
BASE = "https://karchive.vibeline.co.kr"
CATS = ("video", "image", "fashion", "source", "recipe")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style"):
            self.hidden += 1
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.text.append(data.strip())


def get(path):
    for attempt in range(3):
        try:
            raw = urlopen(urljoin(BASE, path), timeout=45).read()
            page = Page()
            page.feed(raw.decode("utf-8"))
            return page, raw
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


groups = []
for cat in CATS:
    raw = (ROOT / (cat + ".html")).read_bytes()
    page = Page()
    page.feed(raw.decode("utf-8"))
    group_paths = sorted({a["href"] for a in page.links if a["href"].startswith("/c/")})
    groups.extend((cat, path) for path in group_paths)
print("Groups on category landing pages:", len(groups), flush=True)


def crawl_group(pair):
    cat, path = pair
    page, raw = get(path)
    posts = sorted({a["href"] for a in page.links if a["href"].startswith("/p/")})
    direct = [a for a in page.links if a["href"].startswith("/api/download?")]
    return {"category": cat, "group_path": path, "post_paths": posts,
            "direct_download_links": direct, "page_text": page.text[:50], "html_bytes": len(raw)}


result = []
errors = []
with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(crawl_group, pair): pair for pair in groups}
    for index, future in enumerate(as_completed(futures), 1):
        try:
            result.append(future.result())
        except Exception as exc:
            errors.append({"pair": futures[future], "error": repr(exc)})
        if index % 50 == 0:
            print(f"Scanned {index}/{len(groups)} groups; {len(errors)} errors", flush=True)
            (ROOT / "group_catalog.partial.json").write_text(json.dumps({"groups": result, "errors": errors}, ensure_ascii=False, indent=2), encoding="utf-8")

result.sort(key=lambda row: (row["category"], row["group_path"]))
posts = {path: row["category"] for row in result for path in row["post_paths"]}
summary = {"groups_by_category": {cat: sum(row["category"] == cat for row in result) for cat in CATS},
           "post_count": len(posts), "posts_by_category": {cat: sum(kind == cat for kind in posts.values()) for cat in CATS},
           "direct_group_downloads": sum(len(row["direct_download_links"]) for row in result), "errors": errors}
(ROOT / "group_catalog.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "post_paths.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "group_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
