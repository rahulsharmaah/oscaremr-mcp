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

## Reliable Local Marketplace Setup

For a lean local plugin package, run:

```powershell
.\scripts\install_codex_local_plugin.ps1
```

On macOS/Linux, use:

```bash
python scripts/install_codex_local_plugin.py \
  --python-path "$HOME/.local/share/oscaremr-mcp/.venv/bin/python" \
  --server-cwd "$HOME/.local/share/oscaremr-mcp"
```

The script creates a Codex local marketplace package with only plugin metadata, assets, skills, and an MCP config that points back to your installed server. This avoids copying development folders such as virtual environments, dependency caches, build output, or git history into the plugin package.

After running it, restart Codex or refresh the Plugins page, then install Oscar EMR MCP from Local Plugins.

For non-technical Windows users, the all-in-one setup runs this step automatically:

```text
Install Oscar EMR MCP.cmd
```

For macOS/Linux users, run:

```bash
./scripts/install_oscar_emr_mcp_unix.sh
```

## Codex Cloud

Codex Cloud cannot use this local stdio server directly unless its cloud sandbox can reach the OSCAR database. For one-click cloud use, Oscar EMR MCP needs a hosted or self-hosted HTTPS MCP gateway with authentication, encrypted database secrets, audit logs, and clinic network access.

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

## Troubleshooting Install Failures

If Codex shows `Failed to install plugin`, check these first:

- Run `.\scripts\install_codex_local_plugin.ps1` and install from the generated Local Plugins marketplace.
- On macOS/Linux, run `./scripts/install_oscar_emr_mcp_unix.sh` and install from the generated Local Plugins marketplace.
- Confirm the server can start with `.\scripts\test_oscar_mcp_stream.ps1`.
- Restart Codex after installing or updating a local plugin.
- Avoid installing from a full development checkout that includes virtual environments, dependency folders, build output, or git history.

## Test the MCP Stream

Use the stream test helper:

```powershell
.\scripts\test_oscar_mcp_stream.ps1
```

This verifies that an MCP client can launch the server and call `health_check`.
