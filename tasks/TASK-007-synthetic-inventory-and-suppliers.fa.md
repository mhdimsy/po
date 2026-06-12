# TASK-007: موجودی و Supplier Synthetic

## هدف

داده synthetic برای مواد، موجودی و supplier را بساز.

## محدوده

- موجودی برای BOM Itemها
- presetهای موجودی: `Plenty`، `Normal`، `Shortage-heavy`، `Random Chaos`
- presetهای supplier: `Reliable`، `Mixed`، `Unreliable`، `Fast but Expensive`
- هر BOM Item بتواند چند supplier داشته باشد.
- هر BOM Item یک supplier پیش‌فرض داشته باشد.
- قیمت مواد در V1 مدل نشود.

## موجودیت‌ها

- Warehouse
- InventoryItem
- Supplier
- BOMItemSupplier
- PurchaseRequest

## پیاده‌سازی نکن

- material cost
- انتخاب خودکار supplier
- integration واقعی خرید
- UI مگر اینکه صریحاً درخواست شود

## مستندات الزامی بعد از اجرا

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/synthetic_materials.md`

## معیار پذیرش

- موجودی با preset قابل تولید باشد.
- supplierها با preset قابل تولید باشند.
- نگاشت BOM Item به supplier از alternativeها و default پشتیبانی کند.
