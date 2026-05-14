# MCP Tools

The server exposes a small set of database tools with guardrails around SQL execution.

## `health_check`

Verifies connection settings and MariaDB reachability without exposing credentials.

## `list_databases`

Lists databases visible to the configured MariaDB account.

## `list_tables`

Lists tables in the configured database by default, or in a supplied database name.

## `describe_table`

Returns column metadata for one table, including type, nullability, keys, defaults, and extras.

## `query_sql`

Runs guarded read-only SQL and returns a bounded result set.

Allowed starts:

- `SELECT`
- `SHOW`
- `DESCRIBE`
- `DESC`
- `EXPLAIN`

Rejected patterns:

- Empty SQL.
- Multi-statement SQL.
- `SELECT INTO OUTFILE`.
- `SELECT INTO DUMPFILE`.

## `execute_admin_sql`

Runs confirmed administrative SQL.

This tool requires `confirm=true`. Destructive operations such as `DROP`, `TRUNCATE`, `ALTER`, and `DELETE` require `allow_destructive=true`.

Use this tool only for intentional local maintenance work.

## `configure_connection`

Writes local connection settings to `.env` and can immediately test the connection.
