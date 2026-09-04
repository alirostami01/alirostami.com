#!/usr/bin/env python3
"""Render the project documentation pages from Markdown into the site theme.

Source:  content/<slug>.md
Output:  <URL path>/index.html  (plus a lowercase alias so a mistyped URL works)

Usage:
    pip install markdown
    python3 scripts/build-project-page.py
"""

import re
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

import theme

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = "https://alirostami.com"

PAGES = [
    {
        "source": "persian-subtitles.md",
        "path": "Persian-Subtitles",
        "aliases": ["persian-subtitles"],
        "title": "Persian Subtitles — افزونهٔ زیرنویس فارسی استرمیو",
        "description": (
            "مستندات Persian Subtitles: افزونهٔ غیررسمی Stremio برای زیرنویس فارسی "
            "فیلم و سریال با اتصال به API سرویس SubSource؛ نصب، پیکربندی، استقرار و عیب‌یابی."
        ),
        "icon": "/images/projects/persian-subtitles.png",
        "repo": "https://github.com/alirostami01/Persian-Subtitles",
    },
]

STYLE = """
    /* keep the theme header/footer in their original LTR layout */
    #header-desktop, #header-mobile, .footer { direction: ltr; }

    .docs-page { direction: rtl; text-align: right; }
    .docs-page .content { line-height: 2.1; }

    /* ---- page head ---- */
    .docs-page .docs-hero {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0 .5rem;
    }
    .docs-page .docs-hero img {
        width: 84px;
        height: 84px;
        flex: 0 0 84px;
        border-radius: 50%;
        filter: drop-shadow(0 .2rem .5rem rgba(0,0,0,.25));
    }
    .docs-page .docs-hero .single-title { margin: 0; text-align: right; }
    .docs-page .docs-hero .docs-hero-sub { font-size: .9rem; opacity: .7; margin: .25rem 0 0; }
    .docs-page .docs-actions {
        display: flex;
        flex-wrap: wrap;
        gap: .6rem;
        margin: 0 0 1.5rem;
    }
    .docs-page .docs-actions a {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        font-size: .85rem;
        line-height: 1.6;
        padding: .4rem 1rem;
        border-radius: 2rem;
        border: 1px solid rgba(128,128,128,.35);
        transition: background .2s ease, border-color .2s ease;
    }
    .docs-page .docs-actions a:hover { background: rgba(45,150,189,.12); border-color: #2d96bd; }
    .docs-page .docs-actions a.primary {
        background: linear-gradient(135deg, #e5405e, #ff7a5c);
        border-color: transparent;
        color: #fff;
        font-weight: 700;
    }
    .docs-page .docs-actions a.primary:hover { filter: brightness(1.08); color: #fff; }

    /* ---- table of contents ---- */
    .docs-page .docs-toc {
        background: rgba(128,128,128,.07);
        border: 1px solid rgba(128,128,128,.2);
        border-radius: .8rem;
        padding: 1rem 1.2rem;
        margin: 0 0 2rem;
    }
    [theme=dark] .docs-page .docs-toc { background: rgba(255,255,255,.04); }
    .docs-page .docs-toc > .docs-toc-title {
        font-weight: 700;
        margin-bottom: .4rem;
        display: flex;
        align-items: center;
        gap: .5rem;
    }
    .docs-page .docs-toc ul {
        list-style: none;
        padding: 0;
        margin: 0;
        columns: 2;
        column-gap: 1.5rem;
    }
    .docs-page .docs-toc ul ul { display: none; }
    .docs-page .docs-toc li { padding: .15rem 0; break-inside: avoid; }
    @media only screen and (max-width: 680px) {
        .docs-page .docs-toc ul { columns: 1; }
        .docs-page .docs-hero { flex-direction: column; text-align: center; }
        .docs-page .docs-hero .single-title { text-align: center; }
    }

    /* ---- headings ---- */
    .docs-page .content h2 {
        margin: 2.8rem 0 1rem;
        padding-bottom: .5rem;
        border-bottom: 1px solid rgba(128,128,128,.25);
    }
    .docs-page .content h3 { margin: 2rem 0 .8rem; }
    .docs-page .content h2 a.headerlink,
    .docs-page .content h3 a.headerlink {
        font-size: .8rem;
        opacity: 0;
        margin-right: .4rem;
        transition: opacity .2s ease;
    }
    .docs-page .content h2:hover a.headerlink,
    .docs-page .content h3:hover a.headerlink { opacity: .5; }

    /* ---- lists ---- */
    .docs-page .content ul,
    .docs-page .content ol { padding-right: 1.6rem; padding-left: 0; }
    .docs-page .content li { margin: .3rem 0; }

    /* ---- code: always LTR ---- */
    .docs-page .content pre,
    .docs-page .content pre code,
    .docs-page .content code {
        direction: ltr;
        unicode-bidi: isolate;
    }
    .docs-page .content pre {
        display: block;
        overflow-x: auto;
        text-align: left;
        padding: .8rem 1rem;
        border-radius: .5rem;
        font-size: .82rem;
        line-height: 1.7;
        border: 1px solid rgba(128,128,128,.2);
    }
    .docs-page .content pre code {
        display: block;
        white-space: pre;
        padding: 0;
        font-size: inherit;
        line-height: inherit;
    }
    .docs-page .content p > code,
    .docs-page .content li > code,
    .docs-page .content td code { font-size: .8rem; }

    /* ---- tables ---- */
    .docs-page .content .table-wrapper > table { text-align: right; }
    .docs-page .content .table-wrapper > table th,
    .docs-page .content .table-wrapper > table td { vertical-align: top; line-height: 1.9; }
    .docs-page .content .table-wrapper > table th { text-align: right; }

    /* ---- blockquote as a note box (RTL border side) ---- */
    .docs-page .content blockquote {
        border-left: none;
        border-right: .35rem solid #6bd6fd;
        padding: .6rem 1rem;
        border-radius: .4rem;
    }
    [theme=dark] .docs-page .content blockquote { border-right-color: #59c5ec; }
    .docs-page .content blockquote p { margin: .3rem 0; }

    .docs-page .content hr { margin: 2rem 0; }
"""


def wrap_tables(html: str) -> str:
    """LoveIt styles tables only inside .table-wrapper (and it enables scrolling)."""
    return re.sub(
        r"<table>(.*?)</table>",
        lambda m: f'<div class="table-wrapper"><table>{m.group(1)}</table></div>',
        html,
        flags=re.S,
    )


def build(spec: dict) -> str:
    md_text = (CONTENT / spec["source"]).read_text(encoding="utf-8")

    # the first heading becomes the page hero, the rest is the article body
    lines = md_text.splitlines()
    assert lines[0].startswith("# ")
    heading = lines[0][2:].strip()
    md_body = "\n".join(lines[1:]).lstrip("\n")

    converter = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "nl2br"],
        extension_configs={
            "toc": {
                "permalink": "#",
                "toc_depth": "2-2",
                "slugify": slugify_unicode,
            }
        },
    )
    body_html = wrap_tables(converter.convert(md_body))
    toc_html = converter.toc

    canonical = f"{SITE}/{spec['path']}/"
    hero = f"""<div class="docs-hero">
            <img src="{spec['icon']}" alt="لوگوی {heading}" width="84" height="84" decoding="async">
            <div>
                <h1 class="single-title animate__animated animate__flipInX">{heading}</h1>
                <p class="docs-hero-sub">مستندات پروژه · افزونهٔ غیررسمی Stremio</p>
            </div>
        </div>
        <div class="docs-actions">
            <a class="primary" href="/support/"><i class="fas fa-heart fa-fw" aria-hidden="true"></i> حمایت از پروژه</a>
            <a href="{spec['repo']}" target="_blank" rel="noopener noreferrer"><i class="fab fa-github fa-fw" aria-hidden="true"></i> مخزن گیت‌هاب</a>
        </div>
        <nav class="docs-toc" aria-label="فهرست مطالب">
            <div class="docs-toc-title"><i class="fas fa-list-ul fa-fw" aria-hidden="true"></i> فهرست مطالب</div>
            {toc_html}
        </nav>"""

    article = f"""<article class="page single docs-page">
        {hero}
        <div class="content" id="content">
{body_html}
        </div>
    </article>"""

    return theme.page(
        title=spec["title"],
        description=spec["description"],
        canonical=canonical,
        body=article,
        style=STYLE,
        og_type="article",
    )


def main() -> None:
    for spec in PAGES:
        html = build(spec)
        for rel in [spec["path"], *spec.get("aliases", [])]:
            out = ROOT / rel / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            print(f"wrote {rel}/index.html ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
