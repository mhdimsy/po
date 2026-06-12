# DATABASE_SCHEMA_DRAFT.md

This is a draft table list for SQL Server. Codex should implement migrations/models incrementally, not all at once if too large.

## Naming

Use snake_case or consistent Python-friendly names in application models. However, CSV import columns should accept existing factory-style names.

## Tables

### import_batches

```text
id
batch_code
source_name
created_at
status
notes
```

### import_files

```text
id
import_batch_id
file_name
file_type
row_count
status
```

### import_validation_issues

```text
id
import_batch_id
file_name
row_number
severity -- Error/Warning
code
message
field_name
raw_value
```

### products

```text
id
import_batch_id
source_product_id
code
title
family
version
configuration
```

### boms

```text
id
import_batch_id
source_bom_id
title
code
sap_code
usage_type_id
parts_group_id
is_critical
is_major_part
```

### bom_parts

```text
id
import_batch_id
bom_parent_id
bom_child_id
quantity
unit
```

### production_orders

```text
id
import_batch_id
source_order_id
code
product_id
bom_id
routing_id
status
priority_score
manual_priority_override
order_date
earliest_start_date
customer_requested_date
committed_delivery_date
internal_production_due_date
material_required_date
shipment_date
customer_name
```

### order_parts

```text
id
import_batch_id
parent_order_id
child_order_id
assignment_status_id
assignment_status_title
```

### routings

```text
id
import_batch_id
source_routine_id
bom_id
title
is_active
```

### routing_operations

```text
id
import_batch_id
source_routine_operation_id
routing_id
process_id
operation_sequence
operation_title
setup_duration_min
operation_duration_min
assembly_duration_min
requires_qc
is_interruptible
can_outsource
outsource_lead_time_min
```

### processes

```text
id
import_batch_id
source_process_id
title
process_type_id
```

### process_types

```text
id
import_batch_id
source_process_type_id
title
```

### work_centers

```text
id
import_batch_id
source_work_center_id
code
title
```

### machines

```text
id
import_batch_id
source_machine_id
work_center_id
code
title
barcode
status
```

### machine_capabilities

```text
id
machine_id
process_id
routing_operation_id nullable
is_primary
setup_factor
processing_factor
```

### operators

```text
id
code
full_name
home_work_center_id
status
hourly_cost nullable -- unused in V1
is_synthetic
```

### skills / operator_skills / operator_authorizations

```text
skills: id, code, title
operator_skills: id, operator_id, skill_id, level
operator_authorizations: id, operator_id, machine_id nullable, process_id nullable, routing_operation_id nullable
```

### calendars / shifts

```text
shifts: id, code, title, start_minute_of_day, end_minute_of_day
calendar_entries: id, owner_type, owner_id, date, shift_id, is_working, overtime_minutes
```

### material_items / warehouses / inventory_balances

```text
material_items: id, bom_id, code, title
warehouses: id, code, title
inventory_balances: id, material_item_id, warehouse_id, on_hand_qty, reserved_qty
```

### material_reservations / material_consumptions

```text
material_reservations: id, order_id, operation_id nullable, material_item_id, warehouse_id, qty, status
material_consumptions: id, order_id, operation_id, material_item_id, warehouse_id, qty, consumed_at
```

### suppliers / bom_item_suppliers / purchase_requests

```text
suppliers: id, code, title, preset_type, default_lead_time_min
bom_item_suppliers: id, material_item_id, supplier_id, is_default
purchase_requests: id, material_item_id, supplier_id nullable, shortage_qty, suggested_qty, final_qty, status, created_at, expected_arrival_at
```

### simulation_runs

```text
id
scenario_id
status
speed_factor
current_sim_time
started_at
paused_at
stopped_at
```

### event_store

```text
id
scenario_id
simulation_run_id nullable
event_type
aggregate_type
aggregate_id
event_time
created_at
payload_json
```

### snapshots

```text
id
scenario_id
simulation_run_id nullable
snapshot_time
created_at
reason
state_json or reference tables
```

### scenarios

```text
id
name
base_import_batch_id
parent_scenario_id nullable
base_snapshot_id nullable
status
created_at
settings_json
```

### resource_reservations

```text
id
scenario_id
operation_id
resource_type -- Machine/Operator/Material
resource_id
start_time
end_time
status -- Planned/Locked/Released/Consumed
```

### optimization_runs

```text
id
scenario_id
trigger_type
policy_json
risk_mode
frozen_window_minutes
status
created_at
score
accepted_at nullable
rejected_at nullable
```

### schedule_operations

```text
id
optimization_run_id
operation_id
machine_id
operator_id
start_time
end_time
status
score
```

### qc_checks / ncrs / ncr_approvals

```text
qc_checks: id, operation_id, status, result, created_at, completed_at
ncrs: id, code, related_order_id, related_operation_id, related_material_id, severity, defect_type, root_cause, responsible_area, status, disposition, impact_type, estimated_delay_min, required_approvals_json
ncr_approvals: id, ncr_id, step_name, status, expected_duration_min, requested_at, decided_at
```

### risk_rule_settings / risk_scores

```text
risk_rule_settings: id, key, value, updated_at
risk_scores: id, scenario_id, aggregate_type, aggregate_id, total_score, components_json, calculated_at
```
