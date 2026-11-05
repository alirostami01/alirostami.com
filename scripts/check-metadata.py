#!/usr/bin/env python3
"""Fail fast on Phase-5 metadata and structured-data regressions."""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from collections.abc import Iterable
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://www.alirostami.com"
PERSON_ID = f"{BASE_URL}/#person"
WEBSITE_ID = f"{BASE_URL}/#website"
TWITTER_HANDLE = "@alirostami01"

CHAPTER_ROOTS = {
    "aima-4e": {
        "book_id": f"{BASE_URL}/aima-4e/#book",
        "book_url": f"{BASE_URL}/aima-4e/",
        "author_count": 2,
    },
    "software-architecture": {
        "book_id": f"{BASE_URL}/software-architecture/#book",
        "book_url": f"{BASE_URL}/software-architecture/",
        "author_count": 2,
    },
}
BOOK_PAGES = {
    "aima-4e-persian/index.html",
    "aima-4e/index.html",
    "fundamentals-of-software-architecture-persian/index.html",
    "software-architecture/index.html",
}
SOFTWARE_PAGES = {"persian-streams/index.html", "persian-subtitles/index.html"}
ARTICLE_PAGES = {
    "posts/a-recap-of-last-year/index.html",
    "posts/aima-4e-persian/index.html",
    "posts/benefits-of-using-obsidian/index.html",
    "posts/fundamentals-of-software-architecture-persian/index.html",
}
ARCHIVE_PAGES = {"posts/index.html"}
GENERATOR_SCRIPTS = (
    "scripts/build-aima-index.py",
    "scripts/build-project-page.py",
    "scripts/build-social-images.py",
    "scripts/build-software-architecture-index.py",
    "scripts/build-support-page.py",
    "scripts/update-sitemaps.py",
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.canonicals: list[str] = []
        self.metas: defaultdict[str, list[str]] = defaultdict(list)
        self.alternates: list[tuple[str, str]] = []
        self.json_scripts: list[tuple[str, str]] = []
        self._in_json = False
        self._json_id = ""
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        lowered = tag.lower()
        if lowered == "html":
            self.html_lang = data.get("lang", "")
        elif lowered == "meta":
            key = (data.get("property") or data.get("name") or "").lower()
            if key:
                self.metas[key].append(data.get("content", ""))
        elif lowered == "link":
            rel = data.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonicals.append(data.get("href", ""))
            if "alternate" in rel and data.get("hreflang"):
                self.alternates.append((data["hreflang"].lower(), data.get("href", "")))
        elif lowered == "script" and data.get("type", "").lower() == "application/ld+json":
            self._in_json = True
            self._json_id = data.get("id", "")
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_json:
            self.json_scripts.append((self._json_id, "".join(self._json_parts).strip()))
            self._in_json = False
            self._json_id = ""
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_json:
            self._json_parts.append(data)


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="strict"))
    return parser


def all_html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if ".git" not in path.parts and "layouts" not in path.parts
    ]


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
    result: dict[Path, str] = {}
    try:
        root = ET.parse(ROOT / "sitemap.xml").getroot()
    except (FileNotFoundError, ET.ParseError) as error:
        errors.append(f"cannot parse sitemap.xml: {error}")
        return result
    for node in root.iter():
        if not node.tag.endswith("loc") or not node.text:
            continue
        url = node.text.strip()
        target = file_for_url(url)
        if target is None:
            errors.append(f"sitemap URL has no local target: {url}")
            continue
        result[target.resolve()] = url
    return result


def indexable_pages(errors: list[str]) -> dict[Path, str]:
    """Discover indexable pages independently from the updater."""
    result = sitemap_pages(errors)
    for path in all_html_pages():
        resolved = path.resolve()
        if resolved in result:
            continue
        parsed = parse_page(path)
        if any("noindex" in value.lower() for value in parsed.metas.get("robots", [])):
            continue
        if len(parsed.canonicals) != 1:
            continue
        canonical = parsed.canonicals[0]
        if not canonical.startswith(f"{BASE_URL}/"):
            continue
        target = file_for_url(canonical)
        if target is not None and target.resolve() == resolved:
            result[resolved] = canonical
    return result


def one_meta(
    parsed: PageParser,
    key: str,
    relative: str,
    errors: list[str],
) -> str:
    values = parsed.metas.get(key, [])
    if len(values) != 1:
        errors.append(f"{relative}: expected one {key!r} meta tag, found {len(values)}")
        return values[0] if values else ""
    if not values[0].strip():
        errors.append(f"{relative}: {key!r} metadata is empty")
    return values[0].strip()


def is_chapter(relative: str) -> bool:
    return any(
        relative.startswith(f"{root}/") and relative != f"{root}/index.html"
        for root in CHAPTER_ROOTS
    )


def type_set(node: dict[str, Any]) -> set[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def nodes_of_type(nodes: Iterable[dict[str, Any]], expected: str) -> list[dict[str, Any]]:
    return [node for node in nodes if expected in type_set(node)]


def walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def reference_id(value: Any) -> str:
    return value.get("@id", "") if isinstance(value, dict) else ""


def validate_image_schema(
    document: dict[str, Any],
    og_image: str,
    relative: str,
    errors: list[str],
) -> None:
    matching = [
        node
        for node in walk(document)
        if "ImageObject" in type_set(node) and node.get("url") == og_image
    ]
    if not matching:
        errors.append(f"{relative}: schema has no ImageObject matching og:image")
        return
    if not any(
        node.get("contentUrl") == og_image
        and node.get("width") == 1200
        and node.get("height") == 630
        and nonempty(node.get("caption"))
        for node in matching
    ):
        errors.append(f"{relative}: social ImageObject lacks URL, 1200x630 dimensions, or caption")


def validate_breadcrumb(
    nodes: list[dict[str, Any]],
    canonical: str,
    relative: str,
    errors: list[str],
) -> None:
    crumbs = nodes_of_type(nodes, "BreadcrumbList")
    if len(crumbs) != 1:
        errors.append(f"{relative}: expected one BreadcrumbList, found {len(crumbs)}")
        return
    crumb = crumbs[0]
    if crumb.get("@id") != f"{canonical}#breadcrumb":
        errors.append(f"{relative}: BreadcrumbList @id does not use the canonical URL")
    items = crumb.get("itemListElement")
    if not isinstance(items, list) or len(items) < 2:
        errors.append(f"{relative}: breadcrumb needs at least two ListItem entries")
        return
    positions = [item.get("position") for item in items if isinstance(item, dict)]
    if positions != list(range(1, len(items) + 1)):
        errors.append(f"{relative}: breadcrumb positions are not sequential: {positions!r}")
    for item in items:
        if not isinstance(item, dict) or "ListItem" not in type_set(item):
            errors.append(f"{relative}: breadcrumb includes a non-ListItem entry")
            continue
        if not nonempty(item.get("name")) or not nonempty(item.get("item")):
            errors.append(f"{relative}: breadcrumb ListItem has an empty name or item")
    if isinstance(items[0], dict) and items[0].get("item") != f"{BASE_URL}/":
        errors.append(f"{relative}: breadcrumb must begin at the canonical homepage")
    if isinstance(items[-1], dict) and items[-1].get("item") != canonical:
        errors.append(f"{relative}: breadcrumb must end at the page canonical URL")


def validate_chapter(
    relative: str,
    canonical: str,
    description: str,
    nodes: list[dict[str, Any]],
    errors: list[str],
    positions: defaultdict[str, list[int]],
) -> None:
    chapters = nodes_of_type(nodes, "Chapter")
    webpages = nodes_of_type(nodes, "WebPage")
    if len(chapters) != 1:
        errors.append(f"{relative}: expected one Chapter node, found {len(chapters)}")
        return
    if len(webpages) != 1:
        errors.append(f"{relative}: expected one WebPage node, found {len(webpages)}")
        return
    chapter = chapters[0]
    webpage = webpages[0]
    root = relative.split("/", 1)[0]
    expected_book = CHAPTER_ROOTS[root]
    expected_chapter_id = f"{canonical}#chapter"
    expected_webpage_id = f"{canonical}#webpage"
    checks = {
        "@id": expected_chapter_id,
        "url": canonical,
        "description": description,
        "inLanguage": "fa-IR",
    }
    for key, expected in checks.items():
        if chapter.get(key) != expected:
            errors.append(f"{relative}: Chapter {key} is {chapter.get(key)!r}, expected {expected!r}")
    if not nonempty(chapter.get("name")):
        errors.append(f"{relative}: Chapter name is empty")
    position = chapter.get("position")
    if not isinstance(position, int) or position < 0:
        errors.append(f"{relative}: Chapter position must be a non-negative integer")
    else:
        positions[root].append(position)
    part = chapter.get("isPartOf")
    if not isinstance(part, dict) or "Book" not in type_set(part):
        errors.append(f"{relative}: Chapter isPartOf must be a Book")
    else:
        if part.get("@id") != expected_book["book_id"] or part.get("url") != expected_book["book_url"]:
            errors.append(f"{relative}: Chapter points to the wrong parent Book")
        if not nonempty(part.get("name")):
            errors.append(f"{relative}: parent Book has no name")
    authors = chapter.get("author")
    if not isinstance(authors, list) or len(authors) != expected_book["author_count"]:
        errors.append(f"{relative}: Chapter must identify both original book authors")
    elif any(not isinstance(author, dict) or not nonempty(author.get("name")) for author in authors):
        errors.append(f"{relative}: Chapter has an unnamed author")
    translator = chapter.get("translator")
    if not isinstance(translator, dict) or translator.get("@id") != PERSON_ID or not nonempty(translator.get("name")):
        errors.append(f"{relative}: Chapter translator must identify Ali Rostami")
    if reference_id(chapter.get("mainEntityOfPage")) != expected_webpage_id:
        errors.append(f"{relative}: Chapter mainEntityOfPage does not reference its WebPage")
    if webpage.get("@id") != expected_webpage_id or webpage.get("url") != canonical:
        errors.append(f"{relative}: WebPage identity is not canonical")
    if webpage.get("description") != description or webpage.get("inLanguage") != "fa-IR":
        errors.append(f"{relative}: WebPage description or language differs from Chapter metadata")
    if reference_id(webpage.get("mainEntity")) != expected_chapter_id:
        errors.append(f"{relative}: WebPage mainEntity does not reference the Chapter")
    if reference_id(webpage.get("breadcrumb")) != f"{canonical}#breadcrumb":
        errors.append(f"{relative}: WebPage does not reference its breadcrumb")


def validate_article(
    relative: str,
    canonical: str,
    description: str,
    language: str,
    nodes: list[dict[str, Any]],
    errors: list[str],
) -> None:
    candidates = nodes_of_type(nodes, "Article") + nodes_of_type(nodes, "BlogPosting")
    # BlogPosting is a subtype conceptually, but represented as one explicit type here.
    unique = {id(node): node for node in candidates}
    articles = list(unique.values())
    if len(articles) != 1:
        errors.append(f"{relative}: expected one Article/BlogPosting node, found {len(articles)}")
        return
    article = articles[0]
    if article.get("@id") != f"{canonical}#article" or article.get("url") != canonical:
        errors.append(f"{relative}: article identity is not canonical")
    if article.get("description") != description or article.get("inLanguage") != language:
        errors.append(f"{relative}: article description or language is inconsistent")
    if not nonempty(article.get("headline")) or not nonempty(article.get("name")):
        errors.append(f"{relative}: article needs a non-empty headline and name")
    if not nonempty(article.get("datePublished")):
        errors.append(f"{relative}: article has no datePublished")
    if "wordcount" in article:
        errors.append(f"{relative}: use the Schema.org wordCount property, not wordcount")
    if "BlogPosting" in type_set(article) and (
        not isinstance(article.get("wordCount"), int) or article["wordCount"] <= 0
    ):
        errors.append(f"{relative}: BlogPosting needs a positive wordCount")
    people = nodes_of_type(nodes, "Person")
    if len(people) != 1 or people[0].get("@id") != PERSON_ID or not nonempty(people[0].get("name")):
        errors.append(f"{relative}: article graph needs one named Person entity for Ali Rostami")
    for role in ("author", "publisher"):
        if reference_id(article.get(role)) != PERSON_ID:
            errors.append(f"{relative}: article {role} does not reference Ali Rostami")
    if reference_id(article.get("mainEntityOfPage")) != f"{canonical}#webpage":
        errors.append(f"{relative}: article mainEntityOfPage is incorrect")


def validate_generic_schema(
    relative: str,
    canonical: str,
    description: str,
    language: str,
    nodes: list[dict[str, Any]],
    errors: list[str],
) -> None:
    expected_type = "WebPage"
    if relative in BOOK_PAGES:
        expected_type = "Book"
    elif relative in SOFTWARE_PAGES:
        expected_type = "SoftwareApplication"
    elif relative in ARCHIVE_PAGES:
        expected_type = "CollectionPage"
    candidates = nodes_of_type(nodes, expected_type)
    if len(candidates) != 1:
        errors.append(f"{relative}: expected one {expected_type} node, found {len(candidates)}")
        return
    primary = candidates[0]
    if primary.get("url") != canonical:
        errors.append(f"{relative}: {expected_type} URL differs from canonical")
    if primary.get("description") != description or primary.get("inLanguage") != language:
        errors.append(f"{relative}: {expected_type} description or language is inconsistent")
    if not nonempty(primary.get("name")):
        errors.append(f"{relative}: {expected_type} name is empty")
    if relative in BOOK_PAGES:
        authors = primary.get("author")
        if not isinstance(authors, list) or len(authors) < 2:
            errors.append(f"{relative}: Book must identify both authors")
        translator = primary.get("translator")
        if not isinstance(translator, dict) or translator.get("@id") != PERSON_ID:
            errors.append(f"{relative}: Book translator does not identify Ali Rostami")
    if relative in SOFTWARE_PAGES:
        author = primary.get("author")
        if not isinstance(author, dict) or author.get("@id") != PERSON_ID:
            errors.append(f"{relative}: SoftwareApplication author does not identify Ali Rostami")
        for key in ("applicationCategory", "operatingSystem", "offers"):
            if not primary.get(key):
                errors.append(f"{relative}: SoftwareApplication is missing {key}")
    if relative in BOOK_PAGES | SOFTWARE_PAGES:
        webpage = nodes_of_type(nodes, "WebPage")
        if len(webpage) != 1:
            errors.append(f"{relative}: entity page needs one WebPage wrapper")
        elif reference_id(webpage[0].get("mainEntity")) != primary.get("@id"):
            errors.append(f"{relative}: WebPage mainEntity does not reference the primary entity")


def validate_home(
    canonical: str,
    description: str,
    nodes: list[dict[str, Any]],
    errors: list[str],
) -> None:
    profiles = nodes_of_type(nodes, "ProfilePage")
    people = nodes_of_type(nodes, "Person")
    websites = nodes_of_type(nodes, "WebSite")
    if len(profiles) != 1 or len(people) != 1 or len(websites) != 1:
        errors.append("index.html: schema must include one ProfilePage, Person, and WebSite")
        return
    profile, person_node, website = profiles[0], people[0], websites[0]
    if profile.get("url") != canonical or profile.get("description") != description:
        errors.append("index.html: ProfilePage URL or description is inconsistent")
    if reference_id(profile.get("mainEntity")) != PERSON_ID:
        errors.append("index.html: ProfilePage mainEntity does not reference Person")
    if person_node.get("@id") != PERSON_ID or not nonempty(person_node.get("name")):
        errors.append("index.html: Person has no stable identity or name")
    if website.get("@id") != WEBSITE_ID or website.get("description") != description:
        errors.append("index.html: WebSite identity or description is inconsistent")
    if reference_id(website.get("publisher")) != PERSON_ID:
        errors.append("index.html: WebSite publisher does not reference Person")


def validate_schema(
    parsed: PageParser,
    relative: str,
    canonical: str,
    description: str,
    language: str,
    og_image: str,
    errors: list[str],
    type_counts: Counter[str],
    positions: defaultdict[str, list[int]],
) -> None:
    if len(parsed.json_scripts) != 1:
        errors.append(f"{relative}: expected one consolidated JSON-LD script, found {len(parsed.json_scripts)}")
        return
    script_id, payload = parsed.json_scripts[0]
    if script_id != "site-metadata-schema":
        errors.append(f"{relative}: JSON-LD script must use id=site-metadata-schema")
    try:
        document = json.loads(html.unescape(payload))
    except (json.JSONDecodeError, TypeError) as error:
        errors.append(f"{relative}: JSON-LD is invalid: {error}")
        return
    if not isinstance(document, dict) or document.get("@context") != "https://schema.org":
        errors.append(f"{relative}: JSON-LD must use the HTTPS Schema.org context")
        return
    graph = document.get("@graph")
    if not isinstance(graph, list) or not graph or any(not isinstance(node, dict) for node in graph):
        errors.append(f"{relative}: JSON-LD must contain a non-empty @graph of objects")
        return
    nodes: list[dict[str, Any]] = graph
    for node in nodes:
        for schema_type in type_set(node):
            type_counts[schema_type] += 1

    # Distinct fully-defined entities must not collide on @id.
    definitions: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in walk(document):
        node_id = node.get("@id")
        if isinstance(node_id, str) and len(node) > 2:
            definitions[node_id].append(node)
    collisions = [node_id for node_id, values in definitions.items() if len(values) > 1]
    if collisions:
        errors.append(f"{relative}: duplicate schema entity definitions: {collisions!r}")

    validate_image_schema(document, og_image, relative, errors)
    if relative == "index.html":
        validate_home(canonical, description, nodes, errors)
        if nodes_of_type(nodes, "BreadcrumbList"):
            errors.append("index.html: homepage should not emit a self-referential breadcrumb")
        return

    validate_breadcrumb(nodes, canonical, relative, errors)
    if is_chapter(relative):
        validate_chapter(relative, canonical, description, nodes, errors, positions)
    elif relative in ARTICLE_PAGES:
        validate_article(relative, canonical, description, language, nodes, errors)
    else:
        validate_generic_schema(relative, canonical, description, language, nodes, errors)


def validate_pipeline(errors: list[str]) -> None:
    source = (ROOT / "scripts/image_utils.py").read_text(encoding="utf-8")
    pipeline = source[source.find("def apply_site_postprocessors") :]
    calls = (
        "apply_image_seo()",
        'run_postprocessor("update-metadata.py")',
        'run_postprocessor("update-performance.py")',
        'run_postprocessor("update-accessibility.py")',
    )
    positions = [pipeline.find(call) for call in calls]
    if any(position < 0 for position in positions):
        errors.append("scripts/image_utils.py: site post-processing pipeline is incomplete")
    elif positions != sorted(positions):
        errors.append("scripts/image_utils.py: metadata must run after image SEO and before performance/accessibility")
    for relative in GENERATOR_SCRIPTS:
        generator = (ROOT / relative).read_text(encoding="utf-8")
        if "apply_site_postprocessors" not in generator or "apply_site_postprocessors()" not in generator:
            errors.append(f"{relative}: generator is not connected to the site post-processing pipeline")


def main() -> int:
    errors: list[str] = []
    validate_pipeline(errors)
    pages = indexable_pages(errors)
    descriptions: defaultdict[str, list[str]] = defaultdict(list)
    type_counts: Counter[str] = Counter()
    locale_counts: Counter[str] = Counter()
    positions: defaultdict[str, list[int]] = defaultdict(list)
    article_count = 0

    required_social = (
        "og:title",
        "og:description",
        "og:type",
        "og:url",
        "og:site_name",
        "og:locale",
        "og:image",
        "og:image:secure_url",
        "og:image:type",
        "og:image:width",
        "og:image:height",
        "og:image:alt",
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:creator",
        "twitter:site",
        "twitter:image",
        "twitter:image:alt",
    )

    for path, canonical in sorted(pages.items(), key=lambda item: item[1]):
        relative = path.relative_to(ROOT).as_posix()
        parsed = parse_page(path)
        if parsed.canonicals != [canonical]:
            errors.append(f"{relative}: canonical mismatch: {parsed.canonicals!r}")
        language = "en-US" if parsed.html_lang.lower().startswith("en") else "fa-IR"
        description = one_meta(parsed, "description", relative, errors)
        if description:
            length = len(description)
            if length < 60 or length > 220:
                errors.append(f"{relative}: description length {length} is outside 60..220")
            descriptions[" ".join(description.casefold().split())].append(relative)
        values = {key: one_meta(parsed, key, relative, errors) for key in required_social}
        if values["og:description"] != description or values["twitter:description"] != description:
            errors.append(f"{relative}: social descriptions must exactly match meta description")
        if values["og:title"] != values["twitter:title"]:
            errors.append(f"{relative}: Open Graph and Twitter titles differ")
        if values["og:url"] != canonical:
            errors.append(f"{relative}: og:url differs from canonical")
        expected_locale = "en_US" if language == "en-US" else "fa_IR"
        if values["og:locale"] != expected_locale:
            errors.append(f"{relative}: og:locale {values['og:locale']!r}, expected {expected_locale!r}")
        locale_counts[values["og:locale"]] += 1
        if values["twitter:creator"] != TWITTER_HANDLE or values["twitter:site"] != TWITTER_HANDLE:
            errors.append(f"{relative}: Twitter creator/site handle is inconsistent")
        if values["twitter:card"] != "summary_large_image":
            errors.append(f"{relative}: Twitter card must be summary_large_image")
        if values["og:image"] != values["og:image:secure_url"] or values["og:image"] != values["twitter:image"]:
            errors.append(f"{relative}: Open Graph and Twitter image URLs differ")
        if values["og:image:type"] != "image/jpeg" or values["og:image:width"] != "1200" or values["og:image:height"] != "630":
            errors.append(f"{relative}: social image type or dimensions are incorrect")
        if values["og:image:alt"] != values["twitter:image:alt"]:
            errors.append(f"{relative}: Open Graph and Twitter image alt text differs")
        if language == "en-US" and re.search(r"[\u0600-\u06ff]", values["og:image:alt"]):
            errors.append(f"{relative}: English social preview has Persian-only image alt text")

        expected_type = "profile" if relative == "index.html" else "website"
        if relative in ARTICLE_PAGES or is_chapter(relative):
            expected_type = "article"
            article_count += 1
        elif relative in BOOK_PAGES:
            expected_type = "book"
        if values["og:type"] != expected_type:
            errors.append(f"{relative}: og:type {values['og:type']!r}, expected {expected_type!r}")

        alternate_locales = parsed.metas.get("og:locale:alternate", [])
        if alternate_locales:
            errors.append(f"{relative}: unexpected og:locale:alternate")
        if parsed.alternates:
            errors.append(f"{relative}: unexpected hreflang links: {parsed.alternates!r}")

        if expected_type == "article":
            author = one_meta(parsed, "article:author", relative, errors)
            section = one_meta(parsed, "article:section", relative, errors)
            if author != f"{BASE_URL}/" or not section:
                errors.append(f"{relative}: article social metadata is incomplete")
        elif parsed.metas.get("article:author") or parsed.metas.get("article:section"):
            errors.append(f"{relative}: non-article page emits article metadata")

        validate_schema(
            parsed,
            relative,
            canonical,
            description,
            language,
            values["og:image"],
            errors,
            type_counts,
            positions,
        )

    duplicates = {key: files for key, files in descriptions.items() if len(files) > 1}
    for files in duplicates.values():
        errors.append(f"duplicate description across pages: {', '.join(files)}")
    for stale in ("this is my personal website", "everything is mine"):
        for key, files in descriptions.items():
            if stale in key:
                errors.append(f"stale placeholder metadata on: {', '.join(files)}")

    expected_positions = {
        "aima-4e": list(range(29)),
        "software-architecture": list(range(1, 29)),
    }
    for root, expected in expected_positions.items():
        actual = sorted(positions[root])
        if actual != expected:
            errors.append(f"{root}: chapter positions are incomplete: {actual!r}")

    if len(pages) != 70:
        errors.append(f"expected 70 indexable pages, found {len(pages)}")
    if article_count != 61:
        errors.append(f"expected 61 article social previews, found {article_count}")
    if locale_counts != Counter({"fa_IR": 67, "en_US": 3}):
        errors.append(f"unexpected locale distribution: {dict(locale_counts)!r}")
    if type_counts["Chapter"] != 57:
        errors.append(f"expected 57 Chapter nodes, found {type_counts['Chapter']}")
    if type_counts["BreadcrumbList"] != 69:
        errors.append(f"expected 69 BreadcrumbList nodes, found {type_counts['BreadcrumbList']}")

    if errors:
        print(f"metadata audit failed ({len(errors)} issue(s)):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("metadata audit passed")
    print(f"  indexable pages: {len(pages)}")
    print(f"  unique descriptions: {len(descriptions)}")
    print(f"  complete Open Graph/Twitter previews: {len(pages)} ({article_count} article)")
    print(f"  locales: fa_IR={locale_counts['fa_IR']}, en_US={locale_counts['en_US']}")
    print(
        "  structured data: "
        f"Chapter={type_counts['Chapter']}, Book={type_counts['Book']}, "
        f"Article/BlogPosting={type_counts['Article'] + type_counts['BlogPosting']}, "
        f"BreadcrumbList={type_counts['BreadcrumbList']}"
    )
    print("  single-site metadata: no language alternates or retired section canonicals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
