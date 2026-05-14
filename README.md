# oscaremr-mcp

`oscaremr-mcp` is a local Model Context Protocol (MCP) server for guarded access to OSCAR EMR MariaDB/MySQL databases. It is designed for healthcare development and support workflows where Codex, Claude Code, or another MCP client needs structured database visibility without hardcoding credentials into source control.

The server runs over stdio, reads connection details from a local ignored `.env`, and exposes tools for health checks, schema inspection, read-only SQL, and explicitly confirmed admin SQL.

## Documentation

The full installation and usage guide is published with GitHub Pages:

https://rahulsharmaah.github.io/oscaremr-mcp/

## Key Features

- Local stdio MCP server built with the official Python MCP SDK `FastMCP`.
- Works with OSCAR EMR and Agentic Clinic-style MariaDB/MySQL databases.
- Interactive setup wizard that writes local credentials to `.env` and tests the connection.
- Codex plugin metadata included via `.codex-plugin/plugin.json`.
- Claude Code helper script that prints the `claude mcp add-json` registration command.
- Guarded SQL execution:
  - Read-only `query_sql` allows only `SELECT`, `SHOW`, `DESCRIBE`, `DESC`, and `EXPLAIN`.
  - Multi-statement SQL is rejected.
  - Admin SQL requires `confirm=true`.
  - `DROP`, `TRUNCATE`, `ALTER`, and `DELETE` require `allow_destructive=true`.
  - Tool responses never return configured passwords.

## MCP Tools

- `health_check`: verifies connection settings and MariaDB reachability without exposing secrets.
- `list_databases`: lists databases visible to the configured account.
- `list_tables`: lists tables in the configured database.
- `describe_table(table_name)`: returns table column metadata.
- `query_sql(sql, limit=200)`: runs guarded read-only SQL with a bounded result set.
- `execute_admin_sql(sql, confirm=true, allow_destructive=false)`: runs confirmed admin SQL with destructive operations blocked by default.
- `configure_connection(...)`: writes connection settings to `.env` and can immediately test them.

## Requirements

- Windows, macOS, or Linux
- Python 3.11+
- Network access to the OSCAR EMR MariaDB/MySQL endpoint
- A MariaDB/MySQL account with the least privilege needed for your workflow

For routine inspection, use a read-only database account. Use root/admin credentials only for local repair work where you understand the impact.

## Installation

```powershell
git clone https://github.com/rahulsharmaah/oscaremr-mcp.git
cd <repository-directory>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

On macOS/Linux:

```bash
git clone https://github.com/rahulsharmaah/oscaremr-mcp.git
cd <repository-directory>
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Configure a Database Connection

Use the interactive wizard:

```powershell
.\scripts\configure_oscar_mcp.ps1
```

The wizard prompts for:

- Host
- Port
- Database
- User
- Password

It writes the values to `.env`, then runs a live connection test. Password input is hidden in the terminal. `.env` is ignored by git and must never be committed.

You can also copy `.env.example` manually:

```powershell
Copy-Item .env.example .env
```

Example:

```dotenv
OSCAR_MCP_MYSQL_HOST=<mysql-host>
OSCAR_MCP_MYSQL_PORT=3306
OSCAR_MCP_MYSQL_DATABASE=<database-name>
OSCAR_MCP_MYSQL_USER=<readonly-user>
OSCAR_MCP_MYSQL_PASSWORD=<password>
```

## Expose OSCAR WSL MariaDB

If OSCAR EMR is running inside WSL on another Windows machine, expose MariaDB through the Windows host before configuring this MCP server.

On the OSCAR Windows host, run PowerShell as Administrator:

```powershell
$wslIp = (wsl -d Ubuntu-22.04 hostname -I).Trim().Split(" ")[0]
wsl -d Ubuntu-22.04 -u root -- bash -lc "sed -i 's/^\s*bind-address\s*=.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf && (systemctl restart mariadb || service mariadb restart)"
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3306
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3306 connectaddress=$wslIp connectport=3306
New-NetFirewallRule -DisplayName "Allow OSCAR MariaDB 3306" -Direction Inbound -Protocol TCP -LocalPort 3306 -Action Allow
```

Then verify from the MCP client machine:

```powershell
Test-NetConnection <oscar-windows-lan-ip> -Port 3306
```

For the full setup, refresh, removal, and troubleshooting guide, see [docs/EXPOSE_OSCAR_WSL_MARIADB.md](docs/EXPOSE_OSCAR_WSL_MARIADB.md).

## Run the MCP Server

```powershell
python -m oscar_db_mcp.server
```

The process waits for an MCP client over stdio. That quiet waiting state is expected.

After installation, this command is also available:

```powershell
oscar-db-mcp
```

## Codex Usage

This repository includes a local Codex plugin manifest:

```text
.codex-plugin/plugin.json
```

Add the repository location you cloned on your machine as a local plugin path in Codex.

For a direct MCP server registration, adapt this template to the location where you keep the repository:

```json
{
  "mcpServers": {
    "oscar-db": {
      "command": "<repository-location>\\.venv\\Scripts\\python.exe",
      "args": ["-m", "oscar_db_mcp.server"],
      "cwd": "<repository-location>"
    }
  }
}
```

## Claude Code Usage

Print the Claude Code registration command:

```powershell
.\scripts\install_claude_code_mcp.ps1
```

The script prints a command like:

```powershell
claude mcp add-json oscar-db '{...}'
```

Run the printed command in the same environment where `claude` is available.

## Smoke Tests

Run unit tests:

```powershell
pytest
```

Run a live database smoke test after configuring `.env`:

```powershell
@'
from oscar_db_mcp.db import OscarDbClient

client = OscarDbClient()
print(client.health_check())
print(client.list_tables()[:20])
'@ | python -
```

Verify that an MCP client can launch the server and call `health_check`:

```powershell
.\scripts\test_oscar_mcp_stream.ps1
```

## Security Model

This project is a local development/support tool. It does not provide a remote auth layer, hosted secrets manager, audit system, or role-based access control by itself.

Required operating rules:

- Never commit `.env`, passwords, database dumps, patient data, or exported PHI/PII.
- Prefer read-only database credentials for inspection.
- Use admin credentials only for intentional local maintenance.
- Review every `execute_admin_sql` call before running it.
- Do not expose this MCP server over an untrusted network.
- Follow your clinic, organization, and jurisdictional privacy requirements when working with health data.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening issues or pull requests.

## License

MIT. See [LICENSE](LICENSE).
