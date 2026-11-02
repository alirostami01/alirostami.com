#!/usr/bin/env python3
"""Apply Phase-2 image SEO metadata and intrinsic image attributes.

The script is deliberately stdlib-only. Run the Pillow-based asset builder first,
then run this post-processor after any page generator:

    python3 scripts/build-social-images.py
    python3 scripts/update-image-seo.py

It is safe to run repeatedly; a second run produces no file changes.
"""

from __future__ import annotations

import html
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from image_utils import (
    BASE_URL,
    ROOT,
    SOCIAL_HEIGHT,
    SOCIAL_WIDTH,
    image_size,
    social_alt_for_page,
    social_card_for_page,
)

IMG_RE = re.compile(r"<img\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
META_RE = re.compile(r"<meta\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
LINK_RE = re.compile(r"<link\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
SCRIPT_RE = re.compile(
    r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script\s*>)',
    flags=re.IGNORECASE | re.DOTALL,
)
IMAGE_META_NAMES = {
    "og:image",
    "og:image:url",
    "og:image:secure_url",
    "og:image:type",
    "og:image:width",
    "og:image:height",
    "og:image:alt",
    "twitter:card",
    "twitter:image",
    "twitter:image:alt",
}
PRIORITY_IMAGE_PAGES = {
    "aima-4e-persian/index.html",
    "fundamentals-of-software-architecture-persian/index.html",
    "persian-streams/index.html",
    "persian-subtitles/index.html",
}
SCHEMA_IMAGE_TYPES = (
    "ProfilePage",
    "Article",
    "BlogPosting",
    "Book",
    "SoftwareApplication",
    "WebPage",
    "CollectionPage",
    "ItemList",
)


def attribute_tokens(tag: str) -> list[tuple[str, str, int, int]]:
    """Return real start-tag attributes without matching text inside quotes."""
    tokens: list[tuple[str, str, int, int]] = []
    length = len(tag)
    index = 1
    while index < length and tag[index].isspace():
        index += 1
    while index < length and not tag[index].isspace() and tag[index] not in "/>":
        index += 1

    while index < length:
        while index < length and tag[index].isspace():
            index += 1
        if index >= length or tag[index] in "/>":
            break
        start = index
        while index < length and not tag[index].isspace() and tag[index] not in "=/>":
            index += 1
        name = tag[start:index]
        while index < length and tag[index].isspace():
            index += 1
        value = ""
        if index < length and tag[index] == "=":
            index += 1
            while index < length and tag[index].isspace():
                index += 1
            if index < length and tag[index] in "\"'":
                quote = tag[index]
                index += 1
                value_start = index
                while index < length and tag[index] != quote:
                    index += 1
                value = tag[value_start:index]
                if index < length:
                    index += 1
            else:
                value_start = index
                while index < length and not tag[index].isspace() and tag[index] != ">":
                    index += 1
                value = tag[value_start:index]
        tokens.append((name.lower(), html.unescape(value), start, index))
    return tokens


def attributes(tag: str) -> dict[str, str]:
    return {name: value for name, value, _start, _end in attribute_tokens(tag)}


def set_attribute(tag: str, name: str, value: str) -> str:
    replacement = f'{name}="{html.escape(value, quote=True)}"'
    for token_name, _value, start, end in attribute_tokens(tag):
        if token_name == name.lower():
            return f"{tag[:start]}{replacement}{tag[end:]}"
    closing = re.search(r"\s*/?>$", tag)
    if closing is None:
        return tag
    return f"{tag[:closing.start()]} {replacement}{tag[closing.start():]}"


def remove_attribute(tag: str, name: str) -> str:
    for token_name, _value, start, end in attribute_tokens(tag):
        if token_name != name.lower():
            continue
        while start > 0 and tag[start - 1] in " \t":
            start -= 1
        return f"{tag[:start]}{tag[end:]}"
    return tag


def meta_name(tag: str) -> str:
    data = attributes(tag)
    return (data.get("property") or data.get("name") or "").lower()


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


def sitemap_pages() -> dict[Path, str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    result: dict[Path, str] = {}
    for node in root.iter():
        if not node.tag.endswith("loc") or not node.text:
            continue
        target = file_for_url(node.text.strip())
        if target is None:
            raise FileNotFoundError(f"Missing sitemap target: {node.text.strip()}")
        result[target.resolve()] = node.text.strip()
    return result


def indexable_pages() -> dict[Path, str]:
    """Return sitemap targets plus any other self-canonical, indexable HTML."""
    result = sitemap_pages()
    for page in html_pages():
        resolved = page.resolve()
        if resolved in result:
            continue
        raw = page.read_text(encoding="utf-8", errors="strict")
        robots = [
            attributes(tag).get("content", "").lower()
            for tag in META_RE.findall(raw)
            if attributes(tag).get("name", "").lower() == "robots"
        ]
        if any("noindex" in directive for directive in robots):
            continue
        canonicals = []
        for tag in LINK_RE.findall(raw):
            data = attributes(tag)
            if "canonical" in data.get("rel", "").lower().split() and data.get("href"):
                canonicals.append(data["href"])
        if len(canonicals) != 1 or not canonicals[0].startswith(f"{BASE_URL}/"):
            continue
        target = file_for_url(canonicals[0])
        if target is not None and target.resolve() == resolved:
            result[resolved] = canonicals[0]
    return result


def image_object(url: str, alt: str) -> dict[str, Any]:
    return {
        "@type": "ImageObject",
        "url": url,
        "contentUrl": url,
        "width": SOCIAL_WIDTH,
        "height": SOCIAL_HEIGHT,
        "caption": alt,
    }


def schema_types(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def schema_entity(document: Any) -> dict[str, Any] | None:
    if not isinstance(document, dict):
        return None
    candidates = document.get("@graph")
    if not isinstance(candidates, list):
        candidates = [document]
    for expected_type in SCHEMA_IMAGE_TYPES:
        for candidate in candidates:
            if isinstance(candidate, dict) and expected_type in schema_types(candidate.get("@type")):
                return candidate
    return None


def update_schema(raw: str, image_url: str, alt: str) -> tuple[str, bool]:
    updated_one = False

    def replace(match: re.Match[str]) -> str:
        nonlocal updated_one
        try:
            document = json.loads(html.unescape(match.group(2)).strip())
        except json.JSONDecodeError:
            return match.group(0)
        entity = schema_entity(document)
        if entity is None or updated_one:
            return match.group(0)
        entity["image"] = image_object(image_url, alt)
        updated_one = True
        payload = json.dumps(document, ensure_ascii=False, indent=2)
        return f"{match.group(1)}\n{payload}\n{match.group(3)}"

    return SCRIPT_RE.sub(replace, raw), updated_one


def normalize_robots(raw: str) -> str:
    found = False

    def replace(tag_match: re.Match[str]) -> str:
        nonlocal found
        tag = tag_match.group(0)
        if attributes(tag).get("name", "").lower() != "robots":
            return tag
        if found:
            return ""
        found = True
        return set_attribute(tag, "content", "index, follow, max-image-preview:large")

    raw = META_RE.sub(replace, raw)
    if not found:
        raw = re.sub(
            r"(<meta\b[^>]*charset[^>]*>)",
            r'\1\n    <meta name="robots" content="index, follow, max-image-preview:large">',
            raw,
            count=1,
            flags=re.IGNORECASE,
        )
    return raw


def insert_before_head(raw: str, snippet: str) -> str:
    match = re.search(r"</head\s*>", raw, flags=re.IGNORECASE)
    if match is None:
        return raw
    line_start = raw.rfind("\n", 0, match.start()) + 1
    if not raw[line_start : match.start()].strip():
        insertion_start = line_start
        separator = ""
    else:
        insertion_start = match.start()
        separator = "\n"
    return (
        f"{raw[:insertion_start]}{separator}{snippet}\n</head>"
        f"{raw[match.end():]}"
    )


def image_meta_block(image_url: str, alt: str) -> str:
    escaped_alt = html.escape(alt, quote=True)
    return f"""    <!-- image-seo:start -->
    <meta property="og:image" content="{image_url}">
    <meta property="og:image:secure_url" content="{image_url}">
    <meta property="og:image:type" content="image/jpeg">
    <meta property="og:image:width" content="{SOCIAL_WIDTH}">
    <meta property="og:image:height" content="{SOCIAL_HEIGHT}">
    <meta property="og:image:alt" content="{escaped_alt}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{image_url}">
    <meta name="twitter:image:alt" content="{escaped_alt}">
    <!-- image-seo:end -->"""


def update_page_metadata(raw: str, relative: Path, canonical: str) -> str:
    card = social_card_for_page(relative)
    image_url = card.url
    image_alt = social_alt_for_page(relative)
    block = image_meta_block(image_url, image_alt)
    marker = re.compile(
        r"[ \t]*<!-- image-seo:start -->.*?<!-- image-seo:end -->",
        flags=re.DOTALL,
    )
    has_marker = marker.search(raw) is not None
    if has_marker:
        raw = marker.sub(block, raw, count=1)
    else:
        raw = META_RE.sub(
            lambda match: "" if meta_name(match.group(0)) in IMAGE_META_NAMES else match.group(0),
            raw,
        )

    raw = normalize_robots(raw)
    raw, has_schema_image = update_schema(raw, image_url, image_alt)
    if not has_schema_image:
        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{canonical}#webpage",
            "url": canonical,
            "image": image_object(image_url, image_alt),
        }
        payload = json.dumps(schema, ensure_ascii=False, indent=2)
        raw = insert_before_head(
            raw,
            f'    <script type="application/ld+json" id="image-seo-schema">\n{payload}\n</script>',
        )
    if not has_marker:
        raw = insert_before_head(raw, block)
    return re.sub(r"[ \t]+$", "", raw, flags=re.MULTILINE)


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


def optimize_content_source(tag: str, relative: Path) -> str:
    data = attributes(tag)
    if relative == Path("index.html") and data.get("data-src", "").endswith("/images/Ali.jpg"):
        tag = set_attribute(tag, "src", "/images/Ali-256.jpg")
        tag = set_attribute(tag, "srcset", "/images/Ali-256.jpg 1x, /images/Ali-512.jpg 2x")
        for name in ("data-src", "data-srcset", "data-sizes"):
            tag = remove_attribute(tag, name)
        if attributes(tag).get("class") == "lazyload":
            tag = remove_attribute(tag, "class")
        tag = set_attribute(tag, "width", "256")
        tag = set_attribute(tag, "height", "256")
    data = attributes(tag)
    source = data.get("src", "")
    if source.endswith("/figures/aima-4e-persian.jpeg") or source.endswith("../figures/aima-4e-persian.jpeg"):
        tag = set_attribute(tag, "src", source.rsplit("/", 1)[0] + "/aima-4e-persian-960.jpg")
    return tag


def update_image_tags(raw: str, page: Path) -> tuple[str, int]:
    relative = page.relative_to(ROOT)
    image_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal image_index
        tag = optimize_content_source(match.group(0), relative)
        data = attributes(tag)
        source = data.get("src") or data.get("data-src") or ""
        target = local_image(source, page)
        if target is not None and target.is_file():
            dimensions = image_size(target)
            if dimensions is not None:
                width, height = dimensions
                if not data.get("width"):
                    tag = set_attribute(tag, "width", str(width))
                if not data.get("height"):
                    tag = set_attribute(tag, "height", str(height))
        priority = image_index == 0 and (
            (relative == Path("index.html") and source.endswith("/images/Ali-256.jpg"))
            or (
                relative.as_posix() in PRIORITY_IMAGE_PAGES
                and source.startswith("/images/projects/")
            )
        )
        if priority:
            tag = set_attribute(tag, "loading", "eager")
            tag = set_attribute(tag, "fetchpriority", "high")
        else:
            tag = set_attribute(tag, "loading", "lazy")
            tag = remove_attribute(tag, "fetchpriority")
        tag = set_attribute(tag, "decoding", "async")
        image_index += 1
        return tag

    return IMG_RE.sub(replace, raw), image_index


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if ".git" not in path.parts and "layouts" not in path.parts
    ]


def main() -> None:
    indexable = indexable_pages()
    changed = 0
    image_count = 0
    for page in html_pages():
        raw = page.read_text(encoding="utf-8", errors="strict")
        updated, count = update_image_tags(raw, page)
        image_count += count
        canonical = indexable.get(page.resolve())
        if canonical:
            updated = update_page_metadata(updated, page.relative_to(ROOT), canonical)
        if updated != raw:
            page.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"image SEO updated: {changed} HTML files; {image_count} img elements checked")
    print(f"indexable pages covered: {len(indexable)}")


if __name__ == "__main__":
    main()
