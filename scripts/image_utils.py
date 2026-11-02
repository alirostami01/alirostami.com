#!/usr/bin/env python3
"""Shared Phase-2 image metadata, routing, and intrinsic-size helpers."""

from __future__ import annotations

import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://www.alirostami.com"
SOCIAL_WIDTH = 1200
SOCIAL_HEIGHT = 630


@dataclass(frozen=True)
class SocialCard:
    key: str
    filename: str
    title: tuple[str, ...]
    subtitle: str
    badge: str
    source_images: tuple[str, ...]
    colors: tuple[str, str, str]
    alt_fa: str
    alt_en: str
    presentation: str = "icon"

    @property
    def path(self) -> Path:
        return ROOT / "images" / "social" / self.filename

    @property
    def url(self) -> str:
        return f"{BASE_URL}/images/social/{self.filename}"


SOCIAL_CARDS: dict[str, SocialCard] = {
    "home": SocialCard(
        key="home",
        filename="ali-rostami.jpg",
        title=("ALI ROSTAMI",),
        subtitle="SOFTWARE ARCHITECTURE  ·  AI  ·  OPEN SOURCE",
        badge="ALIROSTAMI.COM",
        source_images=("images/Ali.jpg",),
        colors=("#07182f", "#123c63", "#24b7d8"),
        alt_fa="علی رستمی؛ معماری نرم‌افزار، هوش مصنوعی و پروژه‌های متن‌باز",
        alt_en="Ali Rostami — software architecture, AI, and open-source projects",
        presentation="portrait",
    ),
    "software-architecture": SocialCard(
        key="software-architecture",
        filename="software-architecture.jpg",
        title=("FUNDAMENTALS OF", "SOFTWARE ARCHITECTURE"),
        subtitle="PERSIAN EDITION  ·  ONLINE READER",
        badge="27 CHAPTERS + APPENDIX",
        source_images=("images/projects/fundamentals-of-software-architecture-persian.png",),
        colors=("#071a36", "#173f77", "#17a9de"),
        alt_fa="ترجمه فارسی مبانی معماری نرم‌افزار؛ مطالعه آنلاین ۲۷ فصل و پیوست",
        alt_en="Fundamentals of Software Architecture — Persian edition and online reader",
    ),
    "aima-4e": SocialCard(
        key="aima-4e",
        filename="aima-4e-persian.jpg",
        title=("ARTIFICIAL INTELLIGENCE", "A MODERN APPROACH"),
        subtitle="4TH EDITION  ·  PERSIAN TRANSLATION",
        badge="AIMA 4e",
        source_images=("images/projects/aima-4e-persian.png",),
        colors=("#080f2f", "#18275d", "#f2bb3f"),
        alt_fa="ترجمه فارسی کتاب هوش مصنوعی؛ یک رویکرد مدرن، ویرایش چهارم",
        alt_en="Artificial Intelligence: A Modern Approach, fourth edition — Persian translation",
    ),
    "persian-streams": SocialCard(
        key="persian-streams",
        filename="persian-streams.jpg",
        title=("PERSIAN STREAMS",),
        subtitle="STREMIO ADD-ON  ·  IRANIAN MOVIES & SERIES",
        badge="OPEN SOURCE",
        source_images=("images/projects/persian-streams.png",),
        colors=("#071b35", "#104b6c", "#08c9cf"),
        alt_fa="Persian Streams؛ افزونه استرمیو برای فیلم‌ها و سریال‌های ایرانی",
        alt_en="Persian Streams — a Stremio add-on for Iranian movies and series",
    ),
    "persian-subtitles": SocialCard(
        key="persian-subtitles",
        filename="persian-subtitles.jpg",
        title=("PERSIAN SUBTITLES",),
        subtitle="STREMIO ADD-ON  ·  SMART FARSI SUBTITLES",
        badge="OPEN SOURCE",
        source_images=("images/projects/persian-subtitles.png",),
        colors=("#07172f", "#17445f", "#02c3c9"),
        alt_fa="Persian Subtitles؛ افزونه هوشمند زیرنویس فارسی برای استرمیو",
        alt_en="Persian Subtitles — smart Farsi subtitles for Stremio",
    ),
    "support": SocialCard(
        key="support",
        filename="support-open-source.jpg",
        title=("SUPPORT OPEN SOURCE",),
        subtitle="BOOKS  ·  ADD-ONS  ·  EDUCATION",
        badge="BUILD KNOWLEDGE TOGETHER",
        source_images=(
            "images/projects/fundamentals-of-software-architecture-persian.png",
            "images/projects/aima-4e-persian.png",
            "images/projects/persian-streams.png",
            "images/projects/persian-subtitles.png",
        ),
        colors=("#17112e", "#40235f", "#eb4b79"),
        alt_fa="حمایت از پروژه‌های متن‌باز، ترجمه کتاب‌ها و آموزش‌های علی رستمی",
        alt_en="Support Ali Rostami's open-source projects, book translations, and education",
        presentation="grid",
    ),
    "blog": SocialCard(
        key="blog",
        filename="articles-and-notes.jpg",
        title=("ARTICLES & NOTES",),
        subtitle="SOFTWARE  ·  AI  ·  PRODUCTIVITY",
        badge="ALI ROSTAMI",
        source_images=("images/Ali.jpg",),
        colors=("#111827", "#263754", "#4eb1d2"),
        alt_fa="مقالات و یادداشت‌های علی رستمی درباره نرم‌افزار، هوش مصنوعی و بهره‌وری",
        alt_en="Ali Rostami's articles and notes on software, AI, and productivity",
        presentation="portrait",
    ),
}


def social_card_for_page(relative: str | Path) -> SocialCard:
    """Map a generated HTML file to its representative social card."""
    value = Path(relative).as_posix().lstrip("./")
    lowered = value.lower()
    if value == "index.html":
        return SOCIAL_CARDS["home"]
    if "support" in lowered:
        return SOCIAL_CARDS["support"]
    if lowered.startswith("software-architecture/") or "fundamentals-of-software-architecture" in lowered:
        return SOCIAL_CARDS["software-architecture"]
    if lowered.startswith("aima-4e/") or "aima-4e-persian" in lowered:
        return SOCIAL_CARDS["aima-4e"]
    if "persian-streams" in lowered:
        return SOCIAL_CARDS["persian-streams"]
    if "persian-subtitles" in lowered:
        return SOCIAL_CARDS["persian-subtitles"]
    return SOCIAL_CARDS["blog"]


def social_alt_for_page(relative: str | Path) -> str:
    card = social_card_for_page(relative)
    value = Path(relative).as_posix()
    return card.alt_en if value.startswith("en/") else card.alt_fa


def local_file_for_url(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != "www.alirostami.com":
        return None
    path = unquote(parsed.path).lstrip("/")
    candidate = ROOT / path
    return candidate if candidate.is_file() else None


def image_size(path: Path) -> tuple[int, int]:
    """Read PNG, GIF, JPEG, or WebP dimensions without third-party packages."""
    with path.open("rb") as handle:
        header = handle.read(32)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return struct.unpack(">II", header[16:24])
        if header[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", header[6:10])
        if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
            kind = header[12:16]
            if kind == b"VP8X":
                width = 1 + int.from_bytes(header[24:27], "little")
                height = 1 + int.from_bytes(header[27:30], "little")
                return width, height
            if kind == b"VP8 ":
                width, height = struct.unpack("<HH", header[26:30])
                return width & 0x3FFF, height & 0x3FFF
            if kind == b"VP8L":
                bits = int.from_bytes(header[21:25], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1

        handle.seek(0)
        if handle.read(2) != b"\xff\xd8":
            raise ValueError(f"unsupported image format: {path}")
        while True:
            byte = handle.read(1)
            while byte == b"\xff":
                byte = handle.read(1)
            if not byte:
                break
            marker = byte[0]
            if marker in {0xD8, 0xD9}:
                continue
            length_bytes = handle.read(2)
            if len(length_bytes) != 2:
                break
            length = int.from_bytes(length_bytes, "big")
            if marker in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }:
                data = handle.read(length - 2)
                return int.from_bytes(data[3:5], "big"), int.from_bytes(data[1:3], "big")
            handle.seek(length - 2, 1)
    raise ValueError(f"could not read image dimensions: {path}")


def apply_image_seo() -> None:
    """Run the stdlib post-processor after a page or sitemap generator."""
    sys.stdout.flush()
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "update-image-seo.py")],
        cwd=ROOT,
        check=True,
    )
