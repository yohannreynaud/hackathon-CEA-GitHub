# Playbook: ITk Component Stage Timeline

**Use when:** the user asks when a specific named ITk component (e.g. "Paris1313", a serial number like `20UPGM24830846`, or a bare module/PCB serial) reached, passed, or is currently at a given production stage — e.g. "When was Paris1313 assembled?", "Has Paris0090 been wirebonded yet?", "What stage is 20UPGB42000033 at?".

Answers "when did component X reach stage Y" and "what stage is X currently at" questions for a single, named component (module, bare module, or PCB).

## 1. Map the question to a stage code

The user names an activity, not a stage code. Translate first:

| User says... | Stage code (module) |
|---|---|
| assembled | `MODULE/ASSEMBLY` |
| wirebonded / wire-bonded | `MODULE/WIREBONDING` |
| initial warm tested | `MODULE/INITIAL_WARM` |
| parylene masked | `MODULE/PARYLENE_MASKING` |
| parylene coated | `MODULE/PARYLENE_COATING` |
| parylene unmasked | `MODULE/PARYLENE_UNMASKING` |
| received its OBWBP / wirebond-protected | `MODULE/WIREBOND_PROTECTION` |
| post-parylene warm tested | `MODULE/POST_PARYLENE_WARM` |
| thermal cycled | `MODULE/THERMAL_CYCLES` |
| final warm tested | `MODULE/FINAL_WARM` |
| final cold tested | `MODULE/FINAL_COLD` |
| final metrology'd | `MODULE/FINAL_METROLOGY` |
| graded / QC status | `MODULE/QC_STATUS` |

The table above is also the ordered production sequence (see [MODULE.md](../docs/components/MODULE.md) §2). Bare modules only have `BAREMODULERECEPTION`; PCBs go `PCB_POPULATION` → `PCB_QC` → `PCB_RECEPTION_MODULE_SITE` (see [BARE_MODULE.md](../docs/components/BARE_MODULE.md), [PCB.md](../docs/components/PCB.md)).

`MODULE/UNHAPPY` and `MODULE/GRAVEYARD` are off-path special stages — if the component is currently in one of these, see [COMPONENT_INVESTIGATION.md](COMPONENT_INVESTIGATION.md) instead.

## 2. Resolve the component

```json
{"tool": "find_component_summary_tool", "parameters": {"alternative_id": "Paris1313"}}
```
(use `serial_number` instead if given a serial). This returns the ObjectId (`_id`), `componentType`, and `currentStage` (sourced from `QC.module.status.latestSyncedStage`/`stage`).

## 3. Decide: reached, not yet reached, or in progress

Compare the requested stage's position in the ordered sequence above to `currentStage`'s position:
- `currentStage` index **>** requested stage index → the stage **was** passed → go to step 4 for the date.
- `currentStage` index **==** requested stage index → currently **at** that stage — still fetch step 4 for a "reached on" date if tests have already been uploaded.
- `currentStage` index **<** requested stage index → **not yet reached** — answer that directly, no further query needed.

## 4. Get the date

Per project convention (see [INTRO.md](../docs/INTRO.md) § Common Requests): the date is the **upload timestamp to LocalDB of the latest test at that stage** — not the earliest one.

```json
{"tool": "find_test_summary_tool", "parameters": {"component_id": "<id>", "stage": "MODULE/ASSEMBLY"}}
```

Take the maximum `date` among the returned tests. Report **date only** (no time) unless the user explicitly asked for a timestamp.

## Example

"When was Paris1313 assembled?"
1. Stage = `MODULE/ASSEMBLY`.
2. `find_component_summary_tool(alternative_id="Paris1313")` → id, `currentStage = MODULE/WIREBONDING` (later than ASSEMBLY → already passed).
3. `find_test_summary_tool(component_id="<id>", stage="MODULE/ASSEMBLY")` → tests dated e.g. 2026-04-20 and 2026-04-23 → answer: **23 avril** (the latest date).
