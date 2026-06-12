# ماژول Risk Dashboard

## هدف

این ماژول برای TASK-015 ساخته شد و دو بخش اصلی دارد:

- Risk Rule Engine برای محاسبه ریسک rule-based در V1.
- داشبورد مدیریتی برای نمایش aggregateهای عملیاتی، کیفیت، مواد، ظرفیت، optimizer و ریسک.

در V1 هیچ AI/ML برای risk scoring استفاده نمی‌شود.

## Backend

مسیرهای اصلی:

- `GET /risk/settings`: خواندن تنظیمات global ریسک.
- `PUT /risk/settings`: به‌روزرسانی weightها و thresholdهای global.
- `POST /risk/calculate/{scenario_id}`: محاسبه مجدد ریسک برای Scenario.
- `GET /risk/scores?scenario_id=...`: خواندن scoreهای محاسبه‌شده.
- `GET /dashboard/manager?scenario_id=...`: داشبورد مدیریتی aggregate.

جدول‌های اضافه‌شده:

- `risk_rule_settings`
- `risk_scores`

## تنظیمات ریسک

تنظیمات فعلی global هستند و per-scenario ذخیره نمی‌شوند:

- `delay_risk_weight`
- `material_shortage_risk_weight`
- `machine_failure_risk_weight`
- `qc_ncr_risk_weight`
- `schedule_instability_weight`
- `low_threshold`
- `medium_threshold`
- `high_threshold`

ترتیب thresholdها اعتبارسنجی می‌شود و باید `low_threshold <= medium_threshold <= high_threshold` باشد.

## خروجی‌های ریسک

محاسبه ریسک سه سطح را پوشش می‌دهد:

- `Operation`
- `Order`
- `Scenario`

componentهای ریسک:

- delay
- material shortage
- machine failure
- QC/NCR
- schedule instability

فرمول فعلی heuristic و ساده است: componentها با weightهای تنظیم‌شده ضرب می‌شوند و میانگین محدودشده به ۱۰۰ به‌عنوان `total_score` ذخیره می‌شود.

## داشبورد مدیریتی

endpoint داشبورد این بخش‌ها را برمی‌گرداند:

- delivery
- delay
- production progress
- capacity
- bottleneck
- material shortage
- NCR/rework
- optimizer performance
- risk

داده‌های داشبورد از current state، NCR/rework، optimizer run و risk scoreهای ذخیره‌شده ساخته می‌شوند.

## Frontend

صفحه Dashboard به endpointهای جدید وصل شده است:

- انتخاب Scenario
- اجرای محاسبه ریسک برای Scenario انتخاب‌شده
- نمایش کارت‌های KPI عملیاتی
- نمایش bottleneckها
- نمایش scoreهای ریسک
- خواندن و ذخیره تنظیمات ریسک

## محدودیت‌های V1

- risk engine کاملاً rule-based است.
- risk settingها global هستند و هنوز per-scenario نیستند.
- فرمول‌ها heuristic هستند و نیاز به calibrate دامنه‌ای دارند.
- `purchase_requests` فعلاً `scenario_id` ندارد؛ بنابراین شمارش درخواست‌های خرید باز در داشبورد global است.
- داشبورد cost/financial KPI ندارد.
