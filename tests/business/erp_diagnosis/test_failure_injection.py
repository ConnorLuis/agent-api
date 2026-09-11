import pytest

from src.app.business.erp_diagnosis.failure_injection import (
    ERPInjectedDependencyError,
    FaultInjectingERPReadService,
)
from src.app.business.erp_diagnosis.models import ERPOperation
from src.app.business.erp_diagnosis.service import SyntheticERPReadService


def test_fault_injecting_service_delegates_non_fault_reads():
    service = FaultInjectingERPReadService(
        fault_point="approval_context",
        base=SyntheticERPReadService(),
    )

    profile = service.get_user_access_profile("SYN-U001")
    assert profile is not None
    assert profile.user_id == "SYN-U001"


def test_fault_injecting_service_raises_only_at_selected_boundary():
    service = FaultInjectingERPReadService(
        fault_point="permission_check",
        base=SyntheticERPReadService(),
    )

    context = service.get_document_context(
        document_id="SYN-PO-001",
        operation=ERPOperation.SUBMIT,
    )
    assert context is not None

    with pytest.raises(ERPInjectedDependencyError):
        service.check_operation_permission(
            user_id="SYN-U001",
            document_id="SYN-PO-001",
            operation=ERPOperation.SUBMIT,
        )
