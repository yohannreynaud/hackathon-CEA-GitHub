# How to Find Comments for a Module or Component

This document describes multiple methods for finding comments in the LocalDB database, from the basic manual approach to using specialized MCP tools.

## Overview

The LocalDB database stores comments in a dedicated `comments` collection. Each comment document contains:
- `component`: ObjectId of the component being commented on
- `comment`: The actual comment text
- `user_id` and `name`: Who created the comment
- `datetime`: When the comment was created (ISO format)
- `componentType`: Type of component (e.g., "module", "bare_module", "module_pcb")

There are **5 specialized MCP tools** for comment retrieval, which are the recommended approach:

| Tool | Purpose |
|------|---------|
| `find_comments_by_component_tool` | Find comments by component ObjectId |
| `find_comments_by_alternative_id_tool` | Find comments using alternative ID (e.g., Paris0060) |
| `find_comments_by_user_tool` | Find comments by user (ID or name) |
| `find_comments_by_date_range_tool` | Find comments within a date range |
| `find_comments_by_keyword_tool` | Find comments containing specific keywords |

## Method 1: Using Specialized MCP Tools (Recommended)

### Find Comments by Alternative ID (Simplest)

For quad modules with alternative IDs (e.g., Paris0060):

```json
{
  "tool": "find_comments_by_alternative_id_tool",
  "parameters": {
    "alternative_id": "Paris0060",
    "component_type": "module"
  }
}
```

This tool automatically:
1. Looks up the component by alternative ID
2. Extracts the ObjectId
3. Returns all comments for that component

### Find Comments by Component ObjectId

If you already have the component ObjectId:

```json
{
  "tool": "find_comments_by_component_tool",
  "parameters": {
    "component_id": "69204afc44c06a9763fa2c11",
    "limit": 20
  }
}
```

### Find Comments by User

To find all comments made by a specific user:

```json
{
  "tool": "find_comments_by_user_tool",
  "parameters": {
    "user_name": "John Doe",
    "start_date": "2025-01-01T00:00:00Z"
  }
}
```

### Find Comments by Date Range

To find comments within a specific time period:

```json
{
  "tool": "find_comments_by_date_range_tool",
  "parameters": {
    "start_date": "2025-06-01T00:00:00Z",
    "end_date": "2025-06-30T23:59:59Z",
    "component_type": "module"
  }
}
```

### Find Comments by Keyword

To search for comments containing specific terms:

```json
{
  "tool": "find_comments_by_keyword_tool",
  "parameters": {
    "keywords": ["wirebond", "breakdown", "disconnected"],
    "component_type": "module",
    "case_sensitive": false
  }
}
```

## Method 2: Manual Query Approach (Legacy)

This is the original method using generic tools. It still works but the specialized tools above are preferred.

To find comments for a specific module given its alternative identifier (e.g., "Paris0060"):

### Step 1: Find the Module Component
Use `find_one_tool` to find the module by its alternative identifier:

```json
{
  "tool": "find_one_tool",
  "parameters": {
    "collection": "component",
    "filter": {
      "properties": {
        "$elemMatch": {
          "code": "ALTERNATIVE_IDENTIFIER",
          "value": "ParisXXXX"
        }
      },
      "componentType": "module"
    }
  }
}
```

Or use the optimized `find_component_summary_tool`:

```json
{
  "tool": "find_component_summary_tool",
  "parameters": {
    "alternative_id": "ParisXXXX"
  }
}
```

### Step 2: Extract the ObjectId
From the result, extract the `_id` field (e.g., "69204afc44c06a9763fa2c11")

### Step 3: Find Comments for the Component
Use `find_all_tool` to find all comments for that component:

```json
{
  "tool": "find_all_tool",
  "parameters": {
    "collection": "comments",
    "filter": {
      "component": "COMPONENT_OBJECT_ID"
    },
    "limit": 20
  }
}
```

Where `COMPONENT_OBJECT_ID` is the ObjectId from Step 2.

## Example Workflows

### Example 1: Quick Comment Lookup by Alternative ID
```json
{
  "tool": "find_comments_by_alternative_id_tool",
  "parameters": {
    "alternative_id": "Paris0060"
  }
}
```

### Example 2: Full Manual Workflow
1. Find module Paris0060:
```json
{
  "tool": "find_component_summary_tool",
  "parameters": {
    "alternative_id": "Paris0060"
  }
}
```

2. Extract ObjectId: "69204afc44c06a9763fa2c11"

3. Find comments:
```json
{
  "tool": "find_comments_by_component_tool",
  "parameters": {
    "component_id": "69204afc44c06a9763fa2c11"
  }
}
```

## Notes

- **Multiple comments** can exist for the same component
- **Not all modules have comments** - it's normal for some components to have no comments
- **Comments can be created at different stages** of production and testing
- **Use the specialized tools** when possible - they are optimized and easier to use
- **Date formats** are in ISO format with timezone: `YYYY-MM-DDTHH:MM:SS.SSS+00:00`
- **Pagination**: All comment tools support `limit` and `skip` parameters for handling large result sets