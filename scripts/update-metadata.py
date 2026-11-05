#!/usr/bin/env python3
"""Normalize page descriptions, social metadata, hreflang, and JSON-LD.

This Phase-5 post-processor is stdlib-only and safe to run repeatedly. It runs
after image SEO so the schema graph can reference the selected social image.
"""

from __future__ import annotations

import copy
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
    social_alt_for_page,
    social_card_for_page,
)
from software_architecture_routes import SOFTWARE_ARCHITECTURE_POSITIONS

HEAD_RE = re.compile(r"(<head\b[^>]*>)(.*?)(</head\s*>)", re.IGNORECASE | re.DOTALL)
META_RE = re.compile(r"<meta\b[^>]*>", re.IGNORECASE | re.DOTALL)
LINK_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE | re.DOTALL)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title\s*>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1\s*>", re.IGNORECASE | re.DOTALL)
HTML_RE = re.compile(r"<html\b[^>]*>", re.IGNORECASE | re.DOTALL)
SCRIPT_RE = re.compile(
    r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>.*?</script\s*>",
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_CONTENT_RE = re.compile(
    r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script\s*>",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)

MANAGED_META = {
    "description",
    "og:title",
    "og:description",
    "og:type",
    "og:url",
    "og:site_name",
    "og:locale",
    "og:locale:alternate",
    "twitter:title",
    "twitter:description",
    "twitter:creator",
    "twitter:site",
    "article:author",
    "article:section",
}

PERSON_ID = f"{BASE_URL}/#person"
WEBSITE_ID = f"{BASE_URL}/#website"
SITE_NAME = "Ali Rostami | علی رستمی"
TWITTER_HANDLE = "@alirostami01"

DESCRIPTIONS = {
    "index.html": (
        "وب‌سایت علی رستمی، معمار ارشد نرم‌افزار؛ معرفی پروژه‌های متن‌باز، "
        "ترجمهٔ فارسی کتاب‌های هوش مصنوعی و معماری نرم‌افزار و مقالات فنی."
    ),
    "aima-4e-persian/index.html": (
        "ترجمهٔ فارسی ویرایش چهارم کتاب هوش مصنوعی: رویکردی نوین اثر استوارت راسل "
        "و پیتر نورویگ؛ همراه مطالعهٔ آنلاین، PDF و فایل‌های متن‌باز."
    ),
    "aima-4e/index.html": (
        "مطالعهٔ آنلاین ترجمهٔ فارسی ویرایش چهارم کتاب هوش مصنوعی: رویکردی نوین، "
        "با فهرست ۲۸ فصل، جست‌وجو و کتاب‌خوان سازگار با موبایل."
    ),
    "fundamentals-of-software-architecture-persian/index.html": (
        "ترجمهٔ فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار اثر مارک ریچاردز و "
        "نیل فورد؛ شامل ۲۷ فصل، پیوست، نسخهٔ PDF و فایل‌های متن‌باز."
    ),
    "software-architecture/index.html": (
        "مطالعهٔ آنلاین ترجمهٔ فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار، با "
        "فهرست ۲۷ فصل، پیوست، جست‌وجو و کتاب‌خوان سازگار با موبایل."
    ),
    "persian-streams/index.html": (
        "Persian Streams افزونه‌ای متن‌باز برای تماشای فیلم‌ها و سریال‌های ایرانی "
        "در Stremio است؛ همراه راهنمای نصب، قابلیت‌ها و سورس پروژه."
    ),
    "persian-subtitles/index.html": (
        "Persian Subtitles افزونه‌ای متن‌باز برای دریافت خودکار زیرنویس فارسی فیلم "
        "و سریال در Stremio است؛ همراه راهنمای نصب و سورس پروژه."
    ),
    "support/index.html": (
        "با حمایت مالی یا غیرمالی از پروژه‌های متن‌باز، ترجمهٔ کتاب‌ها و منابع "
        "آموزشی علی رستمی، به توسعه و نگهداری پایدار آن‌ها کمک کنید."
    ),
    "en/support/index.html": (
        "Support Ali Rostami’s open-source software, Persian book translations, "
        "educational resources, and the infrastructure that keeps them available."
    ),
    "posts/index.html": (
        "Browse Ali Rostami’s articles and notes on software architecture, artificial "
        "intelligence, Linux, productivity, and open-source projects."
    ),
    "categories/index.html": (
        "Browse categories for Ali Rostami’s articles on software engineering, "
        "artificial intelligence, Linux, developer tools, and open-source projects."
    ),
    "tags/index.html": (
        "Explore tags from Ali Rostami’s technical articles and quickly find writing "
        "about software, AI, Linux, productivity, and open-source tools."
    ),
    "posts/a-recap-of-last-year/index.html": (
        "A personal recap of Ali Rostami’s work and learning over the previous year, "
        "including software projects, technical growth, challenges, and future plans."
    ),
    "posts/benefits-of-using-obsidian/index.html": (
        "Explore the practical benefits of Obsidian for connected note-taking, "
        "personal knowledge management, Markdown workflows, and a durable second brain."
    ),
    "posts/aima-4e-persian/index.html": (
        "معرفی پروژهٔ ترجمهٔ فارسی ویرایش چهارم کتاب هوش مصنوعی: رویکردی نوین اثر "
        "راسل و نورویگ؛ همراه مطالعهٔ آنلاین، PDF و سورس کامل."
    ),
    "posts/fundamentals-of-software-architecture-persian/index.html": (
        "معرفی ترجمهٔ فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار اثر مارک ریچاردز "
        "و نیل فورد؛ همراه مطالعهٔ آنلاین، PDF و سورس متن‌باز."
    ),
}

SOCIAL_TITLES = {
    "index.html": "علی رستمی | معماری نرم‌افزار، هوش مصنوعی و متن‌باز",
    "categories/index.html": "Article Categories | Ali Rostami",
    "tags/index.html": "Article Tags | Ali Rostami",
    "posts/index.html": "Articles & Notes | Ali Rostami",
    "posts/a-recap-of-last-year/index.html": "A Recap of Last Year | Ali Rostami",
    "posts/benefits-of-using-obsidian/index.html": "Benefits of Using Obsidian | Ali Rostami",
    "en/support/index.html": "Support Ali Rostami’s Open-Source Work",
    "support/index.html": "حمایت از پروژه‌های متن‌باز علی رستمی",
}

ARCHIVE_PAGES = {"categories/index.html", "tags/index.html", "posts/index.html"}
ARTICLE_PAGES = {
    "posts/a-recap-of-last-year/index.html",
    "posts/benefits-of-using-obsidian/index.html",
    "posts/aima-4e-persian/index.html",
    "posts/fundamentals-of-software-architecture-persian/index.html",
}
SUPPORT_ALTERNATES = {
    "fa": f"{BASE_URL}/support/",
    "en": f"{BASE_URL}/en/support/",
    "x-default": f"{BASE_URL}/support/",
}

BOOKS = {
    "aima-4e": {
        "url": f"{BASE_URL}/aima-4e/",
        "id": f"{BASE_URL}/aima-4e/#book",
        "name": "هوش مصنوعی: رویکردی نوین (ویرایش چهارم)",
        "alternateName": "Artificial Intelligence: A Modern Approach (4th Edition)",
        "authors": ("Stuart Russell", "Peter Norvig"),
    },
    "software-architecture": {
        "url": f"{BASE_URL}/software-architecture/",
        "id": f"{BASE_URL}/software-architecture/#book",
        "name": "مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن (ویرایش دوم)",
        "alternateName": "Fundamentals of Software Architecture: A Modern Engineering Approach (2nd Edition)",
        "authors": ("Mark Richards", "Neal Ford"),
    },
}


def attribute_tokens(tag: str) -> list[tuple[str, str]]:
    """Parse start-tag attributes without mistaking quoted text for attributes."""
    result: list[tuple[str, str]] = []
    length = len(tag)
    index = 1
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
        name = tag[start:index].lower()
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
                start = index
                while index < length and tag[index] != quote:
                    index += 1
                value = tag[start:index]
                if index < length:
                    index += 1
            else:
                start = index
                while index < length and not tag[index].isspace() and tag[index] != ">":
                    index += 1
                value = tag[start:index]
        result.append((name, html.unescape(value)))
    return result


def attributes(tag: str) -> dict[str, str]:
    return dict(attribute_tokens(tag))


def plain_text(fragment: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", fragment)).split())


def title_from(raw: str) -> str:
    match = TITLE_RE.search(raw)
    if match is None:
        raise ValueError("page has no title")
    return plain_text(match.group(1))


def heading_from(raw: str, fallback: str) -> str:
    match = H1_RE.search(raw)
    return plain_text(match.group(1)) if match else fallback


def language_from(raw: str) -> str:
    match = HTML_RE.search(raw)
    language = attributes(match.group(0)).get("lang", "") if match else ""
    return "en-US" if language.lower().startswith("en") else "fa-IR"


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


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if ".git" not in path.parts and "layouts" not in path.parts
    ]


def sitemap_pages() -> dict[Path, str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    result: dict[Path, str] = {}
    for node in root.iter():
        if not node.tag.endswith("loc") or not node.text:
            continue
        url = node.text.strip()
        target = file_for_url(url)
        if target is None:
            raise FileNotFoundError(f"missing sitemap target: {url}")
        result[target.resolve()] = url
    return result


def indexable_pages() -> dict[Path, str]:
    """Return sitemap pages plus self-canonical indexable HTML pages."""
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
        canonicals = [
            data["href"]
            for tag in LINK_RE.findall(raw)
            if "canonical" in (data := attributes(tag)).get("rel", "").lower().split()
            and data.get("href")
        ]
        if len(canonicals) != 1 or not canonicals[0].startswith(f"{BASE_URL}/"):
            continue
        target = file_for_url(canonicals[0])
        if target is not None and target.resolve() == resolved:
            result[resolved] = canonicals[0]
    return result


def description_for(relative: str, heading: str) -> str:
    if relative.startswith("aima-4e/") and relative != "aima-4e/index.html":
        return (
            f"{heading}؛ مطالعهٔ آنلاین ترجمهٔ فارسی کتاب هوش مصنوعی: رویکردی نوین، "
            "ویرایش چهارم."
        )
    if relative.startswith("software-architecture/") and relative != "software-architecture/index.html":
        return f"{heading}؛ مطالعهٔ آنلاین ترجمهٔ فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار."
    try:
        return DESCRIPTIONS[relative]
    except KeyError as error:
        raise KeyError(f"no managed description for {relative}") from error


def social_title_for(relative: str, title: str, heading: str) -> str:
    if relative.startswith("aima-4e/") and relative != "aima-4e/index.html":
        return f"{heading} | ترجمهٔ فارسی AIMA 4e"
    if relative.startswith("software-architecture/") and relative != "software-architecture/index.html":
        return f"{heading} | مبانی معماری نرم‌افزار"
    return SOCIAL_TITLES.get(relative, title)


def og_type_for(relative: str) -> str:
    if relative == "index.html":
        return "profile"
    if relative in ARTICLE_PAGES or is_chapter(relative):
        return "article"
    if relative in {
        "aima-4e/index.html",
        "aima-4e-persian/index.html",
        "software-architecture/index.html",
        "fundamentals-of-software-architecture-persian/index.html",
    }:
        return "book"
    return "website"


def is_chapter(relative: str) -> bool:
    return (
        relative.startswith("aima-4e/") and relative != "aima-4e/index.html"
    ) or (
        relative.startswith("software-architecture/")
        and relative != "software-architecture/index.html"
    )


def meta_key(tag: str) -> str:
    data = attributes(tag)
    return (data.get("property") or data.get("name") or "").lower()


def render_metadata(
    relative: str,
    canonical: str,
    title: str,
    description: str,
    language: str,
) -> str:
    locale = "en_US" if language == "en-US" else "fa_IR"
    lines = [
        "    <!-- metadata-seo:start -->",
        f'    <meta name="description" content="{html.escape(description, quote=True)}">',
        f'    <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'    <meta property="og:description" content="{html.escape(description, quote=True)}">',
        f'    <meta property="og:type" content="{og_type_for(relative)}">',
        f'    <meta property="og:url" content="{html.escape(canonical, quote=True)}">',
        f'    <meta property="og:site_name" content="{html.escape(SITE_NAME, quote=True)}">',
        f'    <meta property="og:locale" content="{locale}">',
    ]
    if relative in {"support/index.html", "en/support/index.html"}:
        alternate_locale = "fa_IR" if locale == "en_US" else "en_US"
        lines.append(f'    <meta property="og:locale:alternate" content="{alternate_locale}">')
    lines.extend(
        [
            f'    <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
            f'    <meta name="twitter:description" content="{html.escape(description, quote=True)}">',
            f'    <meta name="twitter:creator" content="{TWITTER_HANDLE}">',
            f'    <meta name="twitter:site" content="{TWITTER_HANDLE}">',
        ]
    )
    if og_type_for(relative) == "article":
        section = "Artificial Intelligence" if relative.startswith("aima-4e/") else "Software Architecture"
        if relative.startswith("posts/"):
            section = "Articles"
        lines.extend(
            [
                f'    <meta property="article:author" content="{BASE_URL}/">',
                f'    <meta property="article:section" content="{section}">',
            ]
        )
    if relative in {"support/index.html", "en/support/index.html"}:
        for code, url in SUPPORT_ALTERNATES.items():
            lines.append(
                f'    <link rel="alternate" hreflang="{code}" href="{html.escape(url, quote=True)}">'
            )
    lines.append("    <!-- metadata-seo:end -->")
    return "\n".join(lines)


def load_schema_nodes(raw: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for match in SCRIPT_CONTENT_RE.finditer(raw):
        try:
            document = json.loads(html.unescape(match.group(1)).strip())
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(document, dict):
            continue
        graph = document.get("@graph")
        candidates = graph if isinstance(graph, list) else [document]
        for candidate in candidates:
            if isinstance(candidate, dict):
                node = copy.deepcopy(candidate)
                node.pop("@context", None)
                nodes.append(node)
    return nodes


def schema_types(node: dict[str, Any]) -> set[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def image_object(relative: str, canonical: str) -> dict[str, Any]:
    card = social_card_for_page(relative)
    return {
        "@type": "ImageObject",
        "@id": f"{canonical}#primaryimage",
        "url": card.url,
        "contentUrl": card.url,
        "width": SOCIAL_WIDTH,
        "height": SOCIAL_HEIGHT,
        "caption": social_alt_for_page(relative),
    }


def person(language: str) -> dict[str, Any]:
    return {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": "Ali Rostami" if language == "en-US" else "علی رستمی",
        "alternateName": "علی رستمی" if language == "en-US" else "Ali Rostami",
        "url": f"{BASE_URL}/",
    }


def book_reference(book: dict[str, Any]) -> dict[str, Any]:
    return {
        "@type": "Book",
        "@id": book["id"],
        "url": book["url"],
        "name": book["name"],
        "alternateName": book["alternateName"],
        "author": [
            {"@type": "Person", "name": author} for author in book["authors"]
        ],
    }


def breadcrumb(
    relative: str,
    canonical: str,
    page_name: str,
    language: str,
    book: dict[str, Any] | None = None,
) -> dict[str, Any]:
    home = "Home" if language == "en-US" else "خانه"
    items: list[tuple[str, str]] = [(home, f"{BASE_URL}/")]
    if book is not None:
        items.append((book["name"], book["url"]))
    elif relative.startswith("posts/") and relative != "posts/index.html":
        items.append(("Articles" if language == "en-US" else "مقالات", f"{BASE_URL}/posts/"))
    elif relative not in ARCHIVE_PAGES and relative not in {"support/index.html", "en/support/index.html"}:
        items.append(("Projects" if language == "en-US" else "پروژه‌ها", f"{BASE_URL}/#projects"))
    items.append((page_name, canonical))
    return {
        "@type": "BreadcrumbList",
        "@id": f"{canonical}#breadcrumb",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": url,
            }
            for position, (name, url) in enumerate(items, start=1)
        ],
    }


def chapter_position(relative: str) -> int:
    filename = Path(relative).name
    if relative.startswith("aima-4e/"):
        match = re.match(r"(\d+)-", filename)
        if match:
            return int(match.group(1))
    if relative.startswith("software-architecture/"):
        try:
            return SOFTWARE_ARCHITECTURE_POSITIONS[Path(filename).stem]
        except KeyError as error:
            raise ValueError(f"cannot determine chapter position: {relative}") from error
    raise ValueError(f"cannot determine chapter position: {relative}")


def chapter_schema(
    relative: str,
    canonical: str,
    heading: str,
    description: str,
) -> dict[str, Any]:
    book = BOOKS["aima-4e" if relative.startswith("aima-4e/") else "software-architecture"]
    image = image_object(relative, canonical)
    chapter_id = f"{canonical}#chapter"
    webpage_id = f"{canonical}#webpage"
    chapter = {
        "@type": "Chapter",
        "@id": chapter_id,
        "url": canonical,
        "name": heading,
        "description": description,
        "inLanguage": "fa-IR",
        "position": chapter_position(relative),
        "isPartOf": book_reference(book),
        "author": [
            {"@type": "Person", "name": author} for author in book["authors"]
        ],
        "translator": person("fa-IR"),
        "mainEntityOfPage": {"@id": webpage_id},
        "image": {"@id": image["@id"]},
    }
    webpage = {
        "@type": "WebPage",
        "@id": webpage_id,
        "url": canonical,
        "name": heading,
        "description": description,
        "inLanguage": "fa-IR",
        "isPartOf": {"@type": "WebSite", "@id": WEBSITE_ID},
        "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
        "image": image,
        "primaryImageOfPage": {"@id": image["@id"]},
        "mainEntity": {"@id": chapter_id},
    }
    return {
        "@context": "https://schema.org",
        "@graph": [
            chapter,
            webpage,
            breadcrumb(relative, canonical, heading, "fa-IR", book),
        ],
    }


def primary_node(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    priority = (
        "BlogPosting",
        "Article",
        "Book",
        "SoftwareApplication",
        "CollectionPage",
        "ProfilePage",
        "WebPage",
        "WebSite",
    )
    for expected in priority:
        for node in nodes:
            if expected in schema_types(node):
                return copy.deepcopy(node)
    return {"@type": "WebPage"}


def normalize_ali_entity(value: Any, language: str) -> Any:
    if not isinstance(value, dict):
        return value
    name = str(value.get("name", "")).lower()
    if "rostami" in name or "رستمی" in name:
        return person(language)
    return value


def home_schema(
    nodes: list[dict[str, Any]],
    canonical: str,
    title: str,
    description: str,
) -> dict[str, Any]:
    graph = [copy.deepcopy(node) for node in nodes if "BreadcrumbList" not in schema_types(node)]
    profile = next((node for node in graph if "ProfilePage" in schema_types(node)), None)
    website = next((node for node in graph if "WebSite" in schema_types(node)), None)
    person_node = next((node for node in graph if "Person" in schema_types(node)), None)
    if profile is None:
        profile = {"@type": "ProfilePage"}
        graph.insert(0, profile)
    profile.update(
        {
            "@id": f"{canonical}#profilepage",
            "url": canonical,
            "name": title,
            "description": description,
            "inLanguage": "fa-IR",
            "mainEntity": {"@id": PERSON_ID},
            "image": image_object("index.html", canonical),
        }
    )
    if person_node is None:
        person_node = person("fa-IR")
        graph.append(person_node)
    person_node.update({"@type": "Person", "@id": PERSON_ID, "url": canonical})
    if not person_node.get("name"):
        person_node["name"] = "Ali Rostami"
    if isinstance(person_node.get("image"), dict):
        person_node["image"]["@id"] = f"{canonical}#personimage"
    if website is None:
        website = {"@type": "WebSite"}
        graph.append(website)
    website.update(
        {
            "@id": WEBSITE_ID,
            "url": canonical,
            "name": SITE_NAME,
            "description": description,
            "inLanguage": ["fa-IR", "en-US"],
            "publisher": {"@id": PERSON_ID},
        }
    )
    return {"@context": "https://schema.org", "@graph": graph}


def generic_schema(
    relative: str,
    canonical: str,
    page_name: str,
    description: str,
    language: str,
    nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    primary = primary_node(nodes)
    if relative in ARCHIVE_PAGES:
        primary["@type"] = "CollectionPage"
    elif relative in {"support/index.html", "en/support/index.html"}:
        primary["@type"] = "WebPage"
    primary.pop("@context", None)
    primary.pop("license", None)
    types = schema_types(primary)
    entity_suffix = "webpage"
    if "BlogPosting" in types or "Article" in types:
        entity_suffix = "article"
    elif "Book" in types:
        entity_suffix = "book"
    elif "SoftwareApplication" in types:
        entity_suffix = "softwareapplication"
    primary_id = f"{canonical}#{entity_suffix}"
    image = image_object(relative, canonical)
    primary.update(
        {
            "@id": primary_id,
            "url": canonical,
            "description": description,
            "inLanguage": language,
            "image": image,
        }
    )
    if types & {"Article", "BlogPosting"}:
        legacy_word_count = primary.pop("wordcount", None)
        if isinstance(legacy_word_count, int) and legacy_word_count > 0:
            primary["wordCount"] = legacy_word_count
        primary["headline"] = page_name
        primary["name"] = page_name
        primary["author"] = {"@id": PERSON_ID}
        primary["publisher"] = {"@id": PERSON_ID}
        primary["mainEntityOfPage"] = {"@id": f"{canonical}#webpage"}
        primary["isPartOf"] = {"@type": "WebSite", "@id": WEBSITE_ID}
    else:
        if not str(primary.get("name", "")).strip():
            primary["name"] = page_name
        if "Book" in types:
            primary["translator"] = person(language)
            authors = primary.get("author")
            if not isinstance(authors, list) or not authors:
                book = BOOKS["aima-4e" if "aima" in relative else "software-architecture"]
                primary["author"] = [
                    {"@type": "Person", "name": author} for author in book["authors"]
                ]
            primary["mainEntityOfPage"] = {"@id": f"{canonical}#webpage"}
        elif "SoftwareApplication" in types:
            primary["author"] = normalize_ali_entity(primary.get("author"), language) or person(language)
            primary["mainEntityOfPage"] = {"@id": f"{canonical}#webpage"}

    crumb = breadcrumb(relative, canonical, page_name, language)
    if types & {"Article", "BlogPosting", "Book", "SoftwareApplication"}:
        webpage = {
            "@type": "WebPage",
            "@id": f"{canonical}#webpage",
            "url": canonical,
            "name": page_name,
            "description": description,
            "inLanguage": language,
            "isPartOf": {"@type": "WebSite", "@id": WEBSITE_ID},
            "breadcrumb": {"@id": crumb["@id"]},
            "primaryImageOfPage": {"@id": image["@id"]},
            "mainEntity": {"@id": primary_id},
        }
        graph = [primary, webpage]
        if types & {"Article", "BlogPosting"}:
            graph.append(person(language))
        graph.append(crumb)
    else:
        primary["breadcrumb"] = {"@id": crumb["@id"]}
        primary["isPartOf"] = {"@type": "WebSite", "@id": WEBSITE_ID}
        graph = [primary, crumb]
    return {"@context": "https://schema.org", "@graph": graph}


def schema_for(
    relative: str,
    canonical: str,
    title: str,
    heading: str,
    description: str,
    language: str,
    old_nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    if is_chapter(relative):
        return chapter_schema(relative, canonical, heading, description)
    if relative == "index.html":
        return home_schema(old_nodes, canonical, title, description)
    return generic_schema(relative, canonical, heading, description, language, old_nodes)


def render_schema(document: dict[str, Any]) -> str:
    payload = json.dumps(document, ensure_ascii=False, indent=2)
    return f'    <script type="application/ld+json" id="site-metadata-schema">\n{payload}\n    </script>'


def clean_head(head: str, relative: str) -> str:
    head = re.sub(
        r"[ \t]*<!-- metadata-seo:start -->.*?<!-- metadata-seo:end -->[ \t]*",
        "",
        head,
        flags=re.DOTALL,
    )
    head = SCRIPT_RE.sub("", head)
    head = META_RE.sub(lambda match: "" if meta_key(match.group(0)) in MANAGED_META else match.group(0), head)
    if relative in {"support/index.html", "en/support/index.html"}:
        head = LINK_RE.sub(
            lambda match: ""
            if "alternate" in attributes(match.group(0)).get("rel", "").lower().split()
            and attributes(match.group(0)).get("hreflang")
            else match.group(0),
            head,
        )
    head = re.sub(r"[ \t]+(?=\r?$)", "", head, flags=re.MULTILINE)
    head = re.sub(r"(?:\r?\n[ \t]*){3,}", "\n\n", head)
    return head.rstrip()


def update_page(raw: str, relative: str, canonical: str) -> str:
    title = title_from(raw)
    heading = heading_from(raw, title)
    language = language_from(raw)
    description = description_for(relative, heading)
    social_title = social_title_for(relative, title, heading)
    old_nodes = load_schema_nodes(raw)
    schema = schema_for(
        relative,
        canonical,
        social_title,
        heading,
        description,
        language,
        old_nodes,
    )
    metadata_block = render_metadata(relative, canonical, social_title, description, language)
    schema_block = render_schema(schema)

    match = HEAD_RE.search(raw)
    if match is None:
        raise ValueError(f"page has no head element: {relative}")
    cleaned = clean_head(match.group(2), relative)
    downstream = re.search(
        r"^[ \t]*<!-- accessibility-styles:start -->",
        cleaned,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if downstream is None:
        prefix = cleaned
        suffix = ""
    else:
        prefix = cleaned[: downstream.start()].rstrip()
        suffix = "    " + cleaned[downstream.start() :].lstrip()
    separator = "\n" if prefix else ""
    managed = f"{metadata_block}\n{schema_block}"
    tail = f"\n{suffix}" if suffix else ""
    replacement = f"{match.group(1)}{prefix}{separator}{managed}{tail}\n{match.group(3)}"
    updated = f"{raw[:match.start()]}{replacement}{raw[match.end():]}"
    return re.sub(r"[ \t]+$", "", updated, flags=re.MULTILINE)


def main() -> None:
    pages = indexable_pages()
    changed = 0
    chapter_count = 0
    for path, canonical in sorted(pages.items(), key=lambda item: item[1]):
        relative = path.relative_to(ROOT).as_posix()
        raw = path.read_text(encoding="utf-8", errors="strict")
        updated = update_page(raw, relative, canonical)
        chapter_count += is_chapter(relative)
        if updated != raw:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"metadata updated: {changed} HTML files")
    print(f"indexable pages covered: {len(pages)} ({chapter_count} book chapters)")


if __name__ == "__main__":
    main()
