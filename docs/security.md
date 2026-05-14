# Security

Oscar EMR MCP is a local development and support tool. It does not replace organizational access controls, hosted secrets management, database auditing, network controls, or healthcare privacy processes.

## Required Practices

- Never commit `.env`, passwords, database dumps, patient data, or exported PHI/PII.
- Prefer read-only database credentials for inspection.
- Use admin credentials only for intentional local maintenance.
- Review every administrative SQL operation before running it.
- Do not expose this MCP server over an untrusted network.
- Follow your clinic, organization, and jurisdictional privacy requirements when working with health data.

## SQL Guardrails

The read-only query tool accepts only inspection-oriented SQL and rejects multi-statement input.

Administrative SQL is separated into a different tool with explicit confirmation requirements, so routine schema and data inspection stays on the safer path.

## Network Exposure

If you expose MariaDB from WSL or another host, keep it on a trusted private network and prefer firewall rules that limit access to known client machines.
