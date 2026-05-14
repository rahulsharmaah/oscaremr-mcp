from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from oscar_db_mcp.db import OscarDbClient, OscarDbSettings, write_env_file


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def _prompt_int(label: str, default: int) -> int:
    raw_value = _prompt(label, str(default))
    try:
        return int(raw_value)
    except ValueError as exc:
        raise SystemExit(f"{label} must be a number.") from exc


def configure_interactive(env_path: Path | None = None) -> int:
    load_dotenv(dotenv_path=env_path)
    current = OscarDbSettings()

    print("Oscar EMR MCP connection setup")
    print("Enter the MariaDB details. Password input is hidden.")
    print()

    host = _prompt("Host", current.mysql_host or "localhost")
    port = _prompt_int("Port", current.mysql_port or 3306)
    database = _prompt("Database", current.mysql_database or "oscar_15")
    user = _prompt("User", current.mysql_user or "root")
    password = getpass.getpass("Password: ")
    if not password:
        password = current.mysql_password

    env_path = write_env_file(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        path=env_path,
    )

    print()
    print(f"Wrote local config: {env_path}")
    print("Testing connection...")

    settings = OscarDbSettings(
        mysql_host=host,
        mysql_port=port,
        mysql_database=database,
        mysql_user=user,
        mysql_password=password,
    )
    client = OscarDbClient(settings=settings)
    health = client.health_check()
    tables = client.list_tables()

    print(json.dumps(health, indent=2))
    print(json.dumps({"table_count": len(tables), "first_tables": tables[:20]}, indent=2))
    print("Connection OK.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Configure the Oscar EMR MCP server.")
    parser.add_argument("--interactive", action="store_true", help="Prompt for connection details.")
    parser.add_argument("--env-path", type=Path, help="Write connection settings to this env file.")
    args = parser.parse_args(argv)

    if args.interactive:
        return configure_interactive(env_path=args.env_path)

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
