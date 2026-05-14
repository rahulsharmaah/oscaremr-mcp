from __future__ import annotations

from typing import Any

from .base import like_search, require_int


class MedicationToolsMixin:
    def list_patient_allergies(self, demographic_no: int, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT allergyid, demographic_no, entry_date, DESCRIPTION, TYPECODE, reaction,
                   archived, start_date, severity_of_reaction, onset_of_reaction,
                   providerNo, nonDrug, lastUpdateDate
            FROM allergies
            WHERE demographic_no = %s AND (%s OR COALESCE(archived, '0') = '0')
            ORDER BY position, entry_date DESC, allergyid DESC
        """
        return self._run(sql, (require_int(demographic_no, "demographic_no"), bool(include_archived)), limit=limit)
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"), bool(active_only)), limit=limit)
    def search_drug_history(self, demographic_no: int, medication: str, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT drugid, rx_date, end_date, BN, GN, customName, dosage, quantity,
                   freqcode, archived, script_no
            FROM drugs
            WHERE demographic_no = %s
              AND (BN LIKE %s OR GN LIKE %s OR customName LIKE %s)
            ORDER BY rx_date DESC, drugid DESC
        """
        term = like_search(medication)
        return self._run(sql, (require_int(demographic_no, "demographic_no"), term, term, term), limit=limit)
    def list_expiring_or_recently_ended_meds(self, days: int = 30, limit: int = 100) -> dict[str, Any]:
        sql = """
            SELECT drugid, demographic_no, provider_no, rx_date, end_date, BN, GN,
                   customName, quantity, freqcode, archived, script_no
            FROM drugs
            WHERE end_date BETWEEN DATE_SUB(CURDATE(), INTERVAL %s DAY)
                              AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY end_date DESC
        """
        safe_days = max(1, min(require_int(days, "days"), 365))
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
        return self._run(sql, (require_int(demographic_no, "demographic_no"),), limit=limit)
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
        return self._run(sql, (require_int(script_no, "script_no"),), limit=100)
