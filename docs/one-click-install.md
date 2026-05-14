# One-Click Install

Oscar EMR MCP can be simple for clinic teams, but the database connection still has to be configured safely. The project supports friendly local setup paths for Windows, macOS, Linux, Cursor, and Codex Desktop.

## Windows Setup

Download or clone the project and double-click:

```text
Install Oscar EMR MCP.cmd
```

The installer:

- creates a local Python environment;
- installs Oscar EMR MCP dependencies;
- opens the database connection wizard;
- prepares the Codex local plugin package;
- registers the MCP server with Cursor when a database config exists.

Users still need their OSCAR database host, database name, read-only username, and password.

## macOS And Linux Setup

Download or clone the project, open a terminal in the project, and run:

```bash
./scripts/install_oscar_emr_mcp_unix.sh
```

The installer:

- creates a local Python environment under the user's data directory;
- installs Oscar EMR MCP dependencies;
- opens the database connection wizard;
- prepares the Codex local plugin package;
- registers the MCP server with Cursor when a database config exists.

Users still need their OSCAR database host, database name, read-only username, and password.

## Add To Cursor

If `oscar-db-mcp` is already installed on the computer, Cursor can add the MCP server from this deeplink:

[Add Oscar EMR MCP to Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=oscar-emr-mcp&config=eyJ0eXBlIjoic3RkaW8iLCJjb21tYW5kIjoib3NjYXItZGItbWNwIiwiYXJncyI6W10sImVudkZpbGUiOiIke3VzZXJIb21lfSR7L30ub3NjYXJlbXItbWNwJHsvfS5lbnYifQ%3D%3D)

This deeplink installs this MCP configuration:

```json
{
  "type": "stdio",
  "command": "oscar-db-mcp",
  "args": [],
  "envFile": "${userHome}${/}.oscaremr-mcp${/}.env"
}
```

Cursor will still need the database connection values to be configured through the guided setup, `oscar-db-mcp-configure --interactive`, or equivalent environment variables.

## Codex Desktop

Codex Desktop can use the generated local marketplace package:

```powershell
.\scripts\install_codex_local_plugin.ps1
```

For non-technical users, the guided platform setup above runs this automatically. After setup, restart Codex or refresh the Plugins page, then install Oscar EMR MCP from Local Plugins.

## Codex Cloud

The current server is local stdio software. Codex Cloud runs in a sandboxed cloud environment, so it cannot directly reach a clinic's private OSCAR database unless there is a secure network path.

True one-click Codex Cloud support requires a remote MCP gateway:

- HTTPS MCP endpoint;
- authentication and tenant management;
- encrypted database secrets;
- network access to the clinic database or a clinic-side connector;
- audit logs and admin controls;
- least-privilege read-only database access by default.

That gateway should be a separate hosted product or self-hosted deployment. Once it exists, Codex Cloud can connect to the HTTPS MCP endpoint instead of launching the local stdio server.

