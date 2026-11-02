#!/usr/bin/env python3
"""Generate static fallback pages for legacy URL aliases.

Permanent redirects are enforced at the CDN/edge (Cloudflare). These tiny
`noindex` pages are a safe fallback for environments where the edge rules are
not active, and keep duplicate full-content documents out of the repository.
"""

from __future__ import annotations

import csv
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://www.alirostami.com"

# Repository path -> canonical URL path. Keep this list in sync with the
# Cloudflare redirects documented in README.md.
ALIASES: dict[str, str] = {
    # Home/language and generated pagination aliases
    "fa/index.html": "/",
    "en/index.html": "/",
    "fa/categories/index.html": "/categories/",
    "fa/tags/index.html": "/tags/",
    "page/1/index.html": "/",
    "backup-index.html": "/",
    "posts/page/1/index.html": "/posts/",
    # Clean English support URL
    "en/support.html": "/en/support/",
    # Persian support aliases
    "support.html": "/support/",
    "fa/support/index.html": "/support/",
    "fa/support.html": "/support/",
    # Project aliases: casing, extension, and old post routes
    "AIMA-4E-Persian/index.html": "/aima-4e-persian/",
    "aima-4e-persian.html": "/aima-4e-persian/",
    "Fundamentals-of-Software-Architecture-Persian/index.html": "/fundamentals-of-software-architecture-persian/",
    "fundamentals-of-software-architecture-persian.html": "/fundamentals-of-software-architecture-persian/",
    "Persian-Streams/index.html": "/persian-streams/",
    "posts/persian-streams/index.html": "/persian-streams/",
    "Persian-Subtitles/index.html": "/persian-subtitles/",
    "posts/persian-subtitles/index.html": "/persian-subtitles/",
}

# These old XML endpoints no longer have static fallback documents. They still
# need edge redirects so existing feed subscriptions and indexed sitemap URLs
# reach their canonical replacements.
EDGE_ONLY_ALIASES: dict[str, str] = {
    # Explicit index filenames for canonical directory pages
    "/index.html": "/",
    "/categories/index.html": "/categories/",
    "/tags/index.html": "/tags/",
    "/support/index.html": "/support/",
    "/en/support/index.html": "/en/support/",
    "/software-architecture/index.html": "/software-architecture/",
    "/aima-4e/index.html": "/aima-4e/",
    "/fundamentals-of-software-architecture-persian/index.html": "/fundamentals-of-software-architecture-persian/",
    "/aima-4e-persian/index.html": "/aima-4e-persian/",
    "/persian-streams/index.html": "/persian-streams/",
    "/persian-subtitles/index.html": "/persian-subtitles/",
    "/posts/index.html": "/posts/",
    "/posts/fundamentals-of-software-architecture-persian/index.html": "/posts/fundamentals-of-software-architecture-persian/",
    "/posts/aima-4e-persian/index.html": "/posts/aima-4e-persian/",
    "/posts/benefits-of-using-obsidian/index.html": "/posts/benefits-of-using-obsidian/",
    "/posts/a-recap-of-last-year/index.html": "/posts/a-recap-of-last-year/",
    # Retired language-specific feeds and sitemaps
    "/fa/sitemap.xml": "/sitemap.xml",
    "/en/sitemap.xml": "/sitemap.xml",
    "/public/sitemap.xml": "/sitemap.xml",
    "/public/fa/sitemap.xml": "/sitemap.xml",
    "/fa/index.xml": "/index.xml",
    "/fa/categories/index.xml": "/categories/index.xml",
    "/fa/tags/index.xml": "/tags/index.xml",
}


def absolute_url(destination: str) -> str:
    if not destination.startswith("/"):
        raise ValueError(f"redirect destination must start with '/': {destination!r}")
    return f"{BASE_URL}{destination}"


def render_redirect(destination: str) -> str:
    """Return a crawl-safe HTML fallback for an edge-managed redirect."""
    url = absolute_url(destination)
    escaped_url = escape(url, quote=True)
    escaped_path = escape(destination)
    return f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>انتقال دائمی به {escaped_path}</title>
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="{escaped_url}">
  <meta http-equiv="refresh" content="0; url={escaped_url}">
  <script>window.location.replace({url!r} + window.location.search + window.location.hash);</script>
</head>
<body>
  <p>این نشانی منتقل شده است. <a href="{escaped_url}">رفتن به نشانی اصلی</a></p>
</body>
</html>
"""


def write_redirect(path: Path, destination: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_redirect(destination), encoding="utf-8")


def edge_aliases() -> dict[str, str]:
    """Return every path Cloudflare Pages should redirect.

    Folder aliases include slashless and explicit ``index.html`` spellings so
    historical links take one hop directly to the preferred absolute URL.
    """
    routes = dict(EDGE_ONLY_ALIASES)

    # Cloudflare Pages serves HTML documents at extensionless URLs and otherwise
    # emits its own 308 for explicit .html requests. Override those historical
    # chapter URLs with a deliberate 301 to the canonical extensionless route.
    for path in sorted((ROOT / "software-architecture").glob("*.html")):
        if path.name == "index.html":
            continue
        source = f"/software-architecture/{path.name}"
        routes[source] = source.removesuffix(".html")
    for path in sorted((ROOT / "aima-4e").glob("*.html")):
        if path.name == "index.html":
            continue
        source = f"/aima-4e/{quote(path.name)}"
        routes[source] = f"/aima-4e/{quote(path.stem)}"

    for relative_path, destination in ALIASES.items():
        explicit = f"/{relative_path}"
        routes[explicit] = destination
        if explicit.endswith("/index.html"):
            folder = explicit[: -len("index.html")]
            routes[folder] = destination
            routes[folder.rstrip("/")] = destination
    return dict(sorted(routes.items()))


def write_edge_manifest(root: Path = ROOT) -> None:
    lines = [
        f"{source} {absolute_url(destination)} 301"
        for source, destination in edge_aliases().items()
    ]
    (root / "_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"edge manifest: /_redirects ({len(lines)} permanent redirects)")


def bulk_redirect_rows() -> list[tuple[str, ...]]:
    """Return an importable Cloudflare Bulk Redirect List.

    Exact alias entries for both hostnames take users straight to the final URL.
    The final two subpath rules normalize all remaining non-preferred host and
    HTTP-www requests while preserving both path suffix and query string.
    """
    rows: list[tuple[str, ...]] = []
    for source, destination in edge_aliases().items():
        target = absolute_url(destination)
        for host in ("alirostami.com", "www.alirostami.com"):
            rows.append((f"{host}{source}", target, "301", "true", "false", "false", "false"))

    rows.extend(
        [
            (
                "alirostami.com/",
                f"{BASE_URL}/",
                "301",
                "true",
                "false",
                "true",
                "true",
            ),
            (
                "http://www.alirostami.com/",
                f"{BASE_URL}/",
                "301",
                "true",
                "false",
                "true",
                "true",
            ),
        ]
    )
    return rows


def write_bulk_manifest(root: Path = ROOT) -> None:
    path = root / "cloudflare-bulk-redirects.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(bulk_redirect_rows())
    print(f"bulk manifest: /{path.name} ({len(bulk_redirect_rows())} redirects)")


def write_all(root: Path = ROOT) -> None:
    for relative_path, destination in ALIASES.items():
        write_redirect(root / relative_path, destination)
        print(f"redirect fallback: /{relative_path} -> {destination}")
    write_edge_manifest(root)
    write_bulk_manifest(root)


if __name__ == "__main__":
    write_all()
