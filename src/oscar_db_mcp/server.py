from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from oscar_db_mcp.db import OscarDbClient, OscarDbSettings, write_env_file

load_dotenv()

mcp = FastMCP("OSCAR oscar_15 DB")


def client() -> OscarDbClient:
    return OscarDbClient()


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Verify configuration and MariaDB reachability without exposing credentials."""
    return client().health_check()


@mcp.tool()
def list_databases() -> list[str]:
    """List databases visible to the configured MariaDB account."""
    return client().list_databases()


@mcp.tool()
def list_tables(database: str | None = None) -> list[str]:
    """List tables in oscar_15 by default, or in a supplied database name."""
    return client().list_tables(database=database)


@mcp.tool()
def describe_table(table_name: str, database: str | None = None) -> list[dict[str, Any]]:
    """Describe one table's columns, types, nullability, keys, and defaults."""
    return client().describe_table(table_name=table_name, database=database)


@mcp.tool()
def query_sql(sql: str, limit: int = 200) -> dict[str, Any]:
    """Run SELECT, SHOW, DESCRIBE, DESC, or EXPLAIN and return a limited result set."""
    result = client().query_sql(sql=sql, limit=limit)
    return {
        "columns": result.columns,
        "rows": result.rows,
        "row_count": result.row_count,
        "limited_to": result.limited_to,
    }


@mcp.tool()
def execute_admin_sql(
    sql: str,
    confirm: bool = False,
    allow_destructive: bool = False,
) -> dict[str, Any]:
    """Run confirmed admin SQL with destructive operations blocked by default."""
    return client().execute_admin_sql(
        sql=sql,
        confirm=confirm,
        allow_destructive=allow_destructive,
    )


@mcp.tool()
def configure_connection(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    test_connection: bool = True,
) -> dict[str, Any]:
    """Write local connection settings to .env, optionally testing them immediately."""
    env_path = write_env_file(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
    )
    result: dict[str, Any] = {
        "ok": True,
        "env_path": str(env_path),
        "password_saved": bool(password),
    }
    if test_connection:
        settings = OscarDbSettings(
            mysql_host=host,
            mysql_port=port,
            mysql_database=database,
            mysql_user=user,
            mysql_password=password,
        )
        result["health_check"] = OscarDbClient(settings=settings).health_check()
    return result


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
