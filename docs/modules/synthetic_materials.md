# ماژول: synthetic_materials

## هدف

تولید داده synthetic برای مواد، موجودی اولیه، supplierها، نگاشت BOM item به supplier و purchase requestهای اولیه برای کمبودها.

## محدوده

- تولید `InventoryItem` برای BOM itemهای واردشده.
- تولید موجودی اولیه با presetهای `Plenty`، `Normal`، `Shortage-heavy` و `Random Chaos`.
- تولید supplier با presetهای `Reliable`، `Mixed`، `Unreliable` و `Fast but Expensive`.
- پشتیبانی از چند supplier برای هر BOM item.
- تعیین دقیقاً یک supplier پیش‌فرض برای هر BOM item در اجرای عادی generator.
- ایجاد `PurchaseRequest` بدون انتخاب supplier وقتی موجودی تولیدشده کمتر از safety stock باشد.

## موجودیت‌ها

- `Warehouse`
- `InventoryItem`
- `InventoryBalance`
- `Supplier`
- `BOMItemSupplier`
- `PurchaseRequest`

## سرویس‌ها

- `generate_inventory`
- `generate_suppliers`
- `ensure_warehouse`
- `ensure_inventory_item`
- `ensure_suppliers`

## endpointهای API

- `POST /synthetic/inventory/generate`
- `POST /synthetic/suppliers/generate`
- `GET /synthetic/inventory-items`
- `GET /synthetic/inventory-balances`
- `GET /synthetic/suppliers`
- `GET /synthetic/bom-item-suppliers`
- `GET /synthetic/purchase-requests`

## eventها

در TASK-007 event تولید نمی‌شود.

## جدول‌های current state

- `warehouses`
- `inventory_items`
- `inventory_balances`
- `suppliers`
- `bom_item_suppliers`
- `purchase_requests`

## وابستگی‌ها

- جدول `boms` برای ساخت inventory itemها.
- جدول `bom_parts` برای محاسبه safety stock ساده.
- ماژول `database` برای sessionهای SQLModel.

## قوانین validation

- `safety_stock_percent` باید بین ۰ و ۱۰ باشد.
- `suppliers_per_item` باید بین ۱ و ۱۰ باشد.
- preset نامعتبر inventory به `Normal` تبدیل می‌شود.
- preset نامعتبر supplier به `Mixed` تبدیل می‌شود.
- مدل price/cost مواد در V1 پیاده‌سازی نشده است.

## محدودیت‌های فعلی

- انتخاب supplier برای purchase request خودکار انجام نمی‌شود.
- integration واقعی خرید وجود ندارد.
- material cost مدل نشده است.
- داده‌های تولیدشده فعلاً generation batch مستقل ندارند.
- insert واقعی روی SQL Server در این محیط تست نشده است.

## تست‌ها

- `python3 -m compileall backend/app` موفق بود.
- routeهای `/synthetic/inventory/*`، `/synthetic/suppliers/*` و list endpointهای مواد ثبت شدند.
- generator روی SQLite in-memory با ۳ BOM item تست شد.
- برای ۳ BOM item، تعداد ۳ `InventoryItem` و ۳ `InventoryBalance` ساخته شد.
- برای هر BOM item دو supplier mapping ساخته شد و هر item دقیقاً یک default supplier داشت.
- در preset `Shortage-heavy`، تعداد ۳ `PurchaseRequest` بدون supplier انتخاب‌شده ساخته شد.
