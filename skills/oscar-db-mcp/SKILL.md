---
name: oscar-db-mcp
description: Use when a user wants Codex to inspect or query an Agentic Clinic or OSCAR EMR MariaDB/MySQL database through the local OSCAR DB MCP server.
---

# OSCAR DB MCP

Use the `oscar-db` MCP server for Agentic Clinic or OSCAR EMR MariaDB access.

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
