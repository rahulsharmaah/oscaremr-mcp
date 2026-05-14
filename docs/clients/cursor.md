# Cursor Setup

Cursor supports MCP servers through `mcp.json`.

The official Cursor MCP docs support two useful locations:

- Project config: `.cursor/mcp.json`
- Global config: `~/.cursor/mcp.json`

Cursor also resolves variables such as `${workspaceFolder}`, `${userHome}`, and `${/}` in MCP config fields.

## Project Setup

This repository includes a project-level Cursor config:

```json
{
  "mcpServers": {
    "oscar-emr-mcp": {
      "type": "stdio",
      "command": "${workspaceFolder}${/}.venv${/}Scripts${/}python.exe",
      "args": ["-m", "oscar_db_mcp.server"],
      "envFile": "${workspaceFolder}${/}.env"
    }
  }
}
```

Use this when opening the repository itself in Cursor.

## Global Setup on Windows

To make Oscar EMR MCP available from any Cursor workspace on this machine, run:

```powershell
.\scripts\install_cursor_mcp.ps1
```

The script updates Cursor's global MCP configuration and preserves any existing MCP servers. It computes the needed local values during installation instead of hardcoding machine-specific paths in the docs.

After installing, restart Cursor or reload MCP servers from Cursor Settings > MCP.

## Manual Global Setup

You can also add the server manually after installing the package:

```json
{
  "mcpServers": {
    "oscar-emr-mcp": {
      "type": "stdio",
      "command": "oscar-db-mcp",
      "args": []
    }
  }
}
```

Configure connection values with `oscar-db-mcp-configure --interactive`, or set the `OSCAR_MCP_*` environment variables in Cursor's MCP configuration.
