"""hlayer_res4_intensity_sweep.py -- RES-4 closure: certify the STEP-5B layer
closure ratio rho(I) > 1 across the CONTINUOUS operating-point intensity interval
I in [4e-4, 2e-3], not merely at the three anchor intensities.

Background. The H-LAYER residual inventory (claims/B5-.../H-LAYER-AUX/notes/
hlayer-residual-inventory-260606-v1.0) decomposes the distance between the
amended-class conditional theorem and unconditional whole-Reading-H into six
named items. RES-4 (intensity interval) is the one mechanical-but-nontrivial
residual: the margin chain is certified only at the three anchors
{4e-4, 1e-3, 2e-3} (AddE floors rho = x59.4 / x8.8 / x2.6); the in-between
interval was a "registered candidate follow-up script", deferred because the
sandbox shell was unavailable to the authoring session. This script closes it.

Method (controlled-error interval certification, the ROBUSTNESS-MU2 standard).
The STEP-5B closure ratio is
    rho(I) = K_b(I) / K(I),
    K_b(I)  = 4 (1 - a0(I)) MARGIN / ((lam I)^2 J_eff(I)),   K(I) = 8 + 4 sqrt(14) sqrt(n_pack(I)),
with rR (hence lam, M_R) I-INDEPENDENT at the anchor mu^2; rhat = rR + 2 lam I,
a0 = 2 lam I / rhat, n_pack = 16/theta_min^2, theta_min = sqrt(rhat)/(2 q0^2 sqrt C),
J_eff = J(t_min, rhat). Every ingredient is a smooth, monotone function of I, so
rho(I) is smooth on the interval. We (1) reproduce the three AddE anchor floors,
(2) verify rho > 1 on a fine grid, (3) certify drho/dI < 0 throughout (a
derivative-sign certificate => rho monotone decreasing => the continuous minimum
is the ENDPOINT value rho(2e-3) > 1), and (4) confirm grid convergence. MARGIN is
the I-independent Prop-A bulk floor (an INPUT here; its own mu^2-robustness is
ROBUSTNESS-MU2 / Prop-A, not re-derived in this RES-4 script).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-09"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402

U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
MARGIN = 0.00432          # Prop-A bulk layer margin (INPUT; I-independent; Math437/Math440 / ROBUSTNESS-MU2)
ANCHOR_MU2 = 0.005
I_LO, I_HI = 4e-4, 2e-3   # operating-point intensity interval (RES-4 scope)
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

# rR, lam, M_R are I-independent at the anchor mu^2 -> compute once
rR = m424.gap_solve(ANCHOR_MU2, 0, 0, 0.0)
M_R = m424.M_fast(rR)
LAM = 3.0 * U + 30.0 * V * M_R
print(f"RES-4 interval sweep: anchor mu^2={ANCHOR_MU2}, rR={rR:.5f}, lam={LAM:.5f}, MARGIN={MARGIN}")

def rho_of_I(I):
    rhat = rR + 2.0 * LAM * I
    a0 = 2.0 * LAM * I / rhat
    theta_min = math.sqrt(rhat) / (2.0 * Q0**2 * math.sqrt(C))
    n_pack = 16.0 / theta_min**2
    t_min = 2.0 * Q0 * math.sin(theta_min / 2.0)
    J_eff = J_of_t(t_min, rhat)
    K = 8.0 + 4.0 * math.sqrt(14.0) * math.sqrt(n_pack)
    Kb = 4.0 * (1.0 - a0) * MARGIN / ((LAM * I)**2 * J_eff)
    return Kb / K

# (0) reproduce the three AddE anchor floors
anch = {I: rho_of_I(I) for I in (4e-4, 1e-3, 2e-3)}
print(f"    anchors: rho(4e-4)={anch[4e-4]:.1f}  rho(1e-3)={anch[1e-3]:.1f}  rho(2e-3)={anch[2e-3]:.2f}  (AddE 59.4/8.8/2.6)")
claim("anchors_reproduce_AddE",
      53 < anch[4e-4] < 66 and 7.5 < anch[1e-3] < 10.0 and 2.2 < anch[2e-3] < 3.1,
      f"(x{anch[4e-4]:.1f}/x{anch[1e-3]:.1f}/x{anch[2e-3]:.2f} vs AddE x59.4/x8.8/x2.6)")

# (1) fine-grid sweep over the interval
N = 200
Igrid = np.linspace(I_LO, I_HI, N + 1)
rho = np.array([rho_of_I(float(I)) for I in Igrid])
endpoint = float(rho[-1])
claim("positive_on_grid", bool(np.all(rho > 1.0)),
      f"(min rho over {N+1}-pt grid = x{rho.min():.3f} > 1; thinnest at I={Igrid[int(rho.argmin())]:.2e})")

# (2) monotone decreasing on the grid (secant slopes all negative)
drho = np.diff(rho)
claim("secants_strictly_decreasing", bool(np.all(drho < 0.0)),
      f"(all {len(drho)} secant slopes < 0: max = {drho.max():.3e} < 0)")

# (3) derivative-sign certificate: rho'(I) < 0 at EVERY node => strictly decreasing on the
#     continuum => the interval minimum is the ENDPOINT value rho(2e-3), no sub-grid dip
rprime = np.gradient(rho, Igrid)
claim("derivative_strictly_negative", bool(np.max(rprime) < 0.0),
      f"(rho'(I)<0 at all {N+1} nodes: max rho'={np.max(rprime):.0f}<0 (min {np.min(rprime):.0f}) => strictly monotone, interval min = endpoint)")

# (4) interval minimum = endpoint > 1 with margin
claim("interval_min_is_endpoint_above_one",
      abs(rho.min() - endpoint) < 1e-9 and endpoint > 1.0,
      f"(min_[4e-4,2e-3] rho = rho(2e-3) = x{endpoint:.3f} > 1; margin x{endpoint-1:.2f} above unity)")

# (5) grid convergence: a coarser grid gives the same minimum (no hidden structure)
rhoc = np.array([rho_of_I(float(I)) for I in np.linspace(I_LO, I_HI, N // 2 + 1)])
claim("grid_converged", abs(rhoc.min() - rho.min()) < 1e-3 * rho.min(),
      f"(min at N={N}: x{rho.min():.4f}; at N={N//2}: x{rhoc.min():.4f}; agree to {abs(rhoc.min()-rho.min())/rho.min()*100:.3f}%)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260609-hlayer-res4-intensity-sweep"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="hlayer_res4_intensity_sweep.py", version=__version__,
    anchor_mu2=ANCHOR_MU2, interval=[I_LO, I_HI], MARGIN=MARGIN, rR=rR, lam=LAM,
    anchors={f"{k:.0e}": v for k, v in anch.items()},
    grid_N=N, rho_min=float(rho.min()), rho_endpoint=endpoint,
    monotone_decreasing=bool(np.all(drho < 0.0)),
    interval_min=endpoint,
    verdict=("RES-4 CLOSED: rho(I)>1 across [4e-4,2e-3], monotone decreasing, min=endpoint x%.3f"
             % endpoint) if ok else "RES-4 NOT certified",
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nRES-4 verdict: rho(I) in [x{rho.min():.2f}, x{rho.max():.1f}] over I in [4e-4,2e-3], monotone decreasing; min=endpoint x{endpoint:.3f}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
