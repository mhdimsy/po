# نمونه Digital Twin

نمونه محلی Digital Twin برای شبیه‌سازی تولید کارخانه.

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

endpointهای سلامت:

```text
GET http://localhost:8000/health
GET http://localhost:8000/health/db
```

بعد از تنظیم SQL Server، جدول‌های دیتابیس را با این endpoint بسازید:

```text
POST http://localhost:8000/master-data/schema/create
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

frontend روی این آدرس اجرا می‌شود:

```text
http://localhost:5173
```

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
