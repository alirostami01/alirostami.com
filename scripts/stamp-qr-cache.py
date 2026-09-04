#!/usr/bin/env python3
"""Stamp every QR image URL with a content hash so browsers can never show a
stale wallet QR code after an address change.

Rewrites  /images/donate/usdt-trc20.png            ->  ...png?v=e913312f
and       /images/donate/usdt-trc20.png?v=oldhash  ->  ...png?v=e913312f

Idempotent: run it after generate-wallet-qr.py / build-support-page.py.

    python3 scripts/stamp-qr-cache.py
"""

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "lib"}
URL_RE = re.compile(r'(/images/donate/([a-z0-9-]+)\.(?:png|svg))(\?v=[0-9a-f]+)?')


def digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def main() -> int:
    hashes: dict[str, str] = {}
    changed = []

    for page in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in page.parts):
            continue
        html = page.read_text(encoding="utf-8")

        def repl(m: re.Match) -> str:
            url = m.group(1)
            asset = ROOT / url.lstrip("/")
            if not asset.exists():
                return m.group(0)
            if url not in hashes:
                hashes[url] = digest(asset)
            return f"{url}?v={hashes[url]}"

        stamped = URL_RE.sub(repl, html)
        if stamped != html:
            page.write_text(stamped, encoding="utf-8")
            changed.append(str(page.relative_to(ROOT)))

    for url, h in sorted(hashes.items()):
        print(f"{url}  ->  ?v={h}")
    print(f"\n{len(changed)} file(s) updated" + (":" if changed else ""))
    for name in changed:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
