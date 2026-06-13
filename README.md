# نمونه Digital Twin

نمونه محلی Digital Twin برای شبیه‌سازی تولید کارخانه.

## پیش‌نیازها

- Python 3.11 یا بالاتر
- Node.js 20 یا بالاتر
- npm
- SQL Server در صورت نیاز به persistence واقعی
- ODBC Driver 18 for SQL Server برای اتصال `pyodbc`

اگر روی Ubuntu/Debian ساخت virtualenv خطا داد، این بسته را نصب کنید:

```bash
sudo apt install python3-venv
```

## راه‌اندازی Backend

از ریشه پروژه:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

فایل `backend/.env` را باز کنید و مقدار `SQLSERVER_CONNECTION_STRING` را با SQL Server محلی خود تنظیم کنید.

نمونه:

```text
SQLSERVER_CONNECTION_STRING=mssql+pyodbc://user:password@localhost:1433/DigitalTwinPrototype?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

اگر username یا password کاراکتر خاص دارد، باید URL-encode شود. مهم‌ترین موردها:

```text
@  ->  %40
#  ->  %23
%  ->  %25
/  ->  %2F
:  ->  %3A
?  ->  %3F
&  ->  %26
+  ->  %2B
```

مثلاً اگر پسورد `Abc@123` باشد:

```text
SQLSERVER_CONNECTION_STRING=mssql+pyodbc://user:Abc%40123@localhost:1433/DigitalTwinPrototype?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

اجرای API:

```bash
uvicorn app.main:app --reload
```

آدرس backend:

```text
http://127.0.0.1:8000
```

endpointهای سلامت:

```text
GET http://127.0.0.1:8000/health
GET http://127.0.0.1:8000/health/db
```

بعد از تنظیم SQL Server، جدول‌های دیتابیس را با این endpoint بسازید:

```text
POST http://127.0.0.1:8000/master-data/schema/create
```

اگر `python3 -m venv` در سیستم شما در دسترس نبود، می‌توانید موقتاً dependencyها را در مسیر جدا نصب کنید:

```bash
cd backend
python3 -m pip install --target /tmp/jobshop6-pydeps -r requirements.txt
PYTHONPATH=/tmp/jobshop6-pydeps:. uvicorn app.main:app --reload
```

این روش فقط fallback توسعه محلی است؛ برای کار معمولی همان `.venv` بهتر است.

## راه‌اندازی Frontend

در ترمینال جداگانه، از ریشه پروژه:

```bash
cd frontend
npm install
npm run dev
```

آدرس frontend:

```text
http://127.0.0.1:5173
```

فرانت‌اند درخواست‌های `/api/*` را از طریق Vite proxy به backend روی `http://127.0.0.1:8000` می‌فرستد. بنابراین برای کارکرد کامل UI باید backend هم در حال اجرا باشد.

برای build production:

```bash
cd frontend
npm run build
```

## ترتیب پیشنهادی اجرای dev

1. SQL Server را آماده کنید و connection string را در `backend/.env` بگذارید.
2. backend را اجرا کنید.
3. یک بار `POST /master-data/schema/create` را بزنید تا جدول‌ها ساخته شوند.
4. frontend را اجرا کنید.
5. در مرورگر `http://127.0.0.1:5173` را باز کنید.

## دیتای موردنیاز

برای شروع باید Master Data تولید را به‌صورت CSV بدهید. این ۱۱ فایل لازم هستند:

```text
process_types.csv
processes.csv
work_centers.csv
machines.csv
machine_processes.csv
bom.csv
bom_parts.csv
routings.csv
routing_operations.csv
orders.csv
order_parts.csv
```

حداقل ستون‌های هر فایل:

```text
process_types.csv:
Id,Title

processes.csv:
Id,Title,ProcessType_Id

work_centers.csv:
Id,Code,Title

machines.csv:
Id,Title,Barcode,WorkCenter_Id,Status

machine_processes.csv:
Id,Machine_Id,Process_Id,IsPrimary,SetupFactor,ProcessingFactor

bom.csv:
Id,Title,Code,SAPCode,UsageType_Id,PartsGroup_Id,PC

bom_parts.csv:
Id,BOMParent_Id,BOMChild_Id,Quantity,Unit

routings.csv:
Id,BOM_Id,Title,IsActive

routing_operations.csv:
Id,Routine_Id,Process_Id,OperationSequence,OperationDescription,SetupDuration,OperationDuration,AssemblyDuration,RequiresQC,IsInterruptible,CanOutsource,OutsourceLeadTimeMinutes

orders.csv:
Id,Code,Routine_Id,BOM_Id,ProductCode,CustomerName,OrderDate,EarliestStartDate,CustomerRequestedDate,CommittedDeliveryDate,InternalProductionDueDate,MaterialRequiredDate,ShipmentDate,GoodReciept

order_parts.csv:
Id,ParentOrder_Id,ChildOrder_Id,AssignmentStatus_Id,AssignmentStatusTitle
```

ترتیب منطقی آماده‌سازی داده:

1. Process Typeها، Processها و WorkCenterها
2. Machineها و قابلیت هر ماشین در `machine_processes.csv`
3. BOM و ساختار قطعات در `bom_parts.csv`
4. Routing و عملیات تولید در `routing_operations.csv`
5. Orderها و رابطه orderها در `order_parts.csv`

برای تست سریع، یک دیتاست کوچک هم کافی است: ۲ process، ۱ work center، ۲ machine، ۲ BOM item، ۱ routing با ۲ operation و ۱ order.

نکته: در نسخه فعلی، اگر validation حتی warning بدهد، import انجام نمی‌شود. مثلاً هر machine بهتر است حداقل یک capability در `machine_processes.csv` داشته باشد.

بعد از import موفق، داده‌های synthetic مثل operator، skill، shift، inventory، supplier و purchase request از داخل API/UI ساخته می‌شوند.

## ورود CSV

فقط اعتبارسنجی:

```text
POST /imports/validate
```

اجرای import واقعی:

```text
POST /imports/run
```

هر دو endpoint فایل‌ها را به‌صورت multipart و با فیلد `files` دریافت می‌کنند. اگر validation هر error یا warning برگرداند، import انجام نمی‌شود.

## Import از پوشه محلی

برای دیتاست بزرگ‌تر، به‌جای upload از UI می‌توانید فایل‌ها را مستقیم در این پوشه بگذارید:

```text
backend/import_data/
```

نام فایل‌ها باید دقیقاً همان نام‌های موردنیاز باشد:

```text
backend/import_data/process_types.csv
backend/import_data/processes.csv
backend/import_data/work_centers.csv
backend/import_data/machines.csv
backend/import_data/machine_processes.csv
backend/import_data/bom.csv
backend/import_data/bom_parts.csv
backend/import_data/routings.csv
backend/import_data/routing_operations.csv
backend/import_data/orders.csv
backend/import_data/order_parts.csv
```

بعد از قرار دادن فایل‌ها، این endpoint را صدا بزنید:

```bash
curl -X POST "http://127.0.0.1:8000/imports/reset-and-run-from-folder?source_name=folder-import"
```

رفتار این endpoint:

1. فایل‌های داخل `backend/import_data/` را می‌خواند.
2. اول validation کامل را اجرا می‌کند.
3. اگر حتی error یا warning وجود داشته باشد، دیتابیس reset نمی‌شود و import انجام نمی‌شود.
4. اگر validation موفق باشد، کل schema پروژه drop/create می‌شود.
5. فایل‌های جدید import می‌شوند.

این endpoint برای محیط dev است و نباید روی دیتابیس مهم یا production اجرا شود.

## endpointهای مهم توسعه

```text
GET  /health
GET  /health/db
POST /master-data/schema/create
POST /imports/validate
POST /imports/run
POST /imports/reset-and-run-from-folder
GET  /scenarios
GET  /events/current/operations
POST /optimizer/run
GET  /dashboard/manager
GET  /risk/settings
PUT  /risk/settings
POST /risk/calculate/{scenario_id}
```
