# BARE_MODULE Component Documentation

## Overview
This document describes how to find and work with BARE_MODULE components in the LocalDB database for ITk Pixel Detector production.

---

## 1. Component Location and Naming

### Collection
- **Collection**: `component`
- **componentType**: `bare_module`

### chipType Variants
| chipType | Description | Serial Number Pattern |
|----------|-------------|----------------------|
| `Quad bare module` | Production quad bare module (4 FE chips + sensor) | `20UPGB4XXXXXXX` |
| `Digital quad bare module` | Digital quad bare module (no sensor) | `20UPGBQXXXXXXX` |
| `Single bare module` | Single bare module (1 FE chip) | `20UPGB1XXXXXXX` |
| `Tutorial bare module` | Non-production, tutorial/test components | `20UPGXBXXXXXXX` |

### Serial Number Format
- Production Quad: `20UPGB4XXXXXXX` (e.g., `20UPGB42000033`)
- Digital Quad: `20UPGBQXXXXXXX` (e.g., `20UPGBQ2000803`)
- Single: `20UPGB1XXXXXXX` (e.g., `20UPGB10000001`)
- Tutorial: `20UPGXBXXXXXXX` (e.g., `20UPGXB2000013`)

---

## 2. Component Properties

### Required Properties

| Property Code | Description | Possible Values |
|---------------|-------------|-----------------|
| `FECHIP_VERSION` | FE chip version | `RD53A`, `ITkpix_v1`, `ITkpix_v1.1`, `ITkpix_v2`, `No FE chip` |
| `SENSOR_TYPE` | Sensor Type | `No sensor`, `Market survey sensor tile`, `L0 inner pixel 3D sensor tile`, `L0 inner pixel planar sensor tile`, `L1 inner pixel quad sensor tile`, `Outer pixel quad sensor tile`, `Dummy sensor tile` |
| `VENDOR` | Vendor code | `Advacam`, `HPK`, `IZM`, `Leonardo`, `ITk institute` |

### Optional Properties

| Property Code | Description | Possible Values |
|---------------|-------------|-----------------|
| `THICKNESS` | Thickness of FE chips | `Thin`, `Thick` |

---

## 3. Finding Production Bare Modules

### Query to Find Quad Bare Modules (Production)
```json
{
  "collection": "component",
  "filter": {
    "componentType": "bare_module",
    "chipType": "Quad bare module"
  }
}
```

### Query to Find Bare Modules with Sensor
```json
{
  "collection": "component",
  "filter": {
    "componentType": "bare_module",
    "properties.code": "SENSOR_TYPE",
    "properties.value": {"$ne": "No sensor"}
  }
}
```

### Query to Find Bare Modules by Vendor
```json
{
  "collection": "component",
  "filter": {
    "componentType": "bare_module",
    "properties.code": "VENDOR",
    "properties.value": "Advacam"
  }
}
```

---

## 4. Finding Tests for a Bare Module

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
For Bare Module `20UPGB42000033` (ObjectId: `63d148b40499130036777fe4`):
```json
{
  "collection": "QC.result",
  "filter": {
    "component": "63d148b40499130036777fe4"
  }
}
```

---

## 5. Test Structure

### Key Fields in Test Results
| Field | Description |
|-------|-------------|
| `testType` | Type of test (e.g., `VISUAL_INSPECTION`, `MASS_MEASUREMENT`, `QUAD_BARE_MODULE_METROLOGY`) |
| `stage` | Production stage (e.g., `BAREMODULERECEPTION`) |
| `passed` | Boolean - test passed/failed |
| `results` | Object containing test measurements |
| `prodDB_record.institution.code` | Institution that performed the test |
| `prodDB_record.date` | Test date |

### Common Test Types for Bare Modules
| Test Type | Description | Stage |
|-----------|-------------|-------|
| `VISUAL_INSPECTION` | Visual quality check | BAREMODULERECEPTION |
| `MASS_MEASUREMENT` | Mass measurement | BAREMODULERECEPTION |
| `BARE_MODULE_SENSOR_IV` | Sensor IV measurement | BAREMODULERECEPTION |
| `QUAD_BARE_MODULE_METROLOGY` | Dimensional measurements | BAREMODULERECEPTION |

### Test Result Details

#### VISUAL_INSPECTION Results
| Field | Description |
|-------|-------------|
| `SENSOR_CONDITION_PASSED_QC` | Sensor condition (1: good, 2: issues, 3: bad) |
| `FE_CHIP_CONDITION_PASSED_QC` | FE chip condition (1: good, 2: issues, 3: bad) |
| `SMD_COMPONENTS_PASSED_QC` | SMD components (not required for bare modules) |
| `GLUE_DISTRIBUTION_PASSED_QC` | Glue distribution (not applicable) |
| `WIREBONDING_PASSED_QC` | Wirebonding (not applicable) |
| `PARYLENE_COATING_PASSED_QC` | Parylene coating (not applicable) |

#### MASS_MEASUREMENT Results
| Field | Description |
|-------|-------------|
| `MASS` | Mass [mg] |

#### QUAD_BARE_MODULE_METROLOGY Results
| Field | Description |
|-------|-------------|
| `SENSOR_X` | Sensor dimension in x [mm] |
| `SENSOR_Y` | Sensor dimension in y [mm] |
| `SENSOR_THICKNESS` | Average sensor thickness [um] |
| `FECHIPS_X` | FE chips x dimension [mm] |
| `FECHIPS_Y` | FE chips y dimension [mm] |
| `FECHIP_THICKNESS` | Average FE chip thickness [um] |
| `BARE_MODULE_THICKNESS` | Average bare module thickness [um] |

#### BARE_MODULE_SENSOR_IV Results
| Field | Description |
|-------|-------------|
| `LINK_TO_SENSOR_IV_TEST` | Link to sensor IV test result |
| `NON_WORKING_FE_CHIPS` | Non-working FE chips (if first connection failed) |

---

## 6. Production Stages

### Bare Module Stages
| Stage Code | Description |
|------------|-------------|
| `BAREMODULERECEPTION` | Reception at ITk institute |

### Module Assembly Stages (when bare module is attached to module)
| Stage Code | Description |
|------------|-------------|
| `MODULE/ASSEMBLY` | Bare module to module PCB assembly |
| `MODULE/INITIAL_WARM` | Initial warm testing |
| `MODULE/PARYLENE_MASKING` | Parylene masking |
| `MODULE/WIREBONDING` | Wirebonding |

---

## 7. Reference Example

### Production Quad Bare Module: 20UPGB42000033
- **ObjectId**: `63d148b40499130036777fe4`
- **chipType**: `Quad bare module`
- **FECHIP_VERSION**: `ITkpix_v1.1`
- **SENSOR_TYPE**: `Outer pixel quad sensor tile`
- **VENDOR**: `Advacam`
- **THICKNESS**: `null`
- **Tests Found**: 4 tests at BAREMODULERECEPTION stage
  - VISUAL_INSPECTION (passed)
  - MASS_MEASUREMENT (passed, 1250 mg)
  - BARE_MODULE_SENSOR_IV (passed)
  - QUAD_BARE_MODULE_METROLOGY (passed)

---

## 8. Quick Reference Queries

### Get Bare Module by Serial Number
```json
{"collection": "component", "filter": {"serialNumber": "20UPGB42000033"}}
```

### Get Tests by Serial Number (requires 2 steps)
1. Find component to get ObjectId
2. Query QC.result with ObjectId

### Count Quad Bare Modules
```json
{
  "collection": "component",
  "filter": {
    "componentType": "bare_module",
    "chipType": "Quad bare module"
  }
}
```

### Find Bare Modules with ITkpix_v1.1
```json
{
  "collection": "component",
  "filter": {
    "componentType": "bare_module",
    "properties.code": "FECHIP_VERSION",
    "properties.value": "ITkpix_v1.1"
  }
}
```

---

## Notes
- Bare modules are the basic building blocks consisting of FE chips bonded to a sensor
- Production bare modules (`Quad bare module`) have 4 FE chips and a sensor tile
- Digital bare modules (`Digital quad bare module`) have 4 FE chips but no sensor
- Tutorial bare modules (`Tutorial bare module`) are NOT production components
- Always use ObjectId from component collection to query tests in QC.result
- Bare modules can be attached to modules and then follow module assembly stages
