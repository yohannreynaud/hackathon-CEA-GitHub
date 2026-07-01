# PCB Component Documentation

## Overview
This document describes how to find and work with PCB (Printed Circuit Board) components in the LocalDB database for ITk Pixel Detector production.

---

## 1. Component Location and Naming

### Collection
- **Collection**: `component`
- **componentType**: `module_pcb`

### Naming Convention
- **chipType**: `Quad PCB` (production PCBs, also called "flex" or "FLEX_PCB" in other contexts)
- **chipType**: `Tutorial PCB` (non-production, tutorial/test components)

### Serial Number Format
- Production: `20UPGPQXXXXXXX` (e.g., `20UPGPQ2830070`)
- Tutorial: `20UPGXPXXXXXXX`

---

## 2. Finding Production PCBs

### Key Property: PCB_DESIGN_VERSION
Production PCBs have `PCB_DESIGN_VERSION` set to:
- `"4"` = **Production OS** (Outer System)
- `"5"` = **Production IS** (Inner System)

### Query to Find Production PCBs
```json
{
  "collection": "component",
  "filter": {
    "componentType": "module_pcb",
    "properties.code": "PCB_DESIGN_VERSION",
    "properties.value": {"$in": ["4", "5"]}
  }
}
```

### Other Production Properties
| Property Code | Description | Production Values |
|---------------|-------------|-------------------|
| `PCB_MANUFACTURER` | PCB Manufacturer | `"Tecnomec"`, `"NCAB"` |
| `PCB_VENDOR_TECHNOLOGY` | Vendor Technology | `"2"` (NCAB 100μm), `"8"` (Tecnomec 100μm) |
| `PCB_BOM_VERSION` | Bill of Materials | `"22"` = V2 L2 |
| `SMD_POPULATION_VENDOR` | SMD Assembly | `"Norbit EMS AS"`, `"Garner Osborne Ltd"` |

---

## 3. Finding Tests for a PCB

### Collection
- **Collection**: `QC.result`

### Query by Component ObjectId
```json
{
  "collection": "QC.result",
  "filter": {
    "component": "<COMPONENT_OBJECT_ID>"
  }
}
```

### Example
For PCB `20UPGPQ2830070` (ObjectId: `675218df82f4f0f963143fb8`):
```json
{
  "collection": "QC.result",
  "filter": {
    "component": "675218df82f4f0f963143fb8"
  }
}
```

---

## 4. Test Structure

### Key Fields in Test Results
| Field | Description |
|-------|-------------|
| `testType` | Type of test (e.g., `HV_LV_TEST`, `METROLOGY`, `VISUAL_INSPECTION`) |
| `stage` | Production stage (e.g., `PCB_QC`, `PCB_POPULATION`, `PCB_RECEPTION_MODULE_SITE`) |
| `passed` | Boolean - test passed/failed |
| `results` | Object containing test measurements |
| `prodDB_record.institution.code` | Institution that performed the test |
| `prodDB_record.date` | Test date |

### Common Test Types for PCBs
| Test Type | Description | Stage |
|-----------|-------------|-------|
| `VISUAL_INSPECTION` | Visual quality check | PCB_POPULATION, PCB_RECEPTION_MODULE_SITE |
| `HV_LV_TEST` | High/Low voltage electrical test | PCB_QC |
| `METROLOGY` | Dimensional measurements | PCB_RECEPTION_MODULE_SITE |
| `MASS` | Mass measurement | PCB_RECEPTION_MODULE_SITE |
| `DOWEL_TOLERANCE_CHECK` | Dowel pin tolerance check | PCB_QC |
| `COMPONENT_POSITION_CHECK` | Component placement verification | PCB_POPULATION |
| `QUICK_TAB_CUTTING_INSPECTION` | Tab cutting inspection | PCB_QC |

### Production Stages (in order)
1. `PCB_POPULATION` - SMD component assembly
2. `PCB_QC` - Quality Control tests
3. `PCB_RECEPTION_MODULE_SITE` - Reception at module assembly site

---

## 5. Reference Example

### Production PCB: 20UPGPQ2830070
- **ObjectId**: `675218df82f4f0f963143fb8`
- **PCB_DESIGN_VERSION**: `"4"` (Production OS)
- **PCB_MANUFACTURER**: `"Tecnomec"`
- **PCB_VENDOR_TECHNOLOGY**: `"8"` (Tecnomec 100μm trace)
- **PCB_BOM_VERSION**: `"22"` (V2 L2)
- **SMD_POPULATION_VENDOR**: `"Norbit EMS AS"`
- **Tests Found**: 9 tests across 3 stages

---

## 6. Quick Reference Queries

### Get PCB by Serial Number
```json
{"collection": "component", "filter": {"serialNumber": "20UPGPQ2830070"}}
```

### Get Tests by Serial Number (requires 2 steps)
1. Find component to get ObjectId
2. Query QC.result with ObjectId

### Count Production PCBs
```json
{
  "collection": "component",
  "filter": {
    "componentType": "module_pcb",
    "properties.code": "PCB_DESIGN_VERSION",
    "properties.value": {"$in": ["4", "5"]}
  }
}
```

---

## Notes
- PCBs in this database are `module_pcb` type, called "Quad PCB" for production
- The term "FLEX_PCB" or "flex" used elsewhere refers to the same `Quad PCB` type
- Tutorial PCBs (`chipType: "Tutorial PCB"`) are NOT production components
- Always use ObjectId from component collection to query tests in QC.result
