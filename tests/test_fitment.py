from autoparts_core.core.enums import EvidenceKind, FitmentStatus
from autoparts_core.core.models import VehicleQuery
from autoparts_core.fitment.engine import evaluate_fitment


def test_verified_exact_requires_catalogue():
    v = VehicleQuery(make="Volkswagen", model="Passat", generation="B8", year=2017, part_name="headlight")
    r = evaluate_fitment(vehicle=v, oem_as_stated="3G1941007A", title="Headlight left VW Passat B8")
    assert r.status == FitmentStatus.VERIFIED_EXACT
    assert r.evidence_kind == EvidenceKind.OEM_CATALOG


def test_title_only_never_exact():
    v = VehicleQuery(make="Volkswagen", model="Passat", generation="B8", year=2017)
    r = evaluate_fitment(vehicle=v, oem_as_stated=None, title="Headlight left VW Passat B8 2017")
    assert r.status == FitmentStatus.UNCONFIRMED
    assert r.evidence_kind == EvidenceKind.TITLE_ONLY


def test_generation_mismatch_incompatible():
    v = VehicleQuery(make="Volkswagen", model="Passat", generation="B7", year=2012, part_name="headlight")
    r = evaluate_fitment(vehicle=v, oem_as_stated="3G1941007A", title="Passat headlight")
    assert r.status == FitmentStatus.INCOMPATIBLE
