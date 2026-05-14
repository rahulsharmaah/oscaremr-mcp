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

The script updates `~/.cursor/mcp.json` and preserves any existing MCP servers. It computes local paths from the current repository location instead of storing generic machine-specific paths in the docs.

After installing, restart Cursor or reload MCP servers from Cursor Settings > MCP.

## Manual Global Setup

You can also edit `~/.cursor/mcp.json` manually:

```json
{
  "mcpServers": {
    "oscar-emr-mcp": {
      "type": "stdio",
      "command": "<repository-location>\\.venv\\Scripts\\python.exe",
      "args": ["-m", "oscar_db_mcp.server"],
      "envFile": "<repository-location>\\.env"
    }
  }
}
```

Use the Python executable and `.env` file from your own local installation.
