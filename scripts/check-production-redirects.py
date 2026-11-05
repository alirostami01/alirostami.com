#!/usr/bin/env python3
"""Verify Phase-1 redirects and canonical URLs after deployment.

By default this checks production. To exercise Cloudflare Pages locally:

    npx wrangler pages dev . --port 8788
    python3 scripts/check-production-redirects.py --origin http://127.0.0.1:8788

The local mode validates the Pages ``_redirects`` manifest but intentionally
skips scheme/host normalization, which only exists at the Cloudflare zone.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from redirects import BASE_URL, absolute_url, edge_aliases


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


OPENER = urllib.request.build_opener(NoRedirect)
USER_AGENT = "alirostami.com phase-1 SEO deployment audit/1.0"


def request(url: str, timeout: float) -> tuple[int, str]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with OPENER.open(req, timeout=timeout) as response:
            return response.status, response.headers.get("Location", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Location", "")


def fetch(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with OPENER.open(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"GET {url} returned HTTP {response.status}")
        return response.read()


def at_origin(origin: str, path: str, query: str = "") -> str:
    return f"{origin.rstrip('/')}{path}" + (f"?{query}" if query else "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--origin",
        default=BASE_URL,
        help="request origin (default: production preferred origin)",
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="check representative canonical pages instead of every sitemap URL",
    )
    args = parser.parse_args()

    origin = args.origin.rstrip("/")
    query = "phase1_audit=1"
    errors: list[str] = []
    checks = 0

    # Every legacy path must issue one permanent hop directly to its preferred
    # absolute destination while preserving the query string.
    for source, destination in edge_aliases().items():
        url = at_origin(origin, source, query)
        expected = f"{absolute_url(destination)}?{query}"
        try:
            status, location = request(url, args.timeout)
        except Exception as exc:  # network/DNS/TLS failures are audit failures
            errors.append(f"{url}: {exc}")
            continue
        checks += 1
        if status != 301:
            errors.append(f"{url}: expected 301, got {status}")
        if location != expected:
            errors.append(f"{url}: expected Location {expected!r}, got {location!r}")

    # These rules are zone-level and cannot be represented by Pages _redirects.
    if origin == BASE_URL:
        non_preferred_origins = (
            "http://alirostami.com",
            "https://alirostami.com",
            "http://www.alirostami.com",
        )
        for source_origin in non_preferred_origins:
            source = at_origin(source_origin, "/support/", query)
            expected = f"{BASE_URL}/support/?{query}"
            try:
                status, location = request(source, args.timeout)
            except Exception as exc:
                errors.append(f"{source}: {exc}")
                continue
            checks += 1
            if status != 301 or location != expected:
                errors.append(
                    f"{source}: expected 301 -> {expected!r}, got {status} -> {location!r}"
                )

        # Representative aliases on every non-preferred origin catch missing or
        # disabled Bulk Redirect rules (and accidental two-hop host redirects).
        aliases = edge_aliases()
        representative_sources = (
            "/fa/",
            "/AIMA-4E-Persian/",
            "/en/support.html",
            "/categories/",
            "/tags/",
            "/software-architecture/chapter-01.html",
            "/fa/index.xml",
        )
        for source_origin in non_preferred_origins:
            for source_path in representative_sources:
                source = at_origin(source_origin, source_path, query)
                expected = f"{absolute_url(aliases[source_path])}?{query}"
                try:
                    status, location = request(source, args.timeout)
                except Exception as exc:
                    errors.append(f"{source}: {exc}")
                    continue
                checks += 1
                if status != 301 or location != expected:
                    errors.append(
                        f"{source}: expected one-hop 301 -> {expected!r}, "
                        f"got {status} -> {location!r}"
                    )

    # The canonical sitemap must be reachable and all listed URLs must resolve
    # directly with HTTP 200 (no redirect).
    try:
        sitemap_bytes = fetch(at_origin(origin, "/sitemap.xml"), args.timeout)
        sitemap = ET.fromstring(sitemap_bytes)
        locations = [node.text or "" for node in sitemap.iter() if node.tag.endswith("loc")]
    except Exception as exc:
        errors.append(f"sitemap: {exc}")
        locations = []

    if args.quick:
        wanted = {
            f"{BASE_URL}/",
            f"{BASE_URL}/support/",
            f"{BASE_URL}/aima-4e/",
            f"{BASE_URL}/software-architecture/",
        }
        locations = [location for location in locations if location in wanted]

    for location in locations:
        parsed = urllib.parse.urlparse(location)
        local_url = at_origin(origin, parsed.path)
        try:
            status, redirect = request(local_url, args.timeout)
        except Exception as exc:
            errors.append(f"{local_url}: {exc}")
            continue
        checks += 1
        if status != 200 or redirect:
            errors.append(
                f"canonical {location}: expected 200 without Location, got {status} {redirect!r}"
            )

    if errors:
        print(f"Production redirect audit failed with {len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    mode = "production" if origin == BASE_URL else f"local origin {origin}"
    print(f"Production redirect audit passed against {mode}: {checks} HTTP checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
