#!/usr/bin/env python3
"""Add a Persian «کمک شما» link (with a heart) to the English pages.

Every English page gets a menu item next to `Support` that points at the
Persian support page, and the English support page additionally gets a visible
banner at the top of its content so a visitor who landed there by mistake can
switch over.

Idempotent — running it twice changes nothing.

    python3 scripts/add-fa-support-link.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FA_HREF = "/support/"
MARKER = 'class="menu-item menu-item-fa"'

MENU_LINK = (
    f'<a href="{FA_HREF}" class="menu-item menu-item-fa" '
    'title="کمک شما - نسخه فارسی این صفحه">'
    '<i class="fas fa-heart fa-fw" aria-hidden="true"></i>'
    '<span lang="fa" dir="rtl">کمک شما</span></a>'
)

EN_SUPPORT_ITEM = (
    '<a href="/en/support.html" class="menu-item" title="Support">Support</a>'
)

STYLE = """
<style>
/* Persian support link in the English header */
.menu-item-fa{white-space:nowrap;}
.menu-item-fa .fa-heart{color:#e0245e;margin-right:.3rem;
  transition:transform .2s ease;}
.menu-item-fa:hover .fa-heart{transform:scale(1.18);}
.menu-item-fa span[lang="fa"]{
  font-family:Vazirmatn,"Segoe UI","Noto Naskh Arabic",Tahoma,sans-serif;}
[theme=dark] .menu-item-fa .fa-heart{color:#ff5c8a;}

/* Banner on the English support page */
.fa-support-banner{display:flex;align-items:center;gap:.75rem;flex-wrap:wrap;
  margin:0 0 2rem;padding:.9rem 1.1rem;border-radius:12px;text-decoration:none;
  border:1px solid rgba(224,36,94,.25);
  background:linear-gradient(135deg,rgba(224,36,94,.08),rgba(224,36,94,.02));
  color:inherit;transition:border-color .2s ease,transform .2s ease;}
.fa-support-banner:hover{border-color:rgba(224,36,94,.55);transform:translateY(-1px);}
.fa-support-banner .fa-heart{color:#e0245e;font-size:1.15rem;flex:none;}
.fa-support-banner .fa-banner-text{display:flex;flex-direction:column;gap:.15rem;}
.fa-support-banner .fa-banner-fa{direction:rtl;font-weight:600;
  font-family:Vazirmatn,"Segoe UI","Noto Naskh Arabic",Tahoma,sans-serif;}
.fa-support-banner .fa-banner-en{font-size:.86rem;opacity:.72;}
[theme=dark] .fa-support-banner{border-color:rgba(255,92,138,.28);
  background:linear-gradient(135deg,rgba(255,92,138,.10),rgba(255,92,138,.03));}
[theme=dark] .fa-support-banner:hover{border-color:rgba(255,92,138,.6);}
[theme=dark] .fa-support-banner .fa-heart{color:#ff5c8a;}
</style>
"""

BANNER = """<a class="fa-support-banner" href="/support/" hreflang="fa" lang="fa">
                            <i class="fas fa-heart" aria-hidden="true"></i>
                            <span class="fa-banner-text">
                                <span class="fa-banner-fa">کمک شما &mdash; این صفحه را به فارسی ببینید</span>
                                <span class="fa-banner-en" lang="en" dir="ltr">Prefer Persian? Open the Persian version of this page.</span>
                            </span>
                        </a>
                        """


def add_style(html: str) -> str:
    if "menu-item-fa{white-space" in html:
        return html
    return html.replace("</head>", f"{STYLE}</head>", 1)


def patch_generic(html: str) -> str:
    """English pages that already carry a `Support` menu item."""
    return html.replace(EN_SUPPORT_ITEM, EN_SUPPORT_ITEM + MENU_LINK)


def patch_en_support(html: str) -> str:
    """The English support page: no Support item, so prepend to both menus."""
    html = html.replace('<div class="menu-inner">', f'<div class="menu-inner">{MENU_LINK}', 1)
    html = html.replace(
        '<div class="menu" id="menu-mobile">', f'<div class="menu" id="menu-mobile">{MENU_LINK}', 1
    )
    if "fa-support-banner" not in html:
        html = html.replace(
            '<div class="support-intro">\n                            <h1>',
            f'<div class="support-intro">\n                            {BANNER}<h1>',
            1,
        )
    return html


def main() -> int:
    targets = sorted(
        p
        for p in ROOT.rglob("*.html")
        if ".git" not in p.parts
        and "lib" not in p.parts
        and (EN_SUPPORT_ITEM in p.read_text(encoding="utf-8") or p == ROOT / "en/support.html")
    )
    changed = []
    for page in targets:
        html = original = page.read_text(encoding="utf-8")
        if MARKER in html:
            print(f"  skip (already patched)  {page.relative_to(ROOT)}")
            continue
        html = patch_en_support(html) if page == ROOT / "en/support.html" else patch_generic(html)
        html = add_style(html)
        if html != original:
            page.write_text(html, encoding="utf-8")
            changed.append(str(page.relative_to(ROOT)))

    for name in changed:
        print(f"  patched  {name}")
    print(f"\n{len(changed)} page(s) updated out of {len(targets)} English page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
