# Persian Streams

افزونهٔ غیررسمی استرمیو (Stremio) برای پخش فیلم و سریال‌های ایرانی با زیرنویس فارسی.

اگر این افزونه برایتان مفید بوده، با حمایتتان کمک کنید پروژه زنده، سریع و به‌روز بماند. ❤️  
[حمایت از پروژه](/support/)

`Stremio Addon` · `Node.js` · `Cloudflare Workers` · `Apache-2.0`

[مشاهده مخزن در گیت‌هاب](https://github.com/alirostami01/Persian-Streams)

## ⚡ نصب سریع

سریع‌ترین راه استفاده، نصب **نسخهٔ عمومی آماده** افزونه است. این نسخه روی Cloudflare Workers اجرا می‌شود و برای نصب آن نیازی به Node.js، npm، تنظیمات محلی یا راه‌اندازی سرور ندارید.

### 🔗 آدرس نصب

```text
https://stremio.alirostami.com/streams/manifest.json
```

### 🚀 نصب در Stremio

**روش پیشنهادی — نصب مستقیم با لینک `stremio://`:**

[افزودن به Stremio](stremio://stremio.alirostami.com/streams/manifest.json)

لینک بالا را در دستگاهی که Stremio روی آن نصب است باز کنید تا Stremio برای نصب افزونه باز شود.

**نصب دستی در Stremio:**

1. Stremio را باز کنید.
2. وارد بخش **Addons** شوید.
3. آدرس زیر را در قسمت نصب افزونه با URL وارد کنید:

```text
https://stremio.alirostami.com/streams/manifest.json
```

4. افزونهٔ **Persian Streams** را پیدا و روی **Install** کلیک کنید.

**Stremio Web:**

می‌توانید از لینک نصب زیر در نسخهٔ وب Stremio نیز استفاده کنید:

```text
https://web.strem.io/addons?addon=https://stremio.alirostami.com/streams/manifest.json
```

### 🧪 تست نصب

پس از نصب، یک فیلم یا سریال دارای شناسهٔ IMDb (`tt...`) را باز کنید. لینک‌های پخش فارسی باید در بخش **Streams** نمایش داده شوند.

| مورد | مقدار |
|---|---|
| آدرس manifest | `https://stremio.alirostami.com/streams/manifest.json` |
| Resource | `stream` |
| Types | `movie`, `series` |
| شناسه‌های پشتیبانی‌شده | `tt...` |
| Runtime | Cloudflare Workers |

> ℹ️ در نسخهٔ عمومی نیازی به نصب محلی، `npm install` یا تنظیم `BASE_URL` ندارید. فقط افزونه را با آدرس بالا در Stremio نصب کنید.

> ⚠️ این پروژه هیچ فایل ویدیویی، زیرنویس یا محتوای رسانه‌ای را میزبانی نمی‌کند و فقط لینک‌هایی را که منبع پیکربندی‌شده در اختیار می‌گذارد پردازش می‌کند. مسئولیت رعایت قوانین کپی‌رایت و مقررات محلی بر عهدهٔ کاربر است.

## 📖 معرفی

**Persian Streams** یک افزونهٔ غیررسمی برای Stremio است که با دریافت شناسهٔ IMDb از استرمیو، محتوای متناظر را در منبع ایرانیِ تنظیم‌شده پیدا می‌کند و لینک‌های پخش و دانلود را به Stremio برمی‌گرداند.

جریان کلی کار:

1. Stremio شناسهٔ IMDb فیلم یا قسمت سریال را ارسال می‌کند.
2. افزونه در endpoint `quick-search` منبع جست‌وجو می‌کند.
3. فقط نتیجه‌ای انتخاب می‌شود که `imdb_id` آن دقیقاً با شناسهٔ درخواست‌شده برابر باشد.
4. صفحهٔ محتوا با Cheerio پردازش می‌شود.
5. لینک‌های قابل پخش استخراج و با کیفیت، انکودر و وضعیت دوبله به Stremio برگردانده می‌شوند.

## ✨ قابلیت‌ها

- 🎬 پشتیبانی از فیلم و سریال
- 🔎 تطبیق دقیق محتوا با IMDb
- 📺 استخراج فصل و قسمت از شناسه‌های Stremio مانند `tt1234567:1:3`
- 🏷️ نمایش کیفیت واقعی مانند `WEB-DL 4K 2160p 10bit HDR`
- 🧑‍💻 تشخیص encoder از اطلاعات منبع
- 💬 تشخیص وجود زیرنویس فارسی
- 🔊 تشخیص نسخه‌های دوبله
- 🔢 پشتیبانی از اعداد فارسی و عربی-هندی برای فصل و قسمت
- 🗂️ fallback به دایرکتوری فصل برای سریال‌ها
- 🎞️ تشخیص کیفیت از URL و متن پیرامون لینک
- 🧩 استخراج لینک مستقیم و iframe و ساختارهای رایج دانلود
- 📦 پشتیبانی از Node.js/Express و Cloudflare Workers
- ⚡ استفاده از بیلدر سبک Stremio برای runtime مربوط به Worker

## 🔌 مسیرهای نسخهٔ عمومی

| مسیر | کاربرد |
|---|---|
| `/streams/manifest.json` | مانیفست افزونه |
| `/streams/stream/movie/{imdbId}.json` | استریم فیلم |
| `/streams/stream/series/{imdbId}:{season}:{episode}.json` | استریم قسمت سریال |
| `/streams/assets/icons/logo.png` | لوگوی افزونه |

## 🛠️ توسعه و اجرای نسخهٔ شخصی

اگر می‌خواهید نسخهٔ اختصاصی خودتان را اجرا کنید:

```bash
git clone https://github.com/alirostami01/Persian-Streams.git
cd Persian-Streams
npm install
```

برای اجرای Node، `BASE_URL` را تنظیم کنید:

```bash
BASE_URL=https://www.example.com PORT=8000 npm start
```

برای اجرای محلی Worker:

```bash
npx wrangler dev
```

در حالت Worker مسیر manifest محلی به شکل زیر است:

```text
http://localhost:8787/streams/manifest.json
```

جزئیات کامل متغیرهای محیطی، استقرار Node و Cloudflare Workers در README مخزن مستند شده است.

## 🐛 عیب‌یابی سریع

- اگر هیچ استریمی نمایش داده نمی‌شود، ممکن است محتوا در منبع پیکربندی‌شده وجود نداشته باشد.
- اگر `quick-search` نتیجهٔ منطبق با IMDb ندهد، خروجی استریم خالی خواهد بود.
- تغییر ساختار HTML منبع می‌تواند باعث شود استخراج لینک‌ها انجام نشود.
- در نسخهٔ اختصاصی Node، مقدار `BASE_URL` و پورت را بررسی کنید.
- در نسخهٔ Worker، مسیر `/streams/manifest.json` را بررسی کنید.

## 🤝 مشارکت

Pull Requestها و Issueها برای بهبود استخراج لینک، سازگاری با ساختارهای HTML جدید، افزودن تست و بهبود مستندات پذیرفته می‌شوند.

## 📄 مجوز

فایل `LICENSE` این مخزن **Apache License 2.0** است.

---

ساخته شده با ❤️ برای جامعهٔ فارسی‌زبان Stremio — [حمایت از ادامهٔ مسیر](/support/)