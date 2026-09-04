#!/usr/bin/env python3
"""Shared LoveIt-theme page shell used by the hand-built pages of this site.

The site is a published Hugo build, so these pages are generated as plain HTML
that reuses the theme's own stylesheet (/css/style.min.css) and script
(/js/theme.min.js) to stay visually identical to the rest of alirostami.com.
"""

SITE_NAME = "علی رستمی"


def header(active: str = "") -> str:
    """Desktop + mobile header. `active` is the href of the current menu item."""

    def item(href: str, label: str) -> str:
        cls = "menu-item active" if href == active else "menu-item"
        return f'<a href="{href}" class="{cls}" title="{label}">{label}</a>'

    menu = item("/fa/", "خانه") + item("/support/", "حمایت")
    lang = (
        '<a href="javascript:void(0);" class="menu-item language" title="انتخاب زبان">'
        '<i class="fa fa-globe" aria-hidden="true"></i>'
        '<select class="language-select" onchange="location = this.value;">'
        '<option value="/en/support.html">English</option>'
        '<option value="/support/" selected>فارسی</option></select></a>'
    )
    theme_switch = (
        '<a href="javascript:void(0);" class="menu-item theme-switch" title="تغییر ظاهر">'
        '<i class="fas fa-adjust fa-fw" aria-hidden="true"></i></a>'
    )
    return f"""<div id="mask"></div><div class="wrapper"><header class="desktop" id="header-desktop">
    <div class="header-wrapper">
        <div class="header-title">
            <a href="/fa/" title="{SITE_NAME}">Ali Rostami</a>
        </div>
        <div class="menu">
            <div class="menu-inner">{menu}{theme_switch}{lang}</div>
        </div>
    </div>
</header><header class="mobile" id="header-mobile">
    <div class="header-container">
        <div class="header-wrapper">
            <div class="header-title">
                <a href="/fa/" title="{SITE_NAME}">Ali Rostami</a>
            </div>
            <div class="menu-toggle" id="menu-toggle-mobile">
                <span></span><span></span><span></span>
            </div>
        </div>
        <div class="menu" id="menu-mobile">{menu}{theme_switch}{lang}</div>
    </div>
</header>"""


FOOTER = """<footer class="footer">
        <div class="footer-container"><div class="footer-line">ایجاد شده توسط <a href="https://gohugo.io/" target="_blank" rel="noopener noreffer" title="Hugo 0.92.2">Hugo</a> | پوسته - <a href="https://github.com/dillonzq/LoveIt" target="_blank" rel="noopener noreffer" title="LoveIt 0.2.11"><i class="far fa-kiss-wink-heart fa-fw" aria-hidden="true"></i> LoveIt</a>
                </div><div class="footer-line" itemscope itemtype="http://schema.org/CreativeWork"><i class="far fa-copyright fa-fw" aria-hidden="true"></i><span itemprop="copyrightYear">2022 - 2026</span><span class="author" itemprop="copyrightHolder">&nbsp;<a href="/fa/">علی رستمی</a></span></div>
        </div>
    </footer></div>"""


SCRIPTS = """<div id="fixed-buttons"><a href="#" id="back-to-top" class="fixed-button" title="برگشت به بالا">
                <i class="fas fa-arrow-up fa-fw" aria-hidden="true"></i>
            </a>
        </div><script type="text/javascript" src="https://cdn.jsdelivr.net/npm/lazysizes@5.3.2/lazysizes.min.js"></script><script type="text/javascript">window.config={"code":{"copyTitle":"کپی به کلیپ بورد","maxShownLines":50}};</script><script type="text/javascript" src="/js/theme.min.js"></script>"""


def page(
    *,
    title: str,
    description: str,
    canonical: str,
    body: str,
    style: str = "",
    extra_head: str = "",
    extra_scripts: str = "",
    active_menu: str = "",
    og_type: str = "website",
) -> str:
    """Wrap `body` (everything inside <main>) in the full themed HTML document."""
    style_block = f"<style>{style}</style>" if style else ""
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
    <head>
        <meta name="generator" content="Hugo 0.92.2" />
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="robots" content="noodp" />
        <title>{title}</title><meta name="Description" content="{description}"><meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:url" content="{canonical}" /><meta property="og:site_name" content="{SITE_NAME}" />
<meta name="twitter:card" content="summary"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{description}"/>
<meta name="application-name" content="Ali Rostami">
<meta name="apple-mobile-web-app-title" content="Ali Rostami"><meta name="theme-color" content="#ffffff"><meta name="msapplication-TileColor" content="#da532c"><link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="canonical" href="{canonical}" /><link rel="stylesheet" href="/css/style.min.css"><link rel="preload" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css"></noscript><link rel="preload" href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css"></noscript>{extra_head}{style_block}</head>
    <body data-header-desktop="fixed" data-header-mobile="auto"><script type="text/javascript">(window.localStorage && localStorage.getItem('theme') ? localStorage.getItem('theme') === 'dark' : ('auto' === 'auto' ? window.matchMedia('(prefers-color-scheme: dark)').matches : 'auto' === 'dark')) && document.body.setAttribute('theme', 'dark');</script>

        {header(active_menu)}<main class="main">
                <div class="container">{body}</div>
            </main>{FOOTER}

        {SCRIPTS}{extra_scripts}</body>
</html>
"""
