#!/usr/bin/env python3
"""Apply deterministic Phase-3 delivery and runtime performance optimizations.

The post-processor self-hosts critical CSS/JS references, removes obsolete
lazy-loading and broken Disqus requests, loads optional JavaScript only where
its DOM feature exists, and preloads the five above-the-fold images selected by
Phase 2. It is stdlib-only and idempotent.
"""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

from image_utils import ROOT

FONT_AWESOME_LOCAL = "/lib/fontawesome/all.min.css"
ANIMATE_LOCAL = "/lib/animate/animate-subset.min.css"
THEME_SCRIPT = "/js/theme.min.js"

VENDOR_SCRIPTS = {
    "autocomplete": "/lib/autocomplete/autocomplete.min.js",
    "lunr": "/lib/lunr/lunr.min.js",
    "clipboard": "/lib/clipboard/clipboard.min.js",
    "sharer": "/lib/sharer/sharer.min.js",
    "typeit": "/lib/typeit/index.umd.js",
}

FONT_AWESOME_URL_PARTS = ("@fortawesome/fontawesome-free", FONT_AWESOME_LOCAL)
ANIMATE_URL_PARTS = ("animate.css@", ANIMATE_LOCAL)
SCRIPT_URL_PARTS = {
    "autocomplete": ("autocomplete.js@", VENDOR_SCRIPTS["autocomplete"]),
    "lunr": ("lunr@", VENDOR_SCRIPTS["lunr"]),
    "clipboard": ("clipboard@", VENDOR_SCRIPTS["clipboard"]),
    "sharer": ("sharer.js@", VENDOR_SCRIPTS["sharer"]),
    "typeit": ("typeit@", VENDOR_SCRIPTS["typeit"]),
    "lazysizes": ("lazysizes@", "/lib/lazysizes/"),
}

LINK_RE = re.compile(
    r"[ \t]*<link\b[^>]*>(?:[ \t]*\r?\n)?",
    flags=re.IGNORECASE | re.DOTALL,
)
NOSCRIPT_LINK_RE = re.compile(
    r"[ \t]*<noscript>\s*(<link\b[^>]*>)\s*</noscript>(?:[ \t]*\r?\n)?",
    flags=re.IGNORECASE | re.DOTALL,
)
SCRIPT_RE = re.compile(
    r"[ \t]*<script\b[^>]*>.*?</script\s*>(?:[ \t]*\r?\n)?",
    flags=re.IGNORECASE | re.DOTALL,
)
IMG_RE = re.compile(r"<img\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
DISQUS_BLOCK_RE = re.compile(
    r'<div\s+id=["\']disqus_thread["\'][^>]*>\s*</div>\s*'
    r"<noscript>.*?powered by\s*<a[^>]*>Disqus</a>\.\s*</noscript>",
    flags=re.IGNORECASE | re.DOTALL,
)
class StartTagParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.data: dict[str, str] = {}

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not self.data:
            self.data = {name.lower(): value or "" for name, value in attrs}

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def attributes(tag: str) -> dict[str, str]:
    parser = StartTagParser()
    parser.feed(tag)
    return parser.data


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "layouts" not in path.parts
    ]


def insert_before_head(raw: str, snippet: str) -> str:
    match = re.search(r"</head\s*>", raw, flags=re.IGNORECASE)
    if match is None:
        return raw
    line_start = raw.rfind("\n", 0, match.start()) + 1
    if not raw[line_start : match.start()].strip():
        insertion_start = line_start
        separator = ""
    else:
        insertion_start = match.start()
        separator = "\n"
    return f"{raw[:insertion_start]}{separator}{snippet}\n</head>{raw[match.end():]}"


def managed_placeholder(raw: str, name: str) -> tuple[str, str, bool]:
    placeholder = f"__PERFORMANCE_{name.upper().replace('-', '_')}_BLOCK__"
    pattern = re.compile(
        rf"[ \t]*<!-- performance-{re.escape(name)}:start -->.*?"
        rf"<!-- performance-{re.escape(name)}:end -->",
        flags=re.DOTALL,
    )
    present = pattern.search(raw) is not None
    if present:
        raw = pattern.sub(placeholder, raw, count=1)
    return raw, placeholder, present


def install_managed_block(
    raw: str,
    name: str,
    block: str,
    placeholder: str,
    was_present: bool,
) -> str:
    if not block:
        return raw.replace(placeholder, "") if was_present else raw
    wrapped = (
        f"    <!-- performance-{name}:start -->\n"
        f"{block}\n"
        f"    <!-- performance-{name}:end -->"
    )
    if was_present:
        return raw.replace(placeholder, wrapped)
    return insert_before_head(raw, wrapped)


def is_target(value: str, fragments: tuple[str, ...]) -> bool:
    return any(fragment in value for fragment in fragments)


def remove_stylesheet(raw: str, fragments: tuple[str, ...]) -> str:
    def remove_noscript(match: re.Match[str]) -> str:
        href = attributes(match.group(1)).get("href", "")
        return "" if is_target(href, fragments) else match.group(0)

    raw = NOSCRIPT_LINK_RE.sub(remove_noscript, raw)

    def remove_link(match: re.Match[str]) -> str:
        href = attributes(match.group(0)).get("href", "")
        return "" if is_target(href, fragments) else match.group(0)

    return LINK_RE.sub(remove_link, raw)


def uses_font_awesome(raw: str) -> bool:
    return bool(
        re.search(
            r'class=["\'][^"\']*\b(?:fa|fas|far|fab|fa-solid|fa-regular|fa-brands)\b',
            raw,
            flags=re.IGNORECASE,
        )
    )


def update_stylesheets(raw: str) -> str:
    raw, icon_placeholder, had_icons = managed_placeholder(raw, "icons")
    raw, animation_placeholder, had_animations = managed_placeholder(raw, "animations")
    raw = remove_stylesheet(raw, FONT_AWESOME_URL_PARTS)
    raw = remove_stylesheet(raw, ANIMATE_URL_PARTS)

    icon_block = ""
    if uses_font_awesome(raw):
        icon_block = f"""    <style>.fa,.fas,.far,.fab,.fa-solid,.fa-regular,.fa-brands{{display:inline-block;min-width:1em;text-align:center}}.fa-fw{{width:1.25em}}</style>
    <link rel="preload" href="{FONT_AWESOME_LOCAL}" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="{FONT_AWESOME_LOCAL}"></noscript>"""
    raw = install_managed_block(raw, "icons", icon_block, icon_placeholder, had_icons)

    # Theme JS dynamically uses fade/flash animations even when the source HTML
    # has no static animate__ class.
    animation_block = ""
    if THEME_SCRIPT in raw or "animate__" in raw:
        animation_block = f"""    <link rel="preload" href="{ANIMATE_LOCAL}" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="{ANIMATE_LOCAL}"></noscript>"""
    return install_managed_block(
        raw,
        "animations",
        animation_block,
        animation_placeholder,
        had_animations,
    )


def script_kind(source: str) -> str | None:
    if source == THEME_SCRIPT:
        return "theme"
    if source == "https://.disqus.com/embed.js":
        return "broken-disqus"
    for kind, fragments in SCRIPT_URL_PARTS.items():
        if is_target(source, fragments):
            return kind
    return None


def object_boundaries(raw: str, opening: int) -> tuple[int, list[int]]:
    """Return a JS object's closing brace and its top-level comma offsets."""
    depth = 0
    quote = ""
    escaped = False
    commas: list[int] = []
    for index in range(opening, len(raw)):
        char = raw[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in "\"'":
            quote = char
        elif char in "{[":
            depth += 1
        elif char in "}]":
            if depth == 1 and char == "}":
                return index, commas
            depth -= 1
        elif char == "," and depth == 1:
            commas.append(index)
    raise ValueError("unterminated window.config object")


def remove_window_config_property(raw: str, property_name: str) -> str:
    """Remove one top-level property while preserving the surrounding JS."""
    assignments = list(re.finditer(r"\bwindow\.config\s*=\s*\{", raw))
    key_pattern = re.compile(rf"^\s*[\"']?{re.escape(property_name)}[\"']?\s*:")
    for assignment in reversed(assignments):
        opening = raw.find("{", assignment.start())
        closing, commas = object_boundaries(raw, opening)
        starts = [opening + 1, *(comma + 1 for comma in commas)]
        ends = [*commas, closing]
        for segment_index, (start, end) in enumerate(zip(starts, ends)):
            segment = raw[start:end]
            if not key_pattern.match(segment):
                continue
            if segment_index > 0:
                # Remove the preceding comma with a final property, retaining
                # the whitespace that formatted the object's closing brace.
                trailing = re.search(r"\s*$", segment).group(0)
                raw = f"{raw[:commas[segment_index - 1]]}{trailing}{raw[end:]}"
            elif commas:
                leading = re.match(r"\s*", segment).group(0)
                raw = f"{raw[:start]}{leading}{raw[commas[0] + 1:]}"
            else:
                trailing = re.search(r"\s*$", segment).group(0)
                raw = f"{raw[:start]}{trailing}{raw[end:]}"
            break
    return raw


def update_scripts(raw: str) -> str:
    raw = DISQUS_BLOCK_RE.sub("", raw)
    theme_placeholder = "__PERFORMANCE_THEME_SCRIPT__"
    theme_count = 0

    def remove_managed_script(match: re.Match[str]) -> str:
        nonlocal theme_count
        source = attributes(match.group(0)).get("src", "")
        kind = script_kind(source)
        if kind == "theme":
            theme_count += 1
            followed_by_script = re.match(r"[ \t]*<script\b", raw[match.end():], re.IGNORECASE)
            newline = "\n" if match.group(0).endswith("\n") or followed_by_script else ""
            return theme_placeholder + newline
        if kind is not None:
            return ""
        return match.group(0)

    raw = SCRIPT_RE.sub(remove_managed_script, raw)
    if theme_count == 0:
        return raw
    if theme_count != 1:
        raise ValueError(f"expected one theme script, found {theme_count}")

    if not re.search(r"\bwindow\.config\s*=", raw):
        minimal_config = '        <script>window.config={"data":{}};</script>\n'
        raw = raw.replace(theme_placeholder, minimal_config + theme_placeholder, 1)

    dependencies: list[str] = []
    has_search = bool(re.search(r'id=["\']search-input-(?:desktop|mobile)["\']', raw))
    has_highlight = bool(
        re.search(r'class=["\'][^"\']*\bhighlight\b', raw)
        and re.search(r'class=["\'][^"\']*\bchroma\b', raw)
    )
    has_sharer = bool(re.search(r"\bdata-sharer\s*=", raw))
    has_typeit = bool(
        re.search(r'class=["\'][^"\']*\btypeit\b', raw)
        or re.search(r"\bdata-typeit(?:\s|=|>)", raw)
    )
    if not has_typeit:
        # LoveIt may emit stale global TypeIt configuration on pages without a
        # target. Remove it so the deferred theme does not call an absent API.
        raw = remove_window_config_property(raw, "typeit")

    if has_search:
        dependencies.extend((VENDOR_SCRIPTS["autocomplete"], VENDOR_SCRIPTS["lunr"]))
    if has_highlight:
        dependencies.append(VENDOR_SCRIPTS["clipboard"])
    if has_sharer:
        dependencies.append(VENDOR_SCRIPTS["sharer"])
    if has_typeit:
        dependencies.append(VENDOR_SCRIPTS["typeit"])

    scripts = [f'        <script defer src="{source}"></script>' for source in dependencies]
    scripts.append(f'        <script defer src="{THEME_SCRIPT}"></script>')
    position = raw.find(theme_placeholder)
    prefix = "\n" if position > 0 and raw[position - 1] != "\n" else ""
    raw = raw.replace(theme_placeholder, prefix + "\n".join(scripts), 1)
    raw = re.sub(
        rf"(?:\n[ \t]*){{3,}}(?=<script defer src=[\"\'](?:/lib/|{re.escape(THEME_SCRIPT)}))",
        "\n        ",
        raw,
    )
    raw = re.sub(
        r'(?m)^[ \t]*<script>window\.config=\{"data":\{\}\};</script>[ \t]*$',
        '        <script>window.config={"data":{}};</script>',
        raw,
    )
    raw = re.sub(
        r'(<script>window\.config=\{"data":\{\}\};</script>)\n(?:[ \t]*\n)+'
        rf'(?=[ \t]*<script defer src=["\']{re.escape(THEME_SCRIPT)}["\'])',
        r"\1\n",
        raw,
    )
    return re.sub(
        rf'(<script defer src=["\']{re.escape(THEME_SCRIPT)}["\']></script>)[ \t]*(?=</body>)',
        r"\1\n    ",
        raw,
    )


def preload_block(raw: str) -> str:
    for tag in IMG_RE.findall(raw):
        data = attributes(tag)
        if data.get("fetchpriority", "").lower() != "high":
            continue
        source = data.get("src", "")
        if not source.startswith("/"):
            return ""
        parts = [f'    <link rel="preload" as="image" href="{source}" fetchpriority="high"']
        if data.get("srcset"):
            parts.append(f' imagesrcset="{data["srcset"]}"')
        parts.append(">")
        return "".join(parts)
    return ""


def update_image_preload(raw: str) -> str:
    raw, placeholder, present = managed_placeholder(raw, "image-preload")
    return install_managed_block(
        raw,
        "image-preload",
        preload_block(raw),
        placeholder,
        present,
    )


def update_page(raw: str) -> str:
    raw = update_stylesheets(raw)
    raw = update_scripts(raw)
    raw = update_image_preload(raw)
    return re.sub(r"[ \t]+$", "", raw, flags=re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report stale HTML without writing files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed: list[Path] = []
    for page in html_pages():
        raw = page.read_text(encoding="utf-8", errors="strict")
        updated = update_page(raw)
        if updated == raw:
            continue
        changed.append(page.relative_to(ROOT))
        if not args.check:
            page.write_text(updated, encoding="utf-8")

    if args.check and changed:
        print("performance delivery is stale:")
        for page in changed:
            print(f"  - {page.as_posix()}")
        return 1

    action = "would update" if args.check else "updated"
    print(f"performance delivery {action}: {len(changed)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
