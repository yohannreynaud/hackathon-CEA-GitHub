# ITk Pixel Quad Module Documentation

## Overview
This document provides a comprehensive guide to ITk Pixel Quad Modules in the LocalDB database, including component structure, production stages, test types, and query examples.

---

## 1. Component Identification

### Collection and Type
- **Collection**: `component`
- **componentType**: `module`
- **Type Code**: `OUTER_SYSTEM_QUAD_MODULE` (for production quad modules)

### Naming Convention
- **Serial Number Format**: `20UPGMXXXXXXXX` (e.g., `20UPGM24830846`)
- **Alternative ID**: Often starts with "Paris" followed by numbers (e.g., `Paris0076`)

### Key Properties
| Property Code | Description | Typical Values |
|---------------|-------------|----------------|
| `FECHIP_VERSION` | FE chip version | `0`=RD53A, `1`=ITkpix_v1, `2`=ITkpix_v1.1, `3`=ITkpix_v2, `9`=No FE chip |
| `ORIENTATION` | PCB-Bare Orientation isNormal | `true` or `false` |
| `ROOF` | Wirebond protection roof presence | `true` or `false` |
| `ALTERNATIVE_IDENTIFIER` | Alternative ID | String (e.g., "Paris0076") |
| `IS_PREPRODUCTION_MODULE` | Is preproduction module | `true` or `false` |

---

## 2. Production Stages

Quad modules go through the following production stages in order:

1. **MODULE/ASSEMBLY** - Bare module to module PCB assembly
2. **MODULE/WIREBONDING** - Wire Bonding
3. **MODULE/INITIAL_WARM** - Initial Warm testing
4. **MODULE/PARYLENE_MASKING** - Parylene Masking
5. **MODULE/PARYLENE_COATING** - Parylene Unmasking
6. **MODULE/PARYLENE_UNMASKING** - Parylene Coating
7. **MODULE/WIREBOND_PROTECTION** - Outer Barrel Wirebond Protection (OBWBP) Assembly
8. **MODULE/POST_PARYLENE_WARM** - Post Parylene Warm testing (optional)
9. **MODULE/THERMAL_CYCLES** - Thermal Cycles
10. **MODULE/FINAL_WARM**  - Final Warm testing
11. **MODULE/FINAL_COLD** - Final Cold testing
12. **MODULE/FINAL_METROLOGY** - Final Metrology
13. **MODULE/QC_STATUS** - Final Grading

---

## 3. Test Types by Stage

### Stage: MODULE/ASSEMBLY
| Test Type | Description | Key Measurements |
|-----------|-------------|------------------|
| `MASS_MEASUREMENT` | Module mass measurement | Mass (mg), Scale Accuracy |
| `VISUAL_INSPECTION` | Visual quality check | Component conditions (1=Good, 2=Issues, 3=Bad) |
| `QUAD_MODULE_METROLOGY` | Dimensional measurements | Thickness (μm), HV capacitor thickness |
| `FLATNESS` | Module flatness measurement | Backside flatness (μm), measurement points |

### Stage: MODULE/WIREBONDING
| Test Type | Description | Key Measurements |
|-----------|-------------|------------------|
| `WIREBONDING` | Wirebonding information | Temperature (°C), Humidity (%), Reworked wire bonds |
| `WIREBOND_PULL_TEST` | Wirebond strength test | Pull strength (g), Heel breaks (%) |
| `VISUAL_INSPECTION` | Post-wirebonding visual check | Component conditions |

### Stage: MODULE/INITIAL_WARM
| Test Type | Description | Key Measurements |
|-----------|-------------|------------------|
| `IV_MEASURE` | IV curve measurement | Voltage (V), Current (μA), Breakdown voltage |
| `E_SUMMARY` | Electrical test summary | Bad pixels, Electrically bad pixels, Disconnected pixels |

### Stage: MODULE/PARYLENE_MASKING
| Test Type | Description | Key Measurements |
|-----------|-------------|------------------|
| `DE_MASKING` | Parylene (de-)masking | Operator identity, Date |
| `VISUAL_INSPECTION` | Final visual inspection | Component conditions |

---

## 4. Query Examples

### Find Quad Modules by Serial Number Pattern
```json
{
  "collection": "component",
  "filter": {
    "serialNumber": {"$regex": "^20UPGM"},
    "componentType": "module"
  }
}
```

### Find Quad Modules by Alternative ID
```json
{
  "collection": "component",
  "filter": {
    "properties": {
      "$elemMatch": {
        "code": "ALTERNATIVE_IDENTIFIER",
        "value": {"$regex": "^Paris"}
      }
    },
    "componentType": "module"
  }
}
```

### Find All Tests for a Quad Module
```json
{
  "collection": "QC.result",
  "filter": {
    "component": "<COMPONENT_OBJECT_ID>"
  }
}
```

### Find Tests by Stage
```json
{
  "collection": "QC.result",
  "filter": {
    "component": "<COMPONENT_OBJECT_ID>",
    "stage": "MODULE/ASSEMBLY"
  }
}
```

### Find Quad Modules with Specific FE Chip Version
```json
{
  "collection": "component",
  "filter": {
    "componentType": "module",
    "properties": {
      "$elemMatch": {
        "code": "FECHIP_VERSION",
        "value": "3"  // ITkpix_v2
      }
    }
  }
}
```

---

## 5. Data Structure

### Component Document Structure
```json
{
  "_id": ObjectId,
  "serialNumber": "20UPGMXXXXXXXX",
  "componentType": "module",
  "properties": [
    {
      "code": "FECHIP_VERSION",
      "value": "3",
      "name": "FE chip version"
    },
    {
      "code": "ALTERNATIVE_IDENTIFIER",
      "value": "ParisXXXX",
      "name": "Alternative ID"
    }
  ],
  "type": {
    "code": "OUTER_SYSTEM_QUAD_MODULE",
    "name": "Outer system quad module"
  }
}
```

### Test Result Structure
```json
{
  "_id": ObjectId,
  "testType": "MASS_MEASUREMENT",
  "stage": "MODULE/ASSEMBLY",
  "component": ObjectId,  // Reference to component
  "passed": true,
  "results": {
    "MASS": 3135.0,
    "property": {
      "SCALE_ACCURACY": 1.0,
      "MEASUREMENT_DATE": "2025-12-22T13:38:00.000+00:00"
    }
  },
  "prodDB_record": {
    "institution": {"code": "LPNHE"},
    "user": {"userIdentity": "XXXX-XX-XX"},
    "attachments": [...]
  }
}
```

---

## 6. Common Queries Reference

### Count Quad Modules by FE Chip Version
```json
{
  "collection": "component",
  "filter": {
    "componentType": "module",
    "properties": {
      "$elemMatch": {
        "code": "FECHIP_VERSION",
        "value": "3"  // ITkpix_v2
      }
    }
  }
}
```

### Find Quad Modules with Visual Inspection Issues
```json
{
  "collection": "QC.result",
  "filter": {
    "testType": "VISUAL_INSPECTION",
    "stage": "MODULE/ASSEMBLY",
    "results.SMD_COMPONENTS_PASSED_QC": {"$gt": 1}  // 2=Issues, 3=Bad
  }
}
```

### Find Quad Modules with Wirebonding Problems
```json
{
  "collection": "QC.result",
  "filter": {
    "testType": "WIREBOND_PULL_TEST",
    "stage": "MODULE/WIREBONDING",
    "results.PULL_STRENGTH": {"$lt": 7}  // Below 7g threshold
  }
}
```

---

## 7. Notes and Best Practices

### Finding Component ObjectId
1. First query the `component` collection to find the module
2. Use the returned `_id` to query the `QC.result` collection for tests

### Understanding Test Results
- `passed`: Boolean indicating if test passed
- `results`: Contains actual measurement data
- `prodDB_record`: Contains metadata, institution, user, and attachments
- `attachments`: May contain images (EOS URLs) and raw data

### Date Formats
- Measurement dates are in ISO format with timezone: `YYYY-MM-DDTHH:MM:SS.SSS+00:00`
- System dates (`cts`, `mts`) are in MongoDB Date format

### Institutions
- `LPNHE`: Laboratoire de Physique Nucléaire et de Hautes Energies
- Other institutions may appear depending on production site

---

## 8. Quick Reference

### Quad Module vs Other Components
| Aspect | Quad Module | Bare Module | Flex PCB |
|--------|-------------|-------------|----------|
| componentType | `module` | `bare_module` | `module_pcb` |
| Serial Pattern | `20UPGM*` | `20UPGB*` | `20UPGPQ*` |
| Type Code | `OUTER_SYSTEM_QUAD_MODULE` | `BARE_MODULE` | `Quad PCB` |
| Main Stage | MODULE/* | BAREMODULE/* | PCB_* |

### Production Flow
```
Bare Module → Module Assembly → Wirebonding → Initial Warm → Parylene Masking → Final Module
```

---

## 9. Example Workflow

### To analyze a quad module:
1. Find the component by serial number or alternative ID
2. Note the ObjectId from the component document
3. Query QC.result collection using the ObjectId
4. Filter by stage if needed
5. Examine test results and attachments

### Example queries for module "Paris0076":
```bash
# Step 1: Find component
find_one(component, {"properties": {"$elemMatch": {"code": "ALTERNATIVE_IDENTIFIER", "value": "Paris0076"}}})

# Step 2: Get ObjectId from result (e.g., 6943ddd088b791b617bbe9ce)

# Step 3: Find all tests
find_all(QC.result, {"component": "6943ddd088b791b617bbe9ce"})

# Step 4: Find assembly stage tests
find_all(QC.result, {"component": "6943ddd088b791b617bbe9ce", "stage": "MODULE/ASSEMBLY"})
```

---

## 10. Troubleshooting

### No results found?
- Verify the serial number pattern (`20UPGM*` for quad modules)
- Check if the component is marked as `componentType: "module"`
- Try searching by alternative ID if known

### Missing tests?
- The module may not have completed all production stages
- Check the `stage` field in test results
- Some tests are optional depending on production site

### Understanding test failures
- Check the `passed` field (false = failed)
- Examine `results` for specific measurements
- Look at `defects` array in `prodDB_record` for visual inspection issues
- Check attachments for images or raw data

---

## 11. MCP Server Tools

When using the MCP server tools for quad module queries, be aware of the following:

### `find_modules_by_test_criteria_tool` — Pagination Warning

**⚠️ This tool's pagination applies to TEST documents, not MODULE documents.**

This is a common source of incomplete results. The tool:
1. Queries `QC.result` for matching tests (with your `limit`/`skip`)
2. Extracts unique component IDs from those test results
3. Returns the corresponding modules

**Example:** If 10 modules have 110 wirebonding tests at IRFU, calling with `limit=50, skip=0` returns only the modules referenced in the first 50 tests (typically 5-6 modules). You would miss the remaining 4-5 modules that only appear in tests 51-110.

**Solution:**
- Use `count_tool` first to check total test count
- If > 50 tests, paginate with `skip=0,50,100,...` and deduplicate client-side
- **Better alternative:** Use `aggregate_tests_by_component_tool` with `group_by="component"` and `merge_component=true`, then filter for `componentType: "module"`

**Note:** As of 2026-05-06, the tool correctly filters to return only modules (componentType: "module"), fixing an earlier bug where it returned all component types.
