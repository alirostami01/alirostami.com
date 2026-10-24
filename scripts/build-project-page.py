#!/usr/bin/env python3
"""Generates the project documentation page for Fundamentals of Software Architecture Persian."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHAPTERS_TABLE = [
    # (num, title_fa, title_en, pages, filename, ch_idx)
    ("01", "مقدمه", "Introduction", 17, "chapter-01.html", 0),
    ("PART_1", "بخش اول: مبانی", "Part I. Foundations", None, None, None),
    ("02", "تفکر معماری", "Architectural Thinking", 23, "chapter-02.html", 1),
    ("03", "ماژولاریتی", "Modularity", 22, "chapter-03.html", 2),
    ("04", "تعریف ویژگی‌های معماری", "Architectural Characteristics Defined", 17, "chapter-04.html", 3),
    ("05", "شناسایی ویژگی‌های معماری", "Identifying Architectural Characteristics", 18, "chapter-05.html", 4),
    ("06", "سنجش و حاکمیت بر ویژگی‌های معماری", "Measuring and Governing Architecture Characteristics", 16, "chapter-06.html", 5),
    ("07", "دامنهٔ ویژگی‌های معماری", "The Scope of Architectural Characteristics", 12, "chapter-07.html", 6),
    ("08", "تفکر مؤلفه‌محور", "Component-Based Thinking", 26, "chapter-08.html", 7),
    ("PART_2", "بخش دوم: سبک‌های معماری", "Part II. Architecture Styles", None, None, None),
    ("09", "مبانی", "Foundations", 28, "chapter-09.html", 8),
    ("10", "سبک معماری لایه‌ای", "Layered Architecture Style", 15, "chapter-10.html", 9),
    ("11", "سبک معماری تک‌پارچهٔ ماژولار", "The Modular Monolith Architecture Style", 18, "chapter-11.html", 10),
    ("12", "سبک معماری خط لوله", "Pipeline Architecture Style", 15, "chapter-12.html", 11),
    ("13", "سبک معماری میکروکرنل", "Microkernel Architecture Style", 18, "chapter-13.html", 12),
    ("14", "سبک معماری مبتنی بر سرویس", "Service-Based Architecture Style", 23, "chapter-14.html", 13),
    ("15", "سبک معماری رویدادمحور", "Event-Driven Architecture Style", 67, "chapter-15.html", 14),
    ("16", "سبک معماری مبتنی بر فضا", "Space-Based Architecture Style", 39, "chapter-16.html", 15),
    ("17", "معماری سرویس‌گرای ارکستراسیون‌محور", "Orchestration-Driven Service-Oriented Architecture", 19, "chapter-17.html", 16),
    ("18", "معماری میکروسرویس‌ها", "Microservices Architecture", 37, "chapter-18.html", 17),
    ("19", "انتخاب سبک معماری مناسب", "Choosing the Appropriate Architecture Style", 15, "chapter-19.html", 18),
    ("20", "الگوهای معماری", "Architectural Patterns", 17, "chapter-20.html", 19),
    ("PART_3", "بخش سوم: تکنیک‌ها و مهارت‌های نرم", "Part III. Techniques and Soft Skills", None, None, None),
    ("21", "تصمیمات معماری", "Architectural Decisions", 23, "chapter-21.html", 20),
    ("22", "تحلیل ریسک معماری", "Analyzing Architecture Risk", 21, "chapter-22.html", 21),
    ("23", "نمودارکشی معماری", "Diagramming Architecture", 10, "chapter-23.html", 22),
    ("24", "اثربخش کردن تیم‌ها", "Making Teams Effective", 24, "chapter-24.html", 23),
    ("25", "مهارت‌های مذاکره و رهبری", "Negotiation and Leadership Skills", 19, "chapter-25.html", 24),
    ("26", "تقاطع‌های معماری", "Architectural Intersections", 19, "chapter-26.html", 25),
    ("27", "بازنگری در قوانین معماری نرم‌افزار", "The Laws of Software Architecture, Revisited", 13, "chapter-27.html", 26),
    ("پیوست", "پرسش‌های بحث", "Discussion Questions", 13, "appendix.html", 27),
]

GITHUB_REPO = "https://github.com/alirostami01/Fundamentals-of-Software-Architecture_-A-Modern-Engineering-Approach"
GITHUB_PDF = f"{GITHUB_REPO}/raw/main/pdf/book.pdf"

def build_table_rows():
    rows = []
    for item in CHAPTERS_TABLE:
        num, title_fa, title_en, pages, filename, ch_idx = item
        if num.startswith("PART_"):
            rows.append(f"""
<tr style="background: rgba(37,99,235,0.08); font-weight: bold;">
    <td colspan="5" style="padding: 0.75rem 1rem; color: #1e3a8a;">
        <i class="fas fa-layer-group" style="margin-left: 0.5rem;"></i> {title_fa} <span dir="ltr" style="font-weight: normal; font-size: 0.85rem; opacity: 0.8;">({title_en})</span>
    </td>
</tr>""")
        else:
            online_link = f"/software-architecture/#ch-item-{ch_idx}"
            gh_md = f"{GITHUB_REPO}/blob/main/markdown/{'chapter-' + num if num != 'پیوست' else 'appendix'}.md"
            gh_html = f"{GITHUB_REPO}/blob/main/html/{filename}"
            gh_pdf = f"{GITHUB_REPO}/raw/main/pdf/chapters/{'chapter-' + num if num != 'پیوست' else 'appendix'}.pdf"
            pages_str = f" <sub>({pages} ص)</sub>" if pages else ""
            rows.append(f"""<tr>
<td><code>{num}</code></td>
<td>
    <strong><a href="{online_link}">{title_fa}</a></strong><br>
    <sub dir="ltr" style="color: #64748b;">{title_en}</sub>
</td>
<td><a href="{online_link}" class="reader-pill"><i class="fas fa-book-reader"></i> خواندن آنلاین</a></td>
<td><a href="{gh_md}" target="_blank" rel="noopener noreferrer">Markdown</a></td>
<td><a href="{gh_pdf}" target="_blank" rel="noopener noreferrer">PDF{pages_str}</a></td>
</tr>""")
    return "\n".join(rows)

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="robots" content="index, follow" />
        <title>مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن — ترجمهٔ فارسی</title>
        <meta name="Description" content="ترجمه و آماده‌سازی فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار اثر مارک ریچاردز و نیل فورد (۲۰۲۵)؛ شامل ۲۷ فصل کامل، پیوست پرسش‌های بحث، ۲۴۱ شکل، نسخه یکپارچه PDF (۶۵۰ صفحه) و سامانهٔ مطالعهٔ آنلاین تعاملی با سایدبار هوشمند.">
        <meta name="keywords" content="معماری نرم‌افزار, مبانی معماری نرم‌افزار, مارک ریچاردز, نیل فورد, ترجمه فارسی معماری نرم افزار, میکروسرویس‌ها, الگوهای معماری, علی رستمی, Fundamentals of Software Architecture Persian">
        <meta property="og:title" content="مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن — ترجمهٔ فارسی" />
        <meta property="og:description" content="ترجمه و آماده‌سازی فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار اثر مارک ریچاردز و نیل فورد؛ شامل ۲۷ فصل، پیوست، ۲۴۱ شکل، سامانه مطالعه آنلاین تعاملی و نسخه PDF ۶۵۰ صفحه‌ای." />
        <meta property="og:type" content="book" />
        <meta property="og:url" content="https://alirostami.ir/fundamentals-of-software-architecture-persian/" />
        <meta property="og:site_name" content="علی رستمی" />
        <meta property="og:image" content="https://alirostami.ir/images/projects/fundamentals-of-software-architecture-persian.png" />
        <meta name="twitter:card" content="summary_large_image"/>
        <meta name="twitter:title" content="مبانی معماری نرم‌افزار — ترجمهٔ فارسی"/>
        <meta name="twitter:description" content="ترجمه فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار اثر مارک ریچاردز و نیل فورد با ۲۷ فصل و کتابخوان آنلاین تعاملی."/>
        <meta name="twitter:image" content="https://alirostami.ir/images/projects/fundamentals-of-software-architecture-persian.png"/>
        <meta name="application-name" content="Ali Rostami">
        <meta name="apple-mobile-web-app-title" content="Ali Rostami">
        <meta name="theme-color" content="#ffffff">
        <meta name="msapplication-TileColor" content="#da532c">
        <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
        <link rel="manifest" href="/site.webmanifest">
        <link rel="canonical" href="https://alirostami.ir/fundamentals-of-software-architecture-persian/" />
        <link rel="stylesheet" href="/css/style.min.css">
        <link rel="preload" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css"></noscript>
        <link rel="preload" href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css"></noscript>

        <script type="application/ld+json">
        {{
          "@context": "https://schema.org",
          "@graph": [
            {{
              "@type": "Book",
              "@id": "https://alirostami.ir/fundamentals-of-software-architecture-persian/#book",
              "name": "مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن (ویرایش دوم)",
              "alternateName": "Fundamentals of Software Architecture: A Modern Engineering Approach (2nd Edition)",
              "author": [
                {{"@type": "Person", "name": "Mark Richards", "alternateName": "مارک ریچاردز"}},
                {{"@type": "Person", "name": "Neal Ford", "alternateName": "نیل فورد"}}
              ],
              "translator": {{
                "@type": "Person",
                "name": "علی رستمی",
                "url": "https://alirostami.ir/"
              }},
              "inLanguage": "fa",
              "bookFormat": "https://schema.org/EBook",
              "numberOfPages": 650,
              "datePublished": "2025",
              "url": "https://alirostami.ir/fundamentals-of-software-architecture-persian/",
              "image": "https://alirostami.ir/images/projects/fundamentals-of-software-architecture-persian.png",
              "description": "ترجمه و آماده‌سازی فارسی ویرایش دوم کتاب مبانی معماری نرم‌افزار اثر مارک ریچاردز و نیل فورد؛ شامل ۲۷ فصل در ۳ بخش جامع، پیوست، واژه‌نامه تخصصی و نسخه PDF ۶۵۰ صفحه‌ای."
            }},
            {{
              "@type": "BreadcrumbList",
              "@id": "https://alirostami.ir/fundamentals-of-software-architecture-persian/#breadcrumb",
              "itemListElement": [
                {{
                  "@type": "ListItem",
                  "position": 1,
                  "name": "خانه",
                  "item": "https://alirostami.ir/fa/"
                }},
                {{
                  "@type": "ListItem",
                  "position": 2,
                  "name": "پروژه‌ها",
                  "item": "https://alirostami.ir/fa/#projects"
                }},
                {{
                  "@type": "ListItem",
                  "position": 3,
                  "name": "مبانی معماری نرم‌افزار — ترجمهٔ فارسی",
                  "item": "https://alirostami.ir/fundamentals-of-software-architecture-persian/"
                }}
              ]
            }}
          ]
        }}
        </script>
        <style>
    /* keep the theme header/footer in their original LTR layout */
    #header-desktop, #header-mobile, .footer {{ direction: ltr; }}

    .docs-page {{ direction: rtl; text-align: right; }}
    .docs-page .content {{ line-height: 2.1; }}

    /* ---- page head ---- */
    .docs-page .docs-hero {{
        display: flex;
        align-items: center;
        gap: 1.25rem;
        margin: 2rem 0 .75rem;
    }}
    .docs-page .docs-hero img {{
        width: 90px;
        height: 90px;
        flex: 0 0 90px;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
    }}
    .docs-page .docs-hero .single-title {{ margin: 0; text-align: right; font-size: 1.75rem; }}
    .docs-page .docs-hero .docs-hero-sub {{ font-size: .95rem; opacity: .75; margin: .35rem 0 0; line-height: 1.6; }}
    .docs-page .docs-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: .6rem;
        margin: 0 0 1.5rem;
    }}
    .docs-page .docs-actions a {{
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        font-size: .85rem;
        line-height: 1.6;
        padding: .45rem 1.1rem;
        border-radius: 2rem;
        border: 1px solid rgba(128,128,128,.35);
        transition: all .2s ease;
        text-decoration: none;
    }}
    .docs-page .docs-actions a:hover {{ background: rgba(37,99,235,.12); border-color: #2563eb; transform: translateY(-1px); }}
    .docs-page .docs-actions a.primary {{
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        border-color: transparent;
        color: #fff;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }}
    .docs-page .docs-actions a.primary:hover {{ filter: brightness(1.12); color: #fff; }}
    .docs-page .docs-actions a.accent-red {{
        background: linear-gradient(135deg, #e11d48, #f43f5e);
        border-color: transparent;
        color: #fff;
        font-weight: 700;
    }}

    /* ---- table of contents ---- */
    .docs-page .docs-toc {{
        background: rgba(128,128,128,.07);
        border: 1px solid rgba(128,128,128,.2);
        border-radius: .8rem;
        padding: 1.2rem 1.4rem;
        margin: 0 0 2rem;
    }}
    [theme=dark] .docs-page .docs-toc {{ background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.1); }}
    .docs-page .docs-toc > .docs-toc-title {{
        font-weight: 700;
        margin-bottom: .6rem;
        display: flex;
        align-items: center;
        gap: .5rem;
        font-size: 1.05rem;
    }}
    .docs-page .docs-toc ul {{
        list-style: none;
        padding: 0;
        margin: 0;
        columns: 2;
        column-gap: 2rem;
    }}
    .docs-page .docs-toc ul ul {{ display: none; }}
    .docs-page .docs-toc li {{ padding: .25rem 0; break-inside: avoid; }}
    @media only screen and (max-width: 680px) {{
        .docs-page .docs-toc ul {{ columns: 1; }}
        .docs-page .docs-hero {{ flex-direction: column; text-align: center; }}
        .docs-page .docs-hero .single-title {{ text-align: center; }}
    }}

    /* ---- headings ---- */
    .docs-page .content h2 {{
        margin: 2.8rem 0 1rem;
        padding-bottom: .5rem;
        border-bottom: 1px solid rgba(128,128,128,.25);
        color: var(--text-color, inherit);
    }}
    .docs-page .content h3 {{ margin: 2rem 0 .8rem; }}
    .docs-page .content h2 a.headerlink,
    .docs-page .content h3 a.headerlink {{
        font-size: .8rem;
        opacity: 0;
        margin-right: .4rem;
        transition: opacity .2s ease;
    }}
    .docs-page .content h2:hover a.headerlink,
    .docs-page .content h3:hover a.headerlink {{ opacity: .5; }}

    /* ---- lists ---- */
    .docs-page .content ul,
    .docs-page .content ol {{ padding-right: 1.6rem; padding-left: 0; }}
    .docs-page .content li {{ margin: .35rem 0; }}

    /* ---- code: always LTR ---- */
    .docs-page .content pre,
    .docs-page .content pre code,
    .docs-page .content code {{
        direction: ltr;
        unicode-bidi: isolate;
    }}
    .docs-page .content pre {{
        display: block;
        overflow-x: auto;
        text-align: left;
        padding: .9rem 1.1rem;
        border-radius: .5rem;
        font-size: .85rem;
        line-height: 1.7;
        background: rgba(15, 23, 42, 0.04);
        border: 1px solid rgba(128,128,128,.2);
    }}
    [theme=dark] .docs-page .content pre {{
        background: rgba(15, 23, 42, 0.6);
        border-color: rgba(255,255,255,.1);
    }}
    .docs-page .content pre code {{
        display: block;
        white-space: pre;
        padding: 0;
        font-size: inherit;
        line-height: inherit;
    }}
    .docs-page .content p > code,
    .docs-page .content li > code,
    .docs-page .content td code {{
        font-size: .85rem;
        padding: .15rem .35rem;
        border-radius: 4px;
        background: rgba(128,128,128,.12);
    }}

    /* ---- tables ---- */
    .docs-page .content .table-wrapper {{
        overflow-x: auto;
        margin: 1.5rem 0;
        border-radius: 8px;
        border: 1px solid rgba(128,128,128,.2);
    }}
    .docs-page .content .table-wrapper > table {{
        width: 100%;
        border-collapse: collapse;
        text-align: right;
    }}
    .docs-page .content .table-wrapper > table th,
    .docs-page .content .table-wrapper > table td {{
        padding: .65rem .85rem;
        vertical-align: middle;
        line-height: 1.7;
        border-bottom: 1px solid rgba(128,128,128,.15);
    }}
    .docs-page .content .table-wrapper > table th {{
        background: rgba(128,128,128,.08);
        font-weight: 700;
    }}
    .reader-pill {{
        display: inline-flex;
        align-items: center;
        gap: .3rem;
        padding: .2rem .55rem;
        border-radius: 4px;
        background: rgba(37,99,235,.1);
        color: #2563eb !important;
        font-size: .8rem;
        font-weight: 600;
        text-decoration: none;
    }}
    .reader-pill:hover {{
        background: #2563eb;
        color: #fff !important;
    }}

    /* ---- callouts / blockquotes ---- */
    .docs-page .content blockquote {{
        border-left: none;
        border-right: .35rem solid #2563eb;
        padding: .8rem 1.2rem;
        border-radius: .4rem;
        background: rgba(37,99,235,.05);
        margin: 1.5rem 0;
    }}
    [theme=dark] .docs-page .content blockquote {{
        border-right-color: #38bdf8;
        background: rgba(56, 189, 248, 0.08);
    }}
    .docs-page .content blockquote p {{ margin: .3rem 0; }}

    .badge-bar {{
        display: flex;
        flex-wrap: wrap;
        gap: .4rem;
        margin: .75rem 0 1.25rem;
    }}
    .badge-tag {{
        display: inline-block;
        padding: .2rem .6rem;
        border-radius: 4px;
        font-size: .78rem;
        background: rgba(128,128,128,.12);
        color: var(--text-color, #475569);
    }}
    [theme=dark] .badge-tag {{ color: #cbd5e1; }}
</style>
</head>
    <body data-header-desktop="fixed" data-header-mobile="auto"><script type="text/javascript">(window.localStorage && localStorage.getItem('theme') ? localStorage.getItem('theme') === 'dark' : ('auto' === 'auto' ? window.matchMedia('(prefers-color-scheme: dark)').matches : 'auto' === 'dark')) && document.body.setAttribute('theme', 'dark');</script>

        <div id="mask"></div><div class="wrapper"><header class="desktop" id="header-desktop">
    <div class="header-wrapper">
        <div class="header-title">
            <a href="/fa/" title="علی رستمی">Ali Rostami</a>
        </div>
        <div class="menu">
            <div class="menu-inner"><a href="/fa/" class="menu-item" title="خانه">خانه</a><a href="/software-architecture/" class="menu-item" title="مطالعه آنلاین کتاب معماری نرم‌افزار"><i class="fas fa-cubes fa-fw" aria-hidden="true"></i> کتاب معماری نرم‌افزار</a><a href="/aima-4e/" class="menu-item" title="کتاب هوش مصنوعی">کتاب هوش مصنوعی</a><a href="/posts/" class="menu-item" title="مقالات">مقالات</a><a href="/support/" class="menu-item" title="حمایت"><i class="fas fa-heart fa-fw" style="color:#e0245e;" aria-hidden="true"></i> حمایت</a><a href="javascript:void(0);" class="menu-item theme-switch" title="تغییر ظاهر"><i class="fas fa-adjust fa-fw" aria-hidden="true"></i></a><a href="javascript:void(0);" class="menu-item language" title="انتخاب زبان"><i class="fa fa-globe" aria-hidden="true"></i><select class="language-select" onchange="location = this.value;"><option value="/">English</option><option value="/fa/" selected>فارسی</option></select></a></div>
        </div>
    </div>
</header><header class="mobile" id="header-mobile">
    <div class="header-container">
        <div class="header-wrapper">
            <div class="header-title">
                <a href="/fa/" title="علی رستمی">Ali Rostami</a>
            </div>
            <div class="menu-toggle" id="menu-toggle-mobile">
                <span></span><span></span><span></span>
            </div>
        </div>
        <div class="menu" id="menu-mobile"><a href="/fa/" class="menu-item" title="خانه">خانه</a><a href="/software-architecture/" class="menu-item" title="مطالعه آنلاین کتاب معماری نرم‌افزار"><i class="fas fa-cubes fa-fw" aria-hidden="true"></i> کتاب معماری نرم‌افزار</a><a href="/aima-4e/" class="menu-item" title="کتاب هوش مصنوعی">کتاب هوش مصنوعی</a><a href="/posts/" class="menu-item" title="مقالات">مقالات</a><a href="/support/" class="menu-item" title="حمایت"><i class="fas fa-heart fa-fw" style="color:#e0245e;" aria-hidden="true"></i> حمایت</a><a href="javascript:void(0);" class="menu-item theme-switch" title="تغییر ظاهر"><i class="fas fa-adjust fa-fw" aria-hidden="true"></i></a><a href="javascript:void(0);" class="menu-item language" title="انتخاب زبان"><i class="fa fa-globe" aria-hidden="true"></i><select class="language-select" onchange="location = this.value;"><option value="/">English</option><option value="/fa/" selected>فارسی</option></select></a></div>
    </div>
</header><main class="main">
                <div class="container"><article class="page single docs-page">
        <div class="docs-hero">
            <img src="/images/projects/fundamentals-of-software-architecture-persian.png" alt="لوگوی مبانی معماری نرم‌افزار" width="90" height="90" decoding="async">
            <div>
                <h1 class="single-title animate__animated animate__flipInX">مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن</h1>
                <p class="docs-hero-sub">ترجمه و آماده‌سازی فارسی ویرایش دوم (۲۰۲۵) · مارک ریچاردز (Mark Richards) و نیل فورد (Neal Ford) · ترجمهٔ علی رستمی</p>
            </div>
        </div>
        <div class="badge-bar">
            <span class="badge-tag"><i class="fas fa-layer-group"></i> ۲۷ فصل در ۳ بخش</span>
            <span class="badge-tag"><i class="fas fa-file-pdf"></i> نسخه ۶۵۰ صفحه‌ای PDF</span>
            <span class="badge-tag"><i class="fas fa-images"></i> ۲۴۱ تصویر و دیاگرام</span>
            <span class="badge-tag"><i class="fas fa-book-reader"></i> کتابخوان آنلاین با سایدبار</span>
            <span class="badge-tag"><i class="fab fa-github"></i> کاملاً متن‌باز (GPL-3.0)</span>
        </div>
        <div class="docs-actions">
            <a class="primary" href="/software-architecture/"><i class="fas fa-book-reader fa-fw" aria-hidden="true"></i> مطالعهٔ آنلاین کتاب (با سایدبار)</a>
            <a class="primary" href="{GITHUB_PDF}" target="_blank" rel="noopener noreferrer"><i class="fas fa-file-pdf fa-fw" aria-hidden="true"></i> دانلود کامل کتاب از گیت‌هاب (PDF)</a>
            <a class="accent-red" href="/support/"><i class="fas fa-heart fa-fw" aria-hidden="true"></i> حمایت مالی از پروژه</a>
            <a class="" href="{GITHUB_REPO}" target="_blank" rel="noopener noreferrer"><i class="fab fa-github fa-fw" aria-hidden="true"></i> مخزن گیت‌هاب پروژه</a>
            <a class="" href="{GITHUB_REPO}/tree/main/markdown" target="_blank" rel="noopener noreferrer"><i class="fas fa-file-code fa-fw" aria-hidden="true"></i> متن فصل‌ها در Markdown</a>
        </div>
        <nav class="docs-toc" aria-label="فهرست مطالب این صفحه">
            <div class="docs-toc-title"><i class="fas fa-list-ul fa-fw" aria-hidden="true"></i> فهرست محتوای این صفحه</div>
            <div class="toc">
<ul>
<li><a href="#درباره-پروژه">📚 دربارهٔ پروژه</a></li>
<li><a href="#ویژگیهای-پروژه">✨ ویژگی‌های پروژه</a></li>
<li><a href="#بخشهای-سهگانه">🏗️ ساختار و بخش‌های سه‌گانه کتاب</a></li>
<li><a href="#فهرست-فصلها">📖 فهرست فصل‌ها و لینک‌های مطالعه</a></li>
<li><a href="#نسخه-وب-و-کتابخوان">🌐 نسخهٔ وب و مطالعهٔ آنلاین تعاملی</a></li>
<li><a href="#نسخه-pdf">📄 نسخهٔ یکپارچه و فصل‌به‌فصل PDF</a></li>
<li><a href="#تصاویر-و-شکلها">🖼️ تصاویر و دیاگرام‌های فنی (۲۴۱ شکل)</a></li>
<li><a href="#کدها-و-واژگان">💻 واژگان تخصصی و استانداردهای ترجمه</a></li>
<li><a href="#ساختار-مخزن">🗂️ ساختار مخزن گیت‌هاب</a></li>
<li><a href="#مشارکت-در-پروژه">🤝 مشارکت در ویرایش و بهبود کتاب</a></li>
<li><a href="#حمایت-از-پروژه">⭐ حمایت از پروژه</a></li>
<li><a href="#درباره-اثر-اصلی">⚖️ دربارهٔ اثر اصلی و نویسندگان</a></li>
</ul>
</div>
        </nav>
        <div class="content" id="content">
<p>ترجمه، بازبینی و ارائهٔ فارسی ویرایش دوم کتاب پرفروش و مرجع <strong>Fundamentals of Software Architecture: A Modern Engineering Approach (2nd Edition, 2025)</strong> نوشتهٔ دو چهرهٔ نامدار معماری نرم‌افزار در جهان: <strong>Mark Richards</strong> و <strong>Neal Ford</strong> از انتشارات O&rsquo;Reilly.</p>

<blockquote>
<p>🌟 <strong>سامانه مطالعهٔ آنلاین فعال شد:</strong> بدون نیاز به دانلود فایل‌های حجیم، می‌توانید کلیهٔ ۲۷ فصل و پیوست کتاب را به همراه جستجوی سریع، تغییر پوسته (دارک/لایت)، شماره‌گذاری بخش‌ها و ناوبری پیشرفته مطالعه کنید:<br>
👉 <a href="/software-architecture/"><strong>ورود به کتابخوان آنلاین مبانی معماری نرم‌افزار</strong></a></p>
</blockquote>

<h2 id="درباره-پروژه">📚 دربارهٔ پروژه<a class="headerlink" href="#درباره-پروژه" title="Permanent link">#</a></h2>
<p>این مخزن یک پروژهٔ جامع و متن‌باز برای <strong>ترجمه، تدوین و ارائهٔ رایگان فارسی</strong> کتاب مرجع <strong>Fundamentals of Software Architecture (ویرایش دوم)</strong> است.</p>
<p>معماری نرم‌افزار حوزه‌ای بسیار پویا، پرچالش و سرشار از بده‌بستان‌ها (Trade-offs) است. هدف این پروژه ارتقای سطح دانش مهندسی و معماری نرم‌افزار در جامعهٔ فارسی‌زبان از طریق ارائهٔ اثری دقیق، روان و منطبق بر آخرین تغییرات ویرایش دوم (شامل مباحث نوین نظیر ماژولار مونولیت، کوانتوم معماری، توابع برازش، بازبینی قوانین معماری و مهارت‌های نرم تیم‌داری و مذاکره) می‌باشد.</p>

<blockquote>
<p><strong>توجه و شفاف‌سازی:</strong> این پروژه یک تلاش علمی، فرهنگی و عام‌المنفعه به‌صورت مستقل و غیررسمی بوده و به نویسندگان اصلی کتاب یا انتشارات O&rsquo;Reilly وابستگی رسمی ندارد. حقوق معنوی اثر اصلی متعلق به پدیدآورندگان ارجمند آن است.</p>
</blockquote>

<h2 id="ویژگیهای-پروژه">✨ ویژگی‌های پروژه<a class="headerlink" href="#ویژگیهای-پروژه" title="Permanent link">#</a></h2>
<ul>
<li>🇮🇷 <strong>ترجمهٔ دقیق و یکدست فارسی</strong> برای تمام ۲۷ فصل کتاب و پیوست کامل پرسش‌های بحث (Discussion Questions).</li>
<li>🌐 <strong>سامانه کتابخوان آنلاین مدرن</strong> با سایدبار هوشمند، باز/بسته شدن کشویی، هایلایت بخش جاری، جستجوی بلادرنگ در عناوین فصول و همگام‌سازی تم تاریک/روشن.</li>
<li>📕 <strong>نسخهٔ PDF بسیار باکیفیت و استاندارد</strong> در ۶۵۰ صفحه با فهرست پیوندی، شماره‌گذاری فارسی صفحات، نشانک‌های درختی (Bookmarks) و نسخهٔ مجزا برای تک‌تک فصول.</li>
<li>🖼️ <strong>۲۴۱ شکل و دیاگرام باکیفیت</strong> کتاب به تفکیک فصول با عناوین کاملاً فارسی.</li>
<li>📖 <strong>واژه‌نامهٔ جامع تخصصی</strong> در انتهای هر فصل و فایل یکپارچه برای هماهنگی اصطلاحات کلیدی نرم‌افزار.</li>
<li>💻 <strong>حفظ عبارات فنی و کدها</strong> به زبان اصلی در کنار معادل‌های مصطلح فارسی جهت جلوگیری از ابهام در پروژه‌های واقعی.</li>
<li>🌱 <strong>شفاف، مشارکتی و کاملاً متن‌باز</strong> تحت پروانهٔ عمومی GPL-3.0 در گیت‌هاب.</li>
</ul>

<h2 id="بخشهای-سهگانه">🏗️ ساختار و بخش‌های سه‌گانه کتاب<a class="headerlink" href="#بخشهای-سهگانه" title="Permanent link">#</a></h2>
<p>ویرایش دوم این کتاب مباحث را در سه بخش بنیادی و زنجیره‌ای دسته‌بندی کرده است:</p>
<ol>
<li><strong>بخش اول: مبانی (Foundations) — فصل‌های ۱ تا ۸:</strong> آشنایی با تفکر معماری، قوانین بنیادین، تعریف دقیق ماژولاریتی، ویژگی‌های معماری (کیفیت‌های سامانه‌ای، سنجش، حاکمیت و توابع برازش) و تفکر مؤلفه‌محور.</li>
<li><strong>بخش دوم: سبک‌های معماری (Architecture Styles) — فصل‌های ۹ تا ۲۰:</strong> بررسی عمیق و مقایسه‌ای سبک‌های تک‌پارچه و توزیع‌شده شامل معماری لایه‌ای، مونولیت ماژولار، خط لوله (Pipeline)، میکروکرنل، مبتنی بر سرویس، معماری بسیار مقیاس‌پذیر رویدادمحور (Event-Driven)، فضاپایه (Space-Based)، SOA ارکستراسیون‌محور، میکروسرویس‌ها، نحوهٔ انتخاب سبک مناسب و الگوهای معماری.</li>
<li><strong>بخش سوم: تکنیک‌ها و مهارت‌های نرم (Techniques and Soft Skills) — فصل‌های ۲۱ تا ۲۷:</strong> چگونگی اتخاذ و ثبت تصمیمات معماری (ADR)، تحلیل و ارزیابی ریسک، نمودارکشی و مستندسازی مؤثر، توانمندسازی تیم‌های مهندسی، مهارت‌های حیاتی مذاکره و رهبری، تقاطع‌های معماری و بازبینی قوانین نوین معماری نرم‌افزار.</li>
</ol>

<h2 id="فهرست-فصلها">📖 فهرست فصل‌ها و لینک‌های مطالعه<a class="headerlink" href="#فهرست-فصلها" title="Permanent link">#</a></h2>
<blockquote>
<p>📥 <strong>دانلود نسخهٔ کامل کتاب (PDF از گیت‌هاب):</strong> <a href="{GITHUB_PDF}" target="_blank" rel="noopener noreferrer">book.pdf</a> (۶۵۰ صفحه — ۳۸ مگابایت)<br>
🌐 <strong>مطالعه در سامانه کتابخوان آنلاین:</strong> <a href="/software-architecture/">ورود به کتابخوان معماری نرم‌افزار</a></p>
</blockquote>

<div class="table-wrapper">
<table>
<thead>
<tr>
<th style="width: 50px;">فصل</th>
<th>عنوان فصل و موضوعات</th>
<th style="width: 140px;">وب‌سایت</th>
<th style="width: 90px;">Markdown</th>
<th style="width: 110px;">PDF</th>
</tr>
</thead>
<tbody>
{build_table_rows()}
</tbody>
</table>
</div>

<h2 id="نسخه-وب-و-کتابخوان">🌐 نسخهٔ وب و مطالعهٔ آنلاین تعاملی<a class="headerlink" href="#نسخه-وب-و-کتابخوان" title="Permanent link">#</a></h2>
<p>نسخهٔ وب در مسیر <a href="/software-architecture/"><code>/software-architecture/</code></a> به نحوی پیاده‌سازی شده که مطالعهٔ آنلاین کتاب را به تجربه‌ای لذت‌بخش و روان تبدیل کند:</p>
<ul>
<li><strong>سایدبار سه سطحی با انیمیشن آکاردئونی:</strong> فصول بر پایه بخش‌های ۱، ۲ و ۳ سازمان‌دهی شده و هر فصل شامل لیست بخش‌های داخلی (Sub-sections) است.</li>
<li><strong>جستجوی زنده:</strong> در کادر جستجوی سایدبار با تایپ هر واژه (فارسی یا انگلیسی)، فهرست فصول فوراً فیلتر می‌شود.</li>
<li><strong>لینک مستقیم به بخش‌ها (Deep-linking):</strong> با کلیک روی هر سرتیتر، آدرس مرورگر به‌روزرسانی شده و امکان بوکمارک یا اشتراک‌گذاری مستقیم همان بخش وجود دارد.</li>
<li><strong>پشتیبانی کامل از حالت تاریک (Dark Mode):</strong> پوستهٔ کتابخوان به طور هوشمند با تم انتخابی شما در وب‌سایت همگام می‌گردد.</li>
<li><strong>دکمه‌های پیمایش سریع:</strong> دکمه‌های «فصل قبلی»، «فصل بعدی»، «بارگذاری مجدد» و کلیدهای میانبر کیبورد (<kbd>&rarr;</kbd> و <kbd>&larr;</kbd>) برای مطالعهٔ پیوسته تعبیه شده‌اند.</li>
</ul>

<h2 id="نسخه-pdf">📄 نسخهٔ یکپارچه و فصل‌به‌فصل PDF<a class="headerlink" href="#نسخه-pdf" title="Permanent link">#</a></h2>
<p>نسخه‌های PDF با استفاده از مرورگر Chromium بدون سر (Headless) و کتابخانهٔ PyMuPDF با رعایت بالاترین استانداردهای چاپ و نشر تولید شده‌اند:</p>
<ul>
<li><strong><code>pdf/book.pdf</code>:</strong> کل کتاب در ۶۵۰ صفحه A4؛ شامل صفحه عنوان اختصاصی، پیشگفتار، فهرست مندرجات قابل کلیک، ۲۷ فصل، پیوست و واژه‌نامه با نشانک‌های درختی جهت پیمایش در PDF خوان‌ها.</li>
<li><strong><code>pdf/chapters/</code>:</strong> نسخهٔ جداگانه از هر یک از فصول همراه با شماره‌گذاری مستقل برای پرینت یا مطالعه تک‌فصل‌ها.</li>
<li>تایپوگرافی زیبا با فونت اصیل وزیرمتن (Vazirmatn) و فونت کد DejaVu Sans Mono با شماره‌گذاری فارسی و راست‌چین‌سازی اصولی.</li>
</ul>

<h2 id="تصاویر-و-شکلها">🖼️ تصاویر و دیاگرام‌های فنی (۲۴۱ شکل)<a class="headerlink" href="#تصاویر-و-شکلها" title="Permanent link">#</a></h2>
<p>یکی از بزرگ‌ترین نقاط قوت این اثر، دیاگرام‌ها و نمودارهای معماری است. در این پروژه تمامی <strong>۲۴۱ شکل</strong> با بالاترین وضوح استخراج و در پوشهٔ <code>figures/</code> به تفکیک فصول قرار گرفته‌اند. عناوین تمامی شکل‌ها ترجمه شده و در ساختار کتاب جاسازی شده است.</p>

<h2 id="کدها-و-واژگان">💻 واژگان تخصصی و استانداردهای ترجمه<a class="headerlink" href="#کدها-و-واژگان" title="Permanent link">#</a></h2>
<p>برای حفظ دقت مهندسی و ارزش ارجاعی کتاب:</p>
<ul>
<li>اصطلاحات کلیدی معماری نظیر <em>Coupling</em> (کوپلینگ)، <em>Connascence</em> (هم‌زادی)، <em>Fitness Function</em> (تابع برازش)، <em>Architecture Quantum</em> (کوانتوم معماری)، <em>Trade-off</em> (بده‌بستان)، <em>ADR</em> و نام سبک‌ها در اولین کاربرد همراه با معادل انگلیسی آورده شده‌اند.</li>
<li>اسامی توابع، قطعه‌کدها، دستورهای شل و متغیرها دقیقاً به زبان انگلیسی و با جهت LTR قالب‌بندی شده‌اند.</li>
<li>در انتهای هر فصل جدولی اختصاصی تحت عنوان «واژه‌نامه» قرار گرفته تا خواننده با معادل‌های دقیق هر فصل آشنا شود.</li>
</ul>

<h2 id="ساختار-مخزن">🗂️ ساختار مخزن گیت‌هاب<a class="headerlink" href="#ساختار-مخزن" title="Permanent link">#</a></h2>
<pre><code class="language-text">.
├── markdown/                # متن فصل‌ها در قالب Markdown (chapter-01.md تا chapter-27.md + appendix.md + glossary.md)
├── html/                    # نسخهٔ HTML غنی‌شده فصول برای مطالعه مستقیم
├── pdf/                     # خروجی کتاب کامل و تک‌فصل‌ها
│   ├── book.pdf             # ۶۵۰ صفحه کتاب یکپارچه
│   ├── chapters/            # فصول تفکیک‌شده
│   └── fonts/               # قلم‌های فارسی و لاتین
├── figures/                 # ۲۴۱ شکل کتاب در ۲۷ پوشه
├── build_book.py            # اسکریپت ادغام فصول و ساخت book.md و book.html
├── build_pdf.py             # اسکریپت کامپایل PDF با Playwright و PyMuPDF
├── insert_figures.py        # درج دقیق شکل‌ها در متون
├── qa.py                    # آزمون‌های کنترل کیفیت ساختاری و زبانی
├── LICENSE                  # مجوز GPL-3.0
└── README.md                # مستندات پروژه
</code></pre>

<h2 id="مشارکت-در-پروژه">🤝 مشارکت در ویرایش و بهبود کتاب<a class="headerlink" href="#مشارکت-در-پروژه" title="Permanent link">#</a></h2>
<p>ترجمهٔ یک اثر مرجع ۶۵۰ صفحه‌ای همواره می‌تواند با دیدگاه‌ها و بازخوردهای متخصصان پخته‌تر و غنی‌تر شود. از مشارکت تمام مهندسان نرم‌افزار، معماران و دانشجویان صمیمانه استقبال می‌کنیم:</p>
<ul>
<li>اگر غلط املایی، نگارشی یا ابهامی در معادل‌سازی مشاهده کردید، می‌توانید در صفحهٔ گیت‌هاب یک <strong>Issue</strong> باز کنید.</li>
<li>پیشنهادهای اصلاحی را می‌توانید مستقیماً در قالب <strong>Pull Request</strong> ارسال نمایید.</li>
<li>پیش از ارسال، اسکریپت <code>python3 qa.py</code> را اجرا کنید تا از درستی ساختار فایل‌ها اطمینان حاصل شود.</li>
</ul>

<h2 id="حمایت-از-پروژه">⭐ حمایت از پروژه<a class="headerlink" href="#حمایت-از-پروژه" title="Permanent link">#</a></h2>
<p>اگر مطالعهٔ این کتاب و در دسترس بودن این منبع فارسی برای شما یا تیم‌تان مفید و ارزشمند بوده است، می‌توانید از راه‌های زیر به تداوم و توسعهٔ پروژه‌های مشابه کمک کنید:</p>
<ul>
<li><strong>ستاره دادن (Star) به مخزن گیت‌هاب</strong> و معرفی کتاب به همکاران و شبکه‌های اجتماعی مهندسی نرم‌افزار.</li>
<li><strong>حمایت مالی:</strong> از طریق صفحهٔ <a href="/support/">حمایت مالی از علی رستمی</a> جهت تأمین هزینه‌های سرورها و انگیزه برای ترجمه آثار بعدی.</li>
</ul>

<h2 id="درباره-اثر-اصلی">⚖️ دربارهٔ اثر اصلی و نویسندگان<a class="headerlink" href="#درباره-اثر-اصلی" title="Permanent link">#</a></h2>
<p>کتاب <em>Fundamentals of Software Architecture</em> اثر مارک ریچاردز و نیل فورد از شناخته‌شده‌ترین و کاربردی‌ترین مراجع آموزش معماری نرم‌افزار مدرن در دنیاست که توسط انتشارات معتبر O&rsquo;Reilly به چاپ رسیده است. تمرکز این کتاب فراتر از تئوری‌های انتزاعی، بر روی مهندسی عملیاتی، تحلیل بده‌بستان‌ها و توانمندسازی افراد برای تبدیل شدن به معمارانی موفق و واقع‌گرا است.</p>

<hr>
<p style="text-align: center; font-size: 0.9rem; color: #64748b;">
این پروژه با افتخار به عنوان هدیه‌ای به جامعهٔ مهندسی نرم‌افزار فارسی‌زبان تقدیم می‌گردد.
</p>
</div>
</article></div>
            </main><footer class="footer">
        <div class="footer-container"><div class="footer-line">ایجاد شده توسط <a href="https://gohugo.io/" target="_blank" rel="noopener noreffer" title="Hugo 0.92.2">Hugo</a> | پوسته - <a href="https://github.com/dillonzq/LoveIt" target="_blank" rel="noopener noreffer" title="LoveIt 0.2.11"><i class="far fa-kiss-wink-heart fa-fw" aria-hidden="true"></i> LoveIt</a>
                </div><div class="footer-line" itemscope itemtype="http://schema.org/CreativeWork"><i class="far fa-copyright fa-fw" aria-hidden="true"></i><span itemprop="copyrightYear">2022 - 2026</span><span class="author" itemprop="copyrightHolder">&nbsp;<a href="/fa/" target="_blank">علی رستمی</a></span></div>
        </div>
    </footer></div>

        <div id="fixed-buttons"><a href="#" id="back-to-top" class="fixed-button" title="برگشت به بالا">
                <i class="fas fa-arrow-up fa-fw" aria-hidden="true"></i>
            </a>
        </div><script type="text/javascript" src="/js/theme.min.js"></script></body>
</html>
"""

def main():
    target_dir = ROOT / "fundamentals-of-software-architecture-persian"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    target_index = target_dir / "index.html"
    target_index.write_text(HTML_TEMPLATE, encoding="utf-8")
    print(f"Written: {target_index} ({len(HTML_TEMPLATE)} bytes)")

    # Alias 1: root .html file
    alias1 = ROOT / "fundamentals-of-software-architecture-persian.html"
    alias1.write_text(HTML_TEMPLATE, encoding="utf-8")
    print(f"Written alias: {alias1}")

    # Alias 2: Capitalized folder
    cap_dir = ROOT / "Fundamentals-of-Software-Architecture-Persian"
    cap_dir.mkdir(parents=True, exist_ok=True)
    alias2 = cap_dir / "index.html"
    alias2.write_text(HTML_TEMPLATE, encoding="utf-8")
    print(f"Written alias: {alias2}")

if __name__ == "__main__":
    main()
