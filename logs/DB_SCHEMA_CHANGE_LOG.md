# لاگ تغییرات schema دیتابیس

## 2026-06-12 - TASK-003/TASK-005

تعریف جدول‌های SQLModel اضافه شد:

- `import_batches`
- `import_files`
- `import_validation_issues`
- `boms`
- `bom_parts`
- `production_orders`
- `order_parts`
- `routings`
- `routing_operations`
- `process_types`
- `processes`
- `work_centers`
- `machines`
- `machine_processes`

یادداشت‌ها:

- جدول‌ها از طریق `SQLModel.metadata.create_all` و endpoint `POST /master-data/schema/create` ساخته می‌شوند.
- هنوز migration framework اضافه نشده است.
- ردیف‌های master واردشده به `import_batch_id` ارجاع می‌دهند.

## 2026-06-12 - TASK-006

تعریف جدول‌های SQLModel برای منابع انسانی synthetic اضافه شد:

- `operators`
- `skills`
- `operator_skills`
- `shifts`
- `work_center_shift_rules`
- `operator_availability`

یادداشت‌ها:

- `operators.home_work_center_id` به source id مربوط به WorkCenter واردشده اشاره می‌کند.
- `skills.process_id` به source id مربوط به Process واردشده اشاره می‌کند.
- `operator_skills.level` در بازه ۱ تا ۵ تولید می‌شود.
- برای این تسک migration framework اضافه نشده است و ساخت جدول‌ها همچنان از مسیر `POST /master-data/schema/create` انجام می‌شود.

## 2026-06-12 - TASK-007

تعریف جدول‌های SQLModel برای مواد، موجودی و supplier اضافه شد:

- `warehouses`
- `inventory_items`
- `inventory_balances`
- `suppliers`
- `bom_item_suppliers`
- `purchase_requests`

یادداشت‌ها:

- `inventory_items.bom_id` به source id مربوط به BOM واردشده اشاره می‌کند.
- `inventory_balances` موجودی را به warehouse و inventory item وصل می‌کند.
- `bom_item_suppliers` چند supplier برای هر item و یک default supplier را پشتیبانی می‌کند.
- `purchase_requests.supplier_id` nullable است تا انتخاب supplier توسط کاربر انجام شود.
- برای این تسک migration framework اضافه نشده است.

## 2026-06-12 - TASK-008

تعریف جدول‌های SQLModel برای event store و current state اضافه شد:

- `event_store`
- `current_order_states`
- `current_operation_states`
- `current_machine_states`
- `current_operator_states`
- `current_inventory_states`

یادداشت‌ها:

- `event_store.payload_json` به‌صورت JSON ذخیره می‌شود.
- `simulation_time` با واحد دقیقه و به‌صورت nullable ذخیره می‌شود.
- جدول‌های current state به `event_store.event_id` از طریق `last_event_id` ارجاع می‌دهند.
- برای این تسک migration framework اضافه نشده است.

## 2026-06-12 - TASK-009

تعریف جدول‌های SQLModel برای Scenario و Snapshot اضافه شد:

- `scenarios`
- `snapshots`

یادداشت‌ها:

- `scenarios.base_import_batch_id` به `import_batches.id` ارجاع می‌دهد.
- `scenarios.parent_scenario_id` برای fork از Scenario دیگر استفاده می‌شود.
- `scenarios.base_snapshot_id` برای ثبت Snapshot مبنای fork نگهداری می‌شود.
- `snapshots.metadata_json` و `snapshots.state_json` به‌صورت JSON ذخیره می‌شوند.
- برای این تسک migration framework اضافه نشده است.

## 2026-06-12 - TASK-010

تعریف جدول SQLModel برای اجرای simulation اضافه شد:

- `simulation_runs`

یادداشت‌ها:

- `simulation_runs.scenario_id` به `scenarios.id` ارجاع می‌دهد.
- `current_sim_time` با واحد دقیقه ذخیره می‌شود.
- `speed_factor` برای کنترل سرعت simulation نگهداری می‌شود.
- برای این تسک migration framework اضافه نشده است.

## 2026-06-12 - TASK-011

تعریف جدول‌های SQLModel برای optimizer اضافه شد:

- `optimization_runs`
- `schedule_operations`

یادداشت‌ها:

- `optimization_runs.scenario_id` به `scenarios.id` ارجاع می‌دهد.
- `schedule_operations.optimization_run_id` به `optimization_runs.id` ارجاع می‌دهد.
- `optimization_runs.policy_json` و `schedule_operations.reason_json` به‌صورت JSON ذخیره می‌شوند.
- cost model در این schema اضافه نشده است.
- برای این تسک migration framework اضافه نشده است.

## 2026-06-12 - TASK-014

تعریف جدول‌های SQLModel برای QC/NCR/Approval اضافه شد:

- `qc_checks`
- `ncrs`
- `ncr_approvals`
- `rework_orders`
- `replacement_orders`

یادداشت‌ها:

- `ncrs.qc_check_id` به `qc_checks.id` ارجاع می‌دهد.
- `ncr_approvals.ncr_id` به `ncrs.id` ارجاع می‌دهد.
- `rework_orders.ncr_id` و `replacement_orders.ncr_id` به `ncrs.id` ارجاع می‌دهند.
- cost model در این schema اضافه نشده است.
- برای این تسک migration framework اضافه نشده است.

## 2026-06-12 - TASK-015

تعریف جدول‌های SQLModel برای Risk Rule Engine اضافه شد:

- `risk_rule_settings`
- `risk_scores`

یادداشت‌ها:

- `risk_rule_settings` تنظیمات global ریسک و thresholdها را نگهداری می‌کند.
- `risk_scores` scoreهای محاسبه‌شده برای aggregateهای `Operation`، `Order` و `Scenario` را نگهداری می‌کند.
- `risk_scores.components_json` componentهای rule-based ریسک را به‌صورت JSON ذخیره می‌کند.
- تنظیمات ریسک هنوز per-scenario نیستند.
- برای این تسک migration framework اضافه نشده است.
