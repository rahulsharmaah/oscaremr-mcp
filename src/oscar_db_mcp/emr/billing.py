from __future__ import annotations

from datetime import date
from typing import Any

from .base import default_start, like_search, require_int


class BillingAdminToolsMixin:
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
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
        return self._run(sql, (require_int(billing_no, "billing_no"),), limit=limit)
    def search_billing_codes(self, search: str, limit: int = 100) -> dict[str, Any]:
        term = like_search(search)
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
        term = like_search(search)
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
        params: list[Any] = [require_int(demographic_no, "demographic_no"), start_date or default_start(90), end_date or date.today().isoformat()]
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
