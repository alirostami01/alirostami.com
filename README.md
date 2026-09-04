# alirostami.com

استاتیک سایت شخصی (خروجی Hugo + پوسته LoveIt) که مستقیماً از همین مخزن سرو می‌شود.

## صفحه حمایت

صفحه فارسی حمایت از یک منبع واحد ساخته می‌شود و روی چند آدرس سرو می‌شود:

| آدرس | فایل |
|---|---|
| `/support/` (canonical) | `support/index.html` |
| `/support.html` | `support.html` |
| `/fa/support/` | `fa/support/index.html` |
| `/fa/support.html` | `fa/support.html` |

### بازتولید صفحه

```bash
python3 scripts/build-support-page.py
```

محتوای صفحه (متن‌ها، کیف‌پول‌ها، پروژه‌ها و CSS) داخل همان اسکریپت است.

### کدهای QR کیف‌پول‌ها

هر QR دقیقاً خودِ آدرس کیف‌پول را کدگذاری می‌کند (بدون URI scheme یا مبلغ):

```bash
pip install segno
python3 scripts/generate-wallet-qr.py     # -> images/donate/*.png و *.svg
```

## صفحات مستندات پروژه‌ها

محتوا در `content/<slug>.md` نوشته می‌شود و با تم اصلی سایت رندر می‌شود:

| آدرس | منبع |
|---|---|
| `/Persian-Subtitles/` (canonical) | `content/persian-subtitles.md` |
| `/persian-subtitles/` (alias) | همان فایل |

```bash
pip install markdown
cd scripts && python3 build-project-page.py
```

پوستهٔ مشترک (هدر، فوتر، اسکریپت‌ها) در `scripts/theme.py` است.

### آیکون پروژه‌ها

آیکون‌ها در `images/projects/<slug>.png` قرار می‌گیرند
(`persian-subtitles`، `persian-streams`). برای آماده‌سازی یک لوگوی جدید:

```bash
pip install pillow
python3 scripts/prepare-project-icon.py /path/to/logo.png persian-subtitles
python3 scripts/build-support-page.py
```

اسکریپت پس‌زمینه سفید دور لوگوی دایره‌ای را شفاف می‌کند، تصویر را مربع و
به اندازه ۲۵۶×۲۵۶ ذخیره می‌کند.

## پیش‌نمایش محلی

```bash
python3 -m http.server 8000
# http://localhost:8000/support/
```
