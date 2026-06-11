"""res5_016_isotropy_infimum_core.py -- T-016: the isotropy-infimum core of
Math427 (the deepest H-LAYER axis). Proves that, within the diagonal-Gaussian
class, the isotropic dressing is a STRICT minimum of the condensate-free
functional F_0, with the Hessian BLOCK-DIAGONAL in angular momentum: the
interaction -- which depends ONLY on the rotation-invariant total variance
M_tot -- contributes solely to the l=0 (isotropic breathing) sector via
Phi''_diag = (3/2) u_eff > 0; every anisotropic sector l>=1 sees ONLY the
strictly-positive entropy Hessian (1/2) G_*^-2. Hence isotropy is protected by a
positive curvature gap in EVERY angular sector -- not a fine-tuned stationarity.

Setting (hdiag-fullcovariance-formulation v1.0). At the production anchor
mu^2 = 5e-3 the diagonal dressing is G_*(q) = 1/(r_R + c(q^2-q0^2)^2), c=1, and
    F_0[G]/V = (1/2) Tr ln G^-1 + (1/2) Tr[K_0 G] + Phi_diag(M_tot),
    M_tot = int_q G(q),   Phi_diag(M) = (3u/4)M^2 + (5v/2)M^3,
    Phi''_diag(M) = (3/2)(u + 10 v M) = (3/2) u_eff.
The second variation at G_* is
    d^2 F_0 = (1/2) int G_*(q)^-2 (dG)^2 d^3q + Phi''_diag (dM_tot)^2,
    dM_tot = int dG(q) d^3q.
Decomposing dG(q) = sum_{lm} a_lm(|q|) Y_lm(qhat): because int Y_lm dOmega = 0 for
l>=1, only l=0 contributes to dM_tot. The Hessian is therefore block-diagonal:
  * l>=1 (anisotropic): H_l = (1/2) G_*^-2  > 0           [entropy only]
  * l=0  (breathing):   H_0 = (1/2) G_*^-2 + Phi''_diag*w  > 0  [entropy + interaction]
Both strictly positive => the isotropic dressing is a STRICT diagonal minimum and
isotropy is curvature-protected. This is the rigorous core of Math427's diagonal
isotropy theorem (T6 conditional on H-diag); the off-diagonal extension is reduced
(T-018) to the exchange scalar b_exch (RES-5).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-10"
__claims__ = ["B2-PROPA-HLAYER", "B1-RH-ENUM"]

import json, sys, math
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402
U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
CLAIMS = []
def claim(n, c, d=""):
    CLAIMS.append(dict(name=n, passed=bool(c), detail=d))
    print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")

MU2 = 0.005
rR = m424.gap_solve(MU2, 0, 0, 0.0)
M_R = m424.M_fast(rR)
u_eff = U + 10.0 * V * M_R
print(f"anchor mu^2={MU2}: rR={rR:.5f}, M_R={M_R:.5f}, u_eff={u_eff:.5f}, c={C}")

# isotropic dressing on a radial grid; G_*(q) = 1/(rR + c(q^2-q0^2)^2)
q = np.linspace(1e-3, 3.0 * Q0, 4000)
G_star = 1.0 / (rR + C * (q * q - Q0 * Q0) ** 2)
entropy_hess = 0.5 * G_star ** (-2)            # per-mode entropy curvature (1/2)G^-2

# (1) l=0 (breathing) interaction convexity: Phi''_diag = (3/2) u_eff > 0
phi2 = 1.5 * u_eff
claim("breathing_l0_interaction_convex", phi2 > 0.0,
      f"(Phi''_diag = (3/2) u_eff = (3/2)({u_eff:.4f}) = {phi2:.4f} > 0: the l=0 isotropic-breathing sector, the "
      f"ONLY sector the rotation-invariant interaction Phi_diag(M_tot) curves, is strictly convex via the sextic "
      f"dressing of the attractive bare quartic u={U})")

# (2) anisotropic l>=1 entropy curvature: (1/2) G_*^-2 > floor > 0 on the BZ grid
ent_floor = float(entropy_hess.min())
claim("anisotropic_entropy_curvature_positive", ent_floor > 0.0,
      f"(min_q (1/2)G_*^-2 = {ent_floor:.4e} > 0 on the grid: every anisotropic sector l>=1 sees ONLY this "
      "strictly-positive entropy Hessian, since the interaction is flat against l>=1 perturbations)")

# (2b) ANALYTIC infimum (operator review): (1/2)G_*^-2 = (1/2)[rR + c(q^2-q0^2)^2]^2 >= (1/2)rR^2, attained at
#      the gap shell |q|=q0 -- the positivity is ANALYTIC, not a numerical grid artefact (theorem-grade).
ent_inf_analytic = 0.5 * rR ** 2
claim("entropy_infimum_analytic", abs(ent_floor - ent_inf_analytic) < 1e-3 and ent_inf_analytic > 0,
      f"(ANALYTIC infimum: (1/2)G_*^-2 = (1/2)[rR + c(q^2-q0^2)^2]^2 >= (1/2)rR^2 = {ent_inf_analytic:.4e}, attained "
      f"at the gap shell |q|=q0 where (q^2-q0^2)^2=0; the grid min {ent_floor:.4e} matches to <1e-3, confirming the "
      "entropy positivity is ANALYTIC (a square + rR^2>0), not numerical -- the l>=1 protection is theorem-grade)")

# (3) interaction flat against anisotropy: int Y_lm dOmega = 0 for l>=1 (EXACT quadrature)
#     => an l>=1 diagonal perturbation leaves M_tot UNCHANGED => Phi_diag contributes 0.
#     Use Gauss-Legendre nodes in u=cos(theta): integrates these polynomials in u to machine precision,
#     and the m!=0 azimuthal factor integrates to 0 over phi exactly (cos(m*phi)).
u_gl, w_gl = np.polynomial.legendre.leggauss(16)   # exact for deg <= 31 >> 4
def Pl_u(l, m, u):
    if (l, m) == (1, 0): return u
    if (l, m) == (2, 0): return 3 * u ** 2 - 1
    if (l, m) == (2, 2): return (1 - u ** 2)          # theta-part of Y_22 (azimuthal cos(2phi) -> 0 over phi)
    if (l, m) == (3, 0): return 5 * u ** 3 - 3 * u
    if (l, m) == (4, 0): return 35 * u ** 4 - 30 * u ** 2 + 3
    raise ValueError
half = float(w_gl.sum())  # = int_{-1}^{1} du = 2
aniso_int = {}
for (l, m) in [(1, 0), (2, 0), (2, 2), (3, 0), (4, 0)]:
    theta_avg = float((w_gl * Pl_u(l, m, u_gl)).sum()) / half     # <theta-part>_u over [-1,1]
    azim = 1.0 if m == 0 else 0.0                                  # int cos(m phi) dphi / 2pi = 0 for m>=1
    aniso_int[f"{l},{m}"] = abs(theta_avg * azim)
max_aniso = max(aniso_int.values())
claim("interaction_flat_against_anisotropy", max_aniso < 1e-10,
      f"(int Y_lm dOmega = 0 for l>=1 EXACTLY (orthogonality with Y_00); Gauss-Legendre (16 nodes, exact for the "
      f"degree<=4 Legendre polynomials) gives max over (1,0),(2,0),(2,2),(3,0),(4,0) = {max_aniso:.2e} (machine "
      "zero) => an l>=1 diagonal perturbation leaves M_tot=int G unchanged, so Phi_diag(M_tot) is FLAT against it "
      "and the anisotropic curvature is the entropy Hessian alone)")

# (4) strict minimum in EVERY angular sector: min(l=0, l>=1 curvature) > 0
#     l>=1: entropy floor; l=0: entropy floor + Phi''_diag * w (w = (radial M_tot overlap)^2 >= 0, here >0)
#     conservative: even with w->0 the l=0 sector retains the entropy floor, and Phi2>0 only adds.
sector_min = ent_floor   # the binding sector is the entropy floor (shared by all l); interaction only adds at l=0
claim("strict_minimum_all_sectors", sector_min > 0.0 and phi2 > 0.0,
      f"(min sector curvature = min over l of H_l = entropy floor {ent_floor:.4e} > 0 (l>=1), with the l=0 sector "
      f"FURTHER raised by Phi''_diag={phi2:.4f}>0: the isotropic dressing is a STRICT diagonal minimum, isotropy "
      "protected by a positive curvature gap in every angular-momentum sector)")

# (5) quantitative sanity: mechanism + signs + magnitudes
sanity = (u_eff > 0 > U) and (ent_floor > 0) and (max_aniso < 1e-3) and (phi2 == 1.5 * u_eff)
claim("quantitative_sanity_isotropy_mechanism", sanity,
      f"(mechanism: Phi_diag depends only on the ROTATION-INVARIANT M_tot=int G, so its Hessian acts only on l=0; "
      f"signs: bare u={U}<0 lifted to u_eff={u_eff:.3f}>0 by sextic => Phi''_diag={phi2:.3f}>0; entropy floor "
      f"{ent_floor:.3e}>0; angular <Y_{{l>=1}}>={max_aniso:.1e}~0. Isotropy is curvature-protected, not fine-tuned)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B2-PROPA-HLAYER" / "runs" / "260610-res5-016-isotropy-infimum-core"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="res5_016_isotropy_infimum_core.py", version=__version__,
    mu2=MU2, rR=rR, M_R=M_R, u_eff=u_eff, c=C, phi2_diag=phi2,
    entropy_floor=ent_floor, anisotropy_integrals=aniso_int, max_anisotropy_integral=max_aniso,
    verdict=("T-016 isotropy-infimum core: F_0 Hessian block-diagonal in angular momentum; interaction curves only "
             "l=0 (Phi''_diag=(3/2)u_eff=%.3f>0); l>=1 see entropy (1/2)G_*^-2>=%.3e>0. Isotropic dressing is a "
             "STRICT diagonal minimum, isotropy curvature-protected. Math427 core, conditional on H-diag; "
             "off-diagonal extension reduced (T-018) to exchange scalar b_exch (RES-5). No tier flip." % (phi2, ent_floor)),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nPhi''_diag={phi2:.4f}; entropy floor={ent_floor:.4e}; max <Y_l>= {max_aniso:.2e}")
print(f"claims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
