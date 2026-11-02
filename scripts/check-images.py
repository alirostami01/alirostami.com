#!/usr/bin/env python3
"""Independent Phase-2 audit for social metadata and content images.

This checker is stdlib-only and does not call the image post-processor. It fails
non-zero on missing representative images, metadata drift, broken image paths,
or layout-shift/loading regressions.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from image_utils import (
    BASE_URL,
    ROOT,
    SOCIAL_CARDS,
    SOCIAL_HEIGHT,
    SOCIAL_WIDTH,
    image_size,
    social_alt_for_page,
    social_card_for_page,
)

PRIORITY_IMAGE_PAGES = {
    "aima-4e-persian/index.html",
    "fundamentals-of-software-architecture-persian/index.html",
    "persian-streams/index.html",
    "persian-subtitles/index.html",
}
JSON_LD_RE = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>',
    flags=re.IGNORECASE | re.DOTALL,
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.images: list[dict[str, str]] = []
        self.canonicals: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {name.lower(): value or "" for name, value in attrs}
        lowered = tag.lower()
        if lowered == "meta":
            key = (data.get("property") or data.get("name") or "").lower()
            if key:
                self.meta[key].append(data.get("content", ""))
        elif lowered == "img":
            self.images.append(data)
        elif lowered == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonicals.append(data.get("href", ""))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def parse_page(path: Path) -> tuple[str, PageParser]:
    raw = path.read_text(encoding="utf-8", errors="strict")
    parser = PageParser()
    parser.feed(raw)
    return raw, parser


def file_for_url(url: str) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    relative = urllib.parse.unquote(parsed.path).lstrip("/")
    if not relative:
        candidate = ROOT / "index.html"
    elif parsed.path.endswith("/"):
        candidate = ROOT / relative / "index.html"
    else:
        candidate = ROOT / relative
        if not candidate.is_file() and not candidate.suffix:
            candidate = ROOT / f"{relative}.html"
    return candidate if candidate.is_file() else None


def sitemap_pages(errors: list[str]) -> dict[Path, str]:
    try:
        document = ET.parse(ROOT / "sitemap.xml").getroot()
    except (FileNotFoundError, ET.ParseError) as exc:
        errors.append(f"invalid sitemap.xml: {exc}")
        return {}
    pages: dict[Path, str] = {}
    for node in document.iter():
        if not node.tag.endswith("loc") or not node.text:
            continue
        location = node.text.strip()
        target = file_for_url(location)
        if target is None:
            errors.append(f"missing sitemap target: {location}")
            continue
        pages[target.resolve()] = location
    return pages


def indexable_pages(sitemap: dict[Path, str]) -> dict[Path, str]:
    """Discover every self-canonical HTML page that does not declare noindex."""
    result = dict(sitemap)
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts or "layouts" in page.parts or page.resolve() in result:
            continue
        _raw, parsed = parse_page(page)
        robots = [value.lower() for value in parsed.meta.get("robots", [])]
        if any("noindex" in directive for directive in robots):
            continue
        if len(parsed.canonicals) != 1 or not parsed.canonicals[0].startswith(f"{BASE_URL}/"):
            continue
        target = file_for_url(parsed.canonicals[0])
        if target is not None and target.resolve() == page.resolve():
            result[page.resolve()] = parsed.canonicals[0]
    return result


def one_meta(parser: PageParser, name: str, page: Path, errors: list[str]) -> str:
    values = parser.meta.get(name, [])
    if len(values) != 1:
        errors.append(f"{page.relative_to(ROOT)}: expected one {name} meta tag, found {len(values)}")
        return ""
    return values[0]


def schema_image_urls(document: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(document, dict):
        for key, value in document.items():
            if key == "image":
                if isinstance(value, str):
                    result.add(value)
                elif isinstance(value, dict):
                    for image_key in ("url", "contentUrl", "@id"):
                        image_value = value.get(image_key)
                        if isinstance(image_value, str):
                            result.add(image_value)
                elif isinstance(value, list):
                    for item in value:
                        result.update(schema_image_urls({"image": item}))
            result.update(schema_image_urls(value))
    elif isinstance(document, list):
        for value in document:
            result.update(schema_image_urls(value))
    return result


def check_indexable_metadata(pages: dict[Path, str], errors: list[str]) -> None:
    checked_cards: set[Path] = set()
    for page, _canonical in pages.items():
        raw, parsed = parse_page(page)
        relative = page.relative_to(ROOT)
        card = social_card_for_page(relative)
        expected_image = card.url
        expected_alt = social_alt_for_page(relative)
        checked_cards.add(card.path)

        robots = one_meta(parsed, "robots", page, errors).lower()
        if "max-image-preview:large" not in robots or "noindex" in robots:
            errors.append(f"{relative}: robots must allow max-image-preview:large")

        expected_meta = {
            "og:image": expected_image,
            "og:image:secure_url": expected_image,
            "og:image:type": "image/jpeg",
            "og:image:width": str(SOCIAL_WIDTH),
            "og:image:height": str(SOCIAL_HEIGHT),
            "og:image:alt": expected_alt,
            "twitter:card": "summary_large_image",
            "twitter:image": expected_image,
            "twitter:image:alt": expected_alt,
        }
        for name, expected in expected_meta.items():
            actual = one_meta(parsed, name, page, errors)
            if actual != expected:
                errors.append(f"{relative}: {name} is {actual!r}, expected {expected!r}")
            if "favicon" in actual.lower():
                errors.append(f"{relative}: favicon must not be used as {name}")

        schema_urls: set[str] = set()
        scripts = JSON_LD_RE.findall(raw)
        if not scripts:
            errors.append(f"{relative}: no JSON-LD schema found")
        for number, payload in enumerate(scripts, start=1):
            try:
                document = json.loads(html.unescape(payload).strip())
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON-LD block {number}: {exc}")
                continue
            schema_urls.update(schema_image_urls(document))
        if expected_image not in schema_urls:
            errors.append(f"{relative}: JSON-LD does not reference representative image {expected_image}")

    if len(checked_cards) != len(SOCIAL_CARDS):
        missing = sorted(str(card.path.relative_to(ROOT)) for card in SOCIAL_CARDS.values() if card.path not in checked_cards)
        errors.append(f"social card mapping is not exercised by sitemap: {missing}")


def local_image(source: str, page: Path) -> Path | None:
    parsed = urllib.parse.urlparse(html.unescape(source))
    if parsed.scheme and parsed.netloc not in {"alirostami.com", "www.alirostami.com"}:
        return None
    if parsed.netloc and parsed.netloc not in {"alirostami.com", "www.alirostami.com"}:
        return None
    decoded = urllib.parse.unquote(parsed.path)
    if not decoded:
        return None
    if decoded.startswith("/"):
        return ROOT / decoded.lstrip("/")
    return (page.parent / decoded).resolve()


def positive_int(value: str) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def check_content_images(errors: list[str]) -> int:
    image_count = 0
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts or "layouts" in page.parts:
            continue
        _raw, parsed = parse_page(page)
        relative = page.relative_to(ROOT)
        for index, image in enumerate(parsed.images):
            image_count += 1
            source = image.get("src") or image.get("data-src") or ""
            label = f"{relative}: img {index + 1} ({source or 'missing src'})"
            if not image.get("alt", "").strip():
                errors.append(f"{label}: missing non-empty alt")
            width = positive_int(image.get("width", ""))
            height = positive_int(image.get("height", ""))
            if width is None or height is None:
                errors.append(f"{label}: missing positive width and height")
            if image.get("decoding", "").lower() != "async":
                errors.append(f"{label}: decoding must be async")
            priority = index == 0 and (
                (relative == Path("index.html") and source.endswith("/images/Ali-256.jpg"))
                or (
                    relative.as_posix() in PRIORITY_IMAGE_PAGES
                    and source.startswith("/images/projects/")
                )
            )
            expected_loading = "eager" if priority else "lazy"
            if image.get("loading", "").lower() != expected_loading:
                errors.append(f"{label}: loading must be {expected_loading}")
            if priority and image.get("fetchpriority", "").lower() != "high":
                errors.append(f"{label}: above-fold image must use fetchpriority=high")
            if not priority and image.get("fetchpriority", "").lower() == "high":
                errors.append(f"{label}: non-priority image must not use fetchpriority=high")
            if source.endswith("/images/Ali.jpg") or source.endswith("../figures/aima-4e-persian.jpeg"):
                errors.append(f"{label}: unoptimized full-size source is used")

            target = local_image(source, page)
            if target is None:
                errors.append(f"{label}: external or unsupported image URL")
                continue
            if not target.is_file():
                errors.append(f"{label}: target does not exist")
                continue
            try:
                intrinsic_width, intrinsic_height = image_size(target)
            except (OSError, ValueError) as exc:
                errors.append(f"{label}: cannot read dimensions: {exc}")
                continue
            if width and height:
                display_ratio = width / height
                intrinsic_ratio = intrinsic_width / intrinsic_height
                if abs(display_ratio - intrinsic_ratio) / intrinsic_ratio > 0.015:
                    errors.append(
                        f"{label}: width/height ratio {width}×{height} does not match "
                        f"intrinsic {intrinsic_width}×{intrinsic_height}"
                    )
    return image_count


def check_generated_assets(errors: list[str]) -> None:
    for card in SOCIAL_CARDS.values():
        if not card.path.is_file():
            errors.append(f"missing generated social card: {card.path.relative_to(ROOT)}")
            continue
        try:
            dimensions = image_size(card.path)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot inspect {card.path.relative_to(ROOT)}: {exc}")
            continue
        if dimensions != (SOCIAL_WIDTH, SOCIAL_HEIGHT):
            errors.append(f"{card.path.relative_to(ROOT)} is {dimensions}, expected 1200×630")
        if card.path.stat().st_size > 250_000:
            errors.append(f"{card.path.relative_to(ROOT)} exceeds 250 KB")

    responsive = {
        ROOT / "images" / "Ali-256.jpg": ((256, 256), 60_000),
        ROOT / "images" / "Ali-512.jpg": ((512, 512), 130_000),
        ROOT / "figures" / "aima-4e-persian-960.jpg": ((960, 1286), 250_000),
    }
    for path, (expected_dimensions, maximum_size) in responsive.items():
        if not path.is_file():
            errors.append(f"missing optimized image: {path.relative_to(ROOT)}")
            continue
        try:
            dimensions = image_size(path)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot inspect {path.relative_to(ROOT)}: {exc}")
            continue
        if dimensions != expected_dimensions:
            errors.append(f"{path.relative_to(ROOT)} is {dimensions}, expected {expected_dimensions}")
        if path.stat().st_size > maximum_size:
            errors.append(f"{path.relative_to(ROOT)} exceeds {maximum_size:,} bytes")


def main() -> int:
    errors: list[str] = []
    sitemap = sitemap_pages(errors)
    pages = indexable_pages(sitemap)
    check_generated_assets(errors)
    check_indexable_metadata(pages, errors)
    image_count = check_content_images(errors)

    if errors:
        print(f"image SEO audit failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    total_card_bytes = sum(card.path.stat().st_size for card in SOCIAL_CARDS.values())
    print(
        f"image SEO audit passed: {len(pages)} indexable pages ({len(sitemap)} in sitemap), "
        f"{image_count} img elements, {len(SOCIAL_CARDS)} social cards "
        f"({total_card_bytes / 1024:.1f} KiB)"
    )
    print("all social/schema images are 1200×630; all content images have alt, dimensions, loading, and decoding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
