from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Oscar EMR MCP in Cursor's global MCP config.")
    parser.add_argument("--python-path", required=True, help="Python executable that can import oscar_db_mcp.")
    parser.add_argument("--env-file", required=True, help="Env file containing OSCAR_MCP_* database settings.")
    args = parser.parse_args()

    python_path = Path(args.python_path).expanduser()
    env_file = Path(args.env_file).expanduser()
    if not python_path.exists():
        raise SystemExit(f"Missing Python executable: {python_path}")
    if not env_file.exists():
        raise SystemExit(f"Missing env file: {env_file}")

    cursor_dir = Path.home() / ".cursor"
    cursor_mcp = cursor_dir / "mcp.json"
    cursor_dir.mkdir(parents=True, exist_ok=True)

    if cursor_mcp.exists() and cursor_mcp.read_text(encoding="utf-8").strip():
        config = json.loads(cursor_mcp.read_text(encoding="utf-8"))
    else:
        config = {}

    servers = config.setdefault("mcpServers", {})
    servers["oscar-emr-mcp"] = {
        "type": "stdio",
        "command": str(python_path),
        "args": ["-m", "oscar_db_mcp.server"],
        "envFile": str(env_file),
    }

    cursor_mcp.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    print("Installed Oscar EMR MCP in Cursor global MCP config:")
    print(cursor_mcp)
    print()
    print("Restart Cursor or reload MCP servers from Cursor Settings > MCP.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
