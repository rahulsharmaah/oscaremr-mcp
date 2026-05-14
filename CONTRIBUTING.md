# Contributing to oscaremr-mcp

Thank you for helping improve `oscaremr-mcp`. This project touches clinical database workflows, so contributions must keep safety, privacy, and predictable behavior ahead of convenience.

## Contributor Rules

1. Do not commit secrets.
   Never commit `.env`, passwords, tokens, private keys, database dumps, screenshots containing credentials, or connection strings with real credentials.

2. Do not commit patient data.
   Do not include PHI/PII, OSCAR production records, exported clinic data, logs containing patient details, or screenshots of patient charts.

3. Prefer least privilege.
   New tools and examples should default to read-only access. Admin/write operations must be explicit, guarded, and documented.

4. Keep destructive actions guarded.
   Any feature that can modify data must require a clear confirmation flag. Destructive operations such as `DROP`, `TRUNCATE`, `ALTER`, and `DELETE` must remain blocked unless explicitly enabled.

5. Keep MCP tool outputs bounded.
   Query tools should return limited result sets by default. Avoid adding unbounded table dumps or broad export helpers.

6. Maintain local-first behavior.
   This server is intended to run locally over stdio. Do not add hosted telemetry, remote logging, or network exposure without a clear design discussion.

7. Preserve compatibility.
   Avoid breaking existing tool names, argument names, environment variables, or setup scripts unless the change is necessary and documented.

8. Write tests for guardrails.
   Any change to SQL validation, admin execution, configuration, or tool behavior must include focused tests.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Pull Request Checklist

Before opening a pull request:

- Run `pytest`.
- Confirm no `.env` or secret files are staged.
- Confirm no PHI/PII or production data is included.
- Update `README.md` when user-facing behavior changes.
- Update `docs/tools.md` and `docs/architecture.md` when adding or moving MCP tools.
- Add or update tests for SQL guardrails and configuration behavior.
- Explain any admin/write capability changes clearly in the PR description.

## Issue Guidelines

When filing an issue:

- Describe the expected behavior and actual behavior.
- Include OS, Python version, MCP client, and MariaDB/MySQL version when relevant.
- Redact hostnames, usernames, passwords, patient names, chart numbers, and clinic-specific data.
- Include minimal reproduction steps using dummy data.

## Code Style

- Keep code small and explicit.
- Put EMR read-tool logic in the matching `oscar_db_mcp.emr` feature module.
- Keep `oscar_db_mcp.server` focused on MCP registration and thin forwarding.
- Prefer standard library and already-declared dependencies.
- Avoid broad abstractions unless they remove real duplication.
- Return structured data from MCP tools where possible.
- Keep comments focused on non-obvious safety or protocol decisions.

## Security Reports

Do not open a public issue for suspected credential exposure, SQL guardrail bypasses, or privacy-sensitive defects. Follow [SECURITY.md](SECURITY.md).
