# LocalDB MCP Server - Tool Manual

Complete documentation of all **34 MCP tools** available in the LocalDB MongoDB server (25 base tools + 5 unified tools + 4 production statistics / diagnostic tools).

## Table of Contents

- [Overview](#overview)
- [Recent Changes](#recent-changes)
- [Response Format Notes](#response-format-notes)
- [Base Operations](#base-operations)
- [Lightweight Tools](#lightweight-tools)
- [Unified Tools](#unified-tools)
- [Component Lookup](#component-lookup)
- [Quad Module Lookup](#quad-module-lookup)
- [QC Status](#qc-status)
- [Temporal Queries](#temporal-queries)
- [Advanced Queries](#advanced-queries)
- [Comment Tools](#comment-tools)
- [GridFS File Storage](#gridfs-file-storage)
- [Production Statistics](#production-statistics)
- [Diagnostic Tools](#diagnostic-tools)
- [Quick Reference](#quick-reference)
- [Error Handling](#error-handling)
- [Performance Tips](#performance-tips)

---

## Overview

The LocalDB MCP Server provides **34 specialized tools** for querying the LocalDB MongoDB database (25 base tools + 5 unified tools + 4 production statistics / diagnostic tools). All tools return JSON-formatted results and support server-side filtering for optimal performance.

**Prefer Unified Tools:** For component lookup and test queries, always use the **5 unified tools** (see [Unified Tools](#unified-tools) section) — they cover all component types with a single parameterized API.

**This manual documents individual tools.** For end-to-end recipes that chain several tools together to answer a recurring question (production rate, sign-off reports, current-stage census, UNHAPPY/GRAVEYARD investigation, etc.), see the [`playbooks/`](../playbooks/) directory and [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md) § "Question Playbooks".

### Configuration

Tools connect to MongoDB using environment variables:
- `MONGO_HOST`: MongoDB host (default: localhost)
- `MONGO_PORT`: MongoDB port (default: 27017)
- `MONGO_USERNAME`: Username for authentication (optional)
- `MONGO_PASSWORD`: Password for authentication (optional)
- `MONGO_AUTHDB`: Authentication database (default: admin)
- `DATABASE_NAME`: Database name (default: test)

---

## Recent Changes

| Date | Tool | Change | Status |
|------|------|--------|--------|
| 2026-06-30 | **Unified Tools** | **Added 5 unified tools** and **removed 13 redundant legacy tools**: `find_component_by_serial_unified_tool`, `find_component_by_alternative_id_unified_tool`, `find_production_components_unified_tool`, `find_latest_test_unified_tool`, `find_components_with_valid_tests_unified_tool`. All 13 equivalence tests passed before removal. See [Unified Tools](#unified-tools) section. | ✅ Done |
| 2026-05-06 | `find_modules_by_test_criteria_tool` | **Fixed critical bug**: Tool was returning all component types (front-end chips, bare modules, etc.) instead of only modules. Added `componentType: "module"` filter to component query. **Note**: Pagination applies to TESTS not MODULES — see warning below. | ✅ Fixed |
| 2025-XX-XX | `find_components_by_ids_tool`, `find_modules_by_test_criteria_tool`, `aggregate_tests_by_component_tool` | Added three new advanced query tools for batch component lookup, module finding with test criteria, and MongoDB aggregation with component merge. | ✅ Added |
| 2025-XX-XX | `find_anomalous_bare_module_mass_tool` | Fixed server-side bug where tool incorrectly passed `{"$oid": "..."}` dict to MongoDB queries, causing "unknown operator: $oid" error. Now correctly extracts hex string from bson.json_util format. | ✅ Fixed |

---

## Response Format Notes

### ObjectId Serialization
All tools that return MongoDB documents serialize ObjectIds using `bson.json_util.dumps()`, which produces the **extended JSON format**:

```json
"_id": {"$oid": "67c981355ae416616e2a8974"}
```

**Important:** When parsing these responses with standard `json.loads()`, the `_id` field becomes a Python dict `{"$oid": "..."}`. If you need to use this ID in subsequent queries, extract the string value: `object_id = doc["_id"]["$oid"]`.

### Empty Results
| Scenario | Return Value | Applies To |
|----------|--------------|-----------|
| Single document not found | `null` | `find_one_tool`, `find_component_by_id_tool`, `find_latest_*_test_tool` |
| Empty result set (multi-document) | `[]` | All `find_all_*_tool`, `find_*_by_*_tool` (multi-document queries) |
| Query error | `Error: <description>` | All tools |
| GridFS file too large | `{"error": "FILE_TOO_LARGE", ...}` | `gridfs_download_file_tool` |

---

## Base Operations

**See also:** [INTRO.md](INTRO.md) for component type overview and [README.md](../README.md) for server configuration.

### Important: Component References in QC Collections

**The `component` field in `QC.result` and `QC.module.status` collections stores ObjectId as a STRING (not BSON ObjectId).**

This means queries should use:
```json
{"component": "67c981355ae416616e2a8974"}  // ✅ String format
```
Not:
```json
{"component": ObjectId("67c981355ae416616e2a8974")}  // ❌ BSON format (won't match)
```

**Exception:** The `_id` field in all collections stores BSON ObjectId, which is automatically serialized as `{"$oid": "..."}` in JSON responses (see [Response Format Notes](#response-format-notes)).

---

### `find_one_tool`

Retrieve a single document from any MongoDB collection.

**Tip:** Supply a projection (e.g., `{"serialNumber": 1, "currentStage": 1}`) to limit returned fields and stay well within the token budget.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection` | string | Yes | Collection name |
| `filter` | object | No | MongoDB query filter |
| `id` | string | No | ObjectId to search for |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_one_tool",
  "parameters": {
    "collection": "component",
    "filter": {"serialNumber": "20UPGM24830846"}
  }
}
```

---

### `find_all_tool`

Retrieve multiple documents from any MongoDB collection.

**IMPORTANT:** Default limit is 10. Hard server cap is 50. Do not set limit > 10 unless you have verified (via `count_tool`) that the result set is small and each document is compact. Use a projection to return only the fields you need.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `collection` | string | Yes | - | Collection name |
| `filter` | object | No | `{}` | MongoDB query filter |
| `limit` | integer | No | 10 | Maximum results (hard cap: 50) |
| `skip` | integer | No | 0 | Results to skip |
| `projection` | object | No | - | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_all_tool",
  "parameters": {
    "collection": "QC.result",
    "filter": {"testType": "MASS_MEASUREMENT"},
    "limit": 5,
    "projection": {"testType": 1, "stage": 1, "passed": 1}
  }
}
```

---

## Lightweight Tools

These three tools are optimized for minimal token usage and should be preferred when you only need identification or counting information.

**See also:** [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md) § "Prefer lightweight summary tools" for usage guidelines.

### `count_tool`

Count documents in a collection matching a filter — returns a single number. Use this BEFORE any `find_*_tool` call to verify the result volume is manageable. A count query is very fast and uses zero token budget.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection` | string | Yes | MongoDB collection name (e.g., 'component', 'QC.result', 'QC.module.status', 'comments', 'fs.files') |
| `filter` | object | No | MongoDB query filter (optional) |

**Returns:** JSON object: `{"collection": "...", "filter": {...}, "count": N}`

**Examples:**
```json
// Count all modules
{
  "tool": "count_tool",
  "parameters": {
    "collection": "component",
    "filter": {"componentType": "module"}
  }
}

// Count tests for a component at a stage
{
  "tool": "count_tool",
  "parameters": {
    "collection": "QC.result",
    "filter": {"component": "<id>", "stage": "MODULE/ASSEMBLY"}
  }
}
```

---

### `find_component_summary_tool`

Return compact identification fields for component(s) — much smaller than full documents. Returned fields: `serialNumber`, `componentType`, `currentStage`, `properties`, creation/modification timestamps. Children and test blobs are excluded.

**Note on currentStage:** The `currentStage` field is retrieved from the `QC.module.status` collection (not from the component document itself), using the `latestSyncedStage` or `stage` field.

Use this for:
- Confirming a component exists and retrieving its ObjectId
- Checking the current production stage
- Reading properties (FECHIP_VERSION, ALTERNATIVE_IDENTIFIER, etc.)

Only call `find_component_by_*_tool` / `find_one_tool` when you genuinely need the full document (children list, full property set).

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `serial_number` | string | No | - | Exact serial number (e.g., '20UPGM24830846') |
| `alternative_id` | string | No | - | Alternative identifier (e.g., 'Paris0076') — only for modules |
| `component_type` | string | No | - | Filter by type ('module', 'bare_module', 'module_pcb') |
| `limit` | integer | No | 5 | Maximum results |

**Note:** Provide at least one of: `serial_number`, `alternative_id`, or `component_type`.

**Example:**
```json
{
  "tool": "find_component_summary_tool",
  "parameters": {
    "alternative_id": "Paris0076"
  }
}
```

---

### `find_test_summary_tool`

Return a compact list of tests for a component — type, stage, pass/fail, date only. Use this to discover what tests exist for a component before fetching full test documents. This is orders of magnitude smaller than `find_quad_module_tests_by_stage_tool`.

**Workflow:**
1. `find_test_summary_tool` → see test types and dates
2. `find_latest_test_unified_tool` → fetch the specific test you need

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `component_id` | string | Yes | - | ObjectId string of the component |
| `stage` | string | No | - | Filter by production stage |
| `test_type` | string | No | - | Filter by test type |
| `limit` | integer | No | 10 | Maximum results |

**Returns:** JSON array of compact test documents (testType, stage, passed, date)

**Example:**
```json
{
  "tool": "find_test_summary_tool",
  "parameters": {
    "component_id": "67c981355ae416616e2a8974"
  }
}
```

---

## Unified Tools

**See also:** [unification_tool.md](changelog/unification_tool.md) for factorization details, [RESULTAT_UNIFIED_TOOLS.md](changelog/RESULTAT_UNIFIED_TOOLS.md) for test validation, [AMELIORATIONS.md](changelog/AMELIORATIONS.md) § "Priorité 1 : Factoriser les Tools Redondants"

### Overview

The **Unified Tools** replaced 13 redundant legacy tools in a refactoring effort documented in [AMELIORATIONS.md](changelog/AMELIORATIONS.md). The legacy tools have been removed — the unified tools are now the only way to perform these queries.

**Key design principles:**
- **Single implementation per operation**: one tool covers all component types via an optional `component_type` parameter
- **Flexible**: omit `component_type` to search across all types, or specify it for type-scoped queries
- **Validated**: all 13 equivalence tests passed before the legacy tools were removed (see [RESULTAT_UNIFIED_TOOLS.md](changelog/RESULTAT_UNIFIED_TOOLS.md))

---

### `find_component_by_serial_unified_tool`

**UNIFIED TOOL** - Find a component by its serial number. Replaced: `find_component_by_serial_tool`, `find_flex_pcb_by_serial_tool`, `find_bare_module_by_serial_tool`, `find_quad_module_by_serial_tool` (all removed).

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `serial_number` | string | Yes | - | Serial number to search (e.g., '20UPGM24830846' or '20UPGPQ2830070') |
| `component_type` | string | No | - | Filter by type: 'module', 'bare_module', 'module_pcb'. **Omit for generic search across all types** |
| `partial` | boolean | No | false | Enable partial match (regex prefix search) |
| `limit` | integer | No | 5 | Maximum results for partial matches |
| `projection` | object | No | - | Fields to include/exclude (e.g., {"serialNumber": 1, "componentType": 1}) |

**Parameter by component type:**
| Component type | `component_type` value |
|----------------|----------------------|
| Quad module | `"module"` |
| Flex PCB | `"module_pcb"` |
| Bare module | `"bare_module"` |
| Any / generic | *(omit)* |

**Examples:**
```json
// Generic search (replaces find_component_by_serial_tool)
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGM24830846",
    "projection": {"serialNumber": 1, "componentType": 1, "currentStage": 1}
  }
}

// Module-specific (replaces find_quad_module_by_serial_tool)
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGM24830846",
    "component_type": "module",
    "projection": {"serialNumber": 1, "properties.ALTERNATIVE_IDENTIFIER": 1}
  }
}

// PCB-specific (replaces find_flex_pcb_by_serial_tool)
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGPQ2830070",
    "component_type": "module_pcb",
    "projection": {"serialNumber": 1, "properties.PCB_DESIGN_VERSION": 1}
  }
}

// Bare module (replaces find_bare_module_by_serial_tool)
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGB42000033",
    "component_type": "bare_module",
    "projection": {"serialNumber": 1, "properties.FECHIP_VERSION": 1}
  }
}
```

**Note:** The MongoDB filter generated is **strictly equivalent** to legacy tools. For example, `component_type: "module"` generates: `{"serialNumber": "20UPGM24830846", "componentType": "module"}`

---

### `find_component_by_alternative_id_unified_tool`

**UNIFIED TOOL** - Find a component by its alternative identifier. Replaced: `find_quad_module_by_alternative_id_tool` (removed).

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `alternative_id` | string | Yes | - | Alternative identifier (e.g., 'Paris0076', 'Lyon0001') |
| `component_type` | string | No | - | Filter by type: 'module', 'bare_module', 'module_pcb'. **Omit for generic search** |
| `partial` | boolean | No | false | Enable partial match |
| `limit` | integer | No | 5 | Maximum results |
| `projection` | object | No | - | Fields to include/exclude |

**Examples:**
```json
// Module by alternative ID (replaces find_quad_module_by_alternative_id_tool)
{
  "tool": "find_component_by_alternative_id_unified_tool",
  "parameters": {
    "alternative_id": "Paris0076",
    "component_type": "module",
    "projection": {"serialNumber": 1, "componentType": 1, "properties.ALTERNATIVE_IDENTIFIER": 1}
  }
}

// Generic alternative ID search (any component type)
{
  "tool": "find_component_by_alternative_id_unified_tool",
  "parameters": {
    "alternative_id": "Paris0076",
    "projection": {"serialNumber": 1, "componentType": 1}
  }
}
```

**Note — scope:** When `component_type` is **omitted**, the search spans **all** component types. To restrict to modules only, always pass `component_type: "module"`. Example filter: `{"componentType": "module", "properties": {"$elemMatch": {"code": "ALTERNATIVE_IDENTIFIER", "value": "Paris0076"}}}`

---

### `find_production_components_unified_tool`

**UNIFIED TOOL** - Find production components with optional filters. Replaced: `find_production_quad_modules_tool`, `find_production_flex_pcbs_tool`, `find_production_bare_modules_tool` (all removed).

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `component_type` | string | No | - | Component type: 'module', 'bare_module', 'module_pcb' |
| `fe_chip_version` | string | No | - | FE chip version: '0'=RD53A, '1'=ITkpix_v1, '2'=ITkpix_v1.1, '3'=ITkpix_v2 |
| `is_preproduction` | boolean | No | - | Filter by preproduction status (modules only) |
| `manufacturer` | string | No | - | Filter by manufacturer (PCBs only) |
| `vendor` | string | No | - | Filter by vendor (bare modules only) |
| `with_sensor` | boolean | No | false | Only modules with sensor (bare modules only) |
| `limit` | integer | No | 10 | Maximum results (hard cap: 50) |
| `skip` | integer | No | 0 | Results to skip for pagination |
| `projection` | object | No | - | Fields to include/exclude |

**CAUTION:** Large collection. Use `count_tool` first to check volume.

**Parameter by component type:**
| Component type | `component_type` value |
|----------------|----------------------|
| Quad module | `"module"` |
| Flex PCB | `"module_pcb"` |
| Bare module | `"bare_module"` |

**Examples:**
```json
// Production modules (replaces find_production_quad_modules_tool)
{
  "tool": "find_production_components_unified_tool",
  "parameters": {
    "component_type": "module",
    "fe_chip_version": "3",
    "is_preproduction": false,
    "limit": 10,
    "projection": {"serialNumber": 1, "properties.FECHIP_VERSION": 1}
  }
}

// Production PCBs (replaces find_production_flex_pcbs_tool)
{
  "tool": "find_production_components_unified_tool",
  "parameters": {
    "component_type": "module_pcb",
    "manufacturer": "Tecnomec",
    "limit": 10,
    "projection": {"serialNumber": 1, "properties.PCB_DESIGN_VERSION": 1}
  }
}

// Production bare modules (replaces find_production_bare_modules_tool)
{
  "tool": "find_production_components_unified_tool",
  "parameters": {
    "component_type": "bare_module",
    "fe_chip_version": "3",
    "vendor": "LPNHE",
    "with_sensor": true,
    "limit": 10,
    "projection": {"serialNumber": 1, "properties.FECHIP_VERSION": 1}
  }
}
```

**Note:** Filters on `properties` use MongoDB `$elemMatch` with `$all` for multiple property filters, generating **strictly equivalent queries** to legacy tools.

**Note — implicit PCB production filter:** When `component_type: "module_pcb"` is used, the tool automatically adds `PCB_DESIGN_VERSION: {$in: ["4", "5"]}` to restrict results to production PCB designs only. If you need all PCBs regardless of design version, use `find_all_tool` directly on the `component` collection with `filter: {"componentType": "module_pcb"}`.

---

### `find_latest_test_unified_tool`

**UNIFIED TOOL** - Find the latest test of a specific type for a component at a given stage. Replaced: `find_latest_quad_module_test_tool`, `find_latest_pcb_test_tool`, `find_latest_bare_module_test_tool` (all removed).

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `component_id` | string | Yes | Component ObjectId |
| `test_type` | string | Yes | Test type (e.g., 'MASS_MEASUREMENT', 'IV_MEASURE') |
| `stage` | string | Yes | Production stage (e.g., 'MODULE/ASSEMBLY', 'PCB_RECEPTION_MODULE_SITE', 'BAREMODULERECEPTION') |
| `projection` | object | No | Fields to include/exclude |

**Stage by component type:**
| Component | `stage` value |
|-----------|--------------|
| Quad module | any (specify explicitly) |
| Flex PCB | `"PCB_RECEPTION_MODULE_SITE"` |
| Bare module | `"BAREMODULERECEPTION"` |

**Examples:**
```json
// Latest module test (replaces find_latest_quad_module_test_tool)
{
  "tool": "find_latest_test_unified_tool",
  "parameters": {
    "component_id": "67c981355ae416616e2a8974",
    "test_type": "MASS_MEASUREMENT",
    "stage": "MODULE/ASSEMBLY",
    "projection": {"testType": 1, "passed": 1, "results.MASS": 1}
  }
}

// Latest PCB test (replaces find_latest_pcb_test_tool)
{
  "tool": "find_latest_test_unified_tool",
  "parameters": {
    "component_id": "6703f4b8ef991c0043ea26c4",
    "test_type": "IV_MEASURE",
    "stage": "PCB_RECEPTION_MODULE_SITE",
    "projection": {"testType": 1, "passed": 1, "results.IV_MEASURE": 1}
  }
}

// Latest bare module test (replaces find_latest_bare_module_test_tool)
{
  "tool": "find_latest_test_unified_tool",
  "parameters": {
    "component_id": "63d148b40499130036777fe4",
    "test_type": "MASS_MEASUREMENT",
    "stage": "BAREMODULERECEPTION",
    "projection": {"testType": 1, "passed": 1, "results.MASS": 1}
  }
}
```

**Note:** Uses the underlying `find_latest_test_for_component` function with identical sort criteria: `[("prodDB_record.date", -1), ("results.property.MEASUREMENT_DATE", -1), ("sys.cts", -1)]`. **Stage parameter is now required** to ensure explicit stage specification.

---

### `find_components_with_valid_tests_unified_tool`

**UNIFIED TOOL** - Find components with valid tests of specified types. Replaced: `find_pcb_with_valid_tests_tool`, `find_bare_modules_with_valid_tests_tool` (both removed).

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `component_type` | string | Yes | - | Component type: `'PCB'`, `'BARE_MODULE'`, or `'MODULE'` (uppercase, for consistency with QC.module.status collection values) |
| `test_types` | array | No | - | List of test types to check for validity |
| `limit` | integer | No | 10 | Maximum results (hard cap: 50) |
| `skip` | integer | No | 0 | Results to skip for pagination |
| `projection` | object | No | Fields to include/exclude |

**CAUTION:** Large collection. Use `count_tool` first to check volume.

**Parameter by component type:**
| Component | `component_type` value |
|-----------|----------------------|
| Flex PCB | `"PCB"` |
| Bare module | `"BARE_MODULE"` |
| Quad module | `"MODULE"` → stage `MODULE/ASSEMBLY` |

**Examples:**
```json
// PCBs with valid tests (replaces find_pcb_with_valid_tests_tool)
{
  "tool": "find_components_with_valid_tests_unified_tool",
  "parameters": {
    "component_type": "PCB",
    "test_types": ["MASS", "METROLOGY", "VISUAL_INSPECTION"],
    "limit": 10,
    "projection": {"serialNumber": 1, "componentType": 1}
  }
}

// Bare modules with valid tests (replaces find_bare_modules_with_valid_tests_tool)
{
  "tool": "find_components_with_valid_tests_unified_tool",
  "parameters": {
    "component_type": "BARE_MODULE",
    "test_types": ["MASS_MEASUREMENT", "VISUAL_INSPECTION"],
    "limit": 10,
    "projection": {"serialNumber": 1, "componentType": 1}
  }
}
```

**Note:** Filters on `QC_results_pdb` use stage-specific paths that are resolved automatically from `component_type`:

| `component_type` | Stage path used |
|------------------|----------------|
| `PCB` | `QC_results_pdb.PCB_RECEPTION_MODULE_SITE.<test_type>` |
| `BARE_MODULE` | `QC_results_pdb.BAREMODULERECEPTION.<test_type>` |
| `MODULE` | `QC_results_pdb.MODULE/ASSEMBLY.<test_type>` |

---

## Component Lookup

**See also:** [INTRO.md](INTRO.md) for component type overview.

### `find_component_by_id_tool`

Find a component by its MongoDB ObjectId.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `component_id` | string | Yes | ObjectId (24-char hex) |
| `projection` | object | No | Fields to include/exclude (e.g., {"serialNumber": 1, "currentStage": 1}) |

**Example:**
```json
{
  "tool": "find_component_by_id_tool",
  "parameters": {
    "component_id": "67c981355ae416616e2a8974",
    "projection": {"serialNumber": 1, "componentType": 1}
  }
}
```

---

### `find_components_by_ids_tool`

Batch fetch component details for multiple ObjectIds in a single query. This is the primary tool for resolving multiple component references from test results efficiently. For modules, it extracts the alternative_id from properties and includes it as a top-level field.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `component_ids` | array | Yes | List of ObjectId strings to look up |
| `projection` | object | No | Optional projection to limit returned fields (merged with default compact projection) |

**Returns:** JSON array of compact component documents with alternative_id extracted for module components

**Example:**
```json
{
  "tool": "find_components_by_ids_tool",
  "parameters": {
    "component_ids": ["67c981355ae416616e2a8974", "67c981355ae416616e2a8975"],
    "projection": {"serialNumber": 1, "componentType": 1, "currentStage": 1}
  }
}
```

---

## Quad Module Lookup

**See also:** [MODULE.md](components/MODULE.md) for production stages, test types, and quad module details.

### `find_quad_module_tests_by_stage_tool`

Find all tests for a quad module at a specific production stage.

**Test documents can be large** (pixel maps, histograms). Use `find_test_summary_tool` first to see how many tests exist and what their types are, then call this tool for the specific test you need.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `component_id` | string | Yes | Quad module ObjectId |
| `stage` | string | Yes | Production stage |
| `limit` | integer | No | Default: 5 (hard cap: 50) |
| `skip` | integer | No | Default: 0 |
| `projection` | object | No | Fields to include/exclude |

**Stages:** `MODULE/ASSEMBLY`, `MODULE/WIREBONDING`, `MODULE/INITIAL_WARM`, `MODULE/PARYLENE_MASKING`

**Example:**
```json
{
  "tool": "find_quad_module_tests_by_stage_tool",
  "parameters": {
    "component_id": "67c981355ae416616e2a8974",
    "stage": "MODULE/WIREBONDING",
    "projection": {"testType": 1, "passed": 1, "prodDB_record.date": 1}
  }
}
```

---

### `find_quad_modules_with_visual_inspection_issues_tool`

Find quad modules with visual inspection issues.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `stage` | string | No | MODULE/ASSEMBLY | Production stage |
| `severity` | integer | No | 2 | Min severity (1=Good, 2=Issues, 3=Bad) |
| `limit` | integer | No | 20 | Max results (hard cap: 50) |
| `skip` | integer | No | 0 | Skip |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_quad_modules_with_visual_inspection_issues_tool",
  "parameters": {
    "severity": 3,
    "limit": 50,
    "projection": {"testType": 1, "stage": 1, "results.SMD_COMPONENTS_PASSED_QC": 1}
  }
}
```

---

### `find_quad_modules_with_wirebonding_problems_tool`

Find quad modules with wirebonding problems.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `min_pull_strength` | float | No | 7.0 | Min acceptable pull strength (grams) |
| `max_heel_breaks` | float | No | - | Max acceptable heel break % |
| `limit` | integer | No | 20 | Max results (hard cap: 50) |
| `skip` | integer | No | 0 | Skip |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_quad_modules_with_wirebonding_problems_tool",
  "parameters": {
    "min_pull_strength": 5.0,
    "max_heel_breaks": 10.0,
    "projection": {"testType": 1, "results.PULL_STRENGTH": 1}
  }
}
```

---

## QC Status

**See also:** [MODULE.md](components/MODULE.md), [BARE_MODULE.md](components/BARE_MODULE.md), [PCB.md](components/PCB.md) for component-specific QC details.

### `find_quad_modules_in_status_tool`

Find quad modules in the QC.module.status collection.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `component_type` | string | No | MODULE | Type of component (default: "MODULE") |
| `fe_chip_version` | string | No | - | Filter by FE chip version (optional) |
| `has_test` | string | No | - | Filter by presence of a specific test type (optional) |
| `limit` | integer | No | 10 | Maximum documents per page (hard cap: 50) |
| `skip` | integer | No | 0 | Documents to skip for pagination |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_quad_modules_in_status_tool",
  "parameters": {
    "component_type": "MODULE",
    "fe_chip_version": "3",
    "has_test": "MASS_MEASUREMENT",
    "limit": 10,
    "projection": {"serialNumber": 1, "properties.FECHIP_VERSION": 1}
  }
}
```

---

## Temporal Queries

**See also:** [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md) § "Rule 1 — Count before you fetch" for date-range best practices.

### `find_tests_by_date_range_tool`

Find tests performed within a specific date range.

**CAUTION:** Date-range queries on QC.result can return thousands of large documents. Always supply `test_type` to narrow the search, and use a small limit (default 5). Call `count_tool` first to gauge volume.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `start_date` | string | Yes | Start date (ISO format) |
| `end_date` | string | No | End date (ISO format) |
| `test_type` | string | No | Filter by test type |
| `limit` | integer | No | Default: 5 (hard cap: 50) |
| `skip` | integer | No | Default: 0 |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_tests_by_date_range_tool",
  "parameters": {
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T23:59:59Z",
    "test_type": "MASS_MEASUREMENT",
    "projection": {"testType": 1, "passed": 1, "prodDB_record.date": 1}
  }
}
```

---

### `find_components_by_date_range_tool`

Find components created or modified within a date range.

**CAUTION:** Provide `component_type` to narrow the search.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `start_date` | string | Yes | - | Start date (ISO) |
| `end_date` | string | No | - | End date (ISO) |
| `component_type` | string | No | - | Component type |
| `use_updated` | boolean | No | false | Use updatedAt vs createdAt |
| `limit` | integer | No | 10 (hard cap: 50) | Max results |
| `skip` | integer | No | 0 | Skip |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_components_by_date_range_tool",
  "parameters": {
    "start_date": "2025-01-01T00:00:00Z",
    "component_type": "module",
    "projection": {"serialNumber": 1, "componentType": 1, "currentStage": 1}
  }
}
```

---

## Advanced Queries

### `find_anomalous_pcb_measurements_tool`

Find PCBs with anomalous measurements.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `test_type` | string | Yes | Test type (e.g., METROLOGY) |
| `field_name` | string | Yes | Field to check (e.g., Y_DIMENSION) |
| `operator` | string | Yes | Comparison: "lt", "gt", "lte", "gte" |
| `threshold` | float | Yes | Threshold value |
| `limit` | integer | No | Default: 10 (hard cap: 50) |
| `skip` | integer | No | Default: 0 |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_anomalous_pcb_measurements_tool",
  "parameters": {
    "test_type": "METROLOGY",
    "field_name": "Y_DIMENSION",
    "operator": "lt",
    "threshold": 40.5,
    "projection": {"testType": 1, "results.Y_DIMENSION": 1}
  }
}
```

---

### `find_anomalous_bare_module_mass_tool`

Find ITkpix_v2 bare modules with mass outside expected range.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `min_mass` | float | No | 1000.0 | Minimum expected mass (mg) |
| `max_mass` | float | No | 1500.0 | Maximum expected mass (mg) |
| `fe_chip_version` | string | No | "3" | FE chip version |
| `limit` | integer | No | 10 (hard cap: 50) | Max results |
| `skip` | integer | No | 0 | Skip |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_anomalous_bare_module_mass_tool",
  "parameters": {
    "min_mass": 1100.0,
    "max_mass": 1400.0,
    "projection": {"testType": 1, "results.MASS": 1}
  }
}
```

---

### `find_modules_by_test_criteria_tool`

Find modules matching test criteria, returning alternative IDs directly. This performs a join between QC.result and component collections in a single database query. Use this to efficiently find modules that had tests at a specific stage, institution, and date range.


**⚠️ CRITICAL: Pagination applies to TESTS, not MODULES**

This tool first queries the `QC.result` collection for matching tests, then fetches the corresponding module documents. **Pagination (`limit`/`skip`) controls how many TEST documents are retrieved, not how many MODULES are returned.**

**Implications:**
- A single module can have multiple tests at the same stage
- If you have 110 matching tests across 10 modules, `limit=50` returns only the modules referenced in the first 50 tests
- To get ALL modules, you must paginate through ALL tests (e.g., skip=0,50,100) and deduplicate client-side
- The tool **does not** automatically deduplicate across pagination calls

**Example:** If 10 modules have 110 total wirebonding tests at IRFU, and you call with `limit=50, skip=0`, you might only get 5-6 modules (those referenced in tests 1-50). The remaining 4-5 modules would only appear when you call with `skip=50` or `skip=100`.


**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `stage` | string | No | MODULE/WIREBONDING | Production stage |
| `institution` | string | No | - | Institution code (e.g., "IRFU") |
| `start_date` | string | No | - | Start date in ISO format (e.g., "2026-04-27T00:00:00Z") |
| `end_date` | string | No | - | End date in ISO format |
| `limit` | integer | No | 50 | **Maximum TEST documents to fetch** (hard cap: 50) |
| `skip` | integer | No | 0 | **Number of TEST documents to skip** for pagination |

**Returns:** JSON array of module summaries with alternative_id, serialNumber, componentType, and properties. **All returned documents are guaranteed to be modules (componentType: "module")** due to the server-side filter added in the 2026-05-06 fix.

**Example:**
```json
{
  "tool": "find_modules_by_test_criteria_tool",
  "parameters": {
    "stage": "MODULE/WIREBONDING",
    "institution": "IRFU",
    "start_date": "2026-04-27T00:00:00Z",
    "limit": 50,
    "skip": 0
  }
}
```

**Recommended Alternative:** For queries where you need all modules regardless of test count, consider using `aggregate_tests_by_component_tool` with `group_by="component"` and `merge_component=true`, then filter client-side for `componentType: "module"`. This groups by component first, avoiding the pagination issue.


---

### `aggregate_tests_by_component_tool`

Perform MongoDB aggregation with optional component merge. This provides a flexible way to group and join data from different collections. When `merge_component=True` and `group_by="component"`, it automatically joins with the component collection and extracts the alternative_id.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `collection` | string | Yes | - | The primary collection to aggregate (e.g., "QC.result") |
| `filter` | object | No | - | MongoDB query filter |
| `group_by` | string | No | component | Field to group by |
| `merge_component` | boolean | No | true | Whether to merge with component collection |
| `limit` | integer | No | 50 | Maximum number of results (hard cap: 50) |
| `projection` | object | No | - | Optional projection to limit returned fields |

**Returns:** JSON array of aggregated results

**Example:**
```json
{
  "tool": "aggregate_tests_by_component_tool",
  "parameters": {
    "collection": "QC.result",
    "filter": {
      "stage": "MODULE/WIREBONDING",
      "prodDB_record.institution.code": "IRFU"
    },
    "group_by": "component",
    "merge_component": true,
    "limit": 20
  }
}
```

---

## Comment Tools

**See also:** [COMMENTS_QUERY_METHOD.md](COMMENTS_QUERY_METHOD.md) for detailed comment query patterns and examples.

### `find_comments_by_component_tool`

Find all comments for a specific component by its ObjectId.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `component_id` | string | Yes | - | Component ObjectId |
| `limit` | integer | No | 20 | Max comments (hard cap: 50) |
| `skip` | integer | No | 0 | Skip |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_comments_by_component_tool",
  "parameters": {
    "component_id": "67c981355ae416616e2a8974",
    "projection": {"comment": 1, "datetime": 1, "user_name": 1}
  }
}
```

---

### `find_comments_by_alternative_id_tool`

Find all comments for a component using its alternative identifier.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `alternative_id` | string | Yes | - | Alternative ID (e.g., Paris0001) |
| `component_type` | string | No | "module" | Component type |
| `limit` | integer | No | 20 | Max comments |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_comments_by_alternative_id_tool",
  "parameters": {
    "alternative_id": "Paris0076",
    "component_type": "module",
    "projection": {"comment": 1, "datetime": 1}
  }
}
```

---

### `find_comments_by_user_tool`

Find all comments made by a specific user.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | No | User ObjectId |
| `user_name` | string | No | User name (partial match) |
| `start_date` | string | No | Start date (ISO) |
| `end_date` | string | No | End date (ISO) |
| `limit` | integer | No | Default: 20 (hard cap: 50) |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_comments_by_user_tool",
  "parameters": {
    "user_name": "Francesco",
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z",
    "projection": {"comment": 1, "datetime": 1, "component": 1}
  }
}
```

---

### `find_comments_by_date_range_tool`

Find all comments within a specific date range.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `start_date` | string | Yes | Start date (ISO) |
| `end_date` | string | No | End date (ISO) |
| `component_type` | string | No | Filter by component type |
| `limit` | integer | No | Default: 20 |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_comments_by_date_range_tool",
  "parameters": {
    "start_date": "2025-06-01T00:00:00Z",
    "end_date": "2025-06-30T23:59:59Z",
    "component_type": "module",
    "projection": {"comment": 1, "datetime": 1, "component": 1}
  }
}
```

---

### `find_comments_by_keyword_tool`

Find comments containing specific keywords.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `keywords` | array | Yes | - | Keywords to search |
| `component_type` | string | No | - | Filter by type |
| `case_sensitive` | boolean | No | false | Case sensitive search |
| `limit` | integer | No | 20 | Max results |
| `projection` | object | No | Fields to include/exclude |

**Example:**
```json
{
  "tool": "find_comments_by_keyword_tool",
  "parameters": {
    "keywords": ["wirebond", "breakdown", "disconnected"],
    "component_type": "module",
    "projection": {"comment": 1, "datetime": 1, "alternative_id": 1}
  }
}
```

---

## GridFS File Storage

**See also:** [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md) § "Rule 5 — GridFS: metadata before download" for file handling best practices.

### `gridfs_list_files_tool`

List files stored in GridFS with optional filters.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `filename` | string | No | Filter by filename (partial match) |
| `metadata_filter` | object | No | Filter by metadata fields |
| `limit` | integer | No | Default: 20 |

**Example:**
```json
{
  "tool": "gridfs_list_files_tool",
  "parameters": {
    "metadata_filter": {"component_id": "67c981355ae416616e2a8974"},
    "limit": 50
  }
}
```

**Response Format:**
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "filename": "test_report.pdf",
    "length": 1024000,
    "chunkSize": 261120,
    "uploadDate": "2025-01-15T10:30:00Z",
    "contentType": "application/pdf",
    "metadata": {"component_id": "67c981355ae416616e2a8974"}
  }
]
```

---

### `gridfs_get_file_metadata_tool`

Get metadata for a specific file in GridFS.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_id` | string | Yes | File ObjectId |

**Example:**
```json
{
  "tool": "gridfs_get_file_metadata_tool",
  "parameters": {
    "file_id": "507f1f77bcf86cd799439011"
  }
}
```

---

### `gridfs_download_file_tool`

Download a file from GridFS by its ObjectId.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_id` | string | Yes | File ObjectId |

**Example:**
```json
{
  "tool": "gridfs_download_file_tool",
  "parameters": {
    "file_id": "507f1f77bcf86cd799439011"
  }
}
```

**Response Format:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "filename": "test_report.pdf",
  "contentType": "application/pdf",
  "length": 1024000,
  "data_base64": "JVBERi0xLjQKJeLjz9..."
}
```

**Note:** File content is returned as base64-encoded string for JSON transport.

---

## Production Statistics

These tools provide high-level aggregated statistics about module production progress without requiring the agent to paginate through large collections.

---

### `count_wirebonded_modules_tool`

Count production modules that completed wirebonding (distinct modules, not test entries). A module with multiple WIREBONDING records at the same stage is counted only once.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `institution` | string | No | Institution code (e.g., `"IRFU"`, `"LPNHE"`). Omit for all sites. |
| `start_date` | string | No | Lower bound date, ISO 8601 (e.g., `"2026-05-01T00:00:00Z"`) |
| `end_date` | string | No | Upper bound date, ISO 8601 (e.g., `"2026-05-31T23:59:59Z"`) |

**Returns:** JSON object: `{"institution": "IRFU", "start_date": "...", "end_date": "...", "wirebonded_modules_count": 12}`

**Example:**
```json
{
  "tool": "count_wirebonded_modules_tool",
  "parameters": {
    "institution": "IRFU",
    "start_date": "2026-05-01T00:00:00Z",
    "end_date": "2026-05-31T23:59:59Z"
  }
}
```

---

### `find_module_signoffs_tool`

List module sign-off events with component identification, sorted by date. Returns one row per sign-off event.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `institution` | string | No | - | Institution code (e.g., `"IRFU"`). Omit for all sites. |
| `start_date` | string | No | - | Lower bound date, ISO 8601 |
| `end_date` | string | No | - | Upper bound date, ISO 8601 |
| `signoff_test_type` | string | No | `"SIGN_OFF"` | testType used for sign-offs |
| `limit` | integer | No | 200 | Maximum rows to return |
| `skip` | integer | No | 0 | Rows to skip for pagination |

**Returns:** JSON array of `{atlasId, alias, stage, signoff_date}` records sorted by `signoff_date` ascending.

**Example:**
```json
{
  "tool": "find_module_signoffs_tool",
  "parameters": {
    "institution": "IRFU",
    "start_date": "2026-01-01T00:00:00Z"
  }
}
```

---

### `count_module_signoffs_by_stage_tool`

Count signed-off modules grouped by production stage. Each (module, stage) pair is counted at most once even if multiple sign-off records exist.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `institution` | string | No | - | Institution code. Omit for all sites. |
| `start_date` | string | No | - | Lower bound date, ISO 8601 |
| `end_date` | string | No | - | Upper bound date, ISO 8601 |
| `signoff_test_type` | string | No | `"SIGN_OFF"` | testType used for sign-offs |

**Returns:** JSON object with `signoffs_by_stage` array (sorted by count descending) and `total_signoffs`.

**Example:**
```json
{
  "tool": "count_module_signoffs_by_stage_tool",
  "parameters": {
    "institution": "IRFU",
    "start_date": "2026-01-01T00:00:00Z"
  }
}
```

---

## Diagnostic Tools

### `ping_tool`

Check server and MongoDB connectivity. Returns server status and database name.

**Parameters:** None

**Returns:** JSON object: `{"status": "ok", "database": "...", "collections_count": N}`

**Example:**
```json
{
  "tool": "ping_tool",
  "parameters": {}
}
```

**Note:** the server also registers `say_hello_to_mines_student_by_name` — a non-production demo tool (returns a greeting string, no database access). It is intentionally excluded from the 34-tool count above and from the tables below since it performs no LocalDB operation.

---

## Quick Reference

### By Collection

| Collection | Tools |
|------------|-------|
| `component` | find_component_by_id_tool, find_components_by_ids_tool, find_component_summary_tool, find_quad_module_tests_by_stage_tool, find_quad_modules_with_*, **find_component_by_serial_unified_tool, find_component_by_alternative_id_unified_tool, find_production_components_unified_tool** |
| `QC.result` | find_quad_module_tests_by_stage_tool, find_quad_modules_with_*_problems_tool, find_test_summary_tool, find_modules_by_test_criteria_tool, aggregate_tests_by_component_tool, **find_latest_test_unified_tool** |
| `QC.module.status` | find_quad_modules_in_status_tool, **find_components_with_valid_tests_unified_tool** |
| `comments` | find_comments_by_*, count_tool |
| `fs.files` (GridFS) | gridfs_* |
| `QC.result` (aggregated) | count_wirebonded_modules_tool, find_module_signoffs_tool, count_module_signoffs_by_stage_tool |
| *(server)* | ping_tool |

### By Use Case

| Use Case | Tools |
|----------|-------|
| Find component by serial / alt-ID | **find_component_by_serial_unified_tool, find_component_by_alternative_id_unified_tool**, find_component_summary_tool |
| Find component by ObjectId | find_component_by_id_tool, find_components_by_ids_tool |
| Find production components | **find_production_components_unified_tool** |
| Get test results | **find_latest_test_unified_tool**, find_quad_module_tests_by_stage_tool, find_test_summary_tool |
| Find components with valid tests | **find_components_with_valid_tests_unified_tool**, find_quad_modules_in_status_tool |
| Count documents | count_tool |
| Quality issues | find_quad_modules_with_visual_inspection_issues_tool, find_quad_modules_with_wirebonding_problems_tool, find_anomalous_*_tool |
| Comments | find_comments_by_*_tool |
| Files | gridfs_*_tool |
| Date-based | find_*_by_date_range_tool |
| Batch/Joins | find_components_by_ids_tool, find_modules_by_test_criteria_tool, aggregate_tests_by_component_tool |
| Production statistics | count_wirebonded_modules_tool, find_module_signoffs_tool, count_module_signoffs_by_stage_tool |
| Diagnostics | ping_tool |

---

## Error Handling

All tools return:
- `null` for single document not found
- `[]` for empty result sets
- Error messages prefixed with `"Error:"` for exceptions

Invalid ObjectIds are handled gracefully with warning logs.

---

## Performance Tips

1. **Use specific tools** instead of generic `find_all_tool` for better optimization
2. **Set appropriate limits** for large collections
3. **Use pagination** (`skip`/`limit`) for browsing results
4. **Filter early** with specific parameters instead of client-side filtering
5. **Use QC.module.status** to check test validity before fetching full test documents
6. **Use Unified Tools** for component/test queries: `find_component_by_serial_unified_tool`, `find_component_by_alternative_id_unified_tool`, `find_production_components_unified_tool`, `find_latest_test_unified_tool`, `find_components_with_valid_tests_unified_tool`

---

## ⚠️ Pagination Pitfalls

### `find_modules_by_test_criteria_tool` — The Test-Level Pagination Trap

**This is the most common source of confusion and incomplete results.**

The `find_modules_by_test_criteria_tool` applies pagination to **TEST documents**, not MODULE documents. Since a single module can have many tests at the same stage, this leads to unexpected behavior:

```
Scenario: 10 modules, 110 total wirebonding tests at IRFU

Call 1: limit=50, skip=0
  → Fetches tests 1-50
  → Extracts unique module IDs from those 50 tests
  → Returns 5-6 modules (those referenced in tests 1-50)

Call 2: limit=50, skip=50  
  → Fetches tests 51-100
  → Extracts unique module IDs from those 50 tests
  → Returns 4-5 modules (those referenced in tests 51-100)

Call 3: limit=50, skip=100
  → Fetches tests 101-110
  → Extracts unique module IDs from those 10 tests
  → Returns 0-1 modules

Result: You need ALL THREE calls and client-side deduplication to get all 10 modules.
```

**Solution options:**
1. **Manual pagination + dedup**: Call with skip=0,50,100,... and merge results client-side
2. **Use `aggregate_tests_by_component_tool`**: Groups by component first, avoiding the issue
3. **Count first**: Use `count_tool` on QC.result to know how many pagination calls you need

**Rule of thumb:** If `count_tool` on QC.result returns > 50 for your filter, you MUST paginate to get complete module results.
