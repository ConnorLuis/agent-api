from src.app.business.erp_diagnosis.models import ERPOperation
from src.app.business.erp_diagnosis.repository import SyntheticERPRepository
from src.app.business.erp_diagnosis.root_causes import RootCauseCode


def test_synthetic_dataset_contains_dozen_scale_records_only():
    repository = SyntheticERPRepository()
    dataset = repository.dataset

    total_records = (
        len(dataset.users)
        + len(dataset.documents)
        + len(dataset.operation_policies)
        + len(dataset.approval_flows)
        + len(dataset.transfer_rules)
    )

    assert total_records >= 50
    assert "fictional" in dataset.disclaimer.lower()


def test_permission_check_allows_valid_purchase_order_submit():
    repository = SyntheticERPRepository()

    result = repository.check_operation_permission(
        user_id="SYN-U001",
        document_id="SYN-PO-001",
        operation=ERPOperation.SUBMIT,
    )

    assert result is not None
    assert result.allowed is True
    assert result.reasons == []


def test_permission_check_detects_missing_role():
    repository = SyntheticERPRepository()

    result = repository.check_operation_permission(
        user_id="SYN-U002",
        document_id="SYN-PO-001",
        operation=ERPOperation.SUBMIT,
    )

    assert result is not None
    assert RootCauseCode.ROLE_MISSING in result.reasons


def test_permission_check_detects_org_scope_denied():
    repository = SyntheticERPRepository()

    result = repository.check_operation_permission(
        user_id="SYN-U001",
        document_id="SYN-PO-002",
        operation=ERPOperation.SUBMIT,
    )

    assert result is not None
    assert result.role_granted is True
    assert result.data_permission_granted is True
    assert RootCauseCode.ORG_SCOPE_DENIED in result.reasons


def test_permission_check_detects_data_permission_denied():
    repository = SyntheticERPRepository()

    result = repository.check_operation_permission(
        user_id="SYN-U013",
        document_id="SYN-PO-001",
        operation=ERPOperation.SUBMIT,
    )

    assert result is not None
    assert result.role_granted is True
    assert result.org_scope_granted is True
    assert RootCauseCode.DATA_PERMISSION_DENIED in result.reasons


def test_permission_check_detects_invalid_document_state():
    repository = SyntheticERPRepository()

    result = repository.check_operation_permission(
        user_id="SYN-U001",
        document_id="SYN-PO-003",
        operation=ERPOperation.SUBMIT,
    )

    assert result is not None
    assert RootCauseCode.INVALID_DOCUMENT_STATE in result.reasons


def test_approval_context_distinguishes_unbound_and_unresolved():
    repository = SyntheticERPRepository()

    unbound = repository.resolve_approval_context("SYN-EX-002")
    unresolved = repository.resolve_approval_context("SYN-PO-004")

    assert unbound is not None
    assert unbound.bound is False

    assert unresolved is not None
    assert unresolved.bound is True
    assert unresolved.approver_resolved is False


def test_transfer_context_detects_missing_rule():
    repository = SyntheticERPRepository()

    result = repository.resolve_transfer_context(
        document_id="SYN-PR-002",
        target_document_type="PurchaseOrder",
    )

    assert result is not None
    assert result.rule_found is False
