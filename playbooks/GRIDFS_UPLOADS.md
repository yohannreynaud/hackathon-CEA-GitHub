# Playbook: ITk GridFS Recent Uploads

**Use when:** the user asks about recently uploaded files/attachments for ITk modules — e.g. "Show me the last 10 modules for which a source scan have been uploaded by IRFU". Covers GridFS file listing, sorting by recency, and mapping files back to module identities.

## 1. Discover the naming/metadata convention first (if unsure)

`gridfs_list_files_tool` has no built-in sort and its `metadata_filter` requires knowing the exact metadata keys. If you don't already know how a given file type (e.g. "source scan") is named or tagged, sample first:
```json
{"tool": "gridfs_list_files_tool", "parameters": {"limit": 5}}
```
Inspect the `filename` and `metadata` fields of the sample to find the right filter (e.g. a `metadata.institution` key, or a filename pattern like `*source*scan*`).

## 2. Fetch a generous batch and sort client-side

```json
{"tool": "gridfs_list_files_tool", "parameters": {"filename": "source", "metadata_filter": {"institution": "IRFU"}, "limit": 50}}
```
The tool does not sort by `uploadDate` — fetch more than you need (e.g. `limit=50`) and sort the results by `uploadDate` descending yourself, then take the top N the user asked for.

## 3. Map files back to modules

Each file's `metadata` typically references the owning component (e.g. `metadata.component_id`). Resolve identities with:
```json
{"tool": "find_components_by_ids_tool", "parameters": {"component_ids": ["<id1>", "..."], "projection": {"serialNumber": 1, "componentType": 1}}}
```
This tool already returns the full `properties` array and auto-adds a top-level `alternative_id` field for modules.

## Output

List of the last N modules with their upload date and filename, most recent first.
