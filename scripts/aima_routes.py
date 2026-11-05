#!/usr/bin/env python3
"""Canonical AIMA 4e chapter routes and their historical Persian aliases.

The HTML filenames are deployment artifacts, so this table is the single source
of truth used by the reader generator and redirect generator.  Keep chapter
numbers aligned with the fourth-edition table of contents.
"""

from __future__ import annotations

# (historical Persian filename stem, canonical English filename stem)
AIMA_CHAPTER_ROUTE_MAP: tuple[tuple[str, str], ...] = (
    ("00-پیشگفتار", "00-preface"),
    ("01-فصل۱-مقدمه", "01-introduction"),
    ("02-فصل۲-عاملهای-هوشمند", "02-intelligent-agents"),
    ("03-فصل۳-حل-مسئله-با-جستجو", "03-solving-problems-by-searching"),
    ("04-فصل۴-جستجو-در-محیطهای-پیچیده", "04-search-in-complex-environments"),
    ("05-فصل۵-جستجوی-رقابتی-و-بازیها", "05-adversarial-search-and-games"),
    ("06-فصل۶-ارضای-قیود", "06-constraint-satisfaction-problems"),
    ("07-فصل۷-عاملهای-منطقی", "07-logical-agents"),
    ("08-فصل۸-منطق-مرتبه-اول", "08-first-order-logic"),
    ("09-فصل۹-استنتاج-منطق-مرتبه-اول", "09-inference-in-first-order-logic"),
    ("10-فصل۱۰-بازنمایی-دانش", "10-knowledge-representation"),
    ("11-فصل۱۱-برنامهریزی-خودکار", "11-automated-planning"),
    ("12-فصل۱۲-کمی-کردن-عدم-قطعیت", "12-quantifying-uncertainty"),
    ("13-فصل۱۳-استدلال-احتمالاتی", "13-probabilistic-reasoning"),
    ("14-فصل۱۴-استدلال-احتمالاتی-در-طول-زمان", "14-probabilistic-reasoning-over-time"),
    ("15-فصل۱۵-برنامهنویسی-احتمالاتی", "15-probabilistic-programming"),
    ("16-فصل۱۶-تصمیمگیری-ساده", "16-making-simple-decisions"),
    ("17-فصل۱۷-تصمیمگیری-پیچیده", "17-making-complex-decisions"),
    ("18-فصل۱۸-تصمیمگیری-چندعاملی", "18-multiagent-decision-making"),
    ("19-فصل۱۹-یادگیری-از-مثالها", "19-learning-from-examples"),
    ("20-فصل۲۰-یادگیری-مدلهای-احتمالاتی", "20-learning-probabilistic-models"),
    ("21-فصل۲۱-یادگیری-عمیق", "21-deep-learning"),
    ("22-فصل۲۲-یادگیری-تقویتی", "22-reinforcement-learning"),
    ("23-فصل۲۳-پردازش-زبان-طبیعی", "23-natural-language-processing"),
    ("24-فصل۲۴-یادگیری-عمیق-زبان-طبیعی", "24-deep-learning-for-natural-language-processing"),
    ("25-فصل۲۵-بینایی-رایانهای", "25-computer-vision"),
    ("26-فصل۲۶-رباتیک", "26-robotics"),
    ("27-فصل۲۷-فلسفه-اخلاق-ایمنی", "27-philosophy-ethics-and-safety-of-ai"),
    ("28-فصل۲۸-آینده-هوش-مصنوعی", "28-the-future-of-ai"),
)

AIMA_LEGACY_TO_CANONICAL = dict(AIMA_CHAPTER_ROUTE_MAP)
AIMA_CANONICAL_STEMS = tuple(canonical for _, canonical in AIMA_CHAPTER_ROUTE_MAP)


def malformed_legacy_stem(chapter_number: int) -> str:
    """Return the historical blank-title spelling reported for a chapter."""
    return f"{chapter_number:02d}- "
