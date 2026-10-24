#!/usr/bin/env python3
"""Updates sitemap.xml and fa/sitemap.xml with software architecture URLs and validates XML."""

import os
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
TODAY = "2026-10-24"

MAIN_URLS = [
    ("https://alirostami.ir/", "daily", "1.0"),
    ("https://alirostami.ir/fa/", "daily", "1.0"),
    ("https://alirostami.ir/software-architecture/", "weekly", "0.95"),
    ("https://alirostami.ir/fundamentals-of-software-architecture-persian/", "weekly", "0.90"),
    ("https://alirostami.ir/aima-4e/", "weekly", "0.95"),
    ("https://alirostami.ir/aima-4e-persian/", "weekly", "0.90"),
    ("https://alirostami.ir/persian-streams/", "weekly", "0.90"),
    ("https://alirostami.ir/persian-subtitles/", "weekly", "0.90"),
    ("https://alirostami.ir/support/", "monthly", "0.85"),
    ("https://alirostami.ir/posts/", "weekly", "0.85"),
    ("https://alirostami.ir/posts/fundamentals-of-software-architecture-persian/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/aima-4e-persian/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/persian-streams/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/persian-subtitles/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/benefits-of-using-obsidian/", "monthly", "0.70"),
    ("https://alirostami.ir/posts/a-recap-of-last-year/", "monthly", "0.70"),
    ("https://alirostami.ir/en/support.html", "monthly", "0.70"),
]

FA_MAIN_URLS = [
    ("https://alirostami.ir/fa/", "daily", "1.0"),
    ("https://alirostami.ir/software-architecture/", "weekly", "0.95"),
    ("https://alirostami.ir/fundamentals-of-software-architecture-persian/", "weekly", "0.90"),
    ("https://alirostami.ir/aima-4e/", "weekly", "0.95"),
    ("https://alirostami.ir/aima-4e-persian/", "weekly", "0.90"),
    ("https://alirostami.ir/persian-streams/", "weekly", "0.90"),
    ("https://alirostami.ir/persian-subtitles/", "weekly", "0.90"),
    ("https://alirostami.ir/support/", "monthly", "0.85"),
    ("https://alirostami.ir/posts/", "weekly", "0.85"),
    ("https://alirostami.ir/posts/fundamentals-of-software-architecture-persian/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/aima-4e-persian/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/persian-streams/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/persian-subtitles/", "monthly", "0.80"),
    ("https://alirostami.ir/posts/benefits-of-using-obsidian/", "monthly", "0.70"),
    ("https://alirostami.ir/posts/a-recap-of-last-year/", "monthly", "0.70"),
]

# Get AIMA 4e chapters
aima_dir = ROOT / "aima-4e"
aima_files = sorted([f.name for f in aima_dir.glob("*.html") if f.name != "index.html"])

# Get Software Architecture chapters
sa_dir = ROOT / "software-architecture"
sa_files = [f"chapter-{i:02d}.html" for i in range(1, 28)] + ["appendix.html"]

def generate_sitemap(url_list, include_sa_chapters=True, include_aima_chapters=True):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]

    for loc, freq, prio in url_list:
        lines.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""")

    if include_sa_chapters:
        for f in sa_files:
            lines.append(f"""  <url>
    <loc>https://alirostami.ir/software-architecture/{f}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.75</priority>
  </url>""")

    if include_aima_chapters:
        import urllib.parse
        for f in aima_files:
            encoded_f = urllib.parse.quote(f)
            lines.append(f"""  <url>
    <loc>https://alirostami.ir/aima-4e/{encoded_f}</loc>
    <lastmod>2026-10-21</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.75</priority>
  </url>""")

    lines.append('</urlset>\n')
    return "\n".join(lines)

def main():
    root_sitemap = generate_sitemap(MAIN_URLS, True, True)
    fa_sitemap = generate_sitemap(FA_MAIN_URLS, True, True)

    (ROOT / "sitemap.xml").write_text(root_sitemap, encoding="utf-8")
    (ROOT / "fa" / "sitemap.xml").write_text(fa_sitemap, encoding="utf-8")

    # Validate XML
    ET.fromstring(root_sitemap)
    ET.fromstring(fa_sitemap)
    print("Sitemaps generated and XML validated successfully!")

if __name__ == "__main__":
    main()
