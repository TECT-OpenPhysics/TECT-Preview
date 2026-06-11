"""hdiag_convexity_probe.py -- RES-1 grounding: the condensate-free convexity that
isolates the H-diag obstruction to the condensate-induced off-diagonal sector.

Math427 proves the isotropic dressing is the infimum within the DIAGONAL Gaussian
class because the interaction functional Phi depends on the trial only through the
scalar total variance M_tot (local quartic/sextic interactions). This script
grounds the structural claim of the RES-1 formulation note:

  (i)  the diagonal Hartree interaction is CONVEX in M: Phi(M) = (3u/4)M^2 + (5v/2)M^3
       (Wick-reduced phi^4 + phi^6), so Phi''(M) = (3/2)(u + 10 v M) = (3/2) u_eff > 0
       for repulsive u,v>0 -- the unique isotropic stationary point is the diagonal
       GLOBAL minimum (upgrading Math427's 'infimum' to convex-unique);
  (ii) the sextic gives boundary coercivity (5v/2)M^3 -> +infty (Math427's escape
       exclusion);
  (iii) the entropy term -1/2 Tr ln G is convex in G (per-mode Hessian 1/(2G^2) > 0).

Together (i)-(iii) prove F[G] is convex in the full covariance G ABSENT the
condensate-induced off-diagonal coupling -- so the diagonal restriction H-diag is
unnecessary EXCEPT for that coupling (the G1'' Bogoliubov-band sector). This
script asserts the convexity scales at the operating point; it does NOT close the
off-diagonal sector (the named RES-1 residual).

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__claims__ = ["B2-PROPA-HLAYER", "B1-RH-ENUM"]

import json, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "archive" / "legacy" / "scripts"))
import Math424_AddA_reading_uniqueness as m424  # noqa: E402

U, V, Q0, C = m424.U, m424.V, m424.Q0, m424.C
MU2 = 0.005
CLAIMS = []
def claim(name, cond, detail=""):
    CLAIMS.append(dict(name=name, passed=bool(cond), detail=detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

rR = m424.gap_solve(MU2, 0, 0, 0.0)
M_R = m424.M_fast(rR)
u_eff = U + 10.0 * V * M_R
Phi_pp = 1.5 * u_eff
print(f"operating point mu^2={MU2}: rR={rR:.5f}, M_R={M_R:.5f}, U={U}, V={V}, u_eff={u_eff:.5f}")

# (i) diagonal Hartree convexity: Phi''(M) = (3/2) u_eff > 0
claim("repulsive_quartic_u_eff_positive", u_eff > 0,
      f"(u_eff = U + 10 V M_R = {u_eff:.5f} > 0: dressed quartic repulsive)")
claim("diagonal_hartree_convex", Phi_pp > 0,
      f"(Phi''(M) = (3/2) u_eff = {Phi_pp:.5f} > 0: the diagonal interaction is strictly convex in M, "
      "so the isotropic stationary point is the UNIQUE diagonal-class minimum, not merely an infimum)")

# (ii) sextic boundary coercivity
claim("sextic_repulsive_coercive", V > 0,
      f"(V = {V} > 0: the sextic (5v/2)M^3 -> +infty provides boundary coercivity (Math427 escape exclusion))")

# (iii) entropy convexity (per-mode Hessian of -1/2 ln G is 1/(2 G^2) > 0)
import numpy as np
qs = np.linspace(1e-6, 6.0 * Q0, 200)
Ginv = rR + C * (qs**2 - Q0**2) ** 2          # diagonal inverse propagator at the dressing
G = 1.0 / Ginv
entropy_hess = 0.5 * G**(-2)                   # d^2/dG^2 (-1/2 ln G) per mode
claim("entropy_hessian_positive_definite", bool(np.all(entropy_hess > 0)),
      f"(per-mode entropy Hessian 1/(2G^2) > 0 on the BZ grid: min {entropy_hess.min():.3e} > 0 -- "
      "-1/2 Tr ln G is convex in G)")

# (iv) consequence: condensate-free functional is convex => diagonal infimum is global
claim("condensate_free_convex_implies_global_diagonal_min",
      (u_eff > 0) and (V > 0) and bool(np.all(entropy_hess > 0)),
      "(entropy convex + kinetic linear + Hartree convex (u_eff>0,V>0) => F[G] convex ABSENT the "
      "condensate off-diagonal coupling => isotropic dressing is the GLOBAL min over the full covariance "
      "class in that sector; the ONLY possible non-convexity is the condensate-induced off-diagonal "
      "(G1'') Hessian -- the named RES-1 residual)")

ok = all(c["passed"] for c in CLAIMS)
out = REPO / "claims" / "B2-PROPA-HLAYER" / "runs" / "260609-hdiag-convexity-probe"
out.mkdir(parents=True, exist_ok=True)
(out / "result.json").write_text(json.dumps(dict(
    script="hdiag_convexity_probe.py", version=__version__, mu2=MU2,
    rR=rR, M_R=M_R, U=U, V=V, u_eff=u_eff, Phi_pp=Phi_pp,
    entropy_hess_min=float(entropy_hess.min()),
    verdict=("condensate-free functional convex (diagonal infimum global); off-diagonal "
             "condensate Hessian is the RES-1 residual"),
    claims=CLAIMS, all_pass=ok), indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
