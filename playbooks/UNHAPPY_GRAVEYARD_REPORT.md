# Playbook: ITk UNHAPPY / GRAVEYARD Survey

**Use for:** a database-wide survey of ALL modules currently in UNHAPPY or GRAVEYARD stage, together with their comments and the stage they were in right before — e.g. "I want a list of modules in UNHAPPY (respectively GRAVEYARD) stage, with the list of comments for each, and the stage before, as a table with columns AtlasId, Alias, CurrentStage, StageBeforeUnhappy, comments." For a single named component, see [COMPONENT_INVESTIGATION.md](COMPONENT_INVESTIGATION.md) instead — it's a smaller, faster version of the same recipe.

## 1. Find all modules currently in the target stage

```json
{"tool": "count_tool", "parameters": {"collection": "QC.module.status", "filter": {"componentType": "MODULE", "latestSyncedStage": "MODULE/UNHAPPY"}}}
```
```json
{"tool": "find_all_tool", "parameters": {"collection": "QC.module.status", "filter": {"componentType": "MODULE", "latestSyncedStage": "MODULE/UNHAPPY"}, "projection": {"component": 1}, "limit": 50}}
```
Paginate with `skip` if the count exceeds 50. Repeat for `MODULE/GRAVEYARD` if the user asked for both (report them as two separate lists/tables, per the "respectively" phrasing).

## 2. Identify the modules

```json
{"tool": "find_components_by_ids_tool", "parameters": {"component_ids": ["<id1>", "..."], "projection": {"serialNumber": 1, "componentType": 1}}}
```
The `alternative_id` field is auto-populated for modules — use it as `Alias`.

## 3. For each module: comments + stage-before

This is the same per-component recipe as [COMPONENT_INVESTIGATION.md](COMPONENT_INVESTIGATION.md), applied to every module in the list:

- Comments: `find_comments_by_component_tool(component_id="<id>")`
- Stage before UNHAPPY/GRAVEYARD: `find_all_tool(collection="QC.result", filter={"component": "<id>"}, projection={"stage": 1, "testType": 1, "prodDB_record.date": 1}, limit=50)`, sorted by date ascending — the stage of the record immediately preceding the UNHAPPY/GRAVEYARD entry is `StageBeforeUnhappy`.

This is naturally an N+1 query pattern (one comments call + one history call per module). Since UNHAPPY/GRAVEYARD populations are typically small (confirmed by the step-1 count), this is acceptable; if the count is large, tell the user and offer to narrow (e.g. by institution or FE chip version) before running dozens of calls.

## Output

One table per stage (UNHAPPY, GRAVEYARD):

| AtlasId | Alias | CurrentStage | StageBeforeUnhappy | Comments |
|---|---|---|---|---|
| 20UPGM... | Paris1390 | MODULE/UNHAPPY | MODULE/WIREBONDING | "broken wirebond found during pull test..." |
