#!/usr/bin/env python3
"""Shared navigation model for every standard (non-reader) site page."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

READER_PREFIXES = ("aima-4e/", "software-architecture/")


@dataclass(frozen=True)
class MenuItem:
    href: str
    label: str
    title: str
    icon: str = ""


MENU_ITEMS = (
    MenuItem(
        "/software-architecture/",
        "کتاب معماری نرم‌افزار",
        "مطالعه آنلاین کتاب مبانی معماری نرم‌افزار",
        '<i class="fas fa-cubes fa-fw" aria-hidden="true"></i> ',
    ),
    MenuItem(
        "/aima-4e/",
        "کتاب هوش مصنوعی",
        "مطالعه آنلاین کتاب هوش مصنوعی AIMA 4e",
        '<i class="fas fa-brain fa-fw" aria-hidden="true"></i> ',
    ),
    MenuItem(
        "/persian-streams/",
        "افزونه استرمیو Persian Streams",
        "افزونه فیلم و سریال ایرانی Persian Streams برای استرمیو",
    ),
    MenuItem(
        "/persian-subtitles/",
        "افزونه استرمیو Persian Subtitles",
        "افزونه زیرنویس فارسی Persian Subtitles برای استرمیو",
    ),
    MenuItem("/posts/", "مقالات", "آرشیو مقالات و بلاگ"),
    MenuItem(
        "/support/",
        "حمایت",
        "حمایت از پروژه‌ها",
        '<i class="fas fa-heart fa-fw" style="color:#e0245e;" aria-hidden="true"></i> ',
    ),
)

SEARCH_CONFIG = {
    "highlightTag": "em",
    "maxResultLength": 10,
    "noResultsFound": "نتیجه‌ای پیدا نشد",
    "snippetLength": 30,
}


def is_reader_page(relative: str | Path) -> bool:
    value = Path(relative).as_posix().lstrip("./")
    return value.startswith(READER_PREFIXES)


def active_menu_href(relative: str | Path) -> str:
    value = Path(relative).as_posix().lstrip("./")
    if value.startswith("posts/"):
        return "/posts/"
    for href in ("/persian-streams/", "/persian-subtitles/", "/support/"):
        if value == f"{href.strip('/')}/index.html":
            return href
    return ""


def _menu_link(item: MenuItem, active_href: str) -> str:
    active = item.href == active_href
    class_name = "menu-item active" if active else "menu-item"
    current = ' aria-current="page"' if active else ""
    return (
        f'<a href="{item.href}" class="{class_name}" title="{item.title}"{current}>'
        f"{item.icon}{item.label}</a>"
    )


def _search(desktop: bool) -> str:
    target = "desktop" if desktop else "mobile"
    tag = "span" if desktop else "div"
    classes = "menu-item search" if desktop else "search mobile"
    return f'''<{tag} class="{classes}" id="search-{target}">
                        <input type="text" placeholder="جستجو عنوان یا متن..." id="search-input-{target}" aria-label="جستجو عنوان یا متن..." autocomplete="off" enterkeyhint="search">
                        <button class="search-button search-toggle" id="search-toggle-{target}" title="جستجو" aria-controls="search-dropdown-{target}" aria-expanded="false" aria-label="جستجو" type="button">
                            <i class="fas fa-search fa-fw" aria-hidden="true"></i>
                        </button>
                        <button class="search-button search-clear" id="search-clear-{target}" title="پاک کردن" aria-label="پاک کردن" type="button">
                            <i class="fas fa-times-circle fa-fw" aria-hidden="true"></i>
                        </button>
                        <span class="search-button search-loading" id="search-loading-{target}" role="status" aria-live="polite" aria-label="در حال جستجو">
                            <i class="fas fa-spinner fa-fw fa-spin" aria-hidden="true"></i>
                        </span>
                    </{tag}>'''


def render_site_navigation(relative: str | Path = "", *, active_href: str | None = None) -> str:
    """Render the identical accessible header used outside the two book readers."""
    selected = active_menu_href(relative) if active_href is None else active_href
    menu = "".join(_menu_link(item, selected) for item in MENU_ITEMS)
    desktop_search = _search(desktop=True)
    mobile_search = _search(desktop=False)
    theme = '''<button class="menu-item theme-switch" title="تغییر ظاهر" role="switch" aria-checked="false" aria-label="تغییر ظاهر" type="button">
                    <i class="fas fa-adjust fa-fw" aria-hidden="true"></i>
                </button>'''

    return f'''<header class="desktop" id="header-desktop" dir="rtl" aria-label="سربرگ دسکتاپ" data-site-navigation="unified">
    <div class="header-wrapper">
        <div class="header-title">
            <a href="/" title="علی رستمی">علی رستمی</a>
        </div>
        <nav class="menu" dir="rtl" aria-label="پیمایش اصلی دسکتاپ" data-site-navigation="unified">
            <div class="menu-inner">{menu}{desktop_search}{theme}</div>
        </nav>
    </div>
</header><header class="mobile" id="header-mobile" dir="rtl" aria-label="سربرگ موبایل" data-site-navigation="unified">
    <div class="header-container">
        <div class="header-wrapper">
            <div class="header-title">
                <a href="/" title="علی رستمی">علی رستمی</a>
            </div>
            <button class="menu-toggle" id="menu-toggle-mobile" type="button" aria-label="باز کردن منوی اصلی" aria-controls="menu-mobile" aria-expanded="false">
                <span></span><span></span><span></span>
            </button>
        </div>
        <nav class="menu" id="menu-mobile" dir="rtl" aria-label="پیمایش اصلی موبایل" data-site-navigation="unified">{menu}<div class="search-wrapper">
                    {mobile_search}
                    <button class="search-cancel" id="search-cancel-mobile" type="button" aria-label="لغو جستجو">
                        لغو کردن
                    </button>
                </div>{theme}</nav>
    </div>
</header><div class="search-dropdown desktop">
        <div id="search-dropdown-desktop"></div>
    </div>
    <div class="search-dropdown mobile">
        <div id="search-dropdown-mobile"></div>
    </div>
'''
