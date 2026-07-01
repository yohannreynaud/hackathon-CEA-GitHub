# Playbook: ITk Component Root-Cause Investigation (single component)

**Use when:** the user asks about a single, named ITk component in the UNHAPPY or GRAVEYARD stage and wants to understand why — e.g. "Read the comments to understand why Paris1390 is in UNHAPPY stage", "Why did Paris0042 go to GRAVEYARD?". For a database-wide survey of ALL modules in UNHAPPY/GRAVEYARD, see [UNHAPPY_GRAVEYARD_REPORT.md](UNHAPPY_GRAVEYARD_REPORT.md) instead.

## 1. Resolve the component
```json
{"tool": "find_component_summary_tool", "parameters": {"alternative_id": "Paris1390"}}
```
Confirms `currentStage` is `MODULE/UNHAPPY` or `MODULE/GRAVEYARD` and gives the ObjectId.

## 2. Read the comments — this is where the root cause usually lives
```json
{"tool": "find_comments_by_alternative_id_tool", "parameters": {"alternative_id": "Paris1390", "projection": {"comment": 1, "datetime": 1, "user_name": 1}}}
```
Read every comment chronologically. Operators typically log the defect (failed test, broken wirebonds, sensor issue, etc.) as a comment around the time the component was moved to UNHAPPY/GRAVEYARD — quote or summarize the relevant comment(s) in the answer. See [COMMENTS_QUERY_METHOD.md](../docs/COMMENTS_QUERY_METHOD.md) for the full comment-tool reference.

## 3. Find the stage the component was in right before UNHAPPY/GRAVEYARD

There is no dedicated "stage history" field — reconstruct it from the component's own sign-off/test records ordered by date:
```json
{"tool": "find_all_tool", "parameters": {"collection": "QC.result", "filter": {"component": "<id>"}, "projection": {"stage": 1, "testType": 1, "prodDB_record.date": 1}, "limit": 50}}
```
Sort the returned records by `prodDB_record.date` ascending. Find the record where `stage` is `MODULE/UNHAPPY` (or `MODULE/GRAVEYARD`); the **stage of the record immediately before it** (skipping any other UNHAPPY/GRAVEYARD entries) is `StageBeforeUnhappy`. If more than 50 test records exist, paginate with `skip`.

**Tip:** narrowing the same query to `testType: "SIGN_OFF"` first is usually enough to reconstruct the stage progression, since sign-offs mark stage completion — fall back to all test types only if no SIGN_OFF records are found.

## Output

Give a short narrative: current stage, the stage it came from, and a summary of the operator comment(s) explaining why.
