from __future__ import annotations

from typing import Any

from .base import default_end, default_start, like_search, require_int


class ClinicalCareToolsMixin:
    def list_patient_measurements(
        self,
        demographic_no: int,
        measurement_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        clauses = ["m.demographicNo = %s", "m.dateObserved BETWEEN %s AND %s"]
        params: list[Any] = [require_int(demographic_no, "demographic_no"), start_date or default_start(), end_date or default_end(0)]
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
            params = (like_search(search), like_search(search), like_search(search))
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"), bool(include_deleted)), limit=limit)
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
        return self._run(sql, (require_int(prevention_id, "prevention_id"),), limit=limit)
    def list_due_preventions(self, demographic_no: int | None = None, provider_no: str | None = None, limit: int = 100) -> dict[str, Any]:
        clauses = ["COALESCE(deleted, 0) = 0", "next_date IS NOT NULL", "next_date <= CURDATE()"]
        params: list[Any] = []
        if demographic_no is not None:
            clauses.append("demographic_no = %s")
            params.append(require_int(demographic_no, "demographic_no"))
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
