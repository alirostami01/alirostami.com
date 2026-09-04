# Persian Streams

افزونهٔ غیررسمی استرمیو (Stremio) برای پخش فیلم و سریال‌های ایرانی با زیرنویس فارسی.

اگر این افزونه برایتان مفید بوده، با حمایتتان کمک کنید پروژه زنده، سریع و به‌روز بماند. ❤️
[حمایت از پروژه](/support/)

`Stremio Addon` · `Node.js` · `Cloudflare Workers` · `Apache-2.0`

[مشاهده مخزن در گیت‌هاب](https://github.com/alirostami01/Persian-Streams)

## 📖 معرفی

**Persian Streams** یک افزونهٔ غیررسمی برای Stremio است که با دریافت شناسهٔ IMDb از استرمیو، صفحهٔ محتوای متناظر را در منبع ایرانیِ تنظیم‌شده پیدا می‌کند و لینک‌های مستقیم پخش و دانلود را به استرمیو برمی‌گرداند.

**جریان کار نسخهٔ فعلی:**

1. استرمیو شناسهٔ `tt...` را به افزونه می‌فرستد.
2. افزونه آن را به اندپوینت `quick-search` منبع می‌فرستد و نتیجه‌ای را انتخاب می‌کند که `imdb_id` آن دقیقاً با درخواست برابر باشد.
3. صفحهٔ محتوا با Cheerio خوانده و پارس می‌شود.
4. لینک‌های قابل پخش برای فیلم یا قسمت سریال استخراج می‌شوند و به‌همراه برچسب کیفیت، انکودر و وضعیت دوبله برگردانده می‌شوند.

> ⚠️ این پروژه هیچ فایل ویدیویی، زیرنویس یا محتوای رسانه‌ای را میزبانی نمی‌کند و تنها لینک‌هایی را که منبع پیکربندی‌شده در اختیار می‌گذارد پردازش می‌کند. مسئولیت رعایت قوانین کپی‌رایت و مقررات محلی بر عهدهٔ کاربر است.

## ✨ قابلیت‌ها

- 🎬 **پشتیبانی از فیلم و سریال** از طریق منبعی از نوع `stream`
- 🔎 **تطبیق مستقیم با IMDb** با استفاده از `/quick-search?q={imdbId}&sort=modified_at%3Adesc`
- 📺 **استخراج فصل و قسمت** از شناسه‌های استاندارد استرمیو مانند `tt1234567:1:3`
- 🏷️ **نمایش برچسب کیفیت واقعی منبع** (مثلاً `WEB-DL 4K 2160p 10bit HDR`) به‌جای ساده‌سازی آن به یک `1080p` عمومی
- 🧑‍💻 **تشخیص انکودر** از روی برچسب‌هایی مانند `انکودر : PSA` و نمایش آن در توضیح استریم
- 💬 **تشخیص وضعیت زیرنویس فارسی** (دارد / ندارد) با الگوهای فارسی و انگلیسی
- 🔊 **تشخیص نسخهٔ دوبله** با کلیدواژه‌های `Dubbed`، `Dooble`، `دوبله`، `Farsi Dub` و `Persian Dub`
- 🔢 **پشتیبانی از اعداد فارسی و عربی-هندی** در تشخیص فصل و قسمت
- 🗂️ **fallback دایرکتوری باز فصل**: اگر صفحه ساختار باکس دانلود نداشته باشد، لینک پوشهٔ فصل (`/S02/`) دنبال می‌شود و فایل قسمت از روی نام فایل (`S02E05`، `2x05`، `E05`) پیدا می‌شود
- 🎞️ **تشخیص heuristic کیفیت** از URL و متن پیرامون: `4K`، `1080p`، `720p`، `480p`، `360p` یا `Unknown`
- 🧩 **استخراج لینک از ساختارهای رایج صفحهٔ دانلود** شامل `handleDownloadClick(...)`، لینک مستقیم و `iframe`
- 🖼️ **لوگوی مطلق در manifest** که به‌صورت خودکار از میزبان درخواست ساخته می‌شود
- 📦 **دو runtime**: اجرای Node.js/Express (`server.js`) و Cloudflare Workers (`worker.js`) با هستهٔ مشترک `addon.js`
- ⚡ **بیلدر سبک** (`stremio-builder.js`) به‌جای SDK رسمی، برای جلوگیری از باندل‌شدن Express در Workers

## 🗂️ ساختار پروژه

ساختار واقعی و به‌روز پروژه (خروجی `ls -R`):

```text
.
├── .gitignore
├── .github/
│   └── workflows/
│       └── deploy-streams.yml   # دیپلوی خودکار Worker به Cloudflare
├── LICENSE                      # Apache License 2.0
├── README.md                    # راهنمای کاربر و راه‌اندازی
├── addon.js                     # هسته: manifest، استخراج stream، getStreams
├── stremio-builder.js           # بیلدر سبک Stremio (جایگزین SDK رسمی در Workers)
├── server.js                    # سرور Node.js / Express (main در package.json)
├── worker.js                    # آداپتور Cloudflare Workers (main در wrangler.jsonc)
├── wrangler.jsonc               # پیکربندی Worker: alias، assets، vars.BASE_URL
├── package.json                 # اسکریپت‌ها و وابستگی‌های Node.js
├── package-lock.json            # نسخه‌های قفل‌شده وابستگی‌ها
├── assets/
│   └── icons/
│       ├── logo.png             # لوگوی استفاده‌شده در manifest
│       └── player-fa.png        # فایل استاتیک اضافی
└── docs/
    └── DOCUMENTATION.md         # مستندات فنی کامل مطابق ساختار فعلی کد
```

| مسیر | نقش |
|---|---|
| `addon.js` | هستهٔ استخراج؛ تمام توابع `fetch*`، `extract*`، `detect*` به‌همراه manifest و `defineStreamHandler`. خروجی: `{ ...addonInterface, getStreams }` |
| `stremio-builder.js` | کلاس سبک `AddonBuilder` با `defineStreamHandler` و `getInterface()`؛ در `wrangler.jsonc` با alias جایگزین `stremio-addon-sdk` می‌شود |
| `server.js` | سرور Node؛ dotenv، Express، `getRouter(addonInterface)` از SDK رسمی، ساخت لوگوی مطلق با `x-forwarded-proto` و سرو `assets/icons` |
| `worker.js` | Worker؛ پارس مسیرهای `/streams/...`، تولید JSON با CORS، سرو asset از `env.ASSETS` و فراخوانی مستقیم `getStreams` |
| `wrangler.jsonc` | نام Worker، `alias`، `assets.directory`، `vars.BASE_URL` و `compatibility_date` |
| `.github/workflows/deploy-streams.yml` | دیپلوی خودکار Worker هنگام push به `main` |

> پروژه در حال حاضر فایل تست، پیکربندی lint، Dockerfile یا `.env.example` ندارد.

## 🚀 نصب و راه‌اندازی محلی

### پیش‌نیازها

- **Node.js نسخهٔ ۲۰٫۱۸٫۱ یا بالاتر** — دلیل: نسخهٔ قفل‌شدهٔ `cheerio` در `package-lock.json` مقدار `engines.node >= 20.18.1` را الزامی می‌کند.
- **npm**
- برای حالت Worker: **Wrangler** (`npx wrangler`)
- برنامهٔ **Stremio** برای تست نصب افزونه

### ۱. دریافت کد

```bash
git clone https://github.com/alirostami01/Persian-Streams.git
cd Persian-Streams
```

### ۲. نصب وابستگی‌ها

```bash
npm install
```

### ۳. ساخت فایل `.env` (برای Node)

در ریشهٔ پروژه یک فایل `.env` بسازید:

```ini
PORT=8000
BASE_URL=https://www.example.com
```

| متغیر | وضعیت | پیش‌فرض | محل مصرف | توضیح |
|---|---|---|---|---|
| `BASE_URL` | **اجباری** | — | `addon.js` | آدرس پایهٔ منبع ایرانی. اگر تنظیم نشود، برنامه با پیام خطا متوقف می‌شود |
| `PORT` | اختیاری | `8000` | `server.js` | پورت سرور HTTP |

> ℹ️ در نسخهٔ Node فقط همین دو متغیر خوانده می‌شوند. URL مطلق لوگو به‌صورت خودکار از `x-forwarded-proto` و `Host` درخواست ساخته می‌شود.

برای Cloudflare Workers مقدار `BASE_URL` در بخش `vars` فایل `wrangler.jsonc` قرار دارد و در داشبورد Cloudflare قابل override است:

```json
"vars": { "BASE_URL": "https://f2my.top" }
```

می‌توانید بدون فایل `.env` هم اجرا کنید:

```bash
BASE_URL=https://www.example.com PORT=8000 node server.js
```

### ۴. اجرای برنامه

**حالت Node.js** (پیشنهادی برای توسعهٔ محلی):

```bash
npm start        # اجرای معمولی: node server.js
npm run dev      # اجرای توسعه با watch mode: node --watch server.js
```

خروجی موفق:

```text
Persian Streams running on port 8000
Manifest: http://localhost:8000/manifest.json
```

اگر پورت اشغال باشد:

```text
Port 8000 is already in use.
```

راه‌حل:

```bash
PORT=8001 npm start
```

**حالت Cloudflare Workers (Edge):**

```bash
npx wrangler dev
# Manifest: http://localhost:8787/streams/manifest.json
```

### ۵. نصب در Stremio

نسخهٔ Node:

```text
stremio://localhost:8000/manifest.json
```

نسخهٔ Workers (لوکال):

```text
stremio://localhost:8787/streams/manifest.json
```

یا ابتدا manifest را در مرورگر بررسی کنید:

```text
http://localhost:8000/manifest.json
http://localhost:8787/streams/manifest.json
```

## ☁️ استقرار (Deployment)

### گزینهٔ A: میزبانی Node.js (VPS، Railway، Render، Fly.io، Heroku)

1. Node.js نسخهٔ ۲۰٫۱۸٫۱ یا بالاتر روی محیط اجرا فعال باشد.
2. وابستگی‌ها را با `npm install` نصب کنید.
3. دستور اجرا را روی `npm start` (یعنی `node server.js`) بگذارید؛ `main` در `package.json` همین است.
4. `BASE_URL` را در Environment Variables تنظیم کنید (بدون آن سرویس بالا نمی‌آید).
5. `PORT` معمولاً توسط خودِ میزبان تزریق می‌شود و کد آن را می‌خواند.

آدرس نصب پس از استقرار:

```text
stremio://YOUR_DOMAIN/manifest.json
```

مسیرهای ضروری: `/manifest.json`، `/stream/...`، `/assets/icons/logo.png`

### گزینهٔ B: Cloudflare Workers (پیشنهادی برای Edge، رایگان)

`wrangler.jsonc` مقدار `vars.BASE_URL` را دارد و می‌توان آن را در داشبورد override کرد.

```bash
npm install
npx wrangler deploy
```

یا به‌صورت خودکار از طریق GitHub Actions (push به `main` با تغییر در `worker.js`، `addon.js`، `stremio-builder.js`، `wrangler.jsonc` یا `assets/**`).

آدرس نصب پس از استقرار:

```text
stremio://<worker>.workers.dev/streams/manifest.json
```

مسیرهای ضروری Worker: `/streams/manifest.json`، `/streams/stream/...` و `/streams/assets/icons/logo.png`. همهٔ پاسخ‌های JSON هدر `access-control-allow-origin: *` دارند.

**نکات HTTPS و Proxy:**

- **Node:** سرور هدر `x-forwarded-proto` را می‌خواند تا پشت TLS proxy آدرس لوگو `https` شود. اگر پراکسی شما این هدر را ست نمی‌کند، `app.set('trust proxy', true)` را اضافه کنید یا مطمئن شوید مقدار `logo` در `/manifest.json` درست است.
- **Workers:** `url.origin` همیشه scheme درست را دارد و تنظیم اضافه‌ای لازم نیست.

## 🎯 نحوهٔ استفاده

پس از نصب افزونه در استرمیو:

1. یک فیلم یا سریال دارای شناسهٔ IMDb را باز کنید.
2. استرمیو درخواست `stream` را به افزونه می‌فرستد.
3. افزونه با شناسهٔ IMDb در منبع پیکربندی‌شده جست‌وجو می‌کند.
4. برای فیلم‌ها، لینک‌های دانلود و پخش صفحهٔ فیلم استخراج می‌شوند.
5. برای سریال‌ها، فصل و قسمت انتخاب‌شده پیدا می‌شود و لینک همان قسمت برگردانده می‌شود؛ اگر ساختار باکس دانلود پیدا نشود، دایرکتوری فصل به‌عنوان fallback بررسی می‌شود.
6. لینک‌ها با برچسب کیفیت و در صورت تشخیص، با `• دوبله` و `• encoder: ...` در فهرست استریم‌ها نمایش داده می‌شوند.

نمونهٔ خروجی در فهرست استریم‌ها:

```text
WEB-DL 1080p x265          →  S1E3 - WEB-DL 1080p x265 • encoder: PSA
720p • دوبله               →  720p
1080p NF WEB-DL x265 10bit →  S2E5 - 1080p NF WEB-DL x265 10bit
```

## 🔌 مسیرها و API

### Node.js (`server.js`)

| مسیر | توضیح |
|---|---|
| `GET /` | صفحهٔ سادهٔ معرفی افزونه و لینک نصب محلی |
| `GET /manifest.json` | manifest افزونه با URL مطلق لوگو |
| `GET /assets/icons/logo.png` | لوگوی افزونه |
| `GET /stream/movie/{imdbId}.json` | استریم‌های فیلم؛ مثال: `/stream/movie/tt1234567.json` |
| `GET /stream/series/{imdbId}:{season}:{episode}.json` | استریم یک قسمت سریال؛ مثال: `/stream/series/tt1234567:1:3.json` |

### Cloudflare Workers (`worker.js`)

| مسیر | توضیح |
|---|---|
| `GET /` | پاسخ وضعیت JSON: `{ name, status:'ok', manifest:'/streams/manifest.json' }` |
| `GET /streams` یا `/streams/` | ریدایرکت `302` به `/streams/manifest.json` |
| `GET /streams/manifest.json` | manifest با لوگوی مطلق `https://<origin>/streams/assets/icons/logo.png` |
| `GET /streams/assets/icons/logo.png` | لوگوی افزونه (از `env.ASSETS`) |
| `GET /streams/stream/movie/{imdbId}.json` | استریم فیلم در Worker |
| `GET /streams/stream/series/{imdbId}:{season}:{episode}.json` | استریم سریال در Worker |

> مسیر جداگانه‌ای به نام `/health` در کد وجود ندارد و `404` برمی‌گرداند؛ برای health check از `/manifest.json` یا `/streams/manifest.json` استفاده کنید.

بررسی سریع با curl:

```bash
# Node
curl http://localhost:8000/manifest.json
curl http://localhost:8000/stream/movie/tt1234567.json
curl http://localhost:8000/stream/series/tt1234567:1:3.json

# Workers
curl http://localhost:8787/streams/manifest.json
curl http://localhost:8787/streams/stream/movie/tt1234567.json
curl http://localhost:8787/streams/stream/series/tt1234567:1:3.json
```

## ⚙️ خلاصهٔ عملکرد فنی

### معماری ماژولار

```text
                    stremio-builder.js (بیلدر سبک)
                           │
         wrangler.jsonc ───┼─── addon.js (هسته: manifest + getStreams + extract*)
         alias SDK → builder   │         │
                               │         ├── server.js (Express + getRouter)
                               │         └── worker.js (Cloudflare adapter)
                               │
Stremio → /stream/... یا /streams/stream/... → getStreams()
```

### جریان هسته (`addon.js`)

```text
Stremio request
   ↓
builder.defineStreamHandler(args)  ← از stremio-builder.js در Worker، یا SDK رسمی در Node via getRouter
   ↓
getStreams(type, imdbId, season, episode)
   ├─ fetchTitleFromMeta(...)        ← Cinemeta (نتیجه فعلاً استفاده نمی‌شود)
   ├─ resolveViaQuickSearch(imdbId)  ← GET {BASE_URL}/quick-search?q={imdbId}
   ├─ fetchPage(contentUrl)          ← HTML + cheerio.load
   └─ extractMovieStreams($)
      یا extractSeriesStreams($, S, E)
             └─ fallback: extractLegacySeriesStreams → extractStreamsFromSeasonDirectory
   ↓
{ streams: [...] }
```

**جزئیات مهم:**

- تنها راه تطبیق محتوا در نسخهٔ فعلی، `quick-search` مبتنی بر IMDb است؛ fallback مبتنی بر عنوان یا slug وجود ندارد.
- افزونه catalog، meta یا subtitle ارائه نمی‌کند و فقط منبعی از نوع `stream` دارد.
- منبع باید خروجی `quick-search` را به‌صورت آرایهٔ JSON با فیلدهای `imdb_id` و `url` برگرداند.
- لینک‌های فیلم از `.download-list`، `.download-box` و `.dl-box` خوانده می‌شوند.
- لینک‌های سریال از `.download-season` و `.series-downloaditems .d-flex` خوانده می‌شوند.
- کیفیت ابتدا از برچسب متنی صفحه (`کیفیت : ...`) و در نبود آن با heuristic از URL و متن تشخیص داده می‌شود.
- در صورت خطا یا پیدا نشدن محتوا، پاسخ افزونه `{ "streams": [] }` است.
- `addon.js` دیگر سرور ندارد؛ `server.js` نقطهٔ ورود Node و `worker.js` نقطهٔ ورود Edge است.
- `wrangler.jsonc` با `alias: { "stremio-addon-sdk": "./stremio-builder.js" }` از باندل‌شدن Express در Workers جلوگیری می‌کند.

برای توضیح دقیق تک‌تک توابع، selectorها و مسائل شناخته‌شده، فایل `docs/DOCUMENTATION.md` را ببینید.

## 🐛 عیب‌یابی

### پیام `BASE_URL is not set` می‌بینم

- **Node:** فایل `.env` وجود ندارد یا `BASE_URL` در آن تعریف نشده است. مقدار را اضافه کنید و دوباره اجرا کنید. توجه کنید این بررسی حتی هنگام `import` کردن `addon.js` هم اجرا می‌شود.
- **Workers:** مقدار `vars.BASE_URL` در `wrangler.jsonc` یا داشبورد Cloudflare را بررسی کنید.

### پیام `Port 8000 is already in use`

پورت دیگری انتخاب کنید:

```bash
PORT=8001 npm start
```

### هیچ استریمی نمایش داده نمی‌شود

- ممکن است محتوا در منبع پیکربندی‌شده وجود نداشته باشد.
- ممکن است خروجی `/quick-search` هیچ `imdb_id` مطابقی نداشته باشد.
- ممکن است ساختار HTML صفحهٔ منبع تغییر کرده باشد.
- لاگ‌های سرور را بررسی کنید؛ مراحل Quick-search، Resolved، Fetch و تعداد استریم‌ها چاپ می‌شوند.

### در لاگ خطای `TypeError: $ is not a function` می‌بینم

یعنی `quick-search` محتوایی پیدا نکرده و صفحه‌ای برای parse وجود نداشته است. پاسخ HTTP همچنان `{"streams":[]}` است و کاربر خطایی نمی‌بیند؛ این مورد در بخش «مسائل شناخته‌شده» مستندات فنی توضیح داده شده است.

### برچسب زیرنویس فارسی نمایش داده نمی‌شود

وضعیت زیرنویس تشخیص داده می‌شود، اما تابع `formatSubtitleLabel` در نسخهٔ فعلی عمداً رشتهٔ خالی برمی‌گرداند و برچسبی به خروجی اضافه نمی‌کند.

### لوگو در استرمیو نمایش داده نمی‌شود

- **Node:** مطمئن شوید `/assets/icons/logo.png` از بیرون قابل دسترسی است. در استقرار پشت HTTPS، مقدار `logo` در `/manifest.json` را بررسی کنید؛ اگر `http://` بود، باید `x-forwarded-proto` درست تنظیم شود.
- **Workers:** آدرس `https://<worker>/streams/assets/icons/logo.png` را بررسی کنید.

### لینک نصب روی صفحهٔ اصلی هنوز localhost است

صفحهٔ `/` فقط یک صفحهٔ کمکی است و لینک نصب آن در کد به `localhost` اشاره می‌کند. برای نسخهٔ مستقرشده مستقیماً از آدرس عمومی خودتان استفاده کنید:

```bash
# Node
stremio://YOUR_DOMAIN/manifest.json

# Workers
stremio://YOUR_DOMAIN/streams/manifest.json
```

### Worker دیپلوی نمی‌شود

- آیا `CLOUDFLARE_API_TOKEN` و `CLOUDFLARE_ACCOUNT_ID` در secrets گیت‌هاب تنظیم شده‌اند؟
- نسخهٔ Wrangler در workflow روی `4.128.0` پین شده است؛ لاگ Action را بررسی کنید.

## 🤝 مشارکت

Pull Requestها و Issueها برای بهبود استخراج لینک، سازگاری با ساختارهای HTML جدید، افزودن تست و بهبود مستندات با آغوش باز پذیرفته می‌شوند.

پیش از تغییر منطق استخراج، بخش‌های «نقشهٔ ماژول‌ها» و «مسائل شناخته‌شده و بدهی فنی» در `docs/DOCUMENTATION.md` را مطالعه کنید؛ چند مورد کوچک و آماده برای شروع مشارکت آن‌جا فهرست شده‌اند.

## 📄 مجوز

فایل `LICENSE` این مخزن **Apache License 2.0** است.

---

ساخته شده با ❤️ برای جامعهٔ فارسی‌زبان Stremio — [حمایت از ادامهٔ مسیر](/support/)
