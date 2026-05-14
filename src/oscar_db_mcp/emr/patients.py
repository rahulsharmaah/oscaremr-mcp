from __future__ import annotations

from typing import Any

from .base import default_end, default_start, like_search, require_int


class PatientToolsMixin:
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
            params.append(like_search(last_name))
        if first_name:
            clauses.append("d.first_name LIKE %s")
            params.append(like_search(first_name))
        if search:
            clauses.append("(d.last_name LIKE %s OR d.first_name LIKE %s OR d.chart_no LIKE %s OR d.hin LIKE %s)")
            params.extend([like_search(search), like_search(search), like_search(search), like_search(search)])
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=1)
    def get_patient_contacts(self, demographic_no: int) -> dict[str, Any]:
        sql = """
            SELECT demographic_no, address, city, province, postal, phone, phone2,
                   email, consentToUseEmailForCare, family_doctor, family_physician,
                   residentialAddress, residentialCity, residentialProvince, residentialPostal
            FROM demographic
            WHERE demographic_no = %s
        """
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=1)
    def get_patient_pharmacies(self, demographic_no: int, limit: int = 20) -> dict[str, Any]:
        sql = """
            SELECT dp.id, dp.pharmacyID, dp.demographic_no, dp.status, dp.addDate, dp.preferredOrder
            FROM demographicPharmacy dp
            WHERE dp.demographic_no = %s
            ORDER BY dp.preferredOrder, dp.addDate DESC
        """
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
    def get_patient_chart_index(self, demographic_no: int) -> dict[str, Any]:
        demo = require_int(demographic_no, "demographic_no")
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
        demo = require_int(demographic_no, "demographic_no")
        start = start_date or default_start()
        end = end_date or default_end(30)
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
