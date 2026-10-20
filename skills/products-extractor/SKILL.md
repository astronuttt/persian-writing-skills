---
name: products-extractor
description: "Use when extracting official product specs, SKU, or images."
version: 1.1.0
metadata:
  hermes:
    tags: [ecommerce, scraper, product-data, specifications, official-brand, woocommerce]
    category: ecommerce
    related_skills: [brand-product-data, brand-image-acquisition, persian-humanizer]
---

# Products Extractor: پایپ‌لاین استخراج مشخصات رسمی محصول

این اسکیل وظیفه دارد با دریافت حداقل ورودی از کاربر (نام محصول، کد مدل، SKU یا لینک)، تمام مشخصات فنی، نام‌های رسمی، اقلام همراه و تصاویر باکیفیت را مستقیماً از **سایت رسمی شرکت سازنده** استخراج و به صورت یک ساختار تمیز و فکت‌محور تحویل دهد.

## قوانین تغییرناپذیر حقیقت‌سنجی (Ground Rules)
1. **اولویت قطعی با سایت رسمی برند است:** اطلاعات سایت سازنده بر تمام فروشگاه‌های متفرقه ارجحیت دارد.
2. **عدم اختراع مشخصات (Zero Hallucination):** اگر قابلیتی (مانند حذف نویز، ضدآب بودن یا شارژ بی‌سیم) در جدول مشخصات نیامده، **وجود ندارد**.
3. **تفکیک مدل از رنگ:** کدهای انتهای SKU که مربوط به رنگ هستند (مانند `-BK`، `-SL`، `GY`) جزو مدل اصلی نیستند و باید تفکیک شوند.
4. **بررسی اقلام همراه (Box Contents):** محتویات جعبه باید با جدول رسمی و عکس پکیج تطبیق داده شود.

---

## پایپ‌لاین ۳ مرحله‌ای اجرا (Execution Steps)

### گام اول: شناسایی برند و کد فنی
- استخراج برند، شماره مدل یا شناسه SKU از پیام کاربر.
- بررسی لیست برندهای کاتالوگ محلی: `greenlion`, `porodo`, `powerology`, `anker`, `jbl`, `kfsenior`.

### گام دوم: فراخوانی ابزار استخراج (سریع‌ترین مسیر)

#### ۱. اگر برند در کاتالوگ سیستم باشد (مسیر سریع):
از اسکریپت‌های بهینه‌سازی‌شده سیستم در `/root/brand-tools/` استفاده کنید:
```bash
# جستجو و دریافت مشخصات + تصویر رسمی
python3 /root/brand-tools/research.py <brand> <model-or-sku>

# یا خروجی مستقیم JSON با کاتالوگ اختصاصی:
python3 /root/brand-tools/brand_catalog.py <brand> product <model>
```
*نکته دور زدن کلودفلر:* برای سایت‌های گرین لاین، پورودو و پاورولوژی، کانتینر `flaresolverr` روی پورت `127.0.0.1:8191` به طور خودکار چالش Cloudflare را حل می‌کند.

#### ۲. اگر برند خارج از کاتالوگ سیستم باشد (تحقیق وب):
1. جستجو با کوئری دقیق:
   ```python
   web_search(query='<Brand> <Model or SKU> official specifications specifications sheet')
   ```
2. استخراج صفحه رسمی با `web_extract(urls=[official_url])`.
3. اگر صفحه رسمی خطای 403 یا چالش کلودفلر داد:
   ```bash
   python3 /root/brand-tools/brand_catalog.py flare "<url>" --out /tmp/page.html
   ```
4. مسیرهای جایگزین معتبر (در صورت در دسترس نبودن سایت سازنده):
   - صفحه رسمی محصول در آمازون (Amazon Brand Store)
   - صفحات مشخصات فنی داخلی (دیجی‌کالا یا کاتالوگ‌های معتبر واردکننده) فقط برای فکت‌های خام.

---

## فرمت خروجی استاندارد (Output Schema)

خروجی این اسکیل باید یک ساختار تفکیک‌شده باشد که مستقیماً خوراک اسکیل `copywriter` شود:

```json
{
  "brand_en": "Green Lion",
  "brand_fa": "گرین لاین",
  "model": "GNMGF5STND",
  "sku": "GNMGF5STNDGY",
  "official_title_en": "Green Lion MagFold 5-in-1 Wireless Charging Stand",
  "suggested_title_fa": "پایه شارژ بی‌سیم گرین لاین مدل MagFold توان ۱۵ وات",
  "source_url": "https://www.greenlion.net/shop/...",
  "category_suggestion": "شارژر بی‌سیم / هولدر",
  "category_id": 3726,
  "specs": {
    "توان خروجی کلی": "15W",
    "تعداد درگاه خروجی": "3 پد بی‌سیم + 1 خروجی USB-A",
    "فناوری شارژ": "MagSafe / Qi",
    "جنس بدنه": "آلیاژ آلومینیوم و ABS",
    "وزن": "230 گرم",
    "درگاه ورودی": "USB-C (9V/2A)"
  },
  "box_contents": [
    "پایه شارژر MagFold",
    "کابل USB-C به USB-C یک متری",
    "دفترچه راهنما"
  ],
  "verified_limits": [
    "فاقد آداپتور داخل جعبه (نیاز به تهیه آداپتور حداقل ۲۰ وات دارد)"
  ],
  "official_images": [
    "/tmp/greenlion_magfold_01.jpg",
    "/tmp/greenlion_magfold_02.jpg"
  ]
}
```

---

## راهنمای دسته‌بندی‌های پرتکرار (WC Category Mapping)
- شارژر فندکی: `3724`
- هدفون و هدست: `3715`
- هندزفری و ایرپاد: `2265`
- شارژر دیواری / آداپتور: `3726`
- کابل USB-C: `2268`
- کابل AUX: `2272`
- کابل و تبدیل: `2267`
- هولدر و پایه ماشینی: `5222`
- پایه خنک‌کننده و استند لپ‌تاپ: `3719`
- پاوربانک: `2256`
- اسپیکر: `3727`
- اینورتر: `3725`
- گلس و محافظ صفحه: `5259`
- محافظ لنز: `5278`
