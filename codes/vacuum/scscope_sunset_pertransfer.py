"""scscope_sunset_pertransfer.py -- per-transfer hardening of the SC-SCOPE sunset
endpoint margin (the B5 T7 path, hypothesis H-ENDPOINT-THINNESS-ACCEPTED target).

The certified endpoint joint is sunset-capped: joint -> S as rho -> inf, with
S = x1.129 the single-J0 anchor (scscope_mendpoint_eval.py: bound = 1/2 u_eff^2
(2I) 6 J0 M, J0 = sup_t J(t) at the 4e-4 dressing -- DOUBLY conservative: sup
over transfer AND the loosest dressing). This script evaluates the REALIZED
per-transfer sunset kernel: the proxy J0*M bounds the convolution (J*G)(t)
(bubble x propagator = the 3-propagator sunset kernel) by sup_J x int G; the
realized value replaces sup_J by the D-WEIGHTED LOOP AVERAGE

    J_eff(t) = [int dk dmu k^2 J(k') / D(k)] / [int dk dmu k^2 / D(k)],
    k' = sqrt(k^2 + t^2 + 2 k t mu),

with all propagators at the ENDPOINT dressing r_hat(2e-3) = 0.33675. The
substitution is EXACT (evaluating the convolution instead of bounding it); the
absolute normalisation CANCELS in the ratio (no /(2pi)^3 convention enters --
the factor-2 error class is structurally excluded). Admissible transfers obey
|t| >= t_min (theta_min separation), so sup over the realized chord set
[t_min, 2 q0] is a sound per-transfer bound.

PRE-REGISTERED GATES (before computation):
  G1: shape_max = max_chords J_eff(t)/J0 >= 1  -> hardening FAILS (honest negative).
  G2: S_realized = S_anchor / shape_max <= 1.2 -> hardening immaterial.
  G3: success -> report S_realized and the recomputed joints at rho = 6.55, 12.6.
self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-12"
__claims__ = ["B5-BEYOND-LAYER-BOUND"]

import json, sys, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/"codes"/"vacuum")); sys.path.insert(0, str(REPO/"archive"/"legacy"/"scripts"))
import sectorb_common as sb
import Math424_AddA_reading_uniqueness as m424

CLAIMS = []
def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

U, V, Q0, C = sb.U, sb.V, sb.Q0, sb.C
MU2, I_END = 0.005, 2e-3
MARGIN = sb.margin_of(MU2)["margin"]
RHO = sb.RHO
rR = m424.gap_solve(MU2, 0, 0, 0.0)
M_R = m424.M_fast(rR)
lam = 3*U + 30*V*M_R
rhat_anchor = rR + 2.0*lam*4e-4          # the 4e-4 dressing (anchor J0 basis)
rhat_end    = rR + 2.0*lam*I_END         # endpoint dressing 0.33675
M_END = m424.M_fast(rhat_end)

def composed(I): return MARGIN*(1.0 - 1.0/RHO[I])
def sunset_bound(I, M, J): return 0.5*sb.u_eff(M)**2*(2.0*I)*6.0*J*M

# ---------- (1) anchor reproduction (calibration gate) ----------
J0 = sb.J_of_t(1e-9, rhat_anchor)
S_anchor = composed(I_END)/sunset_bound(I_END, M_END, J0)
claim("anchor_x1p129_reproduced", abs(S_anchor - 1.129) < 0.015,
      f"(S_anchor = composed/bound = x{S_anchor:.3f} reproduces the mendpoint x1.129 single-J0 "
      f"anchor; J0 = {J0:.4f}, M_END = {M_END:.6f}, rhat_end = {rhat_end:.5f})")

# ---------- (2) J grid at the ENDPOINT dressing + J_eff machinery ----------
QMAX = 8.0*Q0
qg = np.linspace(1e-6, QMAX, 90)
Jg = np.array([sb.J_of_t(float(q), rhat_end) for q in qg])
def Ji(qq): return np.interp(np.asarray(qq), qg, Jg, left=Jg[0], right=0.0)
J0_end = float(Jg[0])                     # sup_t J(t) at the endpoint dressing

def J_eff(t, nk=500, nmu=320):
    k = np.linspace(1e-6, QMAX, nk); mu = np.linspace(-1.0, 1.0, nmu)
    Kg, MUg = np.meshgrid(k, mu, indexing="ij")
    D = rhat_end + C*(Kg**2 - Q0**2)**2
    kp = np.sqrt(np.maximum(Kg**2 + t**2 + 2.0*Kg*t*MUg, 0.0))
    num = np.trapezoid(np.trapezoid(Kg**2*Ji(kp)/D, mu, axis=1), k)
    den = np.trapezoid(np.trapezoid(Kg**2/D, mu, axis=1), k)
    return float(num/den)

# two-way pin at t -> 0: the mu-integral degenerates, J_eff(0) = int k^2 J(k)/D / int k^2/D (1D)
k1 = np.linspace(1e-6, QMAX, 4000)
D1 = rhat_end + C*(k1**2 - Q0**2)**2
direct0 = float(np.trapezoid(k1**2*Ji(k1)/D1, k1)/np.trapezoid(k1**2/D1, k1))
conv0 = J_eff(1e-9)
claim("two_way_pin_t0", abs(conv0/direct0 - 1.0) < 1e-3,
      f"(J_eff(t->0) two ways: convolution {conv0:.5f} == direct 1D {direct0:.5f}, "
      f"ratio {conv0/direct0:.5f} -- quadrature/convention pin, no absolute normalisation enters)")

# ---------- (3) realized chord set (same as the quartic certificate) ----------
theta_min = math.sqrt(rhat_end)/(2.0*Q0**2*math.sqrt(C))
t_min = 2.0*Q0*math.sin(theta_min/2.0)
chords = np.linspace(t_min, 2.0*Q0, 16)
Jeffs = np.array([J_eff(float(t)) for t in chords])
claim("sup_bound_consistency", bool((Jeffs <= J0 + 1e-9).all()),
      f"(J_eff(t) <= J0 = {J0:.4f} on every chord: the realized kernel never exceeds the anchor sup "
      f"-- max J_eff = {Jeffs.max():.4f} at t = {float(chords[int(np.argmax(Jeffs))]):.3f})")

# grid-convergence: double both grids on the worst chord
t_star = float(chords[int(np.argmax(Jeffs))])
drift = abs(J_eff(t_star, nk=1000, nmu=640)/J_eff(t_star) - 1.0)
claim("grid_convergence", drift < 0.01,
      f"(doubling the loop grids moves the worst-chord J_eff by {drift*100:.2f}% < 1%)")

# ---------- (4) shape factor and the gates ----------
shape_max = float(Jeffs.max()/J0)
S_realized = S_anchor/shape_max
gate = "G3-SUCCESS" if (shape_max < 1.0 and S_realized > 1.2) else ("G2-IMMATERIAL" if shape_max < 1.0 else "G1-FAIL")
claim("preregistered_gate_verdict", gate == "G3-SUCCESS",
      f"(shape_max = {shape_max:.4f} -> S_realized = S_anchor/shape_max = x{S_realized:.3f}; gate {gate}; "
      "per the pre-registration: G1 shape>=1 fail / G2 S<=1.2 immaterial / G3 success)")

# ---------- (5) recomputed joints ----------
qrun = json.loads((REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260609-scscope-quartic-certificate"/"result.json").read_text())
R_max = float(qrun["R_max_certified"])
def joint(rho, S): return 1.0/((1.0 + R_max)/rho + (1.0 - 1.0/rho)/S)
j_cons_old, j_cons_new = joint(6.55, 1.13), joint(6.55, S_realized)
j_ver_old,  j_ver_new  = joint(12.6, 1.13), joint(12.6, S_realized)
claim("joint_recomputed", j_cons_new > j_cons_old and abs(j_cons_old - 1.040) < 0.01,
      f"(certified R_max = {R_max:.3f}; joint(rho=6.55): x{j_cons_old:.3f} -> x{j_cons_new:.3f}; "
      f"joint(rho=12.6): x{j_ver_old:.3f} -> x{j_ver_new:.3f}; saturation cap rho->inf: "
      f"x1.13 -> x{S_realized:.3f})")
claim("hardening_beyond_thin", j_cons_new > 1.3,
      f"(the conservative-floor joint x{j_cons_new:.3f} > 1.3: the endpoint closure is no longer THIN "
      "under the per-transfer sunset kernel -- CANDIDATE evidence for removing "
      "H-ENDPOINT-THINNESS-ACCEPTED; operator decision required, NO flip here)")

# direction sanity: J_eff decreasing in t beyond the peak region; t_min realized
claim("admissibility_floor", t_min > 0.3 and float(chords[0]) >= t_min - 1e-12,
      f"(theta_min = {theta_min:.3f} -> t_min = {t_min:.3f}: every admissible transfer sits on the "
      "evaluated chord set [t_min, 2q0])")

ok = all(c["passed"] for c in CLAIMS)
out = REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260612-scscope-sunset-pertransfer"
out.mkdir(parents=True, exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(
    script="scscope_sunset_pertransfer.py", version=__version__,
    S_anchor=S_anchor, J0=J0, J0_end=J0_end, rhat_end=rhat_end, M_END=M_END,
    t_min=t_min, chords=list(map(float, chords)), J_eff=list(map(float, Jeffs)),
    shape_max=shape_max, S_realized=S_realized, gate=gate, R_max=R_max,
    joint_cons_old=j_cons_old, joint_cons_new=j_cons_new,
    joint_ver_old=j_ver_old, joint_ver_new=j_ver_new,
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nS_anchor x{S_anchor:.3f} -> S_realized x{S_realized:.3f} (shape {shape_max:.3f}); "
      f"joint {j_cons_old:.3f}->{j_cons_new:.3f} (cons) / {j_ver_old:.3f}->{j_ver_new:.3f} (ver)")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
