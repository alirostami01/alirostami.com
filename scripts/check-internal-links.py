#!/usr/bin/env python3
"""Audit Phase-6 internal linking and crawl architecture without dependencies."""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import urllib.parse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://www.alirostami.com"
CANONICAL_HOST = "www.alirostami.com"
HOME_URL = f"{BASE_URL}/"

STYLE_MARKER = "internal-linking-styles"
BREADCRUMB_MARKER = "internal-breadcrumb"
RELATED_MARKER = "internal-related"
CHAPTER_MARKER = "internal-chapter-navigation"
AIMA_HUB_MARKER = "internal-aima-book-hub"

RELATED_PAGES = {
    "index.html",
    "aima-4e-persian/index.html",
    "categories/index.html",
    "en/support/index.html",
    "fundamentals-of-software-architecture-persian/index.html",
    "persian-streams/index.html",
    "persian-subtitles/index.html",
    "posts/a-recap-of-last-year/index.html",
    "posts/aima-4e-persian/index.html",
    "posts/benefits-of-using-obsidian/index.html",
    "posts/fundamentals-of-software-architecture-persian/index.html",
    "posts/index.html",
    "support/index.html",
    "tags/index.html",
}

GENERATOR_SCRIPTS = (
    "scripts/build-aima-index.py",
    "scripts/build-project-page.py",
    "scripts/build-social-images.py",
    "scripts/build-software-architecture-index.py",
    "scripts/build-support-page.py",
    "scripts/update-sitemaps.py",
)

GENERIC_ANCHORS = {
    "click here",
    "continue",
    "here",
    "learn more",
    "more",
    "read more",
    "#",
    "ادامه",
    "ادامه مطلب",
    "اینجا",
    "اینجا کلیک کنید",
    "بیشتر",
    "کلیک کنید",
    "کمک شما",
    "خواندن آنلاین",
    "راهنمای نصب و مستندات",
    "مطالعه آنلاین",
    "مطالعه آنلاین (سایدبار)",
    "مستندات فارسی",
    "مشاهده",
    "مشاهده بیشتر",
}


@dataclass
class Anchor:
    href: str
    attrs: dict[str, str]
    text_parts: list[str] = field(default_factory=list)
    image_alts: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        visible = " ".join("".join(self.text_parts).split())
        image_alt = " ".join(" ".join(self.image_alts).split())
        return visible or image_alt or self.attrs.get("aria-label", "").strip() or self.attrs.get("title", "").strip()


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.canonicals: list[str] = []
        self.noindex = False
        self.ids: set[str] = set()
        self.anchors: list[Anchor] = []
        self.json_scripts: list[tuple[str, str]] = []
        self._anchor: Anchor | None = None
        self._in_json = False
        self._json_id = ""
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        lowered = tag.lower()
        if data.get("id"):
            self.ids.add(data["id"])
        if lowered == "html":
            self.html_lang = data.get("lang", "")
        elif lowered == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonicals.append(data.get("href", ""))
        elif lowered == "meta" and data.get("name", "").lower() == "robots":
            self.noindex = "noindex" in data.get("content", "").lower()
        elif lowered == "a":
            self._anchor = Anchor(data.get("href", ""), data)
        elif lowered == "img" and self._anchor is not None:
            self._anchor.image_alts.append(data.get("alt", ""))
        elif lowered == "script" and data.get("type", "").lower() == "application/ld+json":
            self._in_json = True
            self._json_id = data.get("id", "")
            self._json_parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "a" and self._anchor is not None:
            self.anchors.append(self._anchor)
            self._anchor = None
        elif lowered == "script" and self._in_json:
            self.json_scripts.append((self._json_id, "".join(self._json_parts).strip()))
            self._in_json = False
            self._json_id = ""
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_json:
            self._json_parts.append(data)
        elif self._anchor is not None:
            self._anchor.text_parts.append(data)


@dataclass
class BreadcrumbItem:
    text_parts: list[str] = field(default_factory=list)
    href: str | None = None
    current: bool = False

    @property
    def text(self) -> str:
        return " ".join("".join(self.text_parts).split())


class BreadcrumbParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.nav_count = 0
        self.nav_label = ""
        self.ol_count = 0
        self.items: list[BreadcrumbItem] = []
        self._inside_nav = False
        self._item: BreadcrumbItem | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
        lowered = tag.lower()
        if lowered == "nav" and "site-breadcrumb" in classes:
            self._inside_nav = True
            self.nav_count += 1
            self.nav_label = data.get("aria-label", "").strip()
        elif self._inside_nav and lowered == "ol":
            self.ol_count += 1
        elif self._inside_nav and lowered == "li":
            self._item = BreadcrumbItem(current=data.get("aria-current", "").lower() == "page")
        elif self._inside_nav and lowered == "a" and self._item is not None:
            self._item.href = data.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "li" and self._item is not None:
            self.items.append(self._item)
            self._item = None
        elif lowered == "nav" and self._inside_nav:
            self._inside_nav = False

    def handle_data(self, data: str) -> None:
        if self._item is not None:
            self._item.text_parts.append(data)


ERRORS: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="strict"))
    return parser


def all_html_pages() -> dict[Path, PageParser]:
    result: dict[Path, PageParser] = {}
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or "layouts" in path.parts:
            continue
        result[path.resolve()] = parse_page(path)
    return result


def file_for_url(url: str) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    relative = urllib.parse.unquote(parsed.path).lstrip("/")
    if not relative:
        candidates = (ROOT / "index.html",)
    elif parsed.path.endswith("/"):
        candidates = (ROOT / relative / "index.html",)
    else:
        direct = ROOT / relative
        candidates = (direct, ROOT / f"{relative}.html", direct / "index.html")
    return next((path.resolve() for path in candidates if path.is_file()), None)


def relative_name(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def discover_indexable(parsed_pages: dict[Path, PageParser]) -> dict[Path, str]:
    result: dict[Path, str] = {}
    for path, parser in parsed_pages.items():
        if parser.noindex or len(parser.canonicals) != 1:
            continue
        canonical = parser.canonicals[0]
        url = urllib.parse.urlparse(canonical)
        target = file_for_url(canonical)
        if url.scheme == "https" and url.netloc == CANONICAL_HOST and target == path:
            result[path] = canonical
    return result


def managed_schema(parser: PageParser, relative: str) -> dict[str, Any]:
    scripts = [payload for script_id, payload in parser.json_scripts if script_id == "site-metadata-schema"]
    require(len(scripts) == 1, f"{relative}: expected one managed JSON-LD graph")
    if len(scripts) != 1:
        return {"@graph": []}
    try:
        document = json.loads(scripts[0])
    except json.JSONDecodeError as error:
        require(False, f"{relative}: invalid managed JSON-LD: {error}")
        return {"@graph": []}
    require(isinstance(document, dict) and isinstance(document.get("@graph"), list), f"{relative}: JSON-LD graph is malformed")
    return document if isinstance(document, dict) else {"@graph": []}


def schema_node(document: dict[str, Any], node_type: str) -> dict[str, Any] | None:
    for node in document.get("@graph", []):
        types = node.get("@type", [])
        if isinstance(types, str):
            types = [types]
        if node_type in types:
            return node
    return None


def marker_body(raw: str, marker: str) -> str | None:
    pattern = re.compile(
        rf"<!-- {re.escape(marker)}:start -->(.*?)<!-- {re.escape(marker)}:end -->",
        re.DOTALL,
    )
    matches = pattern.findall(raw)
    return matches[0] if len(matches) == 1 else None


def url_key(url: str) -> tuple[str, str, str, str, str]:
    parsed = urllib.parse.urlparse(url)
    return (
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        urllib.parse.unquote(parsed.path),
        parsed.query,
        urllib.parse.unquote(parsed.fragment),
    )


def internal_url(source: str, href: str) -> urllib.parse.ParseResult | None:
    value = html.unescape(href).strip()
    if not value or value.lower().startswith(("data:", "javascript:", "mailto:", "tel:")):
        return None
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(source, value))
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc.lower() not in {CANONICAL_HOST, "alirostami.com"}:
        return None
    return parsed


def fragment_anchors(fragment: str) -> list[Anchor]:
    parser = PageParser()
    parser.feed(fragment)
    return parser.anchors


def normalize_label(value: str) -> str:
    return " ".join(html.unescape(value).casefold().split())


def audit_breadcrumb(
    raw: str,
    relative: str,
    canonical: str,
    document: dict[str, Any],
) -> None:
    body = marker_body(raw, BREADCRUMB_MARKER)
    breadcrumb = schema_node(document, "BreadcrumbList")
    if relative == "index.html":
        require(raw.count(f"{BREADCRUMB_MARKER}:start") == 0, "index.html: home must not render a breadcrumb")
        require(breadcrumb is None, "index.html: home must not publish BreadcrumbList")
        return

    require(raw.count(f"{BREADCRUMB_MARKER}:start") == 1, f"{relative}: visible breadcrumb marker mismatch")
    require(raw.count(f"{BREADCRUMB_MARKER}:end") == 1, f"{relative}: visible breadcrumb marker mismatch")
    require(body is not None, f"{relative}: visible breadcrumb is missing")
    require(breadcrumb is not None, f"{relative}: JSON-LD breadcrumb is missing")
    if body is None or breadcrumb is None:
        return

    parser = BreadcrumbParser()
    parser.feed(body)
    expected = breadcrumb.get("itemListElement", [])
    require(parser.nav_count == 1, f"{relative}: breadcrumb must contain one nav")
    require(bool(parser.nav_label), f"{relative}: breadcrumb nav has no accessible label")
    require(parser.ol_count == 1, f"{relative}: breadcrumb must use one ordered list")
    require(len(parser.items) == len(expected), f"{relative}: visible/JSON-LD breadcrumb length differs")
    if len(parser.items) != len(expected):
        return

    for index, (visible, structured) in enumerate(zip(parser.items, expected, strict=True)):
        expected_name = " ".join(str(structured.get("name", "")).split())
        expected_url = str(structured.get("item", ""))
        require(visible.text == expected_name, f"{relative}: breadcrumb name {index + 1} differs from JSON-LD")
        if index + 1 == len(expected):
            require(visible.current, f"{relative}: final breadcrumb item lacks aria-current=page")
            require(visible.href is None, f"{relative}: final breadcrumb item must be text, not a self-link")
            require(url_key(expected_url) == url_key(canonical), f"{relative}: final breadcrumb URL is not canonical")
        else:
            require(not visible.current, f"{relative}: only final breadcrumb item may be current")
            require(bool(visible.href), f"{relative}: ancestor breadcrumb item {index + 1} is not linked")
            if visible.href:
                actual_url = urllib.parse.urljoin(canonical, visible.href)
                require(url_key(actual_url) == url_key(expected_url), f"{relative}: breadcrumb URL {index + 1} differs from JSON-LD")


def chapter_records(
    pages: dict[Path, str], documents: dict[str, dict[str, Any]]
) -> dict[str, list[tuple[float, str, str, str]]]:
    result: dict[str, list[tuple[float, str, str, str]]] = {"aima-4e": [], "software-architecture": []}
    for path, canonical in pages.items():
        relative = relative_name(path)
        root = next((key for key in result if relative.startswith(f"{key}/") and relative != f"{key}/index.html"), None)
        if root is None:
            continue
        chapter = schema_node(documents[relative], "Chapter")
        if chapter is None:
            continue
        try:
            position = float(chapter.get("position"))
        except (TypeError, ValueError):
            require(False, f"{relative}: invalid Chapter.position")
            continue
        result[root].append((position, relative, canonical, str(chapter.get("name", "")).strip()))
    for root in result:
        result[root].sort(key=lambda item: (item[0], item[1]))
    return result


def audit_chapter_navigation(
    raw_by_relative: dict[str, str],
    groups: dict[str, list[tuple[float, str, str, str]]],
) -> int:
    chapter_relatives = {record[1] for records in groups.values() for record in records}
    managed_relatives = {record[1] for record in groups["software-architecture"]}
    aima_relatives = {record[1] for record in groups["aima-4e"]}
    for relative, raw in raw_by_relative.items():
        managed_count = int(relative in managed_relatives)
        aima_count = int(relative in aima_relatives)
        require(raw.count(f"{CHAPTER_MARKER}:start") == managed_count, f"{relative}: chapter navigation start marker mismatch")
        require(raw.count(f"{CHAPTER_MARKER}:end") == managed_count, f"{relative}: chapter navigation end marker mismatch")
        require(raw.count(f"{AIMA_HUB_MARKER}:start") == aima_count, f"{relative}: AIMA hub start marker mismatch")
        require(raw.count(f"{AIMA_HUB_MARKER}:end") == aima_count, f"{relative}: AIMA hub end marker mismatch")

    for root, records in groups.items():
        for index, (_position, relative, canonical, _name) in enumerate(records):
            expected: dict[str, str] = {f"{BASE_URL}/{root}/": "hub"}
            if index > 0:
                expected[records[index - 1][2]] = "prev"
            if index + 1 < len(records):
                expected[records[index + 1][2]] = "next"

            if root == "software-architecture":
                body = marker_body(raw_by_relative[relative], CHAPTER_MARKER)
                if body is None:
                    continue
                anchors = fragment_anchors(body)
                require(len(anchors) == len(expected), f"{relative}: chapter navigation link count is incorrect")
            else:
                native_pattern = re.compile(
                    r'<nav\b(?=[^>]*\bclass=["\'][^"\']*\bfooter-nav\b)(?=[^>]*\baria-label=["\'][^"\']+["\'])[^>]*>'
                    r'(.*?)</nav\s*>',
                    re.IGNORECASE | re.DOTALL,
                )
                native = native_pattern.findall(raw_by_relative[relative])
                require(len(native) == 1, f"{relative}: expected one labeled native AIMA footer navigation")
                if len(native) != 1:
                    continue
                anchors = fragment_anchors(native[0])

            actual: dict[str, Anchor] = {}
            for anchor in anchors:
                target = urllib.parse.urljoin(canonical, anchor.href)
                key = next((url for url in expected if url_key(url)[:4] == url_key(target)[:4]), None)
                if key is not None:
                    require(key not in actual, f"{relative}: chapter navigation repeats {key}")
                    actual[key] = anchor
            require(set(actual) == set(expected), f"{relative}: chapter navigation does not link the hub and adjacent chapters")
            for target, relation in expected.items():
                anchor = actual.get(target)
                if anchor is None:
                    continue
                rel_tokens = set(anchor.attrs.get("rel", "").lower().split())
                if relation in {"prev", "next"}:
                    require(relation in rel_tokens, f"{relative}: {relation} chapter link lacks rel={relation}")
                else:
                    require(not ({"prev", "next"} & rel_tokens), f"{relative}: book hub has an adjacent-page rel")
    return len(chapter_relatives)


def main() -> None:
    parsed_pages = all_html_pages()
    pages = discover_indexable(parsed_pages)
    require(len(pages) == 73, f"expected 73 canonical indexable pages, found {len(pages)}")
    require(file_for_url(HOME_URL) in pages, "canonical home page is not indexable")

    file_to_canonical = {path: canonical for path, canonical in pages.items()}
    canonical_to_file = {canonical: path for path, canonical in pages.items()}
    raw_by_relative: dict[str, str] = {}
    documents: dict[str, dict[str, Any]] = {}
    for path in pages:
        relative = relative_name(path)
        raw = path.read_text(encoding="utf-8", errors="strict")
        raw_by_relative[relative] = raw
        documents[relative] = managed_schema(parsed_pages[path], relative)
        require(raw.count(f"{STYLE_MARKER}:start") == 1, f"{relative}: internal-linking style start marker mismatch")
        require(raw.count(f"{STYLE_MARKER}:end") == 1, f"{relative}: internal-linking style end marker mismatch")
        audit_breadcrumb(raw, relative, file_to_canonical[path], documents[relative])

    graph: defaultdict[str, set[str]] = defaultdict(set)
    incoming: defaultdict[str, set[str]] = defaultdict(set)
    internal_link_count = 0
    graph_link_count = 0
    noncanonical_count = 0
    broken_count = 0
    noindex_count = 0
    generic_count = 0
    empty_count = 0

    for source_path, source_canonical in sorted(pages.items(), key=lambda item: item[1]):
        relative = relative_name(source_path)
        parser = parsed_pages[source_path]
        for anchor in parser.anchors:
            target_url = internal_url(source_canonical, anchor.href)
            if target_url is None:
                continue
            internal_link_count += 1
            target_path = file_for_url(target_url.geturl())
            if target_path is None:
                broken_count += 1
                require(False, f"{relative}: broken internal link {anchor.href!r}")
                continue

            target_parser = parsed_pages.get(target_path)
            target_canonical = file_to_canonical.get(target_path)
            if target_path.suffix.lower() == ".html":
                if target_canonical is None:
                    if target_parser is not None and target_parser.noindex:
                        noindex_count += 1
                        require(False, f"{relative}: internal link points to noindex/redirect page {anchor.href!r}")
                    else:
                        broken_count += 1
                        require(False, f"{relative}: internal link points to noncanonical HTML {anchor.href!r}")
                    continue

                expected = urllib.parse.urlparse(target_canonical)
                direct = (
                    target_url.scheme == "https"
                    and target_url.netloc == CANONICAL_HOST
                    and urllib.parse.unquote(target_url.path) == urllib.parse.unquote(expected.path)
                )
                if not direct:
                    noncanonical_count += 1
                    require(False, f"{relative}: internal link is not the direct canonical URL {anchor.href!r}")
                if target_canonical != source_canonical:
                    graph[source_canonical].add(target_canonical)
                    incoming[target_canonical].add(source_canonical)
                    graph_link_count += 1

            fragment = urllib.parse.unquote(target_url.fragment)
            if fragment and not fragment.startswith(":~:"):
                ids = target_parser.ids if target_parser is not None else set()
                require(fragment in ids, f"{relative}: missing fragment #{fragment} in {relative_name(target_path)}")

            label = normalize_label(anchor.label)
            if not label:
                empty_count += 1
                require(False, f"{relative}: internal anchor {anchor.href!r} has no meaningful text or accessible label")
            elif label in GENERIC_ANCHORS:
                generic_count += 1
                require(False, f"{relative}: generic internal anchor text {anchor.label!r} for {anchor.href!r}")

    depth: dict[str, int] = {HOME_URL: 0}
    queue: deque[str] = deque((HOME_URL,))
    while queue:
        source = queue.popleft()
        for target in graph[source]:
            if target not in depth:
                depth[target] = depth[source] + 1
                queue.append(target)

    unreachable = sorted(set(canonical_to_file) - set(depth))
    zero_incoming = sorted(url for url in canonical_to_file if url != HOME_URL and not incoming[url])
    require(not unreachable, f"orphan/unreachable canonical pages: {', '.join(unreachable)}")
    require(not zero_incoming, f"canonical pages with no incoming internal link: {', '.join(zero_incoming)}")
    max_depth = max(depth.values(), default=0)
    require(max_depth <= 2, f"maximum click depth is {max_depth}; expected at most 2")

    # Discovery blocks must exist only on the curated hub/article/project pages.
    for relative, raw in raw_by_relative.items():
        expected = int(relative in RELATED_PAGES)
        require(raw.count(f"{RELATED_MARKER}:start") == expected, f"{relative}: related-content start marker mismatch")
        require(raw.count(f"{RELATED_MARKER}:end") == expected, f"{relative}: related-content end marker mismatch")
        if expected:
            body = marker_body(raw, RELATED_MARKER)
            anchors = fragment_anchors(body or "")
            source_canonical = file_to_canonical[(ROOT / relative).resolve()]
            targets = {
                url_key(urllib.parse.urljoin(source_canonical, anchor.href))
                for anchor in anchors
            }
            # Generated discovery links stay root-relative so their destination is
            # stable even if a page moves deeper in the URL hierarchy.
            require(len(anchors) >= 3, f"{relative}: related-content block has fewer than three links")
            require(len(targets) == len(anchors), f"{relative}: related-content block repeats a destination")
            require(all(anchor.href.startswith("/") for anchor in anchors), f"{relative}: related links must be root-relative canonical paths")

    groups = chapter_records(pages, documents)
    chapter_count = audit_chapter_navigation(raw_by_relative, groups)
    require(chapter_count == 57, f"expected 57 chapter navigation blocks, found {chapter_count}")
    require(len(groups["aima-4e"]) == 29, f"expected 29 AIMA chapter documents, found {len(groups['aima-4e'])}")
    require(len(groups["software-architecture"]) == 28, f"expected 28 architecture chapter documents, found {len(groups['software-architecture'])}")

    # Pipeline contract and generator integration.
    helper_path = ROOT / "scripts" / "image_utils.py"
    helper = helper_path.read_text(encoding="utf-8")
    pipeline_tokens = (
        "apply_image_seo()",
        'run_postprocessor("update-metadata.py")',
        'run_postprocessor("update-internal-links.py")',
        'run_postprocessor("update-performance.py")',
        'run_postprocessor("update-accessibility.py")',
    )
    positions = [helper.find(token, helper.find("def apply_site_postprocessors")) for token in pipeline_tokens]
    require(all(position >= 0 for position in positions), "image_utils.py is missing a Phase-6 post-processor")
    require(positions == sorted(positions), "image_utils.py post-processors are in the wrong order")
    for relative in GENERATOR_SCRIPTS:
        source = (ROOT / relative).read_text(encoding="utf-8")
        require(
            "apply_site_postprocessors" in source and "apply_site_postprocessors()" in source,
            f"{relative}: generator is not connected to the shared post-processing pipeline",
        )

    idempotence = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "update-internal-links.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(idempotence.returncode == 0, f"internal-link updater is not idempotent: {idempotence.stderr.strip()}")

    if ERRORS:
        print(f"internal-link audit failed with {len(ERRORS)} error(s):", file=sys.stderr)
        for error in ERRORS:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    depth_counts = Counter(depth.values())
    unique_edges = sum(len(targets) for targets in graph.values())
    print(
        f"internal-link audit passed: {len(pages)} indexable pages; "
        f"{internal_link_count} internal anchors; {graph_link_count} page-link occurrences; "
        f"{unique_edges} unique graph edges"
    )
    print(
        f"crawl graph: {broken_count} broken, {noindex_count} redirect/noindex, "
        f"{noncanonical_count} noncanonical, {empty_count + generic_count} empty/generic anchors; "
        f"{len(unreachable)} orphans; max depth {max_depth} "
        f"({dict(sorted(depth_counts.items()))})"
    )
    print(
        f"navigation: {len(pages) - 1} visible/JSON-LD breadcrumbs; "
        f"{chapter_count} chapter sequences (29 native AIMA, 28 managed architecture); "
        f"{len(RELATED_PAGES)} discovery sections"
    )


if __name__ == "__main__":
    main()
