#!/usr/bin/env python3
"""Independently audit the AIMA 4e filename and public-URL migration."""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from aima_routes import AIMA_CHAPTER_ROUTE_MAP
from redirects import BASE_URL, absolute_url, edge_aliases

ROOT = Path(__file__).resolve().parent.parent
AIMA_DIR = ROOT / "aima-4e"

# Deliberately duplicated from the generator source of truth.  This checker is
# meant to fail if that source is accidentally reordered or silently changed.
EXPECTED_ROUTES: tuple[tuple[str, str], ...] = (
    ("00-پیشگفتار", "00-preface"),
    ("01-فصل۱-مقدمه", "01-introduction"),
    ("02-فصل۲-عاملهای-هوشمند", "02-intelligent-agents"),
    ("03-فصل۳-حل-مسئله-با-جستجو", "03-solving-problems-by-searching"),
    ("04-فصل۴-جستجو-در-محیطهای-پیچیده", "04-search-in-complex-environments"),
    ("05-فصل۵-جستجوی-رقابتی-و-بازیها", "05-adversarial-search-and-games"),
    ("06-فصل۶-ارضای-قیود", "06-constraint-satisfaction-problems"),
    ("07-فصل۷-عاملهای-منطقی", "07-logical-agents"),
    ("08-فصل۸-منطق-مرتبه-اول", "08-first-order-logic"),
    ("09-فصل۹-استنتاج-منطق-مرتبه-اول", "09-inference-in-first-order-logic"),
    ("10-فصل۱۰-بازنمایی-دانش", "10-knowledge-representation"),
    ("11-فصل۱۱-برنامهریزی-خودکار", "11-automated-planning"),
    ("12-فصل۱۲-کمی-کردن-عدم-قطعیت", "12-quantifying-uncertainty"),
    ("13-فصل۱۳-استدلال-احتمالاتی", "13-probabilistic-reasoning"),
    ("14-فصل۱۴-استدلال-احتمالاتی-در-طول-زمان", "14-probabilistic-reasoning-over-time"),
    ("15-فصل۱۵-برنامهنویسی-احتمالاتی", "15-probabilistic-programming"),
    ("16-فصل۱۶-تصمیمگیری-ساده", "16-making-simple-decisions"),
    ("17-فصل۱۷-تصمیمگیری-پیچیده", "17-making-complex-decisions"),
    ("18-فصل۱۸-تصمیمگیری-چندعاملی", "18-multiagent-decision-making"),
    ("19-فصل۱۹-یادگیری-از-مثالها", "19-learning-from-examples"),
    ("20-فصل۲۰-یادگیری-مدلهای-احتمالاتی", "20-learning-probabilistic-models"),
    ("21-فصل۲۱-یادگیری-عمیق", "21-deep-learning"),
    ("22-فصل۲۲-یادگیری-تقویتی", "22-reinforcement-learning"),
    ("23-فصل۲۳-پردازش-زبان-طبیعی", "23-natural-language-processing"),
    ("24-فصل۲۴-یادگیری-عمیق-زبان-طبیعی", "24-deep-learning-for-natural-language-processing"),
    ("25-فصل۲۵-بینایی-رایانهای", "25-computer-vision"),
    ("26-فصل۲۶-رباتیک", "26-robotics"),
    ("27-فصل۲۷-فلسفه-اخلاق-ایمنی", "27-philosophy-ethics-and-safety-of-ai"),
    ("28-فصل۲۸-آینده-هوش-مصنوعی", "28-the-future-of-ai"),
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.links: list[tuple[str, str, dict[str, str]]] = []
        self.meta: dict[tuple[str, str], list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        lower_tag = tag.lower()
        if lower_tag == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonicals.append(data.get("href", ""))
        if lower_tag == "meta":
            for key in ("name", "property"):
                if data.get(key):
                    self.meta.setdefault((key, data[key].lower()), []).append(data.get("content", ""))
        for attribute in ("href", "src"):
            if data.get(attribute):
                self.links.append((attribute, data[attribute], data))


def parse_page(path: Path) -> tuple[str, PageParser]:
    raw = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(raw)
    return raw, parser


def has_non_ascii_or_space(value: str) -> bool:
    return any(ord(character) > 127 or character.isspace() for character in value)


def json_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from json_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from json_strings(item)


def main() -> int:
    errors: list[str] = []
    expected_stems = tuple(canonical for _, canonical in EXPECTED_ROUTES)
    expected_set = set(expected_stems)
    expected_files = {f"{stem}.html" for stem in expected_stems}
    expected_urls = {f"{BASE_URL}/aima-4e/{stem}" for stem in expected_stems}

    if tuple(AIMA_CHAPTER_ROUTE_MAP) != EXPECTED_ROUTES:
        errors.append("scripts/aima_routes.py no longer matches the independently reviewed mapping")

    for number, stem in enumerate(expected_stems):
        if not re.fullmatch(rf"{number:02d}-[a-z0-9]+(?:-[a-z0-9]+)*", stem):
            errors.append(f"chapter {number:02d} has a noncanonical slug: {stem!r}")
        if has_non_ascii_or_space(stem):
            errors.append(f"chapter {number:02d} route is not ASCII/space-free: {stem!r}")

    actual_files = {
        path.name for path in AIMA_DIR.glob("*.html") if path.name != "index.html"
    }
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        unexpected = sorted(actual_files - expected_files)
        if missing:
            errors.append(f"missing canonical chapter files: {', '.join(missing)}")
        if unexpected:
            errors.append(f"unexpected chapter files: {', '.join(unexpected)}")

    # Every chapter is self-canonical and may publish only canonical AIMA links.
    for stem in expected_stems:
        path = AIMA_DIR / f"{stem}.html"
        if not path.is_file():
            continue
        raw, page = parse_page(path)
        canonical = f"{BASE_URL}/aima-4e/{stem}"
        if page.canonicals != [canonical]:
            errors.append(f"{path.name}: canonical must be {canonical!r}, got {page.canonicals!r}")

        values = page.meta.get(("property", "og:url"), [])
        if values != [canonical]:
            errors.append(f"{path.name}: og:url must be {canonical!r}, got {values!r}")

        base = canonical
        for attribute, value, _ in page.links:
            if value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            resolved = urllib.parse.urlparse(urllib.parse.urljoin(base, value))
            if resolved.netloc not in ("", "www.alirostami.com", "alirostami.com"):
                continue
            decoded_path = urllib.parse.unquote(resolved.path)
            if not decoded_path.startswith("/aima-4e/"):
                continue
            route = decoded_path.removeprefix("/aima-4e/").rstrip("/")
            if not route:
                continue
            if route.endswith(".html"):
                errors.append(f"{path.name}: {attribute} publishes .html chapter URL {value!r}")
                route = route.removesuffix(".html")
            if route not in expected_set:
                errors.append(f"{path.name}: {attribute} publishes unknown/legacy AIMA route {value!r}")

        for match in re.finditer(
            r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            try:
                payload = json.loads(match.group(1))
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}: invalid JSON-LD: {exc}")
                continue
            for value in json_strings(payload):
                if not value.startswith(f"{BASE_URL}/aima-4e/"):
                    continue
                parsed = urllib.parse.urlparse(value)
                route = urllib.parse.unquote(parsed.path).removeprefix("/aima-4e/").rstrip("/")
                if route and route not in expected_set:
                    errors.append(f"{path.name}: JSON-LD publishes unknown/legacy route {value!r}")
                if has_non_ascii_or_space(parsed.path) or parsed.path.endswith(".html"):
                    errors.append(f"{path.name}: JSON-LD route is not canonical ASCII extensionless URL {value!r}")

    # The generated reader must expose only canonical routes in navigation,
    # iframe source, and its CHAPTERS payload.  Its private LEGACY_ROUTES table
    # is intentionally retained so historical hash deep links still resolve.
    index_raw, index_page = parse_page(AIMA_DIR / "index.html")
    chapters_match = re.search(r"const CHAPTERS = (\[.*?\]);\s*const LEGACY_ROUTES", index_raw, re.DOTALL)
    if not chapters_match:
        errors.append("reader index is missing the generated CHAPTERS payload")
    else:
        try:
            chapters = json.loads(chapters_match.group(1))
            routes = tuple(chapter.get("route") for chapter in chapters)
            filenames = tuple(chapter.get("filename") for chapter in chapters)
            if routes != expected_stems:
                errors.append(f"reader CHAPTERS routes are out of order or stale: {routes!r}")
            if filenames != tuple(f"{stem}.html" for stem in expected_stems):
                errors.append("reader CHAPTERS filenames are out of sync with canonical files")
        except (json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"reader CHAPTERS payload is invalid: {exc}")

    title_links = [
        value
        for _, value, attrs in index_page.links
        if "ch-title-link" in attrs.get("class", "").split()
    ]
    if title_links != list(expected_stems):
        errors.append("reader sidebar chapter links do not publish the 29 canonical routes in order")
    iframe_sources = [
        value
        for attribute, value, attrs in index_page.links
        if attribute == "src" and attrs.get("id") == "book-frame"
    ]
    if iframe_sources != [expected_stems[0]]:
        errors.append(f"reader iframe must start at {expected_stems[0]!r}, got {iframe_sources!r}")

    for attribute, value, _ in index_page.links:
        if value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        resolved = urllib.parse.urlparse(urllib.parse.urljoin(f"{BASE_URL}/aima-4e/", value))
        if resolved.netloc not in ("", "www.alirostami.com", "alirostami.com"):
            continue
        decoded_path = urllib.parse.unquote(resolved.path)
        if not decoded_path.startswith("/aima-4e/"):
            continue
        route = decoded_path.removeprefix("/aima-4e/").rstrip("/")
        if route and route not in expected_set:
            errors.append(f"reader {attribute} publishes unknown/legacy AIMA route {value!r}")
        if route.endswith(".html"):
            errors.append(f"reader {attribute} publishes .html chapter URL {value!r}")

    # Sitemap chapter locations must be the exact ASCII extensionless set.
    try:
        sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
        locations = [node.text or "" for node in sitemap_root.iter() if node.tag.endswith("loc")]
    except (ET.ParseError, FileNotFoundError) as exc:
        errors.append(f"cannot read sitemap.xml: {exc}")
        locations = []
    aima_locations = {
        location
        for location in locations
        if urllib.parse.urlparse(location).path.startswith("/aima-4e/")
        and urllib.parse.urlparse(location).path != "/aima-4e/"
    }
    if aima_locations != expected_urls:
        missing = sorted(expected_urls - aima_locations)
        unexpected = sorted(aima_locations - expected_urls)
        if missing:
            errors.append(f"sitemap is missing AIMA routes: {', '.join(missing)}")
        if unexpected:
            errors.append(f"sitemap publishes stale AIMA routes: {', '.join(unexpected)}")
    for location in aima_locations:
        path = urllib.parse.urlparse(location).path
        if has_non_ascii_or_space(path) or path.endswith(".html"):
            errors.append(f"sitemap AIMA URL is not ASCII and extensionless: {location!r}")

    # All historical forms must be one-hop edge aliases to the new canonical.
    redirects = edge_aliases()
    required_redirects: dict[str, str] = {}
    for number, (legacy_stem, canonical_stem) in enumerate(EXPECTED_ROUTES):
        destination = f"/aima-4e/{canonical_stem}"
        malformed_stem = f"{number:02d}- "
        for old_stem in (legacy_stem, malformed_stem):
            encoded = urllib.parse.quote(old_stem)
            required_redirects[f"/aima-4e/{encoded}"] = destination
            required_redirects[f"/aima-4e/{encoded}.html"] = destination
        required_redirects[f"/aima-4e/{canonical_stem}.html"] = destination
        if f"/aima-4e/{canonical_stem}" in redirects:
            errors.append(f"canonical route redirects unexpectedly: /aima-4e/{canonical_stem}")

    for source, destination in required_redirects.items():
        if redirects.get(source) != destination:
            errors.append(
                f"missing direct AIMA redirect {source!r} -> {destination!r}; "
                f"got {redirects.get(source)!r}"
            )

    try:
        manifest_rows = {
            tuple(line.split())
            for line in (ROOT / "_redirects").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
    except FileNotFoundError:
        manifest_rows = set()
        errors.append("missing generated _redirects manifest")
    for source, destination in required_redirects.items():
        row = (source, absolute_url(destination), "301")
        if row not in manifest_rows:
            errors.append(f"_redirects is missing one-hop 301 row: {' '.join(row)}")

    if errors:
        print(f"AIMA route audit failed with {len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "AIMA route audit passed: "
        f"{len(expected_stems)} ASCII chapter files/canonicals, "
        f"{len(required_redirects)} one-hop compatibility redirects."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
