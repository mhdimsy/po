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
- آیا هنگام fork باید current state مربوط به base snapshot فوراً برای Scenario جدید materialize شود یا در TASK replay انجام شود؟
- آیا `base_snapshot_id` در جدول `scenarios` باید foreign key واقعی به `snapshots.id` باشد یا nullable/reference سبک فعلی کافی است؟
- آیا step باید در حالت `Paused` هم مجاز باشد یا فقط در حالت `Running`؟
- آیا transition ساده operation باید فقط یک operation را در هر step پردازش کند یا همه operationهای قابل پردازش همان دقیقه را؟
- آیا accept کردن schedule باید resource reservation جداگانه بسازد یا در TASKهای بعدی با جدول reservation انجام شود؟
- آیا status مربوط به operation بعد از `OperationScheduled` باید همچنان `Queued` بماند یا status جداگانه `Scheduled/Planned` به domain model اضافه شود؟
- آیا manual move معتبر باید در backend به‌صورت event جدید مثل `ScheduleManuallyChanged` ثبت شود؟
- آیا validation drag/drop باید endpoint رسمی backend داشته باشد تا frontend و API رفتار یکسان داشته باشند؟
- آیا NCR approval باید sequential باشد یا هر سه step بتوانند مستقل و موازی تصمیم بگیرند؟
- برای dependent operationها، source of truth وابستگی باید routing sequence باشد یا current operation graph جداگانه لازم است؟
- آیا تنظیمات ریسک باید global بمانند یا برای هر Scenario نسخه جداگانه داشته باشند؟
- آستانه‌های Low/Medium/High برای ریسک باید با چه scale و policy نهایی تأیید شوند؟
- آیا `purchase_requests` باید در schema آینده `scenario_id` داشته باشد تا داشبورد مواد کاملاً scenario-scoped شود؟
