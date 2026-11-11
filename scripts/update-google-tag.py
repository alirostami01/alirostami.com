#!/usr/bin/env python3
"""Install the shared Google tag once in the head of every deployable HTML page."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from google_tag import END_MARKER, SCRIPT_URL, START_MARKER, render_google_tag

ROOT = Path(__file__).resolve().parent.parent
HEAD_RE = re.compile(r"<head\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
MANAGED_BLOCK_RE = re.compile(
    rf"^[ \t]*{re.escape(START_MARKER)}[ \t]*\r?\n.*?"
    rf"^[ \t]*{re.escape(END_MARKER)}[ \t]*(?:\r?\n)?",
    flags=re.IGNORECASE | re.DOTALL | re.MULTILINE,
)


def html_pages() -> list[Path]:
    """Return published HTML, excluding Hugo source partials and hidden trees."""
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "layouts" not in path.parts
    ]


def update_page(raw: str) -> str:
    """Replace managed copies and place one canonical block after opening head."""
    starts = raw.count(START_MARKER)
    ends = raw.count(END_MARKER)
    if starts != ends:
        raise ValueError(f"unbalanced Google tag markers ({starts} start, {ends} end)")

    cleaned = MANAGED_BLOCK_RE.sub("", raw)
    if SCRIPT_URL in cleaned:
        raise ValueError("unmanaged Google tag loader already exists")

    head = HEAD_RE.search(cleaned)
    if head is None:
        raise ValueError("missing <head> element")

    linebreak = "\r\n" if "\r\n" in cleaned else "\n"
    block = render_google_tag("    ").replace("\n", linebreak)
    tail = cleaned[head.end() :]
    separator = "" if tail.startswith(("\n", "\r")) else linebreak
    return f"{cleaned[:head.end()]}{linebreak}{block}{separator}{tail}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report stale HTML without writing files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed: list[Path] = []
    errors: list[str] = []

    for page in html_pages():
        relative = page.relative_to(ROOT)
        raw = page.read_text(encoding="utf-8", errors="strict")
        try:
            updated = update_page(raw)
        except ValueError as exc:
            errors.append(f"{relative.as_posix()}: {exc}")
            continue
        if updated == raw:
            continue
        changed.append(relative)
        if not args.check:
            page.write_text(updated, encoding="utf-8")

    if errors:
        print("Google tag update failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    if args.check and changed:
        print("Google tag output is stale:")
        for page in changed:
            print(f"  - {page.as_posix()}")
        return 1

    action = "would update" if args.check else "updated"
    print(f"Google tag {action}: {len(changed)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
