# Playbook: ITk Production Rate

**Use for:** aggregate production-throughput questions about a time period — e.g. "How many production modules were wirebonded in Paris in April 2026?", "How many modules were assembled at LPNHE last month?". Answers are broken down per institution when the user says "Paris" (a regional grouping of IRFU + LPNHE + IJCLab, not a single institution code) or names one institute. For per-module lists rather than counts, see [SIGNOFF_REPORTS.md](SIGNOFF_REPORTS.md).

Counts how many **distinct modules** completed a given production stage/activity within a date range, optionally split by institution.

## 0. Resolve dates and institutions first

- Convert relative dates ("last month", "April 2026") into explicit ISO 8601 bounds, e.g. `start_date="2026-04-01T00:00:00Z"`, `end_date="2026-04-30T23:59:59Z"`.
- **"Paris" is not a single institution code.** In this database it refers to the three Paris-region institutes: `IRFU`, `LPNHE`, `IJCLab`. When the user says "in Paris", query each institution separately and sum, presenting the per-institution breakdown (see output format below). If a query unexpectedly returns 0 for an institute, double check the exact code casing with a quick `count_tool`.

## 1. Wirebonding rate — use the dedicated tool

```json
{"tool": "count_wirebonded_modules_tool", "parameters": {"institution": "IRFU", "start_date": "2026-04-01T00:00:00Z", "end_date": "2026-04-30T23:59:59Z"}}
```
This deduplicates by component (a module with several `WIREBONDING` test entries counts once). Call once per institution and sum.

## 2. Rate for any other stage — use sign-off counts

There is no per-stage dedicated counter besides wirebonding. Use the sign-off aggregation, which already deduplicates per (component, stage):
```json
{"tool": "count_module_signoffs_by_stage_tool", "parameters": {"institution": "IRFU", "start_date": "2026-04-01T00:00:00Z", "end_date": "2026-04-30T23:59:59Z"}}
```
Read the count for the relevant stage out of the returned `signoffs_by_stage` array. Call once per institution.

## Output format

Match the style the user expects — total first, then breakdown:
```
102 — IRFU: 72, LPNHE: 30
```
or, for a 3-institute "Paris" total including a zero:
```
32 — IRFU: 25, LPNHE: 0, IJCLab: 7
```
