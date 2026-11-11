#!/usr/bin/env python3
"""Audit site-wide Google Tag Manager installation, CSP, and build integration."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from google_tag import CONTAINER_ID, END_MARKER, SCRIPT_URL, START_MARKER, render_google_tag

ROOT = Path(__file__).resolve().parent.parent
HEAD_RE = re.compile(r"<head\b[^>]*>(.*?)</head\s*>", re.IGNORECASE | re.DOTALL)


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "layouts" not in path.parts
    ]


def main() -> int:
    errors: list[str] = []
    pages = html_pages()
    expected_block = render_google_tag("    ")

    for page in pages:
        relative = page.relative_to(ROOT).as_posix()
        raw = page.read_text(encoding="utf-8", errors="strict")
        head = HEAD_RE.search(raw)
        if head is None:
            errors.append(f"{relative}: missing complete head element")
            continue
        head_html = head.group(1)

        if raw.count(START_MARKER) != 1 or raw.count(END_MARKER) != 1:
            errors.append(f"{relative}: expected one balanced managed Google tag block")
        if raw.count(SCRIPT_URL) != 1:
            errors.append(f"{relative}: expected one Google tag loader")
        if raw.count(CONTAINER_ID) != 1:
            errors.append(f"{relative}: expected container {CONTAINER_ID} exactly once")
        if expected_block not in head_html:
            errors.append(f"{relative}: canonical Google tag block is missing from head")
        if not re.search(
            rf'<script\s+async\s+src=["\']{re.escape(SCRIPT_URL)}["\']></script>',
            head_html,
            flags=re.IGNORECASE,
        ):
            errors.append(f"{relative}: Google tag loader is not async")
        for statement in (
            "window.dataLayer = window.dataLayer || [];",
            "function gtag(){dataLayer.push(arguments);}",
            "gtag('js', new Date());",
        ):
            if head_html.count(statement) != 1:
                errors.append(f"{relative}: missing/duplicate initializer {statement!r}")

    custom_head = (ROOT / "layouts/partials/custom-head.html").read_text(encoding="utf-8")
    if render_google_tag("") not in custom_head:
        errors.append("layouts/partials/custom-head.html: canonical Google tag block is missing")

    theme = (ROOT / "scripts/theme.py").read_text(encoding="utf-8")
    if "from google_tag import render_google_tag" not in theme or "GOOGLE_TAG_HEAD" not in theme:
        errors.append("scripts/theme.py: shared Google tag renderer is not integrated")

    helper = (ROOT / "scripts/image_utils.py").read_text(encoding="utf-8")
    google_call = 'run_postprocessor("update-google-tag.py")'
    performance_call = 'run_postprocessor("update-performance.py")'
    if google_call not in helper:
        errors.append("scripts/image_utils.py: Google tag post-processor is missing")
    elif performance_call not in helper or helper.index(google_call) > helper.index(performance_call):
        errors.append("scripts/image_utils.py: Google tag must run before performance processing")

    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    for source in (
        "https://www.googletagmanager.com",
        "https://*.googletagmanager.com",
        "https://*.google-analytics.com",
        "https://*.analytics.google.com",
    ):
        if source not in headers:
            errors.append(f"_headers: CSP source is missing: {source}")

    idempotence = subprocess.run(
        [sys.executable, str(ROOT / "scripts/update-google-tag.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if idempotence.returncode != 0:
        errors.append(
            "Google tag post-processor is not idempotent: "
            + (idempotence.stdout + idempotence.stderr).strip()
        )

    if errors:
        print(f"Google tag audit failed with {len(errors)} issue(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        f"Google tag audit passed: {len(pages)} HTML files load {CONTAINER_ID} "
        "once in head; CSP and generator integration are current."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
