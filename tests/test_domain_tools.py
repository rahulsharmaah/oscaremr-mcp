from oscar_db_mcp.db import QueryResult, bounded_limit
from oscar_db_mcp.domain import OscarEmrReadTools


class FakeClient:
    def __init__(self):
        self.calls = []

    def fetch_read_only(self, sql, params=None, *, limit=100):
        self.calls.append((sql, tuple(params or ()), limit))
        return QueryResult(columns=["ok"], rows=[{"ok": True}], row_count=1, limited_to=limit)


def test_bounded_limit_clamps_values():
    assert bounded_limit(0) == 1
    assert bounded_limit(-10) == 1
    assert bounded_limit(25) == 25
    assert bounded_limit(10_000) == 1000
    assert bounded_limit("bad", default=50) == 50


def test_query_result_as_dict():
    result = QueryResult(columns=["a"], rows=[{"a": 1}], row_count=1, limited_to=10)
    assert result.as_dict() == {
        "columns": ["a"],
        "rows": [{"a": 1}],
        "row_count": 1,
        "limited_to": 10,
    }


def test_find_patients_uses_parameters_for_search_text():
    fake = FakeClient()
    tools = OscarEmrReadTools(fake)
    payload = "abc'; DROP TABLE demographic; --"

    tools.find_patients(search=payload, limit=5)

    sql, params, limit = fake.calls[0]
    assert payload not in sql
    assert params == tuple([f"%{payload}%"] * 4)
    assert limit == 5


def test_access_roles_query_omits_sensitive_security_columns():
    fake = FakeClient()
    tools = OscarEmrReadTools(fake)

    tools.get_access_roles_for_provider("999998")

    sql, _, _ = fake.calls[0]
    lowered = sql.lower()
    assert "password" not in lowered
    assert "pin" not in lowered
    assert "totp" not in lowered


def test_list_abnormal_labs_applies_date_window():
    fake = FakeClient()
    tools = OscarEmrReadTools(fake)

    tools.list_abnormal_labs(start_date="2026-01-01", end_date="2026-01-31", limit=20)

    sql, params, limit = fake.calls[0]
    assert "BETWEEN %s AND %s" in sql
    assert "labPatientPhysicianInfo" in sql
    assert params == ("2026-01-01", "2026-01-31")
    assert limit == 20


def test_list_patient_labs_exposes_result_chain_id():
    fake = FakeClient()
    tools = OscarEmrReadTools(fake)

    tools.list_patient_labs(123, limit=10)

    sql, params, limit = fake.calls[0]
    assert "p.id AS lab_patient_physician_info_id" in sql
    assert "labPatientPhysicianInfo" in sql
    assert params == (123,)
    assert limit == 10
