# Playbook: ITk Sign-off Reports

**Use when:** the user wants a per-module list of sign-off dates and stages, or a per-stage count of sign-offs, since a given date — e.g. "Since April 1st, for all modules in IRFU, give me sign-off dates and stage in a table with columns AtlasId, Alias, Stage, Sign-off date", "For each stage, how many modules have been signed off since March 1st?". For simple throughput counts without per-module detail, see [PRODUCTION_RATE.md](PRODUCTION_RATE.md).

Both variants read `QC.result` documents with `testType: "SIGN_OFF"`, joined to the `component` collection for identification.

## Variant A — list of sign-off events (one row per module × stage)

```json
{"tool": "find_module_signoffs_tool", "parameters": {"institution": "IRFU", "start_date": "2026-04-01T00:00:00Z"}}
```
Returns rows already shaped as `{atlasId, alias, stage, signoff_date}`, sorted by date ascending. Default `limit` is 200 — if you suspect more rows, check `count_tool` on `QC.result` with the same filter (`testType: "SIGN_OFF"`, institution, date range) first, and paginate with `skip`.

Format the requested table exactly as asked, e.g.:

| AtlasId | Alias | Stage | Sign-off date |
|---|---|---|---|
| 20UPGM24830846 | Paris0076 | MODULE/WIREBONDING | 2026-04-23T14:02:11 |

Sign-off dates come back as ISO 8601 with an offset (e.g. `...+00:00` or `Z`); trim to `yyyy-mm-ddTHH:MM:SS` if the user asks for that exact format.

## Variant B — count per stage

```json
{"tool": "count_module_signoffs_by_stage_tool", "parameters": {"institution": "IRFU", "start_date": "2026-03-01T00:00:00Z"}}
```
Returns `{signoffs_by_stage: [{stage, count}, ...], total_signoffs}`, already deduplicated (one sign-off per (component, stage) pair) and sorted by count descending. Present as a Stage | Count table; mention `total_signoffs` as the grand total.

Omit `institution` for an all-sites report. For a "Paris" scope (IRFU + LPNHE + IJCLab), call once per institution and merge/sum — see [PRODUCTION_RATE.md](PRODUCTION_RATE.md) for that convention.
