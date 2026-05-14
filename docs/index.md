---
title: OSCAR EMR MCP Server
description: Safe local MCP server for guarded OSCAR EMR MariaDB/MySQL access from Codex, Claude Code, Cursor, and other AI agents.
keywords:
  - OSCAR EMR MCP
  - OSCAR EMR database
  - Oscar EMR
  - Oscar Yammer
  - Oscar DB MCP
  - OSCAR MariaDB
  - OSCAR MySQL
  - Model Context Protocol
  - MCP server
  - AI agent database access
image: /img/oscar-db-mcp-logo.svg
---

# Oscar EMR MCP

OSCAR EMR MCP Server is a local Model Context Protocol server for guarded access to OSCAR EMR MariaDB/MySQL databases. It helps AI agents such as Codex, Claude Code, Cursor, and other MCP-compatible tools inspect OSCAR database structure safely.

It is designed for development and support workflows where an MCP client needs structured database visibility without embedding credentials in source control.

People sometimes search for this workflow with phrases like Oscar EMR database MCP, Oscar DB MCP, OSCAR MariaDB AI agent access, or voice-transcribed variants such as Oscar Yammer. This project is the safe local MCP server for that OSCAR EMR database inspection workflow.

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
