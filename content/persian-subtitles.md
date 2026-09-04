# Persian Subtitles

افزونهٔ غیررسمی استرمیو (Stremio) برای زیرنویس فارسی فیلم و سریال، متصل به API سرویس SubSource.

اگر این افزونه برایتان مفید بوده، با حمایتتان کمک کنید پروژه زنده، سریع و به‌روز بماند. ❤️
[حمایت از پروژه](/support/)

`Stremio Addon` · `Node.js` · `Cloudflare Workers` · `Apache-2.0`

[مشاهده مخزن در گیت‌هاب](https://github.com/alirostami01/Persian-Subtitles)

## 📖 معرفی

**Persian Subtitles** یک افزونهٔ غیررسمی برای Stremio است که با دریافت شناسهٔ IMDb از استرمیو، فیلم یا سریال متناظر را در SubSource پیدا می‌کند و زیرنویس‌های فارسی همان محتوا را به‌صورت فایل SRT آماده در اختیار Stremio می‌گذارد.

**جریان کار نسخهٔ فعلی:**

1. استرمیو شناسهٔ `tt...` (فیلم) یا `tt1234567:1:3` (سریال) را به منبعی از نوع `subtitles` می‌فرستد.
2. برای سریال‌ها، نام سریال از Cinemeta گرفته می‌شود و با `q={name}&season={n}` در SubSource جست‌وجو می‌شود؛ اگر نتیجه‌ای نبود، جست‌وجوی مستقیم با IMDb به‌عنوان fallback انجام می‌شود.
3. با `movieId` به‌دست‌آمده، زیرنویس‌های `language=farsi_persian` با `sort=rating&limit=100` دریافت می‌شوند.
4. برای سریال‌ها، نتایج بر اساس الگوهای فصل و قسمت (`S01E05`، `S1E5`، `1x05` یا Season Pack کامل) فیلتر می‌شوند.
5. لینک هر زیرنویس به پراکسی داخلی افزونه (`/download/{subtitleId}`) اشاره می‌کند؛ آن‌جا فایل ZIP دانلود می‌شود، فایل SRT از آن استخراج می‌شود و با encoding درست به استرمیو تحویل داده می‌شود.

> ⚠️ این پروژه میزبان هیچ فایل زیرنویس یا رسانه‌ای نیست و تنها از API رسمی SubSource استفاده می‌کند؛ به همین دلیل داشتن کلید API (`API_KEY`) الزامی است. مسئولیت رعایت قوانین کپی‌رایت و مقررات محلی بر عهدهٔ کاربر است.

## ✨ قابلیت‌ها

- 💬 **زیرنویس فارسی از SubSource** با منبع رسمی `api.subsource.net/api/v1`
- 🧠 **استراتژی جست‌وجوی ترکیبی (Hybrid)** برای سریال‌ها: ابتدا «نام سریال + شمارهٔ فصل» از طریق Cinemeta و سپس fallback به «جست‌وجو با IMDb»
- 🎯 **تطبیق هوشمند فصل و قسمت** با الگوهای `S01E05`، `S1E5` و `1x05` و پشتیبانی از Season Pack (`COMPLETE` + `SEASON01` / `S01`)
- 🧪 **نرمال‌سازی پیش از تطبیق**: حذف فاصله، `-`، `.` و `_` و بزرگ‌کردن حروف نام ریلیز تا الگوهای متفاوت یک فایل هم شناسایی شوند
- 📦 **Decoder مستقل ZIP در دو runtime**: در Node با `adm-zip` و در Worker با پارسر دستی ZIP به‌همراه `DecompressionStream('deflate-raw')` (بدون وابستگی خارجی)
- 🔤 **تشخیص خودکار encoding فارسی**: ابتدا UTF-8 و در صورت دیدن کاراکتر جایگزین (`\uFFFD`) یا خطا در حالت strict، تبدیل از Windows-1256
- 🏷️ **برچسب‌گذاری زیرنویس‌ها** با `lang: fas` و `title` تا نام ریلیز (مثلاً `WEB-DL 1080p`) در فهرست استرمیو دیده شود
- 🟡 **متن حمایت (Promo) داخل زیرنویس** با رنگ زرد و مدت و موقعیت قابل تنظیم (`start` / `end`)
- 🔁 **کلاینت HTTP با retry**: حداکثر ۳ تلاش مجدد با backoff تصاعدی و jitter برای خطاهای `ECONNRESET`، `ETIMEDOUT`، `EAI_AGAIN`، `429` و `5xx`
- ⚡ **جلوگیری از socket مرده**: `keepAlive: false` روی agentهای http/https تا اتصال کهنه باعث `read ECONNRESET` نشود
- 🖥️ **حالت Cluster** برای استفاده از همهٔ هسته‌های CPU، با راه‌اندازی خودکار worker از کار افتاده و خاموشی تدریجی
- 🩺 **مسیر `/health`** با وضعیت پروسه (`uptime`، `memory`، `cpuLoad`) برای load balancer و مانیتورینگ
- 🚦 **لاگ درخواست‌ها همراه با زمان پاسخ**: `GET /manifest.json - 200 (15ms)`
- 🌐 **CORS، `trust proxy` و حذف `X-Powered-By`** در نسخهٔ Node؛ هدرهای `access-control-*` روی همهٔ پاسخ‌های Worker
- 🧯 **بدون crash برای کاربر**: هر خطا به `{ "subtitles": [] }` تبدیل می‌شود تا استرمیو فقط فهرست خالی نشان دهد
- 📦 **دو runtime**: Node.js/Express (`server.js` / `addon.js`) و Cloudflare Workers (`worker.js`) با `manifest.js` مشترک
- 🚀 **دیپلوی خودکار Worker** با GitHub Actions و اعتبارسنجی bundle پیش از deploy (`--dry-run`)

## 🗂️ ساختار پروژه

ساختار واقعی و به‌روز پروژه (خروجی `git ls-files`):

```text
.
├── .env.example                     # الگوی کامل متغیرهای محیطی (کپی کنید به .env)
├── .github/
│   └── workflows/
│       └── deploy-worker.yml        # دیپلوی خودکار Worker به Cloudflare
├── .gitignore
├── README.md                        # راهنمای کاربر و راه‌اندازی
├── addon.js                         # نقطه ورود Node/Express + SDK builder
├── apiClient.js                     # کلاینت axios با retry و backoff
├── assets/
│   └── icons/
│       ├── logo.png                 # لوگوی ۲۵۶×۲۵۶ استفاده‌شده در manifest نسخه Worker
│       └── subtitles-fa.png         # تصویر استاتیک اضافی (۲۰۴۸×۲۰۴۸)
├── config.js                        # تمام تنظیمات از env (dotenv) + مقادیر پیش‌فرض
├── docs/
│   └── DOCUMENTATION.md             # مستندات فنی: معماری، منطق، توابع و راهنمای تست
├── downloadProxy.js                 # دانلود ZIP، استخراج SRT، اصلاح encoding، درج متن Promo
├── manifest.js                      # manifest افزونه (subtitles / movie+series / tt)
├── package.json                     # اسکریپت‌ها و وابستگی‌های Node.js
├── package-lock.json                # نسخه‌های قفل‌شده وابستگی‌ها
├── server.js                        # راه‌انداز Cluster (main در package.json)
├── subtitlesHandler.js              # منطق جست‌وجو و فیلتر زیرنویس در Node
├── worker.js                        # آداپتور Cloudflare Workers (main در wrangler.jsonc)
└── wrangler.jsonc                   # پیکربندی Worker: assets، bindings، run_worker_first
```

| مسیر | نقش |
|---|---|
| `manifest.js` | تعریف `id`، `version`، `resources: ["subtitles"]`، `types: ["movie","series"]` و `idPrefixes: ["tt"]` — مشترک بین هر دو runtime |
| `addon.js` | `new addonBuilder(manifest)` + `defineSubtitlesHandler`، ساخت اپ Express، `getRouter(builder.getInterface())`، مسیر `/download/:token`، `GET /health`، لاگ‌گیر و graceful shutdown |
| `config.js` | خواندن env با dotenv و مقادیر پیش‌فرض (`PORT=7000`، `LONG_TIMEOUT=60000`، `MAX_SOCKETS=50` و…) |
| `apiClient.js` | تابع `apiRequest()` — retry با backoff تصاعدی و jitter، agent بدون keepAlive، تشخیص خطای قابل تلاش مجدد |
| `subtitlesHandler.js` | پارس `id`، جست‌وجو در Cinemeta و SubSource، فیلتر فصل و قسمت، ساخت خروجی `{ subtitles: [...] }` |
| `downloadProxy.js` | دانلود ZIP از SubSource، استخراج اولین `.srt`، تبدیل encoding، درج بلوک Promo و پاسخ با `application/x-subrip` |
| `server.js` | منطق cluster؛ اگر `CLUSTER_ENABLED=true` باشد نقش master را می‌گیرد و به تعداد هسته‌ها worker می‌سازد، در غیر این صورت همان پروسهٔ `addon.js` را `require` می‌کند |
| `docs/DOCUMENTATION.md` | مستندات فنی توسعه‌دهنده: معماری، مستندات تابع‌به‌تابع، الگوریتم تطبیق فصل و قسمت و جدول کامل env |
| `worker.js` | مسیرهای زیر پیشوند `/subtitles`، retry با `AbortController`، پارسر دستی ZIP، `TextDecoder` برای UTF-8/Windows-1256 و سرو لوگو از `env.ASSETS` |
| `wrangler.jsonc` | `name: subsource-stremio-addon`، `main: worker.js`، `compatibility_date: 2026-09-02`، `assets.directory: ./assets/icons` با binding `ASSETS` و `run_worker_first` |
| `.github/workflows/deploy-worker.yml` | push به `main` → `npm ci` → `wrangler deploy --dry-run` → `wrangler secret put API_KEY` → `wrangler deploy` (Wrangler روی نسخهٔ `4.128.0` پین شده است) |

> مستندات فنی کامل (معماری، منطق تابع‌به‌تابع، الگوریتم‌ها و جدول کامل env) در `docs/DOCUMENTATION.md` نگه‌داری می‌شود. پروژه در حال حاضر فایل تست، پیکربندی lint و Dockerfile ندارد؛ فایل `LICENSE` در ریشهٔ مخزن موجود است (مقدار `license` در `package.json` برابر Apache License 2.0 است) و تنها نمونهٔ تنظیمات، فایل `.env.example` است.

## 🚀 نصب و راه‌اندازی محلی

### پیش‌نیازها

- **Node.js نسخهٔ ۲۰٫۱۸٫۱ یا بالاتر** — `package.json` مقدار `engines.node >= 14.0.0` را اعلام می‌کند، اما نسخهٔ قفل‌شدهٔ `cheerio` در `package-lock.json` به `engines.node >= 20.18.1` نیاز دارد؛ برای اطمینان، نسخهٔ ۲۲ توصیه می‌شود (CI هم روی Node 22 اجرا می‌شود).
- **npm**
- **کلید API سرویس SubSource** (از `subsource.net`) — بدون آن خروجی افزونه خالی است.
- برای حالت Worker: **Wrangler** (`npx wrangler`)
- برنامهٔ **Stremio** برای تست نصب افزونه

### ۱. دریافت کد

```bash
git clone https://github.com/alirostami01/Persian-Subtitles.git
cd Persian-Subtitles
```

### ۲. نصب وابستگی‌ها

```bash
npm install          # یا برای نصب دقیق بر اساس lock: npm ci
```

### ۳. ساخت فایل `.env` (برای Node)

```bash
cp .env.example .env
```

سپس `API_KEY` را در آن تنظیم کنید. حداقل تنظیمات لازم:

```ini
SERVER_IP=127.0.0.1
PORT=7000
API_KEY=your-subsource-api-key
```

| متغیر | وضعیت | پیش‌فرض | توضیح |
|---|---|---|---|
| `API_KEY` | **اجباری** | — | کلید SubSource؛ در هدر `X-API-Key` ارسال می‌شود. در نبود آن، پیام `API Key is missing from .env file.` در لاگ چاپ و پاسخ `{ subtitles: [] }` برگردانده می‌شود |
| `PORT` | اختیاری | `7000` | پورت سرور HTTP (`app.listen` در `addon.js`) و بخشی از URL لینک زیرنویس |
| `SERVER_IP` | اختیاری | `127.0.0.1` | آدرس یا دامنه‌ای که در `url` هر زیرنویس نوشته می‌شود؛ در استقرار باید روی دامنهٔ عمومی تنظیم شود |

سه متغیر بالا به‌همراه `LONG_TIMEOUT` و `SUBTITLE_PROMO_*` مقادیری هستند که در کد Node واقعاً مصرف می‌شوند؛ فهرست کامل (به‌همراه تنظیمات runtime ویژهٔ Worker) در `docs/DOCUMENTATION.md` آمده است:

| متغیر | پیش‌فرض | توضیح |
|---|---|---|
| `LONG_TIMEOUT` | `60000` | تایم‌اوت درخواست‌ها به SubSource (میلی‌ثانیه) |
| `SUBTITLE_PROMO_TEXT` | متن حمایت پروژه | متن اضافه‌شده داخل زیرنویس؛ با مقدار خالی، درج متن متوقف می‌شود |
| `SUBTITLE_PROMO_DURATION` | `20` | مدت نمایش متن به ثانیه |
| `SUBTITLE_PROMO_POSITION` | `end` | موقعیت درج متن: `start` یا `end` |
| `MAX_SOCKETS` | `50` | سقف اتصال‌های هم‌زمان agentها در `apiClient.js` |
| `CLUSTER_ENABLED` | `false` | فعال‌سازی حالت cluster (فقط با `npm start`) |
| `WORKER_COUNT` | `0` | تعداد پروسه‌های cluster؛ `0` یعنی به تعداد هسته‌های CPU |

در Cloudflare Workers هیچ فایل `.env` خوانده نمی‌شود؛ `API_KEY` باید به‌صورت Worker Secret تنظیم شود و متن Promo از env یا مقدار پیش‌فرض داخلی (`DEFAULT_PROMO_TEXT` در `worker.js`) می‌آید:

```bash
npx wrangler secret put API_KEY                      # برای پروداکشن
printf 'API_KEY="..."\n' > .dev.vars                 # فقط برای wrangler dev محلی
```

اگر ترجیح می‌دهید فایل `.env` نسازید، در Node می‌توانید مقادیر را به‌صورت inline بدهید:

```bash
API_KEY=xxxx SERVER_IP=127.0.0.1 PORT=7000 node server.js
```

### ۴. اجرای برنامه

**حالت Node.js — توسعه (تک‌پروسه):**

```bash
npm run dev          # => node addon.js
```

خروجی موفق:

```text
===========================================
Persian Subtitles Add-on Server Started
===========================================
Server listening on port: 7000
Available CPU cores: 8
Install URL: http://127.0.0.1:7000/manifest.json
Health check: http://127.0.0.1:7000/health
===========================================
```

**حالت Node.js — پروداکشن (Cluster):**

```bash
npm start            # => node server.js
```

```text
===========================================
Starting Cluster Mode
===========================================
Master process 4123 started
Detected 8 CPU cores
Spawning 8 worker processes...
===========================================

Worker 4124 spawned
✓ Worker 4124 is online (1/8)
...
✅ All workers are ready to handle requests!
```

> برای این حالت `CLUSTER_ENABLED=true` در `.env` لازم است؛ اگر `false` باشد، `server.js` همان مسیر تک‌پروسه را می‌رود. برای تعداد ثابت worker، مقدار `WORKER_COUNT` را تنظیم کنید.

اگر پورت اشغال باشد:

```text
Error: listen EADDRINUSE: address already in use :::7000
```

راه‌حل:

```bash
PORT=7001 npm run dev
```

**حالت Cloudflare Workers (Edge):**

```bash
npx wrangler dev
```

```text
⛅️ wrangler is running at http://localhost:8787
Manifest: http://localhost:8787/subtitles/manifest.json
```

> در حالت Worker همهٔ مسیرها زیر پیشوند `/subtitles` قرار دارند؛ باز کردن ریشه (`http://localhost:8787/`) پاسخ `404` می‌دهد و `http://localhost:8787/subtitles` یک پاسخ وضعیت JSON برمی‌گرداند.

### ۵. نصب در Stremio

نسخهٔ Node:

```text
stremio://localhost:7000/manifest.json
```

نسخهٔ Workers (لوکال):

```text
stremio://localhost:8787/subtitles/manifest.json
```

یا ابتدا manifest را در مرورگر باز کنید و روی **Install** کلیک کنید:

```text
http://localhost:7000/manifest.json
http://localhost:8787/subtitles/manifest.json
```

## ☁️ استقرار (Deployment)

### گزینهٔ A: میزبانی Node.js (VPS، Railway، Render، Fly.io، Heroku)

1. Node.js نسخهٔ ۲۰٫۱۸٫۱ یا بالاتر (پیشنهادی: ۲۲) روی محیط اجرا فعال باشد.
2. وابستگی‌ها را نصب کنید: `npm ci`
3. دستور اجرا را روی `npm start` بگذارید (یعنی `node server.js`)؛ `main` در `package.json` همین است. برای اجرای تک‌پروسه: `node addon.js`.
4. `API_KEY` را تنظیم و `SERVER_IP` را روی دامنهٔ عمومی ست کنید (بدون `SERVER_IP` درست، استرمیو نمی‌تواند فایل زیرنویس را دانلود کند).
5. کد، مقدار `PORT` را از env با پیش‌فرض `7000` می‌خواند؛ توجه کنید که `SERVER_IP` و `PORT` مستقیماً در URL هر زیرنویس نوشته می‌شوند، پس همان‌ها را روی آدرس عمومی تنظیم کنید.
6. در پروداکشن `CLUSTER_ENABLED=true` را فعال کنید.

آدرس نصب پس از استقرار:

```text
stremio://YOUR_DOMAIN/manifest.json
```

مسیرهای ضروری: `/manifest.json`، `/subtitles/...`، `/download/{id}`، `/health`

> ⚠️ **توجه مهم:** در نسخهٔ Node، لینک هر زیرنویس به‌صورت `http://${SERVER_IP}:${PORT}/download/...` ساخته می‌شود؛ یعنی scheme همیشه `http` است و `PORT` نیز حتماً در URL می‌آید. برای سرو روی پورت ۴۴۳ پشت TLS proxy، مسیر `/download/...` را در پراکسی به پورت واقعی داخل سرور یا کانتینر پاس بدهید و `SERVER_IP` را فقط روی نام دامنه تنظیم کنید. راه‌حل تمیزتر، ساخت URL از `x-forwarded-proto` و `Host` است که در بخش «سرور Node.js و روت‌ها» در `docs/DOCUMENTATION.md` توضیح داده شده است.

**نمونهٔ Docker** (خودتان بسازید — در مخزن Dockerfile وجود ندارد):

```dockerfile
FROM node:22-alpine
WORKDIR /app
# نکته: مقدار name در package.json فعلاً «Persian Subtitles» است؛
# npm این نام را برای publish نمی‌پذیرد (اجرای محلی مشکلی ندارد).
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
ENV PORT=7000
EXPOSE 7000
CMD ["node", "server.js"]
```

```bash
docker build -t persian-subtitles-addon .
docker run -d -p 7000:7000 --env-file .env persian-subtitles-addon
```

**پشت Load Balancer:**

```nginx
upstream stremio_subtitles {
    server 10.0.0.1:7000;
    server 10.0.0.2:7000;
}

server {
    listen 443 ssl;
    server_name subs.example.com;

    location / {
        proxy_pass http://stremio_subtitles;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://stremio_subtitles/health;
    }
}
```

### گزینهٔ B: Cloudflare Workers (پیشنهادی برای Edge، رایگان)

`wrangler.jsonc` نیازی به تغییر ندارد؛ `API_KEY` نباید در آن نوشته شود (این فایل commit شده است) و باید به‌صورت secret تنظیم شود.

```bash
npm install
npx wrangler secret put API_KEY
npx wrangler deploy
```

یا به‌صورت خودکار از طریق GitHub Actions — trigger در `deploy-worker.yml` فقط با تغییر این فایل‌ها فعال می‌شود: `worker.js`، `manifest.js`، `wrangler.jsonc`، `package.json`، `package-lock.json`، `assets/icons/**` و خودِ workflow (به‌علاوهٔ `workflow_dispatch` دستی).

آدرس نصب پس از استقرار:

```text
stremio://<worker>.workers.dev/subtitles/manifest.json
```

مسیرهای ضروری Worker: `/subtitles/manifest.json`، `/subtitles/movie/...`، `/subtitles/series/...`، `/subtitles/download/{id}` و `/subtitles/logo.png`.

همهٔ پاسخ‌های JSON هدرهای `access-control-allow-origin: *` و `cache-control: no-store` دارند (فقط `manifest.json` با `max-age=300` و فایل زیرنویس با `private, max-age=300` کش می‌شوند).

**Secretهای موردنیاز در GitHub Actions:**

| Secret | کاربرد |
|---|---|
| `CLOUDFLARE_API_TOKEN` | احراز هویت Wrangler |
| `CLOUDFLARE_ACCOUNT_ID` | تعیین account مقصد |
| `SUBSOURCE_API_KEY` | در گام «Configure SubSource API secret» با `wrangler secret put API_KEY` روی Worker تنظیم می‌شود |

**نکات HTTPS و Proxy:**

- **Node:** `app.set('trust proxy', true)` از پیش فعال است تا IP واقعی پشت load balancer درست تشخیص داده شود؛ اما URL زیرنویس‌ها همچنان از `SERVER_IP` و `PORT` ساخته می‌شود، پس آن‌ها را خودتان درست تنظیم کنید.
- **Workers:** `url.origin` همیشه scheme و host درست را دارد و لینک `/subtitles/download/{id}` به‌صورت خودکار ساخته می‌شود؛ تنظیم اضافه‌ای لازم نیست.

## 🎯 نحوهٔ استفاده

پس از نصب افزونه در استرمیو:

1. یک فیلم یا سریال دارای شناسهٔ IMDb را باز کنید.
2. استرمیو درخواست `subtitles` را به افزونه می‌فرستد (`/subtitles/{type}/{id}.json`).
3. افزونه با نام سریال (برای سریال) یا IMDb (برای فیلم و حالت fallback) در SubSource جست‌وجو می‌کند.
4. برای فیلم‌ها، همهٔ زیرنویس‌های فارسی همان `movieId` (مرتب‌شده بر اساس rating، حداکثر ۱۰۰ مورد) برگردانده می‌شوند.
5. برای سریال‌ها، فهرست بر اساس شمارهٔ فصل و قسمت فیلتر می‌شود و اگر نسخهٔ تک‌قسمتی موجود نباشد، Season Pack کامل انتخاب می‌شود.
6. با انتخاب یک زیرنویس، استرمیو فایل را از `/subtitles/download/{subtitleId}` می‌گیرد که SRT خالص و UTF-8 شده را تحویل می‌دهد.
7. در انتها (یا ابتدای) فیلم، متن حمایت زردرنگ نمایش داده می‌شود که با `SUBTITLE_PROMO_*` قابل تغییر یا حذف است.

نمونهٔ پاسخ manifest (نسخهٔ Node):

```json
{
  "id": "org.alirostami.subtitles.persian",
  "version": "1.0.0",
  "name": "Persian Subtitles",
  "author": "Ali Rostami",
  "contactEmail": "rostami.ali@gmail.com",
  "resources": ["subtitles"],
  "types": ["movie", "series"],
  "idPrefixes": ["tt"],
  "catalogs": []
}
```

نمونهٔ یک آیتم زیرنویس در پاسخ:

```json
{
  "id": "1234567",
  "url": "http://127.0.0.1:7000/download/1234567",
  "lang": "fas",
  "title": "WEB-DL 1080p S01E05"
}
```

## 🔌 مسیرها و API

### Node.js (`addon.js` / `server.js`)

| مسیر | توضیح |
|---|---|
| `GET /manifest.json` | manifest افزونه، تولیدشده توسط `getRouter` از SDK رسمی |
| `GET /subtitles/movie/{imdbId}.json` | زیرنویس فیلم؛ مثال: `/subtitles/movie/tt1234567.json` |
| `GET /subtitles/series/{imdbId}:{season}:{episode}.json` | زیرنویس یک قسمت؛ مثال: `/subtitles/series/tt1234567:1:3.json` |
| `GET /download/{subtitleId}` | دانلود SRT (استخراج از ZIP + تبدیل encoding + متن Promo) |
| `GET /health` | وضعیت سرویس: `status`، `timestamp`، `uptime`، `memory`، `cpuLoad` |

### Cloudflare Workers (`worker.js`)

| مسیر | توضیح |
|---|---|
| `GET /subtitles` یا `/subtitles/` | پاسخ JSON: `{ status:'ok', service:'subsource-stremio-addon', runtime:'cloudflare-workers' }` |
| `GET /subtitles/health` | همان پاسخ سلامت (بدون `uptime` و `memory`) |
| `GET /subtitles/manifest.json` | manifest به‌همراه لوگوی مطلق `https://<origin>/subtitles/logo.png` و `behaviorHints.configurable: false` |
| `GET /subtitles/logo.png` | لوگوی افزونه (از `env.ASSETS` — پوشهٔ `assets/icons`) |
| `GET /subtitles/movie/{imdbId}.json` | زیرنویس فیلم در Worker |
| `GET /subtitles/series/{imdbId}:{season}:{episode}.json` | زیرنویس سریال در Worker |
| `GET /subtitles/download/{subtitleId}` | دانلود SRT در Worker |

> هر درخواست غیر از `GET` در Worker پاسخ `405 Method Not Allowed` و هر `OPTIONS` پاسخ `204` با هدرهای CORS می‌گیرد. در Node نیز مسیر ریشه (`GET /`) تعریف نشده و `404` برمی‌گرداند؛ برای بررسی سلامت از `/health` استفاده کنید.

### Endpointهای خارجی مورد استفادهٔ افزونه

| سرویس | endpoint |
|---|---|
| SubSource | `GET /api/v1/movies/search?searchType=text&q={name}&season={n}` |
| SubSource | `GET /api/v1/movies/search?searchType=imdb&imdb={imdbId}` |
| SubSource | `GET /api/v1/subtitles?movieId={id}&language=farsi_persian&sort=rating&limit=100` |
| SubSource | `GET /api/v1/subtitles/{subtitleId}/download` (ZIP) |
| Stremio Cinemeta | `GET https://v3-cinemeta.strem.io/meta/series/{imdbId}.json` |

بررسی سریع با curl:

```bash
# Node
curl http://localhost:7000/manifest.json
curl http://localhost:7000/health
curl http://localhost:7000/subtitles/movie/tt1234567.json
curl http://localhost:7000/subtitles/series/tt1234567:1:3.json
curl http://localhost:7000/download/1234567 | head

# Workers
curl http://localhost:8787/subtitles/manifest.json
curl http://localhost:8787/subtitles/health
curl http://localhost:8787/subtitles/movie/tt1234567.json
curl http://localhost:8787/subtitles/series/tt1234567:1:3.json
```

## ⚙️ خلاصهٔ عملکرد فنی

### معماری ماژولار

```text
                    manifest.js (منبع حقیقت: id, version, resources)
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
   addon.js (Node/Express)               worker.js (Cloudflare Edge)
   SDK رسمی + getRouter                  پارس مسیر + fetch + ZIP parser
        │                                     │
        ├── subtitlesHandler.js               ├── منطق معادل داخل worker.js
        ├── downloadProxy.js                  ├── downloadProxy داخل worker.js
        └── apiClient.js ──► config.js        └── env (API_KEY, SUBTITLE_PROMO_*)
        │
server.js (cluster supervisor → addon.js)
```

### جریان هسته (Node)

```text
Stremio request → /subtitles/{type}/{id}.json
   ↓
getRouter(addonBuilder(manifest).getInterface())   ← از stremio-addon-sdk
   ↓
subtitlesHandler({ type, id })
   ├─ !process.env.API_KEY      → { subtitles: [] } + لاگ خطا
   ├─ parse id                  → series: tt:season:episode / movie: tt
   ├─ getMovieId (سریال)        ← Cinemeta → SubSource search (text + season)
   ├─ fallback                  ← GET /movies/search?searchType=imdb&imdb=...
   ├─ GET /subtitles?movieId=…&language=farsi_persian&sort=rating&limit=100
   ├─ filterSeriesSubtitles(...) ← الگوهای S01E05 / S1E5 / 1x05 / SEASON PACK
   └─ map → { id, url: http://SERVER_IP:PORT/download/{id}, lang:'fas', title }
   ↓
GET /download/:token  (downloadProxy)
   ├─ apiRequest → ZIP (arraybuffer)
   ├─ adm-zip → اولین entry با پسوند .srt
   ├─ iconv-lite → UTF-8، در صورت \uFFFD → Windows-1256
   ├─ addPromoTextToSubtitle(...)  ← بلوک زرد ASS-style، start/end
   └─ 200 + Content-Type: application/x-subrip; charset=utf-8
```

**جزئیات مهم:**

- تطبیق محتوا فقط از طریق SubSource انجام می‌شود؛ جست‌وجوی متنی آزاد یا fallback به slug وجود ندارد.
- افزونه catalog، meta یا stream ارائه نمی‌کند و فقط منبعی از نوع `subtitles` دارد (`catalogs: []`).
- SubSource باید `success: true` و آرایهٔ `data` با فیلدهای `movieId` / `subtitleId` / `releaseInfo` برگرداند.
- نام فایل‌های داخل ZIP اهمیتی ندارد؛ اولین فایل `.srt` داخل آرشیو انتخاب می‌شود.
- متن Promo با تگ `{\c&H00FFFF00&}` نوشته می‌شود؛ پلیرهایی که تگ ASS را نمی‌فهمند آن را به‌صورت خام نشان می‌دهند. برای حذف کامل، `SUBTITLE_PROMO_TEXT` را خالی بگذارید.
- در صورت هر خطا یا پیدا نشدن نتیجه، پاسخ `{ "subtitles": [] }` است؛ یعنی استرمیو فقط فهرست خالی نشان می‌دهد و پخش فیلم مختل نمی‌شود.
- retry فقط برای خطاهای شبکه‌ای و `429`/`5xx` انجام می‌شود؛ سایر خطاهای `4xx` بلافاصله fail می‌شوند.
- `stremio-addon-sdk` و `express` فقط در runtime نود مصرف می‌شوند و در Worker باندل نمی‌شوند (ورودی Worker فایل `worker.js` است که تنها به `manifest.js` وابسته است).
- `wrangler.jsonc` با `assets.directory: ./assets/icons` فایل `logo.png` را در `env.ASSETS` می‌گذارد تا `/subtitles/logo.png` سرو شود.

### وابستگی‌ها

| پکیج | نقش |
|---|---|
| `stremio-addon-sdk` | `addonBuilder` و `getRouter` برای manifest و مسیرهای افزونه |
| `express`، `cors`، `dotenv` | وب‌سرور، CORS و بارگذاری `.env` |
| `axios` | HTTP client در `apiClient.js` |
| `adm-zip` | استخراج `.srt` از آرشیو ZIP (فقط Node) |
| `iconv-lite` | تبدیل Windows-1256 به UTF-8 |
| `cheerio` | پارس HTML (در حال حاضر در مسیر اصلی استفاده نمی‌شود) |
| `https-proxy-agent`، `axios-https-proxy-fix` | پشتیبانی proxy برای شبکه‌های محدود |

## 🐛 عیب‌یابی

### فهرست زیرنویس در استرمیو خالی است

- `API_KEY` تنظیم نشده است؛ در لاگ Node این خط را می‌بینید: `API Key is missing from .env file.` و در لاگ Worker: `Subtitle handler error: API_KEY is not configured.`
- SubSource برای آن `imdbId` نتیجه‌ای ندارد (`Both attempts failed to find a movieId.`).
- زیرنویس `farsi_persian` برای آن `movieId` وجود ندارد (`No Persian subtitles found for movieId: ...`).
- برای سریال‌ها، فیلتر فصل و قسمت همهٔ نتایج را حذف کرده است؛ با لاگ `Applying detailed filter for patterns: [...]` می‌توانید الگوها را بررسی کنید.

### فایل زیرنویس دانلود نمی‌شود (خطای ۴۰۴ یا ۵۰۰ در پلیر)

- `SERVER_IP` هنوز روی `127.0.0.1` است، پس URL داخل پاسخ به آدرس لوکال اشاره می‌کند. آن را روی دامنهٔ عمومی تنظیم و افزونه را دوباره نصب یا رفرش کنید.
- `PORT` داخل URL همان پورتی است که سرور روی آن listen کرده است؛ اگر از بیرون با پورت دیگری (مثلاً ۴۴۳ یا ۸۰۸۰) به سرویس می‌رسید، باید همان مسیر را در پراکسی map کنید.
- پاسخ `Server configuration error` یعنی کلید API روی سرور وجود ندارد (در Worker: secret تنظیم نشده است).

### در لاگ `read ECONNRESET` یا timeout می‌بینم

`apiClient.js` خودش سه بار با backoff تلاش مجدد می‌کند (لاگ: `Request failed (ECONNRESET) ... Retrying in 780ms (attempt 1/3)`). اگر خطا ادامه داشت:

- مقدار `LONG_TIMEOUT` را افزایش دهید (مثلاً `120000`).
- مقدار `MAX_SOCKETS` را کم کنید تا تعداد اتصال‌های هم‌زمان پایین بیاید (پیش‌فرض آن در `config.js` برابر `50` است).
- خروجی شبکه و فایروال را بررسی کنید؛ گاهی پراکسی‌های سازمانی اتصال keep-alive را قطع می‌کنند.

### زیرنویس فارسی به‌هم‌ریخته یا به‌شکل `Ø¶` نمایش داده می‌شود

یعنی فایل با encoding ویندوز-۱۲۵۶ بوده است. کد خودش `\uFFFD` را تشخیص می‌دهد و دوباره encode می‌کند (لاگ: `Re-encoded subtitle from Windows-1256 to UTF-8 for: ...`). اگر باز هم خراب بود، احتمالاً فایل نه UTF-8 با BOM بوده و نه cp1256، و باید الگوریتم تشخیص encoding در `downloadProxy.js` گسترش پیدا کند.

### متن Promo نمایش داده نمی‌شود

- `SUBTITLE_PROMO_TEXT` خالی گذاشته شده است.
- `SUBTITLE_PROMO_POSITION=end` است و زیرنویس فقط یک بلوک کوتاه دارد؛ برای بررسی سریع، مقدار `start` را امتحان کنید.
- پلیر تگ `{\c...}` را پشتیبانی نمی‌کند؛ متن نمایش داده می‌شود ولی بدون رنگ.

### لوگو در استرمیو نمایش داده نمی‌شود

- **Node:** `manifest.js` هیچ فیلد `logo` ندارد و استرمیو از آیکن پیش‌فرض استفاده می‌کند. برای افزودن لوگو، فیلد `logo` را با یک URL مطلق به `manifest.js` اضافه کنید.
- **Workers:** لوگو از `https://<origin>/subtitles/logo.png` سرو می‌شود؛ مطمئن شوید assetها با deploy آپلود شده‌اند (`wrangler deploy` پوشهٔ `assets/icons` را می‌فرستد). اگر `404` گرفتید، binding `ASSETS` و `assets.directory` را در `wrangler.jsonc` بررسی کنید.

### خطای `Worker died` یا بالا نیامدن cluster

- `npm start` با `CLUSTER_ENABLED=true` به تعداد هسته‌ها worker می‌سازد؛ اگر رم کم است، `WORKER_COUNT=2` را تنظیم کنید.
- master پس از از کار افتادن یک worker، یک ثانیه صبر می‌کند و دوباره fork می‌کند (`🔄 New worker ... started`)؛ برای دیدن علت اصلی، لاگ همان worker را ببینید.
- برای توسعه از `npm run dev` (تک‌پروسه) استفاده کنید تا stack trace کامل و بدون نویز داشته باشید.

### `wrangler deploy` در GitHub Actions شکست می‌خورد

- آیا `CLOUDFLARE_API_TOKEN`، `CLOUDFLARE_ACCOUNT_ID` و `SUBSOURCE_API_KEY` در repository secrets تنظیم شده‌اند؟ (گام دوم با `test -n "$SUBSOURCE_API_KEY"` صراحتاً fail می‌شود.)
- اگر تغییرات شما فایل‌های trigger را لمس نکرده باشد، workflow اجرا نمی‌شود؛ از **Run workflow** (`workflow_dispatch`) دستی استفاده کنید.
- نسخهٔ Wrangler در workflow روی `4.128.0` پین شده است؛ لاگ Action را بررسی کنید.

## 🤝 مشارکت

Pull Requestها و Issueها برای بهبود تطبیق فصل و قسمت، سازگاری با تغییرات API سابسورس، افزودن تست و بهبود مستندات با آغوش باز پذیرفته می‌شوند.

پیش از تغییر منطق استخراج، بخش‌های «نقشهٔ ماژول‌ها» و «لایهٔ جست‌وجوی ترکیبی» در `docs/DOCUMENTATION.md` را مطالعه کنید.

## 📄 مجوز

مقدار `license` در `package.json` برابر **Apache License 2.0** است.

---

ساخته شده با ❤️ برای جامعهٔ فارسی‌زبان Stremio — [حمایت از ادامهٔ مسیر](/support/)
