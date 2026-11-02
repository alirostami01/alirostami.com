#!/usr/bin/env python3
"""Independently audit Phase-3 delivery, runtime, caching, and security rules."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent

MANAGED_SCRIPTS = {
    "autocomplete": "/lib/autocomplete/autocomplete.min.js",
    "lunr": "/lib/lunr/lunr.min.js",
    "clipboard": "/lib/clipboard/clipboard.min.js",
    "sharer": "/lib/sharer/sharer.min.js",
    "typeit": "/lib/typeit/index.umd.js",
}
THEME_SCRIPT = "/js/theme.min.js"
FONT_AWESOME = "/lib/fontawesome/all.min.css"
ANIMATE = "/lib/animate/animate-subset.min.css"

EXPECTED_HASHES = {
    "lib/animate/animate-subset.min.css": "8344fd0b5874f86fd386720eef38d1598ae66142d0c34b7dd607754c07dbbd1e",
    "lib/autocomplete/autocomplete.min.js": "ae2da1bd62c6469ee27770ad1cddf2e8296d8a7f6d85b091463e5200c5e320af",
    "lib/clipboard/clipboard.min.js": "e17a1d816e13c0826e0ed7febfabc3277f45571234bde0bf9120829a7169edc9",
    "lib/fontawesome/all.min.css": "5046892c413b64c8b15ce27b043cb0bac95009946b16008d62f8f8b259dd9cb0",
    "lib/lunr/lunr.min.js": "0c50d9002b85780a842afffb567bb54ede402dae7c6dc5997a018614d8044fc8",
    "lib/sharer/sharer.min.js": "ba5171a78670b031914e623431a33a3d73c1ea9897e552ba73bc2c2da7c777b9",
    "lib/typeit/index.umd.js": "4482c8aa2f6138437a0047fb3bb49eaa413dad4489a0995fcc4c81f0e955d269",
    "lib/webfonts/fa-brands-400.ttf": "e523f49c12b13a176014af1a46ae5a0545b136bf56d496426aa881026d0c318a",
    "lib/webfonts/fa-brands-400.woff2": "404c746c8f7e3f9b7611a8f23d908c1a32a5c972236b9d89bb68b05d9bf4b905",
    "lib/webfonts/fa-regular-400.ttf": "4e96a7e098e36fd493194c64e973ba5237da65760c7b746217e63c830326a9ac",
    "lib/webfonts/fa-regular-400.woff2": "6a274e7629c0d71dcf8cab1e7733687ebfe32e2c53b4ca9fad050b4f1d5471f3",
    "lib/webfonts/fa-solid-900.ttf": "03f2986c0824c68bdaf1e16947352f5fe417d03741806097fa9ea7131fe3a019",
    "lib/webfonts/fa-solid-900.woff2": "d76fb4e841748a3f6bc63efa23156e02631c283bf41f84efcbdaf339ea3e1b73",
    "lib/webfonts/fa-v4compatibility.ttf": "86a687cf5ade691e19aa03720ffa7c1ba99dd137f36cc61980eec447f2160627",
    "lib/webfonts/fa-v4compatibility.woff2": "0db31befb4837c56bf176e879a715b5cdf457553fc7e8877f974b4c6ef75b1b1",
}
LICENSES = (
    "lib/animate/LICENSE",
    "lib/autocomplete/LICENSE",
    "lib/clipboard/LICENSE",
    "lib/fontawesome/LICENSE.txt",
    "lib/lunr/LICENSE",
    "lib/sharer/LICENSE",
    "lib/typeit/LICENSE",
)
GENERATOR_SCRIPTS = (
    "scripts/build-aima-index.py",
    "scripts/build-project-page.py",
    "scripts/build-social-images.py",
    "scripts/build-software-architecture-index.py",
    "scripts/build-support-page.py",
    "scripts/update-sitemaps.py",
)

TAG_PATTERNS = {
    name: re.compile(rf"<{name}\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
    for name in ("img", "link", "script")
}
NOSCRIPT_RE = re.compile(r"<noscript\b[^>]*>.*?</noscript\s*>", re.IGNORECASE | re.DOTALL)
MARKER_RE_TEMPLATE = r"<!-- performance-{name}:start -->(.*?)<!-- performance-{name}:end -->"


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


def tags(raw: str, name: str) -> list[tuple[str, dict[str, str], int]]:
    return [
        (match.group(0), attributes(match.group(0)), match.start())
        for match in TAG_PATTERNS[name].finditer(raw)
    ]


def classes(raw: str) -> set[str]:
    result: set[str] = set()
    for match in re.finditer(r"\bclass=[\"']([^\"']*)[\"']", raw, re.IGNORECASE):
        result.update(match.group(1).split())
    return result


def marker_body(raw: str, name: str) -> str | None:
    matches = re.findall(
        MARKER_RE_TEMPLATE.format(name=re.escape(name)),
        raw,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if len(matches) == 1:
        return matches[0]
    return None


def local_path(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    return ROOT / unquote(parsed.path).lstrip("/")


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "layouts" not in path.parts
    ]


def parse_header_rules(raw: str) -> dict[str, dict[str, list[str]]]:
    rules: dict[str, dict[str, list[str]]] = {}
    current = ""
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            current = line.strip()
            rules.setdefault(current, {})
            continue
        if not current or ":" not in line:
            continue
        name, value = line.strip().split(":", 1)
        rules[current].setdefault(name.lower(), []).append(value.strip())
    return rules


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    stats: Counter[str] = Counter()

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    # Supply-chain integrity and expected license material.
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing pinned vendor asset: {relative}")
        if path.is_file():
            require(sha256(path) == expected, f"vendor digest changed: {relative}")
    for relative in LICENSES:
        path = ROOT / relative
        require(path.is_file() and path.stat().st_size > 500, f"missing/empty vendor license: {relative}")
    require((ROOT / "lib/VENDOR.md").is_file(), "missing lib/VENDOR.md provenance notes")

    font_css = (ROOT / "lib/fontawesome/all.min.css").read_text(encoding="utf-8")
    require("font-display:block" not in font_css, "Font Awesome still uses font-display:block")
    require("font-display:swap" in font_css, "Font Awesome does not use font-display:swap")
    animate_css = (ROOT / "lib/animate/animate-subset.min.css").read_text(encoding="utf-8")
    for animation in ("flash", "pulse", "fadeIn", "fadeInDown", "fadeOut", "fadeOutUp", "flipInX"):
        require(f"@keyframes {animation}" in animate_css, f"Animate subset is missing {animation}")
    require(len(animate_css.encode()) < 4_000, "Animate subset unexpectedly exceeds 4 KiB")

    for page in html_pages():
        relative = page.relative_to(ROOT).as_posix()
        raw = page.read_text(encoding="utf-8", errors="strict")
        stats["html"] += 1

        for forbidden in ("cdn.jsdelivr.net", "https://.disqus.com/embed.js", "lazysizes"):
            require(forbidden not in raw, f"{relative}: forbidden runtime reference {forbidden}")

        page_classes = classes(raw)
        script_tags = tags(raw, "script")
        link_tags = tags(raw, "link")
        image_tags = tags(raw, "img")
        script_sources = [data.get("src", "") for _tag, data, _pos in script_tags if data.get("src")]
        script_counts = Counter(script_sources)
        has_theme = script_counts[THEME_SCRIPT] == 1
        if has_theme:
            stats["theme_pages"] += 1
        require(script_counts[THEME_SCRIPT] <= 1, f"{relative}: duplicate theme runtime")

        for tag, data, _position in script_tags:
            source = data.get("src", "")
            if not source:
                continue
            parsed = urlparse(source)
            if parsed.netloc:
                require(parsed.netloc == "comments.app", f"{relative}: unexpected remote script {source}")
                require("defer" in data, f"{relative}: remote script is not deferred: {source}")
                stats["remote_scripts"] += 1
            if source == THEME_SCRIPT or source in MANAGED_SCRIPTS.values():
                require("defer" in data, f"{relative}: managed script is not deferred: {source}")
                require("async" not in data, f"{relative}: managed script must preserve execution order: {source}")
                require(script_counts[source] == 1, f"{relative}: duplicate managed script {source}")
            if source.startswith("/lib/") or source == THEME_SCRIPT:
                target = local_path(source)
                require(target is not None and target.is_file(), f"{relative}: missing local script {source}")

        search = bool(re.search(r'id=["\']search-input-(?:desktop|mobile)["\']', raw, re.IGNORECASE))
        highlight = "highlight" in page_classes and "chroma" in page_classes
        sharer = any("data-sharer" in data for _tag, data, _pos in script_tags) or bool(
            re.search(r"\bdata-sharer(?:\s|=|>)", raw, re.IGNORECASE)
        )
        typeit = "typeit" in page_classes or bool(re.search(r"\bdata-typeit(?:\s|=|>)", raw, re.IGNORECASE))
        expected_scripts = {
            MANAGED_SCRIPTS["autocomplete"]: search,
            MANAGED_SCRIPTS["lunr"]: search,
            MANAGED_SCRIPTS["clipboard"]: highlight,
            MANAGED_SCRIPTS["sharer"]: sharer,
            MANAGED_SCRIPTS["typeit"]: typeit,
        }
        for source, expected in expected_scripts.items():
            actual = script_counts[source] == 1
            require(
                actual == (expected and has_theme),
                f"{relative}: {source} feature/load mismatch (feature={expected}, theme={has_theme})",
            )
            if actual:
                stats[source.rsplit("/", 2)[-2]] += 1

        if has_theme:
            theme_position = next(pos for _tag, data, pos in script_tags if data.get("src") == THEME_SCRIPT)
            config_position = raw.find("window.config")
            require(0 <= config_position < theme_position, f"{relative}: window.config must precede deferred theme JS")
            for source, expected in expected_scripts.items():
                if expected:
                    position = next(
                        (pos for _tag, data, pos in script_tags if data.get("src") == source),
                        -1,
                    )
                    require(0 <= position < theme_position, f"{relative}: dependency must precede theme JS: {source}")
        else:
            require(
                not any(source in MANAGED_SCRIPTS.values() for source in script_sources),
                f"{relative}: managed dependency loaded without theme runtime",
            )
        if not typeit:
            require(
                not re.search(r'["\']typeit["\']\s*:', raw),
                f"{relative}: stale TypeIt config remains without a DOM target",
            )

        uses_icons = bool(
            page_classes
            & {"fa", "fas", "far", "fab", "fa-solid", "fa-regular", "fa-brands"}
        )
        uses_animations = has_theme or any(name.startswith("animate__") for name in page_classes)
        for marker, expected in (("icons", uses_icons), ("animations", uses_animations)):
            starts = raw.count(f"performance-{marker}:start")
            ends = raw.count(f"performance-{marker}:end")
            require(starts == ends == int(expected), f"{relative}: performance-{marker} marker mismatch")

        if uses_icons:
            body = marker_body(raw, "icons") or ""
            require(body.count(FONT_AWESOME) == 2, f"{relative}: invalid Font Awesome async/fallback pair")
            require("rel=\"preload\"" in body and "as=\"style\"" in body, f"{relative}: Font Awesome is not preloaded as CSS")
            require("this.rel='stylesheet'" in body, f"{relative}: Font Awesome async onload is missing")
            require("<noscript>" in body, f"{relative}: Font Awesome noscript fallback is missing")
            stats["icon_pages"] += 1
        if uses_animations:
            body = marker_body(raw, "animations") or ""
            require(body.count(ANIMATE) == 2, f"{relative}: invalid Animate async/fallback pair")
            require("rel=\"preload\"" in body and "as=\"style\"" in body, f"{relative}: Animate is not preloaded as CSS")
            require("this.rel='stylesheet'" in body, f"{relative}: Animate async onload is missing")
            require("<noscript>" in body, f"{relative}: Animate noscript fallback is missing")
            stats["animation_pages"] += 1

        outside_noscript = NOSCRIPT_RE.sub("", raw)
        for _tag, data, _position in tags(outside_noscript, "link"):
            href = data.get("href", "")
            rel = data.get("rel", "").lower().split()
            if href in (FONT_AWESOME, ANIMATE):
                require("preload" in rel and data.get("as", "").lower() == "style", f"{relative}: managed CSS blocks rendering: {href}")
            if "stylesheet" in rel and urlparse(href).netloc:
                require(False, f"{relative}: remote blocking stylesheet {href}")
        for _tag, data, _position in link_tags:
            href = data.get("href", "")
            if href.startswith("/lib/"):
                target = local_path(href)
                require(target is not None and target.is_file(), f"{relative}: missing local stylesheet/asset {href}")

        high_images = [data for _tag, data, _position in image_tags if data.get("fetchpriority", "").lower() == "high"]
        require(len(high_images) <= 1, f"{relative}: updater supports one priority image per page")
        starts = raw.count("performance-image-preload:start")
        ends = raw.count("performance-image-preload:end")
        require(starts == ends == int(bool(high_images)), f"{relative}: priority image preload marker mismatch")
        if high_images:
            image = high_images[0]
            body = marker_body(raw, "image-preload") or ""
            preload_links = [(tag, data) for tag, data, _pos in tags(body, "link") if data.get("as") == "image"]
            require(len(preload_links) == 1, f"{relative}: expected one image preload")
            if preload_links:
                _tag, preload = preload_links[0]
                require(preload.get("href") == image.get("src"), f"{relative}: image preload href mismatch")
                require(preload.get("fetchpriority") == "high", f"{relative}: image preload lacks high priority")
                require(preload.get("imagesrcset", "") == image.get("srcset", ""), f"{relative}: image preload srcset mismatch")
                target = local_path(preload.get("href", ""))
                require(target is not None and target.is_file(), f"{relative}: preloaded image does not exist")
            stats["priority_images"] += 1

    require(stats["priority_images"] == 5, f"expected five LCP image preloads, found {stats['priority_images']}")
    require(stats["remote_scripts"] == 2, f"expected only two deferred comments.app widgets, found {stats['remote_scripts']}")
    require(stats["clipboard"] == 0, "ClipboardJS is requested despite no current copy-code DOM")

    # Cloudflare Pages cache and browser hardening policy.
    headers_path = ROOT / "_headers"
    require(headers_path.is_file(), "missing Cloudflare Pages _headers policy")
    if headers_path.is_file():
        header_raw = headers_path.read_text(encoding="utf-8")
        rules = parse_header_rules(header_raw)
        global_headers = rules.get("/*", {})
        required_headers = {
            "content-security-policy",
            "cross-origin-opener-policy",
            "permissions-policy",
            "referrer-policy",
            "strict-transport-security",
            "x-content-type-options",
            "x-frame-options",
        }
        for name in sorted(required_headers):
            require(len(global_headers.get(name, [])) == 1, f"_headers: missing/duplicate global {name}")
        csp = "".join(global_headers.get("content-security-policy", []))
        for directive in (
            "default-src 'self'",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "script-src 'self' 'unsafe-inline' https://comments.app",
            "style-src 'self' 'unsafe-inline'",
            "frame-src 'self' https://comments.app",
        ):
            require(directive in csp, f"_headers: CSP is missing {directive}")
        require(len(csp) < 2_000, "_headers: CSP exceeds Cloudflare's per-line limit")
        for pattern in ("/lib/*", "/css/*", "/js/*", "/images/*", "/figures/*", "/svg/*"):
            values = rules.get(pattern, {}).get("cache-control", [])
            require(len(values) == 1 and "public" in values[0] and "max-age=" in values[0], f"_headers: invalid cache policy for {pattern}")
            require(not any("immutable" in value for value in values), f"_headers: unhashed assets must not be immutable: {pattern}")

    # Source templates must not reintroduce CDN/runtime debt, and every generator
    # must invoke both post-processors through the shared helper.
    source_paths = [
        path
        for path in (ROOT / "scripts").glob("*.py")
        if path.name not in {"update-performance.py", "check-performance.py"}
    ]
    source_paths.extend(path for path in (ROOT / "layouts").rglob("*") if path.is_file())
    for path in source_paths:
        source = path.read_text(encoding="utf-8", errors="strict")
        relative = path.relative_to(ROOT).as_posix()
        for forbidden in ("cdn.jsdelivr.net", "https://.disqus.com/embed.js", "lazysizes"):
            require(forbidden not in source, f"{relative}: source template contains {forbidden}")
    for relative in GENERATOR_SCRIPTS:
        source = (ROOT / relative).read_text(encoding="utf-8")
        require(
            "apply_site_postprocessors" in source and "apply_site_postprocessors()" in source,
            f"{relative}: generator is not connected to all site post-processors",
        )
    helper = (ROOT / "scripts/image_utils.py").read_text(encoding="utf-8")
    require('run_postprocessor("update-performance.py")' in helper, "image_utils.py does not run the performance post-processor")

    idempotence = subprocess.run(
        [sys.executable, str(ROOT / "scripts/update-performance.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(
        idempotence.returncode == 0,
        "performance post-processor is not idempotent: "
        + (idempotence.stdout + idempotence.stderr).strip(),
    )

    if errors:
        print(f"Performance audit failed with {len(errors)} issue(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    managed_bytes = sum((ROOT / path).stat().st_size for path in EXPECTED_HASHES if not path.startswith("lib/webfonts/"))
    print(
        "Performance audit passed: "
        f"{stats['html']} HTML files; {stats['icon_pages']} icon pages; "
        f"{stats['animation_pages']} animation pages; {stats['theme_pages']} deferred theme pages; "
        f"{stats['priority_images']} LCP preloads; {stats['remote_scripts']} allowed remote widgets; "
        f"{managed_bytes:,} pinned CSS/JS bytes."
    )
    print(
        "Conditional JS pages: "
        f"autocomplete/lunr={stats['autocomplete']}/{stats['lunr']}, "
        f"sharer={stats['sharer']}, typeit={stats['typeit']}, clipboard={stats['clipboard']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
