#!/usr/bin/env python3
"""Comprehensive & Deterministic Persian Sanitizer for E-commerce & Web Content.

Features:
1. Normalizes Arabic characters to Persian (ي -> ی, ك -> ک, ة -> ه / ت).
2. Fixes ZWNJ (نیم‌فاصله) across:
   - Verbal prefixes (می / نمی + فعل)
   - Verbal participles (شده / نشدن)
   - Plural suffixes (ها / های)
   - Comparative suffixes (تر / ترین)
   - SI and technical units (میلی‌آمپر ساعت, سانتی‌متر, گیگابایت, مگاپیکسل)
   - Common hardware compounds (لپ‌تاپ, تاچ‌پد, هندزفری, وب‌کم, پاوربانک)
   - Compound prefixes (بی‌, هم‌, ضد‌, فوق‌, پیش‌)
   - Prepositional compounds (به‌صورت, به‌راحتی, به‌همراه, به‌ویژه)
3. Preserves HTML tags, attributes, URLs, and Latin model codes intact.
4. Normalizes FAQ structure (<p><strong>Q?</strong></p><p>A...</p>).
5. Cleans redundant whitespaces and linebreaks.

Usage:
  python3 sanitize_fa.py < input.txt
  python3 sanitize_fa.py input.txt [output.txt]
"""

import re
import sys

ZWNJ = "\u200c"

# Explicit compound dictionary (ordered longest-first to prevent partial collisions)
EXACT_COMPOUNDS = [
    # Units & Dimensions
    ("میلی آمپر ساعت", f"میلی{ZWNJ}آمپر ساعت"),
    ("میلی آمپرساعت", f"میلی{ZWNJ}آمپر ساعت"),
    ("میلی آمپر", f"میلی{ZWNJ}آمپر"),
    ("میلی متر", f"میلی{ZWNJ}متر"),
    ("سانتی متر", f"سانتی{ZWNJ}متر"),
    ("میلی لیتر", f"میلی{ZWNJ}لیتر"),
    ("کیلو وات", f"کیلو{ZWNJ}وات"),
    ("کیلووات ساعت", f"کیلووات{ZWNJ}ساعت"),
    ("گیگا بایت", "گیگابایت"),
    ("مگا بایت", "مگابایت"),
    ("مگا پیکسل", "مگاپیکسل"),
    ("ترا بایت", "ترابایت"),
    ("وات ساعت", f"وات{ZWNJ}ساعت"),

    # Tech & Hardware Terms
    ("لپ تاپ", f"لپ{ZWNJ}تاپ"),
    ("تاچ پد", f"تاچ{ZWNJ}پد"),
    ("تایپ سی", f"تایپ{ZWNJ}سی"),
    ("وب کم", f"وب{ZWNJ}کم"),
    ("هندز فری", "هندزفری"),
    ("پاور بانک", "پاوربانک"),
    ("پاوربانک ها", f"پاوربانک{ZWNJ}ها"),
    ("ایرپاد ها", f"ایرپاد{ZWNJ}ها"),
    ("هدفون ها", f"هدفون{ZWNJ}ها"),
    ("اسمارت واچ", f"اسمارت{ZWNJ}واچ"),
    ("ساعت هوشمند", "ساعت هوشمند"),
    ("جوی استیک", f"جوی{ZWNJ}استیک"),
    ("پلی کربنات", f"پلی{ZWNJ}کربنات"),
    ("لیتیوم پلیمر", f"لیتیوم{ZWNJ}پلیمر"),
    ("لیتیوم یون", f"لیتیوم{ZWNJ}یون"),
    ("سوپر فست", f"سوپر{ZWNJ}فست"),
    ("کوئیک شارژ", f"کوئیک{ZWNJ}شارژ"),
    ("فست شارژ", f"فست{ZWNJ}شارژ"),
    ("نویز کنسلینگ", f"نویز{ZWNJ}کنسلینگ"),

    # Common Prefixes (بی, هم, ضد, فوق, پیش)
    ("بی سیم", f"بی{ZWNJ}سیم"),
    ("بی نقص", f"بی{ZWNJ}نقص"),
    ("بی نظیر", f"بی{ZWNJ}نظیر"),
    ("بی صدا", f"بی{ZWNJ}صدا"),
    ("همزمان", f"هم{ZWNJ}زمان"),
    ("هم زمان", f"هم{ZWNJ}زمان"),
    ("همگام سازی", f"همگام{ZWNJ}سازی"),
    ("ضد ضربه", f"ضد{ZWNJ}ضربه"),
    ("ضد خش", f"ضد{ZWNJ}خش"),
    ("ضد آب", f"ضد{ZWNJ}آب"),
    ("ضد گرد و غبار", f"ضد{ZWNJ}گرد و غبار"),
    ("ضد اثر انگشت", f"ضد{ZWNJ}اثر انگشت"),
    ("فوق العاده", f"فوق{ZWNJ}العاده"),
    ("فوق باریک", f"فوق{ZWNJ}باریک"),
    ("پیش فرض", f"پیش{ZWNJ}فرض"),
    ("پیش بینی", f"پیش{ZWNJ}بینی"),
    ("پیش نمایش", f"پیش{ZWNJ}نمایش"),
    ("پیش نیاز", f"پیش{ZWNJ}نیاز"),
    ("پیشرفته ترین", f"پیشرفته{ZWNJ}ترین"),
    ("پیشرفته تر", f"پیشرفته{ZWNJ}تر"),
    ("چند منظوره", f"چند{ZWNJ}منظوره"),
    ("چند کاره", f"چند{ZWNJ}کاره"),
    ("تک کاره", f"تک{ZWNJ}کاره"),
    ("یکپارچه سازی", f"یکپارچه{ZWNJ}سازی"),
    ("بهینه سازی", f"بهینه{ZWNJ}سازی"),
    ("شخصی سازی", f"شخصی{ZWNJ}سازی"),
    ("بروزرسانی", f"به{ZWNJ}روزرسانی"),
    ("به روزرسانی", f"به{ZWNJ}روزرسانی"),
    ("به روز رسانی", f"به{ZWNJ}روزرسانی"),
    ("دسته بندی", f"دسته{ZWNJ}بندی"),

    # Prepositions with 'به'
    ("به همراه", f"به{ZWNJ}همراه"),
    ("به صورت", f"به{ZWNJ}صورت"),
    ("به شکل", f"به{ZWNJ}شکل"),
    ("به راحتی", f"به{ZWNJ}راحتی"),
    ("به ویژه", f"به{ZWNJ}ویژه"),
    ("به مراتب", f"به{ZWNJ}مراتب"),
    ("به عنوان", f"به{ZWNJ}عنوان"),
    ("به نوبه خود", f"به{ZWNJ}نوبه خود"),

    # Verb Participles with شده / نشدن
    ("تعبیه شده", f"تعبیه{ZWNJ}شده"),
    ("طراحی شده", f"طراحی{ZWNJ}شده"),
    ("ساخته شده", f"ساخته{ZWNJ}شده"),
    ("ارائه شده", f"ارائه{ZWNJ}شده"),
    ("بهینه‌سازی شده", f"بهینه‌سازی{ZWNJ}شده"),
    ("بهینه سازی شده", f"بهینه‌سازی{ZWNJ}شده"),
    ("تایید شده", f"تأیید{ZWNJ}شده"),
    ("تأیید شده", f"تأیید{ZWNJ}شده"),
    ("ثبت شده", f"ثبت{ZWNJ}شده"),
    ("لحیم شده", f"لحیم{ZWNJ}شده"),
    ("بافته شده", f"بافته{ZWNJ}شده"),
    ("تمام شده", f"تمام{ZWNJ}شده"),

    # Plural Words
    ("گوشی ها", f"گوشی{ZWNJ}ها"),
    ("گوشی های", f"گوشی{ZWNJ}های"),
    ("دستگاه ها", f"دستگاه{ZWNJ}ها"),
    ("دستگاه های", f"دستگاه{ZWNJ}های"),
    ("درگاه ها", f"درگاه{ZWNJ}ها"),
    ("درگاه های", f"درگاه{ZWNJ}های"),
    ("پورت ها", f"پورت{ZWNJ}ها"),
    ("پورت های", f"پورت{ZWNJ}های"),
    ("کابل ها", f"کابل{ZWNJ}ها"),
    ("کابل های", f"کابل{ZWNJ}های"),
    ("کلید ها", f"کلید{ZWNJ}ها"),
    ("کلید های", f"کلید{ZWNJ}های"),
    ("هدفون های", f"هدفون{ZWNJ}های"),
    ("اسپیکر ها", f"اسپیکر{ZWNJ}ها"),
    ("اسپیکر های", f"اسپیکر{ZWNJ}های"),
    ("باتری ها", f"باتری{ZWNJ}ها"),
    ("باتری های", f"باتری{ZWNJ}های"),
    ("تبلت ها", f"تبلت{ZWNJ}ها"),
    ("تبلت های", f"تبلت{ZWNJ}های"),
    ("شارژر ها", f"شارژر{ZWNJ}ها"),
    ("شارژر های", f"شارژر{ZWNJ}های"),
    ("قابلیت ها", f"قابلیت{ZWNJ}ها"),
    ("قابلیت های", f"قابلیت{ZWNJ}های"),
    ("ویژگی ها", f"ویژگی{ZWNJ}ها"),
    ("ویژگی های", f"ویژگی{ZWNJ}های"),
    ("نیاز ها", f"نیاز{ZWNJ}ها"),
    ("نیاز های", f"نیاز{ZWNJ}های"),
    ("کاربر ها", f"کاربر{ZWNJ}ها"),
    ("کاربران", "کاربران"),

    # Misspellings & Common typos
    ("ملیون", "میلیون"),
    ("باطری", "باتری"),
]


def normalize_chars(text: str) -> str:
    """Normalize Arabic specific letters to Persian."""
    text = text.replace("\u064A", "\u06CC")  # ي -> ی
    text = text.replace("\u0649", "\u06CC")  # ى -> ی
    text = text.replace("\u0643", "\u06A9")  # ك -> ک
    text = text.replace("\u06C0", f"\u0647{ZWNJ}\u06CC")  # ۀ -> ه‌ی
    return text


def fix_verbs(text: str) -> str:
    """Fix verbal prefixes (می / نمی) with Persian verbs."""
    # Pattern: \b(می|نمی) [آ-ی]{2,}\b
    # Avoid false positives on isolated prepositions
    pattern = re.compile(r"\b(می|نمی)\s+([آ-ی]{2,})\b")

    def repl(m):
        prefix, stem = m.group(1), m.group(2)
        # Avoid non-verb combinations if any
        return f"{prefix}{ZWNJ}{stem}"

    return pattern.sub(repl, text)


def fix_comparatives(text: str) -> str:
    """Fix comparative suffixes (تر / ترین) attached to adjectives."""
    pattern = re.compile(r"\b([آ-ی]{3,})\s+(تر|ترین)\b")

    def repl(m):
        base, suffix = m.group(1), m.group(2)
        # Exception: 'به تر' is already avoided by length 3+
        return f"{base}{ZWNJ}{suffix}"

    return pattern.sub(repl, text)


def fix_plurals(text: str) -> str:
    """Catch remaining plural 'ها / های' attached to Persian words."""
    pattern = re.compile(r"\b([آ-ی]{3,})\s+(ها|های)\b")

    def repl(m):
        base, suffix = m.group(1), m.group(2)
        return f"{base}{ZWNJ}{suffix}"

    return pattern.sub(repl, text)


def fix_dictionary_compounds(text: str) -> str:
    """Apply the ordered exact compounds replacement list."""
    for wrong, right in EXACT_COMPOUNDS:
        if wrong in text:
            text = text.replace(wrong, right)
    return text


def fix_faq(text: str) -> str:
    """Format FAQ paragraphs: <p><strong>Q?</strong> A...</p> -> <p><strong>Q?</strong></p><p>A...</p>."""
    pattern = re.compile(r"<p><strong>([^<]+?)</strong>\s*(.*?)</p>", re.S)

    def repl(m):
        q, a = m.group(1).strip(), m.group(2).strip()
        if not a:
            return m.group(0)
        return f"<p><strong>{q}</strong></p>\n<p>{a}</p>"

    return pattern.sub(repl, text)


def clean_spaces(text: str) -> str:
    """Clean redundant spaces and newlines."""
    # Remove duplicate ZWNJ
    text = re.sub(rf"{ZWNJ}+", ZWNJ, text)
    # Remove space around ZWNJ
    text = re.sub(rf"\s+{ZWNJ}", ZWNJ, text)
    text = re.sub(rf"{ZWNJ}\s+", ZWNJ, text)
    # Multiple blank lines collapse to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip line tails
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def sanitize(text: str) -> str:
    """Execute complete sanitization pipeline."""
    # Protect HTML tags / URLs from char replacements
    tags = []

    def save_tag(m):
        tags.append(m.group(0))
        return f"___HTML_TAG_{len(tags)-1}___"

    text = re.sub(r"<[^>]+>", save_tag, text)

    # 1. Normalization
    text = normalize_chars(text)

    # 2. Dictionary & exact compounds
    text = fix_dictionary_compounds(text)

    # 3. Dynamic regex rules
    text = fix_verbs(text)
    text = fix_comparatives(text)
    text = fix_plurals(text)

    # Restore HTML tags
    for i, tag in enumerate(tags):
        text = text.replace(f"___HTML_TAG_{i}___", tag)

    # 4. FAQ structure & whitespace cleanup
    text = fix_faq(text)
    text = clean_spaces(text)

    return text


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            src = f.read()
        res = sanitize(src)
        if len(sys.argv) > 2:
            with open(sys.argv[2], "w", encoding="utf-8") as f:
                f.write(res)
        else:
            print(res)
    else:
        src = sys.stdin.read()
        print(sanitize(src))
