"""Measure the entry-page files in a local static build, without claiming CDN bytes."""

import argparse
import gzip
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit


class EntryReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag == "script" and "src" in values:
            self.references.append(values["src"])
        elif tag == "link" and "href" in values:
            rel = (values.get("rel") or "").split()
            if any(kind in rel for kind in ("stylesheet", "preload", "modulepreload")):
                self.references.append(values["href"])


def local_path(dist, reference):
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or not parsed.path:
        raise ValueError(f"Entry reference needs a local build file: {reference}")
    relative = Path(parsed.path.lstrip("/"))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Entry reference leaves the build directory: {reference}")
    target = (dist / relative).resolve()
    if not target.is_relative_to(dist.resolve()) or not target.is_file():
        raise ValueError(f"Entry reference is missing or leaves the build: {reference}")
    return target


def measure(dist, entry="index.html"):
    dist = Path(dist).resolve()
    page = local_path(dist, entry)
    parser = EntryReferences()
    parser.feed(page.read_text(encoding="utf-8"))
    files = dict.fromkeys([page, *(local_path(dist, ref) for ref in parser.references)])
    rows = []
    for path in files:
        content = path.read_bytes()
        rows.append({"path": path.relative_to(dist).as_posix(),
                     "sha256": sha256(content).hexdigest(),
                     "raw_bytes": len(content),
                     "local_gzip_bytes": len(gzip.compress(content, mtime=0))})
    all_paths = sorted(dist.rglob("*"))
    if any(path.is_symlink() or not (path.is_file() or path.is_dir()) for path in all_paths):
        raise ValueError("Build contains a symlink or unsupported member")
    all_files = [path for path in all_paths if path.is_file()]
    return {"scope": "Local entry HTML and direct assets, plus complete static-file raw total",
            "entry": entry, "files": rows,
            "raw_entry_bytes": sum(row["raw_bytes"] for row in rows),
            "local_gzip_entry_bytes": sum(row["local_gzip_bytes"] for row in rows),
            "all_static_files": len(all_files),
            "all_static_raw_bytes": sum(path.stat().st_size for path in all_files),
            "limits": [
                "Local gzip size is not a measured Amplify or browser transfer.",
                "The all-file raw total is a conservative publisher-review threshold, not a lower bound for one visit.",
                "Compression negotiation, browser cache, CDN behavior and subsequent requests are unknown.",
                "Other pages, fonts, images, API calls, retries and backend work are excluded.",
                "Public visits are not capped by this measurement.",
            ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=Path(__file__).resolve().parents[3] / "app/dist")
    parser.add_argument("--entry", default="index.html")
    args = parser.parse_args()
    try:
        result = measure(args.dist, args.entry)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Bundle measurement stopped: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
