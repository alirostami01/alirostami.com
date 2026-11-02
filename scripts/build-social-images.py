#!/usr/bin/env python3
"""Build deterministic 1200×630 social cards and right-sized content images.

Requires Pillow:

    python3 -m pip install pillow
    python3 scripts/build-social-images.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from image_utils import (
    ROOT,
    SOCIAL_CARDS,
    SOCIAL_HEIGHT,
    SOCIAL_WIDTH,
    apply_site_postprocessors,
)

FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ROOT / "lib" / "katex" / "fonts" / "KaTeX_SansSerif-Bold.ttf",
)
REGULAR_FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ROOT / "lib" / "katex" / "fonts" / "KaTeX_SansSerif-Regular.ttf",
)


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]


def font(candidates: tuple[Path, ...], size: int) -> ImageFont.FreeTypeFont:
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    raise FileNotFoundError("No suitable TrueType font was found")


def gradient(start: str, end: str) -> Image.Image:
    first, second = rgb(start), rgb(end)
    image = Image.new("RGB", (SOCIAL_WIDTH, SOCIAL_HEIGHT))
    draw = ImageDraw.Draw(image)
    for x in range(SOCIAL_WIDTH):
        ratio = x / (SOCIAL_WIDTH - 1)
        color = tuple(round(a + (b - a) * ratio) for a, b in zip(first, second))
        draw.line((x, 0, x, SOCIAL_HEIGHT), fill=color)
    return image


def rounded_panel(image: Image.Image, box: tuple[int, int, int, int], radius: int = 34) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(box, radius=radius, fill=(255, 255, 255, 24), outline=(255, 255, 255, 54), width=2)
    image.paste(overlay, (0, 0), overlay)


def paste_rounded_photo(canvas: Image.Image, source: Path, box: tuple[int, int, int, int]) -> None:
    width, height = box[2] - box[0], box[3] - box[1]
    photo = ImageOps.fit(Image.open(source).convert("RGB"), (width, height), Image.Resampling.LANCZOS, centering=(0.5, 0.4))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width, height), radius=30, fill=255)
    canvas.paste(photo, box[:2], mask)


def paste_icon(canvas: Image.Image, source: Path, center: tuple[int, int], size: int) -> None:
    icon = Image.open(source).convert("RGBA")
    icon.thumbnail((size, size), Image.Resampling.LANCZOS)
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    radius = size // 2 + 22
    glow_draw.ellipse(
        (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        fill=(30, 210, 230, 44),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    canvas.paste(glow, (0, 0), glow)
    position = (center[0] - icon.width // 2, center[1] - icon.height // 2)
    canvas.paste(icon, position, icon)


def draw_card(key: str) -> Path:
    card = SOCIAL_CARDS[key]
    image = gradient(card.colors[0], card.colors[1]).convert("RGBA")
    draw = ImageDraw.Draw(image)
    accent = rgb(card.colors[2])

    # Subtle technical grid and framing make the cards recognizable without
    # competing with their text at small preview sizes.
    for x in range(0, SOCIAL_WIDTH, 60):
        draw.line((x, 0, x, SOCIAL_HEIGHT), fill=(255, 255, 255, 10), width=1)
    for y in range(0, SOCIAL_HEIGHT, 60):
        draw.line((0, y, SOCIAL_WIDTH, y), fill=(255, 255, 255, 10), width=1)
    draw.rectangle((34, 34, SOCIAL_WIDTH - 34, SOCIAL_HEIGHT - 34), outline=(*accent, 120), width=2)
    draw.line((65, 86, 710, 86), fill=(*accent, 210), width=6)

    panel = (790, 92, 1135, 538)
    rounded_panel(image, panel)
    sources = tuple(ROOT / source for source in card.source_images)
    if card.presentation == "portrait":
        paste_rounded_photo(image, sources[0], (810, 112, 1115, 518))
    elif card.presentation == "grid":
        positions = ((875, 212), (1048, 212), (875, 412), (1048, 412))
        for source, position in zip(sources, positions):
            paste_icon(image, source, position, 132)
    else:
        paste_icon(image, sources[0], (962, 315), 285)

    draw = ImageDraw.Draw(image)
    title_size = 54 if len(card.title) > 1 else 64
    title_font = font(FONT_CANDIDATES, title_size)
    subtitle_font = font(REGULAR_FONT_CANDIDATES, 25)
    badge_font = font(FONT_CANDIDATES, 20)
    site_font = font(REGULAR_FONT_CANDIDATES, 19)

    y = 160 if len(card.title) == 1 else 126
    for line in card.title:
        draw.text((72, y), line, font=title_font, fill=(250, 252, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0, 80))
        y += title_size + 18
    draw.text((75, y + 28), card.subtitle, font=subtitle_font, fill=(*accent, 255))

    badge_box = (74, 438, 74 + max(250, int(draw.textlength(card.badge, font=badge_font)) + 54), 490)
    draw.rounded_rectangle(badge_box, radius=26, fill=(*accent, 36), outline=(*accent, 180), width=2)
    draw.text((badge_box[0] + 26, badge_box[1] + 13), card.badge, font=badge_font, fill=(244, 249, 255, 255))
    draw.text((74, 551), "www.alirostami.com", font=site_font, fill=(214, 226, 240, 230))

    card.path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(card.path, "JPEG", quality=88, optimize=True, progressive=True, subsampling="4:2:0")
    return card.path


def build_responsive_content_images() -> list[Path]:
    outputs: list[Path] = []

    portrait = Image.open(ROOT / "images" / "Ali.jpg").convert("RGB")
    for size in (256, 512):
        output = ROOT / "images" / f"Ali-{size}.jpg"
        resized = ImageOps.fit(portrait, (size, size), Image.Resampling.LANCZOS)
        resized.save(output, "JPEG", quality=86, optimize=True, progressive=True, subsampling="4:2:0")
        outputs.append(output)

    cover = Image.open(ROOT / "figures" / "aima-4e-persian.jpeg").convert("RGB")
    width = 960
    height = round(cover.height * width / cover.width)
    cover = cover.resize((width, height), Image.Resampling.LANCZOS)
    cover_output = ROOT / "figures" / "aima-4e-persian-960.jpg"
    cover.save(cover_output, "JPEG", quality=85, optimize=True, progressive=True, subsampling="4:2:0")
    outputs.append(cover_output)
    return outputs


def main() -> None:
    generated = [draw_card(key) for key in SOCIAL_CARDS]
    generated.extend(build_responsive_content_images())
    for path in generated:
        print(f"generated {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")
    apply_site_postprocessors()


if __name__ == "__main__":
    main()
