"""Read public kArchive listings. No model downloads or runtime changes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.parse import urlencode, urljoin
from concurrent.futures import ThreadPoolExecutor
import json
import sys

ROOT = Path(__file__).resolve().parent
BASE = "https://karchive.vibeline.co.kr"


class Listing(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current = None
        self.hidden = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.hidden += 1
        if tag == "article":
            self.current = {"text": []}
        if self.current is not None:
            if tag == "a" and a.get("href", "").startswith("/models/"):
                self.current["page_url"] = urljoin(BASE, a["href"])
                self.current["id"] = a["href"].split("/")[-1]
            if tag == "a" and a.get("href", "").startswith("/api/model-download"):
                self.current["download_url"] = urljoin(BASE, a["href"])
            if tag == "img":
                self.current["thumbnail_url"] = a.get("src")
                self.current["title"] = a.get("alt")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden -= 1
        if tag == "article" and self.current:
            self.rows.append(self.current)
            self.current = None

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.text.append(data.strip())
            if self.current is not None:
                self.current["text"].append(data.strip())


def fetch_query(query):
    url = BASE + "/models?" + urlencode({"q": query, "sort": "popular"})
    raw = urlopen(url, timeout=40).read()
    folder = ROOT / "search_pages"
    folder.mkdir(exist_ok=True)
    (folder / (query + ".html")).write_bytes(raw)
    parsed = Listing()
    parsed.feed(raw.decode("utf-8"))
    for row in parsed.rows:
        row["search_term"] = query
        row["text"] = row["text"][-3:]
    return query, parsed.rows


if __name__ == "__main__":
    terms = sys.argv[1:] or ["lab", "industrial", "medical", "crate", "barrier", "server", "robot", "military", "generator", "apocalypse"]
    rows = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for term, found in pool.map(fetch_query, terms):
            rows.extend(found)
            print(json.dumps({"query": term, "first_page_count": len(found), "examples": [{"id": r["id"], "title": r.get("title")} for r in found[:12]]}, ensure_ascii=False), flush=True)
    previous_path = ROOT / "search_catalog.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else []
    unique = {r["id"]: r for r in previous + rows}
    (ROOT / "search_catalog.json").write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    print("Unique catalog entries:", len(unique))
