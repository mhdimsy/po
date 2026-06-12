# TASK-007: Synthetic Inventory and Suppliers

## Goal

synthetic material/inventory/supplier را بساز.

## Scope

- inventory for BOM Items
- inventory presets: Plenty, Normal, Shortage-heavy, Random Chaos
- supplier presets: Reliable, Mixed, Unreliable, Fast but Expensive
- each BOM Item can have multiple suppliers
- one default supplier per BOM Item
- material price is not modeled in V1

## Entities

- Warehouse
- InventoryItem
- Supplier
- BOMItemSupplier
- PurchaseRequest

## Do not implement

- material cost
- automatic supplier selection
- real purchasing integration
- UI unless explicitly requested

## Required documentation updates

- `logs/IMPLEMENTATION_LOG.md`
- `logs/CHANGELOG.md`
- `logs/DB_SCHEMA_CHANGE_LOG.md`
- `logs/TESTING_LOG.md`
- `docs/modules/synthetic_materials.md`

## Acceptance criteria

- Inventory can be generated with preset.
- Suppliers can be generated with preset.
- BOM Item supplier mapping supports alternatives + default.
