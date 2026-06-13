# سند چشم‌انداز هدف نهایی هوش مصنوعی، یادگیری ماشین و بهینه‌سازی تولید

این سند مکمل سند شناخت وضع موجود سیستم برنامه‌ریزی تولید است. سند وضع موجود توضیح می‌دهد سیستم فعلی چگونه کار می‌کند؛ این سند توضیح می‌دهد هدف آینده سازمان از استفاده از هوش مصنوعی، یادگیری ماشین، بهینه‌سازی و شبیه‌سازی در فرایند تولید چیست.

هدف این سند، تعریف مسیر مطلوب آینده است؛ نه ادعا درباره قابلیت‌های فعلی سیستم. هر جا در این سند از ظرفیت، پیش‌بینی، optimizer، simulation یا تصمیم‌یار صحبت می‌شود، منظور قابلیت هدف/آینده است مگر اینکه صریحاً خلاف آن گفته شود.

---

## 1. فلسفه اصلی

هدف سازمان از استفاده از AI/ML این نیست که یک مدل هوشمند جای برنامه‌ریز تولید، مدیر تولید یا سیستم فعلی را بگیرد. هدف این است که برنامه‌ریزی و کنترل تولید از حالت ایستا، واکنشی و مبتنی بر تجربه فردی به سمت یک سیستم داده‌محور، پیش‌بینانه، ظرفیت‌محور، قابل توضیح و قابل بهبود مستمر حرکت کند.

چشم‌انداز نهایی:

```text
Plan → Execute → Measure → Learn → Recommend → Optimize → Re-plan
```

یعنی سیستم باید بتواند:

1. برنامه فعلی را بفهمد.
2. اجرای واقعی را اندازه‌گیری کند.
3. انحراف برنامه و اجرا را تحلیل کند.
4. از داده‌های گذشته یاد بگیرد.
5. ریسک‌های آینده را پیش‌بینی کند.
6. گزینه‌های تصمیم‌گیری پیشنهاد بدهد.
7. سناریوها را شبیه‌سازی کند.
8. برنامه ظرفیت‌دار و واقع‌بینانه‌تر تولید کند.
9. نتیجه تصمیم‌ها را دوباره اندازه‌گیری کند و یادگیری را ادامه دهد.

---

## 2. تفکیک مهم: وضع موجود در برابر هدف آینده

سند وضع موجود، منبع شناخت سیستم فعلی است. در شناخت فعلی:

- موتور اصلی برنامه‌ریزی `Query_TimeNeed` است.
- خروجی اصلی برنامه‌ریزی `Query_TimeNeedTable` است.
- `Query_TimeNeedTable` یک snapshot محاسباتی است، نه جدول خام تراکنشی.
- داشبوردها مصرف‌کننده خروجی برنامه و MRP هستند، نه موتور برنامه‌ریزی.
- در کدهای بررسی‌شده، finite capacity scheduling دیده نشده است.
- `RealEndDate` همیشه پایان واقعی قطعی نیست.
- `OrderStatus` منبع برنامه‌ریزی نیست؛ متن وضعیت است.

این سند، هدف آینده را تعریف می‌کند:

```text
حرکت از planning snapshot ساده و backward
به planning/optimization layer داده‌محور، پیش‌بینانه، ظرفیت‌محور و قابل شبیه‌سازی.
```

بنابراین ایجنت نباید مفاهیم این سند را به سیستم فعلی نسبت دهد. اگر گفته می‌شود «ظرفیت ماشین»، «critical path پیش‌بینانه» یا «optimizer»، این‌ها قابلیت‌های مطلوب آینده‌اند، نه الزاماً قابلیت موجود.

---

## 3. هدف نهایی سازمان

هدف نهایی، ساخت یک لایه هوشمند تصمیم‌یار برای تولید است که روی داده‌های واقعی کارخانه کار کند و به سوال‌های زیر پاسخ دهد:

- کدام سفارش‌ها در معرض تأخیر هستند؟
- کدام عملیات‌ها اگر امروز انجام نشوند مسیر بحرانی ایجاد می‌کنند؟
- گلوگاه واقعی امروز، این هفته و ماه آینده کجاست؟
- کدام ماشین، WorkCenter، قطعه، NCR یا shortage بیشترین اثر را روی تحویل محصول دارد؟
- زمان واقعی انجام هر operation احتمالاً چقدر خواهد بود؟
- اگر اولویت یک سفارش تغییر کند، چه اثری روی بقیه محصولات دارد؟
- اگر یک ماشین از دسترس خارج شود، چه سفارش‌هایی آسیب می‌بینند؟
- اگر یک قطعه outsource شود، چند روز از lead time کم می‌شود؟
- کدام تصمیم باعث کاهش makespan، کاهش delay، کاهش WIP یا افزایش on-time delivery می‌شود؟

---

## 4. نقش‌های مختلف AI/ML/Optimization

در این پروژه باید بین چهار نقش متفاوت تمایز گذاشت:

### 4.1 تحلیل توصیفی

هدف: فهم اینکه چه اتفاقی افتاده است.

نمونه‌ها:

- چرا این محصول delay شده است؟
- سهم تولید، MRP، NCR، waiting و shortage در تأخیر چقدر بوده است؟
- کدام WorkCenter بیشترین backlog را داشته است؟
- کدام نوع operation بیشترین deviation از زمان استاندارد دارد؟

### 4.2 پیش‌بینی با ML

هدف: پیش‌بینی آنچه احتمالاً اتفاق خواهد افتاد.

نمونه‌ها:

- پیش‌بینی مدت واقعی هر operation
- پیش‌بینی احتمال delay برای order یا product
- پیش‌بینی ریسک NCR یا rework
- پیش‌بینی زمان تکمیل واقعی
- پیش‌بینی downtime یا افت ظرفیت ماشین

### 4.3 بهینه‌سازی

هدف: انتخاب بهترین تصمیم در میان گزینه‌های ممکن.

نمونه‌ها:

- ترتیب‌دهی operations روی ماشین‌ها
- تخصیص operation به ماشین/WorkCenter
- کاهش مجموع تأخیرها
- کاهش makespan
- کاهش queue time
- کاهش setup
- اولویت‌دهی به سفارش‌هایی که روی critical path هستند

### 4.4 شبیه‌سازی و سناریوسازی

هدف: دیدن اثر تصمیم قبل از اجرا.

نمونه‌ها:

- اگر سفارش A جلو بیفتد چه می‌شود؟
- اگر ماشین X سه روز متوقف شود چه می‌شود؟
- اگر material برای قطعه Y دیر برسد چه محصولاتی ضربه می‌خورند؟
- اگر capacity فلان WorkCenter افزایش یابد، delivery کدام محصول بهتر می‌شود؟

---

## 5. اصل کلیدی معماری تصمیم‌گیری

قاعده محوری این پروژه:

```text
ML predicts.
Optimization decides.
Simulation validates.
Human approves.
```

یعنی:

- ML برای پیش‌بینی استفاده می‌شود.
- Optimizer برای ساخت برنامه پیشنهادی استفاده می‌شود.
- Simulation برای سنجش اثر برنامه استفاده می‌شود.
- انسان تصمیم نهایی، override و تأیید عملیاتی را انجام می‌دهد.

LLM مثل ChatGPT یا ایجنت سازمانی، نقش رابط هوشمند، تحلیلگر، توضیح‌دهنده و تولیدکننده کوئری/گزارش را دارد. LLM نباید به‌تنهایی موتور قطعی زمان‌بندی تولید فرض شود.

---

## 6. قابلیت‌های هدف

### 6.1 تحلیل انحراف برنامه و اجرا

سیستم هدف باید بتواند برای هر product/order/operation بگوید:

- برنامه چه بوده است؟
- اجرا چه شده است؟
- اختلاف از کجا آمده است؟
- آیا انحراف ناشی از تولید، متریال، NCR، ظرفیت، ماشین، انتظار، بازرسی یا داده ناقص بوده است؟

خروجی مطلوب:

```text
Delay Explanation
Root Cause Category
Impact Days
Impacted Product/Order/Operation
Confidence Level
Evidence from data
```

### 6.2 پیش‌بینی مدت واقعی عملیات

سیستم باید بتواند مدت واقعی عملیات را بر اساس سابقه پیش‌بینی کند، نه فقط زمان استاندارد routing.

ویژگی‌های ورودی ممکن:

- Product family
- BOM / PartGroup
- Process
- ProcessType
- WorkCenter
- Machine
- Operation sequence
- Standard duration
- Historical actual duration
- Queue before operation
- NCR history
- Material readiness
- Operator/team, if available
- Shift/calendar, if available

خروجی مطلوب:

```text
PredictedDuration
PredictionInterval
RiskOfOverrun
TopFactors
```

### 6.3 پیش‌بینی ریسک تأخیر

برای هر product/order/major part، سیستم باید ریسک delay را پیش‌بینی کند.

خروجی مطلوب:

```text
DelayRiskScore: 0..100
EstimatedDelayDays
MainRiskDrivers
RecommendedActions
```

نمونه توضیح:

```text
این order ریسک تأخیر 78٪ دارد، چون عملیات machining هنوز شروع نشده، WorkCenter مربوطه backlog بالایی دارد، و یک child part با shortage باز وجود دارد.
```

### 6.4 تشخیص critical path و critical operations

سیستم هدف باید بتواند مسیرهای حساس را در سطح product tree تشخیص دهد.

سطوح تحلیل:

- Product
- Major Part
- BOM node
- Order
- Operation
- Machine/WorkCenter
- Material/NCR constraint

خروجی مطلوب:

```text
CriticalPath
CriticalOperations
CriticalOrders
SlackDays
RiskDrivers
LatestSafeStartDate
```

هدف این نیست که critical path هرگز وجود نداشته باشد؛ هدف این است که critical path زودتر شناسایی شود، slackها دیده شوند و تصمیم‌های زودهنگام گرفته شود.

### 6.5 تحلیل bottleneck ماشین و WorkCenter

سیستم باید بتواند گلوگاه‌های فعلی و آینده را تشخیص دهد.

شاخص‌ها:

- Load / capacity
- Queue length
- Waiting time
- Utilization
- Backlog hours
- Number of critical operations waiting
- Delay impact if unavailable

خروجی مطلوب:

```text
BottleneckWorkCenter
BottleneckMachine
CapacityGapHours
AffectedOrders
AffectedProducts
RecommendedPriority
```

### 6.6 زمان‌بندی ظرفیت‌دار

در بلوغ بالاتر، سیستم باید بتواند برنامه‌ای بسازد که محدودیت ظرفیت را رعایت کند.

قیود مهم:

- ترتیب عملیات هر order
- ظرفیت ماشین/WorkCenter
- تقویم کاری
- availability ماشین
- material readiness
- NCR/rework constraints
- outsourcing lead time
- setup time
- inspection constraints
- priority rules
- due dates

اهداف ممکن:

- کمینه‌کردن makespan
- کمینه‌کردن مجموع delay
- کمینه‌کردن تعداد محصولات دیرکرده
- کمینه‌کردن WIP
- کمینه‌کردن setup
- بیشینه‌کردن on-time delivery

این قابلیت باید ابتدا به‌صورت pilot محدود اجرا شود، نه در کل کارخانه.

### 6.7 سناریوسازی

سیستم باید بتواند سناریوهای What-if را اجرا کند.

نمونه سناریوها:

- اگر order A اولویت بالاتر بگیرد چه می‌شود؟
- اگر machine X برای 3 روز unavailable شود چه می‌شود؟
- اگر material Y دو هفته دیر برسد چه اثری دارد؟
- اگر عملیات Z outsource شود چه می‌شود؟
- اگر capacity یک WorkCenter افزایش یابد چه تأثیری دارد؟

خروجی مطلوب:

```text
ScenarioImpact
ChangedCompletionDates
ChangedDelayDays
NewBottlenecks
OrdersImproved
OrdersWorsened
```

### 6.8 بهبود مستمر

سیستم باید از انحراف‌های گذشته یاد بگیرد.

چرخه هدف:

```text
Planned Time
Actual Time
Deviation
Reason Category
Model Update
Planning Rule Improvement
```

مثلاً اگر یک operation همیشه 2 برابر زمان استاندارد طول می‌کشد، سیستم باید این deviation را تشخیص دهد و در پیش‌بینی‌های بعدی لحاظ کند.

### 6.9 کیفیت، NCR و rework

سیستم باید NCR را فقط به‌عنوان برچسب وضعیت نبیند، بلکه اثر زمانی آن را تحلیل کند.

قابلیت‌های هدف:

- تشخیص NCRهای اثرگذار بر delivery
- برآورد delay ناشی از NCR
- پیش‌بینی ریسک NCR برای process/part/supplier/machine
- اولویت‌دهی NCR بر اساس اثر بر critical path
- تفکیک delay ناشی از rework از delay ناشی از waiting یا shortage

### 6.10 نگهداری و تعمیرات پیش‌بینانه

اگر داده‌های ماشین کافی باشد، سیستم باید بتواند ریسک توقف ماشین‌های bottleneck را پیش‌بینی کند.

قابلیت‌های هدف:

- downtime risk
- maintenance priority
- effect of machine downtime on delivery
- best maintenance window
- machine reliability trend

---

## 7. داده‌های لازم

### 7.1 داده‌های موجود که باید استفاده شوند

از سیستم فعلی می‌توان این حوزه‌های داده را به‌عنوان شروع استفاده کرد:

- Product delivery commitments
- Orders
- Order tree
- BOM tree
- Routine
- RoutineOperations
- Process / ProcessType
- Planning snapshot
- Operation execution
- MachineData
- MRP shortage
- NCR/NPN
- Dashboard outputs

### 7.2 داده‌هایی که احتمالاً باید تکمیل شوند

برای رسیدن به هدف نهایی، احتمالاً این داده‌ها هم لازم می‌شوند:

- تقویم کاری واقعی
- شیفت‌ها
- ظرفیت روزانه WorkCenter
- ظرفیت روزانه Machine
- machine availability
- downtime history
- setup time matrix
- operator/team availability
- material ready date
- inspection duration
- outsourcing lead time
- manual priority changes
- reason code برای توقف یا تأخیر
- actual queue start/end
- rework start/end
- NCR open/close/effect dates

### 7.3 داده‌های مشتق‌شده پیشنهادی

برای تحلیل و ML بهتر، بهتر است لایه‌های تحلیلی ساخته شوند:

```text
OperationExecutionFact
OrderStateSnapshot
ProductStateSnapshot
CapacityCalendar
MaterialStatusSnapshot
NCRImpactFact
MachineAvailabilityFact
DelayReasonFact
PlanningDeviationFact
```

این‌ها الزاماً جایگزین جدول‌های فعلی نیستند؛ می‌توانند در یک analytics mart جداگانه ساخته شوند.

---

## 8. معماری پیشنهادی هدف

معماری مطلوب چندلایه است:

```text
Source Systems
  → Data Extraction / Read-only Connectors
    → Analytics Data Mart
      → Feature Store
        → ML Models
        → Optimization Engine
        → Simulation Engine
        → Recommendation Layer
          → Dashboard / LLM Assistant / Planner UI
```

### 8.1 Source Systems

سیستم‌های عملیاتی موجود، دیتابیس SQL Server، داده ماشین، MRP، QC/NCR و داشبوردها.

### 8.2 Analytics Data Mart

لایه‌ای جدا برای تحلیل، بدون دستکاری مستقیم سیستم عملیاتی.

### 8.3 Feature Store

محل نگهداری featureهای قابل استفاده برای مدل‌ها، مثل:

- historical duration deviation
- WorkCenter backlog
- shortage flag
- NCR open flag
- queue time
- machine utilization
- operation criticality

### 8.4 ML Models

مدل‌های پیش‌بینی:

- operation duration prediction
- delay risk prediction
- NCR risk prediction
- downtime prediction
- completion date estimation

### 8.5 Optimization Engine

موتور تصمیم‌گیری برای ساخت برنامه پیشنهادی با قیود.

روش‌های ممکن:

- constraint programming
- mixed-integer optimization
- heuristic scheduling
- metaheuristics
- dispatching rules enhanced by ML

### 8.6 Simulation Engine

موتور what-if برای تست سناریو قبل از اعمال در برنامه واقعی.

### 8.7 LLM Assistant

ایجنت/دستیار هوشمند برای:

- توضیح خروجی‌ها
- ساخت کوئری read-only
- مستندسازی
- root cause analysis
- تولید گزارش مدیریتی
- مقایسه سناریوها
- پرسش و پاسخ از روی داده‌ها و اسناد

---

## 9. سطح‌بندی بلوغ

### سطح 0: وضع موجود

- برنامه‌ریزی snapshot/backward
- داشبوردهای تفسیری
- تحلیل دستی
- ظرفیت محدود وارد برنامه‌ریزی اصلی نشده یا شواهد کافی وجود ندارد

### سطح 1: تحلیل و شفافیت

- تحلیل delay
- طبقه‌بندی علت‌ها
- گزارش deviation
- داشبورد bottleneck توصیفی

### سطح 2: پیش‌بینی

- پیش‌بینی زمان operation
- پیش‌بینی delay risk
- پیش‌بینی completion date
- هشدار زودهنگام

### سطح 3: پیشنهاد تصمیم

- recommendation برای اولویت‌دهی
- شناسایی operationهای critical
- پیشنهاد رفع bottleneck
- پیشنهاد تمرکز روی shortage/NCR اثرگذار

### سطح 4: شبیه‌سازی

- what-if سناریوها
- اثر تغییر اولویت
- اثر downtime
- اثر material delay
- اثر outsourcing

### سطح 5: برنامه‌ریزی ظرفیت‌دار محدود

- finite capacity scheduling برای یک scope محدود
- رعایت precedence و ظرفیت
- مقایسه برنامه پیشنهادی با برنامه فعلی

### سطح 6: بهبود مستمر بسته‌شده

- یادگیری از اجرای واقعی
- اصلاح پیش‌بینی‌ها
- ارزیابی تصمیم‌های قبلی
- بهبود قواعد برنامه‌ریزی
- human-in-the-loop optimization

---

## 10. نقشه راه پیشنهادی

### فاز 1: Data Audit و Loss Mapping

هدف: فهم دقیق اینکه زمان تولید کجا از دست می‌رود.

خروجی‌ها:

- taxonomy علت‌های delay
- نقشه داده‌های موجود و ناقص
- تعریف شاخص‌های پایه
- شناسایی data quality issues

### فاز 2: Operation Duration Prediction

هدف: پیش‌بینی زمان واقعی عملیات بر اساس سابقه.

خروجی‌ها:

- مدل پیش‌بینی مدت operation
- مقایسه standard time و actual/predicted time
- شناسایی operationهای با deviation بالا

### فاز 3: Delay Risk و Critical Path Early Warning

هدف: هشدار زودهنگام برای سفارش‌ها و عملیات‌های حساس.

خروجی‌ها:

- delay risk score
- critical operation list
- critical path per product
- top risk drivers

### فاز 4: Bottleneck و Capacity Visibility

هدف: دیدن بار واقعی WorkCenter/Machine و اثر آن روی delivery.

خروجی‌ها:

- WorkCenter load vs capacity
- machine backlog
- queue impact
- capacity gap

### فاز 5: What-if Simulation

هدف: تست تصمیم‌ها قبل از اجرا.

خروجی‌ها:

- scenario comparison
- impact on due dates
- bottleneck shifts
- affected products/orders

### فاز 6: Finite Capacity Scheduler Pilot

هدف: ساخت scheduler محدود برای یک خانواده محصول یا یک WorkCenter بحرانی.

خروجی‌ها:

- برنامه پیشنهادی ظرفیت‌دار
- مقایسه با برنامه فعلی
- میزان کاهش delay/makespan
- feedback از plannerها

### فاز 7: Rollout و Continuous Improvement

هدف: گسترش تدریجی و اتصال چرخه یادگیری.

خروجی‌ها:

- مدل‌های پایدارتر
- governance
- داشبورد مدیریتی
- human-in-loop workflow
- audit trail تصمیم‌ها

---

## 11. معیارهای موفقیت

معیارهای اصلی:

- کاهش lead time
- کاهش total delay days
- افزایش on-time delivery
- کاهش WIP
- کاهش waiting/queue time
- کاهش rework impact
- کاهش schedule deviation
- کاهش planner cycle time
- افزایش predictability

معیارهای تحلیلی:

- accuracy پیش‌بینی duration
- accuracy پیش‌بینی delay
- precision/recall هشدارهای critical
- درصد delayهای دارای root cause مشخص
- درصد تصمیم‌های پیشنهادی پذیرفته‌شده توسط planner

معیارهای سازمانی:

- اعتماد plannerها به سیستم
- توضیح‌پذیری خروجی‌ها
- کاهش وابستگی به دانش فردی
- سرعت پاسخ به سوالات مدیریتی
- امکان audit تصمیم‌ها

---

## 12. اصول ایمنی و حاکمیت

### 12.1 Human-in-the-loop

هیچ پیشنهاد AI/optimizer نباید بدون تأیید انسانی وارد برنامه عملیاتی شود، مگر بعد از بلوغ و کنترل کامل.

### 12.2 Read-only first

در فازهای اولیه، اتصال AI به دیتابیس باید read-only باشد. هرگونه update/delete/insert یا تغییر در برنامه عملیاتی باید فقط با درخواست صریح و فرآیند تأیید انجام شود.

### 12.3 Explainability

هر پیشنهاد باید قابل توضیح باشد:

```text
Recommendation
Reason
Expected Impact
Affected Orders
Risks
Confidence
Data Evidence
```

### 12.4 عدم جایگزینی ناگهانی سیستم فعلی

سیستم جدید ابتدا باید در حالت shadow mode اجرا شود؛ یعنی برنامه پیشنهادی تولید کند ولی برنامه واقعی را تغییر ندهد. بعد از مقایسه و اعتمادسازی، می‌توان وارد pilot عملیاتی شد.

### 12.5 کنترل کیفیت داده

اگر داده ناقص یا متناقض باشد، مدل باید uncertainty را اعلام کند و تصمیم قطعی ندهد.

---

## 13. نقش ایجنت‌ها

ایجنت‌ها باید بسته به نوع سوال، بین دو حالت تفکیک کنند:

### حالت A: شناخت وضع موجود

اگر سوال درباره سیستم فعلی، کوئری، stored procedure، dashboard، NCR، MRP، BOM، Order، Routing، `Query_TimeNeed` یا `Query_TimeNeedTable` است:

- ابتدا سند وضع موجود را بخوان.
- پاسخ را بر اساس سیستم فعلی بده.
- فقط کوئری read-only پیشنهاد بده مگر درخواست صریح تغییر داده وجود داشته باشد.
- قابلیت‌های هدف آینده را به سیستم فعلی نسبت نده.

### حالت B: طراحی هدف آینده / AI / Optimization

اگر سوال درباره بهبود، هوش مصنوعی، یادگیری ماشین، بهینه‌سازی، کاهش زمان تولید، کاهش critical path، finite capacity، prediction، simulation یا continuous improvement است:

- ابتدا سند وضع موجود را برای شناخت محدودیت‌ها بخوان.
- سپس این سند هدف آینده را برای جهت‌گیری بخوان.
- صریحاً تفکیک کن چه چیزی در سیستم فعلی وجود دارد و چه چیزی هدف آینده است.
- از پرش مستقیم به redesign کامل خودداری کن.
- پیشنهادها را به‌صورت مرحله‌ای، pilot-first و data-driven بده.

---

## 14. قالب پاسخ پیشنهادی ایجنت برای سوالات AI/Optimization

وقتی کاربر سوالی درباره بهینه‌سازی تولید با AI می‌پرسد، پاسخ بهتر است این ساختار را داشته باشد:

1. تشخیص نوع مسئله:
   - prediction
   - optimization
   - simulation
   - root cause analysis
   - dashboard/visibility
   - data quality

2. اتصال به وضع موجود:
   - از کدام جدول‌ها/خروجی‌های فعلی می‌توان شروع کرد؟
   - چه داده‌هایی کم است؟

3. خروجی هدف:
   - مدل، داشبورد، هشدار، recommendation یا optimizer؟

4. مسیر اجرای پیشنهادی:
   - pilot کوچک
   - داده موردنیاز
   - معیار موفقیت
   - ریسک‌ها

5. احتیاط‌ها:
   - human approval
   - read-only
   - shadow mode
   - عدم ادعای دقت بدون validation

---

## 15. مثال‌های پروژه مناسب برای شروع

### پروژه 1: طبقه‌بندی علت delay

هدف: برای هر delay مشخص شود علت اصلی چیست.

دسته‌ها:

- production delay
- material shortage
- NCR/rework
- capacity bottleneck
- waiting/queue
- machine downtime
- data issue
- unknown

### پروژه 2: پیش‌بینی duration عملیات

هدف: تخمین مدت واقعی operation قبل از شروع.

ورودی‌ها:

- routing standard time
- process
- part family
- WorkCenter/Machine
- historical actual time
- NCR/quality history
- queue/load indicators

### پروژه 3: هشدار زودهنگام critical operation

هدف: هر روز لیست operationهایی تولید شود که اگر انجام نشوند، محصول را وارد delay می‌کنند.

### پروژه 4: dashboard گلوگاه

هدف: نمایش WorkCenter/Machineهایی که بیشترین اثر را بر delivery دارند.

### پروژه 5: simulation تغییر اولویت

هدف: planner بتواند قبل از تغییر اولویت ببیند چه سفارش‌هایی بهتر و چه سفارش‌هایی بدتر می‌شوند.

### پروژه 6: scheduler ظرفیت‌دار محدود

هدف: ابتدا فقط برای یک WorkCenter یا خانواده محصول، برنامه ظرفیت‌دار آزمایشی ساخته شود.

---

## 16. ضدالگوها

این کارها در پروژه خطرناک یا زودهنگام هستند:

- شروع مستقیم با scheduler کامل کل کارخانه
- استفاده از AI بدون data quality assessment
- تغییر خودکار برنامه تولید بدون تأیید انسانی
- یکی دانستن LLM با optimizer
- نسبت‌دادن قابلیت‌های آینده به سیستم فعلی
- تمرکز روی مدل پیچیده قبل از تعریف مسئله ساده و قابل اندازه‌گیری
- ساخت داشبوردهای زیاد بدون actionability
- استفاده از prediction بدون سنجش accuracy و business impact

---

## 17. جمع‌بندی نهایی

هدف نهایی سازمان از AI/ML در تولید، ساخت یک سیستم تصمیم‌یار و بهینه‌ساز تدریجی است که بتواند از داده‌های واقعی یاد بگیرد، تأخیرها را زودتر پیش‌بینی کند، گلوگاه‌ها و مسیرهای بحرانی را قبل از بحران نشان دهد، سناریوهای تصمیم‌گیری را شبیه‌سازی کند و در نهایت به برنامه‌ریزی ظرفیت‌دار و بهبود مستمر برسد.

این مسیر باید تدریجی، قابل اندازه‌گیری، explainable و human-in-the-loop باشد.

فرمول خلاصه:

```text
Current System Understanding
  → Data Quality & Loss Mapping
    → Prediction
      → Risk & Critical Path Detection
        → Scenario Simulation
          → Finite Capacity Optimization
            → Continuous Improvement Loop
```

