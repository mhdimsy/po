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
- Scenario و Snapshot روی SQL Server واقعی در این محیط تست نشده‌اند.
- fork فعلی state را به Scenario جدید کپی نمی‌کند و فقط رابطه parent/base snapshot را ثبت می‌کند.
- simulation engine روی SQL Server واقعی در این محیط تست نشده است.
- start conditionهای واقعی operation مثل material availability، machine capability، operator authorization، calendar و QC/NCR هنوز بررسی نمی‌شوند.
- optimizer روی SQL Server واقعی در این محیط تست نشده است.
- optimizer فعلی heuristic ساده است و constraint optimization کامل، machine capability، operator authorization، calendar واقعی و QC/NCR blocking را کامل اعمال نمی‌کند.
- UI اولیه با مرورگر واقعی یا تست end-to-end بررسی نشده است.
- UI در محیط dev برای جلوگیری از CORS از Vite proxy مسیر `/api` استفاده می‌کند.
- `gantt-task-react` با `--legacy-peer-deps` نصب شد، چون peer dependency آن React 18 است و پروژه React 19 دارد.
- validation مربوط به drag/drop فعلاً در frontend انجام می‌شود و backend endpoint مستقل برای validate/apply manual move وجود ندارد.
- Gantt/drag-drop با تست مرورگر end-to-end بررسی نشده است.
- QC/NCR/Approval روی SQL Server واقعی در این محیط تست نشده است.
- dependent operation blocking فعلاً operation مرتبط مستقیم را block می‌کند و graph کامل وابستگی‌ها هنوز وجود ندارد.
- Risk Rule Engine و Dashboard روی SQL Server واقعی در این محیط تست نشده‌اند.
- فرمول ریسک فعلی heuristic و rule-based است و هنوز با داده واقعی یا نظر domain expert calibrate نشده است.
- `purchase_requests` فعلاً `scenario_id` ندارد؛ بنابراین شمارش درخواست‌های خرید باز در داشبورد global است.
- Dashboard با مرورگر واقعی یا تست end-to-end بررسی نشده است.
