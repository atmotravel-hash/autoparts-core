from autoparts_core.core.enums import AssemblyCompleteness, Condition
from autoparts_core.identity.condition import normalize_completeness, normalize_condition


def test_condition_maps():
    assert normalize_condition("Brand New")[0] == Condition.NEW
    assert normalize_condition("Gebraucht")[0] == Condition.USED
    assert normalize_condition("Damaged — cracked")[0] == Condition.DAMAGED


def test_completeness():
    assert normalize_completeness("housing only")[0] == AssemblyCompleteness.HOUSING_ONLY
    assert normalize_completeness("complete assembly")[0] == AssemblyCompleteness.COMPLETE_ASSEMBLY
