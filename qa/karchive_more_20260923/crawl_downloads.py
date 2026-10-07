"""Discover the site's actual per-item download links, preserving source pages."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin, urlsplit, parse_qs
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import json
import time

ROOT = Path(__file__).resolve().parent
BASE = "https://karchive.vibeline.co.kr"


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


def parse_link(category, page_path, link, page_text):
    href = link["href"]
    parsed = urlsplit(href)
    assert parsed.path == "/api/download"
    query = parse_qs(parsed.query)
    source_url = query["url"][0]
    source_parsed = urlsplit(source_url)
    assert source_parsed.scheme == "https" and source_parsed.netloc == "pub-cb229c0cebb64c3c80457a98ee0ea01d.r2.dev"
    assert ".." not in source_parsed.path.split("/")
    suffix = Path(source_parsed.path).suffix.lower()
    assert suffix in (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mp3", ".wav", ".zip", ".pdf")
    # Related-post links can cross categories (for example a video links to a
    # character sheet). Classify the actual file by its source collection.
    source_collection = source_parsed.path.strip("/").split("/", 1)[0]
    if source_collection in ("fashion", "source", "recipe"):
        category = source_collection
    elif suffix in (".mp4", ".mp3", ".wav"):
        category = "video"
    else:
        category = "image"
    return {"category": category, "page_path": page_path, "page_url": urljoin(BASE, page_path),
            "download_url": urljoin(BASE, href), "source_url": source_url,
            "original_filename": query.get("filename", [""])[0], "extension": suffix,
            "page_title": page_text[24:29], "page_text": page_text[24:80] if category == "recipe" else page_text[24:45]}


def scan_post(task):
    page_path, category = task
    for attempt in range(3):
        try:
            raw = urlopen(urljoin(BASE, page_path), timeout=45).read()
            page = Page()
            page.feed(raw.decode("utf-8"))
            links = [a for a in page.links if a["href"].startswith("/api/download?")]
            return [parse_link(category, page_path, link, page.text) for link in links]
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


posts = json.loads((ROOT / "post_paths.json").read_text(encoding="utf-8"))
groups = json.loads((ROOT / "group_catalog.json").read_text(encoding="utf-8"))
links = []
for row in groups:
    for link in row["direct_download_links"]:
        links.append(parse_link(row["category"], row["group_path"], link, row["page_text"]))
print("Direct group downloads:", len(links), "posts to scan:", len(posts), flush=True)

errors = []
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = {pool.submit(scan_post, task): task for task in posts.items()}
    for index, future in enumerate(as_completed(futures), 1):
        try:
            links.extend(future.result())
        except Exception as exc:
            errors.append({"task": futures[future], "error": repr(exc)})
        if index % 200 == 0:
            print(f"Scanned {index}/{len(posts)} posts; links={len(links)} errors={len(errors)}", flush=True)
            (ROOT / "downloads_catalog.partial.json").write_text(json.dumps({"links": links, "errors": errors}, ensure_ascii=False), encoding="utf-8")

links.sort(key=lambda row: (row["category"], row["page_path"], row["source_url"]))
unique = {row["source_url"]: row for row in links}
report = {"download_links_total": len(links), "unique_source_files": len(unique),
          "by_category": dict(Counter(row["category"] for row in unique.values())),
          "extensions": dict(Counter(row["extension"] for row in unique.values())),
          "no_download_pages": len(posts) - len({row["page_path"] for row in links if row["page_path"].startswith("/p/")}),
          "errors": errors}
(ROOT / "downloads_catalog.json").write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "downloads_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
