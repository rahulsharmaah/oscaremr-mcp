# Claude Code Setup

Use the helper script to print a Claude Code registration command:

```powershell
.\scripts\install_claude_code_mcp.ps1
```

The script prints a command similar to:

```powershell
claude mcp add-json oscar-db '{...}'
```

Run the printed command in the same environment where `claude` is available.

If Claude Code is not on `PATH`, copy the generated server JSON into your Claude MCP configuration.
