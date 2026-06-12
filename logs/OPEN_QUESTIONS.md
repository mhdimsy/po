# پرسش‌های باز

## 2026-06-12

- آیا validation مربوط به CSV باید گزارش‌های ناموفق را در `import_validation_issues` ذخیره کند، یا این جدول فقط بعد از وجود `ImportBatch` استفاده شود؟
- دقیقاً کدام فیلدهای BOM مشخص می‌کنند یک آیتم assembly است و باید warning مربوط به `BOM_WITHOUT_CHILD` بگیرد؟ پیاده‌سازی فعلی فقط وقتی title/code/PC نشانه‌های assembly-like داشته باشند warning می‌دهد.
- آیا تولید منابع انسانی synthetic باید هر بار یک generation batch مستقل داشته باشد تا بتوان داده‌های تولیدی هر اجرا را جداگانه حذف یا مقایسه کرد؟
- آیا `home_work_center_id` و `skills.process_id` باید در آینده به primary key داخلی جدول‌ها اشاره کنند یا source idهای واردشده از CSV برای prototype کافی هستند؟
- آیا `inventory_items.bom_id` باید در آینده به primary key داخلی جدول `boms` اشاره کند یا source id مربوط به BOM برای prototype کافی است؟
- آیا تولید موجودی/supplier باید batch مستقل داشته باشد تا بتوان چند preset را کنار هم مقایسه یا rollback کرد؟
- آیا `aggregate_id` در event store باید همیشه string بماند یا برای aggregateهای داخلی به integer تغییر کند؟
- آیا projectionهای current state باید synchronous در همان transaction append اجرا شوند یا در آینده event processor جدا داشته باشیم؟
