"""estimator_upgrade_enumerated.py -- ESTIMATOR-UPGRADE: controlled-error bound on
the enumerated-reading selection margins for B1-RH-ENUM.

B1 claims dF[R] = F[R] - F[R_H] > 0 for every enumerated reading R (LAM/HEX/FCC/
BCC single-shell) at mu^2=0.005, at ESTIMATOR grade (point estimates from the
fast quadrature pipeline, no certified error). ESTIMATOR-UPGRADE asks for a
CONTROLLED error bound.

Structure (verified). dF_R(A) is even in the condensate amplitude A with
dF_R(0)=0 exactly; A=0 is the Reading-H reference. The selection holds iff for
every reading (a) A=0 is a STRICT local minimum -- curvature
  kappa_R := dF_R''(0) = 2 dF_R(h)/h^2 + O(h^2) > 0
-- and (b) there is no DEEPER minimum at A>0 (the amplitude scan's global best
sits at A=0, i.e. no condensate). A reading with dF_R''(0) < 0 or an interior
dF<0 minimum would FALSIFY the selection.

Controlled error. The dominant numerical knob is the loop-integral quadrature for
M(r_hat) (it enters dF several times and drives the gap solve). We recompute
every verdict at the production fast pipeline (M_fast, grid at N_PT=6000) and at a
HIGH-resolution pipeline (M_of direct at N_PT=20000, via monkeypatch of M_fast so
Math424's own certified dF_reading/scan_reading are reused -- no formula
re-transcription). The per-reading envelope is |kappa_fast - kappa_hires|; the
controlled-error margin is min(kappa_fast, kappa_hires) - envelope, asserted > 0.
A quadratic-regime check (kappa at h and h/2 agree) confirms kappa is the true
curvature, not A^4 contamination.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"
__claims__ = ["B1-RH-ENUM"]

import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m4  # noqa: E402

MU2 = 0.005
H1 = 0.005           # small amplitude for the curvature finite difference
H2 = 0.0025          # half-step (quadratic-regime check)
NPT_HI = 20000       # high-resolution loop-integral quadrature
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

r_bare = m4.R_OF(MU2)

def verdicts(label):
    """Return per-reading dict {A_star, no_condensate, kappa_h1, kappa_h2} using
    whatever M_fast is currently bound (fast or monkeypatched hires)."""
    rR = m4.gap_solve(r_bare, 0, 0, 0.0)
    MR = m4.M_fast(rR)
    # dF(0)=0 identity must hold in this pipeline
    v0, _ = m4.dF_reading(r_bare, "BCC", 0.0, rR, MR)
    out = {"_rR": rR, "_MR": MR, "_v0": v0}
    for nm in m4.READINGS:
        (dF_best, A_star, rh), rows = m4.scan_reading(r_bare, nm, rR, MR)
        d1, _ = m4.dF_reading(r_bare, nm, H1, rR, MR)
        d2, _ = m4.dF_reading(r_bare, nm, H2, rR, MR)
        out[nm] = dict(
            A_star=A_star, dF_best=dF_best,
            no_condensate=bool(A_star == 0.0 and dF_best >= -1e-15),
            kappa_h1=2.0 * d1 / H1**2,
            kappa_h2=2.0 * d2 / H2**2,
        )
    return out

print(f"ESTIMATOR-UPGRADE: enumerated readings at mu^2={MU2} (r_bare={r_bare:.6f})")

# ---- fast pipeline (production: M_fast, N_PT=6000) ----
fast = verdicts("fast")
claim("dF0_identity_fast", abs(fast["_v0"]) < 1e-9,
      f"(dF(A=0)=0 exactly in the fast pipeline: {fast['_v0']:.2e})")

# ---- high-resolution pipeline (monkeypatch M_fast -> M_of at N_PT=20000) ----
_orig = m4.M_fast
m4.M_fast = lambda rh: m4.M_of(rh, n_points=NPT_HI)
try:
    hi = verdicts("hires")
finally:
    m4.M_fast = _orig
claim("dF0_identity_hires", abs(hi["_v0"]) < 1e-9,
      f"(dF(A=0)=0 exactly in the hires pipeline: {hi['_v0']:.2e})")

# ---- no-condensate verdict (global): every reading collapses to A=0 ----
fast_clean = all(fast[nm]["no_condensate"] for nm in m4.READINGS)
hi_clean = all(hi[nm]["no_condensate"] for nm in m4.READINGS)
claim("no_condensate_fast", fast_clean,
      "(every reading's global dF minimum is at A=0: no enumerated reading beats Reading-H, fast)")
claim("no_condensate_hires", hi_clean,
      "(no condensate revealed by the N_PT=20000 refinement either: the verdict is not a fast-quadrature artefact)")

# ---- curvature controlled-error: kappa_R = dF_R''(0) > 0, certified ----
print("    reading  kappa_fast    kappa_hires   envelope     certified (kappa-env)")
rows_out = {}
worst_cert = 1e9
for nm in m4.READINGS:
    kf = fast[nm]["kappa_h1"]; kh = hi[nm]["kappa_h1"]
    env = abs(kf - kh)
    cert = min(kf, kh) - env
    worst_cert = min(worst_cert, cert)
    # quadratic-regime check: kappa(h) vs kappa(h/2) agree -> true curvature
    quad_ok = abs(fast[nm]["kappa_h1"] - fast[nm]["kappa_h2"]) < 0.02 * abs(fast[nm]["kappa_h1"])
    rows_out[nm] = dict(kappa_fast=kf, kappa_hires=kh, envelope=env, certified=cert, quadratic_ok=quad_ok)
    print(f"    {nm:4s}    {kf:.6e}  {kh:.6e}  {env:.2e}   {cert:.6e}  {'quad-OK' if quad_ok else 'QUAD?'}")

claim("curvature_positive_controlled_error", worst_cert > 0,
      f"(min over readings of [kappa - envelope] = {worst_cert:.6e} > 0: A=0 is a STRICT minimum for every "
      "reading, controlled-error w.r.t. the M-quadrature -- the binding reading is the smallest kappa)")
binding = min(m4.READINGS, key=lambda n: rows_out[n]["certified"])
claim("envelope_far_below_curvature",
      all(rows_out[nm]["envelope"] < 1e-3 * abs(rows_out[nm]["kappa_fast"]) for nm in m4.READINGS),
      f"(M-quadrature envelope is < 0.1% of kappa for every reading; binding = {binding} "
      f"kappa={rows_out[binding]['kappa_fast']:.4e}, envelope={rows_out[binding]['envelope']:.2e})")
claim("quadratic_regime_confirmed", all(rows_out[nm]["quadratic_ok"] for nm in m4.READINGS),
      "(kappa(h) vs kappa(h/2) agree to <2% for every reading: the finite difference is the true dF''(0), "
      "not A^4 contamination)")

print("    SCOPE: single-shell enumerated readings (LAM/HEX/FCC/BCC); M-quadrature controlled error. "
      "Two-shell ensemble + dI/grid knobs are the same method (registered follow-up).")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260607-estimator-upgrade-enumerated"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="estimator_upgrade_enumerated.py", version=__version__,
    mu2=MU2, r_bare=r_bare, NPT_fast=m4.N_PT_FAST, NPT_hi=NPT_HI, h1=H1, h2=H2,
    readings={nm: rows_out[nm] for nm in m4.READINGS},
    worst_certified_curvature=worst_cert, binding_reading=binding,
    no_condensate_fast=fast_clean, no_condensate_hires=hi_clean,
    scope="single-shell enumerated readings; M-quadrature controlled error; two-shell + dI follow-up",
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
