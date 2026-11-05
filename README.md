# alirostami.com

استاتیک سایت شخصی (خروجی Hugo + پوسته LoveIt) که مستقیماً از همین مخزن سرو می‌شود.

## دامنه و URLهای canonical

دامنه و صفحهٔ اصلی ترجیحی سایت:

```text
https://www.alirostami.com/
```

سایت یک خروجی واحد با صفحهٔ اصلی فارسی (`fa-IR`) دارد و هیچ tree استاتیکی برای
`/fa/`، `/en/`، `/categories/` یا `/tags/` منتشر نمی‌شود. مسیرهای زبانی قدیمی
به نزدیک‌ترین صفحهٔ اصلی و مسیرهای taxonomy/term به `/posts/` یک‌مرحله‌ای 301
می‌شوند. URLهای canonical با حروف کوچک و، برای صفحات پوشه‌ای، با اسلش انتهایی
نوشته می‌شوند.
صفحات فصل‌ها مطابق رفتار Cloudflare Pages بدون پسوند `.html` canonical هستند؛
نسخهٔ دارای پسوند با 301 به همان URL بدون پسوند می‌رود. هر ۲۹ فصل AIMA فایل و
URL انگلیسی lowercase و ASCII دارد (برای نمونه `aima-4e/01-introduction.html`
با canonical برابر `/aima-4e/01-introduction`). جدول ثابت migration در
`scripts/aima_routes.py` منبع حقیقت generator و redirectها است. URLهای فارسی
قبلی و شکل‌های قدیمی دارای `%20`، با و بدون `.html`، مستقیماً با 301 به URL
انگلیسی نهایی می‌روند و فایل محتوای تکراری ندارند. این قرارداد با دستور زیر
مستقل بررسی می‌شود:

```bash
python3 scripts/check-aima-routes.py
```

همین قرارداد برای ۲۷ فصل و پیوست کتاب معماری نرم‌افزار نیز برقرار است؛ برای
نمونه فایل `software-architecture/01-introduction.html` canonical برابر
`/software-architecture/01-introduction` دارد و پیوست در مسیر
`/software-architecture/appendix-discussion-questions` منتشر می‌شود. جدول ثابت
migration در `scripts/software_architecture_routes.py` نگهداری می‌شود و
`chapter-NN`ها و `appendix` قدیمی، با و بدون `.html`، مستقیماً به مقصد نهایی
می‌روند. بررسی مستقل این قرارداد:

```bash
python3 scripts/check-software-architecture-routes.py
```

تمام aliasها باید در Cloudflare با پاسخ **301** به URL نهایی برسند و هیچ فایل
HTML ثابتی برای آن‌ها در مخزن وجود نداشته باشد. پوشه‌های uppercase، مسیرهای
pagination قدیمی و شکل‌های موازی `page.html` فقط در manifestهای لبه ثبت می‌شوند:

```bash
python3 scripts/redirects.py
```

فهرست aliasها در `scripts/redirects.py` منبع واحد redirectهای URL است. این
اسکریپت هر فایل alias باقی‌مانده را حذف می‌کند و `_redirects` و
`cloudflare-bulk-redirects.csv` را بازتولید می‌کند. Cloudflare Pages manifest
اول را هنگام deploy می‌خواند و برای تمام aliasهای ثبت‌شده پاسخ 301 می‌دهد.

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
روش ترجیحی برای redirect تک‌مرحله‌ای است. Query String باید حفظ شود. بخش‌های
قدیمی زبان و taxonomy و مسیرهای Feed/Sitemap نیز مستقیماً redirect می‌شوند:

```text
/en/                         → /
/en/support/                 → /support/
/fa/                         → /
/fa/support/                 → /support/
/categories/                 → /posts/
/tags/                       → /posts/
/categories/index.xml        → /index.xml
/tags/index.xml              → /index.xml
/fa/sitemap.xml              → /sitemap.xml
/en/sitemap.xml              → /sitemap.xml
/public/sitemap.xml          → /sitemap.xml
/public/fa/sitemap.xml       → /sitemap.xml
/fa/index.xml                → /index.xml
/fa/categories/index.xml     → /index.xml
/fa/tags/index.xml           → /index.xml
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
| `/support/` | تنها canonical | `support/index.html` |
| `/support.html` | alias → `/support/` | فقط `_redirects`؛ بدون فایل HTML |
| `/fa/support/` | alias → `/support/` | فقط `_redirects`؛ بدون فایل HTML |
| `/fa/support.html` | alias → `/support/` | فقط `_redirects`؛ بدون فایل HTML |
| `/en/support/` | alias → `/support/` | فقط `_redirects`؛ بدون فایل HTML |
| `/en/support.html` | alias → `/support/` | فقط `_redirects`؛ بدون فایل HTML |

### بازتولید صفحه

```bash
python3 scripts/build-support-page.py
```

محتوای صفحه (متن‌ها، کیف‌پول‌ها، پروژه‌ها و CSS) داخل همان اسکریپت است.
اسکریپت فقط canonical اصلی و manifestهای redirect لبه را می‌سازد.

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
تولید می‌شوند. همان build نسخه‌های responsive تصویر پروفایل را نیز می‌سازد و
سپس metadata تصویری و ویژگی‌های تصاویر HTML را به‌صورت idempotent به‌روز
می‌کند. جلد canonical کتاب AIMA به‌صورت WebP با ابعاد `960×1286` و بدون نسخهٔ
full-size تکراری در `figures/aima-4e-persian.webp` نگهداری می‌شود:

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

هر ۵۸۴ تصویر فصل و جلد اکنون فقط با فرمت WebP منتشر می‌شود: نمودارهای PNG
معماری نرم‌افزار به‌صورت lossless و تصاویر JPEG فصل‌های AIMA با کیفیت بالا و
metadata حذف‌شده تبدیل شده‌اند. فایل‌های `remove*`، تصویرهای orphan، نسخه‌های
PNG/JPEG موازی و منبع full-size جلد در tree قابل‌انتشار نگهداری نمی‌شوند.
`_headers` نیز برای هر دو شاخهٔ تصاویر فصل cache سی‌روزه تعریف می‌کند. ممیزی
مستقل بازگشت هر فایل موقت، فرمت قدیمی، تصویر orphan یا asset بزرگ‌تر از ۶۰۰ KB
را خطا می‌داند.

ممیزی مستقل و بدون dependency ثالث:

```bash
python3 scripts/check-images.py
```

## Metadata و Structured Data

post-processor متادیتا برای هر ۷۰ صفحهٔ indexable توضیح یکتا، Open Graph،
Twitter Card، `og:locale` و URL canonical هماهنگ می‌سازد. چون سایت یک ساختار
canonical واحد دارد، هیچ `hreflang` یا `og:locale:alternate` زبانی تولید نمی‌شود.

JSON-LD هر صفحه در یک graph معتبر تجمیع می‌شود. ۵۷ صفحهٔ فصل با موجودیت‌های
جداگانهٔ `Chapter` و `WebPage` به `Book` والد متصل‌اند و نام، توضیح، زبان،
نویسندگان، مترجم، شمارهٔ فصل، تصویر و breadcrumb دارند. صفحات کتاب، مقاله،
نرم‌افزار، آرشیو و پروفایل نیز schema تخصصی خود را حفظ می‌کنند؛ نویسنده و
publisher مقاله‌ها به موجودیت نام‌دار `Person` متصل است.

اجرای دستی و ممیزی مستقلِ stdlib-only:

```bash
python3 scripts/update-metadata.py   # idempotent؛ اجرای دوم نباید فایلی را تغییر دهد
python3 scripts/check-metadata.py
```

checker کامل بودن و یکتایی descriptionها، هم‌خوانی canonical/OG/Twitter، locale،
نبود alternate زبانی، اعتبار JSON-LD، رابطهٔ Chapter→Book/WebPage، نویسنده و
publisher مقاله و breadcrumb ۶۹ صفحهٔ غیرخانه را بررسی می‌کند.

## لینک‌سازی داخلی و Crawl Architecture

post-processor لینک‌سازی برای هر ۷۰ صفحهٔ indexable مسیرهای crawlable و
قابل‌مشاهده می‌سازد. breadcrumb قابل‌مشاهدهٔ ۶۹ صفحه مستقیماً از
`BreadcrumbList` همان صفحه تولید می‌شود؛ بنابراین نام و hierarchy رابط کاربری
با JSON-LD همواره هم‌راستاست. هر ۵۷ فصل کتاب نیز لینک‌های استاتیک و توصیفی به
فهرست کتاب و فصل قبلی/بعدی دارد؛ ناوبری بومی ۲۹ فصل AIMA تکمیل و برای ۲۸ فصل
معماری نرم‌افزار مسیر مستقل ساخته می‌شود. ۱۱ صفحهٔ hub، پروژه، مقاله و آرشیو با
بخش‌های مرتبط به هم متصل‌اند؛ صفحهٔ خانه نیز به همهٔ مسیرهای اصلی `/posts/`،
کتابخوان‌ها، پروژه‌های ترجمه، افزونه‌های Stremio و `/support/` لینک مستقیم دارد.
CTAهای کوتاه و permalinkهای `#` نیز نام مقصد توصیفی دارند تا متن لینک برای
crawler و فناوری کمکی مبهم نباشد.

اجرای دستی، بررسی stale output و ممیزی مستقلِ stdlib-only:

```bash
python3 scripts/update-internal-links.py
python3 scripts/update-internal-links.py --check
python3 scripts/check-internal-links.py
```

checker تمام anchorهای داخلی و fragmentها را resolve می‌کند و لینک شکسته، لینک
به redirect/`noindex`، مسیر غیرcanonical، anchor خالی یا عمومی و orphan page را
رد می‌کند. graph نهایی باید از خانه کاملاً قابل‌دسترسی و حداکثر click depth آن
۲ باشد. checker همچنین تطابق breadcrumb قابل‌مشاهده با JSON-LD، توالی فصل‌ها،
اتصال generatorها به pipeline و idempotence updater را بررسی می‌کند.

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

تمام generatorهای مستندشده post-processorهای تصاویر، Metadata، لینک‌سازی داخلی،
Performance و سپس Accessibility را از طریق `apply_site_postprocessors()` اجرا می‌کنند.
بنابراین پس از بازتولید هر صفحه، اجرای جداگانه لازم نیست؛ بااین‌حال audit نهایی
همهٔ فازها باید اجرا شود:

```bash
python3 scripts/check-images.py
python3 scripts/check-seo-urls.py
python3 scripts/check-aima-routes.py
python3 scripts/check-software-architecture-routes.py
python3 scripts/check-metadata.py
python3 scripts/check-internal-links.py
python3 scripts/check-performance.py
python3 scripts/check-accessibility.py
```

فایل `_headers` سیاست Cloudflare Pages را تعریف می‌کند: CSP و headerهای
سخت‌سازی مرورگر روی همهٔ پاسخ‌های استاتیک اعمال می‌شوند، `comments.app` تنها
runtime خارجی مجاز است و assetهای vendor تا ۳۰ روز و CSS/JS دست‌اول تا ۷ روز
cache می‌شوند. چون نام فایل‌ها content hash ندارد، از `immutable` استفاده نشده
است. بعد از تغییر عمدی یک فایل vendor، digest متناظر در
`scripts/check-performance.py` نیز باید همراه نسخه و provenance به‌روزرسانی شود.

## Accessibility و ناوبری صفحه‌کلید

post-processor دسترس‌پذیری، خروجی canonical و صفحهٔ 404 را با ساختار ثابت و
هم‌راستا با الزامات قابل‌بررسی WCAG 2.2 AA به‌روزرسانی می‌کند. هر صفحه یک
skip link به `main#main-content`، یک عنوان اصلی، ترتیب heading بدون پرش، focus
قابل‌دیدن، کنتراست اصلاح‌شدهٔ متن/لینک‌های پوسته و حالت
`prefers-reduced-motion` دارد. aliasهای redirect فقط در لبه تعریف شده‌اند و
بنابراین هیچ سند HTML تکراری وارد این markup یا ممیزی نمی‌شود.

کنترل‌های search، theme، بازگشت و منوی موبایل به `button` بومی تبدیل شده‌اند و
toggle منوی موبایل با `aria-expanded` و `aria-controls` همگام است. فهرست‌های
بازشوندهٔ مقالات از `details`/`summary`
بومی استفاده می‌کنند، landmarkهای navigation نام یکتا و سرستون‌های جدول
`scope="col"` دارند. لینک‌های آیکونی نام صریح دارند و لینک‌های
`target="_blank"` با `noopener noreferrer` ایمن می‌شوند. کتابخوان‌های AIMA و
معماری نرم‌افزار نیز برای باز و بسته کردن
فصل‌ها از button بومی استفاده می‌کنند، وضعیت accordion را همگام می‌سازند، با
Escape بسته می‌شوند و shortcut فصل‌ها روی کنترل‌های focused اجرا نمی‌شود.

اجرای دستی، بررسی idempotence و ممیزی مستقلِ stdlib-only:

```bash
python3 scripts/update-accessibility.py
python3 scripts/update-accessibility.py --check
python3 scripts/check-accessibility.py
```

checker هر ۷۱ فایل HTML را می‌خواند و landmark، skip link، heading hierarchy،
accessible name، مرجع‌های ARIA، ترتیب focus، کنترل‌های کتابخوان، امنیت تب جدید،
اتصال generatorها و idempotence را بررسی می‌کند. این ممیزی استاتیک جای آزمون
دستی با صفحه‌کلید و screen reader روی مرورگرهای هدف را نمی‌گیرد.

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
