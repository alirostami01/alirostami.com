# Persian Subtitles

افزونهٔ غیررسمی استرمیو (Stremio) برای زیرنویس فارسی فیلم و سریال، متصل به API سرویس SubSource.

اگر این افزونه برایتان مفید بوده، با حمایتتان کمک کنید پروژه زنده، سریع و به‌روز بماند. ❤️  
[حمایت از پروژه](/support/)

`Stremio Addon` · `Node.js` · `Cloudflare Workers` · `Apache-2.0`

[مشاهده مخزن در گیت‌هاب](https://github.com/alirostami01/Persian-Subtitles)

## ⚡ نصب سریع

سریع‌ترین راه استفاده، نصب **نسخهٔ عمومی آماده** افزونه است. این نسخه روی Cloudflare Workers اجرا می‌شود و برای نصب آن نیازی به Node.js، npm، کلید API یا راه‌اندازی سرور ندارید.

### 🔗 آدرس نصب

```text
https://stremio.alirostami.com/subtitles/manifest.json
```

### 🚀 نصب در Stremio

**روش پیشنهادی — با لینک `stremio://`:**

```text
stremio://stremio.alirostami.com/subtitles/manifest.json
```

این لینک را در محیطی که Stremio روی آن نصب است باز کنید تا افزونه مستقیماً برای نصب به Stremio منتقل شود.

**نصب دستی:**

1. Stremio را باز کنید.
2. وارد بخش **Addons** شوید.
3. آدرس زیر را در قسمت نصب افزونه با URL وارد کنید:

```text
https://stremio.alirostami.com/subtitles/manifest.json
```

4. افزونهٔ **Persian Subtitles** را نصب کنید.

> ℹ️ اگر آدرس `manifest.json` را در مرورگر باز کنید، فقط JSON مانیفست نمایش داده می‌شود؛ برای نصب، آدرس را داخل Stremio وارد کنید یا از لینک `stremio://` استفاده کنید.

### 🧪 تست نصب

پس از نصب، یک فیلم یا سریال دارای شناسهٔ IMDb (`tt...`) را باز کنید. در بخش **Subtitles** باید زیرنویس‌های فارسی نمایش داده شوند.

| مورد | مقدار |
|---|---|
| آدرس manifest | `https://stremio.alirostami.com/subtitles/manifest.json` |
| شناسه افزونه | `org.alirostami.subtitles.persian` |
| Runtime | Cloudflare Workers |
| Resource | `subtitles` |
| Types | `movie`, `series` |
| شناسه‌های پشتیبانی‌شده | `tt...` |
| Health check | `https://stremio.alirostami.com/subtitles/health` |

> ⚠️ نمونهٔ عمومی بدون نیاز به کلید API برای کاربر قابل استفاده است. اگر می‌خواهید نسخهٔ اختصاصی خود را با کلید API و دامنهٔ خودتان اجرا کنید، بخش «نصب و راه‌اندازی محلی» و «استقرار» در README مخزن را مطالعه کنید.

## 📖 معرفی

**Persian Subtitles** یک افزونهٔ غیررسمی برای Stremio است که با دریافت شناسهٔ IMDb از استرمیو، فیلم یا سریال متناظر را در SubSource پیدا می‌کند و زیرنویس‌های فارسی آن را به‌صورت SRT در اختیار Stremio قرار می‌دهد.

جریان کلی کار:

1. Stremio شناسهٔ IMDb فیلم یا سریال را ارسال می‌کند.
2. برای سریال‌ها، نام و فصل از Cinemeta دریافت و در SubSource جست‌وجو می‌شود.
3. در صورت نیاز، جست‌وجوی IMDb به‌عنوان fallback انجام می‌شود.
4. زیرنویس‌های فارسی دریافت و برای فصل و قسمت موردنظر فیلتر می‌شوند.
5. فایل ZIP زیرنویس دانلود، SRT استخراج و encoding آن برای نمایش صحیح فارسی اصلاح می‌شود.

> ⚠️ این پروژه میزبان هیچ فایل زیرنویس یا رسانه‌ای نیست و از API سرویس SubSource استفاده می‌کند. مسئولیت رعایت قوانین کپی‌رایت و مقررات محلی بر عهدهٔ کاربر است.

## ✨ قابلیت‌ها

- 💬 دریافت زیرنویس فارسی از SubSource
- 🎯 تطبیق فصل و قسمت با الگوهای رایج مانند `S01E05`، `S1E5` و `1x05`
- 📦 استخراج خودکار SRT از ZIP
- 🔤 تشخیص encoding فارسی و تبدیل Windows-1256 به UTF-8 در صورت نیاز
- 🏷️ نمایش نام ریلیز و کیفیت زیرنویس در Stremio
- 🟡 امکان افزودن متن حمایت (Promo) به زیرنویس
- 🔁 retry برای خطاهای موقت شبکه، `429` و `5xx`
- 🌐 پشتیبانی از Node.js/Express و Cloudflare Workers
- 🚀 دیپلوی خودکار نسخهٔ Worker با GitHub Actions

## 🔌 مسیرهای نسخهٔ عمومی

| مسیر | کاربرد |
|---|---|
| `/subtitles/manifest.json` | مانیفست افزونه |
| `/subtitles/health` | بررسی سلامت سرویس |
| `/subtitles/movie/{imdbId}.json` | زیرنویس فیلم |
| `/subtitles/series/{imdbId}:{season}:{episode}.json` | زیرنویس قسمت سریال |
| `/subtitles/download/{subtitleId}` | دریافت SRT |

## 🛠️ توسعه و اجرای نسخهٔ شخصی

برای اجرای نسخهٔ اختصاصی، کد پروژه را دریافت و وابستگی‌ها را نصب کنید:

```bash
git clone https://github.com/alirostami01/Persian-Subtitles.git
cd Persian-Subtitles
npm ci
```

برای اجرای Node، فایل `.env` را از `.env.example` بسازید و حداقل `API_KEY` را تنظیم کنید:

```bash
cp .env.example .env
npm run dev
```

برای Cloudflare Workers نیز `API_KEY` باید به‌صورت Secret تنظیم و Worker با Wrangler deploy شود. جزئیات کامل در README مخزن موجود است.

## 🐛 عیب‌یابی سریع

- اگر فهرست زیرنویس خالی است، ممکن است فیلم در SubSource پیدا نشده باشد یا زیرنویس فارسی برای آن موجود نباشد.
- اگر فایل زیرنویس دانلود نمی‌شود، اتصال سرویس عمومی و مسیر `/subtitles/download/...` را بررسی کنید.
- اگر متن فارسی خراب نمایش داده می‌شود، encoding فایل منبع ممکن است غیرمعمول باشد.
- برای نسخهٔ اختصاصی، وجود `API_KEY` و تنظیم صحیح دامنه و پورت را بررسی کنید.

## 🤝 مشارکت

Pull Requestها و Issueها برای بهبود جست‌وجو، تطبیق فصل و قسمت، سازگاری با API و بهبود مستندات پذیرفته می‌شوند.

## 📄 مجوز

فایل `LICENSE` این مخزن **Apache License 2.0** است.

---

ساخته شده با ❤️ برای جامعهٔ فارسی‌زبان Stremio — [حمایت از ادامهٔ مسیر](/support/)