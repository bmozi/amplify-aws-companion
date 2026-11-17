#!/usr/bin/env python3
"""Check extracted PDF folios, contents locators, and topic-finder chapter numbers.

This is a navigation preflight. It cannot judge visible typography or semantic
accuracy of a topic-finder description; inspect the exact rendered pages too.
"""

import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--chapters", type=int, default=34)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    pdf = args.pdf.resolve()
    extracted = subprocess.check_output(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"], text=True
    )
    pages = extracted.split("\f")
    if pages[-1] == "":
        pages.pop()

    issues = []
    for number, page in enumerate(pages, 1):
        found = re.findall(r"AMPLIFY AWS\s*\|\s*(\d+)", page)
        expected = [] if number == 1 else [str(number)]
        if found != expected:
            issues.append({"kind": "folio", "page": number, "found": found, "expected": expected})

    contents = pages[2] if len(pages) >= 3 else ""
    entries = []
    for line in contents.splitlines():
        match = re.match(r"^\s*\uf0b7\s+(.+?)\.{4,}\s*(\d+)\s*$", line)
        if not match:
            continue
        title, number = match.group(1).strip(), int(match.group(2))
        entries.append({"title": title, "page": number})
        if not 1 <= number <= len(pages):
            issues.append({"kind": "locator_range", "title": title, "page": number})
            continue
        opening = " ".join(pages[number - 1].splitlines()[:3])
        title_matches = normalize(opening).startswith(normalize(title))
        if title == "Topic finder":
            title_matches = any(normalize(line) == title for line in pages[number - 1].splitlines())
        if not title_matches:
            issues.append({"kind": "locator_title", "title": title,
                           "page": number, "opening": opening})

    chapter_entries = [entry for entry in entries if entry["title"].startswith("Chapter ")]
    chapter_numbers = [int(re.match(r"Chapter (\d+)", entry["title"]).group(1))
                       for entry in chapter_entries]
    if chapter_numbers != list(range(1, args.chapters + 1)):
        issues.append({"kind": "chapter_sequence", "found": chapter_numbers})
    other_titles = [entry["title"] for entry in entries if not entry["title"].startswith("Chapter ")]
    if other_titles != ["Learning routes and prerequisite checks", "What you will practice", "Topic finder"]:
        issues.append({"kind": "other_contents_entries", "found": other_titles})

    finder_entries = [entry for entry in entries if entry["title"] == "Topic finder"]
    if len(finder_entries) != 1:
        issues.append({"kind": "topic_finder_locator", "found": finder_entries})
        finder_text = ""
    else:
        finder_page = finder_entries[0]["page"]
        if finder_page != len(pages):
            issues.append({"kind": "topic_finder_split", "start_page": finder_page,
                           "end_page": len(pages),
                           "reason": "Two alphabetical columns must remain together on one final page"})
        finder_text = "\n".join(pages[finder_page - 1:])
    # The printed finder uses two compact chapter numbers per topic in two columns.
    finder_text = finder_text.split("Topic finder", 1)[-1]
    pairs = re.findall(r"\b(\d+)\s*·\s*(\d+)\b", finder_text)
    references = [int(value) for pair in pairs for value in pair]
    if not pairs:
        issues.append({"kind": "topic_finder_empty_references"})
    for reference in references:
        if not 1 <= reference <= args.chapters:
            issues.append({"kind": "topic_finder_chapter", "chapter": reference})

    result = {
        "pdf": str(pdf), "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "pages": len(pages), "expected_folios": "cover unnumbered; pages 2 through end numbered",
        "contents_entries": entries, "topic_finder_chapter_reference_count": len(references),
        "issues": issues,
        "scope": "Extracted text and locator alignment only; not visible layout, topic accuracy, binding geometry, or release approval",
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered)
    else:
        print(rendered, end="")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
