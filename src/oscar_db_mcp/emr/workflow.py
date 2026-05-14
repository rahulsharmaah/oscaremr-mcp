from __future__ import annotations

from typing import Any

from .base import like_search, require_int


class WorkflowToolsMixin:
    def list_patient_notes(self, demographic_no: int, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT note_id, update_date, observation_date, demographic_no, provider_no,
                   signed, locked, archived, encounter_type, billing_code,
                   LEFT(REPLACE(note, '\n', ' '), 500) AS note_snippet
            FROM casemgmt_note
            WHERE demographic_no = %s AND (%s OR COALESCE(archived, 0) = 0)
            ORDER BY observation_date DESC, note_id DESC
        """
        return self._run(sql, (require_int(demographic_no, "demographic_no"), bool(include_archived)), limit=limit)
    def get_note_detail(self, note_id: int) -> dict[str, Any]:
        sql = """
            SELECT note_id, update_date, observation_date, demographic_no, provider_no,
                   signed, locked, archived, encounter_type, billing_code, note
            FROM casemgmt_note
            WHERE note_id = %s
        """
        return self._run(sql, (require_int(note_id, "note_id"),), limit=1)
    def search_patient_notes(self, demographic_no: int, term: str, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT note_id, observation_date, update_date, provider_no, signed, locked,
                   archived, LEFT(REPLACE(note, '\n', ' '), 500) AS note_snippet
            FROM casemgmt_note
            WHERE demographic_no = %s AND note LIKE %s
            ORDER BY observation_date DESC, note_id DESC
        """
        return self._run(sql, (require_int(demographic_no, "demographic_no"), like_search(term)), limit=limit)
    def list_patient_issues(self, demographic_no: int, active_only: bool = True, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT ci.id, ci.demographic_no, ci.issue_id, i.code, i.description,
                   ci.acute, ci.certain, ci.major, ci.resolved, ci.type, ci.update_date
            FROM casemgmt_issue ci
            LEFT JOIN issue i ON i.issue_id = ci.issue_id
            WHERE ci.demographic_no = %s AND (%s = FALSE OR COALESCE(ci.resolved, 0) = 0)
            ORDER BY ci.update_date DESC, ci.id DESC
        """
        return self._run(sql, (require_int(demographic_no, "demographic_no"), bool(active_only)), limit=limit)
    def list_patient_ticklers(self, demographic_no: int, open_only: bool = True, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT tickler_no, demographic_no, message, status, update_date, service_date,
                   creator, priority, task_assigned_to, category_id
            FROM tickler
            WHERE demographic_no = %s AND (%s = FALSE OR LOWER(status) NOT IN ('c', 'complete', 'completed', 'd', 'deleted'))
            ORDER BY service_date DESC, tickler_no DESC
        """
        return self._run(sql, (require_int(demographic_no, "demographic_no"), bool(open_only)), limit=limit)
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
        return self._run(sql, (require_int(tickler_no, "tickler_no"),), limit=limit)
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
    def get_message_metadata(self, message_id: int, limit: int = 50) -> dict[str, Any]:
        sql = """
            SELECT m.messageid, m.thedate, m.theime, m.thesubject, m.sentby,
                   m.sentto, m.sentbyNo, m.sentByLocation, m.actionstatus, m.type,
                   m.type_link, ml.provider_no, ml.status, ml.folderid
            FROM messagetbl m
            LEFT JOIN messagelisttbl ml ON ml.message = m.messageid
            WHERE m.messageid = %s
        """
        return self._run(sql, (require_int(message_id, "message_id"),), limit=limit)
