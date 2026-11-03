#!/usr/bin/env python3
"""Build the book reader index (aima-4e/index.html) and inject reader helpers.

Features:
- Responsive documentation reader layout (GitBook/VitePress style, fully RTL).
- Independent scrollable sidebar with search & accordion (chapters and sub-sections).
- Interactive iframe reader with URL-hash sync and deep-linking to #sec-...
- Dark/Light theme synchronization with the site LoveIt theme.
- Keyboard navigation (prev/next chapter).
- Top navigation pill injected into chapter files so direct visits can return to sidebar.
"""

import glob
import html as html_lib
import json
import os
import re
from pathlib import Path

from image_utils import apply_site_postprocessors

ROOT = Path(__file__).resolve().parent.parent
AIMA_DIR = ROOT / "aima-4e"


def extract_chapters():
    files = sorted(glob.glob(str(AIMA_DIR / "*.html")))
    chapters = []

    for fpath in files:
        fname = os.path.basename(fpath)
        if fname == "index.html":
            continue

        with open(fpath, "r", encoding="utf-8") as fp:
            html = fp.read()

        title_m = re.search(r"<title>(.*?)</title>", html)
        title = title_m.group(1).strip() if title_m else fname

        subtitle_m = re.search(r'<p class="subtitle">(.*?)</p>', html)
        subtitle = subtitle_m.group(1).strip() if subtitle_m else ""

        badge_m = re.search(r'<span class="badge gold">(.*?)</span>', html)
        badge = badge_m.group(1).strip() if badge_m else ""
        if not badge:
            if "00-" in fname:
                badge = "پیشگفتار"
            else:
                num_m = re.search(r"(\d+)", fname)
                badge = f"فصل {int(num_m.group(1))}" if num_m else ""

        toc_m = re.search(
            r'<nav\b[^>]*class=["\'][^"\']*\btoc\b[^"\']*["\'][^>]*>(.*?)</nav>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        sections = []
        if toc_m:
            for href, text in re.findall(r'<a href="([^"]+)">([^<]+)</a>', toc_m.group(1)):
                sections.append({
                    "href": href.strip(),
                    "title": text.strip()
                })

        # Clean title for sidebar
        short_title = title
        if " — " in title:
            parts = title.split(" — ")
            short_title = parts[1]

        chapters.append({
            "filename": fname,
            "route": Path(fname).stem,
            "title": title,
            "short_title": short_title,
            "subtitle": subtitle,
            "badge": badge,
            "sections": sections
        })

    return chapters


def generate_index_html(chapters):
    chapters_json = json.dumps(chapters, ensure_ascii=False)

    # Generate sidebar items HTML
    sidebar_items_html = []
    for idx, ch in enumerate(chapters):
        ch_id = f"ch-item-{idx}"
        badge_html = f'<span class="ch-badge">{ch["badge"]}</span>' if ch["badge"] else ""

        sections_html = []
        for sec in ch["sections"]:
            sec_href = f"{ch['route']}{sec['href']}"
            sections_html.append(
                f'<li class="sec-item">'
                f'<a href="{sec_href}" data-ch-idx="{idx}" data-file="{ch["route"]}" data-hash="{sec["href"]}" class="sec-link">'
                f'<span class="sec-dot"></span><span class="sec-text">{sec["title"]}</span>'
                f'</a></li>'
            )

        sections_ul = f'<ul class="ch-sections" id="sections-{idx}">{"".join(sections_html)}</ul>' if sections_html else ""
        chapter_label = html_lib.escape(ch["short_title"], quote=True)
        chevron = (
            f'<button type="button" class="ch-chevron" aria-expanded="false" '
            f'aria-controls="sections-{idx}" aria-label="نمایش بخش‌های {chapter_label}">'
            f'<i class="fas fa-chevron-left" aria-hidden="true"></i></button>'
            if sections_html
            else ""
        )

        sidebar_items_html.append(f"""
        <div class="ch-card" id="{ch_id}" data-idx="{idx}" data-file="{ch['route']}">
            <div class="ch-header" data-idx="{idx}">
                <a href="{ch['route']}" class="ch-title-link" data-idx="{idx}" data-file="{ch['route']}">
                    {badge_html}
                    <span class="ch-title">{ch['short_title']}</span>
                </a>
                {chevron}
            </div>
            {sections_ul}
        </div>
        """)

    sidebar_content = "\n".join(sidebar_items_html)

    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="index, follow">
    <script>
        // Prevent iframe recursion: index.html should never be inside an iframe!
        if (window.self !== window.top) {{
            window.top.location = window.location.href;
        }}
    </script>
    <title>هوش مصنوعی: رویکردی نوین (AIMA 4e) — مطالعه آنلاین با فهرست و سایدبار</title>
    <meta name="Description" content="نسخهٔ وب و مطالعهٔ آنلاین ترجمهٔ فارسی کتاب هوش مصنوعی: یک رویکرد مدرن (ویرایش چهارم) اثر استوارت راسل و پیتر نورویگ با سایدبار، فهرست کامل فصول و زیرفصل‌ها.">
    <meta property="og:title" content="هوش مصنوعی: رویکردی نوین (AIMA 4e) — مطالعه آنلاین کتاب">
    <meta property="og:description" content="مطالعه آنلاین ترجمه فارسی کتاب هوش مصنوعی ویرایش چهارم تالیف راسل و نورویگ با سایدبار کامل، فصول ۲۸گانه و جستجوی مباحث.">
    <meta property="og:type" content="book">
    <meta property="og:url" content="https://www.alirostami.com/aima-4e/">
    <link rel="canonical" href="https://www.alirostami.com/aima-4e/">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
    <link rel="stylesheet" href="/css/style.min.css">
    <!-- performance-icons:start -->
    <style>.fa,.fas,.far,.fab,.fa-solid,.fa-regular,.fa-brands{{display:inline-block;min-width:1em;text-align:center}}.fa-fw{{width:1.25em}}</style>
    <link rel="preload" href="/lib/fontawesome/all.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="/lib/fontawesome/all.min.css"></noscript>
    <!-- performance-icons:end -->
    <script type="application/ld+json">
{{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "Book",
                "@id": "https://www.alirostami.com/aima-4e/#book",
                "name": "هوش مصنوعی: رویکردی نوین (ویرایش چهارم)",
                "alternateName": "Artificial Intelligence: A Modern Approach (AIMA 4th Edition)",
                "author": [
                    {{"@type": "Person", "name": "Stuart Russell"}},
                    {{"@type": "Person", "name": "Peter Norvig"}}
                ],
                "translator": {{
                    "@type": "Person",
                    "name": "علی رستمی",
                    "url": "https://www.alirostami.com/"
                }},
                "inLanguage": "fa",
                "bookFormat": "https://schema.org/EBook",
                "url": "https://www.alirostami.com/aima-4e/",
                "description": "نسخه وب و مطالعه آنلاین ترجمه کامل فارسی کتاب هوش مصنوعی: رویکردی نوین ویرایش چهارم تالیف راسل و نورویگ با سایدبار هوشمند، فهرست فصول و امکان جستجو."
            }},
            {{
                "@type": "BreadcrumbList",
                "@id": "https://www.alirostami.com/aima-4e/#breadcrumb",
                "itemListElement": [
                    {{
                        "@type": "ListItem",
                        "position": 1,
                        "name": "خانه",
                        "item": "https://www.alirostami.com/"
                    }},
                    {{
                        "@type": "ListItem",
                        "position": 2,
                        "name": "پروژه‌ها",
                        "item": "https://www.alirostami.com/#projects"
                    }},
                    {{
                        "@type": "ListItem",
                        "position": 3,
                        "name": "مطالعه آنلاین کتاب هوش مصنوعی",
                        "item": "https://www.alirostami.com/aima-4e/"
                    }}
                ]
            }}
        ]
    }}
</script>
    <style>
        :root {{
            --sidebar-width: 340px;
            --top-header-height: 56px;
            --reader-bg: #f8fafc;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --accent: #2563eb;
            --accent-soft: #eff6ff;
            --wine: #8b2942;
        }}
        [theme=dark] {{
            --reader-bg: #0b1120;
            --card-bg: #1e293b;
            --border-color: #334155;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-soft: rgba(56, 189, 248, 0.12);
            --wine: #fb7185;
        }}
        * {{ box-sizing: border-box; }}
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            font-family: Vazirmatn, "Segoe UI", Tahoma, sans-serif;
            background-color: var(--reader-bg);
            color: var(--text-main);
            direction: rtl;
        }}

        /* Header */
        .reader-header {{
            height: var(--top-header-height);
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 1rem;
            position: relative;
            z-index: 40;
        }}
        .header-brand-group {{
            display: flex;
            align-items: center;
            gap: .5rem;
        }}
        .btn-home-return {{
            display: inline-flex;
            align-items: center;
            gap: .35rem;
            padding: .35rem .65rem;
            border-radius: 6px;
            font-size: .82rem;
            font-weight: 600;
            text-decoration: none;
            color: var(--accent);
            background: var(--accent-soft);
            border: 1px solid rgba(56, 189, 248, 0.25);
            transition: all .2s;
            white-space: nowrap;
        }}
        .btn-home-return:hover {{
            background: var(--accent);
            color: #fff;
        }}
        .brand-divider {{
            color: var(--text-muted);
            opacity: .4;
            font-size: .9rem;
            margin: 0 .15rem;
        }}
        .header-brand {{
            display: flex;
            align-items: center;
            gap: .5rem;
            text-decoration: none;
            color: var(--text-main);
            font-weight: 700;
            font-size: 1.02rem;
            white-space: nowrap;
        }}
        .header-brand .book-icon {{
            color: var(--accent);
            font-size: 1.25rem;
        }}
        .header-brand-badge {{
            font-size: .75rem;
            font-weight: 600;
            color: var(--accent);
            background: var(--accent-soft);
            padding: .15rem .45rem;
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.2);
            letter-spacing: .5px;
            margin-right: .3rem;
        }}
        .header-actions {{
            display: flex;
            align-items: center;
            gap: .5rem;
        }}
        .btn-header {{
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            padding: .4rem .75rem;
            border-radius: 6px;
            font-size: .85rem;
            text-decoration: none;
            color: var(--text-muted);
            background: transparent;
            border: 1px solid transparent;
            transition: all .2s;
            cursor: pointer;
        }}
        .btn-header:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: var(--border-color);
        }}
        .btn-header.primary {{
            background: var(--accent);
            color: #fff;
        }}
        .btn-header.primary:hover {{
            filter: brightness(1.1);
        }}
        .mobile-toggle {{
            display: none;
        }}

        /* App Workspace */
        .reader-workspace {{
            display: flex;
            height: calc(100vh - var(--top-header-height));
            overflow: hidden;
            position: relative;
        }}

        /* Sidebar */
        .reader-sidebar {{
            width: var(--sidebar-width);
            min-width: var(--sidebar-width);
            background: var(--card-bg);
            border-left: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            height: 100%;
            z-index: 30;
            transition: transform .3s ease;
        }}
        .sidebar-search-box {{
            padding: .75rem;
            border-bottom: 1px solid var(--border-color);
            background: var(--card-bg);
        }}
        .search-wrapper-inner {{
            position: relative;
            display: flex;
            align-items: center;
        }}
        .search-wrapper-inner i {{
            position: absolute;
            right: .75rem;
            color: var(--text-muted);
            font-size: .85rem;
        }}
        .search-input {{
            width: 100%;
            padding: .5rem 2.2rem .5rem .75rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background: var(--reader-bg);
            color: var(--text-main);
            font-family: inherit;
            font-size: .85rem;
            outline: none;
            transition: border-color .2s;
        }}
        .search-input:focus {{
            border-color: var(--accent);
        }}
        .sidebar-controls {{
            padding: .4rem .75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: .78rem;
            border-bottom: 1px solid var(--border-color);
            background: rgba(128,128,128,.03);
        }}
        .sidebar-controls .sidebar-action {{
            appearance: none;
            border: 0;
            padding: 0;
            background: transparent;
            color: var(--text-muted);
            font: inherit;
            text-decoration: none;
            cursor: pointer;
        }}
        .sidebar-controls .sidebar-action:hover {{
            color: var(--accent);
        }}
        .sidebar-scroll {{
            flex: 1;
            overflow-y: auto;
            padding: .5rem;
            scrollbar-width: thin;
        }}

        /* Chapter items */
        .ch-card {{
            margin-bottom: .35rem;
            border-radius: 8px;
            border: 1px solid transparent;
            transition: background .15s, border-color .15s;
        }}
        .ch-card:hover {{
            background: var(--accent-soft);
        }}
        .ch-card.active {{
            background: var(--accent-soft);
            border-color: var(--accent);
        }}
        .ch-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: .45rem .6rem;
            cursor: pointer;
            user-select: none;
        }}
        .ch-title-link {{
            display: flex;
            align-items: center;
            gap: .5rem;
            text-decoration: none;
            color: var(--text-main);
            flex: 1;
            font-size: .88rem;
            font-weight: 500;
        }}
        .ch-card.active .ch-title-link {{
            color: var(--accent);
            font-weight: 700;
        }}
        .ch-badge {{
            font-size: .72rem;
            padding: .15rem .45rem;
            border-radius: 999px;
            background: rgba(128,128,128,.15);
            color: var(--text-muted);
            white-space: nowrap;
        }}
        .ch-card.active .ch-badge {{
            background: var(--accent);
            color: #fff;
        }}
        .ch-chevron {{
            appearance: none;
            border: 0;
            background: transparent;
            font: inherit;
            font-size: .75rem;
            color: var(--text-muted);
            cursor: pointer;
            transition: transform .25s ease;
            padding: .2rem .4rem;
        }}
        .ch-card.expanded .ch-chevron {{
            transform: rotate(-90deg);
        }}
        .ch-sections {{
            list-style: none;
            margin: 0;
            padding: .2rem .75rem .4rem 1.5rem;
            display: none;
            border-right: 2px solid var(--border-color);
            margin-right: 1.2rem;
        }}
        .ch-card.expanded .ch-sections {{
            display: block;
        }}
        .sec-item {{
            margin: .25rem 0;
        }}
        .sec-link {{
            display: flex;
            align-items: baseline;
            gap: .4rem;
            color: var(--text-muted);
            text-decoration: none;
            font-size: .82rem;
            line-height: 1.5;
            padding: .2rem .35rem;
            border-radius: 4px;
            transition: all .15s;
        }}
        .sec-link:hover {{
            color: var(--accent);
            background: rgba(128,128,128,.08);
        }}
        .sec-link.active {{
            color: var(--accent);
            font-weight: 600;
            background: rgba(128,128,128,.12);
        }}
        .sec-dot {{
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: var(--text-muted);
            flex-shrink: 0;
            transform: translateY(-2px);
        }}
        .sec-link.active .sec-dot {{
            background: var(--accent);
        }}

        /* Main Reader Frame */
        .reader-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
            background: var(--reader-bg);
        }}
        .reader-toolbar {{
            height: 44px;
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 .75rem;
            font-size: .85rem;
        }}
        .toolbar-title {{
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: .5rem;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }}
        .toolbar-nav {{
            display: flex;
            align-items: center;
            gap: .3rem;
        }}
        .btn-tool {{
            display: inline-flex;
            align-items: center;
            gap: .3rem;
            padding: .25rem .55rem;
            border-radius: 6px;
            font-size: .8rem;
            text-decoration: none;
            color: var(--text-muted);
            border: 1px solid var(--border-color);
            background: var(--card-bg);
            cursor: pointer;
            transition: all .15s;
        }}
        .btn-tool:hover:not(:disabled) {{
            color: var(--accent);
            border-color: var(--accent);
        }}
        .btn-tool:disabled {{
            opacity: .4;
            cursor: not-allowed;
        }}

        .frame-container {{
            flex: 1;
            width: 100%;
            height: calc(100% - 44px);
            position: relative;
            background: var(--reader-bg);
        }}
        #book-frame {{
            width: 100%;
            height: 100%;
            border: 0;
            display: block;
            background: transparent;
        }}

        /* Mobile drawer overlay */
        .sidebar-backdrop {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,.5);
            z-index: 25;
            opacity: 0;
            transition: opacity .3s ease;
        }}

        @media (max-width: 900px) {{
            .mobile-toggle {{
                display: inline-flex !important;
            }}
            .header-brand-badge {{
                display: none;
            }}
            .reader-sidebar {{
                position: fixed;
                top: var(--top-header-height);
                bottom: 0;
                right: 0;
                transform: translateX(100%);
                box-shadow: -4px 0 20px rgba(0,0,0,.15);
            }}
            .reader-sidebar.open {{
                transform: translateX(0);
            }}
            .sidebar-backdrop.open {{
                display: block;
                opacity: 1;
            }}
        }}
        @media (max-width: 600px) {{
            .header-brand .brand-title-text {{
                display: none;
            }}
            .brand-divider {{
                display: none;
            }}
        }}
    </style>
</head>
<body data-theme="light">
<script>
    (function() {{
        var t = localStorage.getItem('theme');
        if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.body.setAttribute('theme', 'dark');
            document.body.setAttribute('data-theme', 'dark');
        }}
    }})();
</script>

<header class="reader-header">
    <div style="display:flex;align-items:center;gap:.6rem;">
        <button type="button" class="btn-header mobile-toggle" id="btn-toggle-sidebar" title="فهرست و سایدبار" aria-label="باز کردن فهرست فصول" aria-controls="reader-sidebar" aria-expanded="false">
            <i class="fas fa-bars fa-fw" aria-hidden="true"></i>
            <span>فهرست فصول</span>
        </button>
        <div class="header-brand-group">
            <a href="/" class="btn-home-return" title="بازگشت به سایت اصلی علی رستمی">
                <i class="fas fa-home fa-fw"></i>
                <span>سایت اصلی</span>
            </a>
            <span class="brand-divider">/</span>
            <a href="/aima-4e/" class="header-brand" title="مطالعه آنلاین کتاب هوش مصنوعی: رویکردی نوین (AIMA 4e)">
                <i class="fas fa-brain book-icon"></i>
                <span class="brand-title-text">هوش مصنوعی: رویکردی نوین</span>
                <span class="header-brand-badge">AIMA 4e</span>
            </a>
        </div>
    </div>

    <div class="header-actions">
        <a href="/aima-4e-persian/" class="btn-header" title="معرفی و مشخصات پروژه">
            <i class="fas fa-info-circle fa-fw"></i>
            <span class="d-none-sm">دربارهٔ پروژه</span>
        </a>
        <a href="https://github.com/alirostami01/aima-4e-persian/raw/main/pdf/aima-4e-persian.pdf" target="_blank" rel="noopener noreferrer" class="btn-header primary" title="دانلود کل کتاب PDF">
            <i class="fas fa-file-pdf fa-fw"></i>
            <span class="d-none-sm">دانلود PDF</span>
        </a>
        <a href="https://github.com/alirostami01/aima-4e-persian" target="_blank" rel="noopener noreferrer" class="btn-header" title="مخزن گیت‌هاب">
            <i class="fab fa-github fa-fw"></i>
        </a>
        <a href="/support/" class="btn-header" title="حمایت از پروژه">
            <i class="fas fa-heart fa-fw" style="color:#e0245e;"></i>
        </a>
        <button type="button" class="btn-header" id="btn-theme-toggle" title="تغییر ظاهر تاریک/روشن" aria-label="تغییر ظاهر تاریک یا روشن" aria-pressed="false">
            <i class="fas fa-adjust fa-fw" aria-hidden="true"></i>
        </button>
    </div>
</header>

<div class="reader-workspace">
    <!-- Sidebar -->
    <aside class="reader-sidebar" id="reader-sidebar" aria-label="فهرست فصول و بخش‌های کتاب">
        <div class="sidebar-search-box">
            <div class="search-wrapper-inner">
                <i class="fas fa-search" aria-hidden="true"></i>
                <input type="search" id="sidebar-search" class="search-input" placeholder="جستجو در فصول و بخش‌ها..." aria-label="جستجو در فصول و بخش‌ها" autocomplete="off" enterkeyhint="search">
            </div>
        </div>
        <div class="sidebar-controls">
            <span>فهرست فصول (۲۸ فصل + پیشگفتار)</span>
            <div style="display:flex;gap:.5rem;">
                <button type="button" class="sidebar-action" id="btn-expand-all">باز کردن همه</button>
                <span aria-hidden="true">·</span>
                <button type="button" class="sidebar-action" id="btn-collapse-all">بستن همه</button>
            </div>
        </div>
        <div class="sidebar-scroll" id="sidebar-scroll">
            {sidebar_content}
        </div>
    </aside>

    <div class="sidebar-backdrop" id="sidebar-backdrop" aria-hidden="true"></div>

    <!-- Main Content Reader -->
    <main class="reader-content" id="main-content" tabindex="-1">
        <h1 class="sr-only">مطالعه آنلاین هوش مصنوعی: رویکردی نوین، ویرایش چهارم</h1>
        <div class="reader-toolbar">
            <div class="toolbar-title" id="current-title" aria-live="polite" aria-atomic="true">
                <i class="fas fa-book-open" style="color:var(--accent);"></i>
                <span id="title-text">پیشگفتار</span>
            </div>
            <div class="toolbar-nav">
                <button type="button" class="btn-tool" id="btn-prev-ch" title="فصل قبلی">
                    <span>فصل قبلی</span>
                    <i class="fas fa-arrow-right" aria-hidden="true"></i>
                </button>
                <button type="button" class="btn-tool" id="btn-next-ch" title="فصل بعدی">
                    <i class="fas fa-arrow-left" aria-hidden="true"></i>
                    <span>فصل بعدی</span>
                </button>
                <a class="btn-tool" id="btn-open-tab" href="00-پیشگفتار" target="_blank" rel="noopener noreferrer" title="باز کردن در تب مستقل" aria-label="باز کردن فصل جاری در تب مستقل">
                    <i class="fas fa-external-link-alt" aria-hidden="true"></i>
                </a>
            </div>
        </div>
        <div class="frame-container">
            <iframe id="book-frame" name="book-frame" src="00-پیشگفتار" title="متن فصل کتاب"></iframe>
        </div>
    </main>
</div>

<script>
    const CHAPTERS = {chapters_json};
    let currentChapterIndex = 0;

    const frame = document.getElementById('book-frame');
    const titleText = document.getElementById('title-text');
    const btnPrev = document.getElementById('btn-prev-ch');
    const btnNext = document.getElementById('btn-next-ch');
    const btnOpenTab = document.getElementById('btn-open-tab');
    const sidebar = document.getElementById('reader-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    const searchInput = document.getElementById('sidebar-search');
    const sidebarToggle = document.getElementById('btn-toggle-sidebar');
    const themeToggle = document.getElementById('btn-theme-toggle');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function setCardExpanded(card, expanded) {{
        if (!card) return;
        card.classList.toggle('expanded', expanded);
        const toggle = card.querySelector('.ch-chevron');
        if (toggle) toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    }}

    function syncThemeButton() {{
        themeToggle.setAttribute('aria-pressed', document.body.getAttribute('theme') === 'dark' ? 'true' : 'false');
    }}

    function syncThemeToFrame() {{
        const isDark = document.body.getAttribute('theme') === 'dark';
        try {{
            if (frame.contentDocument) {{
                const doc = frame.contentDocument;
                if (isDark) {{
                    doc.documentElement.setAttribute('theme', 'dark');
                    doc.body.setAttribute('theme', 'dark');
                    if (!doc.getElementById('aima-dark-theme-style')) {{
                        const s = doc.createElement('style');
                        s.id = 'aima-dark-theme-style';
                        s.textContent = `
                            [theme=dark] {{
                                --ink: #e2e8f0 !important;
                                --muted: #94a3b8 !important;
                                --paper: #0b1120 !important;
                                --card: #1e293b !important;
                                --line: #334155 !important;
                                --wine: #fb7185 !important;
                                --wine-soft: #831843 !important;
                                --teal: #38bdf8 !important;
                                --teal-soft: #0c4a6e !important;
                                --gold: #facc15 !important;
                                --ok: #4ade80 !important;
                                --ok-soft: #064e3b !important;
                                --bad: #f87171 !important;
                                --bad-soft: #7f1d1d !important;
                                --navy: #f1f5f9 !important;
                            }}
                            [theme=dark] body {{
                                background: var(--paper) !important;
                                color: var(--ink) !important;
                            }}
                            [theme=dark] .ex {{
                                background: #162032 !important;
                                border-color: #334155 !important;
                            }}
                        `;
                        doc.head.appendChild(s);
                    }}
                }} else {{
                    doc.documentElement.removeAttribute('theme');
                    doc.body.removeAttribute('theme');
                    const s = doc.getElementById('aima-dark-theme-style');
                    if (s) s.remove();
                }}
            }}
        }} catch(e) {{}}
    }}

    frame.addEventListener('load', () => {{
        syncThemeToFrame();
        try {{
            const doc = frame.contentDocument;
            if (doc) {{
                // Always remove or hide #aima-top-nav inside the reader frame
                const nav = doc.getElementById('aima-top-nav');
                if (nav) nav.style.display = 'none';

                // Intercept any links pointing to index.html to break out of iframe
                doc.querySelectorAll('a[href*="index.html"]').forEach(a => {{
                    a.setAttribute('target', '_top');
                }});
            }}
            const loc = frame.contentWindow.location;
            const pathname = loc.pathname;
            const currentFile = decodeURIComponent(pathname.substring(pathname.lastIndexOf('/') + 1));
            const currentHash = loc.hash;

            // Breakout if index.html was accidentally loaded inside frame
            if (currentFile === 'index.html' || currentFile === '') {{
                window.top.location = '/aima-4e/';
                return;
            }}

            const idx = CHAPTERS.findIndex(c => c.route === currentFile);
            if (idx !== -1) {{
                updateActiveState(idx, currentHash);
            }}
        }} catch(e) {{}}
    }});

    function loadChapter(idx, hash = '') {{
        if (idx < 0 || idx >= CHAPTERS.length) return;
        currentChapterIndex = idx;
        const ch = CHAPTERS[idx];
        const targetUrl = ch.route + (hash ? (hash.startsWith('#') ? hash : '#' + hash) : '');

        frame.src = targetUrl;
        updateActiveState(idx, hash);

        // Update parent location hash
        try {{
            history.replaceState(null, '', '#' + encodeURIComponent(targetUrl));
        }} catch(e) {{}}

        // Close the mobile drawer without leaving focus on hidden content.
        const sidebarWasOpen = sidebar.classList.contains('open');
        closeSidebar();
        if (sidebarWasOpen) document.getElementById('main-content').focus();
    }}

    function updateActiveState(idx, hash = '') {{
        currentChapterIndex = idx;
        const ch = CHAPTERS[idx];

        // Update Title & Nav
        titleText.textContent = ch.title;
        frame.title = 'متن ' + ch.title;
        btnPrev.disabled = (idx <= 0);
        btnNext.disabled = (idx >= CHAPTERS.length - 1);
        btnOpenTab.href = ch.route + (hash || '');

        // Update Sidebar active classes and current-page announcement.
        document.querySelectorAll('.ch-card').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.ch-title-link, .sec-link').forEach(link => link.removeAttribute('aria-current'));
        const activeTitleLink = document.querySelector(`.ch-title-link[data-idx="${{idx}}"]`);
        if (activeTitleLink) activeTitleLink.setAttribute('aria-current', 'page');

        const activeCard = document.getElementById('ch-item-' + idx);
        if (activeCard) {{
            activeCard.classList.add('active');
            setCardExpanded(activeCard, true);

            if (hash) {{
                const cleanHash = hash.startsWith('#') ? hash : '#' + hash;
                const secLink = activeCard.querySelector(`a.sec-link[data-hash="${{cleanHash}}"]`);
                if (secLink) {{
                    secLink.classList.add('active');
                    secLink.setAttribute('aria-current', 'location');
                    activeTitleLink?.removeAttribute('aria-current');
                }}
            }}

            // Scroll sidebar if not visible
            activeCard.scrollIntoView({{ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' }});
        }}
    }}

    // Sidebar Accordion Click
    document.querySelectorAll('.ch-header').forEach(header => {{
        header.addEventListener('click', (e) => {{
            const card = header.closest('.ch-card');
            const idx = parseInt(header.dataset.idx, 10);

            // If clicking the title directly
            if (e.target.closest('.ch-title-link')) {{
                e.preventDefault();
                loadChapter(idx);
            }} else {{
                // The native button provides keyboard activation for the accordion.
                setCardExpanded(card, !card.classList.contains('expanded'));
            }}
        }});
    }});

    // Section Links Click
    document.querySelectorAll('.sec-link').forEach(link => {{
        link.addEventListener('click', (e) => {{
            e.preventDefault();
            const idx = parseInt(link.dataset.chIdx, 10);
            const hash = link.dataset.hash;
            loadChapter(idx, hash);
        }});
    }});

    // Prev / Next Buttons
    btnPrev.addEventListener('click', () => {{
        if (currentChapterIndex > 0) loadChapter(currentChapterIndex - 1);
    }});
    btnNext.addEventListener('click', () => {{
        if (currentChapterIndex < CHAPTERS.length - 1) loadChapter(currentChapterIndex + 1);
    }});

    // Expand / Collapse All
    document.getElementById('btn-expand-all').addEventListener('click', () => {{
        document.querySelectorAll('.ch-card').forEach(c => setCardExpanded(c, true));
    }});
    document.getElementById('btn-collapse-all').addEventListener('click', () => {{
        document.querySelectorAll('.ch-card').forEach(c => setCardExpanded(c, false));
    }});

    // Realtime Search
    searchInput.addEventListener('input', (e) => {{
        const query = e.target.value.trim().toLowerCase();
        if (!query) {{
            document.querySelectorAll('.ch-card').forEach(c => {{
                c.style.display = '';
                c.querySelectorAll('.sec-item').forEach(s => s.style.display = '');
            }});
            return;
        }}

        CHAPTERS.forEach((ch, idx) => {{
            const card = document.getElementById('ch-item-' + idx);
            if (!card) return;

            const chMatch = ch.title.toLowerCase().includes(query) || ch.short_title.toLowerCase().includes(query);
            let hasSecMatch = false;

            card.querySelectorAll('.sec-item').forEach(item => {{
                const txt = item.textContent.toLowerCase();
                if (txt.includes(query)) {{
                    item.style.display = '';
                    hasSecMatch = true;
                }} else {{
                    item.style.display = 'none';
                }}
            }});

            if (chMatch || hasSecMatch) {{
                card.style.display = '';
                setCardExpanded(card, true);
                if (chMatch) {{
                    card.querySelectorAll('.sec-item').forEach(s => s.style.display = '');
                }}
            }} else {{
                card.style.display = 'none';
            }}
        }});
    }});

    // Mobile Drawer
    function openSidebar() {{
        sidebar.classList.add('open');
        backdrop.classList.add('open');
        sidebarToggle.setAttribute('aria-expanded', 'true');
        searchInput.focus();
    }}
    function closeSidebar(restoreFocus = false) {{
        const wasOpen = sidebar.classList.contains('open');
        sidebar.classList.remove('open');
        backdrop.classList.remove('open');
        sidebarToggle.setAttribute('aria-expanded', 'false');
        if (restoreFocus && wasOpen) sidebarToggle.focus();
    }}
    sidebarToggle.addEventListener('click', openSidebar);
    backdrop.addEventListener('click', () => closeSidebar(true));

    // Theme Switcher Button
    themeToggle.addEventListener('click', () => {{
        const current = document.body.getAttribute('theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('theme', next);
        document.body.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        syncThemeButton();
        syncThemeToFrame();
    }});
    syncThemeButton();

    // Handle deep link from Hash on initial load
    window.addEventListener('DOMContentLoaded', () => {{
        const hash = decodeURIComponent(location.hash.replace(/^#/, ''));
        if (hash) {{
            let targetFile = hash;
            let targetHash = '';
            if (hash.includes('#')) {{
                const p = hash.split('#');
                targetFile = p[0];
                targetHash = '#' + p[1];
            }}
            targetFile = targetFile.replace(/\.html$/, '');
            const idx = CHAPTERS.findIndex(c => c.route === targetFile);
            if (idx !== -1) {{
                loadChapter(idx, targetHash);
                return;
            }}
        }}
        // Default: Chapter 0 (Preface)
        loadChapter(0);
    }});

    // Keyboard shortcuts never override native controls or modified key commands.
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') {{
            closeSidebar(true);
            return;
        }}
        if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
        if (e.target.closest('input, textarea, select, button, a, [contenteditable="true"]')) return;
        if (e.key === 'ArrowLeft') btnNext.click();
        if (e.key === 'ArrowRight') btnPrev.click();
    }});
</script>
</body>
</html>
"""
    return html


def inject_chapter_helpers(chapters):
    """Add a standalone floating pill to chapter HTML files that only appears when NOT inside an iframe."""
    for ch in chapters:
        fpath = AIMA_DIR / ch["filename"]
        with open(fpath, "r", encoding="utf-8") as fp:
            content = fp.read()

        # Chapter-to-chapter navigation must use the extensionless routes that
        # Cloudflare Pages serves directly, not its built-in .html redirects.
        for target in chapters:
            for quote_char in ('"', "'"):
                content = content.replace(
                    f'href={quote_char}{target["filename"]}',
                    f'href={quote_char}{target["route"]}',
                )
        content = content.replace('href="index.html"', 'href="/aima-4e/"')
        content = content.replace("href='index.html'", "href='/aima-4e/'")

        import urllib.parse
        quoted_route = urllib.parse.quote(ch["route"])
        canon_tag = f'<link rel="canonical" href="https://www.alirostami.com/aima-4e/{quoted_route}">'
        if 'rel="canonical"' in content:
            content = re.sub(
                r'<link rel="canonical" href="[^"]+">', canon_tag, content, count=1
            )
        elif "<head>" in content:
            content = content.replace("<head>", f"<head>\n    {canon_tag}")

        # Remove any previous banners or injected scripts
        content = re.sub(
            r'(\s*<style id="aima-top-nav-style">.*?</style>)?\s*(<script id="aima-top-nav-script">.*?</script>)?\s*<div id="aima-top-nav".*?</div>\s*',
            '',
            content,
            flags=re.DOTALL
        )
        content = re.sub(r'<script id="aima-standalone-helper">.*?</script>\s*', '', content, flags=re.DOTALL)

        helper_script = f"""<script id="aima-standalone-helper">
  if (window.self === window.top) {{
    window.addEventListener('DOMContentLoaded', function() {{
      var b = document.createElement('a');
      b.href = '/aima-4e/#{ch["route"]}';
      b.target = '_top';
      b.style.cssText = 'position:fixed;bottom:22px;left:22px;background:#24344d;color:#fff;padding:9px 16px;border-radius:24px;box-shadow:0 6px 18px rgba(0,0,0,.25);text-decoration:none;font-size:13px;font-family:Tahoma,sans-serif;z-index:99999;display:inline-flex;align-items:center;gap:6px;transition:transform .2s;border:1px solid rgba(255,255,255,.2);';
      b.innerHTML = '📖 باز کردن در کتابخوان با سایدبار';
      b.onmouseover = function() {{ b.style.transform = 'translateY(-2px)'; }};
      b.onmouseout = function() {{ b.style.transform = 'none'; }};
      document.body.appendChild(b);
    }});
  }}
</script>
"""
        # Append before </body>
        if "</body>" in content:
            updated = content.replace("</body>", helper_script + "</body>")
        else:
            updated = content + helper_script

        with open(fpath, "w", encoding="utf-8") as fp:
            fp.write(updated)


def main():
    chapters = extract_chapters()
    print(f"Loaded {len(chapters)} chapters.")

    # 1. Write aima-4e/index.html
    index_html = generate_index_html(chapters)
    out_file = AIMA_DIR / "index.html"
    out_file.write_text(index_html, encoding="utf-8")
    print(f"Generated {out_file} ({len(index_html)} bytes)")

    # 2. Inject chapter nav helpers
    inject_chapter_helpers(chapters)
    print("Injected nav helpers into chapter files.")
    apply_site_postprocessors()


if __name__ == "__main__":
    main()
