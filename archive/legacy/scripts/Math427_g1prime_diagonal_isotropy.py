#!/usr/bin/env python3
"""Math427_g1prime_diagonal_isotropy.py -- G1' execution (CLAUDE.md 6.3.8).

CLAIM (Math427 Proposition): within the DIAGONAL Gaussian trial class
G^-1(q) = r_hat(q_dir) + c (q^2 - q0^2)^2  (any angular profile r_hat(q_dir),
the two-parameter Bragg-cone family of Math426-AddA S2 included), the
Gibbs-Bogoliubov variational optimum at every condensate amplitude A is the
ISOTROPIC profile r_hat(q_dir) = const. Reason: with local quartic/sextic
interactions Wick-contracted, the interactions enter F_var only through
M_tot = int_q G(q); the pointwise Euler-Lagrange equation for r_hat(q_dir)
is direction-independent, so the unique stationary profile is constant.
Consequence: the corrected-canonical isotropic Hartree restoration
(Math426: A* = 0 for LAM/HEX/FCC/BCC at r_braz = mu2 = 0.005) is the
INFIMUM over the entire diagonal-anisotropic family -- the dispatched
cone-family attack cannot lower the ordered free energy.

NUMERICAL VERIFICATION: explicit two-parameter cone-family
F_var(A, r_ring, r_B, w) for BCC and HEX at corrected canonical:
 (i)  at fixed A > 0 (including the MF amplitude), the minimum over
      (r_ring, r_B) sits on the isotropic diagonal r_B = r_ring within
      grid tolerance, for several cone widths w;
 (ii) min over the full (A, r_ring, r_B) scan equals the isotropic
      Math426 result: global minimum at A* = 0, dF = 0;
 (iii) identity F_cone(r, r, w) == F_iso(r) exactly (implementation check).

Cone geometry: 2n cones of half-angle w around the Bragg directions;
solid-angle fraction f_B = n (1 - cos w). Radial loop integral is
direction-independent, so M_B = f_B M_rad(r_B), M_ring = (1-f_B) M_rad(r_ring),
I-integrals split identically.
"""
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import Math424_AddA_reading_uniqueness as m424   # M_fast, dI grid, COMB

U, V, Q0 = -0.86, 3.24, 0.6801747616
MU2 = 0.005
R_BRAZ = MU2                       # corrected canonical shell mass (Math426)
CLAIMS = []

def claim(name, expected, actual, tol):
    ok = abs(actual - expected) <= tol
    CLAIMS.append(dict(name=name, expected=expected, actual=actual,
                       tol=tol, passed=bool(ok)))
    assert ok, f"FAIL {name}: {expected} vs {actual}"

def claim_true(name, cond, detail=""):
    CLAIMS.append(dict(name=name, expected=True, actual=bool(cond),
                       tol=0, passed=bool(cond), detail=detail))
    assert cond, f"FAIL {name}: {detail}"

M_rad = m424.M_fast                 # radial loop integral (interp table)
_QG = m424._QG
_DEN0 = m424._DEN0

def I_rad(r_hat, r_ref):
    """Radial part of (1/2pi^2) int q^2 ln[(r_hat+den)/(r_ref+den)] dq."""
    integrand = _QG ** 2 * np.log((r_hat + _DEN0) / (r_ref + _DEN0))
    val = np.trapz(integrand, _QG) / (2 * np.pi ** 2)
    val += (r_hat - r_ref) / (1.0 * _QG[-1]) / (2 * np.pi ** 2)
    return float(val)

def F_cone(name, A, r_ring, r_B, w, r_R, M_R):
    """Gibbs-Bogoliubov dF for the cone-family trial state (relative to R_H).

    M_tot = (1-f) M_rad(r_ring) + f M_rad(r_B); entropy/coupling terms split
    with the same angular weights; interactions use M_tot (local Wick).
    """
    cmb = m424.COMB[name]
    n, N4, N6 = cmb["n"], cmb["N4"], cmb["N6"]
    f = min(max(n * (1.0 - math.cos(w)), 0.0), 1.0)
    Mr, Mb = M_rad(r_ring), M_rad(r_B)
    M = (1 - f) * Mr + f * Mb
    dI = (1 - f) * I_rad(r_ring, r_R) + f * I_rad(r_B, r_R)
    rM = (1 - f) * r_ring * Mr + f * r_B * Mb
    A2, A4, A6 = A * A, A ** 4, A ** 6
    r = R_BRAZ
    return (0.5 * dI - 0.5 * (rM - r_R * M_R)
            + 0.5 * r * (2 * n * A2 + M - M_R)
            + 3 * U * n * A2 * M + 0.75 * U * (M * M - M_R * M_R)
            + 0.25 * U * N4 * A4 + 2.5 * V * N4 * A4 * M
            + 15 * V * n * A2 * M * M + 2.5 * V * (M ** 3 - M_R ** 3)
            + (V / 6.0) * N6 * A6)

# ---- disordered reference at corrected canonical ----
r_R = m424.gap_solve(R_BRAZ, 0, 0, 0.0)
M_R = M_rad(r_R)
claim("corrected_r_R", 0.3045, r_R, 5e-3)

# ---- (iii) implementation identity: cone == isotropic on the diagonal ----
iso = m424.dF_reading(R_BRAZ, "BCC", 0.06, r_R, M_R)
rh_iso = iso[1]; f_iso = iso[0]
cone_diag = F_cone("BCC", 0.06, rh_iso, rh_iso, 0.35, r_R, M_R)
claim("diagonal_identity_cone_eq_iso", f_iso, cone_diag, 1e-10)

# ---- (i)+(ii) scans ----
out_scans = {}
overall_min = (0.0, None)
for name in ["BCC", "HEX"]:
    cmb = m424.COMB[name]
    n, N4, N6 = cmb["n"], cmb["N4"], cmb["N6"]
    A_scale = math.sqrt(abs(U) * N4 / (V * N6))
    A_list = [0.5 * A_scale, A_scale, 1.5 * A_scale, 2.0 * A_scale]
    rgrid = np.geomspace(0.02, 3.0, 26)
    best_offdiag_gain = 0.0
    rows = []
    def iso_min_refined(A, w):
        """Continuum-accurate isotropic 1-d minimum via coarse grid + golden."""
        vals = [(F_cone(name, A, r, r, w, r_R, M_R), r) for r in rgrid]
        v0, r0 = min(vals)
        lo = r0 / 1.6; hi = r0 * 1.6
        for _ in range(60):
            m1 = lo + 0.382 * (hi - lo); m2 = lo + 0.618 * (hi - lo)
            if F_cone(name, A, m1, m1, w, r_R, M_R) <                F_cone(name, A, m2, m2, w, r_R, M_R):
                hi = m2
            else:
                lo = m1
        rb = 0.5 * (lo + hi)
        return min(v0, F_cone(name, A, rb, rb, w, r_R, M_R))

    for w in (0.15, 0.35, 0.60):
        for A in A_list:
            # PROPOSITION TEST: any 2-d GRID minimum must lie at or above the
            # continuum isotropic minimum (subset-min >= continuum-min; the
            # continuum optimum is on the diagonal by the pointwise EL
            # argument). Grid-vs-grid comparison would false-positive on
            # discretisation (observed 2.6e-5 for HEX before this fix).
            fiso = iso_min_refined(A, w)
            best2 = min(F_cone(name, A, rr, rb, w, r_R, M_R)
                        for rr in rgrid for rb in rgrid)
            rows.append(dict(w=w, A=float(A), F_iso_min=fiso, F_2d_min=best2))
            gain = fiso - best2          # >0 would mean anisotropy beats the
            best_offdiag_gain = max(best_offdiag_gain, gain)  # continuum iso
            if best2 < overall_min[0]:
                overall_min = (best2, (name, w, float(A)))
    out_scans[name] = rows
    claim_true(f"no_anisotropic_gain_{name}",
               best_offdiag_gain <= 1e-9,
               f"max gain vs refined isotropic floor = {best_offdiag_gain:.2e}")

# ---- (ii) global minimum still the disordered state ----
claim_true("global_min_remains_A0",
           overall_min[0] >= -1e-9,
           f"min dF over all scans = {overall_min[0]:.3e} at {overall_min[1]}")

out = dict(theory_tag="Math427", date="2026-06-04",
           r_braz=R_BRAZ, r_R=r_R, M_R=M_R,
           scans=out_scans,
           overall_min=dict(dF=overall_min[0], where=str(overall_min[1])),
           claims=CLAIMS)
os.makedirs("Runs/math/Math427", exist_ok=True)
json.dump(out, open("Runs/math/Math427/g1prime_diagonal_isotropy.json", "w"),
          indent=1)
npass = sum(1 for c in CLAIMS if c["passed"])
print(f"r_R={r_R:.6f} M_R={M_R:.6f}")
print(f"max anisotropic gain (must be <=0 up to tol): see claims")
print(f"global min dF = {overall_min[0]:.3e} at {overall_min[1]}")
print(f"claims: {npass}/{len(CLAIMS)} PASS")
sys.exit(0)
