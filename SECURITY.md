# Security Policy

## Supported Versions

This project is pre-1.0. Security fixes are applied to the `main` branch.

## Reporting a Vulnerability

If you find a vulnerability, do not open a public issue.

Report privately to the repository owner:

- GitHub: `rahulsharmaah`
- Repository: `https://github.com/rahulsharmaah/oscaremr-mcp`

Include:

- A concise description of the issue.
- Steps to reproduce using dummy data.
- Impact assessment.
- Any proposed fix.

Do not include real patient data, production database dumps, credentials, or private keys.

## Security Expectations

`oscaremr-mcp` is a local MCP server for database workflows. It does not replace organizational access controls, auditing, network controls, or healthcare privacy processes.

Operators are responsible for:

- Using least-privilege database accounts.
- Keeping `.env` private and out of source control.
- Running the server only on trusted machines.
- Reviewing admin SQL before execution.
- Following applicable health privacy laws and organizational policies.

## Secret Handling

The project intentionally uses `.env` for local development credentials. `.env` is ignored by git. Example values belong in `.env.example`; real credentials do not.

If a secret is accidentally committed:

1. Revoke or rotate the secret immediately.
2. Remove it from the repository history if needed.
3. Audit any systems that used the exposed credential.
4. Add or improve guardrails that would have prevented the leak.
