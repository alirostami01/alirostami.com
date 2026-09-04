#!/usr/bin/env python3
"""Audit every wallet QR code on the site.

For each HTML page it finds every /images/donate/*.png (or .svg) image, picks up
the wallet address shown in the same card (a <code> element or the data-address
of the copy button), decodes the QR image and reports whether the decoded
payload is byte-for-byte identical to the displayed address.

    pip install opencv-python-headless segno pillow
    python3 scripts/verify-wallet-qr.py
"""

import re
import sys
from pathlib import Path

import cv2
import segno

ROOT = Path(__file__).resolve().parent.parent
IMG_RE = re.compile(r'<img[^>]+src="(/images/donate/([a-z0-9-]+)\.png)"[^>]*>', re.I)
CODE_RE = re.compile(r"<code[^>]*>([^<]+)</code>")
DATA_RE = re.compile(r'data-address="([^"]+)"')

# addresses of record (the single source of truth used by the generators)
EXPECTED = {
    "bitcoin": "bc1qg7xap7ys84j6s0zj7e607whwgak4gvzttw0yew",
    "usdt-trc20": "TEL83d98uJqtVcJfttjjK7dCEB7q9g7fg",
    "ethereum": "0xD52B0e8a6244e1c155285020191199524349292f",
    "solana": "BEXuadMGmKCPJQ7ZAvB4HooYjn6psMXARzr2doeie4y9",
}

SKIP_DIRS = {".git", "node_modules", "lib", "css", "js"}


def decode(png: Path) -> str:
    image = cv2.imread(str(png))
    if image is None:
        return ""
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    return text


def card_address(html: str, img_start: int, img_end: int, prev_end: int, next_start: int) -> str:
    """Address printed inside the same wallet card as this image.

    Every card renders as: heading -> <img> -> <code>address</code> -> copy button,
    so the address is looked for *after* the image first and only then before it,
    always staying inside the slice that belongs to this card (between the
    previous and the next QR image on the page).
    """
    after = html[img_end:next_start]
    before = html[prev_end:img_start]
    for chunk in (after, before):
        codes = CODE_RE.findall(chunk)
        datas = DATA_RE.findall(chunk)
        if codes:
            return codes[0].strip()
        if datas:
            return datas[0].strip()
    return ""


def main() -> int:
    decoded_cache: dict[str, str] = {}
    rows = []
    failures = 0

    pages = sorted(
        p
        for p in ROOT.rglob("*.html")
        if not any(part in SKIP_DIRS for part in p.parts)
    )

    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        matches = list(IMG_RE.finditer(html))
        for i, m in enumerate(matches):
            src, slug = m.group(1), m.group(2)
            png = ROOT / src.lstrip("/")
            if src not in decoded_cache:
                decoded_cache[src] = decode(png)
            payload = decoded_cache[src]
            prev_end = matches[i - 1].end() if i else 0
            next_start = matches[i + 1].start() if i + 1 < len(matches) else len(html)
            shown = card_address(html, m.start(), m.end(), prev_end, next_start)
            expected = EXPECTED.get(slug, "")
            ok = payload and payload == shown == expected
            failures += 0 if ok else 1
            rows.append(
                (
                    str(page.relative_to(ROOT)),
                    slug,
                    "OK" if ok else "MISMATCH",
                    shown,
                    payload,
                )
            )

    width = max((len(r[0]) for r in rows), default=10)
    print(f"{'page'.ljust(width)}  {'wallet'.ljust(12)}  status")
    print("-" * (width + 26))
    for page, slug, status, shown, payload in rows:
        print(f"{page.ljust(width)}  {slug.ljust(12)}  {status}")
        if status != "OK":
            print(f"    shown on page: {shown!r}")
            print(f"    inside the QR: {payload!r}")

    # cross-check the standalone SVG twins (same payload, vector output)
    print("\nSVG twins (not referenced by any page, kept for print/retina use):")
    for slug, address in EXPECTED.items():
        svg = ROOT / "images" / "donate" / f"{slug}.svg"
        if not svg.exists():
            print(f"  {slug.ljust(12)}  MISSING")
            failures += 1
            continue
        fresh = ROOT / "images" / "donate" / f".{slug}.check.svg"
        segno.make(address, error="h").save(
            fresh, scale=10, border=4, dark="#000000", light="#ffffff"
        )
        identical = fresh.read_bytes() == svg.read_bytes()
        fresh.unlink()
        print(f"  {slug.ljust(12)}  {'OK' if identical else 'MISMATCH'}")
        failures += 0 if identical else 1

    print(f"\n{len(rows)} QR images checked on {len(pages)} pages — "
          f"{'all consistent' if failures == 0 else str(failures) + ' problem(s)'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
