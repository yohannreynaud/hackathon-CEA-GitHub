# Playbook: ITk Current-Stage Census

**Use when:** the user asks how many, or which, ITk modules are currently at a given production stage right now — e.g. "How many and which modules are currently at the FINAL_METROLOGY stage at IRFU?", optionally split across institutions (including the "Paris" grouping of IRFU + LPNHE + IJCLab). This is a live snapshot of current stage, not a historical count of past sign-offs — for that, see [SIGNOFF_REPORTS.md](SIGNOFF_REPORTS.md).

"Currently at stage X" means the component's **live** stage right now, stored in `QC.module.status` (`latestSyncedStage`, falling back to `stage`) — not a historical sign-off count, since a module can be signed off at a stage and then move past it later.

## 1. Check volume, then list the modules at that stage

```json
{"tool": "count_tool", "parameters": {"collection": "QC.module.status", "filter": {"componentType": "MODULE", "latestSyncedStage": "MODULE/FINAL_METROLOGY"}}}
```
If some documents only populate the legacy field, repeat with `"stage"` instead of `"latestSyncedStage"` and merge results (status docs may only have one of the two fields set).

```json
{"tool": "find_all_tool", "parameters": {"collection": "QC.module.status", "filter": {"componentType": "MODULE", "latestSyncedStage": "MODULE/FINAL_METROLOGY"}, "projection": {"component": 1}, "limit": 50}}
```
Paginate with `skip` if the count exceeds 50. Collect the `component` id strings.

## 2. Identify the modules (AtlasId / Alias)

```json
{"tool": "find_components_by_ids_tool", "parameters": {"component_ids": ["<id1>", "<id2>"], "projection": {"serialNumber": 1, "componentType": 1}}}
```
This tool already returns the full `properties` array and auto-adds a top-level `alternative_id` field for modules — no need to add a `properties.*` sub-projection.

## 3. Attribute institution (if the user asked "at IRFU")

`QC.module.status` doesn't carry institution directly. Attribute each module to the institute that signed it off at that stage, in one batch call:
```json
{"tool": "find_all_tool", "parameters": {"collection": "QC.result", "filter": {"component": {"$in": ["<id1>", "<id2>"]}, "stage": "MODULE/FINAL_METROLOGY", "testType": "SIGN_OFF"}, "projection": {"component": 1, "prodDB_record.institution.code": 1, "_id": 0}}}
```
Group by institution and count. Filter the module list from step 2 down to just the requested institution, or report the full per-institution breakdown.

## Output format

State the total, then the per-institution breakdown, e.g.:
```
At IRFU: 25
At LPNHE: 0
At IJCLab: 7
In Paris in total: 32
```
followed by the list of AtlasIds/Aliases if "which modules" was asked.
