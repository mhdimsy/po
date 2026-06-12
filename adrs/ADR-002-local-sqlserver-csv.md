# ADR-002: Local SQL Server + CSV Import

## Status
Accepted

## Decision
Use local SQL Server for V1 and import seed data from multiple CSV files.

## Consequences
- No direct production DB connection.
- No Docker required.
- Import validation becomes a key feature.
- CSV names stay close to current factory table/column names.
