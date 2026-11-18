#!/usr/bin/env python3
"""Build the Persian Jensen Huang article from the shared site article shell."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from image_utils import ROOT, apply_site_postprocessors

_sitemap_spec = importlib.util.spec_from_file_location(
    "site_sitemap_builder", ROOT / "scripts" / "update-sitemaps.py"
)
if _sitemap_spec is None or _sitemap_spec.loader is None:
    raise RuntimeError("could not load the sitemap generator")
_sitemap_module = importlib.util.module_from_spec(_sitemap_spec)
_sitemap_spec.loader.exec_module(_sitemap_module)
write_sitemap = _sitemap_module.write_sitemap

SOURCE = ROOT / "posts" / "aima-4e-persian" / "index.html"
TARGET = ROOT / "posts" / "jensen-huang-nvidia" / "index.html"
TITLE = "جنسن هوانگ و انویدیا؛ از انقلاب هوش مصنوعی تا بحران مدیریتی"
PUBLISHED = "2026-11-18T12:00:00+03:30"
PERSIAN_DATE = "۲۷ آبان ۱۴۰۵"

BODY = r'''<div class="content" id="content">
                            <p class="lead">جنسن هوانگ، هم‌بنیان‌گذار انویدیا، از چهره‌هایی است که با سرمایه‌گذاری بلندمدت روی پردازش موازی و نرم‌افزار CUDA، مسیر صنعت تراشه و زیرساخت هوش مصنوعی را تغییر داد. در نوامبر ۲۰۲۶، خبر کناره‌گیری او از مدیرعاملی انویدیا در پی گزارش‌هایی دربارهٔ روابط شخصی و نگرانی‌های حاکمیت شرکتی و امنیت ملی، بار دیگر جایگاه اخلاق و پاسخ‌گویی مدیران فناوری را به بحث گذاشت.</p>

                            <figure class="article-hero">
                                <img src="/images/posts/jensen-huang.jpeg" alt="جنسن هوانگ، هم‌بنیان‌گذار و مدیرعامل پیشین انویدیا، با کت چرمی مشکی" width="1280" height="720" fetchpriority="high" decoding="async">
                                <figcaption>جنسن هوانگ؛ چهره‌ای محوری در گذار انویدیا از گرافیک رایانه‌ای به رایانش شتاب‌یافته و هوش مصنوعی. عکس: تصویر پیوست‌شده توسط نویسنده.</figcaption>
                            </figure>

                            <aside class="fact-note" aria-label="یادداشت دربارهٔ دقت و وضعیت گزارش‌ها">
                                <strong>یادداشت دقت:</strong> این مقاله تا ۱۸ نوامبر ۲۰۲۶ به‌روز شده است. استعفای هوانگ و معرفی مدیرعامل موقت در اطلاعیهٔ رسمی انویدیا تأیید شده؛ اما اطلاعیه علت استعفا را شرح نمی‌دهد. مطالب مربوط به روابط شخصی و ارتباط احتمالی یک مدیر تجاری با دستگاه اطلاعاتی، گزارش رسانه‌ها و ادعاهای تأییدنشده‌اند و نباید با اثبات جرم یا نتیجهٔ قضایی اشتباه گرفته شوند.
                            </aside>

                            <h2>از تایوان تا سیلیکون‌ولی</h2>
                            <p>جنسن هوانگ (Jensen Huang؛ نام چینی: 黃仁勳) در سال ۱۹۶۳ در تایوان متولد شد و در کودکی به ایالات متحده رفت. او مهندسی برق را در دانشگاه ایالتی اورگن خواند و کارشناسی ارشد همین رشته را از دانشگاه استنفورد گرفت. پیش از راه‌اندازی شرکت خود، در شرکت‌های LSI Logic و AMD کار کرد؛ تجربه‌ای که آشنایی عملی او با طراحی تراشه و صنعت نیمه‌رسانا را شکل داد. <a href="https://nvidianews.nvidia.com/bios/jensen-huang" target="_blank" rel="noopener noreferrer">زندگی‌نامهٔ رسمی انویدیا</a> این مسیر تحصیلی و حرفه‌ای را ثبت کرده است.</p>

                            <h2>تأسیس انویدیا و شرط‌بندی روی GPU</h2>
                            <p>هوانگ در سال ۱۹۹۳ با کریس مالاخوفسکی (Chris Malachowsky) و کرتیس پریم (Curtis Priem) انویدیا را بنیان گذاشت. تمرکز نخست شرکت پردازنده‌های گرافیکی برای رایانه‌های شخصی و بازی بود؛ بازاری رقابتی که مسیرش از ابتدا تضمین‌شده نبود. در سال ۱۹۹۹ انویدیا GeForce 256 را عرضه کرد و GPU را به‌عنوان واحدی مستقل برای پردازش گرافیکی معرفی کرد. این نقطهٔ عطف بعدها زمینهٔ استفاده از GPUها در محاسبات فراتر از گرافیک را فراهم کرد.</p>

                            <h2>CUDA؛ پلی از گرافیک به هوش مصنوعی</h2>
                            <p>GPUها برای اجرای هم‌زمان تعداد زیادی عملیات طراحی شده‌اند. هوانگ و انویدیا این قابلیت را به پردازش علمی و عمومی گسترش دادند: پلتفرم CUDA که در ۲۰۰۶ معرفی شد، امکان برنامه‌نویسی GPU را برای محاسباتی فراتر از ترسیم تصویر فراهم کرد. با رشد یادگیری عمیق، این زیربنا به مزیت مهمی برای آموزش و اجرای مدل‌های هوش مصنوعی تبدیل شد.</p>
                            <p>امروزه نقش انویدیا فراتر از فروش تراشه است: شتاب‌دهنده‌ها، شبکه‌سازی مراکز داده، کتابخانه‌های نرم‌افزاری و ابزارهای توسعه‌اش با هم یک پلتفرم رایانش شتاب‌یافته می‌سازند. این مجموعه در آموزش مدل‌های بزرگ، خدمات ابری، شبیه‌سازی، رباتیک، خودروهای خودران و پردازش تصویر به‌کار می‌رود. هوانگ را می‌توان نه فقط مدیر یک سازندهٔ GPU، بلکه از معماران تجاری این اکوسیستم دانست.</p>

                            <h2>سبک رهبری و بهای رشد سریع</h2>
                            <p>هوانگ به تمرکز بر افق‌های بلندمدت، سرمایه‌گذاری سنگین در تحقیق‌وتوسعه و تصمیم‌گیری سریع شناخته می‌شود. ساختار سازمانی نسبتاً کم‌لایه و دسترسی مستقیم او به مدیران و کارکنان نیز بارها توصیف شده است. چنین سبکی می‌تواند هماهنگی و سرعت را بالا ببرد، اما در کنار فرهنگ کاری پرفشار، پرسش‌هایی دربارهٔ تمرکز اختیار، فشار بر کارکنان و میزان وابستگی شرکت به بنیان‌گذار ایجاد می‌کند.</p>
                            <p>موفقیت انویدیا حاصل یک تصمیم یا یک فرد نبود؛ پژوهش مهندسان، اکوسیستم توسعه‌دهندگان، سرمایه‌گذاری پیوسته و انتخاب‌های دشوار شرکت نیز در آن سهم داشتند. همین نکته برای فهم بحران جانشینی اهمیت دارد: سازمانی که به یک بنیان‌گذار گره بخورد، باید برای انتقال مسئولیت هم برنامه داشته باشد.</p>

                            <h2>چه چیزی در نوامبر ۲۰۲۶ گزارش شد؟</h2>
                            <p>در روزهای پیش از اعلام کناره‌گیری، گزارش‌های رسانه‌ای دربارهٔ رابطهٔ خارج از ازدواج هوانگ منتشر شد. نیویورک‌تایمز گزارش داد که او در یادداشتی به کارکنان در ۸ نوامبر، بی‌وفایی به همسرش را پذیرفت و بابت آسیبی که به خانواده‌اش وارد شده عذرخواهی کرد. این روزنامه همچنین از ارتباطی با آلیس هوانگ (Alice Huang)، مدیر اجرایی پیشین شرکت سنگاپوری Megaspeed، نوشت و مدعی شد نهادهای اطلاعاتی آمریکا او را مظنون به ارتباط با چین می‌دانند. برخی گزارش‌ها همچنین ارتباط تجاری Megaspeed با زیرساخت‌های پردازشی انویدیا را مطرح کردند. این موارد حساسیت‌هایی دربارهٔ تضاد منافع و دسترسی به فناوری‌های مشمول کنترل صادرات برانگیخت.</p>
                            <p>باید مرز میان واقعیت تأییدشده و ادعا روشن بماند: ادعای جاسوسی دربارهٔ آلیس هوانگ در گزارش‌ها به‌عنوان ارزیابی یا ظن اطلاعاتی مطرح شده است؛ در زمان نگارش این مقاله اثبات قضایی آن اعلام نشده و خود گزارش‌های خبری نیز دربارهٔ تأیید مستقل آن قید گذاشته‌اند. در منابع بررسی‌شده، اتهام کیفری علیه جنسن هوانگ مطرح نشده است. رابطهٔ شخصی یا ارتباط تجاری به‌تنهایی اثبات جاسوسی یا تخلف قانونی نیست.</p>
                            <p>در روزهای بعد رسانه‌ها گزارش دیگری دربارهٔ رابطهٔ احتمالی هوانگ با یکی از مدیران انویدیا، کیمبرلی پاول (Kimberly Powell)، منتشر کردند. از آنجا که گزارش‌ها او را در ساختار سازمانی زیرمجموعهٔ هوانگ توصیف می‌کردند، بحث از حریم خصوصی فراتر رفت و موضوع رابطهٔ قدرت، سیاست‌های محل کار و تضاد منافع مطرح شد. این بخش نیز باید به‌عنوان گزارش رسانه‌ای و نه یافتهٔ نهایی تحقیق داخلی خوانده شود.</p>

                            <h2>استعفا یا برکناری؟ آنچه رسماً اعلام شد</h2>
                            <p>انویدیا در ۱۲ نوامبر ۲۰۲۶ اعلام کرد هوانگ از ریاست، مدیرعاملی و عضویت در هیئت‌مدیره استعفا داده است. کولت کرس (Colette Kress)، مدیر ارشد مالی شرکت، تا زمان انتخاب جانشین دائمی به‌عنوان مدیرعامل موقت منصوب شد و هاروی جونز (Harvey C. Jones) ریاست هیئت‌مدیره را برعهده گرفت. اطلاعیهٔ رسمی از سهم هوانگ در شرکت قدردانی می‌کند، اما دلیل کناره‌گیری را بیان نمی‌کند. بنابراین توصیف دقیق این است که او رسماً استعفا داد؛ گزارش‌های رسانه‌ای هم‌زمان از فشار و بررسی هیئت‌مدیره خبر داده‌اند.</p>
                            <p>در ۱۷ نوامبر، به‌گزارش آسوشیتدپرس، هیئت‌مدیره به‌اتفاق آرا با بازگشت هوانگ مخالفت کرد و اعلام کرد قصد ندارد او را دوباره مدیرعامل کند. در نتیجه، تا تاریخ به‌روزرسانی این مقاله، کرس همچنان مدیرعامل موقت بود و جست‌وجو برای جانشین دائمی ادامه داشت. این تصمیم به معنای پایان فوری نقش تاریخی هوانگ در شکل‌گیری شرکت نیست؛ اما نشان می‌دهد هیئت‌مدیره بحران را مسئله‌ای فراتر از یک عذرخواهی شخصی تلقی کرده است.</p>

                            <h2>چرا ماجرا به حاکمیت شرکتی گره خورد؟</h2>
                            <ul>
                                <li><strong>اعتماد و اعتبار:</strong> مدیرعامل نمایندهٔ شرکت در برابر کارکنان، سرمایه‌گذاران، مشتریان و دولت‌هاست؛ رفتار او می‌تواند بر اعتماد به کل سازمان اثر بگذارد.</li>
                                <li><strong>تضاد منافع و رابطهٔ قدرت:</strong> رابطهٔ شخصی با شریک تجاری یا کارمندِ زیرمجموعه، حتی بدون اثبات تخلف، شفافیت و بررسی مستقل را ضروری می‌کند.</li>
                                <li><strong>فناوری راهبردی و صادرات:</strong> تراشه‌های پیشرفتهٔ هوش مصنوعی مشمول محدودیت‌های صادراتی‌اند؛ ازاین‌رو ارزیابی هرگونه دسترسی یا ارتباط تجاری با دقت بیشتری انجام می‌شود.</li>
                                <li><strong>جانشینی و نظارت:</strong> هیئت‌مدیره باید هم از منافع شرکت حفاظت کند و هم تصمیم‌هایش را بر شواهد و روندهای روشن بنا کند؛ بحران نشان می‌دهد برنامهٔ جانشینی تا چه حد مهم است.</li>
                            </ul>

                            <h2>پیامدهای احتمالی برای انویدیا</h2>
                            <p>در کوتاه‌مدت، آزمون اصلی شرکت حفظ تداوم محصول، پشتیبانی از مشتریان و آرامش کارکنان و سرمایه‌گذاران است. در ادامه، انتخاب مدیرعامل دائمی، شفافیت دربارهٔ بررسی‌های داخلی و رعایت کنترل‌های صادراتی می‌تواند بر اعتماد بازار اثر بگذارد. خروج بنیان‌گذار مهم است، اما انویدیا تیم‌های مهندسی، زنجیرهٔ تأمین، نرم‌افزار و مشتریان گسترده‌ای دارد؛ بنابراین نباید سرنوشت عملیات شرکت را با فرد واحدی یکی دانست.</p>

                            <h2>درس‌هایی فراتر از یک مدیرعامل</h2>
                            <ul>
                                <li>موفقیت حرفه‌ای کسی را از پاسخ‌گویی اخلاقی معاف نمی‌کند.</li>
                                <li>اعتبار مدیران ارشد بخشی از سرمایهٔ شرکت است، اما سازوکارهای نظارتی باید از شخصیت افراد مستقل بماند.</li>
                                <li>تضاد منافع را باید زود، شفاف و با بررسی بی‌طرفانه مدیریت کرد؛ به‌ویژه وقتی رابطهٔ قدرت یا فناوری حساس مطرح است.</li>
                                <li>اتهام رسانه‌ای با واقعیت اثبات‌شده یکسان نیست؛ پوشش مسئولانه باید عدم‌قطعیت را آشکار کند.</li>
                                <li>هیچ شرکت بزرگی نباید آن‌قدر به یک بنیان‌گذار وابسته باشد که جانشینی‌اش به بحران بدل شود.</li>
                            </ul>

                            <h2>جمع‌بندی</h2>
                            <p>جنسن هوانگ در بیش از سه دهه، انویدیا را از شرکتی در بازار گرافیک رایانه‌ای به یکی از ستون‌های رایانش شتاب‌یافته و موج هوش مصنوعی رساند. اما بحران نوامبر ۲۰۲۶ یادآور شد که برتری فنی برای حفظ اعتماد کافی نیست: اخلاق حرفه‌ای، شفافیت، رعایت مقررات و حاکمیت شرکتی هم بخشی از رهبری‌اند. دربارهٔ اتهام‌های مطرح‌شده باید دقیق و محتاط بود؛ آنچه قطعی است کناره‌گیری اعلام‌شده و تصمیم هیئت‌مدیره برای نپذیرفتن بازگشت اوست.</p>

                            <h2>منابع و مطالعهٔ بیشتر</h2>
                            <ol class="article-sources">
                                <li><a href="https://nvidianews.nvidia.com/bios/jensen-huang" target="_blank" rel="noopener noreferrer">زندگی‌نامهٔ جنسن هوانگ — اتاق خبر انویدیا</a>؛ بنیان‌گذاری شرکت، تحصیلات و سوابق شغلی.</li>
                                <li><a href="https://nvidianews.nvidia.com/news/nvidia-announces-ceo-transition" target="_blank" rel="noopener noreferrer">اعلام رسمی تغییر مدیرعامل — انویدیا، ۱۲ نوامبر ۲۰۲۶</a>؛ استعفا و معرفی مدیرعامل موقت. متن اطلاعیه علت استعفا را مشخص نمی‌کند.</li>
                                <li><a href="https://www.nytimes.com/live/2026/11/12/business/nvidia-jensen-huang-resigns" target="_blank" rel="noopener noreferrer">پوشش زندهٔ نیویورک‌تایمز از کناره‌گیری هوانگ</a>؛ گزارش‌های روابط شخصی و نگرانی‌های امنیت ملی، با انتساب به منابع رسانه‌ای.</li>
                                <li><a href="https://apnews.com/article/nvidia-jensen-huang-china-national-security-chips-3026bcbe04ab57b844884382e583422a" target="_blank" rel="noopener noreferrer">آسوشیتدپرس، ۱۷ نوامبر ۲۰۲۶: هیئت‌مدیره با بازگشت هوانگ مخالفت کرد</a>.</li>
                                <li><a href="https://engineering.stanford.edu/about/history/heroes/2018-heroes/jensen-huang" target="_blank" rel="noopener noreferrer">زندگی‌نامهٔ هوانگ در دانشکدهٔ مهندسی استنفورد</a>.</li>
                            </ol>
                        </div>'''

FOOTER = r'''<footer class="article-end" id="post-footer">
                            <div class="article-end-meta">
                                <span class="article-end-date"><i class="fas fa-calendar-check fa-fw" aria-hidden="true"></i> منتشرشده در <time datetime="2026-11-18">۲۷ آبان ۱۴۰۵</time></span>
                                <span class="article-end-source"><i class="fas fa-file-lines fa-fw" aria-hidden="true"></i> بر پایهٔ ۵ منبع رسمی و خبری</span>
                            </div>
                            <nav class="article-end-links" aria-label="پیوندهای پایان مقاله">
                                <a href="/posts/"><i class="fas fa-list-ul fa-fw" aria-hidden="true"></i> بازگشت به همهٔ مقاله‌ها</a>
                                <span class="article-end-sep" aria-hidden="true">|</span>
                                <a href="/"><i class="fas fa-house fa-fw" aria-hidden="true"></i> صفحهٔ اصلی</a>
                            </nav>
                        </footer>'''

STYLE = r'''
            .post-page-fa .article-end { box-sizing:border-box; display:block; width:auto; height:auto; margin:2.4rem 0 0; padding:1.1rem 0 0; border-top:1px solid rgba(128,128,128,.28); font-size:.9rem; line-height:1.9; text-align:right; }
            .post-page-fa .article-end-meta { display:flex; flex-wrap:wrap; align-items:center; gap:.25rem 1.1rem; margin:0 0 .45rem; color:#5f5f66; }
            .post-page-fa .article-end-meta > span { display:inline-flex; align-items:center; gap:.35rem; }
            .post-page-fa .article-end-meta time { font-weight:600; }
            .post-page-fa .article-end-links { display:flex; flex-wrap:wrap; align-items:center; gap:.35rem .55rem; }
            .post-page-fa .article-end-links a { display:inline-flex; align-items:center; gap:.35rem; font-weight:600; color:#1d789b; text-decoration:none; text-underline-offset:.18em; }
            .post-page-fa .article-end-links a:hover, .post-page-fa .article-end-links a:focus-visible { color:#a41354; text-decoration:underline; }
            .post-page-fa .article-end-sep { color:#a9a9b3; }
            [theme=dark] .post-page-fa .article-end { border-top-color:rgba(255,255,255,.18); }
            [theme=dark] .post-page-fa .article-end-meta { color:#b7bbc5; }
            [theme=dark] .post-page-fa .article-end-links a { color:#6bc5e6; }
            [theme=dark] .post-page-fa .article-end-links a:hover, [theme=dark] .post-page-fa .article-end-links a:focus-visible { color:#fff; }
            .post-page-fa .article-hero { margin: 1.7rem 0 2rem; }
            .post-page-fa .article-hero img { display:block; width:100%; height:auto; max-height:38rem; object-fit:cover; border-radius:1rem; }
            .post-page-fa .article-hero figcaption { margin-top:.55rem; color:var(--text-secondary,#666); font-size:.88rem; line-height:1.7; }
            .post-page-fa .fact-note { margin:1.5rem 0; padding:1rem 1.2rem; border-right:4px solid #76b900; border-radius:.55rem; background:rgba(118,185,0,.09); line-height:1.95; }
            .post-page-fa .article-sources { padding-right:1.35rem; }
            .post-page-fa .article-sources li { margin:.65rem 0; overflow-wrap:anywhere; }
            [theme=dark] .post-page-fa .fact-note { background:rgba(118,185,0,.12); }
'''


FEED_ITEM = '''<item>
    <title>جنسن هوانگ و انویدیا؛ از انقلاب هوش مصنوعی تا بحران مدیریتی</title>
    <link>https://www.alirostami.com/posts/jensen-huang-nvidia/</link>
    <pubDate>Wed, 18 Nov 2026 12:00:00 &#43;0330</pubDate>
    <author>Ali Rostami</author>
    <guid>https://www.alirostami.com/posts/jensen-huang-nvidia/</guid>
    <description><![CDATA[روایت زندگی حرفه‌ای جنسن هوانگ و نقش او در رشد انویدیا و هوش مصنوعی؛ همراه با مرور مستند گزارش‌های نوامبر ۲۰۲۶ و تفکیک واقعیت از ادعا.]]></description>
</item>
'''


def update_feed(feed: Path) -> None:
    raw = feed.read_text(encoding="utf-8")
    raw = re.sub(
        r"<item>\s*<title>جنسن هوانگ و انویدیا.*?</item>\s*",
        "",
        raw,
        flags=re.DOTALL,
    )
    raw = re.sub(
        r"<lastBuildDate>.*?</lastBuildDate>",
        "<lastBuildDate>Wed, 18 Nov 2026 12:00:00 &#43;0330</lastBuildDate>",
        raw,
        count=1,
    )
    raw, count = re.subn(r"(?=<item>)", FEED_ITEM, raw, count=1)
    if count != 1:
        raise RuntimeError(f"{feed.relative_to(ROOT)} has no article insertion point")
    feed.write_text(raw, encoding="utf-8")


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    raw = raw.replace("هوش مصنوعی: یک رویکرد مدرن — ترجمهٔ فارسی (AIMA 4e) - علی رستمی", f"{TITLE} - علی رستمی", 1)
    raw = raw.replace('2026-10-20T12:00:00+03:30', PUBLISHED)
    raw = raw.replace(
        "https://www.alirostami.com/posts/aima-4e-persian/",
        "https://www.alirostami.com/posts/jensen-huang-nvidia/",
        1,
    )
    raw = raw.replace("هوش مصنوعی: یک رویکرد مدرن — ترجمهٔ فارسی (AIMA 4e)", TITLE)
    raw = raw.replace("ویرایش چهارم (AIMA 4th Edition)", "تحلیل فناوری و حاکمیت شرکتی")
    raw = raw.replace("<!-- Action Buttons Section -->", "")
    raw = re.sub(
        r'(<div class="post-actions-panel">.*?</div>\s*)(<div class="content" id="content">)',
        r'\2',
        raw,
        count=1,
        flags=re.DOTALL,
    )
    marker = '            .reading-feature-card {'
    style_end = raw.find('        </style>', raw.find(marker))
    if style_end == -1:
        raise RuntimeError("article shell has no expected style insertion point")
    raw = raw[:style_end] + STYLE + raw[style_end:]
    start = raw.find('<div class="content" id="content">')
    end = raw.find('\n\n                        <div class="post-footer" id="post-footer">', start)
    if start < 0 or end < 0:
        raise RuntimeError("article shell body markers are missing")
    raw = raw[:start] + BODY + raw[end:]
    raw = raw.replace('datetime="2026-10-20"', 'datetime="2026-11-18"', 1)
    raw = raw.replace('۲۰ مهر ۱۴۰۵ (2026-10-20)', f'{PERSIAN_DATE} (2026-11-18)', 1)
    raw = raw.replace('منتشر شده در ۲۰ مهر ۱۴۰۵', f'منتشرشده در {PERSIAN_DATE}', 1)
    raw, footer_count = re.subn(
        r'<div class="post-footer" id="post-footer">.*?(?=</article>)',
        FOOTER,
        raw,
        count=1,
        flags=re.DOTALL,
    )
    if footer_count != 1:
        raise RuntimeError("article shell footer block is missing")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(raw, encoding="utf-8")
    for feed in (ROOT / "posts" / "index.xml", ROOT / "index.xml"):
        update_feed(feed)
    write_sitemap()
    apply_site_postprocessors()
    print(f"generated {TARGET.relative_to(ROOT)} and refreshed its metadata, sitemap, and RSS entry")


if __name__ == "__main__":
    main()
