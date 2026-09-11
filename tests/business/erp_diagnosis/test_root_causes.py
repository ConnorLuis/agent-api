from src.app.business.erp_diagnosis.root_causes import (
    ROOT_CAUSE_DEFINITIONS,
    RootCauseCode,
    get_root_cause_definition,
)


def test_root_cause_taxonomy_is_complete_and_unique():
    assert set(ROOT_CAUSE_DEFINITIONS) == set(RootCauseCode)
    assert len({item.value for item in RootCauseCode}) == len(RootCauseCode)


def test_dependency_unavailable_requires_human_review():
    definition = get_root_cause_definition(RootCauseCode.DEPENDENCY_UNAVAILABLE)

    assert definition.requires_human is True
    assert "实时业务事实" in definition.description
