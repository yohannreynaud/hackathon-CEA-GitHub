# Playbook: ITk Recent Stage Completions

**Use when:** the user asks which NEW modules have completed/passed a given production stage since a recent date — e.g. "What are the new modules which have successfully completed the FINAL_COLD stage at IRFU since last Wednesday". Answers with a list of modules, not just a count — for a pure count see [PRODUCTION_RATE.md](PRODUCTION_RATE.md).

## 1. Resolve the date

Convert relative expressions ("since last Wednesday", "in the past week") to an explicit ISO 8601 `start_date` using the current date.

## 2. Check volume, then pull the sign-off events for that stage

```json
{"tool": "count_tool", "parameters": {"collection": "QC.result", "filter": {"testType": "SIGN_OFF", "stage": "MODULE/FINAL_COLD", "prodDB_record.institution.code": "IRFU", "prodDB_record.date": {"$gte": "2026-06-24T00:00:00Z"}}}}
```

```json
{"tool": "find_module_signoffs_tool", "parameters": {"institution": "IRFU", "start_date": "2026-06-24T00:00:00Z"}}
```
Filter the returned rows client-side to `stage == "MODULE/FINAL_COLD"` — the tool doesn't take a stage filter itself. Each remaining row is one new completion; dedupe by `atlasId` if a module could appear twice (shouldn't normally happen, since sign-off is a one-time event per stage).

**Fallback:** if a stage genuinely has no `SIGN_OFF` records (check with `count_tool` — some intermediate stages may only be marked via their characteristic test, e.g. `WIREBONDING` for wirebonding), use `aggregate_tests_by_component_tool` instead:
```json
{"tool": "aggregate_tests_by_component_tool", "parameters": {"collection": "QC.result", "filter": {"stage": "MODULE/FINAL_COLD", "prodDB_record.institution.code": "IRFU", "prodDB_record.date": {"$gte": "2026-06-24T00:00:00Z"}}, "group_by": "component", "merge_component": true, "limit": 50}}
```
This groups by component first, avoiding the test-level pagination trap documented in [TOOL_MANUAL.md](../docs/TOOL_MANUAL.md) (the `find_modules_by_test_criteria_tool` pitfall) — prefer it over that tool when the goal is "give me all modules".

## Output

List the modules (AtlasId / Alias) and state the count, e.g. "12 modules: Paris0041, Paris0055, ...".
