# Configuration

The server reads database settings from a local `.env` file. This file is intentionally ignored by git.

## Interactive Setup

Use the setup helper:

```powershell
.\scripts\configure_oscar_mcp.ps1
```

The wizard prompts for:

- Host
- Port
- Database
- User
- Password

It writes `.env` and immediately tests the connection.

## Manual Setup

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Then fill in values for your database:

```dotenv
OSCAR_MCP_MYSQL_HOST=<mysql-host>
OSCAR_MCP_MYSQL_PORT=3306
OSCAR_MCP_MYSQL_DATABASE=<database-name>
OSCAR_MCP_MYSQL_USER=<readonly-user>
OSCAR_MCP_MYSQL_PASSWORD=<password>
OSCAR_MCP_CONNECT_TIMEOUT=5
OSCAR_MCP_READ_TIMEOUT=30
OSCAR_MCP_WRITE_TIMEOUT=30
```

## Live Smoke Test

After configuring `.env`, run:

```powershell
@'
from oscar_db_mcp.db import OscarDbClient

client = OscarDbClient()
print(client.health_check())
print(client.list_tables()[:20])
'@ | python -
```

The health check response intentionally reports whether a user and password are configured, but it never returns the password value.
