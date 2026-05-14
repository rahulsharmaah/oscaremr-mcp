# Contributing

Contributions should preserve the project’s safety-first design.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,docs]"
pytest
```

## Before Opening a Pull Request

- Keep credentials and local environment details out of commits.
- Add or update tests for SQL guardrail changes.
- Prefer portable examples over machine-specific paths or IP addresses.
- Keep MCP tool responses free of configured passwords.

## Documentation

Build the docs locally:

```powershell
mkdocs build --strict
```

Preview the docs locally:

```powershell
mkdocs serve
```
