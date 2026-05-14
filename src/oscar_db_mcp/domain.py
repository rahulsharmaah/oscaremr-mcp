from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from oscar_db_mcp.db import OscarDbClient, bounded_limit


def _like(value: str) -> str:
    return f"%{value.strip()}%"


def _int(value: int | str, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer.") from exc


def _default_start(days_back: int = 365) -> str:
    return (date.today() - timedelta(days=days_back)).isoformat()


def _default_end(days_forward: int = 365) -> str:
    return (date.today() + timedelta(days=days_forward)).isoformat()


class OscarEmrReadTools:
    def __init__(self, client: OscarDbClient | None = None):
        self.client = client or OscarDbClient()

    def _run(self, sql: str, params: tuple[Any, ...] = (), *, limit: int = 100) -> dict[str, Any]:
        return self.client.fetch_read_only(sql, params, limit=limit).as_dict()

    def find_patients(
        self,
        search: str | None = None,
        last_name: str | None = None,
        first_name: str | None = None,
        hin: str | None = None,
        chart_no: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        clauses: list[str] = []
        params: list[Any] = []
        if hin:
            clauses.append("d.hin = %s")
            params.append(hin)
        if chart_no:
            clauses.append("d.chart_no = %s")
            params.append(chart_no)
        if last_name:
            clauses.append("d.last_name LIKE %s")
            params.append(_like(last_name))
        if first_name:
            clauses.append("d.first_name LIKE %s")
            params.append(_like(first_name))
        if search:
            clauses.append("(d.last_name LIKE %s OR d.first_name LIKE %s OR d.chart_no LIKE %s OR d.hin LIKE %s)")
            params.extend([_like(search), _like(search), _like(search), _like(search)])
        if not clauses:
            raise ValueError("Provide search, last_name, first_name, hin, or chart_no.")
        sql = """
            SELECT d.demographic_no, d.last_name, d.first_name, d.year_of_birth,
                   d.month_of_birth, d.date_of_birth, d.sex, d.hin, d.chart_no,
                   d.patient_status, d.provider_no
            FROM demographic d
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY d.last_name, d.first_name
        """
        return self._run(sql, tuple(params), limit=limit)

    def get_patient_summary(self, demographic_no: int) -> dict[str, Any]:
        sql = """
            SELECT d.demographic_no, d.title, d.last_name, d.first_name, d.middleNames,
                   d.pref_name, d.year_of_birth, d.month_of_birth, d.date_of_birth,
                   d.sex, d.gender, d.hin, d.ver, d.chart_no, d.patient_status,
                   d.roster_status, d.roster_date, d.provider_no,
                   p.first_name AS provider_first_name, p.last_name AS provider_last_name,
                   d.lastUpdateDate
            FROM demographic d
            LEFT JOIN provider p ON p.provider_no = d.provider_no
            WHERE d.demographic_no = %s
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=1)

    def get_patient_contacts(self, demographic_no: int) -> dict[str, Any]:
        sql = """
            SELECT demographic_no, address, city, province, postal, phone, phone2,
                   email, consentToUseEmailForCare, family_doctor, family_physician,
                   residentialAddress, residentialCity, residentialProvince, residentialPostal
            FROM demographic
            WHERE demographic_no = %s
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=1)

    def get_patient_pharmacies(self, demographic_no: int, limit: int = 20) -> dict[str, Any]:
        sql = """
            SELECT dp.id, dp.pharmacyID, dp.demographic_no, dp.status, dp.addDate, dp.preferredOrder
            FROM demographicPharmacy dp
            WHERE dp.demographic_no = %s
            ORDER BY dp.preferredOrder, dp.addDate DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_patient_chart_index(self, demographic_no: int) -> dict[str, Any]:
        demo = _int(demographic_no, "demographic_no")
        sql = """
            SELECT 'appointments' AS area, COUNT(*) AS item_count, MAX(appointment_date) AS latest_date FROM appointment WHERE demographic_no = %s
            UNION ALL SELECT 'notes', COUNT(*), MAX(observation_date) FROM casemgmt_note WHERE demographic_no = %s
            UNION ALL SELECT 'medications', COUNT(*), MAX(rx_date) FROM drugs WHERE demographic_no = %s
            UNION ALL SELECT 'allergies', COUNT(*), MAX(lastUpdateDate) FROM allergies WHERE demographic_no = %s
            UNION ALL SELECT 'measurements', COUNT(*), MAX(dateObserved) FROM measurements WHERE demographicNo = %s
            UNION ALL SELECT 'ticklers', COUNT(*), MAX(update_date) FROM tickler WHERE demographic_no = %s
            UNION ALL SELECT 'eforms', COUNT(*), MAX(form_date) FROM eform_data WHERE demographic_no = %s
            UNION ALL SELECT 'consults', COUNT(*), MAX(lastUpdateDate) FROM consultationRequests WHERE demographicNo = %s
            UNION ALL SELECT 'billing', COUNT(*), MAX(billing_date) FROM billing WHERE demographic_no = %s
        """
        return self._run(sql, (demo, demo, demo, demo, demo, demo, demo, demo, demo), limit=20)

    def get_patient_timeline(
        self,
        demographic_no: int,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        demo = _int(demographic_no, "demographic_no")
        start = start_date or _default_start()
        end = end_date or _default_end(30)
        sql = """
            SELECT 'appointment' AS event_type, appointment_date AS event_date,
                   appointment_no AS item_id, provider_no, status,
                   LEFT(CONCAT(COALESCE(reason,''), ' ', COALESCE(notes,'')), 240) AS summary
            FROM appointment
            WHERE demographic_no = %s AND appointment_date BETWEEN %s AND %s
            UNION ALL
            SELECT 'note', observation_date, note_id, provider_no, signed,
                   LEFT(REPLACE(note, '\n', ' '), 240)
            FROM casemgmt_note
            WHERE demographic_no = %s AND observation_date BETWEEN %s AND %s
            UNION ALL
            SELECT 'medication', rx_date, drugid, provider_no, archived,
                   LEFT(CONCAT(COALESCE(BN,''), ' ', COALESCE(GN,''), ' ', COALESCE(customName,'')), 240)
            FROM drugs
            WHERE demographic_no = %s AND rx_date BETWEEN %s AND %s
            UNION ALL
            SELECT 'tickler', service_date, tickler_no, task_assigned_to, status,
                   LEFT(message, 240)
            FROM tickler
            WHERE demographic_no = %s AND service_date BETWEEN %s AND %s
            ORDER BY event_date DESC
        """
        return self._run(sql, (demo, start, end, demo, start, end, demo, start, end, demo, start, end), limit=limit)

    def list_patient_appointments(
        self,
        demographic_no: int,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        sql = """
            SELECT a.appointment_no, a.provider_no, p.first_name AS provider_first_name,
                   p.last_name AS provider_last_name, a.appointment_date, a.start_time,
                   a.end_time, a.status, a.type, a.reasonCode, a.reason, a.location,
                   LEFT(a.notes, 240) AS notes
            FROM appointment a
            LEFT JOIN provider p ON p.provider_no = a.provider_no
            WHERE a.demographic_no = %s AND a.appointment_date BETWEEN %s AND %s
            ORDER BY a.appointment_date DESC, a.start_time DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), start_date or _default_start(365), end_date or _default_end(90)), limit=limit)

    def get_appointment_detail(self, appointment_no: int) -> dict[str, Any]:
        sql = """
            SELECT a.appointment_no, a.demographic_no, a.provider_no, a.appointment_date,
                   a.start_time, a.end_time, a.status, a.type, a.reasonCode, a.reason,
                   a.location, a.resources, a.billing, a.urgency, a.creator,
                   a.createdatetime, a.updatedatetime, a.notes, a.remarks
            FROM appointment a
            WHERE a.appointment_no = %s
        """
        return self._run(sql, (_int(appointment_no, "appointment_no"),), limit=1)

    def list_provider_schedule(
        self,
        provider_no: str,
        start_date: str,
        end_date: str,
        limit: int = 200,
    ) -> dict[str, Any]:
        sql = """
            SELECT a.appointment_no, a.demographic_no, a.name, a.appointment_date,
                   a.start_time, a.end_time, a.status, a.type, a.reason, a.location
            FROM appointment a
            WHERE a.provider_no = %s AND a.appointment_date BETWEEN %s AND %s
            ORDER BY a.appointment_date, a.start_time
        """
        return self._run(sql, (provider_no, start_date, end_date), limit=limit)

    def list_no_shows_or_cancellations(
        self,
        provider_no: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        clauses = ["a.appointment_date BETWEEN %s AND %s", "(LOWER(a.status) LIKE '%%n%%' OR LOWER(a.status) LIKE '%%c%%' OR LOWER(a.status) LIKE '%%cancel%%' OR LOWER(a.status) LIKE '%%no%%')"]
        params: list[Any] = [start_date or _default_start(90), end_date or date.today().isoformat()]
        if provider_no:
            clauses.append("a.provider_no = %s")
            params.append(provider_no)
        sql = """
            SELECT a.appointment_no, a.demographic_no, a.provider_no, a.appointment_date,
                   a.start_time, a.end_time, a.status, a.type, a.reason
            FROM appointment a
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY a.appointment_date DESC, a.start_time DESC
        """
        return self._run(sql, tuple(params), limit=limit)

    def list_patient_allergies(self, demographic_no: int, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT allergyid, demographic_no, entry_date, DESCRIPTION, TYPECODE, reaction,
                   archived, start_date, severity_of_reaction, onset_of_reaction,
                   providerNo, nonDrug, lastUpdateDate
            FROM allergies
            WHERE demographic_no = %s AND (%s OR COALESCE(archived, '0') = '0')
            ORDER BY position, entry_date DESC, allergyid DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), bool(include_archived)), limit=limit)

    def list_patient_medications(self, demographic_no: int, active_only: bool = True, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT d.drugid, d.provider_no, d.demographic_no, d.rx_date, d.end_date,
                   d.BN, d.GN, d.customName, d.dosage, d.quantity, d.freqcode,
                   d.duration, d.durunit, d.repeat, d.route, d.drug_form,
                   d.archived, d.long_term, d.prn, d.script_no, d.lastUpdateDate
            FROM drugs d
            WHERE d.demographic_no = %s
              AND (%s = FALSE OR (COALESCE(d.archived, 0) = 0 AND (d.end_date IS NULL OR d.end_date >= CURDATE())))
            ORDER BY d.rx_date DESC, d.drugid DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), bool(active_only)), limit=limit)

    def search_drug_history(self, demographic_no: int, medication: str, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT drugid, rx_date, end_date, BN, GN, customName, dosage, quantity,
                   freqcode, archived, script_no
            FROM drugs
            WHERE demographic_no = %s
              AND (BN LIKE %s OR GN LIKE %s OR customName LIKE %s)
            ORDER BY rx_date DESC, drugid DESC
        """
        term = _like(medication)
        return self._run(sql, (_int(demographic_no, "demographic_no"), term, term, term), limit=limit)

    def list_expiring_or_recently_ended_meds(self, days: int = 30, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT drugid, demographic_no, provider_no, rx_date, end_date, BN, GN,
                   customName, quantity, freqcode, archived, script_no
            FROM drugs
            WHERE end_date BETWEEN DATE_SUB(CURDATE(), INTERVAL %s DAY)
                              AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY end_date DESC
        """
        safe_days = max(1, min(_int(days, "days"), 365))
        return self._run(sql, (safe_days, safe_days), limit=limit)

    def list_patient_prescriptions(self, demographic_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT p.script_no, p.provider_no, p.demographic_no, p.date_prescribed,
                   p.date_printed, p.dates_reprinted, LEFT(p.rx_comments, 240) AS rx_comments,
                   COUNT(d.drugid) AS drug_count
            FROM prescription p
            LEFT JOIN drugs d ON d.script_no = p.script_no
            WHERE p.demographic_no = %s
            GROUP BY p.script_no, p.provider_no, p.demographic_no, p.date_prescribed,
                     p.date_printed, p.dates_reprinted, p.rx_comments
            ORDER BY p.date_prescribed DESC, p.script_no DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_prescription_detail(self, script_no: int) -> dict[str, Any]:
        sql = """
            SELECT p.script_no, p.provider_no, p.demographic_no, p.date_prescribed,
                   p.date_printed, p.dates_reprinted, p.textView, p.rx_comments,
                   d.drugid, d.BN, d.GN, d.customName, d.dosage, d.quantity,
                   d.freqcode, d.duration, d.durunit, d.repeat, d.route, d.end_date
            FROM prescription p
            LEFT JOIN drugs d ON d.script_no = p.script_no
            WHERE p.script_no = %s
            ORDER BY d.position, d.drugid
        """
        return self._run(sql, (_int(script_no, "script_no"),), limit=100)

    def list_patient_measurements(
        self,
        demographic_no: int,
        measurement_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        clauses = ["m.demographicNo = %s", "m.dateObserved BETWEEN %s AND %s"]
        params: list[Any] = [_int(demographic_no, "demographic_no"), start_date or _default_start(), end_date or _default_end(0)]
        if measurement_type:
            clauses.append("m.type = %s")
            params.append(measurement_type)
        sql = """
            SELECT m.id, m.type, mt.typeDisplayName, m.providerNo, m.dataField,
                   m.measuringInstruction, LEFT(m.comments, 240) AS comments,
                   m.dateObserved, m.dateEntered, m.appointmentNo
            FROM measurements m
            LEFT JOIN measurementType mt ON mt.type = m.type
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY m.dateObserved DESC, m.id DESC
        """
        return self._run(sql, tuple(params), limit=limit)

    def trend_patient_measurement(self, demographic_no: int, measurement_type: str, limit: int = 200) -> dict[str, Any]:
        return self.list_patient_measurements(demographic_no, measurement_type, limit=limit)

    def list_measurement_types(self, search: str | None = None, limit: int = 200) -> dict[str, Any]:
        params: tuple[Any, ...] = ()
        where = ""
        if search:
            where = "WHERE type LIKE %s OR typeDisplayName LIKE %s OR typeDescription LIKE %s"
            params = (_like(search), _like(search), _like(search))
        sql = f"""
            SELECT id, type, typeDisplayName, typeDescription, measuringInstruction, validation, createDate
            FROM measurementType
            {where}
            ORDER BY typeDisplayName, type
        """
        return self._run(sql, params, limit=limit)

    def list_patient_preventions(self, demographic_no: int, include_deleted: bool = False, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT id, demographic_no, creation_date, prevention_date, provider_no,
                   provider_name, prevention_type, deleted, refused, next_date, never,
                   creator, lastUpdateDate, snomedId
            FROM preventions
            WHERE demographic_no = %s AND (%s OR COALESCE(deleted, 0) = 0)
            ORDER BY prevention_date DESC, id DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), bool(include_deleted)), limit=limit)

    def get_prevention_detail(self, prevention_id: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT p.id, p.demographic_no, p.prevention_date, p.provider_no,
                   p.prevention_type, p.deleted, p.refused, p.next_date, p.never,
                   p.snomedId, e.keyval, e.val
            FROM preventions p
            LEFT JOIN preventionsExt e ON e.prevention_id = p.id
            WHERE p.id = %s
            ORDER BY e.keyval
        """
        return self._run(sql, (_int(prevention_id, "prevention_id"),), limit=limit)

    def list_due_preventions(self, demographic_no: int | None = None, provider_no: str | None = None, limit: int = 100) -> dict[str, Any]:
        clauses = ["COALESCE(deleted, 0) = 0", "next_date IS NOT NULL", "next_date <= CURDATE()"]
        params: list[Any] = []
        if demographic_no is not None:
            clauses.append("demographic_no = %s")
            params.append(_int(demographic_no, "demographic_no"))
        if provider_no:
            clauses.append("provider_no = %s")
            params.append(provider_no)
        sql = """
            SELECT id, demographic_no, prevention_type, prevention_date, next_date,
                   provider_no, provider_name, refused, never, lastUpdateDate
            FROM preventions
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY next_date, prevention_type
        """
        return self._run(sql, tuple(params), limit=limit)

    def list_patient_notes(self, demographic_no: int, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT note_id, update_date, observation_date, demographic_no, provider_no,
                   signed, locked, archived, encounter_type, billing_code,
                   LEFT(REPLACE(note, '\n', ' '), 500) AS note_snippet
            FROM casemgmt_note
            WHERE demographic_no = %s AND (%s OR COALESCE(archived, 0) = 0)
            ORDER BY observation_date DESC, note_id DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), bool(include_archived)), limit=limit)

    def get_note_detail(self, note_id: int) -> dict[str, Any]:
        sql = """
            SELECT note_id, update_date, observation_date, demographic_no, provider_no,
                   signed, locked, archived, encounter_type, billing_code, note
            FROM casemgmt_note
            WHERE note_id = %s
        """
        return self._run(sql, (_int(note_id, "note_id"),), limit=1)

    def search_patient_notes(self, demographic_no: int, term: str, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT note_id, observation_date, update_date, provider_no, signed, locked,
                   archived, LEFT(REPLACE(note, '\n', ' '), 500) AS note_snippet
            FROM casemgmt_note
            WHERE demographic_no = %s AND note LIKE %s
            ORDER BY observation_date DESC, note_id DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), _like(term)), limit=limit)

    def list_patient_issues(self, demographic_no: int, active_only: bool = True, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT ci.id, ci.demographic_no, ci.issue_id, i.code, i.description,
                   ci.acute, ci.certain, ci.major, ci.resolved, ci.type, ci.update_date
            FROM casemgmt_issue ci
            LEFT JOIN issue i ON i.issue_id = ci.issue_id
            WHERE ci.demographic_no = %s AND (%s = FALSE OR COALESCE(ci.resolved, 0) = 0)
            ORDER BY ci.update_date DESC, ci.id DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), bool(active_only)), limit=limit)

    def list_patient_ticklers(self, demographic_no: int, open_only: bool = True, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT tickler_no, demographic_no, message, status, update_date, service_date,
                   creator, priority, task_assigned_to, category_id
            FROM tickler
            WHERE demographic_no = %s AND (%s = FALSE OR LOWER(status) NOT IN ('c', 'complete', 'completed', 'd', 'deleted'))
            ORDER BY service_date DESC, tickler_no DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"), bool(open_only)), limit=limit)

    def list_provider_ticklers(self, provider_no: str, status: str | None = None, limit: int = 100) -> dict[str, Any]:
        clauses = ["task_assigned_to = %s"]
        params: list[Any] = [provider_no]
        if status:
            clauses.append("status = %s")
            params.append(status)
        sql = """
            SELECT tickler_no, demographic_no, message, status, update_date, service_date,
                   creator, priority, task_assigned_to, category_id
            FROM tickler
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY service_date DESC, tickler_no DESC
        """
        return self._run(sql, tuple(params), limit=limit)

    def get_tickler_detail(self, tickler_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT t.tickler_no, t.demographic_no, t.message, t.status, t.update_date,
                   t.service_date, t.creator, t.priority, t.task_assigned_to,
                   c.id AS comment_id, c.provider_no AS comment_provider_no,
                   c.update_date AS comment_update_date, c.message AS comment
            FROM tickler t
            LEFT JOIN tickler_comments c ON c.tickler_no = t.tickler_no
            WHERE t.tickler_no = %s
            ORDER BY c.update_date
        """
        return self._run(sql, (_int(tickler_no, "tickler_no"),), limit=limit)

    def list_patient_messages(self, demographic_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT m.messageid, m.thedate, m.theime, m.thesubject, m.sentby,
                   m.sentto, m.actionstatus, m.type, ml.provider_no, ml.status, ml.folderid
            FROM msgDemoMap map
            JOIN messagetbl m ON m.messageid = map.messageID
            LEFT JOIN messagelisttbl ml ON ml.message = m.messageid
            WHERE map.demographic_no = %s
            ORDER BY m.thedate DESC, m.theime DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_message_metadata(self, message_id: int, limit: int = 50) -> dict[str, Any]:
        sql = """
            SELECT m.messageid, m.thedate, m.theime, m.thesubject, m.sentby,
                   m.sentto, m.sentbyNo, m.sentByLocation, m.actionstatus, m.type,
                   m.type_link, ml.provider_no, ml.status, ml.folderid
            FROM messagetbl m
            LEFT JOIN messagelisttbl ml ON ml.message = m.messageid
            WHERE m.messageid = %s
        """
        return self._run(sql, (_int(message_id, "message_id"),), limit=limit)

    def list_patient_documents(self, demographic_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT d.document_no, d.doctype, d.docClass, d.docSubClass, d.docdesc,
                   d.docfilename, d.doccreator, d.responsible, d.status, d.contenttype,
                   d.contentdatetime, d.observationdate, d.reviewer, d.reviewdatetime,
                   d.number_of_pages, d.receivedDate, d.abnormal, dm.reviewed_flag
            FROM doc_manager dm
            JOIN ctl_document cd ON cd.module = 'demographic' AND cd.module_id = dm.demographic_no
            JOIN document d ON d.document_no = cd.document_no
            WHERE dm.demographic_no = %s
            ORDER BY COALESCE(d.observationdate, d.contentdatetime, d.updatedatetime) DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_document_metadata(self, document_no: int) -> dict[str, Any]:
        sql = """
            SELECT document_no, doctype, docClass, docSubClass, docdesc, docfilename,
                   doccreator, responsible, source, sourceFacility, program_id,
                   updatedatetime, status, contenttype, contentdatetime, public1,
                   observationdate, reviewer, reviewdatetime, number_of_pages,
                   appointment_no, restrictToProgram, receivedDate, abnormal
            FROM document
            WHERE document_no = %s
        """
        return self._run(sql, (_int(document_no, "document_no"),), limit=1)

    def list_unreviewed_documents(self, provider_no: str | None = None, limit: int = 100) -> dict[str, Any]:
        clauses = ["(reviewer IS NULL OR reviewer = '' OR reviewdatetime IS NULL)"]
        params: list[Any] = []
        if provider_no:
            clauses.append("(responsible = %s OR reviewer = %s)")
            params.extend([provider_no, provider_no])
        sql = """
            SELECT document_no, doctype, docdesc, docfilename, responsible, reviewer,
                   status, contentdatetime, receivedDate, abnormal
            FROM document
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY COALESCE(receivedDate, contentdatetime, updatedatetime) DESC
        """
        return self._run(sql, tuple(params), limit=limit)

    def list_patient_eforms(self, demographic_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT fdid, fid, form_name, subject, demographic_no, status, form_date,
                   form_time, form_provider, showLatestFormOnly, patient_independent
            FROM eform_data
            WHERE demographic_no = %s
            ORDER BY form_date DESC, form_time DESC, fdid DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_eform_values(self, fdid: int, limit: int = 200) -> dict[str, Any]:
        sql = """
            SELECT id, fdid, fid, demographic_no, var_name, LEFT(var_value, 1000) AS var_value
            FROM eform_values
            WHERE fdid = %s
            ORDER BY var_name, id
        """
        return self._run(sql, (_int(fdid, "fdid"),), limit=limit)

    def list_patient_labs(self, demographic_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT r.id, r.demographic_no, r.lab_no, r.lab_type, r.created, r.dateModified,
                   p.id AS lab_patient_physician_info_id,
                   i.result_status, i.final_result_count, i.obr_date, i.priority,
                   i.requesting_client, i.discipline, i.report_status, i.accessionNum,
                   i.sending_facility, i.label
            FROM patientLabRouting r
            LEFT JOIN hl7TextInfo i ON i.lab_no = r.lab_no
            LEFT JOIN labPatientPhysicianInfo p ON p.accession_num = i.accessionNum
            WHERE r.demographic_no = %s
            ORDER BY COALESCE(i.obr_date, r.created) DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_lab_results(self, lab_patient_physician_info_id: int, limit: int = 200) -> dict[str, Any]:
        sql = """
            SELECT id, labPatientPhysicianInfo_id, line_type, title, test_name,
                   abn, minimum, maximum, units, result, description, location_id
            FROM labTestResults
            WHERE labPatientPhysicianInfo_id = %s
            ORDER BY id
        """
        return self._run(sql, (_int(lab_patient_physician_info_id, "lab_patient_physician_info_id"),), limit=limit)

    def list_abnormal_labs(self, start_date: str | None = None, end_date: str | None = None, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT r.id, r.labPatientPhysicianInfo_id, p.service_date, p.collection_date,
                   r.title, r.test_name, r.abn, r.result, r.units, r.minimum,
                   r.maximum, r.description
            FROM labTestResults r
            LEFT JOIN labPatientPhysicianInfo p ON p.id = r.labPatientPhysicianInfo_id
            WHERE COALESCE(r.abn, '') <> ''
              AND DATE(COALESCE(p.service_date, p.collection_date, p.lastUpdateDate)) BETWEEN %s AND %s
            ORDER BY r.id DESC
        """
        return self._run(sql, (start_date or _default_start(30), end_date or date.today().isoformat()), limit=limit)

    def list_patient_consults(self, demographic_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT requestId, referalDate, serviceId, specId, appointmentDate,
                   appointmentTime, LEFT(reason, 240) AS reason, providerNo,
                   demographicNo, status, statusText, urgency, followUpDate,
                   site_name, lastUpdateDate
            FROM consultationRequests
            WHERE demographicNo = %s
            ORDER BY COALESCE(lastUpdateDate, referalDate) DESC, requestId DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_consult_detail(self, request_id: int) -> dict[str, Any]:
        sql = """
            SELECT requestId, referalDate, serviceId, specId, appointmentDate,
                   appointmentTime, reason, clinicalInfo, currentMeds, allergies,
                   providerNo, demographicNo, status, statusText, sendTo,
                   concurrentProblems, urgency, appointmentInstructions,
                   patientWillBook, followUpDate, site_name, lastUpdateDate
            FROM consultationRequests
            WHERE requestId = %s
        """
        return self._run(sql, (_int(request_id, "request_id"),), limit=1)

    def list_consults_by_status(self, status: str, provider_no: str | None = None, limit: int = 100) -> dict[str, Any]:
        clauses = ["status = %s"]
        params: list[Any] = [status]
        if provider_no:
            clauses.append("providerNo = %s")
            params.append(provider_no)
        sql = """
            SELECT requestId, referalDate, appointmentDate, providerNo, demographicNo,
                   status, statusText, urgency, followUpDate, lastUpdateDate
            FROM consultationRequests
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY COALESCE(lastUpdateDate, referalDate) DESC
        """
        return self._run(sql, tuple(params), limit=limit)

    def list_patient_billing_summary(self, demographic_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT b.billing_no, b.provider_no, b.appointment_no, b.billing_date,
                   b.billing_time, b.total, b.status, b.billingtype,
                   bm.billingmaster_no, bm.billingstatus, bm.billing_code,
                   bm.bill_amount, bm.service_date, bm.dx_code1, bm.dx_code2, bm.dx_code3
            FROM billing b
            LEFT JOIN billingmaster bm ON bm.billing_no = b.billing_no
            WHERE b.demographic_no = %s
            ORDER BY b.billing_date DESC, b.billing_no DESC
        """
        return self._run(sql, (_int(demographic_no, "demographic_no"),), limit=limit)

    def get_billing_claim_detail(self, billing_no: int, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT b.billing_no, b.demographic_no, b.provider_no, b.billing_date,
                   b.total, b.status, b.billingtype, bm.billingmaster_no,
                   bm.billingstatus, bm.billing_code, bm.bill_amount, bm.service_date,
                   bd.billing_dt_no, bd.service_code, bd.service_desc,
                   bd.billing_amount, bd.diagnostic_code, bd.billingunit
            FROM billing b
            LEFT JOIN billingmaster bm ON bm.billing_no = b.billing_no
            LEFT JOIN billingdetail bd ON bd.billing_no = b.billing_no
            WHERE b.billing_no = %s
            ORDER BY bm.billingmaster_no, bd.billing_dt_no
        """
        return self._run(sql, (_int(billing_no, "billing_no"),), limit=limit)

    def search_billing_codes(self, search: str, limit: int = 100) -> dict[str, Any]:
        term = _like(search)
        sql = """
            SELECT 'service' AS code_type, service_code AS code, description, value, region, specialty, NULL AS status
            FROM billingservice
            WHERE service_code LIKE %s OR description LIKE %s
            UNION ALL
            SELECT 'diagnostic', diagnostic_code, description, NULL, region, NULL, status
            FROM diagnosticcode
            WHERE diagnostic_code LIKE %s OR description LIKE %s
            ORDER BY code_type, code
        """
        return self._run(sql, (term, term, term, term), limit=limit)

    def list_provider_directory(self, status: str | None = None, limit: int = 200) -> dict[str, Any]:
        where = ""
        params: tuple[Any, ...] = ()
        if status:
            where = "WHERE status = %s"
            params = (status,)
        sql = f"""
            SELECT provider_no, last_name, first_name, provider_type, specialty,
                   team, phone, work_phone, email, status, job_title, title,
                   practitionerNoType
            FROM provider
            {where}
            ORDER BY last_name, first_name
        """
        return self._run(sql, params, limit=limit)

    def get_provider_summary(self, provider_no: str) -> dict[str, Any]:
        sql = """
            SELECT provider_no, last_name, first_name, provider_type, specialty,
                   team, sex, dob, address, phone, work_phone, ohip_no, rma_no,
                   billing_no, hso_no, status, practitionerNo, init, job_title,
                   email, title, supervisor, practitionerNoType
            FROM provider
            WHERE provider_no = %s
        """
        return self._run(sql, (provider_no,), limit=1)

    def search_specialists(self, search: str, limit: int = 100) -> dict[str, Any]:
        term = _like(search)
        sql = """
            SELECT specId, fName, lName, proLetters, address, phone, fax, email,
                   specType, referralNo, institutionId, departmentId, salutation,
                   hideFromView
            FROM professionalSpecialists
            WHERE fName LIKE %s OR lName LIKE %s OR specType LIKE %s OR referralNo LIKE %s
            ORDER BY lName, fName
        """
        return self._run(sql, (term, term, term, term), limit=limit)

    def get_access_roles_for_provider(self, provider_no: str, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT s.security_no, s.user_name, s.provider_no, s.b_ExpireSet,
                   s.date_ExpireDate, s.b_LocalLockSet, s.b_RemoteLockSet,
                   sur.role_name
            FROM security s
            LEFT JOIN secUserRole sur ON sur.provider_no = s.provider_no
            WHERE s.provider_no = %s
            ORDER BY sur.role_name
        """
        return self._run(sql, (provider_no,), limit=limit)

    def audit_patient_access_log(
        self,
        demographic_no: int,
        start_date: str | None = None,
        end_date: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        clauses = ["demographic_no = %s", "DATE(dateTime) BETWEEN %s AND %s"]
        params: list[Any] = [_int(demographic_no, "demographic_no"), start_date or _default_start(90), end_date or date.today().isoformat()]
        if action:
            clauses.append("action = %s")
            params.append(action)
        sql = """
            SELECT id, dateTime, provider_no, action, content, contentId, ip,
                   demographic_no, securityId
            FROM log
            WHERE """ + " AND ".join(clauses) + """
            ORDER BY dateTime DESC, id DESC
        """
        return self._run(sql, tuple(params), limit=limit)
