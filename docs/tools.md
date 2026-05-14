# MCP Tools

Oscar EMR MCP exposes a guarded database toolkit plus a broad set of structured read-only EMR lookup tools.

All structured EMR tools generate SQL internally, use parameterized values, and return bounded result sets shaped like:

```json
{
  "columns": ["..."],
  "rows": [{ "...": "..." }],
  "row_count": 1,
  "limited_to": 100
}
```

## Core Database Tools

- `health_check`: verify configuration and MariaDB reachability without exposing credentials.
- `list_databases`: list databases visible to the configured account.
- `list_tables`: list tables in the configured database or a supplied database.
- `describe_table`: describe columns, keys, defaults, and extras for one table.
- `query_sql`: run guarded `SELECT`, `SHOW`, `DESCRIBE`, `DESC`, or `EXPLAIN` SQL.
- `execute_admin_sql`: run confirmed admin SQL; destructive SQL requires `allow_destructive=true`.
- `configure_connection`: write local `.env` settings and optionally test the connection.

## Patient And Chart Navigation

- `find_patients`: search demographics by name, HIN, chart number, or broad text.
- `get_patient_summary`: return identity, DOB, status, roster, and provider summary.
- `get_patient_contacts`: return patient contact and address fields.
- `get_patient_pharmacies`: list pharmacy links for a patient.
- `get_patient_chart_index`: return counts and latest dates for major chart areas.
- `get_patient_timeline`: combine appointments, notes, medications, and ticklers into a bounded timeline.

## Scheduling

- `list_patient_appointments`: list patient appointments in a date window.
- `get_appointment_detail`: return one appointment with reason, status, notes, and metadata.
- `list_provider_schedule`: list a provider appointment schedule for a date window.
- `list_no_shows_or_cancellations`: list appointment rows whose status suggests no-show or cancellation.

## Medications And Allergies

- `list_patient_allergies`: list allergy and reaction rows.
- `list_patient_medications`: list active or historical medication rows.
- `search_drug_history`: search one patient's medication history by medication name.
- `list_expiring_or_recently_ended_meds`: find medications ending in a recent/upcoming window.
- `list_patient_prescriptions`: list prescription/script history.
- `get_prescription_detail`: return one prescription with drug rows.

## Measurements And Prevention

- `list_patient_measurements`: list vitals/measurements with optional type and date filters.
- `trend_patient_measurement`: return rows for trending one measurement type.
- `list_measurement_types`: list configured measurement types.
- `list_patient_preventions`: list prevention/immunization/screening rows.
- `get_prevention_detail`: return one prevention with extension values.
- `list_due_preventions`: list prevention rows due today or earlier.

## Notes, Issues, Tasks, And Messages

- `list_patient_notes`: list chart note metadata and snippets.
- `get_note_detail`: return one chart note by note ID.
- `search_patient_notes`: search note text within one patient chart.
- `list_patient_issues`: list problem/issue rows.
- `list_patient_ticklers`: list patient ticklers/tasks.
- `list_provider_ticklers`: list ticklers assigned to a provider.
- `get_tickler_detail`: return one tickler with comments.
- `list_patient_messages`: list message metadata linked to a patient.
- `get_message_metadata`: return message metadata without attachment blobs.

## Documents, eForms, Labs, And Consults

- `list_patient_documents`: list patient document metadata without file contents.
- `get_document_metadata`: return document metadata without file contents.
- `list_unreviewed_documents`: list unreviewed document metadata.
- `list_patient_eforms`: list submitted eForms for a patient.
- `get_eform_values`: return structured eForm variables for one submitted form.
- `list_patient_labs`: list patient lab routing and lab metadata, including `lab_patient_physician_info_id` when OSCAR can link the lab to structured results.
- `get_lab_results`: return structured lab result rows by `lab_patient_physician_info_id`.
- `list_abnormal_labs`: list lab rows with abnormal flags in a date window.
- `list_patient_consults`: list patient consultation/referral requests.
- `get_consult_detail`: return one consultation request.
- `list_consults_by_status`: list consultation requests by status and optional provider.

## Billing, Provider Directory, And Audit

- `list_patient_billing_summary`: list billing claim summary rows for a patient.
- `get_billing_claim_detail`: return billing claim detail rows for one billing number.
- `search_billing_codes`: search billing service and diagnostic codes.
- `list_provider_directory`: list providers with contact and specialty metadata.
- `get_provider_summary`: return one provider's administrative directory details, including contact, billing, registration, and practitioner identifiers.
- `search_specialists`: search the specialist/referral contact directory.
- `get_access_roles_for_provider`: list security user and role names without password fields.
- `audit_patient_access_log`: list audit log rows for one patient/date/action scope.

## Guardrails

- Broad raw SQL remains restricted to read-only statements in `query_sql`.
- Structured EMR tools use internal SQL and parameter binding for user-provided values.
- Result limits are clamped between `1` and `1000`.
- Tools avoid password, PIN, TOTP, document blob, attachment, and raw file-content fields.
- Administrative SQL remains separate from routine read-only tools.
