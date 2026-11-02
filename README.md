# alirostami.com

استاتیک سایت شخصی (خروجی Hugo + پوسته LoveIt) که مستقیماً از همین مخزن سرو می‌شود.

## دامنه و URLهای canonical

دامنه و صفحهٔ اصلی ترجیحی سایت:

```text
https://www.alirostami.com/
```

صفحهٔ اصلی فارسی است (`fa-IR`) و `/fa/` یک alias قدیمی محسوب می‌شود. URLهای
canonical با حروف کوچک و، برای صفحات پوشه‌ای، با اسلش انتهایی نوشته می‌شوند.
صفحات فصل‌ها مطابق رفتار Cloudflare Pages بدون پسوند `.html` canonical هستند؛
نسخهٔ دارای پسوند با 301 به همان URL بدون پسوند می‌رود. تمام aliasها باید در
Cloudflare با پاسخ **301** به URL نهایی برسند. فایل‌های
HTML مربوط به aliasها فقط fallbackهای کوچک `noindex` هستند تا در محیط‌های
بدون Rule لبه، محتوای تکراری کامل سرو نشود:

```bash
python3 scripts/redirects.py
```

فهرست aliasها در `scripts/redirects.py` منبع واحد redirectهای URL است. این
اسکریپت علاوه بر fallbackهای HTML، فایل `_redirects` را نیز می‌سازد. Cloudflare
Pages این manifest را هنگام deploy می‌خواند و برای تمام aliasهای ثبت‌شده پاسخ
301 می‌دهد.

### Ruleهای موردنیاز Cloudflare

اسکریپت `redirects.py` دو manifest لبه می‌سازد:

- `_redirects`: برای Cloudflare Pages؛ تمام aliasها روی host فعلی 301 می‌شوند.
- `cloudflare-bulk-redirects.csv`: برای import در **Bulk Redirects**؛ aliasها را
  روی هر دو host مستقیماً به مقصد `https://www...` می‌برد و host/scheme سایر
  مسیرها را نیز یک‌مرحله‌ای normalize می‌کند. فایل CSV header ندارد و Query
  String را حفظ می‌کند.

برای production، CSV در یک **Bulk Redirect List** import و سپس آن List با یک
**Bulk Redirect Rule** فعال شود. این روش همهٔ ترکیب‌های HTTP/HTTPS و
www/non-www را بدون زنجیرهٔ redirect پوشش می‌دهد. تبدیل سراسری Path به حروف
کوچک نباید فعال شود؛ چون نام بعضی assetها case-sensitive است.

اگر Bulk Redirects قابل استفاده نبود، `_redirects` aliasهای Cloudflare Pages را
پوشش می‌دهد و یک **Single Redirect** جداگانه برای host ساخته می‌شود. شرط:

```text
(http.host eq "alirostami.com") or
(http.host eq "www.alirostami.com" and
 starts_with(http.request.full_uri, "http://"))
```

نوع مقصد **Dynamic** و expression آن چنین است:

```text
concat("https://www.alirostami.com", http.request.uri.path)
```

Status Code برابر `301` و گزینهٔ **Preserve query string** روشن باشد. خروجی:

```text
http://alirostami.com/*       → https://www.alirostami.com/*  (301)
https://alirostami.com/*      → https://www.alirostami.com/*  (301)
http://www.alirostami.com/*   → https://www.alirostami.com/*  (301)
```

این حالت fallback ممکن است برای alias روی host غیرترجیحی دو hop ایجاد کند؛ CSV
روش ترجیحی برای redirect تک‌مرحله‌ای است. Query String باید حفظ شود. مسیرهای قدیمی Feed و Sitemap نیز redirect می‌شوند:

```text
/fa/sitemap.xml              → /sitemap.xml
/en/sitemap.xml              → /sitemap.xml
/public/sitemap.xml          → /sitemap.xml
/public/fa/sitemap.xml       → /sitemap.xml
/fa/index.xml                → /index.xml
/fa/categories/index.xml     → /categories/index.xml
/fa/tags/index.xml           → /tags/index.xml
```

Sitemap واحد سایت فقط URLهای canonical را دارد:

```bash
python3 scripts/update-sitemaps.py
python3 scripts/check-seo-urls.py
```

اعتبارسنجی واقعی 301 و 200 با runtime محلی Cloudflare Pages:

```bash
npx --yes wrangler@latest pages dev . --port 8788
python3 scripts/check-production-redirects.py --origin http://127.0.0.1:8788
```

پس از deploy و فعال‌سازی Bulk Redirect Rule، audit production اجرا می‌شود:

```bash
python3 scripts/check-production-redirects.py
```

## صفحه حمایت

| آدرس | نقش | فایل |
|---|---|---|
| `/support/` | canonical فارسی | `support/index.html` |
| `/en/support/` | canonical انگلیسی | `en/support/index.html` |
| `/support.html` | alias → `/support/` | `support.html` |
| `/fa/support/` | alias → `/support/` | `fa/support/index.html` |
| `/fa/support.html` | alias → `/support/` | `fa/support.html` |
| `/en/support.html` | alias → `/en/support/` | `en/support.html` |

### بازتولید صفحه

```bash
python3 scripts/build-support-page.py
```

محتوای فارسی صفحه (متن‌ها، کیف‌پول‌ها، پروژه‌ها و CSS) داخل همان اسکریپت است.
اسکریپت، صفحه canonical فارسی و fallbackهای redirect آن را می‌سازد.

### کدهای QR کیف‌پول‌ها

هر QR دقیقاً خودِ آدرس کیف‌پول را کدگذاری می‌کند (بدون URI scheme یا مبلغ):

```bash
pip install segno
python3 scripts/generate-wallet-qr.py     # -> images/donate/*.png و *.svg
```

پس از هر تغییر آدرس، برای اینکه مرورگر بازدیدکننده QR قدیمی را از کش نشان ندهد،
باید هش محتوا روی آدرس تصویرها زده شود (idempotent است):

```bash
python3 scripts/stamp-qr-cache.py         # -> /images/donate/x.png?v=<md5[:8]>
```

بررسی صحت (دیکود واقعی هر QR روی همهٔ صفحات و مقایسه با آدرس نمایش‌داده‌شده):

```bash
pip install opencv-python-headless segno
python3 scripts/verify-wallet-qr.py
```

ترتیب کامل بعد از عوض شدن یک آدرس ولت:

```bash
python3 scripts/generate-wallet-qr.py
python3 scripts/build-support-page.py
python3 scripts/stamp-qr-cache.py
python3 scripts/verify-wallet-qr.py
```

### لینک فارسی روی صفحات انگلیسی

لینک «کمک شما» در صفحهٔ انگلیسی Support به `/support/` می‌رود:

```bash
python3 scripts/add-fa-support-link.py    # idempotent
```

## صفحات مستندات پروژه‌ها

محتوا در `content/<slug>.md` نگهداری می‌شود. URLهای canonical همگی lowercase هستند:

| URL canonical | منبع |
|---|---|
| `/persian-subtitles/` | `content/persian-subtitles.md` |
| `/persian-streams/` | `content/persian-streams.md` |
| `/aima-4e-persian/` | `content/aima-4e-persian.md` |
| `/fundamentals-of-software-architecture-persian/` | قالب `scripts/build-project-page.py` |

aliasهای قدیمی مانند `/Persian-Streams/`، نسخه‌های `.html` و مسیرهای تکراری
`/posts/persian-*/` باید فقط به URLهای بالا redirect شوند.

```bash
pip install markdown
python3 scripts/build-project-page.py
python3 scripts/redirects.py
```

پوستهٔ مشترک صفحات دست‌ساز در `scripts/theme.py` است.

### آیکون پروژه‌ها

آیکون‌ها در `images/projects/<slug>.png` قرار می‌گیرند. برای آماده‌سازی لوگوی جدید:

```bash
pip install pillow
python3 scripts/prepare-project-icon.py /path/to/logo.png persian-subtitles
python3 scripts/build-support-page.py
```

اسکریپت پس‌زمینه سفید دور لوگوی دایره‌ای را شفاف می‌کند و تصویر را به اندازه
۲۵۶×۲۵۶ ذخیره می‌کند.

## بهینه‌سازی و SEO تصاویر

کارت‌های نمایندهٔ صفحات با ابعاد استاندارد `1200×630` در `images/social/`
تولید می‌شوند. همان build، نسخه‌های responsive تصویر پروفایل و جلد بهینهٔ
کتاب AIMA را نیز می‌سازد و سپس metadata تصویری و ویژگی‌های تصاویر HTML را
به‌صورت idempotent به‌روز می‌کند:

```bash
python3 -m pip install pillow
python3 scripts/build-social-images.py
```

فقط برای اجرای دوبارهٔ post-processor (بدون Pillow):

```bash
python3 scripts/update-image-seo.py
```

post-processor برای همهٔ صفحات indexable (از جمله همهٔ URLهای sitemap)،
`og:image`، Twitter Card، تصویر JSON-LD و `max-image-preview:large` را تنظیم
می‌کند. برای تمام تگ‌های `img` نیز `width`، `height`، `loading` و `decoding` ثبت می‌شود. generatorهای صفحات و
sitemap در انتهای اجرا همین post-processor را فراخوانی می‌کنند تا خروجی build
از metadata تصویری جدا نشود.

ممیزی مستقل و بدون dependency ثالث:

```bash
python3 scripts/check-images.py
```

## Performance و Core Web Vitals

dependencyهای مرورگر با نسخهٔ دقیق در `lib/` نگهداری می‌شوند و در زمان اجرا
درخواستی به jsDelivr ارسال نمی‌شود. فهرست نسخه‌ها، مسیرهای upstream و تغییرهای
عمدی در `lib/VENDOR.md` ثبت شده است. Font Awesome با `font-display: swap` و
Animate.css به‌صورت subset حداقلی سرو می‌شوند؛ هر دو stylesheet غیرحیاتی با
`preload`/`onload` و fallback داخل `noscript` بارگذاری می‌شوند.

post-processor عملکرد، بر اساس DOM هر صفحه فقط dependency موردنیاز را پیش از
`theme.min.js` و با `defer` اضافه می‌کند: search به autocomplete/Lunr، دکمه‌های
share به Sharer و TypeIt فقط به هدف واقعی TypeIt متصل می‌شوند. ClipboardJS در
خروجی فعلی بارگذاری نمی‌شود، lazysizes بلااستفاده حذف شده و embed خراب Disqus
نیز حذف می‌شود. تصاویر بالای صفحه که `fetchpriority="high"` دارند به‌طور
خودکار در `<head>` preload می‌شوند.

اجرای دستی و بررسی idempotence:

```bash
python3 scripts/update-performance.py
python3 scripts/update-performance.py --check
python3 scripts/check-performance.py
```

تمام generatorهای مستندشده ابتدا post-processor تصاویر و سپس post-processor
Performance را از طریق `apply_site_postprocessors()` اجرا می‌کنند. بنابراین
پس از بازتولید هر صفحه، اجرای جداگانه لازم نیست؛ بااین‌حال audit نهایی هر دو فاز
باید اجرا شود:

```bash
python3 scripts/check-images.py
python3 scripts/check-seo-urls.py
python3 scripts/check-performance.py
```

فایل `_headers` سیاست Cloudflare Pages را تعریف می‌کند: CSP و headerهای
سخت‌سازی مرورگر روی همهٔ پاسخ‌های استاتیک اعمال می‌شوند، `comments.app` تنها
runtime خارجی مجاز است و assetهای vendor تا ۳۰ روز و CSS/JS دست‌اول تا ۷ روز
cache می‌شوند. چون نام فایل‌ها content hash ندارد، از `immutable` استفاده نشده
است. بعد از تغییر عمدی یک فایل vendor، digest متناظر در
`scripts/check-performance.py` نیز باید همراه نسخه و provenance به‌روزرسانی شود.

## پیش‌نمایش محلی

پیش‌نمایش دقیق رفتار Cloudflare Pages (شامل `_redirects`، `_headers` و URLهای بدون پسوند):

```bash
npx --yes wrangler@latest pages dev . --port 8788
# http://localhost:8788/
```

پیش‌نمایش سبک و بدون وابستگی نیز redirectها و URLهای بدون پسوند را شبیه‌سازی
می‌کند:

```bash
python3 scripts/devserver.py 8000
# http://localhost:8000/
```
