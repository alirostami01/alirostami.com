#!/usr/bin/env python3
"""Generate edge-only redirects and remove static legacy alias documents.

Canonical content exists at exactly one lowercase repository path. Historical
case variants, parallel ``page.html`` spellings, pagination, and retired routes
are represented only in the Cloudflare redirect manifests.
"""

from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import quote

from aima_routes import AIMA_CHAPTER_ROUTE_MAP, malformed_legacy_stem
from software_architecture_routes import SOFTWARE_ARCHITECTURE_ROUTE_MAP

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://www.alirostami.com"

# Former repository path -> canonical URL path. These paths must not exist as
# static documents; they are retained here solely to generate edge redirects.
LEGACY_PAGE_ALIASES: dict[str, str] = {
    # Home/language and generated pagination aliases
    "fa/index.html": "/",
    "en/index.html": "/",
    "fa/categories/index.html": "/posts/",
    "fa/tags/index.html": "/posts/",
    "page/1/index.html": "/",
    "backup-index.html": "/",
    "posts/page/1/index.html": "/posts/",
    # Retired language, taxonomy, and term sections
    "en/support/index.html": "/support/",
    "en/support.html": "/support/",
    "categories/index.html": "/posts/",
    "categories/index.xml": "/index.xml",
    "tags/index.html": "/posts/",
    "tags/index.xml": "/index.xml",
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
    "/support/index.html": "/support/",
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
    "/fa/categories/index.xml": "/index.xml",
    "/fa/tags/index.xml": "/index.xml",
}


def absolute_url(destination: str) -> str:
    if not destination.startswith("/"):
        raise ValueError(f"redirect destination must start with '/': {destination!r}")
    return f"{BASE_URL}{destination}"


def remove_static_aliases(root: Path = ROOT) -> list[str]:
    """Delete legacy alias documents and now-empty alias-only directories."""
    removed: list[str] = []
    for relative_path in LEGACY_PAGE_ALIASES:
        path = root / relative_path
        if not path.is_file():
            continue
        path.unlink()
        removed.append(relative_path)

        parent = path.parent
        while parent != root:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent

    for relative_path in removed:
        print(f"removed static alias: /{relative_path}")
    return removed


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

    # Generic chapter-NN and appendix routes were the original public URLs.
    # Keep both their extensionless and .html spellings as direct aliases.
    for legacy_stem, canonical_stem in SOFTWARE_ARCHITECTURE_ROUTE_MAP:
        destination = f"/software-architecture/{canonical_stem}"
        routes[f"/software-architecture/{legacy_stem}"] = destination
        routes[f"/software-architecture/{legacy_stem}.html"] = destination

    for path in sorted((ROOT / "aima-4e").glob("*.html")):
        if path.name == "index.html":
            continue
        source = f"/aima-4e/{quote(path.name)}"
        routes[source] = f"/aima-4e/{quote(path.stem)}"

    # Preserve every pre-migration AIMA URL in one hop.  Both the actual
    # Persian slugs and the previously reported blank-title spellings are edge
    # aliases only; no duplicate HTML documents are kept indexable.
    for chapter_number, (legacy_stem, canonical_stem) in enumerate(AIMA_CHAPTER_ROUTE_MAP):
        destination = f"/aima-4e/{canonical_stem}"
        for old_stem in (legacy_stem, malformed_legacy_stem(chapter_number)):
            encoded_stem = quote(old_stem)
            routes[f"/aima-4e/{encoded_stem}"] = destination
            routes[f"/aima-4e/{encoded_stem}.html"] = destination

    for relative_path, destination in LEGACY_PAGE_ALIASES.items():
        explicit = f"/{relative_path}"
        routes[explicit] = destination
        if explicit.endswith("/index.html"):
            folder = explicit[: -len("index.html")]
            routes[folder] = destination
            routes[folder.rstrip("/")] = destination
    return dict(sorted(routes.items()))


def write_edge_manifest(root: Path = ROOT) -> None:
    remove_static_aliases(root)
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
    write_edge_manifest(root)
    write_bulk_manifest(root)


if __name__ == "__main__":
    write_all()
