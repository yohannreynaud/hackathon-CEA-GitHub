# MCP Server for MongoDB

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes MongoDB operations to LLM agents.

## Overview

This project provides MCP servers for querying MongoDB databases. It implements the MCP specification using streamable-http transport, enabling remote access from MCP-compatible AI clients.

Three server variants are included:

| Server | Description |
|--------|-------------|
| `mcp_server.py` | Generic MongoDB server with `find_one` and `find_all` tools |
| `mcp_server_localdb.py` | Specialized server for ITk LocalDB with domain-specific query tools (34 tools) |
| `app.py` | REST API server providing additional HTTP endpoints for LLM-driven queries |

## Documentation

Reference documentation for the LocalDB server lives in [`docs/`](docs/) — start with [`docs/INTRO.md`](docs/INTRO.md):

| File | Covers |
|------|--------|
| [`docs/INTRO.md`](docs/INTRO.md) | Orientation and quick links — start here |
| [`docs/AGENT_SYSTEM_PROMPT.md`](docs/AGENT_SYSTEM_PROMPT.md) | System prompt to paste into any agent using this MCP server |
| [`docs/TOOL_MANUAL.md`](docs/TOOL_MANUAL.md) | Full parameter reference for every tool |
| [`docs/COMMENTS_QUERY_METHOD.md`](docs/COMMENTS_QUERY_METHOD.md) | Comment retrieval patterns |
| [`docs/components/`](docs/components/) | Per-component-type docs: `MODULE.md`, `BARE_MODULE.md`, `PCB.md`, `CPR.md` |
| [`docs/changelog/`](docs/changelog/) | History of the unified-tools refactor (AMELIORATIONS, unification notes, test results) |
| [`playbooks/`](playbooks/) | Step-by-step recipes for recurring question patterns (production rate, sign-off reports, stage census, etc.) |

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp_servers

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

## Configuration

Set environment variables for MongoDB connection:

```bash
export MONGO_HOST=localhost
export MONGO_PORT=27017
export MONGO_USERNAME=<username>      # Optional
export MONGO_PASSWORD=<password>      # Optional
export MONGO_AUTHDB=admin             # Authentication database
export DATABASE_NAME=test             # Target database
```

## Running

```bash
# Generic MongoDB server
python mcp_server.py

# ITk LocalDB server (primary server)
python mcp_server_localdb.py

# Or with uvicorn for the LocalDB server
uvicorn mcp_server_localdb:app --host 0.0.0.0 --port 8000

# REST API server (alternative)
uvicorn app:app --host 0.0.0.0 --port 8001
```

## Tools

### Generic Server (`mcp_server.py`)

| Tool | Description |
|------|-------------|
| `find_one_tool` | Retrieve a single document by filter or ObjectId |
| `find_all_tool` | Retrieve multiple documents with pagination |

### LocalDB Server (`mcp_server_localdb.py`)

The LocalDB server provides **38 specialized tools** organized into the following categories:

**Base Operations:**
- `find_one_tool` - Retrieve a single document from any collection
- `find_all_tool` - Retrieve multiple documents with pagination

**Note on Projections:** All query tools (both generic and specialized) support an optional `projection` parameter to limit which fields are returned from MongoDB. This significantly reduces token usage and improves performance. Example: `{"projection": {"serialNumber": 1, "currentStage": 1}}`

**Lightweight Tools (Token-Optimized):**
- `count_tool` - Count documents matching a filter (zero token budget)
- `find_component_summary_tool` - Compact component identification (no children/test blobs)
- `find_test_summary_tool` - Compact test list (type, stage, pass/fail, date only)

**Component Lookup:**
- `find_component_by_serial_tool` - Find component by serial number
- `find_flex_pcb_by_serial_tool` - Find flex PCB by serial number
- `find_bare_module_by_serial_tool` - Find bare module by serial number
- `find_component_by_id_tool` - Find component by ObjectId
- `find_components_by_ids_tool` - Batch fetch component details for multiple ObjectIds

**Quad Module Queries:**
- `find_quad_module_by_serial_tool` - Find quad module by serial number
- `find_quad_module_by_alternative_id_tool` - Find by alternative ID (e.g., Paris0076)
- `find_production_quad_modules_tool` - List production quad modules with filters
- `find_quad_module_tests_by_stage_tool` - Get tests at specific production stage
- `find_latest_quad_module_test_tool` - Get latest test of specific type
- `find_quad_modules_with_visual_inspection_issues_tool` - Find modules with QC issues
- `find_quad_modules_with_wirebonding_problems_tool` - Find wirebonding problems
- `find_quad_modules_in_status_tool` - Find modules in QC.module.status collection

**Production Components:**
- `find_production_flex_pcbs_tool` - List production flex PCBs (PCB_DESIGN_VERSION 4 or 5)
- `find_production_bare_modules_tool` - List production bare modules with filters

**Test Results:**
- `find_latest_pcb_test_tool` - Latest PCB test at PCB_RECEPTION_MODULE_SITE stage
- `find_latest_bare_module_test_tool` - Latest bare module test at BAREMODULERECEPTION stage

**QC Status Queries:**
- `find_pcb_with_valid_tests_tool` - Find PCBs with valid tests of specified types
- `find_bare_modules_with_valid_tests_tool` - Find bare modules with valid tests

**Temporal Queries:**
- `find_tests_by_date_range_tool` - Tests within date range
- `find_components_by_date_range_tool` - Components by creation/modification date

**Advanced Queries:**
- `find_anomalous_pcb_measurements_tool` - PCBs with out-of-spec measurements
- `find_anomalous_bare_module_mass_tool` - ITkpix_v2 bare modules with anomalous mass
- `find_modules_by_test_criteria_tool` - Find modules matching test criteria with join
- `aggregate_tests_by_component_tool` - MongoDB aggregation with optional component merge

**Comment Tools:**
- `find_comments_by_component_tool` - Comments for a component by ObjectId
- `find_comments_by_alternative_id_tool` - Comments using alternative identifier
- `find_comments_by_user_tool` - Comments by user (ID or name)
- `find_comments_by_date_range_tool` - Comments within date range
- `find_comments_by_keyword_tool` - Comments containing specific keywords

**GridFS File Storage:**
- `gridfs_list_files_tool` - List files with optional filters
- `gridfs_get_file_metadata_tool` - Get file metadata by ObjectId
- `gridfs_download_file_tool` - Download file content (base64-encoded, size-limited)

## Architecture

```
┌─────────────────┐    MCP/streamable-http    ┌─────────────────┐
│   LLM Agent     │◄─────────────────────────►│   MCP Server    │
│  (Claude, etc)  │       JSON-RPC            │   (Python)      │
└─────────────────┘                           └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │    MongoDB      │
                                              │   (PyMongo)     │
                                              └─────────────────┘
```

## Testing

```bash
pytest test_mcp_server.py -v
```

## Dependencies

- Python 3.10+
- `mcp` - MCP Python SDK
- `pymongo` - MongoDB async driver
- `fastapi` - ASGI framework
- `uvicorn` - ASGI server

## License

Internal use - CERN ITk project
