#!/usr/bin/env python3
"""No-cache local preview with Cloudflare-style routes and redirects.

The server understands the generated ``_redirects`` manifest and serves
``chapter.html`` when the browser requests the canonical extensionless
``/chapter`` route. For the closest deployment emulation, use Wrangler instead:

    npx --yes wrangler@latest pages dev . --port 8788

Basic dependency-free preview:

    python3 scripts/devserver.py [port]
"""

from __future__ import annotations

import functools
import http.server
import os
import socketserver
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def redirects() -> dict[str, tuple[str, int]]:
    """Load the generated Pages redirect manifest."""
    rules: dict[str, tuple[str, int]] = {}
    manifest = ROOT / "_redirects"
    if not manifest.is_file():
        return rules
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        source, destination, status = line.split()
        rules[source] = (destination, int(status))
    return rules


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_header(self, keyword: str, value: str) -> None:
        if keyword.lower() == "last-modified":  # stop 304 revalidation entirely
            return
        super().send_header(keyword, value)

    def send_head(self):  # type: ignore[no-untyped-def]
        # Drop conditional headers so the base handler can never answer 304.
        for name in ("If-Modified-Since", "If-None-Match"):
            while name in self.headers:
                del self.headers[name]

        parsed = urllib.parse.urlsplit(self.path)
        rule = redirects().get(parsed.path)
        if rule:
            destination, status = rule
            if parsed.query:
                separator = "&" if "?" in destination else "?"
                destination = f"{destination}{separator}{parsed.query}"
            self.send_response(status)
            self.send_header("Location", destination)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        # Match Cloudflare Pages' canonical extensionless HTML handling.
        decoded_path = urllib.parse.unquote(parsed.path)
        relative = decoded_path.lstrip("/")
        if relative and not Path(relative).suffix and (ROOT / f"{relative}.html").is_file():
            encoded_html_path = urllib.parse.quote(f"/{relative}.html", safe="/%")
            self.path = urllib.parse.urlunsplit(
                (parsed.scheme, parsed.netloc, encoded_html_path, parsed.query, parsed.fragment)
            )

        return super().send_head()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with Server(("0.0.0.0", port), functools.partial(Handler, directory=ROOT)) as httpd:
        print(f"serving {ROOT} on http://0.0.0.0:{port} (cache disabled)", flush=True)
        httpd.serve_forever()
