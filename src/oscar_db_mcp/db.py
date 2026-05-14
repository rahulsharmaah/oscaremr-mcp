from __future__ import annotations

import re
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import pymysql
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymysql.connections import Connection
from pymysql.cursors import DictCursor


IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_$]+$")
READ_ONLY_START_RE = re.compile(r"^\s*(select|show|describe|desc|explain)\b", re.IGNORECASE)
READ_ONLY_FORBIDDEN_RE = re.compile(r"\binto\s+(out|dump)file\b", re.IGNORECASE)
DESTRUCTIVE_RE = re.compile(r"\b(drop|truncate|alter|delete)\b", re.IGNORECASE)


class SqlGuardError(ValueError):
    """Raised when SQL does not satisfy the MCP server guardrails."""


class OscarDbSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OSCAR_MCP_",
        extra="ignore",
    )

    mysql_host: str = Field(default="localhost")
    mysql_port: int = Field(default=3306)
    mysql_database: str = Field(default="oscar_15")
    mysql_user: str = Field(default="")
    mysql_password: str = Field(default="")
    connect_timeout: int = Field(default=5)
    read_timeout: int = Field(default=30)
    write_timeout: int = Field(default=30)

    @property
    def safe_config(self) -> dict[str, Any]:
        return {
            "host": self.mysql_host,
            "port": self.mysql_port,
            "database": self.mysql_database,
            "user_configured": bool(self.mysql_user),
            "password_configured": bool(self.mysql_password),
            "connect_timeout": self.connect_timeout,
            "read_timeout": self.read_timeout,
            "write_timeout": self.write_timeout,
        }


def env_file_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".env"


def write_env_file(
    *,
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    connect_timeout: int = 5,
    read_timeout: int = 30,
    write_timeout: int = 30,
    path: Path | None = None,
) -> Path:
    selected_path = path or env_file_path()
    lines = [
        f"OSCAR_MCP_MYSQL_HOST={host}",
        f"OSCAR_MCP_MYSQL_PORT={int(port)}",
        f"OSCAR_MCP_MYSQL_DATABASE={database}",
        f"OSCAR_MCP_MYSQL_USER={user}",
        f"OSCAR_MCP_MYSQL_PASSWORD={password}",
        f"OSCAR_MCP_CONNECT_TIMEOUT={int(connect_timeout)}",
        f"OSCAR_MCP_READ_TIMEOUT={int(read_timeout)}",
        f"OSCAR_MCP_WRITE_TIMEOUT={int(write_timeout)}",
        "",
    ]
    selected_path.write_text("\n".join(lines), encoding="ascii")
    return selected_path


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    limited_to: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "columns": self.columns,
            "rows": self.rows,
            "row_count": self.row_count,
            "limited_to": self.limited_to,
        }


def bounded_limit(limit: int, *, default: int = 100, maximum: int = 1000) -> int:
    try:
        selected = int(limit)
    except (TypeError, ValueError):
        selected = int(default)
    return max(1, min(selected, int(maximum)))


def quote_identifier(value: str) -> str:
    if not IDENTIFIER_RE.fullmatch(value):
        raise SqlGuardError(f"Unsafe identifier: {value!r}")
    return f"`{value}`"


def normalize_sql(sql: str) -> str:
    cleaned = sql.strip()
    if not cleaned:
        raise SqlGuardError("SQL must not be empty.")

    while cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()

    if ";" in cleaned:
        raise SqlGuardError("Multi-statement SQL is not allowed.")

    return cleaned


def validate_read_only_sql(sql: str) -> str:
    cleaned = normalize_sql(sql)
    if not READ_ONLY_START_RE.match(cleaned):
        raise SqlGuardError("query_sql only allows SELECT, SHOW, DESCRIBE, DESC, or EXPLAIN.")
    if READ_ONLY_FORBIDDEN_RE.search(cleaned):
        raise SqlGuardError("query_sql does not allow SELECT INTO OUTFILE or DUMPFILE.")
    return cleaned


def validate_admin_sql(
    sql: str,
    *,
    confirm: bool,
    allow_destructive: bool,
) -> str:
    if not confirm:
        raise SqlGuardError("execute_admin_sql requires confirm=true.")

    cleaned = normalize_sql(sql)
    if DESTRUCTIVE_RE.search(cleaned) and not allow_destructive:
        raise SqlGuardError(
            "DROP, TRUNCATE, ALTER, and DELETE require allow_destructive=true."
        )
    return cleaned


class OscarDbClient:
    def __init__(self, settings: OscarDbSettings | None = None):
        self.settings = settings or OscarDbSettings()

    @contextmanager
    def connect(self, database: str | None = None) -> Iterator[Connection]:
        connection = pymysql.connect(
            host=self.settings.mysql_host,
            port=int(self.settings.mysql_port),
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            database=database if database is not None else self.settings.mysql_database,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=True,
            connect_timeout=int(self.settings.connect_timeout),
            read_timeout=int(self.settings.read_timeout),
            write_timeout=int(self.settings.write_timeout),
        )
        try:
            yield connection
        finally:
            connection.close()

    def health_check(self) -> dict[str, Any]:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DATABASE() AS database_name, VERSION() AS version")
                row = cursor.fetchone() or {}
        return {
            "ok": True,
            "config": self.settings.safe_config,
            "database_name": row.get("database_name"),
            "server_version": row.get("version"),
        }

    def list_databases(self) -> list[str]:
        with self.connect(database=None) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                rows = cursor.fetchall()
        return [str(next(iter(row.values()))) for row in rows]

    def list_tables(self, database: str | None = None) -> list[str]:
        selected_database = database or self.settings.mysql_database
        with self.connect(database=selected_database) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                rows = cursor.fetchall()
        return [str(next(iter(row.values()))) for row in rows]

    def describe_table(self, table_name: str, database: str | None = None) -> list[dict[str, Any]]:
        selected_database = database or self.settings.mysql_database
        table_sql = quote_identifier(table_name)
        with self.connect(database=selected_database) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_sql}")
                return list(cursor.fetchall())

    def query_sql(self, sql: str, limit: int = 200) -> QueryResult:
        cleaned = validate_read_only_sql(sql)
        safe_limit = bounded_limit(limit, default=200, maximum=1000)
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(cleaned)
                rows = list(cursor.fetchmany(safe_limit))
                columns = [description[0] for description in cursor.description or []]
        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            limited_to=safe_limit,
        )

    def fetch_read_only(
        self,
        sql: str,
        params: tuple[Any, ...] | list[Any] | None = None,
        *,
        limit: int = 100,
    ) -> QueryResult:
        cleaned = validate_read_only_sql(sql)
        safe_limit = bounded_limit(limit, default=100, maximum=1000)
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(cleaned, tuple(params or ()))
                rows = list(cursor.fetchmany(safe_limit))
                columns = [description[0] for description in cursor.description or []]
        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            limited_to=safe_limit,
        )

    def execute_admin_sql(
        self,
        sql: str,
        *,
        confirm: bool = False,
        allow_destructive: bool = False,
    ) -> dict[str, Any]:
        cleaned = validate_admin_sql(
            sql,
            confirm=confirm,
            allow_destructive=allow_destructive,
        )
        with self.connect() as connection:
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(cleaned)
        return {
            "ok": True,
            "affected_rows": affected_rows,
            "destructive_allowed": allow_destructive,
        }
