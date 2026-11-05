#!/usr/bin/env python3
"""Normalize the site header on every page except the two online book readers."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from image_utils import ROOT
from site_navigation import SEARCH_CONFIG, is_reader_page, render_site_navigation

HEADER_START_RE = re.compile(
    r'<header\b(?=[^>]*\bclass=["\'][^"\']*\bdesktop\b)[^>]*>',
    re.IGNORECASE | re.DOTALL,
)
MAIN_START_RE = re.compile(r"<main\b[^>]*>", re.IGNORECASE | re.DOTALL)
WINDOW_CONFIG_RE = re.compile(
    r'(<script\b[^>]*>\s*window\.config\s*=\s*)(\{.*?\})(;\s*</script\s*>)',
    re.IGNORECASE | re.DOTALL,
)


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "layouts" not in path.parts
    ]


def update_search_config(raw: str, relative: str) -> str:
    match = WINDOW_CONFIG_RE.search(raw)
    if match is None:
        raise ValueError(f"{relative}: window.config script is missing")
    try:
        config = json.loads(match.group(2))
    except json.JSONDecodeError as error:
        raise ValueError(f"{relative}: window.config is not valid JSON: {error}") from error
    config["search"] = dict(SEARCH_CONFIG)
    serialized = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    return f"{raw[:match.start(2)]}{serialized}{raw[match.end(2):]}"


def update_page(path: Path, raw: str) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if is_reader_page(relative):
        return raw

    header = HEADER_START_RE.search(raw)
    if header is None:
        raise ValueError(f"{relative}: desktop header is missing")
    main = MAIN_START_RE.search(raw, header.end())
    if main is None:
        raise ValueError(f"{relative}: main element is missing after the header")

    normalized = f"{raw[:header.start()]}{render_site_navigation(relative)}{raw[main.start():]}"
    return update_search_config(normalized, relative)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated navigation is stale")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed: list[str] = []
    standard = 0
    readers = 0
    for path in html_pages():
        relative = path.relative_to(ROOT).as_posix()
        if is_reader_page(relative):
            readers += 1
            continue
        standard += 1
        raw = path.read_text(encoding="utf-8", errors="strict")
        updated = update_page(path, raw)
        if updated == raw:
            continue
        changed.append(relative)
        if not args.check:
            path.write_text(updated, encoding="utf-8")

    if args.check and changed:
        print(f"site navigation is stale in {len(changed)} file(s):")
        for relative in changed:
            print(f"  - {relative}")
        return 1

    action = "would update" if args.check else "updated"
    print(f"site navigation {action}: {len(changed)} HTML files")
    print(f"navigation scope: {standard} unified standard pages; {readers} reader pages preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
