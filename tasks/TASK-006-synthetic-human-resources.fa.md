# TASK-006: منابع انسانی Synthetic

## هدف

generator نیروی انسانی synthetic را بساز.

## محدوده

- تولید تعداد قابل تنظیم اپراتور؛ مقدار پیش‌فرض ۵۰۰ نفر
- پیشنهاد توزیع بر اساس داده‌های WorkCenter/Machine
- سطح مهارت تصادفی ۱ تا ۵
- نسبت multi-skill قابل تنظیم
- شیفت‌های قابل تنظیم بر اساس WorkCenter
- ذخیره اپراتورها، skillها و shiftهای تولیدشده در دیتابیس

## موجودیت‌ها

- Operator
- Skill
- OperatorSkill
- Shift
- WorkCenterShiftRule
- OperatorAvailability

## پیاده‌سازی نکن

- منطق assignment مربوط به optimizer
- مدل fatigue
- auth/users
- UI مگر اینکه صریحاً درخواست شود

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/synthetic_humans.md`

## معیار پذیرش

- endpoint به‌صورت پیش‌فرض ۵۰۰ اپراتور تولید کند.
- نسبت multi-skill قابل تنظیم باشد.
- سطح skillها به‌صورت تصادفی در بازه ۱ تا ۵ باشد.
- داده‌های تولیدشده قابل list شدن باشند.
