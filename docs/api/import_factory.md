# مستند API: import_factory

## مسیر پایه

`/imports`

## endpointها

### `POST /imports/validate`

هدف:

اعتبارسنجی مجموعه فایل‌های CSV الزامی بدون نوشتن در دیتابیس.

درخواست:

`multipart/form-data` با فیلد تکرارشونده `files`.

پاسخ:

```json
{
  "import_ready": true,
  "total_rows": 13,
  "files": [],
  "issues": []
}
```

خطاها:

- فایل missing
- ستون missing
- `Id` تکراری
- نوع داده نامعتبر
- FK target پیدا نشد
- warning blocker

یادداشت:

طبق تصمیم پروژه، warningها هم import readiness را block می‌کنند.

### `POST /imports/run`

هدف:

اعتبارسنجی مجموعه CSV و import آن فقط وقتی هیچ error یا warning وجود ندارد.

درخواست:

`multipart/form-data`:

- `files`: فایل‌های CSV تکرارشونده
- `source_name`: رشته اختیاری

پاسخ:

```json
{
  "import_batch_id": 1,
  "import_ready": true,
  "total_rows": 13,
  "imported_rows_by_file": {},
  "created_entity_counts": {},
  "issues": []
}
```

خطاها:

اگر validation شکست بخورد، هیچ ردیفی در دیتابیس درج نمی‌شود و پاسخ شامل issueها با `import_batch_id` برابر `0` است.

یادداشت:

این endpoint به database session تنظیم‌شده نیاز دارد.
