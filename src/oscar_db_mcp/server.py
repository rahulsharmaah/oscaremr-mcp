from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from oscar_db_mcp.db import OscarDbClient, OscarDbSettings, write_env_file
from oscar_db_mcp.domain import OscarEmrReadTools

load_dotenv()

mcp = FastMCP("OSCAR oscar_15 DB")


def client() -> OscarDbClient:
    return OscarDbClient()


def read_tools() -> OscarEmrReadTools:
    return OscarEmrReadTools(client())


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
    return result.as_dict()


@mcp.tool()
def find_patients(
    search: str | None = None,
    last_name: str | None = None,
    first_name: str | None = None,
    hin: str | None = None,
    chart_no: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Find patients by name, HIN, chart number, or broad search text."""
    return read_tools().find_patients(search, last_name, first_name, hin, chart_no, limit)


@mcp.tool()
def get_patient_summary(demographic_no: int) -> dict[str, Any]:
    """Return a patient identity, roster, status, and provider summary."""
    return read_tools().get_patient_summary(demographic_no)


@mcp.tool()
def get_patient_contacts(demographic_no: int) -> dict[str, Any]:
    """Return patient contact and address fields from demographic."""
    return read_tools().get_patient_contacts(demographic_no)


@mcp.tool()
def get_patient_pharmacies(demographic_no: int, limit: int = 20) -> dict[str, Any]:
    """List pharmacy links for a patient."""
    return read_tools().get_patient_pharmacies(demographic_no, limit)


@mcp.tool()
def get_patient_chart_index(demographic_no: int) -> dict[str, Any]:
    """Return counts and latest dates for major patient chart areas."""
    return read_tools().get_patient_chart_index(demographic_no)


@mcp.tool()
def get_patient_timeline(
    demographic_no: int,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Return a bounded chronological patient timeline across key chart areas."""
    return read_tools().get_patient_timeline(demographic_no, start_date, end_date, limit)


@mcp.tool()
def list_patient_appointments(
    demographic_no: int,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List patient appointments within a date window."""
    return read_tools().list_patient_appointments(demographic_no, start_date, end_date, limit)


@mcp.tool()
def get_appointment_detail(appointment_no: int) -> dict[str, Any]:
    """Return one appointment's scheduling metadata and notes."""
    return read_tools().get_appointment_detail(appointment_no)


@mcp.tool()
def list_provider_schedule(provider_no: str, start_date: str, end_date: str, limit: int = 200) -> dict[str, Any]:
    """List a provider schedule from appointments for a date window."""
    return read_tools().list_provider_schedule(provider_no, start_date, end_date, limit)


@mcp.tool()
def list_no_shows_or_cancellations(
    provider_no: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List appointments whose status suggests no-show or cancellation."""
    return read_tools().list_no_shows_or_cancellations(provider_no, start_date, end_date, limit)


@mcp.tool()
def list_patient_allergies(demographic_no: int, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
    """List patient allergies and reactions."""
    return read_tools().list_patient_allergies(demographic_no, include_archived, limit)


@mcp.tool()
def list_patient_medications(demographic_no: int, active_only: bool = True, limit: int = 100) -> dict[str, Any]:
    """List patient medication rows from drugs."""
    return read_tools().list_patient_medications(demographic_no, active_only, limit)


@mcp.tool()
def search_drug_history(demographic_no: int, medication: str, limit: int = 100) -> dict[str, Any]:
    """Search a patient's drug history by medication name."""
    return read_tools().search_drug_history(demographic_no, medication, limit)


@mcp.tool()
def list_expiring_or_recently_ended_meds(days: int = 30, limit: int = 100) -> dict[str, Any]:
    """List medications ending within a recent/upcoming day window."""
    return read_tools().list_expiring_or_recently_ended_meds(days, limit)


@mcp.tool()
def list_patient_prescriptions(demographic_no: int, limit: int = 100) -> dict[str, Any]:
    """List prescription/script history for a patient."""
    return read_tools().list_patient_prescriptions(demographic_no, limit)


@mcp.tool()
def get_prescription_detail(script_no: int) -> dict[str, Any]:
    """Return one prescription/script with its drug rows."""
    return read_tools().get_prescription_detail(script_no)


@mcp.tool()
def list_patient_measurements(
    demographic_no: int,
    measurement_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List patient measurements/vitals with optional type and date filters."""
    return read_tools().list_patient_measurements(demographic_no, measurement_type, start_date, end_date, limit)


@mcp.tool()
def trend_patient_measurement(demographic_no: int, measurement_type: str, limit: int = 200) -> dict[str, Any]:
    """Return measurement rows for trending a patient measurement type."""
    return read_tools().trend_patient_measurement(demographic_no, measurement_type, limit)


@mcp.tool()
def list_measurement_types(search: str | None = None, limit: int = 200) -> dict[str, Any]:
    """List configured measurement types."""
    return read_tools().list_measurement_types(search, limit)


@mcp.tool()
def list_patient_preventions(demographic_no: int, include_deleted: bool = False, limit: int = 100) -> dict[str, Any]:
    """List patient prevention records."""
    return read_tools().list_patient_preventions(demographic_no, include_deleted, limit)


@mcp.tool()
def get_prevention_detail(prevention_id: int, limit: int = 100) -> dict[str, Any]:
    """Return one prevention with extension values."""
    return read_tools().get_prevention_detail(prevention_id, limit)


@mcp.tool()
def list_due_preventions(
    demographic_no: int | None = None,
    provider_no: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List prevention rows with next_date due today or earlier."""
    return read_tools().list_due_preventions(demographic_no, provider_no, limit)


@mcp.tool()
def list_patient_notes(demographic_no: int, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
    """List patient chart note metadata and snippets."""
    return read_tools().list_patient_notes(demographic_no, include_archived, limit)


@mcp.tool()
def get_note_detail(note_id: int) -> dict[str, Any]:
    """Return one chart note by note_id."""
    return read_tools().get_note_detail(note_id)


@mcp.tool()
def search_patient_notes(demographic_no: int, term: str, limit: int = 100) -> dict[str, Any]:
    """Search note text within one patient's chart."""
    return read_tools().search_patient_notes(demographic_no, term, limit)


@mcp.tool()
def list_patient_issues(demographic_no: int, active_only: bool = True, limit: int = 100) -> dict[str, Any]:
    """List patient issues/problem-list rows."""
    return read_tools().list_patient_issues(demographic_no, active_only, limit)


@mcp.tool()
def list_patient_ticklers(demographic_no: int, open_only: bool = True, limit: int = 100) -> dict[str, Any]:
    """List patient ticklers/tasks."""
    return read_tools().list_patient_ticklers(demographic_no, open_only, limit)


@mcp.tool()
def list_provider_ticklers(provider_no: str, status: str | None = None, limit: int = 100) -> dict[str, Any]:
    """List ticklers assigned to a provider."""
    return read_tools().list_provider_ticklers(provider_no, status, limit)


@mcp.tool()
def get_tickler_detail(tickler_no: int, limit: int = 100) -> dict[str, Any]:
    """Return one tickler with comments."""
    return read_tools().get_tickler_detail(tickler_no, limit)


@mcp.tool()
def list_patient_messages(demographic_no: int, limit: int = 100) -> dict[str, Any]:
    """List message metadata linked to a patient."""
    return read_tools().list_patient_messages(demographic_no, limit)


@mcp.tool()
def get_message_metadata(message_id: int, limit: int = 50) -> dict[str, Any]:
    """Return metadata for one message without attachment blobs."""
    return read_tools().get_message_metadata(message_id, limit)


@mcp.tool()
def list_patient_documents(demographic_no: int, limit: int = 100) -> dict[str, Any]:
    """List patient document metadata without file contents."""
    return read_tools().list_patient_documents(demographic_no, limit)


@mcp.tool()
def get_document_metadata(document_no: int) -> dict[str, Any]:
    """Return document metadata without file contents."""
    return read_tools().get_document_metadata(document_no)


@mcp.tool()
def list_unreviewed_documents(provider_no: str | None = None, limit: int = 100) -> dict[str, Any]:
    """List document metadata for unreviewed documents."""
    return read_tools().list_unreviewed_documents(provider_no, limit)


@mcp.tool()
def list_patient_eforms(demographic_no: int, limit: int = 100) -> dict[str, Any]:
    """List submitted eForms for a patient."""
    return read_tools().list_patient_eforms(demographic_no, limit)


@mcp.tool()
def get_eform_values(fdid: int, limit: int = 200) -> dict[str, Any]:
    """Return structured eForm variable values for one submitted form."""
    return read_tools().get_eform_values(fdid, limit)


@mcp.tool()
def list_patient_labs(demographic_no: int, limit: int = 100) -> dict[str, Any]:
    """List patient lab routing and lab metadata."""
    return read_tools().list_patient_labs(demographic_no, limit)


@mcp.tool()
def get_lab_results(lab_patient_physician_info_id: int, limit: int = 200) -> dict[str, Any]:
    """Return structured lab result rows for one lab patient/physician info id."""
    return read_tools().get_lab_results(lab_patient_physician_info_id, limit)


@mcp.tool()
def list_abnormal_labs(start_date: str | None = None, end_date: str | None = None, limit: int = 100) -> dict[str, Any]:
    """List lab result rows with non-empty abnormal flags."""
    return read_tools().list_abnormal_labs(start_date, end_date, limit)


@mcp.tool()
def list_patient_consults(demographic_no: int, limit: int = 100) -> dict[str, Any]:
    """List consultation/referral requests for a patient."""
    return read_tools().list_patient_consults(demographic_no, limit)


@mcp.tool()
def get_consult_detail(request_id: int) -> dict[str, Any]:
    """Return one consultation request detail."""
    return read_tools().get_consult_detail(request_id)


@mcp.tool()
def list_consults_by_status(status: str, provider_no: str | None = None, limit: int = 100) -> dict[str, Any]:
    """List consultation requests by status, optionally scoped to a provider."""
    return read_tools().list_consults_by_status(status, provider_no, limit)


@mcp.tool()
def list_patient_billing_summary(demographic_no: int, limit: int = 100) -> dict[str, Any]:
    """List patient billing claim summary rows."""
    return read_tools().list_patient_billing_summary(demographic_no, limit)


@mcp.tool()
def get_billing_claim_detail(billing_no: int, limit: int = 100) -> dict[str, Any]:
    """Return billing claim detail rows for one billing number."""
    return read_tools().get_billing_claim_detail(billing_no, limit)


@mcp.tool()
def search_billing_codes(search: str, limit: int = 100) -> dict[str, Any]:
    """Search billing service and diagnostic codes."""
    return read_tools().search_billing_codes(search, limit)


@mcp.tool()
def list_provider_directory(status: str | None = None, limit: int = 200) -> dict[str, Any]:
    """List providers with contact and specialty metadata."""
    return read_tools().list_provider_directory(status, limit)


@mcp.tool()
def get_provider_summary(provider_no: str) -> dict[str, Any]:
    """Return provider directory details."""
    return read_tools().get_provider_summary(provider_no)


@mcp.tool()
def search_specialists(search: str, limit: int = 100) -> dict[str, Any]:
    """Search specialist/referral contact directory."""
    return read_tools().search_specialists(search, limit)


@mcp.tool()
def get_access_roles_for_provider(provider_no: str, limit: int = 100) -> dict[str, Any]:
    """List security user and role names for a provider without password fields."""
    return read_tools().get_access_roles_for_provider(provider_no, limit)


@mcp.tool()
def audit_patient_access_log(
    demographic_no: int,
    start_date: str | None = None,
    end_date: str | None = None,
    action: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List audit log rows for one patient/date/action scope."""
    return read_tools().audit_patient_access_log(demographic_no, start_date, end_date, action, limit)


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
