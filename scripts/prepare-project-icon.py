#!/usr/bin/env python3
"""Normalise a project icon for the support page.

Drop the original logo anywhere, then run:

    python3 scripts/prepare-project-icon.py ~/Downloads/logo.png persian-subtitles
    python3 scripts/prepare-project-icon.py ~/Downloads/logo2.png persian-streams

It makes the flat white/solid background around a round logo transparent,
squares + resizes the image to 256x256 and writes it to
images/projects/<slug>.png — exactly where the support page expects it.

Valid slugs: persian-subtitles, persian-streams
(then run: python3 scripts/build-support-page.py)
"""

import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "images" / "projects"
SIZE = 256
TOLERANCE = 28  # how close to white/uniform a border pixel must be to be cut out


def make_border_transparent(im: Image.Image, tol: int = TOLERANCE) -> Image.Image:
    """Flood-fill from the image border and clear pixels close to the corner colour."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    base = px[0, 0][:3]
    if not all(c >= 255 - tol for c in base):
        # corner is not white-ish: keep the background as-is
        return im
    seen = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y][x]:
            continue
        r, g, b, _ = px[x, y]
        if r >= 255 - tol and g >= 255 - tol and b >= 255 - tol:
            seen[y][x] = True
            px[x, y] = (r, g, b, 0)
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def square(im: Image.Image) -> Image.Image:
    w, h = im.size
    if w == h:
        return im
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2))
    return canvas


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    src, slug = Path(sys.argv[1]).expanduser(), sys.argv[2]
    if not src.exists():
        raise SystemExit(f"file not found: {src}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    im = square(make_border_transparent(Image.open(src)))
    im = im.resize((SIZE, SIZE), Image.LANCZOS)
    dest = OUT_DIR / f"{slug}.png"
    im.save(dest, optimize=True)
    print(f"wrote {dest.relative_to(ROOT)} ({dest.stat().st_size} bytes, {SIZE}x{SIZE})")
    print("now run: python3 scripts/build-support-page.py")


if __name__ == "__main__":
    main()
