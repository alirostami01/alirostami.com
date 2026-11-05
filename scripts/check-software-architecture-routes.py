#!/usr/bin/env python3
"""Independently audit the software-architecture chapter URL migration."""

from __future__ import annotations

import csv
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from redirects import BASE_URL, absolute_url, edge_aliases
from software_architecture_routes import SOFTWARE_ARCHITECTURE_ROUTE_MAP

ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = ROOT / "software-architecture"

# Deliberately duplicated from the generator source of truth so an accidental
# edit to that source cannot silently redefine what the checker accepts.
EXPECTED_ROUTES: tuple[tuple[str, str], ...] = (
    ("chapter-01", "01-introduction"),
    ("chapter-02", "02-architectural-thinking"),
    ("chapter-03", "03-modularity"),
    ("chapter-04", "04-architectural-characteristics-defined"),
    ("chapter-05", "05-identifying-architectural-characteristics"),
    ("chapter-06", "06-measuring-and-governing-architectural-characteristics"),
    ("chapter-07", "07-the-scope-of-architectural-characteristics"),
    ("chapter-08", "08-component-based-thinking"),
    ("chapter-09", "09-foundations"),
    ("chapter-10", "10-layered-architecture-style"),
    ("chapter-11", "11-the-modular-monolith-architecture-style"),
    ("chapter-12", "12-pipeline-architecture-style"),
    ("chapter-13", "13-microkernel-architecture-style"),
    ("chapter-14", "14-service-based-architecture-style"),
    ("chapter-15", "15-event-driven-architecture-style"),
    ("chapter-16", "16-space-based-architecture-style"),
    ("chapter-17", "17-orchestration-driven-service-oriented-architecture"),
    ("chapter-18", "18-microservices-architecture"),
    ("chapter-19", "19-choosing-the-appropriate-architecture-style"),
    ("chapter-20", "20-architectural-patterns"),
    ("chapter-21", "21-architectural-decisions"),
    ("chapter-22", "22-analyzing-architecture-risk"),
    ("chapter-23", "23-diagramming-architecture"),
    ("chapter-24", "24-making-teams-effective"),
    ("chapter-25", "25-negotiation-and-leadership-skills"),
    ("chapter-26", "26-architectural-intersections"),
    ("chapter-27", "27-the-laws-of-software-architecture-revisited"),
    ("appendix", "appendix-discussion-questions"),
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.links: list[tuple[str, str, dict[str, str]]] = []
        self.meta: dict[tuple[str, str], list[str]] = {}
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        lower_tag = tag.lower()
        if data.get("id"):
            self.ids.add(data["id"])
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


def schema_nodes(payload: object):
    if isinstance(payload, dict):
        graph = payload.get("@graph")
        if isinstance(graph, list):
            for node in graph:
                if isinstance(node, dict):
                    yield node
        else:
            yield payload


def internal_architecture_route(base: str, value: str) -> str | None:
    resolved = urllib.parse.urlparse(urllib.parse.urljoin(base, value))
    if resolved.netloc not in ("", "www.alirostami.com", "alirostami.com"):
        return None
    decoded = urllib.parse.unquote(resolved.path)
    if not decoded.startswith("/software-architecture/"):
        return None
    return decoded.removeprefix("/software-architecture/").rstrip("/")


def main() -> int:
    errors: list[str] = []
    expected_stems = tuple(canonical for _, canonical in EXPECTED_ROUTES)
    expected_set = set(expected_stems)
    expected_files = {f"{stem}.html" for stem in expected_stems}
    expected_urls = {
        f"{BASE_URL}/software-architecture/{stem}" for stem in expected_stems
    }

    if tuple(SOFTWARE_ARCHITECTURE_ROUTE_MAP) != EXPECTED_ROUTES:
        errors.append(
            "scripts/software_architecture_routes.py no longer matches the independently reviewed mapping"
        )

    for position, stem in enumerate(expected_stems, start=1):
        valid = (
            re.fullmatch(rf"{position:02d}-[a-z0-9]+(?:-[a-z0-9]+)*", stem)
            if position <= 27
            else re.fullmatch(r"appendix-[a-z0-9]+(?:-[a-z0-9]+)*", stem)
        )
        if not valid:
            errors.append(f"chapter position {position} has a noncanonical slug: {stem!r}")
        if has_non_ascii_or_space(stem):
            errors.append(f"chapter route is not ASCII/space-free: {stem!r}")

    actual_files = {
        path.name for path in BOOK_DIR.glob("*.html") if path.name != "index.html"
    }
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        unexpected = sorted(actual_files - expected_files)
        if missing:
            errors.append(f"missing canonical chapter files: {', '.join(missing)}")
        if unexpected:
            errors.append(f"unexpected chapter files: {', '.join(unexpected)}")

    # Chapters must be self-canonical and publish only canonical chapter hrefs.
    for position, stem in enumerate(expected_stems, start=1):
        path = BOOK_DIR / f"{stem}.html"
        if not path.is_file():
            continue
        raw, page = parse_page(path)
        canonical = f"{BASE_URL}/software-architecture/{stem}"
        if page.canonicals != [canonical]:
            errors.append(f"{path.name}: canonical must be {canonical!r}, got {page.canonicals!r}")
        og_urls = page.meta.get(("property", "og:url"), [])
        if og_urls != [canonical]:
            errors.append(f"{path.name}: og:url must be {canonical!r}, got {og_urls!r}")

        for attribute, value, _attrs in page.links:
            if attribute != "href" or value.startswith(
                ("#", "mailto:", "tel:", "javascript:", "data:")
            ):
                continue
            route = internal_architecture_route(canonical, value)
            if route is None or not route:
                continue
            if route.endswith(".html"):
                errors.append(f"{path.name}: href publishes .html chapter URL {value!r}")
                route = route.removesuffix(".html")
            if route not in expected_set:
                errors.append(
                    f"{path.name}: href publishes unknown/legacy architecture route {value!r}"
                )

        chapter_positions: list[object] = []
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
            for node in schema_nodes(payload):
                node_type = node.get("@type")
                types = set(node_type if isinstance(node_type, list) else [node_type])
                if "Chapter" in types:
                    chapter_positions.append(node.get("position"))
            for value in json_strings(payload):
                if not value.startswith(f"{BASE_URL}/software-architecture/"):
                    continue
                parsed = urllib.parse.urlparse(value)
                route = urllib.parse.unquote(parsed.path).removeprefix(
                    "/software-architecture/"
                ).rstrip("/")
                if route and route not in expected_set:
                    errors.append(
                        f"{path.name}: JSON-LD publishes unknown/legacy route {value!r}"
                    )
                if has_non_ascii_or_space(parsed.path) or parsed.path.endswith(".html"):
                    errors.append(
                        f"{path.name}: JSON-LD route is not ASCII/extensionless {value!r}"
                    )
        if chapter_positions != [position]:
            errors.append(
                f"{path.name}: Chapter.position must be {position}, got {chapter_positions!r}"
            )

    # Reader navigation, iframe, payload, and route-fragment targets.
    index_raw, index_page = parse_page(BOOK_DIR / "index.html")
    chapters_match = re.search(
        r"const CHAPTERS = (\[.*?\]);\s*const LEGACY_ROUTES",
        index_raw,
        re.DOTALL,
    )
    if not chapters_match:
        errors.append("reader index is missing the generated CHAPTERS payload")
    else:
        try:
            chapters = json.loads(chapters_match.group(1))
            routes = tuple(chapter.get("filename") for chapter in chapters)
            if routes != expected_stems:
                errors.append(f"reader CHAPTERS routes are stale or out of order: {routes!r}")
        except (json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"reader CHAPTERS payload is invalid: {exc}")

    legacy_match = re.search(
        r"const LEGACY_ROUTES = (\{.*?\});\s*let currentChapterIdx",
        index_raw,
        re.DOTALL,
    )
    if not legacy_match:
        errors.append("reader index is missing the LEGACY_ROUTES compatibility payload")
    else:
        try:
            legacy_routes = json.loads(legacy_match.group(1))
            for index, (legacy, canonical) in enumerate(EXPECTED_ROUTES):
                if legacy_routes.get(legacy) != canonical:
                    errors.append(f"reader does not preserve legacy hash route {legacy!r}")
                if legacy_routes.get(f"ch-item-{index}") != canonical:
                    errors.append(f"reader does not preserve historical ch-item-{index} hash")
        except json.JSONDecodeError as exc:
            errors.append(f"reader LEGACY_ROUTES payload is invalid: {exc}")

    title_links = [
        value
        for _attribute, value, attrs in index_page.links
        if "ch-title-link" in attrs.get("class", "").split()
    ]
    if title_links != list(expected_stems):
        errors.append("reader sidebar links do not publish all 28 canonical routes in order")
    iframe_sources = [
        value
        for attribute, value, attrs in index_page.links
        if attribute == "src" and attrs.get("id") == "book-frame"
    ]
    if iframe_sources != [expected_stems[0]]:
        errors.append(f"reader iframe must start at {expected_stems[0]!r}, got {iframe_sources!r}")
    missing_ids = sorted(expected_set - index_page.ids)
    if missing_ids:
        errors.append(f"reader is missing canonical deep-link targets: {', '.join(missing_ids)}")

    for attribute, value, _attrs in index_page.links:
        if value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        route = internal_architecture_route(f"{BASE_URL}/software-architecture/", value)
        if route is None or not route:
            continue
        if route.endswith(".html"):
            errors.append(f"reader {attribute} publishes .html chapter URL {value!r}")
            route = route.removesuffix(".html")
        if route not in expected_set:
            errors.append(f"reader {attribute} publishes unknown/legacy route {value!r}")

    # Project table links should open the reader on canonical chapter hashes.
    _project_raw, project_page = parse_page(
        ROOT / "fundamentals-of-software-architecture-persian" / "index.html"
    )
    project_hashes = [
        urllib.parse.unquote(urllib.parse.urlparse(value).fragment)
        for attribute, value, _attrs in project_page.links
        if attribute == "href" and value.startswith("/software-architecture/#")
    ]
    expected_hashes = [stem for stem in expected_stems for _ in range(2)]
    if project_hashes != expected_hashes:
        errors.append("project chapter table does not publish canonical reader deep links")

    # Sitemap must contain exactly the new extensionless chapter URLs.
    try:
        sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
        locations = [node.text or "" for node in sitemap_root.iter() if node.tag.endswith("loc")]
    except (ET.ParseError, FileNotFoundError) as exc:
        errors.append(f"cannot read sitemap.xml: {exc}")
        locations = []
    architecture_locations = {
        location
        for location in locations
        if urllib.parse.urlparse(location).path.startswith("/software-architecture/")
        and urllib.parse.urlparse(location).path != "/software-architecture/"
    }
    if architecture_locations != expected_urls:
        missing = sorted(expected_urls - architecture_locations)
        unexpected = sorted(architecture_locations - expected_urls)
        if missing:
            errors.append(f"sitemap is missing architecture routes: {', '.join(missing)}")
        if unexpected:
            errors.append(f"sitemap publishes stale architecture routes: {', '.join(unexpected)}")
    for location in architecture_locations:
        route_path = urllib.parse.urlparse(location).path
        if has_non_ascii_or_space(route_path) or route_path.endswith(".html"):
            errors.append(f"sitemap route is not ASCII and extensionless: {location!r}")

    # Every old route and every canonical .html spelling is one direct 301 hop.
    redirects = edge_aliases()
    required_redirects: dict[str, str] = {}
    for legacy_stem, canonical_stem in EXPECTED_ROUTES:
        destination = f"/software-architecture/{canonical_stem}"
        required_redirects[f"/software-architecture/{legacy_stem}"] = destination
        required_redirects[f"/software-architecture/{legacy_stem}.html"] = destination
        required_redirects[f"/software-architecture/{canonical_stem}.html"] = destination
        if f"/software-architecture/{canonical_stem}" in redirects:
            errors.append(
                f"canonical route redirects unexpectedly: /software-architecture/{canonical_stem}"
            )
    for source, destination in required_redirects.items():
        if redirects.get(source) != destination:
            errors.append(
                f"missing direct architecture redirect {source!r} -> {destination!r}; "
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

    try:
        with (ROOT / "cloudflare-bulk-redirects.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            bulk_rows = {tuple(row) for row in csv.reader(handle)}
    except FileNotFoundError:
        bulk_rows = set()
        errors.append("missing generated cloudflare-bulk-redirects.csv")
    for source, destination in required_redirects.items():
        target = absolute_url(destination)
        for host in ("alirostami.com", "www.alirostami.com"):
            row = (
                f"{host}{source}",
                target,
                "301",
                "true",
                "false",
                "false",
                "false",
            )
            if row not in bulk_rows:
                errors.append(f"bulk manifest is missing direct redirect for {host}{source}")

    if errors:
        print(
            f"Software-architecture route audit failed with {len(errors)} problem(s):"
        )
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "Software-architecture route audit passed: "
        f"{len(expected_stems)} ASCII chapter files/canonicals, "
        f"{len(required_redirects)} one-hop compatibility redirects."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
