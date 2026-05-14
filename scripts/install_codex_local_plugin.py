from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def replace_tree(source: Path, target: Path) -> None:
    if target.exists() or target.is_symlink():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    shutil.copytree(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Oscar EMR MCP into a Codex local marketplace.")
    parser.add_argument("--marketplace-name", default="oscar-db-mcp-local")
    parser.add_argument("--python-path", required=True, help="Python executable that can import oscar_db_mcp.")
    parser.add_argument("--server-cwd", required=True, help="Working directory used when Codex launches the MCP server.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    marketplace_root = codex_home() / "local-marketplaces" / args.marketplace_name
    plugin_root = marketplace_root / "plugins" / "oscar-db-mcp"
    agents_plugins = marketplace_root / ".agents" / "plugins"

    marketplace_root.mkdir(parents=True, exist_ok=True)
    agents_plugins.mkdir(parents=True, exist_ok=True)

    if plugin_root.exists() or plugin_root.is_symlink():
        plugin_root_resolved = plugin_root.resolve()
        marketplace_resolved = marketplace_root.resolve()
        if marketplace_resolved not in plugin_root_resolved.parents and plugin_root_resolved != marketplace_resolved:
            raise SystemExit("Refusing to replace plugin package outside the Codex local marketplace.")
        shutil.rmtree(plugin_root)

    plugin_root.mkdir(parents=True, exist_ok=True)
    for item in [".codex-plugin", "assets", "skills"]:
        replace_tree(repo_root / item, plugin_root / item)

    mcp_config = {
        "mcpServers": {
            "oscar-db": {
                "command": str(Path(args.python_path).expanduser()),
                "args": ["-m", "oscar_db_mcp.server"],
                "cwd": str(Path(args.server_cwd).expanduser()),
            }
        }
    }
    (plugin_root / ".mcp.json").write_text(json.dumps(mcp_config, indent=2) + "\n", encoding="utf-8")

    marketplace = {
        "name": "local",
        "interface": {"displayName": "Local Plugins"},
        "plugins": [
            {
                "name": "oscar-db-mcp",
                "source": {"source": "local", "path": "./plugins/oscar-db-mcp"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            }
        ],
    }
    (agents_plugins / "marketplace.json").write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")

    print("Codex local marketplace ready:")
    print(marketplace_root)
    print()
    print("Restart Codex or refresh the Plugins page, then install Oscar EMR MCP from Local Plugins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
