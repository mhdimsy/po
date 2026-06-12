# مشکلات شناخته‌شده

## 2026-06-12

- اتصال واقعی به SQL Server تست نشد، چون connection string محلی برای SQL Server تنظیم نشده بود.
- `python3 -m venv` تا زمانی که `python3-venv`/`ensurepip` روی سیستم نصب نشود در دسترس نیست.
- `npm install` تعداد 3 vulnerability در dependencyها گزارش کرد: 2 مورد moderate و 1 مورد high. دستور `npm audit fix --force` اجرا نشد، چون ممکن است تغییرات breaking ایجاد کند.
- دستور health مبتنی بر FastAPI `TestClient` در این محیط hang شد؛ برای verification از تست مستقیم تابع‌ها استفاده شد.
- دستور `curl` جداگانه نتوانست به dev server مربوط به uvicorn وصل شود، با اینکه session سرور startup روی port 8000 را گزارش کرده بود.
- generator منابع انسانی synthetic فعلاً generation batch جداگانه ندارد و داده‌های قبلی را قبل از تولید جدید پاک نمی‌کند.
- insert واقعی منابع انسانی synthetic روی SQL Server در این محیط تست نشده است.
- generator موجودی و supplier synthetic فعلاً generation batch جداگانه ندارد و داده‌های قبلی را قبل از تولید جدید پاک نمی‌کند.
- insert واقعی موجودی و supplier synthetic روی SQL Server در این محیط تست نشده است.
- event store و current state روی SQL Server واقعی در این محیط تست نشده‌اند.
- projection فعلی current state ساده است و همه event typeهای آینده را پوشش نمی‌دهد.
