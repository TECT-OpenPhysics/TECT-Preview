"""consolidation_provenance_audit.py -- independent provenance audit of
estimator-upgrade-closure-consolidation v1.0: every headline number in the
consolidation note is cross-checked against the SOURCE JSON artefact of the note
that produced it. Addresses the operator review point (2026-06-07) that the
consolidation summary, not each original, was reviewed.

self-test asserts (exit 0 iff all pass): each consolidation number matches its
source run_diagnostics JSON within tolerance.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__claims__ = ["B1-RH-ENUM"]

import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R = REPO / "claims" / "B1-RH-ENUM" / "runs"
def load(name): return json.loads((R / name / "result.json").read_text())

CLAIMS = []
def check(name, got, expected, tol):
    ok = abs(got - expected) <= tol
    CLAIMS.append(dict(name=name, got=got, expected=expected, tol=tol, passed=ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {got:.4e} vs {expected:.4e} (tol {tol:.1e})")

e = load("260607-estimator-upgrade-enumerated")
check("enumerated_binding_kappa_LAM", e["readings"]["LAM"]["kappa_fast"], 0.851, 2e-3)
k = load("260607-estimator-upgrade-knobs")
check("knobs_continuum_LB_LAM", k["continuum"]["LAM"]["continuum_lower_bound"], 8.8e-7, 1e-7)
check("knobs_continuum_LB_BCC", k["continuum"]["BCC"]["continuum_lower_bound"], 2.5e-7, 1e-7)
d = load("260607-twoshell-continuum-bound")
check("diagonal_min", d["min_off_origin"], 3.9e-5, 5e-6)
check("diagonal_continuum_LB", d["continuum_lower_bound"], 1.2e-4, 2e-5)
check("diagonal_kappa_110", d["kappa_110"], 5.16, 2e-2)
check("diagonal_kappa_200", d["kappa_200"], 3.86, 2e-2)
b = load("260607-twoshell-anchored-bracket")
check("anchored_bracket_min", b["min_anchored"], 6.7e-4, 5e-5)
ac = load("260607-twoshell-anchored-continuum")
check("anchored_continuum_grid_min", ac["grid_min"], 4.64e-4, 2e-5)
check("anchored_continuum_bulk_LB", ac["continuum_lower_bound"], 1.34e-3, 1e-4)
check("anchored_continuum_kappa_110", ac["anchored_kappa_110"], 5.16, 2e-2)
check("anchored_continuum_kappa_200", ac["anchored_kappa_200"], 3.86, 2e-2)

ok = all(c["passed"] for c in CLAIMS)
out = R / "260607-consolidation-provenance-audit"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="consolidation_provenance_audit.py", version=__version__,
    all_consolidation_numbers_match_sources=ok, claims=CLAIMS), indent=2))
print(f"\nPROVENANCE AUDIT: {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} "
      f"{'ALL MATCH' if ok else 'MISMATCH'}")
sys.exit(0 if ok else 1)
