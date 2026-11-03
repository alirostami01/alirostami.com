#!/usr/bin/env python3
"""Build visible breadcrumbs, related routes, and static book navigation.

The Phase-6 post-processor is dependency-free and deterministic. It consumes the
BreadcrumbList emitted by update-metadata.py so the visible trail and JSON-LD
cannot drift, then adds a small set of curated discovery paths and crawlable
previous/next links for every book chapter.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_HOST = "www.alirostami.com"

HEAD_END_RE = re.compile(r"</head\s*>", re.IGNORECASE)
MAIN_START_RE = re.compile(r"<main\b[^>]*>", re.IGNORECASE | re.DOTALL)
MAIN_END_RE = re.compile(r"</main\s*>", re.IGNORECASE)
SCHEMA_RE = re.compile(
    r'<script\b[^>]*id=["\']site-metadata-schema["\'][^>]*>(.*?)</script\s*>',
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
ANCHOR_RE = re.compile(r"(<a\b[^>]*>)(.*?)(</a\s*>)", re.IGNORECASE | re.DOTALL)
HEADING_RE = re.compile(r"(<h([1-6])\b[^>]*>)(.*?)(</h\2\s*>)", re.IGNORECASE | re.DOTALL)
HREF_RE = re.compile(r"\bhref\s*=\s*([\"'])(.*?)\1", re.IGNORECASE | re.DOTALL)

STYLE_MARKER = "internal-linking-styles"
BREADCRUMB_MARKER = "internal-breadcrumb"
RELATED_MARKER = "internal-related"
CHAPTER_MARKER = "internal-chapter-navigation"
AIMA_HUB_MARKER = "internal-aima-book-hub"
POST_ARCHIVE_MARKER = "internal-post-archive-entry"
MARKERS = (
    STYLE_MARKER,
    BREADCRUMB_MARKER,
    RELATED_MARKER,
    CHAPTER_MARKER,
    AIMA_HUB_MARKER,
    POST_ARCHIVE_MARKER,
)

# The labels are deliberately descriptive: every generated anchor is useful out
# of context to readers, assistive technology, and search crawlers.
RELATED_CONTENT: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {
    "index.html": (
        "مسیرهای اصلی سایت",
        (
            ("مقالات و یادداشت‌های فنی علی رستمی", "/posts/"),
            ("دسته‌بندی موضوعی مقاله‌ها و پروژه‌ها", "/categories/"),
            ("برچسب‌های موضوعی محتوا", "/tags/"),
            ("ترجمهٔ فارسی کتاب هوش مصنوعی AIMA، ویرایش چهارم", "/aima-4e-persian/"),
            ("ترجمهٔ فارسی مبانی معماری نرم‌افزار، ویرایش دوم", "/fundamentals-of-software-architecture-persian/"),
            ("Support open-source projects in English", "/en/support/"),
        ),
    ),
    "posts/index.html": (
        "More ways to explore",
        (
            ("Project hub: Persian translation of AIMA, fourth edition", "/aima-4e-persian/"),
            ("Project hub: Persian translation of Fundamentals of Software Architecture", "/fundamentals-of-software-architecture-persian/"),
            ("Browse articles and projects by category", "/categories/"),
            ("Explore the site’s topic tags", "/tags/"),
        ),
    ),
    "categories/index.html": (
        "Browse topic categories",
        (
            ("Artificial intelligence and the Persian AIMA translation", "/aima-4e-persian/"),
            ("Read the Persian AIMA book online", "/aima-4e/"),
            ("Software architecture and the Persian book translation", "/fundamentals-of-software-architecture-persian/"),
            ("Read Fundamentals of Software Architecture online", "/software-architecture/"),
            ("Open-source Stremio add-ons", "/persian-streams/"),
            ("Productivity and knowledge-management articles", "/posts/benefits-of-using-obsidian/"),
        ),
    ),
    "tags/index.html": (
        "Explore popular topics",
        (
            ("AIMA and artificial intelligence resources", "/aima-4e-persian/"),
            ("Software architecture resources", "/fundamentals-of-software-architecture-persian/"),
            ("Stremio streaming tools", "/persian-streams/"),
            ("Persian subtitle tools for Stremio", "/persian-subtitles/"),
            ("Obsidian and connected note-taking", "/posts/benefits-of-using-obsidian/"),
            ("All articles and project notes", "/posts/"),
        ),
    ),
    "posts/a-recap-of-last-year/index.html": (
        "Related reading",
        (
            ("Benefits of Using Obsidian", "/posts/benefits-of-using-obsidian/"),
            ("Browse all articles and project notes", "/posts/"),
            ("Browse content by category", "/categories/"),
            ("Explore topic tags", "/tags/"),
        ),
    ),
    "posts/benefits-of-using-obsidian/index.html": (
        "Related reading",
        (
            ("A Recap of Last Year", "/posts/a-recap-of-last-year/"),
            ("Browse all articles and project notes", "/posts/"),
            ("Browse content by category", "/categories/"),
            ("Explore topic tags", "/tags/"),
        ),
    ),
    "posts/aima-4e-persian/index.html": (
        "مسیرهای مرتبط با این ترجمه",
        (
            ("مستندات ترجمهٔ فارسی کتاب هوش مصنوعی AIMA", "/aima-4e-persian/"),
            ("مطالعهٔ آنلاین ترجمهٔ فارسی AIMA", "/aima-4e/"),
            ("معرفی ترجمهٔ فارسی مبانی معماری نرم‌افزار", "/posts/fundamentals-of-software-architecture-persian/"),
            ("همهٔ مقاله‌ها و یادداشت‌های پروژه", "/posts/"),
        ),
    ),
    "posts/fundamentals-of-software-architecture-persian/index.html": (
        "مسیرهای مرتبط با این ترجمه",
        (
            ("مستندات ترجمهٔ فارسی مبانی معماری نرم‌افزار", "/fundamentals-of-software-architecture-persian/"),
            ("مطالعهٔ آنلاین مبانی معماری نرم‌افزار", "/software-architecture/"),
            ("معرفی ترجمهٔ فارسی کتاب هوش مصنوعی AIMA", "/posts/aima-4e-persian/"),
            ("همهٔ مقاله‌ها و یادداشت‌های پروژه", "/posts/"),
        ),
    ),
    "aima-4e-persian/index.html": (
        "مطالب مرتبط با پروژهٔ AIMA",
        (
            ("مطالعهٔ آنلاین ترجمهٔ فارسی AIMA، ویرایش چهارم", "/aima-4e/"),
            ("معرفی و گزارش پروژهٔ ترجمهٔ فارسی AIMA", "/posts/aima-4e-persian/"),
            ("ترجمهٔ فارسی مبانی معماری نرم‌افزار", "/fundamentals-of-software-architecture-persian/"),
            ("حمایت از ادامهٔ ترجمه‌ها و پروژه‌های متن‌باز", "/support/"),
        ),
    ),
    "fundamentals-of-software-architecture-persian/index.html": (
        "مطالب مرتبط با کتاب معماری نرم‌افزار",
        (
            ("مطالعهٔ آنلاین مبانی معماری نرم‌افزار، ویرایش دوم", "/software-architecture/"),
            ("معرفی و گزارش پروژهٔ ترجمهٔ معماری نرم‌افزار", "/posts/fundamentals-of-software-architecture-persian/"),
            ("ترجمهٔ فارسی کتاب هوش مصنوعی AIMA", "/aima-4e-persian/"),
            ("حمایت از ادامهٔ ترجمه‌ها و پروژه‌های متن‌باز", "/support/"),
        ),
    ),
    "persian-streams/index.html": (
        "پروژه‌ها و مسیرهای مرتبط",
        (
            ("افزونهٔ زیرنویس فارسی برای Stremio", "/persian-subtitles/"),
            ("مقاله‌ها و یادداشت‌های فنی", "/posts/"),
            ("حمایت از توسعهٔ افزونه‌های متن‌باز", "/support/"),
        ),
    ),
    "persian-subtitles/index.html": (
        "پروژه‌ها و مسیرهای مرتبط",
        (
            ("افزونهٔ پخش فیلم و سریال ایرانی برای Stremio", "/persian-streams/"),
            ("مقاله‌ها و یادداشت‌های فنی", "/posts/"),
            ("حمایت از توسعهٔ افزونه‌های متن‌باز", "/support/"),
        ),
    ),
    "support/index.html": (
        "پروژه‌هایی که می‌توانید حمایت کنید",
        (
            ("ترجمهٔ فارسی مبانی معماری نرم‌افزار", "/fundamentals-of-software-architecture-persian/"),
            ("ترجمهٔ فارسی کتاب هوش مصنوعی AIMA", "/aima-4e-persian/"),
            ("افزونهٔ Persian Streams برای Stremio", "/persian-streams/"),
            ("افزونهٔ Persian Subtitles برای Stremio", "/persian-subtitles/"),
            ("Read the support page in English", "/en/support/"),
        ),
    ),
    "en/support/index.html": (
        "Projects your support sustains",
        (
            ("Persian translation of Fundamentals of Software Architecture", "/fundamentals-of-software-architecture-persian/"),
            ("Persian translation of Artificial Intelligence: A Modern Approach", "/aima-4e-persian/"),
            ("Persian Streams open-source Stremio add-on", "/persian-streams/"),
            ("Read the support page in Persian", "/support/"),
        ),
    ),
}

TARGET_LABELS = {
    "/aima-4e/": "کتاب هوش مصنوعی AIMA",
    "/aima-4e-persian/": "پروژهٔ ترجمهٔ فارسی AIMA",
    "/en/support/": "English support page",
    "/fundamentals-of-software-architecture-persian/": "پروژهٔ ترجمهٔ مبانی معماری نرم‌افزار",
    "/persian-streams/": "افزونهٔ Persian Streams",
    "/persian-subtitles/": "افزونهٔ Persian Subtitles",
    "/software-architecture/": "کتاب مبانی معماری نرم‌افزار",
    "/support/": "صفحهٔ حمایت فارسی",
}
AMBIGUOUS_LABELS = {
    "خواندن آنلاین",
    "مطالعه آنلاین",
    "مطالعه آنلاین (سایدبار)",
    "مستندات فارسی",
    "راهنمای نصب و مستندات",
    "کمک شما",
}

STYLE_BLOCK = """    <!-- internal-linking-styles:start -->
    <style>
    .site-breadcrumb{box-sizing:border-box;width:min(100%,72rem);margin:0 auto .75rem;padding:.65rem clamp(1rem,3vw,2rem);color:var(--text-muted,var(--text-secondary,#5f6368));font-size:.875rem;line-height:1.6;flex:0 0 auto}
    .site-breadcrumb ol{display:flex;flex-wrap:wrap;align-items:center;gap:.15rem .45rem;margin:0;padding:0;list-style:none}
    .site-breadcrumb li{display:inline-flex;align-items:center;min-width:0;overflow-wrap:anywhere}
    .site-breadcrumb li+li::before{content:"/";margin-inline-end:.45rem;color:var(--text-muted,var(--text-secondary,#777));opacity:.7}
    .site-breadcrumb a{color:var(--link-color,var(--accent,#1769aa));text-decoration-thickness:.08em;text-underline-offset:.16em}
    .site-breadcrumb [aria-current="page"]{font-weight:600;color:var(--text-color,var(--text-main,#30343b))}
    .reader-content>.site-breadcrumb{width:100%;margin:0;padding-block:.4rem;background:var(--card-bg,var(--reader-bg,#fff));border-bottom:1px solid var(--border-color,#ddd)}
    .related-content,.chapter-sequence{box-sizing:border-box;width:min(calc(100% - 2rem),56rem);margin:2rem auto;padding:1.25rem clamp(1rem,3vw,1.5rem);border:1px solid var(--border-color,#d9dde3);border-radius:.75rem;background:var(--card-bg,var(--content-bg,rgba(127,127,127,.04)));color:var(--text-color,var(--text-main,inherit))}
    .related-content h2,.chapter-sequence-title{margin:0 0 .85rem;font-size:1.2rem;font-weight:700;line-height:1.5}
    .related-content ul,.chapter-sequence ul{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:.65rem 1.25rem;margin:0;padding:0;list-style:none}
    .related-content li,.chapter-sequence li{margin:0;padding:0}
    .related-content a,.chapter-sequence a{display:inline-block;color:var(--link-color,var(--accent,#1769aa));font-weight:600;line-height:1.65;text-decoration-thickness:.08em;text-underline-offset:.18em;overflow-wrap:anywhere}
    .chapter-sequence .book-index a{color:var(--text-color,var(--text-main,#30343b))}
    .footer-nav .book-index{font-weight:700}
    #projects{scroll-margin-top:5rem}
    @media(max-width:600px){.site-breadcrumb{font-size:.82rem}.related-content,.chapter-sequence{width:calc(100% - 1rem);margin:1.25rem auto;padding:1rem}}
    </style>
    <!-- internal-linking-styles:end -->"""


class HeadFactsParser(HTMLParser):
    """Collect just enough head data to discover canonical indexable pages."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonicals: list[str] = []
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonicals.append(data.get("href", ""))
        elif tag.lower() == "meta" and data.get("name", "").lower() == "robots":
            self.noindex = "noindex" in data.get("content", "").lower()


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
    return next((path for path in candidates if path.is_file()), None)


def indexable_pages() -> dict[Path, str]:
    pages: dict[Path, str] = {}
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or "layouts" in path.parts:
            continue
        parser = HeadFactsParser()
        parser.feed(path.read_text(encoding="utf-8", errors="strict"))
        if parser.noindex or len(parser.canonicals) != 1:
            continue
        canonical = parser.canonicals[0]
        parsed = urllib.parse.urlparse(canonical)
        target = file_for_url(canonical)
        if (
            parsed.scheme == "https"
            and parsed.netloc == CANONICAL_HOST
            and target is not None
            and target.resolve() == path.resolve()
        ):
            pages[path] = canonical
    return pages


def relative_name(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def remove_marker(raw: str, marker: str) -> str:
    pattern = re.compile(
        rf"[ \t]*<!-- {re.escape(marker)}:start -->.*?<!-- {re.escape(marker)}:end -->[ \t]*(?:\r?\n)?",
        re.DOTALL,
    )
    return pattern.sub("", raw)


def plain_text(fragment: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", fragment)).split())


def set_tag_attribute(opening: str, name: str, value: str) -> str:
    escaped = html.escape(value, quote=True)
    pattern = re.compile(rf"\s+{re.escape(name)}\s*=\s*([\"']).*?\1", re.IGNORECASE | re.DOTALL)
    replacement = f' {name}="{escaped}"'
    if pattern.search(opening):
        return pattern.sub(replacement, opening, count=1)
    return f"{opening[:-1]}{replacement}>"


def contextualize_heading_permalinks(raw: str, english: bool) -> str:
    """Give Markdown's visible # permalinks a destination-specific name."""

    def replace_heading(match: re.Match[str]) -> str:
        body = match.group(3)

        def is_headerlink(anchor: re.Match[str]) -> bool:
            opening = anchor.group(1)
            return "headerlink" in opening.lower() and plain_text(anchor.group(2)) == "#"

        if not any(is_headerlink(anchor) for anchor in ANCHOR_RE.finditer(body)):
            return match.group(0)
        label_source = ANCHOR_RE.sub(lambda anchor: "" if is_headerlink(anchor) else anchor.group(0), body)
        label = plain_text(label_source)
        if not label:
            return match.group(0)
        accessible = f"Permanent link to section {label}" if english else f"پیوند مستقیم به بخش {label}"

        def replace_anchor(anchor: re.Match[str]) -> str:
            if not is_headerlink(anchor):
                return anchor.group(0)
            opening = set_tag_attribute(anchor.group(1), "title", accessible)
            opening = set_tag_attribute(opening, "aria-label", accessible)
            text = html.escape(accessible)
            return (
                f'{opening}<span class="sr-only">{text}</span>'
                f'<span aria-hidden="true">#</span>{anchor.group(3)}'
            )

        updated_body = ANCHOR_RE.sub(replace_anchor, body)
        return f"{match.group(1)}{updated_body}{match.group(4)}"

    return HEADING_RE.sub(replace_heading, raw)


def contextualize_ambiguous_anchors(raw: str, canonical: str, chapter_names: list[str]) -> str:
    """Retain compact visible CTAs while adding a precise destination name."""

    def replace(anchor: re.Match[str]) -> str:
        label = plain_text(anchor.group(2))
        if label not in AMBIGUOUS_LABELS:
            return anchor.group(0)
        href_match = HREF_RE.search(anchor.group(1))
        if href_match is None:
            return anchor.group(0)
        destination = urllib.parse.urlparse(
            urllib.parse.urljoin(canonical, html.unescape(href_match.group(2)).strip())
        )
        target_label = TARGET_LABELS.get(urllib.parse.unquote(destination.path))
        chapter_match = re.fullmatch(r"ch-item-(\d+)", urllib.parse.unquote(destination.fragment))
        if chapter_match and urllib.parse.unquote(destination.path) == "/software-architecture/":
            index = int(chapter_match.group(1))
            if index < len(chapter_names):
                target_label = f"{chapter_names[index]} از کتاب مبانی معماری نرم‌افزار"
        if not target_label:
            return anchor.group(0)
        suffix = f'<span class="sr-only">: {html.escape(target_label)}</span>'
        return f"{anchor.group(1)}{anchor.group(2)}{suffix}{anchor.group(3)}"

    return ANCHOR_RE.sub(replace, raw)


def enhance_aima_footer_navigation(raw: str, relative: str) -> str:
    """Reuse AIMA's native footer without duplicating its previous/next links."""
    footer_pattern = re.compile(
        r'<(?P<tag>div|nav)(?P<attrs>[^>]*\bclass=["\'][^"\']*\bfooter-nav\b[^"\']*["\'][^>]*)>'
        r'(?P<body>.*?)</(?P=tag)\s*>',
        re.IGNORECASE | re.DOTALL,
    )
    matches = list(footer_pattern.finditer(raw))
    if len(matches) != 1:
        raise ValueError(f"{relative}: expected one native AIMA footer navigation")
    match = matches[0]
    body = match.group("body")

    def add_relation(content: str, relation: str, value: str) -> str:
        pattern = re.compile(
            rf"(<strong>[^<]*فصل {value}:?</strong>\s*)(<a\b[^>]*>)",
            re.IGNORECASE,
        )
        return pattern.sub(
            lambda found: f'{found.group(1)}{set_tag_attribute(found.group(2), "rel", relation)}',
            content,
            count=1,
        )

    body = add_relation(body, "prev", "قبلی")
    body = add_relation(body, "next", "بعدی")

    hub = (
        "\n  <!-- internal-aima-book-hub:start -->\n"
        '  <p class="book-index"><a href="/aima-4e/">فهرست کامل کتاب هوش مصنوعی AIMA</a></p>\n'
        "  <!-- internal-aima-book-hub:end -->"
    )
    body, count = re.subn(r"(?=\s*<p><a\b[^>]*\bclass=[\"'][^\"']*\btop-link\b)", hub, body, count=1)
    if count != 1:
        raise ValueError(f"{relative}: AIMA footer has no back-to-top insertion point")
    opening = set_tag_attribute(f'<nav{match.group("attrs")}>', "aria-label", "پیمایش فصل‌های کتاب هوش مصنوعی")
    replacement = f"{opening}{body}</nav>"
    return f"{raw[:match.start()]}{replacement}{raw[match.end():]}"


def update_posts_archive(raw: str) -> str:
    """Keep both canonical Persian book articles visible in the Posts archive."""
    aima_pattern = re.compile(
        r'(<a\b[^>]*\bhref=["\'])/aima-4e-persian/(["\'][^>]*\bclass=["\'][^"\']*\barchive-item-link\b)',
        re.IGNORECASE,
    )
    raw, aima_count = aima_pattern.subn(
        r"\1/posts/aima-4e-persian/\2",
        raw,
        count=1,
    )
    normalized_aima = re.findall(
        r'<a\b[^>]*\bhref=["\']/posts/aima-4e-persian/["\'][^>]*\bclass=["\'][^"\']*\barchive-item-link\b',
        raw,
        flags=re.IGNORECASE,
    )
    if aima_count not in {0, 1} or len(normalized_aima) != 1:
        raise ValueError("posts/index.html: could not normalize the AIMA article archive link")

    entry = """<!-- internal-post-archive-entry:start -->
                    <article class="archive-item">
                        <a href="/posts/fundamentals-of-software-architecture-persian/" class="archive-item-link">مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن — ترجمهٔ فارسی</a>
                        <span class="archive-item-date">10-24</span>
                    </article>
                    <!-- internal-post-archive-entry:end -->"""
    year_pattern = re.compile(
        r'(<h2\b[^>]*\bclass=["\'][^"\']*\bgroup-title\b[^>]*>\s*2026\s*</h2>)',
        re.IGNORECASE,
    )
    raw, year_count = year_pattern.subn(rf"\1{entry}", raw, count=1)
    if year_count != 1:
        raise ValueError("posts/index.html: could not find the 2026 archive group")
    return raw


def schema_document(raw: str, relative: str) -> dict[str, Any]:
    matches = SCHEMA_RE.findall(raw)
    if len(matches) != 1:
        raise ValueError(f"{relative}: expected one managed JSON-LD graph")
    document = json.loads(matches[0])
    if not isinstance(document, dict) or not isinstance(document.get("@graph"), list):
        raise ValueError(f"{relative}: invalid managed JSON-LD graph")
    return document


def schema_node(document: dict[str, Any], node_type: str) -> dict[str, Any] | None:
    for node in document.get("@graph", []):
        types = node.get("@type", [])
        if isinstance(types, str):
            types = [types]
        if node_type in types:
            return node
    return None


def href_for_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc not in {CANONICAL_HOST, "alirostami.com"}:
        raise ValueError(f"breadcrumb item is not an internal URL: {url}")
    href = parsed.path or "/"
    if parsed.query:
        href += f"?{parsed.query}"
    if parsed.fragment:
        href += f"#{parsed.fragment}"
    return href


def breadcrumb_items(document: dict[str, Any], relative: str) -> list[dict[str, Any]]:
    node = schema_node(document, "BreadcrumbList")
    if node is None:
        if relative == "index.html":
            return []
        raise ValueError(f"{relative}: JSON-LD breadcrumb is missing")
    elements = node.get("itemListElement")
    if not isinstance(elements, list) or len(elements) < 2:
        raise ValueError(f"{relative}: JSON-LD breadcrumb is incomplete")
    return elements


def render_breadcrumb(items: list[dict[str, Any]], english: bool) -> str:
    label = "Breadcrumb trail" if english else "مسیر راهنما"
    lines = [
        "    <!-- internal-breadcrumb:start -->",
        f'    <nav class="site-breadcrumb" aria-label="{label}">',
        "      <ol>",
    ]
    for index, item in enumerate(items):
        name = html.escape(str(item.get("name", "")).strip())
        url = str(item.get("item", "")).strip()
        if not name or not url:
            raise ValueError("breadcrumb item requires a name and URL")
        if index == len(items) - 1:
            lines.append(f'        <li aria-current="page"><span>{name}</span></li>')
        else:
            href = html.escape(href_for_url(url), quote=True)
            lines.append(f'        <li><a href="{href}">{name}</a></li>')
    lines.extend(
        (
            "      </ol>",
            "    </nav>",
            "    <!-- internal-breadcrumb:end -->",
        )
    )
    return "\n".join(lines)


def render_related(heading: str, links: tuple[tuple[str, str], ...]) -> str:
    lines = [
        "    <!-- internal-related:start -->",
        '    <section class="related-content" aria-labelledby="related-resources-title">',
        f'      <h2 id="related-resources-title">{html.escape(heading)}</h2>',
        "      <ul>",
    ]
    for label, href in links:
        lines.append(
            f'        <li><a href="{html.escape(href, quote=True)}">{html.escape(label)}</a></li>'
        )
    lines.extend(("      </ul>", "    </section>", "    <!-- internal-related:end -->"))
    return "\n".join(lines)


def chapter_groups(
    pages: dict[Path, str], documents: dict[str, dict[str, Any]]
) -> dict[str, list[tuple[float, str, str, str]]]:
    groups: dict[str, list[tuple[float, str, str, str]]] = {"aima-4e": [], "software-architecture": []}
    for path, canonical in pages.items():
        relative = relative_name(path)
        root = next((value for value in groups if relative.startswith(f"{value}/") and relative != f"{value}/index.html"), None)
        if root is None:
            continue
        chapter = schema_node(documents[relative], "Chapter")
        if chapter is None:
            continue
        position = chapter.get("position")
        try:
            order = float(position)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{relative}: Chapter.position is invalid") from error
        name = str(chapter.get("name", "")).strip()
        if not name:
            raise ValueError(f"{relative}: Chapter.name is missing")
        groups[root].append((order, relative, canonical, name))
    for root in groups:
        groups[root].sort(key=lambda item: (item[0], item[1]))
    return groups


def render_chapter_navigation(
    root: str,
    current_index: int,
    chapters: list[tuple[float, str, str, str]],
) -> str:
    _order, _relative, _canonical, _name = chapters[current_index]
    links: list[tuple[str, str, str]] = []
    if current_index > 0:
        previous = chapters[current_index - 1]
        links.append((f"فصل قبلی: {previous[3]}", href_for_url(previous[2]), "prev"))
    book_label = (
        "فهرست کامل کتاب هوش مصنوعی AIMA"
        if root == "aima-4e"
        else "فهرست کامل کتاب مبانی معماری نرم‌افزار"
    )
    links.append((book_label, f"/{root}/", ""))
    if current_index + 1 < len(chapters):
        following = chapters[current_index + 1]
        links.append((f"فصل بعدی: {following[3]}", href_for_url(following[2]), "next"))

    lines = [
        "    <!-- internal-chapter-navigation:start -->",
        '    <nav class="chapter-sequence" aria-labelledby="chapter-navigation-title">',
        '      <p class="chapter-sequence-title" id="chapter-navigation-title">ادامهٔ مطالعه</p>',
        "      <ul>",
    ]
    for label, href, relation in links:
        class_name = ' class="book-index"' if not relation else ""
        rel = f' rel="{relation}"' if relation else ""
        lines.append(
            f'        <li{class_name}><a href="{html.escape(href, quote=True)}"{rel}>{html.escape(label)}</a></li>'
        )
    lines.extend(("      </ul>", "    </nav>", "    <!-- internal-chapter-navigation:end -->"))
    return "\n".join(lines)


def insert_before_closing_main(raw: str, block: str, relative: str) -> str:
    matches = list(MAIN_END_RE.finditer(raw))
    if not matches:
        raise ValueError(f"{relative}: page has no main element")
    match = matches[-1]
    return f"{raw[:match.start()].rstrip()}\n{block}\n    {raw[match.start():]}"


def update_page(
    raw: str,
    relative: str,
    canonical: str,
    document: dict[str, Any],
    chapter_navigation: str | None,
    software_chapter_names: list[str],
) -> str:
    for marker in MARKERS:
        raw = remove_marker(raw, marker)

    language_match = re.search(r"<html\b[^>]*\blang=[\"']([^\"']+)", raw, re.IGNORECASE)
    english = bool(language_match and language_match.group(1).lower().startswith("en"))
    raw = contextualize_heading_permalinks(raw, english)
    raw = contextualize_ambiguous_anchors(raw, canonical, software_chapter_names)
    if relative.startswith("aima-4e/") and relative != "aima-4e/index.html":
        raw = enhance_aima_footer_navigation(raw, relative)
    if relative == "posts/index.html":
        raw = update_posts_archive(raw)

    # Phase-5 breadcrumbs use /#projects as the parent for project and reader
    # pages. Make that route a real, stable jump target at the first project.
    if relative == "index.html" and not re.search(r'\bid=["\']projects["\']', raw, re.IGNORECASE):
        raw, count = re.subn(
            r'(<article\b)(?=[^>]*\bclass=["\'][^"\']*\bsummary\b)',
            r'\1 id="projects"',
            raw,
            count=1,
            flags=re.IGNORECASE,
        )
        if count != 1:
            raise ValueError("index.html: could not create the #projects jump target")

    # Keep managed styles immediately before the accessibility layer. Falling
    # back to </head> also supports a newly generated page before Phase 4 runs.
    accessibility = re.search(
        r"^[ \t]*<!-- accessibility-styles:start -->",
        raw,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if accessibility is not None:
        raw = f"{raw[:accessibility.start()].rstrip()}\n{STYLE_BLOCK}\n{raw[accessibility.start():].lstrip(chr(10) + chr(13))}"
    else:
        head_end = HEAD_END_RE.search(raw)
        if head_end is None:
            raise ValueError(f"{relative}: page has no head element")
        raw = f"{raw[:head_end.start()].rstrip()}\n{STYLE_BLOCK}\n{raw[head_end.start():]}"

    items = breadcrumb_items(document, relative)
    if items:
        main = MAIN_START_RE.search(raw)
        if main is None:
            raise ValueError(f"{relative}: page has no main element")
        block = render_breadcrumb(items, english)
        raw = f"{raw[:main.end()]}\n{block}\n{raw[main.end():].lstrip(chr(10) + chr(13))}"

    if relative in RELATED_CONTENT:
        raw = insert_before_closing_main(raw, render_related(*RELATED_CONTENT[relative]), relative)
    if chapter_navigation is not None:
        raw = insert_before_closing_main(raw, chapter_navigation, relative)

    raw = re.sub(r"[ \t]+$", "", raw, flags=re.MULTILINE)
    return raw


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated internal navigation is stale")
    arguments = parser.parse_args()

    pages = indexable_pages()
    documents: dict[str, dict[str, Any]] = {}
    source: dict[str, str] = {}
    for path in pages:
        relative = relative_name(path)
        source[relative] = path.read_text(encoding="utf-8", errors="strict")
        documents[relative] = schema_document(source[relative], relative)

    groups = chapter_groups(pages, documents)
    chapter_blocks: dict[str, str] = {}
    for root, chapters in groups.items():
        if root != "software-architecture":
            continue
        for index, (_order, relative, _canonical, _name) in enumerate(chapters):
            chapter_blocks[relative] = render_chapter_navigation(root, index, chapters)

    software_chapter_names = [record[3] for record in groups["software-architecture"]]
    changed: list[str] = []
    for path in sorted(pages):
        relative = relative_name(path)
        updated = update_page(
            source[relative],
            relative,
            pages[path],
            documents[relative],
            chapter_blocks.get(relative),
            software_chapter_names,
        )
        if updated != source[relative]:
            changed.append(relative)
            if not arguments.check:
                path.write_text(updated, encoding="utf-8")

    if arguments.check and changed:
        preview = ", ".join(changed[:8])
        suffix = " …" if len(changed) > 8 else ""
        print(f"internal linking is stale in {len(changed)} files: {preview}{suffix}", file=sys.stderr)
        raise SystemExit(1)

    action = "would update" if arguments.check else "updated"
    print(f"internal linking {action}: {len(changed)} HTML files")
    print(
        f"crawl architecture covered: {len(pages)} indexable pages, "
        f"{sum(len(value) for value in groups.values())} book chapters, "
        f"{len(RELATED_CONTENT)} discovery sections"
    )


if __name__ == "__main__":
    main()
