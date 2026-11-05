#!/usr/bin/env python3
"""Shared LoveIt-theme page shell used by the hand-built pages of this site.

The site is a published Hugo build, so these pages are generated as plain HTML
that reuses the theme's own stylesheet (/css/style.min.css) and script
(/js/theme.min.js) to stay visually identical to the rest of alirostami.com.
"""

from site_navigation import render_site_navigation

SITE_NAME = "علی رستمی"


def header(active: str = "") -> str:
    """Return the shared desktop/mobile shell used by every non-reader page."""
    return f'<div id="mask"></div><div class="wrapper">{render_site_navigation(active_href=active)}'


FOOTER = """<footer class="footer">
        <div class="footer-container"><div class="footer-line">ایجاد شده توسط <a href="https://gohugo.io/" target="_blank" rel="noopener noreffer" title="Hugo 0.92.2">Hugo</a> | پوسته - <a href="https://github.com/dillonzq/LoveIt" target="_blank" rel="noopener noreffer" title="LoveIt 0.2.11"><i class="far fa-kiss-wink-heart fa-fw" aria-hidden="true"></i> LoveIt</a>
                </div><div class="footer-line" itemscope itemtype="http://schema.org/CreativeWork"><i class="far fa-copyright fa-fw" aria-hidden="true"></i>2022 - <span itemprop="copyrightYear">2026</span><span class="author" itemprop="copyrightHolder">&nbsp;<a href="/">علی رستمی</a></span></div>
        </div>
    </footer></div>"""


SCRIPTS = """<div id="fixed-buttons"><a href="#" id="back-to-top" class="fixed-button" title="برگشت به بالا">
                <i class="fas fa-arrow-up fa-fw" aria-hidden="true"></i>
            </a>
        </div><script type="text/javascript">window.config={"code":{"copyTitle":"کپی به کلیپ بورد","maxShownLines":50},"search":{"highlightTag":"em","maxResultLength":10,"noResultsFound":"نتیجه‌ای پیدا نشد","snippetLength":30}};</script>
        <script defer src="/lib/autocomplete/autocomplete.min.js"></script>
        <script defer src="/lib/lunr/lunr.min.js"></script>
        <script defer src="/js/theme.min.js"></script>"""


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
<meta property="og:url" content="{canonical}" /><meta property="og:image" content="https://www.alirostami.com/images/social/ali-rostami.jpg" />
        <meta property="og:image:alt" content="علی رستمی؛ معماری نرم‌افزار، هوش مصنوعی و پروژه‌های متن‌باز" />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
<meta property="og:site_name" content="{SITE_NAME}" />
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:image" content="https://www.alirostami.com/images/social/ali-rostami.jpg"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{description}"/>
<meta name="application-name" content="Ali Rostami">
<meta name="apple-mobile-web-app-title" content="Ali Rostami"><meta name="theme-color" content="#ffffff"><meta name="msapplication-TileColor" content="#da532c"><link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="192x192" href="/android-chrome-192x192.png">
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><link rel="canonical" href="{canonical}" /><link rel="stylesheet" href="/css/style.min.css">
        <!-- performance-icons:start -->
        <style>.fa,.fas,.far,.fab,.fa-solid,.fa-regular,.fa-brands{{display:inline-block;min-width:1em;text-align:center}}.fa-fw{{width:1.25em}}</style>
        <link rel="preload" href="/lib/fontawesome/all.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="/lib/fontawesome/all.min.css"></noscript>
        <!-- performance-icons:end -->
        <!-- performance-animations:start -->
        <link rel="preload" href="/lib/animate/animate-subset.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="/lib/animate/animate-subset.min.css"></noscript>
        <!-- performance-animations:end -->{extra_head}{style_block}</head>
    <body data-header-desktop="fixed" data-header-mobile="auto"><script type="text/javascript">(window.localStorage && localStorage.getItem('theme') ? localStorage.getItem('theme') === 'dark' : ('auto' === 'auto' ? window.matchMedia('(prefers-color-scheme: dark)').matches : 'auto' === 'dark')) && document.body.setAttribute('theme', 'dark');</script>

        {header(active_menu)}<main class="main">
                <div class="container">{body}</div>
            </main>{FOOTER}

        {SCRIPTS}{extra_scripts}</body>
</html>
"""
