#!/usr/bin/env python3
"""Fail fast on Phase-1 URL, canonical, redirect, and sitemap regressions."""

from __future__ import annotations

import csv
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from redirects import (
    ALIASES,
    BASE_URL,
    ROOT,
    absolute_url,
    bulk_redirect_rows,
    edge_aliases,
)


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.hrefs: list[str] = []
        self.html_lang = ""
        self.html_dir = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "html":
            self.html_lang = data.get("lang", "")
            self.html_dir = data.get("dir", "")
        if tag.lower() == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonicals.append(data.get("href", ""))
        if tag.lower() == "meta" and data.get("name", "").lower() == "robots":
            self.robots.append(data.get("content", ""))
        if data.get("href"):
            self.hrefs.append(data["href"])
        if data.get("src"):
            self.hrefs.append(data["src"])


def parse_html(path: Path) -> HeadParser:
    parser = HeadParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser


def route_for_file(relative: str) -> str:
    path = Path(relative)
    if path.name == "index.html":
        parent = path.parent.as_posix()
        return "/" if parent == "." else f"/{parent}/"
    return f"/{path.as_posix()}"


def file_for_url(url: str) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)
    relative = path.lstrip("/")
    if not relative:
        candidate = ROOT / "index.html"
    elif path.endswith("/"):
        candidate = ROOT / relative / "index.html"
    else:
        candidate = ROOT / relative
        if not candidate.is_file() and not candidate.suffix:
            candidate = ROOT / f"{relative}.html"
    return candidate if candidate.is_file() else None


def main() -> int:
    errors: list[str] = []

    # Preferred homepage and robots declaration.
    home = parse_html(ROOT / "index.html")
    if home.html_lang.lower() != "fa-ir" or home.html_dir.lower() != "rtl":
        errors.append("index.html must use lang=fa-IR and dir=rtl")
    if home.canonicals != [f"{BASE_URL}/"]:
        errors.append(f"index.html canonical is invalid: {home.canonicals!r}")

    not_found = parse_html(ROOT / "404.html")
    if not any("noindex" in directive.lower() for directive in not_found.robots):
        errors.append("404.html must be noindex")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    declarations = re.findall(r"^Sitemap:\s*(\S+)", robots, flags=re.MULTILINE | re.IGNORECASE)
    if declarations != [f"{BASE_URL}/sitemap.xml"]:
        errors.append(f"robots.txt must declare exactly one canonical sitemap: {declarations!r}")

    for legacy in (
        "fa/sitemap.xml",
        "en/sitemap.xml",
        "public/sitemap.xml",
        "public/fa/sitemap.xml",
        "fa/index.xml",
        "fa/categories/index.xml",
        "fa/tags/index.xml",
        "fa/404.html",
    ):
        if (ROOT / legacy).exists():
            errors.append(f"legacy index file still exists: {legacy}")

    # Cloudflare Pages consumes this deploy-time redirect manifest. Host-wide
    # non-www/HTTP normalization still requires a zone-level Redirect Rule.
    manifest_path = ROOT / "_redirects"
    try:
        manifest_rows = [
            tuple(line.split())
            for line in manifest_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    except FileNotFoundError:
        manifest_rows = []
        errors.append("missing Cloudflare Pages _redirects manifest")
    expected_rows = {
        (source, absolute_url(destination), "301")
        for source, destination in edge_aliases().items()
    }
    actual_rows = set(manifest_rows)
    if len(actual_rows) != len(manifest_rows):
        errors.append("_redirects contains duplicate rules")
    if actual_rows != expected_rows:
        errors.append("_redirects is out of sync with scripts/redirects.py")

    bulk_path = ROOT / "cloudflare-bulk-redirects.csv"
    try:
        with bulk_path.open(encoding="utf-8", newline="") as handle:
            actual_bulk_rows = [tuple(row) for row in csv.reader(handle)]
    except FileNotFoundError:
        actual_bulk_rows = []
        errors.append("missing Cloudflare Bulk Redirects CSV manifest")
    if actual_bulk_rows != bulk_redirect_rows():
        errors.append("cloudflare-bulk-redirects.csv is out of sync")

    # Redirect fallbacks must be noindex and canonicalize to their destination.
    alias_routes = set(edge_aliases())
    alias_routes.update(urllib.parse.unquote(route) for route in tuple(alias_routes))
    for relative, destination in ALIASES.items():
        path = ROOT / relative
        route = route_for_file(relative)
        alias_routes.add(route)
        if route.endswith("/") and route != "/":
            alias_routes.add(route.rstrip("/"))
        if not path.is_file():
            errors.append(f"missing redirect fallback: {relative}")
            continue
        parsed = parse_html(path)
        expected = f"{BASE_URL}{destination}"
        if parsed.canonicals != [expected]:
            errors.append(f"redirect canonical mismatch: {relative} -> {parsed.canonicals!r}")
        if not any("noindex" in directive.lower() for directive in parsed.robots):
            errors.append(f"redirect fallback is indexable: {relative}")
        if path.stat().st_size > 4096:
            errors.append(f"redirect fallback contains too much duplicate content: {relative}")

    # Validate the one canonical sitemap and every page it contains.
    sitemap_path = ROOT / "sitemap.xml"
    try:
        xml_root = ET.parse(sitemap_path).getroot()
    except (ET.ParseError, FileNotFoundError) as exc:
        errors.append(f"invalid sitemap.xml: {exc}")
        xml_root = ET.Element("empty")

    locations = [node.text or "" for node in xml_root.iter() if node.tag.endswith("loc")]
    if len(locations) != len(set(locations)):
        errors.append("sitemap.xml contains duplicate URLs")

    for location in locations:
        parsed_url = urllib.parse.urlparse(location)
        if parsed_url.scheme != "https" or parsed_url.netloc != "www.alirostami.com":
            errors.append(f"non-preferred host in sitemap: {location}")
            continue
        if parsed_url.path in alias_routes or parsed_url.path.startswith("/fa/"):
            errors.append(f"alias URL in sitemap: {location}")
        target = file_for_url(location)
        if target is None:
            errors.append(f"missing sitemap target: {location}")
            continue
        page = parse_html(target)
        if page.canonicals != [location]:
            errors.append(
                f"sitemap page is not self-canonical: {location} -> {page.canonicals!r}"
            )
        if any("noindex" in directive.lower() for directive in page.robots):
            errors.append(f"noindex URL in sitemap: {location}")

    # Canonical pages must never link back to known aliases or the bare host.
    html_files = sorted(ROOT.rglob("*.html"))
    for path in html_files:
        if ".git" in path.parts or "layouts" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in ALIASES:
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        if "https://alirostami.com" in raw or "http://alirostami.com" in raw:
            errors.append(f"bare-domain absolute URL in {relative}")
        page = parse_html(path)
        base = f"{BASE_URL}{route_for_file(relative)}"
        for href in page.hrefs:
            if href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            resolved = urllib.parse.urlparse(urllib.parse.urljoin(base, href))
            linked_host = resolved.netloc.lower()
            if linked_host and linked_host not in {"www.alirostami.com", "alirostami.com"}:
                continue
            if linked_host == "alirostami.com":
                errors.append(f"bare-domain internal link in {relative}: {href}")
                continue
            linked_path = urllib.parse.unquote(resolved.path)
            if linked_path in alias_routes:
                errors.append(f"internal alias link in {relative}: {href}")
            if file_for_url(urllib.parse.urlunparse(resolved)) is None:
                errors.append(f"broken internal link in {relative}: {href}")

    if errors:
        print(f"Phase-1 SEO URL audit failed with {len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "Phase-1 SEO URL audit passed: "
        f"{len(locations)} canonical sitemap URLs, "
        f"{len(ALIASES)} noindex redirect fallbacks, one preferred host."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
