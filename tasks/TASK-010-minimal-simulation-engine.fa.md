# TASK-010: Simulation Engine حداقلی

## هدف

simulation engine حداقلی را بساز.

## محدوده

- واحد زمان داخلی: دقیقه
- start / pause / resume / step
- core ساده event-based
- tick فقط برای refresh وضعیت
- statusهای operation:
  - Queued
  - WaitingMaterial
  - WaitingMachine
  - WaitingOperator
  - Setup
  - Running
  - Finished
  - Blocked

## پیاده‌سازی نکن

- QC/NCR کامل
- optimizer کامل
- Gantt UI
- AI/ML

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/simulation.md`

## معیار پذیرش

- بتوان زمان simulation را step کرد.
- تغییر وضعیت‌ها event بسازند.
- جدول‌های current state به‌روزرسانی شوند.
