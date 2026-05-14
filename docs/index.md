# OSCAR DB MCP

OSCAR DB MCP is a local Model Context Protocol server for guarded access to Agentic Clinic and OSCAR EMR MariaDB/MySQL databases.

It is designed for development and support workflows where an MCP client needs structured database visibility without embedding credentials in source control.

## What It Provides

- Health checks for configured MariaDB connectivity.
- Database and table discovery.
- Table schema inspection.
- Guarded read-only SQL execution.
- Confirmed administrative SQL for intentional maintenance work.
- Local setup helpers for Codex and Claude Code.

## Safety Model

The default workflow is inspection-first. Read-only SQL is limited to `SELECT`, `SHOW`, `DESCRIBE`, `DESC`, and `EXPLAIN`, and multi-statement SQL is rejected.

Administrative SQL is available only through a separate tool that requires explicit confirmation. Destructive operations require an additional opt-in flag.

## Typical Flow

1. Install the Python package in a local virtual environment.
2. Configure a MariaDB connection with the setup wizard.
3. Register the MCP server with your client.
4. Use read-only tools for schema inspection and safe queries.

## Requirements

- Python 3.11 or newer.
- Network access to the target MariaDB/MySQL server.
- A MariaDB/MySQL account with the least privilege needed for your workflow.

For routine inspection, prefer a read-only database account.
