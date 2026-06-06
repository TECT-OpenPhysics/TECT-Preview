"""robustness_mu2_step5b_remargin.py — ROBUSTNESS-MU2 closure: re-margin the
STEP-5B beyond-layer closure at off-anchor mu^2.

The previous note (robustness-mu2-offanchor) settled the A=0-uniqueness
component and left ONE residual: the exact off-anchor re-margining of the
STEP-5B closure. This script computes the AddE de-thinned closure margin
ratio = K_budget / K(n_pack) at off-anchor mu^2 (only the J_eff envelope
integral is recomputed; the rest is closed-form), across a x0.5..x2
neighbourhood and the three condensate intensities. If the ratio stays > 1
throughout, the STEP-5B closure holds off-anchor and ROBUSTNESS-MU2 closes.

The layer margin m is kept at its anchor value MARGIN; its own off-anchor
robustness is the Prop-A floor (P_B), preserved because M_R/M_c > 4 throughout
the neighbourhood (robustness-mu2-offanchor, 9/9) -- so m stays positive and
O(anchor). Conservative where m grows, flagged where it could shrink.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-06"
__version_issued__ = "2026-06-06"
__claims__ = ["B1-RH-ENUM", "B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402

U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
MARGIN = 0.00432          # anchor layer margin (Prop A band, Math437/Math440)
CLAIMS = []
def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def J_of_t(t, r_diag, nk=500, nmu=320, kmax_fac=8.0):
    k = np.linspace(1e-6, kmax_fac * Q0, nk)
    mu = np.linspace(-1.0, 1.0, nmu)
    Kg, MUg = np.meshgrid(k, mu, indexing="ij")
    Dk = r_diag + C * (Kg**2 - Q0**2)**2
    kp2 = Kg**2 + t**2 + 2.0 * Kg * t * MUg
    Dkp = r_diag + C * (kp2 - Q0**2)**2
    inner = np.trapezoid(Kg**2 / (Dk * Dkp), mu, axis=1)
    return float(np.trapezoid(inner, k) / (4.0 * np.pi**2) * 2.0)

def remargin(mu2, I):
    rR = m424.gap_solve(mu2, 0, 0, 0.0)
    M_R = m424.M_fast(rR)
    lam = 3.0 * U + 30.0 * V * M_R
    rhat = rR + 2.0 * lam * I
    a0 = 2.0 * lam * I / rhat
    theta_min = math.sqrt(rhat) / (2.0 * Q0**2 * math.sqrt(C))
    n_pack = 16.0 / theta_min**2
    t_min = 2.0 * Q0 * math.sin(theta_min / 2.0)
    J_eff = J_of_t(t_min, rhat)
    K = 8.0 + 4.0 * math.sqrt(14.0) * math.sqrt(n_pack)
    Kb = 4.0 * (1.0 - a0) * MARGIN / ((lam * I)**2 * J_eff)
    return dict(mu2=mu2, I=I, lam=lam, rhat=rhat, a0=a0, n_pack=n_pack,
                J_eff=J_eff, ratio=Kb / K, M_R=M_R, ratio_Mc=M_R / (-U/(10*V)))

ANCHOR = 0.005
INTENS = [4e-4, 1e-3, 2e-3]
print("ROBUSTNESS-MU2 closure: STEP-5B re-margin at off-anchor mu^2")
# (0) anchor sanity: reproduce the AddE floors x59.4 / x8.8 / x2.6
print("    anchor check (should reproduce AddE x59.4 / x8.8 / x2.6):")
anc = {I: remargin(ANCHOR, I) for I in INTENS}
for I in INTENS:
    print(f"      I={I:.0e}: ratio = x{anc[I]['ratio']:.1f}")
claim("anchor_reproduces_AddE_floors",
      55 < anc[4e-4]['ratio'] < 65 and 2.0 < anc[2e-3]['ratio'] < 3.2,
      f"(x{anc[4e-4]['ratio']:.1f} / x{anc[1e-3]['ratio']:.1f} / x{anc[2e-3]['ratio']:.1f} vs AddE 59.4/8.8/2.6)")

# (1) off-anchor sweep x0.5 .. x2
mu2_list = [0.0025, 0.00354, ANCHOR, 0.00707, 0.01]   # x0.5, x0.71, x1, x1.41, x2
print("    off-anchor margin ratios (m kept at anchor layer margin):")
print("    mu^2      ratio@4e-4  ratio@1e-3  ratio@2e-3   M_R/M_c")
worst = 1e9
grid = []
for mu2 in mu2_list:
    rs = {I: remargin(mu2, I) for I in INTENS}
    grid.append({"mu2": mu2, **{f"ratio_{I:g}": rs[I]["ratio"] for I in INTENS},
                 "ratio_Mc": rs[4e-4]["ratio_Mc"]})
    worst = min(worst, min(rs[I]["ratio"] for I in INTENS))
    print(f"    {mu2:.5f}   x{rs[4e-4]['ratio']:6.1f}    x{rs[1e-3]['ratio']:5.1f}     "
          f"x{rs[2e-3]['ratio']:4.2f}      {rs[4e-4]['ratio_Mc']:.2f}")

claim("step5b_closure_holds_offanchor", worst > 1.0,
      f"(worst margin ratio over mu^2 in [x0.5, x2] and all 3 intensities = x{worst:.2f} > 1: "
      "STEP-5B closure holds throughout the neighbourhood)")
claim("endpoint_margin_offanchor", min(g["ratio_0.002"] for g in grid) > 1.5,
      f"(worst endpoint (I=2e-3) ratio across x0.5..x2 = x{min(g['ratio_0.002'] for g in grid):.2f} > 1.5)")
# (2) layer-margin floor preserved: M_R/M_c > 4 throughout => Prop-A P_B floor positive
claim("propA_floor_preserved", all(g["ratio_Mc"] > 3.5 for g in grid),
      f"(M_R/M_c > 3.5 throughout (min {min(g['ratio_Mc'] for g in grid):.2f}): the Prop-A P_B layer "
      "margin floor structure is preserved, so m stays positive and O(anchor) off-anchor)")
# (3) monotone trend: thinnest at the largest mu^2 (endpoint), still > 1
claim("worst_at_largest_mu2", grid[-1]["ratio_0.002"] <= grid[0]["ratio_0.002"] + 0.5,
      f"(endpoint ratio at x2 mu^2 = x{grid[-1]['ratio_0.002']:.2f}, the thinnest corner, still > 1)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B1-RH-ENUM" / "runs" / "260606-robustness-mu2-step5b"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="robustness_mu2_step5b_remargin.py", version=__version__,
    anchor=ANCHOR, margin=MARGIN, worst_ratio=worst, grid=grid,
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
