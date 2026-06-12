# ماژول: gantt

## هدف

نمایش schedule پیشنهادی optimizer در قالب Gantt آماده React و پشتیبانی از drag/drop دستی همراه با validation سخت‌گیرانه قبل از اعمال تغییر.

## محدوده

- استفاده از کتابخانه آماده `gantt-task-react`.
- نمایش operationها بر اساس machine timeline.
- نمایش schedule پیشنهادی optimizer.
- drag/drop دستی از طریق `onDateChange` کتابخانه.
- validation قبل از اعمال حرکت.
- block کردن حرکت نامعتبر و نمایش دلیل conflict.

## موجودیت‌ها

این تسک موجودیت backend جدید اضافه نمی‌کند.

## سرویس‌ها

- تبدیل `ScheduleOperation` به taskهای Gantt در frontend.
- validation سمت UI برای manual move.
- نگهداری draft move در state صفحه Schedule.

## endpointهای API

- `GET /scenarios`
- `POST /optimizer/run`
- `GET /optimizer/runs`
- `GET /optimizer/runs/{optimization_run_id}/schedule`
- `POST /optimizer/runs/{optimization_run_id}/accept`

## قوانین validation

حرکت دستی قبل از اعمال بررسی می‌شود:

- precedence عملیات‌های یک order
- overlap ماشین
- overlap اپراتور
- material blocker از خروجی optimizer
- calendar/shift ساده با بازه 06:00 تا 22:00
- blockerهای QC/Approval/NCR اگر در `blocked_reason` یا status موجود باشند

## رفتار conflict

اگر conflict وجود داشته باشد:

- تغییر به Gantt اعمال نمی‌شود.
- لیست reasonها نمایش داده می‌شود.
- کتابخانه Gantt با برگشت `false` حرکت را rollback می‌کند.

## محدودیت‌های فعلی

- validation سمت UI است و endpoint backend جدا برای manual move validation هنوز وجود ندارد.
- alternative suggestion هوشمند یا AI وجود ندارد.
- machine capability و operator authorization واقعی هنوز از backend برای drag/drop خوانده نمی‌شود.
- calendar فعلی ساده است و فقط بازه ثابت 06:00 تا 22:00 را بررسی می‌کند.
- تست مرورگر end-to-end اجرا نشده است.

## تست‌ها

- `npm install gantt-task-react --legacy-peer-deps` موفق بود.
- `npm run build` موفق بود.
- TypeScript compile موفق بود.
- Vite production build موفق بود.
