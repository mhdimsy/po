# PROJECT_CANONICAL_CONTEXT.md

## وضعیت این سند

این فایل، مرجع کوتاه و canonical برای ادامه‌ی مکالمات و کار ایجنت‌ها روی پروژه برنامه‌ریزی تولید است.

اگر بین مکالمات قبلی پروژه، برداشت‌های قبلی، یا پاسخ‌های قدیمی با این فایل و دو سند اصلی پروژه تناقض وجود داشت، این ترتیب اعتبار رعایت شود:

1. `PROJECT_CANONICAL_CONTEXT.md`
2. `turbine_production_system_knowledge_fa.md`
3. `turbine_production_ai_target_state_fa.md`
4. مکالمات قبلی پروژه فقط به‌عنوان زمینه تاریخی

مکالمات قبلی نباید به‌تنهایی مبنای تصمیم فنی، طراحی دیتامارت، طراحی AI/ML یا تحلیل سیستم قرار بگیرند.

---

## اصل مرکزی پروژه

پروژه دو مسیر متفاوت دارد که باید همیشه از هم جدا شوند:

```text
A) شناخت، نقد یا ادامه‌ی سیستم فعلی
B) ساخت سیستم جدید / AI / Optimization از صفر یا به‌صورت لایه مستقل
```

اشتباه اصلی این است که نیازهای مسیر A را به مسیر B تحمیل کنیم.

---

## مسیر A: شناخت یا نقد سیستم فعلی

اگر هدف این باشد که بفهمیم سیستم فعلی چگونه کار می‌کند، یا `Query_TimeNeed` و داشبوردهای فعلی چقدر درست یا غلط عمل کرده‌اند، نقطه شروع اصلی این‌ها هستند:

```text
Query_TimeNeed
Query_TimeNeedTable
Query_TimeNeedView
Dash_ProductDashboard_15
Dash_ProductDashboardProductsMajorParts_16_01
MRPOutput / MRPOutputBlades
```

در این مسیر، تاریخچه‌ی روزانه‌ی `Query_TimeNeedTable` مفید و گاهی لازم است، چون نشان می‌دهد سیستم فعلی در هر روز چه برنامه‌ای تولید کرده بود.

این history برای پاسخ به این سؤال‌ها لازم است:

- سیستم در فلان روز چه `LatestStartDate` و `LatestFinishDate` داده بود؟
- برنامه فعلی روزبه‌روز چقدر جابه‌جا شده است؟
- delay از اجرای واقعی آمده یا از تغییر خود برنامه؟
- `Query_TimeNeed` چقدر خوش‌بینانه یا بدبینانه برنامه‌ریزی می‌کرده؟

پس برای نقد و baseline گرفتن از سیستم فعلی:

```text
Query_TimeNeedTable history مهم است.
```

---

## مسیر B: ساخت سیستم جدید / AI / Optimization

اگر هدف ساخت یک سیستم جدید، دیتامارت تحلیلی، مدل ML، simulator، optimizer یا scheduler ظرفیت‌دار باشد، تاریخچه‌ی قدیمی `Query_TimeNeedTable` شرط شروع نیست.

در این مسیر، سؤال اصلی این نیست که سیستم فعلی در گذشته چه فکری می‌کرده؛ سؤال اصلی این است که کارخانه واقعاً چگونه رفتار می‌کند.

داده‌های مهم‌تر برای مسیر جدید:

```text
Order / OrderParts
BOM / BOMParts
Routine / RoutineOperations
OrderRoutineOperation
OrderRoutineOperationMachine
MachineData
Machine / WorkCenter
MRPOutput / MRPOutputBlades
NPN / NCR tables
Capacity calendar, if available
Machine availability, if available
Material readiness, if available
```

در این مسیر، هسته‌ی تحلیلی باید از execution واقعی، routing، ساختار BOM/order، ظرفیت، MRP و NCR ساخته شود.

پس برای ساخت سیستم جدید:

```text
Execution history مهم‌تر از Query_TimeNeedTable history است.
```

`Query_TimeNeedTable` در مسیر جدید فقط نقش‌های زیر را دارد:

- baseline سیستم فعلی
- reference برای فهم وضع موجود
- منبع کمکی برای مقایسه old vs new
- نقشه اولیه برای شناخت product/order tree در snapshot فعلی

اما نباید منبع اصلی یادگیری، execution یا scheduler آینده فرض شود.

---

## قانون تصمیم کوتاه

```text
برای ادامه یا نقد سیستم فعلی:
    Query_TimeNeedTable history مهم است.

برای ساخت سیستم جدید از صفر:
    Execution history، routing، BOM/order precedence، capacity، MRP و NCR مهم‌ترند.
```

---

## تفکیک داده‌ها

### Planning Snapshot فعلی

```text
Query_TimeNeed
Query_TimeNeedTable
Query_TimeNeedView
```

این‌ها نشان می‌دهند برنامه فعلی سیستم چه چیزی محاسبه کرده است.

### Execution واقعی

```text
OrderRoutineOperation
OrderRoutineOperationMachine
MachineData
```

این‌ها برای فهم اجرای واقعی، مدت واقعی عملیات، شروع/پایان واقعی، ماشین/WorkCenter و deviation از زمان استاندارد مهم‌ترند.

### ساختار محصول و سفارش

```text
ProductsDeliveryDate
[Order]
OrderParts
BOM
BOMParts
Routine
RoutineOperations
Process
ProcessType
```

این‌ها برای ساخت مدل جدید، precedence و routing لازم‌اند.

### MRP و NCR

```text
MRPOutput
MRPOutputBlades
NPN
NCRTasksStatus
NCRSpecialPartOrder
```

این‌ها برای تحلیل shortage، material readiness، کیفیت، NCR و rework استفاده می‌شوند.

---

## نکات احتیاطی ثابت

- `Query_TimeNeedTable` جدول خام تراکنشی نیست؛ snapshot محاسباتی است.
- `Query_TimeNeed` موتور اصلی ساخت snapshot برنامه‌ریزی فعلی است.
- داشبوردها مصرف‌کننده `Query_TimeNeedTable` و MRP هستند، نه موتور برنامه‌ریزی.
- `RealEndDate` همیشه پایان واقعی قطعی نیست؛ ممکن است محاسباتی یا تخمینی باشد.
- `OrderStatus` فقط متن وضعیت است و منبع برنامه‌ریزی نیست.
- `No Order` بدون بررسی `AssignmentStatus` تحلیل نشود.
- ظرفیت ماشین/WorkCenter در کدهای بررسی‌شده وارد زمان‌بندی اصلی نشده، مگر شواهد جدید خلافش ارائه شود.
- برای تحلیل سیستم فعلی، پیش‌فرض فقط `SELECT` / read-only است.
- برای هر `UPDATE`, `DELETE`, `INSERT`, `TRUNCATE` یا تغییر داده باید درخواست صریح و آگاهانه وجود داشته باشد.

---

## نقش AI/ML/RL در پروژه

در سیستم فعلی، AI/ML/RL وجود ندارد و نباید به `Query_TimeNeed` نسبت داده شود.

برای آینده:

```text
ML predicts.
Optimization decides.
Simulation validates.
Human approves.
```

یادگیری تقویتی یا RL اگر روزی وارد شود، باید ابتدا در simulation/shadow mode باشد، نه مستقیم روی کارخانه واقعی یا دیتابیس عملیاتی.

برای شروع مسیر آینده، RL اولویت اول نیست. اولویت‌های عملی‌تر:

1. Data audit و loss mapping
2. ساخت execution history
3. مقایسه standard duration با actual duration
4. پیش‌بینی duration عملیات
5. delay risk و critical operation early warning
6. bottleneck/capacity visibility
7. what-if simulation
8. finite capacity scheduler pilot

---

## دستور رفتاری برای ایجنت‌ها

قبل از هر کدنویسی یا طراحی:

1. مشخص کن سؤال درباره سیستم فعلی است یا هدف آینده.
2. اصطلاحات دامنه را شفاف کن.
3. assumptions را بنویس.
4. ریسک‌های تفسیر اشتباه داده را مشخص کن.
5. برای سیستم فعلی فقط read-only کوئری بده، مگر درخواست صریح تغییر داده وجود داشته باشد.
6. قابلیت‌های آینده مثل finite capacity، optimizer، simulation، prediction و RL را به سیستم فعلی نسبت نده.
7. اگر محصول یا order خاص مطرح شد، ابتدا `ProductDeliveryDate_Id` و `Order_Id` پیدا شود.
8. برای تحلیل برنامه فعلی از `Query_TimeNeedTable` شروع کن.
9. برای ساخت سیستم جدید از execution واقعی و routing/BOM/order/capacity/MRP/NCR شروع کن.

---

## خلاصه نهایی

این پروژه نباید در این دام بیفتد که چون `Query_TimeNeedTable` history کامل نداریم، پس نمی‌توانیم سیستم جدید بسازیم.

حقیقت دقیق‌تر این است:

```text
برای ارزیابی گذشته‌ی سیستم فعلی، history کامل Query_TimeNeedTable مفید است.
برای ساخت سیستم جدید، execution history و داده‌های واقعی تولید پایه اصلی‌اند.
```

بنابراین از این به بعد، اسناد و پاسخ‌ها باید این تفکیک را رعایت کنند.
