from __future__ import annotations

from datetime import date
from typing import Any

from .base import default_start, require_int


class RecordsToolsMixin:
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
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
        return self._run(sql, (require_int(document_no, "document_no"),), limit=1)
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
    def get_eform_values(self, fdid: int, limit: int = 200) -> dict[str, Any]:
        sql = """
            SELECT id, fdid, fid, demographic_no, var_name, LEFT(var_value, 1000) AS var_value
            FROM eform_values
            WHERE fdid = %s
            ORDER BY var_name, id
        """
        return self._run(sql, (require_int(fdid, "fdid"),), limit=limit)
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
    def get_lab_results(self, lab_patient_physician_info_id: int, limit: int = 200) -> dict[str, Any]:
        sql = """
            SELECT id, labPatientPhysicianInfo_id, line_type, title, test_name,
                   abn, minimum, maximum, units, result, description, location_id
            FROM labTestResults
            WHERE labPatientPhysicianInfo_id = %s
            ORDER BY id
        """
        return self._run(sql, (require_int(lab_patient_physician_info_id, "lab_patient_physician_info_id"),), limit=limit)
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
        return self._run(sql, (start_date or default_start(30), end_date or date.today().isoformat()), limit=limit)
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
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
        return self._run(sql, (require_int(request_id, "request_id"),), limit=1)
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
