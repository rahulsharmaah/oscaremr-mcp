# Project Architecture

Oscar EMR MCP keeps the public MCP entry point small and moves EMR-specific behavior into feature modules.

## Python Package Layout

- `oscar_db_mcp.server`: MCP tool registration and thin request forwarding.
- `oscar_db_mcp.db`: database settings, SQL guardrails, connection handling, and query result shaping.
- `oscar_db_mcp.configure`: command-line connection setup.
- `oscar_db_mcp.domain`: compatibility import for the full read-only EMR toolset.
- `oscar_db_mcp.emr.base`: shared helpers for date defaults, search terms, integer validation, and read-only execution.
- `oscar_db_mcp.emr.patients`: patient search, summary, contacts, pharmacies, chart index, and timeline.
- `oscar_db_mcp.emr.scheduling`: appointments, provider schedules, no-shows, and cancellations.
- `oscar_db_mcp.emr.medications`: allergies, medications, drug history, and prescriptions.
- `oscar_db_mcp.emr.clinical`: measurements and preventions.
- `oscar_db_mcp.emr.workflow`: notes, issues, ticklers, and messages.
- `oscar_db_mcp.emr.records`: documents, eForms, labs, and consults.
- `oscar_db_mcp.emr.billing`: billing codes, claims, providers, specialists, access roles, and audit logs.

## Adding A Tool

1. Put the SQL and domain logic in the matching `oscar_db_mcp.emr` module.
2. Keep user inputs parameterized through `fetch_read_only`; do not format user-provided values into SQL strings.
3. Add a thin wrapper in `oscar_db_mcp.server` with the `@mcp.tool()` decorator.
4. Document the tool in `docs/tools.md`.
5. Add a focused test for important guardrails, parameters, or result fields.

## Design Rules

- Keep `server.py` as transport glue, not business logic.
- Keep feature modules small enough for review by domain.
- Avoid returning password, PIN, TOTP, document blob, attachment, or raw file-content fields.
- Prefer read-only tools for routine workflows; keep administrative actions separate and explicit.
