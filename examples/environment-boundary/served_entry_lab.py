"""Inspect the JavaScript a loopback static server actually returns.

This is a bounded local response check, not browser execution or AWS hosting proof.
"""

from __future__ import annotations

import argparse
from functools import partial
import hashlib
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path, PurePosixPath
import threading
from urllib.parse import urlsplit
from urllib.request import urlopen

from inspect_outputs import FIELDS, load_outputs, read_value


MAX_HTML = 1024 * 1024
MAX_JS = 32 * 1024 * 1024


class ModuleScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag != "script":
            return
        values = dict(attrs)
        if values.get("type") == "module" and values.get("src"):
            self.sources.append(values["src"])


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def entry_path(root: Path, source: str) -> Path:
    parsed = urlsplit(source)
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or
            "\\" in parsed.path or not parsed.path.endswith(".js")):
        raise ValueError("module script must be a plain same-origin JavaScript path")
    parts = PurePosixPath(parsed.path.lstrip("/")).parts
    if not parts or any(part in {".", ".."} for part in parts):
        raise ValueError("unsafe module script path")
    path = root.joinpath(*parts)
    if path.is_symlink() or not path.is_file() or root.resolve() not in path.resolve().parents:
        raise ValueError("module script is not a regular file beneath the build")
    return path


def read_response(url: str, maximum: int) -> bytes:
    with urlopen(url, timeout=5) as response:
        if response.status != 200 or response.geturl() != url:
            raise ValueError("loopback server did not return the requested file directly")
        data = response.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError("loopback response exceeds the inspection limit")
    return data


def inspect(document: dict, outputs_digest: str, root: Path, forbidden=None,
            forbidden_digest=None) -> dict:
    if not root.is_dir() or root.is_symlink() or not (root / "index.html").is_file():
        raise ValueError("expected a regular local build directory with index.html")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        html = read_response(base + "/index.html", MAX_HTML)
        scripts = ModuleScripts()
        scripts.feed(html.decode("utf-8"))
        if not 1 <= len(scripts.sources) <= 8 or len(scripts.sources) != len(set(scripts.sources)):
            raise ValueError("expected one to eight distinct module script entries")
        served = []
        same_as_build = []
        hashes = []
        total = 0
        for source in scripts.sources:
            path = entry_path(root, source)
            data = read_response(base + "/" + path.relative_to(root).as_posix(), MAX_JS)
            total += len(data)
            if total > MAX_JS:
                raise ValueError("module script responses exceed the inspection limit")
            served.append(data)
            same_as_build.append(data == path.read_bytes())
            hashes.append(hashlib.sha256(data).hexdigest())
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    selected = {name: (any(read_value(document, field).encode() in data for data in served)
                       if read_value(document, field) is not None else None)
                for name, field in FIELDS.items()}
    distinct = None
    if forbidden is not None:
        distinct = {}
        for name, field in FIELDS.items():
            value = read_value(forbidden, field)
            approved = read_value(document, field)
            distinct[name] = (None if value is None or value == approved
                              else any(value.encode() in data for data in served))
    passed = (all(same_as_build) and all(value is not False for value in selected.values())
              and not any(value is True for value in (distinct or {}).values()))
    return {
        "outputs_sha256": outputs_digest,
        "index_response_sha256": hashlib.sha256(html).hexdigest(),
        "module_entry_response_sha256": hashes,
        "module_entry_count": len(served),
        "response_matches_local_build": same_as_build,
        "selected_values_found_in_served_entries": selected,
        "distinct_forbidden_values_found_in_served_entries": distinct,
        "forbidden_outputs_sha256": forbidden_digest,
        "local_served_entry_check_passed": passed,
        "scope": "loopback index and its module entry responses only; no browser execution, imported/dynamic chunks, runtime settings, live host, authorization or AWS proof",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outputs", type=Path)
    parser.add_argument("built_directory", type=Path)
    parser.add_argument("--forbid-outputs", type=Path)
    args = parser.parse_args(argv)
    try:
        document, digest = load_outputs(args.outputs)
        forbidden, forbidden_digest = (load_outputs(args.forbid_outputs)
                                       if args.forbid_outputs else (None, None))
        report = inspect(document, digest, args.built_directory, forbidden, forbidden_digest)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"served entry check stopped: {error}\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["local_served_entry_check_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
