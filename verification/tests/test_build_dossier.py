"""Regression tests for generated sector-dossier negative routing."""

import importlib.util
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "verification" / "scripts" / "build_dossier.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("sector_dossier_builder", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_modern_negative_tag_uses_only_primary_family_and_explicit_claims():
    module = load_builder()

    claims, refs = module.negative_references(
        "NG-2026-07-31-A13-ELLIPTIC-GAUSSIAN-D4-FLOOR-UNIFORMITY",
        "pointwise D2, D3, and D4 quotient jets",
        ["The D4 witness and R132 computation remain inside A13."],
    )
    assert claims == []
    assert refs == {"A13"}

    claims, refs = module.negative_references(
        "NG-2026-07-31-A13-R132-D2-SCOPE",
        "audit a D2 mathematical token",
        ["No explicit cross-sector claim is cited."],
    )
    assert claims == []
    assert refs == {"A13"}

    claims, refs = module.negative_references(
        "NG-2026-07-31-A13-EXPLICIT-CROSS-SECTOR",
        "compare with D4-QUANTUM-CONSISTENCY",
        ["The full claim ID is an intentional cross-sector reference."],
    )
    assert claims == ["D4-QUANTUM-CONSISTENCY"]
    assert refs == {"A13", "D4"}


def test_legacy_negative_without_primary_namespace_keeps_short_refs():
    module = load_builder()
    claims, refs = module.negative_references(
        "NG-LEGACY-ROUTE",
        "B5 / B1 comparison",
        ["Legacy prose used short family references."],
    )
    assert claims == []
    assert refs == {"B1", "B5"}
