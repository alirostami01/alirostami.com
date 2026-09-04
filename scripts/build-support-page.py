#!/usr/bin/env python3
"""Build the Persian support page inside the site's LoveIt theme shell.

One source of truth -> written to every URL the page must answer on:

    /support/            -> support/index.html      (canonical)
    /support.html        -> support.html            (legacy/extension URL)
    /fa/support/         -> fa/support/index.html
    /fa/support.html     -> fa/support.html         (legacy)

Usage:
    python3 scripts/build-support-page.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = "https://alirostami.com/support/"

WALLETS = [
    {
        "id": "bitcoin",
        "name": "بیت‌کوین",
        "symbol": "Bitcoin (BTC)",
        "network": "شبکه: Bitcoin",
        "icon": "fa-brands fa-bitcoin",
        "color": "#f7931a",
        "address": "bc1qg7xap7ys84j6s0zj7e607whwgak4gvzttw0yew",
        "note": "",
    },
    {
        "id": "usdt-trc20",
        "name": "تتر",
        "symbol": "USDT (TRC20)",
        "network": "شبکه: TRON (TRC20)",
        "icon": "fa-brands fa-tether",
        "color": "#26a17b",
        "address": "TEL83d98uJqtVcJfttjjK7dCEB7q9g7fg",
        "note": "فقط از شبکه TRC20 استفاده کنید؛ ارسال از شبکه‌های دیگر باعث از دست رفتن دارایی می‌شود.",
    },
    {
        "id": "ethereum",
        "name": "اتریوم",
        "symbol": "Ethereum (ETH)",
        "network": "شبکه: Ethereum (ERC20)",
        "icon": "fa-brands fa-ethereum",
        "color": "#627eea",
        "address": "0xD52B0e8a6244e1c155285020191199524349292f",
        "note": "",
    },
    {
        "id": "solana",
        "name": "سولانا",
        "symbol": "Solana (SOL)",
        "network": "شبکه: Solana",
        "icon": "fa-solid fa-coins",
        "color": "#14f195",
        "address": "BEXuadMGmKCPJQ7ZAvB4HooYjn6psMXARzr2doeie4y9",
        "note": "",
    },
]

PROJECTS = [
    {
        "title": "Persian Subtitles",
        "subtitle": "افزونه غیررسمی Stremio",
        "icon": "/images/projects/persian-subtitles.png",
        "url": "https://github.com/alirostami01/Persian-Subtitles",
        "docs": "/Persian-Subtitles/",
        "description": (
            "Persian Subtitles یک افزونه غیررسمی برای Stremio است که با دریافت شناسه IMDb "
            "از استرمیو، فیلم یا سریال متناظر را در SubSource پیدا می‌کند و زیرنویس‌های فارسی "
            "همان محتوا را به‌صورت فایل SRT آماده در اختیار Stremio می‌گذارد."
        ),
        "tags": ["Stremio", "زیرنویس فارسی", "SubSource", "SRT"],
    },
    {
        "title": "Persian Streams",
        "subtitle": "افزونه غیررسمی Stremio",
        "icon": "/images/projects/persian-streams.png",
        "url": "https://github.com/alirostami01/Persian-Streams",
        "docs": "/Persian-Streams/",
        "description": (
            "Persian Streams یک افزونه غیررسمی برای Stremio است که با دریافت شناسه IMDb "
            "از استرمیو، صفحه محتوای متناظر را در منبع ایرانیِ تنظیم‌شده پیدا می‌کند و "
            "لینک‌های مستقیم پخش/دانلود را به Stremio برمی‌گرداند."
        ),
        "tags": ["Stremio", "پخش آنلاین", "لینک مستقیم", "منبع ایرانی"],
    },
]

WHY = [
    ("fa-solid fa-screwdriver-wrench", "توسعه قابلیت‌های جدید"),
    ("fa-solid fa-bug", "رفع خطا و نگهداری پروژه‌ها"),
    ("fa-solid fa-server", "هزینه سرور، دامنه و زیرساخت"),
    ("fa-solid fa-book-open", "توسعه و نگهداری پروژه‌های متن‌باز"),
    ("fa-solid fa-rocket", "ساخت پروژه‌های تازه"),
]

NON_FINANCIAL = [
    ("fa-solid fa-star", "ستاره دادن به پروژه‌ها در گیت‌هاب"),
    ("fa-solid fa-bug", "گزارش باگ و مشکلات"),
    ("fa-solid fa-lightbulb", "پیشنهاد قابلیت‌های جدید"),
    ("fa-solid fa-file-lines", "بهبود مستندات"),
    ("fa-solid fa-code-branch", "مشارکت در کد"),
    ("fa-solid fa-bullhorn", "معرفی پروژه‌ها به دیگران"),
]

SOCIAL = [
    ("https://github.com/alirostami01", "fa-brands fa-github", "GitHub"),
    ("https://twitter.com/alirostami01", "fa-brands fa-twitter", "Twitter"),
    ("https://www.instagram.com/alirostami01", "fa-brands fa-instagram", "Instagram"),
    ("https://t.me/alirostami01", "fa-brands fa-telegram-plane", "Telegram"),
    ("https://linkedin.com/in/alirostami01", "fa-brands fa-linkedin", "LinkedIn"),
    ("mailto:rostami.ali@gmail.com", "fa-regular fa-envelope", "Email"),
]

STYLE = """
    /* ---------- Persian support page (theme-aware, scoped) ---------- */
    /* keep the theme header/footer in their original LTR layout */
    #header-desktop, #header-mobile, .footer { direction: ltr; }

    .support-page { direction: rtl; text-align: right; }
    .support-page .single-title { text-align: center; }
    .support-page .content { line-height: 2; }
    .support-page .content .support-lead {
        text-align: center;
        max-width: 44rem;
        margin: 0 auto 2.5rem;
        opacity: .85;
    }
    .support-page .content h2 {
        display: flex;
        align-items: center;
        gap: .5rem;
        margin: 2.6rem 0 1.2rem;
        font-size: 1.4rem;
        border-bottom: 1px solid rgba(128,128,128,.25);
        padding-bottom: .5rem;
    }
    .support-page .content h2 i { color: #2d96bd; font-size: 1.2rem; }
    [theme=dark] .support-page .content h2 i { color: #55bde2; }

    .support-page .content .support-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr));
        gap: 1rem;
    }
    .support-page .content .support-card {
        background: rgba(128,128,128,.07);
        border: 1px solid rgba(128,128,128,.2);
        border-radius: .8rem;
        padding: 1.1rem 1.2rem;
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .support-page .content .support-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 .5rem 1.2rem rgba(0,0,0,.12);
    }
    [theme=dark] .support-page .content .support-card { background: rgba(255,255,255,.04); }

    .support-page .content ul.support-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .support-page .content ul.support-list li {
        display: flex;
        align-items: center;
        gap: .6rem;
        padding: .35rem 0;
        line-height: 1.8;
    }
    .support-page .content ul.support-list li i {
        color: #2d96bd;
        width: 1.4rem;
        text-align: center;
        flex: 0 0 1.4rem;
    }
    [theme=dark] .support-page .content ul.support-list li i { color: #55bde2; }

    /* ---------- Rial / gateway ---------- */
    .support-page .content .donate-box { text-align: center; padding: 1.6rem 1.2rem; }
    .support-page .content a.donate-btn {
        display: inline-flex;
        align-items: center;
        gap: .5rem;
        margin-top: .8rem;
        padding: .65rem 1.6rem;
        border-radius: 2rem;
        background: linear-gradient(135deg, #e5405e, #ff7a5c);
        color: #fff;
        font-weight: 700;
        box-shadow: 0 .3rem .8rem rgba(229,64,94,.35);
    }
    .support-page .content a.donate-btn:hover { filter: brightness(1.08); color: #fff; }

    /* ---------- Wallets ---------- */
    .support-page .content .wallet-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr));
        gap: 1.2rem;
    }
    .support-page .content .wallet-card { text-align: center; }
    .support-page .content .wallet-head {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: .55rem;
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.6;
    }
    .support-page .content .wallet-head i { font-size: 1.5rem; }
    .support-page .content p.wallet-network {
        font-size: .82rem;
        opacity: .7;
        margin: .2rem 0 .9rem;
        line-height: 1.6;
    }
    .support-page .content img.qr {
        display: block;
        width: 168px;
        height: 168px;
        max-width: 100%;
        margin: 0 auto 1rem;
        background: #fff;
        padding: 8px;
        border-radius: .6rem;
        box-sizing: border-box;
        image-rendering: pixelated;
    }
    .support-page .content code.wallet-address {
        display: block;
        direction: ltr;
        text-align: center;
        word-break: break-all;
        line-break: anywhere;
        font-size: .72rem;
        line-height: 1.7;
        border-radius: .4rem;
        padding: .5rem .6rem;
        margin-bottom: .8rem;
    }
    .support-page .content button.copy-address {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        cursor: pointer;
        border: 1px solid rgba(128,128,128,.4);
        background: transparent;
        color: inherit;
        font-family: inherit;
        font-size: .85rem;
        line-height: 1.6;
        border-radius: 2rem;
        padding: .35rem 1rem;
        transition: background .2s ease, border-color .2s ease, color .2s ease;
    }
    .support-page .content button.copy-address:hover {
        background: rgba(45,150,189,.15);
        border-color: #2d96bd;
        color: #2d96bd;
    }
    .support-page .content button.copy-address.copied { border-color: #2ecc71; color: #2ecc71; }
    .support-page .content p.wallet-note {
        font-size: .78rem;
        line-height: 1.9;
        margin: .8rem 0 0;
        color: #c78b00;
    }
    [theme=dark] .support-page .content p.wallet-note { color: #e0b341; }

    /* ---------- Projects ---------- */
    .support-page .content .project-card {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        text-align: right;
    }
    .support-page .content .project-card > img {
        width: 80px;
        height: 80px;
        flex: 0 0 80px;
        border-radius: 50%;
        filter: drop-shadow(0 .2rem .5rem rgba(0,0,0,.25));
    }
    .support-page .content .project-body { flex: 1 1 auto; min-width: 0; }
    .support-page .content .project-body h3 { margin: 0 0 .1rem; font-size: 1.1rem; }
    .support-page .content p.project-sub { font-size: .82rem; opacity: .7; margin: 0 0 .5rem; line-height: 1.6; }
    .support-page .content .project-body p { margin: 0 0 .7rem; font-size: .92rem; line-height: 1.9; }
    .support-page .content .project-tags { display: flex; flex-wrap: wrap; gap: .35rem; margin-bottom: .7rem; }
    .support-page .content .project-tags span {
        font-size: .72rem;
        line-height: 1.9;
        padding: 0 .6rem;
        border-radius: 1rem;
        background: rgba(45,150,189,.15);
        color: #2d96bd;
    }
    [theme=dark] .support-page .content .project-tags span { color: #55bde2; }
    .support-page .content .project-links {
        display: flex;
        flex-wrap: wrap;
        gap: .3rem 1.1rem;
    }
    .support-page .content a.project-link {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        font-size: .85rem;
    }

    /* ---------- Contact ---------- */
    .support-page .content .support-social {
        display: flex;
        justify-content: center;
        gap: 1.2rem;
        font-size: 1.5rem;
        margin-top: .8rem;
    }
    .support-page .content .support-social a { opacity: .85; }
    .support-page .content .support-social a:hover { opacity: 1; }

    @media only screen and (max-width: 680px) {
        .support-page .content .project-card { flex-direction: column; align-items: center; text-align: center; }
        .support-page .content .project-tags { justify-content: center; }
    }
"""


def header(active_home: str = "/fa/") -> str:
    return f"""<div id="mask"></div><div class="wrapper"><header class="desktop" id="header-desktop">
    <div class="header-wrapper">
        <div class="header-title">
            <a href="{active_home}" title="فارسی">Ali Rostami</a>
        </div>
        <div class="menu">
            <div class="menu-inner"><a href="/fa/" class="menu-item" title="خانه">خانه</a><a href="/support/" class="menu-item active" title="حمایت">حمایت</a><a href="javascript:void(0);" class="menu-item theme-switch" title="تغییر ظاهر">
                    <i class="fas fa-adjust fa-fw" aria-hidden="true"></i>
                </a><a href="javascript:void(0);" class="menu-item language" title="انتخاب زبان">
                    <i class="fa fa-globe" aria-hidden="true"></i>
                    <select class="language-select" id="language-select-desktop" onchange="location = this.value;"><option value="/en/support.html">English</option><option value="/support/" selected>فارسی</option></select>
                </a></div>
        </div>
    </div>
</header><header class="mobile" id="header-mobile">
    <div class="header-container">
        <div class="header-wrapper">
            <div class="header-title">
                <a href="{active_home}" title="فارسی">Ali Rostami</a>
            </div>
            <div class="menu-toggle" id="menu-toggle-mobile">
                <span></span><span></span><span></span>
            </div>
        </div>
        <div class="menu" id="menu-mobile"><a href="/fa/" class="menu-item" title="خانه">خانه</a><a href="/support/" class="menu-item active" title="حمایت">حمایت</a><a href="javascript:void(0);" class="menu-item theme-switch" title="تغییر ظاهر">
                <i class="fas fa-adjust fa-fw" aria-hidden="true"></i>
            </a><a href="javascript:void(0);" class="menu-item" title="انتخاب زبان">
                    <i class="fa fa-globe fa-fw" aria-hidden="true"></i>
                    <select class="language-select" onchange="location = this.value;"><option value="/en/support.html">English</option><option value="/support/" selected>فارسی</option></select>
                </a></div>
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
        </div><script type="text/javascript" src="https://cdn.jsdelivr.net/npm/lazysizes@5.3.2/lazysizes.min.js"></script><script type="text/javascript">window.config={"code":{"copyTitle":"کپی به کلیپ بورد","maxShownLines":50}};</script><script type="text/javascript" src="/js/theme.min.js"></script><script type="text/javascript">
    document.querySelectorAll('.copy-address').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var address = btn.getAttribute('data-address');
            var done = function () {
                var original = btn.innerHTML;
                btn.classList.add('copied');
                btn.innerHTML = '<i class="fas fa-check fa-fw" aria-hidden="true"></i> کپی شد';
                setTimeout(function () {
                    btn.classList.remove('copied');
                    btn.innerHTML = original;
                }, 2000);
            };
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(address).then(done);
            } else {
                var input = document.createElement('textarea');
                input.value = address;
                document.body.appendChild(input);
                input.select();
                document.execCommand('copy');
                document.body.removeChild(input);
                done();
            }
        });
    });
    </script>"""


def wallet_html(w: dict) -> str:
    note = (
        f'\n            <p class="wallet-note"><i class="fas fa-triangle-exclamation fa-fw" aria-hidden="true"></i> {w["note"]}</p>'
        if w["note"]
        else ""
    )
    return f"""<div class="support-card wallet-card">
            <div class="wallet-head"><i class="{w['icon']}" style="color:{w['color']}" aria-hidden="true"></i><span>{w['name']}</span></div>
            <p class="wallet-network">{w['symbol']} &middot; {w['network']}</p>
            <img class="qr" src="/images/donate/{w['id']}.png" alt="کد QR آدرس {w['name']}" width="168" height="168" loading="lazy" decoding="async">
            <code class="wallet-address">{w['address']}</code>
            <button type="button" class="copy-address" data-address="{w['address']}"><i class="fas fa-copy fa-fw" aria-hidden="true"></i> کپی آدرس</button>{note}
        </div>"""


def project_html(p: dict) -> str:
    tags = "".join(f"<span>{t}</span>" for t in p["tags"])
    docs = (
        f'<a class="project-link" href="{p["docs"]}">'
        '<i class="fas fa-book fa-fw" aria-hidden="true"></i> مستندات فارسی</a>'
        if p.get("docs")
        else ""
    )
    return f"""<div class="support-card project-card">
            <img src="{p['icon']}" alt="آیکون پروژه {p['title']}" width="80" height="80" loading="lazy" decoding="async">
            <div class="project-body">
                <h3>{p['title']}</h3>
                <p class="project-sub">{p['subtitle']}</p>
                <p>{p['description']}</p>
                <div class="project-tags">{tags}</div>
                <div class="project-links"><a class="project-link" href="{p['url']}" target="_blank" rel="noopener noreferrer"><i class="fab fa-github fa-fw" aria-hidden="true"></i> مشاهده در گیت‌هاب</a>{docs}</div>
            </div>
        </div>"""


def build(canonical: str) -> str:
    why = "".join(
        f'\n            <li><i class="{i}" aria-hidden="true"></i><span>{t}</span></li>' for i, t in WHY
    )
    non_fin = "".join(
        f'\n            <li><i class="{i}" aria-hidden="true"></i><span>{t}</span></li>' for i, t in NON_FINANCIAL
    )
    wallets = "\n        ".join(wallet_html(w) for w in WALLETS)
    projects = "\n        ".join(project_html(p) for p in PROJECTS)
    social = "".join(
        f'<a href="{u}" title="{t}" target="_blank" rel="noopener noreferrer"><i class="{i} fa-fw" aria-hidden="true"></i></a>'
        for u, i, t in SOCIAL
    )

    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
    <head>
        <meta name="generator" content="Hugo 0.92.2" />
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="robots" content="noodp" />
        <title>حمایت از پروژه‌های من - علی رستمی</title><meta name="Description" content="حمایت مالی و غیرمالی از پروژه‌های متن‌باز علی رستمی؛ درگاه پرداخت ریالی و کیف‌پول‌های ارز دیجیتال به همراه کد QR."><meta property="og:title" content="حمایت از پروژه‌های من" />
<meta property="og:description" content="حمایت مالی و غیرمالی از پروژه‌های متن‌باز علی رستمی؛ درگاه پرداخت ریالی و کیف‌پول‌های ارز دیجیتال به همراه کد QR." />
<meta property="og:type" content="website" />
<meta property="og:url" content="{CANONICAL}" /><meta property="og:site_name" content="علی رستمی" />
<meta name="twitter:card" content="summary"/>
<meta name="twitter:title" content="حمایت از پروژه‌های من"/>
<meta name="twitter:description" content="حمایت مالی و غیرمالی از پروژه‌های متن‌باز علی رستمی."/>
<meta name="application-name" content="Ali Rostami">
<meta name="apple-mobile-web-app-title" content="Ali Rostami"><meta name="theme-color" content="#ffffff"><meta name="msapplication-TileColor" content="#da532c"><link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="mask-icon" href="/safari-pinned-tab.svg" color="#5bbad5"><link rel="manifest" href="/site.webmanifest"><link rel="canonical" href="{canonical}" /><link rel="alternate" hreflang="fa" href="{CANONICAL}" /><link rel="alternate" hreflang="en" href="https://alirostami.com/en/support.html" /><link rel="stylesheet" href="/css/style.min.css"><link rel="preload" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.1.1/css/all.min.css"></noscript><link rel="preload" href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css"></noscript><script type="application/ld+json">
    {{
        "@context": "http://schema.org",
        "@type": "WebPage",
        "url": "{CANONICAL}",
        "inLanguage": "fa",
        "name": "حمایت از پروژه‌های من",
        "description": "حمایت مالی و غیرمالی از پروژه‌های متن‌باز علی رستمی.",
        "license": "Everything is mine"
    }}
    </script><style>{STYLE}</style></head>
    <body data-header-desktop="fixed" data-header-mobile="auto"><script type="text/javascript">(window.localStorage && localStorage.getItem('theme') ? localStorage.getItem('theme') === 'dark' : ('auto' === 'auto' ? window.matchMedia('(prefers-color-scheme: dark)').matches : 'auto' === 'dark')) && document.body.setAttribute('theme', 'dark');</script>

        {header()}<main class="main">
                <div class="container"><article class="page single support-page">
        <h1 class="single-title animate__animated animate__flipInX">حمایت از پروژه‌های من</h1>
        <div class="content" id="content">
        <p class="support-lead">اگر یکی از پروژه‌های من برای شما مفید بوده، با حمایت مالی یا غیرمالی می‌توانید به ادامه توسعه، نگهداری و بهبود آن‌ها کمک کنید. هر کمکی، هرچقدر هم کوچک، دلگرم‌کننده است. ❤️</p>

        <h2><i class="fas fa-circle-question fa-fw" aria-hidden="true"></i>چرا حمایت کنیم؟</h2>
        <div class="support-card">
          <ul class="support-list">{why}
          </ul>
        </div>

        <h2><i class="fas fa-money-bill-wave fa-fw" aria-hidden="true"></i>حمایت ریالی</h2>
        <div class="support-card donate-box">
            <p>برای حمایت مالی از داخل ایران می‌توانید از درگاه امن زیر استفاده کنید:</p>
            <a href="https://pay.example.com/donate" target="_blank" rel="noopener noreferrer" class="donate-btn"><i class="fas fa-heart fa-fw" aria-hidden="true"></i> پرداخت از طریق درگاه</a>
        </div>

        <h2><i class="fab fa-bitcoin fa-fw" aria-hidden="true"></i>کیف‌پول‌های ارز دیجیتال</h2>
        <p>کد QR هر کیف‌پول دقیقاً همان آدرس نوشته‌شده در کارت را در خود دارد؛ می‌توانید آن را اسکن کنید یا آدرس را کپی کنید.</p>
        <div class="wallet-grid">
        {wallets}
        </div>

        <h2><i class="fas fa-rocket fa-fw" aria-hidden="true"></i>پروژه‌های من</h2>
        <div class="support-grid">
        {projects}
        </div>

        <h2><i class="fas fa-star fa-fw" aria-hidden="true"></i>حمایت غیرمالی</h2>
        <div class="support-card">
          <ul class="support-list">{non_fin}
          </ul>
        </div>

        <h2><i class="fas fa-comments fa-fw" aria-hidden="true"></i>ارتباط با من</h2>
        <div class="support-card" style="text-align:center">
            <p>اگر سؤال یا پیشنهادی دارید، از هر یک از راه‌های زیر در دسترس هستم:</p>
            <div class="support-social">{social}</div>
        </div>
        </div>
    </article></div>
            </main>{FOOTER}

        {SCRIPTS}</body>
</html>
"""


TARGETS = {
    "support/index.html": CANONICAL,
    "support.html": CANONICAL,
    "fa/support/index.html": CANONICAL,
    "fa/support.html": CANONICAL,
}


def main() -> None:
    for rel, canonical in TARGETS.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build(canonical), encoding="utf-8")
        print(f"wrote {rel} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
