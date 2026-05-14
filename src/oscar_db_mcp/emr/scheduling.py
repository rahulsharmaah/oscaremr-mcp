from __future__ import annotations

from datetime import date
from typing import Any

from .base import default_end, default_start, require_int


class SchedulingToolsMixin:
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"), start_date or default_start(365), end_date or default_end(90)), limit=limit)
    def get_appointment_detail(self, appointment_no: int) -> dict[str, Any]:
        sql = """
            SELECT a.appointment_no, a.demographic_no, a.provider_no, a.appointment_date,
                   a.start_time, a.end_time, a.status, a.type, a.reasonCode, a.reason,
                   a.location, a.resources, a.billing, a.urgency, a.creator,
                   a.createdatetime, a.updatedatetime, a.notes, a.remarks
            FROM appointment a
            WHERE a.appointment_no = %s
        """
        return self._run(sql, (require_int(appointment_no, "appointment_no"),), limit=1)
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
        params: list[Any] = [start_date or default_start(90), end_date or date.today().isoformat()]
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
