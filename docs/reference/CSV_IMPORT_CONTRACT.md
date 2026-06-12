# CSV_IMPORT_CONTRACT.md

## Import approach

V1 imports multiple CSV files. Column names should be close to the current factory SQL Server schema.

Flow:

```text
Upload/select CSV files
→ Validate Only
→ show errors/warnings
→ import only if no error and no warning
→ create ImportBatch
→ load master/order/routing/machine data
```

Warnings block import.

## Required CSV files

```text
bom.csv
bom_parts.csv
orders.csv
order_parts.csv
routings.csv
routing_operations.csv
processes.csv
process_types.csv
machines.csv
work_centers.csv
machine_processes.csv
```

## Suggested columns

### bom.csv

```csv
Id,Title,Code,SAPCode,UsageType_Id,PartsGroup_Id,PC
```

### bom_parts.csv

```csv
Id,BOMParent_Id,BOMChild_Id,Quantity,Unit
```

### orders.csv

```csv
Id,Code,Routine_Id,BOM_Id,ProductCode,CustomerName,OrderDate,EarliestStartDate,CustomerRequestedDate,CommittedDeliveryDate,InternalProductionDueDate,MaterialRequiredDate,ShipmentDate,GoodReciept
```

### order_parts.csv

```csv
Id,ParentOrder_Id,ChildOrder_Id,AssignmentStatus_Id,AssignmentStatusTitle
```

### routings.csv

```csv
Id,BOM_Id,Title,IsActive
```

### routing_operations.csv

```csv
Id,Routine_Id,Process_Id,OperationSequence,OperationDescription,SetupDuration,OperationDuration,AssemblyDuration,RequiresQC,IsInterruptible,CanOutsource,OutsourceLeadTimeMinutes
```

### processes.csv

```csv
Id,Title,ProcessType_Id
```

### process_types.csv

```csv
Id,Title
```

### work_centers.csv

```csv
Id,Code,Title
```

### machines.csv

```csv
Id,Title,Barcode,WorkCenter_Id,Status
```

### machine_processes.csv

```csv
Id,Machine_Id,Process_Id,IsPrimary,SetupFactor,ProcessingFactor
```

## Validation rules

### Blocking errors

```text
- Missing required file
- Missing required column
- Duplicate primary Id in same file
- FK target missing, e.g. BOMChild_Id not found in bom.csv
- Invalid date format
- Invalid number format
- Negative duration
- Operation without Routine_Id or Process_Id
- Machine without WorkCenter_Id
```

### Blocking warnings

The user decided warnings should also block import.

Treat these as warnings, but still block import:

```text
- Machine has no process capability
- BOM item has no title but has Id
- Order child assignment status is empty
- RoutingOperation has no standard duration
- Process has no ProcessType_Id
- Routing has no operation
- BOM parent has no child and is expected to be assembly
```

## Import output

After validation/import, return:

```text
ImportBatchId
TotalRows
ImportedRowsByFile
IssuesByFile
CreatedEntityCounts
```
