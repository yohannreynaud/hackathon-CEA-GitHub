# Child-Parent Relationship (CPR) Collection Documentation

## Overview
This document describes the `childParentRelation` collection in LocalDB, which tracks hierarchical relationships between ITk Pixel components: quad modules, bare modules, flex PCBs, and frontend chips.

---

## 1. Collection Structure

### Collection Name
- **Collection**: `childParentRelation`

### Document Fields
```json
{
  "_id": ObjectId,          // Unique identifier
  "parent": ObjectId,       // Parent component (module, bare_module, or flex PCB)
  "child": ObjectId,        // Child component
  "chipId": Integer,        // Chip identifier (-1 if not applicable)
  "status": String,         // Relationship status (e.g., "active")
  "sys": {                  // System metadata
    "mts": Date,           // Last modified timestamp
    "cts": Date,           // Creation timestamp
    "rev": Integer          // Revision number
  },
  "dbVersion": Float       // Database version
}
```

---

## 2. Relationship Types

### Quad Module Composition
A quad module (`componentType: "module"`) is composed of:
1. **1 Bare Module** (`componentType: "bare_module"`)
2. **1 Flex PCB** (`componentType: "module_pcb"`)
3. **4 Frontend Chips** (individual FE chips)

### Hierarchy
```
Quad Module (Parent)
├── Bare Module (Child)
│   └── 4 Frontend Chips (Children of bare module)
├── Flex PCB (Child)
└── 4 Frontend Chips (Direct children of quad module)
```

**Note**: Frontend chips appear as children of both the bare module and the quad module.

---

## 3. Query Examples

### Find All Children of a Quad Module
```json
{
  "collection": "childParentRelation",
  "filter": {
    "parent": "<QUAD_MODULE_OBJECT_ID>"
  }
}
```

### Find Parent of a Component
```json
{
  "collection": "childParentRelation",
  "filter": {
    "child": "<COMPONENT_OBJECT_ID>"
  }
}
```

### Find Relationships by Status
```json
{
  "collection": "childParentRelation",
  "filter": {
    "status": "active"
  }
}
```

### Find All Quad Modules with Children
```json
{
  "collection": "childParentRelation",
  "filter": {
    "parent": {
      "$in": [
        "<QUAD_MODULE_ID_1>",
        "<QUAD_MODULE_ID_2>"
      ]
    }
  }
}
```

---

## 4. Navigation Patterns

### From Quad Module to Components
1. Query `childParentRelation` with quad module as `parent`
2. Extract all `child` ObjectIds
3. Query `component` collection for each child

### From Bare Module to Quad Module
1. Query `childParentRelation` with bare module as `child`
2. Extract the `parent` ObjectId
3. Query `component` collection for the parent

### From Frontend Chip to Parents
1. Query `childParentRelation` with FE chip as `child`
2. Extract all `parent` ObjectIds (may include both bare module and quad module)
3. Query `component` collection for each parent

---

## 5. Component Identification

### Component Types
| Type | componentType | Serial Pattern | Description |
|------|---------------|----------------|-------------|
| Quad Module | `module` | `20UPGM*` | Assembled module with bare module + flex PCB |
| Bare Module | `bare_module` | `20UPGB*` | Bare module with sensor and FE chips |
| Flex PCB | `module_pcb` | `20UPGPQ*` | Flexible PCB for module assembly |
| Frontend Chip | `bare_module` | `20UPGB*` | Individual FE chip (part of bare module) |

### Key Properties
| Property | Description | Values |
|----------|-------------|--------|
| `FECHIP_VERSION` | FE chip version | `0`=RD53A, `1`=ITkpix_v1, `2`=ITkpix_v1.1, `3`=ITkpix_v2, `9`=No FE chip |
| `SENSOR_TYPE` | Sensor type | `0`=No sensor, `1`=Market survey, `2`=L0 inner 3D, `3`=L0 inner planar, `4`=L1 inner quad, `5`=Outer quad, `9`=Dummy |
| `VENDOR` | Vendor code | `0`=Advacam, `1`=Leonardo, `2`=IZM, `3`=HPK (in-kind), etc. |

---

## 6. Example Workflows

### Workflow 1: Analyze Quad Module Composition
```bash
# Step 1: Find quad module by serial number
find_one(component, {"serialNumber": "20UPGM24810779"})
# Get ObjectId from result (e.g., 6992eada9e0bed6d7d9d3492)

# Step 2: Find all children
find_all(childParentRelation, {"parent": "6992eada9e0bed6d7d9d3492"})
# Extract child ObjectIds from results

# Step 3: Query each child component
for child_id in child_ids:
    find_one(component, {"_id": child_id})
```

### Workflow 2: Trace Bare Module to Quad Module
```bash
# Step 1: Find bare module by serial number
find_one(component, {"serialNumber": "20UPGB43000630"})
# Get ObjectId from result

# Step 2: Find parent quad module
find_all(childParentRelation, {"child": "<BARE_MODULE_OBJECT_ID>"})
# Extract parent ObjectId from results

# Step 3: Query quad module
find_one(component, {"_id": "<PARENT_OBJECT_ID>"})
```

### Workflow 3: Find All Quad Modules with Specific Bare Module
```bash
# Step 1: Find all bare modules by vendor
find_all(component, {
  "componentType": "bare_module",
  "properties": {
    "$elemMatch": {
      "code": "VENDOR",
      "value": "0"  // Advacam
    }
  }
})

# Step 2: For each bare module, find parent quad modules
for bare_module in bare_modules:
    find_all(childParentRelation, {"child": bare_module["_id"]})
```

---

## 7. Data Consistency Notes

### Expected Relationships
- A quad module should have **6 children**: 1 bare module, 1 flex PCB, 4 FE chips
- A bare module should have **4 children**: FE chips
- Frontend chips should have **2 parents**: bare module and quad module

### Common Issues
1. **Missing relationships**: Some components may not have all expected relationships
2. **Orphaned components**: Children may exist without parents
3. **Duplicate relationships**: Same parent-child pair may appear multiple times

### Verification Queries
```json
// Find quad modules with incomplete children
{
  "collection": "childParentRelation",
  "filter": {
    "parent": "<QUAD_MODULE_ID>"
  },
  "count": true
}
// Expected: 6 children per quad module

// Find orphaned components
{
  "collection": "component",
  "filter": {
    "_id": {
      "$nin": [
        // Array of all child IDs from childParentRelation
      ]
    },
    "componentType": "bare_module"
  }
}
```

---

## 8. Best Practices

### Query Optimization
1. **Use ObjectId for direct lookups**: Faster than serial number searches
2. **Cache parent-child relationships**: Reduce repeated queries
3. **Batch queries**: Fetch multiple components in one call

### Data Navigation
1. **Always verify relationships**: Check both parent and child perspectives
2. **Handle missing data gracefully**: Some relationships may not exist
3. **Use alternative identifiers**: Serial numbers or alternative IDs when ObjectId is unavailable

### Error Handling
1. **Check for null results**: Components may not have expected relationships
2. **Validate ObjectId format**: Ensure 24-character hexadecimal strings
3. **Verify component types**: Confirm expected types (module, bare_module, etc.)

---

## 9. Reference: Component Flow

```
Bare Module Production
│
├── Sensor attachment
├── FE chip bonding
└── Testing
    │
    ▼
Module Assembly
│
├── Bare module + Flex PCB gluing
├── Wirebonding
└── Testing
    │
    ▼
Final Module
│
├── Parylene coating
├── Final testing
└── Shipping
```

### Relationship Creation Timeline
1. Bare module created → FE chips added as children
2. Quad module created → bare module, flex PCB, and FE chips added as children
3. Relationships remain static after module completion

---

## 10. Troubleshooting

### No relationships found?
- Verify the component exists in `component` collection
- Check if the component is marked as `componentType: "module"` or `"bare_module"`
- Search by alternative ID if ObjectId fails

### Inconsistent child count?
- Some FE chips may be missing from relationships
- Check if components were produced in different batches
- Verify production dates match

### ObjectId search fails?
- Try searching by serial number instead
- Verify the ObjectId is 24 characters and hexadecimal
- Check for database indexing issues

---

## 11. Example: Complete Module Analysis

### Input: Quad Module Serial Number
```
20UPGM24810779 (Paris0104)
```

### Step-by-Step Analysis
1. **Find quad module** → Get ObjectId
2. **Find children** → 6 ObjectIds
3. **Classify children**:
   - 1 bare module (`20UPGB*`)
   - 1 flex PCB (`20UPGPQ*`)
   - 4 FE chips
4. **Analyze bare module**:
   - Vendor, sensor type, FE chip version
   - Production batch
5. **Analyze flex PCB**:
   - Manufacturer, design version, BOM version
6. **Verify FE chips**:
   - Confirm they appear in both bare module and quad module relationships

### Expected Output
```json
{
  "quad_module": {
    "serial": "20UPGM24810779",
    "bare_module": "20UPGB43000630",
    "flex_pcb": "20UPGPQXXXXXXX",
    "fe_chips": ["chip1", "chip2", "chip3", "chip4"],
    "vendor": "Advacam",
    "sensor_type": "Outer quad"
  }
}
```

---

## 12. Glossary

- **Quad Module**: Assembled module with bare module + flex PCB
- **Bare Module**: Module with sensor and FE chips, no PCB
- **Flex PCB**: Flexible printed circuit board for module assembly
- **FE Chip**: Frontend chip (RD53A, ITkpix_v1, ITkpix_v2, etc.)
- **CPR**: Child-Parent Relationship collection
- **ObjectId**: 24-character hexadecimal MongoDB identifier
- **Alternative ID**: Human-readable identifier (e.g., "Paris0104")
