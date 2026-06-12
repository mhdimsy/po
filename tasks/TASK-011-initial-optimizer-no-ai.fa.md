# TASK-011: Optimizer اولیه بدون AI

## هدف

Optimizer اولیه بدون AI بساز.

## محدوده

- تولید schedule با heuristic
- constraint مربوط به precedence
- availability ماشین
- eligibility/availability اپراتور
- availability مواد
- calendar handling ساده
- priority سفارش
- due date
- schedule پیشنهادی
- accept کردن schedule

## صراحتاً بدون AI

- بدون ML training
- بدون AI recommendation
- بدون prediction model

## بدون cost model

Cost در V1 خاموش است.

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/optimizer.md`

## معیار پذیرش

- endpoint اجرای optimizer، schedule پیشنهادی برگرداند.
- schedule پیشنهادی شامل score و changed operation count باشد.
- schedule قابل accept شدن باشد.
