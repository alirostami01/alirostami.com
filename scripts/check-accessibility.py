#!/usr/bin/env python3
"""Independently audit generated HTML for Phase-4 accessibility invariants."""

from __future__ import annotations

import html
import re
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
GENERATOR_SCRIPTS = (
    "scripts/build-aima-index.py",
    "scripts/build-project-page.py",
    "scripts/build-social-images.py",
    "scripts/build-software-architecture-index.py",
    "scripts/build-support-page.py",
    "scripts/update-sitemaps.py",
)
READER_PAGES = (
    "aima-4e/index.html",
    "software-architecture/index.html",
)
VALID_ARIA_STATES = {"true", "false"}
CONTRAST_PAIRS = (
    ("#5f5f66", "#ffffff", 4.5, "light muted text"),
    ("#b7bbc5", "#292a2d", 4.5, "dark muted text"),
    ("#1d789b", "#ffffff", 4.5, "light content links"),
    ("#6bc5e6", "#292a2d", 4.5, "dark content links"),
    ("#0563c1", "#ffffff", 3.0, "light focus indicator"),
    ("#7dd3fc", "#292a2d", 3.0, "dark focus indicator"),
)


class PageAuditParser(HTMLParser):
    """Collect the small DOM subset needed by the static audit."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_attrs: dict[str, str] = {}
        self.robots = ""
        self.has_refresh = False
        self.ids: list[str] = []
        self.duplicate_attributes: list[tuple[str, str]] = []
        self.references: list[tuple[str, str]] = []
        self.fragments: list[str] = []
        self.headings: list[dict[str, object]] = []
        self._heading_stack: list[dict[str, object]] = []
        self.controls: list[dict[str, object]] = []
        self._control_stack: list[dict[str, object]] = []
        self.form_controls: list[tuple[str, dict[str, str]]] = []
        self.anchors: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self.icons: list[dict[str, str]] = []
        self.iframes: list[dict[str, str]] = []
        self.headers: list[dict[str, str]] = []
        self.mains: list[dict[str, str]] = []
        self.menus: list[tuple[str, dict[str, str]]] = []
        self.navs: list[dict[str, str]] = []
        self.table_headers: list[dict[str, str]] = []
        self.aria_states: list[tuple[str, str, str]] = []
        self.positive_tabindexes: list[tuple[str, str]] = []
        self.first_focusable: tuple[str, dict[str, str]] | None = None
        self.body_seen = False

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {name.lower(): value or "" for name, value in attrs}

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs = self.attrs_dict(attrs_list)
        names = [name.lower() for name, _value in attrs_list]
        for name, count in Counter(names).items():
            if count > 1:
                self.duplicate_attributes.append((tag, name))

        if tag == "html":
            self.html_attrs = attrs
        if tag == "body":
            self.body_seen = True
        if tag == "meta":
            if attrs.get("name", "").lower() == "robots":
                self.robots = attrs.get("content", "")
            if attrs.get("http-equiv", "").lower() == "refresh":
                self.has_refresh = True

        element_id = attrs.get("id")
        if element_id:
            self.ids.append(element_id)
        for attribute in ("aria-controls", "aria-labelledby", "aria-describedby"):
            if attrs.get(attribute):
                self.references.append((attribute, attrs[attribute]))
        for attribute in ("aria-expanded", "aria-checked", "aria-pressed"):
            if attribute in attrs:
                self.aria_states.append((tag, attribute, attrs[attribute]))

        tabindex = attrs.get("tabindex")
        if tabindex:
            try:
                if int(tabindex) > 0:
                    self.positive_tabindexes.append((tag, tabindex))
            except ValueError:
                self.positive_tabindexes.append((tag, tabindex))

        classes = set(attrs.get("class", "").split())
        if tag == "main":
            self.mains.append(attrs)
        if tag == "header":
            self.headers.append(attrs)
        if tag == "nav":
            self.navs.append(attrs)
        if tag == "th":
            self.table_headers.append(attrs)
        if "menu" in classes:
            self.menus.append((tag, attrs))
        if tag == "i":
            self.icons.append(attrs)
        if tag == "iframe":
            self.iframes.append(attrs)
        if tag in {"input", "select", "textarea"}:
            self.form_controls.append((tag, attrs))
        if tag == "a":
            self.anchors.append(attrs)
            href = attrs.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.fragments.append(href[1:])
        if tag == "button":
            self.buttons.append(attrs)

        if re.fullmatch(r"h[1-6]", tag):
            heading = {"level": int(tag[1]), "attrs": attrs, "text": []}
            self.headings.append(heading)
            self._heading_stack.append(heading)

        if tag in {"a", "button"}:
            control = {
                "tag": tag,
                "attrs": attrs,
                "text": [],
                "image_alts": [],
                "nested_select": False,
                "nested_control": bool(self._control_stack),
            }
            self._control_stack.append(control)

        if tag == "img" and attrs.get("alt"):
            for control in self._control_stack:
                control["image_alts"].append(attrs["alt"])
        if tag == "select":
            for control in self._control_stack:
                control["nested_select"] = True

        if self.body_seen and self.first_focusable is None and self.is_focusable(tag, attrs):
            self.first_focusable = (tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if re.fullmatch(r"h[1-6]", tag) and self._heading_stack:
            self._heading_stack.pop()
        if tag in {"a", "button"} and self._control_stack:
            for index in range(len(self._control_stack) - 1, -1, -1):
                if self._control_stack[index]["tag"] == tag:
                    control = self._control_stack.pop(index)
                    self.controls.append(control)
                    break

    def handle_data(self, data: str) -> None:
        for heading in self._heading_stack:
            heading["text"].append(data)
        for control in self._control_stack:
            control["text"].append(data)

    @staticmethod
    def is_focusable(tag: str, attrs: dict[str, str]) -> bool:
        if attrs.get("hidden") is not None or attrs.get("aria-hidden", "").lower() == "true":
            return False
        if attrs.get("tabindex") == "-1":
            return False
        if tag == "a":
            return bool(attrs.get("href"))
        if tag == "button":
            return "disabled" not in attrs
        if tag == "input":
            return attrs.get("type", "text").lower() != "hidden" and "disabled" not in attrs
        if tag in {"select", "textarea"}:
            return "disabled" not in attrs
        if "tabindex" in attrs:
            try:
                return int(attrs["tabindex"]) >= 0
            except ValueError:
                return True
        return False


def html_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if "layouts" not in path.parts
        and not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
    ]


def has_accessible_name(control: dict[str, object]) -> bool:
    attrs = control["attrs"]
    assert isinstance(attrs, dict)
    if attrs.get("aria-label", "").strip() or attrs.get("aria-labelledby", "").strip():
        return True
    text = " ".join("".join(control["text"]).split())
    image_alts = " ".join(control["image_alts"]).strip()
    return bool(text or image_alts)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def relative_luminance(color: str) -> float:
    value = color.removeprefix("#")
    channels = [int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted((relative_luminance(foreground), relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def audit_page(path: Path, errors: list[str], stats: Counter[str]) -> None:
    relative = path.relative_to(ROOT).as_posix()
    raw = path.read_text(encoding="utf-8", errors="strict")
    parser = PageAuditParser()
    parser.feed(raw)
    parser.close()

    stats["html"] += 1
    noindex = "noindex" in parser.robots.lower()
    redirect_fallback = noindex and parser.has_refresh
    enhanced = not redirect_fallback
    indexable = not noindex
    if enhanced:
        stats["enhanced"] += 1
    if indexable:
        stats["indexable"] += 1

    id_counts = Counter(parser.ids)
    for element_id, count in id_counts.items():
        require(count == 1, f"{relative}: duplicate id #{element_id}", errors)
    for tag, attribute in parser.duplicate_attributes:
        require(False, f"{relative}: <{tag}> repeats the {attribute} attribute", errors)
    for tag, tabindex in parser.positive_tabindexes:
        require(False, f"{relative}: <{tag}> uses positive/invalid tabindex={tabindex}", errors)

    for attrs in parser.anchors:
        href = attrs.get("href", "")
        if attrs.get("target", "").lower() == "_blank":
            rel = set(attrs.get("rel", "").lower().split())
            require(
                {"noopener", "noreferrer"}.issubset(rel),
                f"{relative}: target=_blank link lacks noopener noreferrer ({href or 'no href'})",
                errors,
            )
        require(not href.lower().startswith("javascript:"), f"{relative}: javascript pseudo-link was not converted to a button", errors)
        require(bool(href), f"{relative}: anchor has no href and is not keyboard-focusable", errors)

    if not enhanced:
        return

    require(bool(parser.html_attrs.get("lang")), f"{relative}: <html> lacks lang", errors)
    if parser.html_attrs.get("lang", "").lower().startswith("fa"):
        require(parser.html_attrs.get("dir", "").lower() == "rtl", f"{relative}: Persian page lacks dir=rtl", errors)

    require(raw.count("<!-- accessibility-styles:start -->") == 1, f"{relative}: managed accessibility style is missing/duplicated", errors)
    require(raw.count("<!-- accessibility-styles:end -->") == 1, f"{relative}: accessibility style end marker is missing/duplicated", errors)
    require(":focus-visible" in raw, f"{relative}: focus-visible styling is missing", errors)
    require("prefers-reduced-motion:reduce" in raw, f"{relative}: reduced-motion override is missing", errors)
    require("min-width:2rem" in raw, f"{relative}: compact toggles lack a 32px minimum target width", errors)
    require(not re.search(r'<div\b[^>]*\bclass=["\'][^"\']*\bdetails-summary\b', raw, re.IGNORECASE), f"{relative}: disclosure summary is a non-keyboard div", errors)
    disclosure_count = raw.count('<details class="details')
    require(disclosure_count == raw.count('<summary class="details-summary'), f"{relative}: native disclosure lacks a matching summary", errors)
    stats["disclosures"] += disclosure_count
    for color in ("#5f5f66", "#b7bbc5", "#1d789b", "#6bc5e6"):
        require(color in raw, f"{relative}: managed contrast color {color} is missing", errors)
    if "/lib/typeit/" in raw:
        require("window.config.typeit.speed=0" in raw, f"{relative}: reduced-motion users still receive animated typing", errors)

    require(len(parser.mains) == 1, f"{relative}: expected exactly one main landmark, found {len(parser.mains)}", errors)
    if len(parser.mains) == 1:
        main = parser.mains[0]
        require(main.get("id") == "main-content", f"{relative}: main landmark lacks id=main-content", errors)
        require(main.get("tabindex") == "-1", f"{relative}: main skip target lacks tabindex=-1", errors)

    skip_links = [
        attrs for attrs in parser.anchors
        if "skip-link" in set(attrs.get("class", "").split())
    ]
    require(len(skip_links) == 1, f"{relative}: expected one skip link, found {len(skip_links)}", errors)
    if skip_links:
        require(skip_links[0].get("href") == "#main-content", f"{relative}: skip link has the wrong target", errors)
    first = parser.first_focusable
    require(
        bool(first and first[0] == "a" and "skip-link" in set(first[1].get("class", "").split())),
        f"{relative}: skip link is not the first focusable element",
        errors,
    )
    stats["skip_links"] += len(skip_links)

    h1s = [heading for heading in parser.headings if heading["level"] == 1]
    require(len(h1s) == 1, f"{relative}: expected exactly one h1, found {len(h1s)}", errors)
    for heading in h1s:
        attrs = heading["attrs"]
        text = " ".join("".join(heading["text"]).split())
        require(bool(text or attrs.get("aria-label")), f"{relative}: h1 has no accessible text", errors)
    levels = [int(heading["level"]) for heading in parser.headings]
    require(bool(levels and levels[0] == 1), f"{relative}: first heading is not h1", errors)
    for previous, current in zip(levels, levels[1:]):
        require(current <= previous + 1, f"{relative}: heading level jumps h{previous} to h{current}", errors)
    stats["headings"] += len(levels)

    ids = set(parser.ids)
    for attribute, references in parser.references:
        for reference in references.split():
            require(reference in ids, f"{relative}: {attribute} references missing #{reference}", errors)
    for fragment in parser.fragments:
        target = html.unescape(unquote(fragment))
        require(target in ids, f"{relative}: link references missing #{target}", errors)

    for tag, attrs in parser.form_controls:
        if tag == "input" and attrs.get("type", "").lower() == "hidden":
            continue
        require(
            bool(attrs.get("aria-label", "").strip() or attrs.get("aria-labelledby", "").strip()),
            f"{relative}: <{tag}> lacks an explicit accessible name",
            errors,
        )
        stats["form_controls"] += 1

    for attrs in parser.table_headers:
        require(attrs.get("scope") in {"col", "row", "colgroup", "rowgroup"}, f"{relative}: table header lacks a valid scope", errors)
        stats["table_headers"] += 1

    for control in parser.controls:
        attrs = control["attrs"]
        require(has_accessible_name(control), f"{relative}: <{control['tag']}> lacks an accessible name", errors)
        require(not control["nested_control"], f"{relative}: interactive controls are nested", errors)
        require(not control["nested_select"], f"{relative}: select is nested inside a link/button", errors)
        classes = set(attrs.get("class", "").split())
        if classes & {"search-toggle", "search-clear", "search-cancel", "theme-switch", "history-back", "share-button", "script-button"}:
            require(control["tag"] == "button", f"{relative}: scripted control is not a native button", errors)
        if control["tag"] == "button":
            require(attrs.get("type") == "button", f"{relative}: button lacks type=button", errors)
        stats["controls"] += 1

    for attrs in parser.icons:
        require(attrs.get("aria-hidden") == "true", f"{relative}: decorative icon is exposed to assistive technology", errors)
    for attrs in parser.iframes:
        require(bool(attrs.get("title", "").strip()), f"{relative}: iframe lacks a title", errors)
    for tag, _attrs in parser.menus:
        require(tag == "nav", f"{relative}: menu should use the native nav landmark", errors)
    navigation_names: list[str] = []
    for attrs in parser.navs:
        name = attrs.get("aria-label") or attrs.get("aria-labelledby", "")
        require(bool(name), f"{relative}: navigation landmark lacks a name", errors)
        if name:
            navigation_names.append(name)
    require(len(navigation_names) == len(set(navigation_names)), f"{relative}: repeated navigation landmarks have duplicate names", errors)

    responsive_headers = [
        attrs for attrs in parser.headers
        if set(attrs.get("class", "").split()) & {"desktop", "mobile"}
    ]
    header_names = [attrs.get("aria-label", "") for attrs in responsive_headers]
    require(all(header_names), f"{relative}: responsive header landmark lacks a name", errors)
    require(len(header_names) == len(set(header_names)), f"{relative}: repeated header landmarks have duplicate names", errors)

    for tag, attribute, value in parser.aria_states:
        require(value.lower() in VALID_ARIA_STATES, f"{relative}: <{tag}> has invalid {attribute}={value}", errors)

    theme_switches = [
        attrs for attrs in parser.buttons
        if "theme-switch" in set(attrs.get("class", "").split())
    ]
    if theme_switches:
        require(raw.count("<!-- accessibility-runtime:start -->") == 1, f"{relative}: theme/menu controls lack ARIA state runtime", errors)
        require("mask.addEventListener" in raw, f"{relative}: dismissing the menu does not synchronize ARIA state", errors)
        require(".search input" in raw, f"{relative}: search focus does not synchronize ARIA state", errors)
    for attrs in theme_switches:
        require(attrs.get("role") == "switch", f"{relative}: theme control lacks switch semantics", errors)
        require(attrs.get("aria-checked") in VALID_ARIA_STATES, f"{relative}: switch lacks aria-checked", errors)

    mobile_toggles = [
        attrs for attrs in parser.buttons
        if attrs.get("id") == "menu-toggle-mobile"
    ]
    if "id=\"menu-mobile\"" in raw:
        require(len(mobile_toggles) == 1, f"{relative}: mobile menu does not use one native button", errors)
        if mobile_toggles:
            require(mobile_toggles[0].get("aria-controls") == "menu-mobile", f"{relative}: mobile menu button lacks aria-controls", errors)
            require(mobile_toggles[0].get("aria-expanded") in VALID_ARIA_STATES, f"{relative}: mobile menu button lacks aria-expanded", errors)


def audit_readers(errors: list[str], stats: Counter[str]) -> None:
    for relative in READER_PAGES:
        raw = (ROOT / relative).read_text(encoding="utf-8")
        toggles = re.findall(r'<button\b[^>]*\bclass=["\'][^"\']*\bch-chevron\b[^"\']*["\'][^>]*>', raw, re.IGNORECASE)
        require(bool(toggles), f"{relative}: chapter accordions have no native toggle buttons", errors)
        for toggle in toggles:
            require('aria-expanded="false"' in toggle, f"{relative}: accordion toggle lacks collapsed state", errors)
            require("aria-controls=" in toggle, f"{relative}: accordion toggle lacks aria-controls", errors)
        stats["accordion_toggles"] += len(toggles)
        for control_id in ("btn-expand-all", "btn-collapse-all"):
            require(
                bool(re.search(rf'<button\b[^>]*\bid=["\']{control_id}["\']', raw, re.IGNORECASE)),
                f"{relative}: #{control_id} is not a native button",
                errors,
            )
        require("function setCardExpanded" in raw, f"{relative}: accordion ARIA state synchronizer is missing", errors)
        require("e.key === 'Escape'" in raw, f"{relative}: Escape does not close the mobile sidebar", errors)
        require("prefers-reduced-motion: reduce" in raw, f"{relative}: JS does not respect reduced motion", errors)
        require("[contenteditable=\"true\"]" in raw, f"{relative}: arrow shortcuts can override focused controls", errors)
        require("searchInput.focus()" in raw, f"{relative}: opening the mobile sidebar does not move focus", errors)
        require("getElementById('main-content').focus()" in raw, f"{relative}: closing after chapter selection leaves focus hidden", errors)
        require("aria-live=\"polite\"" in raw, f"{relative}: current chapter title is not announced", errors)

    for relative in ("scripts/build-aima-index.py", "scripts/build-software-architecture-index.py"):
        source = (ROOT / relative).read_text(encoding="utf-8")
        for token in ("setCardExpanded", "aria-expanded", "aria-controls", "closeSidebar(true)"):
            require(token in source, f"{relative}: generated reader source lacks {token}", errors)


def audit_pipeline(errors: list[str]) -> None:
    helper = (ROOT / "scripts/image_utils.py").read_text(encoding="utf-8")
    accessibility_call = 'run_postprocessor("update-accessibility.py")'
    performance_call = 'run_postprocessor("update-performance.py")'
    require(accessibility_call in helper, "image_utils.py does not run the accessibility post-processor", errors)
    require(
        helper.find(accessibility_call) > helper.find(performance_call) >= 0,
        "accessibility post-processing must run after performance post-processing",
        errors,
    )
    for relative in GENERATOR_SCRIPTS:
        source = (ROOT / relative).read_text(encoding="utf-8")
        require(
            "apply_site_postprocessors" in source and "apply_site_postprocessors()" in source,
            f"{relative}: generator is not connected to all site post-processors",
            errors,
        )

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/update-accessibility.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(
        result.returncode == 0,
        "accessibility post-processor is not idempotent: " + (result.stdout + result.stderr).strip(),
        errors,
    )


def main() -> int:
    errors: list[str] = []
    stats: Counter[str] = Counter()
    pages = html_pages()
    for path in pages:
        audit_page(path, errors, stats)
    audit_readers(errors, stats)
    audit_pipeline(errors)
    for foreground, background, minimum, label in CONTRAST_PAIRS:
        ratio = contrast_ratio(foreground, background)
        require(ratio >= minimum, f"{label} contrast is {ratio:.2f}:1, expected at least {minimum}:1", errors)

    require(stats["html"] == 74, f"expected 74 generated HTML files, found {stats['html']}", errors)
    require(stats["enhanced"] == 74, f"expected 74 enhanced pages, found {stats['enhanced']}", errors)
    require(stats["indexable"] == 73, f"expected 73 indexable pages, found {stats['indexable']}", errors)
    require(stats["skip_links"] == stats["enhanced"], "not every enhanced page has one skip link", errors)

    if errors:
        print(f"Accessibility audit failed with {len(errors)} issue(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        "Accessibility audit passed: "
        f"{stats['html']} HTML files; {stats['enhanced']} enhanced pages; "
        f"{stats['indexable']} indexable pages; {stats['skip_links']} skip links; "
        f"{stats['headings']} headings; {stats['controls']} named controls; "
        f"{stats['form_controls']} labeled form controls; {stats['table_headers']} scoped table headers; "
        f"{stats['disclosures']} native disclosures; {stats['accordion_toggles']} keyboard accordion toggles."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
