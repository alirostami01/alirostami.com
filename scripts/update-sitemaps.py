#!/usr/bin/env python3
"""Generate the single canonical sitemap for alirostami.com.

Only 200-status canonical pages belong in the sitemap. Legacy language
sitemaps and URL aliases are intentionally excluded and are redirected at the
Cloudflare edge.
"""

from __future__ import annotations

import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://www.alirostami.com"
TODAY = datetime.now(ZoneInfo("Asia/Tehran")).date().isoformat()

# URL path, repository file, change frequency, priority. The latter two are
# retained for compatibility, although Google primarily uses loc + lastmod.
MAIN_PAGES = [
    ("/", "index.html", "weekly", "1.0"),
    ("/software-architecture/", "software-architecture/index.html", "weekly", "0.95"),
    (
        "/fundamentals-of-software-architecture-persian/",
        "fundamentals-of-software-architecture-persian/index.html",
        "weekly",
        "0.90",
    ),
    ("/aima-4e/", "aima-4e/index.html", "weekly", "0.95"),
    ("/aima-4e-persian/", "aima-4e-persian/index.html", "weekly", "0.90"),
    ("/persian-streams/", "persian-streams/index.html", "weekly", "0.90"),
    ("/persian-subtitles/", "persian-subtitles/index.html", "weekly", "0.90"),
    ("/support/", "support/index.html", "monthly", "0.75"),
    ("/posts/", "posts/index.html", "weekly", "0.80"),
    (
        "/posts/fundamentals-of-software-architecture-persian/",
        "posts/fundamentals-of-software-architecture-persian/index.html",
        "monthly",
        "0.75",
    ),
    ("/posts/aima-4e-persian/", "posts/aima-4e-persian/index.html", "monthly", "0.75"),
    (
        "/posts/benefits-of-using-obsidian/",
        "posts/benefits-of-using-obsidian/index.html",
        "yearly",
        "0.60",
    ),
    (
        "/posts/a-recap-of-last-year/",
        "posts/a-recap-of-last-year/index.html",
        "yearly",
        "0.50",
    ),
    ("/en/support/", "en/support/index.html", "monthly", "0.60"),
]

LEGACY_INDEX_FILES = (
    ROOT / "fa" / "sitemap.xml",
    ROOT / "en" / "sitemap.xml",
    ROOT / "public" / "sitemap.xml",
    ROOT / "public" / "fa" / "sitemap.xml",
    ROOT / "fa" / "index.xml",
    ROOT / "fa" / "categories" / "index.xml",
    ROOT / "fa" / "tags" / "index.xml",
)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def last_modified(relative_file: str) -> str:
    """Use today for working-tree changes, otherwise the latest Git date."""
    if git("status", "--porcelain", "--", relative_file):
        return TODAY
    committed = git("log", "-1", "--format=%aI", "--", relative_file)
    if committed:
        timestamp = datetime.fromisoformat(committed).astimezone(ZoneInfo("Asia/Tehran"))
        return timestamp.date().isoformat()
    return TODAY


def entries() -> list[tuple[str, str, str, str]]:
    rows = list(MAIN_PAGES)

    for number in range(1, 28):
        filename = f"chapter-{number:02d}.html"
        rows.append(
            (
                f"/software-architecture/{Path(filename).stem}",
                f"software-architecture/{filename}",
                "monthly",
                "0.75",
            )
        )
    rows.append(
        (
            "/software-architecture/appendix",
            "software-architecture/appendix.html",
            "monthly",
            "0.70",
        )
    )

    for file_path in sorted((ROOT / "aima-4e").glob("*.html")):
        if file_path.name == "index.html":
            continue
        encoded_route = urllib.parse.quote(file_path.stem)
        relative = file_path.relative_to(ROOT).as_posix()
        rows.append((f"/aima-4e/{encoded_route}", relative, "monthly", "0.75"))

    return rows


def generate() -> str:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    root = ET.Element(f"{{{namespace}}}urlset")

    seen: set[str] = set()
    for url_path, relative_file, frequency, priority in entries():
        absolute = f"{BASE_URL}{url_path}"
        if absolute in seen:
            raise ValueError(f"duplicate sitemap URL: {absolute}")
        seen.add(absolute)

        source = ROOT / relative_file
        if not source.is_file():
            raise FileNotFoundError(f"sitemap target does not exist: {relative_file}")

        url = ET.SubElement(root, f"{{{namespace}}}url")
        ET.SubElement(url, f"{{{namespace}}}loc").text = absolute
        ET.SubElement(url, f"{{{namespace}}}lastmod").text = last_modified(relative_file)
        ET.SubElement(url, f"{{{namespace}}}changefreq").text = frequency
        ET.SubElement(url, f"{{{namespace}}}priority").text = priority

    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def main() -> None:
    sitemap = generate()
    ET.fromstring(sitemap)
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    for legacy in LEGACY_INDEX_FILES:
        if legacy.exists():
            legacy.unlink()
            print(f"removed legacy index file: {legacy.relative_to(ROOT)}")

    count = len(entries())
    print(f"generated sitemap.xml with {count} canonical URLs")


if __name__ == "__main__":
    main()
