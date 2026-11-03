#!/usr/bin/env python3
"""Apply deterministic keyboard, semantics, and accessible-name improvements."""

from __future__ import annotations

import argparse
import html
import re
from html.parser import HTMLParser
from pathlib import Path

from image_utils import ROOT

STYLE = """    <style>
    .sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
    .skip-link{position:fixed;top:.75rem;left:.75rem;z-index:100000;padding:.65rem 1rem;border-radius:.35rem;background:#fff;color:#073b70;font-weight:700;box-shadow:0 2px 12px rgba(0,0,0,.25);transform:translateY(-180%);transition:transform .15s ease}
    .skip-link:focus{transform:translateY(0)}
    :where(a,button,input,select,textarea,[tabindex]):focus-visible{outline:3px solid #0563c1!important;outline-offset:3px!important}
    [theme=dark] :where(a,button,input,select,textarea,[tabindex]):focus-visible,[data-theme=dark] :where(a,button,input,select,textarea,[tabindex]):focus-visible{outline-color:#7dd3fc!important}
    body[data-header-desktop] :where(.single .post-meta,.single .post-meta a,.single .content ruby rt,.single .content .footnotes,.post-info-mod,.post-info-license,.archive .archive-item-date,.archive .tag-cloud-tags a sup,.home-disclaimer,.summary .content,.details-icon,.toc ruby rt,.fixed-button,.search .search-button,.suggestion-date,.suggestion-context,.search-footer){color:#5f5f66!important}
    body[theme=dark][data-header-desktop] :where(.single .post-meta,.single .post-meta a,.single .content ruby rt,.single .content .footnotes,.post-info-mod,.post-info-license,.archive .archive-item-date,.archive .tag-cloud-tags a sup,.home-disclaimer,.summary .content,.details-icon,.toc ruby rt,.fixed-button,.search .search-button,.suggestion-date,.suggestion-context,.search-footer){color:#b7bbc5!important}
    body[data-header-desktop] :where(.single .content a:not(.headerlink),.summary .content a,.single .post-meta a,.post-info-mod a,.post-info-license a,.search-footer a){color:#1d789b!important}
    body[theme=dark][data-header-desktop] :where(.single .content a:not(.headerlink),.summary .content a,.single .post-meta a,.post-info-mod a,.post-info-license a,.search-footer a){color:#6bc5e6!important}
    body[data-header-desktop] .single .content a:not(.headerlink){text-decoration:underline!important;text-underline-offset:.15em}
    body[data-header-desktop] :where(.single .content a:not(.headerlink),.summary .content a,.single .post-meta a,.post-info-mod a,.post-info-license a,.search-footer a):hover{color:#a41354!important}
    body[theme=dark][data-header-desktop] :where(.single .content a:not(.headerlink),.summary .content a,.single .post-meta a,.post-info-mod a,.post-info-license a,.search-footer a):hover{color:#fff!important}
    body[data-header-desktop] .search input::placeholder{color:#5f5f66!important;opacity:1}
    body[theme=dark][data-header-desktop] .search input::placeholder{color:#b7bbc5!important}
    button.menu-toggle{appearance:none;border:0;padding:0;background:transparent;color:inherit;font:inherit;min-width:2rem;min-height:2rem}
    button.search-button,button.search-cancel,button.theme-switch,button.history-back,button.share-button,button.script-button{appearance:none;border:0;padding:0;background:transparent;color:inherit;font:inherit;line-height:inherit;cursor:pointer}
    button.search-button,button.theme-switch,button.share-button,button.script-button{min-width:1.5rem;min-height:1.5rem}
    button.history-back{text-decoration:underline;text-underline-offset:.15em}
    summary.details-summary{list-style:none}
    summary.details-summary::-webkit-details-marker{display:none}
    .sidebar-controls .sidebar-action,.ch-chevron{appearance:none;border:0;background:transparent;color:inherit;font:inherit;cursor:pointer;min-height:1.5rem}
    .sidebar-controls .sidebar-action{color:var(--text-muted)}
    .sidebar-controls .sidebar-action:hover{color:var(--accent)}
    .ch-chevron{padding:.2rem .4rem;min-width:2rem}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
    </style>"""

RUNTIME = """    <script>
    (function(){
      'use strict';
      if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches&&window.config&&window.config.typeit){window.config.typeit.speed=0;window.config.typeit.cursorSpeed=0;window.config.typeit.duration=0;}
      function initAccessibility(){
        var menuToggle=document.getElementById('menu-toggle-mobile');
        var mobileMenu=document.getElementById('menu-mobile');
        var mask=document.getElementById('mask');
        var themeSwitches=document.querySelectorAll('.theme-switch');
        var searchToggles=document.querySelectorAll('.search-toggle');
        function later(fn){if(window.requestAnimationFrame){requestAnimationFrame(fn);}else{setTimeout(fn,0);}}
        function syncMenu(){if(menuToggle&&mobileMenu){menuToggle.setAttribute('aria-expanded',mobileMenu.classList.contains('active')?'true':'false');}}
        function syncTheme(){var dark=document.body.getAttribute('theme')==='dark';themeSwitches.forEach(function(item){item.setAttribute('aria-checked',dark?'true':'false');});}
        function syncSearch(){searchToggles.forEach(function(item){var mobile=item.id.indexOf('mobile')!==-1;var header=document.getElementById(mobile?'header-mobile':'header-desktop');item.setAttribute('aria-expanded',header&&header.classList.contains('open')?'true':'false');});}
        if(menuToggle){menuToggle.addEventListener('click',function(){later(syncMenu);});}
        if(mask){mask.addEventListener('click',function(){later(syncMenu);later(syncSearch);});}
        themeSwitches.forEach(function(item){item.addEventListener('click',function(){later(syncTheme);});});
        searchToggles.forEach(function(item){item.addEventListener('click',function(){later(syncSearch);});});
        document.querySelectorAll('.search input').forEach(function(item){item.addEventListener('focus',function(){later(syncSearch);});});
        document.querySelectorAll('.search-cancel').forEach(function(item){item.addEventListener('click',function(){later(syncSearch);});});
        document.addEventListener('keydown',function(event){
          if(event.key!=='Escape')return;
          var wasOpen=mobileMenu&&mobileMenu.classList.contains('active');
          document.body.classList.remove('blur');
          if(mobileMenu)mobileMenu.classList.remove('active');
          if(menuToggle)menuToggle.classList.remove('active');
          document.querySelectorAll('header.open').forEach(function(header){header.classList.remove('open');});
          syncMenu();syncSearch();
          if(wasOpen&&menuToggle)menuToggle.focus();
        });
        syncMenu();syncTheme();syncSearch();
      }
      if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',initAccessibility);}else{initAccessibility();}
    })();
    </script>"""

START_TAG_RE = {
    name: re.compile(rf"<{name}\b[^>]*>", re.IGNORECASE | re.DOTALL)
    for name in ("a", "body", "button", "div", "h1", "header", "i", "iframe", "input", "main", "nav", "select", "span", "th")
}
CONTROL_RE = re.compile(
    r"<(?P<tag>a|button)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)\s*>",
    re.IGNORECASE | re.DOTALL,
)
STYLE_MARKER_RE = re.compile(
    r"\n?[ \t]*<!-- accessibility-styles:start -->.*?<!-- accessibility-styles:end -->[ \t]*\n?",
    re.DOTALL,
)
RUNTIME_MARKER_RE = re.compile(
    r"\n?[ \t]*<!-- accessibility-runtime:start -->.*?<!-- accessibility-runtime:end -->[ \t]*\n?",
    re.DOTALL,
)


class NativeStructureParser(HTMLParser):
    def __init__(self, raw: str) -> None:
        super().__init__(convert_charrefs=True)
        self.raw = raw
        self.offsets: list[int] = []
        offset = 0
        for line in raw.splitlines(keepends=True):
            self.offsets.append(offset)
            offset += len(line)
        self.stack: list[tuple[str | None, int]] = []
        self.replacements: list[tuple[int, int, str]] = []

    def absolute_position(self) -> int:
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "div":
            return
        data = {name.lower(): value or "" for name, value in attrs}
        classes = set(data.get("class", "").split())
        if "menu" in classes:
            replacement = "nav"
        elif "details" in classes:
            replacement = "details"
        elif "details-summary" in classes:
            replacement = "summary"
        else:
            replacement = None
        self.stack.append((replacement, self.absolute_position()))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "div" or not self.stack:
            return
        replacement, opening = self.stack.pop()
        if not replacement:
            return
        closing = self.absolute_position()
        closing_end = self.raw.find(">", closing) + 1
        self.replacements.append((opening, opening + 4, f"<{replacement}"))
        self.replacements.append((closing, closing_end, f"</{replacement}>"))


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


def attribute_tokens(tag: str) -> list[tuple[str, str, int, int]]:
    tokens: list[tuple[str, str, int, int]] = []
    length = len(tag)
    index = 1
    while index < length and tag[index].isspace():
        index += 1
    while index < length and not tag[index].isspace() and tag[index] not in "/>":
        index += 1
    while index < length:
        while index < length and tag[index].isspace():
            index += 1
        if index >= length or tag[index] in "/>":
            break
        start = index
        while index < length and not tag[index].isspace() and tag[index] not in "=/>":
            index += 1
        name = tag[start:index]
        while index < length and tag[index].isspace():
            index += 1
        value = ""
        if index < length and tag[index] == "=":
            index += 1
            while index < length and tag[index].isspace():
                index += 1
            if index < length and tag[index] in "\"'":
                quote = tag[index]
                index += 1
                value_start = index
                while index < length and tag[index] != quote:
                    index += 1
                value = tag[value_start:index]
                if index < length:
                    index += 1
            else:
                value_start = index
                while index < length and not tag[index].isspace() and tag[index] != ">":
                    index += 1
                value = tag[value_start:index]
        tokens.append((name.lower(), html.unescape(value), start, index))
    return tokens


def set_attribute(tag: str, name: str, value: str) -> str:
    replacement = f'{name}="{html.escape(value, quote=True)}"'
    for token_name, _value, start, end in attribute_tokens(tag):
        if token_name == name.lower():
            return f"{tag[:start]}{replacement}{tag[end:]}"
    closing = re.search(r"\s*/?>$", tag)
    if closing is None:
        return tag
    return f"{tag[:closing.start()]} {replacement}{tag[closing.start():]}"


def remove_attribute(tag: str, name: str) -> str:
    for token_name, _value, start, end in attribute_tokens(tag):
        if token_name != name.lower():
            continue
        while start > 0 and tag[start - 1] in " \t":
            start -= 1
        return f"{tag[:start]}{tag[end:]}"
    return tag


def class_tokens(tag: str) -> set[str]:
    return set(attributes(tag).get("class", "").split())


def update_tags(raw: str, name: str, callback) -> str:
    return START_TAG_RE[name].sub(lambda match: callback(match.group(0)), raw)


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "layouts" not in path.parts
    ]


def is_redirect_fallback(raw: str) -> bool:
    return bool(
        re.search(r'<meta\b[^>]*http-equiv=["\']refresh["\']', raw, re.IGNORECASE)
        and re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*noindex', raw, re.IGNORECASE)
    )


def page_language(raw: str) -> str:
    match = re.search(r'<html\b[^>]*\blang=["\']([^"\']+)', raw, re.IGNORECASE)
    return match.group(1).lower() if match else "en"


def page_title(raw: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", raw, re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<[^>]+>", " ", match.group(1) if match else "Main content")
    return " ".join(html.unescape(value).split())


def replace_native_structures(raw: str) -> str:
    parser = NativeStructureParser(raw)
    parser.feed(raw)
    parser.close()
    for start, end, replacement in sorted(parser.replacements, reverse=True):
        raw = f"{raw[:start]}{replacement}{raw[end:]}"
    return raw


def replace_language_wrappers(raw: str) -> str:
    pattern = re.compile(
        r"<a\b(?P<attrs>[^>]*)>(?P<body>(?:(?!</a>).)*?<select\b.*?</select>\s*)</a\s*>",
        re.IGNORECASE | re.DOTALL,
    )

    def replace(match: re.Match[str]) -> str:
        opening = f"<a{match.group('attrs')}>"
        opening = remove_attribute(opening, "href")
        opening = remove_attribute(opening, "target")
        opening = remove_attribute(opening, "role")
        opening = remove_attribute(opening, "title")
        return f"<span{opening[2:-1]}>{match.group('body')}</span>"

    return pattern.sub(replace, raw)


def replace_javascript_links(raw: str) -> str:
    pattern = re.compile(
        r"<a\b(?P<attrs>[^>]*\bhref=[\"']javascript:[^\"']*[\"'][^>]*)>(?P<body>.*?)</a\s*>",
        re.IGNORECASE | re.DOTALL,
    )

    def replace(match: re.Match[str]) -> str:
        opening = f"<button{match.group('attrs')}>"
        opening = remove_attribute(opening, "href")
        opening = remove_attribute(opening, "target")
        opening = remove_attribute(opening, "rel")
        opening = set_attribute(opening, "type", "button")
        classes = class_tokens(opening)
        if "theme-switch" in classes:
            opening = set_attribute(opening, "role", "switch")
            opening = set_attribute(opening, "aria-checked", "false")
        else:
            opening = remove_attribute(opening, "role")
        if not classes:
            data = attributes(opening)
            if "history.back" in data.get("onclick", ""):
                control_class = "history-back"
            elif "data-sharer" in data:
                control_class = "share-button"
            else:
                control_class = "script-button"
            opening = set_attribute(opening, "class", control_class)
        return f"{opening}{match.group('body')}</button>"

    return pattern.sub(replace, raw)


def replace_mobile_toggle(raw: str, language: str) -> str:
    pattern = re.compile(
        r'<div\b(?P<attrs>[^>]*\bid=["\']menu-toggle-mobile["\'][^>]*)>'
        r"(?P<body>\s*<span></span>\s*<span></span>\s*<span></span>\s*)</div\s*>",
        re.IGNORECASE | re.DOTALL,
    )
    label = "باز کردن منوی اصلی" if language.startswith("fa") else "Open main menu"

    def replace(match: re.Match[str]) -> str:
        opening = f"<button{match.group('attrs')}>"
        opening = set_attribute(opening, "type", "button")
        opening = set_attribute(opening, "aria-label", label)
        opening = set_attribute(opening, "aria-controls", "menu-mobile")
        opening = set_attribute(opening, "aria-expanded", "false")
        return f"{opening}{match.group('body')}</button>"

    return pattern.sub(replace, raw)


def normalize_chapter_structure(path: Path, raw: str) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith("aima-4e/") and path.name != "index.html":
        raw = raw.replace('<div class="page">', '<main class="page">', 1)
        raw = raw.replace("\n</div>\n<script id=\"aima-standalone-helper\">", "\n</main>\n<script id=\"aima-standalone-helper\">", 1)
        if not re.search(r"<h1\b", raw, re.IGNORECASE):
            subtitle = re.search(r'<p class="subtitle">(.*?)</p>', raw, re.IGNORECASE | re.DOTALL)
            if subtitle:
                heading = f'<h1 class="chapter-title">{subtitle.group(1)}</h1>'
                raw = f"{raw[:subtitle.start()]}{heading}{raw[subtitle.end():]}"
            else:
                kicker_end = re.search(r'<div class="kicker">.*?</div>', raw, re.IGNORECASE | re.DOTALL)
                if kicker_end:
                    raw = f"{raw[:kicker_end.end()]}\n<h1 class=\"chapter-title\">پیشگفتار</h1>{raw[kicker_end.end():]}"
        heading = re.search(r'<h1\b[^>]*class=["\'][^"\']*\bchapter-title\b[^"\']*["\'][^>]*>.*?</h1\s*>', raw, re.IGNORECASE | re.DOTALL)
        kicker = re.search(r'<div class="kicker">.*?</div>', raw, re.IGNORECASE | re.DOTALL)
        toc = re.search(r'<nav\b[^>]*class=["\'][^"\']*\btoc\b', raw, re.IGNORECASE)
        if heading and kicker and toc and heading.start() > toc.start():
            heading_html = heading.group(0)
            raw = f"{raw[:heading.start()]}{raw[heading.end():]}"
            kicker = re.search(r'<div class="kicker">.*?</div>', raw, re.IGNORECASE | re.DOTALL)
            raw = f"{raw[:kicker.end()]}\n{heading_html}{raw[kicker.end():]}"
    elif relative.startswith("software-architecture/") and path.name != "index.html":
        raw = raw.replace('data-a11y-heading="promoted"', 'data-a11y-heading="promoted-from-h4"')
        raw = raw.replace(
            "        h3 {\n            font-size: 1.35rem;",
            "        h2 {\n            font-size: 1.35rem;",
            1,
        )
        raw = raw.replace(
            "        h4 {\n            font-size: 1.15rem;",
            "        h3 {\n            font-size: 1.15rem;",
            1,
        )
        raw = raw.replace(
            "            h3 {\n                font-size: 1.2rem;",
            "            h2 {\n                font-size: 1.2rem;",
            1,
        )
        if '<main class="chapter-main"' not in raw:
            raw = raw.replace(
                '<article class="chapter-content">',
                '<main class="chapter-main">\n<article class="chapter-content">',
                1,
            )
            raw = raw.replace(
                "</article>\n\n<script id=\"fosa-standalone-helper\">",
                "</article>\n</main>\n\n<script id=\"fosa-standalone-helper\">",
                1,
            )
        def promote_heading(match: re.Match[str]) -> str:
            level = int(match.group("level"))
            attrs = match.group("attrs")
            if "data-a11y-heading" in attrs:
                return match.group(0)
            target = level - 1
            marker = f' data-a11y-heading="promoted-from-h{level}"' if level > 3 else ""
            return f"<h{target}{attrs}{marker}>{match.group('body')}</h{target}>"

        raw = re.sub(
            r"<h(?P<level>[345])(?P<attrs>\b[^>]*)>(?P<body>.*?)</h(?P=level)\s*>",
            promote_heading,
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return raw


def fix_known_html_issues(path: Path, raw: str) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative == "aima-4e/10-فصل۱۰-بازنمایی-دانش.html":
        raw = raw.replace(") < ExpectedScore(e2)", ") &lt; ExpectedScore(e2)")
    elif relative == "aima-4e/22-فصل۲۲-یادگیری-تقویتی.html":
        raw = raw.replace("اگر n < Nₑ", "اگر n &lt; Nₑ")
    elif relative == "aima-4e/13-فصل۱۳-استدلال-احتمالاتی.html":
        raw = raw.replace(
            "در نقشه‌برداری مکان ژن‌ها در ژنوم انسان نقش حیاتی داشتند.\n<p>جودیا پرل",
            "در نقشه‌برداری مکان ژن‌ها در ژنوم انسان نقش حیاتی داشتند.</p>\n<p>جودیا پرل",
            1,
        )
    elif relative == "posts/index.html":
        raw = raw.replace("<title>All Posts & Articles", "<title>All Posts &amp; Articles", 1)
    return raw


def normalize_headings(path: Path, raw: str) -> str:
    relative = path.relative_to(ROOT).as_posix()
    raw = re.sub(
        r'(<div\b[^>]*\bid=["\']toc-auto["\'][^>]*>\s*)<h2(\b[^>]*class=["\'][^"\']*\btoc-title\b[^"\']*["\'][^>]*)>(.*?)</h2\s*>',
        r"\1<p\2>\3</p>",
        raw,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if relative == "index.html":
        raw = re.sub(
            r'<h1(\b[^>]*class=["\'][^"\']*\bsingle-title\b[^"\']*["\'][^>]*)>(.*?)</h1\s*>',
            r"<h2\1>\2</h2>",
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )
    if relative in {"categories/index.html", "tags/index.html", "posts/index.html"}:
        raw = re.sub(
            r'<h2(\b[^>]*class=["\'][^"\']*\bsingle-title\b[^"\']*["\'][^>]*)>(.*?)</h2\s*>',
            r"<h1\1>\2</h1>",
            raw,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    if relative == "posts/index.html":
        raw = re.sub(
            r'<h3(\b[^>]*class=["\'][^"\']*\bgroup-title\b[^"\']*["\'][^>]*)>(.*?)</h3\s*>',
            r"<h2\1>\2</h2>",
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )
    if relative in {
        "posts/aima-4e-persian/index.html",
        "posts/fundamentals-of-software-architecture-persian/index.html",
    }:
        raw = re.sub(r"<h3(\b[^>]*)>(.*?)</h3\s*>", r"<h2\1>\2</h2>", raw, count=1, flags=re.IGNORECASE | re.DOTALL)
    return raw


def add_main_target(raw: str) -> str:
    changed = False

    def update(tag: str) -> str:
        nonlocal changed
        if changed:
            return tag
        changed = True
        tag = set_attribute(tag, "id", "main-content")
        return set_attribute(tag, "tabindex", "-1")

    return update_tags(raw, "main", update)


def ensure_primary_heading(raw: str) -> str:
    if re.search(r"<h1\b", raw, re.IGNORECASE):
        return raw
    main = re.search(r"<main\b[^>]*>", raw, re.IGNORECASE)
    if not main:
        return raw
    heading = f'<h1 class="sr-only">{html.escape(page_title(raw))}</h1>'
    return f"{raw[:main.end()]}\n{heading}{raw[main.end():]}"


def add_table_header_scopes(raw: str) -> str:
    def update_thead(match: re.Match[str]) -> str:
        return update_tags(match.group(0), "th", lambda tag: set_attribute(tag, "scope", "col"))

    return re.sub(r"<thead\b.*?</thead\s*>", update_thead, raw, flags=re.IGNORECASE | re.DOTALL)


def update_control_markup(raw: str, language: str) -> str:
    label_language = "انتخاب زبان" if language.startswith("fa") else "Select language"
    desktop_navigation = "پیمایش اصلی دسکتاپ" if language.startswith("fa") else "Desktop main navigation"
    mobile_navigation = "پیمایش اصلی موبایل" if language.startswith("fa") else "Mobile main navigation"
    desktop_header = "سربرگ دسکتاپ" if language.startswith("fa") else "Desktop header"
    mobile_header = "سربرگ موبایل" if language.startswith("fa") else "Mobile header"

    if re.search(r'<a\b[^>]*\bhref=["\']#top["\']', raw, re.IGNORECASE):
        raw = update_tags(raw, "body", lambda tag: set_attribute(tag, "id", "top"))
    if not re.search(r'\bid=["\']comments["\']', raw, re.IGNORECASE):
        raw = re.sub(
            r'<a\b[^>]*\bhref=["\']#comments["\'][^>]*>.*?</a\s*>',
            "",
            raw,
            flags=re.IGNORECASE | re.DOTALL,
        )

    def update_input(tag: str) -> str:
        data = attributes(tag)
        if not data.get("aria-label") and not data.get("aria-labelledby"):
            label = data.get("placeholder") or ("جستجو" if language.startswith("fa") else "Search")
            tag = set_attribute(tag, "aria-label", label)
        if data.get("type", "").lower() in {"search", "text"} and "search" in data.get("id", ""):
            tag = set_attribute(tag, "autocomplete", "off")
            tag = set_attribute(tag, "enterkeyhint", "search")
        return tag

    raw = update_tags(raw, "input", update_input)

    def update_select(tag: str) -> str:
        data = attributes(tag)
        if not data.get("aria-label") and not data.get("aria-labelledby"):
            tag = set_attribute(tag, "aria-label", label_language)
        return tag

    raw = update_tags(raw, "select", update_select)
    has_desktop_dropdown = bool(re.search(r'\bid=["\']search-dropdown-desktop["\']', raw, re.IGNORECASE))
    has_mobile_dropdown = bool(re.search(r'\bid=["\']search-dropdown-mobile["\']', raw, re.IGNORECASE))

    def update_button(tag: str) -> str:
        data = attributes(tag)
        if not data.get("type"):
            tag = set_attribute(tag, "type", "button")
        classes = set(data.get("class", "").split())
        if "history-back" in classes and "data-sharer" in data:
            classes.remove("history-back")
            classes.add("share-button")
            tag = set_attribute(tag, "class", " ".join(sorted(classes)))
        if "copy-address" in classes:
            tag = set_attribute(tag, "aria-live", "polite")
        return tag

    raw = update_tags(raw, "button", update_button)

    def update_anchor(tag: str) -> str:
        data = attributes(tag)
        href = data.get("href", "")
        classes = set(data.get("class", "").split())
        if href.lower().startswith("javascript:"):
            tag = set_attribute(tag, "role", "switch" if "theme-switch" in classes else "button")
            if "theme-switch" in classes:
                tag = set_attribute(tag, "aria-checked", "false")
        if "search-toggle" in classes:
            mobile = data.get("id", "").endswith("mobile")
            if mobile:
                target = "search-dropdown-mobile" if has_mobile_dropdown else "search-input-mobile"
            else:
                target = "search-dropdown-desktop" if has_desktop_dropdown else "search-input-desktop"
            tag = set_attribute(tag, "aria-controls", target)
            tag = set_attribute(tag, "aria-expanded", "false")
        if "active" in classes and "menu-item" in classes:
            tag = set_attribute(tag, "aria-current", "page")
        if data.get("target", "").lower() == "_blank":
            rel = [token for token in data.get("rel", "").split() if token.lower() != "noreffer"]
            for token in ("noopener", "noreferrer"):
                if token not in {value.lower() for value in rel}:
                    rel.append(token)
            tag = set_attribute(tag, "rel", " ".join(rel))
        return tag

    raw = update_tags(raw, "a", update_anchor)

    def update_div(tag: str) -> str:
        tokens = class_tokens(tag)
        if "menu" in tokens:
            tag = set_attribute(tag, "role", "navigation")
            label = mobile_navigation if attributes(tag).get("id") == "menu-mobile" else desktop_navigation
            tag = set_attribute(tag, "aria-label", label)
        return tag

    raw = update_tags(raw, "div", update_div)

    def update_nav(tag: str) -> str:
        data = attributes(tag)
        tokens = class_tokens(tag)
        tag = remove_attribute(tag, "role")
        if "menu" in tokens:
            label = mobile_navigation if data.get("id") == "menu-mobile" else desktop_navigation
            return set_attribute(tag, "aria-label", label)
        if data.get("aria-label") or data.get("aria-labelledby"):
            return tag
        if data.get("id") == "TableOfContents" or "toc" in tokens:
            label = "فهرست مطالب" if language.startswith("fa") else "Table of contents"
        elif data.get("id"):
            label = ("پیمایش " if language.startswith("fa") else "Navigation ") + data["id"]
        else:
            label = "پیمایش تکمیلی" if language.startswith("fa") else "Secondary navigation"
        return set_attribute(tag, "aria-label", label)

    raw = update_tags(raw, "nav", update_nav)

    def update_header(tag: str) -> str:
        tokens = class_tokens(tag)
        if "desktop" in tokens:
            return set_attribute(tag, "aria-label", desktop_header)
        if "mobile" in tokens:
            return set_attribute(tag, "aria-label", mobile_header)
        return tag

    raw = update_tags(raw, "header", update_header)

    def update_span(tag: str) -> str:
        if "search-loading" in class_tokens(tag):
            tag = set_attribute(tag, "role", "status")
            tag = set_attribute(tag, "aria-live", "polite")
            tag = set_attribute(tag, "aria-label", "در حال جستجو" if language.startswith("fa") else "Searching")
        return tag

    raw = update_tags(raw, "span", update_span)
    raw = update_tags(raw, "i", lambda tag: set_attribute(tag, "aria-hidden", "true"))

    def label_controls(match: re.Match[str]) -> str:
        opening = f"<{match.group('tag')}{match.group('attrs')}>"
        data = attributes(opening)
        body = match.group("body")
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", body)).split())
        image_alt = re.search(r'<img\b[^>]*\balt=["\']([^"\']+)', body, re.IGNORECASE)
        if not data.get("aria-label") and not data.get("aria-labelledby"):
            title = data.get("title", "")
            if "headerlink" in set(data.get("class", "").split()) and title:
                opening = set_attribute(opening, "aria-label", title)
            elif not text and not image_alt and title:
                opening = set_attribute(opening, "aria-label", title)
            elif not text and not image_alt and data.get("href") == "/":
                opening = set_attribute(opening, "aria-label", "خانه" if language.startswith("fa") else "Home")
            elif not text and not image_alt and data.get("href"):
                href = data["href"].lower()
                social_labels = {
                    "github.com": "GitHub profile",
                    "twitter.com": "Twitter profile",
                    "x.com": "X profile",
                    "instagram.com": "Instagram profile",
                    "t.me": "Telegram profile",
                }
                for host, label in social_labels.items():
                    if host in href:
                        opening = set_attribute(opening, "aria-label", label)
                        break
        return f"{opening}{body}</{match.group('tag')}>"

    return CONTROL_RE.sub(label_controls, raw)


def update_error_heading(raw: str, language: str) -> str:
    label = "صفحه پیدا نشد" if language.startswith("fa") else "Page not found"

    def update(tag: str) -> str:
        if attributes(tag).get("id") == "error-emoji":
            return remove_attribute(tag, "aria-label")
        return tag

    raw = update_tags(raw, "h1", update)
    raw = re.sub(
        r'(<h1\b[^>]*\bid=["\']error-emoji["\'][^>]*>)\s*(</h1\s*>)',
        rf'\1<span class="sr-only">{html.escape(label)}</span>\2',
        raw,
        count=1,
        flags=re.IGNORECASE,
    )
    old_script = "document.getElementById('error-emoji').appendChild(document.createTextNode(emojiArray[Math.floor(Math.random() * emojiArray.length)]));"
    new_script = (
        "var emoji = document.createElement('span'); "
        "emoji.setAttribute('aria-hidden', 'true'); "
        "emoji.appendChild(document.createTextNode(emojiArray[Math.floor(Math.random() * emojiArray.length)])); "
        "document.getElementById('error-emoji').appendChild(emoji);"
    )
    return raw.replace(old_script, new_script, 1)


def install_style(raw: str) -> str:
    raw = STYLE_MARKER_RE.sub("\n", raw)
    match = re.search(r"</head\s*>", raw, re.IGNORECASE)
    if not match:
        return raw
    block = f"    <!-- accessibility-styles:start -->\n{STYLE}\n    <!-- accessibility-styles:end -->\n"
    prefix = raw[:match.start()].rstrip() + "\n"
    return f"{prefix}{block}{raw[match.start():]}"


def install_skip_link(raw: str, language: str) -> str:
    raw = re.sub(
        r"\n?[ \t]*<!-- accessibility-skip-link -->\s*<a\b[^>]*\bclass=[\"'][^\"']*\bskip-link\b[^\"']*[\"'][^>]*>.*?</a>[ \t]*\n?",
        "\n",
        raw,
        flags=re.IGNORECASE | re.DOTALL,
    )
    body = re.search(r"<body\b[^>]*>", raw, re.IGNORECASE)
    if not body or 'id="main-content"' not in raw:
        return raw
    text = "رفتن به محتوای اصلی" if language.startswith("fa") else "Skip to main content"
    link = f'\n    <!-- accessibility-skip-link -->\n    <a class="skip-link" href="#main-content">{text}</a>\n'
    return f"{raw[:body.end()]}{link}{raw[body.end():].lstrip(chr(10))}"


def install_runtime(raw: str) -> str:
    raw = RUNTIME_MARKER_RE.sub("\n", raw)
    if not re.search(r'(?:class=["\'][^"\']*\btheme-switch\b|role=["\'](?:button|switch)["\'])', raw, re.IGNORECASE):
        return raw
    closing = re.search(r"</body\s*>", raw, re.IGNORECASE)
    if not closing:
        return raw
    block = f"    <!-- accessibility-runtime:start -->\n{RUNTIME}\n    <!-- accessibility-runtime:end -->\n"
    prefix = raw[:closing.start()].rstrip() + "\n"
    return f"{prefix}{block}{raw[closing.start():]}"


def update_page(path: Path, raw: str) -> str:
    if is_redirect_fallback(raw):
        return raw
    language = page_language(raw)
    raw = STYLE_MARKER_RE.sub("", raw)
    raw = RUNTIME_MARKER_RE.sub("", raw)
    raw = fix_known_html_issues(path, raw)
    raw = normalize_chapter_structure(path, raw)
    raw = normalize_headings(path, raw)
    raw = replace_language_wrappers(raw)
    raw = replace_javascript_links(raw)
    raw = replace_mobile_toggle(raw, language)
    raw = replace_native_structures(raw)
    raw = add_table_header_scopes(raw)
    raw = add_main_target(raw)
    raw = ensure_primary_heading(raw)
    raw = update_control_markup(raw, language)
    raw = update_error_heading(raw, language)
    raw = install_style(raw)
    raw = install_skip_link(raw, language)
    raw = install_runtime(raw)
    return re.sub(r"[ \t]+$", "", raw, flags=re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report stale HTML without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed: list[Path] = []
    for path in html_pages():
        raw = path.read_text(encoding="utf-8", errors="strict")
        updated = update_page(path, raw)
        if updated == raw:
            continue
        changed.append(path.relative_to(ROOT))
        if not args.check:
            path.write_text(updated, encoding="utf-8")
    if args.check and changed:
        print("accessibility markup is stale:")
        for path in changed:
            print(f"  - {path.as_posix()}")
        return 1
    action = "would update" if args.check else "updated"
    print(f"accessibility markup {action}: {len(changed)} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
