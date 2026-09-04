#!/usr/bin/env python3
"""Static preview server for the site with caching disabled.

`python3 -m http.server` answers conditional requests with 304, which makes a
browser keep showing an old QR image after a wallet address changes. This
variant sends no-store headers so the preview is always the files on disk.

    python3 scripts/devserver.py [port]
"""
import functools, http.server, os, socketserver, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_header(self, keyword, value):
        if keyword.lower() == "last-modified":   # stop 304 revalidation entirely
            return
        super().send_header(keyword, value)

    def send_head(self):
        # drop the conditional header so the base handler can never answer 304
        for name in ("If-Modified-Since", "If-None-Match"):
            while name in self.headers:
                del self.headers[name]
        return super().send_head()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with Server(("0.0.0.0", port), functools.partial(Handler, directory=ROOT)) as httpd:
        print(f"serving {ROOT} on http://0.0.0.0:{port} (cache disabled)", flush=True)
        httpd.serve_forever()
