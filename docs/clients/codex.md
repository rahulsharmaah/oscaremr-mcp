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

If you prefer direct MCP configuration after installing the package, use the console command:

```json
{
  "mcpServers": {
    "oscar-db": {
      "command": "oscar-db-mcp",
      "args": []
    }
  }
}
```

Configure connection values with `oscar-db-mcp-configure --interactive`, or provide the `OSCAR_MCP_*` environment variables through your MCP client.

## Test the MCP Stream

Use the stream test helper:

```powershell
.\scripts\test_oscar_mcp_stream.ps1
```

This verifies that an MCP client can launch the server and call `health_check`.
