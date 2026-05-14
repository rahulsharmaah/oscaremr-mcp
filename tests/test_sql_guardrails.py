import pytest

from oscar_db_mcp.db import (
    SqlGuardError,
    quote_identifier,
    validate_admin_sql,
    validate_read_only_sql,
)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM demographic",
        "SHOW TABLES",
        "DESCRIBE demographic",
        "DESC demographic",
        "EXPLAIN SELECT * FROM demographic",
    ],
)
def test_query_sql_allows_read_only_statements(sql):
    assert validate_read_only_sql(sql) == sql


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE demographic SET last_name = 'x'",
        "INSERT INTO demographic (last_name) VALUES ('x')",
        "DELETE FROM demographic",
        "ALTER TABLE demographic ADD COLUMN x int",
        "DROP TABLE demographic",
    ],
)
def test_query_sql_rejects_writes(sql):
    with pytest.raises(SqlGuardError):
        validate_read_only_sql(sql)


def test_multi_statement_sql_is_rejected():
    with pytest.raises(SqlGuardError):
        validate_read_only_sql("SELECT 1; SELECT 2")


def test_query_sql_rejects_select_into_outfile():
    with pytest.raises(SqlGuardError):
        validate_read_only_sql("SELECT * FROM demographic INTO OUTFILE '/tmp/export.txt'")


def test_admin_sql_requires_confirmation():
    with pytest.raises(SqlGuardError):
        validate_admin_sql("UPDATE demographic SET last_name = 'x'", confirm=False, allow_destructive=False)


def test_admin_sql_allows_confirmed_non_destructive_write():
    assert (
        validate_admin_sql(
            "UPDATE demographic SET last_name = 'x'",
            confirm=True,
            allow_destructive=False,
        )
        == "UPDATE demographic SET last_name = 'x'"
    )


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM demographic WHERE demographic_no = 1",
        "ALTER TABLE demographic ADD COLUMN x int",
        "DROP TABLE demographic",
        "TRUNCATE TABLE demographic",
    ],
)
def test_admin_sql_blocks_destructive_without_flag(sql):
    with pytest.raises(SqlGuardError):
        validate_admin_sql(sql, confirm=True, allow_destructive=False)


def test_admin_sql_allows_destructive_with_flag():
    assert (
        validate_admin_sql(
            "DELETE FROM demographic WHERE demographic_no = 1",
            confirm=True,
            allow_destructive=True,
        )
        == "DELETE FROM demographic WHERE demographic_no = 1"
    )


def test_identifier_quoting_blocks_unsafe_table_names():
    assert quote_identifier("demographic") == "`demographic`"
    with pytest.raises(SqlGuardError):
        quote_identifier("demographic; DROP TABLE provider")
