#!/usr/bin/env python3
"""Audit the shared header while preserving the two specialized book readers."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

from site_navigation import MENU_ITEMS, SEARCH_CONFIG, active_menu_href, is_reader_page

ROOT = Path(__file__).resolve().parent.parent
WINDOW_CONFIG_RE = re.compile(
    r'<script\b[^>]*>\s*window\.config\s*=\s*(\{.*?\});\s*</script\s*>',
    re.IGNORECASE | re.DOTALL,
)


class NavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current_header = ""
        self.current_menu = ""
        self.headers: dict[str, dict[str, object]] = {}

    @staticmethod
    def data(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {name.lower(): value or "" for name, value in attrs}

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        data = self.data(attrs_list)
        classes = set(data.get("class", "").split())
        if tag == "header":
            kind = "desktop" if "desktop" in classes else "mobile" if "mobile" in classes else ""
            if kind:
                self.current_header = kind
                self.headers[kind] = {
                    "attrs": data,
                    "nav": {},
                    "links": [],
                    "active": [],
                    "brands": [],
                    "inputs": [],
                    "themes": 0,
                }
            return
        if not self.current_header:
            return
        record = self.headers[self.current_header]
        if tag == "nav" and "menu" in classes:
            self.current_menu = self.current_header
            record["nav"] = data
        elif tag == "a":
            href = data.get("href", "")
            if "menu-item" in classes and self.current_menu:
                record["links"].append(href)  # type: ignore[union-attr]
                if "active" in classes:
                    record["active"].append((href, data.get("aria-current", "")))  # type: ignore[union-attr]
            elif href == "/":
                record["brands"].append(href)  # type: ignore[union-attr]
        elif tag == "input" and data.get("id", "").startswith("search-input-"):
            record["inputs"].append(data.get("id", ""))  # type: ignore[union-attr]
        elif tag == "button" and "theme-switch" in classes:
            record["themes"] = int(record["themes"]) + 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.current_menu:
            self.current_menu = ""
        elif tag == "header" and self.current_header:
            self.current_header = ""


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "layouts" not in path.parts
    ]


def main() -> int:
    errors: list[str] = []
    expected_links = [item.href for item in MENU_ITEMS]
    standard_count = 0
    reader_count = 0

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    for path in html_pages():
        relative = path.relative_to(ROOT).as_posix()
        raw = path.read_text(encoding="utf-8", errors="strict")
        if is_reader_page(relative):
            reader_count += 1
            require(
                'data-site-navigation="unified"' not in raw,
                f"{relative}: specialized reader header was replaced",
            )
            continue

        standard_count += 1
        parser = NavigationParser()
        parser.feed(raw)
        require(set(parser.headers) == {"desktop", "mobile"}, f"{relative}: missing unified header pair")
        expected_active = active_menu_href(relative)
        for kind in ("desktop", "mobile"):
            record = parser.headers.get(kind)
            if not record:
                continue
            header_attrs = record["attrs"]
            nav_attrs = record["nav"]
            require(header_attrs.get("dir") == "rtl", f"{relative}: {kind} header is not RTL")
            require(
                header_attrs.get("data-site-navigation") == "unified",
                f"{relative}: {kind} header lacks the shared-navigation marker",
            )
            require(nav_attrs.get("dir") == "rtl", f"{relative}: {kind} menu is not RTL")
            require(
                nav_attrs.get("data-site-navigation") == "unified",
                f"{relative}: {kind} menu is not generated from the shared source",
            )
            require(record["links"] == expected_links, f"{relative}: {kind} menu links differ: {record['links']!r}")
            require(record["brands"] == ["/"], f"{relative}: {kind} brand does not link home exactly once")
            expected_input = f"search-input-{kind}"
            require(record["inputs"] == [expected_input], f"{relative}: {kind} search control differs")
            require(record["themes"] == 1, f"{relative}: {kind} must contain one theme control")
            active = record["active"]
            if expected_active:
                require(active == [(expected_active, "page")], f"{relative}: {kind} active menu item is incorrect")
            else:
                require(active == [], f"{relative}: {kind} has an unexpected active menu item")

        config_match = WINDOW_CONFIG_RE.search(raw)
        require(config_match is not None, f"{relative}: window.config is missing")
        if config_match is not None:
            try:
                config = json.loads(config_match.group(1))
            except json.JSONDecodeError as error:
                errors.append(f"{relative}: invalid window.config JSON: {error}")
            else:
                require(config.get("search") == SEARCH_CONFIG, f"{relative}: shared search config differs")

    require(standard_count == 12, f"expected 12 standard pages, found {standard_count}")
    require(reader_count == 59, f"expected 59 preserved reader pages, found {reader_count}")

    helper = (ROOT / "scripts/image_utils.py").read_text(encoding="utf-8")
    navigation_call = 'run_postprocessor("update-site-navigation.py")'
    internal_call = 'run_postprocessor("update-internal-links.py")'
    performance_call = 'run_postprocessor("update-performance.py")'
    require(navigation_call in helper, "generator pipeline does not run the navigation post-processor")
    require(
        helper.find(internal_call) < helper.find(navigation_call) < helper.find(performance_call),
        "navigation must run after internal links and before performance delivery",
    )
    for relative in (
        "scripts/theme.py",
        "scripts/build-project-page.py",
        "scripts/build-support-page.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8")
        require("site_navigation" in source, f"{relative}: shared navigation source is not connected")

    check = subprocess.run(
        [sys.executable, str(ROOT / "scripts/update-site-navigation.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(
        check.returncode == 0,
        "navigation post-processor is not idempotent: " + (check.stdout + check.stderr).strip(),
    )

    if errors:
        print(f"Site-navigation audit failed with {len(errors)} problem(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        "Site-navigation audit passed: "
        f"{standard_count} standard pages share {len(expected_links)} ordered menu routes; "
        f"{reader_count} online-reader pages retain specialized navigation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
