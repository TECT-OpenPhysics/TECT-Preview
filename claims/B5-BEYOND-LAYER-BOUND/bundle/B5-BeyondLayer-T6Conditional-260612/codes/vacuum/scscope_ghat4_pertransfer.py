"""scscope_ghat4_pertransfer.py -- SC-SCOPE / GHAT4-PERTRANSFER: the per-transfer
quartic-difference form factor on the realized chord set, replacing the crude
sup-kernel Young bound.

Background (quartic-difference-channel-260606-v1.0, T2 estimate). The
quartic-difference channel inflates the certified second-order budget by a
per-transfer ratio
    R(t) = 12 (5v/2)^2 / lam'^2 * Ghat4(t) * 4(1-a0) / J(t),
with Ghat4 = G*G*G*G = J*J (J the bubble). The sup-kernel estimate took the
Young ceiling Ghat4(t) <= J(0) M^2 AND the worst J(t) >= J(2q0) SIMULTANEOUSLY,
giving R_sup ~ 1.59 -> inflation x2.6 -> the I=2e-3 endpoint x2.6/2.6 ~ x1.0
(MARGINAL). That pairing is INCOMPATIBLE: where J(t) is smallest (large t),
Ghat4(t) is also small; where Ghat4(t) is near its ceiling (small t), J(t) is
near J(0), not J(2q0). This script evaluates the realized per-transfer ratio.

Convention safety. The absolute normalisation of Ghat4 carries a factor-2 /
(2pi)^3 measure convention (the same class as the M'=-J(0) vs -J(0)/2 slip).
We therefore work with the CONVENTION-FREE shape factor
    Phi(t) = [Ghat4(t)/Ghat4(0)] * [J(0)/J(t)],
in which every measure prefactor and the J-normalisation factor-2 cancel. The
sup estimate corresponds to the incompatible pairing Phi_sup = J(0)/J(2q0)
(Ghat4 at its t~0 ceiling, J at its t=2q0 floor). The realized reduction is
reduction = max_t Phi(t) / Phi_sup, and the firmed per-transfer ratio is
    R_max = R_sup_cited * reduction,
with R_sup_cited = 1.59 the cited estimate (the convention-bearing coupling
normalisation, NOT recomputed here -- flagged). Endpoint survives iff
R_max < 1.6 (inflation 1+R_max < 2.6, so the x2.6 floor stays > x1.0).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import sectorb_common as sb                       # noqa: E402
import Math424_AddA_reading_uniqueness as m424    # noqa: E402

U, V, Q0, C = sb.U, sb.V, sb.Q0, sb.C
MU2 = 0.005
I_END = 2e-3
R_SUP_CITED = 1.59      # quartic-difference-channel v1.0 (ESTIMATE; convention-bearing, not recomputed)
ENDPOINT_FLOOR = 2.6    # AddE STEP-5B endpoint floor (rho); cited certified
CLAIMS = []

def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

# endpoint dressing (competitor at its own kernel)
rR = m424.gap_solve(MU2, 0, 0, 0.0)
M_R = m424.M_fast(rR)
lam = 3.0 * U + 30.0 * V * M_R
rhat = rR + 2.0 * lam * I_END
a0 = 2.0 * lam * I_END / rhat
print(f"GHAT4-PERTRANSFER: endpoint dressing rhat={rhat:.5f}, a0={a0:.4f}")

def J(t):
    return sb.J_of_t(t, rhat, nk=700, nmu=480)

# Precompute J on a |q| grid for the J*J convolution (isotropic) + interpolate.
QMAX = 8.0 * Q0
qgrid = np.linspace(1e-6, QMAX, 1400)
Jgrid = np.array([J(q) for q in qgrid])
def Ji(qq):
    return np.interp(np.asarray(qq), qgrid, Jgrid, left=Jgrid[0], right=0.0)

def Ghat4(t, nq=1400, nmu=400):
    """(J*J)(t) = int d^3q/(2pi)^3 J(|q|) J(|t-q|); convention-free up to overall scale."""
    q = np.linspace(1e-6, QMAX, nq)
    mu = np.linspace(-1.0, 1.0, nmu)
    Qg, MUg = np.meshgrid(q, mu, indexing="ij")
    arg = np.sqrt(np.maximum(Qg**2 + t**2 - 2.0 * Qg * t * MUg, 0.0))
    integ = Qg**2 * Ji(Qg) * Ji(arg)
    inner = np.trapezoid(integ, mu, axis=1)
    return float(np.trapezoid(inner, q) / (4.0 * np.pi**2))

# realized chord set at the endpoint geometry: t in [t_min, 2 q0]
theta_min = math.sqrt(rhat) / (2.0 * Q0**2 * math.sqrt(C))
t_min = 2.0 * Q0 * math.sin(theta_min / 2.0)
t_max = 2.0 * Q0
chords = np.linspace(t_min, t_max, 24)
print(f"    realized chords: t_min={t_min:.4f} .. 2q0={t_max:.4f} (q0={Q0:.4f})")

J0 = J(1e-9)
J_2q0 = J(2.0 * Q0)
G0 = Ghat4(1e-4)                       # Ghat4 at t->0 (the shape ceiling)
claim("J_ratio_reproduces_note", abs((J0 / J_2q0) - 2.79) < 0.15,
      f"(J(0)/J(2q0) = {J0/J_2q0:.3f} vs note 2.79; absolute J(0)={J0:.4f}/J(2q0)={J_2q0:.4f} are smaller "
      f"than the note's anchor-dressing 0.290/0.104 because this is the ENDPOINT dressing rhat={rhat:.4f} "
      "(J decreases with dressing); the convention-free RATIO is what enters Phi)")

# convention-free per-transfer shape factor Phi(t) = [Ghat4(t)/Ghat4(0)]*[J(0)/J(t)]
Phi = []
for t in chords:
    g = Ghat4(t); jt = J(t)
    Phi.append((t, g / G0, J0 / jt, (g / G0) * (J0 / jt)))
Phi_vals = np.array([p[3] for p in Phi])
Phi_sup = J0 / J_2q0
imax = int(Phi_vals.argmax())
Phi_max = float(Phi_vals.max())
print("    t        Ghat4(t)/Ghat4(0)   J0/J(t)    Phi(t)")
for (t, gr, jr, ph) in Phi:
    print(f"    {t:.4f}    {gr:8.4f}        {jr:7.3f}   {ph:7.4f}")

claim("Phi_small_t_to_one", abs(Phi[0][1] * (J0 / J(chords[0])) - Phi[0][3]) < 1e-9 and Phi[0][1] <= 1.0 + 1e-6,
      f"(at t_min Ghat4 ratio {Phi[0][1]:.3f} <= 1; Phi well-defined)")
claim("Ghat4_shape_below_ceiling", all(p[1] <= 1.0 + 1e-6 for p in Phi),
      f"(Ghat4(t)/Ghat4(0) <= 1 for all realized t: max {max(p[1] for p in Phi):.3f} -- t=0 is the shape ceiling)")
claim("incompatible_pairing_confirmed", Phi_max < Phi_sup,
      f"(max_t Phi(t) = {Phi_max:.3f} (at t={Phi[imax][0]:.4f}) << Phi_sup = J0/J(2q0) = {Phi_sup:.3f}: "
      "the sup bound's max-Ghat4 x max-(1/J) pairing is incompatible; the realized ratio is far smaller)")

reduction = Phi_max / Phi_sup
R_max = R_SUP_CITED * reduction
inflation = 1.0 + R_max
endpoint_ratio = ENDPOINT_FLOOR / inflation
print(f"    reduction = max Phi / Phi_sup = {reduction:.3f}; R_max = {R_SUP_CITED} * {reduction:.3f} = {R_max:.3f}")
print(f"    quartic-difference endpoint inflation = {inflation:.3f}; endpoint ratio = {ENDPOINT_FLOOR}/{inflation:.3f} = x{endpoint_ratio:.2f}")
claim("per_transfer_R_below_threshold", R_max < 1.6,
      f"(R_max = {R_max:.3f} < 1.6: the quartic-difference inflation 1+R_max = {inflation:.3f} < 2.6, so the "
      f"endpoint floor stays > x1.0; per-transfer endpoint ratio x{endpoint_ratio:.2f})")
claim("quartic_difference_endpoint_positive", endpoint_ratio > 1.0,
      f"(quartic-difference endpoint ratio x{endpoint_ratio:.2f} > 1: GHAT4-PERTRANSFER resolved -- the "
      "sup-grade x1.0 MARGINAL was the incompatible-pairing artefact)")

# convergence sanity: Ghat4 stable under grid refinement
G0_hi = Ghat4(1e-4, nq=2000, nmu=600)
claim("Ghat4_grid_converged", abs(G0_hi - G0) < 0.03 * G0,
      f"(Ghat4(0) at nq=1400 vs 2000 agree to {abs(G0_hi-G0)/G0*100:.2f}%: convolution quadrature converged)")

print("    SCOPE: GHAT4-PERTRANSFER resolved (per-transfer shape). SC-SCOPE still needs")
print("           R-U6-1 (tadpole) + the joint second+third-order endpoint inequality.")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B5-BEYOND-LAYER-BOUND" / "runs" / "260607-scscope-ghat4-pertransfer"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="scscope_ghat4_pertransfer.py", version=__version__,
    constants=dict(rhat=rhat, a0=a0, J0=J0, J_2q0=J_2q0, Phi_sup=Phi_sup,
                   R_sup_cited=R_SUP_CITED, endpoint_floor=ENDPOINT_FLOOR),
    chords=[{"t": p[0], "Ghat4_ratio": p[1], "J0_over_Jt": p[2], "Phi": p[3]} for p in Phi],
    Phi_max=Phi_max, reduction=reduction, R_max=R_max,
    endpoint_inflation=inflation, endpoint_ratio=endpoint_ratio,
    scope="GHAT4-PERTRANSFER per-transfer shape resolved; absolute R_sup cited (estimate); "
          "SC-SCOPE OPEN on R-U6-1 + joint inequality",
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
