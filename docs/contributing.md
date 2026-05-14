# Contributing

Contributions should preserve the project’s safety-first design.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Before Opening a Pull Request

- Keep credentials and local environment details out of commits.
- Add or update tests for SQL guardrail changes.
- Prefer portable examples over machine-specific paths or IP addresses.
- Keep MCP tool responses free of configured passwords.
- Put new EMR tool logic in the matching `oscar_db_mcp.emr` feature module.
- Add MCP wrappers in `oscar_db_mcp.server` only after the domain logic is covered.

## Project Structure

Read [Project Architecture](architecture.md) before adding new tools. The MCP entry point stays thin, while OSCAR EMR behavior is grouped by feature area under `oscar_db_mcp.emr`.

## Documentation

Build the docs locally:

```powershell
npm install
npm run build
```

Preview the docs locally:

```powershell
npm run start
```
