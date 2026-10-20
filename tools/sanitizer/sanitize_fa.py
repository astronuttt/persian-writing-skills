#!/usr/bin/env python3
"""Deterministic Persian sanitizer for Gemini description output.

Fixes: ZWNJ (نیم‌فاصله) in known compounds, FAQ format (question + answer
on separate paragraphs), whitespace. Run AFTER every Gemini output, BEFORE
showing/applying. Never touches values, prices, or model codes.

Usage: python3 sanitize_fa.py < input.txt   (or python3 sanitize_fa.py file)
"""
import re
import sys

# Ordered longest-first; space-separated wrong forms -> ZWNJ-correct forms
ZWNJ_FIXES = [
    ("میلی آمپر ساعت", "میلی‌آمپر ساعت"),
    ("میلی آمپر", "میلی‌آمپر"),
    ("میلی متر", "میلی‌متر"),
    ("سانتی متر", "سانتی‌متر"),
    ("میلی لیتر", "میلی‌لیتر"),
    ("تایپ سی", "تایپ‌سی"),
    ("نیم قلم", "نیم‌قلم"),
    ("می شود", "می‌شود"),
    ("می کند", "می‌کند"),
    ("می کنند", "می‌کنند"),
    ("می کنید", "می‌کنید"),
    ("می کنم", "می‌کنم"),
    ("می باشد", "می‌باشد"),
    ("می سازد", "می‌سازد"),
    ("می رسد", "می‌رسد"),
    ("می دهد", "می‌دهد"),
    ("می گوید", "می‌گوید"),
    ("می گیرید", "می‌گیرید"),
    ("بی سیم", "بی‌سیم"),
    ("همزمان", "هم‌زمان"),
    ("گوشی ها", "گوشی‌ها"),
    ("دستگاه ها", "دستگاه‌ها"),
    ("درگاه ها", "درگاه‌ها"),
    ("محصولات", None),  # placeholder no-op (keeps list ordering simple)
    ("باقی مانده", "باقی‌مانده"),
    ("پلی کربنات", "پلی‌کربنات"),
    ("لیتیوم پلیمر ", "لیتیوم پلیمری "),
    ("ملیون", "میلیون"),
    ("جوی استیک", "جوی‌استیک"),
]


def fix_zwnj(text: str) -> str:
    for wrong, right in ZWNJ_FIXES:
        if right is None:
            continue
        text = text.replace(wrong, right)
    return text


def fix_faq(text: str) -> str:
    """<p><strong>Q?</strong> A...</p>  ->  <p><strong>Q?</strong></p>\n<p>A...</p>"""
    # only when question and answer share a <p> (Sina's format: separate lines)
    pattern = re.compile(r"<p><strong>([^<]+?)</strong>\s*(.*?)</p>", re.S)
    def repl(m):
        q, a = m.group(1).strip(), m.group(2).strip()
        if not a:
            return m.group(0)
        return f"<p><strong>{q}</strong></p>\n<p>{a}</p>"
    return pattern.sub(repl, text)


def sanitize(text: str) -> str:
    text = fix_zwnj(text)
    text = fix_faq(text)
    # collapse 3+ newlines, strip trailing spaces on lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(l.rstrip() for l in text.splitlines()).strip()
    return text


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            src = f.read()
    else:
        src = sys.stdin.read()
    print(sanitize(src))
