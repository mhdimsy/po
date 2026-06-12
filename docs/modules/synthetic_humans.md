# ماژول: synthetic_humans

## هدف

تولید نیروی انسانی synthetic برای شبیه‌سازی تولید کارخانه، شامل اپراتورها، مهارت‌ها، شیفت‌ها، قوانین شیفت برای WorkCenter و availability اپراتورها.

## محدوده

- تولید تعداد قابل تنظیم اپراتور؛ مقدار پیش‌فرض ۵۰۰ نفر است.
- پیشنهاد توزیع اپراتورها بر اساس WorkCenter و تعداد Machineهای واردشده.
- تولید سطح مهارت تصادفی در بازه ۱ تا ۵.
- پشتیبانی از نسبت قابل تنظیم multi-skill.
- تعریف شیفت‌های پیش‌فرض و ruleهای قابل تنظیم برای WorkCenter.
- ذخیره داده‌های تولیدشده در دیتابیس.

## موجودیت‌ها

- `Operator`
- `Skill`
- `OperatorSkill`
- `Shift`
- `WorkCenterShiftRule`
- `OperatorAvailability`

## سرویس‌ها

- `generate_operators`
- `ensure_default_shifts`
- `ensure_skills`
- `ensure_shift_rules`
- `propose_distribution`

## endpointهای API

- `POST /synthetic/operators/generate`
- `GET /synthetic/operators`
- `GET /synthetic/skills`
- `GET /synthetic/shifts`

## eventها

در TASK-006 event تولید نمی‌شود.

## جدول‌های current state

داده‌های تولیدشده در جدول‌های زیر ذخیره می‌شوند:

- `operators`
- `skills`
- `operator_skills`
- `shifts`
- `work_center_shift_rules`
- `operator_availability`

## وابستگی‌ها

- جدول‌های master data برای `WorkCenter`
- جدول‌های master data برای `Machine`
- جدول‌های master data برای `Process`
- جدول `machine_processes` برای پیشنهاد skillهای مرتبط با WorkCenter

## قوانین validation

- `count` باید بین ۱ و ۱۰۰۰۰ باشد.
- `multi_skill_ratio` باید بین ۰ و ۱ باشد.
- هر skill level با مقدار تصادفی ۱ تا ۵ ساخته می‌شود.
- اگر WorkCenter وجود نداشته باشد، generator همه اپراتورها را در bucket عمومی `General` قرار می‌دهد.

## محدودیت‌های فعلی

- assignment logic مربوط به optimizer پیاده‌سازی نشده است.
- مدل fatigue پیاده‌سازی نشده است.
- auth/user واقعی وجود ندارد.
- تولید اپراتور فعلاً داده‌های قبلی را پاک نمی‌کند و batch جداگانه برای generation ندارد.
- اتصال و insert واقعی روی SQL Server در این محیط تست نشده است.

## تست‌ها

- `python3 -m compileall backend/app` موفق بود.
- routeهای `/synthetic/*` در FastAPI ثبت شدند.
- generator روی SQLite in-memory با داده master تست شد.
- تولید ۲۰ اپراتور تستی، ۳۳ ردیف `OperatorSkill` و توزیع ۱۳/۷ بر اساس تعداد machineها ایجاد کرد.
- سطح مهارت‌های تولیدشده در تست بین ۱ و ۵ بود.
