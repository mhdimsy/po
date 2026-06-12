# TASK-013: Gantt و Drag/Drop

## هدف

گانت چارت را با کتابخانه آماده React اضافه کن.

## محدوده

- نمایش operationها بر اساس machine
- نمایش current schedule
- نمایش suggested schedule
- drag/drop برای جابه‌جایی دستی
- validation سخت‌گیرانه قبل از apply
- conflictها apply را block کنند
- دلیل conflictها نمایش داده شود

## validation باید بررسی کند

- precedence عملیات‌ها
- availability/status ماشین
- eligibility/availability اپراتور
- availability مواد
- calendar
- blockerهای QC/Approval/NCR اگر موجود باشند

## پیاده‌سازی نکن

- Gantt سفارشی از صفر با Canvas/SVG
- پیشنهاد جایگزین با AI

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/gantt.md`

## معیار پذیرش

- Gantt schedule را render کند.
- drag/drop validation را صدا بزند.
- move نامعتبر با reasonها block شود.
