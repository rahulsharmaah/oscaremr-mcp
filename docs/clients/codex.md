# Codex Setup

This repository includes local Codex plugin metadata.

## Local Plugin

Add the project location you cloned on your machine as a local plugin path in Codex.

The plugin manifest lives at:

```text
.codex-plugin/plugin.json
```

The plugin points Codex at the MCP server definition in:

```text
.mcp.json
```

## Direct MCP Registration

If you prefer direct MCP configuration, adapt this template to your environment:

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

For non-Windows environments, use the Python executable inside the virtual environment for that platform.

## Test the MCP Stream

Use the stream test helper:

```powershell
.\scripts\test_oscar_mcp_stream.ps1
```

This verifies that an MCP client can launch the server and call `health_check`.
