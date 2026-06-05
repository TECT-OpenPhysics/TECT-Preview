#!/usr/bin/env python3
"""Math426_g4_kernel_reconciliation.py -- G4 gate execution (CLAUDE.md 6.3.8).

QUESTION (G4, opened in Math425): is the Math400-AddF N=64 BCC "true local
min" a stationary point of the same continuum MF functional to which the
Math425 CS no-condensation theorem was applied at canonical?

METHOD: code-anchored kernel forensics. The production functional
(Codes/pde/real_backend_pt_bcc_mixed_v3.py::shell_free_energy, faithfully
mirrored by Codes/supplementary/Math374_canonical_BCC_hessian.py) uses
    K(q) = r_eff + Z q^2 + Y q^4,  r_eff = mu2 + Y q0^4,  Z = -2 Y q0^2,
which is IDENTICALLY  K(q) = mu2 + Y (q^2 - q0^2)^2.  Therefore the
Brazovskii shell mass (kernel minimum) is
    r_braz = K(q0) = mu2 = +0.005   (canonical),
NOT the Math400-AddE-mapped r = mu2 + Y q0^4 = +0.219 (that value is K(0)).

VERDICT ENCODED IN ASSERTS BELOW:
 (1) K(q0) measured from the actual code on a plane wave = mu2 (1e-10).
 (2) Under the corrected r_braz = mu2: 4 r v / u^2 = 0.0876 < J_BCC = 0.575
     -> MF condensation EXISTS at canonical -> Math400-AddF N=64 BCC local
     min is CONSISTENT (G4 contradiction RESOLVED: the Math425 theorem was
     applied with the AddE-mapped r, i.e. to a DIFFERENT functional).
 (3) Math425 theorem re-scoped in production convention: no-condensation
     region is mu2 > u^2/(4v) = 0.0571 (canonical mu2=0.005 is OUTSIDE).
 (4) Corrected disordered gap equation r_R = mu2 + 3uM + 15vM^2 still has a
     unique positive root at canonical (Path-alpha survives qualitatively;
     r_R shifts 0.4193 -> value asserted below).
 (5) Corrected-canonical HARTREE comparison (Math424-AddA machinery,
     r_bare = 0.005): single-shell condensate readings vs Reading H --
     records whether fluctuation restoration still selects A* = 0.
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import Math374_canonical_BCC_hessian as m374
import Math424_AddA_reading_uniqueness as m424   # builds M-interp table

U, V, Q0 = -0.86, 3.24, 0.6801747616
MU2 = 0.005
CLAIMS = []

def claim(name, expected, actual, tol):
    ok = abs(actual - expected) <= tol
    CLAIMS.append(dict(name=name, expected=expected, actual=actual,
                       tol=tol, passed=bool(ok)))
    assert ok, f"FAIL {name}: {expected} vs {actual} (tol {tol})"

def claim_true(name, cond, detail=""):
    CLAIMS.append(dict(name=name, expected=True, actual=bool(cond),
                       tol=0, passed=bool(cond), detail=detail))
    assert cond, f"FAIL {name}: {detail}"

# ---- (1) code-anchored kernel measurement ----
N = 32
grid = m374.setup_grid(N)
r_eff = MU2 + 1.0 * Q0 ** 4
Z_eff = -2.0 * 1.0 * Q0 ** 2
params = dict(r=r_eff, Z=Z_eff, Y=1.0, lam=m374.LAM_LOCKED,
              gam=m374.GAM_LOCKED, q0=Q0, mu2=MU2)
Vol = grid["L"] ** 3

def K_measured(k_mult):
    """Extract K(|k|) by evaluating the code's F on eps*cos(k x)."""
    eps = 1e-5
    k = k_mult * (2.0 * np.pi / grid["L"])          # on-grid mode
    psi = eps * np.cos(k * grid["X"])
    F = m374.free_energy_canonical(psi, grid, params)
    # F/V = (1/2) K <psi^2> = (1/4) K eps^2  (quartic/sextic O(eps^4) negligible)
    return 4.0 * F / (Vol * eps * eps), k

K0_meas, k_used = K_measured(2)    # 2 * (2pi/L) = q0 exactly (L = 2 a_BCC)
claim("on_grid_mode_is_q0", Q0, k_used, 1e-12)
claim("K(q0)_measured_equals_mu2", MU2, K0_meas, 1e-8)
K_zero = 4.0 * m374.free_energy_canonical(
    1e-5 * np.ones_like(grid["X"]), grid, params) / (Vol * 1e-10) / 2.0
# constant field: F/V = (1/2) K(0) eps^2 -> K(0) = 2F/(V eps^2)
claim("K(0)_equals_AddE_mapped_r", r_eff, K_zero, 1e-8)
# analytic identity check on a third mode (1.5 q0 = 3 * fundamental)
K15_meas, k15 = K_measured(3)
K15_analytic = MU2 + (k15 ** 2 - Q0 ** 2) ** 2
claim("K(1.5q0)_matches_brazovskii_form", K15_analytic, K15_meas, 1e-8)

# ---- (2) corrected MF condensation criterion at canonical ----
r_braz = MU2
thr = 4.0 * r_braz * V / (U * U)
claim("corrected_threshold_4rv_u2", 0.08759, thr, 1e-4)
J_BCC = 540 ** 2 / (12 * 42240)
claim_true("MF_condensation_EXISTS_corrected",
           J_BCC > thr, f"J_BCC={J_BCC:.4f} > {thr:.4f}")
claim_true("Math425_theorem_does_not_bite_at_canonical_production",
           r_braz < U * U / (4 * V),
           f"r_braz={r_braz} < r*={U*U/(4*V):.6f}")

# ---- (4) corrected disordered gap equation ----
rR_corr = m424.gap_solve(r_braz, 0, 0, 0.0)
claim_true("corrected_gap_unique_positive_root", rR_corr is not None
           and rR_corr > 0, f"r_R={rR_corr}")
M_corr = m424.M_fast(rR_corr)
print(f"[corrected canonical] r_braz={r_braz}  r_R={rR_corr:.6f}  M={M_corr:.6f}")
claim("corrected_r_R_value", 0.32, rR_corr, 0.05)   # pre-registered window

# ---- (5) corrected-canonical Hartree comparison (the decisive physics) ----
hartree = {}
all_restored = True
for name in ["LAM", "HEX", "FCC", "BCC"]:
    (dF, Astar, rh), rows = m424.scan_reading(r_braz, name, rR_corr, M_corr)
    mf = m424.mf_threshold(name, r_braz)
    hartree[name] = dict(dF_min=dF, A_star=Astar, r_hat=rh, mf_discriminant=mf)
    print(f"  {name}: MF disc={mf:+.1f}  A*={Astar:.4f}  dF={dF:+.3e}")
    if Astar > 0 and dF < -1e-9:
        all_restored = False
claim_true("hartree_restoration_at_corrected_canonical", all_restored,
           "Reading H must still be the Hartree-level global minimum")

out = dict(theory_tag="Math426", date="2026-06-04",
           kernel=dict(K_q0_measured=K0_meas, K_zero_measured=K_zero,
                       r_braz_corrected=r_braz,
                       addE_mapped_r=r_eff, Z_eff=Z_eff),
           corrected=dict(threshold=thr, J_BCC=J_BCC, r_R=rR_corr, M=M_corr),
           hartree_corrected_canonical=hartree, claims=CLAIMS)
os.makedirs("Runs/math/Math426", exist_ok=True)
json.dump(out, open("Runs/math/Math426/g4_kernel_reconciliation.json", "w"),
          indent=1)
npass = sum(1 for c in CLAIMS if c["passed"])
print(f"claims: {npass}/{len(CLAIMS)} PASS")
sys.exit(0)
