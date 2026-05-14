---
name: oscar-db-mcp
description: Use when a user wants Codex to inspect or query an OSCAR EMR MariaDB/MySQL database through the local Oscar EMR MCP server.
---

# Oscar EMR MCP

Use the `oscar-db` MCP server for OSCAR EMR MariaDB/MySQL access.

Prefer read-only tools first:

- `health_check`
- `list_databases`
- `list_tables`
- `describe_table`
- `query_sql`

Use `execute_admin_sql` only when the user explicitly asks for writes or repair work. Require clear confirmation for destructive operations.

For local setup, run:

```powershell
.\scripts\configure_oscar_mcp.ps1
```
