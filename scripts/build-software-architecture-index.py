#!/usr/bin/env python3
"""Build the book reader for Fundamentals of Software Architecture (software-architecture/index.html)
and prepare all chapter files with theme-awareness, section deep-linking IDs, image fixes, and standalone helpers.
"""

import os
import re
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = ROOT / "software-architecture"

PARTS = [
    {
        "id": "part-1",
        "title": "بخش اول: مبانی",
        "desc": "فصل‌های ۱ تا ۸: مفاهیم پایه، ماژولاریتی، ویژگی‌های معماری و تفکر مؤلفه‌محور",
        "range": (1, 8),
    },
    {
        "id": "part-2",
        "title": "بخش دوم: سبک‌های معماری",
        "desc": "فصل‌های ۹ تا ۲۰: معماری‌های لایه‌ای، خط لوله، میکروکرنل، رویدادمحور، فضاپایه و میکروسرویس‌ها",
        "range": (9, 20),
    },
    {
        "id": "part-3",
        "title": "بخش سوم: تکنیک‌ها و مهارت‌های نرم",
        "desc": "فصل‌های ۲۱ تا ۲۷: تصمیم‌گیری، تحلیل ریسک، نمودارکشی، اثربخشی تیم، مذاکره و رهبری",
        "range": (21, 27),
    },
    {
        "id": "part-appendix",
        "title": "پیوست و منابع",
        "desc": "پرسش‌های بحث و مرور نهایی",
        "range": (999, 999),
    },
]


def process_chapters():
    """Reads raw chapter HTML, fixes image paths, injects section IDs, wraps in full HTML."""
    chapter_files = sorted([f for f in BOOK_DIR.glob("chapter-*.html")])
    appendix_file = BOOK_DIR / "appendix.html"
    all_files = list(chapter_files)
    if appendix_file.exists():
        all_files.append(appendix_file)

    chapters_info = []

    for fpath in all_files:
        fname = fpath.name
        content = fpath.read_text(encoding="utf-8")

        # Extract H1 title
        h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", content)
        raw_h1 = h1_m.group(1).strip() if h1_m else fname
        raw_h1_clean = re.sub(r"<[^>]+>", "", raw_h1).strip()

        # Determine badge and clean short title
        if fname.startswith("chapter-"):
            ch_num = int(re.search(r"chapter-(\d+)", fname).group(1))
            badge = f"فصل {ch_num}"
            if " — " in raw_h1_clean:
                short_title = raw_h1_clean.split(" — ", 1)[1]
            elif ":" in raw_h1_clean:
                short_title = raw_h1_clean.split(":", 1)[1].strip()
            else:
                short_title = raw_h1_clean
        else:
            ch_num = 999
            badge = "پیوست"
            if ":" in raw_h1_clean:
                short_title = raw_h1_clean.split(":", 1)[1].strip()
            else:
                short_title = raw_h1_clean

        # Fix relative image paths: ../figures/ -> figures/
        content = re.sub(r'src=["\']\.\./figures/', 'src="figures/', content)

        # Inject section IDs into H3 (and H2 if any)
        sections = []
        sec_idx = 1

        def replace_h3(match):
            nonlocal sec_idx
            attrs = match.group(1) or ""
            inner = match.group(2)
            clean_text = re.sub(r"<[^>]+>", "", inner).strip()
            sec_id = f"sec-{sec_idx}"
            sec_idx += 1
            sections.append({
                "id": sec_id,
                "title": clean_text,
                "href": f"#{sec_id}",
            })
            # Preserve existing styles but ensure id is set
            if "id=" not in attrs:
                return f'<h3 id="{sec_id}"{attrs}>{inner}</h3>'
            return match.group(0)

        # Remove existing IDs if any, then re-inject
        content = re.sub(r'<h3([^>]*)>(.*?)</h3>', replace_h3, content, flags=re.DOTALL)

        # Build clean standalone wrapped HTML if not already wrapped
        if "<!DOCTYPE html>" not in content:
            # Strip outer article wrapper inline styles to let CSS handle it
            content = re.sub(r'<article[^>]*>', '<article class="chapter-content">', content, count=1)
            
            wrapped_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{raw_h1_clean} — مبانی معماری نرم‌افزار</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css">
    <style>
        :root {{
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1a1a1a;
            --text-muted: #555555;
            --border-color: #e2e8f0;
            --accent: #2c5f8a;
            --accent-soft: #eef4fa;
            --wine: #8b2942;
            --code-bg: #f1f5f9;
        }}
        [data-theme="dark"], [theme="dark"] {{
            --bg: #0b1120;
            --card-bg: #1e293b;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent: #38bdf8;
            --accent-soft: rgba(56, 189, 248, 0.12);
            --wine: #fb7185;
            --code-bg: #0f172a;
        }}
        * {{ box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{
            margin: 0;
            padding: 24px 16px 80px;
            font-family: Vazirmatn, "IRANSans", "Segoe UI", Tahoma, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 2;
            direction: rtl;
        }}
        .chapter-content {{
            max-width: 50rem;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 2.2rem;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            box-shadow: 0 4px 18px rgba(0,0,0,.04);
        }}
        h1 {{
            font-size: 1.85rem;
            margin: 0 0 1.2rem;
            border-bottom: 3px solid var(--accent);
            padding-bottom: .6rem;
            color: var(--accent);
            line-height: 1.4;
        }}
        h3 {{
            font-size: 1.35rem;
            color: var(--accent);
            margin: 2.4rem 0 .9rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: .4rem;
            line-height: 1.4;
            scroll-margin-top: 1rem;
        }}
        h4 {{
            font-size: 1.15rem;
            color: var(--accent);
            margin: 1.6rem 0 .6rem;
            line-height: 1.4;
        }}
        p {{
            text-align: justify;
            margin: 0 0 1.2rem;
        }}
        figure {{
            margin: 1.6rem 0;
            padding: 1.2rem;
            background: var(--accent-soft);
            border-right: 4px solid var(--accent);
            border-radius: 8px;
            text-align: center;
        }}
        figure img {{
            display: block;
            max-width: 100%;
            height: auto;
            margin: 0 auto .9rem;
            background: #fff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }}
        figcaption {{
            font-size: .95rem;
            color: var(--text-main);
            line-height: 1.8;
            text-align: justify;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.6rem 0;
            font-size: .95rem;
        }}
        table th, table td {{
            border: 1px solid var(--border-color);
            padding: .6rem .8rem;
        }}
        table th {{
            background: var(--accent);
            color: #fff;
        }}
        bdi {{
            font-family: Consolas, Monaco, monospace;
            direction: ltr;
            unicode-bidi: isolate;
        }}
        pre, code {{
            font-family: Consolas, Monaco, monospace;
            direction: ltr;
            unicode-bidi: isolate;
        }}
        pre {{
            background: var(--code-bg);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            overflow-x: auto;
            color: var(--text-main);
        }}
        section.support {{
            margin: 0 0 1.8rem;
            padding: 1.1rem 1.3rem;
            background: var(--accent-soft);
            border-right: 5px solid var(--accent);
            border-radius: 6px;
        }}
        section.support a {{
            color: var(--accent);
            font-weight: 600;
        }}
        hr {{
            border: none;
            border-top: 1px dashed var(--border-color);
            margin: 2rem 0;
        }}
        @media (max-width: 640px) {{
            .chapter-content {{
                padding: 1.2rem;
            }}
            body {{
                padding: 10px 8px 60px;
            }}
            h1 {{
                font-size: 1.5rem;
            }}
            h3 {{
                font-size: 1.2rem;
            }}
        }}
    </style>
    <script>
        (function() {{
            var t = localStorage.getItem('theme');
            if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
                document.documentElement.setAttribute('theme', 'dark');
                document.documentElement.setAttribute('data-theme', 'dark');
            }}
            window.addEventListener('message', function(e) {{
                if (e.data && e.data.theme) {{
                    document.documentElement.setAttribute('theme', e.data.theme);
                    document.documentElement.setAttribute('data-theme', e.data.theme);
                }}
            }});
        }})();
    </script>
</head>
<body>
{content}
<script id="fosa-standalone-helper">
  if (window.self === window.top) {{
    window.addEventListener('DOMContentLoaded', function() {{
      var b = document.createElement('a');
      b.href = 'index.html#{fname}';
      b.target = '_top';
      b.style.cssText = 'position:fixed;bottom:22px;left:22px;background:#1e293b;color:#fff;padding:9px 16px;border-radius:24px;box-shadow:0 6px 18px rgba(0,0,0,.25);text-decoration:none;font-size:13px;font-family:Tahoma,sans-serif;z-index:99999;display:inline-flex;align-items:center;gap:6px;border:1px solid rgba(255,255,255,.2);';
      b.innerHTML = '📖 باز کردن در کتابخوان با سایدبار';
      document.body.appendChild(b);
    }});
  }}
</script>
</body>
</html>"""
            fpath.write_text(wrapped_html, encoding="utf-8")
        else:
            # File was already wrapped, update content
            fpath.write_text(content, encoding="utf-8")

        chapters_info.append({
            "filename": fname,
            "ch_num": ch_num,
            "badge": badge,
            "raw_title": raw_h1_clean,
            "short_title": short_title,
            "sections": sections,
        })

    return chapters_info


def build_reader_index(chapters):
    """Generates the interactive reader index software-architecture/index.html."""
    # Build sidebar HTML with 3 Parts accordion
    sidebar_items_html = []

    for part in PARTS:
        part_chapters = [
            c for c in chapters
            if part["range"][0] <= c["ch_num"] <= part["range"][1]
        ]
        if not part_chapters:
            continue

        part_header = f"""
        <div class="part-header" id="{part['id']}">
            <div class="part-title-wrapper">
                <i class="fas fa-layer-group part-icon"></i>
                <span class="part-title">{part['title']}</span>
            </div>
            <span class="part-desc">{part['desc']}</span>
        </div>
        """
        sidebar_items_html.append(part_header)

        for c in part_chapters:
            ch_idx = chapters.index(c)
            ch_id = f"ch-item-{ch_idx}"
            badge_html = f'<span class="ch-badge">{c["badge"]}</span>'

            sec_html = []
            for s in c["sections"]:
                sec_href = f"{c['filename']}{s['href']}"
                sec_html.append(
                    f'<li class="sec-item">'
                    f'<a href="{sec_href}" data-ch-idx="{ch_idx}" data-file="{c["filename"]}" data-hash="{s["href"]}" class="sec-link">'
                    f'<span class="sec-dot"></span><span class="sec-text">{s["title"]}</span>'
                    f'</a></li>'
                )

            sections_ul = f'<ul class="ch-sections" id="sections-{ch_idx}">{"".join(sec_html)}</ul>' if sec_html else ""
            chevron = f'<i class="fas fa-chevron-left ch-chevron" aria-hidden="true"></i>' if sec_html else ""

            sidebar_items_html.append(f"""
            <div class="ch-card" id="{ch_id}" data-idx="{ch_idx}" data-file="{c['filename']}">
                <div class="ch-header" data-idx="{ch_idx}">
                    <a href="{c['filename']}" class="ch-title-link" data-idx="{ch_idx}" data-file="{c['filename']}">
                        {badge_html}
                        <span class="ch-title">{c['short_title']}</span>
                    </a>
                    {chevron}
                </div>
                {sections_ul}
            </div>
            """)

    sidebar_content = "\n".join(sidebar_items_html)
    chapters_json = json.dumps(chapters, ensure_ascii=False)

    reader_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="index, follow">
    <script>
        if (window.self !== window.top) {{
            window.top.location = window.location.href;
        }}
    </script>
    <title>مبانی معماری نرم‌افزار (ویرایش دوم) — مطالعهٔ آنلاین با فهرست و سایدبار</title>
    <meta name="Description" content="نسخهٔ وب و سامانهٔ مطالعهٔ آنلاین ترجمهٔ فارسی کتاب مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن اثر مارک ریچاردز و نیل فورد (ویرایش دوم، ۲۰۲۵) شامل ۲۷ فصل، پیوست و واژه‌نامه.">
    <meta property="og:title" content="مبانی معماری نرم‌افزار — مطالعه آنلاین کتاب">
    <meta property="og:description" content="مطالعه آنلاین ترجمه فارسی کتاب مبانی معماری نرم‌افزار اثر مارک ریچاردز و نیل فورد با سایدبار کامل، ۲۷ فصل، واژه‌نامه و جستجوی پیشرفته.">
    <meta property="og:type" content="book">
    <meta property="og:url" content="https://alirostami.ir/software-architecture/">
    <link rel="canonical" href="https://alirostami.ir/software-architecture/">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
    <link rel="stylesheet" href="/css/style.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "Book",
                "@id": "https://alirostami.ir/software-architecture/#book",
                "name": "مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن (ویرایش دوم)",
                "alternateName": "Fundamentals of Software Architecture: A Modern Engineering Approach 2nd Edition",
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
                "url": "https://alirostami.ir/software-architecture/",
                "description": "نسخه وب و مطالعه آنلاین ترجمه کامل فارسی کتاب مبانی معماری نرم‌افزار: رویکردی مهندسی و مدرن با سایدبار هوشمند، فهرست فصول، بخش‌بندی سه‌گانه و امکان جستجو."
            }},
            {{
                "@type": "BreadcrumbList",
                "@id": "https://alirostami.ir/software-architecture/#breadcrumb",
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
                        "name": "مطالعه آنلاین کتاب معماری نرم‌افزار",
                        "item": "https://alirostami.ir/software-architecture/"
                    }}
                ]
            }}
        ]
    }}
    </script>
    <style>
        :root {{
            --sidebar-width: 350px;
            --top-header-height: 56px;
            --reader-bg: #f8fafc;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --accent: #2563eb;
            --accent-soft: #eff6ff;
            --brand-primary: #1e3a8a;
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
            --brand-primary: #60a5fa;
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
            transition: transform .3s ease;
            z-index: 30;
        }}
        .sidebar-search-box {{
            padding: .85rem;
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
            padding: .45rem 2.2rem .45rem .75rem;
            border-radius: 6px;
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
            padding: .4rem .85rem;
            font-size: .75rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            background: var(--reader-bg);
        }}
        .sidebar-controls a {{
            color: var(--accent);
            cursor: pointer;
            text-decoration: none;
        }}
        .sidebar-controls a:hover {{
            text-decoration: underline;
        }}
        .sidebar-scroll {{
            flex: 1;
            overflow-y: auto;
            padding: .5rem;
        }}
        .sidebar-scroll::-webkit-scrollbar {{
            width: 6px;
        }}
        .sidebar-scroll::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 3px;
        }}

        /* Part Headers in Sidebar */
        .part-header {{
            margin: 1rem 0 .4rem;
            padding: .4rem .6rem;
            background: var(--accent-soft);
            border-radius: 6px;
            border-right: 3px solid var(--accent);
        }}
        .part-title-wrapper {{
            display: flex;
            align-items: center;
            gap: .4rem;
            color: var(--accent);
            font-weight: 700;
            font-size: .85rem;
        }}
        .part-desc {{
            display: block;
            font-size: .72rem;
            color: var(--text-muted);
            margin-top: .15rem;
            line-height: 1.4;
        }}

        /* Chapter Card */
        .ch-card {{
            margin-bottom: .35rem;
            border-radius: 6px;
            transition: background .15s;
        }}
        .ch-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: .45rem .6rem;
            border-radius: 6px;
            cursor: pointer;
            user-select: none;
            transition: all .15s;
        }}
        .ch-header:hover {{
            background: var(--accent-soft);
        }}
        .ch-card.active > .ch-header {{
            background: var(--accent-soft);
            color: var(--accent);
            font-weight: 700;
        }}
        .ch-title-link {{
            display: flex;
            align-items: center;
            gap: .5rem;
            text-decoration: none;
            color: inherit;
            flex: 1;
            min-width: 0;
        }}
        .ch-badge {{
            font-size: .7rem;
            font-weight: 600;
            padding: .15rem .4rem;
            border-radius: 4px;
            background: var(--border-color);
            color: var(--text-muted);
            flex-shrink: 0;
        }}
        .ch-card.active .ch-badge {{
            background: var(--accent);
            color: #fff;
        }}
        .ch-title {{
            font-size: .88rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .ch-chevron {{
            font-size: .75rem;
            color: var(--text-muted);
            transition: transform .2s ease;
            margin-right: .3rem;
        }}
        .ch-card.expanded .ch-chevron {{
            transform: rotate(-90deg);
        }}

        /* Section Sub-items */
        .ch-sections {{
            list-style: none;
            margin: 0;
            padding: .2rem 0 .4rem 0;
            display: none;
            border-right: 2px solid var(--border-color);
            margin-right: .9rem;
        }}
        .ch-card.expanded .ch-sections {{
            display: block;
        }}
        .sec-item {{
            margin: 0;
        }}
        .sec-link {{
            display: flex;
            align-items: center;
            gap: .5rem;
            padding: .3rem .6rem;
            font-size: .82rem;
            color: var(--text-muted);
            text-decoration: none;
            border-radius: 4px;
            transition: all .15s;
        }}
        .sec-link:hover {{
            color: var(--accent);
            background: var(--accent-soft);
        }}
        .sec-link.active {{
            color: var(--accent);
            font-weight: 600;
            background: var(--accent-soft);
        }}
        .sec-dot {{
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: var(--text-muted);
            opacity: .4;
            flex-shrink: 0;
        }}
        .sec-link.active .sec-dot {{
            background: var(--accent);
            opacity: 1;
        }}
        .sec-text {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* Main Content Frame */
        .reader-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            background: var(--reader-bg);
            position: relative;
            overflow: hidden;
        }}
        .reader-toolbar {{
            height: 44px;
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 1rem;
            font-size: .85rem;
            z-index: 10;
        }}
        .toolbar-title {{
            display: flex;
            align-items: center;
            gap: .5rem;
            font-weight: 600;
            color: var(--text-main);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
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
        <button class="btn-header mobile-toggle" id="btn-toggle-sidebar" title="فهرست و سایدبار">
            <i class="fas fa-bars fa-fw"></i>
            <span>فهرست فصول</span>
        </button>
        <div class="header-brand-group">
            <a href="/fa/" class="btn-home-return" title="بازگشت به سایت اصلی علی رستمی">
                <i class="fas fa-home fa-fw"></i>
                <span>سایت اصلی</span>
            </a>
            <span class="brand-divider">/</span>
            <a href="index.html" class="header-brand" title="مطالعه آنلاین کتاب مبانی معماری نرم‌افزار">
                <i class="fas fa-cubes book-icon"></i>
                <span class="brand-title-text">مبانی معماری نرم‌افزار</span>
                <span class="header-brand-badge">ویرایش دوم</span>
            </a>
        </div>
    </div>

    <div class="header-actions">
        <a href="/fundamentals-of-software-architecture-persian/" class="btn-header" title="معرفی و مشخصات پروژه">
            <i class="fas fa-info-circle fa-fw"></i>
            <span class="d-none-sm">دربارهٔ پروژه</span>
        </a>
        <a href="https://github.com/alirostami01/Fundamentals-of-Software-Architecture_-A-Modern-Engineering-Approach/raw/main/pdf/book.pdf" target="_blank" rel="noopener noreferrer" class="btn-header primary" title="دانلود کل کتاب PDF از گیت‌هاب (۶۵۰ صفحه)">
            <i class="fas fa-file-pdf fa-fw"></i>
            <span class="d-none-sm">دانلود PDF</span>
        </a>
        <a href="https://github.com/alirostami01/Fundamentals-of-Software-Architecture_-A-Modern-Engineering-Approach" target="_blank" rel="noopener noreferrer" class="btn-header" title="مخزن گیت‌هاب">
            <i class="fab fa-github fa-fw"></i>
        </a>
        <a href="/support/" class="btn-header" title="حمایت از پروژه">
            <i class="fas fa-heart fa-fw" style="color:#e0245e;"></i>
        </a>
        <button class="btn-header" id="btn-theme-toggle" title="تغییر ظاهر تاریک/روشن">
            <i class="fas fa-adjust fa-fw"></i>
        </button>
    </div>
</header>

<div class="reader-workspace">
    <!-- Sidebar -->
    <aside class="reader-sidebar" id="reader-sidebar">
        <div class="sidebar-search-box">
            <div class="search-wrapper-inner">
                <i class="fas fa-search" aria-hidden="true"></i>
                <input type="search" id="sidebar-search" class="search-input" placeholder="جستجو در ۲۷ فصل و بخش‌ها..." autocomplete="off">
            </div>
        </div>
        <div class="sidebar-controls">
            <span>فهرست فصول (۲۷ فصل + پیوست)</span>
            <div style="display:flex;gap:.5rem;">
                <a id="btn-expand-all">باز کردن همه</a>
                <span>·</span>
                <a id="btn-collapse-all">بستن همه</a>
            </div>
        </div>
        <div class="sidebar-scroll" id="sidebar-scroll">
            {sidebar_content}
        </div>
    </aside>

    <div class="sidebar-backdrop" id="sidebar-backdrop"></div>

    <!-- Main Content Reader -->
    <main class="reader-content">
        <div class="reader-toolbar">
            <div class="toolbar-title" id="current-title">
                <i class="fas fa-book-open" style="color:var(--accent);"></i>
                <span id="title-text">فصل ۱: مقدمه</span>
            </div>
            <div class="toolbar-nav">
                <button class="btn-tool" id="btn-prev-chapter" title="فصل قبلی (کلید ←)">
                    <i class="fas fa-chevron-right fa-fw"></i>
                    <span>قبلی</span>
                </button>
                <button class="btn-tool" id="btn-next-chapter" title="فصل بعدی (کلید →)">
                    <span>بعدی</span>
                    <i class="fas fa-chevron-left fa-fw"></i>
                </button>
                <button class="btn-tool" id="btn-refresh-frame" title="بارگذاری مجدد این فصل">
                    <i class="fas fa-redo fa-fw"></i>
                </button>
                <a class="btn-tool" id="btn-direct-link" target="_blank" title="باز کردن در برگهٔ جداگانه">
                    <i class="fas fa-external-link-alt fa-fw"></i>
                </a>
            </div>
        </div>

        <div class="frame-container">
            <iframe id="book-frame" name="book-frame" src="chapter-01.html" title="کتابخوان معماری نرم‌افزار"></iframe>
        </div>
    </main>
</div>

<script>
    const CHAPTERS = {chapters_json};

    let currentChapterIdx = 0;
    const iframe = document.getElementById('book-frame');
    const titleText = document.getElementById('title-text');
    const btnPrev = document.getElementById('btn-prev-chapter');
    const btnNext = document.getElementById('btn-next-chapter');
    const btnDirect = document.getElementById('btn-direct-link');
    const btnRefresh = document.getElementById('btn-refresh-frame');
    const sidebar = document.getElementById('reader-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    const searchInput = document.getElementById('sidebar-search');

    function syncThemeToFrame() {{
        const theme = document.body.getAttribute('theme') || 'light';
        try {{
            if (iframe.contentWindow) {{
                iframe.contentWindow.postMessage({{ theme: theme }}, '*');
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                if (doc && doc.documentElement) {{
                    doc.documentElement.setAttribute('theme', theme);
                    doc.documentElement.setAttribute('data-theme', theme);
                }}
            }}
        }} catch(e) {{}}
    }}

    iframe.addEventListener('load', () => {{
        syncThemeToFrame();
        try {{
            const win = iframe.contentWindow;
            win.addEventListener('hashchange', () => {{
                updateActiveSectionLink(win.location.hash);
            }});
        }} catch(e) {{}}
    }});

    function loadChapter(idx, hash = '') {{
        if (idx < 0 || idx >= CHAPTERS.length) return;
        currentChapterIdx = idx;
        const ch = CHAPTERS[idx];

        titleText.textContent = `${{ch.badge}}: ${{ch.short_title}}`;
        document.title = `${{ch.badge}}: ${{ch.short_title}} — مبانی معماری نرم‌افزار`;

        btnPrev.disabled = (idx === 0);
        btnNext.disabled = (idx === CHAPTERS.length - 1);
        btnDirect.href = ch.filename + hash;

        // Update active chapter in sidebar
        document.querySelectorAll('.ch-card').forEach(card => card.classList.remove('active'));
        const activeCard = document.getElementById(`ch-item-${{idx}}`);
        if (activeCard) {{
            activeCard.classList.add('active');
            activeCard.classList.add('expanded');
            if (window.innerWidth > 900) {{
                activeCard.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}

        // Update iframe source
        const targetSrc = ch.filename + hash;
        if (iframe.getAttribute('src') !== targetSrc) {{
            iframe.src = targetSrc;
        }} else if (hash) {{
            try {{
                iframe.contentWindow.location.hash = hash;
            }} catch(e) {{
                iframe.src = targetSrc;
            }}
        }}

        // Update URL hash
        const stateHash = '#' + ch.filename + (hash ? hash : '');
        if (location.hash !== stateHash) {{
            history.replaceState(null, '', stateHash);
        }}

        updateActiveSectionLink(hash);
        closeSidebar();
    }}

    function updateActiveSectionLink(hash) {{
        document.querySelectorAll('.sec-link').forEach(l => l.classList.remove('active'));
        if (hash) {{
            const link = document.querySelector(`.sec-link[data-ch-idx="${{currentChapterIdx}}"][data-hash="${{hash}}"]`);
            if (link) link.classList.add('active');
        }}
    }}

    // Chapter header click accordion & load
    document.querySelectorAll('.ch-header').forEach(header => {{
        header.addEventListener('click', (e) => {{
            const idx = parseInt(header.getAttribute('data-idx'));
            const card = header.closest('.ch-card');
            
            if (e.target.closest('.ch-chevron')) {{
                card.classList.toggle('expanded');
                return;
            }}
            
            e.preventDefault();
            card.classList.toggle('expanded');
            loadChapter(idx);
        }});
    }});

    // Section sub-link click
    document.querySelectorAll('.sec-link').forEach(link => {{
        link.addEventListener('click', (e) => {{
            e.preventDefault();
            const idx = parseInt(link.getAttribute('data-ch-idx'));
            const hash = link.getAttribute('data-hash') || '';
            loadChapter(idx, hash);
        }});
    }});

    // Toolbar Navigation Buttons
    btnPrev.addEventListener('click', () => {{
        if (currentChapterIdx > 0) loadChapter(currentChapterIdx - 1);
    }});
    btnNext.addEventListener('click', () => {{
        if (currentChapterIdx < CHAPTERS.length - 1) loadChapter(currentChapterIdx + 1);
    }});
    btnRefresh.addEventListener('click', () => {{
        iframe.src = iframe.src;
    }});

    // Expand/Collapse All
    document.getElementById('btn-expand-all').addEventListener('click', () => {{
        document.querySelectorAll('.ch-card').forEach(c => c.classList.add('expanded'));
    }});
    document.getElementById('btn-collapse-all').addEventListener('click', () => {{
        document.querySelectorAll('.ch-card').forEach(c => c.classList.remove('expanded'));
    }});

    // Instant Sidebar Search Filter
    searchInput.addEventListener('input', (e) => {{
        const q = e.target.value.trim().toLowerCase();
        if (!q) {{
            document.querySelectorAll('.ch-card').forEach(card => card.style.display = '');
            document.querySelectorAll('.sec-item').forEach(sec => sec.style.display = '');
            document.querySelectorAll('.part-header').forEach(p => p.style.display = '');
            return;
        }}
        document.querySelectorAll('.part-header').forEach(p => p.style.display = 'none');
        document.querySelectorAll('.ch-card').forEach(card => {{
            const title = card.querySelector('.ch-title').textContent.toLowerCase();
            const badge = card.querySelector('.ch-badge').textContent.toLowerCase();
            let matchesSec = false;
            card.querySelectorAll('.sec-item').forEach(sec => {{
                const sText = sec.textContent.toLowerCase();
                if (sText.includes(q)) {{
                    sec.style.display = '';
                    matchesSec = true;
                }} else {{
                    sec.style.display = 'none';
                }}
            }});
            if (title.includes(q) || badge.includes(q) || matchesSec) {{
                card.style.display = '';
                card.classList.add('expanded');
            }} else {{
                card.style.display = 'none';
            }}
        }});
    }});

    // Mobile Sidebar Drawer
    function openSidebar() {{
        sidebar.classList.add('open');
        backdrop.classList.add('open');
    }}
    function closeSidebar() {{
        sidebar.classList.remove('open');
        backdrop.classList.remove('open');
    }}
    document.getElementById('btn-toggle-sidebar').addEventListener('click', openSidebar);
    backdrop.addEventListener('click', closeSidebar);

    // Theme Switcher Button
    document.getElementById('btn-theme-toggle').addEventListener('click', () => {{
        const current = document.body.getAttribute('theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('theme', next);
        document.body.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        syncThemeToFrame();
    }});

    // Deep link from Hash on initial load
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
            const idx = CHAPTERS.findIndex(c => c.filename === targetFile);
            if (idx !== -1) {{
                loadChapter(idx, targetHash);
                return;
            }}
        }}
        loadChapter(0);
    }});

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {{
        if (e.target.tagName === 'INPUT') return;
        if (e.key === 'ArrowLeft') btnNext.click();
        if (e.key === 'ArrowRight') btnPrev.click();
    }});
</script>
</body>
</html>"""

    final_html = reader_html
    out_file = BOOK_DIR / "index.html"
    out_file.write_text(final_html, encoding="utf-8")
    print(f"Generated {out_file} ({len(final_html)} bytes)")


if __name__ == "__main__":
    print("Processing chapters...")
    chapters = process_chapters()
    print(f"Processed {len(chapters)} chapters.")
    print("Building reader index...")
    build_reader_index(chapters)
    print("Done!")
