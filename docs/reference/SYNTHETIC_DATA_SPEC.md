# SYNTHETIC_DATA_SPEC.md

## Synthetic operators

Default target: 500 operators/technicians.

Distribution:

```text
System proposes distribution based on imported WorkCenters and Machines.
User confirms/edits.
```

Skill level:

```text
Random simple level 1..5.
```

Multi-skill:

```text
Configurable ratio by user.
Some operators can work across WorkCenters.
```

Shift generation:

```text
Configurable by WorkCenter.
Example:
Machining: 40% Shift1, 40% Shift2, 20% Shift3
Assembly: 60% Shift1, 40% Shift2
QC: 50% Shift1, 50% Shift2
Packing: 100% Shift1
```

## Synthetic inventory

Initial inventory generated for BOM items using presets:

```text
Plenty
Normal
Shortage-heavy
Random Chaos
```

## Suppliers

Supplier presets:

```text
Reliable Suppliers
Mixed Suppliers
Unreliable Suppliers
Fast but Expensive Suppliers
```

Each BOM item can have multiple suppliers, one default.

When shortage occurs:

```text
Purchase request is created.
User selects supplier.
System suggests quantity = shortage + fixed safety stock percent.
User can edit final quantity.
```

Safety stock:

```text
Global fixed percentage for all BOM items.
```

Material price/cost is not modeled in V1.
