from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from oscar_db_mcp.db import OscarDbClient


def like_search(value: str) -> str:
    return f"%{value.strip()}%"


def require_int(value: int | str, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer.") from exc


def default_start(days_back: int = 365) -> str:
    return (date.today() - timedelta(days=days_back)).isoformat()


def default_end(days_forward: int = 365) -> str:
    return (date.today() + timedelta(days=days_forward)).isoformat()


class BaseReadTools:
    def __init__(self, client: OscarDbClient | None = None):
        self.client = client or OscarDbClient()

    def _run(self, sql: str, params: tuple[Any, ...] = (), *, limit: int = 100) -> dict[str, Any]:
        return self.client.fetch_read_only(sql, params, limit=limit).as_dict()
