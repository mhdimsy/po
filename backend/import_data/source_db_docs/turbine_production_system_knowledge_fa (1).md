# سند شناخت سیستم برنامه‌ریزی تولید و داشبورد محصولات

این سند برای استفاده در Project Instructions یا به‌عنوان فایل شناخت برای ایجنت/مدل بعدی نوشته شده است. هدف سند، شناخت سیستم موجود است؛ نه پیشنهاد اصلاح، نه طراحی الگوریتم جدید، و نه قضاوت درباره درست یا غلط بودن فرآیندها.

---

## 1. هدف تحلیل

کاربر برنامه‌نویس تازه‌وارد به شرکتی با سیستم برنامه‌ریزی تولید کارخانه توربین است. گفته شده برنامه‌ریزی فعلی «backward» است، ظرفیت را در نظر نمی‌گیرد، و NCRها باعث می‌شوند خروجی برنامه‌ریزی با واقعیت اختلاف پیدا کند.

هدف فعلی فقط شناخت سیستم است:

- دیتابیس SQL Server است.
- دسترسی به دیتابیس وجود دارد.
- دسترسی به برنامه‌نویسان قبلی وجود ندارد.
- باید با reverse engineering از روی دیتابیس، stored procedureها، view/reportها و داده‌ها، منطق سیستم فهمیده شود.
- فعلاً نباید وارد پیشنهاد اصلاح، finite capacity scheduling، redesign یا تغییر داده شد.

---

## 2. اصل مهم برای ایجنت بعدی

هر بار که کاربر درباره این سیستم سؤال می‌پرسد، فرض کن موضوع اصلی یکی از این‌هاست:

1. شناخت ساختار داده
2. شناخت منطق برنامه‌ریزی موجود
3. شناخت منطق داشبوردها
4. نوشتن کوئری‌های read-only برای تحلیل
5. مستندسازی روابط و جریان داده

از پیشنهادهای بهبود، تغییر الگوریتم، update/delete/insert عملیاتی، یا نسخه‌پیچی برای برنامه‌ریزی ظرفیت خودداری کن مگر کاربر صریحاً وارد فاز بهبود شود.

---

## 3. تصویر کلی سیستم

سیستم دو لایه اصلی دارد:

### 3.1 لایه رسمی/تراکنشی دیتابیس

این لایه شامل موجودیت‌های اصلی تولید است:

- `ProductsDeliveryDate`
- `[Order]`
- `OrderParts`
- `Routine`
- `RoutineOperations`
- `Process`
- `ProcessType`
- `BOM`
- `BOMParts`
- `AssignmentStatus`
- `OrderRoutineOperation`
- `OrderRoutineOperationMachine`
- `Machine`

### 3.2 لایه محاسباتی/گزارشی

این لایه خروجی برنامه‌ریزی و داشبوردها را می‌سازد:

- `Query_TimeNeed`
- `Query_TimeNeedTable`
- `Query_TimeNeedView`
- `Dash_ProductDashboard_15`
- `Dash_ProductDashboardProductsMajorParts_16_01`
- `ProductTotalActualTime`
- `RemainedOperationsDuration`
- `MRPOutput`
- `MRPOutputBlades`
- `MRPOutputForView`
- `NPN`
- `NCRTasksStatus`
- `NCRSpecialPartOrder`

---

## 4. جریان داده اصلی برنامه‌ریزی

جریان اصلی سیستم چنین فهمیده شده است:

```text
ProductsDeliveryDate
  → Order
    → Routine
      → BOM
        → BOMParts

Order
  → OrderParts
    → Parent / Child Orders

Routine
  → RoutineOperations
    → Process
      → ProcessType

Query_TimeNeed
  → باز کردن BOM tree
  → باز کردن Order tree
  → اتصال به RoutineOperations
  → محاسبه OPTime / OPDay / LS / LF / ES / EF
  → TRUNCATE Query_TimeNeedTable
  → INSERT خروجی جدید در Query_TimeNeedTable

Query_TimeNeedTable
  → Query_TimeNeedView
  → Dash_ProductDashboard_15
  → Dash_ProductDashboardProductsMajorParts_16_01
```

---

## 5. موتور اصلی برنامه‌ریزی: `dbo.Query_TimeNeed`

`Query_TimeNeed` قلب سیستم برنامه‌ریزی است. این stored procedure فقط گزارش نمی‌سازد؛ بلکه قبل و حین محاسبه بعضی داده‌ها را نیز تغییر می‌دهد. برای مثال در ابتدای procedure مواردی مثل `UPDATE ProductsDeliveryDate`، `DELETE ComponentAssignment` و `INSERT ComponentAssignment` دیده شده است.

نکات مهم:

- این SP مقدار `@ToDate` را به‌صورت `DATEADD(MONTH,10,GETDATE())` تعریف می‌کند.
- برای بعضی کدهای `PB-PBI%`، مقدار `PlannedDueDate` را به شش ماه بعد از تاریخ روز تغییر می‌دهد.
- از `Query_TimeNeedTable` قبلی هم در بعضی محاسبات استفاده می‌کند.
- جدول‌های موقت زیادی می‌سازد، مثل:
  - `#BOMPattern`
  - `#BOMPattern1`
  - `#BOMPattern2`
  - `#FinalResult`
  - `#FinalResult2`
  - `#ProductDelivery`
- در انتهای SP، `Query_TimeNeedTable` را `TRUNCATE` می‌کند و دوباره پر می‌کند.

---

## 6. خروجی اصلی برنامه‌ریزی: `Query_TimeNeedTable`

`Query_TimeNeedTable` یک جدول snapshot محاسباتی است، نه جدول تراکنشی خام. این جدول خروجی اجرای `Query_TimeNeed` است و هر بار پاک و مجدداً ساخته می‌شود.

ستون‌های مهم:

- `ProductDeliveryDate_Id`
- `ProductDeliverDate`
- `BomParent_Id`
- `Bom_Id`
- `OrderParent_Id`
- `ParentOrder`
- `Order_Id`
- `ChildOrder`
- `Routine_Id`
- `AssignmentStatus`
- `Level`
- `RoutineOperation_Id`
- `Operation`
- `Process`
- `OrderTime`
- `OrderDay`
- `OPTime`
- `OPDay`
- `LS`
- `LF`
- `ES`
- `EF`
- `LatestStartDate`
- `LatestFinishDate`
- `EarliestStartDate`
- `EarliestFinishDate`
- `KennNumber`
- `StartDateTime`
- `EndDateTime`
- `OperationStatus`
- `RealEndDate`
- `OrderStatus`
- `PK`

---

## 7. فرمول تاریخ‌دهی در `Query_TimeNeedTable`

در انتهای `Query_TimeNeed` تاریخ‌های برنامه‌ریزی از `PlannedDueDate` و offsetهای `LS/LF/ES/EF` ساخته می‌شوند.

فرمول‌ها:

```sql
DATEADD(DAY, LS, DATEADD(DAY, -MaxLF, PlannedDueDate)) AS LatestStartDate
DATEADD(DAY, LF, DATEADD(DAY, -MaxLF, PlannedDueDate)) AS LatestFinishDate
DATEADD(DAY, ES, DATEADD(DAY, -MaxLF, PlannedDueDate)) AS EarliestStartDate
DATEADD(DAY, EF, DATEADD(DAY, -MaxLF, PlannedDueDate)) AS EarliestFinishDate
```

برداشت:

```text
BaseDate = PlannedDueDate - MaxLF
LatestStartDate   = BaseDate + LS
LatestFinishDate  = BaseDate + LF
EarliestStartDate = BaseDate + ES
EarliestFinishDate= BaseDate + EF
```

بنابراین سیستم واقعاً backward از تاریخ تعهد محصول (`PlannedDueDate`) تاریخ‌دهی می‌کند.

---

## 8. ظرفیت در برنامه‌ریزی

در منطق بررسی‌شده‌ی `Query_TimeNeed` و داشبوردها، نشانه‌ای از finite capacity scheduling دیده نشده است.

چیزهایی که دیده نشدند:

- ظرفیت ماشین
- ظرفیت WorkCenter
- تقویم ظرفیت
- شیفت کاری به‌عنوان محدودیت
- بارگذاری منابع
- queue روی ماشین
- conflict resolution بین سفارش‌ها
- محدودیت هم‌زمانی چند سفارش روی یک ماشین

بنابراین فعلاً شناخت سیستم این است که تاریخ‌ها بر اساس routing، زمان‌های استاندارد، درخت BOM/order و تاریخ تعهد ساخته می‌شوند؛ نه بر اساس ظرفیت محدود ماشین/منبع.

این نکته فقط شناخت سیستم است، نه پیشنهاد اصلاح.

---

## 9. مفهوم `RealEndDate`

نام `RealEndDate` گمراه‌کننده است. در نمونه‌ها دیده شد که برای عملیات‌هایی با `OperationStatus = 'Not Started'` هم `RealEndDate` مقدار آینده دارد.

بنابراین:

```text
RealEndDate همیشه پایان واقعی نیست.
در بسیاری از موارد، مخصوصاً برای عملیات شروع‌نشده، مقدار محاسباتی/تخمینی است.
```

در داشبورد و `Query_TimeNeedView`، delay معمولاً از اختلاف `RealEndDate` و `LatestFinishDate` ساخته می‌شود:

```text
Delay = RealEndDate - LatestFinishDate
```

پس باید هنگام تحلیل گفت: `RealEndDate` می‌تواند actual یا estimated/calculated باشد، بسته به وضعیت operation/order.

---

## 10. وضعیت عملیات: `OperationStatus`

در خروجی `Query_TimeNeedTable` مقدارهایی مثل این دیده شده‌اند:

- `Not Started`
- `Finished`
- احتمالاً `Current`

منطق کلی:

```text
Finished     → عملیات EndDateTime دارد یا سفارش GR شده است
Not Started  → عملیات شروع نشده
Current      → عملیات شروع شده ولی تمام نشده
```

برای فهم دقیق‌تر وضعیت عملیات باید به `OrderRoutineOperation.StartDateTime` و `OrderRoutineOperation.EndDateTime` نگاه کرد.

---

## 11. تابع وضعیت سفارش: `dbo.NCRAndOrderStratus`

تابع `NCRAndOrderStratus(@O_Id)` فقط متن وضعیت سفارش را تولید می‌کند، نه برنامه‌ریزی را.

خروجی نمونه:

```text
<<5300004434>> <<<0/48  [ 0/0  ] >>>
```

ساختار خروجی:

```text
<<NCR_OR_NPN_NOTIFICATION>> <<<DoneAll/TotalAll [DoneMachining/TotalMachining]>>>
```

اگر سفارش `GoodReciept = 1` داشته باشد، خروجی اصلی وضعیت سفارش `GR` می‌شود:

```text
<<<GR>>>
```

قسمت `[DoneMachining/TotalMachining]` فقط عملیات‌هایی را می‌شمارد که `ProcessType_Id = 1` دارند، یعنی Machining.

نقش NCR در این تابع:

- اگر در جدول `NPN` برای `ProdOrder = Order.Code` رکورد وجود داشته باشد، شماره Notification اول خروجی می‌آید.
- NCR/NPN در این تابع فقط به‌صورت برچسب وضعیت متنی ظاهر می‌شود.
- این تابع تاریخ‌های برنامه‌ریزی را تغییر نمی‌دهد.
- این تابع capacity یا delay را محاسبه نمی‌کند.

---

## 12. موجودیت‌های رسمی و روابط FK

روابط رسمی مهم دیتابیس:

```text
ProductsDeliveryDate.Order_Id → Order.Id
Order.Routine_Id → Routine.Id
Routine.BOM_Id → BOM.Id
BOMParts.BOMParent_Id → BOM.Id
BOMParts.BOMChild_Id → BOM.Id
RoutineOperations.Routine_Id → Routine.Id
RoutineOperations.Process_Id → Process.Id
OrderRoutineOperation.Order_Id → Order.Id
OrderRoutineOperation.RoutineOperation_Id → RoutineOperations.Id
OrderRoutineOperationMachine.OrderRoutineOperation_Id → OrderRoutineOperation.Id
OrderRoutineOperationMachine.Machine_Id → Machine.Id
OrderParts.ParentOrder_Id → Order.Id
OrderParts.ChildOrder_Id → Order.Id
OrderParts.AssignmentStatus_Id → AssignmentStatus.Id
```

روابط کیفیت/NCR مرتبط:

```text
NCRPriorityByOrder.Order_Id → Order.Id
NCRSpecialPartOrder.Order_Id → Order.Id
QCDailyReportBarcode.Order_Id → Order.Id
QCDailyReportBarcode.Bom_Id → BOM.Id
QCDailyReportBarcode.RoutineOperations_Id → RoutineOperations.Id
QCdescription.Order_Id → Order.Id
```

نکته مهم:

این آبجکت‌ها FK رسمی قابل مشاهده نداشتند یا دست‌کم در خروجی FKها دیده نشدند:

- `Query_TimeNeedTable`
- `MRPOutput`
- `MRPOutputBlades`
- `MRPOutputForView`
- `MachineData`
- `NPN`

بنابراین اتصالشان بیشتر با convention، join دستی، stored procedure و کد انجام می‌شود.

---

## 13. جدول‌ها و نقش آن‌ها

### `ProductsDeliveryDate`

تعهد محصول را نگه می‌دارد.

نقش‌های مهم:

- اتصال محصول به order ریشه
- نگهداری `PlannedDueDate`
- نگهداری وضعیت actual delivery با فیلدهایی مثل `ActualDueDate`
- ورودی اصلی `Query_TimeNeed`

### `[Order]`

سفارش تولید را نگه می‌دارد.

ستون‌های کلیدی:

- `Id`
- `Routine_Id`
- `Code`
- `GoodReciept`

`GoodReciept = 1` معمولاً در status به‌صورت `GR` دیده می‌شود.

### `OrderParts`

درخت سفارش‌ها را نگه می‌دارد.

ستون‌های کلیدی:

- `ParentOrder_Id`
- `ChildOrder_Id`
- `AssignmentStatus_Id`

این جدول نشان می‌دهد کدام سفارش فرزند به کدام سفارش والد تخصیص دارد.

### `AssignmentStatus`

lookup وضعیت assignment:

```text
1 Predicted Assignment
2 In-Use Assignment
3 Final Assignment
4 Auto Assignment
5 Scrap
6 Old
7 Suspended
```

نکته: مقادیری مثل `No Need` و `Component` در lookup رسمی `AssignmentStatus` نیستند و به‌صورت متنی/محاسباتی در خروجی‌ها ظاهر می‌شوند.

### `BOM`

ساختار قطعات/محصول را نگه می‌دارد.

ستون‌های مهمی که در سیستم استفاده می‌شوند:

- `Id`
- `Title`
- `Code`
- `UsageType_Id`
- `SAPCode`
- `PC`
- `PartsGroup_Id`

### `BOMParts`

رابط parent-child بین BOMهاست.

```text
BOMParent_Id
BOMChild_Id
```

### `Routine`

route کلی ساخت یک BOM را نگه می‌دارد.

```text
Routine.Id
Routine.BOM_Id
```

### `RoutineOperations`

عملیات‌های route را نگه می‌دارد.

ستون‌های کلیدی:

- `Routine_Id`
- `Process_Id`
- `SetupDuration`
- `OperationDuration`
- `AssemblyDuration`
- `OperationDescription`
- `OperationSequence`

### `Process`

lookup عملیات/فرآیند است.

به `ProcessType` وصل می‌شود.

نمونه‌ها:

- `HM-Boring`
- `HM-Turning`
- `MSM-Turning`
- `MSM-Turning-H`
- `Assembly`
- `Pre-Assembly`
- `Quality Control`
- `OutSource`
- `Welding`
- `Heat Treatment`
- `Manual Operations`

### `ProcessType`

lookup نوع فرآیند:

```text
1 Machining
2 Assembly
3 Test
4 OutSourcing
5 Other
6 Welding
```

### `OrderRoutineOperation`

اجرای عملیات برای یک order را نگه می‌دارد.

ستون‌های کلیدی:

- `Order_Id`
- `RoutineOperation_Id`
- `StartDateTime`
- `EndDateTime`
- `UniqueKey`
- `WorkCenter`

این جدول برای شناخت اجرای واقعی بسیار مهم است.

### `OrderRoutineOperationMachine`

اتصال عملیات order به ماشین است.

```text
OrderRoutineOperation_Id
Machine_Id
```

در نمونه بررسی‌شده برای order ریشه، بسیاری از Machine_Idها NULL بودند و WorkCenter پر بود؛ پس ممکن است برخی برنامه‌ها در سطح WorkCenter باشند، نه ماشین دقیق.

### `MachineData`

داده‌های ثبت‌شده از ماشین/بارکد است.

اتصال غیررسمی مهم:

```text
MachineData.Bolla = OrderRoutineOperation.UniqueKey
```

در `ProductTotalActualTime` فقط رکوردهای `MachineData` با:

```sql
SmallOperationCode = 14
```

برای duration واقعی استفاده شده‌اند.

### `MRPOutput`, `MRPOutputBlades`

خروجی/ورودی مربوط به MRP و کمبود تأمین است.

در داشبوردها برای تشخیص shortage استفاده می‌شوند:

```sql
WHERE Shortage > 0
```

### `NPN`

جدول NCR/NPN است.

در تابع `NCRAndOrderStratus` به شکل زیر استفاده می‌شود:

```text
NPN.ProdOrder = Order.Code
```

و اگر رکورد وجود داشته باشد، `Notification` در ابتدای `OrderStatus` نمایش داده می‌شود.

---

## 14. lookupهای مهم

### `AssignmentStatus`

```text
1 Predicted Assignment
2 In-Use Assignment
3 Final Assignment
4 Auto Assignment
5 Scrap
6 Old
7 Suspended
```

### `ProcessType`

```text
1 Machining
2 Assembly
3 Test
4 OutSourcing
5 Other
6 Welding
```

### `PartsGroup`

نمونه‌های مهم:

```text
18 Blade & Vane
20 Skid
19 PartsWithLongAssemblyAndSmallMachinigDuration
```

در کدها، `PartsGroup_Id = 18` یعنی Blade/Vane و بعضی جاها جداگانه یا حذف‌شده از محاسبه آمده است.

### `UsageType`

خانواده محصول است، مثل:

```text
MGT-70
MGT-30/Version 1
MGT-75
MGT-40
MGT-20
MST-70C
MST-55C
MST-54C
MST-50C
MST-50/1801
Compressor/T3
COMPRESSOR ON SKID-BidBoland
SKID/Compressor/SHURIJEH
```

داشبوردها روی لیستی از UsageTypeها فیلتر دارند.

---

## 15. داشبورد سطح محصول: `Dash_ProductDashboard_15`

این stored procedure داشبورد وضعیت محصولات را می‌سازد.

ورودی‌های اصلی:

- `Query_TimeNeedTable`
- `ProductsDeliveryDate`
- `[Order]`
- `Routine`
- `BOM`
- `UsageType`
- `MRPOutput`
- `MRPOutputBlades`
- `usagetypeMappingForDashboard`

### منطق کلی

ابتدا `Query_TimeNeedTable` را با اطلاعات محصول و BOM ترکیب می‌کند.

سپس موارد زیر را حذف می‌کند:

```sql
AssignmentStatus IN ('No Need','Component')
```

بعد shortage را از `MRPOutput` و `MRPOutputBlades` تشخیص می‌دهد:

```sql
Shortage > 0
```

اگر یک child shortage داشته باشد، shortage به parentهای BOM هم propagate می‌شود.

### محاسبه زمان‌ها

`TotalTime`:

```text
جمع OPTime همه عملیات‌های محصول، به‌جز بعضی PartsGroupها مثل Blade/Vane
```

`PlanTime`:

```text
جمع OPTime عملیات‌هایی که LatestFinishDate < GETDATE()
```

`ActualTime`:

```text
جمع OPTime عملیات‌هایی که OperationStatus = 'Finished'
```

`DelayProductionTime`:

```text
جمع OPTime عملیات‌هایی که:
- LatestFinishDate < GETDATE()
- OperationStatus در Current یا Not Started است
- Shortage = 0
```

### درصدها

`Plan%`:

```text
PlanTime / TotalTime * 100
```

`Actual%`:

```text
ActualTime / TotalTime * 100
```

`DelayProduction%` و `DelayProcurement%` از ترکیب gap بین Plan و Actual و سهم shortage/non-shortage ساخته می‌شوند.

برداشت شناختی:

داشبورد محصول، برنامه‌ریزی جدید تولید نمی‌کند؛ خروجی `Query_TimeNeedTable` را تفسیر می‌کند.

---

## 16. داشبورد Major Parts: `Dash_ProductDashboardProductsMajorParts_16_01`

این stored procedure داشبورد وضعیت ماژورپارت‌ها / ماژول‌های محصول را می‌سازد.

ورودی‌های مهم:

- `Query_TimeNeedTable`
- `ProductsPartsMappingForDashboard`
- `MRPOutput`
- `MRPOutputBlades`
- `Query_TimeNeedView`
- `BarcodePath`
- `usagetypeMappingForDashboard`

### منطق کلی

1. ابتدا مثل داشبورد محصول، داده‌های باز از `Query_TimeNeedTable` را می‌گیرد.
2. قطعات را با `ProductsPartsMappingForDashboard` به Major Part وصل می‌کند.
3. با loop، Major Part را به زیرمجموعه‌های BOM propagate می‌کند.
4. shortage را از MRP پیدا می‌کند.
5. `Query_TimeNeedView` را اجرا می‌کند و خروجی آن را در `#TEMP` می‌ریزد.
6. delay تولیدی و delay تأمینی را در سطح Major Part تحلیل می‌کند.
7. با یک margin از `BarcodePath`، critical module را مشخص می‌کند.

برداشت شناختی:

این SP هم برنامه‌ریزی انجام نمی‌دهد؛ بلکه خروجی برنامه‌ریزی و MRP را در سطح Major Part تفسیر می‌کند.

---

## 17. `Query_TimeNeedView`

این procedure یک نمای مدیریتی/گزارشی روی `Query_TimeNeedTable` می‌سازد.

خروجی‌هایی مثل این تولید می‌کند:

- Product code
- Customer
- DeliveryDate
- Part title
- ParentOrder
- Order
- SAPCode
- Assembly/Part
- KennNo
- Level
- AssignmentStatus
- OrderStatus
- Delay
- ComponentQTY
- OrderDay
- NCRRelatedPart
- LatestStartDate
- LatestFinishDate
- RealEndDate
- MainDelay
- ShortageList
- NCRStatus

منطق delay:

```text
Delay = DATEDIFF(DAY, MAX(LatestFinishDate), MAX(RealEndDate))
```

اما برای `AssignmentStatus = Component` یا `No Need`، delay را صفر می‌کند.

---

## 18. `ProductTotalActualTime`

این procedure زمان واقعی تولید را از مسیر زیر محاسبه می‌کند:

```text
Query_TimeNeedTable
  → OrderRoutineOperation
    → UniqueKey = MachineData.Bolla
      → MachineData.Duration
        → Machine
          → MachineProcess
            → Process
```

فقط رکوردهای `MachineData` با `SmallOperationCode = 14` را در نظر می‌گیرد.

برداشت:

این procedure برای actual duration است، نه برنامه‌ریزی.

---

## 19. `RemainedOperationsDuration`

این scalar function زمان باقی‌مانده عملیات یک order را حساب می‌کند.

ورودی:

```text
@Order_Id
```

منابع داده:

- `[Order]`
- `OrderRoutineOperation`
- `RoutineOperations`
- `OrderRoutineOperationRoutingTime`
- `RoutineOperationsEngineering`
- `Routine`
- `BOM`
- `COOIS$`
- `TotalBOMBlades`

شرط مهم:

```text
EndDateTime IS NULL
GoodReciept = 0
```

یعنی فقط عملیات‌هایی که تمام نشده‌اند و order هنوز GR نشده را در زمان باقی‌مانده حساب می‌کند.

---

## 20. NCR در سیستم

NCR/NPN در چند نقطه دیده شده است:

- `NPN`
- `NCRCheck`
- `NCRPriorityByOrder`
- `NCRTasksStatus`
- `NCRSpecialPartOrder`
- `NCRLongText$`
- `ncrtask$`

شناخت فعلی:

- `NPN` برای نمایش Notification در `OrderStatus` استفاده می‌شود.
- `NCRTasksStatus` در `Query_TimeNeedView` برای `NCRStatus` join می‌شود.
- `NCRSpecialPartOrder` برای مشخص‌کردن قطعات خاص مرتبط با NCR استفاده می‌شود.
- در کدهای بررسی‌شده، NCR مستقیماً ظرفیت یا تاریخ‌دهی عملیات را تغییر نمی‌دهد، مگر به‌صورت غیرمستقیم در assignment/related partها.

باید این جمله با احتیاط استفاده شود:

```text
در بخش‌های بررسی‌شده، NCR بیشتر در status، نمایش، mapping و برخی روابط قطعه/سفارش اثر دارد؛ نه در finite scheduling یا capacity.
```

---

## 21. نکات مهم از نمونه محصول `A118-108200`

نمونه بررسی‌شده:

```text
Order_Id = 91757
OrderCode = A118-108200
ProductDeliveryDate_Id = 7798
```

در `Query_TimeNeedTable` برای این محصول:

- ریشه محصول Level 0 است.
- order ریشه `91757` دارای 48 عملیات است.
- همه عملیات‌های ریشه `Not Started` بودند.
- `OrderStatus` ریشه:
  ```text
  <<5300004434>> <<<0/48 [0/0]>>>
  ```
- درخت محصول شامل زیرسفارش‌های زیادی در Levelهای پایین‌تر است.
- بسیاری از زیرسفارش‌ها `GR` هستند.
- بعضی بخش‌ها `Order_Id = NULL` دارند.
- اما `Order_Id = NULL` وقتی `AssignmentStatus = No Need` یا `Component` باشد، در داشبورد اصلی حذف یا delay آن صفر می‌شود.

نکته شناختی:

```text
داشبورد محصول فقط سفارش ریشه را نمی‌بیند؛ کل tree محصول را از Query_TimeNeedTable بررسی می‌کند.
```

---

## 22. تفسیر `No Order`

`No Order` به‌تنهایی به معنی مشکل قطعی نیست.

باید همیشه همراه با `AssignmentStatus` بررسی شود.

اگر:

```text
Order_Id IS NULL
AssignmentStatus = No Need
```

یا:

```text
Order_Id IS NULL
AssignmentStatus = Component
```

این ردیف‌ها در داشبوردهای اصلی معمولاً حذف یا delay آن‌ها صفر می‌شود.

پس برای شناخت/تحلیل داشبورد، No Order موثر یعنی:

```sql
Order_Id IS NULL
AND (AssignmentStatus IS NULL OR AssignmentStatus NOT IN ('No Need','Component'))
```

---

## 23. تفکیک برنامه‌ریزی، اجرا و داشبورد

برای جلوگیری از اشتباه، این سه مفهوم جدا نگه داشته شوند:

### برنامه‌ریزی

منبع اصلی:

```text
Query_TimeNeed
Query_TimeNeedTable
```

داده‌های مهم:

```text
PlannedDueDate
LS / LF / ES / EF
LatestStartDate / LatestFinishDate
EarliestStartDate / EarliestFinishDate
OPTime / OPDay
```

### اجرا

منبع اصلی:

```text
OrderRoutineOperation
MachineData
QCDailyReportBarcode
```

داده‌های مهم:

```text
StartDateTime
EndDateTime
UniqueKey
WorkCenter
MachineData.Bolla
MachineData.Duration
MachineData.SmallOperationCode
```

### داشبورد

منبع اصلی:

```text
Dash_ProductDashboard_15
Dash_ProductDashboardProductsMajorParts_16_01
Query_TimeNeedView
```

داده‌های مهم:

```text
Plan%
Actual%
DelayProduction%
DelayProcurement%
CriticalModule
Shortage
NCRStatus
```

---

## 24. قواعد مهم برای نوشتن کوئری

### 24.1 کوئری‌های read-only مجاز و مناسب‌اند

برای شناخت سیستم، فقط `SELECT` بنویس مگر کاربر صریحاً چیز دیگری بخواهد.

### 24.2 با `[Order]` حتماً براکت بزن

چون `ORDER` کلمه کلیدی SQL است:

```sql
SELECT * FROM dbo.[Order]
```

### 24.3 در joinهای متنی SAP code ممکن است نیاز به COLLATE باشد

در procedureها مواردی مثل این دیده شده:

```sql
COLLATE Persian_100_CI_AS
COLLATE Arabic_CI_AS
```

### 24.4 `Query_TimeNeedTable` snapshot است

برای تحلیل خوب است، ولی منبع خام نیست.

### 24.5 `RealEndDate` را actual قطعی فرض نکن

همیشه با `OperationStatus`, `StartDateTime`, `EndDateTime`, `GoodReciept` بررسی شود.

### 24.6 در داشبورد، `No Need` و `Component` را جدا بررسی کن

چون معمولاً از محاسبه اصلی حذف می‌شوند.

---

## 25. کوئری‌های پایه مفید

### 25.1 پیدا کردن تعهد محصول از روی کد order

```sql
SELECT
    pdd.Id AS ProductDeliveryDate_Id,
    pdd.Order_Id,
    o.Code AS ProductOrder,
    pdd.PlannedDueDate,
    pdd.ActualDueDate
FROM ProductsDeliveryDate pdd
JOIN dbo.[Order] o ON pdd.Order_Id = o.Id
WHERE o.Code = @ProductOrder;
```

### 25.2 خلاصه درخت برنامه برای یک ProductDeliveryDate

```sql
SELECT
    Order_Id,
    MAX(ChildOrder) AS ChildOrder,
    MAX(ParentOrder) AS ParentOrder,
    Level,
    COUNT(*) AS OperationCount,
    SUM(ISNULL(OPTime,0)) AS TotalOPTime,
    SUM(CASE WHEN OperationStatus = 'Finished' THEN ISNULL(OPTime,0) ELSE 0 END) AS FinishedOPTime,
    MIN(LatestFinishDate) AS MinLatestFinishDate,
    MAX(LatestFinishDate) AS MaxLatestFinishDate,
    MAX(RealEndDate) AS MaxRealEndDate,
    DATEDIFF(DAY, MAX(LatestFinishDate), MAX(RealEndDate)) AS DelayDays,
    MAX(OrderStatus) AS OrderStatus
FROM Query_TimeNeedTable
WHERE ProductDeliveryDate_Id = @ProductDeliveryDate_Id
GROUP BY Order_Id, Level
ORDER BY Level, Order_Id;
```

### 25.3 عملیات یک order واقعی

```sql
SELECT
    oro.Id AS OrderRoutineOperationId,
    oro.Order_Id,
    o.Code AS OrderCode,
    ro.Id AS RoutineOperation_Id,
    ro.OperationSequence,
    p.Title AS Process,
    p.ProcessType_Id,
    ro.SetupDuration,
    ro.OperationDuration,
    ro.AssemblyDuration,
    oro.StartDateTime,
    oro.EndDateTime,
    oro.UniqueKey,
    oro.WorkCenter
FROM OrderRoutineOperation oro
LEFT JOIN dbo.[Order] o
    ON oro.Order_Id = o.Id
LEFT JOIN RoutineOperations ro
    ON oro.RoutineOperation_Id = ro.Id
LEFT JOIN Process p
    ON ro.Process_Id = p.Id
WHERE oro.Order_Id = @Order_Id
ORDER BY ro.OperationSequence;
```

### 25.4 ماشین‌های وصل‌شده به عملیات order

```sql
SELECT
    oro.Order_Id,
    o.Code AS OrderCode,
    ro.OperationSequence,
    p.Title AS Process,
    oro.UniqueKey,
    m.Id AS Machine_Id,
    m.Title AS MachineTitle,
    m.Barcode AS MachineBarcode
FROM OrderRoutineOperation oro
LEFT JOIN dbo.[Order] o
    ON oro.Order_Id = o.Id
LEFT JOIN RoutineOperations ro
    ON oro.RoutineOperation_Id = ro.Id
LEFT JOIN Process p
    ON ro.Process_Id = p.Id
LEFT JOIN OrderRoutineOperationMachine orom
    ON oro.Id = orom.OrderRoutineOperation_Id
LEFT JOIN Machine m
    ON orom.Machine_Id = m.Id
WHERE oro.Order_Id = @Order_Id
ORDER BY ro.OperationSequence;
```

### 25.5 MachineData برای یک order

```sql
SELECT
    md.*
FROM MachineData md
WHERE LTRIM(RTRIM(md.Bolla)) IN (
    SELECT LTRIM(RTRIM(oro.UniqueKey))
    FROM OrderRoutineOperation oro
    WHERE oro.Order_Id = @Order_Id
)
ORDER BY md.Bolla, md.DueDate;
```

### 25.6 No Order موثر در داشبورد

```sql
SELECT TOP 100
    Id,
    ProductDeliveryDate_Id,
    Level,
    BomParent_Id,
    Bom_Id,
    OrderParent_Id,
    Order_Id,
    Operation,
    Process,
    OPTime,
    OPDay,
    LatestFinishDate,
    RealEndDate,
    DATEDIFF(DAY, LatestFinishDate, RealEndDate) AS DelayDays,
    AssignmentStatus,
    OrderStatus,
    PK
FROM Query_TimeNeedTable
WHERE ProductDeliveryDate_Id = @ProductDeliveryDate_Id
  AND Order_Id IS NULL
  AND (AssignmentStatus IS NULL OR AssignmentStatus NOT IN ('No Need','Component'))
ORDER BY
    DATEDIFF(DAY, LatestFinishDate, RealEndDate) DESC,
    Level,
    Bom_Id,
    Operation;
```

### 25.7 NCR/NPNهای مربوط به یک order

```sql
SELECT
    o.Id AS Order_Id,
    o.Code AS OrderCode,
    n.Notification,
    n.ShortText,
    n.CreatedOn,
    n.DefectType,
    n.Severity,
    n.Scrap,
    n.RejectQty
FROM dbo.[Order] o
LEFT JOIN NPN n
    ON n.ProdOrder = o.Code
WHERE o.Id = @Order_Id
   OR o.Code = @OrderCode;
```

---

## 26. چیزهایی که هنوز کامل کشف نشده‌اند

این‌ها برای شناخت کامل‌تر بعدی مهم‌اند:

1. جزئیات کامل محاسبه `LS/LF/ES/EF` در وسط `Query_TimeNeed`
2. دقیق‌ترین منطق تولید `OperationStatus`
3. نقش کامل `NCRSpecialPartOrder` در assignmentها
4. منطق کامل `Query_TimeNeedView` در تفکیک MainDelay
5. ساختار دقیق `MRPOutput`, `MRPOutputBlades`, `MRPOutputForView`
6. اینکه آیا ظرفیت در جای دیگری خارج از کدهای بررسی‌شده وجود دارد یا نه
7. تعریف کامل `Machine`, `MachineProcess`, `WorkCenter` و تقویم‌ها، اگر وجود داشته باشند
8. نقش `Calendar` در سیستم، چون فعلاً در برنامه‌ریزی اصلی شواهد مستقیم از استفاده ظرفیت‌محور دیده نشده

---

## 27. جمع‌بندی نهایی شناخت

شناخت فعلی سیستم:

```text
سیستم برنامه‌ریزی تولید یک snapshot از وضعیت برنامه تولید می‌سازد.
موتور اصلی آن dbo.Query_TimeNeed است.
خروجی اصلی آن Query_TimeNeedTable است.
این خروجی بر اساس تاریخ تعهد محصول، BOM، order tree، routing و زمان‌های استاندارد ساخته می‌شود.
تاریخ‌دهی با فرمول backward از PlannedDueDate انجام می‌شود.
داشبوردها برنامه‌ریزی جدید نمی‌سازند؛ خروجی Query_TimeNeedTable و MRP را تفسیر می‌کنند.
Actual execution از OrderRoutineOperation و MachineData قابل ردیابی است.
NCR/NPN بیشتر در status، view و برخی relationهای سفارش/قطعه دیده می‌شود.
در کدهای بررسی‌شده، capacity محدود ماشین/WorkCenter در زمان‌بندی اصلی دیده نشده است.
```

---

## 28. دستور رفتاری برای ایجنت

وقتی کاربر بعداً درباره این سیستم سؤال کرد:

1. اول مشخص کن سؤال درباره کدام لایه است:
   - planning snapshot
   - execution
   - dashboard
   - NCR
   - MRP/shortage
   - BOM/order tree

2. از این آبجکت‌ها به‌عنوان نقطه شروع استفاده کن:
   - planning: `Query_TimeNeedTable`
   - planning engine: `Query_TimeNeed`
   - dashboard product: `Dash_ProductDashboard_15`
   - dashboard major part: `Dash_ProductDashboardProductsMajorParts_16_01`
   - execution: `OrderRoutineOperation`
   - actual machine data: `MachineData`
   - order tree: `OrderParts`
   - BOM tree: `BOMParts`
   - status text: `NCRAndOrderStratus`
   - management view: `Query_TimeNeedView`

3. فقط کوئری read-only بده مگر کاربر صراحتاً تغییر داده بخواهد.

4. مراقب باش:
   - `RealEndDate` را پایان واقعی قطعی فرض نکنی.
   - `No Order` را بدون بررسی `AssignmentStatus` مشکل فرض نکنی.
   - `OrderStatus` را منبع برنامه‌ریزی فرض نکنی؛ این فقط متن وضعیت است.
   - داشبوردها را موتور برنامه‌ریزی فرض نکنی؛ آن‌ها مصرف‌کننده خروجی برنامه‌اند.
   - capacity scheduling را به سیستم نسبت ندهی مگر شواهد جدید پیدا شود.

5. اگر کاربر از یک محصول یا order خاص حرف زد، اول این دو شناسه را پیدا کن:
   - `ProductDeliveryDate_Id`
   - `Order_Id`

بعد تحلیل را از `Query_TimeNeedTable` شروع کن.
