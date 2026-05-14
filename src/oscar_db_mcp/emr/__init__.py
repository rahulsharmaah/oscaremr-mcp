from __future__ import annotations

from .base import BaseReadTools
from .billing import BillingAdminToolsMixin
from .clinical import ClinicalCareToolsMixin
from .medications import MedicationToolsMixin
from .patients import PatientToolsMixin
from .records import RecordsToolsMixin
from .scheduling import SchedulingToolsMixin
from .workflow import WorkflowToolsMixin


class OscarEmrReadTools(
    PatientToolsMixin,
    SchedulingToolsMixin,
    MedicationToolsMixin,
    ClinicalCareToolsMixin,
    WorkflowToolsMixin,
    RecordsToolsMixin,
    BillingAdminToolsMixin,
    BaseReadTools,
):
    """Read-only OSCAR EMR toolset grouped by clinical domain."""


__all__ = ["OscarEmrReadTools"]
